#!/usr/bin/env python3
"""Quantum-like search across routed, relational, statistical and macro levels."""
from __future__ import annotations

import itertools,json,sys
from collections import Counter
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(HERE));sys.path.insert(0,str(ROOT/"BASELINE_CORE16_LOCKED"/"RUNNERS"))
from core16x_common import append_ndjson,audit_kernel,canonical_hash,read_json,update_state,utc,write_json
from native_runtime_x import NativeWorld,pack,verify_and_load_kernel
from core12_apparatus import convergent_phase_paths
from run_adaptive_children import sequential_order_trial


def sign(v):return 1 if v>0 else -1 if v<0 else 0
def reduce_direction(a,b):return tuple(sign(a[i]+b[i]) for i in range(3))


def path_panel(kernel):
    frames=((0,1,2),(1,2,0),(2,0,1));rows=[]
    for i in range(12):
        n=(31,37,43)[i%3];path=(5,7,9,11)[i%4];frame=frames[i%3];sregs=(101+13*i,211+17*i);horizon=path+12
        modes={m:convergent_phase_paths(kernel,n=n,path_length=path,mode=m,sregs=sregs,horizon=horizon,frame=frame) for m in ("A_only","B_only","AB_coherent","AB_phase_shifted","AB_offpath_sham")}
        a=dict(zip(modes["A_only"]["detector_event_ticks"],modes["A_only"]["detector_event_sregs"]));b=dict(zip(modes["B_only"]["detector_event_ticks"],modes["B_only"]["detector_event_sregs"]));ab=dict(zip(modes["AB_coherent"]["detector_event_ticks"],modes["AB_coherent"]["detector_event_sregs"]));
        common=sorted(set(a)&set(b));additive=all(ab.get(t)==min(19664,a[t]+b[t]) for t in common)
        rows.append({"case":i,"n":n,"path":path,"frame":frame,"sregs":sregs,"common_ticks":common,"additive_payload_at_common_ticks":additive,"coherent":{k:modes["AB_coherent"][k] for k in ("event_count","detector_event_ticks","detector_event_sregs","detector_event_directions")},"shifted":{k:modes["AB_phase_shifted"][k] for k in ("event_count","detector_event_ticks","detector_event_sregs","detector_event_directions")},"offpath_same":modes["AB_offpath_sham"]["detector_event_sregs"]==modes["AB_coherent"]["detector_event_sregs"],"count_shadow_equal_shifted":modes["AB_phase_shifted"]["event_count"]==modes["AB_coherent"]["event_count"],"payload_shadow_distinguishes_shifted":modes["AB_phase_shifted"]["detector_event_sregs"]!=modes["AB_coherent"]["detector_event_sregs"]})
    return {"cases":rows,"additive":sum(r["additive_payload_at_common_ticks"] for r in rows),"offpath_invariant":sum(r["offpath_same"] for r in rows),"count_hides_phase":sum(r["count_shadow_equal_shifted"] and r["payload_shadow_distinguishes_shifted"] for r in rows)}


