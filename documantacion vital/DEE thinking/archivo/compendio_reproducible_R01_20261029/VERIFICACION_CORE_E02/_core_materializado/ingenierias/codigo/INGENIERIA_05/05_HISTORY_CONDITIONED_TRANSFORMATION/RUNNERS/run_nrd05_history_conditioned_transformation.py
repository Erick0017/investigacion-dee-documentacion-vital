#!/usr/bin/env python3
"""NRD05: four-world test of history-conditioned transformation by identical E2."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ENGINEERING = ROOT.parent
BUNDLED = ROOT.parent / "04_RAW_CAUSAL_MINIMUM" / "DEPENDENCIES" if (ROOT.parent / "04_RAW_CAUSAL_MINIMUM" / "DEPENDENCIES").is_dir() else ROOT / "DEPENDENCIES"
ING02_RUNNERS = BUNDLED / "INGENIERIA_02_RUNNERS" if (BUNDLED / "INGENIERIA_02_RUNNERS").is_dir() else ENGINEERING / "INGENIERIA_02" / "RUNNERS"
NRD04_RUNNERS = ROOT.parent / "04_RAW_CAUSAL_MINIMUM" / "RUNNERS" if (ROOT.parent / "04_RAW_CAUSAL_MINIMUM" / "RUNNERS").is_dir() else ENGINEERING / "INGENIERIA_05_RAW_CAUSAL_MINIMUM" / "RUNNERS"
if BUNDLED.is_dir():
    os.environ.setdefault("DEE_V27_TESTS_ROOT", str(BUNDLED))
sys.path.insert(0, str(NRD04_RUNNERS))
sys.path.insert(0, str(ING02_RUNNERS))

import run_nrd04_stage_ab as core  # noqa: E402
from ing02_common import NativeWorld, add, fields, load_kernel, pack, seal, transform, write_json  # noqa: E402
from temporal_order_apparatus_v1 import construct  # noqa: E402

MAIN_GEOMETRY = {"permutation": (0, 1, 2), "signs": (1, 1, 1)}
SEPARATED_GEOMETRY = {"permutation": (1, 0, 2), "signs": (1, -1, 1)}
CONFIGS = {
    "MAIN_S0": {"id": "MAIN_S0", "n": 23, "origin": (11, 11, 11), "permutation": (0, 1, 2), "signs": (1, 1, 1)},
    "SEPARATED_S0": {"id": "SEPARATED_S0", "n": 23, "origin": (11, 11, 11), "permutation": (0, 1, 2), "signs": (1, 1, 1)},
    "FRESH_V1": {"id": "FRESH_V1", "n": 19, "origin": (9, 9, 9), "permutation": (1, 0, 2), "signs": (1, -1, 1)},
    "FRESH_V2": {"id": "FRESH_V2", "n": 25, "origin": (12, 12, 12), "permutation": (2, 1, 0), "signs": (-1, 1, 1)},
}
WORLDS = ("W00", "W10", "W01", "W11")
HORIZONS = (32, 64)


class GeometryNotClean(RuntimeError):
    pass


def sha_array(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def apparatus(cfg, mode):
    return {**cfg, "mode": mode, "event_sreg": 0}


def compose_transform(vector, secondary, cfg):
    return transform(transform(vector, secondary["permutation"], secondary["signs"]), cfg["permutation"], cfg["signs"])


def geometry(ports, cfg, secondary):
    tf = lambda v: compose_transform(v, secondary, cfg)
    dir_a, dir_b = tf((0, 0, -1)), tf((0, 0, 1))
    target_a = add(tuple(ports["a"]), tf((0, -1, 0)), 1, cfg["n"])
    target_b = add(tuple(ports["b"]), tf((0, 1, 0)), 1, cfg["n"])
    return target_a, target_b, dir_a, dir_b


def direct_route_set(ports, cfg, secondary, event):
    target_a, target_b, dir_a, dir_b = geometry(ports, cfg, secondary)
    if event == "E1_AB":
        source_b = add(target_b, dir_b, -1, cfg["n"])
        return {target_a, source_b, target_b}
    if event == "E2_BA":
        source_b = add(target_b, dir_b, -1, cfg["n"])
        source_a = add(target_a, dir_a, -2, cfg["n"])
        middle_a = add(source_a, dir_a, 1, cfg["n"])
        return {source_b, target_b, source_a, middle_a, target_a}
    raise ValueError(event)


def initiate_e1(world, ports, cfg):
    target_a, target_b, dir_a, dir_b = geometry(ports, cfg, MAIN_GEOMETRY)
    source_b = add(target_b, dir_b, -1, cfg["n"])
    if int(world.raw_a[target_a]) or int(world.raw_a[source_b]):
        raise GeometryNotClean(f"E1 collision at {target_a} or {source_b}")
    world.inject(target_a, pack(5000, 0, dir_a, 1), 17)
    world.inject(source_b, pack(0, 0, dir_b, 1), 19)
    return [list(target_a), list(source_b)]


def initiate_e2(world, ports, cfg, secondary):
    target_a, target_b, dir_a, dir_b = geometry(ports, cfg, secondary)
    source_b = add(target_b, dir_b, -1, cfg["n"])
    source_a = add(target_a, dir_a, -2, cfg["n"])
    if int(world.raw_a[source_b]) or int(world.raw_a[source_a]):
        raise GeometryNotClean(f"E2 sources not empty: {source_b}={int(world.raw_a[source_b])}, {source_a}={int(world.raw_a[source_a])}")
    world.inject(source_b, pack(0, 0, dir_b, 1), 19)
    world.inject(source_a, pack(0, 0, dir_a, 1), 17)
    return [list(source_b), list(source_a)]


def checkpoint(world):
    return world.raw_a.copy(), world.clock_a.copy()


def states_equal(left, right):
    return bool(np.array_equal(left[0], right[0]) and np.array_equal(left[1], right[1]))


def configure_pulse(cfg):
    offset = transform((0, 0, -3), cfg["permutation"], cfg["signs"])
    direction = tuple(-int(np.sign(v)) for v in offset)
    core.PULSE_Q = tuple((cfg["origin"][i] + offset[i]) % cfg["n"] for i in range(3))
    core.PULSE_RAW = pack(8000, 0, direction, 1)


def diagnostic(kernel, state):
    c0, c3 = core.run(kernel, state, False), core.run(kernel, state, True)
    return {
        "C0": {h: c0[h] for h in HORIZONS},
        "C3": {h: c3[h] for h in HORIZONS},
        "RESPONSE": {h: core.response(c3[h], c0[h]) for h in HORIZONS},
    }


def pair_effect(left, right):
    return np.bitwise_xor(left[0], right[0]), np.bitwise_xor(left[1], right[1])


def effect_signature(left, right):
    raw_diff = left[0] != right[0]
    clock_diff = left[1] != right[1]
    lf, rf = fields(left[0]), fields(right[0])
    return {
        "raw_xor_sha256": sha_array(np.bitwise_xor(left[0], right[0])),
        "clock_xor_sha256": sha_array(np.bitwise_xor(left[1], right[1])),
        "raw_diff_mask_sha256": sha_array(raw_diff),
        "clock_diff_mask_sha256": sha_array(clock_diff),
        "raw_diff_positions": int(np.count_nonzero(raw_diff)),
        "clock_diff_positions": int(np.count_nonzero(clock_diff)),
        "field_diff_positions": {key: int(np.count_nonzero(lf[key] != rf[key])) for key in lf},
    }


def compare_effects(no_history, with_history):
    return core.compare(no_history, with_history)


def analyze_stage(stage_states, diagnostics):
    immediate_no = pair_effect(stage_states["W01"], stage_states["W00"])
    immediate_yes = pair_effect(stage_states["W11"], stage_states["W10"])
    result = {
        "immediate_effect_without_history": effect_signature(stage_states["W01"], stage_states["W00"]),
        "immediate_effect_with_history": effect_signature(stage_states["W11"], stage_states["W10"]),
        "immediate_effect_comparison": compare_effects(immediate_no, immediate_yes),
        "future_effects": {},
    }
    conditioned_by_horizon = {}
    for h in HORIZONS:
        row = {}
        differs = False
        for category in ("C0", "C3", "RESPONSE"):
            no_effect = pair_effect(diagnostics["W01"][category][h], diagnostics["W00"][category][h])
            yes_effect = pair_effect(diagnostics["W11"][category][h], diagnostics["W10"][category][h])
            comparison = compare_effects(no_effect, yes_effect)
            row[category] = {
                "without_history": effect_signature(diagnostics["W01"][category][h], diagnostics["W00"][category][h]),
                "with_history": effect_signature(diagnostics["W11"][category][h], diagnostics["W10"][category][h]),
                "effect_comparison": comparison,
            }
            differs = differs or not comparison["equal"]
        result["future_effects"][str(h)] = row
        conditioned_by_horizon[str(h)] = differs
    result["conditioned_by_horizon"] = conditioned_by_horizon
    result["history_conditioned_transformation"] = (
        not result["immediate_effect_comparison"]["equal"]
        and all(conditioned_by_horizon.values())
    )
    return result


def run_factorial(kernel, cfg, e2_secondary, require_disjoint, telemetry):
    configure_pulse(cfg)
    template, ports = construct(kernel, apparatus(cfg, "no_events"))
    worlds = {name: NativeWorld(kernel, template.raw_a, template.clock_a) for name in WORLDS}
    touched_e1 = {name: initiate_e1(worlds[name], ports, cfg) for name in ("W10", "W11")}
    expected_ab, _ = construct(kernel, apparatus(cfg, "AB"))
    for name in ("W10", "W11"):
        if not states_equal(checkpoint(worlds[name]), checkpoint(expected_ab)):
            raise RuntimeError(f"{cfg['id']} {name} E1 is not exact AB")
    for _ in range(4):
        for world in worlds.values():
            world.tick()
    pre = {name: checkpoint(world) for name, world in worlds.items()}
    if not states_equal(pre["W00"], pre["W01"]) or not states_equal(pre["W10"], pre["W11"]):
        raise RuntimeError(f"{cfg['id']} pre-E2 contamination")

    e1_routes = direct_route_set(ports, cfg, MAIN_GEOMETRY, "E1_AB")
    e2_routes = direct_route_set(ports, cfg, e2_secondary, "E2_BA")
    route_overlap = sorted(e1_routes & e2_routes)
    if require_disjoint and route_overlap:
        raise GeometryNotClean(f"Direct route overlap: {route_overlap}")
    touched_e2 = {name: initiate_e2(worlds[name], ports, cfg, e2_secondary) for name in ("W01", "W11")}
    if touched_e2["W01"] != touched_e2["W11"]:
        raise RuntimeError("E2 was not identical across histories")
    for _ in range(4):
        for world in worlds.values():
            world.tick()
    stages = {"D0": {name: checkpoint(world) for name, world in worlds.items()}}
    for _ in range(64):
        for world in worlds.values():
            world.tick()
    stages["D64"] = {name: checkpoint(world) for name, world in worlds.items()}

    analyses = {}
    for stage, stage_states in stages.items():
        diagnostics = {name: diagnostic(kernel, state) for name, state in stage_states.items()}
        analyses[stage] = analyze_stage(stage_states, diagnostics)
        for name, state in stage_states.items():
            telemetry[f"{cfg['id']}_{stage}_{name}_raw_a"] = state[0]
            telemetry[f"{cfg['id']}_{stage}_{name}_clock_a"] = state[1]
            for category in ("C0", "C3", "RESPONSE"):
                for h in HORIZONS:
                    telemetry[f"{cfg['id']}_{stage}_{name}_{category}_h{h}_raw"] = diagnostics[name][category][h][0]
                    telemetry[f"{cfg['id']}_{stage}_{name}_{category}_h{h}_clock"] = diagnostics[name][category][h][1]
    return {
        "configuration": cfg["id"],
        "pre_E2_consistency": {"W00_equals_W01": True, "W10_equals_W11": True},
        "E1_touched": touched_e1,
        "E2_touched": touched_e2,
        "E1_direct_route": [list(q) for q in sorted(e1_routes)],
        "E2_direct_route": [list(q) for q in sorted(e2_routes)],
        "direct_route_overlap": [list(q) for q in route_overlap],
        "direct_routes_disjoint": not route_overlap,
        "stages": analyses,
        "retained_conditioning": analyses["D0"]["history_conditioned_transformation"] and analyses["D64"]["history_conditioned_transformation"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--threads", type=int, default=1)
    args = parser.parse_args()
    kernel, runtime = load_kernel(args.threads)
    telemetry = {}
    executed, limitations = {}, []

    main_case = run_factorial(kernel, CONFIGS["MAIN_S0"], MAIN_GEOMETRY, False, telemetry)
    executed["MAIN_S0"] = main_case
    main_initial = main_case["stages"]["D0"]["history_conditioned_transformation"]
    main_retained = main_case["retained_conditioning"]

    if main_initial:
        try:
            executed["SEPARATED_S0"] = run_factorial(kernel, CONFIGS["SEPARATED_S0"], SEPARATED_GEOMETRY, True, telemetry)
        except GeometryNotClean as error:
            limitations.append({"configuration": "SEPARATED_S0", "reason": str(error)})

    if main_retained:
        for name in ("FRESH_V1", "FRESH_V2"):
            executed[name] = run_factorial(kernel, CONFIGS[name], MAIN_GEOMETRY, False, telemetry)

    np.savez_compressed(ROOT / "TELEMETRY" / "NRD05_FACTORIAL_STATES_AND_FUTURES.npz", **telemetry)
    separated = executed.get("SEPARATED_S0")
    direct_survives = bool(separated and separated["retained_conditioning"])
    fresh_cases = [executed.get(name) for name in ("FRESH_V1", "FRESH_V2")]
    fresh_pass = len([c for c in fresh_cases if c is not None]) == 2 and all(c["retained_conditioning"] for c in fresh_cases)

    if not main_initial:
        status = "SEQUENTIAL_CHANGE_WITHOUT_DEMONSTRATED_HISTORY_CONDITIONING"
    elif not main_retained:
        status = "TRANSIENT_HISTORY_CONDITIONING"
    elif separated is not None and not direct_survives:
        status = "LOCAL_HISTORY_PATH_INTERACTION"
    elif direct_survives and fresh_pass:
        status = "DEE_NATIVE_HISTORY_CONDITIONED_TRANSFORMATION"
    elif separated is None:
        status = "HISTORY_CONDITIONED_TRANSFORMATION_DIRECT_PATH_UNRESOLVED"
    else:
        status = "HISTORY_CONDITIONED_TRANSFORMATION_FRESH_NOT_CONFIRMED"

    result = seal({
        "experiment_id": "NRD05_HISTORY_CONDITIONED_LANDSCAPE_TRANSFORMATION",
        "status": status,
        "runtime": runtime,
        "executed_cases": executed,
        "limitations": limitations,
        "adjudication": {
            "main_history_conditioning_D0": main_initial,
            "main_history_conditioning_retained_D64": main_retained,
            "direct_path_exclusion_constructed": separated is not None,
            "conditioning_survives_disjoint_E2_route": direct_survives,
            "fresh_V1_V2_pass": fresh_pass,
            "third_experience_authorized_here": False,
            "l4": False,
        },
        "host_intervention_statement": "E1 and E2 were initiated as frozen physical carrier conditions. No RAW causal support was copied or edited. After each initiation, original worlds were only ticked/checkpointed/observed; the frozen panel was applied only to diagnostic clones.",
        "telemetry": "TELEMETRY/NRD05_FACTORIAL_STATES_AND_FUTURES.npz"
    })
    out = ROOT / "RESULTS" / "NRD05_HISTORY_CONDITIONED_TRANSFORMATION.json"
    write_json(out, result)
    print(json.dumps({
        "result": str(out),
        "status": status,
        "adjudication": result["adjudication"],
        "case_summary": {
            name: {
                "D0": case["stages"]["D0"]["history_conditioned_transformation"],
                "D64": case["stages"]["D64"]["history_conditioned_transformation"],
                "routes_disjoint": case["direct_routes_disjoint"],
            }
            for name, case in executed.items()
        },
        "limitations": limitations,
    }, indent=2))


if __name__ == "__main__":
    main()
