#!/usr/bin/env python3
"""RAW-only fresh replication of post-HOST_STOP history-conditioned dynamics."""
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
ENGINEERING = ROOT.parent
NRD06 = ENGINEERING / "INGENIERIA_05_HISTORY_SPECIFICITY" / "RUNNERS"
NRD05 = ENGINEERING / "INGENIERIA_05_HISTORY_CONDITIONED_TRANSFORMATION" / "RUNNERS"
sys.path[:0] = [str(NRD06), str(NRD05)]
import run_nrd05_history_conditioned_transformation as nrd05  # noqa: E402
import run_nrd06_history_specificity as nrd06  # noqa: E402

CONFIGS = ("MAIN_S0", "FRESH_V1", "FRESH_V2")
HISTORIES = {"H0": "no_events", "HA": "AB", "HB": "BA"}
OFFSETS = (0, 16, 32, 64, 128, 256, 391)
HORIZONS = (32, 64)
CATEGORIES = ("C0", "C3", "C4", "R3", "R4")


def sha_raw(raw):
    return hashlib.sha256(np.ascontiguousarray(raw).tobytes()).hexdigest()


def run_c4(kernel, state, cfg):
    raw, clock = state
    world = nrd05.NativeWorld(kernel, raw, clock)
    origin = tuple(cfg["origin"])
    axes = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
    for direction in axes:
        q = tuple((origin[i] - 3 * direction[i]) % cfg["n"] for i in range(3))
        world.inject(q, nrd05.pack(8000, 0, direction, 1), 0)
    out = {}
    for tick in range(1, 65):
        world.tick()
        if tick in HORIZONS:
            out[tick] = nrd05.checkpoint(world)
    return out


def panel(kernel, state, cfg):
    base = nrd05.diagnostic(kernel, state)
    c4 = run_c4(kernel, state, cfg)
    return {
        "C0": base["C0"], "C3": base["C3"], "C4": c4,
        "R3": {h: nrd05.pair_effect(base["C3"][h], base["C0"][h]) for h in HORIZONS},
        "R4": {h: nrd05.pair_effect(c4[h], base["C0"][h]) for h in HORIZONS},
    }


def panel_raw_fingerprint(value):
    rows = [value[c][h][0] for c in CATEGORIES for h in HORIZONS]
    digest = hashlib.sha256()
    for raw in rows:
        digest.update(np.ascontiguousarray(raw).tobytes())
    return digest.hexdigest()


def temporal_raw_effect(previous, current):
    return {c: {h: np.bitwise_xor(current[c][h][0], previous[c][h][0]) for h in HORIZONS} for c in CATEGORIES}


def effects_distinct(left, right):
    by_horizon = {
        str(h): any(not np.array_equal(left[c][h], right[c][h]) for c in CATEGORIES)
        for h in HORIZONS
    }
    return {"distinct_by_horizon": by_horizon, "distinct_all_horizons": all(by_horizon.values())}


