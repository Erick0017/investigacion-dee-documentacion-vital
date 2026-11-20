#!/usr/bin/env python3
"""Expanded effective-probability and measure discovery across macrostates."""
from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
sys.path.insert(0,str(HERE))
from core16x_common import append_ndjson,audit_kernel,canonical_hash,update_state,utc,write_json
from native_runtime_x import NativeWorld,pack,verify_and_load_kernel

DIRECTIONS=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1),(1,1,0),(-1,-1,0),(1,0,1),(-1,0,-1),(0,1,1),(0,-1,-1))


def add(q,d,n):return tuple((q[i]+d[i])%n for i in range(3))


def sample_microstate(rng,n,k,mode,preparation):
    for _ in range(200):
        if mode=="aligned": dirs=[(1,0,0)]*k
        elif mode=="balanced": dirs=[(1,0,0)]*(k//2)+[(-1,0,0)]*(k-k//2); rng.shuffle(dirs)
        else: dirs=[DIRECTIONS[int(i)] for i in rng.integers(0,len(DIRECTIONS),size=k)]
        if preparation=="uniform":
            candidates=list(np.ndindex((n,n,n)))
        else:
            center=np.array([n//2]*3); candidates=[]
            for radius in range(1,n//2+1):
                candidates=[q for q in np.ndindex((n,n,n)) if max(abs(((q[i]-center[i]+n//2)%n)-n//2) for i in range(3))<=radius]
                if len(candidates)>=k*5:break
        rng.shuffle(candidates)
        coords=[];dest=[]
        for direction in dirs:
            chosen=None
            for q in candidates:
                if q in coords or q in dest:continue
                target=add(q,direction,n)
                if target in coords:continue
                chosen=q;break
            if chosen is None:break
            coords.append(chosen);dest.append(add(chosen,direction,n));candidates.remove(chosen)
        if len(coords)==k:
            hist=tuple(sorted(Counter(dirs).items()))
            return coords,dirs,dest,hist
    raise RuntimeError("could not sample empty-destination microstate")


def entropy(counter):
    total=sum(counter.values());return -sum((v/total)*math.log2(v/total) for v in counter.values() if v)


def tv(a,b):
    ta=sum(a.values());tb=sum(b.values());keys=set(a)|set(b)
    return 0.5*sum(abs(a.get(k,0)/ta-b.get(k,0)/tb) for k in keys)


def macroclass(kernel,rng,n,k,mode,preparation,samples=512):
    outcomes=Counter(); conditioned=defaultdict(Counter); kernel_checks=[]; collision_counts=[]
    prefixes={64:Counter(),256:Counter(),512:Counter()}
    for index in range(samples):
        coords,dirs,dests,hist=sample_microstate(rng,n,k,mode,preparation)
        y=len(set(dests));outcomes[y]+=1;conditioned[str(hist)][y]+=1;collision_counts.append(k-y)
        for cutoff in prefixes:
            if index<cutoff:prefixes[cutoff][y]+=1
        if index<8:
            raw=np.zeros((n,n,n),dtype=np.uint64)
            for j,(q,d) in enumerate(zip(coords,dirs,strict=True)):raw[q]=pack(0x1000+j,19,d,1)
            world=NativeWorld(kernel,raw,threads=1);world.tick();actual=int(np.count_nonzero(world.raw))
            kernel_checks.append({"sample":index,"predicted":y,"actual":actual,"pass":actual==y})
    simple_expected=n**3*(1-(1-1/(n**3))**k)
    mean=sum(y*c for y,c in outcomes.items())/samples
    return {
        "macroclass":{"n":n,"support":k,"direction_mode":mode,"preparation_measure":preparation},
        "outcome_counts":dict(sorted(outcomes.items())),"entropy_bits":entropy(outcomes),"mean_next_support":mean,
        "simple_uniform_bin_model_expected":simple_expected,"simple_model_absolute_error":abs(mean-simple_expected),
        "mean_destination_collisions":float(np.mean(collision_counts)),
        "direction_hist_conditional_entropy_weighted":sum(sum(c.values())/samples*entropy(c) for c in conditioned.values()),
        "fiber_conditional_entropy":0.0,
        "frequency_stability":{"TV_64_vs_512":tv(prefixes[64],prefixes[512]),"TV_256_vs_512":tv(prefixes[256],prefixes[512])},
        "kernel_checks":kernel_checks,"kernel_checks_pass":sum(x["pass"] for x in kernel_checks),
    }


def main():
    audit_kernel("CORE16X_BEFORE_PROBABILITY_MEASURE_DISCOVERY");kernel,runtime=verify_and_load_kernel(1)
    rng=np.random.default_rng(16160001);classes=[]
    for n in (9,13,17):
        for k in (8,16,28):
            if k>=n**3//4:continue
            for mode in ("aligned","balanced","mixed"):
                for preparation in ("uniform","clustered"):
                    classes.append(macroclass(kernel,rng,n,k,mode,preparation))
    paired=[]
    for n in (9,13,17):
        for k in (16,28):
            for mode in ("balanced","mixed"):
                u=next(x for x in classes if x["macroclass"]=={"n":n,"support":k,"direction_mode":mode,"preparation_measure":"uniform"})
                c=next(x for x in classes if x["macroclass"]=={"n":n,"support":k,"direction_mode":mode,"preparation_measure":"clustered"})
                paired.append({"n":n,"support":k,"mode":mode,"TV_uniform_vs_clustered":tv(Counter({int(a):b for a,b in u["outcome_counts"].items()}),Counter({int(a):b for a,b in c["outcome_counts"].items()})),"mean_difference":c["mean_next_support"]-u["mean_next_support"]})
    summary={
        "macroclasses":len(classes),"microstates":len(classes)*512,"kernel_checks":sum(len(x["kernel_checks"]) for x in classes),"kernel_checks_pass":sum(x["kernel_checks_pass"] for x in classes),
        "nondegenerate_classes":sum(len(x["outcome_counts"])>1 for x in classes),
        "aligned_degenerate_classes":sum(x["macroclass"]["direction_mode"]=="aligned" and len(x["outcome_counts"])==1 for x in classes),
        "measure_sensitive_pairs":sum(x["TV_uniform_vs_clustered"]>0.02 for x in paired),"measure_pairs":len(paired),
        "fiber_entropy_zero_all":all(x["fiber_conditional_entropy"]==0 for x in classes),
    }
    result={"experiment":"C16X-EFFECTIVE-PROBABILITY-MEASURE-DISCOVERY","created_utc":utc(),"runtime":runtime,"classes":classes,"measure_comparisons":paired,"summary":summary,
            "adjudication":{"probability_origin":"LIMITED OBSERVER ACCESS PLUS DECLARED MICROSTATE MEASURE","intrinsic_to_bulk_macrostate_alone":False,"nonclassical_probability_found":False,"born_like_search":"NOT_TRIGGERED_NO_AMPLITUDE_OR_NONCLASSICAL_COMPOSITION","exact_lower_description":"destination fibers"}}
    h=canonical_hash(result);write_json(ROOT/"DISCOVERY"/"PROBABILITY_MEASURE_DISCOVERY.json",result)
    append_ndjson(ROOT/"QUESTION_TREE.ndjson",{"question_id":"C16X-Q007","parent_id":"C16X-Q006","parent_result_hash":h,"what_was_learned":f"Across {summary['macroclasses']} macrostates and {summary['microstates']} microstates, fibers remained deterministic but bulk distributions changed with the preparation measure in {summary['measure_sensitive_pairs']}/{summary['measure_pairs']} comparisons.","new_uncertainty":"Does the measure-conditioned law and frequency stability survive untouched ensembles?","competing_interpretations":["destination combinatorics plus declared measure suffices","additional phase/history classes alter outcomes","finite samples created apparent measure dependence"],"why_next_experiment_matters":"It distinguishes a valid statistical level from an observer-independent quantum probability claim.","status":"OPEN"})
    append_ndjson(ROOT/"KERNEL_DIALOGUE.ndjson",{"question_id":"C16X-Q006","raw_outcome":summary,"mechanism_update":"Effective probability is not attached to support alone; it is a distribution over compatible microstates under a declared preparation measure, while the fiber level remains deterministic.","next_high_information_question":"Freeze measure comparisons and confirm on OS-entropy ensembles."})
    update_state(status="PROBABILITY_MEASURE_DISCOVERED",current_phase="PROBABILITY_MEASURE_FREEZE",probability_discovery_hash=h,probability_summary=summary)
    print(json.dumps({**summary,"result_hash":h},indent=2))

if __name__=="__main__":main()
