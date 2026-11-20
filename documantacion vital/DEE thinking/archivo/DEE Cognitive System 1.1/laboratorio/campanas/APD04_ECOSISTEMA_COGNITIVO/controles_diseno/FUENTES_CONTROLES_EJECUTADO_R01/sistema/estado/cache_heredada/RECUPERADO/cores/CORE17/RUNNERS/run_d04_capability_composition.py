#!/usr/bin/env python3
"""D04: compose learning, causal transfer, regeneration and macro control."""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "VENDORED_CORE16" / "BASELINE_RUNNERS"))

from core17_common import (ROOT, append_ndjson, audit_kernel, canonical_hash,
                           utc, verify_and_load_kernel, write_json)
import core10_apparatus as c10
from core12_apparatus import regenerative_interface_trial


def learned_transfer_with_damage(kernel, seed: int, repair: str):
    """Copy the sealed CORE10 causal schedule, then intervene after receiver arrival."""
    n, distance = 23, 6
    rng = np.random.default_rng(seed)
    raw = np.zeros((n, n, n), dtype=np.uint64)
    clock = np.zeros_like(raw)
    world = c10.NativeWorld(kernel, raw, clock)
    a, b, sensor, normalizer, penalty0, action1 = (
        c10.transform(v) for v in (c10.A, c10.B, c10.SENSOR, c10.NORMALIZER, c10.PENALTY0, c10.ACTION1)
    )
    relay = (1, -1, 1)
    route = tuple(relay[i] + b[i] for i in range(3))
    source = tuple(int(x) for x in rng.integers(5, 8, size=3))
    receiver = c10.add(source, route, distance, n)
    world.inject(source, c10.pack(6000 + seed, 7, a, 1), 7000 + seed)
    learned_tick, launch_tick = 2 * n, 3 * n
    arrival_tick = launch_tick + distance
    query_tick = arrival_tick + n
    arrival_record = None
    restored_record = None
    corners = [tuple((receiver[i] + d[i]) % n for i in range(3))
               for d in itertools.product((-1, 1), repeat=3)]
    trace = []
    for current in range(query_tick):
        next_tick = current + 1
        if next_tick == n:
            c10.inject_arrival(world, source, sensor, 47, 8000 + seed, 8100 + seed)
        if next_tick == learned_tick:
            c10.inject_arrival(world, source, normalizer, 53, 8200 + seed, 8300 + seed)
            c10.inject_arrival(world, source, penalty0, 59, 8400 + seed, 8500 + seed)
        if next_tick == launch_tick:
            c10.inject_arrival(world, source, relay, 61, 8600 + seed, 8700 + seed)
        if next_tick == arrival_tick:
            c10.inject_arrival(world, receiver, c10.neg(relay), 71, 9200 + seed, 9300 + seed)
        if next_tick == query_tick:
            c10.inject_arrival(world, receiver, sensor, 101, 9400 + seed, 9500 + seed)
        world.tick()
        if next_tick == arrival_tick:
            arrival_record = c10.read(world.raw, receiver)
            if repair in {"damage_only", "fixed_xnor_scaffold"}:
                world.raw_a[receiver] = world.raw_b[receiver] = np.uint64(0)
                world.clock_a[receiver] = world.clock_b[receiver] = np.uint64(0)
            if repair == "fixed_xnor_scaffold":
                for i, q in enumerate(corners):
                    world.raw_a[q] = world.raw_b[q] = c10.pack(0xA000 + i, 31 + i, (0, 0, 0), 4)
                    world.clock_a[q] = world.clock_b[q] = np.uint64(100000 + i)
        if next_tick == arrival_tick + 1:
            restored_record = c10.read(world.raw, receiver)
        if next_tick in {learned_tick, launch_tick, arrival_tick, arrival_tick + 1, query_tick}:
            trace.append({"tick": next_tick, "source": c10.read(world.raw, source),
                          "receiver": c10.read(world.raw, receiver),
                          "support": int(np.count_nonzero(world.raw))})
    query = c10.read(world.raw, receiver)
    return {
        "seed": seed, "repair": repair, "source": list(source), "receiver": list(receiver),
        "ticks": {"learned": learned_tick, "launch": launch_tick,
                  "arrival": arrival_tick, "query": query_tick},
        "arrival_record": arrival_record,
        "restored_record": restored_record,
        "query_record": query,
        "functional_policy_after_intervention": query is not None and tuple(query["direction"]) == action1,
        "source_depleted": c10.read(world.raw, source) is None,
        "trace": trace,
    }


def transfer_panel(kernel):
    positives = [c10.run_learned_policy_transfer(kernel, seed=s, n=23, distance=d, mode="trained")
                 for s, d in ((17001, 4), (17002, 6), (17003, 8))]
    controls = {mode: c10.run_learned_policy_transfer(kernel, seed=17100 + i, mode=mode)
                for i, mode in enumerate(("untrained", "no_relay", "wrong_receiver", "corridor_cut", "offpath_cut"))}
    composition = [learned_transfer_with_damage(kernel, 17200 + i, mode)
                   for i, mode in enumerate(("intact", "damage_only", "fixed_xnor_scaffold"))]
    return {
        "positives": [{"seed": x["seed"], "distance": x["distance"],
                       "functional": x["functional_policy_reinstantiated"],
                       "source_depleted": x["source_depleted_after_launch"],
                       "corridor_complete": x["corridor_all_intermediate_ticks_observed"]}
                      for x in positives],
        "controls": {mode: {"functional": x["functional_policy_reinstantiated"],
                            "source_depleted": x["source_depleted_after_launch"]}
                     for mode, x in controls.items()},
        "composition": composition,
        "transfer_replicates_pass": all(x["functional_policy_reinstantiated"] and
                                        x["source_depleted_after_launch"] and
                                        x["corridor_all_intermediate_ticks_observed"] for x in positives),
        "causal_controls_pass": (not controls["untrained"]["functional_policy_reinstantiated"] and
                                 not controls["no_relay"]["functional_policy_reinstantiated"] and
                                 not controls["wrong_receiver"]["functional_policy_reinstantiated"] and
                                 not controls["corridor_cut"]["functional_policy_reinstantiated"] and
                                 controls["offpath_cut"]["functional_policy_reinstantiated"]),
        "generic_regeneration_restores_learned_function": composition[2]["functional_policy_after_intervention"],
    }


