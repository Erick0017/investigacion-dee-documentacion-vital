#!/usr/bin/env python3
"""Frozen C6H02 holdout: unseen-direction transfer and reversible plasticity."""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from native_core import NativeWorld, atomic_json, canonical_hash, fields, pack, verify_and_load_kernel

WORK = Path(__file__).resolve().parents[1]
LOCK = WORK / "HOLDOUT_LOCKS" / "C6H02_CLASS_GENERALIZATION_AND_REVERSIBLE_PLASTICITY.json"
OUT = WORK / "RESULTS" / "C6H02_class_generalization_reversal_holdout.json"
EXPECTED_LOCK_SHA256 = "0bcddcf4c84b144c54c83cd3a200d4df3b4bdae144108781350d5970348d7553"

BASE = {
    "cue": (1, 0, 0), "teacher_B": (-1, 1, 0), "memory_B": (0, 1, 0),
    "teacher_C": (-1, 0, 1), "memory_C": (0, 0, 1), "eraser_B": (1, -1, 0),
}


def add(q, d, k, n):
    return tuple((q[i] + k*d[i]) % n for i in range(3))


def transform(v, permutation, signs):
    return tuple(signs[i] * v[permutation[i]] for i in range(3))


def signsum(*vectors):
    return tuple(int(np.sign(sum(v[i] for v in vectors))) for i in range(3))


def decode(raw, q):
    if int(raw[q]) == 0:
        return None
    f = fields(raw)
    return {"state":int(f["state"][q]), "sreg":int(f["sreg"][q]), "d":[int(f[x][q]) for x in ("dx","dy","dz")], "semantic":int(f["semantic"][q])}


def wilson(k, n, z=1.959963984540054):
    p = k/n
    den = 1 + z*z/n
    center = (p + z*z/(2*n))/den
    half = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/den
    return center-half, center+half


def place_initial(raw, clock, target, tick, direction, sreg, state, clk, n):
    q = add(target, direction, -tick, n)
    if int(raw[q]) != 0:
        raise RuntimeError(f"initial overlap {q}")
    raw[q] = pack(state, sreg, direction, 1)
    clock[q] = np.uint64(clk)


def schedule_arrival(schedule, target, event_tick, path, direction, sreg, state, clk, n, label):
    schedule[event_tick-path].append({"label":label, "port":add(target,direction,-path,n), "direction":direction, "sreg":sreg, "state":state, "clock":clk})


def inject(world, spec):
    q = spec["port"]
    if int(world.raw[q]) != 0:
        raise RuntimeError(f"occupied frozen port {q} ({spec['label']})")
    value = pack(spec["state"], spec["sreg"], spec["direction"], 1)
    world.raw_a[q] = value; world.raw_b[q] = value
    world.clock_a[q] = np.uint64(spec["clock"]); world.clock_b[q] = np.uint64(spec["clock"])


def make_initial(kernel, cell, mode):
    n, j, t0, v = cell["n"], tuple(cell["junction"]), cell["train_tick"], cell["vectors"]
    raw = np.zeros((n,n,n), dtype=np.uint64); clock = np.zeros_like(raw)
    if mode != "untrained":
        teacher = tuple(v["teacher_C"] if mode == "label_shuffled" else v["teacher_B"])
        tt = t0+1 if mode == "history_shuffled" else t0
        place_initial(raw,clock,j,t0,tuple(v["cue"]),cell["cue_sreg"],cell["states"][0],cell["clocks"][0],n)
        place_initial(raw,clock,j,tt,teacher,cell["teacher_sreg"],cell["states"][1],cell["clocks"][1],n)
    return NativeWorld(kernel,raw,clock,threads=1)


def run_transfer(kernel, cell, query_direction, query_index, mode):
    n, j, t0, v = cell["n"], tuple(cell["junction"]), cell["train_tick"], cell["vectors"]
    memory = tuple(v["memory_B"])
    delay = 13 if query_index % 2 == 0 else n+6
    tq = t0+delay; qpath = 4
    target = add(j,memory,delay,n)
    q_sreg = 101 + query_index*37
    world = make_initial(kernel,cell,mode)
    schedule = defaultdict(list)
    schedule_arrival(schedule,target,tq,qpath,query_direction,q_sreg,cell["states"][2],cell["clocks"][2],n,"genuinely_unseen_query")
    port_empty=True; record=None
    for tick in range(tq+1):
        for spec in schedule[tick]:
            port_empty = port_empty and int(world.raw[spec["port"]]) == 0
            inject(world,spec)
        if tick == tq: record=decode(world.raw,target)
        if tick < tq: world.tick()
    sm=min(cell["cue_sreg"]+cell["teacher_sreg"],19664)
    exp_d=list(signsum(memory,query_direction)); exp_s=min(sm+q_sreg,19664)
    trained=record is not None and record["d"]==exp_d and record["sreg"]==exp_s
    neutral=record is not None and record["d"]==list(query_direction) and record["sreg"]==q_sreg
    return {"frame":cell["frame"],"mode":mode,"n":n,"query_index":query_index,"query_direction":list(query_direction),"delay":delay,"post_wrap":delay>n,"target":list(target),"port_empty":port_empty,"record":record,"expected_d":exp_d,"expected_sreg":exp_s,"trained_exact":trained,"neutral_exact":neutral}


