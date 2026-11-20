#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(HERE));sys.path.insert(0,str(ROOT/"BASELINE_CORE16_LOCKED"/"RUNNERS"))
from core16x_common import append_ndjson,audit_kernel,canonical_hash,read_json,sha256_file,update_state,utc,write_json
from native_runtime_x import verify_and_load_kernel
from core10_apparatus import run_learned_policy_transfer
from core12_apparatus import regenerative_interface_trial
from run_c8h02_repeated_scaffold_regeneration import simulate as regeneration_simulate

def main():
    audit_kernel("CORE16X_BEFORE_CAPABILITY_HOLDOUT");lock=read_json(ROOT/"HOLDOUT_LOCKS"/"FUNCTIONAL_CAPABILITY_LOCK.json");ch=read_json(ROOT/"FINAL_HOLDOUTS"/"CAPABILITY_CHALLENGES.json")
    for name,expected in lock["source_hashes"].items():
        if sha256_file(ROOT/"RUNNERS_NEW"/name)!=expected:raise RuntimeError(f"frozen source changed: {name}")
    kernel,runtime=verify_and_load_kernel(1);transfers=[]
    expected={"trained":True,"untrained":False,"corridor_cut":False,"receiver_none":False}
    for spec in ch["transfer"]:
        for mode in expected:
            r=run_learned_policy_transfer(kernel,seed=spec["seed"],n=spec["n"],distance=spec["distance"],mode=mode,permutation=tuple(spec["permutation"]),signs=tuple(spec["signs"]))
            transfers.append({"id":spec["id"],"mode":mode,"observed":r["functional_policy_reinstantiated"],"expected":expected[mode],"pass":r["functional_policy_reinstantiated"]==expected[mode],"receiver":r["receiver"],"source_depleted":r["source_depleted_after_launch"],"corridor":r["corridor_all_intermediate_ticks_observed"]})
    regenerations=[]
    for spec in ch["regeneration"]:
        center=tuple(spec["center"]);p=regeneration_simulate(kernel,spec["n"],center,spec["seed"],"primary_payload_nuisance",spec["cycles"]);c=regeneration_simulate(kernel,spec["n"],center,spec["seed"]+1,"missing_corner",spec["cycles"])
        regenerations.append({"id":spec["id"],"primary":p,"control":c,"pass":p["recoveries"]==spec["cycles"] and p["scaffold_raw_unchanged"] and c["recoveries"]==0})
    guards=[]
    for spec in ch["guard"]:
        arms=[]
        for count in (5,6):
            r=regenerative_interface_trial(kernel,n=spec["n"],source_distance=7,downstream_distance=5,horizon=22,mode="semantic4_custom",direction=tuple(spec["direction"]),center=tuple(spec["center"]),source_sreg=spec["sreg"],semantic4_indices=list(range(count)))
            arms.append({"count":count,"events":r["downstream_event_ticks"]["5"]})
        guards.append({"id":spec["id"],"arms":arms,"pass":len(arms[0]["events"])>0 and len(arms[1]["events"])==0})
    summary={"transfer_pass":sum(r["pass"] for r in transfers),"transfer_total":len(transfers),"regeneration_pass":sum(r["pass"] for r in regenerations),"regeneration_total":len(regenerations),"guard_pass":sum(r["pass"] for r in guards),"guard_total":len(guards)}
    summary["overall_pass"]=summary["transfer_pass"]==summary["transfer_total"] and summary["regeneration_pass"]==summary["regeneration_total"] and summary["guard_pass"]==summary["guard_total"]
    result={"holdout":"C16X-FUNCTIONAL-CAPABILITY-FINAL-V1","executed_utc":utc(),"runtime":runtime,"lock_sha256":lock["lock_sha256"],"challenge_sha256":ch["challenge_sha256"],"transfers":transfers,"regenerations":regenerations,"guards":guards,"summary":summary}
    h=canonical_hash(result);write_json(ROOT/"FINAL_HOLDOUTS"/"CAPABILITY_HOLDOUT_RESULTS.json",result)
    append_ndjson(ROOT/"QUESTION_TREE.ndjson",{"question_id":"C16X-Q015","parent_id":"C16X-Q014","parent_result_hash":h,"what_was_learned":f"Functional transfer/control passed {summary['transfer_pass']}/{summary['transfer_total']}, regeneration {summary['regeneration_pass']}/{summary['regeneration_total']}, guard grammar {summary['guard_pass']}/{summary['guard_total']}.","new_uncertainty":"Can one unified response representation merge routed, functional and statistical subbranches without losing their distinct hidden coordinates?","competing_interpretations":["branched overlapping graph","single enriched response level","strict ladder"],"why_next_experiment_matters":"Final level selection must compare compression and task sufficiency across all confirmed laws.","status":"OPEN" if summary["overall_pass"] else "HOLDOUT_FAILED"})
    append_ndjson(ROOT/"KERNEL_DIALOGUE.ndjson",{"question_id":"C16X-Q014","raw_outcome":summary,"mechanism_update":"Functional response, bounded route addressability, regeneration topology and macro control grammar survive fresh worlds; they form a native capability layer with explicit mechanisms and external access still unknown.","next_high_information_question":"Finalize empirical level graph, Bell prerequisite audit and theory placement."})
    update_state(status="CAPABILITY_HOLDOUT_PASS" if summary["overall_pass"] else "CAPABILITY_HOLDOUT_FAIL",current_phase="LEVEL_GRAPH_AND_BELL_SYNTHESIS",capability_holdout_hash=h,capability_holdout_summary=summary)
    print(json.dumps(summary,indent=2))
if __name__=="__main__":main()

