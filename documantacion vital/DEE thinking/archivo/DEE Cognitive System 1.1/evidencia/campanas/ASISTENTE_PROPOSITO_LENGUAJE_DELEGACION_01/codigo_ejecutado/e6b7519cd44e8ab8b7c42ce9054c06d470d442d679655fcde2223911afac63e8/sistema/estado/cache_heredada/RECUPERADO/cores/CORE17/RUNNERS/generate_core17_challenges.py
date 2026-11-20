#!/usr/bin/env python3
"""Generate untouched CORE17 final challenges after source freeze using OS entropy."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from core17_common import ROOT, canonical_hash, fresh_seed, read_json, utc, write_json


def main():
    path = ROOT / "FRESH_CHALLENGES" / "CORE17_FINAL_CHALLENGES.json"
    if path.exists():
        raise RuntimeError("untouched challenge set already exists")
    lock = read_json(ROOT / "HOLDOUT_LOCKS" / "CORE17_FINAL_LOCK.json")
    seed = fresh_seed(); rng = np.random.default_rng(seed)
    clock_cases = []
    for i in range(12):
        clock_cases.append({"challenge_id": f"CLK{i:02d}", "case_seed": int(rng.integers(0, 2**63)),
                            "n": int(rng.choice((19, 23, 27))), "modules": int(rng.integers(1, 11)),
                            "delay": int(rng.integers(0, 585)), "mode": "positive"})
    for i, mode in enumerate(("equal_clock", "equal_clock", "off_gate", "off_gate"), 12):
        clock_cases.append({"challenge_id": f"CLK{i:02d}", "case_seed": int(rng.integers(0, 2**63)),
                            "n": 23, "modules": int(rng.integers(3, 9)),
                            "delay": int(rng.integers(0, 390)), "mode": mode})
    probability_cases = [{"challenge_id": f"PRB{i:02d}", "k": k} for i, k in enumerate((2, 4, 6, 8))]
    directions = ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
    macro_cases = []
    for i in range(8):
        n = int(rng.choice((41, 43, 47))); d = directions[i % len(directions)]
        macro_cases.append({"challenge_id": f"MAC{i:02d}", "n": n, "horizon": int(rng.integers(21, 140)),
                            "direction": list(d), "center": [n // 2] * 3,
                            "source_sreg": int(rng.integers(23, 1000))})
    operator_cases = []
    for i in range(12):
        operator_cases.append({"challenge_id": f"OPR{i:02d}", "case_seed": int(rng.integers(0, 2**63)),
                               "n": (7, 8, 9)[i % 3], "density": (0.025, 0.055, 0.10, 0.16)[i % 4],
                               "include_fusion": bool(i % 2 == 0), "ticks": int(rng.integers(5, 10))})
    frames = [((0,1,2),(1,1,1)),((1,2,0),(1,-1,1)),((2,0,1),(-1,1,1)),((0,2,1),(-1,-1,1))]
    level_cases = []
    for i in range(6):
        p, s = frames[i % 4]
        level_cases.append({"challenge_id": f"LVL{i:02d}", "case_seed": int(rng.integers(1, 10_000_000)),
                            "n": (27, 31, 35)[i % 3], "distance": (5, 7, 9)[i % 3],
                            "permutation": list(p), "signs": list(s), "direction": list(directions[i]),
                            "sreg": int(rng.integers(50, 500))})
    challenges = {"schema": "dee.v27.core17.challenges.v1", "created_utc": utc(),
                  "os_entropy_master_seed": seed, "lock_sha256": lock["lock_sha256"],
                  "clock_cases": clock_cases, "probability_cases": probability_cases,
                  "macro_cases": macro_cases, "operator_cases": operator_cases, "level_cases": level_cases}
    challenges["challenge_sha256"] = canonical_hash(challenges)
    write_json(path, challenges)
    print(json.dumps({"challenge_sha256": challenges["challenge_sha256"], "master_seed": seed,
                      "case_counts": {k: len(v) for k, v in challenges.items() if k.endswith("_cases")}}, indent=2))


if __name__ == "__main__":
    main()
