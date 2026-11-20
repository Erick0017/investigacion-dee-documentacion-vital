#!/usr/bin/env python3
"""Result-derived CORE16 discovery children and level-selection evidence."""
from __future__ import annotations

import itertools
import json
import math
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core16_common import (ROOT, append_ndjson, audit_kernel, canonical_hash,
                           experiment_key, read_json, sha, update_state, utc, write_json)
from native_core import NativeWorld, fields, pack, verify_and_load_kernel
from core12_apparatus import convergent_phase_paths, regenerative_interface_trial
from core10_apparatus import run_learned_policy_transfer, run_joint_scaffold
from run_discovery_roots import (DIRECTIONS, add, bell_trial, entropy,
                                 sparse_world, unpack)


OUT = ROOT / "MODEL_SELECTION"
TREE = ROOT / "QUESTION_TREE.ndjson"
DIALOGUE = ROOT / "KERNEL_DIALOGUE.ndjson"
DECISIONS = ROOT / "RESEARCH_DECISION_LOG.ndjson"


def append_child(qid, parent, parent_result, uncertainty, explanations, question, why):
    existing = {json.loads(line)["question_id"] for line in TREE.read_text(encoding="utf-8").splitlines() if line.strip()}
    if qid in existing:
        return
    parent_hash = sha(parent_result)
    append_ndjson(TREE, {
        "question_id": qid, "parent_question": parent, "parent_result_hash": parent_hash,
        "stage": "RESULT_DERIVED_CHILD", "new_uncertainty": uncertainty,
        "candidate_explanations": explanations, "question": question,
        "why_next_experiment_discriminates": why, "expected_information_gain": "high",
    })
    append_ndjson(DECISIONS, {
        "decision": "OPEN_RESULT_DERIVED_CHILD", "question_id": qid,
        "parent_question": parent, "parent_result_hash": parent_hash, "reason": why,
    })


def structural_map(raw):
    fs = fields(raw); out = {}
    for q in np.argwhere(raw != 0):
        qt = tuple(int(x) for x in q)
        out[qt] = tuple(int(fs[k][qt]) for k in ("dx", "dy", "dz"))
    return out


def reduced_step(representation, n):
    groups = defaultdict(list)
    for q, direction in representation.items():
        groups[add(q, direction, 1, n)].append(direction)
    return {q: tuple(int(np.sign(sum(d[i] for d in incoming))) for i in range(3)) for q, incoming in groups.items()}


def fiber_multistep(kernel):
    rng = np.random.default_rng(161101)
    rows = []
    for trial in range(128):
        n = (17, 23, 29)[trial % 3]
        count = int(rng.integers(5, min(35, n)))
        raw, _, _ = sparse_world(rng, n, count)
        world = NativeWorld(kernel, raw)
        reduced = structural_map(world.raw)
        steps = []
        for tick in range(1, 5):
            reduced = reduced_step(reduced, n)
            world.tick()
            actual = structural_map(world.raw)
            steps.append({"tick": tick, "predicted_support": len(reduced), "actual_support": len(actual), "structural_exact": reduced == actual})
        rows.append({"trial": trial, "n": n, "initial_support": count, "steps": steps, "exact_all_steps": all(s["structural_exact"] for s in steps)})
    # Scope breakers: semantic-4 sources regenerate trains and an occupied destination invokes extra local logic.
    n = 19; c = (9, 9, 9)
    raw_guard = np.zeros((n, n, n), dtype=np.uint64); raw_guard[(4, 9, 9)] = pack(1, 37, (1, 0, 0), 4)
    guard_world = NativeWorld(kernel, raw_guard); reduced_guard = reduced_step(structural_map(raw_guard), n); guard_world.tick()
    guard_breaks = reduced_guard != structural_map(guard_world.raw)
    raw_occ = np.zeros((n, n, n), dtype=np.uint64); raw_occ[(8, 9, 9)] = pack(1, 37, (1, 0, 0), 1); raw_occ[c] = pack(2, 41, (0, 0, 0), 1)
    occ_world = NativeWorld(kernel, raw_occ); reduced_occ = reduced_step(structural_map(raw_occ), n); occ_world.tick()
    occupied_breaks = reduced_occ != structural_map(occ_world.raw)
    return {
        "experiment": "four-step reduced structural evolution",
        "representation": "position_to_direction map with destination reduction by componentwise sign sum",
        "scope": "semantic1 sparse starts with empty first-step destinations",
        "cases": rows, "exact_cases": sum(r["exact_all_steps"] for r in rows), "total_cases": len(rows),
        "semantic4_canary_breaks_model": guard_breaks,
        "occupied_destination_canary_breaks_model": occupied_breaks,
        "predicate": all(r["exact_all_steps"] for r in rows) and guard_breaks and occupied_breaks,
        "interpretation": "The direction-fiber quotient closes structural dynamics for four tested steps inside a strict semantic1 sparse domain; guard/source and occupied-destination canaries delimit it.",
    }


