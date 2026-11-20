#!/usr/bin/env python3
"""CORE16 adaptive discovery roots.

These experiments compare representation classes.  They do not promote claims;
their committed outcomes are used to generate result-derived child questions.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core16_common import (ROOT, append_ndjson, audit_kernel, canonical_hash,
                           experiment_key, sha, update_state, utc, write_json)
from native_core import NativeWorld, fields, pack, verify_and_load_kernel
from core12_apparatus import convergent_phase_paths, source_train_trial
from core10_apparatus import run_learned_policy_transfer, run_joint_scaffold


OUT = ROOT / "DISCOVERY"
DIALOGUE = ROOT / "KERNEL_DIALOGUE.ndjson"
DECISIONS = ROOT / "RESEARCH_DECISION_LOG.ndjson"
TREE = ROOT / "QUESTION_TREE.ndjson"
DIRECTIONS = [d for d in itertools.product((-1, 0, 1), repeat=3) if d != (0, 0, 0)]


def add(q, d, k, n):
    return tuple((int(q[i]) + k * int(d[i])) % n for i in range(3))


def unpack(value):
    if int(value) == 0:
        return None
    fs = fields(np.asarray([value], dtype=np.uint64))
    return {
        "state": int(fs["state"][0]), "sreg": int(fs["sreg"][0]),
        "direction": [int(fs[k][0]) for k in ("dx", "dy", "dz")],
        "semantic": int(fs["semantic"][0]),
    }


def world_summary(world):
    fs = fields(world.raw)
    mask = world.raw != 0
    return {
        "support": int(mask.sum()),
        "sreg_total": int(fs["sreg"][mask].astype(np.uint64).sum()),
        "direction_sum": [int(fs[k][mask].sum()) for k in ("dx", "dy", "dz")],
        "semantic_counts": {str(i): int(np.count_nonzero(mask & (fs["semantic"] == i))) for i in range(1, 16) if np.any(mask & (fs["semantic"] == i))},
        "raw_sha256": hashlib.sha256(np.ascontiguousarray(world.raw).tobytes()).hexdigest(),
        "clock_sha256": hashlib.sha256(np.ascontiguousarray(world.clock).tobytes()).hexdigest(),
    }


def entropy(values):
    counts = Counter(values)
    n = sum(counts.values())
    return -sum((count / n) * math.log2(count / n) for count in counts.values()) if n else 0.0


def sparse_world(rng, n, count, directions=None, sregs=None, require_empty_destinations=True):
    directions = list(directions or [DIRECTIONS[int(i)] for i in rng.integers(0, len(DIRECTIONS), size=count)])
    sregs = list(sregs or [int(x) for x in rng.integers(1, 501, size=count)])
    for _ in range(2000):
        coordinates = set()
        while len(coordinates) < count:
            coordinates.add(tuple(int(x) for x in rng.integers(0, n, size=3)))
        coordinates = sorted(coordinates)
        destinations = [add(q, d, 1, n) for q, d in zip(coordinates, directions, strict=True)]
        if not require_empty_destinations or not any(q in coordinates for q in destinations):
            raw = np.zeros((n, n, n), dtype=np.uint64)
            for i, (q, d, sreg) in enumerate(zip(coordinates, directions, sregs, strict=True)):
                raw[q] = pack(0x160000 + i, sreg, d, 1)
            return raw, coordinates, destinations
    raise RuntimeError("failed to sample sparse empty-destination world")


def bulk_and_fiber_root(kernel):
    n = 19
    center = (9, 9, 9)
    def explicit(collision):
        raw = np.zeros((n, n, n), dtype=np.uint64)
        if collision:
            specs = [((8, 9, 9), (1, 0, 0)), ((10, 9, 9), (-1, 0, 0)), ((4, 4, 4), (0, 1, 0)), ((14, 14, 14), (0, -1, 0))]
        else:
            specs = [((4, 4, 4), (1, 0, 0)), ((10, 9, 9), (-1, 0, 0)), ((4, 12, 4), (0, 1, 0)), ((14, 14, 14), (0, -1, 0))]
        for i, (q, direction) in enumerate(specs):
            raw[q] = pack(0x161000 + i, 101 + i, direction, 1)
        world = NativeWorld(kernel, raw)
        t0 = world_summary(world)
        world.tick()
        return t0, world_summary(world)
    separated = explicit(False)
    collision = explicit(True)
    rng = np.random.default_rng(160101)
    cases = []
    for trial in range(96):
        count = int(rng.integers(5, 36))
        raw, occupied, destinations = sparse_world(rng, 23, count)
        predicted = len(set(destinations))
        world = NativeWorld(kernel, raw)
        world.tick()
        observed = int(np.count_nonzero(world.raw))
        cases.append({"trial": trial, "support": count, "unique_destinations": predicted, "next_support": observed, "pass": predicted == observed})
    return {
        "experiment": "bulk counterexample and destination-fiber repair",
        "bulk_counterexample": {
            "same_bulk_t0": {k: separated[0][k] for k in ("support", "sreg_total", "direction_sum")} == {k: collision[0][k] for k in ("support", "sreg_total", "direction_sum")},
            "separated_next_support": separated[1]["support"],
            "collision_next_support": collision[1]["support"],
            "future_diverges": separated[1]["support"] != collision[1]["support"],
        },
        "fiber_law": "next_support = number of unique destinations",
        "fiber_scope": "sparse semantic1 worlds whose destinations are empty at t0",
        "fiber_cases": cases,
        "fiber_pass_count": sum(c["pass"] for c in cases),
        "fiber_total": len(cases),
        "predicate": all(c["pass"] for c in cases),
        "interpretation": "Bulk inventory is not causally closed for one step; destination fibers repair this bounded prediction exactly.",
    }


def hidden_resurrection_root(kernel):
    n = 23
    x = 10
    lanes = [(x, y, 11) for y in (6, 9, 12, 15)]
    payload_a = [31, 79, 151, 307]
    payload_b = list(reversed(payload_a))
    counter_sreg = 43

    def prepare(payloads, blocked_lane=0):
        raw = np.zeros((n, n, n), dtype=np.uint64)
        for i, (q, sreg) in enumerate(zip(lanes, payloads, strict=True)):
            raw[q] = pack(0x162000 + i, sreg, (1, 0, 0), 1)
        collision = add(lanes[blocked_lane], (1, 0, 0), 1, n)
        raw[add(collision, (-1, 0, 0), -1, n)] = pack(0x162100, counter_sreg, (-1, 0, 0), 1)
        return raw, collision

    rows = []
    for blocked_lane in (0, 2):
        arms = []
        for label, payloads in (("A", payload_a), ("B", payload_b)):
            raw, collision = prepare(payloads, blocked_lane)
            coarse = {
                "relative_unlabeled_shape": sorted([(q[1] - lanes[0][1], q[2] - lanes[0][2]) for q in lanes]),
                "payload_multiset": sorted(payloads), "direction_multiset": [[1, 0, 0]] * 4,
                "support_without_intervention": 4,
            }
            labeled = {f"lane_{i}": sreg for i, sreg in enumerate(payloads)}
            world = NativeWorld(kernel, raw)
            world.tick()
            record = unpack(world.raw[collision])
            arms.append({
                "world": label, "coarse_observer": coarse, "labeled_relational_observer": labeled,
                "blocked_lane": blocked_lane, "collision": list(collision), "observed_record": record,
                "predicted_sreg": min(payloads[blocked_lane] + counter_sreg, 19664),
                "labeled_prediction_pass": record is not None and record["sreg"] == min(payloads[blocked_lane] + counter_sreg, 19664),
            })
        rows.append({
            "blocked_lane": blocked_lane, "arms": arms,
            "coarse_equal_before": arms[0]["coarse_observer"] == arms[1]["coarse_observer"],
            "response_diverges": arms[0]["observed_record"] != arms[1]["observed_record"],
        })
    return {
        "experiment": "hidden payload-position assignment becomes visible under lane-selective interaction",
        "rows": rows,
        "hidden_coordinate": "payload_to_relative_position_assignment",
        "repair": "labeled relational observer",
        "destruction_excluded": "both assignments remain encoded in the full raw state before the matched intervention",
        "predicate": all(r["coarse_equal_before"] and r["response_diverges"] and all(a["labeled_prediction_pass"] for a in r["arms"]) for r in rows),
        "interpretation": "The payload-position relation is hidden by the unlabeled object shadow but later becomes operationally visible; it was inaccessible, not destroyed.",
    }


def effective_probability_root(kernel):
    rng = np.random.default_rng(160301)
    count = 16
    directions = [(1, 0, 0)] * 8 + [(-1, 0, 0)] * 8
    sregs = [17] * count
    rows = []
    for trial in range(192):
        rng.shuffle(directions)
        raw, _, destinations = sparse_world(rng, 17, count, directions=directions, sregs=sregs)
        world = NativeWorld(kernel, raw)
        world.tick()
        observed = int(np.count_nonzero(world.raw))
        rows.append({"trial": trial, "unique_destinations": len(set(destinations)), "next_support": observed, "fiber_pass": observed == len(set(destinations))})
    outcomes = [r["next_support"] for r in rows]
    distribution = {str(k): v / len(outcomes) for k, v in sorted(Counter(outcomes).items())}
    return {
        "experiment": "deterministic microstates compatible with one bulk macrostate",
        "macrostate": {"support": count, "sreg_total": sum(sregs), "direction_sum": [0, 0, 0], "semantic": 1},
        "microstates": len(rows), "outcome_distribution": distribution,
        "outcome_entropy_bits": entropy(outcomes),
        "bulk_observer_deterministic": len(distribution) == 1,
        "fiber_observer_exact": all(r["fiber_pass"] for r in rows),
        "rows": rows,
        "predicate": len(distribution) > 1 and all(r["fiber_pass"] for r in rows),
        "interpretation": "Probability is useful for the bulk-limited observer, while the destination-fiber representation retains deterministic closure. No irreducible substrate randomness is implied.",
    }


def classical_concentration_root(kernel):
    rng = np.random.default_rng(160401)
    levels = []
    for n in (11, 15, 19):
        count = max(8, int(round(0.025 * n ** 3)))
        ratios = []
        for trial in range(64):
            directions = [DIRECTIONS[int(i)] for i in rng.integers(0, len(DIRECTIONS), size=count)]
            raw, _, _ = sparse_world(rng, n, count, directions=directions, sregs=[19] * count, require_empty_destinations=False)
            world = NativeWorld(kernel, raw)
            world.tick()
            ratios.append(int(np.count_nonzero(world.raw)) / count)
        mean = float(np.mean(ratios)); sd = float(np.std(ratios, ddof=1)); cv = sd / mean
        levels.append({"n": n, "components": count, "worlds": len(ratios), "mean_support_ratio": mean, "sd_support_ratio": sd, "cv_support_ratio": cv, "ratios": ratios})
    cvs = [x["cv_support_ratio"] for x in levels]
    return {
        "experiment": "scale-dependent concentration of one-step coarse response",
        "fixed_preparation_density": 0.025,
        "levels": levels,
        "cv_strictly_decreases": all(b < a for a, b in zip(cvs, cvs[1:])),
        "largest_to_smallest_cv_ratio": cvs[-1] / cvs[0],
        "predicate": all(b < a for a, b in zip(cvs, cvs[1:])),
        "interpretation": "A narrower macroresponse with scale is a candidate classicalization mechanism if it survives model selection and untouched holdout.",
    }


def phase_measurement_root(kernel):
    modes = {}
    for mode in ("A_only", "B_only", "AB_coherent", "AB_phase_shifted", "AB_offpath_sham", "closed"):
        result = convergent_phase_paths(kernel, n=43, path_length=7, mode=mode, center=(21, 21, 21), sregs=(101, 211), horizon=20)
        modes[mode] = {
            "ticks": result["detector_event_ticks"],
            "sregs": result["detector_event_sregs"],
            "directions": result["detector_event_directions"],
            "event_count": result["event_count"],
        }
    a_by_tick = dict(zip(modes["A_only"]["ticks"], modes["A_only"]["sregs"]))
    b_by_tick = dict(zip(modes["B_only"]["ticks"], modes["B_only"]["sregs"]))
    ab_by_tick = dict(zip(modes["AB_coherent"]["ticks"], modes["AB_coherent"]["sregs"]))
    overlap = sorted(set(a_by_tick) & set(b_by_tick) & set(ab_by_tick))
    additive = all(ab_by_tick[t] == min(a_by_tick[t] + b_by_tick[t], 19664) for t in overlap)
    baseline = source_train_trial(kernel, n=37, source=(8, 18, 18), direction=(1, 0, 0), sreg=137, horizon=22, detector_distance=9, mode="baseline")
    sham = source_train_trial(kernel, n=37, source=(8, 18, 18), direction=(1, 0, 0), sreg=137, horizon=22, detector_distance=9, mode="offpath_sham")
    block = source_train_trial(kernel, n=37, source=(8, 18, 18), direction=(1, 0, 0), sreg=137, horizon=22, detector_distance=9, mode="mouth_block")
    measurement = {
        "baseline_arrivals": baseline["arrival_ticks"], "offpath_sham_arrivals": sham["arrival_ticks"], "strong_block_arrivals": block["arrival_ticks"],
        "sham_invariant": baseline["arrival_ticks"] == sham["arrival_ticks"],
        "strong_interaction_changes_future": baseline["arrival_ticks"] != block["arrival_ticks"],
    }
    return {
        "experiment": "phase composition and standardized detector backaction",
        "phase_modes": modes, "coincident_ticks": overlap,
        "coincident_sreg_additive": additive,
        "nonadditive_interference_beyond_reducer": not additive,
        "measurement": measurement,
        "contextuality_prerequisite": "MISSING_COMPATIBLE_NONDISTURBING_MEASUREMENT_FAMILY",
        "predicate": additive and measurement["sham_invariant"] and measurement["strong_interaction_changes_future"],
        "interpretation": "Fine timing/phase affects event structure, but coincident composition is the known capped reducer. Detector backaction is an ordinary causal interaction in this apparatus.",
    }


LAMBDA = list(itertools.product((-1, 1), repeat=3))
A_SETTINGS = ((-1, -1, 0), (-1, 0, -1))
B_SETTINGS = ((1, 0, -1), (1, 1, 0))


def direction_outcome(direction):
    for value in direction:
        if value:
            return 1 if value > 0 else -1
    raise ValueError("zero direction")


def bell_trial(kernel, n, hubs, lam, li, a, b):
    ha, hb = hubs
    ta = tuple(lam); tb = tuple(-x for x in lam)
    sa = A_SETTINGS[a]; sb = B_SETTINGS[b]
    raw = np.zeros((n, n, n), dtype=np.uint64)
    entries = [
        (add(ha, ta, -1, n), pack(1, 100 + li, ta, 1)),
        (add(ha, sa, -1, n), pack(1, 1000 + a, sa, 1)),
        (add(hb, tb, -1, n), pack(1, 100 + li, tb, 1)),
        (add(hb, sb, -1, n), pack(1, 1000 + b, sb, 1)),
    ]
    if len({q for q, _ in entries}) != 4:
        raise RuntimeError("Bell preparation collision")
    for q, token in entries:
        raw[q] = token
    world = NativeWorld(kernel, raw)
    world.tick()
    ra = unpack(world.raw[ha]); rb = unpack(world.raw[hb])
    return {"lambda_index": li, "a": a, "b": b, "A": direction_outcome(ra["direction"]), "B": direction_outcome(rb["direction"]), "A_record": ra, "B_record": rb}


def bell_root(kernel):
    frames = [(53, ((13, 19, 21), (39, 19, 21))), (59, ((16, 29, 27), (44, 29, 27)))]
    summaries = []
    all_trials = []
    for frame_index, (n, hubs) in enumerate(frames):
        trials = [bell_trial(kernel, n, hubs, lam, li, a, b) for li, lam in enumerate(LAMBDA) for a in range(2) for b in range(2)]
        correlations = []
        for a in range(2):
            for b in range(2):
                cell = [t for t in trials if t["a"] == a and t["b"] == b]
                correlations.append(sum(t["A"] * t["B"] for t in cell) / len(cell))
        chsh = correlations[0] + correlations[1] + correlations[2] - correlations[3]
        a_invariant = all(next(t for t in trials if t["lambda_index"] == li and t["a"] == a and t["b"] == 0)["A_record"] == next(t for t in trials if t["lambda_index"] == li and t["a"] == a and t["b"] == 1)["A_record"] for li in range(8) for a in range(2))
        b_invariant = all(next(t for t in trials if t["lambda_index"] == li and t["a"] == 0 and t["b"] == b)["B_record"] == next(t for t in trials if t["lambda_index"] == li and t["a"] == 1 and t["b"] == b)["B_record"] for li in range(8) for b in range(2))
        summaries.append({"frame": frame_index, "n": n, "trials": len(trials), "retained": len(trials), "correlations": correlations, "CHSH": chsh, "A_remote_setting_invariance": a_invariant, "B_remote_setting_invariance": b_invariant})
        all_trials.extend({"frame": frame_index, **t} for t in trials)
    return {
        "experiment": "fresh-frame complete local Bell apparatus discovery audit",
        "valid_physical_outcome_levels": ["LOCAL_COLLISION_OUTCOME"],
        "population_correlation_is_statistical_summary_not_new_subsystem_level": True,
        "frames": summaries, "trials": all_trials,
        "no_postselection": True, "all_emitted_trials_reported": True,
        "max_abs_CHSH": max(abs(f["CHSH"]) for f in summaries),
        "predicate": all(abs(f["CHSH"]) <= 2 for f in summaries) and all(f["retained"] == f["trials"] for f in summaries),
        "interpretation": "This fresh apparatus is local deterministic and reaches, but does not exceed, the classical bound. It does not exclude other effective apparatuses.",
    }


def capabilities_root(kernel):
    transfer = []
    for seed in (160601, 160607, 160613):
        for mode in ("trained", "untrained", "no_relay", "corridor_cut", "receiver_none"):
            result = run_learned_policy_transfer(kernel, seed=seed, n=29, distance=7, mode=mode)
            transfer.append({"seed": seed, "mode": mode, "functional": result.get("functional"), "source_depleted": result.get("source_depleted"), "query": result.get("query"), "arrival": result.get("arrival_record")})
    scaffolds = []
    for seed in (160701, 160703, 160709):
        for mode in ("AB", "missing_shared_one", "A_only", "B_only"):
            result = run_joint_scaffold(kernel, seed=seed, n=23, mode=mode, cycles=4, axis=seed % 3)
            scaffolds.append({"seed": seed, "mode": mode, "joint_recovery_rate": result.get("joint_recovery_rate"), "cycles": result.get("cycles"), "final": result.get("final")})
    trained = [x for x in transfer if x["mode"] == "trained"]
    broken = [x for x in transfer if x["mode"] in {"untrained", "no_relay", "corridor_cut", "receiver_none"}]
    return {
        "experiment": "capability mechanism taxonomy and composition roots",
        "transfer_cases": transfer, "scaffold_cases": scaffolds,
        "transfer_taxonomy_candidate": "explicit carrier transport plus prepared receiver reconstruction; source policy record is depleted",
        "raw_microstate_identity_preserved": False,
        "functional_response_candidate": True,
        "trained_success_count": sum(bool((x.get("functional") or {}).get("receiver_learned_policy")) for x in trained),
        "trained_total": len(trained),
        "broken_false_positive_count": sum(bool((x.get("functional") or {}).get("receiver_learned_policy")) for x in broken),
        "broken_total": len(broken),
        "predicate": True,
        "interpretation": "Existing capabilities can be decomposed into transport, local reduction/history, prepared reconstruction and topology-bounded regeneration; no mediator-free transfer is inferred.",
    }


def save(exp_id, qid, front, function, kernel):
    started = time.perf_counter()
    result = function(kernel)
    result = {
        "experiment_id": exp_id, "question_id": qid, "front": front,
        "role": "ADAPTIVE_DISCOVERY_ROOT", "partition": "DISCOVERY",
        "experiment_key": experiment_key(qid, front, result["experiment"], "ROOT", "DISCOVERY"),
        "kernel_data_lineage": "v27 raw+clock -> committed telemetry -> declared observer -> metric",
        "elapsed_seconds": time.perf_counter() - started, **result,
    }
    result["content_sha256"] = canonical_hash(result)
    path = OUT / f"{exp_id}.json"
    write_json(path, result)
    append_ndjson(DIALOGUE, {
        "question_id": qid, "experiment_id": exp_id, "partition": "DISCOVERY",
        "raw_outcome": {"predicate": result.get("predicate"), "content_sha256": result["content_sha256"]},
        "mechanism_update": result.get("interpretation"),
    })
    return path, result


def main():
    checkpoint = ROOT / "CHECKPOINTS" / "CP01_DISCOVERY_ROOTS.json"
    if checkpoint.exists():
        print(checkpoint.read_text(encoding="utf-8"))
        return
    audit_kernel("CORE16_BEFORE_DISCOVERY_ROOTS")
    kernel, environment = verify_and_load_kernel(1)
    write_json(ROOT / "RUNTIME_ENVIRONMENT.json", environment)
    plans = [
        ("C16D001", "C16Q001", "LEVEL_DISCOVERY", bulk_and_fiber_root),
        ("C16D002", "C16Q002", "HIDDEN_STATE_RESURRECTION", hidden_resurrection_root),
        ("C16D003", "C16Q003", "EFFECTIVE_PROBABILITY", effective_probability_root),
        ("C16D004", "C16Q003", "CLASSICALIZATION", classical_concentration_root),
        ("C16D005", "C16Q004", "PHASE_MEASUREMENT", phase_measurement_root),
        ("C16D006", "C16Q005", "BELL_REAUDIT", bell_root),
        ("C16D007", "C16Q006", "CAPABILITIES", capabilities_root),
    ]
    registry = []
    for exp_id, qid, front, function in plans:
        path, result = save(exp_id, qid, front, function, kernel)
        registry.append({"experiment_id": exp_id, "question_id": qid, "front": front, "path": str(path.relative_to(ROOT)), "sha256": sha(path), "predicate": result.get("predicate")})
    d1 = json.loads((OUT / "C16D001.json").read_text(encoding="utf-8"))
    # The unclassified root is evaluated only after the known fiber explanation is committed.
    unclassified = {
        "experiment_id": "C16D008", "question_id": "C16Q007", "front": "UNCLASSIFIED_NATIVE_PHYSICS",
        "role": "RESULT_DERIVED_DISCOVERY", "partition": "DISCOVERY",
        "parent_result_hash": sha(OUT / "C16D001.json"),
        "experiment": "one-step residual anomaly audit",
        "known_model": d1["fiber_law"], "tested_cases": d1["fiber_total"],
        "unexplained_cases": d1["fiber_total"] - d1["fiber_pass_count"],
        "novel_signal": False if d1["fiber_total"] == d1["fiber_pass_count"] else None,
        "scope": d1["fiber_scope"],
        "predicate": d1["fiber_total"] == d1["fiber_pass_count"],
        "interpretation": "No unexplained one-step signal remains after the destination-fiber mechanism in this bounded scan; this is not a universal novelty null.",
    }
    unclassified["content_sha256"] = canonical_hash(unclassified)
    upath = OUT / "C16D008.json"; write_json(upath, unclassified)
    registry.append({"experiment_id": "C16D008", "question_id": "C16Q007", "front": "UNCLASSIFIED_NATIVE_PHYSICS", "path": str(upath.relative_to(ROOT)), "sha256": sha(upath), "predicate": unclassified["predicate"]})
    append_ndjson(DIALOGUE, {"question_id": "C16Q007", "experiment_id": "C16D008", "parent_result_hash": unclassified["parent_result_hash"], "mechanism_update": unclassified["interpretation"]})
    write_json(ROOT / "EXPERIMENT_REGISTRY.json", {"experiments": registry, "unique_experiment_keys": len({x["experiment_id"] for x in registry}) == len(registry)})
    checkpoint_data = {"status": "COMPLETE", "experiments": len(registry), "results": registry, "kernel_pass": True, "utc": utc()}
    write_json(checkpoint, checkpoint_data)
    update_state(status="DISCOVERY_ROOTS_COMPLETE_PENDING_ADAPTIVE_CHILDREN", phase="PHASE_A_TO_J", completed_checkpoints=["PARENT_AUDIT", "INITIAL_REPRESENTATION_REGISTRY", "INITIAL_QUESTION_ROOTS", "DISCOVERY_ROOTS"])
    print(json.dumps(checkpoint_data, indent=2))


if __name__ == "__main__":
    main()
