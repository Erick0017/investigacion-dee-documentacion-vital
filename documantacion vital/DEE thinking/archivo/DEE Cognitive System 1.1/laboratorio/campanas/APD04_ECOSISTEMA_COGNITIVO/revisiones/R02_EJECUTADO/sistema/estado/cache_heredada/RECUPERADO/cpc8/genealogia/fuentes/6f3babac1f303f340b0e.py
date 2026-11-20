#!/usr/bin/env python3
"""C6D04: bounded discovery of transfer, extinction, reversal and reacquisition.

All post-initial experiences enter through empty carrier ports. No learner cell is
edited to contain a desired response. This is discovery, not confirmation.
"""
from __future__ import annotations

import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from native_core import NativeWorld, atomic_json, canonical_hash, fields, pack, verify_and_load_kernel


WORK = Path(__file__).resolve().parents[1]
OUT = WORK / "RESULTS" / "C6D04_reversal_extinction_transfer.json"

CUE = (1, 0, 0)
TEACHER_B = (-1, 1, 0)
MEMORY_B = (0, 1, 0)
TEACHER_C = (-1, 0, 1)
MEMORY_C = (0, 0, 1)
ERASER_B = (1, -1, 0)
EXTINCTED_ROUTE = (1, 1, 0)


def add(q, d, k, n):
    return tuple((q[i] + k * d[i]) % n for i in range(3))


def signsum(*vectors):
    return tuple(int(np.sign(sum(v[i] for v in vectors))) for i in range(3))


def decode(raw, q):
    if int(raw[q]) == 0:
        return None
    f = fields(raw)
    return {
        "state": int(f["state"][q]),
        "sreg": int(f["sreg"][q]),
        "d": [int(f[x][q]) for x in ("dx", "dy", "dz")],
        "semantic": int(f["semantic"][q]),
    }


def place_initial_arrival(raw, clock, target, tick, direction, sreg, state, clk, n):
    start = add(target, direction, -tick, n)
    if int(raw[start]) != 0:
        raise RuntimeError(f"initial overlap at {start}")
    raw[start] = pack(state, sreg, direction, 1)
    clock[start] = np.uint64(clk)
    return start


def schedule_arrival(schedule, target, event_tick, path, direction, sreg, state, clk, n, label):
    inject_tick = event_tick - path
    port = add(target, direction, -path, n)
    schedule[inject_tick].append({
        "label": label, "port": port, "direction": direction, "sreg": sreg,
        "state": state, "clock": clk, "event_tick": event_tick,
    })


def inject(world, spec):
    q = spec["port"]
    if int(world.raw[q]) != 0:
        raise RuntimeError(f"occupied ordinary input port {q} for {spec['label']}")
    value = pack(spec["state"], spec["sreg"], spec["direction"], 1)
    world.raw_a[q] = value
    world.raw_b[q] = value
    world.clock_a[q] = np.uint64(spec["clock"])
    world.clock_b[q] = np.uint64(spec["clock"])


def initial_world(kernel, n, junction, train_tick, mode):
    raw = np.zeros((n, n, n), dtype=np.uint64)
    clock = np.zeros_like(raw)
    if mode not in {"untrained"}:
        train_junction = add(junction, (0, 0, 5), 1, n) if mode == "matched_exposure" else junction
        teacher = TEACHER_C if mode == "label_shuffled" else TEACHER_B
        teacher_tick = train_tick + 1 if mode == "history_shuffled" else train_tick
        place_initial_arrival(raw, clock, train_junction, train_tick, CUE, 5, 301, 3001, n)
        place_initial_arrival(raw, clock, train_junction, teacher_tick, teacher, 7, 303, 3003, n)
    return NativeWorld(kernel, raw, clock, threads=1)


