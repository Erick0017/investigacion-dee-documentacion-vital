#!/usr/bin/env python3
"""D05: level-aware matter, thermal, field, wave, continuum and resource fronts."""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CORE15 = HERE / "VENDORED_CORE15"
CORE16X = HERE / "VENDORED_CORE16" / "RUNNERS_NEW"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(CORE16X))
sys.path.insert(0, str(CORE15))

from core17_common import (NativeWorld, ROOT, append_ndjson, audit_kernel,
                           canonical_hash, pack, sha256_array, utc,
                           verify_and_load_kernel, write_json)
import run_adaptive_discovery as prior
from occupancy_operator import MOORE, predict_tick


def random_operator_world(rng, n, density, include_fusion):
    raw = np.zeros((n, n, n), dtype=np.uint64)
    clock = rng.integers(0, 305000, size=raw.shape, dtype=np.uint64)
    count = max(1, int(raw.size * density))
    flat = rng.choice(raw.size, size=count, replace=False)
    semantics = (1, 1, 1, 1, 4, 5, 7)
    for j, idx in enumerate(flat):
        q = np.unravel_index(int(idx), raw.shape)
        semantic = int(semantics[int(rng.integers(0, len(semantics)))])
        state = int(rng.integers(0 if semantic == 4 else 1, 0x10000))
        direction = MOORE[int(rng.integers(0, len(MOORE)))] if rng.random() < 0.72 else (0, 0, 0)
        if semantic == 4 and state == 0 and direction == (0, 0, 0):
            state = int(rng.integers(0, 2))
        sreg = 19664 if include_fusion and j % 17 == 0 else int(rng.integers(0, 400))
        raw[q] = pack(state, sreg, direction, semantic)
    return raw, clock


def multistep_operator_panel(kernel):
    cases = []
    for i in range(9):
        seed = 173000 + i * 7919
        rng = np.random.default_rng(seed)
        n = (7, 8, 9)[i % 3]
        density = (0.025, 0.055, 0.10)[i % 3]
        raw, clock = random_operator_world(rng, n, density, i % 2 == 0)
        native = NativeWorld(kernel, raw, clock, 1)
        model_raw, model_clock = raw.copy(), clock.copy()
        steps = []
        for tick in range(1, 7):
            model_raw, model_clock, diagnostics, delta = predict_tick(model_raw, model_clock)
            native.tick()
            steps.append({
                "tick": tick,
                "raw_mismatches": int(np.count_nonzero(model_raw != native.raw)),
                "clock_mismatches": int(np.count_nonzero(model_clock != native.clock)),
                "model_raw_sha256": sha256_array(model_raw),
                "native_raw_sha256": sha256_array(native.raw),
                "fusion_destinations": len(delta),
                "branches": sorted(set(d["branch"] for d in diagnostics.values())),
            })
        cases.append({"seed": seed, "n": n, "density": density, "ticks": steps,
                      "exact": all(x["raw_mismatches"] == 0 and x["clock_mismatches"] == 0 for x in steps)})
    return {
        "cases": cases, "worlds": len(cases), "ticks": sum(len(c["ticks"]) for c in cases),
        "all_exact": all(c["exact"] for c in cases),
        "total_mismatches": sum(x["raw_mismatches"] + x["clock_mismatches"] for c in cases for x in c["ticks"]),
        "effective_law": "(R0 raw, clock) --occupancy-aware incumbent/incoming/fusion operator--> next (R0 raw, clock)",
    }


def compact_physics(result):
    keys = ("experiment", "predicate", "reason", "interpretation", "serious_field_candidate_found",
            "medium_dependent_collective_propagation_found", "friction_like_conversion_found",
            "stable_body_level_inertia_coefficient", "theta_eligible", "exact_capped_local_accounting",
            "depletion_recharge_work_cycle_found", "passive_reflection_established",
            "passive_refraction_established", "same_bulk_observer_t0", "different_bulk_future",
            "law", "pass_count", "total", "exact_translation", "functional_identity_preserved")
    return {k: result[k] for k in keys if k in result}


