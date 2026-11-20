#!/usr/bin/env python3
"""Pinned DEE v27 runtime and evidence helpers for INGENIERIA 02."""
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


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TESTS = ROOT.parents[2]
EXPEDIENTE = ROOT.parents[1]
CORE_DIR = EXPEDIENTE / "CORE"
ENGINEERING_DIR = ROOT.parent
ING01_DIR = ENGINEERING_DIR / "INGENIERIA_01"

EXPECTED = {
    "wheel": "69297e6f06761c8b2f65d24a3fd7a2f16a3f67595a7f9660739ab65f47abc939",
    "package": "7e2991b1fc8a053ee44ead6e177b129855ae9265dea68505a8e545f0c3fdf8b4",
    "kernel": "0b17ba32037935a255b0f2182a52137bceab424f7e09126b761076b63e42c6ff",
}
STATE_MASK = np.uint64((1 << 32) - 1)
SREG_MASK = np.uint64(0xFFFF)
SEM_MASK = np.uint64(0xF)


def utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path | str) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def seal(value: dict) -> dict:
    value = dict(value)
    value.setdefault("created_utc", utc())
    value["content_sha256"] = canonical_hash(value)
    return value


def write_json(path: Path | str, value: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def append_ndjson(path: Path | str, value: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {"created_utc": utc(), **value}
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")


def _candidate_roots():
    env = os.environ.get("DEE_V27_TESTS_ROOT")
    if env:
        yield Path(env)
    yield TESTS
    for parent in Path(__file__).resolve().parents:
        yield parent


def load_kernel(threads: int = 1):
    if sys.version_info[:2] != (3, 13):
        raise RuntimeError(f"DEE v27 requires CPython 3.13; observed {sys.version}")
    for candidate in _candidate_roots():
        extracted = candidate / "DEE_CODEX_NATIVE_DISCOVERY_AND_CLOSURE_V1_WORK" / "ANALYSIS" / "binary_api" / "wheel_extracted"
        if (extracted / "dee_universe_v27" / "dee_kernel_v27.cp313-win_amd64.pyd").exists():
            sys.path.insert(0, str(extracted))
            break
    importlib.invalidate_caches()
    import dee_universe_v27 as package
    from dee_universe_v27 import dee_kernel_v27 as kernel

    package_path = Path(package.__file__).resolve()
    kernel_path = Path(kernel.__file__).resolve()
    observed = {"package": sha256_file(package_path), "kernel": sha256_file(kernel_path), "wheel": None}
    for candidate in _candidate_roots():
        wheel = candidate / "dee_universe_v27-27.0.0-cp313-cp313-win_amd64.whl"
        if wheel.exists():
            observed["wheel"] = sha256_file(wheel)
            break
    if observed["package"] != EXPECTED["package"] or observed["kernel"] != EXPECTED["kernel"]:
        raise RuntimeError(f"sealed identity mismatch: {observed}")
    if observed["wheel"] is not None and observed["wheel"] != EXPECTED["wheel"]:
        raise RuntimeError(f"wheel identity mismatch: {observed['wheel']}")
    runtime = {
        "observed_hashes": observed,
        "python": sys.version,
        "numpy": np.__version__,
        "platform": platform.platform(),
        "threads": int(threads),
        "package_path": str(package_path),
        "kernel_path": str(kernel_path),
    }
    return kernel, runtime


def pack(state: int, sreg: int, direction: tuple[int, int, int], semantic: int = 1) -> np.uint64:
    return np.uint64(
        (int(state) & 0xFFFFFFFF)
        | ((int(sreg) & 0xFFFF) << 32)
        | ((int(direction[0]) & 0xF) << 48)
        | ((int(direction[1]) & 0xF) << 52)
        | ((int(direction[2]) & 0xF) << 56)
        | ((int(semantic) & 0xF) << 60)
    )


def signed_nibble(raw, shift: int):
    value = (np.asarray(raw, dtype=np.uint64) >> np.uint64(shift)) & np.uint64(0xF)
    value = value.astype(np.int16)
    return np.where(value >= 8, value - 16, value)


def fields(raw: np.ndarray) -> dict:
    return {
        "state": (raw & STATE_MASK).astype(np.uint32),
        "sreg": ((raw >> np.uint64(32)) & SREG_MASK).astype(np.uint16),
        "dx": signed_nibble(raw, 48),
        "dy": signed_nibble(raw, 52),
        "dz": signed_nibble(raw, 56),
        "semantic": ((raw >> np.uint64(60)) & SEM_MASK).astype(np.uint8),
    }


def unpack_scalar(raw) -> dict:
    value = np.uint64(raw)
    return {
        "raw": int(value),
        "state": int(value & STATE_MASK),
        "sreg": int((value >> np.uint64(32)) & SREG_MASK),
        "direction": [int(signed_nibble(value, shift)) for shift in (48, 52, 56)],
        "semantic": int((value >> np.uint64(60)) & SEM_MASK),
    }


def add(q: tuple[int, int, int], d: tuple[int, int, int], k: int, n: int) -> tuple[int, int, int]:
    return tuple((int(q[i]) + int(k) * int(d[i])) % int(n) for i in range(3))


def neg(direction: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(-int(x) for x in direction)


def transform(vector, permutation=(0, 1, 2), signs=(1, 1, 1)):
    return tuple(int(signs[i]) * int(vector[permutation[i]]) for i in range(3))


def read(raw: np.ndarray, q: tuple[int, int, int]):
    return unpack_scalar(raw[q]) if int(raw[q]) else None


def raw_sha(raw: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(raw).tobytes()).hexdigest()


def full_sha(raw: np.ndarray, clock: np.ndarray) -> str:
    h = hashlib.sha256()
    h.update(np.ascontiguousarray(raw).tobytes())
    h.update(np.ascontiguousarray(clock).tobytes())
    return h.hexdigest()


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
    def raw(self):
        return self.raw_a

    def tick(self) -> dict:
        return {
            str(key): value
            for key, value in dict(
                self.kernel.tick_universo_lazy(
                    self.raw_a,
                    self.raw_b,
                    self.clock_a,
                    self.clock_b,
                    self.n,
                    self.threads,
                )
            ).items()
        }

    def inject(self, q, value, clock=0) -> None:
        q = tuple(int(x) % self.n for x in q)
        self.raw_a[q] = np.uint64(value)
        self.raw_b[q] = np.uint64(value)
        self.clock_a[q] = np.uint64(clock)
        self.clock_b[q] = np.uint64(clock)

    def clear(self, q) -> None:
        self.inject(q, np.uint64(0), 0)


def place_arrival(raw, clock, target, tick, direction, state, sreg, semantic=1):
    source = add(target, direction, -int(tick), raw.shape[0])
    if int(raw[source]):
        raise RuntimeError(f"initial trajectory collision at {source}")
    raw[source] = pack(state, sreg, direction, semantic)
    clock[source] = np.uint64(0)
    return source


def summarize(raw: np.ndarray, clock: np.ndarray | None = None) -> dict:
    parsed = fields(raw)
    result = {
        "support": int(np.count_nonzero(raw)),
        "raw_sha256": raw_sha(raw),
        "state_sum": int(parsed["state"].astype(np.uint64).sum()),
        "sreg_sum": int(parsed["sreg"].astype(np.uint64).sum()),
        "semantic_counts": {
            str(i): int(np.sum(parsed["semantic"] == i)) for i in range(16) if np.any(parsed["semantic"] == i)
        },
    }
    if clock is not None:
        result["full_sha256"] = full_sha(raw, clock)
    return result
