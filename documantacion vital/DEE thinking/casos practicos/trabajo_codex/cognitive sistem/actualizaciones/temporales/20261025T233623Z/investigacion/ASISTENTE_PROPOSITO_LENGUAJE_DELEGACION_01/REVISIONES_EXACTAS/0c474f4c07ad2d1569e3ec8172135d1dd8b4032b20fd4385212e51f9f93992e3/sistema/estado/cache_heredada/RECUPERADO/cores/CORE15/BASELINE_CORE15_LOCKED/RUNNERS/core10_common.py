"""Atomic persistence and sealed DEE v27 helpers for CORE10."""
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
EXTRACTED = ROOT / "KERNEL" / "wheel_extracted"
WHEEL_FILE = ROOT / "KERNEL" / "dee_universe_v27-27.0.0-cp313-cp313-win_amd64.whl"
PACKAGE_FILE = EXTRACTED / "dee_universe_v27" / "__init__.py"
KERNEL_FILE = EXTRACTED / "dee_universe_v27" / "dee_kernel_v27.cp313-win_amd64.pyd"
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


def json_native(value):
    if isinstance(value, dict): return {key: json_native(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)): return [json_native(item) for item in value]
    if isinstance(value, np.generic): return value.item()
    return value


def atomic_json(path: Path, value: object) -> None:
    value = json_native(value); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)


def atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(value); stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)


def append_ndjson(path: Path, value: dict) -> None:
    prior = path.read_text(encoding="utf-8") if path.exists() else ""
    atomic_text(path, prior + json.dumps(json_native(value), separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n")


def append_log(event: dict) -> None:
    append_ndjson(ROOT / "SCIENCE_LOG.ndjson", {"timestamp_utc": utc_now(), **event})


def dialogue(question: str, experiment: str, response: object, interpretation: str, alternatives: list[str], next_question: str, confidence: str, evidence_level: str) -> None:
    append_ndjson(ROOT / "KERNEL_DIALOGUE.ndjson", {"timestamp_utc": utc_now(), "question": question, "experiment": experiment, "kernel_response": response, "interpretation": interpretation, "alternatives": alternatives, "next_question": next_question, "confidence": confidence, "evidence_level": evidence_level})


def question(row: dict) -> None:
    append_ndjson(ROOT / "QUESTION_TREE.ndjson", {"timestamp_utc": utc_now(), **row})


def update_state(**updates) -> None:
    path = ROOT / "STATE.json"; state = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    state.update(json_native(updates)); state["timestamp_utc"] = utc_now(); atomic_json(path, state)


def verify_and_load_kernel(threads: int = 1):
    if sys.version_info[:2] != (3, 13): raise RuntimeError(f"DEE v27 requires CPython 3.13; observed {sys.version}")
    observed = {"wheel": sha256_file(WHEEL_FILE), "package": sha256_file(PACKAGE_FILE), "kernel": sha256_file(KERNEL_FILE)}
    if observed != EXPECTED: raise RuntimeError(f"sealed identity mismatch: {observed}")
    sys.path.insert(0, str(EXTRACTED)); importlib.invalidate_caches()
    import dee_universe_v27 as package
    from dee_universe_v27 import dee_kernel_v27 as kernel
    if Path(package.__file__).resolve() != PACKAGE_FILE.resolve() or Path(kernel.__file__).resolve() != KERNEL_FILE.resolve(): raise RuntimeError("wrong DEE installation imported")
    return kernel, {"observed_hashes": observed, "python": sys.version, "numpy": np.__version__, "platform": platform.platform(), "threads": int(threads)}


def pack(state: int, sreg: int, direction: tuple[int, int, int], semantic: int = 1) -> np.uint64:
    return np.uint64((state & 0xFFFFFFFF) | ((sreg & 0xFFFF) << 32) | ((direction[0] & 0xF) << 48) | ((direction[1] & 0xF) << 52) | ((direction[2] & 0xF) << 56) | ((semantic & 0xF) << 60))


def signed_nibble(raw, shift: int):
    value = (np.asarray(raw, dtype=np.uint64) >> np.uint64(shift)) & np.uint64(0xF); value = value.astype(np.int16)
    return np.where(value >= 8, value - 16, value)


def fields(raw: np.ndarray) -> dict[str, np.ndarray]:
    return {"state": (raw & STATE_MASK).astype(np.uint32), "sreg": ((raw >> np.uint64(32)) & SREG_MASK).astype(np.uint16), "dx": signed_nibble(raw, 48), "dy": signed_nibble(raw, 52), "dz": signed_nibble(raw, 56), "semantic": ((raw >> np.uint64(60)) & SEM_MASK).astype(np.uint8)}


def unpack_scalar(raw) -> dict:
    value = np.uint64(raw)
    return {"raw": int(value), "state": int(value & STATE_MASK), "sreg": int((value >> np.uint64(32)) & SREG_MASK), "direction": [int(signed_nibble(value, shift)) for shift in (48, 52, 56)], "semantic": int((value >> np.uint64(60)) & SEM_MASK)}


class NativeWorld:
    def __init__(self, kernel, raw: np.ndarray, clock: np.ndarray | None = None, threads: int = 1):
        self.kernel = kernel; self.n = int(raw.shape[0]); self.threads = int(threads)
        self.raw_a = np.ascontiguousarray(raw, dtype=np.uint64).copy(); self.raw_b = self.raw_a.copy()
        base_clock = np.zeros_like(raw, dtype=np.uint64) if clock is None else clock
        self.clock_a = np.ascontiguousarray(base_clock, dtype=np.uint64).copy(); self.clock_b = self.clock_a.copy()
    @property
    def raw(self): return self.raw_a
    def tick(self) -> dict: return {str(k): v for k, v in dict(self.kernel.tick_universo_lazy(self.raw_a, self.raw_b, self.clock_a, self.clock_b, self.n, self.threads)).items()}
    def inject(self, coordinate: tuple[int, int, int], value: int | np.uint64, clock: int = 0) -> None:
        if int(self.raw_a[coordinate]): raise RuntimeError(f"occupied injection port {coordinate}")
        self.raw_a[coordinate] = np.uint64(value); self.raw_b[coordinate] = np.uint64(value); self.clock_a[coordinate] = np.uint64(clock); self.clock_b[coordinate] = np.uint64(clock)
