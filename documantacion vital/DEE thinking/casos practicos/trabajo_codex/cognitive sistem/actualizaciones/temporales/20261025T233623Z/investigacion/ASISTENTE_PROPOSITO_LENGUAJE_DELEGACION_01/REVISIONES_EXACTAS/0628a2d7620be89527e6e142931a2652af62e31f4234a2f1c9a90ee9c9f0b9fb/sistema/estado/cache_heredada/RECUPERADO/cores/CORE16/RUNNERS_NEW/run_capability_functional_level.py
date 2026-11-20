#!/usr/bin/env python3
"""Capability composition, addressability, programmability and functional-level search."""
from __future__ import annotations
import itertools,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(HERE));sys.path.insert(0,str(ROOT/"BASELINE_CORE16_LOCKED"/"RUNNERS"))
from core16x_common import append_ndjson,audit_kernel,canonical_hash,read_json,update_state,utc,write_json
from native_runtime_x import verify_and_load_kernel
from core10_apparatus import run_learned_policy_transfer
from core12_apparatus import regenerative_interface_trial
from run_c8h02_repeated_scaffold_regeneration import simulate as regeneration_simulate

def transfer_panel(kernel):
    frames=[((0,1,2),(1,1,1)),((1,2,0),(1,-1,1)),((2,0,1),(-1,1,1)),((0,2,1),(-1,-1,1))]
    positives=[];controls=[];address_pairs=[]
    for i in range(12):
        p,s=frames[i%len(frames)];n=(27,31,35)[i%3];distance=(5,7,9)[i%3];seed=162000+i*113
        r=run_learned_policy_transfer(kernel,seed=seed,n=n,distance=distance,mode="trained",permutation=p,signs=s)
        positives.append({"case":i,"n":n,"distance":distance,"frame":{"permutation":p,"signs":s},"receiver":r["receiver"],"functional":r["functional_policy_reinstantiated"],"source_depleted":r["source_depleted_after_launch"],"corridor_complete":r["corridor_all_intermediate_ticks_observed"],"arrival":r["arrival_record"],"query":r["query_record"]})
        if i<6:
            for mode in ("untrained","no_relay","corridor_cut","offpath_cut","receiver_none","wrong_receiver","memory_ablation"):
                c=run_learned_policy_transfer(kernel,seed=seed,n=n,distance=distance,mode=mode,permutation=p,signs=s)
                controls.append({"case":i,"mode":mode,"functional":c["functional_policy_reinstantiated"],"source_depleted":c["source_depleted_after_launch"],"corridor_complete":c["corridor_all_intermediate_ticks_observed"],"receiver":c["receiver"]})
    for i in range(6):
        p,s=frames[i%len(frames)];seed=163000+i*211;n=37
        a=run_learned_policy_transfer(kernel,seed=seed,n=n,distance=5,mode="trained",permutation=p,signs=s);b=run_learned_policy_transfer(kernel,seed=seed,n=n,distance=9,mode="trained",permutation=p,signs=s)
        address_pairs.append({"case":i,"receiver_near":a["receiver"],"receiver_far":b["receiver"],"distinct":a["receiver"]!=b["receiver"],"near_functional":a["functional_policy_reinstantiated"],"far_functional":b["functional_policy_reinstantiated"],"near_corridor":a["corridor_all_intermediate_ticks_observed"],"far_corridor":b["corridor_all_intermediate_ticks_observed"]})
    expected_controls={"untrained":False,"no_relay":False,"corridor_cut":False,"offpath_cut":True,"receiver_none":False,"wrong_receiver":False,"memory_ablation":False}
    return {"positives":positives,"controls":controls,"address_pairs":address_pairs,"positive_pass":sum(r["functional"] and r["source_depleted"] and r["corridor_complete"] for r in positives),"control_pass":sum(r["functional"]==expected_controls[r["mode"]] for r in controls),"control_total":len(controls),"address_pass":sum(r["distinct"] and r["near_functional"] and r["far_functional"] and r["near_corridor"] and r["far_corridor"] for r in address_pairs),"address_total":len(address_pairs),"classification":"ROUTE_AND_DISTANCE_SELECTED_DESTRUCTIVE_FUNCTIONAL_RECONSTRUCTION_WITH_EXPLICIT_CARRIER_AND_PREPARED_RECEIVER"}

