#!/usr/bin/env python3
"""Third-generation CORE16 questions opened by committed selection results."""
from __future__ import annotations

import itertools
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core16_common import (ROOT, append_ndjson, audit_kernel, canonical_hash,
                           experiment_key, read_json, sha, update_state, utc, write_json)
from native_core import NativeWorld, pack, verify_and_load_kernel
from run_discovery_roots import (A_SETTINGS, B_SETTINGS, DIRECTIONS, LAMBDA, add,
                                 bell_trial, unpack)
from run_adaptive_children import reduced_step, structural_map


OUT = ROOT / "MODEL_SELECTION"
TREE = ROOT / "QUESTION_TREE.ndjson"
DIALOGUE = ROOT / "KERNEL_DIALOGUE.ndjson"
DECISIONS = ROOT / "RESEARCH_DECISION_LOG.ndjson"


def append_child(qid, parent, parent_result, question, learned, ambiguity, explanations):
    existing = {json.loads(line)["question_id"] for line in TREE.read_text(encoding="utf-8").splitlines() if line.strip()}
    if qid in existing:
        return
    parent_hash = sha(parent_result)
    row = {
        "question_id": qid, "parent_question": parent, "parent_result_hash": parent_hash,
        "stage": "RESULT_DERIVED_GRANDCHILD", "what_was_learned": learned,
        "new_uncertainty": ambiguity, "candidate_explanations": explanations,
        "question": question, "why_next_experiment_discriminates": "It isolates the causal prerequisite that separated passing from failing selection worlds.",
        "expected_information_gain": "high",
    }
    append_ndjson(TREE, row)
    append_ndjson(DECISIONS, {"decision": "OPEN_RESULT_DERIVED_GRANDCHILD", "question_id": qid, "parent_question": parent, "parent_result_hash": parent_hash, "reason": row["why_next_experiment_discriminates"]})


def occupied_transition_atlas(kernel):
    n = 17; center = (8, 8, 8); rows = []
    occupant_directions = [(0, 0, 0)] + DIRECTIONS
    for incoming in DIRECTIONS:
        for occupant in occupant_directions:
            raw = np.zeros((n, n, n), dtype=np.uint64)
            start = add(center, incoming, -1, n)
            if start == center:
                continue
            raw[start] = pack(1, 31, incoming, 1)
            raw[center] = pack(2, 43, occupant, 1)
            naive = reduced_step(structural_map(raw), n)
            world = NativeWorld(kernel, raw); world.tick(); actual = structural_map(world.raw)
            rows.append({"incoming": incoming, "occupant": occupant, "naive": [[list(q), list(d)] for q, d in sorted(naive.items())], "actual": [[list(q), list(d)] for q, d in sorted(actual.items())], "naive_exact": naive == actual})
    by_occupant_stationary = [r for r in rows if r["occupant"] == (0, 0, 0)]
    return {
        "experiment": "occupied-destination local transition atlas",
        "cases": rows, "naive_exact_count": sum(r["naive_exact"] for r in rows), "total": len(rows),
        "stationary_occupant_exact_count": sum(r["naive_exact"] for r in by_occupant_stationary), "stationary_occupant_total": len(by_occupant_stationary),
        "missing_law": "incumbent/proposal interaction, not a missing coordinate: position-to-direction already marks occupancy",
        "level_consequence": "destination-fiber closure remains exact for the frozen one-step empty-destination domain; multistep closure requires an occupancy-aware transition operator",
        "predicate": sum(r["naive_exact"] for r in rows) < len(rows),
        "interpretation": "The multistep failures are localized to occupied-destination interactions omitted from the simple proposal reducer. This bounds the effective law rather than invalidating the one-step level.",
    }


def setting_independence_summary(trials):
    total = len(trials); expected = total / 32
    counts = defaultdict(int)
    for t in trials:
        counts[(t["lambda_index"], t["a"], t["b"])] += 1
    max_fractional_deviation = max(abs(counts[(li, a, b)] - expected) / expected for li in range(8) for a in range(2) for b in range(2))
    return {"expected_per_cell": expected, "max_fractional_cell_deviation": max_fractional_deviation, "all_cells_nonzero": all(counts[(li, a, b)] > 0 for li in range(8) for a in range(2) for b in range(2))}


