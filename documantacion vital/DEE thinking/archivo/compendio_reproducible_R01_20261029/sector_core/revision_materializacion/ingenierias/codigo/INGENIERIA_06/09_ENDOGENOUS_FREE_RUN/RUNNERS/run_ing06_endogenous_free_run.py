#!/usr/bin/env python3
"""Method A: intervention-free main-world continuation after validated histories."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BLOCK = HERE.parent
ROOT = BLOCK.parent
BUNDLED = ROOT / "DEPENDENCIES" / "INGENIERIA_05_HISTORY_SPECIFICITY" / "RUNNERS"
WORKSPACE = ROOT.parent / "INGENIERIA_05_HISTORY_SPECIFICITY" / "RUNNERS"
sys.path.insert(0, str(BUNDLED if BUNDLED.is_dir() else WORKSPACE))

import run_nrd06_history_specificity as nrd06  # noqa: E402

nrd05 = nrd06.nrd05
HISTORIES = {"H0": "no_events", "HA": "AB", "HB": "BA"}
OFFSETS = (0, 16, 32, 64, 128, 256, 391)
HORIZONS = (32, 64)
CATEGORIES = ("C0", "C3", "C4", "R3", "R4")


def sha_arrays(items):
    digest = hashlib.sha256()
    for item in items:
        digest.update(np.ascontiguousarray(item).tobytes())
    return digest.hexdigest()


def run_c4(kernel, state, cfg):
    world = nrd05.NativeWorld(kernel, state[0], state[1])
    for offset in ((3, 0, 0), (-3, 0, 0), (0, 3, 0), (0, -3, 0), (0, 0, 3), (0, 0, -3)):
        transformed = nrd05.transform(offset, cfg["permutation"], cfg["signs"])
        q = tuple((cfg["origin"][i] + transformed[i]) % cfg["n"] for i in range(3))
        direction = tuple(-int(np.sign(v)) for v in transformed)
        world.inject(q, nrd05.pack(8000, 0, direction, 1), 0)
    out = {}
    for tick in range(1, 65):
        world.tick()
        if tick in HORIZONS:
            out[tick] = nrd05.checkpoint(world)
    return out


def diagnostic_panel(kernel, state, cfg):
    base = nrd05.diagnostic(kernel, state)
    c4 = run_c4(kernel, state, cfg)
    return {
        "C0": base["C0"],
        "C3": base["C3"],
        "C4": c4,
        "R3": base["RESPONSE"],
        "R4": {h: nrd05.pair_effect(c4[h], base["C0"][h]) for h in HORIZONS},
    }


def fingerprint(panel):
    arrays = []
    summary = {}
    for category in CATEGORIES:
        summary[category] = {}
        for horizon in HORIZONS:
            state = panel[category][horizon]
            arrays.extend(state)
            summary[category][str(horizon)] = {
                "raw_sha256": nrd05.sha_array(state[0]),
                "clock_sha256": nrd05.sha_array(state[1]),
                "raw_nonzero": int(np.count_nonzero(state[0])),
                "clock_nonzero": int(np.count_nonzero(state[1])),
            }
    return {"sha256": sha_arrays(arrays), "summary": summary}


def temporal_effect(previous, current):
    return {
        category: {h: nrd05.pair_effect(current[category][h], previous[category][h]) for h in HORIZONS}
        for category in CATEGORIES
    }


def compare_temporal_effects(left, right):
    rows = {}
    distinct_by_horizon = {}
    for horizon in HORIZONS:
        rows[str(horizon)] = {}
        any_difference = False
        for category in CATEGORIES:
            comparison = nrd05.compare_effects(left[category][horizon], right[category][horizon])
            rows[str(horizon)][category] = comparison
            any_difference = any_difference or not comparison["equal"]
        distinct_by_horizon[str(horizon)] = any_difference
    return {"details": rows, "distinct_by_horizon": distinct_by_horizon, "distinct_all_horizons": all(distinct_by_horizon.values())}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--threads", type=int, default=1)
    args = parser.parse_args()
    kernel, runtime = nrd05.load_kernel(args.threads)
    cfg = nrd05.CONFIGS["MAIN_S0"]
    nrd05.configure_pulse(cfg)
    worlds = {
        history: nrd05.construct(kernel, nrd05.apparatus(cfg, mode))[0]
        for history, mode in HISTORIES.items()
    }
    nrd06.tick_all(worlds, 4)

    checkpoints = {}
    telemetry = {}
    elapsed = 0
    for offset in OFFSETS:
        nrd06.tick_all(worlds, offset - elapsed)
        elapsed = offset
        checkpoints[offset] = {history: nrd05.checkpoint(world) for history, world in worlds.items()}
        for history, state in checkpoints[offset].items():
            telemetry[f"T{offset}_{history}_raw_a"] = state[0]
            telemetry[f"T{offset}_{history}_clock_a"] = state[1]

    panels = {}
    fingerprints = {}
    for offset in OFFSETS:
        panels[offset] = {}
        fingerprints[offset] = {}
        for history in HISTORIES:
            panel = diagnostic_panel(kernel, checkpoints[offset][history], cfg)
            panels[offset][history] = panel
            fingerprints[offset][history] = fingerprint(panel)
            for category in CATEGORIES:
                for horizon in HORIZONS:
                    state = panel[category][horizon]
                    telemetry[f"T{offset}_{history}_{category}_h{horizon}_raw"] = state[0]
                    telemetry[f"T{offset}_{history}_{category}_h{horizon}_clock"] = state[1]

    intervals = []
    for index in range(1, len(OFFSETS)):
        before, after = OFFSETS[index - 1], OFFSETS[index]
        effects = {history: temporal_effect(panels[before][history], panels[after][history]) for history in HISTORIES}
        comparisons = {
            "H0_vs_HA": compare_temporal_effects(effects["H0"], effects["HA"]),
            "H0_vs_HB": compare_temporal_effects(effects["H0"], effects["HB"]),
            "HA_vs_HB": compare_temporal_effects(effects["HA"], effects["HB"]),
        }
        changed = {history: fingerprints[before][history]["sha256"] != fingerprints[after][history]["sha256"] for history in HISTORIES}
        persistence_observable = index + 2 < len(OFFSETS)
        future_indices = range(index, index + 3) if persistence_observable else range(index, len(OFFSETS))
        persists = {
            history: all(
                fingerprints[OFFSETS[j]][history]["sha256"] != fingerprints[before][history]["sha256"]
                for j in future_indices
            )
            for history in HISTORIES
        }
        history_conditioned = all(value["distinct_all_horizons"] for value in comparisons.values())
        intervals.append({
            "before_offset": before,
            "after_offset": after,
            "fingerprint_changed": changed,
            "persists_beyond_before": persists,
            "history_conditioned_temporal_effect": history_conditioned,
            "comparisons": comparisons,
            "persistence_observable": persistence_observable,
            "candidate": persistence_observable and all(changed.values()) and all(persists.values()) and history_conditioned,
            "public_state_change": {
                history: nrd05.effect_signature(checkpoints[after][history], checkpoints[before][history])
                for history in HISTORIES
            },
        })

    candidates = [row for row in intervals if row["candidate"]]
    every_interval_changes = all(all(row["fingerprint_changed"].values()) for row in intervals)
    every_interval_conditioned = all(row["history_conditioned_temporal_effect"] for row in intervals)
    if candidates and every_interval_changes and every_interval_conditioned:
        status = "HISTORY_CONDITIONED_CONTINUOUS_REACHABILITY_EVOLUTION"
    elif candidates:
        status = "DEE_NATIVE_ENDOGENOUS_REACHABILITY_TRANSITION_CANDIDATE"
    elif every_interval_changes:
        status = "GENERIC_CONTINUOUS_REACHABILITY_DRIFT"
    else:
        status = "NO_ENDOGENOUS_REACHABILITY_CHANGE_OBSERVED"

    np.savez_compressed(BLOCK / "TELEMETRY" / "ING06_ENDOGENOUS_FREE_RUN.npz", **telemetry)
    result = nrd05.seal({
        "experiment_id": "ING06_ENDOGENOUS_FREE_RUN",
        "status": status,
        "runtime": runtime,
        "host_stop_tick": 4,
        "main_world_interventions_after_host_stop": 0,
        "checkpoint_offsets": OFFSETS,
        "fingerprints": {str(offset): value for offset, value in fingerprints.items()},
        "intervals": intervals,
        "candidate_intervals": [{"before": row["before_offset"], "after": row["after_offset"]} for row in candidates],
        "adjudication": {
            "reachability_changes_after_host_stop": bool(candidates),
            "history_conditioned": bool(candidates and every_interval_conditioned),
            "discrete_transition_demonstrated": status == "DEE_NATIVE_ENDOGENOUS_REACHABILITY_TRANSITION_CANDIDATE",
            "continuous_evolution_observed": status == "HISTORY_CONDITIONED_CONTINUOUS_REACHABILITY_EVOLUTION",
            "new_unpreloaded_contingency_demonstrated": False,
            "formal_RW3": False,
            "L4": False
        },
        "telemetry": "TELEMETRY/ING06_ENDOGENOUS_FREE_RUN.npz"
    })
    nrd05.write_json(BLOCK / "RESULTS" / "ING06_ENDOGENOUS_FREE_RUN.json", result)
    print(json.dumps({
        "status": status,
        "candidate_intervals": result["candidate_intervals"],
        "all_intervals_changed": every_interval_changes,
        "all_intervals_history_conditioned": every_interval_conditioned,
        "new_unpreloaded_contingency": False,
    }, indent=2))


if __name__ == "__main__":
    main()