def programmability_panel(kernel):
    dirs=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1));rows=[]
    for d in dirs:
        for count in range(9):
            r=regenerative_interface_trial(kernel,n=35,source_distance=7,downstream_distance=5,horizon=22,mode="semantic4_custom",direction=d,center=(17,17,17),source_sreg=173,semantic4_indices=list(range(count)))
            events=r["downstream_event_ticks"]["5"]
            rows.append({"direction":d,"guard_count":count,"event_ticks":events,"event_count":len(events),"transmits":len(events)>0})
    by_count={str(k):{"transmit":sum(r["transmits"] for r in rows if r["guard_count"]==k),"block":sum(not r["transmits"] for r in rows if r["guard_count"]==k)} for k in range(9)}
    k5=[r for r in rows if r["guard_count"]==5];k6=[r for r in rows if r["guard_count"]==6]
    return {"rows":rows,"by_count":by_count,"one_cell_k5_k6_selects_macro_outcome":all(r["transmits"] for r in k5) and all(not r["transmits"] for r in k6),"control_grammar":"semantic4 guard support count crosses exact topology-dependent k5/k6 train-response boundary in this ordered-corner family","programmability_scope":"prepared interface selects transmission/blocking of repeated carrier train; not general-purpose computation or external technological access"}

def regeneration_panel(kernel):
    primary=[];controls=[]
    for i in range(6):
        n=(19,23,27)[i%3];center=tuple((5+3*i+j*2)%n for j in range(3));primary.append(regeneration_simulate(kernel,n,center,164000+i*97,"primary_payload_nuisance",12))
        controls.append(regeneration_simulate(kernel,n,center,165000+i*97,"missing_corner",6));controls.append(regeneration_simulate(kernel,n,center,166000+i*97,"disconnected_corner",6))
    return {"primary":primary,"controls":controls,"primary_recoveries":sum(r["recoveries"] for r in primary),"primary_cycles":sum(r["cycles"] for r in primary),"primary_scaffold_unchanged":sum(r["scaffold_raw_unchanged"] for r in primary),"control_recoveries":sum(r["recoveries"] for r in controls),"control_cycles":sum(r["cycles"] for r in controls),"damage_boundary":"center deletion is restored with intact eight-corner semantic4 topology; scaffold-corner loss is not repaired","resource_accounting":"scaffold raw/s_reg is nondepleting in scope; no work/energy cycle established"}

