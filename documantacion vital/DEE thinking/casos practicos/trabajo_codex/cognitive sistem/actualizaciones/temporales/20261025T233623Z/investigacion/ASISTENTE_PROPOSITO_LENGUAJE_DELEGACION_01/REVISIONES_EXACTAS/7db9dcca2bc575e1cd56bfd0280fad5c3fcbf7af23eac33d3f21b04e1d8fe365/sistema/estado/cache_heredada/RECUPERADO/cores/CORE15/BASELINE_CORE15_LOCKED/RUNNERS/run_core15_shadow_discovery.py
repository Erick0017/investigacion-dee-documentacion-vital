"""CORE15 discovery: empirical observer-equivalence and cross-phenomenon shadow search."""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core15_common import (
    ROOT,
    audit_kernel,
    experiment_key,
    read_json,
    record_dialogue,
    record_question,
    update_state,
    utc,
    write_json,
)
from native_core import NativeWorld, fields, pack, verify_and_load_kernel
from core12_apparatus import convergent_phase_paths, regenerative_interface_trial, source_train_trial
from run_c6h01_associative_plasticity_holdout import BASE as ASSOC_BASE, simulate as assoc_sim, transform as assoc_transform
from run_c6h08_dissipative_ensemble_holdout import DIRECTIONS, prepared_support, simulate as ensemble_sim


def add(q, d, k, n):
    return tuple((q[i] + k * d[i]) % n for i in range(3))


def unpack(value: np.uint64 | int | None):
    if value is None or int(value) == 0:
        return None
    raw = np.array([value], dtype=np.uint64)
    item = fields(raw)
    return {
        "state": int(item["state"][0]),
        "sreg": int(item["sreg"][0]),
        "direction": [int(item[k][0]) for k in ("dx", "dy", "dz")],
        "semantic": int(item["semantic"][0]),
    }


def sparse_state(world: NativeWorld) -> list[dict]:
    rows = []
    for coord in np.argwhere(world.raw != 0):
        q = tuple(int(x) for x in coord)
        rows.append({"q": list(q), "raw": int(world.raw[q]), "clock": int(world.clock[q]), **unpack(world.raw[q])})
    return rows


def trace_world(kernel, raw, clock, horizon):
    world = NativeWorld(kernel, raw, clock)
    rows = []
    for tick in range(horizon + 1):
        rows.append({"tick": tick, "active": sparse_state(world), "raw_hash": hashlib.sha256(world.raw.tobytes()).hexdigest(), "clock_hash": hashlib.sha256(world.clock.tobytes()).hexdigest()})
        if tick < horizon:
            world.tick()
    return rows


def direction_pair(kernel, n=31, seed=151001):
    rng = np.random.default_rng(seed)
    q = tuple(int(x) for x in rng.integers(7, n - 7, size=3))
    raw_a = np.zeros((n, n, n), np.uint64); raw_b = np.zeros_like(raw_a); clock = np.zeros_like(raw_a)
    raw_a[q] = pack(0xACE1, 137, (1, 0, 0), 1)
    raw_b[q] = pack(0xACE1, 137, (0, 1, 0), 1)
    ta, tb = trace_world(kernel, raw_a, clock, 3), trace_world(kernel, raw_b, clock, 3)
    occ_equal_t0 = [x["q"] for x in ta[0]["active"]] == [x["q"] for x in tb[0]["active"]]
    future_different = ta[1]["raw_hash"] != tb[1]["raw_hash"]
    return {"mechanism": "directed singleton transport", "n": n, "seed": seed, "initial_coordinate": list(q), "M_OCCUPANCY_equal_t0": occ_equal_t0, "hidden_difference": "direction", "future_raw_different": future_different, "trace_A": ta, "trace_B": tb, "predicate": occ_equal_t0 and future_different}


def reducer_payload_pair(kernel, n=33, distance=6, seed=151101):
    rng = np.random.default_rng(seed); center = tuple(int(x) for x in rng.integers(9, n - 9, size=3))
    def run(sregs):
        raw = np.zeros((n, n, n), np.uint64); clock = np.zeros_like(raw)
        qa, qb = add(center, (-1, 0, 0), distance, n), add(center, (1, 0, 0), distance, n)
        raw[qa] = pack(0xA, sregs[0], (1, 0, 0), 1); raw[qb] = pack(0xB, sregs[1], (-1, 0, 0), 1)
        world = NativeWorld(kernel, raw, clock); trace = []
        for tick in range(distance + 2):
            trace.append({"tick": tick, "center": unpack(world.raw[center]), "support": int(np.count_nonzero(world.raw))})
            if tick < distance + 1: world.tick()
        return trace, [list(qa), list(qb)]
    a, coords = run((101, 211)); b, _ = run((101, 307))
    ca = next((x["center"] for x in a if x["center"]), None); cb = next((x["center"] for x in b if x["center"]), None)
    return {"mechanism": "destination reducer", "n": n, "seed": seed, "center": list(center), "initial_coordinates": coords, "same_occupancy_direction_semantic": True, "hidden_difference": "s_reg", "center_A": ca, "center_B": cb, "trace_A": a, "trace_B": b, "predicate": ca is not None and cb is not None and ca["sreg"] != cb["sreg"]}


