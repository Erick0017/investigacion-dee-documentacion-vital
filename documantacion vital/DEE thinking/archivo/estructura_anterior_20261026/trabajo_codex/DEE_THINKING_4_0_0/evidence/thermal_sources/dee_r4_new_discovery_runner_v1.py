from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import shutil
import sys
import time
import traceback
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

CAMPAIGN = "DEE_R4_NEW_FROM_FIRST_PRINCIPLES_V1"
VERSION = "1.0.1"
PRELOCK_SHA = "27095e83d9e43edeccadc44f19d927d48010984752f4148151948fd2815ad376"
EXPECTED_SOURCE_SHA = "44a80f7863d78f596099ddf7d41c9947fa8513503f65067097f1f3b05a8207ab"
EXPECTED_KERNEL_SHA = "0b17ba32037935a255b0f2182a52137bceab424f7e09126b761076b63e42c6ff"
EXPECTED_PACKAGE_SHA = "7e2991b1fc8a053ee44ead6e177b129855ae9265dea68505a8e545f0c3fdf8b4"
EXPECTED_WHEEL_SHA = "69297e6f06761c8b2f65d24a3fd7a2f16a3f67595a7f9660739ab65f47abc939"
EXPECTED_WHEEL_NAME = "dee_universe_v27-27.0.0-cp313-cp313-win_amd64.whl"
P_KERNEL = 19665
SREG_CAP = 19664
BOOTSTRAP_B = 2000
HORIZON = 16
AGES = (32, 96)
NOMINAL_N = 48
NOMINAL_RHO = 0.01
PRIMARY_PREPS = ("direction_cloud", "mixed", "balanced_collisions")
CAL_CONTROLS = ("vacuum", "sparse_normal")
OBS_NAMES = ("DIR_DENSITY", "SREG_DENSITY", "RAW_SUPPORT_FRACTION", "STATE_OCCUPANCY_FRACTION")
CHANNELS = ("I_DIRECTION", "I_SREG")
EPSILONS = (-1, 1, 2)
FIELDS = ("grid_A", "grid_B", "clock_A", "clock_B")
SEM_NORMAL = 1
MASK_STATE = np.uint64(0x00000000FFFFFFFF)
MASK_SREG = np.uint64(0x0000FFFF00000000)
MASK_NIBBLE = np.uint64(0xF)
SHIFT_SREG = 32
SHIFT_DIRX = 48
SHIFT_DIRY = 52
SHIFT_DIRZ = 56
SHIFT_SEM = 60
DIR_SHIFTS = (SHIFT_DIRX, SHIFT_DIRY, SHIFT_DIRZ)
CAMPAIGN_SEED_STRING = "DEE_R4_NEW_20260930_V1"
SEED_MOD = 2**63 - 1

MOORE = tuple(
    (dx, dy, dz)
    for dx in (-1, 0, 1)
    for dy in (-1, 0, 1)
    for dz in (-1, 0, 1)
    if (dx, dy, dz) != (0, 0, 0)
)


class Paused(Exception):
    pass


class TechnicalStop(RuntimeError):
    pass