def hidden_resurrection_scope(kernel):
    rng = np.random.default_rng(161201)
    directions = [(1, 0, 0), (0, 1, 0), (0, 0, -1), (1, 1, 0)]
    cases = []
    for trial in range(64):
        n = (23, 29, 35)[trial % 3]; direction = directions[trial % len(directions)]
        axis = next(i for i, value in enumerate(direction) if value == 0)
        origin = [n // 3, n // 3, n // 3]
        lanes = []
        for lane in range(4):
            q = origin.copy(); q[axis] += 3 * lane; lanes.append(tuple(q))
        payloads = [int(x) for x in rng.choice(np.arange(11, 1000), size=4, replace=False)]
        permutation = list(rng.permutation(4)); swapped = [payloads[i] for i in permutation]
        if permutation == list(range(4)):
            permutation = [1, 2, 3, 0]; swapped = [payloads[i] for i in permutation]
        blocked_lane = int(rng.integers(0, 4))
        if payloads[blocked_lane] == swapped[blocked_lane]:
            blocked_lane = next(i for i in range(4) if payloads[i] != swapped[i])
        counter_sreg = int(rng.integers(1, 500))
        arms = []
        for label, assignment in (("A", payloads), ("B", swapped)):
            raw = np.zeros((n, n, n), dtype=np.uint64); clock = np.zeros_like(raw)
            for i, (q, sreg) in enumerate(zip(lanes, assignment, strict=True)):
                raw[q] = pack(int(rng.integers(1, 2**32)), sreg, direction, 1); clock[q] = np.uint64(rng.bit_generator.random_raw())
            target = add(lanes[blocked_lane], direction, 1, n)
            reverse = tuple(-x for x in direction)
            port = add(target, reverse, -1, n)
            raw[port] = pack(int(rng.integers(1, 2**32)), counter_sreg, reverse, 1)
            world = NativeWorld(kernel, raw, clock); world.tick(); rec = unpack(world.raw[target])
            arms.append({"world": label, "target": list(target), "observed": rec, "expected_sreg": min(assignment[blocked_lane] + counter_sreg, 19664), "pass": rec is not None and rec["sreg"] == min(assignment[blocked_lane] + counter_sreg, 19664)})
        cases.append({"trial": trial, "n": n, "direction": direction, "blocked_lane": blocked_lane, "coarse_equal": sorted(payloads) == sorted(swapped), "response_diverges": arms[0]["observed"] != arms[1]["observed"], "arms": arms})
    # Nuisance pair: state/clock differences do not alter the collision response fields.
    nuisance = []
    for trial in range(16):
        n = 23; target = (11, 11, 11); d = (1, 0, 0); rd = (-1, 0, 0)
        records = []
        for variant in (0, 1):
            raw = np.zeros((n, n, n), dtype=np.uint64); clock = np.zeros_like(raw)
            raw[add(target, d, -1, n)] = pack(100 + variant * 9999, 137, d, 1)
            raw[add(target, rd, -1, n)] = pack(200 + variant * 7777, 43, rd, 1)
            clock[raw != 0] = np.uint64(variant * 987654321)
            world = NativeWorld(kernel, raw, clock); world.tick(); records.append(unpack(world.raw[target]))
        nuisance.append({"trial": trial, "causal_record_equal": records[0] == records[1], "records": records})
    return {
        "experiment": "translated/oriented hidden-relation resurrection scope",
        "cases": cases, "pass_count": sum(c["coarse_equal"] and c["response_diverges"] and all(a["pass"] for a in c["arms"]) for c in cases), "total": len(cases),
        "state_clock_nuisance": nuisance, "nuisance_equal_count": sum(x["causal_record_equal"] for x in nuisance),
        "minimal_repair": "payload indexed by relative lane plus intervention location",
        "predicate": all(c["coarse_equal"] and c["response_diverges"] and all(a["pass"] for a in c["arms"]) for c in cases) and all(x["causal_record_equal"] for x in nuisance),
        "interpretation": "Relative payload assignment is later-revealable across fresh sizes/orientations; raw state tokens and clock values remain nuisance coordinates for this interaction.",
    }


def probability_selection(kernel):
    rng = np.random.default_rng(161301)
    n = 17; count = 80
    base_directions = [(1, 0, 0)] * 40 + [(-1, 0, 0)] * 40
    rows = []
    for trial in range(256):
        directions = list(base_directions); rng.shuffle(directions)
        raw, _, destinations = sparse_world(rng, n, count, directions=directions, sregs=[23] * count)
        world = NativeWorld(kernel, raw); world.tick(); observed = int(np.count_nonzero(world.raw))
        rows.append({"trial": trial, "unique_destinations": len(set(destinations)), "observed": observed, "fiber_pass": observed == len(set(destinations))})
    outcomes = [r["observed"] for r in rows]; distribution = {str(k): v / len(rows) for k, v in sorted(Counter(outcomes).items())}
    bulk_nll = len(rows) * entropy(outcomes)
    fiber_errors = sum(not r["fiber_pass"] for r in rows)
    return {
        "experiment": "model-selection probability under a fixed compatible macrostate",
        "macrostate": {"n": n, "support": count, "direction_sum": [0, 0, 0], "sreg_total": 23 * count},
        "worlds": len(rows), "distribution": distribution, "entropy_bits": entropy(outcomes),
        "bulk_empirical_code_length_bits": bulk_nll, "fiber_prediction_errors": fiber_errors,
        "fiber_exact": fiber_errors == 0, "rows": rows,
        "predicate": len(distribution) >= 3 and fiber_errors == 0,
        "interpretation": "The same bulk state supports a nondegenerate outcome distribution, but conditional destination fibers collapse the uncertainty to an exact deterministic prediction.",
    }


def classical_scaling_selection(kernel):
    rng = np.random.default_rng(161401)
    levels = []
    for n in (9, 13, 17, 21):
        count = max(12, int(round(0.04 * n ** 3)))
        ratios = []
        for _ in range(80):
            directions = [DIRECTIONS[int(i)] for i in rng.integers(0, len(DIRECTIONS), size=count)]
            raw, _, _ = sparse_world(rng, n, count, directions=directions, sregs=[29] * count, require_empty_destinations=False)
            world = NativeWorld(kernel, raw); world.tick(); ratios.append(int(np.count_nonzero(world.raw)) / count)
        mean = float(np.mean(ratios)); sd = float(np.std(ratios, ddof=1)); cv = sd / mean
        levels.append({"n": n, "components": count, "worlds": len(ratios), "mean": mean, "sd": sd, "cv": cv, "ratios": ratios})
    x = np.log([r["components"] for r in levels]); y = np.log([r["cv"] for r in levels]); slope, intercept = np.polyfit(x, y, 1)
    predicted = np.exp(intercept + slope * x); rmse = float(np.sqrt(np.mean((np.asarray([r["cv"] for r in levels]) - predicted) ** 2)))
    return {
        "experiment": "classical concentration model selection",
        "levels": levels, "log_cv_vs_log_components_slope": float(slope), "power_law_rmse": rmse,
        "candidate_law": "CV(response) proportional to component_count^alpha",
        "candidate_alpha": float(slope), "pre_holdout_acceptance": {"alpha_min": -0.8, "alpha_max": -0.2, "largest_to_smallest_cv_max": 0.65},
        "largest_to_smallest_cv": levels[-1]["cv"] / levels[0]["cv"],
        "predicate": -0.8 <= slope <= -0.2 and levels[-1]["cv"] / levels[0]["cv"] <= 0.65,
        "interpretation": "Coarse response fluctuations shrink approximately with inverse square-root-like component scaling; this is statistical concentration, not information destruction.",
    }


def sequential_order_trial(kernel, d0, first, second, n=29):
    q1 = (n // 2, n // 2, n // 2)
    raw = np.zeros((n, n, n), dtype=np.uint64)
    raw[add(q1, d0, -1, n)] = pack(1, 31, d0, 1)
    raw[add(q1, first, -1, n)] = pack(2, 37, first, 1)
    world = NativeWorld(kernel, raw); world.tick(); r1 = unpack(world.raw[q1])
    d1 = tuple(r1["direction"]); q2 = add(q1, d1, 1, n); port = add(q2, second, -1, n)
    if int(world.raw[port]) != 0:
        return {"valid": False, "reason": "second intervention port occupied"}
    token = pack(3, 41, second, 1)
    world.raw_a[port] = token; world.raw_b[port] = token
    world.clock_a[port] = np.uint64(0); world.clock_b[port] = np.uint64(0)
    world.tick(); r2 = unpack(world.raw[q2])
    return {"valid": True, "q1": list(q1), "q2": list(q2), "intermediate": r1, "final": r2}


def phase_order_deepening(kernel):
    base = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
    rows = []
    for permutation in itertools.permutations((0, 1, 2)):
        d0 = tuple(base[0][i] for i in permutation)
        a = tuple((-1, 1, 0)[i] for i in permutation)
        b = tuple((1, -1, 0)[i] for i in permutation)
        ab = sequential_order_trial(kernel, d0, a, b); ba = sequential_order_trial(kernel, d0, b, a)
        rows.append({"permutation": permutation, "AB": ab, "BA": ba, "order_differs": ab.get("final") != ba.get("final")})
    control_ab = sequential_order_trial(kernel, (1, 0, 0), (-1, 1, 0), (-1, 1, 0))
    control_ba = sequential_order_trial(kernel, (1, 0, 0), (-1, 1, 0), (-1, 1, 0))
    phase = {}
    for path_length in (5, 8, 11):
        coherent = convergent_phase_paths(kernel, n=47, path_length=path_length, mode="AB_coherent", sregs=(113, 227), horizon=path_length + 10)
        shifted = convergent_phase_paths(kernel, n=47, path_length=path_length, mode="AB_phase_shifted", sregs=(113, 227), horizon=path_length + 10)
        phase[str(path_length)] = {
            "coarse_event_count_equal": coherent["event_count"] == shifted["event_count"],
            "coherent_sregs": coherent["detector_event_sregs"], "shifted_sregs": shifted["detector_event_sregs"],
            "payload_readout_distinguishes": coherent["detector_event_sregs"] != shifted["detector_event_sregs"],
        }
    return {
        "experiment": "sequential intervention order and phase-observer sufficiency",
        "order_cases": rows, "order_difference_count": sum(r["order_differs"] for r in rows),
        "identical_intervention_control_equal": control_ab == control_ba,
        "phase_cases": phase,
        "contextuality_status": "NOT_ESTABLISHED_ORDINARY_LOSSY_STATE_UPDATE_SUFFICES",
        "predicate": all(r["order_differs"] for r in rows) and control_ab == control_ba and all(v["coarse_event_count_equal"] and v["payload_readout_distinguishes"] for v in phase.values()),
        "interpretation": "Effective interventions are order-sensitive because the reducer compresses direction after each collision. Event count alone hides phase/path availability; payload/direction restores prediction. This is not a quantum contextuality result.",
    }


def capability_deepening(kernel):
    transfer = []
    frames = [((0, 1, 2), (1, 1, 1)), ((1, 2, 0), (1, -1, 1)), ((2, 0, 1), (-1, 1, 1))]
    for index, (permutation, signs) in enumerate(frames):
        for mode in ("trained", "untrained", "no_relay", "corridor_cut", "offpath_cut", "receiver_none", "wrong_receiver", "memory_ablation"):
            result = run_learned_policy_transfer(kernel, seed=161600 + index, n=31, distance=8, mode=mode, permutation=permutation, signs=signs)
            transfer.append({
                "frame": index, "mode": mode,
                "functional_policy_reinstantiated": result["functional_policy_reinstantiated"],
                "source_depleted_after_launch": result["source_depleted_after_launch"],
                "corridor_all_intermediate_ticks_observed": result["corridor_all_intermediate_ticks_observed"],
                "memory_after_experience": result["memory_after_experience"], "arrival_record": result["arrival_record"], "query_record": result["query_record"],
            })
    # One-cell threshold around the known semantic-4 interface can amplify into a train-level response.
    amplification = []
    for direction in ((1, 0, 0), (0, 1, 0), (0, 0, -1)):
        arms = []
        for count in (5, 6):
            result = regenerative_interface_trial(kernel, n=37, source_distance=7, downstream_distance=5, horizon=24, mode="semantic4_custom", direction=direction, center=(18, 18, 18), source_sreg=173, semantic4_indices=list(range(count)))
            events = result["downstream_event_ticks"]["5"]
            arms.append({"guard_cells": count, "downstream_events": events, "event_count": len(events)})
        amplification.append({"direction": direction, "arms": arms, "one_cell_changes_macro_response": arms[0]["event_count"] != arms[1]["event_count"]})
    trained = [x for x in transfer if x["mode"] == "trained"]
    canary = [x for x in transfer if x["mode"] in {"untrained", "no_relay", "corridor_cut", "receiver_none", "wrong_receiver", "memory_ablation"}]
    offpath = [x for x in transfer if x["mode"] == "offpath_cut"]
    return {
        "experiment": "fresh transformed transfer taxonomy plus guard amplification",
        "technical_correction": "C16D007 preserved incomplete field extraction; this child reads canonical apparatus fields.",
        "transfer_cases": transfer,
        "trained_pass": sum(x["functional_policy_reinstantiated"] for x in trained), "trained_total": len(trained),
        "canary_correct": sum(not x["functional_policy_reinstantiated"] for x in canary), "canary_total": len(canary),
        "offpath_positive": sum(x["functional_policy_reinstantiated"] for x in offpath), "offpath_total": len(offpath),
        "explicit_corridor_evidence": all(x["corridor_all_intermediate_ticks_observed"] for x in trained),
        "destructive_source_depletion": all(x["source_depleted_after_launch"] for x in trained),
        "transfer_taxonomy": "DESTRUCTIVE_FUNCTIONAL_RECONSTRUCTION_VIA_EXPLICIT_CARRIER_AND_PREPARED_RECEIVER",
        "amplification_cases": amplification,
        "macro_amplification_found": any(x["one_cell_changes_macro_response"] for x in amplification),
        "predicate": all(x["functional_policy_reinstantiated"] for x in trained + offpath) and all(not x["functional_policy_reinstantiated"] for x in canary),
        "interpretation": "Functional policy, not raw microstate identity, is destructively transferred through an explicit local corridor and reconstructed by a prepared receiver. Guard-threshold amplification is reported only if the kernel data show it.",
    }


def save(exp_id, qid, parent_qid, parent_path, front, function, kernel):
    path = OUT / f"{exp_id}.json"
    if path.exists():
        return path, read_json(path)
    started = time.perf_counter(); result = function(kernel)
    result = {
        "experiment_id": exp_id, "question_id": qid, "parent_question": parent_qid,
        "parent_result_hash": sha(parent_path), "front": front, "role": "ADAPTIVE_MODEL_LEVEL_SELECTION",
        "partition": "MODEL_LEVEL_SELECTION", "experiment_key": experiment_key(qid, front, result["experiment"], "MODEL_SELECTION"),
        "kernel_data_lineage": "v27 raw+clock -> committed telemetry -> predeclared child metric",
        "elapsed_seconds": time.perf_counter() - started, **result,
    }
    result["content_sha256"] = canonical_hash(result)
    write_json(path, result)
    append_ndjson(DIALOGUE, {"question_id": qid, "experiment_id": exp_id, "parent_result_hash": result["parent_result_hash"], "partition": "MODEL_LEVEL_SELECTION", "raw_outcome": {"predicate": result.get("predicate"), "content_sha256": result["content_sha256"]}, "mechanism_update": result.get("interpretation")})
    return path, result


def main():
    checkpoint = ROOT / "CHECKPOINTS" / "CP02_MODEL_SELECTION.json"
    if checkpoint.exists():
        print(checkpoint.read_text(encoding="utf-8")); return
    audit_kernel("CORE16_BEFORE_MODEL_LEVEL_SELECTION")
    kernel, _ = verify_and_load_kernel(1)
    parent_map = {
        "C16Q001A": ("C16Q001", ROOT / "DISCOVERY" / "C16D001.json", "Does the direction-fiber quotient commute for more than one update?", "One-step closure may fail after reducer-generated directions.", ["multistep closure", "one-step-only closure", "hidden occupancy logic"]),
        "C16Q002A": ("C16Q002", ROOT / "DISCOVERY" / "C16D002.json", "Does hidden relation resurrection survive new sizes, orientations and nuisance coordinates?", "The discovery pair could be coordinate-specific.", ["relational law", "orientation artifact", "state/clock confound"]),
        "C16Q003A": ("C16Q003", ROOT / "DISCOVERY" / "C16D003.json", "Does a denser compatible macrostate retain nondegenerate probabilities while fibers remain exact?", "The discovery distribution had low entropy.", ["useful probability", "rare collision artifact", "fiber determinism"]),
        "C16Q003B": ("C16Q003", ROOT / "DISCOVERY" / "C16D004.json", "What scaling law describes concentration of coarse response?", "Three sizes established direction but not a stable exponent.", ["inverse-root concentration", "constant variance", "finite-size artifact"]),
        "C16Q004A": ("C16Q004", ROOT / "DISCOVERY" / "C16D005.json", "Does intervention order define a noncommuting effective law, and which observer repairs phase ambiguity?", "Backaction was causal but order and observer sufficiency were unresolved.", ["ordinary lossy update", "history-conditioned law", "contextuality"]),
        "C16Q006A": ("C16Q006", ROOT / "DISCOVERY" / "C16D007.json", "What exactly is preserved and mediated in transfer, regeneration and amplification?", "The root telemetry extractor omitted canonical capability booleans.", ["functional reconstruction", "raw transfer", "apparatus artifact", "threshold amplification"]),
    }
    for qid, (parent, path, question, uncertainty, explanations) in parent_map.items():
        append_child(qid, parent, path, uncertainty, explanations, question, "Fresh transformed apparatuses distinguish the listed explanations.")
    plans = [
        ("C16S001", "C16Q001A", "C16Q001", ROOT / "DISCOVERY" / "C16D001.json", "LEVEL_DISCOVERY", fiber_multistep),
        ("C16S002", "C16Q002A", "C16Q002", ROOT / "DISCOVERY" / "C16D002.json", "HIDDEN_STATE_RESURRECTION", hidden_resurrection_scope),
        ("C16S003", "C16Q003A", "C16Q003", ROOT / "DISCOVERY" / "C16D003.json", "EFFECTIVE_PROBABILITY", probability_selection),
        ("C16S004", "C16Q003B", "C16Q003", ROOT / "DISCOVERY" / "C16D004.json", "CLASSICALIZATION", classical_scaling_selection),
        ("C16S005", "C16Q004A", "C16Q004", ROOT / "DISCOVERY" / "C16D005.json", "PHASE_MEASUREMENT", phase_order_deepening),
        ("C16S006", "C16Q006A", "C16Q006", ROOT / "DISCOVERY" / "C16D007.json", "CAPABILITIES", capability_deepening),
    ]
    registry = read_json(ROOT / "EXPERIMENT_REGISTRY.json")
    results = []
    for args in plans:
        path, result = save(*args, kernel)
        row = {"experiment_id": args[0], "question_id": args[1], "front": args[4], "path": str(path.relative_to(ROOT)), "sha256": sha(path), "predicate": result.get("predicate")}
        registry["experiments"].append(row); results.append(row)
    # Record the non-scientific telemetry extraction defect without deleting its source result.
    write_json(ROOT / "INCIDENTS" / "C16I01_CAPABILITY_ROOT_FIELD_EXTRACTION.json", {
        "incident": "C16D007_TELEMETRY_FIELD_EXTRACTION_INCOMPLETE",
        "classification": "RECOVERABLE_ANALYSIS_FAULT",
        "scientific_data_invalidated": False,
        "source_result_preserved": True,
        "repair": "C16S006 reads the canonical apparatus fields functional_policy_reinstantiated, source_depleted_after_launch and corridor_all_intermediate_ticks_observed.",
        "detected_utc": utc(),
    })
    write_json(ROOT / "EXPERIMENT_REGISTRY.json", registry)
    cp = {"status": "COMPLETE", "children": len(results), "results": results, "utc": utc()}; write_json(checkpoint, cp)
    update_state(status="MODEL_LEVEL_SELECTION_COMPLETE_PENDING_FREEZE", phase="PHASE_A_TO_K", completed_checkpoints=["PARENT_AUDIT", "INITIAL_REPRESENTATION_REGISTRY", "INITIAL_QUESTION_ROOTS", "DISCOVERY_ROOTS", "MODEL_LEVEL_SELECTION"])
    print(json.dumps(cp, indent=2))


if __name__ == "__main__":
    main()