def semantic_pair(kernel, n=37, distance=9, seed=151201):
    rng = np.random.default_rng(seed); source = tuple(int(x) for x in rng.integers(8, n - 12, size=3)); direction = (1, 0, 0); detector = add(source, direction, distance, n)
    def run(semantic):
        raw = np.zeros((n, n, n), np.uint64); clock = np.zeros_like(raw); raw[source] = pack(0, 173, direction, semantic)
        world = NativeWorld(kernel, raw, clock); events=[]; source_present=[]
        for tick in range(distance + 10):
            if int(world.raw[detector]): events.append(tick)
            source_present.append(bool(world.raw[source]))
            world.tick()
        return {"events": events, "source_present": source_present}
    carrier, source_mode = run(1), run(4)
    return {"mechanism": "semantic source behavior", "n": n, "seed": seed, "source": list(source), "detector": list(detector), "same_occupancy_sreg_direction": True, "hidden_difference": "semantic", "semantic1": carrier, "semantic4": source_mode, "predicate": carrier != source_mode and len(source_mode["events"]) > len(carrier["events"])}


def clock_pair(kernel, n=31, horizon=12, seed=151301):
    rng=np.random.default_rng(seed); q=tuple(int(x) for x in rng.integers(7,n-7,size=3)); direction=(1,0,0)
    raw=np.zeros((n,n,n),np.uint64); raw[q]=pack(0x55AA,199,direction,1)
    c0=np.zeros_like(raw); c1=np.zeros_like(raw); c1[q]=np.uint64(0x123456789ABCDEF0)
    a,b=trace_world(kernel,raw,c0,horizon),trace_world(kernel,raw,c1,horizon)
    raw_equal=all(x["raw_hash"]==y["raw_hash"] for x,y in zip(a,b)); clock_different=any(x["clock_hash"]!=y["clock_hash"] for x,y in zip(a,b))
    return {"mechanism":"clock residual under singleton transport","n":n,"seed":seed,"same_full_raw_t0":True,"hidden_difference":"clock","raw_trajectory_equal":raw_equal,"clock_trajectory_different":clock_different,"horizon":horizon,"trace_A":a,"trace_B":b,"predicate":raw_equal and clock_different}


def guard_geometry_pair(kernel, n=43, seed=151401):
    rng=np.random.default_rng(seed); center=tuple(int(x) for x in rng.integers(12,n-12,size=3)); d=(1,0,0); h=31; L=9; sreg=331
    organized=regenerative_interface_trial(kernel,n,L,7,h,"semantic4_full",d,center,sreg)
    shuffled=regenerative_interface_trial(kernel,n,L,7,h,"semantic4_shuffled",d,center,sreg)
    org_events=organized["downstream_event_ticks"]["7"]; shuf_events=shuffled["downstream_event_ticks"]["7"]
    return {"mechanism":"semantic-topological guard interface","n":n,"seed":seed,"center":list(center),"same_inventory":True,"hidden_difference":"relative guard geometry","organized_detector_events":org_events,"shuffled_detector_events":shuf_events,"predicate":not org_events and bool(shuf_events),"organized":organized,"shuffled":shuffled}