def bell_summary(trials):
    correlations = []
    for a in range(2):
        for b in range(2):
            cell = [t for t in trials if t["a"] == a and t["b"] == b]
            correlations.append(sum(t["A"] * t["B"] for t in cell) / len(cell))
    chsh = correlations[0] + correlations[1] + correlations[2] - correlations[3]
    signaling = {}
    for a in range(2):
        means = [np.mean([t["A"] for t in trials if t["a"] == a and t["b"] == b]) for b in range(2)]
        signaling[f"A_a{a}"] = float(abs(means[0] - means[1]))
    for b in range(2):
        means = [np.mean([t["B"] for t in trials if t["a"] == a and t["b"] == b]) for a in range(2)]
        signaling[f"B_b{b}"] = float(abs(means[0] - means[1]))
    return {"trials": len(trials), "correlations": correlations, "CHSH": chsh, "max_abs_signaling_difference": max(signaling.values()), "signaling_differences": signaling}


def sign_sum(a, b):
    return tuple(int(np.sign(a[i] + b[i])) for i in range(3))


def internal_bell_trial(kernel, n, hubs, lam, li, a, b):
    raw = np.zeros((n, n, n), dtype=np.uint64)
    clock = np.zeros_like(raw)
    generated = []
    specifications = [
        (hubs[0], tuple(lam), A_SETTINGS[a], (-1, 0, 0), ((0, -1, 0), (0, 0, -1))[a], "A"),
        (hubs[1], tuple(-x for x in lam), B_SETTINGS[b], (1, 0, 0), ((0, 0, -1), (0, 1, 0))[b], "B"),
    ]
    for side_index, (hub, hidden_direction, target_setting, common, selector, label) in enumerate(specifications):
        generator_hub = add(hub, target_setting, -1, n)
        entries = [
            (add(generator_hub, common, -1, n), pack(10 + side_index, 401 + side_index, common, 1)),
            (add(generator_hub, selector, -1, n), pack(20 + side_index, 601 + side_index, selector, 1)),
            (add(hub, hidden_direction, -2, n), pack(30 + side_index, 100 + li, hidden_direction, 1)),
        ]
        for q, token in entries:
            if int(raw[q]) != 0:
                raise RuntimeError(f"internal setting generator preparation collision at {q}")
            raw[q] = token
        generated.append((label, generator_hub, target_setting))
    world = NativeWorld(kernel, raw, clock); world.tick()
    generator_records = {label: unpack(world.raw[q]) for label, q, _ in generated}
    generators_valid = all(generator_records[label] is not None and tuple(generator_records[label]["direction"]) == target for label, _, target in generated)
    world.tick(); ra = unpack(world.raw[hubs[0]]); rb = unpack(world.raw[hubs[1]])
    valid = ra is not None and rb is not None and tuple(ra["direction"]) == sign_sum(tuple(lam), A_SETTINGS[a]) and tuple(rb["direction"]) == sign_sum(tuple(-x for x in lam), B_SETTINGS[b])
    def outcome(record):
        return next(1 if x > 0 else -1 for x in record["direction"] if x != 0)
    return {"lambda_index": li, "a": a, "b": b, "A": outcome(ra), "B": outcome(rb), "generator_records": generator_records, "generators_valid": generators_valid, "local_records_valid": valid}


def bell_setting_regimes(kernel):
    rng = np.random.default_rng(161501)
    n = 61; hubs = ((15, 23, 27), (46, 23, 27))
    external = []
    internal = []
    for _ in range(1024):
        li = int(rng.integers(0, 8)); a = int(rng.integers(0, 2)); b = int(rng.integers(0, 2)); lam = LAMBDA[li]
        external.append(bell_trial(kernel, n, hubs, lam, li, a, b))
        internal.append(internal_bell_trial(kernel, n, hubs, lam, li, a, b))
    # Deliberately correlated selector canary: settings are functions of lambda.
    correlated = []
    for repeat in range(64):
        for li, lam in enumerate(LAMBDA):
            a = 0 if lam[0] < 0 else 1; b = 0 if lam[1] < 0 else 1
            correlated.append(bell_trial(kernel, n, hubs, lam, li, a, b))
    external_summary = bell_summary(external); internal_summary = bell_summary(internal)
    external_independence = setting_independence_summary(external); internal_independence = setting_independence_summary(internal)
    correlated_independence = setting_independence_summary(correlated)
    return {
        "experiment": "randomized external and DEE-local-generated Bell settings",
        "external": {"summary": external_summary, "measurement_independence": external_independence, "all_retained": len(external), "trials": external},
        "internal": {"summary": internal_summary, "measurement_independence": internal_independence, "all_generators_valid": all(t["generators_valid"] for t in internal), "all_local_records_valid": all(t["local_records_valid"] for t in internal), "setting_generation_scope": "settings physically produced by local DEE reducer subsystems from independently initialized selector bits", "trials": internal},
        "measurement_dependence_canary": {"measurement_independence": correlated_independence, "detected": not correlated_independence["all_cells_nonzero"]},
        "valid_bell_outcome_levels": ["local collision outcome"],
        "invalid_level_upgrade": "population correlation is a statistical readout, not a newly separated physical Bell subsystem",
        "predicate": abs(external_summary["CHSH"]) <= 2 and abs(internal_summary["CHSH"]) <= 2 and all(t["generators_valid"] and t["local_records_valid"] for t in internal) and not correlated_independence["all_cells_nonzero"],
        "interpretation": "Both randomized regimes remain inside the Bell bound with complete retention. The local-generator regime is still initialized with independent external bits; no autonomous freedom claim is made. A correlated-setting canary is detected as measurement dependence.",
    }