def run_reversal(kernel, cell, variant):
    n,j,t0,v=cell["n"],tuple(cell["junction"]),cell["train_tick"],cell["vectors"]
    cue=tuple(v["cue"]); mb=tuple(v["memory_B"]); mc=tuple(v["memory_C"]); eraser=tuple(v["eraser_B"])
    reset_t=t0+9; retrain_t=t0+13; tq=retrain_t+11
    teacher_kind="C" if variant.endswith("C") else "B"
    memory=mc if teacher_kind=="C" else mb
    teacher=tuple(v["teacher_C"] if teacher_kind=="C" else v["teacher_B"])
    world=make_initial(kernel,cell,"trained")
    schedule=defaultdict(list)
    reset_target=add(j,mb,reset_t-t0,n)
    schedule_arrival(schedule,reset_target,reset_t,3,eraser,29,cell["states"][3],cell["clocks"][3],n,"ordinary_reset")
    if not variant.startswith("no_retrain"):
        schedule_arrival(schedule,j,retrain_t,3,cue,cell["cue_sreg"],cell["states"][4],cell["clocks"][4],n,"retraining_cue")
        teacher_t=retrain_t+1 if variant.startswith("history_shuffled") else retrain_t
        schedule_arrival(schedule,j,teacher_t,3,teacher,cell["teacher_sreg"],cell["states"][5],cell["clocks"][5],n,"retraining_teacher")
    target=add(j,memory,tq-retrain_t,n)
    schedule_arrival(schedule,target,tq,4,cue,911,cell["states"][6],cell["clocks"][6],n,"post_retraining_probe")
    ports_empty=True; records={}
    for tick in range(tq+1):
        for spec in schedule[tick]:
            ports_empty = ports_empty and int(world.raw[spec["port"]]) == 0
            inject(world,spec)
        if tick==reset_t: records["reset"]=decode(world.raw,reset_target)
        if tick==retrain_t: records["retrain"]=decode(world.raw,j)
        if tick==tq: records["probe"]=decode(world.raw,target)
        if tick<tq: world.tick()
    rec=records.get("probe"); sm=min(cell["cue_sreg"]+cell["teacher_sreg"],19664)
    learned=rec is not None and rec["d"]==list(signsum(memory,cue)) and rec["sreg"]==min(sm+911,19664)
    neutral=rec is not None and rec["d"]==list(cue) and rec["sreg"]==911
    return {"frame":cell["frame"],"variant":variant,"ports_empty":ports_empty,"records":records,"learned":learned,"neutral":neutral}


