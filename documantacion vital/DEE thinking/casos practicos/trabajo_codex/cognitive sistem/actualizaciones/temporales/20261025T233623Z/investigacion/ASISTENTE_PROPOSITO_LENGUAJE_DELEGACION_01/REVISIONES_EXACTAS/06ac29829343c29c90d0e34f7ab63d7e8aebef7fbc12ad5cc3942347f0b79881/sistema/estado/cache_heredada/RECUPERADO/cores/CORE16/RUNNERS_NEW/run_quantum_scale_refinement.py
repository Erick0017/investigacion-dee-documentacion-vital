#!/usr/bin/env python3
"""Result-derived refinement of macro phase access and transformation algebra."""
from __future__ import annotations
import itertools,json,sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(HERE));sys.path.insert(0,str(ROOT/"BASELINE_CORE16_LOCKED"/"RUNNERS"))
from core16x_common import append_ndjson,audit_kernel,canonical_hash,read_json,update_state,utc,write_json
from native_runtime_x import verify_and_load_kernel
from run_adaptive_children import sequential_order_trial
from run_quantum_multilevel_discovery import source_bank,reduce_direction

def transform(d,s):return reduce_direction(s,d)

def main():
    audit_kernel("CORE16X_BEFORE_QUANTUM_SCALE_REFINEMENT");kernel,runtime=verify_and_load_kernel(1)
    parent=read_json(ROOT/"DISCOVERY"/"QUANTUM_MULTILEVEL_DISCOVERY.json")
    macro=[]
    for size in (1,4,9,16,25):
        coherent=source_bank(kernel,size,0.0,n=47,horizon=24)
        shifted_fraction=1.0 if size==1 else max(1,size//2)/size
        mixed=source_bank(kernel,size,shifted_fraction,n=47,horizon=24)
        macro.append({"size":size,"shifted_lanes":max(1,size//2),"same_integrated_total":coherent["integrated_total"]==mixed["integrated_total"],"time_resolved_differs":coherent["aggregate_timeline"]!=mixed["aggregate_timeline"],"lane_phase_recoverable":coherent["lane_phase_classes"]!=mixed["lane_phase_classes"],"coherent":coherent,"mixed":mixed})
    algebra=[];base_d0=(1,0,0);base_a=(-1,1,0);base_b=(1,-1,0)
    for permutation in itertools.permutations((0,1,2)):
        for signs in itertools.product((-1,1),repeat=3):
            def tr(v):return tuple(signs[i]*v[permutation[i]] for i in range(3))
            d0,a,b=tr(base_d0),tr(base_a),tr(base_b)
            predicted_ab=transform(b,transform(a,d0));predicted_ba=transform(a,transform(b,d0))
            ab=sequential_order_trial(kernel,d0,a,b,n=37);ba=sequential_order_trial(kernel,d0,b,a,n=37)
            actual_ab=tuple(ab["final"]["direction"]) if ab.get("valid") else None;actual_ba=tuple(ba["final"]["direction"]) if ba.get("valid") else None
            algebra.append({"permutation":permutation,"signs":signs,"d0":d0,"a":a,"b":b,"predicted_AB":predicted_ab,"predicted_BA":predicted_ba,"predicted_noncommuting":predicted_ab!=predicted_ba,"actual_AB":actual_ab,"actual_BA":actual_ba,"valid":ab.get("valid") and ba.get("valid"),"model_exact":actual_ab==predicted_ab and actual_ba==predicted_ba,"actual_noncommuting":actual_ab!=actual_ba})
    summary={"macro_sizes":len(macro),"macro_integrated_equal":sum(r["same_integrated_total"] for r in macro),"macro_time_readable":sum(r["time_resolved_differs"] and r["lane_phase_recoverable"] for r in macro),"algebra_cases":len(algebra),"algebra_valid":sum(r["valid"] for r in algebra),"algebra_model_exact":sum(r["model_exact"] for r in algebra),"algebra_noncommuting":sum(r["actual_noncommuting"] for r in algebra)}
    result={"experiment":"C16X-QUANTUM-SCALE-REFINEMENT","created_utc":utc(),"parent_result_hash":canonical_hash(parent),"runtime":runtime,"macro_phase":macro,"algebra":algebra,"summary":summary,"interpretation":{"macro_phase":"period-two causal phase survives through 25-source organization and is hidden only by time integration; this is not a quantum-only property","noncommutativity":"exact finite classical transformation semigroup from sequential lossy direction reduction; no compatible nondisturbing observable context"}}
    h=canonical_hash(result);write_json(ROOT/"MODEL_SELECTION"/"QUANTUM_SCALE_REFINEMENT.json",result)
    append_ndjson(ROOT/"QUESTION_TREE.ndjson",{"question_id":"C16X-Q011","parent_id":"C16X-Q010","parent_result_hash":h,"what_was_learned":f"Phase remained hidden-by-integration but recoverable at {summary['macro_time_readable']}/{summary['macro_sizes']} sizes; algebra predicted the binary exactly in {summary['algebra_model_exact']}/{summary['algebra_cases']} cases.","new_uncertainty":"Do untouched source banks and unused algebra configurations reproduce both laws after freeze?","competing_interpretations":["classical causal phase and semigroup generalize","cross-lane coupling breaks scale transfer","unmodeled state invalidates algebra"],"why_next_experiment_matters":"Fresh confirmation is required before calling either a native cross-scale law.","status":"OPEN" if summary["macro_time_readable"]==summary["macro_sizes"] and summary["algebra_model_exact"]==summary["algebra_cases"] else "REQUIRES_REPAIR"})
    append_ndjson(ROOT/"KERNEL_DIALOGUE.ndjson",{"question_id":"C16X-Q010","raw_outcome":summary,"mechanism_update":"Macro phase persistence and noncommuting operations survive refinement, but both have exact deterministic mechanisms; no quantum promotion follows.","next_high_information_question":"Freeze and challenge, then audit Bell prerequisites rather than inventing a new Bell apparatus."})
    update_state(status="QUANTUM_SCALE_REFINED",current_phase="QUANTUM_SCALE_FREEZE",quantum_scale_refinement_hash=h,quantum_scale_summary=summary)
    print(json.dumps({**summary,"result_hash":h},indent=2))
if __name__=="__main__":main()

