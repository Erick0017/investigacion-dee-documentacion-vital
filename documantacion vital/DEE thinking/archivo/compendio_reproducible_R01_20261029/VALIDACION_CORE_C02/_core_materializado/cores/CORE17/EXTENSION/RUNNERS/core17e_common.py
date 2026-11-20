#!/usr/bin/env python3
"""Shared helpers for the definitive CORE17 frontier closure extension."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TESTS = ROOT.parent
PACKAGE_ROOT_CANDIDATES = [HERE.parent.parent, TESTS / "DEE_V27_CORE17_COMPLETE_REALITY_INTEGRATION_WORK"]
PACKAGE_ROOT = next((path for path in PACKAGE_ROOT_CANDIDATES if (path / "RUNNERS" / "core17_common.py").is_file()), None)
if PACKAGE_ROOT is None:
    raise FileNotFoundError("CORE17 retained runners not found")
sys.path.insert(0, str(PACKAGE_ROOT / "RUNNERS"))

from core17_common import (  # noqa: E402,F401
    EXPECTED,
    NativeWorld,
    audit_kernel,
    canonical_hash,
    pack,
    read_json,
    sha256_array,
    sha256_file,
    unpack,
    utc,
    verify_and_load_kernel,
)


CANONICAL_CORE = TESTS / "EXPEDIENTE_EXPERIMENTOS_DEE" / "CORE"
OFFICIAL_CORE17 = CANONICAL_CORE / "17_DEE_V27_REALITY_UNIFICATION_CROSS_SCALE_PHYSICS_AND_CAPABILITIES_RESULTADOS.zip"
PRE_EXTENSION_SHA256 = "c1764e3314473c5d1f893bdfd92f051ae4da9931e2a4c3b21250e83676ac0063"


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temp, path)


def append_ndjson(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as target:
        target.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def seal(value: dict) -> dict:
    value = dict(value)
    value["content_sha256"] = canonical_hash(value)
    return value

