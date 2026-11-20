#!/usr/bin/env python3
"""Result-derived refinement of clustered probability failures by native branch."""
from __future__ import annotations

import json,sys
from collections import Counter
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(HERE))
from core16x_common import append_ndjson,audit_kernel,canonical_hash,read_json,update_state,utc,write_json
from native_runtime_x import NativeWorld,pack,verify_and_load_kernel
from occupancy_operator import predict_tick,unpack
from run_probability_measure_discovery import sample_microstate


def trial(kernel,rng,n,k,mode,index):
    coords,dirs,dests,_=sample_microstate(rng,n,k,mode,"clustered")
    raw=np.zeros((n,n,n),dtype=np.uint64);clock=np.zeros_like(raw)
    for j,(q,d) in enumerate(zip(coords,dirs,strict=True)):raw[q]=pack(0x2000+j,19,d,1)
    predicted,_,diagnostics,_=predict_tick(raw,clock)
    world=NativeWorld(kernel,raw,clock,1);world.tick();actual=world.raw
    branch_occupied=Counter()
    for q,diag in diagnostics.items():
        if int(predicted[q])!=0:branch_occupied[diag["branch"]]+=1
    unique_dest=len(set(dests))
    xnor=branch_occupied["EMPTY_XNOR_BIRTH"]
    surviving=branch_occupied["INCUMBENT_MATTER_RULE"]
    incoming=branch_occupied["EMPTY_INCOMING_REDUCER"]
    models={
        "M1_unique_destinations":unique_dest,
        "M2_destinations_plus_XNOR":unique_dest+xnor,
        "M3_destinations_plus_surviving_incumbents":unique_dest+surviving,
        "M4_branch_union":int(np.count_nonzero(predicted)),
    }
    actual_support=int(np.count_nonzero(actual))
    return {"case":index,"n":n,"support":k,"mode":mode,"unique_destinations":unique_dest,"branch_occupied":dict(branch_occupied),"models":models,"actual_support":actual_support,"operator_support":int(np.count_nonzero(predicted)),"operator_raw_exact":bool(np.array_equal(predicted,actual)),"model_exact":{name:value==actual_support for name,value in models.items()}}


def main():
    audit_kernel("CORE16X_BEFORE_PROBABILITY_BRANCH_REFINEMENT");kernel,runtime=verify_and_load_kernel(1)
    parent=read_json(ROOT/"DISCOVERY"/"PROBABILITY_MEASURE_DISCOVERY.json");parent_hash=canonical_hash(parent)
    rows=[];rng=np.random.default_rng(16160808)
    for n in (9,13,17):
        for k in (16,28):
            for mode in ("aligned","balanced","mixed"):
                for i in range(24):rows.append(trial(kernel,rng,n,k,mode,len(rows)))
    scores={name:sum(row["model_exact"][name] for row in rows) for name in rows[0]["models"]}
    summary={"trials":len(rows),"operator_raw_exact":sum(r["operator_raw_exact"] for r in rows),"model_exact_scores":scores,
             "trials_with_XNOR":sum(r["branch_occupied"].get("EMPTY_XNOR_BIRTH",0)>0 for r in rows),
             "trials_with_surviving_incumbent":sum(r["branch_occupied"].get("INCUMBENT_MATTER_RULE",0)>0 for r in rows),
             "fiber_only_failures":sum(not r["model_exact"]["M1_unique_destinations"] for r in rows)}
    result={"experiment":"C16X-PROBABILITY-BRANCH-REFINEMENT","created_utc":utc(),"parent_result_hash":parent_hash,"runtime":runtime,"rows":rows,"summary":summary,
            "adjudication":"Clustered ensembles do not merely reweight destination collisions; they change the mixture of executed native branches. Effective probabilities require preparation measure plus branch-sufficient local state."}
    h=canonical_hash(result);write_json(ROOT/"MODEL_SELECTION"/"PROBABILITY_BRANCH_REFINEMENT.json",result)
    append_ndjson(ROOT/"QUESTION_TREE.ndjson",{"question_id":"C16X-Q008","parent_id":"C16X-Q007","parent_result_hash":h,"what_was_learned":f"Fiber-only failed {summary['fiber_only_failures']}/{summary['trials']} clustered trials; the full branch union matched {scores['M4_branch_union']}/{summary['trials']} and raw {summary['operator_raw_exact']}/{summary['trials']}.","new_uncertainty":"Can the branch-sufficient statistical law predict untouched preparation measures and scales?","competing_interpretations":["local branch mixture is sufficient","unmodeled history changes branch weights","finite-grid topology dominates"],"why_next_experiment_matters":"It freezes the first corrected probability law rather than the falsified fiber-only law.","status":"OPEN" if scores["M4_branch_union"]==len(rows) else "REQUIRES_REPAIR"})
    append_ndjson(ROOT/"KERNEL_DIALOGUE.ndjson",{"question_id":"C16X-Q007","raw_outcome":summary,"mechanism_update":"Probability at the coarse level is a mixture over local native branches; clustered preparation can activate XNOR genesis and incumbent survival, so destination multiplicity alone is insufficient outside sparse scope.","next_high_information_question":"Freeze branch-union law and test fresh measures/scales."})
    update_state(status="PROBABILITY_BRANCH_REFINED",current_phase="PROBABILITY_REFINED_FREEZE",probability_refinement_hash=h,probability_refinement_summary=summary)
    print(json.dumps({**summary,"result_hash":h},indent=2))

if __name__=="__main__":main()