def run_transfer(kernel, query_direction, mode):
    n, junction, train_tick, query_tick, path = 41, (20, 20, 20), 4, 16, 4
    world = initial_world(kernel, n, junction, train_tick, mode)
    target = add(junction, MEMORY_B, query_tick-train_tick, n)
    schedule = defaultdict(list)
    q_sreg = 101 + sum((i+2)*v for i, v in enumerate(query_direction))
    schedule_arrival(schedule, target, query_tick, path, query_direction, q_sreg, 311, 3011, n, "unseen_query")
    port_empty = True
    record = None
    for tick in range(query_tick+1):
        for spec in schedule[tick]:
            port_empty = port_empty and int(world.raw[spec["port"]]) == 0
            inject(world, spec)
        if tick == query_tick:
            record = decode(world.raw, target)
        if tick < query_tick:
            world.tick()
    expected_d = list(signsum(MEMORY_B, query_direction))
    expected_s = min(12 + q_sreg, 19664)
    neutral_d = list(query_direction)
    trained_exact = record is not None and record["d"] == expected_d and record["sreg"] == expected_s
    neutral_exact = record is not None and record["d"] == neutral_d and record["sreg"] == q_sreg
    return {
        "mode": mode, "query_direction": list(query_direction), "query_sreg": q_sreg,
        "expected_trained_direction": expected_d, "expected_trained_sreg": expected_s,
        "target": list(target), "port_empty": port_empty, "record": record,
        "trained_exact": trained_exact, "neutral_exact": neutral_exact,
    }


def run_extinction(kernel, mode):
    n, junction, train_tick = 43, (21, 21, 21), 4
    extinction_tick, query_tick, path = 12, 22, 3
    world = initial_world(kernel, n, junction, train_tick, "trained")
    schedule = defaultdict(list)
    memory_at_extinction = add(junction, MEMORY_B, extinction_tick-train_tick, n)
    extinction_target = add(memory_at_extinction, (0, 0, 5), 1, n) if mode == "matched_exposure" else memory_at_extinction
    arrival_tick = extinction_tick + 1 if mode == "history_shuffled" else extinction_tick
    if mode != "no_extinction":
        schedule_arrival(schedule, extinction_target, arrival_tick, path, CUE, 13, 321, 3021, n, "unreinforced_cue")
    old_target = add(junction, MEMORY_B, query_tick-train_tick, n)
    schedule_arrival(schedule, old_target, query_tick, 4, CUE, 17, 323, 3023, n, "old_channel_probe")
    records = {}
    ports_empty = True
    for tick in range(query_tick+1):
        for spec in schedule[tick]:
            ports_empty = ports_empty and int(world.raw[spec["port"]]) == 0
            inject(world, spec)
        if tick == extinction_tick:
            records["extinction_event"] = decode(world.raw, memory_at_extinction)
        if tick == query_tick:
            records["old_channel"] = decode(world.raw, old_target)
        if tick < query_tick:
            world.tick()
    old = records.get("old_channel")
    extinguished = old is not None and old["d"] == list(CUE) and old["sreg"] == 17
    retained = old is not None and old["d"] == list(EXTINCTED_ROUTE) and old["sreg"] == 29
    return {"mode": mode, "ports_empty": ports_empty, "records": records, "old_channel_extinguished": extinguished, "old_channel_retained": retained}


def run_reversal(kernel, variant, teacher_kind):
    n, junction, train_tick = 47, (23, 23, 23), 4
    reset_tick, retrain_tick, query_tick = 12, 15, 24
    world = initial_world(kernel, n, junction, train_tick, "trained")
    schedule = defaultdict(list)
    memory_at_reset = add(junction, MEMORY_B, reset_tick-train_tick, n)
    if variant != "no_reset":
        schedule_arrival(schedule, memory_at_reset, reset_tick, 3, ERASER_B, 13, 331, 3031, n, "ordinary_reset")
    if variant != "no_retrain":
        teacher = TEACHER_C if teacher_kind == "C" else TEACHER_B
        schedule_arrival(schedule, junction, retrain_tick, 3, CUE, 5, 333, 3033, n, "retraining_cue")
        teacher_arrival = retrain_tick + 1 if variant == "history_shuffled" else retrain_tick
        schedule_arrival(schedule, junction, teacher_arrival, 3, teacher, 7, 335, 3035, n, "retraining_teacher")
    memory = MEMORY_C if teacher_kind == "C" else MEMORY_B
    new_target = add(junction, memory, query_tick-retrain_tick, n)
    schedule_arrival(schedule, new_target, query_tick, 4, CUE, 11, 337, 3037, n, "new_channel_probe")
    records = {}
    ports_empty = True
    for tick in range(query_tick+1):
        for spec in schedule[tick]:
            ports_empty = ports_empty and int(world.raw[spec["port"]]) == 0
            inject(world, spec)
        if tick == reset_tick:
            records["reset_event"] = decode(world.raw, memory_at_reset)
        if tick == retrain_tick:
            records["retrain_event"] = decode(world.raw, junction)
        if tick == query_tick:
            records["new_channel"] = decode(world.raw, new_target)
        if tick < query_tick:
            world.tick()
    expected_memory_s = 12
    expected_d = list(signsum(memory, CUE))
    new = records.get("new_channel")
    learned = new is not None and new["d"] == expected_d and new["sreg"] == min(expected_memory_s+11, 19664)
    neutral = new is not None and new["d"] == list(CUE) and new["sreg"] == 11
    return {"variant": variant, "teacher_kind": teacher_kind, "ports_empty": ports_empty, "records": records, "learned": learned, "neutral": neutral}


