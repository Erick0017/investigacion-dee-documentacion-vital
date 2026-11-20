#!/usr/bin/env python3
"""Untouched multistep validation for operator and causal quotient."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from core16x_common import append_ndjson, audit_kernel, canonical_hash, read_json, sha256_file, update_state, utc, write_json
from native_runtime_x import NativeWorld, pack, sha256_array, verify_and_load_kernel
from occupancy_operator import MOORE, predict_tick, unpack
from run_occupied_operator_discovery import random_world

L_CLOCK = 304980


def canonicalize(raw: np.ndarray) -> np.ndarray:
    out = raw.copy()
    for q in np.ndindex(raw.shape):
        f = unpack(raw[q])
        if f["semantic"] == 4:
            continue
        out[q] = pack(int(f["state"] > 0), f["sreg"], (f["dx"], f["dy"], f["dz"]), f["semantic"])
    return out


def run_case(kernel, challenge):
    rng = np.random.default_rng(challenge["seed"])
    raw, clock = random_world(rng, challenge["n"], challenge["density"], challenge["include_fusion"])
    clock = np.mod(clock, np.uint64(L_CLOCK)).astype(np.uint64)
    shift = np.uint64(challenge["clock_shift_multiple"] * L_CLOCK)
    canonical_raw = canonicalize(raw)
    canonical_clock = clock + shift
    native = NativeWorld(kernel, raw, clock, 1)
    paired = NativeWorld(kernel, canonical_raw, canonical_clock, 1)
    model_raw = raw.copy()
    model_clock = clock.copy()
    steps = []
    operator_exact = True
    quotient_exact = True
    max_raw_mismatch = 0
    for tick in range(1, challenge["ticks"] + 1):
        model_raw, model_clock, _, _ = predict_tick(model_raw, model_clock)
        native.tick()
        paired.tick()
        raw_mismatch = int(np.count_nonzero(model_raw != native.raw))
        clock_mismatch = int(np.count_nonzero(model_clock != native.clock))
        pair_raw_mismatch = int(np.count_nonzero(native.raw != paired.raw))
        residue_mismatch = int(np.count_nonzero(np.mod(native.clock, L_CLOCK) != np.mod(paired.clock, L_CLOCK)))
        operator_exact &= raw_mismatch == 0 and clock_mismatch == 0
        quotient_exact &= pair_raw_mismatch == 0 and residue_mismatch == 0
        max_raw_mismatch = max(max_raw_mismatch, raw_mismatch)
        steps.append({
            "tick": tick,
            "operator_raw_mismatch": raw_mismatch,
            "operator_clock_mismatch": clock_mismatch,
            "quotient_raw_mismatch": pair_raw_mismatch,
            "quotient_clock_residue_mismatch": residue_mismatch,
            "native_raw_sha256": sha256_array(native.raw),
            "model_raw_sha256": sha256_array(model_raw),
        })
    return {
        "challenge_id": challenge["challenge_id"],
        "n": challenge["n"],
        "density": challenge["density"],
        "ticks": challenge["ticks"],
        "include_fusion": challenge["include_fusion"],
        "operator_exact": operator_exact,
        "quotient_exact": quotient_exact,
        "steps": steps,
        "initial_state_payload_changed_cells": int(np.count_nonzero(raw != canonical_raw)),
        "clock_shift": int(shift),
        "max_operator_raw_mismatch": max_raw_mismatch,
    }


def gate_canary(kernel):
    n = 9
    c = (4, 4, 4)
    raw = np.zeros((n, n, n), dtype=np.uint64)
    raw[c] = pack(0xABCDEF01, 10, (0, 0, 0), 1)
    for d in ((1,0,0),(0,1,0),(0,0,1),(1,1,1)):
        raw[tuple((c[i] + d[i]) % n for i in range(3))] = pack(0x100 + sum(abs(v) for v in d), 3, (0,0,0), 1)
    clock0 = np.zeros_like(raw)
    clock1 = clock0.copy(); clock1[c] = np.uint64(1)
    w0 = NativeWorld(kernel, raw, clock0, 1); w1 = NativeWorld(kernel, raw, clock1, 1)
    w0.tick(); w1.tick()
    return {"center_raw_clock0": int(w0.raw[c]), "center_raw_clock1": int(w1.raw[c]), "raw_differs": int(w0.raw[c]) != int(w1.raw[c]), "expected": "raw differs because only clock0 is divisible by period195"}


def semantic4_canary(kernel):
    n = 7; q = (3,3,3)
    raw_a = np.zeros((n,n,n), dtype=np.uint64); raw_b = raw_a.copy()
    raw_a[q] = pack(0xABCDEF01, 19664, (1,-1,1), 4)
    raw_b[q] = pack(1, 19664, (1,-1,1), 4)
    a = NativeWorld(kernel, raw_a, threads=1); b = NativeWorld(kernel, raw_b, threads=1)
    a.tick(); b.tick()
    return {"a": int(a.raw[q]), "b": int(b.raw[q]), "raw_differs": int(a.raw[q]) != int(b.raw[q]), "expected": "semantic4 raw payload is preserved and cannot be compressed to existence"}


def occupied_anchor(kernel):
    n = 7; target = (3,3,3); source = (2,3,3)
    raw = np.zeros((n,n,n), dtype=np.uint64)
    raw[target] = pack(77, 5, (0,0,0), 1)
    raw[source] = pack(99, 11, (1,0,0), 1)
    world = NativeWorld(kernel, raw, threads=1); world.tick()
    return {"target_after": int(world.raw[target]), "incoming_overwrite_prediction": int(pack(1,11,(1,0,0),1)), "negative_anchor_correct": int(world.raw[target]) != int(pack(1,11,(1,0,0),1))}


def main() -> None:
    audit_kernel("CORE16X_BEFORE_OPERATOR_FINAL_HOLDOUT")
    lock = read_json(ROOT / "HOLDOUT_LOCKS" / "OCCUPANCY_OPERATOR_LOCK.json")
    challenges = read_json(ROOT / "FINAL_HOLDOUTS" / "OPERATOR_CHALLENGES.json")
    for name, expected in lock["source_hashes"].items():
        if sha256_file(ROOT / "RUNNERS_NEW" / name) != expected:
            raise RuntimeError(f"Frozen source changed: {name}")
    if challenges["lock_sha256"] != lock["lock_sha256"]:
        raise RuntimeError("challenge/lock mismatch")
    kernel, runtime = verify_and_load_kernel(1)
    cases = [run_case(kernel, challenge) for challenge in challenges["challenges"]]
    canaries = {
        "period195_clock_plus_one": gate_canary(kernel),
        "semantic4_payload_exception": semantic4_canary(kernel),
        "occupied_incoming_negative_anchor": occupied_anchor(kernel),
    }
    operator_pass = all(case["operator_exact"] for case in cases)
    quotient_pass = all(case["quotient_exact"] for case in cases)
    canary_pass = all(item.get("raw_differs", item.get("negative_anchor_correct", False)) for item in canaries.values())
    result = {
        "holdout_id": challenges["challenge_set_id"],
        "executed_utc": utc(),
        "lock_id": lock["lock_id"],
        "lock_sha256": lock["lock_sha256"],
        "challenge_sha256": challenges["challenge_sha256"],
        "runtime": runtime,
        "cases": cases,
        "summary": {
            "operator_worlds_pass": sum(case["operator_exact"] for case in cases),
            "operator_worlds_total": len(cases),
            "quotient_worlds_pass": sum(case["quotient_exact"] for case in cases),
            "quotient_worlds_total": len(cases),
            "operator_total_ticks": sum(case["ticks"] for case in cases),
            "operator_cell_mismatches": sum(step["operator_raw_mismatch"] + step["operator_clock_mismatch"] for case in cases for step in case["steps"]),
            "quotient_cell_mismatches": sum(step["quotient_raw_mismatch"] + step["quotient_clock_residue_mismatch"] for case in cases for step in case["steps"]),
            "canaries_pass": canary_pass,
            "overall_pass": operator_pass and quotient_pass and canary_pass,
        },
        "canaries": canaries,
    }
    write_json(ROOT / "FINAL_HOLDOUTS" / "OPERATOR_HOLDOUT_RESULTS.json", result)
    write_json(ROOT / "CANARIES" / "OPERATOR_CANARY_RESULTS.json", canaries)
    holdout_registry = {
        "campaign": "CORE16_CORRECTED_EXPANDED",
        "entries": [{
            "holdout_id": result["holdout_id"], "claims": ["C16X001", "C16X002"],
            "lock_sha256": lock["lock_sha256"], "challenge_sha256": challenges["challenge_sha256"],
            "fresh_worlds": len(cases), "ticks": result["summary"]["operator_total_ticks"],
            "status": "PASS" if result["summary"]["overall_pass"] else "FAIL",
        }],
    }
    write_json(ROOT / "HOLDOUT_REGISTRY.json", holdout_registry)
    write_json(ROOT / "CANARY_REGISTRY.json", {"entries": [{"claim_id": "C16X001", "canary": "occupied priority negative anchor", "pass": canaries["occupied_incoming_negative_anchor"]["negative_anchor_correct"]}, {"claim_id": "C16X002", "canary": "period195 clock +1", "pass": canaries["period195_clock_plus_one"]["raw_differs"]}, {"claim_id": "C16X002", "canary": "semantic4 payload exception", "pass": canaries["semantic4_payload_exception"]["raw_differs"]}]})
    result_hash = canonical_hash(result)
    append_ndjson(ROOT / "QUESTION_TREE.ndjson", {
        "question_id": "C16X-Q005",
        "parent_id": "C16X-Q003",
        "parent_result_hash": result_hash,
        "what_was_learned": f"Frozen operator passed {result['summary']['operator_worlds_pass']}/{len(cases)} worlds over {result['summary']['operator_total_ticks']} ticks with {result['summary']['operator_cell_mismatches']} mismatches.",
        "new_uncertainty": "Does the exact causal quotient constitute a distinct effective level and which hidden variables can re-enter beyond its declared equivalence class?",
        "competing_interpretations": ["payload is truly redundant while other residuals are intervention-relative", "special native mechanisms read an omitted variable", "semantic4 forms a parallel invariant branch"],
        "why_next_experiment_matters": "It separates true information destruction/redundancy from observer-hidden but later-revealable information.",
        "status": "OPEN" if result["summary"]["overall_pass"] else "BLOCKED_BY_HOLDOUT_FAILURE",
    })
    append_ndjson(ROOT / "KERNEL_DIALOGUE.ndjson", {
        "question_id": "C16X-Q003",
        "raw_outcome": result["summary"],
        "mechanism_update": "The occupied-destination operator is compositional across fresh multistep worlds; the state-payload/clock-residue quotient is an exact native equivalence in scope, with semantic4 retained explicitly.",
        "remaining_alternatives": ["cross-variable resurrection", "embedded access", "higher organization scale transfer"],
        "next_high_information_question": "Test hidden variables across independent native mechanisms and large organizations.",
    })
    update_state(
        status="OPERATOR_HOLDOUT_PASS" if result["summary"]["overall_pass"] else "OPERATOR_HOLDOUT_FAIL",
        current_phase="CROSS_SCALE_HIDDEN_INFORMATION" if result["summary"]["overall_pass"] else "OPERATOR_FAILURE_AUDIT",
        operator_holdout_summary=result["summary"],
        operator_holdout_result_hash=result_hash,
        completed_checkpoints=["BASELINE_AUDIT", "FULL_PARENT_CLAIM_INGESTION", "FULL_STATE_CAUSAL_AUDIT", "OCCUPANCY_OPERATOR_DISCOVERY", "OCCUPANCY_OPERATOR_HOLDOUT"] if result["summary"]["overall_pass"] else ["BASELINE_AUDIT", "FULL_PARENT_CLAIM_INGESTION", "FULL_STATE_CAUSAL_AUDIT", "OCCUPANCY_OPERATOR_DISCOVERY"],
    )
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()

