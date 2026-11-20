#!/usr/bin/env python3
"""NRD06: identity-specific history conditioning and gated recurrent update pilot."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ENGINEERING = ROOT.parent
NRD05_RUNNERS = (
    ROOT.parent / "05_HISTORY_CONDITIONED_TRANSFORMATION" / "RUNNERS"
    if (ROOT.parent / "05_HISTORY_CONDITIONED_TRANSFORMATION" / "RUNNERS").is_dir()
    else ENGINEERING / "INGENIERIA_05_HISTORY_CONDITIONED_TRANSFORMATION" / "RUNNERS"
)
sys.path.insert(0, str(NRD05_RUNNERS))

import run_nrd05_history_conditioned_transformation as nrd05  # noqa: E402

HISTORIES = {"H0": "no_events", "HA": "AB", "HB": "BA"}
HORIZONS = nrd05.HORIZONS
PAIR_NAMES = (("H0", "HA"), ("H0", "HB"), ("HA", "HB"))


def tick_all(worlds, count):
    for _ in range(count):
        for world in worlds.values():
            world.tick()


def effect_pair(branches, history):
    return nrd05.pair_effect(branches[history]["PROBE"], branches[history]["CONTROL"])


def pair_label(left, right):
    return f"{left}_vs_{right}"


def classify_analysis(result):
    """Classify a transformation from the complete immediate+future signature.

    Equal immediate XOR effects do not imply equal transformations when the
    frozen future panel separates those effects at both horizons.
    """
    distinct = {}
    equivalent = {}
    for left, right in PAIR_NAMES:
        label = pair_label(left, right)
        comparison = result["pairwise_comparisons"][label]
        immediate_equal = comparison["immediate"]["equal"]
        future_distinct = all(comparison["distinct_by_horizon"].values())
        future_equivalent = all(comparison["equivalent_by_horizon"].values())
        distinct[label] = (not immediate_equal) or future_distinct
        equivalent[label] = immediate_equal and future_equivalent
    if all(distinct.values()):
        classification = "HISTORY_SPECIFIC_TRANSFORMATION"
    elif equivalent["HA_vs_HB"] and distinct["H0_vs_HA"] and distinct["H0_vs_HB"]:
        classification = "GENERIC_HISTORY_CONDITIONING"
    elif all(equivalent.values()):
        classification = "NO_HISTORY_SPECIFIC_EFFECT"
    else:
        classification = "UNEXPECTED_NATIVE_HISTORY_MECHANISM"
    result["classification"] = classification
    result["pairwise_distinct"] = distinct
    result["pairwise_equivalent"] = equivalent
    return result


def analyze_three(branches, diagnostics):
    immediate = {}
    effects = {history: effect_pair(branches, history) for history in HISTORIES}
    for history in HISTORIES:
        immediate[history] = nrd05.effect_signature(
            branches[history]["PROBE"], branches[history]["CONTROL"]
        )

    comparisons = {}
    distinct = {}
    equivalent = {}
    for left, right in PAIR_NAMES:
        label = pair_label(left, right)
        immediate_cmp = nrd05.compare_effects(effects[left], effects[right])
        future = {}
        horizon_distinct = {}
        horizon_equivalent = {}
        for horizon in HORIZONS:
            row = {}
            any_difference = False
            all_equal = True
            for category in ("C0", "C3", "RESPONSE"):
                left_effect = nrd05.pair_effect(
                    diagnostics[left]["PROBE"][category][horizon],
                    diagnostics[left]["CONTROL"][category][horizon],
                )
                right_effect = nrd05.pair_effect(
                    diagnostics[right]["PROBE"][category][horizon],
                    diagnostics[right]["CONTROL"][category][horizon],
                )
                cmp = nrd05.compare_effects(left_effect, right_effect)
                row[category] = {
                    "left_effect": nrd05.effect_signature(
                        diagnostics[left]["PROBE"][category][horizon],
                        diagnostics[left]["CONTROL"][category][horizon],
                    ),
                    "right_effect": nrd05.effect_signature(
                        diagnostics[right]["PROBE"][category][horizon],
                        diagnostics[right]["CONTROL"][category][horizon],
                    ),
                    "comparison": cmp,
                }
                any_difference = any_difference or not cmp["equal"]
                all_equal = all_equal and cmp["equal"]
            future[str(horizon)] = row
            horizon_distinct[str(horizon)] = any_difference
            horizon_equivalent[str(horizon)] = all_equal
        comparisons[label] = {
            "immediate": immediate_cmp,
            "future": future,
            "distinct_by_horizon": horizon_distinct,
            "equivalent_by_horizon": horizon_equivalent,
        }
        distinct[label] = (not immediate_cmp["equal"]) or all(horizon_distinct.values())
        equivalent[label] = immediate_cmp["equal"] and all(horizon_equivalent.values())

    if all(distinct.values()):
        classification = "HISTORY_SPECIFIC_TRANSFORMATION"
    elif equivalent["HA_vs_HB"] and distinct["H0_vs_HA"] and distinct["H0_vs_HB"]:
        classification = "GENERIC_HISTORY_CONDITIONING"
    elif all(equivalent.values()):
        classification = "NO_HISTORY_SPECIFIC_EFFECT"
    else:
        classification = "UNEXPECTED_NATIVE_HISTORY_MECHANISM"
    return classify_analysis({
        "classification": classification,
        "transformation_signatures": immediate,
        "pairwise_comparisons": comparisons,
        "pairwise_distinct": distinct,
        "pairwise_equivalent": equivalent,
    })


def save_case_telemetry(prefix, stage, branches, diagnostics, telemetry):
    for history in HISTORIES:
        for branch in ("CONTROL", "PROBE"):
            state = branches[history][branch]
            base = f"{prefix}_{stage}_{history}_{branch}"
            telemetry[f"{base}_raw_a"] = state[0]
            telemetry[f"{base}_clock_a"] = state[1]
            for category in ("C0", "C3", "RESPONSE"):
                for horizon in HORIZONS:
                    future = diagnostics[history][branch][category][horizon]
                    telemetry[f"{base}_{category}_h{horizon}_raw"] = future[0]
                    telemetry[f"{base}_{category}_h{horizon}_clock"] = future[1]


def run_specificity_case(kernel, cfg, probe_geometry, require_disjoint, telemetry):
    nrd05.configure_pulse(cfg)
    constructed = {
        history: nrd05.construct(kernel, nrd05.apparatus(cfg, mode))
        for history, mode in HISTORIES.items()
    }
    worlds = {history: value[0] for history, value in constructed.items()}
    ports = constructed["H0"][1]
    tick_all(worlds, 4)
    pre_probe = {history: nrd05.checkpoint(world) for history, world in worlds.items()}

    branches = {
        history: {
            "CONTROL": nrd05.NativeWorld(kernel, state[0], state[1]),
            "PROBE": nrd05.NativeWorld(kernel, state[0], state[1]),
        }
        for history, state in pre_probe.items()
    }
    touched = {}
    for history in HISTORIES:
        touched[history] = nrd05.initiate_e2(branches[history]["PROBE"], ports, cfg, probe_geometry)
    if not (touched["H0"] == touched["HA"] == touched["HB"]):
        raise RuntimeError("The frozen probe did not touch identical coordinates across histories")

    history_routes = (
        nrd05.direct_route_set(ports, cfg, nrd05.MAIN_GEOMETRY, "E1_AB")
        | nrd05.direct_route_set(ports, cfg, nrd05.MAIN_GEOMETRY, "E2_BA")
    )
    probe_route = nrd05.direct_route_set(ports, cfg, probe_geometry, "E2_BA")
    overlap = sorted(history_routes & probe_route)
    if require_disjoint and overlap:
        raise nrd05.GeometryNotClean(f"Probe route overlaps prior-history routes: {overlap}")

    flat = {f"{history}_{branch}": world for history, pair in branches.items() for branch, world in pair.items()}
    tick_all(flat, 4)
    stages = {
        "D0": {
            history: {branch: nrd05.checkpoint(world) for branch, world in pair.items()}
            for history, pair in branches.items()
        }
    }
    tick_all(flat, 64)
    stages["D64"] = {
        history: {branch: nrd05.checkpoint(world) for branch, world in pair.items()}
        for history, pair in branches.items()
    }

    analyses = {}
    for stage, stage_branches in stages.items():
        diagnostics = {
            history: {branch: nrd05.diagnostic(kernel, state) for branch, state in pair.items()}
            for history, pair in stage_branches.items()
        }
        analyses[stage] = analyze_three(stage_branches, diagnostics)
        save_case_telemetry(cfg["id"], stage, stage_branches, diagnostics, telemetry)

    return {
        "configuration": cfg["id"],
        "histories": {history: mode.upper() for history, mode in HISTORIES.items()},
        "common_checkpoint_ticks": 4,
        "probe_touched": touched,
        "prior_history_direct_route": [list(q) for q in sorted(history_routes)],
        "probe_direct_route": [list(q) for q in sorted(probe_route)],
        "route_overlap": [list(q) for q in overlap],
        "direct_routes_disjoint": not overlap,
        "stages": analyses,
        "retained_history_specificity": (
            analyses["D0"]["classification"] == "HISTORY_SPECIFIC_TRANSFORMATION"
            and analyses["D64"]["classification"] == "HISTORY_SPECIFIC_TRANSFORMATION"
        ),
        "retained_generic_conditioning": (
            analyses["D0"]["classification"] == "GENERIC_HISTORY_CONDITIONING"
            and analyses["D64"]["classification"] == "GENERIC_HISTORY_CONDITIONING"
        ),
    }


def run_c4_capacity(kernel, state, cfg, telemetry):
    control = nrd05.NativeWorld(kernel, state[0], state[1])
    challenged = nrd05.NativeWorld(kernel, state[0], state[1])
    offsets = ((3, 0, 0), (-3, 0, 0), (0, 3, 0), (0, -3, 0), (0, 0, 3), (0, 0, -3))
    touched = []
    for offset in offsets:
        transformed = nrd05.transform(offset, cfg["permutation"], cfg["signs"])
        q = tuple((cfg["origin"][i] + transformed[i]) % cfg["n"] for i in range(3))
        direction = tuple(-int(np.sign(v)) for v in transformed)
        challenged.inject(q, nrd05.pack(8000, 0, direction, 1), 0)
        touched.append(list(q))
    tick_all({"CONTROL": control, "C4": challenged}, 4)
    post = {"CONTROL": nrd05.checkpoint(control), "C4": nrd05.checkpoint(challenged)}
    diag = {branch: nrd05.diagnostic(kernel, branch_state) for branch, branch_state in post.items()}
    immediate_cmp = nrd05.compare_effects(nrd05.pair_effect(post["C4"], post["CONTROL"]), (np.zeros_like(post["C4"][0]), np.zeros_like(post["C4"][1])))
    by_horizon = {}
    for horizon in HORIZONS:
        differs = False
        rows = {}
        for category in ("C0", "C3", "RESPONSE"):
            comparison = nrd05.compare_effects(
                nrd05.pair_effect(diag["C4"][category][horizon], diag["CONTROL"][category][horizon]),
                (np.zeros_like(diag["C4"][category][horizon][0]), np.zeros_like(diag["C4"][category][horizon][1])),
            )
            rows[category] = comparison
            differs = differs or not comparison["equal"]
        by_horizon[str(horizon)] = {"future_distinction": differs, "comparisons_to_zero_effect": rows}
    for branch in ("CONTROL", "C4"):
        telemetry[f"F3_CAPACITY_{branch}_raw_a"] = post[branch][0]
        telemetry[f"F3_CAPACITY_{branch}_clock_a"] = post[branch][1]
        for category in ("C0", "C3", "RESPONSE"):
            for horizon in HORIZONS:
                telemetry[f"F3_CAPACITY_{branch}_{category}_h{horizon}_raw"] = diag[branch][category][horizon][0]
                telemetry[f"F3_CAPACITY_{branch}_{category}_h{horizon}_clock"] = diag[branch][category][horizon][1]
    return {
        "challenge": "C4_SIX_AXIS_RADIUS3",
        "touched": touched,
        "immediate_distinction": not immediate_cmp["equal"],
        "future_by_horizon": by_horizon,
        "future_causal_capacity_observed": (not immediate_cmp["equal"]) and all(row["future_distinction"] for row in by_horizon.values()),
        "scope_note": "This is a frozen diagnostic test of capacity to produce a further retained future distinction, not by itself a claim of autonomous renewed competence.",
    }


def run_recurrent_pilot(kernel, cfg, telemetry):
    nrd05.configure_pulse(cfg)
    template, ports = nrd05.construct(kernel, nrd05.apparatus(cfg, "no_events"))
    worlds = {name: nrd05.NativeWorld(kernel, template.raw_a, template.clock_a) for name in ("G0", "G1", "G2")}
    sequence = {"F0": nrd05.checkpoint(worlds["G2"])}
    nrd05.initiate_e1(worlds["G1"], ports, cfg)
    nrd05.initiate_e1(worlds["G2"], ports, cfg)
    tick_all(worlds, 4)
    sequence["F1"] = nrd05.checkpoint(worlds["G2"])
    nrd05.initiate_e2(worlds["G2"], ports, cfg, nrd05.MAIN_GEOMETRY)
    tick_all(worlds, 4)
    sequence["F2"] = nrd05.checkpoint(worlds["G2"])

    branches = {
        name: {
            "CONTROL": nrd05.NativeWorld(kernel, world.raw_a, world.clock_a),
            "PROBE": nrd05.NativeWorld(kernel, world.raw_a, world.clock_a),
        }
        for name, world in worlds.items()
    }
    recurrent_histories = {"H0": branches["G0"], "HA": branches["G1"], "HB": branches["G2"]}
    touched = {}
    for history in HISTORIES:
        touched[history] = nrd05.initiate_e2(recurrent_histories[history]["PROBE"], ports, cfg, nrd05.SEPARATED_GEOMETRY)
    flat = {f"{history}_{branch}": world for history, pair in recurrent_histories.items() for branch, world in pair.items()}
    tick_all(flat, 4)
    post = {
        history: {branch: nrd05.checkpoint(world) for branch, world in pair.items()}
        for history, pair in recurrent_histories.items()
    }
    sequence["F3"] = post["HB"]["PROBE"]
    diagnostics = {
        history: {branch: nrd05.diagnostic(kernel, state) for branch, state in pair.items()}
        for history, pair in post.items()
    }
    analysis = analyze_three(post, diagnostics)
    save_case_telemetry("RECURRENT", "F3", post, diagnostics, telemetry)
    for label, state in sequence.items():
        telemetry[f"SEQUENCE_{label}_raw_a"] = state[0]
        telemetry[f"SEQUENCE_{label}_clock_a"] = state[1]
    capacity = run_c4_capacity(kernel, sequence["F3"], cfg, telemetry)
    recurrent = analysis["classification"] == "HISTORY_SPECIFIC_TRANSFORMATION"
    return {
        "sequence_state_hashes": {
            label: {"raw_a": nrd05.sha_array(state[0]), "clock_a": nrd05.sha_array(state[1])}
            for label, state in sequence.items()
        },
        "third_probe_touched": touched,
        "third_transformation_analysis": analysis,
        "third_history_conditioned_update": recurrent,
        "future_capacity": capacity,
        "classification": (
            "DEE_NATIVE_RECURRENT_HISTORY_CONDITIONED_ADAPTATION"
            if recurrent and capacity["future_causal_capacity_observed"]
            else "THIRD_UPDATE_WITHOUT_CONFIRMED_FUTURE_CAPACITY"
            if recurrent
            else "NO_THIRD_HISTORY_SPECIFIC_UPDATE"
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--resume-after-main", action="store_true")
    args = parser.parse_args()
    kernel, runtime = nrd05.load_kernel(args.threads)
    telemetry_path = ROOT / "TELEMETRY" / "NRD06_SPECIFICITY_STATES_AND_FUTURES.npz"
    telemetry = {}
    executed = {}
    limitations = []

    if args.resume_after_main:
        previous = json.loads((ROOT / "RESULTS" / "NRD06_HISTORY_SPECIFICITY.json").read_text(encoding="utf-8"))
        main_case = previous["executed_cases"]["MAIN_S0"]
        for stage in ("D0", "D64"):
            main_case["stages"][stage] = classify_analysis(main_case["stages"][stage])
        main_case["retained_history_specificity"] = all(
            main_case["stages"][stage]["classification"] == "HISTORY_SPECIFIC_TRANSFORMATION"
            for stage in ("D0", "D64")
        )
        main_case["retained_generic_conditioning"] = all(
            main_case["stages"][stage]["classification"] == "GENERIC_HISTORY_CONDITIONING"
            for stage in ("D0", "D64")
        )
        with np.load(telemetry_path) as prior_telemetry:
            telemetry = {name: prior_telemetry[name] for name in prior_telemetry.files}
    else:
        main_case = run_specificity_case(kernel, nrd05.CONFIGS["MAIN_S0"], nrd05.MAIN_GEOMETRY, False, telemetry)
    executed["MAIN_S0"] = main_case
    main_positive = main_case["stages"]["D0"]["classification"] in {
        "HISTORY_SPECIFIC_TRANSFORMATION", "GENERIC_HISTORY_CONDITIONING"
    }
    main_specific_retained = main_case["retained_history_specificity"]

    if main_positive:
        try:
            executed["SEPARATED_S0"] = run_specificity_case(
                kernel, nrd05.CONFIGS["SEPARATED_S0"], nrd05.SEPARATED_GEOMETRY, True, telemetry
            )
        except nrd05.GeometryNotClean as error:
            limitations.append({"configuration": "SEPARATED_S0", "reason": str(error)})

    if main_specific_retained:
        for name in ("FRESH_V1", "FRESH_V2"):
            executed[name] = run_specificity_case(
                kernel, nrd05.CONFIGS[name], nrd05.MAIN_GEOMETRY, False, telemetry
            )

    fresh_pass = all(
        name in executed and executed[name]["retained_history_specificity"]
        for name in ("FRESH_V1", "FRESH_V2")
    )
    recurrent = None
    if main_specific_retained and fresh_pass:
        recurrent = run_recurrent_pilot(kernel, nrd05.CONFIGS["MAIN_S0"], telemetry)

    np.savez_compressed(telemetry_path, **telemetry)

    separated = executed.get("SEPARATED_S0")
    route_survives = bool(separated and separated["retained_history_specificity"])
    path_reuse = bool(main_specific_retained and separated and not route_survives)
    if main_specific_retained and fresh_pass:
        specificity_status = "DEE_NATIVE_HISTORY_SPECIFIC_TRANSFORMATION"
    elif main_case["retained_generic_conditioning"]:
        specificity_status = "GENERIC_HISTORY_CONDITIONING"
    elif main_case["stages"]["D0"]["classification"] == "HISTORY_SPECIFIC_TRANSFORMATION":
        specificity_status = "TRANSIENT_HISTORY_SPECIFICITY"
    elif main_case["stages"]["D0"]["classification"] == "NO_HISTORY_SPECIFIC_EFFECT":
        specificity_status = "NO_HISTORY_SPECIFIC_EFFECT"
    else:
        specificity_status = "UNEXPECTED_NATIVE_HISTORY_MECHANISM"

    overall = recurrent["classification"] if recurrent else specificity_status
    result = nrd05.seal({
        "experiment_id": "NRD06_HISTORY_SPECIFICITY_AND_RECURRENT_CHANGE",
        "status": overall,
        "specificity_status": specificity_status,
        "runtime": runtime,
        "executed_cases": executed,
        "limitations": limitations,
        "adjudication": {
            "history_identity_matters": main_specific_retained and fresh_pass,
            "generic_prior_perturbation_only": specificity_status == "GENERIC_HISTORY_CONDITIONING",
            "effect_persists_D64": main_specific_retained or main_case["retained_generic_conditioning"],
            "fresh_V1_V2_pass": fresh_pass,
            "alternate_route_executed": separated is not None,
            "specificity_survives_disjoint_probe_route": route_survives,
            "history_dependent_path_reuse": path_reuse,
            "recurrent_F3_executed": recurrent is not None,
            "third_history_conditioned_update": bool(recurrent and recurrent["third_history_conditioned_update"]),
            "future_causal_capacity_observed": bool(recurrent and recurrent["future_capacity"]["future_causal_capacity_observed"]),
            "formal_RW3": False,
            "L4": False,
        },
        "recurrent_pilot": recurrent,
        "host_intervention_statement": "All histories and probes used frozen physical DEE carrier constructions. Python initiated only those frozen experiences and otherwise ticked, cloned diagnostic branches, checkpointed, observed, logged, and stopped. No discovered RAW support or adaptive state was copied into a world.",
        "telemetry": "TELEMETRY/NRD06_SPECIFICITY_STATES_AND_FUTURES.npz",
    })
    out = ROOT / "RESULTS" / "NRD06_HISTORY_SPECIFICITY.json"
    nrd05.write_json(out, result)
    if recurrent is not None:
        nrd05.write_json(ROOT / "RESULTS" / "NRD06_RECURRENT_PILOT.json", nrd05.seal(recurrent))
    print(json.dumps({
        "result": str(out),
        "status": overall,
        "specificity_status": specificity_status,
        "cases": {
            name: {
                "D0": case["stages"]["D0"]["classification"],
                "D64": case["stages"]["D64"]["classification"],
                "retained_specificity": case["retained_history_specificity"],
                "routes_disjoint": case["direct_routes_disjoint"],
            }
            for name, case in executed.items()
        },
        "recurrent": None if recurrent is None else {
            "classification": recurrent["classification"],
            "third_update": recurrent["third_history_conditioned_update"],
            "future_capacity": recurrent["future_capacity"]["future_causal_capacity_observed"],
        },
        "limitations": limitations,
    }, indent=2))


if __name__ == "__main__":
    main()
