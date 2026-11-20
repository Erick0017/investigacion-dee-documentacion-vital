#!/usr/bin/env python3
"""Build the causal state inventory from the exact v27 kernel and restored corpus."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core16x_common import ROOT, TESTS, append_ndjson, audit_kernel, canonical_hash, read_json, sha256_file, update_state, utc, write_json


def main() -> None:
    kernel_row = audit_kernel("CORE16X_FULL_STATE_AUDIT")
    source_root = TESTS / "DEE_CODEX_NATIVE_DISCOVERY_AND_CLOSURE_V1_WORK" / "ANALYSIS" / "binary_api" / "wheel_extracted" / "dee_universe_v27"
    cpp = source_root / "dee_kernel_v27.cpp"
    wrapper = source_root / "dee_universe_v27.py"
    audit_report = source_root.parents[1] / "AUDIT_REPORT.md"
    claim_graph = read_json(ROOT / "CORE01_16_COMPLETE_CLAIM_GRAPH.json")
    mechanism_counts = Counter()
    for claim in claim_graph["claim_nodes"]:
        mechanism_counts.update(claim.get("mechanisms", []))

    stored = [
        {
            "component": "grid_raw_A",
            "storage": "uint64[N^3] canonical current grid",
            "subfields": [
                {"name": "state", "bits": "0..31", "type": "uint32", "causal_role": "existence/rule payload; state>0 defines exists"},
                {"name": "s_reg", "bits": "32..47", "type": "uint16", "executed_cap": 19664, "causal_role": "local register used by gradients, fusion threshold and reducer composition; not pre-named energy"},
                {"name": "direction_x", "bits": "48..51", "type": "signed nibble [-8,7]", "causal_role": "destination proposal/routed transport and response anchoring"},
                {"name": "direction_y", "bits": "52..55", "type": "signed nibble [-8,7]", "causal_role": "destination proposal/routed transport and response anchoring"},
                {"name": "direction_z", "bits": "56..59", "type": "signed nibble [-8,7]", "causal_role": "destination proposal/routed transport and response anchoring"},
                {"name": "semantic", "bits": "60..63", "type": "uint4", "causal_role": "rule-family selector; semantic 4 is exact raw-fixed observer/guard state"},
            ],
            "persistent": True,
            "kernel_read": True,
            "kernel_write": True,
        },
        {
            "component": "clock_A",
            "storage": "uint64[N^3] canonical local clocks",
            "subfields": [{"name": "local_clock", "type": "uint64", "causal_role": "increments mod 2^64 and gates reachable matter updates with active periods 195/260/391/782"}],
            "persistent": True,
            "kernel_read": True,
            "kernel_write": True,
        },
        {
            "component": "toroidal_coordinate_and_N",
            "storage": "array position plus integer N",
            "subfields": [{"name": "coordinate", "type": "Z_N^3"}, {"name": "N", "type": "integer >=4 in wrapper"}],
            "persistent": True,
            "kernel_read": True,
            "kernel_write": False,
        },
    ]
    implementation = [
        {"component": "grid_raw_B", "role": "double-buffer target, copied back to A every tick", "independent_state": False},
        {"component": "clock_B", "role": "double-buffer target, copied back to A every tick", "independent_state": False},
        {"component": "wrapper_tick_global", "role": "Python bookkeeping only; not read by binary kernel", "independent_state": False},
        {"component": "thread_count", "role": "execution partition; valid runs agree across tested thread counts", "independent_state": False},
    ]
    transient = [
        {"component": "Moore_neighborhood", "derived_from": ["grid_raw_A", "coordinate", "N"], "causal_role": "26-neighbor local input"},
        {"component": "n_active", "derived_from": ["Moore_neighborhood"], "causal_role": "matter rule and clock gate"},
        {"component": "direction_sum", "derived_from": ["Moore_neighborhood.direction"], "causal_role": "write protection and symmetric reducer"},
        {"component": "s_reg_gradient", "derived_from": ["Moore_neighborhood.s_reg", "offsets"], "causal_role": "direction response; crystallization branch is formally unreachable"},
        {"component": "tetrahedral_signature", "derived_from": ["Moore_neighborhood.occupancy"], "causal_role": "selects strong-tension matter rule"},
        {"component": "XNOR_pair_signature", "derived_from": ["Moore_neighborhood.occupancy"], "causal_role": "semantic-7 birth"},
        {"component": "incoming_destination_sources", "derived_from": ["neighbor direction", "target coordinate"], "causal_role": "empty-destination symmetric reducer"},
        {"component": "incoming_reducer", "derived_from": ["incoming_destination_sources"], "causal_role": "one source copies raw fields; multiple sources sum capped s_reg and sign-compose direction"},
        {"component": "delta_demux", "derived_from": ["fusion-eligible emitters", "candidate accessibility", "tie order"], "causal_role": "post-update additive destination modification; atomic transient reset each tick"},
        {"component": "proposal/destination fibers", "derived_from": ["coordinate", "direction", "N"], "causal_role": "routed causal equivalence used by one-step closure"},
    ]
    emergent = [
        {"component": "phase", "ontological_status": "relational/derived", "basis": "clock residues, period-two trains, oscillator histories", "not_a_separate_kernel_field": True},
        {"component": "history", "ontological_status": "trajectory relation", "basis": "prior full states, persistent raw/clock traces, trained configurations", "not_a_separate_kernel_field": True},
        {"component": "lineage", "ontological_status": "causal provenance relation", "basis": "state-transition ancestry reconstructed by apparatus", "not_a_separate_kernel_field": True},
        {"component": "topology/accessibility", "ontological_status": "relational", "basis": "toroidal adjacency, local interface configuration, reachable routes", "not_a_separate_kernel_field": True},
        {"component": "basin/regime", "ontological_status": "trajectory equivalence class", "basis": "longitudinal state behavior", "not_a_separate_kernel_field": True},
        {"component": "coupling_state", "ontological_status": "multi-system relation", "basis": "joint response and shared interface/history", "not_a_separate_kernel_field": True},
        {"component": "functional_state", "ontological_status": "intervention-response equivalence class", "basis": "preserved behavior despite microstate replacement", "not_a_separate_kernel_field": True},
    ]
    schema = {
        "schema": "DEE_V27_FULL_STATE_SCHEMA_V1",
        "created_utc": utc(),
        "campaign_premise": "P0_FIXED",
        "kernel_identity": kernel_row["observed"],
        "reference_state": "X_t = (grid_raw_A, clock_A, N/toroidal coordinate relation)",
        "canonical_persistent_state": stored,
        "implementation_buffers_not_independent_state": implementation,
        "within_tick_transient_causal_variables": transient,
        "validated_derived_or_trajectory_information": emergent,
        "critical_distinction": "Phase, history, lineage, basin, coupling and functional identity are real causal/relational information but are not extra hidden arrays in the v27 binary.",
        "causal_dependency_radius": {"raw_one_tick_Chebyshev_upper_bound": 3, "witness_saturates": 3, "clock_direct_read_radius": 0},
        "clock_law": "c_i(t)=c_i(0)+t mod 2^64; raw-causal reachable period L=304980 before wrap",
        "exact_symmetries_and_breaks": {"toroidal_translation": "EXACT", "full_cubic_Oh": "FALSE_GLOBALLY_DUE_TO_DEMUX_TIES"},
        "formal_boundaries": {"crystallization_branch": "UNREACHABLE", "demux_edge_min": "UNUSED", "kernel_many_to_one": "PROVEN"},
        "source_provenance": {
            "cpp_path": str(cpp.relative_to(TESTS)), "cpp_sha256": sha256_file(cpp),
            "wrapper_path": str(wrapper.relative_to(TESTS)), "wrapper_sha256": sha256_file(wrapper),
            "binary_api_audit_path": str(audit_report.relative_to(TESTS)), "binary_api_audit_sha256": sha256_file(audit_report),
            "restored_claim_graph_sha256": sha256_file(ROOT / "CORE01_16_COMPLETE_CLAIM_GRAPH.json"),
        },
    }
    write_json(ROOT / "DEE_FULL_STATE_SCHEMA.json", schema)

    atlas_entries = [
        {"information": "state", "stored_in": "grid_raw_A bits 0..31", "read_by": ["exists", "alive rule", "matter rule", "census"], "altered_by": ["local update", "injection", "demux post-update"], "transported": "single-source directional copy can discard original state by writing state=1 at destination", "loss": "isolated nonzero zero-direction states can collapse many-to-one", "later_revealable": True},
        {"information": "s_reg", "stored_in": "grid_raw_A bits 32..47", "read_by": ["gradients", "fusion threshold", "incoming reducer", "candidate selection"], "altered_by": ["clock-gated increment", "fusion reset", "reducer sum/cap", "demux delta"], "transported": True, "copied": True, "loss": "cap/reset/many-to-one", "later_revealable": True},
        {"information": "direction", "stored_in": "grid_raw_A bits 48..59", "read_by": ["destination routing", "vector symmetry", "response anchoring"], "altered_by": ["incoming reducer sign composition", "gradient response", "death"], "transported": True, "copied": True, "loss": "sum/sign composition and death", "later_revealable": True},
        {"information": "semantic", "stored_in": "grid_raw_A bits 60..63", "read_by": ["observer immutability", "orphan exclusion", "rule selection", "census"], "altered_by": ["birth/injection", "ordinary local survival", "death"], "transported": "directional arrivals become semantic 1", "copied": "semantic 4 is fixed in place", "loss": "transport normalization/death", "later_revealable": True},
        {"information": "local_clock", "stored_in": "clock_A", "read_by": ["clock-gated s_reg increment"], "altered_by": ["universal +1 mod 2^64", "apparatus injection/reset"], "transported": False, "copied": False, "loss": "not destroyed by ordinary tick; raw accessibility is interaction-conditioned", "later_revealable": True},
        {"information": "position/topology", "stored_in": "array index and toroidal N", "read_by": ["all local neighborhoods", "routing", "interfaces"], "altered_by": ["not dynamically rewritten; occupancy patterns move"], "transported": False, "copied": False, "loss": "coarse observers may quotient translations/routes", "later_revealable": True},
        {"information": "destination multiplicity", "stored_in": "not persistent; relation of positions and directions", "read_by": ["empty-destination reducer"], "altered_by": ["state evolution"], "transported": False, "copied": False, "loss": "coarse bulk observer hides it", "later_revealable": True},
        {"information": "history/lineage", "stored_in": "trajectory plus persistent raw/clock/organization", "read_by": ["history-conditioned apparatuses", "learning/memory mechanisms"], "altered_by": ["interaction and training"], "transported": "mechanism-specific", "copied": "not generally", "loss": "some distinctions erased by many-to-one update", "later_revealable": "mechanism-specific"},
        {"information": "phase", "stored_in": "relations among clocks/events/periodic organizations", "read_by": ["phase-sensitive routes and detectors"], "altered_by": ["evolution", "coupling", "coarse observation"], "transported": "by phase-bearing organization/event", "copied": "not established universally", "loss": "can become inaccessible without being destroyed", "later_revealable": True},
        {"information": "functional_identity", "stored_in": "distributed organization and response law", "read_by": ["standardized interventions"], "altered_by": ["damage", "regeneration", "reinstantiation", "coupling"], "transported": "reconstructed in validated mechanisms", "copied": "raw identity not necessarily", "loss": "functional failure threshold", "later_revealable": True},
    ]
    atlas = {
        "schema": "DEE_INFORMATION_CAUSAL_ATLAS_V1",
        "created_utc": utc(),
        "entries": atlas_entries,
        "parent_mechanism_claim_frequencies": dict(mechanism_counts.most_common()),
        "rule": "Kernel fields are named by executed causal role, not assigned external physical nouns.",
        "buffer_boundary": "Only A plus topology is the pre-tick state; B and delta_demux are implementation/transient state during a tick.",
    }
    write_json(ROOT / "DEE_INFORMATION_CAUSAL_ATLAS.json", atlas)

    # Restored evidence implies parallel candidate branches; all remain candidates until prospective task tests.
    candidates = [
        {"level_id": "L0_FULL_NATIVE", "kind": "reference", "representation": ["raw packed grid", "local clocks", "toroidal topology"], "status": "EXACT_REFERENCE"},
        {"level_id": "L1_ROUTED_EVENT", "kind": "causal-event", "representation": ["destination fibers", "incoming reducer", "event timing", "direction", "semantic"], "status": "BASELINE_VALIDATED_RECHECK_PENDING"},
        {"level_id": "L1_PHASE_HISTORY", "kind": "parallel relational-temporal", "representation": ["clock residues", "phase relations", "ordered history", "lineage"], "status": "CANDIDATE_FROM_RESTORED_CORPUS"},
        {"level_id": "L2_ORGANIZATION_RESPONSE", "kind": "relational-material", "representation": ["interface topology", "basin", "coupling", "standardized response"], "status": "BASELINE_VALIDATED_RECHECK_PENDING"},
        {"level_id": "L2_FUNCTIONAL", "kind": "parallel functional-history", "representation": ["functional identity", "memory", "regeneration", "reinstantiation"], "status": "CANDIDATE_FROM_RESTORED_CORPUS"},
        {"level_id": "L3_STATISTICAL_ENSEMBLE", "kind": "distributional", "representation": ["macroclass", "outcome distribution", "concentration", "fluctuation"], "status": "BASELINE_VALIDATED_RECHECK_PENDING"},
        {"level_id": "L4_CONTINUUM_FIELD", "kind": "coarse-spatial", "representation": ["occupancy-aware coarse state", "spatial distributed predictors"], "status": "PREREQUISITE_OPERATOR_PENDING"},
    ]
    registry = {
        "schema": "CORE16X_LEVEL_DISCOVERY_REGISTRY_V1",
        "created_utc": utc(),
        "baseline_E1_E2_E3_are_not_assumed_final": True,
        "candidates": candidates,
        "selection_requirements": ["compression", "predictive sufficiency", "stable law", "prospective generalization", "nontrivial distinction from lower level"],
        "next_tests": ["occupied-destination operator", "cross-variable hidden resurrection", "embedded observer accessibility", "multi-macroclass probability", "functional-history level discrimination"],
    }
    write_json(ROOT / "LEVEL_DISCOVERY_REGISTRY.json", registry)
    graph = {
        "schema": "CORE16X_REALITY_LEVEL_GRAPH_PROVISIONAL_V1",
        "created_utc": utc(),
        "status": "PROVISIONAL_PENDING_PROSPECTIVE_LEVEL_TESTS",
        "nodes": candidates,
        "edges": [
            {"from": "L0_FULL_NATIVE", "to": "L1_ROUTED_EVENT", "relation": "REDUCTION_CANDIDATE"},
            {"from": "L0_FULL_NATIVE", "to": "L1_PHASE_HISTORY", "relation": "REDUCTION_CANDIDATE"},
            {"from": "L1_ROUTED_EVENT", "to": "L2_ORGANIZATION_RESPONSE", "relation": "COMPOSITION_CANDIDATE"},
            {"from": "L1_PHASE_HISTORY", "to": "L2_FUNCTIONAL", "relation": "HISTORY_SUPPORT_CANDIDATE"},
            {"from": "L2_ORGANIZATION_RESPONSE", "to": "L2_FUNCTIONAL", "relation": "OVERLAP_OR_MERGE_UNRESOLVED"},
            {"from": "L2_ORGANIZATION_RESPONSE", "to": "L3_STATISTICAL_ENSEMBLE", "relation": "ENSEMBLE_REDUCTION_CANDIDATE"},
            {"from": "L1_ROUTED_EVENT", "to": "L4_CONTINUUM_FIELD", "relation": "COARSE_DYNAMICS_PREREQUISITE"},
        ],
        "interpretation": "The restored corpus requires testing a branched/overlapping graph; it does not yet establish seven distinct empirical levels.",
    }
    write_json(ROOT / "REALITY_LEVEL_GRAPH.json", graph)
    append_ndjson(ROOT / "QUESTION_TREE.ndjson", {
        "question_id": "C16X-Q002",
        "parent_id": "C16X-Q001",
        "parent_result_hash": canonical_hash({"schema": schema["reference_state"], "candidates": [c["level_id"] for c in candidates]}),
        "what_was_learned": "The complete persistent kernel state is raw+clock+topology; phase/history/lineage/functional identity are derived causal relations, not undiscovered primitive arrays.",
        "new_uncertainty": "Can a compressed occupancy-aware local operator extend routed closure across occupied destinations without reverting to full raw state?",
        "competing_interpretations": ["incumbents block ordinary incoming reduction and need matter-neighborhood statistics", "incoming reducer composes with incumbent", "fusion/XNOR branches require a richer operator"],
        "why_next_experiment_matters": "It attacks the exact prior multistep failure and determines whether L4 coarse effective dynamics exists.",
        "status": "OPEN",
    })
    append_ndjson(ROOT / "KERNEL_DIALOGUE.ndjson", {
        "question_id": "C16X-Q002",
        "raw_outcome": {"stored_components": 3, "transient_components": len(transient), "derived_relations": len(emergent)},
        "mechanism_update": "Separate persistent fields from causal relations and within-tick variables; candidate levels must not pretend relational history is a hidden buffer.",
        "next_high_information_question": "Derive and binary-test the incumbent-aware destination operator.",
    })
    update_state(
        status="FULL_STATE_AUDITED",
        current_phase="OCCUPANCY_AWARE_OPERATOR_DISCOVERY",
        full_state_schema_pass=True,
        level_graph_status="PROVISIONAL",
        completed_checkpoints=["BASELINE_AUDIT", "FULL_PARENT_CLAIM_INGESTION", "FULL_STATE_CAUSAL_AUDIT"],
    )
    print(json.dumps({"stored": len(stored), "transient": len(transient), "derived": len(emergent), "candidate_level_nodes": len(candidates), "mechanism_claims": dict(mechanism_counts.most_common(8))}, indent=2))


if __name__ == "__main__":
    main()