def run_config(kernel, cfg, telemetry):
    nrd05.configure_pulse(cfg)
    worlds = {h: nrd05.construct(kernel, nrd05.apparatus(cfg, mode))[0] for h, mode in HISTORIES.items()}
    nrd06.tick_all(worlds, 4)
    checkpoints, panels, fingerprints = {}, {}, {}
    elapsed = 0
    for offset in OFFSETS:
        nrd06.tick_all(worlds, offset - elapsed)
        elapsed = offset
        checkpoints[offset] = {h: nrd05.checkpoint(w) for h, w in worlds.items()}
        panels[offset], fingerprints[offset] = {}, {}
        for history, state in checkpoints[offset].items():
            telemetry[f"{cfg['id']}_T{offset}_{history}_raw_a"] = state[0]
            telemetry[f"{cfg['id']}_T{offset}_{history}_clock_a_FORENSIC"] = state[1]
            panels[offset][history] = panel(kernel, state, cfg)
            fingerprints[offset][history] = panel_raw_fingerprint(panels[offset][history])
            for category in CATEGORIES:
                for horizon in HORIZONS:
                    telemetry[f"{cfg['id']}_T{offset}_{history}_{category}_h{horizon}_raw"] = panels[offset][history][category][horizon][0]

    intervals = []
    for index in range(1, len(OFFSETS)):
        before, after = OFFSETS[index - 1], OFFSETS[index]
        effects = {h: temporal_raw_effect(panels[before][h], panels[after][h]) for h in HISTORIES}
        future_distinct = effects_distinct(effects["HA"], effects["HB"])
        main_raw_changed = {
            h: not np.array_equal(checkpoints[before][h][0], checkpoints[after][h][0]) for h in HISTORIES
        }
        ha_hb_raw_distinct = not np.array_equal(
            np.bitwise_xor(checkpoints[after]["HA"][0], checkpoints[before]["HA"][0]),
            np.bitwise_xor(checkpoints[after]["HB"][0], checkpoints[before]["HB"][0]),
        )
        persistence_observable = index + 2 < len(OFFSETS)
        persists = all(
            fingerprints[OFFSETS[j]][history] != fingerprints[before][history]
            for history in ("HA", "HB")
            for j in (range(index, index + 3) if persistence_observable else range(index, len(OFFSETS)))
        )
        candidate = persistence_observable and ha_hb_raw_distinct and future_distinct["distinct_all_horizons"] and persists
        intervals.append({
            "before": before, "after": after,
            "main_raw_changed": main_raw_changed,
            "ha_hb_raw_temporal_effect_distinct": ha_hb_raw_distinct,
            "ha_hb_future_raw_temporal_effect": future_distinct,
            "persistence_observable": persistence_observable,
            "persists": persists,
            "candidate": candidate,
            "raw_diff_positions": {
                h: int(np.count_nonzero(checkpoints[before][h][0] != checkpoints[after][h][0])) for h in HISTORIES
            },
        })
    candidates = [r for r in intervals if r["candidate"]]
    return {
        "configuration": cfg["id"],
        "candidate_intervals": [{"before": r["before"], "after": r["after"]} for r in candidates],
        "pass": bool(candidates),
        "intervals": intervals,
        "primary_gate_used_clock_a": False,
        "main_world_interventions_after_host_stop": 0,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--threads", type=int, default=1)
    args = parser.parse_args()
    kernel, runtime = nrd05.load_kernel(args.threads)
    telemetry, cases = {}, {}
    for name in CONFIGS:
        cases[name] = run_config(kernel, nrd05.CONFIGS[name], telemetry)
    replicated = all(cases[name]["pass"] for name in CONFIGS)
    status = "DEE_NATIVE_HISTORY_CONDITIONED_POST_HOST_RAW_DYNAMICS" if replicated else "RAW_ONLY_FRESH_REPLICATION_NOT_CONFIRMED"
    np.savez_compressed(BLOCK / "TELEMETRY" / "ING06_RAW_ONLY_FRESH.npz", **telemetry)
    result = nrd05.seal({
        "experiment_id": "ING06_RAW_ONLY_FRESH_POST_HOST",
        "status": status,
        "runtime": runtime,
        "host_stop_tick": 4,
        "checkpoint_offsets": OFFSETS,
        "primary_gate_excludes_clock_a": True,
        "cases": cases,
        "fresh_replication": replicated,
        "new_unpreloaded_contingency_demonstrated": False,
        "formal_RW3": False,
        "L4": False,
        "telemetry": "TELEMETRY/ING06_RAW_ONLY_FRESH.npz",
    })
    nrd05.write_json(BLOCK / "RESULTS" / "ING06_RAW_ONLY_FRESH.json", result)
    print(json.dumps({"status": status, "passes": {k: v["pass"] for k, v in cases.items()}, "candidate_intervals": {k: v["candidate_intervals"] for k, v in cases.items()}, "clock_used_in_gate": False}, indent=2))


if __name__ == "__main__":
    main()
