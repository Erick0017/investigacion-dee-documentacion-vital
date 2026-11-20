"""Hash-pinned, atomic helpers for DEE v27 CORE08."""
from __future__ import annotations

import hashlib
import importlib
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT.parent
KERNEL_ROOT = ROOT / "KERNEL"
EXTRACTED = KERNEL_ROOT / "wheel_extracted"
PACKAGE_FILE = EXTRACTED / "dee_universe_v27" / "__init__.py"
KERNEL_FILE = EXTRACTED / "dee_universe_v27" / "dee_kernel_v27.cp313-win_amd64.pyd"
WHEEL_FILE = KERNEL_ROOT / "dee_universe_v27-27.0.0-cp313-cp313-win_amd64.whl"
EXPECTED = {
    "wheel": "69297e6f06761c8b2f65d24a3fd7a2f16a3f67595a7f9660739ab65f47abc939",
    "package": "7e2991b1fc8a053ee44ead6e177b129855ae9265dea68505a8e545f0c3fdf8b4",
    "kernel": "0b17ba32037935a255b0f2182a52137bceab424f7e09126b761076b63e42c6ff",
}

STATE_MASK = np.uint64((1 << 32) - 1)
SREG_MASK = np.uint64(0xFFFF)
SEM_MASK = np.uint64(0xF)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(value)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def append_log(event: dict) -> None:
    row = {"timestamp_utc": utc_now(), **event}
    with (ROOT / "SCIENCE_LOG.ndjson").open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(row, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def update_state(**updates) -> None:
    path = ROOT / "STATE.json"
    state = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    state.update(updates)
    state["timestamp_utc"] = utc_now()
    atomic_json(path, state)


def verify_and_load_kernel(threads: int = 1):
    if sys.version_info[:2] != (3, 13):
        raise RuntimeError(f"DEE v27 requires CPython 3.13; observed {sys.version}")
    observed = {
        "wheel": sha256_file(WHEEL_FILE),
        "package": sha256_file(PACKAGE_FILE),
        "kernel": sha256_file(KERNEL_FILE),
    }
    if observed != EXPECTED:
        raise RuntimeError(f"sealed identity mismatch: {observed}")
    sys.path.insert(0, str(EXTRACTED))
    importlib.invalidate_caches()
    import dee_universe_v27 as package
    from dee_universe_v27 import dee_kernel_v27 as kernel
    if Path(package.__file__).resolve() != PACKAGE_FILE.resolve():
        raise RuntimeError(f"wrong package imported: {package.__file__}")
    if Path(kernel.__file__).resolve() != KERNEL_FILE.resolve():
        raise RuntimeError(f"wrong binary imported: {kernel.__file__}")
    return kernel, {
        "observed_hashes": observed,
        "wheel_path": str(WHEEL_FILE),
        "package_path": str(PACKAGE_FILE),
        "kernel_path": str(KERNEL_FILE),
        "python": sys.version,
        "numpy": np.__version__,
        "platform": platform.platform(),
        "threads": int(threads),
    }


def pack(state: int, sreg: int, direction: tuple[int, int, int], semantic: int = 1) -> np.uint64:
    return np.uint64(
        (state & 0xFFFFFFFF)
        | ((sreg & 0xFFFF) << 32)
        | ((direction[0] & 0xF) << 48)
        | ((direction[1] & 0xF) << 52)
        | ((direction[2] & 0xF) << 56)
        | ((semantic & 0xF) << 60)
    )


def signed_nibble(raw: np.ndarray | np.uint64 | int, shift: int):
    value = (np.asarray(raw, dtype=np.uint64) >> np.uint64(shift)) & np.uint64(0xF)
    value = value.astype(np.int16)
    return np.where(value >= 8, value - 16, value)


def unpack_scalar(raw: np.uint64 | int) -> dict:
    value = np.uint64(raw)
    return {
        "raw": int(value),
        "state": int(value & STATE_MASK),
        "s_reg": int((value >> np.uint64(32)) & SREG_MASK),
        "direction": [int(signed_nibble(value, shift)) for shift in (48, 52, 56)],
        "semantic": int((value >> np.uint64(60)) & SEM_MASK),
    }


def fields(raw: np.ndarray) -> dict[str, np.ndarray]:
    return {
        "state": (raw & STATE_MASK).astype(np.uint32),
        "sreg": ((raw >> np.uint64(32)) & SREG_MASK).astype(np.uint16),
        "dx": signed_nibble(raw, 48),
        "dy": signed_nibble(raw, 52),
        "dz": signed_nibble(raw, 56),
        "semantic": ((raw >> np.uint64(60)) & SEM_MASK).astype(np.uint8),
    }


class NativeWorld:
    def __init__(self, kernel, raw: np.ndarray, clock: np.ndarray | None = None, threads: int = 1):
        if raw.ndim != 3 or len(set(raw.shape)) != 1:
            raise ValueError("raw must be cubic")
        if clock is None:
            clock = np.zeros_like(raw, dtype=np.uint64)
        if raw.shape != clock.shape:
            raise ValueError("raw and clock shapes differ")
        self.kernel = kernel
        self.n = int(raw.shape[0])
        self.threads = int(threads)
        self.raw_a = np.ascontiguousarray(raw, dtype=np.uint64).copy()
        self.raw_b = self.raw_a.copy()
        self.clock_a = np.ascontiguousarray(clock, dtype=np.uint64).copy()
        self.clock_b = self.clock_a.copy()
        self.tick_index = 0

    @property
    def raw(self) -> np.ndarray:
        return self.raw_a

    @property
    def clock(self) -> np.ndarray:
        return self.clock_a

    def tick(self) -> dict:
        info = dict(self.kernel.tick_universo_lazy(
            self.raw_a, self.raw_b, self.clock_a, self.clock_b, self.n, self.threads
        ))
        self.tick_index += 1
        return {str(key): value for key, value in info.items()}

    def set_raw(self, coordinate: tuple[int, int, int], value: np.uint64 | int) -> None:
        self.raw_a[coordinate] = np.uint64(value)