def main():
    audit_kernel("CORE16X_BEFORE_CAPABILITY_FUNCTIONAL_LEVEL");kernel,runtime=verify_and_load_kernel(1)
    transfer=transfer_panel(kernel);program=programmability_panel(kernel);regen=regeneration_panel(kernel);baseline=read_json(ROOT/"BASELINE_CORE16_LOCKED"/"CAPABILITY_ATLAS.json")
    functional_gate=transfer["positive_pass"]==len(transfer["positives"]) and transfer["control_pass"]==transfer["control_total"] and transfer["address_pass"]==transfer["address_total"]
    regen_gate=regen["primary_recoveries"]==regen["primary_cycles"] and regen["control_recoveries"]==0
    result={"experiment":"C16X-CAPABILITY-FUNCTIONAL-LEVEL","created_utc":utc(),"runtime":runtime,"transfer_addressability":transfer,"programmability":program,"regeneration":regen,"baseline":baseline,
            "functional_level_test":{"compression":"learned policy direction/response class replaces source raw microstate","predictive_tasks":["receiver query response","route-selected reconstruction","damage recovery"],"stable_laws":functional_gate and regen_gate,"fresh_worlds_in_this_discovery":len(transfer["positives"])+len(regen["primary"]),"not_trivial_raw_variable":True,"disposition":"L2_FUNCTIONAL_SUBBRANCH_SUPPORTED_PENDING_FRESH_FREEZE" if functional_gate and regen_gate else "NOT_ESTABLISHED","merge_test":"Shares intervention-response equivalence with L2 relational organization but requires history/policy coordinates; retain as overlapping L2F subbranch, not a new total order rung."},
            "capability_status":{"regeneration":"CAPABILITY_EXISTS_IN_DEE_EXTERNAL_ACCESS_UNKNOWN","functional_reinstantiation":"CAPABILITY_EXISTS_IN_DEE_ROUTE_ADDRESSABLE_PREPARED_RECEIVER","programmability":"BOUNDED_MACRO_OUTCOME_SELECTION_EXTERNAL_CONTROL_UNKNOWN","remote_effect":"NOT_FOUND_EXPLICIT_CARRIER_REQUIRED","resource_cost":"UNACCOUNTED"}}
    h=canonical_hash(result);write_json(ROOT/"DISCOVERY"/"CAPABILITY_FUNCTIONAL_LEVEL.json",result)
    append_ndjson(ROOT/"QUESTION_TREE.ndjson",{"question_id":"C16X-Q014","parent_id":"C16X-Q013","parent_result_hash":h,"what_was_learned":f"Functional transfer passed {transfer['positive_pass']}/{len(transfer['positives'])}, controls {transfer['control_pass']}/{transfer['control_total']}, address pairs {transfer['address_pass']}/{transfer['address_total']}; regeneration {regen['primary_recoveries']}/{regen['primary_cycles']} with {regen['control_recoveries']}/{regen['control_cycles']} damaged-scaffold controls.","new_uncertainty":"Does the L2 functional subbranch and bounded control grammar survive untouched worlds, and can it merge predictively with relational organization?","competing_interpretations":["overlapping functional sublevel","apparatus-specific rule","fully reducible to routed event state without added history"],"why_next_experiment_matters":"A new level requires prospective generalization and nontrivial response compression.","status":"OPEN" if functional_gate and regen_gate and program["one_cell_k5_k6_selects_macro_outcome"] else "REQUIRES_REPAIR"})
    append_ndjson(ROOT/"KERNEL_DIALOGUE.ndjson",{"question_id":"C16X-Q013","raw_outcome":{"transfer":transfer["positive_pass"],"controls":transfer["control_pass"],"address":transfer["address_pass"],"regeneration":f"{regen['primary_recoveries']}/{regen['primary_cycles']}","programmable_boundary":program["one_cell_k5_k6_selects_macro_outcome"]},"mechanism_update":"Functional response is compressed and route-addressable through explicit carriers; regeneration and guard control are precise local information transformations, not magic or carrier-free remoteness.","next_high_information_question":"Freeze L2F/addressability/control claims and test fresh worlds."})
    update_state(status="FUNCTIONAL_LEVEL_DISCOVERED" if functional_gate and regen_gate else "FUNCTIONAL_LEVEL_UNRESOLVED",current_phase="FUNCTIONAL_LEVEL_FREEZE",capability_functional_hash=h)
    print(json.dumps({"transfer":f"{transfer['positive_pass']}/{len(transfer['positives'])}","controls":f"{transfer['control_pass']}/{transfer['control_total']}","address":f"{transfer['address_pass']}/{transfer['address_total']}","regen":f"{regen['primary_recoveries']}/{regen['primary_cycles']}","regen_controls":f"{regen['control_recoveries']}/{regen['control_cycles']}","programmability":program["one_cell_k5_k6_selects_macro_outcome"],"functional_gate":functional_gate,"hash":h},indent=2))
if __name__=="__main__":main()

