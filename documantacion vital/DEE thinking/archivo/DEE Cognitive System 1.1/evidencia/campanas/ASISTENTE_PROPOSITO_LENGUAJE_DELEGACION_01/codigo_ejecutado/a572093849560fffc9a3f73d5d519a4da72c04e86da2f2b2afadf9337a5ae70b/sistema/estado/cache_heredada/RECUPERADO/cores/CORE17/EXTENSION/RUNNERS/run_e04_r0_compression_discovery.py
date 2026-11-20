#!/usr/bin/env python3
"""Discover and test a genuine factorized causal quotient below full R0."""
from __future__ import annotations

import hashlib
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from core17e_common import PACKAGE_ROOT, ROOT, append_ndjson, audit_kernel, seal, verify_and_load_kernel, write_json

BASE = PACKAGE_ROOT / "RUNNERS" / "VENDORED_CORE16" / "BASELINE_RUNNERS"
sys.path.insert(0, str(BASE))
from core10_common import NativeWorld  # noqa: E402


CLOCK_PERIODS = (195, 260, 391, 782)
CLOCK_MODULUS = math.lcm(*CLOCK_PERIODS)
STATE_MASK = np.uint64(0xFFFFFFFF)
UPPER_MASK = np.uint64(0xFFFFFFFF00000000)
SEM_MASK = np.uint64(0xF)


