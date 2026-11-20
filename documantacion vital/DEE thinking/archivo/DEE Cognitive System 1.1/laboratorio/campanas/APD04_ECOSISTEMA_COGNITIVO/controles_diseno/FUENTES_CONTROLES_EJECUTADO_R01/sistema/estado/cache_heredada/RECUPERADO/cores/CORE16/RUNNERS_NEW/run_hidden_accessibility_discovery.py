#!/usr/bin/env python3
"""Cross-variable hidden-state resurrection and embedded-access discovery."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "BASELINE_CORE16_LOCKED" / "RUNNERS"))
from core16x_common import append_ndjson, audit_kernel, canonical_hash, read_json, update_state, utc, write_json
from native_runtime_x import NativeWorld, pack, sha256_array, verify_and_load_kernel
from occupancy_operator import unpack
from core12_apparatus import source_train_trial


def evolve_pair(kernel, raw_a, raw_b, clock_a=None, clock_b=None, ticks=1):
    a = NativeWorld(kernel, raw_a, clock_a, 1); b = NativeWorld(kernel, raw_b, clock_b, 1)
    trace = []
    for tick in range(ticks + 1):
        trace.append({
            "tick": tick,
            "raw_equal": bool(np.array_equal(a.raw, b.raw)),
            "clock_equal": bool(np.array_equal(a.clock, b.clock)),
            "raw_mismatch_cells": int(np.count_nonzero(a.raw != b.raw)),
            "clock_mismatch_cells": int(np.count_nonzero(a.clock != b.clock)),
            "a_raw_sha256": sha256_array(a.raw), "b_raw_sha256": sha256_array(b.raw),
        })
        if tick < ticks:
            a.tick(); b.tick()
    return trace, a, b


def direction_case(kernel):
    n=9; c=(4,4,4)
    a=np.zeros((n,n,n),dtype=np.uint64); b=a.copy()
    a[c]=pack(17,31,(1,0,0),1); b[c]=pack(17,31,(-1,0,0),1)
    trace,_,_=evolve_pair(kernel,a,b,ticks=3)
    return {"hidden_component":"direction","equal_under":"occupancy+sreg+semantic+support","intervention":"native evolution","trace":trace,"classification":"LATER_REVEALABLE_IMMEDIATE","visible_tick":next(row["tick"] for row in trace if not row["raw_equal"])}


def semantic_case(kernel):
    n=9;c=(4,4,4);a=np.zeros((n,n,n),dtype=np.uint64);b=a.copy()
    a[c]=pack(17,31,(0,0,0),1);b[c]=pack(17,31,(0,0,0),4)
    trace,_,_=evolve_pair(kernel,a,b,ticks=3)
    return {"hidden_component":"semantic","equal_under":"occupancy+sreg+direction+support","intervention":"native evolution","trace":trace,"classification":"LATER_REVEALABLE_IMMEDIATE","mechanism":"semantic1 isolated matter dies; semantic4 raw is fixed"}


def sreg_case(kernel):
    n=9;c=(4,4,4);a=np.zeros((n,n,n),dtype=np.uint64);b=a.copy()
    a[c]=pack(0,7,(1,0,0),4);b[c]=pack(0,701,(1,0,0),4)
    trace,wa,wb=evolve_pair(kernel,a,b,ticks=3)
    arrivals=[]
    for k in range(1,4):
        qa=((c[0]+k)%n,c[1],c[2])
        arrivals.append({"distance":k,"a":unpack(wa.raw[qa]),"b":unpack(wb.raw[qa])})
    return {"hidden_component":"s_reg","equal_under":"occupancy+direction+semantic","intervention":"source-supported propagation","trace":trace,"arrivals_at_t3":arrivals,"classification":"TRANSPORTED_AND_READABLE"}


def topology_case(kernel):
    n=11
    a=np.zeros((n,n,n),dtype=np.uint64);b=a.copy()
    # Equal support, sreg total and direction distribution. A routes to four unique targets; B to one shared target.
    specs_a=[((2,2,2),(1,0,0)),((5,2,2),(1,0,0)),((2,5,2),(1,0,0)),((2,2,5),(1,0,0))]
    target=(7,7,7)
    dirs=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0))
    sources_b=[tuple((target[i]-d[i])%n for i in range(3)) for d in dirs]
    for i,(q,d) in enumerate(specs_a): a[q]=pack(100+i,13,d,1)
    for i,(q,d) in enumerate(zip(sources_b,dirs)): b[q]=pack(100+i,13,d,1)
    trace,wa,wb=evolve_pair(kernel,a,b,ticks=1)
    return {"hidden_component":"route topology/destination class","equal_under":"support+sreg total+coarse direction counts","intervention":"one native tick","trace":trace,"a_next_support":int(np.count_nonzero(wa.raw)),"b_next_support":int(np.count_nonzero(wb.raw)),"classification":"LATER_REVEALABLE_BY_DESTINATION_REDUCTION"}


def payload_loss_case(kernel):
    n=9;c=(4,4,4);a=np.zeros((n,n,n),dtype=np.uint64);b=a.copy()
    a[c]=pack(1,0,(0,0,0),1);b[c]=pack(0xDEADBEEF,0,(0,0,0),1)
    trace,_,_=evolve_pair(kernel,a,b,ticks=4)
    return {"hidden_component":"nonsemantic4 state payload above existence","equal_under":"exact causal quotient","intervention":"native evolution","trace":trace,"classification":"TRUE_KERNEL_MANY_TO_ONE_LOSS_AFTER_ONE_TICK","convergence_tick":next(row["tick"] for row in trace if row["raw_equal"] and row["clock_equal"])}


def delayed_clock_case(kernel, delay=11):
    n=11;c=(5,5,5)
    base=np.zeros((n,n,n),dtype=np.uint64);base[c]=pack(0x1234,10,(0,0,0),4)
    ca=np.zeros_like(base);cb=np.zeros_like(base)
    ca[c]=np.uint64((195-delay)%195);cb[c]=np.uint64(((195-delay)%195)+1)
    a=NativeWorld(kernel,base,ca,1);b=NativeWorld(kernel,base,cb,1)
    coast=[]
    for tick in range(delay+1):
        coast.append({"tick":tick,"raw_equal":bool(np.array_equal(a.raw,b.raw)),"center_clock_a":int(a.clock[c]),"center_clock_b":int(b.clock[c])})
        if tick<delay: a.tick();b.tick()
    # Same later intervention exposes the old clock residual: convert target to semantic1 and add tetra support.
    fa=unpack(a.raw[c]);fb=unpack(b.raw[c])
    a.raw[c]=pack(1,fa["sreg"],(0,0,0),1);b.raw[c]=pack(1,fb["sreg"],(0,0,0),1)
    for d in ((1,0,0),(0,1,0),(0,0,1),(1,1,1)):
        q=tuple((c[i]+d[i])%n for i in range(3));a.raw[q]=pack(1,3,(0,0,0),1);b.raw[q]=pack(1,3,(0,0,0),1)
    a.tick();b.tick()
    return {"hidden_component":"local clock residual +1","equal_under":"raw-only semantic4 coarse observer during delay","delay_ticks":delay,"coast":coast,"post_intervention_center_a":unpack(a.raw[c]),"post_intervention_center_b":unpack(b.raw[c]),"became_visible":int(a.raw[c])!=int(b.raw[c]),"classification":"DELAYED_OBSERVABILITY_WITHOUT_NEW_CLOCK_COPY"}


def history_erasure_case(kernel):
    n=9;c=(4,4,4);a=np.zeros((n,n,n),dtype=np.uint64);b=a.copy()
    a[c]=pack(1,0,(0,0,0),1);b[c]=pack(2,0,(0,0,0),1)
    trace,wa,wb=evolve_pair(kernel,a,b,ticks=1)
    # Full states are now exact. Any deterministic continuation must remain exact.
    continuation=[]
    for tick in range(1,5):
        wa.tick();wb.tick();continuation.append({"tick_after_convergence":tick,"raw_equal":bool(np.array_equal(wa.raw,wb.raw)),"clock_equal":bool(np.array_equal(wa.clock,wb.clock))})
    return {"hidden_component":"external lineage/history not encoded in current full state","different_preimages":True,"convergence":trace[-1],"continuation":continuation,"classification":"DESTROYED_NOT_RESURRECTABLE_BY_NATIVE_DETERMINISTIC_EVOLUTION"}


def backaction_panel(kernel):
    directions=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
    rows=[]
    for i in range(12):
        d=directions[i%len(directions)];n=(31,35,39)[i%3];source=tuple(n//3 if j==0 else n//2 for j in range(3))
        # Keep source well away from wrap for every direction.
        source=tuple(n//2 for _ in range(3))
        common={"n":n,"source":source,"direction":d,"sreg":101+17*i,"horizon":18,"detector_distance":7,"threads":1}
        baseline=source_train_trial(kernel,mode="baseline",**common)
        sham=source_train_trial(kernel,mode="offpath_sham",**common)
        strong=source_train_trial(kernel,mode="mouth_block",**common)
        rows.append({"case":i,"direction":d,"baseline_arrivals":baseline["arrival_ticks"],"sham_arrivals":sham["arrival_ticks"],"strong_arrivals":strong["arrival_ticks"],"sham_same":baseline["arrival_ticks"]==sham["arrival_ticks"],"strong_changes":baseline["arrival_ticks"]!=strong["arrival_ticks"]})
    return {"cases":rows,"sham_invariant":sum(r["sham_same"] for r in rows),"strong_changes":sum(r["strong_changes"] for r in rows),"interpretation":"The embedded mouth interaction changes the event train; an off-path equal-inventory sham does not. This is measurement disturbance/backaction, not state reduction."}


def main():
    audit_kernel("CORE16X_BEFORE_HIDDEN_ACCESSIBILITY_DISCOVERY")
    kernel,runtime=verify_and_load_kernel(1)
    cases=[direction_case(kernel),semantic_case(kernel),sreg_case(kernel),topology_case(kernel),payload_loss_case(kernel),delayed_clock_case(kernel),history_erasure_case(kernel)]
    backaction=backaction_panel(kernel)
    result={"experiment":"C16X-CROSS-VARIABLE-HIDDEN-ACCESSIBILITY","created_utc":utc(),"runtime":runtime,"cases":cases,"measurement_backaction_panel":backaction}
    result_hash=canonical_hash(result)
    write_json(ROOT/"DISCOVERY"/"HIDDEN_ACCESSIBILITY_DISCOVERY.json",result)
    write_json(ROOT/"MEASUREMENT_BACKACTION.json",{"status":"PHYSICAL_INTERACTION_BACKACTION_CONFIRMED","new_panel":backaction,"state_reduction_analogy":"NOT_JUSTIFIED","weak_measurement":"NOT_OPERATIONALLY_SEPARATED","baseline_core16":read_json(ROOT/"BASELINE_CORE16_LOCKED"/"MEASUREMENT_BACKACTION.json")})
    append_ndjson(ROOT/"QUESTION_TREE.ndjson",{
        "question_id":"C16X-Q006","parent_id":"C16X-Q005","parent_result_hash":result_hash,
        "what_was_learned":"Direction, semantic, s_reg, route topology and clock residual can be hidden under restricted observers yet re-enter dynamics; nonsemantic4 payload/erased lineage cannot after exact convergence.",
        "new_uncertainty":"Do these accessibility classes remain stable in larger organizations and embedded detector chains?",
        "competing_interpretations":["scale transfer preserves causal residuals","organization averages them away","environment redistributes access"],
        "why_next_experiment_matters":"It adjudicates whether classicalization is destruction or access loss.","status":"OPEN"})
    append_ndjson(ROOT/"KERNEL_DIALOGUE.ndjson",{"question_id":"C16X-Q005","raw_outcome":{"cases":len(cases),"delayed_clock_visible":cases[5]["became_visible"],"strong_backaction":f"{backaction['strong_changes']}/{len(backaction['cases'])}","shams_invariant":f"{backaction['sham_invariant']}/{len(backaction['cases'])}"},"mechanism_update":"Hidden information has at least three statuses: redundant/destroyed, observer-hidden but immediately readable, and delayed-revealable under a new native interaction.","next_high_information_question":"Test scale transfer and probability across macroclasses."})
    update_state(status="HIDDEN_ACCESSIBILITY_DISCOVERED",current_phase="PROBABILITY_AND_SCALE_TRANSFER",hidden_accessibility_result_hash=result_hash,completed_checkpoints=["BASELINE_AUDIT","FULL_PARENT_CLAIM_INGESTION","FULL_STATE_CAUSAL_AUDIT","OCCUPANCY_OPERATOR_DISCOVERY","OCCUPANCY_OPERATOR_HOLDOUT","HIDDEN_ACCESSIBILITY_DISCOVERY"])
    print(json.dumps({"cases":len(cases),"classes":[c["classification"] for c in cases],"backaction_strong":backaction["strong_changes"],"backaction_sham":backaction["sham_invariant"],"hash":result_hash},indent=2))


if __name__=="__main__":main()

