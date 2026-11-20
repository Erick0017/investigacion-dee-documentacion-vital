"""Pure reanalysis finalizer: JSON inputs only, no native import or evolution.

Keeps the executed local replay artifacts intact.  Adds explicit case identity
to the event graph and separates endpoint-compatible transport from reconstructed
single-transition dependencies.  Different cases are never joined as one MAIN.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def observed_endpoint_check(case, source, target):
    dt = target["tick"] - source["tick"]
    predicted = [(source["site"][i] + dt * source["direction"][i]) % 67 for i in range(3)]
    return {
        "case": case,
        "source": source,
        "target": target,
        "delta_ticks": dt,
        "predicted_wrapped_site_without_interaction": predicted,
        "endpoint_fields_compatible": (
            predicted == target["site"]
            and source["raw"] == target["raw"]
            and target["clock"] - source["clock"] == dt
        ),
        "coverage": "OBSERVED_ENDPOINTS_WITH_BALLISTIC_COMPATIBILITY_NOT_EVERY_INTERMEDIATE_TRANSITION",
        "not_dependency_edge": True,
        "boundary": "A matching payload/direction at two endpoints does not establish unique ancestry. Single-step local reconstructions and selective interventions are stored separately.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    out = root / "resultados/CHANNEL_ANALYSIS"
    old_graph = read(out / "EVENT_GRAPH.json")
    windows = {label: read(out / label / "WINDOW.json") for label in (
        "A_ACQUISITION", "B_CONTACT", "B_COMMON_QUERY", "BANK_COST"
    )}
    graph = {
        "scope": "Four separate reconstructed local transitions, identified by actual case. No link joins MAIN_MINUS t155 to FULL_PLUS t153.",
        "source_graph": "resultados/CHANNEL_ANALYSIS/EVENT_GRAPH.json",
        "source_graph_sha256": digest(out / "EVENT_GRAPH.json"),
        "nodes": [],
        "edges": [],
        "unreconstructed_transitions": [
            "A common query t69->70 was observed in MAIN but not among these four local branch reconstructions.",
            "Environmental interception and final resource delivery were observed in MAIN; only the first cost encounter t152->153 was locally reconstructed here.",
        ],
    }
    for node in old_graph["nodes"]:
        label = node["id"].split(":", 1)[0]
        graph["nodes"].append({**node, "source_case": windows[label]["source_case"],
                               "window_evidence": f"resultados/CHANNEL_ANALYSIS/{label}/WINDOW.json"})
    for edge in old_graph["edges"]:
        label = edge["source"].split(":", 1)[0]
        graph["edges"].append({**edge, "source_case": windows[label]["source_case"],
                               "coverage": "OBSERVED_SINGLE_NATIVE_TRANSITION_RULE_PARTICIPATION"})

    main_minus = read(root / "resultados/confirmacion/MAIN_MINUS/NATIVO/MEASUREMENTS.json")
    full_plus = read(root / "resultados/confirmacion/FULL_PLUS/NATIVO/MEASUREMENTS.json")
    source_a = next(s for s in windows["B_CONTACT"]["reconstruction"]["sources"] if s["s_reg"] == 21)
    source_b = next(s for s in windows["B_COMMON_QUERY"]["reconstruction"]["sources"] if s["s_reg"] == 37)
    source_action = next(s for s in windows["BANK_COST"]["reconstruction"]["sources"] if s["s_reg"] == 42)
    graph["transport_endpoint_checks_not_certified_edges"] = [
        observed_endpoint_check("MAIN_MINUS", main_minus["A_emission"], source_a),
        observed_endpoint_check("MAIN_MINUS", windows["B_CONTACT"]["reconstruction"]["observed_post"], source_b),
        observed_endpoint_check("FULL_PLUS", full_plus["B_common_responses"]["Bplus"], source_action),
    ]
    write(out / "EVENT_GRAPH_WITH_CASE_SCOPE.json", graph)

    records = read(out / "RECORD_ANALYSIS.json")
    by_id = {row["id"]: row for row in records["rows"]}
    cut = read(out / "CUT_WORLD_EQUIVALENCE.json")
    inv = read(root / "resultados/INVERSE_MECHANISM/SUMMARY.json")
    material_path = root / "resultados/INVERSE_MECHANISM/OCCUPIED_REFINEMENT/MATERIAL_BRANCH.json"
    material = read(material_path)
    core_expected = {
        "src/channel.py": "a313f41e923fe22cfd2a7716cdf108a0b061bca72f805e85c6d0dc3f8d903141",
        "src/channel_dual.py": "8660e91ccf56f9ede253b31971b289e244319c473d49a25fa276bf65143463c3",
        "src/channel_discovery.py": "d2aa5452e1edf292404013e1e206a26d1c0b2314bc9e4253c7f45976e14647d9",
    }
    frozen = {p: {"expected": expected, "actual": digest(root / p), "unchanged": digest(root / p) == expected}
              for p, expected in core_expected.items()}
    selected = ["MAIN_MINUS", "FULL_PLUS", "CUT_MINUS", "CUT_PLUS", "B_NAIVE", "B_WRONG_RELATION",
                "B_UNPAIRED", "B_TEACHER_ONLY", "A_UNPAIRED", "A_NAIVE", "A_QUERY_OMITTED",
                "MESSAGE_CONSTANT_PLUS", "MESSAGE_OFF_DIRECTION", "B_ROUTE_COMPONENT_REMOVED",
                "B_ACQUIRED_COMPONENT_REMOVED", "SHAM_DUMMY_REMOVAL", "CUT_WITH_ACTUATOR_REFERENCE",
                "RESERVED_TRANSLATION_PLUS", "RESERVED_TRANSLATION_MINUS_SWAPPED"]
    result = {
        "classification": "READ_ONLY_REANALYSIS_NOT_NEW_NATIVE_CASES",
        "native_calls_in_this_finalizer": 0,
        "native_records_reanalyzed": records["native_case_records"],
        "case_counts_boundary": "27 native confirmation records. Language controls, inverse diagnostics, technical replays and discovery attempts remain separate identities; none is counted again as an independent native confirmation.",
        "frozen_core": frozen,
        "field_mechanism": [
            {"event": "A experience acquisition", "case": "MAIN_MINUS", "transition": [2, 3],
             "observed": "5(-1,0,0)+11(+1,-1,0) ->16(0,-1,0) at empty A", "source": "A_ACQUISITION/WINDOW.json"},
            {"event": "Message contacts acquired B relation", "case": "MAIN_MINUS", "transition": [87, 88],
             "observed": "21(-1,-1,0)+16(0,0,+1) ->37(-1,-1,+1) at empty Bminus", "source": "B_CONTACT/WINDOW.json"},
            {"event": "Retained relation receives common regional physical query", "case": "MAIN_MINUS", "transition": [154, 155],
             "observed": "37(-1,-1,+1)+5(0,-1,0) ->42(-1,-1,+1)", "source": "B_COMMON_QUERY/WINDOW.json"},
            {"event": "Physical action spends optional resource", "case": "FULL_PLUS", "transition": [152, 153],
             "observed": "42(-1,+1,+1)+3(+1,0,-1) ->45(0,+1,0)", "source": "BANK_COST/WINDOW.json"},
        ],
        "branch_coverage": {
            "all_four": "Observed empty-destination directional reducer; crystal/XNOR/semantic4 precedence inspected and not selected. All evaluated RAW, clock, state, semantic, payload and direction match native output.",
            "complete_replay_RAW_clock_comparison": ["A_ACQUISITION", "B_CONTACT", "B_COMMON_QUERY"],
            "bank_comparison_scope": "Actual stored target at153 matches; no historical full-world153 checkpoint exists, so no complete-world parity claim is made for BANK_COST.",
            "demux": "No overflow postpass applicable in these windows. The empty-destination helper historically named buscar_fuente_demux is not the aplicar_demux overflow postpass.",
        },
        "finite_channel_isolation": cut,
        "first_observed_context_differences": {
            key: {role: panel["first_observed_difference"]["tick"] if panel["first_observed_difference"] else None
                  for role, panel in value["contexts"].items()}
            for key, value in records["precontact_contrasts"].items()
        },
        "functional_contrasts": [{"id": ident, "F_sum": by_id[ident]["primary_sum"],
                                  "R_sum": by_id[ident]["optional_sum"], "external_utility": by_id[ident]["external_utility"],
                                  "physical_profiles": by_id[ident]["physical_bank_profiles"],
                                  "admission": by_id[ident]["admission"]} for ident in selected],
        "cost_baselines": records["physical_fixed_policy_cost_panel"],
        "selectivity": {
            "acquired_B_z": "Compatible acquired z, sender history and transmitted message are required for the measured direction-dependent bank use in these controls. Equal-dose wrong/unpaired B and B-naive controls do not supply z to the common y-query.",
            "field_compensation": "Postcontact DY removal retains utility5 because the prepared common query supplies y. DZ removal gives utility4 because that query contains no z. This is selective contextual compensation, not universal repair or erasure of all acquired information.",
            "constant_message": "Forcing the opposite-context A message to the same plus direction gives utility3 rather than5. Content/direction matters, not just presence or charge21.",
            "actuator_rescue": "CUT_WITH_ACTUATOR_REFERENCE returns utility5 by a declared external diagnostic injection at the outbound action site. It checks actuator/environment availability; it does not restore the learned state or demonstrate native reacquisition.",
        },
        "lexical_inverse_obstacle": {
            "W1": {"transition": [252, 253, 254], "observed": "The forward21 and residual uncued opposite report11 reach an empty common site: reducer produces32 direction0 at253, isolated state vanishes254.",
                   "evidence": "resultados/INVERSE_MECHANISM/W1_CANDIDATE_253/MECHANISM.json"},
            "W2": {"transition": [286, 287], "observed": "Forward21 and opposite report11 instead occupy adjacent sites and each points at the other. Both occupied material centers have n_active1, tetra false, T_local2.5, rule_value0 and become RAW0 at287 before any empty-site reducer can combine them.",
                   "evidence": "resultados/INVERSE_MECHANISM/OCCUPIED_REFINEMENT/MATERIAL_BRANCH.json",
                   "external_operation_journal_unchanged": material["external_operation_journal_unchanged"],
                   "pending_inputs_at267": material["pending_inputs_at_source"]},
            "falsified_hypothesis_preserved": "The initial prediction of a W2 empty-site coincidence at320 was contradicted by the recorded earlier loss at287. The original candidate320 replay and config remain in INVERSE_MECHANISM/SUMMARY.json; no retiming was used to manufacture an inverse result.",
            "inverse_window": "Later probes were admitted and produced input-only load5 at the queried hubs. These records do not show an admission rejection or the predicted inverse response26.",
            "memory_expression_boundary": "Loss of the specifically tracked21 candidates is established. This does not prove that every causally relevant trace of the history has disappeared from the full world, nor that no other interface could expose it.",
        },
        "modality_and_scope": [
            "A/B are declared finite mobile mechanisms and one distributed receiver, not two complete basal bodies inferred from two carriers.",
            "Inputs and synthetic environmental threats/resources are supplied through predeclared interfaces under a fixed EXPERIENCE_PROTOCOL. Native transformations, transport and bank encounters evolve under v27.",
            "The event graph and scores are external measurements; no oracle or utility value is fed into native state.",
            "Semantic presence/absence at a specified sampling window is external transduction, not a demonstrated native detector of arbitrary absence.",
            "No learned optimality beyond the finite two-context panel, unlimited memory, arbitrary language acquisition, recurrent self-repair or global cognitive verdict is claimed.",
        ],
        "coverage_gaps": [
            "The sparse transport endpoint checks are compatible with the declared paths but do not certify every intermediate ancestry transition.",
            "Local rule participation is not counterfactual necessity; the existing selective intervention cases supply the separate finite causal contrasts.",
            "No unique minimal global causal graph has been established.",
            "Inverse production is not demonstrated by the unmodified forward language continuation; observed obstacles and falsified hypotheses are preserved.",
            "The finite bank task and external score do not establish that B learned arbitrary utility functions or discovered its own evaluation metric.",
        ],
        "evidence": {
            "case_scoped_graph": "resultados/CHANNEL_ANALYSIS/EVENT_GRAPH_WITH_CASE_SCOPE.json",
            "original_graph_preserved": "resultados/CHANNEL_ANALYSIS/EVENT_GRAPH.json",
            "inverse_candidate_window_count": len(inv["windows"]),
            "instrumented_material_refinement": "resultados/INVERSE_MECHANISM/OCCUPIED_REFINEMENT/MATERIAL_BRANCH.json",
        },
        "closure": "No further native windows opened after the final267->287 instrumented repeat. This finalizer imports no DEE module and reads JSON only.",
    }
    write(out / "MECHANISM_SUMMARY.json", result)
    print(json.dumps({"native_records": len(by_id), "all_frozen_core_unchanged": all(x["unchanged"] for x in frozen.values()),
                      "output": str(out / "MECHANISM_SUMMARY.json"), "native_calls": 0}))


if __name__ == "__main__":
    main()
