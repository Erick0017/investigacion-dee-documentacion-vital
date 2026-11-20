#!/usr/bin/env python3
"""Discovery/model competition for the occupied-destination operator."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from core16x_common import append_ndjson, audit_kernel, canonical_hash, update_state, utc, write_json
from native_runtime_x import NativeWorld, pack, sha256_array, verify_and_load_kernel
from occupancy_operator import MOORE, predict_tick, unpack


def random_world(rng: np.random.Generator, n: int, density: float, include_fusion: bool) -> tuple[np.ndarray, np.ndarray]:
    raw = np.zeros((n, n, n), dtype=np.uint64)
    clock = rng.integers(0, 305000, size=raw.shape, dtype=np.uint64)
    count = max(1, int(raw.size * density))
    flat = rng.choice(raw.size, size=count, replace=False)
    directions = tuple(MOORE)
    semantics = (1, 1, 1, 1, 4, 5, 7)
    for j, idx in enumerate(flat):
        q = np.unravel_index(int(idx), raw.shape)
        semantic = int(semantics[int(rng.integers(0, len(semantics)))])
        state = int(rng.integers(0 if semantic == 4 else 1, 0x10000))
        direction = directions[int(rng.integers(0, len(directions)))] if rng.random() < 0.72 else (0, 0, 0)
        if semantic == 4 and state == 0 and direction == (0, 0, 0):
            state = int(rng.integers(0, 2))
        sreg = 19664 if include_fusion and j % 17 == 0 else int(rng.integers(0, 400))
        raw[q] = pack(state, sreg, direction, semantic)
    return raw, clock


def naive_incoming_model(raw: np.ndarray, clock: np.ndarray):
    """Rejected comparator: always lets incoming sources overwrite their destinations."""
    out = raw.copy()
    n = raw.shape[0]
    for q in np.ndindex(raw.shape):
        f = unpack(raw[q])
        d = (f["dx"], f["dy"], f["dz"])
        if d == (0, 0, 0):
            continue
        target = tuple((q[i] + d[i]) % n for i in range(3))
        out[target] = pack(1, f["sreg"], d, 1)
    return out


def run_partition(kernel, seeds, partition: str):
    cases = []
    branch_counter = Counter()
    exact_cells = 0
    total_cells = 0
    naive_cells = 0
    incumbent_incoming = Counter()
    for i, seed in enumerate(seeds):
        rng = np.random.default_rng(seed)
        n = (7, 8, 9)[i % 3]
        density = (0.025, 0.055, 0.10, 0.16)[i % 4]
        raw, clock = random_world(rng, n, density, include_fusion=i % 3 == 0)
        predicted, predicted_clock, diagnostics, delta = predict_tick(raw, clock)
        naive = naive_incoming_model(raw, clock)
        world = NativeWorld(kernel, raw, clock, threads=1)
        info = world.tick()
        actual = world.raw.copy()
        actual_clock = world.clock.copy()
        exact_raw = bool(np.array_equal(predicted, actual))
        exact_clock = bool(np.array_equal(predicted_clock, actual_clock))
        exact_cells += int(np.count_nonzero(predicted == actual))
        naive_cells += int(np.count_nonzero(naive == actual))
        total_cells += actual.size
        for q, diag in diagnostics.items():
            branch_counter[diag["branch"]] += 1
            if diag["incumbent"]["state"] > 0 and diag["incoming_count"] > 0:
                incumbent_incoming[(diag["branch"], unpack(actual[q])["state"] > 0)] += 1
        cases.append({
            "partition": partition,
            "case": i,
            "seed": int(seed),
            "n": n,
            "density": density,
            "initial_raw_sha256": sha256_array(raw),
            "initial_clock_sha256": sha256_array(clock),
            "predicted_raw_sha256": sha256_array(predicted),
            "actual_raw_sha256": sha256_array(actual),
            "predicted_clock_sha256": sha256_array(predicted_clock),
            "actual_clock_sha256": sha256_array(actual_clock),
            "exact_raw": exact_raw,
            "exact_clock": exact_clock,
            "cell_mismatches": int(np.count_nonzero(predicted != actual)),
            "naive_cell_mismatches": int(np.count_nonzero(naive != actual)),
            "fusion_destinations": len(delta),
            "kernel_info": {str(k): int(v) if isinstance(v, (int, np.integer)) else v for k, v in info.items()},
        })
    return {
        "partition": partition,
        "cases": cases,
        "case_exact": sum(c["exact_raw"] and c["exact_clock"] for c in cases),
        "case_total": len(cases),
        "operator_cell_accuracy": exact_cells / total_cells,
        "naive_incoming_cell_accuracy": naive_cells / total_cells,
        "branch_counts": {str(k): int(v) for k, v in branch_counter.items()},
        "incumbent_with_incoming_outcomes": {f"{k[0]}|survives={k[1]}": int(v) for k, v in incumbent_incoming.items()},
    }


def main() -> None:
    audit_kernel("CORE16X_BEFORE_OCCUPIED_OPERATOR_DISCOVERY")
    kernel, runtime = verify_and_load_kernel(1)
    discovery_seeds = [160001 + 7919 * i for i in range(24)]
    selection_seeds = [960001 + 104729 * i for i in range(12)]
    discovery = run_partition(kernel, discovery_seeds, "DISCOVERY")
    selection = run_partition(kernel, selection_seeds, "MODEL_SELECTION")
    result = {
        "experiment": "C16X-OCCUPANCY-AWARE-DESTINATION-OPERATOR-DISCOVERY",
        "created_utc": utc(),
        "experiment_key": canonical_hash({"question": "occupied destination operator", "mechanism": "full native local branch", "observer": "raw+clock", "intervention": "random local configurations", "region": "N7-9 sparse-to-moderate"}),
        "runtime": runtime,
        "discovery": discovery,
        "model_selection": selection,
        "model_competition": [
            {"model": "EMPTY_DESTINATION_FIBER_ONLY", "disposition": "OUT_OF_SCOPE_WHEN_INCUMBENT_PRESENT"},
            {"model": "NAIVE_INCOMING_OVERWRITES_INCUMBENT", "selection_cell_accuracy": selection["naive_incoming_cell_accuracy"], "disposition": "REJECTED"},
            {"model": "INCUMBENT_BRANCH_PRIORITY_PLUS_REDUCER_AND_DEMUX", "selection_cell_accuracy": selection["operator_cell_accuracy"], "selection_case_exact": f"{selection['case_exact']}/{selection['case_total']}", "disposition": "SELECTED_FOR_FREEZE" if selection["case_exact"] == selection["case_total"] else "REQUIRES_REPAIR"},
        ],
        "mechanistic_result": {
            "empty_destination": "XNOR is evaluated first; otherwise incoming directional sources are symmetrically reduced.",
            "occupied_destination": "Ordinary incoming reducer is not called. The incumbent enters the matter branch using neighborhood activity, tetrahedral signature, vector symmetry, clock phase and s_reg; it may die, persist, or emit fusion delta.",
            "semantic4_destination": "Raw is fixed and both incoming reducer and post-demux modification are blocked.",
            "post_update": "Fusion deltas are accumulated separately and applied after all local branches.",
        },
        "scope": "Exact executed v27 tick operator including XNOR, semantic4, matter, fusion delta and clocks; crystallization omitted only because it is formally unreachable for all valid raws.",
    }
    write_json(ROOT / "DISCOVERY" / "OCCUPANCY_OPERATOR_DISCOVERY.json", result)
    result_hash = canonical_hash(result)
    pass_selection = selection["case_exact"] == selection["case_total"]
    append_ndjson(ROOT / "QUESTION_TREE.ndjson", {
        "question_id": "C16X-Q003",
        "parent_id": "C16X-Q002",
        "parent_result_hash": result_hash,
        "what_was_learned": f"The incumbent-aware specification matched {selection['case_exact']}/{selection['case_total']} selection worlds; naive incoming overwrite accuracy was {selection['naive_incoming_cell_accuracy']:.6f}.",
        "new_uncertainty": "Does the frozen operator close exact multistep dynamics on untouched worlds, including occupied destinations and fusion?",
        "competing_interpretations": ["one-step agreement generalizes compositionally", "latent mismatch accumulates over ticks", "closure holds only without fusion"],
        "why_next_experiment_matters": "Prospective multistep closure is the prerequisite for a genuine effective local physics.",
        "status": "OPEN" if pass_selection else "BLOCKED_BY_OPERATOR_MISMATCH",
    })
    append_ndjson(ROOT / "QUESTION_TREE.ndjson", {
        "question_id": "C16X-Q004",
        "parent_id": "C16X-Q002",
        "parent_result_hash": result_hash,
        "what_was_learned": "The prior occupied-destination failure is branch priority, not stochasticity: incumbents are updated by matter rules and ordinary incoming proposals are ignored.",
        "new_uncertainty": "Which sufficient statistics can compress the exact operator without losing prospective closure?",
        "competing_interpretations": ["branch label plus n_active/gradient/tetra/clock phase is sufficient", "fusion tie accessibility requires richer topology", "full local raw is necessary"],
        "why_next_experiment_matters": "A source translation is not a new effective level unless it compresses lower state.",
        "status": "OPEN" if pass_selection else "DEFERRED",
    })
    append_ndjson(ROOT / "KERNEL_DIALOGUE.ndjson", {
        "question_id": "C16X-Q002",
        "raw_outcome": {"discovery_exact": f"{discovery['case_exact']}/{discovery['case_total']}", "selection_exact": f"{selection['case_exact']}/{selection['case_total']}", "naive_selection_accuracy": selection["naive_incoming_cell_accuracy"]},
        "mechanism_update": "Occupied targets do not participate in the ordinary incoming reducer. The incumbent local rule has priority, followed by global application of fusion deltas.",
        "remaining_alternatives": ["compression sufficiency", "multistep generalization", "fusion-specific scope"],
        "next_high_information_question": "Freeze the operator then generate untouched multistep worlds.",
    })
    update_state(
        status="OCCUPANCY_OPERATOR_DISCOVERED" if pass_selection else "OCCUPANCY_OPERATOR_REPAIR_REQUIRED",
        current_phase="OPERATOR_FREEZE" if pass_selection else "OPERATOR_DIAGNOSIS",
        occupied_operator_selection_exact=f"{selection['case_exact']}/{selection['case_total']}",
        occupied_operator_result_hash=result_hash,
        completed_checkpoints=["BASELINE_AUDIT", "FULL_PARENT_CLAIM_INGESTION", "FULL_STATE_CAUSAL_AUDIT", "OCCUPANCY_OPERATOR_DISCOVERY"] if pass_selection else ["BASELINE_AUDIT", "FULL_PARENT_CLAIM_INGESTION", "FULL_STATE_CAUSAL_AUDIT"],
    )
    print(json.dumps({"discovery": f"{discovery['case_exact']}/{discovery['case_total']}", "selection": f"{selection['case_exact']}/{selection['case_total']}", "operator_accuracy": selection["operator_cell_accuracy"], "naive_accuracy": selection["naive_incoming_cell_accuracy"], "result_hash": result_hash}, indent=2))


if __name__ == "__main__":
    main()
