#!/usr/bin/env python3
"""Frozen C7H01: causal transfer of learned response repertoire."""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core07_common import NativeWorld, atomic_json, canonical_hash, fields, pack, verify_and_load_kernel

WORK = Path(__file__).resolve().parents[1]
LOCK = WORK / "HOLDOUT_LOCKS" / "C7H01_FUNCTIONAL_LEARNING_TRANSFER.json"
OUT = WORK / "RESULTS" / "C7H01_functional_learning_transfer.json"
EXPECTED_LOCK_SHA256 = "a8d7ec3305de5fa0d91969cf05b37d93c3f45125a444c83f1ef5c3b1e3a58e93"
BASE = {
    "cue": (1, 0, 0),
    "teacher": (-1, 1, 0),
    "memory": (0, 1, 0),
    "relay": (1, -1, 0),
    "transfer": (1, 0, 0),
    "query": (0, 1, 0),
    "response": (1, 1, 0),
    "off_path": (0, 0, 1),
}


def add(q, d, k, n):
    return tuple((q[i] + k * d[i]) % n for i in range(3))


def transform(v, permutation, signs):
    return tuple(signs[i] * v[permutation[i]] for i in range(3))


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


def place_initial(raw, clock, target, tick, d, sreg, state, clk, n):
    q = add(target, d, -tick, n)
    if int(raw[q]) != 0:
        raise RuntimeError(f"initial overlap {q}")
    raw[q] = pack(state, sreg, d, 1)
    clock[q] = np.uint64(clk)


def inject(world, q, d, sreg, state, clk):
    if int(world.raw[q]) != 0:
        raise RuntimeError(f"occupied injection port {q}")
    value = pack(state, sreg, d, 1)
    world.raw_a[q] = value
    world.raw_b[q] = value
    world.clock_a[q] = np.uint64(clk)
    world.clock_b[q] = np.uint64(clk)


def clear(world, q):
    present = int(world.raw[q]) != 0
    world.raw_a[q] = np.uint64(0)
    world.raw_b[q] = np.uint64(0)
    world.clock_a[q] = np.uint64(0)
    world.clock_b[q] = np.uint64(0)
    return present


def wilson(k, n, z=1.959963984540054):
    p = k / n
    den = 1 + z * z / n
    center = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [center - half, center + half]


