#!/usr/bin/env python3
"""Shared, hash-pinned runtime and evidence helpers for CORE17."""
from __future__ import annotations

import hashlib
import importlib
import json
import os
import platform
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TESTS = ROOT.parent
OFFICIAL_CORE = TESTS / "EXPEDIENTE_EXPERIMENTOS_DEE" / "CORE"
EXTRACTED = TESTS / "DEE_CODEX_NATIVE_DISCOVERY_AND_CLOSURE_V1_WORK" / "ANALYSIS" / "binary_api" / "wheel_extracted"
PACKAGE_FILE = EXTRACTED / "dee_universe_v27" / "__init__.py"
KERNEL_FILE = EXTRACTED / "dee_universe_v27" / "dee_kernel_v27.cp313-win_amd64.pyd"
WHEEL_FILE = TESTS / "dee_universe_v27-27.0.0-cp313-cp313-win_amd64.whl"

EXPECTED = {
    "wheel": "69297e6f06761c8b2f65d24a3fd7a2f16a3f67595a7f9660739ab65f47abc939",
    "package": "7e2991b1fc8a053ee44ead6e177b129855ae9265dea68505a8e545f0c3fdf8b4",
    "kernel": "0b17ba32037935a255b0f2182a52137bceab424f7e09126b761076b63e42c6ff",
}

STATE_MASK = np.uint64((1 << 32) - 1)
SREG_MASK = np.uint64(0xFFFF)
SEM_MASK = np.uint64(0xF)
P_KERNEL = 19665


def utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def sha256_array(value: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(value).view(np.uint8)).hexdigest()


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def append_ndjson(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def fresh_seed() -> int:
    return int.from_bytes(secrets.token_bytes(8), "little") & ((1 << 63) - 1)


def pack(state: int, sreg: int, direction: tuple[int, int, int], semantic: int = 1) -> np.uint64:
    return np.uint64(
        (int(state) & 0xFFFFFFFF)
        | ((int(sreg) & 0xFFFF) << 32)
        | ((int(direction[0]) & 0xF) << 48)
        | ((int(direction[1]) & 0xF) << 52)
        | ((int(direction[2]) & 0xF) << 56)
        | ((int(semantic) & 0xF) << 60)
    )


def signed4(value: int) -> int:
    value &= 0xF
    return value - 16 if value >= 8 else value


def unpack(value: int) -> dict:
    value = int(value)
    return {
        "state": value & 0xFFFFFFFF,
        "sreg": (value >> 32) & 0xFFFF,
        "direction": [signed4(value >> 48), signed4(value >> 52), signed4(value >> 56)],
        "semantic": (value >> 60) & 0xF,
    }


def fields(raw: np.ndarray) -> dict[str, np.ndarray]:
    def signed(shift: int) -> np.ndarray:
        x = ((raw >> np.uint64(shift)) & np.uint64(0xF)).astype(np.int16)
        return np.where(x >= 8, x - 16, x)
    return {
        "state": (raw & STATE_MASK).astype(np.uint32),
        "sreg": ((raw >> np.uint64(32)) & SREG_MASK).astype(np.uint16),
        "dx": signed(48), "dy": signed(52), "dz": signed(56),
        "semantic": ((raw >> np.uint64(60)) & SEM_MASK).astype(np.uint8),
    }


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
        "python": sys.version,
        "numpy": np.__version__,
        "platform": platform.platform(),
        "threads": int(threads),
        "wheel_path": str(WHEEL_FILE),
        "package_path": str(PACKAGE_FILE),
        "kernel_path": str(KERNEL_FILE),
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
        return {str(k): v for k, v in info.items()}

    def inject(self, q: tuple[int, int, int], value: int, clock_value: int = 0) -> None:
        q = tuple(int(x) % self.n for x in q)
        self.raw_a[q] = np.uint64(value)
        self.raw_b[q] = np.uint64(value)
        self.clock_a[q] = np.uint64(clock_value)
        self.clock_b[q] = np.uint64(clock_value)


def audit_kernel(stage: str) -> dict:
    _, environment = verify_and_load_kernel(1)
    record = {"stage": stage, "utc": utc(), "observed": environment["observed_hashes"], "pass": True}
    path = ROOT / "KERNEL_IMMUTABILITY_AUDIT.json"
    ledger = read_json(path) if path.exists() else {"expected": EXPECTED, "checks": [], "all_pass": True}
    ledger["checks"].append(record)
    ledger["all_pass"] = all(x["pass"] for x in ledger["checks"])
    write_json(path, ledger)
    return record
