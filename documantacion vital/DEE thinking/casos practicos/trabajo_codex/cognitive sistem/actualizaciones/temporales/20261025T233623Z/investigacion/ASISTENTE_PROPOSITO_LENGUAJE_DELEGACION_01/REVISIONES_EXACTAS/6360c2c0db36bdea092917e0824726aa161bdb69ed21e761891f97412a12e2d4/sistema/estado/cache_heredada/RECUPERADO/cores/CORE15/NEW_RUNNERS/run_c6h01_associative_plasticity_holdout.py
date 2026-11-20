#!/usr/bin/env python3
"""Frozen C6H01 associative-plasticity holdout."""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from native_core import NativeWorld, atomic_json, canonical_hash, fields, pack, verify_and_load_kernel


WORK = Path(__file__).resolve().parents[1]
LOCK = WORK / "HOLDOUT_LOCKS" / "C6H01_COLLISION_WRITTEN_ASSOCIATIVE_PLASTICITY.json"
OUT = WORK / "RESULTS" / "C6H01_associative_plasticity_holdout.json"
EXPECTED_LOCK_SHA256 = "d803b826c106a30317691c55411e34595aa6e86eb98afac651fab5e792652de7"

BASE = {
    "cue": (1, 0, 0),
    "teacher": (-1, 1, 0),
    "memory": (0, 1, 0),
    "wrong_teacher": (-1, 0, 1),
    "eraser": (1, -1, 0),
    "off_shift": (0, 0, 4),
}


def add(q, d, k, n):
    return tuple((q[i] + k * d[i]) % n for i in range(3))


def transform(v, permutation, signs):
    return tuple(signs[i] * v[permutation[i]] for i in range(3))


def signsum(a, b):
    return tuple(int(np.sign(a[i] + b[i])) for i in range(3))


def decode(raw, q):
    if int(raw[q]) == 0:
        return None
    f = fields(raw)
    return {"state": int(f["state"][q]), "sreg": int(f["sreg"][q]), "d": [int(f[x][q]) for x in ("dx", "dy", "dz")], "semantic": int(f["semantic"][q])}


def wilson(k, n, z=1.959963984540054):
    p = k / n
    den = 1 + z*z/n
    center = (p + z*z/(2*n)) / den
    half = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
    return center-half, center+half


def place_arrival(raw, clock, target, tick, direction, sreg, state, clk, n):
    start = add(target, direction, -tick, n)
    if int(raw[start]) != 0:
        raise RuntimeError(f"initial overlap at {start}")
    raw[start] = pack(state, sreg, direction, 1)
    clock[start] = np.uint64(clk)
    return start