def main():
    kernel, environment = verify_and_load_kernel(1)
    directions = [d for d in itertools.product((-1, 0, 1), repeat=3) if d != (0, 0, 0) and d != MEMORY_B]
    transfer_modes = ("trained", "untrained", "history_shuffled", "label_shuffled", "matched_exposure")
    transfer = [run_transfer(kernel, d, mode) for d in directions for mode in transfer_modes]
    extinction = [run_extinction(kernel, mode) for mode in ("cue_only", "no_extinction", "matched_exposure", "history_shuffled")]
    reversal = [
        run_reversal(kernel, "full", "C"),
        run_reversal(kernel, "no_retrain", "C"),
        run_reversal(kernel, "history_shuffled", "C"),
        run_reversal(kernel, "full", "B"),
        run_reversal(kernel, "no_retrain", "B"),
    ]
    trained = [r for r in transfer if r["mode"] == "trained"]
    negatives = [r for r in transfer if r["mode"] != "trained"]
    summary = {
        "unseen_query_directions": len(directions),
        "transfer_trained_exact": sum(r["trained_exact"] for r in trained),
        "transfer_trained_total": len(trained),
        "transfer_negative_neutral": sum(r["neutral_exact"] for r in negatives),
        "transfer_negative_total": len(negatives),
        "all_transfer_ports_empty": all(r["port_empty"] for r in transfer),
        "extinction_old_channel_neutral": next(r["old_channel_extinguished"] for r in extinction if r["mode"] == "cue_only"),
        "extinction_controls_retain": all(r["old_channel_retained"] for r in extinction if r["mode"] != "cue_only"),
        "all_extinction_ports_empty": all(r["ports_empty"] for r in extinction),
        "reversal_C_learned": reversal[0]["learned"],
        "reversal_controls_neutral": reversal[1]["neutral"] and reversal[2]["neutral"],
        "reacquisition_B_learned": reversal[3]["learned"],
        "reacquisition_control_neutral": reversal[4]["neutral"],
        "all_reversal_ports_empty": all(r["ports_empty"] for r in reversal),
    }
    result = {
        "schema":"dee.v27.core06.c6d04.v1",
        "experiment_id":"C6D04_REVERSAL_EXTINCTION_TRANSFER",
        "role":"DISCOVERY_EVIDENCE_ONLY",
        "question":"Does the confirmed collision-written learner transfer to unseen query directions and support ordinary-experience extinction, reversal and reacquisition?",
        "hypotheses":{
            "H_operator_transfer":"the trained memory route applies the reducer map to collision-compatible directions never used in training",
            "H_fixed_memory":"an unreinforced cue cannot alter the learned route",
            "H_reversible":"ordinary reset plus a new paired experience can replace or reacquire the route",
            "H_exposure":"unpaired, shuffled or off-channel exposure reproduces the effect",
        },
        "operational_note":"Extinction means loss of the old-channel response; it need not mean destruction of all history. Reversal includes an ordinary reset carrier, not hidden-state editing.",
        "kernel_environment":environment,
        "summary":summary,
        "transfer":transfer,
        "extinction":extinction,
        "reversal_and_reacquisition":reversal,
    }
    result["content_sha256"] = canonical_hash(result)
    atomic_json(OUT, result)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