def simulate(kernel, cell, query, mode, lock):
    n = cell["n"]
    t0 = lock["domain"]["train_tick"]
    tr = lock["domain"]["relay_tick"]
    tq = lock["domain"]["query_tick"]
    path = lock["domain"]["query_path"]
    cut_tick = tr + lock["parameters"]["cut_offset_after_relay"]
    v = cell["vectors"]
    cue, teacher, memory = tuple(v["cue"]), tuple(v["teacher"]), tuple(v["memory"])
    relay, transfer = tuple(v["relay"]), tuple(v["transfer"])
    query_d, response = tuple(v["query"]), tuple(v["response"])
    off = tuple(v["off_path"])
    junction = tuple(cell["junction"])
    relay_point = add(junction, memory, tr - t0, n)
    receiver = add(relay_point, transfer, tq - tr, n)
    cut_point = add(relay_point, transfer, cut_tick - tr, n)
    off_path_point = add(cut_point, off, lock["parameters"]["off_path_offset"], n)
    sham_receiver = add(receiver, off, 3, n)
    raw = np.zeros((n, n, n), dtype=np.uint64)
    clock = np.zeros_like(raw)

    has_training = mode not in {"source_removed", "untrained_source"}
    learned_delta = cell["delta"] + lock["parameters"]["wrong_label_offset"] if mode == "label_shuffled_source" else cell["delta"]
    if has_training:
        y = cell["training_x"] + learned_delta
        cue_state = cell["states"][6] if mode == "state_nuisance" else cell["states"][0]
        teacher_state = cell["states"][7] if mode == "state_nuisance" else cell["states"][1]
        place_initial(raw, clock, junction, t0, cue, cell["B"] - cell["training_x"], cue_state, cell["clocks"][0], n)
        place_initial(raw, clock, junction, t0, teacher, y, teacher_state, cell["clocks"][1], n)
    elif mode == "untrained_source":
        place_initial(raw, clock, junction, t0, cue, cell["B"] - cell["training_x"], cell["states"][0], cell["clocks"][0], n)

    relay_d = tuple(-x for x in memory) if mode == "direction_zero" else relay
    if mode != "no_transfer":
        place_initial(raw, clock, relay_point, tr, relay_d, 0, cell["states"][2], cell["clocks"][2], n)

    world = NativeWorld(kernel, raw, clock, threads=1)
    injection_target = sham_receiver if mode == "destination_sham" else receiver
    injection_port = add(injection_target, query_d, -path, n)
    events = {}
    for tick in range(tq + 1):
        if tick == t0:
            events["training"] = decode(world.raw, junction)
        if tick == t0 + 3 and mode == "memory_ablation":
            events["memory_ablation_present"] = clear(world, add(junction, memory, 3, n))
        if tick == tr:
            events["relay"] = decode(world.raw, relay_point)
        if tick == cut_tick and mode == "corridor_cut":
            events["corridor_cut_present"] = clear(world, cut_point)
        if tick == cut_tick and mode == "off_path_cut":
            events["off_path_cut_present"] = clear(world, off_path_point)
        if tick == tq - path:
            events["query_port_empty"] = int(world.raw[injection_port]) == 0
            inject(world, injection_port, query_d, query, cell["states"][4], cell["clocks"][4])
        if tick == tq:
            events["receiver"] = decode(world.raw, receiver)
            events["sham_receiver"] = decode(world.raw, sham_receiver)
        if tick < tq:
            world.tick()

    rec = events["receiver"]
    decoded = None if rec is None else rec["sreg"] - cell["B"]
    exact = rec is not None and rec["d"] == list(response) and decoded == query + cell["delta"]
    expected_memory = cell["B"] + learned_delta
    training = events.get("training")
    relay_record = events.get("relay")
    training_exact = training is not None and training["d"] == list(memory) and training["sreg"] == expected_memory
    relay_exact = relay_record is not None and relay_record["d"] == list(transfer) and relay_record["sreg"] == expected_memory
    return {
        "cell": cell["cell"],
        "n": n,
        "frame": cell["frame"],
        "delta": cell["delta"],
        "training_x": cell["training_x"],
        "query": query,
        "mode": mode,
        "expected": query + cell["delta"],
        "decoded": decoded,
        "exact_function": exact,
        "training_exact": training_exact,
        "relay_exact": relay_exact,
        "geometry": {"junction": list(junction), "relay": list(relay_point), "receiver": list(receiver), "cut": list(cut_point)},
        "events": events,
    }