def simulate(kernel, cell, mode):
    n = cell["n"]
    junction = tuple(cell["junction"])
    train_tick = cell["train_tick"]
    delay = cell["delay"]
    cue = tuple(cell["vectors"]["cue"])
    teacher = tuple(cell["vectors"]["teacher"])
    memory = tuple(cell["vectors"]["memory"])
    wrong_teacher = tuple(cell["vectors"]["wrong_teacher"])
    eraser = tuple(cell["vectors"]["eraser"])
    off_shift = tuple(cell["vectors"]["off_shift"])
    raw = np.zeros((n, n, n), dtype=np.uint64)
    clock = np.zeros_like(raw)
    train_junction = add(junction, off_shift, 1, n) if mode == "matched_exposure" else junction
    cue_present = mode not in {"untrained", "teacher_only"}
    teacher_present = mode not in {"untrained", "cue_only"}
    selected_teacher = wrong_teacher if mode == "label_shuffled" else teacher
    teacher_tick = train_tick + 1 if mode == "history_shuffled" else train_tick
    starts = {}
    if cue_present:
        starts["training_cue"] = place_arrival(raw, clock, train_junction, train_tick, cue, cell["cue_sreg"], cell["states"][0], cell["clocks"][0], n)
    if teacher_present:
        starts["teacher"] = place_arrival(raw, clock, train_junction, teacher_tick, selected_teacher, cell["teacher_sreg"], cell["states"][1], cell["clocks"][1], n)
    query_tick = train_tick + delay
    inject_tick = query_tick - cell["query_path"]
    readout = add(junction, memory, delay, n)
    query_target = add(readout, off_shift, 1, n) if mode == "off_channel" else readout
    query_port = add(query_target, cue, -cell["query_path"], n)
    reset_tick = train_tick + 3
    reset_point = add(junction, memory, reset_tick-train_tick, n)
    if mode == "reset_experience":
        starts["eraser"] = place_arrival(raw, clock, reset_point, reset_tick, eraser, cell["eraser_sreg"], cell["states"][3], cell["clocks"][3], n)
    world = NativeWorld(kernel, raw, clock, threads=1)
    port_empty = None
    ablation_present = None
    train_record = None
    readout_record = None
    query_record = None
    for tick in range(query_tick + 1):
        if tick == inject_tick and mode != "query_absent":
            port_empty = int(world.raw[query_port]) == 0
            if not port_empty:
                raise RuntimeError(f"occupied frozen input port at {query_port}, tick {tick}")
            world.raw_a[query_port] = pack(cell["states"][2], cell["query_sreg"], cue, 1)
            world.raw_b[query_port] = world.raw_a[query_port]
            world.clock_a[query_port] = np.uint64(cell["clocks"][2])
            world.clock_b[query_port] = np.uint64(cell["clocks"][2])
        if tick == reset_tick and mode == "memory_ablation":
            point = add(junction, memory, tick-train_tick, n)
            ablation_present = int(world.raw[point]) != 0
            world.raw_a[point] = np.uint64(0)
            world.raw_b[point] = np.uint64(0)
            world.clock_a[point] = np.uint64(0)
            world.clock_b[point] = np.uint64(0)
        if tick == train_tick:
            train_record = decode(world.raw, train_junction)
        if tick == query_tick:
            readout_record = decode(world.raw, readout)
            query_record = decode(world.raw, query_target)
        if tick < query_tick:
            world.tick()
    memory_sreg = min(cell["cue_sreg"] + cell["teacher_sreg"], 19664)
    expected_response_sreg = min(memory_sreg + cell["query_sreg"], 19664)
    expected_response_d = list(signsum(memory, cue))
    training_exact = train_record is not None and train_record["d"] == list(memory) and train_record["sreg"] == memory_sreg
    trained_exact = readout_record is not None and readout_record["d"] == expected_response_d and readout_record["sreg"] == expected_response_sreg
    neutral_exact = readout_record is not None and readout_record["d"] == list(cue) and readout_record["sreg"] == cell["query_sreg"]
    memory_only_exact = readout_record is not None and readout_record["d"] == list(memory) and readout_record["sreg"] == memory_sreg
    off_channel_exact = mode == "off_channel" and memory_only_exact and query_record is not None and query_record["d"] == list(cue) and query_record["sreg"] == cell["query_sreg"]
    return {
        "cell_id": cell["cell_id"], "mode": mode, "n": n, "junction": list(junction), "train_tick": train_tick,
        "delay": delay, "post_wrap": delay > n, "readout": list(readout), "query_target": list(query_target), "query_port": list(query_port),
        "starts": {key: list(value) for key, value in starts.items()}, "port_empty": port_empty, "ablation_present": ablation_present,
        "train_record": train_record, "readout_record": readout_record, "query_record": query_record,
        "memory_sreg": memory_sreg, "expected_response_sreg": expected_response_sreg, "expected_response_d": expected_response_d,
        "training_exact": training_exact, "trained_exact": trained_exact, "neutral_exact": neutral_exact,
        "memory_only_exact": memory_only_exact, "off_channel_exact": off_channel_exact,
    }


