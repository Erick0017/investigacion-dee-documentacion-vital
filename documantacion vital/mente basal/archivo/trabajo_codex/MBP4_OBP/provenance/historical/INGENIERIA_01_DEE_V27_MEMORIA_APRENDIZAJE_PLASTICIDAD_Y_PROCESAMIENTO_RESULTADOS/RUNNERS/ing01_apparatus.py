#!/usr/bin/env python3
"""Minimal native policy-memory apparatus for INGENIERIA 01."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent; sys.path.insert(0,str(HERE))
from ing01_common import BASE_RUNNERS
sys.path.insert(0,str(BASE_RUNNERS))
from core10_apparatus import A,B,SENSOR,NORMALIZER,PENALTY0,ACTION0,ACTION1,NativeWorld,add,inject_arrival,pack,read,transform  # noqa:E402


def sign_sum(*vectors):
    sums=[sum(v[i] for v in vectors) for i in range(3)]
    return tuple(1 if x>0 else -1 if x<0 else 0 for x in sums)


def compact_learning_cycle(kernel,seed:int,bit:int,permutation=(0,1,2),signs=(1,1,1),n=11,query=True):
    rng=np.random.default_rng(seed); raw=np.zeros((n,n,n),np.uint64); clock=np.zeros_like(raw); world=NativeWorld(kernel,raw,clock,threads=1)
    a,b,sensor,normalizer,penalty,action0,action1=(transform(v,permutation,signs) for v in (A,B,SENSOR,NORMALIZER,PENALTY0,ACTION0,ACTION1))
    q=tuple(int(x) for x in rng.integers(3,n-3,size=3)); initial=pack(1000+seed%100000,7,a,1); world.raw_a[q]=initial; world.raw_b[q]=initial; world.clock_a[q]=np.uint64(2000+seed); world.clock_b[q]=world.clock_a[q]
    target1=add(q,a,1,n)
    port1=add(target1,sensor,-1,n)
    if int(world.raw_a[port1]):
        raise RuntimeError(f"pre-injection collision seed={seed} permutation={permutation} signs={signs} q={q} a={a} sensor={sensor} target={target1} port={port1}")
    inject_arrival(world,target1,sensor,47,3000+seed,4000+seed); world.tick(); r1=read(world.raw,target1)
    expected1=action0; target2=add(target1,expected1,1,n); inject_arrival(world,target2,normalizer,53,5000+seed,6000+seed)
    if bit: inject_arrival(world,target2,penalty,59,7000+seed,8000+seed)
    world.tick(); r2=read(world.raw,target2); learned=b if bit else a
    result={"seed":seed,"bit":bit,"n":n,"frame":{"permutation":list(permutation),"signs":list(signs)},"coordinates":{"q0":q,"after_experience":target1,"after_consequence":target2},"records":{"initial":read(np.asarray([initial],dtype=np.uint64),(0,)) if False else {"raw":int(initial)},"after_experience":r1,"after_consequence":r2},"expected":{"after_experience_direction":list(expected1),"learned_direction":list(learned)},"write_correct":r1 is not None and tuple(r1["direction"])==expected1 and r2 is not None and tuple(r2["direction"])==learned,"write_ticks":2}
    if query:
        target3=add(target2,learned,1,n); inject_arrival(world,target3,sensor,101,9000+seed,10000+seed); world.tick(); rq=read(world.raw,target3); expectedq=action1 if bit else action0
        result.update({"query_coordinate":target3,"query_record":rq,"expected_query_direction":list(expectedq),"read_correct":rq is not None and tuple(rq["direction"])==expectedq,"read_ticks":1})
    return result


def direct_overwrite_tick(world,current_q,current_direction,writer_direction,sreg,state,clock):
    target=add(current_q,current_direction,1,world.n); inject_arrival(world,target,writer_direction,sreg,state,clock); world.tick(); return target,read(world.raw,target)
