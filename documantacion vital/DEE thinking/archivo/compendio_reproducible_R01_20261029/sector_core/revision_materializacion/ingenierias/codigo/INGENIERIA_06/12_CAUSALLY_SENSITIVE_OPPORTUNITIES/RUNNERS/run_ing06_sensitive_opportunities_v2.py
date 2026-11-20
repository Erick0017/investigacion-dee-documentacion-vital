#!/usr/bin/env python3
"""Causal correction V2: toroidally equivalent, future-relevant opportunities."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent; BLOCK=HERE.parent; ROOT=BLOCK.parent; ENGINEERING=ROOT.parent
sys.path[:0]=[str(HERE),str(ENGINEERING/"INGENIERIA_05_HISTORY_CONDITIONED_TRANSFORMATION"/"RUNNERS"),str(ENGINEERING/"INGENIERIA_05_HISTORY_SPECIFICITY"/"RUNNERS")]
import run_ing06_sensitive_opportunities as v1  # noqa: E402
import run_nrd05_history_conditioned_transformation as nrd05  # noqa: E402
import run_nrd06_history_specificity as nrd06  # noqa: E402

N=39; ORIGIN=(19,6,19); OFFSETS=(0,16,32,64,128,256); HORIZONS=(32,64)
OPPORTUNITIES={"P1":(-13,13,0),"P2":(0,13,0),"P3":(13,13,0)}
GLOBAL=v1.GLOBAL; HISTORIES={"H0":None,"HA":"AB","HB":"BA"}

def make_world(kernel,configuration,history,omit=None):
    spec=GLOBAL[configuration]; raw=np.zeros((N,N,N),np.uint64); clock=np.zeros_like(raw)
    if HISTORIES[history] is not None:
        cfg={"n":N,"origin":ORIGIN,"permutation":spec[0],"signs":spec[1],"mode":HISTORIES[history],"event_sreg":0}
        central,_=nrd05.construct(kernel,cfg); v1.merge_instance(raw,clock,central)
    for name,offset in OPPORTUNITIES.items():
        if name==omit: continue
        moved=nrd05.transform(offset,spec[0],spec[1]); center=tuple((ORIGIN[i]+moved[i])%N for i in range(3))
        cfg={"n":N,"origin":center,"permutation":spec[0],"signs":spec[1],"mode":"AB","event_sreg":0}
        apparatus,_=nrd05.construct(kernel,cfg); v1.merge_instance(raw,clock,apparatus)
    return nrd05.NativeWorld(kernel,raw,clock)

def free_future(kernel,state):
    world=nrd05.NativeWorld(kernel,state[0],state[1]); out={}
    for tick in range(1,65):
        world.tick()
        if tick in HORIZONS: out[tick]=nrd05.checkpoint(world)
    return out

def relation(kernel,full,omitted):
    ff,fo=free_future(kernel,full),free_future(kernel,omitted)
    vectors=[v1.raw_signature(full,omitted)]+[v1.raw_signature(ff[h],fo[h]) for h in HORIZONS]
    return {"fingerprint":hashlib.sha256(json.dumps(vectors,separators=(",", ":")).encode()).hexdigest(),"vectors":vectors,"future_relevant":any(any(x) for x in vectors[1:])}

def observe(kernel,states):
    relations={p:relation(kernel,states["FULL"],states[f"OMIT_{p}"]) for p in OPPORTUNITIES}
    pattern=[relations[p]["fingerprint"] for p in OPPORTUNITIES]
    return {"relations":relations,"equivalent":len(set(pattern))==1,"all_future_relevant":all(x["future_relevant"] for x in relations.values()),"pattern":pattern}

def checkpoints(branches): return {name:nrd05.checkpoint(world) for name,world in branches.items()}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--threads",type=int,default=1); args=parser.parse_args()
    kernel,runtime=nrd05.load_kernel(args.threads); gates={}; telemetry={}
    for config in GLOBAL:
        branches={"FULL":make_world(kernel,config,"H0"),**{f"OMIT_{p}":make_world(kernel,config,"H0",p) for p in OPPORTUNITIES}}
        nrd06.tick_all(branches,4); gates[config]=observe(kernel,checkpoints(branches))
    gate_pass=all(x["equivalent"] and x["all_future_relevant"] for x in gates.values())
    if not gate_pass:
        result=nrd05.seal({"experiment_id":"ING06_SENSITIVE_OPPORTUNITIES_V2","status":"SENSITIVITY_OR_EQUIVALENCE_GATE_FAILED","runtime":runtime,"gates":gates,"history_stage_executed":False,"formal_RW3":False,"L4":False})
        nrd05.write_json(BLOCK/"RESULTS"/"ING06_SENSITIVE_OPPORTUNITIES_V2.json",result)
        print(json.dumps({"status":result["status"],"gates":{k:{"equivalent":x["equivalent"],"all_future_relevant":x["all_future_relevant"]} for k,x in gates.items()}},indent=2)); return
    cases={}
    for config in GLOBAL:
        worlds={h:{"FULL":make_world(kernel,config,h),**{f"OMIT_{p}":make_world(kernel,config,h,p) for p in OPPORTUNITIES}} for h in HISTORIES}
        flat={f"{h}_{b}":w for h,bs in worlds.items() for b,w in bs.items()}; nrd06.tick_all(flat,4); elapsed=0; rows={}
        for offset in OFFSETS:
            nrd06.tick_all(flat,offset-elapsed); elapsed=offset; rows[str(offset)]={}
            for history,branches in worlds.items():
                states=checkpoints(branches)
                for branch,state in states.items(): telemetry[f"{config}_T{offset}_{history}_{branch}_raw_a"]=state[0]; telemetry[f"{config}_T{offset}_{history}_{branch}_clock_a"]=state[1]
                rows[str(offset)][history]=observe(kernel,states)
            rows[str(offset)]["HA_HB_patterns_different"]=rows[str(offset)]["HA"]["pattern"]!=rows[str(offset)]["HB"]["pattern"]
        positives=[]
        for i,offset in enumerate(OFFSETS[:-2]):
            window=OFFSETS[i:i+3]
            if all(rows[str(t)]["H0"]["equivalent"] and rows[str(t)]["H0"]["all_future_relevant"] and not rows[str(t)]["HA"]["equivalent"] and not rows[str(t)]["HB"]["equivalent"] and rows[str(t)]["HA_HB_patterns_different"] and rows[str(t)]["HA"]["all_future_relevant"] and rows[str(t)]["HB"]["all_future_relevant"] for t in window): positives.append(offset)
        cases[config]={"observations":rows,"persistent_positive_window_starts":positives,"pass":bool(positives)}
    replicated=all(x["pass"] for x in cases.values()); status="HISTORY_CONDITIONED_EQUIVALENCE_BREAKING" if replicated else "NO_EQUIVALENCE_BREAK_OBSERVED_WITH_SENSITIVE_OPPORTUNITIES"
    np.savez_compressed(BLOCK/"TELEMETRY"/"ING06_SENSITIVE_OPPORTUNITIES_V2.npz",**telemetry)
    result=nrd05.seal({"experiment_id":"ING06_SENSITIVE_OPPORTUNITIES_V2","status":status,"runtime":runtime,"gates":gates,"history_stage_executed":True,"cases":cases,"fresh_replication":replicated,"main_world_interventions_after_host_stop":0,"new_unpreloaded_contingency_demonstrated":False,"formal_RW3":False,"L4":False,"telemetry":"TELEMETRY/ING06_SENSITIVE_OPPORTUNITIES_V2.npz"})
    nrd05.write_json(BLOCK/"RESULTS"/"ING06_SENSITIVE_OPPORTUNITIES_V2.json",result)
    print(json.dumps({"status":status,"gates":{k:{"equivalent":x["equivalent"],"all_future_relevant":x["all_future_relevant"]} for k,x in gates.items()},"passes":{k:x["pass"] for k,x in cases.items()}},indent=2))

if __name__=="__main__": main()
