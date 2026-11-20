#!/usr/bin/env python3
"""C6H08 frozen confirmation of sectorial dissipative ensemble relaxation."""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from native_core import NativeWorld, atomic_json, canonical_hash, fields, pack, sha256_file, verify_and_load_kernel


WORK = Path(__file__).resolve().parents[1]
LOCK = WORK / "HOLDOUT_LOCKS" / "C6H08_DISSIPATIVE_NORMAL_ENSEMBLE_RELAXATION.json"
OUT = WORK / "RESULTS" / "C6H08_dissipative_ensemble_holdout.json"
EXPECTED_LOCK_SHA256 = "25c601b4eb589ec5ae583f094c90e9b0589e4eb526a42fb2a6e2ae8b0afebd0f"
DIRECTIONS = [d for d in itertools.product((-1, 0, 1), repeat=3) if d != (0, 0, 0)]


def prepared_support(n, count, rng):
    grid = list(itertools.product((3 * i for i in range(n // 3)), repeat=3))
    indices = rng.choice(len(grid), size=count, replace=False)
    return [grid[int(i)] for i in indices]


def metrics(raw):
    f = fields(raw)
    mask = raw != 0
    return {"support": int(np.count_nonzero(mask)), "sreg_sum": int(np.sum(f["sreg"], where=mask, dtype=np.uint64))}


def simulate(kernel, n, support, sregs, clocks, directions, horizon, aligned):
    raw = np.zeros((n, n, n), dtype=np.uint64)
    clock = np.zeros_like(raw)
    for q, sreg, token, d in zip(support, sregs, clocks, directions, strict=True):
        raw[q] = pack(1, sreg, d, 1)
        clock[q] = np.uint64(token)
    initial = raw.copy()
    world = NativeWorld(kernel, raw, clock, threads=1)
    trace = []
    raw_translation_exact = True
    for tick in range(horizon + 1):
        trace.append({"tick": tick, **metrics(world.raw)})
        if aligned:
            expected = np.roll(initial, shift=tick, axis=0)
            raw_translation_exact = raw_translation_exact and np.array_equal(world.raw, expected)
        if tick < horizon:
            world.tick()
    return trace, raw_translation_exact


def main():
    observed_lock = sha256_file(LOCK)
    if observed_lock != EXPECTED_LOCK_SHA256:
        raise RuntimeError(f"holdout lock mismatch: {observed_lock}")
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    kernel, environment = verify_and_load_kernel(1)
    cases = []
    for n in (18, 25):
        capacity = (n // 3) ** 3
        for fill in (0.25, 0.70):
            count = int(round(capacity * fill))
            for replicate in range(4):
                seed = 668000 + 1000 * n + 100 * int(fill * 100) + replicate
                rng = np.random.default_rng(seed)
                support = prepared_support(n, count, rng)
                sregs = [int(x) for x in rng.integers(1, 8, size=count)]
                clocks = [int(x) for x in rng.integers(0, 2**32, size=count, dtype=np.uint64)]
                mixed = [DIRECTIONS[int(i)] for i in rng.integers(0, len(DIRECTIONS), size=count)]
                horizon = 8 * n
                for arm, directions in (("aligned", [(1, 0, 0)] * count), ("mixed", mixed)):
                    trace, translated = simulate(kernel, n, support, sregs, clocks, directions, horizon, arm == "aligned")
                    support_values = [r["support"] for r in trace]
                    sreg_values = [r["sreg_sum"] for r in trace]
                    tail = trace[-2 * n:]
                    cases.append({
                        "n": n, "fill": fill, "replicate": replicate, "seed": seed, "arm": arm,
                        "count": count, "initial_sreg_sum": sum(sregs), "horizon": horizon,
                        "raw_translation_exact": translated,
                        "support_nonincreasing": all(b <= a for a, b in zip(support_values, support_values[1:])),
                        "sreg_nonincreasing": all(b <= a for a, b in zip(sreg_values, sreg_values[1:])),
                        "support_contracted": support_values[-1] < support_values[0],
                        "support_exact": all(x == support_values[0] for x in support_values),
                        "sreg_exact": all(x == sreg_values[0] for x in sreg_values),
                        "terminal_constant": len({r["support"] for r in tail}) == 1 and len({r["sreg_sum"] for r in tail}) == 1,
                        "support_ratio": support_values[-1] / support_values[0],
                        "final_support": support_values[-1], "final_sreg_sum": sreg_values[-1],
                        "trace": trace,
                    })
    aligned = [c for c in cases if c["arm"] == "aligned"]
    mixed = [c for c in cases if c["arm"] == "mixed"]
    density_gaps = {}
    for n in (18, 25):
        low = [c["support_ratio"] for c in mixed if c["n"] == n and c["fill"] == 0.25]
        high = [c["support_ratio"] for c in mixed if c["n"] == n and c["fill"] == 0.70]
        density_gaps[str(n)] = {"low_mean": sum(low) / len(low), "high_mean": sum(high) / len(high), "gap": sum(low) / len(low) - sum(high) / len(high)}
    summary = {
        "worlds": len(cases),
        "aligned_support_exact": sum(c["support_exact"] and c["raw_translation_exact"] for c in aligned),
        "aligned_sreg_exact": sum(c["sreg_exact"] for c in aligned),
        "mixed_support_nonincreasing": sum(c["support_nonincreasing"] for c in mixed),
        "mixed_sreg_nonincreasing": sum(c["sreg_nonincreasing"] for c in mixed),
        "mixed_support_contracted": sum(c["support_contracted"] for c in mixed),
        "mixed_terminal_constant": sum(c["terminal_constant"] for c in mixed),
        "density_gaps": density_gaps,
    }
    threshold = lock["minimum_relevance"]
    passed = (
        summary["aligned_support_exact"] == threshold["aligned_support_exact"]
        and summary["aligned_sreg_exact"] == threshold["aligned_sreg_exact"]
        and summary["mixed_support_nonincreasing"] == threshold["mixed_support_nonincreasing"]
        and summary["mixed_sreg_nonincreasing"] == threshold["mixed_sreg_nonincreasing"]
        and summary["mixed_support_contracted"] == threshold["mixed_support_contracted"]
        and summary["mixed_terminal_constant"] == threshold["mixed_terminal_constant"]
        and all(row["gap"] >= threshold["density_gap_each_N"] for row in density_gaps.values())
    )
    result = {
        "schema":"dee.v27.core06.c6h08.v1",
        "experiment_id":"C6H08_DISSIPATIVE_NORMAL_ENSEMBLE_RELAXATION",
        "role":"FROZEN_CONFIRMATION",
        "lock_sha256":observed_lock,
        "kernel_environment":environment,
        "verdict":"PASS" if passed else "FAIL",
        "summary":summary,
        "cases":cases,
        "promotion":lock["promotion_if_pass"] if passed else [],
        "interpretation":"A pass establishes a bounded dissipative statistical law and Lyapunov-like observables in this prepared normal sector, not physical thermodynamics, equilibrium or an asymptotic theorem.",
    }
    result["content_sha256"] = canonical_hash(result)
    atomic_json(OUT, result)
    print(json.dumps({"verdict": result["verdict"], **summary}, indent=2, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
