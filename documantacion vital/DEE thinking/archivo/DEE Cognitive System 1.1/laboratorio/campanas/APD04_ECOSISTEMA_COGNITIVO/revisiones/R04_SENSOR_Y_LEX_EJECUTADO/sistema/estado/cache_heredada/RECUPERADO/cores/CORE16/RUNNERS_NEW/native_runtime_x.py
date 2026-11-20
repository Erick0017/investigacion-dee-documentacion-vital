#!/usr/bin/env python3
"""Retarget the locked CORE16 runtime helper to the canonical tests paths."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TESTS = ROOT.parent
BASE_RUNNERS = ROOT / "BASELINE_CORE16_LOCKED" / "RUNNERS"
sys.path.insert(0, str(BASE_RUNNERS))

import native_core as _base

EXTRACTED = TESTS / "DEE_CODEX_NATIVE_DISCOVERY_AND_CLOSURE_V1_WORK" / "ANALYSIS" / "binary_api" / "wheel_extracted"
_base.TESTS = TESTS
_base.EXTRACTED = EXTRACTED
_base.PACKAGE_FILE = EXTRACTED / "dee_universe_v27" / "__init__.py"
_base.KERNEL_FILE = EXTRACTED / "dee_universe_v27" / "dee_kernel_v27.cp313-win_amd64.pyd"
_base.WHEEL_FILE = TESTS / "dee_universe_v27-27.0.0-cp313-cp313-win_amd64.whl"

NativeWorld = _base.NativeWorld
pack = _base.pack
fields = _base.fields
sha256_array = _base.sha256_array
verify_and_load_kernel = _base.verify_and_load_kernel