def ensemble_direction_pair(kernel, n=20, fill=.42, seed=151501):
    rng=np.random.default_rng(seed); cap=(n//3)**3; count=max(8,int(round(cap*fill))); support=prepared_support(n,count,rng)
    sregs=[int(x) for x in rng.integers(1,8,size=count)]; clocks=[int(x) for x in rng.integers(0,2**32,size=count,dtype=np.uint64)]
    mixed=[DIRECTIONS[int(i)] for i in rng.integers(0,len(DIRECTIONS),size=count)]; aligned=[(1,0,0)]*count; horizon=5*n
    mt,_=ensemble_sim(kernel,n,support,sregs,clocks,mixed,horizon,False); at,exact=ensemble_sim(kernel,n,support,sregs,clocks,aligned,horizon,True)
    mixed_contract=mt[-1]["support"]<mt[0]["support"]; aligned_constant=at[-1]["support"]==at[0]["support"]
    return {"mechanism":"collision-sensitive ensemble","n":n,"fill":fill,"seed":seed,"same_support_sreg_semantic_clock":True,"hidden_difference":"direction distribution","mixed_trace":mt,"aligned_trace":at,"mixed_contracts":mixed_contract,"aligned_support_constant":aligned_constant,"aligned_translation_exact":exact,"predicate":mixed_contract and aligned_constant and exact}


def assoc_cell(index,n,delay,seed):
    rng=np.random.default_rng(seed); junction=tuple(int(x) for x in rng.integers(9,n-9,size=3)); frame=((index%3,(index+1)%3,(index+2)%3),(1,-1 if index%2 else 1,1))
    vectors={k:list(assoc_transform(v,*frame)) for k,v in ASSOC_BASE.items()}
    return {"cell_id":f"C15D{index}","n":n,"junction":list(junction),"train_tick":4+index%3,"delay":delay,"query_path":3,"vectors":vectors,"cue_sreg":7+index,"teacher_sreg":13+index,"query_sreg":19+index,"eraser_sreg":23,"states":[int(x) for x in rng.integers(1,2**32,size=4,dtype=np.uint64)],"clocks":[int(rng.bit_generator.random_raw()) for _ in range(4)]}


def associative_history_pair(kernel, n=43, delay=13, seed=151601):
    cell=assoc_cell(1,n,delay,seed); modes=["trained_pair","history_shuffled","memory_ablation"]
    rows=[assoc_sim(kernel,cell,mode) for mode in modes]; by={row["mode"]:row for row in rows}
    predicate=by["trained_pair"]["trained_exact"] and not by["history_shuffled"]["trained_exact"] and not by["memory_ablation"]["trained_exact"]
    return {"mechanism":"associative history-bearing lineage","n":n,"delay":delay,"seed":seed,"same_query_and_endpoint_observer":"query preparation matched; training/history differs","hidden_difference":"ordered causal history/lineage","rows":rows,"predicate":bool(predicate)}


def phase_pair(kernel, n=45, L=8, seed=151701):
    rng=np.random.default_rng(seed); center=tuple(int(x) for x in rng.integers(12,n-12,size=3)); sregs=(109,223)
    coherent=convergent_phase_paths(kernel,n,L,"AB_coherent",center,sregs,L+12,(0,1,2)); shifted=convergent_phase_paths(kernel,n,L,"AB_phase_shifted",center,sregs,L+12,(0,1,2))
    different=(coherent["detector_event_ticks"],coherent["detector_event_sregs"])!=(shifted["detector_event_ticks"],shifted["detector_event_sregs"])
    return {"mechanism":"phase/history-conditioned convergent routes","n":n,"seed":seed,"center":list(center),"same_paths_inventory":True,"hidden_difference":"relative parity/history","coherent_events":{"ticks":coherent["detector_event_ticks"],"sregs":coherent["detector_event_sregs"]},"shifted_events":{"ticks":shifted["detector_event_ticks"],"sregs":shifted["detector_event_sregs"]},"predicate":different,"coherent":coherent,"shifted":shifted}


def run_module(kernel, module_id, question, mechanism, preparation, observer, intervention, region, fn, alternatives):
    key=experiment_key(question,mechanism,preparation,observer,intervention,region)
    record_question(question_id=module_id,parent_question_id=None,front="OBSERVER_SHADOW",question=question,mechanism_class=mechanism,current_uncertainty=alternatives,why_high_information="Creates an explicit observer-equivalence pair and applies a matched future interaction.",positive_meaning="Hidden coordinate is causally required in this domain.",negative_meaning="The hidden coordinate is irrelevant within this interaction/horizon.",experiment=preparation,observer=observer,intervention=intervention,parameter_region=region,experiment_key=key,status="DISCOVERY_OPEN")
    started=time.perf_counter(); result=fn(); result.update({"module_id":module_id,"experiment_key":key,"role":"DISCOVERY","elapsed_seconds":time.perf_counter()-started})
    write_json(ROOT/"RESULTS"/(module_id+".json"),result)
    record_dialogue(question_id=module_id,question=question,apparatus=preparation,kernel_response={"predicate":result.get("predicate"),"mechanism":result.get("mechanism")},simpler_explanation=alternatives,next_discriminating_question="Freeze only if reproduced across fresh worlds; otherwise retain as bounded discovery.",evidence_level="DISCOVERY")
    return result,{"module_id":module_id,"experiment_key":key,"question":question,"mechanism_class":mechanism,"preparation_family":preparation,"observer_family":observer,"intervention":intervention,"parameter_region":region,"status":"DISCOVERY_COMPLETE","predicate":bool(result.get("predicate"))}


def main():
    marker=ROOT/"RESULTS"/"C15D00_SHADOW_DISCOVERY_SUMMARY.json"
    if marker.exists(): print(marker.read_text(encoding="utf-8")); return
    audit_kernel("CORE15_BEFORE_DISCOVERY"); kernel,environment=verify_and_load_kernel(1); write_json(ROOT/"RUNTIME_ENVIRONMENT.json",environment)
    specs=[
      ("C15D01_DIRECTION","Can occupancy alone predict the next state of a localized event?","MC_DIRECTED_SINGLETON","same occupied coordinate/payload, two directions","M_OCCUPANCY vs M_KINEMATIC","native evolution","N31 interior",lambda:direction_pair(kernel),"geometry/age-only null"),
      ("C15D02_PAYLOAD","Can occupancy and direction predict a simultaneous destination reduction?","MC_DESTINATION_REDUCER","matched convergent carriers, different s_reg","M_KINEMATIC vs M_REL","same collision","N33 distance6",lambda:reducer_payload_pair(kernel),"inventory-free reducer null"),
      ("C15D03_SEMANTIC","Can occupancy, direction and s_reg predict source persistence and event trains?","MC_SEMANTIC_SOURCE","same source record except semantic","M_REL without/with semantic","native propagation","N37 distance9",lambda:semantic_pair(kernel),"single-carrier and source-equivalent null"),
      ("C15D04_CLOCK","Does a raw-identical local clock difference become visible to singleton transport?","MC_CLOCK_RESIDUAL","same complete raw, different source clock","M_REL vs M_CLOCK_RESIDUAL","native singleton evolution","N31 horizon12",lambda:clock_pair(kernel),"clock-as-universal-behavioral-coordinate vs inert residual"),
      ("C15D05_GEOMETRY","Does equal inventory predict interface capture without relational geometry?","MC_GUARD_INTERFACE","organized versus shuffled semantic4 equal inventory","M_INVENTORY vs M_INTERFACE","period-two incident train","N43 fresh center",lambda:guard_geometry_pair(kernel),"inventory-only and passive-center nulls"),
      ("C15D06_DIRECTION_DISSIPATION","Does equal support/payload predict ensemble relaxation without direction distribution?","MC_COLLISION_ENSEMBLE","same support/sreg/semantic/clock, aligned versus mixed directions","M_BULK vs M_REL","native ensemble evolution","N20 fill0.42",lambda:ensemble_direction_pair(kernel),"dose-only and support-only nulls"),
      ("C15D07_HISTORY","Does current query/endpoint state predict response without ordered causal history?","MC_ASSOCIATIVE_LINEAGE","trained, shuffled-history and mediator-ablation worlds","M_EVENT vs M_HISTORY","fresh identical query","N43 delay13",lambda:associative_history_pair(kernel),"query-only and geometry-only nulls"),
      ("C15D08_PHASE","Do equal routes/inventory predict the detector record without relative phase/history?","MC_PHASE_PATH","coherent versus one-tick-shifted convergent routes","M_TRANSPORT vs M_EVENT_CAUSAL","same detector","N45 L8",lambda:phase_pair(kernel),"independent-path and inventory-only nulls"),
    ]
    results={}; experiments=[]
    for spec in specs:
        result,row=run_module(kernel,*spec); results[spec[0]]=result; experiments.append(row)
    passed=sum(bool(x["predicate"]) for x in results.values())
    summary={"module":"C15D00_SHADOW_DISCOVERY_SUMMARY","role":"DISCOVERY","modules":len(results),"positive_predicates":passed,"all_experiment_keys_unique":len({x['experiment_key'] for x in experiments})==len(experiments),"clock_result":"FUNCTIONALLY_INVISIBLE_WITHIN_SINGLETON_PANEL" if results["C15D04_CLOCK"]["predicate"] else "CLOCK_AFFECTS_RAW_TRAJECTORY_OR_TRACE_NOT_PRESERVED","candidate_components":["route/geometry","direction field","s_reg payload","semantic/source class","relative phase","target history","guard topology","ordered lineage","coupling context"],"provisional_shadow":"small coupled family of task-relative causal observers; no universal scalar","completed_utc":utc()}
    write_json(marker,summary); write_json(ROOT/"EXPERIMENT_REGISTRY.json",{"experiments":experiments,"unique":summary["all_experiment_keys_unique"]})
    write_json(ROOT/"DISCOVERY_FLEXIBILITY_LEDGER.json",{"observer_families_inspected":["M_OCCUPANCY","M_KINEMATIC","M_BULK","M_REL","M_EVENT_CAUSAL","M_INTERFACE","M_HISTORY","M_CLOCK_RESIDUAL"],"combinations_inspected":8,"adaptive_thresholds":0,"adaptive_sign_flips":0,"post_result_probe_design":0,"discovery_modules":len(results),"selection_use":"observer freeze only; none are confirmation"})
    update_state(status="DISCOVERY_COMPLETE",completed_modules=["C15A01","C15D00"],last_completed="C15D00_SHADOW_DISCOVERY_SUMMARY",experiments_executed=len(results))
    audit_kernel("CORE15_AFTER_DISCOVERY"); print(json.dumps(summary,indent=2))


if __name__=="__main__": main()