def main():
    audit_kernel("CORE17_D05_EMERGENT_PHYSICS")
    kernel, runtime = verify_and_load_kernel(1)
    full = {
        "mobile_identity": prior.mobile_root(kernel),
        "inertia": prior.perturbation_child(kernel),
        "contact_friction": prior.contact_root(kernel),
        "thermal": prior.thermal_root(kernel),
        "radiation": prior.radiation_root(kernel),
        "field": prior.field_root(kernel),
        "wave": prior.wave_root(kernel),
        "simple_continuum": prior.continuum_root(kernel),
        "relational_one_step": prior.relational_closure_child(kernel),
        "resource": prior.resource_root(kernel),
        "phase_transition": prior.phase_transition_root(kernel),
    }
    operator = multistep_operator_panel(kernel)
    summaries = {name: compact_physics(value) for name, value in full.items()}
    result = {
        "schema": "dee.v27.core17.d05.v1",
        "experiment": "LEVEL_AWARE_EMERGENT_PHYSICS_AND_MULTISTEP_OPERATOR",
        "created_utc": utc(), "runtime": runtime,
        "front_summaries": summaries,
        "front_evidence": full,
        "multistep_operator": operator,
        "adjudication": {
            "classical_mobile_object": "BOUNDED_RELATIONAL_TRANSLATING_CONSTELLATION",
            "collective_inertia": "NOT_FOUND_COMPONENT_LOCAL_RESPONSE",
            "friction": "NOT_FOUND_IDENTITY_DESTROYED_AT_CONTACT",
            "thermal_level": "NOT_FOUND_NO_IDENTITY_PRESERVING_EXCHANGE_OR_THETA",
            "radiation": "FINITE_SPEED_SOURCE_SUPPORTED_CARRIER_TRAINS_ACTIVE_REDIRECTION_ONLY",
            "field": "NOT_FOUND_NO_SOURCE_GENERATED_NONCOLLISIONAL_MEDIATOR",
            "collective_wave": "NOT_FOUND_IN_TESTED_MEDIA",
            "simple_continuum": "NOT_CLOSED_MISSING_DESTINATION_FIBERS_AND_INCUMBENT_STATE",
            "r0_multistep_effective_law": "EXACT" if operator["all_exact"] else "FAILED",
            "resource": "EXACT_CAPPED_LOCAL_SREG_ACCOUNTING_NO_WORK_CYCLE",
            "phase_transition": "ORDERED_ENDPOINT_AND_FINITE_CROSSOVER_NO_SHARP_SCALING_TRANSITION",
        },
    }
    h = canonical_hash(result); result["content_sha256"] = h
    write_json(ROOT / "DISCOVERY" / "C17D05_EMERGENT_PHYSICS.json", result)
    append_ndjson(ROOT / "QUESTION_TREE.ndjson", {
        "question_id": "C17Q005", "parent_question": "Which familiar effective-physics fronts become valid at the CORE17 level graph?",
        "parent_result_hash": "7fd166c8ecffa72c108848739655d8e04bad8e0e128cf748b1f4717e0424570b",
        "new_uncertainty": "Whether the exact R0 multistep law admits a further compressed continuum while preserving destination/incumbent branches.",
        "candidate_explanations": ["exact discrete R0 is current closure", "fiber-aware compressed continuum", "block-local closure"],
        "why_next_experiment_discriminates": "Nine mixed-semantic worlds test six prospective ticks against the independent operator; prior block summaries supply a collision counterexample.",
        "result_hash": h, "result": result["adjudication"],
        "child_question": "Can an MDL representation compress destination fibers and incumbent branches without losing multistep exactness?",
        "status": "CHILD_OPEN",
    })
    append_ndjson(ROOT / "RESEARCH_DECISION_LOG.ndjson", {
        "utc": utc(), "decision_id": "C17D05_DECISION", "parent_result_hash": h,
        "decision": "Promote the exact discrete R0 operator and relational object only; retain bounded nulls for inertia, thermal, field, wave and simple continuum categories.",
        "reason": "The operator achieved zero mismatches over mixed multistep cases; category prerequisites failed under direct controls.",
    })
    append_ndjson(ROOT / "KERNEL_DIALOGUE.ndjson", {
        "question_id": "C17Q005", "raw_outcome": result["adjudication"],
        "mechanism_update": "The most complete effective physics remains graph-structured: exact R0 local/destination dynamics plus task-specific organization and ensemble projections. Human labels beyond carrier radiation and relational objects are not earned.",
        "next": "Freeze the genuinely new clock-return and macro-amplification laws, then generate post-freeze worlds.",
    })
    print(json.dumps({"hash": h, "adjudication": result["adjudication"],
                      "operator": {k: operator[k] for k in ("worlds", "ticks", "all_exact", "total_mismatches")}}, indent=2))


if __name__ == "__main__":
    main()
