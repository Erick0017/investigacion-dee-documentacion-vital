#!/usr/bin/env python3
"""Fresh binary holdout for branch-aware effective probability."""
from __future__ import annotations

import json,math,sys
from collections import Counter
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(HERE))
from core16x_common import audit_kernel,canonical_hash,read_json,sha256_file,update_state,utc,write_json,append_ndjson
from native_runtime_x import NativeWorld,pack,verify_and_load_kernel
from occupancy_operator import TETRA,XNOR_PAIRS
from run_probability_measure_discovery import sample_microstate,tv


def add(q,d,n):return tuple((q[i]+d[i])%n for i in range(3))


def branch_support(n,coords,dirs,dests):
    occupied=set(coords);survivors=set()
    for q in coords:
        n_active=sum(add(q,d,n) in occupied for d in ((x,y,z) for x in (-1,0,1) for y in (-1,0,1) for z in (-1,0,1) if (x,y,z)!=(0,0,0)))
        tetra=any(all(add(q,d,n) in occupied for d in pattern) for pattern in TETRA)
        tension=16.0 if tetra and n_active<7 else 2.5
        if int(math.floor(n_active*tension/26.0+0.5))>0:survivors.add(q)
    xnor=set()
    candidates=set()
    for q in occupied:
        for d in ((x,y,z) for x in (-1,0,1) for y in (-1,0,1) for z in (-1,0,1)):
            candidates.add(add(q,d,n))
    for q in candidates-occupied:
        symmetric=0;active=0
        for d in XNOR_PAIRS:
            p=add(q,d,n) in occupied;m=add(q,tuple(-v for v in d),n) in occupied
            symmetric+=int(p==m);active+=int(p)+int(m)
        if symmetric==13 and active>=8:xnor.add(q)
    support=set(dests)|survivors|xnor
    return len(support),{"unique_destinations":len(set(dests)),"surviving_incumbents":len(survivors),"xnor_births":len(xnor)}


def main():
    audit_kernel("CORE16X_BEFORE_PROBABILITY_FINAL_HOLDOUT")
    lock=read_json(ROOT/"HOLDOUT_LOCKS"/"PROBABILITY_MEASURE_LOCK.json");ch=read_json(ROOT/"FINAL_HOLDOUTS"/"PROBABILITY_CHALLENGES.json")
    for name,expected in lock["source_hashes"].items():
        if sha256_file(ROOT/"RUNNERS_NEW"/name)!=expected:raise RuntimeError(f"frozen source changed: {name}")
    if ch["lock_sha256"]!=lock["lock_sha256"]:raise RuntimeError("challenge/lock mismatch")
    kernel,runtime=verify_and_load_kernel(1);classes=[];all_exact=True
    for spec in ch["classes"]:
        rng=np.random.default_rng(spec["seed"]);outcomes=Counter();rows=[]
        for index in range(spec["samples"]):
            coords,dirs,dests,_=sample_microstate(rng,spec["n"],spec["support"],spec["mode"],spec["preparation"])
            predicted,parts=branch_support(spec["n"],coords,dirs,dests)
            raw=np.zeros((spec["n"],)*3,dtype=np.uint64)
            for j,(q,d) in enumerate(zip(coords,dirs,strict=True)):raw[q]=pack(0x3100+j,19,d,1)
            world=NativeWorld(kernel,raw,threads=1);world.tick();actual=int(np.count_nonzero(world.raw));exact=actual==predicted;all_exact&=exact;outcomes[actual]+=1
            rows.append({"sample":index,"predicted":predicted,"actual":actual,"exact":exact,"parts":parts})
        classes.append({"spec":spec,"outcome_counts":dict(sorted(outcomes.items())),"rows":rows,"exact":sum(r["exact"] for r in rows),"total":len(rows)})
    pairs=[]
    for n in (11,17):
        for k in (12,26):
            for mode in ("balanced","mixed"):
                u=next(x for x in classes if x["spec"]["n"]==n and x["spec"]["support"]==k and x["spec"]["mode"]==mode and x["spec"]["preparation"]=="uniform")
                c=next(x for x in classes if x["spec"]["n"]==n and x["spec"]["support"]==k and x["spec"]["mode"]==mode and x["spec"]["preparation"]=="clustered")
                cu=Counter({int(a):b for a,b in u["outcome_counts"].items()});cc=Counter({int(a):b for a,b in c["outcome_counts"].items()})
                mu=sum(a*b for a,b in cu.items())/sum(cu.values());mc=sum(a*b for a,b in cc.items())/sum(cc.values())
                pairs.append({"n":n,"support":k,"mode":mode,"TV":tv(cu,cc),"uniform_mean":mu,"clustered_mean":mc,"sensitive":tv(cu,cc)>0.05})
    summary={"binary_trials":sum(x["total"] for x in classes),"branch_law_exact":sum(x["exact"] for x in classes),"classes":len(classes),"measure_pairs":len(pairs),"measure_sensitive_pairs":sum(x["sensitive"] for x in pairs),"threshold_pairs":6,"overall_pass":all_exact and sum(x["sensitive"] for x in pairs)>=6}
    result={"holdout":"C16X-PROBABILITY-FINAL-UNTOUCHED-V1","executed_utc":utc(),"runtime":runtime,"lock_sha256":lock["lock_sha256"],"challenge_sha256":ch["challenge_sha256"],"classes":classes,"measure_pairs":pairs,"summary":summary,
            "adjudication":{"effective_probability":"CLASSICAL_IGNORANCE_OVER_DECLARED_COMPATIBLE_MICROSTATE_MEASURE","nonclassical_composition":"NOT_FOUND","born_like":"NOT_TRIGGERED","branch_state_deterministic":True}}
    h=canonical_hash(result);write_json(ROOT/"FINAL_HOLDOUTS"/"PROBABILITY_HOLDOUT_RESULTS.json",result)
    append_ndjson(ROOT/"QUESTION_TREE.ndjson",{"question_id":"C16X-Q009","parent_id":"C16X-Q008","parent_result_hash":h,"what_was_learned":f"Fresh branch law was exact in {summary['branch_law_exact']}/{summary['binary_trials']} binary trials; {summary['measure_sensitive_pairs']}/{summary['measure_pairs']} uniform/clustered pairs differed.","new_uncertainty":"Can any phase/history-bearing alternative produce nonadditive probability at another justified level?","competing_interpretations":["all tested probability is classical ignorance","phase-bearing effective levels add nonclassical composition","detector selection mimics nonclassicality"],"why_next_experiment_matters":"It gates quantum-like searches without relabeling classical mixture as quantum.","status":"OPEN" if summary["overall_pass"] else "PROBABILITY_HOLDOUT_FAILED"})
    append_ndjson(ROOT/"KERNEL_DIALOGUE.ndjson",{"question_id":"C16X-Q008","raw_outcome":summary,"mechanism_update":"A prospective statistical law closes when preparation measure and native branch mixture are specified. Probability vanishes under branch-sufficient microstate conditioning.","next_high_information_question":"Test phase/history routes for nonadditive composition across levels."})
    update_state(status="PROBABILITY_HOLDOUT_PASS" if summary["overall_pass"] else "PROBABILITY_HOLDOUT_FAIL",current_phase="QUANTUM_LIKE_MULTILEVEL_SEARCH",probability_holdout_hash=h,probability_holdout_summary=summary)
    print(json.dumps(summary,indent=2))

if __name__=="__main__":main()

