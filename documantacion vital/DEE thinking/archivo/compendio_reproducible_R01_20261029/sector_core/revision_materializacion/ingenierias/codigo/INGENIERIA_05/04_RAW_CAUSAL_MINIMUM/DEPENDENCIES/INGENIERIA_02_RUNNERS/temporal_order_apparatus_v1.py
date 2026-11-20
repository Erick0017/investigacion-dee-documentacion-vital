#!/usr/bin/env python3
"""Experience-written AB/BA temporal order in paired relative memory."""
from __future__ import annotations

import numpy as np

from ing02_common import NativeWorld, add, pack, read, summarize, transform
from run_d09_relative_readout_longevity import PATTERN_A, PATTERN_B


def put(raw,clock,q,state,sreg,direction=(0,0,0),semantic=1,phase=0):
    if int(raw[q]):raise RuntimeError(f"overlap at {q}: {read(raw,q)}")
    raw[q]=pack(state,sreg,direction,semantic);clock[q]=np.uint64(phase)


def install_event(raw,clock,memory,target_offset,direction,when,n,state_base,sreg=3):
    target=add(memory,target_offset,1,n)
    if when=="early":
        put(raw,clock,target,state_base,sreg,direction,1,17)
        return target
    if when=="late":
        source=add(target,direction,-1,n)
        # state0 routes at tick1 without entering the active count at tick0.
        put(raw,clock,source,0,sreg,direction,1,19)
        return source
    raise ValueError(when)


def construct(kernel,challenge):
    n=int(challenge.get("n",23));c=tuple(challenge.get("origin",(n//2,)*3));mode=challenge.get("mode","AB")
    permutation=tuple(challenge.get("permutation",(0,1,2)));signs=tuple(challenge.get("signs",(1,1,1)))
    tf=lambda v:transform(v,permutation,signs)
    axis=tf((1,0,0));a=add(c,tf((-1,0,0)),1,n);b=add(c,axis,1,n)
    raw=np.zeros((n,n,n),np.uint64);clock=np.zeros_like(raw)
    put(raw,clock,a,1000,100,(0,0,0),1,260);put(raw,clock,b,2000,100,(0,0,0),1,260)
    for i,o in enumerate(PATTERN_A):put(raw,clock,add(a,tf(o),1,n),3000+i,0,(0,0,0),4,31+i)
    for i,o in enumerate(PATTERN_B):put(raw,clock,add(b,tf(o),1,n),4000+i,0,(0,0,0),4,41+i)
    schedule={
        "AB":("early","late"),"BA":("late","early"),
        "simultaneous_early":("early","early"),"simultaneous_late":("late","late"),
        "no_events":(None,None),"route_cut":("early","late"),"finite_reader":("early","late"),
    }[mode]
    event_sources=[]
    event_sreg=int(challenge.get("event_sreg",3))
    if schedule[0]:event_sources.append(install_event(raw,clock,a,tf((0,-1,0)),tf((0,0,-1)),schedule[0],n,5000,event_sreg))
    if schedule[1]:event_sources.append(install_event(raw,clock,b,tf((0,1,0)),tf((0,0,1)),schedule[1],n,5001,event_sreg))
    reader_source=add(c,tf((0,-2,0)),1,n)
    if mode!="route_cut":put(raw,clock,reader_source,6000,7,tf((0,1,0)),1 if mode=="finite_reader" else 4,23)
    return NativeWorld(kernel,raw,clock),{"a":a,"b":b,"comparator":c,"reader_source":reader_source,"event_sources":event_sources,"axis":axis}


def run_case(kernel,challenge):
    world,ports=construct(kernel,challenge);h=int(challenge.get("horizon",128));trace=[]
    source0=int(world.raw[ports["reader_source"]]) if challenge.get("mode")!="route_cut" else 0;source_fixed=True
    for tick in range(1,h+1):
        info=world.tick();a,b,c=(read(world.raw,ports[k]) for k in ("a","b","comparator"))
        if challenge.get("mode")!="route_cut" and int(world.raw[ports["reader_source"]])!=source0:source_fixed=False
        if tick<=12 or tick in {16,32,64,128}:
            trace.append({"tick":tick,"a":a,"b":b,"delta":None if a is None or b is None else a["sreg"]-b["sreg"],
                "comparator":c,"x":None if c is None else c["direction"][0],
                "axis_projection":None if c is None else sum(c["direction"][i]*ports["axis"][i] for i in range(3)),
                "support":int(np.count_nonzero(world.raw)),
                "kernel":{str(k):int(v) if isinstance(v,(int,np.integer)) else v for k,v in info.items()}})
    return {"challenge_id":challenge.get("challenge_id"),"n":world.n,"mode":challenge.get("mode"),"horizon":h,
        "ports":{k:[list(q) for q in v] if k=="event_sources" else list(v) for k,v in ports.items()},
        "source_raw_fixed":source_fixed if challenge.get("mode")!="route_cut" else None,
        "trace":trace,"terminal":summarize(world.raw,world.clock_a),"python_interventions_after_t0":0}
