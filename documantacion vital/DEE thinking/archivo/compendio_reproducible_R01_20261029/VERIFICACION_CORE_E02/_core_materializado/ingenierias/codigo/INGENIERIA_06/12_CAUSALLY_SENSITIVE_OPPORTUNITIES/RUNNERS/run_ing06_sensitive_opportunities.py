#!/usr/bin/env python3
"""Gated test of history-conditioned breaking among future-relevant opportunities."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BLOCK = HERE.parent
ROOT = BLOCK.parent
ENGINEERING = ROOT.parent
NRD05 = ENGINEERING / "INGENIERIA_05_HISTORY_CONDITIONED_TRANSFORMATION" / "RUNNERS"
NRD06 = ENGINEERING / "INGENIERIA_05_HISTORY_SPECIFICITY" / "RUNNERS"
sys.path[:0] = [str(NRD05), str(NRD06)]
import run_nrd05_history_conditioned_transformation as nrd05  # noqa: E402
import run_nrd06_history_specificity as nrd06  # noqa: E402

N = 31
ORIGIN = (15, 15, 15)
OFFSETS = (0, 16, 32, 64, 128, 256)
HORIZONS = (32, 64)
OPPORTUNITIES = {
    "P1": ((-9, 0, 0), ((0, 1, 2), (1, 1, 1))),
    "P2": ((0, -9, 0), ((1, 0, 2), (1, 1, 1))),
    "P3": ((0, 0, -9), ((2, 1, 0), (1, 1, 1))),
}
GLOBAL = {
    "MAIN_S0": ((0, 1, 2), (1, 1, 1)),
    "FRESH_V1": ((1, 0, 2), (1, -1, 1)),
    "FRESH_V2": ((2, 1, 0), (-1, 1, 1)),
}
HISTORIES = {"H0": "no_events", "HA": "AB", "HB": "BA"}


def tf(v, spec):
    return nrd05.transform(v, spec[0], spec[1])


def compose(local, global_spec):
    targets = [tf(tf(tuple(1 if i == j else 0 for i in range(3)), local), global_spec) for j in range(3)]
    for permutation in itertools.permutations(range(3)):
        for signs in itertools.product((-1, 1), repeat=3):
            candidate = (permutation, signs)
            if all(tf(tuple(1 if i == j else 0 for i in range(3)), candidate) == targets[j] for j in range(3)):
                return candidate
    raise RuntimeError("signed permutation composition failed")


def shifted(offset, global_spec):
    moved = tf(offset, global_spec)
    return tuple((ORIGIN[i] + moved[i]) % N for i in range(3))


def merge_instance(raw, clock, instance):
    occupied = instance.raw_a != 0
    if np.any((raw != 0) & occupied):
        raise RuntimeError("apparatus overlap")
    raw[occupied] = instance.raw_a[occupied]
    clock[occupied] = instance.clock_a[occupied]


def make_world(kernel, configuration, history, omit=None):
    global_spec = GLOBAL[configuration]
    raw = np.zeros((N, N, N), dtype=np.uint64)
    clock = np.zeros_like(raw)
    central_cfg = {"n": N, "origin": ORIGIN, "permutation": global_spec[0], "signs": global_spec[1], "mode": HISTORIES[history], "event_sreg": 0}
    central, _ = nrd05.construct(kernel, central_cfg)
    merge_instance(raw, clock, central)
    for name, (offset, local_spec) in OPPORTUNITIES.items():
        if name == omit:
            continue
        spec = compose(local_spec, global_spec)
        cfg = {"n": N, "origin": shifted(offset, global_spec), "permutation": spec[0], "signs": spec[1], "mode": "AB", "event_sreg": 0}
        opportunity, _ = nrd05.construct(kernel, cfg)
        merge_instance(raw, clock, opportunity)
    return nrd05.NativeWorld(kernel, raw, clock)


def future(kernel, state, configuration):
    cfg = {"n": N, "origin": ORIGIN, "permutation": GLOBAL[configuration][0], "signs": GLOBAL[configuration][1]}
    c0_world = nrd05.NativeWorld(kernel, state[0], state[1])
    c4_world = nrd05.NativeWorld(kernel, state[0], state[1])
    axes = ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
    for axis in axes:
        direction = tf(axis, GLOBAL[configuration])
        q = tuple((ORIGIN[i] - 3 * direction[i]) % N for i in range(3))
        if int(c4_world.raw_a[q]):
            raise RuntimeError(f"C4 source occupied: {q}")
        c4_world.inject(q, nrd05.pack(8000, 0, direction, 1), 0)
    out = {"C0": {}, "C4": {}}
    for tick in range(1, 65):
        c0_world.tick(); c4_world.tick()
        if tick in HORIZONS:
            out["C0"][tick] = nrd05.checkpoint(c0_world)
            out["C4"][tick] = nrd05.checkpoint(c4_world)
    return out


def raw_signature(left, right):
    lf, rf = nrd05.fields(left[0]), nrd05.fields(right[0])
    return (
        int(np.count_nonzero(left[0] != right[0])),
        int(np.count_nonzero(lf["state"] != rf["state"])),
        int(np.count_nonzero(lf["sreg"] != rf["sreg"])),
        int(np.count_nonzero(lf["semantic"] != rf["semantic"])),
        *sorted(int(np.count_nonzero(lf[k] != rf[k])) for k in ("dx", "dy", "dz")),
    )


def relation(kernel, full, omitted, configuration):
    f_full, f_omit = future(kernel, full, configuration), future(kernel, omitted, configuration)
    vectors = [raw_signature(full, omitted)]
    for horizon in HORIZONS:
        c0 = raw_signature(f_full["C0"][horizon], f_omit["C0"][horizon])
        c4 = raw_signature(f_full["C4"][horizon], f_omit["C4"][horizon])
        response = raw_signature(
            nrd05.pair_effect(f_full["C4"][horizon], f_full["C0"][horizon]),
            nrd05.pair_effect(f_omit["C4"][horizon], f_omit["C0"][horizon]),
        )
        vectors.extend((c0, c4, response))
    digest = hashlib.sha256(json.dumps(vectors, separators=(",", ":")).encode()).hexdigest()
    return {"fingerprint": digest, "vectors": vectors, "future_relevant": any(any(v) for v in vectors[1:])}


def observe(kernel, states, configuration):
    full = states["FULL"]
    relations = {p: relation(kernel, full, states[f"OMIT_{p}"], configuration) for p in OPPORTUNITIES}
    pattern = [relations[p]["fingerprint"] for p in OPPORTUNITIES]
    return {
        "relations": relations,
        "equivalent": len(set(pattern)) == 1,
        "all_future_relevant": all(v["future_relevant"] for v in relations.values()),
        "pattern": pattern,
    }


def checkpoint_branches(branches):
    return {name: nrd05.checkpoint(world) for name, world in branches.items()}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--threads", type=int, default=1); args = parser.parse_args()
    kernel, runtime = nrd05.load_kernel(args.threads)
    telemetry, gates = {}, {}
    gate_states = {}
    for configuration in GLOBAL:
        branches = {"FULL": make_world(kernel, configuration, "H0"), **{f"OMIT_{p}": make_world(kernel, configuration, "H0", p) for p in OPPORTUNITIES}}
        nrd06.tick_all(branches, 4)
        states = checkpoint_branches(branches)
        gate_states[configuration] = states
        gates[configuration] = observe(kernel, states, configuration)
    gates_pass = all(v["equivalent"] and v["all_future_relevant"] for v in gates.values())
    if not gates_pass:
        status = "SENSITIVITY_OR_EQUIVALENCE_GATE_FAILED"
        result = nrd05.seal({"experiment_id":"ING06_CAUSALLY_SENSITIVE_EQUIVALENT_OPPORTUNITIES","status":status,"runtime":runtime,"gates":gates,"history_stage_executed":False,"formal_RW3":False,"L4":False})
        nrd05.write_json(BLOCK / "RESULTS" / "ING06_SENSITIVE_OPPORTUNITIES.json", result)
        print(json.dumps({"status":status,"gates":{k:{"equivalent":v["equivalent"],"all_future_relevant":v["all_future_relevant"]} for k,v in gates.items()}},indent=2)); return

    cases = {}
    for configuration in GLOBAL:
        worlds = {h:{"FULL":make_world(kernel,configuration,h),**{f"OMIT_{p}":make_world(kernel,configuration,h,p) for p in OPPORTUNITIES}} for h in HISTORIES}
        flat = {f"{h}_{b}":w for h,x in worlds.items() for b,w in x.items()}
        nrd06.tick_all(flat, 4)
        elapsed, rows = 0, {}
        for offset in OFFSETS:
            nrd06.tick_all(flat, offset - elapsed); elapsed = offset
            rows[str(offset)] = {}
            for history, branches in worlds.items():
                states = checkpoint_branches(branches)
                for branch, state in states.items():
                    telemetry[f"{configuration}_T{offset}_{history}_{branch}_raw_a"] = state[0]
                    telemetry[f"{configuration}_T{offset}_{history}_{branch}_clock_a"] = state[1]
                rows[str(offset)][history] = observe(kernel, states, configuration)
            rows[str(offset)]["HA_HB_patterns_different"] = rows[str(offset)]["HA"]["pattern"] != rows[str(offset)]["HB"]["pattern"]
        positives=[]
        for i,offset in enumerate(OFFSETS[:-2]):
            window=OFFSETS[i:i+3]
            if all(rows[str(t)]["H0"]["equivalent"] and rows[str(t)]["H0"]["all_future_relevant"] and not rows[str(t)]["HA"]["equivalent"] and not rows[str(t)]["HB"]["equivalent"] and rows[str(t)]["HA_HB_patterns_different"] and rows[str(t)]["HA"]["all_future_relevant"] and rows[str(t)]["HB"]["all_future_relevant"] for t in window): positives.append(offset)
        cases[configuration]={"observations":rows,"persistent_positive_window_starts":positives,"pass":bool(positives)}
    replicated=all(v["pass"] for v in cases.values())
    status="HISTORY_CONDITIONED_EQUIVALENCE_BREAKING" if replicated else "NO_EQUIVALENCE_BREAK_OBSERVED_WITH_SENSITIVE_OPPORTUNITIES"
    np.savez_compressed(BLOCK / "TELEMETRY" / "ING06_SENSITIVE_OPPORTUNITIES.npz", **telemetry)
    result=nrd05.seal({"experiment_id":"ING06_CAUSALLY_SENSITIVE_EQUIVALENT_OPPORTUNITIES","status":status,"runtime":runtime,"gates":gates,"history_stage_executed":True,"cases":cases,"fresh_replication":replicated,"main_world_interventions_after_host_stop":0,"new_unpreloaded_contingency_demonstrated":False,"formal_RW3":False,"L4":False,"telemetry":"TELEMETRY/ING06_SENSITIVE_OPPORTUNITIES.npz"})
    nrd05.write_json(BLOCK / "RESULTS" / "ING06_SENSITIVE_OPPORTUNITIES.json",result)
    print(json.dumps({"status":status,"gates":{k:{"equivalent":v["equivalent"],"all_future_relevant":v["all_future_relevant"]} for k,v in gates.items()},"passes":{k:v["pass"] for k,v in cases.items()}},indent=2))


if __name__ == "__main__": main()