def reduce_state(raw: np.ndarray, clock: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Canonical representative of the tested predictive equivalence class."""
    semantic = (raw >> np.uint64(60)) & SEM_MASK
    state = raw & STATE_MASK
    sem4 = semantic == np.uint64(4)
    nonzero = state > 0
    reduced_raw = raw.copy()
    ordinary = ~sem4
    reduced_raw[ordinary] = (raw[ordinary] & UPPER_MASK) | nonzero[ordinary].astype(np.uint64)
    reduced_clock = np.mod(clock, np.uint64(CLOCK_MODULUS)).astype(np.uint64)
    reduced_clock[sem4] = np.uint64(0)
    return reduced_raw, reduced_clock


def digest(raw: np.ndarray, clock: np.ndarray) -> str:
    h = hashlib.sha256(); h.update(np.ascontiguousarray(raw).tobytes()); h.update(np.ascontiguousarray(clock).tobytes()); return h.hexdigest()


def make_world(rng: np.random.Generator, n: int, density: float) -> tuple[np.ndarray, np.ndarray]:
    raw = np.zeros((n, n, n), dtype=np.uint64)
    clock = rng.integers(0, 2**52, size=raw.shape, dtype=np.uint64)
    occupied = rng.random(raw.shape) < density
    coords = np.argwhere(occupied)
    semantics = np.array([1, 1, 1, 4, 5, 7], dtype=np.uint64)
    for q in coords:
        idx = tuple(int(x) for x in q)
        state = int(rng.integers(1, 2**32, dtype=np.uint64))
        sreg = int(rng.integers(0, 19665))
        direction = tuple(int(x) for x in rng.integers(-1, 2, size=3))
        semantic = int(rng.choice(semantics))
        value = ((state & 0xFFFFFFFF) | ((sreg & 0xFFFF) << 32) | ((direction[0] & 0xF) << 48) | ((direction[1] & 0xF) << 52) | ((direction[2] & 0xF) << 56) | ((semantic & 0xF) << 60))
        raw[idx] = np.uint64(value)
    return raw, clock


def run_pair(kernel, seed: int, n: int, density: float, ticks: int) -> dict:
    rng = np.random.default_rng(seed)
    raw, clock = make_world(rng, n, density)
    craw, cclock = reduce_state(raw, clock)
    original = NativeWorld(kernel, raw.copy(), clock.copy(), threads=1)
    canonical = NativeWorld(kernel, craw.copy(), cclock.copy(), threads=1)
    trace = [{"tick": 0, "original_reduced_sha256": digest(*reduce_state(original.raw, original.clock_a)), "canonical_sha256": digest(*reduce_state(canonical.raw, canonical.clock_a)), "mismatch_raw": 0, "mismatch_clock": 0}]
    passed = True
    for tick in range(1, ticks + 1):
        original.tick(); canonical.tick()
        oraw, oclock = reduce_state(original.raw, original.clock_a)
        rraw, rclock = reduce_state(canonical.raw, canonical.clock_a)
        mr = int(np.count_nonzero(oraw != rraw)); mc = int(np.count_nonzero(oclock != rclock))
        trace.append({"tick": tick, "original_reduced_sha256": digest(oraw, oclock), "canonical_sha256": digest(rraw, rclock), "mismatch_raw": mr, "mismatch_clock": mc})
        if mr or mc:
            passed = False
            break
    return {"seed": seed, "n": n, "density": density, "ticks_requested": ticks, "ticks_compared": len(trace) - 1, "passed": passed, "trace": trace}


def main() -> None:
    if CLOCK_MODULUS != 304980:
        raise RuntimeError(CLOCK_MODULUS)
    kernel, runtime = verify_and_load_kernel(1)
    configs = [(7, 0.07, 40), (7, 0.18, 40), (9, 0.05, 32), (9, 0.14, 32), (11, 0.03, 24), (11, 0.09, 24)]
    rows = [run_pair(kernel, 1741000 + i * 10007, n, d, t) for i, (n, d, t) in enumerate(configs)]
    representation = {
        "name": "R0_FACTOR_52",
        "domain": "well-formed voxels: raw=0 or state>0; s_reg in 0..19664; clocks away from uint64 wrap",
        "non_semantic4": {"existence_bits": 1, "s_reg_bits": 16, "direction_bits": 12, "semantic_bits": 4, "clock_phase_bits": 19, "total_bits": 52},
        "semantic4": {"full_raw_bits": 64, "clock_bits": 0, "total_bits": 64},
        "baseline_full_R0_bits_per_cell": 128,
        "clock_periods": list(CLOCK_PERIODS),
        "clock_modulus": CLOCK_MODULUS,
        "modulus_minimality_scope": "minimal positive fixed global modulus divisible by every reachable incumbent matter update period",
        "compression_is_not_concatenation": True,
        "discarded_coordinates": ["31 state-magnitude bits for non-semantic4 occupied cells", "absolute clock quotient", "all semantic4 clock bits"],
    }
    result = seal({
        "schema": "dee.v27.core17.extension.r0_factor_compression.discovery.v1",
        "representation": representation,
        "period_derivation": [
            {"n_active": 4, "strong_tetrahedral": True, "missing": 4, "period": 195},
            {"n_active": 5, "strong_tetrahedral": True, "missing": 3, "period": 260},
            {"n_active": 6, "strong_tetrahedral": True, "missing": 2, "period": 391},
            {"n_active": 7, "strong_tetrahedral": False, "missing": 1, "period": 782},
        ],
        "rows": rows,
        "summary": {"worlds": len(rows), "all_passed": all(r["passed"] for r in rows), "ticks_compared": sum(r["ticks_compared"] for r in rows), "raw_mismatches": sum(x["mismatch_raw"] for r in rows for x in r["trace"]), "clock_mismatches": sum(x["mismatch_clock"] for r in rows for x in r["trace"])},
        "runtime": runtime,
    })
    write_json(ROOT / "DISCOVERY" / "C17E04_R0_FACTOR_COMPRESSION.json", result)
    append_ndjson(ROOT / "QUESTION_TREE.ndjson", {"id": "C17EQ004", "parent_question": "C17EQ001", "parent_result_hash": result["content_sha256"], "question": "Does R0_FACTOR_52 preserve the reduced dynamics on post-freeze worlds?", "competing_hypotheses": ["exact quotient in stated domain", "selection-world artifact"], "discriminating_next_action": "freeze and fresh-test densities/sizes not used in discovery"})
    print({"hash": result["content_sha256"], **result["summary"], "clock_modulus": CLOCK_MODULUS})
    if not result["summary"]["all_passed"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