def main():
    observed=hashlib.sha256(LOCK.read_bytes()).hexdigest()
    if observed != EXPECTED_LOCK_SHA256: raise RuntimeError(f"lock mismatch {observed}")
    lock=json.loads(LOCK.read_text(encoding="utf-8"))
    kernel,environment=verify_and_load_kernel(1)
    cells=[]
    for fi,(n,t0,frame,sregs,seed) in enumerate(zip(lock["domain"]["new_sizes"],lock["domain"]["train_ticks"],lock["domain"]["frames"],lock["parameters"]["training_sreg_by_frame"],lock["parameters"]["seeds"],strict=True)):
        rng=np.random.default_rng(seed)
        vectors={k:list(transform(v,frame["permutation"],frame["signs"])) for k,v in BASE.items()}
        cells.append({"frame":fi,"n":n,"train_tick":t0,"junction":[int(x) for x in rng.integers(10,n-10,size=3)],"vectors":vectors,"cue_sreg":sregs[0],"teacher_sreg":sregs[1],"states":[int(x) for x in rng.integers(1,2**32,size=7,dtype=np.uint64)],"clocks":[int(rng.bit_generator.random_raw()) for _ in range(7)]})
    transfers=[]
    for cell in cells:
        excluded={tuple(cell["vectors"][k]) for k in ("cue","teacher_B","memory_B")}
        queries=[q for q in itertools.product((-1,0,1),repeat=3) if q!=(0,0,0) and q not in excluded]
        if len(queries)!=23: raise RuntimeError("query class not 23")
        for qi,q in enumerate(queries):
            for mode in lock["parameters"]["core_modes"]:
                transfers.append(run_transfer(kernel,cell,q,qi,mode))
    reversals=[run_reversal(kernel,cell,variant) for cell in cells for variant in lock["parameters"]["reversal_variants"]]
    trained=[r for r in transfers if r["mode"]=="trained"]
    negatives=[r for r in transfers if r["mode"]!="trained"]
    postwrap=[r for r in trained if r["post_wrap"]]
    full_c=[r for r in reversals if r["variant"]=="full_C"]
    controls_c=[r for r in reversals if r["variant"] in {"no_retrain_C","history_shuffled_C"}]
    full_b=[r for r in reversals if r["variant"]=="full_B"]
    controls_b=[r for r in reversals if r["variant"]=="no_retrain_B"]
    exact_count=sum(r["trained_exact"] for r in trained); interval=wilson(exact_count,len(trained))
    rates={
        "unseen_transfer_exact":exact_count/len(trained),
        "negative_neutral":sum(r["neutral_exact"] for r in negatives)/len(negatives),
        "negative_false_transfer":sum(r["trained_exact"] for r in negatives)/len(negatives),
        "post_wrap_transfer_exact":sum(r["trained_exact"] for r in postwrap)/len(postwrap),
        "transfer_ports_empty":sum(r["port_empty"] for r in transfers)/len(transfers),
        "reversal_full_C":sum(r["learned"] for r in full_c)/len(full_c),
        "reversal_controls_neutral":sum(r["neutral"] for r in controls_c)/len(controls_c),
        "reacquisition_full_B":sum(r["learned"] for r in full_b)/len(full_b),
        "reacquisition_control_neutral":sum(r["neutral"] for r in controls_b)/len(controls_b),
        "reversal_ports_empty":sum(r["ports_empty"] for r in reversals)/len(reversals),
    }
    m=lock["minimum_relevance"]
    pass_conditions={
        "transfer":rates["unseen_transfer_exact"]>=m["unseen_transfer_exact_rate"],
        "every_transfer":all(r["trained_exact"] for r in trained),
        "every_frame":all(sum(r["trained_exact"] for r in trained if r["frame"]==fi)==23 for fi in range(3)),
        "wilson":interval[0]>=m["unseen_transfer_wilson_95_lower"],
        "negative_neutral":rates["negative_neutral"]>=m["negative_neutral_rate"],
        "negative_false":rates["negative_false_transfer"]<=m["negative_false_transfer_rate_max"],
        "post_wrap":rates["post_wrap_transfer_exact"]>=m["post_wrap_transfer_exact_rate"],
        "ports":rates["transfer_ports_empty"]>=m["ports_empty_rate"] and rates["reversal_ports_empty"]>=m["ports_empty_rate"],
        "reversal":rates["reversal_full_C"]>=m["reversal_full_C_rate"],
        "reversal_controls":rates["reversal_controls_neutral"]>=m["reversal_controls_neutral_rate"],
        "reacquisition":rates["reacquisition_full_B"]>=m["reacquisition_full_B_rate"],
        "reacquisition_control":rates["reacquisition_control_neutral"]>=m["reacquisition_control_neutral_rate"],
    }
    verdict="PASS" if all(pass_conditions.values()) else "FAIL"
    result={"schema":"dee.v27.core06.c6h02.v1","experiment_id":lock["hypothesis_id"],"role":"FROZEN_CONFIRMATION","lock_sha256":observed,"kernel_environment":environment,"sample_sizes":{"frames":3,"genuinely_unseen_queries":69,"transfer_worlds":len(transfers),"negative_worlds":len(negatives),"reversal_worlds":len(reversals)},"rates":rates,"unseen_transfer_wilson_95":interval,"pass_conditions":pass_conditions,"verdict":verdict,"cells":cells,"transfers":transfers,"reversals":reversals}
    result["content_sha256"]=canonical_hash(result); atomic_json(OUT,result)
    print(json.dumps({k:result[k] for k in ("sample_sizes","rates","unseen_transfer_wilson_95","pass_conditions","verdict")},indent=2,sort_keys=True))
    return 0 if verdict=="PASS" else 2


if __name__=="__main__": raise SystemExit(main())