def main():
    observed = hashlib.sha256(LOCK.read_bytes()).hexdigest()
    if observed != EXPECTED_LOCK_SHA256:
        raise RuntimeError(f"holdout lock mismatch: {observed}")
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    kernel, environment = verify_and_load_kernel(lock["parameters"]["threads"])
    cells = []
    for i, (n, delta, x, queries, frame, seed) in enumerate(zip(
        lock["domain"]["new_sizes"],
        lock["domain"]["new_deltas"],
        lock["domain"]["training_x"],
        lock["domain"]["unseen_queries_by_cell"],
        lock["domain"]["frames"],
        lock["parameters"]["seeds"],
        strict=True,
    )):
        if x in queries:
            raise RuntimeError("holdout query leaked into training input")
        rng = np.random.default_rng(seed)
        vectors = {k: list(transform(d, frame["permutation"], frame["signs"])) for k, d in BASE.items()}
        junction = [int(q) for q in rng.integers(9, n - 9, size=3)]
        cells.append({
            "cell": i,
            "n": n,
            "delta": delta,
            "training_x": x,
            "queries": queries,
            "B": lock["domain"]["base_offset"],
            "frame": frame,
            "vectors": vectors,
            "junction": junction,
            "states": [int(q) for q in rng.integers(1, 2**32, size=8, dtype=np.uint64)],
            "clocks": [int(rng.bit_generator.random_raw()) for _ in range(8)],
        })

    cases = [simulate(kernel, cell, query, mode, lock) for cell in cells for query in cell["queries"] for mode in lock["parameters"]["modes"]]
    positive_modes = {"transferred", "off_path_cut", "state_nuisance"}
    negative_modes = set(lock["parameters"]["modes"]) - positive_modes
    positives = [c for c in cases if c["mode"] in positive_modes]
    negatives = [c for c in cases if c["mode"] in negative_modes]
    exact_positive = sum(c["exact_function"] for c in positives)
    rates = {
        "positive_exact_rate": exact_positive / len(positives),
        "negative_inexact_rate": sum(not c["exact_function"] for c in negatives) / len(negatives),
        "negative_any_exact_rate": sum(c["exact_function"] for c in negatives) / len(negatives),
        "ports_empty_rate": sum(c["events"].get("query_port_empty") is True for c in cases) / len(cases),
        "memory_ablation_target_present_rate": sum(c["events"].get("memory_ablation_present") is True for c in cases if c["mode"] == "memory_ablation") / len([c for c in cases if c["mode"] == "memory_ablation"]),
        "corridor_cut_target_present_rate": sum(c["events"].get("corridor_cut_present") is True for c in cases if c["mode"] == "corridor_cut") / len([c for c in cases if c["mode"] == "corridor_cut"]),
        "off_path_cut_target_empty_rate": sum(c["events"].get("off_path_cut_present") is False for c in cases if c["mode"] == "off_path_cut") / len([c for c in cases if c["mode"] == "off_path_cut"]),
        "training_and_relay_exact_rate": sum(c["training_exact"] and c["relay_exact"] for c in positives) / len(positives),
    }
    interval = wilson(exact_positive, len(positives))
    m = lock["minimum_relevance"]
    pass_conditions = {
        "positive": rates["positive_exact_rate"] >= m["positive_exact_rate"],
        "positive_wilson": interval[0] >= m["positive_wilson_95_lower"],
        "negative": rates["negative_inexact_rate"] >= m["negative_inexact_rate"],
        "no_control_exact": rates["negative_any_exact_rate"] <= m["negative_any_exact_rate_max"],
        "ports": rates["ports_empty_rate"] >= m["ports_empty_rate"],
        "memory_ablation": rates["memory_ablation_target_present_rate"] >= m["memory_ablation_target_present_rate"],
        "corridor_cut": rates["corridor_cut_target_present_rate"] >= m["corridor_cut_target_present_rate"],
        "off_path_cut": rates["off_path_cut_target_empty_rate"] >= m["off_path_cut_target_empty_rate"],
        "mechanism": rates["training_and_relay_exact_rate"] >= m["training_and_relay_exact_rate"],
    }
    verdict = "PASS" if all(pass_conditions.values()) else "FAIL"
    result = {
        "schema": "dee.v27.core07.c7h01.v1",
        "experiment_id": lock["hypothesis_id"],
        "role": "FROZEN_CONFIRMATION",
        "lock_sha256": observed,
        "kernel_environment": environment,
        "sample_sizes": {"cells": len(cells), "queries": sum(len(c["queries"]) for c in cells), "cases": len(cases), "positive_cases": len(positives), "negative_controls": len(negatives)},
        "rates": rates,
        "positive_wilson_95": interval,
        "pass_conditions": pass_conditions,
        "verdict": verdict,
        "epistemic_scope": "Functional identity is equality of the frozen unseen-query response repertoire after continuous causal carrier transfer. This does not establish instantaneous transfer, material teleportation, or an external physical Rosetta.",
        "cells": cells,
        "cases": cases,
    }
    result["content_sha256"] = canonical_hash(result)
    atomic_json(OUT, result)
    print(json.dumps({k: result[k] for k in ("sample_sizes", "rates", "positive_wilson_95", "pass_conditions", "verdict")}, indent=2, sort_keys=True))
    return 0 if verdict == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
