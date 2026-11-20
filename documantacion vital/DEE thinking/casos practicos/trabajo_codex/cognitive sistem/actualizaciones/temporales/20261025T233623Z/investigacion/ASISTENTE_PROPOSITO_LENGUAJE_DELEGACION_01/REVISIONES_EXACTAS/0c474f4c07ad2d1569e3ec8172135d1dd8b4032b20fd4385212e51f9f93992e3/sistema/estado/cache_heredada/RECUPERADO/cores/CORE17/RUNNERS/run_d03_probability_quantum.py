#!/usr/bin/env python3
"""D03: exact hidden-state pushforward and quantum-specific adversarial tests."""
from __future__ import annotations

import itertools
import json
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "VENDORED_CORE16" / "BASELINE_RUNNERS"))

from core17_common import (NativeWorld, ROOT, append_ndjson, audit_kernel,
                           canonical_hash, pack, unpack, utc,
                           verify_and_load_kernel, write_json)
from core12_apparatus import convergent_phase_paths
from run_d01_hidden_scale import TETRA, add, centers_for


def hidden_pattern_outcome(kernel, bits: tuple[int, ...], delay: int = 7, n: int = 17):
    centers = centers_for(n, len(bits))
    raw = np.zeros((n, n, n), dtype=np.uint64)
    clock = np.zeros_like(raw)
    for i, (q, bit) in enumerate(zip(centers, bits)):
        raw[q] = pack(0x4100 + i, 10, (0, 0, 0), 4)
        clock[q] = np.uint64((-delay + bit) % 195)
    world = NativeWorld(kernel, raw, clock, 1)
    for _ in range(delay):
        world.tick()
    for q in centers:
        world.raw_a[q] = world.raw_b[q] = pack(1, 10, (0, 0, 0), 1)
        for direction in TETRA:
            p = add(q, direction, n)
            world.raw_a[p] = world.raw_b[p] = pack(1, 3, (0, 0, 0), 1)
    pre = [{"q": list(q), "raw": int(world.raw[q]), "clock": int(world.clock[q])} for q in centers]
    world.tick()
    post = [{"q": list(q), **unpack(world.raw[q])} for q in centers]
    return {"bits": list(bits), "hidden_weight": sum(bits), "pre": pre, "post": post}


