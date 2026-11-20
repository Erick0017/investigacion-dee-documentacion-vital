"""Sealed DEE v27 helpers and atomic CORE12 persistence."""
from __future__ import annotations

import hashlib
import importlib
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT.parent
EXTRACTED = ROOT / "KERNEL" / "wheel_extracted"
WHEEL_FILE = ROOT / "KERNEL" / "dee_universe_v27-27.0.0-cp313-cp313-win_amd64.whl"
PACKAGE_FILE = EXTRACTED / "dee_universe_v27" / "__init__.py"
KERNEL_FILE = EXTRACTED / "dee_universe_v27" / "dee_kernel_v27.cp313-win_amd64.pyd"
EXPECTED = {
    "wheel": "69297e6f06761c8b2f65d24a3fd7a2f16a3f67595a7f9660739ab65f47abc939",
    "package": "7e2991b1fc8a053ee44ead6e177b129855ae9265dea68505a8e545f0c3fdf8b4",
    "kernel": "0b17ba32037935a255b0f2182a52137bceab424f7e09126b761076b63e42c6ff",
}
PARENT_HASHES = {
    "CORE01": "06c9721e11efbb8907d0283633ae7a08b5f58c424c7342ed0465a3fe266de1e4",
    "CORE02": "4c29c9530c80f21c5e3af03ff5b3ff79d36367ba8480bb137ae7a3ec84b76058",
    "CORE03": "553bba71dc21929443e6032801607d90a7b3d7ced5c45f1078295338efb16640",
    "CORE04": "48dc7452e72c6372b526bf271112d5826386e5fe9bfde9218258fd9e297fd3d2",
    "CORE05": "aeb4c45ddba43a3bfefe54da5177823ced28e4fc233363a3b0f4f8411a7bcd8b",
    "CORE06": "3f81b016b0f1d5a1bb0b9a7e43807ba68e81eb0120fab0a2a32b4d1081ecef6e",
    "CORE07": "707a83c9c23d891152e2ecbe92673a72aec58ab2242d152537d35ba62fcfad4f",
    "CORE08": "275d3e665c0d0c97c3da80ee487819078fc55dbca24bd4e40c7dafa5b5e7a5fc",
    "CORE09": "70ef26424a11ae907e39a4a25f9dfe4864ed0d11a7ae33cfc22f395238091d96",
    "CORE10": "2fedd8aa7a488584ed15ab8e8e86a4bd892c97914e7153945cc7fe019a87b515",
    "CORE11": "c8b591c5eb4e90a5de947da992337434be98802c024c860991ba8d967d9fb885",
}
STATE_MASK = np.uint64((1 << 32) - 1)
SREG_MASK = np.uint64(0xFFFF)
SEM_MASK = np.uint64(0xF)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def json_native(value):
    if isinstance(value, dict):
        return {str(k): json_native(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_native(v) for v in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(json_native(value), stream, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


def atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(value)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


def append_ndjson(path: Path, row: dict) -> None:
    prior = path.read_text(encoding="utf-8") if path.exists() else ""
    atomic_text(path, prior + json.dumps(json_native(row), separators=(",", ":"), ensure_ascii=False) + "\n")


def append_log(event: dict) -> None:
    append_ndjson(ROOT / "SCIENCE_LOG.ndjson", {"timestamp_utc": utc_now(), **event})


def question(row: dict) -> None:
    append_ndjson(ROOT / "QUESTION_TREE.ndjson", {"timestamp_utc": utc_now(), **row})


def dialogue(row: dict) -> None:
    append_ndjson(ROOT / "KERNEL_DIALOGUE.ndjson", {"timestamp_utc": utc_now(), **row})


def update_state(**updates) -> None:
    path = ROOT / "STATE.json"
    state = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    state.update(json_native(updates))
    state["timestamp_utc"] = utc_now()
    atomic_json(path, state)


def kernel_hashes() -> dict:
    return {"wheel": sha256_file(WHEEL_FILE), "package": sha256_file(PACKAGE_FILE), "kernel": sha256_file(KERNEL_FILE)}


def verify_and_load_kernel(threads: int = 1):
    if sys.version_info[:2] != (3, 13):
        raise RuntimeError(f"DEE v27 requires CPython 3.13; observed {sys.version}")
    observed = kernel_hashes()
    if observed != EXPECTED:
        raise RuntimeError(f"sealed identity mismatch: {observed}")
    sys.path.insert(0, str(EXTRACTED))
    importlib.invalidate_caches()
    import dee_universe_v27 as package
    from dee_universe_v27 import dee_kernel_v27 as kernel
    if Path(package.__file__).resolve() != PACKAGE_FILE.resolve() or Path(kernel.__file__).resolve() != KERNEL_FILE.resolve():
        raise RuntimeError("wrong DEE installation imported")
    return kernel, {"observed_hashes": observed, "python": sys.version, "numpy": np.__version__, "platform": platform.platform(), "threads": int(threads)}


def update_kernel_audit(stage: str) -> None:
    path = ROOT / "KERNEL_IMMUTABILITY_AUDIT.json"
    audit = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"expected": EXPECTED, "checks": []}
    observed = kernel_hashes()
    passed = observed == EXPECTED
    audit["checks"].append({"stage": stage, "timestamp_utc": utc_now(), "observed": observed, "pass": passed})
    audit["all_pass"] = all(row["pass"] for row in audit["checks"])
    atomic_json(path, audit)
    if not passed:
        raise RuntimeError(f"kernel immutability failure at {stage}: {observed}")


def update_budget(module: str, estimated_seconds: float, decision: str) -> dict:
    path = ROOT / "TIME_BUDGET.json"
    budget = json.loads(path.read_text(encoding="utf-8"))
    elapsed = max(0.0, time.time() - float(budget["start_epoch_utc"]))
    budget.update({
        "last_update_utc": utc_now(),
        "elapsed_seconds": round(elapsed, 3),
        "remaining_seconds": round(max(0.0, budget["hard_wall_seconds"] - elapsed), 3),
        "estimated_next_module_seconds": estimated_seconds,
        "next_module": module,
        "decision_to_run_or_skip": decision,
    })
    atomic_json(path, budget)
    return budget


def pack(state: int, sreg: int, direction: tuple[int, int, int], semantic: int = 1) -> np.uint64:
    return np.uint64((state & 0xFFFFFFFF) | ((sreg & 0xFFFF) << 32) | ((direction[0] & 0xF) << 48) | ((direction[1] & 0xF) << 52) | ((direction[2] & 0xF) << 56) | ((semantic & 0xF) << 60))


def signed_nibble(raw, shift: int):
    value = (np.asarray(raw, dtype=np.uint64) >> np.uint64(shift)) & np.uint64(0xF)
    value = value.astype(np.int16)
    return np.where(value >= 8, value - 16, value)


def fields(raw: np.ndarray) -> dict[str, np.ndarray]:
    return {
        "state": (raw & STATE_MASK).astype(np.uint32),
        "sreg": ((raw >> np.uint64(32)) & SREG_MASK).astype(np.uint16),
        "dx": signed_nibble(raw, 48), "dy": signed_nibble(raw, 52), "dz": signed_nibble(raw, 56),
        "semantic": ((raw >> np.uint64(60)) & SEM_MASK).astype(np.uint8),
    }


def unpack_scalar(raw) -> dict:
    value = np.uint64(raw)
    return {
        "raw": int(value), "state": int(value & STATE_MASK),
        "sreg": int((value >> np.uint64(32)) & SREG_MASK),
        "direction": [int(signed_nibble(value, shift)) for shift in (48, 52, 56)],
        "semantic": int((value >> np.uint64(60)) & SEM_MASK),
    }


class NativeWorld:
    def __init__(self, kernel, raw: np.ndarray, clock: np.ndarray | None = None, threads: int = 1):
        self.kernel = kernel
        self.n = int(raw.shape[0])
        self.threads = int(threads)
        self.raw_a = np.ascontiguousarray(raw, dtype=np.uint64).copy()
        self.raw_b = self.raw_a.copy()
        base = np.zeros_like(raw, dtype=np.uint64) if clock is None else clock
        self.clock_a = np.ascontiguousarray(base, dtype=np.uint64).copy()
        self.clock_b = self.clock_a.copy()

    @property
    def raw(self): return self.raw_a

    @property
    def clock(self): return self.clock_a

    def tick(self) -> dict:
        return {str(k): json_native(v) for k, v in dict(self.kernel.tick_universo_lazy(self.raw_a, self.raw_b, self.clock_a, self.clock_b, self.n, self.threads)).items()}
