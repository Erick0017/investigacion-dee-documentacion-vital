#!/usr/bin/env python3
"""Result-derived selection tests for D01, D03 and D04 candidate laws."""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "VENDORED_CORE16" / "BASELINE_RUNNERS"))

from core17_common import (NativeWorld, ROOT, append_ndjson, audit_kernel,
                           canonical_hash, fresh_seed, pack, unpack, utc,
                           verify_and_load_kernel, write_json)
from core12_apparatus import regenerative_interface_trial
from run_d03_probability_quantum import probability_pushforward


def random_centers(rng, n, count):
    centers = []
    while len(centers) < count:
        q = tuple(int(x) for x in rng.integers(3, n - 3, size=3))
        if all(max(min(abs(q[i] - p[i]), n - abs(q[i] - p[i])) for i in range(3)) >= 4 for p in centers):
            centers.append(q)
    return centers


def gate_case(kernel, rng, n, modules, delay, off_gate=False, equal=False):
    centers = random_centers(rng, n, modules)
    signs = [tuple(1 if int(x) else -1 for x in rng.integers(0, 2, size=3)) for _ in centers]
    raw = np.zeros((n, n, n), dtype=np.uint64)
    ca = np.zeros_like(raw); cb = np.zeros_like(raw)
    phase = 17 if off_gate else 0
    for i, q in enumerate(centers):
        raw[q] = pack(0x5100 + i, 10, (0, 0, 0), 4)
        ca[q] = np.uint64((phase - delay) % 195)
        cb[q] = ca[q] if equal else np.uint64((phase - delay + 1) % 195)
    a = NativeWorld(kernel, raw, ca, 1); b = NativeWorld(kernel, raw, cb, 1)
    coast_equal = True
    for _ in range(delay):
        coast_equal &= bool(np.array_equal(a.raw, b.raw)); a.tick(); b.tick()
    coast_equal &= bool(np.array_equal(a.raw, b.raw))
    for q, s in zip(centers, signs):
        tetra = ((s[0], 0, 0), (0, s[1], 0), (0, 0, s[2]), s)
        for w in (a, b):
            w.raw_a[q] = w.raw_b[q] = pack(1, 10, (0, 0, 0), 1)
            for d in tetra:
                p = tuple((q[i] + d[i]) % n for i in range(3))
                w.raw_a[p] = w.raw_b[p] = pack(1, 3, (0, 0, 0), 1)
    a.tick(); b.tick()
    changed = sum(int(a.raw[q]) != int(b.raw[q]) for q in centers)
    return {"n": n, "modules": modules, "delay": delay, "off_gate": off_gate,
            "equal_clock": equal, "coast_equal": coast_equal,
            "changed_centers": changed,
            "expected_changed": 0 if off_gate or equal else modules,
            "pass": coast_equal and changed == (0 if off_gate or equal else modules)}


def macro_selection(kernel, rng):
    directions = ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
    rows = []
    for i, d in enumerate(directions):
        n = (41, 43, 47)[i % 3]; horizon = int(rng.integers(21, 96)); center = (n // 2,) * 3
        pair = {"n": n, "direction": list(d), "center": list(center), "horizon": horizon}
        for count in (5, 6):
            r = regenerative_interface_trial(kernel, n=n, source_distance=7, downstream_distance=5,
                                             horizon=horizon, mode="semantic4_custom", direction=d,
                                             center=center, source_sreg=149 + i,
                                             semantic4_indices=list(range(count)), threads=1)
            pair[f"k{count}_events"] = len(r["downstream_event_ticks"]["5"])
        pair["expected_k5"] = max(0, (horizon - 10) // 2)
        pair["pass"] = pair["k5_events"] == pair["expected_k5"] and pair["k6_events"] == 0
        rows.append(pair)
    return rows


def main():
    audit_kernel("CORE17_S01_MODEL_SELECTION")
    kernel, runtime = verify_and_load_kernel(1)
    seed = fresh_seed(); rng = np.random.default_rng(seed)
    gates = []
    for i in range(9):
        n = (19, 23, 27)[i % 3]; modules = (1, 2, 3, 4, 5, 6, 7, 8, 10)[i]
        delay = int(rng.integers(0, 390))
        gates.append(gate_case(kernel, rng, n, modules, delay))
    gates.append(gate_case(kernel, rng, 23, 6, 31, off_gate=True))
    gates.append(gate_case(kernel, rng, 23, 6, 31, equal=True))
    probabilities = [probability_pushforward(kernel, k) for k in (3, 5, 7)]
    macro = macro_selection(kernel, rng)
    result = {
        "schema": "dee.v27.core17.selection.v1", "created_utc": utc(), "runtime": runtime,
        "os_entropy_seed": seed, "clock_gate_cases": gates,
        "probability_cases": [{"k": x["k"], "microstates": x["microstates_exhausted"],
                               "exact": x["micro_to_macro_exact"] and x["uniform_exact"],
                               "weighted_max_errors": {p: v["max_abs_error"] for p, v in x["weighted_measures"].items()}}
                              for x in probabilities],
        "macro_control_cases": macro,
        "selection": {
            "clock_model_selected": all(x["pass"] for x in gates),
            "probability_pushforward_selected": all(x["micro_to_macro_exact"] and x["uniform_exact"] and
                                                    max(v["max_abs_error"] for v in x["weighted_measures"].values()) < 1e-12 for x in probabilities),
            "macro_horizon_law_selected": all(x["pass"] for x in macro),
            "clock_law": "changed_centers = module_count at gate; zero for equal-clock or off-gate controls",
            "probability_law": "for k independent binary clock classes, P(R=r)=C(k,r)p^r(1-p)^(k-r)",
            "macro_law": "k5 events=max(0,floor((horizon-10)/2)); k6 events=0 for sealed source_distance=7/downstream=5 apparatus",
        },
    }
    h = canonical_hash(result); result["content_sha256"] = h
    write_json(ROOT / "MODEL_SELECTION" / "C17S01_MODEL_SELECTION.json", result)
    append_ndjson(ROOT / "QUESTION_TREE.ndjson", {
        "question_id": "C17Q001A", "parent_question": "C17Q001/C17Q003/C17Q004",
        "parent_result_hash": "71ef45e9a2ac681d7de22e562c60943dee30978b93f31a31ab3d060ff4dd7004",
        "new_uncertainty": "Whether selected laws survive untouched worlds created only after source freeze.",
        "candidate_explanations": ["geometry-independent native laws", "selection-set overfit"],
        "why_next_experiment_discriminates": "The apparatus, code, metrics and exact predictions can now be frozen before new OS-entropy challenges exist.",
        "result_hash": h, "result": result["selection"], "child_question": "Fresh post-freeze confirmation", "status": "READY_TO_FREEZE",
    })
    print(json.dumps({"hash": h, "selection": result["selection"], "seed": seed}, indent=2))


if __name__ == "__main__":
    main()