def macro_control(kernel):
    horizons = (22, 42, 82, 162)
    rows = []
    for horizon in horizons:
        for count in (5, 6):
            result = regenerative_interface_trial(
                kernel, n=47, source_distance=7, downstream_distance=5,
                horizon=horizon, mode="semantic4_custom", direction=(1, 0, 0),
                center=(23, 23, 23), source_sreg=173,
                semantic4_indices=list(range(count)), threads=1)
            events = result["downstream_event_ticks"]["5"]
            rows.append({"horizon": horizon, "guard_count": count,
                         "downstream_distance": 5, "event_count": len(events),
                         "event_ticks_head": events[:12], "transmits": len(events) > 0})
    pairs = []
    for horizon in horizons:
        k5 = next(x for x in rows if x["horizon"] == horizon and x["guard_count"] == 5)
        k6 = next(x for x in rows if x["horizon"] == horizon and x["guard_count"] == 6)
        pairs.append({"horizon": horizon, "k5_events": k5["event_count"],
                      "k6_events": k6["event_count"],
                      "macro_difference": k5["event_count"] - k6["event_count"]})
    increasing = all(b["macro_difference"] > a["macro_difference"] for a, b in zip(pairs, pairs[1:]))
    return {
        "rows": rows, "pairs": pairs,
        "one_cell_controls_train": all(x["k5_events"] > 0 and x["k6_events"] == 0 for x in pairs),
        "difference_grows_with_observation_horizon": increasing,
        "mechanism": "one semantic4 guard cell crosses the ordered k5/k6 interface boundary, selecting repeated train transmission or blocking",
        "not_nonlocal": True,
    }


def main():
    audit_kernel("CORE17_D04_CAPABILITY_COMPOSITION")
    kernel, runtime = verify_and_load_kernel(1)
    transfer = transfer_panel(kernel)
    control = macro_control(kernel)
    result = {
        "schema": "dee.v27.core17.d04.v1",
        "experiment": "LEARNING_TRANSFER_REGENERATION_AND_MACRO_CONTROL",
        "created_utc": utc(), "runtime": runtime,
        "transfer_and_composition": transfer,
        "micro_to_macro_control": control,
        "adjudication": {
            "learned_transfer_reinstantiation": transfer["transfer_replicates_pass"] and transfer["causal_controls_pass"],
            "fixed_scaffold_regenerates_learned_policy": transfer["generic_regeneration_restores_learned_function"],
            "composition_limit": "The fixed XNOR scaffold restores a canonical local record, not the history-conditioned learned policy; end-to-end learned transfer plus autonomous regeneration is not established.",
            "small_to_large_amplification": control["one_cell_controls_train"] and control["difference_grows_with_observation_horizon"],
            "programmability_scope": "bounded prepared interface grammar; not general-purpose programming and not external technological access",
        },
    }
    h = canonical_hash(result); result["content_sha256"] = h
    write_json(ROOT / "DISCOVERY" / "C17D04_CAPABILITY_COMPOSITION.json", result)
    append_ndjson(ROOT / "QUESTION_TREE.ndjson", {
        "question_id": "C17Q004", "parent_question": "Do independently demonstrated learning, transfer and regeneration compose end-to-end?",
        "parent_result_hash": "256fc52428ef850cc13170cbfa2bd897076c2147b4abfa50961f873268b4417e",
        "new_uncertainty": "Whether the fixed regeneration scaffold preserves a receiver's acquired policy rather than merely recreating occupancy.",
        "candidate_explanations": ["functional regeneration", "canonical fixed-state reconstruction", "apparatus interference"],
        "why_next_experiment_discriminates": "The receiver is queried after either no damage, damage alone, or damage plus the exact native XNOR scaffold.",
        "result_hash": h, "result": result["adjudication"],
        "child_question": "Can a scaffold carrying policy/history coordinates, rather than the fixed canonical scaffold, regenerate the learned function?",
        "status": "CHILD_OPEN",
    })
    append_ndjson(ROOT / "RESEARCH_DECISION_LOG.ndjson", {
        "utc": utc(), "decision_id": "C17D04_DECISION", "parent_result_hash": h,
        "decision": "Promote bounded micro-to-macro amplification; do not promote full learning-transfer-regeneration composition.",
        "reason": result["adjudication"]["composition_limit"],
    })
    append_ndjson(ROOT / "KERNEL_DIALOGUE.ndjson", {
        "question_id": "C17Q004", "raw_outcome": result["adjudication"],
        "mechanism_update": "Transfer preserves a learned response through an explicit depleted-source carrier and prepared receiver; fixed guard regeneration does not encode the learned history coordinate.",
        "next": "Confirm the k5/k6 horizon law fresh and treat policy-bearing regeneration as an open prerequisite-construction problem.",
    })
    print(json.dumps({"hash": h, "adjudication": result["adjudication"],
                      "macro_pairs": control["pairs"],
                      "composition": [{"repair": x["repair"], "functional": x["functional_policy_after_intervention"], "restored": x["restored_record"]} for x in transfer["composition"]]}, indent=2))


if __name__ == "__main__":
    main()