def clean(x: Any) -> Any:
    if isinstance(x, dict):
        return {str(k): clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(v) for v in x]
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, np.generic):
        return x.item()
    if isinstance(x, Path):
        return str(x)
    if isinstance(x, float):
        if not math.isfinite(x):
            return None
        return float(x)
    return x


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(clean(obj), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def atomic_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(canonical_bytes(obj))
    os.replace(tmp, path)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def signed_nibble_scalar(v: int) -> int:
    return v - 16 if (v & 8) else v


def signed_nibble(arr: np.ndarray) -> np.ndarray:
    a = np.asarray(arr, dtype=np.int16)
    return np.where((a & 0x8) != 0, a - 16, a)


def pack_voxel(state: int = 1, sreg: int = 0, dx: int = 0, dy: int = 0, dz: int = 0, semantic: int = SEM_NORMAL) -> np.uint64:
    if not (0 <= int(state) < 2**32):
        raise ValueError("state out of range")
    if not (0 <= int(sreg) < 2**16):
        raise ValueError("sreg out of range")
    if not (0 <= int(semantic) < 16):
        raise ValueError("semantic out of range")
    if not all(-8 <= int(v) <= 7 for v in (dx, dy, dz)):
        raise ValueError("direction out of range")
    def nib(v: int) -> int:
        return (v if v >= 0 else v + 16) & 0xF
    out = np.uint64(int(state) & 0xFFFFFFFF)
    out |= np.uint64(int(sreg) & 0xFFFF) << np.uint64(SHIFT_SREG)
    out |= np.uint64(nib(int(dx))) << np.uint64(SHIFT_DIRX)
    out |= np.uint64(nib(int(dy))) << np.uint64(SHIFT_DIRY)
    out |= np.uint64(nib(int(dz))) << np.uint64(SHIFT_DIRZ)
    out |= np.uint64(int(semantic) & 0xF) << np.uint64(SHIFT_SEM)
    return out


def unpack_fields(raw: np.ndarray) -> Dict[str, np.ndarray]:
    a = np.asarray(raw, dtype=np.uint64)
    return {
        "state": (a & MASK_STATE).astype(np.uint32),
        "sreg": ((a >> np.uint64(SHIFT_SREG)) & np.uint64(0xFFFF)).astype(np.uint16),
        "dx": signed_nibble((a >> np.uint64(SHIFT_DIRX)) & MASK_NIBBLE),
        "dy": signed_nibble((a >> np.uint64(SHIFT_DIRY)) & MASK_NIBBLE),
        "dz": signed_nibble((a >> np.uint64(SHIFT_DIRZ)) & MASK_NIBBLE),
        "semantic": ((a >> np.uint64(SHIFT_SEM)) & MASK_NIBBLE).astype(np.uint8),
    }


def unpack_scalar(v: int) -> Dict[str, int]:
    return {
        "state": int(v & 0xFFFFFFFF),
        "sreg": int((v >> SHIFT_SREG) & 0xFFFF),
        "dx": signed_nibble_scalar(int((v >> SHIFT_DIRX) & 0xF)),
        "dy": signed_nibble_scalar(int((v >> SHIFT_DIRY) & 0xF)),
        "dz": signed_nibble_scalar(int((v >> SHIFT_DIRZ) & 0xF)),
        "semantic": int((v >> SHIFT_SEM) & 0xF),
    }


def state_hash(s: Dict[str, Any]) -> str:
    h = hashlib.sha256()
    h.update(canonical_bytes({"tick": int(s["tick"]), "shape": list(np.asarray(s["grid_A"]).shape)}))
    for k in FIELDS:
        h.update(k.encode("ascii"))
        h.update(np.ascontiguousarray(s[k], dtype="<u8").tobytes())
    return h.hexdigest()


def field_hashes(s: Dict[str, Any]) -> Dict[str, str]:
    out = {}
    for k in FIELDS:
        out[k] = sha_bytes(np.ascontiguousarray(s[k], dtype="<u8").tobytes())
    return out


def clone_state(s: Dict[str, Any]) -> Dict[str, Any]:
    return {k: (v.copy() if isinstance(v, np.ndarray) else int(v) if k == "tick" else v) for k, v in s.items()}


def seed_digest(domain: str, panel: str, preparation: str, role: str, index: int) -> bytes:
    msg = f"{CAMPAIGN_SEED_STRING}|{domain}|{panel}|{preparation}|{role}|{int(index)}".encode("utf-8")
    return hashlib.sha256(msg).digest()


def seed_for(domain: str, panel: str, preparation: str, role: str, index: int) -> int:
    d = seed_digest(domain, panel, preparation, role, index)
    v = int.from_bytes(d[:8], "big") % SEED_MOD
    return 1 if v == 0 else v


def translation_for(domain: str, panel: str, preparation: str, role: str, index: int, n: int) -> Tuple[int, int, int]:
    d = seed_digest(domain, panel, preparation, role, index)
    return tuple(int.from_bytes(d[o:o+8], "big") % int(n) for o in (8, 16, 24))


def site_index(seed: int, preparation: str, age: int, panel: str, channel: str, count: int) -> int:
    if count <= 0:
        raise ValueError("empty eligible site set")
    msg = f"{CAMPAIGN_SEED_STRING}|SITE|{panel}|{preparation}|{int(age)}|{int(seed)}|{channel}".encode("utf-8")
    d = hashlib.sha256(msg).digest()
    return int.from_bytes(d[:8], "big") % int(count)


def roll_state(s: Dict[str, Any], shift: Tuple[int, int, int]) -> Dict[str, Any]:
    out = clone_state(s)
    for k in FIELDS:
        out[k] = np.roll(out[k], shift=shift, axis=(0, 1, 2))
    return out


def random_direction(rng: np.random.Generator) -> Tuple[int, int, int]:
    return MOORE[int(rng.integers(0, len(MOORE)))]


def blank_state(n: int) -> Dict[str, Any]:
    z = np.zeros((n, n, n), dtype=np.uint64)
    return {"grid_A": z.copy(), "grid_B": z.copy(), "clock_A": z.copy(), "clock_B": z.copy(), "tick": 0}


def build_initial_state(n: int, family: str, density: float, seed: int, translation: Tuple[int, int, int]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    s = blank_state(n)
    g = s["grid_A"]
    c = s["clock_A"]
    rng = np.random.default_rng(int(seed))
    total = n ** 3
    meta: Dict[str, Any] = {"family": family, "requested_density": float(density), "seed": int(seed)}
    if family == "vacuum":
        meta.update({"requested_count": 0, "actual_raw_nonzero": 0})
    elif family in ("direction_cloud", "mixed", "sparse_normal"):
        count = max(0, min(total, int(round(float(density) * total))))
        ids = rng.choice(total, size=count, replace=False) if count else np.asarray([], dtype=np.int64)
        flat = g.reshape(-1)
        clk = c.reshape(-1)
        for idx in ids:
            d = random_direction(rng)
            ii = int(idx)
            if family == "direction_cloud":
                flat[ii] = pack_voxel(1, int(rng.choice((0, 4, 8, 16, 31))), d[0], d[1], d[2], SEM_NORMAL)
            elif family == "mixed":
                mode = int(rng.integers(0, 4))
                if mode == 0:
                    flat[ii] = pack_voxel(0, int(rng.choice((4, 8, 12))), d[0], d[1], d[2], SEM_NORMAL)
                elif mode == 1:
                    flat[ii] = pack_voxel(1, int(rng.choice((0, 4, 8, 16))), d[0], d[1], d[2], SEM_NORMAL)
                elif mode == 2:
                    flat[ii] = pack_voxel(1, int(rng.choice((0, 4))), 0, 0, 0, 2)
                else:
                    flat[ii] = pack_voxel(1, 0, 0, 0, 0, SEM_NORMAL)
                    clk[ii] = np.uint64(int(rng.choice((0, 7, 17, 23, 391))))
            else:
                flat[ii] = pack_voxel(1, int(rng.choice((0, 1, 2))), 0, 0, 0, SEM_NORMAL)
        meta.update({"requested_count": int(count), "actual_raw_nonzero": int(np.count_nonzero(g))})
    elif family == "balanced_collisions":
        target_count = max(1, int(round(float(density) * total / 3.0)))
        occupied = set()
        made = 0
        for _ in range(target_count * 5):
            if made >= target_count:
                break
            target = np.asarray(rng.integers(2, n - 2, size=3), dtype=int)
            o1, o2 = rng.choice(len(MOORE), size=2, replace=False)
            offs = (np.asarray(MOORE[int(o1)]), np.asarray(MOORE[int(o2)]))
            qs = [tuple(((target + o) % n).tolist()) for o in offs]
            if any(q in occupied for q in qs):
                continue
            for q, o in zip(qs, offs):
                d = -o
                g[q] = pack_voxel(1, int(rng.choice((4, 8, 16, 31, 391))), int(d[0]), int(d[1]), int(d[2]), SEM_NORMAL)
                c[q] = np.uint64(int(rng.choice((0, 17, 23, 391))))
                occupied.add(q)
            made += 1
        meta.update({"targets_requested": int(target_count), "targets_materialized": int(made), "source_sites": int(len(occupied)), "actual_raw_nonzero": int(np.count_nonzero(g))})
    else:
        raise ValueError(f"unknown preparation {family}")
    if translation != (0, 0, 0):
        s = roll_state(s, translation)
    meta["translation"] = list(map(int, translation))
    meta["realized_raw_support_fraction_t0"] = float(np.mean(s["grid_A"] != 0))
    meta["initial_state_hash"] = state_hash(s)
    return s, meta


def observables(s: Dict[str, Any], axis: int) -> Dict[str, Any]:
    g = np.asarray(s["grid_A"], dtype=np.uint64)
    f = unpack_fields(g)
    v = float(g.size)
    dirs = (f["dx"], f["dy"], f["dz"])
    primary = np.asarray([
        float(np.sum(dirs[axis], dtype=np.int64) / v),
        float(np.sum(f["sreg"], dtype=np.uint64) / v),
        float(np.count_nonzero(g) / v),
        float(np.count_nonzero(f["state"]) / v),
    ], dtype=float)
    return {
        "primary": primary,
        "clock_nonzero_fraction": float(np.count_nonzero(s["clock_A"]) / v),
    }


def raw_activity(s0: Dict[str, Any], s1: Dict[str, Any]) -> float:
    changed = (s0["grid_A"] != s1["grid_A"]) | (s0["clock_A"] != s1["clock_A"])
    return float(np.mean(changed))


def internal_activity(s0: Dict[str, Any], s1: Dict[str, Any]) -> float:
    best = 1.0
    for shift in ((i, j, k) for i in (-1, 0, 1) for j in (-1, 0, 1) for k in (-1, 0, 1)):
        mismatch = np.zeros_like(s1["grid_A"], dtype=bool)
        for field in FIELDS:
            mismatch |= np.roll(s0[field], shift=shift, axis=(0, 1, 2)) != s1[field]
        val = float(np.mean(mismatch))
        if val < best:
            best = val
    return best


def eligible_sites(s: Dict[str, Any], axis: int) -> np.ndarray:
    masks = []
    for field in ("grid_A", "grid_B"):
        f = unpack_fields(s[field])
        d = (f["dx"], f["dy"], f["dz"])[axis]
        masks.append((f["state"] > 0) & (f["semantic"] == SEM_NORMAL) & (f["sreg"] >= 1) & (f["sreg"] <= 19662) & (d >= -7) & (d <= 5))
    m = masks[0] & masks[1]
    return np.argwhere(m)


def rewrite_voxel(raw: np.uint64, channel: str, axis: int, epsilon: int) -> np.uint64:
    d = unpack_scalar(int(raw))
    if channel == "I_DIRECTION":
        vec = [d["dx"], d["dy"], d["dz"]]
        vec[axis] += int(epsilon)
        return pack_voxel(d["state"], d["sreg"], vec[0], vec[1], vec[2], d["semantic"])
    if channel == "I_SREG":
        return pack_voxel(d["state"], d["sreg"] + int(epsilon), d["dx"], d["dy"], d["dz"], d["semantic"])
    raise ValueError(channel)


def intervene(s: Dict[str, Any], preparation: str, age: int, panel: str, seed: int, channel: str, axis: int, epsilon: int, sham: bool = False) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
    coords = eligible_sites(s, axis)
    if len(coords) == 0:
        return None, {"eligible": False, "eligible_count": 0, "channel": channel, "epsilon": int(epsilon)}
    q = tuple(map(int, coords[site_index(seed, preparation, age, panel, channel, len(coords))]))
    out = clone_state(s)
    before_clocks = {k: out[k].copy() for k in ("clock_A", "clock_B")}
    for field in ("grid_A", "grid_B"):
        old = np.uint64(out[field][q])
        out[field][q] = old if sham else rewrite_voxel(old, channel, axis, epsilon)
    if not np.array_equal(before_clocks["clock_A"], out["clock_A"]) or not np.array_equal(before_clocks["clock_B"], out["clock_B"]):
        raise TechnicalStop("intervention changed clock buffer")
    return out, {
        "eligible": True,
        "eligible_count": int(len(coords)),
        "site": list(q),
        "channel": channel,
        "epsilon": int(epsilon),
        "pre_state_hash": state_hash(s),
        "post_state_hash": state_hash(out),
        "pre_field_hashes": field_hashes(s),
        "post_field_hashes": field_hashes(out),
    }


class Native:
    def __init__(self, threads: int, wheel_path: str = "", source_path: str = ""):
        if platform.system() != "Windows":
            raise TechnicalStop(f"external runner requires native Windows; got {platform.system()}")
        if sys.version_info[:2] != (3, 13):
            raise TechnicalStop(f"CPython 3.13 required; got {sys.version}")
        try:
            import dee_universe_v27 as pkg
            from dee_universe_v27 import UniversoDEE_v27, dee_kernel_v27
        except Exception as e:
            raise TechnicalStop("real dee_universe_v27 is required; no fallback backend exists") from e
        self.pkg = pkg
        self.cls = UniversoDEE_v27
        self.kernel_module = dee_kernel_v27
        self.threads = int(threads)
        kp = Path(dee_kernel_v27.__file__).resolve()
        pp = Path(pkg.__file__).resolve()
        kernel_sha = sha_file(kp)
        package_sha = sha_file(pp)
        if kernel_sha != EXPECTED_KERNEL_SHA:
            raise TechnicalStop(f"kernel .pyd SHA mismatch: {kernel_sha}")
        if package_sha != EXPECTED_PACKAGE_SHA:
            raise TechnicalStop(f"package __init__.py SHA mismatch: {package_sha}")
        wheel_status = "NOT_FOUND"
        wheel_sha = None
        candidates = []
        if wheel_path:
            candidates.append(Path(wheel_path).resolve())
        here = Path(__file__).resolve().parent
        candidates.extend([
            here / EXPECTED_WHEEL_NAME,
            Path.cwd() / EXPECTED_WHEEL_NAME,
            pp.parent / EXPECTED_WHEEL_NAME,
            pp.parent.parent / EXPECTED_WHEEL_NAME,
        ])
        seen = set()
        wp = None
        for cand in candidates:
            key = str(cand).lower()
            if key in seen:
                continue
            seen.add(key)
            if cand.is_file():
                wp = cand.resolve()
                break
        if wp is None:
            raise TechnicalStop(
                "canonical wheel bytes are required for OFFICIAL_WHL verification. "
                f"Place {EXPECTED_WHEEL_NAME} beside the runner or pass --wheel PATH"
            )
        wheel_sha = sha_file(wp)
        if wheel_sha != EXPECTED_WHEEL_SHA:
            raise TechnicalStop(f"wheel SHA mismatch: {wheel_sha}")
        wheel_status = "VERIFIED"
        source_status = "NOT_PROVIDED"
        source_sha = None
        if source_path:
            sp = Path(source_path).resolve()
            if not sp.is_file():
                raise TechnicalStop(f"source path not found: {sp}")
            source_sha = sha_file(sp)
            if source_sha != EXPECTED_SOURCE_SHA:
                raise TechnicalStop(f"source SHA mismatch: {source_sha}")
            source_status = "VERIFIED"
        self.env = {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": sys.version,
            "numpy": np.__version__,
            "package_path": str(pp),
            "kernel_path": str(kp),
            "package_sha256": package_sha,
            "kernel_sha256": kernel_sha,
            "wheel_status": wheel_status,
            "wheel_sha256": wheel_sha,
            "wheel_path": str(wp),
            "source_status": source_status,
            "source_sha256": source_sha,
            "kernel_version_string": getattr(dee_kernel_v27, "VERSION", None),
            "package_version": getattr(pkg, "__version__", None),
            "threads_requested": self.threads,
        }

    def new(self, s: Dict[str, Any], threads: Optional[int] = None) -> Any:
        u = self.cls(N=int(s["grid_A"].shape[0]), n_hilos=int(self.threads if threads is None else threads))
        for field in FIELDS:
            np.asarray(getattr(u, field)).reshape(s[field].shape)[:] = s[field]
        if hasattr(u, "tick_global"):
            u.tick_global = int(s["tick"])
        return u

    def snap(self, u: Any) -> Dict[str, Any]:
        n = int(u.N)
        return {
            **{field: np.asarray(getattr(u, field), dtype=np.uint64).reshape((n, n, n)).copy() for field in FIELDS},
            "tick": int(getattr(u, "tick_global", 0)),
        }

    def step(self, u: Any) -> None:
        u.tick(1)


class Run:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.started = time.perf_counter()
        self.native_steps = 0
        self.root_dir = Path(__file__).resolve().parent
        self.work = Path(args.workdir or (Path.cwd() / (CAMPAIGN + "_DISCOVERY_WORK"))).resolve()
        self.work.mkdir(parents=True, exist_ok=True)
        self.lock_path = self.work / "RUNNING.lock"
        if args.unlock and self.lock_path.exists():
            self.lock_path.unlink()
        try:
            fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode("ascii"))
            os.close(fd)
        except FileExistsError as e:
            raise RuntimeError("RUNNING.lock exists. Use --unlock only after confirming no process is active.") from e
        self.runner_sha = sha_file(Path(__file__).resolve())
        self.prelock = load_json(self.root_dir / "PRE_EXECUTION_LOCK.json")
        if sha_bytes(canonical_bytes(self.prelock)) != PRELOCK_SHA:
            self.release()
            raise TechnicalStop("PRE_EXECUTION_LOCK SHA mismatch")
        self.contract = {
            "campaign": CAMPAIGN,
            "version": VERSION,
            "runner_sha256": self.runner_sha,
            "pre_execution_lock_sha256": PRELOCK_SHA,
            "holdout_embargoed": True,
        }
        cp = self.work / "CONTRACT.json"
        if cp.exists() and load_json(cp) != clean(self.contract):
            self.release()
            raise TechnicalStop("contract changed; use a new workdir")
        atomic_json(cp, self.contract)
        self.status_path = self.work / "RUN_STATUS.json"
        if not self.status_path.exists():
            atomic_json(self.status_path, {"campaign": CAMPAIGN, "version": VERSION, "status": "initialized", "holdout_touched": False})
        self.native: Optional[Native] = None

    def release(self) -> None:
        try:
            if self.lock_path.exists():
                self.lock_path.unlink()
        except Exception:
            pass

    def guard(self) -> None:
        if self.args.hours > 0 and (time.perf_counter() - self.started) >= self.args.hours * 3600.0:
            raise Paused("time budget reached")
        if self.args.max_disk_gb > 0:
            total = 0
            for p in self.work.rglob("*"):
                if p.is_file():
                    try:
                        total += p.stat().st_size
                    except OSError:
                        pass
            if total > self.args.max_disk_gb * (1024**3):
                raise Paused("disk budget reached")

    def step(self, u: Any) -> None:
        self.guard()
        assert self.native is not None
        self.native.step(u)
        self.native_steps += 1

    def module(self, name: str, fn) -> Any:
        path = self.work / "modules" / f"{name}.json"
        if path.exists():
            return load_json(path)
        self.guard()
        result = fn()
        atomic_json(path, result)
        return result

    def telemetry_path(self, domain: str, role: str, prep: str, index: int) -> Path:
        return self.work / "telemetry" / domain / role / prep / f"world_{index:04d}.json"

    def set_status(self, **kwargs: Any) -> None:
        data = load_json(self.status_path) if self.status_path.exists() else {}
        data.update(clean(kwargs))
        data["native_steps_this_invocation"] = int(self.native_steps)
        data["seconds_this_invocation"] = float(time.perf_counter() - self.started)
        atomic_json(self.status_path, data)

    def finalize_zip(self, summary: Dict[str, Any]) -> Path:
        shutil.copyfile(Path(__file__).resolve(), self.work / Path(__file__).name)
        for name in ("R4_NEW_PREREGISTRATION.json", "PRE_EXECUTION_LOCK.json", "PRE_EXECUTION_LOCK.sha256", "EXPECTED_V27_IDENTITY.json", "TECHNICAL_HOTFIX_V1_0_1.json"):
            shutil.copyfile(self.root_dir / name, self.work / name)
        atomic_json(self.work / "SUMMARY.json", summary)
        rows = []
        for p in sorted(self.work.rglob("*")):
            if not p.is_file() or p.name in ("RUNNING.lock", "MANIFEST.json") or p.suffix in (".tmp", ".zip"):
                continue
            rows.append({"path": p.relative_to(self.work).as_posix(), "sha256": sha_file(p), "bytes": int(p.stat().st_size)})
        manifest = {"campaign": CAMPAIGN, "status": "completed_discovery_locked", "official_delivery": "single_zip", "holdout_touched": False, "files": rows}
        atomic_json(self.work / "MANIFEST.json", manifest)
        out = Path(self.args.output or (Path.cwd() / "DEE_R4_NEW_DISCOVERY_V1_RESULTADOS.zip")).resolve()
        if out.exists():
            raise TechnicalStop(f"refusing to overwrite existing official ZIP: {out}")
        with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for p in sorted(self.work.rglob("*")):
                if not p.is_file() or p.name == "RUNNING.lock" or p.suffix == ".tmp" or p == out:
                    continue
                z.write(p, arcname=p.relative_to(self.work).as_posix())
        return out


def all_planned_seed_records() -> List[Dict[str, Any]]:
    rows = []
    def add(domain: str, panel: str, prep: str, role: str, n_worlds: int, n: int):
        for i in range(n_worlds):
            rows.append({"domain": domain, "panel": panel, "preparation": prep, "role": role, "index": i, "seed": seed_for(domain, panel, prep, role, i), "translation": list(translation_for(domain, panel, prep, role, i, n))})
    for prep in PRIMARY_PREPS:
        add("CALIBRATION", "CALIBRATION", prep, "F", 12, 48)
        add("CALIBRATION", "CALIBRATION", prep, "R", 6, 48)
        add("DISCOVERY", "DISCOVERY", prep, "F", 16, 48)
        add("DISCOVERY", "DISCOVERY", prep, "R", 16, 48)
    for prep in CAL_CONTROLS:
        add("CALIBRATION", "CAL_CONTROL", prep, "F", 6, 48)
    hold = {
        "H1": (48, 16), "H2_Y": (48, 8), "H2_Z": (48, 8), "H2_N64": (64, 8), "H2_RHO02": (48, 8)
    }
    for panel, (n, count) in hold.items():
        for prep in PRIMARY_PREPS:
            add("HOLDOUT", panel, prep, "F", count, n)
            add("HOLDOUT", panel, prep, "R", count, n)
    return rows


def static_self_tests() -> Dict[str, Any]:
    checks: Dict[str, Any] = {}
    rows = all_planned_seed_records()
    seeds = [r["seed"] for r in rows]
    checks["seed_count"] = len(seeds)
    checks["seed_unique"] = len(seeds) == len(set(seeds))
    checks["seed_reproducible"] = rows[:20] == all_planned_seed_records()[:20]
    groups: Dict[str, set] = {}
    for r in rows:
        key = r["domain"] + ":" + r["role"]
        groups.setdefault(key, set()).add(r["seed"])
    cal = set().union(*(v for k, v in groups.items() if k.startswith("CALIBRATION:")))
    disc = set().union(*(v for k, v in groups.items() if k.startswith("DISCOVERY:")))
    hold = set().union(*(v for k, v in groups.items() if k.startswith("HOLDOUT:")))
    checks["domains_disjoint"] = not (cal & disc or cal & hold or disc & hold)
    checks["F_R_disjoint"] = all(not (groups.get(d + ":F", set()) & groups.get(d + ":R", set())) for d in ("CALIBRATION", "DISCOVERY", "HOLDOUT"))
    vals = [
        pack_voxel(1, 1, 0, 0, 0, 1),
        pack_voxel(123, 19664, -7, 5, 1, 3),
        pack_voxel(1, 17, 7, -8, 0, 1),
    ]
    rt_ok = True
    for v in vals:
        d = unpack_scalar(int(v))
        vv = pack_voxel(d["state"], d["sreg"], d["dx"], d["dy"], d["dz"], d["semantic"])
        rt_ok &= int(vv) == int(v)
    checks["pack_unpack_roundtrip"] = bool(rt_ok)
    syn = blank_state(8)
    q = (2, 3, 4)
    syn["grid_A"][q] = pack_voxel(1, 10, 1, -1, 0, 1)
    syn["grid_B"][q] = syn["grid_A"][q]
    obs = observables(syn, 0)["primary"]
    checks["synthetic_observer"] = bool(abs(obs[0] - 1 / 512) < 1e-15 and abs(obs[1] - 10 / 512) < 1e-15 and abs(obs[2] - 1 / 512) < 1e-15 and abs(obs[3] - 1 / 512) < 1e-15)
    dstate, meta = intervene(syn, "synthetic", 0, "SELFTEST", 123, "I_DIRECTION", 0, 1)
    sstate, meta2 = intervene(syn, "synthetic", 0, "SELFTEST", 123, "I_SREG", 0, 1)
    checks["direction_h0_algebra"] = bool(dstate is not None and np.allclose(observables(dstate, 0)["primary"] - obs, [1/512, 0, 0, 0], atol=1e-15))
    checks["sreg_h0_algebra"] = bool(sstate is not None and np.allclose(observables(sstate, 0)["primary"] - obs, [0, 1/512, 0, 0], atol=1e-15))
    checks["clock_preserved_direction"] = bool(dstate is not None and np.array_equal(dstate["clock_A"], syn["clock_A"]) and np.array_equal(dstate["clock_B"], syn["clock_B"]))
    checks["clock_preserved_sreg"] = bool(sstate is not None and np.array_equal(sstate["clock_A"], syn["clock_A"]) and np.array_equal(sstate["clock_B"], syn["clock_B"]))
    t = (2, 1, 3)
    checks["translation_reproducible"] = state_hash(roll_state(syn, t)) == state_hash(roll_state(syn, t))
    obj = {"b": 2, "a": [1, 3]}
    checks["canonical_hash_reproducible"] = sha_bytes(canonical_bytes(obj)) == sha_bytes(canonical_bytes(obj))
    pre = Path(__file__).resolve().parent / "PRE_EXECUTION_LOCK.json"
    checks["prelock_present"] = pre.is_file()
    checks["prelock_sha_ok"] = pre.is_file() and sha_bytes(canonical_bytes(load_json(pre))) == PRELOCK_SHA
    checks["all_pass"] = all(bool(v) for k, v in checks.items() if k not in ("seed_count", "all_pass"))
    return checks


def center_one_tick(native: Native, offsets: Sequence[Sequence[int]], sregs: Sequence[int], threads: int, clock_center: int = 0, start_center: Optional[int] = None) -> Dict[str, Any]:
    n = 11
    ctr = np.asarray([5, 5, 5])
    s = blank_state(n)
    if start_center is not None:
        s["grid_A"][tuple(ctr)] = pack_voxel(1, int(start_center), 0, 0, 0, SEM_NORMAL)
        s["clock_A"][tuple(ctr)] = np.uint64(int(clock_center))
    for o, sr in zip(offsets, sregs):
        oo = np.asarray(o, dtype=int)
        d = -oo
        q = tuple((ctr + oo).tolist())
        s["grid_A"][q] = pack_voxel(1, int(sr), int(d[0]), int(d[1]), int(d[2]), SEM_NORMAL)
    u = native.new(s, threads=threads)
    native.step(u)
    out = native.snap(u)
    return {"state": out, "center": unpack_scalar(int(out["grid_A"][tuple(ctr)])), "clock": int(out["clock_A"][tuple(ctr)])}


def native_canaries(run: Run) -> Dict[str, Any]:
    assert run.native is not None
    native = run.native
    out: Dict[str, Any] = {}
    seed = seed_for("CALIBRATION", "CANARY", "direction_cloud", "F", 0)
    trans = translation_for("CALIBRATION", "CANARY", "direction_cloud", "F", 0, 16)
    s0, _ = build_initial_state(16, "direction_cloud", 0.02, seed, trans)
    u = native.new(s0)
    snap = native.snap(u)
    out["A_snapshot_reconstruction"] = state_hash(s0) == state_hash(snap)
    ua = native.new(s0)
    ub = native.new(s0)
    clone_ok = True
    for _ in range(16):
        run.step(ua); run.step(ub)
        if state_hash(native.snap(ua)) != state_hash(native.snap(ub)):
            clone_ok = False
            break
    out["B_base_clone_16"] = clone_ok
    # Technical hotfix v1.0.1: the initial DEE preparation intentionally seeds
    # grid_A/clock_A while grid_B/clock_B are scratch buffers until the native
    # tick synchronizes them. eligible_sites() correctly requires simultaneous
    # eligibility in A and B for a real matched intervention, so applying the
    # sham to the virgin t=0 preparation made the canary structurally
    # ineligible. Test the sham on an explicit intervention-ready dual-buffer
    # state instead. This changes only the instrumentation canary, not any
    # calibration/discovery preparation, observer, intervention, seed, or fit.
    sham_base = blank_state(12)
    q_sham = (4, 4, 4)
    sham_base["grid_A"][q_sham] = pack_voxel(1, 10, 1, 0, 0, SEM_NORMAL)
    sham_base["grid_B"][q_sham] = sham_base["grid_A"][q_sham]
    sham, _ = intervene(sham_base, "synthetic", 0, "CANARY", 456, "I_DIRECTION", 0, 1, sham=True)
    if sham is None:
        out["C_sham_16"] = False
    else:
        ua = native.new(sham_base); ub = native.new(sham)
        sham_ok = state_hash(sham_base) == state_hash(sham)
        for _ in range(16):
            run.step(ua); run.step(ub)
            if state_hash(native.snap(ua)) != state_hash(native.snap(ub)):
                sham_ok = False; break
        out["C_sham_16"] = sham_ok
    u1 = native.new(s0, threads=1); u4 = native.new(s0, threads=4)
    for _ in range(16):
        run.step(u1); run.step(u4)
    out["D_threads1_vs4"] = state_hash(native.snap(u1)) == state_hash(native.snap(u4))
    syn = blank_state(12)
    q = (4, 4, 4)
    syn["grid_A"][q] = pack_voxel(1, 10, 1, 0, 0, 1)
    syn["grid_B"][q] = syn["grid_A"][q]
    before = observables(syn, 0)["primary"]
    d1, _ = intervene(syn, "synthetic", 0, "CANARY", 456, "I_DIRECTION", 0, 1)
    sr1, _ = intervene(syn, "synthetic", 0, "CANARY", 456, "I_SREG", 0, 1)
    out["E_direction_h0"] = bool(d1 is not None and np.allclose(observables(d1, 0)["primary"] - before, [1/(12**3), 0, 0, 0], atol=1e-15))
    out["F_sreg_h0"] = bool(sr1 is not None and np.allclose(observables(sr1, 0)["primary"] - before, [0, 1/(12**3), 0, 0], atol=1e-15))
    bounds_ok = True
    for channel in CHANNELS:
        for eps in (-1, 2):
            st, _ = intervene(syn, "synthetic", 0, "CANARY", 456, channel, 0, eps)
            bounds_ok &= st is not None
    out["G_bounds_minus1_plus2"] = bool(bounds_ok)
    faces = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
    p1957 = center_one_tick(native, faces, [0]*6, 1, 0, 19657)["center"]
    p1964 = center_one_tick(native, faces, [0]*6, 1, 0, 19664)["center"]
    p1964_phase1 = center_one_tick(native, faces, [0]*6, 1, 1, 19664)["center"]
    agg = center_one_tick(native, MOORE[:6], [3278,3278,3278,3277,3277,3277], 1)["center"]
    out["P_KERNEL_behavior"] = {
        "start19657_clock0_next_sreg": p1957["sreg"],
        "start19664_clock0_next_sreg": p1964["sreg"],
        "start19664_clock1_next_sreg": p1964_phase1["sreg"],
        "aggregate19665_center_sreg": agg["sreg"],
        "pass": bool(p1957["sreg"] >= 19657 and p1964["sreg"] < 19664 and p1964_phase1["sreg"] >= 19664 and agg["sreg"] == SREG_CAP),
    }
    out["all_pass"] = all(bool(v if not isinstance(v, dict) else v.get("pass", False)) for k, v in out.items() if k != "all_pass")
    if not out["all_pass"]:
        raise TechnicalStop("native runtime canary failed")
    return out


def axis_index(axis: str) -> int:
    return {"x":0, "y":1, "z":2}[axis]


def age_snapshots(run: Run, initial: Dict[str, Any], ages: Sequence[int]) -> Dict[int, Dict[str, Any]]:
    assert run.native is not None
    u = run.native.new(initial)
    out: Dict[int, Dict[str, Any]] = {}
    target = sorted(set(map(int, ages)))
    now = int(initial["tick"])
    for t in range(now + 1, max(target) + 1):
        run.step(u)
        if t in target:
            out[t] = run.native.snap(u)
    return out


def series_from_state(run: Run, start: Dict[str, Any], axis: int, horizon: int = HORIZON) -> Dict[str, Any]:
    assert run.native is not None
    u = run.native.new(start)
    obs = []
    hashes = []
    fields = []
    states = [run.native.snap(u)]
    for h in range(horizon + 1):
        if h > 0:
            run.step(u)
            states.append(run.native.snap(u))
        s = states[-1]
        obs.append(observables(s, axis)["primary"].tolist())
        hashes.append(state_hash(s))
        fields.append(field_hashes(s))
    a_raw = raw_activity(states[0], states[1]) if horizon >= 1 else 0.0
    a_int = internal_activity(states[0], states[1]) if horizon >= 1 else 0.0
    return {"observables": obs, "state_hashes": hashes, "field_hashes": fields, "raw_activity_h0_h1": a_raw, "internal_activity_h0_h1": a_int}


def run_f_world(run: Run, domain: str, panel: str, prep: str, index: int, n: int, rho: float, ages: Sequence[int], axis: str) -> Dict[str, Any]:
    path = run.telemetry_path(domain, "F", prep, index)
    if path.exists():
        return load_json(path)
    run.guard()
    seed = seed_for(domain, panel, prep, "F", index)
    trans = translation_for(domain, panel, prep, "F", index, n)
    init, meta = build_initial_state(n, prep, rho, seed, trans)
    snaps = age_snapshots(run, init, ages)
    axis_i = axis_index(axis)
    record = {"domain":domain,"panel":panel,"cohort":"F","preparation":prep,"index":index,"seed":seed,"N":n,"requested_density":rho,"translation":list(trans),"axis":axis,"preparation_meta":meta,"ages":{}}
    for age in ages:
        s = snaps[int(age)]
        ser = series_from_state(run, s, axis_i)
        record["ages"][str(age)] = {"snapshot_hash":state_hash(s),"snapshot_field_hashes":field_hashes(s),"realized_raw_support_fraction":float(np.mean(s["grid_A"] != 0)),"tick_global":int(s["tick"]),"series":ser}
    atomic_json(path, record)
    return record


def run_r_world(run: Run, domain: str, panel: str, prep: str, index: int, n: int, rho: float, ages: Sequence[int], axis: str, include_sham: bool = False) -> Dict[str, Any]:
    path = run.telemetry_path(domain, "R", prep, index)
    if path.exists():
        return load_json(path)
    run.guard()
    seed = seed_for(domain, panel, prep, "R", index)
    trans = translation_for(domain, panel, prep, "R", index, n)
    init, meta = build_initial_state(n, prep, rho, seed, trans)
    snaps = age_snapshots(run, init, ages)
    axis_i = axis_index(axis)
    record = {"domain":domain,"panel":panel,"cohort":"R","preparation":prep,"index":index,"seed":seed,"N":n,"requested_density":rho,"translation":list(trans),"axis":axis,"preparation_meta":meta,"ages":{}}
    for age in ages:
        s = snaps[int(age)]
        base_series = series_from_state(run, s, axis_i)
        age_rec: Dict[str, Any] = {"snapshot_hash":state_hash(s),"snapshot_field_hashes":field_hashes(s),"realized_raw_support_fraction":float(np.mean(s["grid_A"] != 0)),"tick_global":int(s["tick"]),"base":base_series,"probes":{}}
        for channel in CHANNELS:
            age_rec["probes"][channel] = {}
            for eps in EPSILONS:
                ps, imeta = intervene(s, prep, int(age), panel, seed, channel, axis_i, int(eps), sham=False)
                if ps is None:
                    age_rec["probes"][channel][str(eps)] = {"intervention":imeta,"series":None}
                else:
                    pser = series_from_state(run, ps, axis_i)
                    age_rec["probes"][channel][str(eps)] = {"intervention":imeta,"series":pser}
            if include_sham:
                ss, smeta = intervene(s, prep, int(age), panel, seed, channel, axis_i, 1, sham=True)
                age_rec["probes"][channel]["SHAM"] = {"intervention":smeta,"series":series_from_state(run, ss, axis_i) if ss is not None else None}
        record["ages"][str(age)] = age_rec
    atomic_json(path, record)
    return record


def run_control_world(run: Run, prep: str, index: int) -> Dict[str, Any]:
    return run_f_world(run, "CALIBRATION", "CAL_CONTROL", prep, index, 48, 0.0 if prep == "vacuum" else 0.01, (32,), "x")


def collect_calibration(run: Run) -> Dict[str, Any]:
    f_records = []
    r_records = []
    controls = []
    for prep in PRIMARY_PREPS:
        for i in range(12):
            f_records.append(run_f_world(run, "CALIBRATION", "CALIBRATION", prep, i, 48, 0.01, AGES, "x"))
        for i in range(6):
            r_records.append(run_r_world(run, "CALIBRATION", "CALIBRATION", prep, i, 48, 0.01, AGES, "x", include_sham=True))
    for prep in CAL_CONTROLS:
        for i in range(6):
            controls.append(run_control_world(run, prep, i))
    return {"status":"completed","F_worlds":len(f_records),"R_worlds":len(r_records),"control_worlds":len(controls)}


def f_cell_matrix(work: Path, domain: str, prep: str, n_worlds: int, age: int) -> np.ndarray:
    rows = []
    for i in range(n_worlds):
        r = load_json(work / "telemetry" / domain / "F" / prep / f"world_{i:04d}.json")
        rows.append(np.asarray(r["ages"][str(age)]["series"]["observables"], dtype=float))
    return np.stack(rows, axis=0)


def r_cell_data(work: Path, domain: str, prep: str, n_worlds: int, age: int) -> Dict[str, Any]:
    worlds = []
    for i in range(n_worlds):
        r = load_json(work / "telemetry" / domain / "R" / prep / f"world_{i:04d}.json")
        worlds.append(r["ages"][str(age)])
    return {"worlds":worlds}


def covariance_tensor(x: np.ndarray) -> np.ndarray:
    # x: worlds x (h=0..16) x observers
    n, hlen, p = x.shape
    if n < 2:
        raise ValueError("need at least 2 worlds")
    out = np.zeros((p, p, hlen), dtype=float)
    base = x[:, 0, :]
    for a in range(p):
        for b in range(p):
            for h in range(hlen):
                out[a,b,h] = float(np.cov(x[:,h,a], base[:,b], ddof=1)[0,1])
    return out


def response_tensor(rdata: Dict[str, Any], epsilon: int) -> Tuple[np.ndarray, Dict[str, float], Dict[str, np.ndarray]]:
    # returns mean chi [obs, channel, h], eligible fractions, per-world deltas keyed channel
    worlds = rdata["worlds"]
    p = len(OBS_NAMES); q = len(CHANNELS); hlen = HORIZON + 1
    mean = np.full((p,q,hlen), np.nan, dtype=float)
    fracs: Dict[str,float] = {}
    per: Dict[str,np.ndarray] = {}
    for bi, channel in enumerate(CHANNELS):
        rows = []
        for w in worlds:
            pr = w["probes"][channel][str(epsilon)]
            if pr["series"] is None:
                continue
            base = np.asarray(w["base"]["observables"], dtype=float)
            probe = np.asarray(pr["series"]["observables"], dtype=float)
            rows.append((probe - base) / float(epsilon))
        fracs[channel] = len(rows) / max(1, len(worlds))
        if rows:
            arr = np.stack(rows, axis=0)  # worlds x h x obs
            per[channel] = arr
            mean[:,bi,:] = np.mean(arr, axis=0).T
        else:
            per[channel] = np.empty((0,hlen,p), dtype=float)
    return mean, fracs, per


def energy_distance(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, float); y = np.asarray(y, float)
    def md(a: np.ndarray, b: np.ndarray) -> float:
        d = a[:,None,:] - b[None,:,:]
        return float(np.mean(np.sqrt(np.sum(d*d, axis=2))))
    return max(0.0, 2.0*md(x,y) - md(x,x) - md(y,y))


def quantile(a: Sequence[float], q: float) -> float:
    arr = np.asarray(list(a), dtype=float)
    return float(np.quantile(arr, q)) if arr.size else 0.0


def calibration_analysis(run: Run) -> Dict[str, Any]:
    cells = []
    pooled = []
    for prep in PRIMARY_PREPS:
        for age in AGES:
            x = f_cell_matrix(run.work, "CALIBRATION", prep, 12, age)
            cells.append((prep, age, x))
            pooled.append(x[:,[0,8,16],:].reshape(-1,4))
    pooled_arr = np.concatenate(pooled, axis=0)
    mu = np.mean(pooled_arr, axis=0)
    sd = np.std(pooled_arr, axis=0, ddof=1)
    sd = np.where(sd > 0, sd, 1.0)
    rng = np.random.default_rng(seed_for("CALIBRATION", "ANALYSIS", "thresholds", "A", 0))
    ed_null = []
    for prep, age, x in cells:
        for tidx in (0,8,16):
            z = (x[:,tidx,:] - mu) / sd
            n = len(z)
            for _ in range(256):
                perm = rng.permutation(n)
                half = n // 2
                ed_null.append(energy_distance(z[perm[:half]], z[perm[half:2*half]]))
    epsilon_stat = quantile(ed_null, 0.99)
    cnull: Dict[str,List[float]] = {f"{a},{b}":[] for a in range(4) for b in range(4)}
    rng2 = np.random.default_rng(seed_for("CALIBRATION", "ANALYSIS", "cov_null", "A", 0))
    for prep, age, x in cells:
        n = x.shape[0]
        for _ in range(256):
            perm = rng2.permutation(n)
            for a in range(4):
                xa = x[:,:,a]
                for b in range(4):
                    y0 = x[perm,0,b]
                    vals = []
                    for h in range(HORIZON+1):
                        vals.append(float(np.cov(xa[:,h], y0, ddof=1)[0,1]))
                    cnull[f"{a},{b}"].append(max(abs(v) for v in vals))
    c_floor = {k: quantile(v,0.99) for k,v in cnull.items()}
    sham_vals = {str(a):[] for a in range(4)}
    for prep in PRIMARY_PREPS:
        for age in AGES:
            rd = r_cell_data(run.work, "CALIBRATION", prep, 6, age)
            for w in rd["worlds"]:
                for channel in CHANNELS:
                    sh = w["probes"][channel].get("SHAM")
                    if sh and sh["series"] is not None:
                        base=np.asarray(w["base"]["observables"],float); probe=np.asarray(sh["series"]["observables"],float)
                        diff=np.abs(probe-base)
                        for a in range(4): sham_vals[str(a)].append(float(np.max(diff[:,a])))
    chi_floor = {k: quantile(v,0.99) for k,v in sham_vals.items()}
    vacuum_raw=[]; vacuum_int=[]
    for i in range(6):
        r=load_json(run.work/"telemetry"/"CALIBRATION"/"F"/"vacuum"/f"world_{i:04d}.json")
        s=r["ages"]["32"]["series"]
        vacuum_raw.append(float(s["raw_activity_h0_h1"])); vacuum_int.append(float(s["internal_activity_h0_h1"]))
    event_floor=max(quantile(vacuum_raw,0.99),1/(48**3))
    turnover_floor=max(quantile(vacuum_int,0.99),1/(48**3))
    return {
        "status":"completed",
        "standardization":{"mean":mu.tolist(),"sd":sd.tolist()},
        "stationarity_epsilon":epsilon_stat,
        "C_noise_floor":c_floor,
        "CHI_noise_floor":chi_floor,
        "TURNOVER_floor":turnover_floor,
        "EVENT_floor":event_floor,
        "null_counts":{"energy_distance":len(ed_null),"covariance_per_pair":len(next(iter(cnull.values())))},
    }


def collect_discovery(run: Run) -> Dict[str, Any]:
    f=0;r=0
    for prep in PRIMARY_PREPS:
        for i in range(16):
            run_f_world(run,"DISCOVERY","DISCOVERY",prep,i,48,0.01,AGES,"x"); f+=1
        for i in range(16):
            run_r_world(run,"DISCOVERY","DISCOVERY",prep,i,48,0.01,AGES,"x",include_sham=False); r+=1
    return {"status":"completed","F_worlds":f,"R_worlds":r}


def bootstrap_response_nonzero(per_world: np.ndarray, obs_index: int, floor: float, rng: np.random.Generator, B: int = BOOTSTRAP_B) -> Dict[str, Any]:
    # per_world: worlds x h x obs
    if per_world.shape[0] == 0:
        return {"pass":False,"lower95":0.0,"point":0.0}
    arr = per_world[:,1:,obs_index]
    point=float(np.linalg.norm(np.mean(arr,axis=0)))
    vals=[]
    n=arr.shape[0]
    for _ in range(B):
        ids=rng.integers(0,n,size=n)
        vals.append(float(np.linalg.norm(np.mean(arr[ids],axis=0))))
    low=quantile(vals,0.025)
    return {"pass":bool(low > floor*math.sqrt(HORIZON)),"lower95":low,"point":point}


def stationarity_label(x: np.ndarray, cal: Dict[str, Any]) -> Dict[str, Any]:
    mu=np.asarray(cal["standardization"]["mean"],float); sd=np.asarray(cal["standardization"]["sd"],float)
    z=(x-mu[None,None,:])/sd[None,None,:]
    d08=energy_distance(z[:,0,:],z[:,8,:]); d016=energy_distance(z[:,0,:],z[:,16,:]); d816=energy_distance(z[:,8,:],z[:,16,:])
    eps=float(cal["stationarity_epsilon"])
    if d08<=eps and d016<=eps: label="STATIONARY_CANDIDATE"
    elif d08>eps and d016>eps and d816<d08: label="RELAXING_CANDIDATE"
    elif (d08<=eps) != (d016<=eps): label="QUASI_STATIONARY"
    else: label="NONSTATIONARY_OTHER"
    return {"label":label,"d_0_8":d08,"d_0_16":d016,"d_8_16":d816,"epsilon":eps}


def cell_discovery(run: Run, prep: str, age: int, cal: Dict[str, Any], rng: np.random.Generator) -> Dict[str, Any]:
    x=f_cell_matrix(run.work,"DISCOVERY",prep,16,age)
    C=covariance_tensor(x)
    rd=r_cell_data(run.work,"DISCOVERY",prep,16,age)
    resp1, fracs, per1=response_tensor(rd,1)
    resp2, _, per2=response_tensor(rd,2)
    respm, _, perm=response_tensor(rd,-1)
    c_floor=cal["C_noise_floor"]
    cdd=float(C[0,0,0]); css=float(C[1,1,0])
    c_ok=(cdd>float(c_floor["0,0"]) and css>float(c_floor["1,1"]))
    bD=bootstrap_response_nonzero(per1["I_DIRECTION"],0,float(cal["CHI_noise_floor"]["0"]),rng)
    bS=bootstrap_response_nonzero(per1["I_SREG"],1,float(cal["CHI_noise_floor"]["1"]),rng)
    site_ok=min(fracs.values())>=0.85
    eligible=bool(c_ok and site_ok and bD["pass"] and bS["pass"])
    linearity={}
    for bi,(ch,ai) in enumerate((("I_DIRECTION",0),("I_SREG",1))):
        r1=resp1[ai,bi,1:]; r2=resp2[ai,bi,1:]; rm=respm[ai,bi,1:]
        den=max(2.0*float(np.linalg.norm(r1)),1e-300)
        d2=float(np.linalg.norm(r2-2*r1)/den); dm=float(np.linalg.norm(rm+r1)/den)
        linearity[ch]={"D2":d2,"Dminus":dm,"linear_candidate":bool(d2<=0.25 and dm<=0.25)}
    return {
      "id":f"{prep}@{age}","preparation":prep,"age":age,
      "C":C.tolist(),"chi_plus1":resp1.tolist(),"chi_plus2":resp2.tolist(),"chi_minus1":respm.tolist(),
      "site_fractions":fracs,"C0":{"DD":cdd,"SS":css},"C0_resolvable":c_ok,
      "response_nonzero":{"D":bD,"S":bS},"eligible":eligible,"linearity":linearity,
      "stationarity":stationarity_label(x,cal)
    }


def rho_tensor(cell: Dict[str, Any], cal: Dict[str, Any]) -> Tuple[np.ndarray,np.ndarray]:
    C=np.asarray(cell["C"],float)
    p=C.shape[0]; hlen=C.shape[2]
    rho=np.full_like(C,np.nan)
    valid=np.zeros((p,p),dtype=bool)
    floors=cal["C_noise_floor"]
    for a in range(p):
        for b in range(p):
            va=C[a,a,0]; vb=C[b,b,0]
            if va>float(floors[f"{a},{a}"]) and vb>float(floors[f"{b},{b}"]):
                den=math.sqrt(max(va*vb,0.0))
                if den>0:
                    rho[a,b,:]=C[a,b,:]/den; valid[a,b]=True
    return rho,valid


def K_from_rho(rho: np.ndarray, kind: str) -> np.ndarray:
    if kind=="K0": return rho.copy()
    if kind=="K1":
        out=np.full_like(rho,np.nan); out[:,:,1:]=rho[:,:,1:]-rho[:,:,:-1]; return out
    if kind=="K2": return np.cumsum(rho,axis=2)
    raise ValueError(kind)


def build_design(cells: List[Dict[str,Any]], cal: Dict[str,Any], model: str, Kkind: str, train_ids: Sequence[str]) -> Tuple[np.ndarray,np.ndarray,np.ndarray,List[Tuple[str,int,int,int]],float]:
    rows=[]; y=[]; scales=[]; keys=[]
    # parameter mapping fixed by model
    if model=="M1": pcount=2
    elif model=="M2": pcount=8
    elif model=="M3": pcount=24
    elif model=="M0": pcount=0
    else: raise ValueError(model)
    for cell in cells:
        if cell["id"] not in train_ids: continue
        chi=np.asarray(cell["chi_plus1"],float)
        rho,valid=rho_tensor(cell,cal)
        K=K_from_rho(rho,Kkind) if model!="M3" else rho
        C=np.asarray(cell["C"],float)
        for a in range(4):
            scale=max(math.sqrt(max(C[a,a,0],0.0)),1/(48**3))
            for b in range(2):
                for h in range(1,HORIZON+1):
                    yy=float(chi[a,b,h])
                    if not math.isfinite(yy): continue
                    x=np.zeros(pcount,dtype=float)
                    if model=="M0": pass
                    elif model=="M1":
                        if a==0 and b==0:
                            if not valid[0,0] or not math.isfinite(K[0,0,h]): raise ValueError("invalid M1 K DD")
                            x[0]=K[0,0,h]
                        elif a==1 and b==1:
                            if not valid[1,1] or not math.isfinite(K[1,1,h]): raise ValueError("invalid M1 K SS")
                            x[1]=K[1,1,h]
                    elif model=="M2":
                        if not valid[a,b] or not math.isfinite(K[a,b,h]): raise ValueError("invalid M2 K pair")
                        x[a*2+b]=K[a,b,h]
                    elif model=="M3":
                        if not valid[a,b]: raise ValueError("invalid M3 rho pair")
                        base=(a*2+b)*3
                        for u in range(3):
                            hh=h-u
                            x[base+u]=0.0 if hh<0 else float(rho[a,b,hh])
                    rows.append(x); y.append(yy); scales.append(scale); keys.append((cell["id"],a,b,h))
    X=np.vstack(rows) if rows else np.zeros((0,pcount),float)
    Y=np.asarray(y,float); S=np.asarray(scales,float)
    if pcount==0: cond=1.0
    else:
        Xs=X/S[:,None]
        if Xs.shape[0]<pcount or np.linalg.matrix_rank(Xs)<pcount: cond=float("inf")
        else: cond=float(np.linalg.cond(Xs))
    return X,Y,S,keys,cond


def fit_candidate(cells: List[Dict[str,Any]], cal: Dict[str,Any], model: str, Kkind: str, train_ids: Sequence[str]) -> Dict[str,Any]:
    try:
        X,Y,S,keys,cond=build_design(cells,cal,model,Kkind,train_ids)
    except Exception as e:
        return {"valid":False,"reason":str(e),"condition_number":None}
    if cond>1e8:
        return {"valid":False,"reason":"condition_number_or_rank","condition_number":cond}
    if model=="M0": beta=np.zeros(0,float); pred=np.zeros_like(Y)
    else:
        Xs=X/S[:,None]; Ys=Y/S
        beta=np.linalg.lstsq(Xs,Ys,rcond=None)[0]
        pred=X@beta
    resid=(Y-pred)/S
    rmse=float(math.sqrt(np.mean(resid**2))) if len(resid) else float("inf")
    return {"valid":True,"condition_number":cond,"parameters":beta.tolist(),"rmse_standardized":rmse,"n":len(Y)}


def predict_candidate(cells: List[Dict[str,Any]], cal: Dict[str,Any], model: str, Kkind: str, params: Sequence[float], test_ids: Sequence[str]) -> Dict[str,Any]:
    X,Y,S,keys,cond=build_design(cells,cal,model,Kkind,test_ids)
    beta=np.asarray(params,float)
    pred=np.zeros_like(Y) if model=="M0" else X@beta
    resid=(Y-pred)/S
    return {"rmse_standardized":float(math.sqrt(np.mean(resid**2))) if len(resid) else float("inf"),"sse_standardized":float(np.sum(resid**2)),"n":len(Y),"keys":keys,"pred":pred.tolist(),"obs":Y.tolist(),"scales":S.tolist()}


def candidate_registry() -> List[Tuple[str,str,str]]:
    return [
      ("M0","K0","M0"),
      ("M1_K0","K0","M1"),("M1_K1","K1","M1"),("M1_K2","K2","M1"),
      ("M2_K0","K0","M2"),("M2_K1","K1","M2"),("M2_K2","K2","M2"),
      ("M3","K0","M3")
    ]


def discovery_analysis(run: Run, cal: Dict[str,Any]) -> Dict[str,Any]:
    rng=np.random.default_rng(seed_for("DISCOVERY","ANALYSIS","bootstrap","A",0))
    cells=[]
    for prep in PRIMARY_PREPS:
        for age in AGES:
            cells.append(cell_discovery(run,prep,age,cal,rng))
    eligible=[c for c in cells if c["eligible"]]
    fams=set(c["preparation"] for c in eligible); ages=set(c["age"] for c in eligible)
    eligibility_ok=len(eligible)>=3 and len(fams)>=2 and {32,96}.issubset(ages)
    if not eligibility_ok:
        return {"status":"UNINFORMATIVE","reason":"insufficient_eligible_cells","cells":cells,"eligible_cells":[c["id"] for c in eligible],"selection":None}
    ids=[c["id"] for c in eligible]
    results=[]
    complexity={"M0":0,"M1":1,"M2":2,"M3":3}; korder={"K0":0,"K1":1,"K2":2}
    for cname,Kkind,model in candidate_registry():
        fold_scores=[]; invalid=None
        for hold in ids:
            train=[x for x in ids if x!=hold]
            fit=fit_candidate(eligible,cal,model,Kkind,train)
            if not fit["valid"]:
                invalid=fit; break
            test=predict_candidate(eligible,cal,model,Kkind,fit["parameters"],[hold])
            fold_scores.append(test["rmse_standardized"])
        if invalid is not None:
            results.append({"candidate":cname,"model":model,"K":Kkind,"valid":False,"reason":invalid.get("reason"),"condition_number":invalid.get("condition_number")})
            continue
        cv=float(np.mean(fold_scores))
        # cluster bootstrap over state-cell fold scores
        vals=[]; m=len(fold_scores)
        brng=np.random.default_rng(seed_for("DISCOVERY","ANALYSIS",cname,"BOOT",0))
        for _ in range(BOOTSTRAP_B):
            ix=brng.integers(0,m,size=m); vals.append(float(np.mean(np.asarray(fold_scores)[ix])))
        se=float(np.std(vals,ddof=1))
        final=fit_candidate(eligible,cal,model,Kkind,ids)
        results.append({"candidate":cname,"model":model,"K":Kkind,"valid":True,"cv_nrmse":cv,"cv_se":se,"fold_scores":fold_scores,"final_fit":final})
    valid=[r for r in results if r.get("valid")]
    if not valid:
        return {"status":"UNINFORMATIVE","reason":"all_candidates_invalid","cells":cells,"eligible_cells":ids,"candidates":results,"selection":None}
    best=min(valid,key=lambda r:r["cv_nrmse"])
    cutoff=best["cv_nrmse"]+best["cv_se"]
    acceptable=[r for r in valid if r["cv_nrmse"]<=cutoff]
    selected=min(acceptable,key=lambda r:(complexity[r["model"]],korder.get(r["K"],0),r["cv_nrmse"]))
    sel_fit=selected["final_fit"]
    pred=predict_candidate(eligible,cal,selected["model"],selected["K"],sel_fit["parameters"],ids)
    obs=np.asarray(pred["obs"],float); pp=np.asarray(pred["pred"],float); scales=np.asarray(pred["scales"],float)
    res=(obs-pp)/scales
    bias=float(np.mean(res)) if len(res) else 0.0
    corr=float(np.corrcoef(obs,pp)[0,1]) if len(obs)>1 and np.std(obs)>0 and np.std(pp)>0 else 0.0
    residual_lag=[]
    # group residuals by cell,a,b using keys then lag1 over h
    grouped={}
    for key,val in zip(pred["keys"],res): grouped.setdefault(tuple(key[:3]),[]).append((key[3],float(val)))
    for seq in grouped.values():
        seq=sorted(seq); a=np.asarray([v for _,v in seq],float)
        if len(a)>2 and np.std(a[:-1])>0 and np.std(a[1:])>0: residual_lag.append(float(np.corrcoef(a[:-1],a[1:])[0,1]))
    selection={"selected_candidate":selected["candidate"],"selected_model":selected["model"],"selected_K":selected["K"],"parameters":sel_fit["parameters"],"best_raw_candidate":best["candidate"],"one_se_cutoff":cutoff,"acceptable_candidates":[r["candidate"] for r in acceptable],"residual_diagnostics":{"standardized_bias":bias,"correlation_observed_predicted":corr,"mean_abs_lag1_residual_correlation":float(np.mean(np.abs(residual_lag))) if residual_lag else None,"rmse_standardized":pred["rmse_standardized"]}}
    return {"status":"DISCOVERY_MODEL_SELECTED","cells":cells,"eligible_cells":ids,"candidates":results,"selection":selection}


def frozen_lock(run: Run, env: Dict[str,Any], canaries: Dict[str,Any], cal: Dict[str,Any], disc: Dict[str,Any]) -> Dict[str,Any]:
    selection=disc.get("selection")
    return {
      "lock_type":"FROZEN_ANALYSIS_LOCK",
      "campaign":CAMPAIGN,
      "version":VERSION,
      "pre_execution_lock_sha256":PRELOCK_SHA,
      "runner_sha256":run.runner_sha,
      "actual_runtime_identity":env,
      "native_canaries":canaries,
      "calibrated_noise_values":cal,
      "eligible_discovery_cells":disc.get("eligible_cells",[]),
      "selected_K":selection.get("selected_K") if selection else None,
      "selected_model":selection.get("selected_model") if selection else None,
      "selected_candidate":selection.get("selected_candidate") if selection else None,
      "selected_parameters":selection.get("parameters") if selection else None,
      "fit_window":[1,16],
      "h0_policy":"INSTRUMENTATION_ONLY",
      "intercept":False,
      "model_selection_trace":disc.get("candidates",[]),
      "linearity_diagnostics":{c["id"]:c["linearity"] for c in disc.get("cells",[])},
      "stationarity_diagnostics":{c["id"]:c["stationarity"] for c in disc.get("cells",[])},
      "residual_diagnostics":selection.get("residual_diagnostics") if selection else None,
      "holdout_specification":load_json(run.root_dir/"R4_NEW_PREREGISTRATION.json")["holdout_embargoed"],
      "holdout_touched":False,
      "post_lock_policy":"IMMUTABLE; HOLDOUT MUST USE THIS EXACT LOCK WITHOUT REFIT"
    }


def runtime_gate(run: Run) -> Dict[str,Any]:
    st=static_self_tests()
    if not st["all_pass"]:
        raise TechnicalStop("static self-test failed")
    native=Native(run.args.threads,run.args.wheel,run.args.source_cpp)
    run.native=native
    return {"run_mode":"OFFICIAL_WHL_INSTALLED_BINARY","static_self_tests":st,"environment":native.env}


def build_summary(run: Run, gate: Dict[str,Any], canaries: Dict[str,Any], cal: Dict[str,Any], disc: Dict[str,Any], lock_sha: str) -> Dict[str,Any]:
    return {
      "campaign":CAMPAIGN,
      "version":VERSION,
      "RUN_MODE":"OFFICIAL_WHL",
      "EXECUTION_GATE_STATUS":"PASSED",
      "KERNEL_IDENTITY_STATUS":"VERIFIED_PACKAGE_AND_PYD_PLUS_BEHAVIORAL_P_KERNEL_CANARY",
      "CANARY_STATUS":"PASS",
      "PRE_EXECUTION_LOCK_SHA256":PRELOCK_SHA,
      "DISCOVERY_EXECUTED":True,
      "HOLDOUT_TOUCHED":False,
      "calibration_result":cal,
      "eligible_cells":disc.get("eligible_cells",[]),
      "selected_K":disc.get("selection",{}).get("selected_K") if disc.get("selection") else None,
      "selected_M":disc.get("selection",{}).get("selected_model") if disc.get("selection") else None,
      "all_cv_scores":[{"candidate":r.get("candidate"),"valid":r.get("valid"),"cv_nrmse":r.get("cv_nrmse"),"cv_se":r.get("cv_se"),"reason":r.get("reason")} for r in disc.get("candidates",[])],
      "linearity":{c["id"]:c["linearity"] for c in disc.get("cells",[])},
      "residual_diagnostics":disc.get("selection",{}).get("residual_diagnostics") if disc.get("selection") else None,
      "discovery_status":disc.get("status"),
      "FROZEN_ANALYSIS_LOCK_SHA256":lock_sha,
      "next_block":"R4_NEW_FRESH_HOLDOUT",
      "native_steps_this_invocation":run.native_steps,
    }


def parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(description="DEE R4-NEW discovery-only runner. HOLDOUT IS EMBARGOED.")
    p.add_argument("--threads",type=int,default=4)
    p.add_argument("--hours",type=float,default=24.0)
    p.add_argument("--workdir",default="")
    p.add_argument("--output",default="")
    p.add_argument("--wheel",default="",help="Optional path to canonical wheel bytes for SHA verification")
    p.add_argument("--source-cpp",default="",help="Optional path to exact canonical dee_kernel_v27.cpp for SHA verification")
    p.add_argument("--max-disk-gb",type=float,default=12.0)
    p.add_argument("--unlock",action="store_true")
    p.add_argument("--self-test",action="store_true")
    return p


def main() -> None:
    args=parser().parse_args()
    if args.self_test:
        print(json.dumps(clean(static_self_tests()),indent=2,sort_keys=True))
        return
    run=Run(args)
    try:
        run.set_status(status="runtime_gate")
        gate=run.module("RUNTIME_GATE",lambda:runtime_gate(run))
        if run.native is None:
            # module may have been loaded from checkpoint; restore native now
            run.native=Native(args.threads,args.wheel,args.source_cpp)
        run.set_status(status="native_canaries")
        canaries=run.module("NATIVE_CANARIES",lambda:native_canaries(run))
        run.set_status(status="calibration")
        run.module("CALIBRATION_DATASET",lambda:collect_calibration(run))
        cal=run.module("CALIBRATION_ANALYSIS",lambda:calibration_analysis(run))
        run.set_status(status="discovery")
        run.module("DISCOVERY_DATASET",lambda:collect_discovery(run))
        disc=run.module("DISCOVERY_ANALYSIS",lambda:discovery_analysis(run,cal))
        lock=frozen_lock(run,gate["environment"],canaries,cal,disc)
        lock_path=run.work/"FROZEN_ANALYSIS_LOCK.json"
        if lock_path.exists():
            existing=load_json(lock_path)
            if existing!=clean(lock):
                raise TechnicalStop("existing frozen lock differs from recomputed lock")
        else:
            atomic_json(lock_path,lock)
        lock_sha=sha_file(lock_path)
        atomic_text(run.work/"FROZEN_ANALYSIS_LOCK.sha256",lock_sha+"  FROZEN_ANALYSIS_LOCK.json\n")
        summary=build_summary(run,gate,canaries,cal,disc,lock_sha)
        run.set_status(status="completed_discovery_locked",holdout_touched=False,frozen_analysis_lock_sha256=lock_sha)
        out=run.finalize_zip(summary)
        print(json.dumps({"status":"completed_discovery_locked","official_zip":str(out),"frozen_analysis_lock_sha256":lock_sha,"holdout_touched":False},indent=2))
    except Paused as e:
        run.set_status(status="PAUSED",pause_reason=str(e),holdout_touched=False)
        print("PAUSED. No official ZIP exists until completion. Repeat the exact command with the same runner and workdir.")
    except Exception as e:
        run.set_status(status="FAILED_TECHNICAL",error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc(),holdout_touched=False)
        raise
    finally:
        run.release()


if __name__=="__main__":
    main()
