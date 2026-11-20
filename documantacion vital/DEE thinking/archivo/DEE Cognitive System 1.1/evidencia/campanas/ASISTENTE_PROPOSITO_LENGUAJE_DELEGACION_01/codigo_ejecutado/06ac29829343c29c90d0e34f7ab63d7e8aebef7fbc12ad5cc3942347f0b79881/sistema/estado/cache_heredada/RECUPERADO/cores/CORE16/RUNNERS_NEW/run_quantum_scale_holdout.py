#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(HERE));sys.path.insert(0,str(ROOT/"BASELINE_CORE16_LOCKED"/"RUNNERS"))
from core16x_common import append_ndjson,audit_kernel,canonical_hash,read_json,sha256_file,update_state,utc,write_json
from native_runtime_x import verify_and_load_kernel
from run_adaptive_children import sequential_order_trial
from run_quantum_multilevel_discovery import source_bank,reduce_direction

def T(d,s):return reduce_direction(s,d)
def main():
    audit_kernel("CORE16X_BEFORE_QUANTUM_SCALE_HOLDOUT");lock=read_json(ROOT/"HOLDOUT_LOCKS"/"QUANTUM_SCALE_LOCK.json");ch=read_json(ROOT/"FINAL_HOLDOUTS"/"QUANTUM_SCALE_CHALLENGES.json")
    for name,expected in lock["source_hashes"].items():
        if sha256_file(ROOT/"RUNNERS_NEW"/name)!=expected:raise RuntimeError(f"frozen source changed: {name}")
    kernel,runtime=verify_and_load_kernel(1);macro=[]
    for spec in ch["macro"]:
        coherent=source_bank(kernel,spec["size"],0.0,n=spec["n"],horizon=spec["horizon"]);mixed=source_bank(kernel,spec["size"],spec["shifted_fraction"],n=spec["n"],horizon=spec["horizon"])
        macro.append({"spec":spec,"integrated_equal":coherent["integrated_total"]==mixed["integrated_total"],"time_differs":coherent["aggregate_timeline"]!=mixed["aggregate_timeline"],"lane_phase_differs":coherent["lane_phase_classes"]!=mixed["lane_phase_classes"],"coherent":coherent,"mixed":mixed})
    algebra=[]
    for spec in ch["algebra"]:
        d0=tuple(spec["d0"]);a=tuple(spec["a"]);b=tuple(spec["b"]);ab=sequential_order_trial(kernel,d0,a,b,n=spec["n"]);ba=sequential_order_trial(kernel,d0,b,a,n=spec["n"])
        pab=T(b,T(a,d0));pba=T(a,T(b,d0));actual_ab=tuple(ab["final"]["direction"]) if ab.get("valid") else None;actual_ba=tuple(ba["final"]["direction"]) if ba.get("valid") else None
        algebra.append({"spec":spec,"valid":ab.get("valid") and ba.get("valid"),"predicted_AB":pab,"predicted_BA":pba,"actual_AB":actual_ab,"actual_BA":actual_ba,"model_exact":actual_ab==pab and actual_ba==pba,"noncommuting":actual_ab!=actual_ba})
    control=source_bank(kernel,6,0.0,n=47,horizon=24);control2=source_bank(kernel,6,0.0,n=47,horizon=24)
    summary={"macro_pass":sum(r["integrated_equal"] and r["time_differs"] and r["lane_phase_differs"] for r in macro),"macro_total":len(macro),"algebra_pass":sum(r["valid"] and r["model_exact"] and r["noncommuting"] for r in algebra),"algebra_total":len(algebra),"identical_control_equal":control==control2}
    summary["overall_pass"]=summary["macro_pass"]==summary["macro_total"] and summary["algebra_pass"]==summary["algebra_total"] and summary["identical_control_equal"]
    result={"holdout":"C16X-QUANTUM-SCALE-FINAL-V1","executed_utc":utc(),"runtime":runtime,"lock_sha256":lock["lock_sha256"],"challenge_sha256":ch["challenge_sha256"],"macro":macro,"algebra":algebra,"summary":summary,"adjudication":"Cross-scale phase accessibility and noncommuting response are native laws, but exact deterministic train/reducer mechanisms defeat quantum-specific interpretation."}
    h=canonical_hash(result);write_json(ROOT/"FINAL_HOLDOUTS"/"QUANTUM_SCALE_HOLDOUT_RESULTS.json",result)
    append_ndjson(ROOT/"QUESTION_TREE.ndjson",{"question_id":"C16X-Q012","parent_id":"C16X-Q011","parent_result_hash":h,"what_was_learned":f"Macro phase passed {summary['macro_pass']}/{summary['macro_total']} fresh banks and semigroup law {summary['algebra_pass']}/{summary['algebra_total']} fresh executions.","new_uncertainty":"Does any accepted level now supply two separated correlated subsystems satisfying Bell prerequisites beyond the preserved baseline apparatus?","competing_interpretations":["no new Bell-valid subsystem exists","functional organizations provide new settings/outcomes","coarse selection fabricates apparent correlation"],"why_next_experiment_matters":"Bell tests are valid only after subsystem and assumption prerequisites, not by relabeling phase trains.","status":"OPEN" if summary["overall_pass"] else "HOLDOUT_FAILED"})
    append_ndjson(ROOT/"KERNEL_DIALOGUE.ndjson",{"question_id":"C16X-Q011","raw_outcome":summary,"mechanism_update":"Phase-like information survives large organization under a time-resolved observer; classical noncommutativity generalizes. Neither supplies amplitudes, contextual compatibility or nonfactorizable correlations.","next_high_information_question":"Perform prerequisite-first multilevel Bell audit and classicalization analysis."})
    update_state(status="QUANTUM_SCALE_HOLDOUT_PASS" if summary["overall_pass"] else "QUANTUM_SCALE_HOLDOUT_FAIL",current_phase="BELL_AND_CLASSICALIZATION_AUDIT",quantum_scale_holdout_hash=h,quantum_scale_holdout_summary=summary)
    print(json.dumps(summary,indent=2))
if __name__=="__main__":main()

