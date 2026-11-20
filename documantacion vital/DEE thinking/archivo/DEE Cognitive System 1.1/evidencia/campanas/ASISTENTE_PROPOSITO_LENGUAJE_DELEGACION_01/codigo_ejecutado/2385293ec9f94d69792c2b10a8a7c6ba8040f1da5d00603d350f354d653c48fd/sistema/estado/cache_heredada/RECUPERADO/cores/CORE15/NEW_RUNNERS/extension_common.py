#!/usr/bin/env python3
"""Shared atomic persistence and provenance helpers for the CORE15 expansion."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT.parent
ARCHIVE = TESTS / "EXPEDIENTE_EXPERIMENTOS_DEE" / "CORE"
BASELINE_WORK = TESTS / "DEE_V27_CORE15_OBSERVER_SHADOW_MULTIPHYSICS_WORK"
OFFICIAL_NAME = "15_DEE_V27_OBSERVER_SHADOW_MULTIPHYSICS_AND_FINAL_ROSETTA_RESULTADOS.zip"
OFFICIAL = ARCHIVE / OFFICIAL_NAME
BASELINE_SHA = "611517a8e5c24f21f82167540208c3ca05e27479189fc3c3a19d19941b3f4700"
EXPECTED = {
    "wheel": "69297e6f06761c8b2f65d24a3fd7a2f16a3f67595a7f9660739ab65f47abc939",
    "package": "7e2991b1fc8a053ee44ead6e177b129855ae9265dea68505a8e545f0c3fdf8b4",
    "kernel": "0b17ba32037935a255b0f2182a52137bceab424f7e09126b761076b63e42c6ff",
}


def utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def native(value):
    try:
        import numpy as np
        if isinstance(value, np.generic):
            return value.item()
        if isinstance(value, np.ndarray):
            return value.tolist()
    except ImportError:
        pass
    if isinstance(value, dict):
        return {str(k): native(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [native(v) for v in value]
    return value


def write_json(path: Path, value: object) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(native(value), stream, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def write_text(path: Path, value: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(value)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def append_ndjson(path: Path, row: dict) -> None:
    prior = path.read_text(encoding="utf-8") if path.exists() else ""
    write_text(path, prior + json.dumps(native({"utc": utc(), **row}), separators=(",", ":"), ensure_ascii=False) + "\n")


def read_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def kernel_paths() -> dict[str, Path]:
    extracted = TESTS / "DEE_CODEX_NATIVE_DISCOVERY_AND_CLOSURE_V1_WORK" / "ANALYSIS" / "binary_api" / "wheel_extracted" / "dee_universe_v27"
    return {
        "wheel": TESTS / "dee_universe_v27-27.0.0-cp313-cp313-win_amd64.whl",
        "package": extracted / "__init__.py",
        "kernel": extracted / "dee_kernel_v27.cp313-win_amd64.pyd",
    }


def audit_kernel(stage: str) -> dict:
    path = ROOT / "KERNEL_IMMUTABILITY_AUDIT.json"
    audit = read_json(path) if path.exists() else {"expected": EXPECTED, "checks": []}
    observed = {name: sha(p) for name, p in kernel_paths().items()}
    row = {"stage": stage, "utc": utc(), "observed": observed, "pass": observed == EXPECTED}
    audit["checks"].append(row)
    audit["all_pass"] = all(x["pass"] for x in audit["checks"])
    write_json(path, audit)
    if not row["pass"]:
        raise RuntimeError(f"canonical kernel mismatch at {stage}: {observed}")
    return row


def result_hash(path: Path) -> str:
    return sha(path)


def experiment_key(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def update_state(**fields) -> None:
    path = ROOT / "STATE.json"
    state = read_json(path) if path.exists() else {"status": "INITIALIZING", "started_utc": utc(), "completed_checkpoints": []}
    state.update(native(fields))
    state["updated_utc"] = utc()
    write_json(path, state)

