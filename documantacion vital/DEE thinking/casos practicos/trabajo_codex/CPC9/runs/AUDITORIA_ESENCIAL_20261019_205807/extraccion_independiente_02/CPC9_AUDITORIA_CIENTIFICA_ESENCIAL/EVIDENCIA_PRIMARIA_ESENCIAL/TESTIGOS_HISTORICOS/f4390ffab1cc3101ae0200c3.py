#!/usr/bin/env python3
"""Frozen C7H03: monotonic functional reprogramming and bounded repair negative."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core07_common import NativeWorld, atomic_json, canonical_hash, fields, pack, verify_and_load_kernel

WORK = Path(__file__).resolve().parents[1]
LOCK = WORK / "HOLDOUT_LOCKS" / "C7H03_REPROGRAMMABLE_FUNCTIONAL_MATTER.json"
OUT = WORK / "RESULTS" / "C7H03_reprogrammable_functional_matter.json"
EXPECTED_LOCK_SHA256 = "125bfd3299276bf3178330c983e42549803fae13b367f7c418cb0c08d27d59b4"
BASE = {
    "cue": (1, 0, 0), "teacher": (-1, 1, 0), "memory": (0, 1, 0),
    "programmer": (1, -1, 0), "programmed": (1, 0, 0), "redirect": (-1, 1, 0),
    "response": (1, 1, 0), "off": (0, 0, 1),
}


def add(q, d, k, n):
    return tuple((q[i] + k * d[i]) % n for i in range(3))


def transform(v, permutation, signs):
    return tuple(signs[i] * v[permutation[i]] for i in range(3))


def decode(raw, q):
    if int(raw[q]) == 0:
        return None
    f = fields(raw)
    return {"state": int(f["state"][q]), "sreg": int(f["sreg"][q]), "d": [int(f[x][q]) for x in ("dx", "dy", "dz")], "semantic": int(f["semantic"][q])}


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


def overwrite(world, q, *, state=None, sreg=None, direction=None, clock=None):
    rec = decode(world.raw, q)
    if rec is None:
        return False
    value = pack(rec["state"] if state is None else state, rec["sreg"] if sreg is None else sreg, tuple(rec["d"]) if direction is None else direction, rec["semantic"])
    world.raw_a[q] = value
    world.raw_b[q] = value
    if clock is not None:
        world.clock_a[q] = np.uint64(clock)
        world.clock_b[q] = np.uint64(clock)
    return True


def clear(world, q):
    present = int(world.raw[q]) != 0
    world.raw_a[q] = np.uint64(0); world.raw_b[q] = np.uint64(0)
    world.clock_a[q] = np.uint64(0); world.clock_b[q] = np.uint64(0)
    return present


def simulate(kernel, cell, query, mode, lock):
    n, v = cell["n"], cell["vectors"]
    cue, teacher, memory = tuple(v["cue"]), tuple(v["teacher"]), tuple(v["memory"])
    programmer, programmed, redirect = tuple(v["programmer"]), tuple(v["programmed"]), tuple(v["redirect"])
    response, off = tuple(v["response"]), tuple(v["off"])
    t0, tp, tr, td, trepair, tq, path = (lock["domain"][k] for k in ("train_tick", "program_tick", "redirect_tick", "damage_tick", "repair_tick", "query_tick", "query_path"))
    j = tuple(cell["junction"])
    pp = add(j, memory, tp - t0, n)
    rp = add(pp, programmed, tr - tp, n)
    dp = add(rp, memory, td - tr, n)
    repair_modes = {"direction_damage_repair", "direction_damage_offpath_repair", "load_damage_repair", "support_damage_repair"}
    normal_receiver = add(rp, memory, tq - tr, n)
    repaired_receiver = add(dp, memory, tq - trepair, n)
    receiver = repaired_receiver if mode in repair_modes or mode == "direction_damage_no_repair" else normal_receiver
    raw = np.zeros((n, n, n), dtype=np.uint64); clock = np.zeros_like(raw)
    x, B = cell["training_x"], lock["domain"]["base_offset"]
    cue_state = cell["states"][9] if mode == "source_state_nuisance" else cell["states"][0]
    teacher_state = cell["states"][10] if mode == "source_state_nuisance" else cell["states"][1]
    place_initial(raw, clock, j, t0, cue, B - x, cue_state, cell["clocks"][0], n)
    place_initial(raw, clock, j, t0, teacher, x + cell["delta"], teacher_state, cell["clocks"][1], n)
    if mode != "programmer_absent":
        ptarget = add(pp, off, 3, n) if mode == "programmer_offpath" else pp
        place_initial(raw, clock, ptarget, tp, programmer, cell["update"], cell["states"][2], cell["clocks"][2], n)
    place_initial(raw, clock, rp, tr, redirect, 0, cell["states"][3], cell["clocks"][3], n)
    if mode in repair_modes:
        repair_target = add(dp, off, 2, n) if mode == "direction_damage_offpath_repair" else dp
        place_initial(raw, clock, repair_target, trepair, memory, 0, cell["states"][4], cell["clocks"][4], n)
    world = NativeWorld(kernel, raw, clock, threads=1)
    query_port = add(receiver, cue, -path, n)
    events = {}
    for tick in range(tq + 1):
        if tick == t0: events["trained"] = decode(world.raw, j)
        if tick == t0 + 3 and mode == "memory_ablation": events["memory_ablation_present"] = clear(world, add(j, memory, 3, n))
        if tick == tp: events["programmed"] = decode(world.raw, pp)
        if tick == tr: events["redirected"] = decode(world.raw, rp)
        if tick == td:
            if mode in {"direction_damage_no_repair", "direction_damage_repair", "direction_damage_offpath_repair"}: events["damage_present"] = overwrite(world, dp, direction=(0, 0, 0))
            elif mode == "load_damage_repair": events["damage_present"] = overwrite(world, dp, sreg=0, direction=(0, 0, 0))
            elif mode == "support_damage_repair": events["damage_present"] = clear(world, dp)
            elif mode == "state_damage": events["damage_present"] = overwrite(world, dp, state=cell["states"][8])
            elif mode == "clock_damage": events["damage_present"] = overwrite(world, dp, clock=cell["clocks"][8])
        if tick == trepair: events["repair_event"] = decode(world.raw, dp)
        if tick == tq - path:
            events["query_port_empty"] = int(world.raw[query_port]) == 0
            inject(world, query_port, cue, query, cell["states"][6], cell["clocks"][6])
        if tick == tq: events["receiver"] = decode(world.raw, receiver)
        if tick < tq: world.tick()
    trained = events.get("trained"); prog = events.get("programmed"); redir = events.get("redirected"); rec = events.get("receiver")
    trained_exact = trained is not None and trained["d"] == list(memory) and trained["sreg"] == B + cell["delta"]
    programmed_exact = prog is not None and prog["d"] == list(programmed) and prog["sreg"] == B + cell["delta"] + cell["update"]
    redirected_exact = redir is not None and redir["d"] == list(memory) and redir["sreg"] == B + cell["delta"] + cell["update"]
    decoded_value = None if rec is None else rec["sreg"] - B
    exact = rec is not None and rec["d"] == list(response) and decoded_value == query + cell["delta"] + cell["update"]
    return {"cell": cell["cell"], "n": n, "frame": cell["frame"], "delta": cell["delta"], "update": cell["update"], "query": query, "mode": mode, "expected": query + cell["delta"] + cell["update"], "decoded": decoded_value, "exact_updated_function": exact, "intermediate_exact": trained_exact and programmed_exact and redirected_exact, "events": events}


def main():
    observed = hashlib.sha256(LOCK.read_bytes()).hexdigest()
    if observed != EXPECTED_LOCK_SHA256: raise RuntimeError(f"lock mismatch {observed}")
    lock = json.loads(LOCK.read_text(encoding="utf-8")); kernel, environment = verify_and_load_kernel(lock["parameters"]["threads"])
    cells = []
    for i, (n, delta, update, queries, frame, x, seed) in enumerate(zip(lock["domain"]["new_sizes"], lock["domain"]["new_deltas"], lock["domain"]["new_updates"], lock["domain"]["unseen_queries_by_cell"], lock["domain"]["frames"], lock["parameters"]["training_x"], lock["parameters"]["seeds"], strict=True)):
        if x in queries: raise RuntimeError("query leaked into training input")
        rng = np.random.default_rng(seed)
        vectors = {k: list(transform(d, frame["permutation"], frame["signs"])) for k, d in BASE.items()}
        cells.append({"cell": i, "n": n, "delta": delta, "update": update, "queries": queries, "training_x": x, "frame": frame, "vectors": vectors, "junction": [int(q) for q in rng.integers(10, n - 10, size=3)], "states": [int(q) for q in rng.integers(1, 2**32, size=12, dtype=np.uint64)], "clocks": [int(rng.bit_generator.random_raw()) for _ in range(12)]})
    cases = [simulate(kernel, cell, q, mode, lock) for cell in cells for q in cell["queries"] for mode in lock["parameters"]["modes"]]
    positive_modes = {"reprogrammed", "source_state_nuisance", "state_damage", "clock_damage"}
    negative_modes = set(lock["parameters"]["modes"]) - positive_modes
    positives = [c for c in cases if c["mode"] in positive_modes]; negatives = [c for c in cases if c["mode"] in negative_modes]
    rates = {
        "positive_exact_rate": sum(c["exact_updated_function"] for c in positives) / len(positives),
        "negative_inexact_rate": sum(not c["exact_updated_function"] for c in negatives) / len(negatives),
        "intermediate_mechanism_exact_rate": sum(c["intermediate_exact"] for c in positives) / len(positives),
        "ports_empty_rate": sum(c["events"].get("query_port_empty") is True for c in cases) / len(cases),
        "delayed_routing_repair_rate": sum(c["exact_updated_function"] for c in cases if c["mode"] == "direction_damage_repair") / len([c for c in cases if c["mode"] == "direction_damage_repair"]),
        "load_repair_rate": sum(c["exact_updated_function"] for c in cases if c["mode"] == "load_damage_repair") / len([c for c in cases if c["mode"] == "load_damage_repair"]),
        "support_repair_rate": sum(c["exact_updated_function"] for c in cases if c["mode"] == "support_damage_repair") / len([c for c in cases if c["mode"] == "support_damage_repair"]),
    }
    m = lock["minimum_relevance"]
    pass_conditions = {"positive": rates["positive_exact_rate"] >= m["positive_exact_rate"], "negative": rates["negative_inexact_rate"] >= m["negative_inexact_rate"], "mechanism": rates["intermediate_mechanism_exact_rate"] >= m["intermediate_mechanism_exact_rate"], "ports": rates["ports_empty_rate"] >= m["ports_empty_rate"], "routing_no_repair": rates["delayed_routing_repair_rate"] <= m["delayed_routing_repair_rate_max"], "load_no_repair": rates["load_repair_rate"] <= m["load_repair_rate_max"], "support_no_repair": rates["support_repair_rate"] <= m["support_repair_rate_max"]}
    verdict = "PASS" if all(pass_conditions.values()) else "FAIL"
    result = {"schema": "dee.v27.core07.c7h03.v1", "experiment_id": lock["hypothesis_id"], "role": "FROZEN_CONFIRMATION", "lock_sha256": observed, "kernel_environment": environment, "sample_sizes": {"cells": len(cells), "queries": sum(len(c["queries"]) for c in cells), "cases": len(cases), "positive_cases": len(positives), "negative_cases": len(negatives)}, "rates": rates, "pass_conditions": pass_conditions, "verdict": verdict, "adjudication_scope": "Lineage/response-quotient reprogramming only. The update is additive/monotonic, externally programmed and not autonomous learning improvement. Repair negative is bounded to delayed generic direction scaffolds after direction-zero, load or support damage.", "cells": cells, "cases": cases}
    result["content_sha256"] = canonical_hash(result); atomic_json(OUT, result)
    print(json.dumps({k: result[k] for k in ("sample_sizes", "rates", "pass_conditions", "verdict")}, indent=2, sort_keys=True)); return 0 if verdict == "PASS" else 2


if __name__ == "__main__": raise SystemExit(main())
