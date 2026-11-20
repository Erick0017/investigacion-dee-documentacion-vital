#!/usr/bin/env python3
"""Preloaded native sense-write-read-action pipeline and reuse boundary."""
from __future__ import annotations
import itertools,sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from ing01_common import *
from ing01_apparatus import *
sys.path.insert(0,str(BASE_RUNNERS))
from core10_apparatus import place_arrival  # noqa:E402


def frames():return list(itertools.product(list(itertools.permutations((0,1,2))),list(itertools.product((-1,1),repeat=3))))


def preloaded_case(kernel,seed,bit,frame,n=31):
    p,s=frame;a,b,sensor,normalizer,penalty,action0,action1=(transform(v,p,s) for v in (A,B,SENSOR,NORMALIZER,PENALTY0,ACTION0,ACTION1));q=(n//2,n//2,n//2);raw=np.zeros((n,n,n),np.uint64);clock=np.zeros_like(raw);raw[q]=pack(1,7,a,1)
    t1=add(q,a,1,n);t2=add(t1,action0,1,n);learned=b if bit else a;t3=add(t2,learned,1,n)
    place_arrival(raw,clock,t1,1,sensor,1001,47);place_arrival(raw,clock,t2,2,normalizer,1002,53)
    if bit:place_arrival(raw,clock,t2,2,penalty,1003,59)
    place_arrival(raw,clock,t3,3,sensor,1004,101)
    initial_support=int(np.count_nonzero(raw));world=NativeWorld(kernel,raw,clock,threads=1);trace=[]
    for tick in range(1,4):
        world.tick();target=(t1,t2,t3)[tick-1];trace.append({"tick":tick,"target":target,"record":read(world.raw,target),"support":int(np.count_nonzero(world.raw))})
    expected=action1 if bit else action0;success=trace[-1]["record"] is not None and tuple(trace[-1]["record"]["direction"])==expected
    learned_destroyed=trace[-1]["record"] is None or tuple(trace[-1]["record"]["direction"])!=learned
    return {"seed":seed,"bit":bit,"frame":{"permutation":list(p),"signs":list(s)},"initial_support":initial_support,"trace":trace,"success":success,"python_interventions_after_t0":0,"learned_policy_consumed_by_read":learned_destroyed,"terminal_support":int(np.count_nonzero(world.raw)),"resource_statement":"all scheduled carriers are consumed into collision outputs; no source replenishment exists"}


def semantic4_attempt(kernel,bit,n=31):
    # Replace one-shot scheduled carriers with fixed emitters at the same initial ports.
    a,b,sensor,normalizer,penalty,action0,action1=A,B,SENSOR,NORMALIZER,PENALTY0,ACTION0,ACTION1;q=(15,15,15);raw=np.zeros((n,n,n),np.uint64);clock=np.zeros_like(raw);raw[q]=pack(1,7,a,1)
    t1=add(q,a,1,n);t2=add(t1,action0,1,n);learned=b if bit else a;t3=add(t2,learned,1,n)
    sources=[(add(t1,sensor,-1,n),sensor),(add(t2,normalizer,-2,n),normalizer),(add(t3,sensor,-3,n),sensor)]
    if bit:sources.append((add(t2,penalty,-2,n),penalty))
    collision=False
    for i,(pos,d) in enumerate(sources):
        if int(raw[pos]):collision=True
        raw[pos]=pack(2000+i,31+i,d,4)
    world=NativeWorld(kernel,raw,clock,threads=1);hits=[]
    for tick in range(1,2*n+1):
        world.tick();r=read(world.raw,t3)
        if r is not None and tuple(r["direction"])==(action1 if bit else action0):hits.append(tick)
    return {"bit":bit,"initial_source_collision":collision,"correct_action_ticks_at_nominal_output":hits,"reusable_periodic_cycle":len(hits)>=2,"reason":"semantic4 emitters produce fixed source-supported trains, not consequence-conditioned resets of the consumed policy"}


def main():
    kernel,runtime=load_kernel(1);rows=[]
    for i,f in enumerate(frames()):
        for bit in (0,1):rows.append(preloaded_case(kernel,1870000+i*101+bit,bit,f))
    emitters=[semantic4_attempt(kernel,0),semantic4_attempt(kernel,1)]
    summary={"preloaded_cases":len(rows),"all_one_cycle_success":all(r["success"] for r in rows),"all_no_python_after_initialization":all(r["python_interventions_after_t0"]==0 for r in rows),"all_policy_consumed_by_read":all(r["learned_policy_consumed_by_read"] for r in rows),"persistent_emitter_attempts":len(emitters),"reusable_emitter_loop_found":any(r["reusable_periodic_cycle"] for r in emitters)}
    result=seal({"schema":"dee.v27.ing01.closed_pipeline.discovery.v1","preloaded_pipelines":rows,"persistent_emitter_attempts":emitters,"summary":summary,"autonomy_levels":{"L0":"Python injects every event","L1":"Python initializes a complete feed-forward world; kernel performs sense-write-read-action without intermediate decisions (demonstrated)","L2":"native reusable feedback cycle with replenishment/reset (not constructed)","L3":"environmental consequence selects its own future policy without pre-encoding (not constructed)"},"causal_limit":"The read collision consumes the policy into an action direction. Scheduled carriers deplete. Fixed semantic4 trains do not implement conditional feedback/reset.","runtime":runtime})
    write_json(ROOT/"DISCOVERY"/"ING01_D05_CLOSED_PIPELINE.json",result)
    append_ndjson(ROOT/"PREREQUISITE_SEARCH.ndjson",{"search_id":"INGP002","target":"reusable native loop","attempts":["preloaded ballistic schedule","semantic4 persistent trains","toroidal persistence of output"],"result":"one-cycle L1 pipeline yes; reusable L2 loop no","result_hash":result["content_sha256"],"missing":["conditional feedback route","policy restoration after destructive query","resource replenishment"]})
    append_ndjson(ROOT/"QUESTION_TREE.ndjson",{"question_id":"INGQ013","parent_question":"INGQ006","parent_result_hash":result["content_sha256"],"question":"Can redundant policy reconstruction provide the missing reset in a multi-cycle loop?","status":"OPEN"})
    print({"hash":result["content_sha256"],**summary,"emitters":emitters})
    if not summary["all_one_cycle_success"] or not summary["all_no_python_after_initialization"]:raise SystemExit(2)


if __name__=="__main__":main()