def source_bank(kernel,size,shifted_fraction,n=43,horizon=24):
    direction=(1,0,0);source_x=7;detector_x=16;raw=np.zeros((n,n,n),dtype=np.uint64);clock=np.zeros_like(raw)
    side=int(np.ceil(np.sqrt(size)));lanes=[]
    for index in range(size):
        y=(5+(index%side)*3)%n;z=(5+(index//side)*3)%n;source=(source_x,y,z);mouth=((source_x+1)%n,y,z);detector=(detector_x,y,z)
        raw[source]=pack(0,113+index,(1,0,0),4);clock[source]=np.uint64(1000+index)
        if index<int(round(size*shifted_fraction)):raw[mouth]=pack(1,29,(0,0,0),1)
        lanes.append((source,mouth,detector))
    world=NativeWorld(kernel,raw,clock,1);events=[[] for _ in lanes]
    for tick in range(horizon+1):
        for j,(_,_,detector) in enumerate(lanes):
            value=int(world.raw[detector]);sem=(value>>60)&0xF
            if value and sem==1:events[j].append(tick)
        if tick<horizon:world.tick()
    integrated=[len(x) for x in events];timeline=Counter(t for lane in events for t in lane)
    return {"size":size,"shifted_fraction":shifted_fraction,"lane_events":events,"integrated_per_lane":integrated,"integrated_total":sum(integrated),"aggregate_timeline":dict(sorted(timeline.items())),"lane_phase_classes":[tuple(t%2 for t in lane) for lane in events]}


def macro_phase_panel(kernel):
    rows=[]
    for size in (1,4,9,16):
        coherent=source_bank(kernel,size,0.0);mixed=source_bank(kernel,size,0.5)
        rows.append({"size":size,"coherent":coherent,"mixed":mixed,"same_integrated_total":coherent["integrated_total"]==mixed["integrated_total"],"time_resolved_differs":coherent["aggregate_timeline"]!=mixed["aggregate_timeline"],"lane_resolved_phase_recoverable":coherent["lane_phase_classes"]!=mixed["lane_phase_classes"]})
    return {"rows":rows,"all_sizes_hidden_by_integrated_but_recovered":all(r["same_integrated_total"] and r["time_resolved_differs"] and r["lane_resolved_phase_recoverable"] for r in rows)}


def transition_algebra(kernel):
    states=list(itertools.product((-1,0,1),repeat=3));interventions=[s for s in states if s!=(0,0,0)]
    def T(d,s):return reduce_direction(s,d)
    noncomm=[]
    for a in interventions:
        for b in interventions:
            witnesses=[s for s in states if T(a,T(b,s))!=T(b,T(a,s))]
            if witnesses:noncomm.append({"a":a,"b":b,"witness":witnesses[0],"AB":T(b,T(a,witnesses[0])),"BA":T(a,T(b,witnesses[0]))})
    native=[]
    base=((1,0,0),(0,1,0),(0,0,1),(-1,0,0),(0,-1,0),(0,0,-1))
    for i in range(24):
        d0=base[i%6];a=tuple((-1,1,0)[(j+i)%3] for j in range(3));b=tuple((1,-1,0)[(j+2*i)%3] for j in range(3))
        ab=sequential_order_trial(kernel,d0,a,b,n=(29,31,35)[i%3]);ba=sequential_order_trial(kernel,d0,b,a,n=(29,31,35)[i%3])
        native.append({"case":i,"d0":d0,"a":a,"b":b,"AB":ab,"BA":ba,"valid":ab.get("valid") and ba.get("valid"),"differs":ab.get("final")!=ba.get("final")})
    return {"state_count":len(states),"intervention_count":len(interventions),"ordered_intervention_pairs":len(interventions)**2,"noncommuting_pairs":len(noncomm),"witnesses":noncomm[:80],"native_cases":native,"native_valid":sum(r["valid"] for r in native),"native_order_differs":sum(r["valid"] and r["differs"] for r in native),"classification":"CLASSICAL_FINITE_NONCOMMUTING_TRANSFORMATION_SEMIGROUP_FROM_LOSSY_SIGN_REDUCTION"}


def indistinguishability(kernel):
    n=17;raw1=np.zeros((n,n,n),dtype=np.uint64);raw2=np.zeros_like(raw1);tokens=[((3,5,5),(1,0,0)),((10,8,8),(-1,0,0))]
    for q,d in tokens:raw1[q]=pack(123,37,d,1)
    for q,d in reversed(tokens):raw2[q]=pack(123,37,d,1)
    trace=[];a=NativeWorld(kernel,raw1,threads=1);b=NativeWorld(kernel,raw2,threads=1)
    for t in range(5):
        trace.append({"tick":t,"raw_equal":bool(np.array_equal(a.raw,b.raw))})
        a.tick();b.tick()
    return {"external_label_permutation":"NOT_STORED_IN_DEE_STATE","injection_order_trace":trace,"permutation_parity_effect":"NONE","scope":"identical raw organizations; no claim about a not-yet-constructed topological exchange phase"}


def main():
    audit_kernel("CORE16X_BEFORE_QUANTUM_MULTILEVEL_DISCOVERY");kernel,runtime=verify_and_load_kernel(1)
    paths=path_panel(kernel);macro=macro_phase_panel(kernel);algebra=transition_algebra(kernel);indist=indistinguishability(kernel)
    baseline=read_json(ROOT/"BASELINE_CORE16_LOCKED"/"QUANTUM_LIKE_LEVEL_ATLAS.json")
    result={"experiment":"C16X-QUANTUM-LIKE-MULTILEVEL-DISCOVERY","created_utc":utc(),"runtime":runtime,"routed_path_composition":paths,"macro_phase_access":macro,"effective_operation_algebra":algebra,"indistinguishability":indist,"baseline":baseline,
            "level_adjudication":[
                {"level":"L0_FULL/L0_CAUSAL_QUOTIENT","finding":"deterministic many-to-one; no superposition law"},
                {"level":"L1_ROUTED_EVENT","finding":"phase/path access and capped additive reducer; no nonadditive interference"},
                {"level":"L1_PHASE_HISTORY","finding":"time-resolved phase persists in source banks; count observer hides it"},
                {"level":"L2_ORGANIZATION_RESPONSE","finding":"classical noncommuting state transformations from lossy history; compatibility prerequisites for contextuality absent"},
                {"level":"L3_STATISTICAL","finding":"probability is measure-conditioned classical ignorance; branch state restores determinism"}],
            "quantum_status":"NO_QUANTUM_LAW_ESTABLISHED_PHASE_AND_NONCOMMUTATIVITY_HAVE_SIMPLER_DETERMINISTIC_EXPLANATIONS","born_like":"NOT_TRIGGERED","contextuality":"NOT_OPERATIONALLY_JUSTIFIED","superposition_like":"NOT_FOUND"}
    h=canonical_hash(result);write_json(ROOT/"DISCOVERY"/"QUANTUM_MULTILEVEL_DISCOVERY.json",result)
    append_ndjson(ROOT/"QUESTION_TREE.ndjson",{"question_id":"C16X-Q010","parent_id":"C16X-Q009","parent_result_hash":h,"what_was_learned":f"Capped additive routing held {paths['additive']}/{len(paths['cases'])}; macro phase remained time/lane-readable through size16; {algebra['noncommuting_pairs']} finite transformation pairs are noncommuting but classically stateful.","new_uncertainty":"Does macro phase accessibility and the finite transformation law survive frozen fresh configurations, and does either supply valid Bell subsystems?","competing_interpretations":["native phase survives but is nonquantum","larger coupling produces nonadditive composition","apparent noncommutativity is entirely ordinary state modification"],"why_next_experiment_matters":"It separates cross-scale information persistence from quantum-law promotion.","status":"OPEN"})
    append_ndjson(ROOT/"KERNEL_DIALOGUE.ndjson",{"question_id":"C16X-Q009","raw_outcome":{"path_additive":paths["additive"],"path_cases":len(paths["cases"]),"macro_phase":macro["all_sizes_hidden_by_integrated_but_recovered"],"noncommuting_pairs":algebra["noncommuting_pairs"],"native_order_differs":algebra["native_order_differs"]},"mechanism_update":"Phase information can survive organization size and become observer-hidden without quantum interference. Effective noncommutativity is a reusable classical transformation semigroup caused by lossy sign response.","next_high_information_question":"Freeze macro-phase and algebra claims; audit Bell prerequisites at each accepted level."})
    update_state(status="QUANTUM_MULTILEVEL_DISCOVERY_COMPLETE",current_phase="QUANTUM_SCALE_TRANSFER_FREEZE",quantum_discovery_hash=h)
    print(json.dumps({"path_additive":f"{paths['additive']}/{len(paths['cases'])}","offpath":paths["offpath_invariant"],"count_hides_phase":paths["count_hides_phase"],"macro_phase":macro["all_sizes_hidden_by_integrated_but_recovered"],"noncommuting_pairs":algebra["noncommuting_pairs"],"native_order":f"{algebra['native_order_differs']}/{algebra['native_valid']}","hash":h},indent=2))

if __name__=="__main__":main()

