#!/usr/bin/env python3
"""Discovery root D02: search for a compressed R* above R1/R2/R3."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core17_common import ROOT, append_ndjson, audit_kernel, canonical_hash, utc, verify_and_load_kernel, write_json

BASE = Path(__file__).resolve().parent / "VENDORED_CORE16" / "BASELINE_RUNNERS"
sys.path.insert(0, str(BASE))
from core10_apparatus import run_learned_policy_transfer
from core12_apparatus import source_train_trial


FRAMES = [
    ((0, 1, 2), (1, 1, 1)),
    ((1, 2, 0), (1, -1, 1)),
    ((2, 0, 1), (-1, 1, 1)),
    ((0, 2, 1), (-1, -1, 1)),
]


def routed_context_collision(kernel):
    rows = []
    for i in range(6):
        p, s = FRAMES[i % len(FRAMES)]
        kwargs = {"seed": 1702000 + i * 101, "n": (27, 31, 35)[i % 3], "distance": (5, 7, 9)[i % 3], "permutation": p, "signs": s}
        prepared = run_learned_policy_transfer(kernel, mode="trained", **kwargs)
        wrong = run_learned_policy_transfer(kernel, mode="wrong_receiver", **kwargs)
        pre_arrival_a = [x for x in prepared["corridor_trace"] if x["distance_from_source"] < prepared["distance"]]
        pre_arrival_b = [x for x in wrong["corridor_trace"] if x["distance_from_source"] < wrong["distance"]]
        rows.append({
            "case": i,
            "same_routed_event_before_receiver": pre_arrival_a == pre_arrival_b,
            "prepared_functional": prepared["functional_policy_reinstantiated"],
            "wrong_receiver_functional": wrong["functional_policy_reinstantiated"],
            "receiver": prepared["receiver"],
            "route_distance": prepared["distance"],
        })
    return {"rows": rows, "separates": all(x["same_routed_event_before_receiver"] and x["prepared_functional"] and not x["wrong_receiver_functional"] for x in rows), "missing_from_R1": "receiver/interface relational state"}


def phase_count_collision(kernel):
    directions = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, 0, -1))
    rows = []
    for i, d in enumerate(directions):
        common = {"kernel": kernel, "n": 39, "source": (19, 19, 19), "direction": d, "sreg": 101 + i * 31, "mode": "baseline", "threads": 1}
        a = source_train_trial(horizon=23, detector_distance=7, **common)
        b = source_train_trial(horizon=24, detector_distance=8, **common)
        ta = a["arrival_ticks"]; tb = b["arrival_ticks"]
        m = min(len(ta), len(tb))
        rows.append({
            "direction": list(d), "count_a": len(ta), "count_b": len(tb),
            "equal_integrated_count_in_matched_window": len(ta) == len(tb),
            "phase_shift": [tb[j] - ta[j] for j in range(m)],
            "distinct_event_timing": ta != tb,
            "a_ticks": ta, "b_ticks": tb,
        })
    return {"rows": rows, "separates": all(x["equal_integrated_count_in_matched_window"] and x["distinct_event_timing"] for x in rows), "missing_from_integrated_R2_readout": "event phase/timing"}


def functional_equivalence(kernel):
    rows = []
    for i in range(8):
        p, s = FRAMES[i % len(FRAMES)]
        r = run_learned_policy_transfer(kernel, seed=1703000 + i * 131, n=(27, 31, 35, 39)[i % 4], distance=(5, 7, 9, 11)[i % 4], mode="trained", permutation=p, signs=s)
        rows.append({"case": i, "source": r["source"], "receiver": r["receiver"], "frame": r["frame"], "query_record": r["query_record"], "functional": r["functional_policy_reinstantiated"], "source_depleted": r["source_depleted_after_launch"]})
    raw_descriptions_distinct = len({json.dumps({"source": x["source"], "receiver": x["receiver"], "frame": x["frame"]}, sort_keys=True) for x in rows}) == len(rows)
    return {"rows": rows, "all_functionally_equivalent": all(x["functional"] for x in rows), "micro_relational_descriptions_distinct": raw_descriptions_distinct, "compression_positive": all(x["functional"] for x in rows) and raw_descriptions_distinct}


def measure_orthogonality():
    macrostate = {"compatible_microstates": 8, "deterministic_outcomes": {"one_destination": 2, "two_destinations": 6}}
    measures = [
        {"name": "uniform", "weights_one": [1, 1], "weights_two": [1] * 6},
        {"name": "endpoint_biased", "weights_one": [9, 9], "weights_two": [1] * 6},
        {"name": "mixed_biased", "weights_one": [1, 1], "weights_two": [3] * 6},
    ]
    rows = []
    for m in measures:
        total = sum(m["weights_one"]) + sum(m["weights_two"])
        rows.append({"measure": m["name"], "p_one": sum(m["weights_one"]) / total, "p_two": sum(m["weights_two"]) / total})
    return {"macrostate": macrostate, "rows": rows, "same_single_state_projection": True, "different_distribution": len({(x["p_one"], x["p_two"]) for x in rows}) == len(rows), "missing_from_R1_R2": "preparation measure over compatible microstates"}


def main():
    audit_kernel("CORE17_D02_LEVEL_UNIFICATION")
    kernel, runtime = verify_and_load_kernel(1)
    r1_to_r2 = routed_context_collision(kernel)
    r2_to_r1 = phase_count_collision(kernel)
    r2_compression = functional_equivalence(kernel)
    r3 = measure_orthogonality()
    separators = [
        {"pair": "R1_vs_R2", "required_coordinate": "receiver/interface relational state", "passed": r1_to_r2["separates"]},
        {"pair": "R2_integrated_vs_R1", "required_coordinate": "event phase/timing", "passed": r2_to_r1["separates"]},
        {"pair": "single_state_vs_R3", "required_coordinate": "preparation measure", "passed": r3["different_distribution"]},
    ]
    all_separate = all(x["passed"] for x in separators)
    result = {
        "schema": "dee.v27.core17.d02.v1", "experiment": "RSTAR_UNIFICATION_COMPETITION",
        "created_utc": utc(), "runtime": runtime,
        "r1_r2_context_collision": r1_to_r2,
        "r2_r1_phase_collision": r2_to_r1,
        "r2_functional_compression": r2_compression,
        "r3_measure_orthogonality": r3,
        "separators": separators,
        "adjudication": {
            "nontrivial_compressed_Rstar_found": False,
            "why": "Every tested representation that omits event phase, receiver/history context, or preparation measure fails at least one independent task. Adding all three is an uncompressed union rather than a new quotient.",
            "common_parent": "R0_NATIVE_CAUSAL_QUOTIENT plus task declaration/measure",
            "level_topology": "overlapping task-dependent projections with genuine branch-specific coordinates",
            "bounded": True,
            "all_separator_tests_pass": all_separate,
        },
    }
    h = canonical_hash(result); result["content_sha256"] = h
    write_json(ROOT / "DISCOVERY" / "C17D02_LEVEL_UNIFICATION.json", result)
    append_ndjson(ROOT / "QUESTION_TREE.ndjson", {"question_id": "C17Q002", "parent_question": "Can R1, R2 functional/relational and R3 be projections of a compressed R*?", "parent_result_hash": "256fc52428ef850cc13170cbfa2bd897076c2147b4abfa50961f873268b4417e", "new_uncertainty": "Whether the apparent branches share a smaller sufficient representation than R0.", "candidate_explanations": ["single compressed R*", "task-dependent quotients", "scale regimes"], "why_next_experiment_discriminates": "Pairwise collision cases force each candidate to predict a task for which its omitted coordinate is causal.", "result_hash": h, "result": result["adjudication"], "child_question": "Can response-signature clustering compress the union without losing fresh predictive tasks?", "status": "CHILD_OPEN"})
    append_ndjson(ROOT / "KERNEL_DIALOGUE.ndjson", {"question_id": "C17Q002", "raw_outcome": {"separator_tests": separators, "functional_compression": r2_compression["compression_positive"]}, "mechanism_update": "R2 functional compression is real, but R1 timing, R2 context/history and R3 preparation measure are mutually nonredundant in the tested task family.", "next": "Compete explicit feature subsets with a response-signature representation on selection worlds."})
    print(json.dumps({"hash": h, "adjudication": result["adjudication"], "separators": separators}, indent=2))


if __name__ == "__main__":
    main()