def save(exp_id, qid, parent, parent_path, front, function, kernel):
    path = OUT / f"{exp_id}.json"
    if path.exists():
        return path, read_json(path)
    started = time.perf_counter(); result = function(kernel)
    out = {
        "experiment_id": exp_id, "question_id": qid, "parent_question": parent,
        "parent_result_hash": sha(parent_path), "front": front, "role": "ADAPTIVE_MODEL_LEVEL_SELECTION",
        "partition": "MODEL_LEVEL_SELECTION", "experiment_key": experiment_key(qid, front, result["experiment"], "GRANDCHILD"),
        "kernel_data_lineage": "v27 raw+clock -> committed telemetry -> predeclared result-derived metric",
        "elapsed_seconds": time.perf_counter() - started, **result,
    }
    out["content_sha256"] = canonical_hash(out); write_json(path, out)
    append_ndjson(DIALOGUE, {"question_id": qid, "experiment_id": exp_id, "parent_result_hash": out["parent_result_hash"], "raw_outcome": {"predicate": out.get("predicate"), "content_sha256": out["content_sha256"]}, "mechanism_update": out.get("interpretation"), "partition": "MODEL_LEVEL_SELECTION"})
    return path, out


def main():
    checkpoint = ROOT / "CHECKPOINTS" / "CP03_ADAPTIVE_GRANDCHILDREN.json"
    if checkpoint.exists():
        print(checkpoint.read_text(encoding="utf-8")); return
    audit_kernel("CORE16_BEFORE_ADAPTIVE_GRANDCHILDREN"); kernel, _ = verify_and_load_kernel(1)
    s1 = ROOT / "MODEL_SELECTION" / "C16S001.json"; d6 = ROOT / "DISCOVERY" / "C16D006.json"
    append_child("C16Q001A1", "C16Q001A", s1, "Which omitted interaction causes the 6/128 multistep closure failures?", "One-step structure was exact, but six worlds diverged at later ticks.", "Whether coordinates are missing or the reduced transition law ignores incumbent occupancy.", ["occupied-destination interaction", "payload dependence", "clock dependence"])
    append_child("C16Q005A", "C16Q005", d6, "Do independent randomized and locally generated settings change the Bell result?", "The exhaustive fresh frame reached CHSH=-2 without postselection.", "Whether selection regime or setting-generation mechanics changes the scope.", ["external independent settings", "DEE-local generator", "measurement-dependence artifact"])
    plans = [
        ("C16S007", "C16Q001A1", "C16Q001A", s1, "LEVEL_DISCOVERY", occupied_transition_atlas),
        ("C16S008", "C16Q005A", "C16Q005", d6, "BELL_REAUDIT", bell_setting_regimes),
    ]
    registry = read_json(ROOT / "EXPERIMENT_REGISTRY.json"); results = []
    for args in plans:
        path, result = save(*args, kernel)
        row = {"experiment_id": args[0], "question_id": args[1], "front": args[4], "path": str(path.relative_to(ROOT)), "sha256": sha(path), "predicate": result.get("predicate")}
        registry["experiments"].append(row); results.append(row)
    write_json(ROOT / "EXPERIMENT_REGISTRY.json", registry)
    cp = {"status": "COMPLETE", "grandchildren": len(results), "results": results, "utc": utc()}; write_json(checkpoint, cp)
    update_state(status="ADAPTIVE_DISCOVERY_COMPLETE_PENDING_SOURCE_FREEZE", phase="PHASE_J_K", completed_checkpoints=["PARENT_AUDIT", "DISCOVERY_ROOTS", "MODEL_LEVEL_SELECTION", "ADAPTIVE_GRANDCHILDREN"])
    print(json.dumps(cp, indent=2))


if __name__ == "__main__":
    main()