def main():
    observed = hashlib.sha256(LOCK.read_bytes()).hexdigest()
    if observed != EXPECTED_LOCK_SHA256:
        raise RuntimeError(f"lock mismatch: {observed}")
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    kernel, environment = verify_and_load_kernel(1)
    delays_raw = lock["domain"]["delays_per_frame"]
    sreg_pairs = lock["parameters"]["training_sreg_pairs"]
    query_sregs = lock["parameters"]["query_sreg"]
    cells = []
    for frame_index, (n, train_tick, frame, seed) in enumerate(zip(lock["domain"]["new_sizes"], lock["domain"]["train_ticks"], lock["domain"]["frames"], lock["parameters"]["seeds"], strict=True)):
        rng = np.random.default_rng(seed)
        junction = tuple(int(x) for x in rng.integers(8, n-8, size=3))
        vectors = {name: transform(value, frame["permutation"], frame["signs"]) for name, value in BASE.items()}
        for trial_index, delay_spec in enumerate(delays_raw):
            delay = int(delay_spec) if delay_spec.isdigit() else n + int(delay_spec.split("+")[1])
            states = [int(x) for x in rng.integers(1, 2**32, size=4, dtype=np.uint64)]
            clocks = [int(rng.bit_generator.random_raw()) for _ in range(4)]
            cells.append({
                "cell_id": f"F{frame_index}_T{trial_index}", "frame_index": frame_index, "trial_index": trial_index,
                "n": n, "junction": list(junction), "train_tick": train_tick, "delay": delay, "query_path": lock["domain"]["query_path_length"],
                "vectors": {name: list(value) for name, value in vectors.items()}, "cue_sreg": sreg_pairs[trial_index][0],
                "teacher_sreg": sreg_pairs[trial_index][1], "query_sreg": query_sregs[trial_index], "eraser_sreg": 13,
                "states": states, "clocks": clocks,
            })
    cases = []
    core_modes = lock["parameters"]["core_modes_every_trial"]
    extended_modes = lock["parameters"]["extended_modes_trial_3"]
    for cell in cells:
        for mode in core_modes:
            cases.append(simulate(kernel, cell, mode))
        if cell["trial_index"] == 3:
            for mode in extended_modes:
                cases.append(simulate(kernel, cell, mode))
    trained = [c for c in cases if c["mode"] == "trained_pair"]
    core_negative = [c for c in cases if c["mode"] in {"untrained", "history_shuffled", "label_shuffled"}]
    single_matched = [c for c in cases if c["mode"] in {"cue_only", "teacher_only", "matched_exposure"}]
    reset_ablation = [c for c in cases if c["mode"] in {"reset_experience", "memory_ablation"}]
    absent = [c for c in cases if c["mode"] == "query_absent"]
    off = [c for c in cases if c["mode"] == "off_channel"]
    post_wrap = [c for c in trained if c["post_wrap"]]
    trained_exact_count = sum(c["training_exact"] and c["trained_exact"] for c in trained)
    interval = wilson(trained_exact_count, len(trained))
    rates = {
        "trained_exact": trained_exact_count / len(trained),
        "core_negative_neutral": sum(c["neutral_exact"] for c in core_negative) / len(core_negative),
        "core_negative_false_trained": sum(c["trained_exact"] for c in core_negative) / len(core_negative),
        "single_and_matched_neutral": sum(c["neutral_exact"] for c in single_matched) / len(single_matched),
        "reset_and_ablation_neutral": sum(c["neutral_exact"] for c in reset_ablation) / len(reset_ablation),
        "query_absent_memory_only": sum(c["memory_only_exact"] for c in absent) / len(absent),
        "off_channel_specific": sum(c["off_channel_exact"] for c in off) / len(off),
        "query_ports_empty": sum(c["port_empty"] is not False for c in cases) / len(cases),
        "post_wrap_trained_exact": sum(c["training_exact"] and c["trained_exact"] for c in post_wrap) / len(post_wrap),
        "ablation_memory_present": sum(c["ablation_present"] is True for c in cases if c["mode"] == "memory_ablation") / len([c for c in cases if c["mode"] == "memory_ablation"]),
    }
    threshold = lock["minimum_relevance"]
    pass_conditions = {
        "trained": rates["trained_exact"] >= threshold["trained_exact_rate"],
        "every_cell": all(c["training_exact"] and c["trained_exact"] for c in trained),
        "wilson": interval[0] >= threshold["trained_wilson_95_lower"],
        "core_neutral": rates["core_negative_neutral"] >= threshold["core_negative_neutral_rate"],
        "core_false": rates["core_negative_false_trained"] <= threshold["core_negative_trained_false_rate_max"],
        "single_matched": rates["single_and_matched_neutral"] >= threshold["extended_single_and_matched_neutral_rate"],
        "reset_ablation": rates["reset_and_ablation_neutral"] >= threshold["reset_and_ablation_neutral_rate"],
        "absent": rates["query_absent_memory_only"] >= threshold["query_absent_memory_only_rate"],
        "off": rates["off_channel_specific"] >= threshold["off_channel_specific_rate"],
        "ports": rates["query_ports_empty"] >= threshold["query_ports_empty_rate"],
        "post_wrap": rates["post_wrap_trained_exact"] >= threshold["post_wrap_trained_exact_rate"],
        "ablation_target": rates["ablation_memory_present"] == 1.0,
    }
    fail_conditions = {
        "trained": rates["trained_exact"] < 0.90,
        "frame": any(sum(c["training_exact"] and c["trained_exact"] for c in trained if c["cell_id"].startswith(f"F{i}_")) < 3 for i in range(5)),
        "core_neutral": rates["core_negative_neutral"] < 0.95,
        "core_false": rates["core_negative_false_trained"] > 0.05,
        "extended": min(rates["single_and_matched_neutral"], rates["reset_and_ablation_neutral"], rates["query_absent_memory_only"], rates["off_channel_specific"], rates["query_ports_empty"]) < 0.80,
        "post_wrap": rates["post_wrap_trained_exact"] < 0.90,
    }
    verdict = "PASS" if all(pass_conditions.values()) else "FAIL" if any(fail_conditions.values()) else "INCONCLUSIVE"
    result = {
        "schema": "dee.v27.core06.c6h01.v1", "experiment_id": lock["hypothesis_id"], "role": "FROZEN_CONFIRMATION",
        "lock_sha256": observed, "kernel_environment": environment, "sample_sizes": {"cells": len(cells), "worlds": len(cases), "trained": len(trained), "core_negative": len(core_negative), "post_wrap_trained": len(post_wrap)},
        "rates": rates, "trained_wilson_95": list(interval), "pass_conditions": pass_conditions, "fail_conditions": fail_conditions,
        "verdict": verdict, "cells": cells, "cases": cases,
    }
    result["content_sha256"] = canonical_hash(result)
    atomic_json(OUT, result)
    print(json.dumps({key: result[key] for key in ("sample_sizes", "rates", "trained_wilson_95", "pass_conditions", "verdict")}, indent=2, sort_keys=True))
    return 0 if verdict == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
