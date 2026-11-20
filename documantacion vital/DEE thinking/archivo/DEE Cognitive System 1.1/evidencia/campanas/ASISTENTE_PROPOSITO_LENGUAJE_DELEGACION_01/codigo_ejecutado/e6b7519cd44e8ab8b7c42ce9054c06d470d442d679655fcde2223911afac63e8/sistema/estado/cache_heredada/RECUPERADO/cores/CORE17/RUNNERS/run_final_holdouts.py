#!/usr/bin/env python3
"""Frozen CORE17 final evaluator. Challenges must be created after source freeze."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "VENDORED_CORE16" / "RUNNERS_NEW"))
sys.path.insert(0, str(HERE / "VENDORED_CORE16" / "BASELINE_RUNNERS"))

from core17_common import (NativeWorld, ROOT, audit_kernel, canonical_hash, pack,
                           read_json, sha256_array, sha256_file, utc,
                           verify_and_load_kernel, write_json)
from core10_apparatus import run_learned_policy_transfer
from core12_apparatus import regenerative_interface_trial, source_train_trial
from occupancy_operator import predict_tick
from run_d03_probability_quantum import probability_pushforward
from run_d05_emergent_physics import random_operator_world
from run_s01_model_selection import gate_case


def verify_freeze(lock):
    observed = {}
    for rel, expected in lock["source_hashes"].items():
        path = ROOT / rel
        observed[rel] = sha256_file(path)
        if observed[rel] != expected:
            raise RuntimeError(f"frozen source changed: {rel}")
    return observed


def clock_panel(kernel, specs):
    rows = []
    for spec in specs:
        rng = np.random.default_rng(spec["case_seed"])
        row = gate_case(kernel, rng, spec["n"], spec["modules"], spec["delay"],
                        off_gate=spec["mode"] == "off_gate", equal=spec["mode"] == "equal_clock")
        row["challenge_id"] = spec["challenge_id"]
        rows.append(row)
    return {"rows": rows, "pass": all(x["pass"] for x in rows)}


def probability_panel(kernel, specs):
    rows = []
    for spec in specs:
        result = probability_pushforward(kernel, spec["k"])
        error = max(v["max_abs_error"] for v in result["weighted_measures"].values())
        rows.append({"challenge_id": spec["challenge_id"], "k": spec["k"],
                     "microstates": result["microstates_exhausted"],
                     "uniform_exact": result["uniform_exact"],
                     "micro_to_macro_exact": result["micro_to_macro_exact"],
                     "weighted_max_error": error,
                     "pass": result["uniform_exact"] and result["micro_to_macro_exact"] and error < 1e-12})
    return {"rows": rows, "pass": all(x["pass"] for x in rows)}


def macro_panel(kernel, specs):
    rows = []
    for spec in specs:
        row = {k: spec[k] for k in ("challenge_id", "n", "horizon", "direction", "center")}
        for count in (5, 6):
            result = regenerative_interface_trial(
                kernel, n=spec["n"], source_distance=7, downstream_distance=5,
                horizon=spec["horizon"], mode="semantic4_custom",
                direction=tuple(spec["direction"]), center=tuple(spec["center"]),
                source_sreg=spec["source_sreg"], semantic4_indices=list(range(count)), threads=1)
            row[f"k{count}_ticks"] = result["downstream_event_ticks"]["5"]
            row[f"k{count}_events"] = len(row[f"k{count}_ticks"])
        row["expected_k5"] = max(0, (spec["horizon"] - 10) // 2)
        row["pass"] = row["k5_events"] == row["expected_k5"] and row["k6_events"] == 0
        rows.append(row)
    return {"rows": rows, "pass": all(x["pass"] for x in rows)}


def operator_panel(kernel, specs):
    cases = []
    for spec in specs:
        rng = np.random.default_rng(spec["case_seed"])
        raw, clock = random_operator_world(rng, spec["n"], spec["density"], spec["include_fusion"])
        world = NativeWorld(kernel, raw, clock, 1)
        model_raw, model_clock = raw.copy(), clock.copy()
        steps = []
        for tick in range(1, spec["ticks"] + 1):
            model_raw, model_clock, _, _ = predict_tick(model_raw, model_clock)
            world.tick()
            steps.append({"tick": tick,
                          "raw_mismatches": int(np.count_nonzero(model_raw != world.raw)),
                          "clock_mismatches": int(np.count_nonzero(model_clock != world.clock)),
                          "native_raw_sha256": sha256_array(world.raw),
                          "model_raw_sha256": sha256_array(model_raw)})
        cases.append({"challenge_id": spec["challenge_id"], "seed": spec["case_seed"],
                      "n": spec["n"], "ticks": steps,
                      "pass": all(x["raw_mismatches"] == 0 and x["clock_mismatches"] == 0 for x in steps)})
    return {"rows": cases, "total_ticks": sum(len(x["ticks"]) for x in cases),
            "total_mismatches": sum(s["raw_mismatches"] + s["clock_mismatches"] for x in cases for s in x["ticks"]),
            "pass": all(x["pass"] for x in cases)}


def level_panel(kernel, specs):
    rows = []
    for spec in specs:
        kwargs = {"seed": spec["case_seed"], "n": spec["n"], "distance": spec["distance"],
                  "permutation": tuple(spec["permutation"]), "signs": tuple(spec["signs"])}
        prepared = run_learned_policy_transfer(kernel, mode="trained", **kwargs)
        wrong = run_learned_policy_transfer(kernel, mode="wrong_receiver", **kwargs)
        before_a = [x for x in prepared["corridor_trace"] if x["distance_from_source"] < prepared["distance"]]
        before_b = [x for x in wrong["corridor_trace"] if x["distance_from_source"] < wrong["distance"]]
        d = tuple(spec["direction"]); common = {"kernel": kernel, "n": 39, "source": (19, 19, 19),
                                                "direction": d, "sreg": spec["sreg"], "mode": "baseline", "threads": 1}
        phase_a = source_train_trial(horizon=23, detector_distance=7, **common)
        phase_b = source_train_trial(horizon=24, detector_distance=8, **common)
        row = {"challenge_id": spec["challenge_id"],
               "same_routed_event_before_receiver": before_a == before_b,
               "prepared_functional": prepared["functional_policy_reinstantiated"],
               "wrong_receiver_functional": wrong["functional_policy_reinstantiated"],
               "phase_a": phase_a["arrival_ticks"], "phase_b": phase_b["arrival_ticks"],
               "equal_integrated_count": len(phase_a["arrival_ticks"]) == len(phase_b["arrival_ticks"]),
               "distinct_timing": phase_a["arrival_ticks"] != phase_b["arrival_ticks"]}
        row["pass"] = (row["same_routed_event_before_receiver"] and row["prepared_functional"] and
                       not row["wrong_receiver_functional"] and row["equal_integrated_count"] and row["distinct_timing"])
        rows.append(row)
    return {"rows": rows, "pass": all(x["pass"] for x in rows)}


def canaries(kernel):
    n = 7; target = (3, 3, 3); source = (2, 3, 3)
    raw = np.zeros((n, n, n), dtype=np.uint64)
    raw[target] = pack(77, 5, (0, 0, 0), 1); raw[source] = pack(99, 11, (1, 0, 0), 1)
    world = NativeWorld(kernel, raw, threads=1); world.tick()
    incoming_only = int(pack(1, 11, (1, 0, 0), 1))
    transfer_cut = run_learned_policy_transfer(kernel, seed=179991, mode="corridor_cut")
    transfer_sham = run_learned_policy_transfer(kernel, seed=179991, mode="offpath_cut")
    return {
        "incumbent_branch": {"observed": int(world.raw[target]), "naive_incoming": incoming_only,
                             "pass": int(world.raw[target]) != incoming_only},
        "transfer_path": {"corridor_cut_functional": transfer_cut["functional_policy_reinstantiated"],
                          "offpath_cut_functional": transfer_sham["functional_policy_reinstantiated"],
                          "pass": (not transfer_cut["functional_policy_reinstantiated"] and transfer_sham["functional_policy_reinstantiated"])},
    }


def main():
    audit_kernel("CORE17_FINAL_HOLDOUT")
    lock = read_json(ROOT / "HOLDOUT_LOCKS" / "CORE17_FINAL_LOCK.json")
    challenges = read_json(ROOT / "FRESH_CHALLENGES" / "CORE17_FINAL_CHALLENGES.json")
    observed_sources = verify_freeze(lock)
    if challenges["lock_sha256"] != lock["lock_sha256"]:
        raise RuntimeError("challenge/lock mismatch")
    kernel, runtime = verify_and_load_kernel(1)
    panels = {
        "clock": clock_panel(kernel, challenges["clock_cases"]),
        "probability": probability_panel(kernel, challenges["probability_cases"]),
        "macro_control": macro_panel(kernel, challenges["macro_cases"]),
        "operator": operator_panel(kernel, challenges["operator_cases"]),
        "level_separation": level_panel(kernel, challenges["level_cases"]),
    }
    cs = canaries(kernel)
    overall = all(x["pass"] for x in panels.values()) and all(x["pass"] for x in cs.values())
    result = {"schema": "dee.v27.core17.final_holdout.v1", "executed_utc": utc(),
              "lock_sha256": lock["lock_sha256"], "challenge_sha256": challenges["challenge_sha256"],
              "runtime": runtime, "observed_source_hashes": observed_sources,
              "panels": panels, "canaries": cs,
              "summary": {"fresh_worlds": sum(len(x["rows"]) for x in panels.values()),
                          "panel_passes": {k: v["pass"] for k, v in panels.items()},
                          "canary_passes": {k: v["pass"] for k, v in cs.items()},
                          "operator_ticks": panels["operator"]["total_ticks"],
                          "operator_mismatches": panels["operator"]["total_mismatches"],
                          "overall_pass": overall}}
    result["content_sha256"] = canonical_hash(result)
    write_json(ROOT / "FINAL_HOLDOUTS" / "CORE17_FINAL_RESULTS.json", result)
    write_json(ROOT / "CANARIES" / "CORE17_CANARY_RESULTS.json", cs)
    print(json.dumps({"summary": result["summary"], "content_sha256": result["content_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