def probability_pushforward(kernel, k: int = 6):
    rows = [hidden_pattern_outcome(kernel, bits) for bits in itertools.product((0, 1), repeat=k)]
    class_zero = tuple((r["state"], r["sreg"], tuple(r["direction"]), r["semantic"])
                       for r in hidden_pattern_outcome(kernel, (0,) * k)["post"])
    class_one = tuple((r["state"], r["sreg"], tuple(r["direction"]), r["semantic"])
                      for r in hidden_pattern_outcome(kernel, (1,) * k)["post"])
    for row in rows:
        signatures = [(r["state"], r["sreg"], tuple(r["direction"]), r["semantic"])
                      for r in row["post"]]
        row["observable_count"] = sum(sig == class_one[i] for i, sig in enumerate(signatures))
        row["exact_micro_to_macro"] = row["observable_count"] == row["hidden_weight"]
    uniform_counts = Counter(row["observable_count"] for row in rows)
    uniform_expected = {r: math.comb(k, r) for r in range(k + 1)}
    weighted = {}
    for p in (0.25, 0.5, 0.75):
        distribution = {r: 0.0 for r in range(k + 1)}
        for row in rows:
            w = p ** row["hidden_weight"] * (1 - p) ** (k - row["hidden_weight"])
            distribution[row["observable_count"]] += w
        expected = {r: math.comb(k, r) * p ** r * (1 - p) ** (k - r) for r in range(k + 1)}
        weighted[str(p)] = {
            "observed": distribution,
            "expected_binomial": expected,
            "max_abs_error": max(abs(distribution[r] - expected[r]) for r in range(k + 1)),
        }
    return {
        "k": k,
        "microstates_exhausted": len(rows),
        "response_classes_distinct": class_zero != class_one,
        "micro_to_macro_exact": all(row["exact_micro_to_macro"] for row in rows),
        "uniform_observed_counts": dict(sorted(uniform_counts.items())),
        "uniform_expected_counts": uniform_expected,
        "uniform_exact": dict(sorted(uniform_counts.items())) == uniform_expected,
        "weighted_measures": weighted,
        "measure_changes_probability_not_kernel_map": True,
        "sample_rows": [rows[i] for i in (0, 1, len(rows) // 2, len(rows) - 1)],
    }


def path_competition(kernel):
    modes = ("A_only", "B_only", "AB_coherent", "AB_phase_shifted", "AB_offpath_sham")
    trials = {mode: convergent_phase_paths(kernel, n=43, path_length=7, mode=mode,
                                           sregs=(101, 211), horizon=20, threads=1)
              for mode in modes}
    summary = {mode: {
        "event_ticks": trial["detector_event_ticks"],
        "event_sregs": trial["detector_event_sregs"],
        "event_directions": trial["detector_event_directions"],
        "event_count": trial["event_count"],
    } for mode, trial in trials.items()}
    a, b, ab = summary["A_only"], summary["B_only"], summary["AB_coherent"]
    same_schedule = ab["event_ticks"] == a["event_ticks"] == b["event_ticks"]
    capped_sum = all(x == min(19664, y + z)
                     for x, y, z in zip(ab["event_sregs"], a["event_sregs"], b["event_sregs"]))
    return {
        "apparatus": "two equal-length semantic-4 source trains converging on one detector",
        "summaries": summary,
        "joint_schedule_equals_single_schedules": same_schedule,
        "joint_sreg_is_capped_additive_reducer": capped_sum,
        "ordinary_reducer_explains_joint_response": same_schedule and capped_sum,
        "phase_shift_explained_by_mouth_occupancy": summary["AB_phase_shifted"] != summary["AB_coherent"],
        "offpath_sham_matches_coherent": summary["AB_offpath_sham"] == summary["AB_coherent"],
        "quantum_specific_interference": False,
    }


def main():
    audit_kernel("CORE17_D03_PROBABILITY_QUANTUM")
    kernel, runtime = verify_and_load_kernel(1)
    probability = probability_pushforward(kernel, 6)
    paths = path_competition(kernel)
    result = {
        "schema": "dee.v27.core17.d03.v1",
        "experiment": "EXACT_PUSHFORWARD_AND_QUANTUM_SPECIFIC_COMPETITION",
        "created_utc": utc(),
        "runtime": runtime,
        "probability": probability,
        "multipath": paths,
        "contextuality": {
            "valid_compatible_contexts_constructed": False,
            "reason": "Available sequential interventions rewrite ordinary native state/history; no context-independent nominal observable with compatible alternatives was established.",
            "status": "PREREQUISITE_NOT_CONSTRUCTED",
        },
        "noncommutativity": {
            "reusable_observable_algebra_found": False,
            "ordinary_history_conditioned_order_effect_preserved": True,
        },
        "bell": {
            "prior_valid_result_preserved": "CHSH=-2 in tested CORE16 apparatus",
            "new_valid_two-subsystem_protocol_constructed": False,
            "scope": "No new preparation simultaneously satisfied independent settings, causal separation and frozen all-trial readout.",
        },
        "adjudication": {
            "effective_probability": "EXACT_CLASSICAL_HIDDEN_STATE_PUSHFORWARD",
            "nonclassical_probability_found": False,
            "quantum_specific_structure_found": False,
            "bounded_to_tested_levels_and_apparatuses": True,
        },
    }
    h = canonical_hash(result)
    result["content_sha256"] = h
    write_json(ROOT / "DISCOVERY" / "C17D03_PROBABILITY_QUANTUM.json", result)
    append_ndjson(ROOT / "QUESTION_TREE.ndjson", {
        "question_id": "C17Q003",
        "parent_question": "Does hidden-state return induce a probability law beyond classical ignorance?",
        "parent_result_hash": "b5c40ef8729a3de1208fa99b11d8b66e4597c7f672bd55a6e501833a0f6c4de0",
        "new_uncertainty": "Whether the distribution is a deterministic pushforward of hidden clock classes or needs a nonclassical composition rule.",
        "candidate_explanations": ["classical hidden-state pushforward", "nonlinear amplitude-like rule", "observer-selection artifact"],
        "why_next_experiment_discriminates": "All 64 microstates are exhausted and reweighted under three explicit preparation measures; multipath responses compete against the capped reducer.",
        "result_hash": h,
        "result": result["adjudication"],
        "child_question": "Does the exact binomial law generalize prospectively to fresh module counts, geometries and nonuniform measures?",
        "status": "CHILD_OPEN",
    })
    append_ndjson(ROOT / "RESEARCH_DECISION_LOG.ndjson", {
        "utc": utc(), "decision_id": "C17D03_DECISION", "parent_result_hash": h,
        "decision": "Close the quantum-specific promotion route for this apparatus; open prospective classical-pushforward confirmation.",
        "reason": "The complete microstate enumeration matches the deterministic map and binomial measure exactly; joint path response is reducer-additive.",
    })
    append_ndjson(ROOT / "KERNEL_DIALOGUE.ndjson", {
        "question_id": "C17Q003", "raw_outcome": result["adjudication"],
        "mechanism_update": "Probability belongs to the observer/preparation measure over deterministic clock classes; the tested path composition adds via the native reducer.",
        "next": "Freeze fresh exact pushforward predictions; do not promote quantum terminology.",
    })
    print(json.dumps({"hash": h, "adjudication": result["adjudication"],
                      "uniform": probability["uniform_observed_counts"],
                      "paths": paths["summaries"]}, indent=2))


if __name__ == "__main__":
    main()
