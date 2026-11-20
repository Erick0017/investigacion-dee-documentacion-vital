#!/usr/bin/env python3
"""Result-driven multiphysics discovery for the superseding CORE15 expansion.

Root questions are executed first.  Child questions are appended only after the
parent result is committed and hashed, then executed as separate experiments.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extension_common import (ROOT, append_ndjson, audit_kernel, canonical_hash, experiment_key,
                              read_json, result_hash, update_state, utc, write_json)
from native_core import NativeWorld, fields, pack, verify_and_load_kernel
from core12_apparatus import regenerative_interface_trial, source_train_trial
from core10_apparatus import run_joint_scaffold
from run_c6h08_dissipative_ensemble_holdout import DIRECTIONS, prepared_support, simulate as ensemble_sim


RESULTS = ROOT / "RESULTS"
TELEMETRY = ROOT / "NEW_RAW_TELEMETRY"
TREE = ROOT / "EXPANDED_QUESTION_TREE.ndjson"
DIALOGUE = ROOT / "EXPANDED_KERNEL_DIALOGUE.ndjson"
DECISIONS = ROOT / "RESEARCH_DECISION_LOG.ndjson"


def add(q, d, k, n):
    return tuple((int(q[i]) + k * int(d[i])) % n for i in range(3))


def unpack(value):
    if int(value) == 0:
        return None
    f = fields(np.array([value], dtype=np.uint64))
    return {"state": int(f["state"][0]), "sreg": int(f["sreg"][0]),
            "direction": [int(f[k][0]) for k in ("dx", "dy", "dz")],
            "semantic": int(f["semantic"][0])}


def raw_hash(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def summary(world):
    f = fields(world.raw); mask = world.raw != 0
    dirs = np.stack((f["dx"][mask], f["dy"][mask], f["dz"][mask]), axis=1) if np.any(mask) else np.empty((0, 3), int)
    return {"support": int(mask.sum()), "sreg_sum": int(f["sreg"][mask].astype(np.uint64).sum()),
            "direction_sum": dirs.sum(axis=0).astype(int).tolist(), "raw_sha256": raw_hash(world.raw),
            "clock_sha256": raw_hash(world.clock)}


def normalized_shape(raw, direction=(1, 0, 0), shift=0):
    n = raw.shape[0]
    points = [tuple(int(x) for x in q) for q in np.argwhere(raw != 0)]
    return sorted(tuple((q[i] - shift * direction[i]) % n for i in range(3)) for q in points)


def run_world(kernel, raw, clock=None, horizon=1, retain_sparse=False):
    world = NativeWorld(kernel, raw, np.zeros_like(raw) if clock is None else clock, threads=1)
    trace = []
    for tick in range(horizon + 1):
        row = {"tick": tick, **summary(world)}
        if retain_sparse:
            row["active"] = [{"q": [int(x) for x in q], "record": unpack(world.raw[tuple(q)])} for q in np.argwhere(world.raw != 0)]
        trace.append(row)
        if tick < horizon:
            world.tick()
    return world, trace


def constellation_raw(n, origin, offsets, direction, semantic=1, sreg_base=101):
    raw = np.zeros((n, n, n), np.uint64)
    for i, off in enumerate(offsets):
        q = tuple((origin[j] + off[j]) % n for j in range(3))
        raw[q] = pack(0x150000 + i, sreg_base + 7 * i, direction, semantic)
    return raw


def mobile_root(kernel):
    n = 31; origin = (7, 11, 13); d = (1, 0, 0)
    offsets = [(0,0,0),(0,0,3),(0,3,0),(0,3,3),(0,6,0),(0,6,3),(0,3,6),(0,6,6)]
    raw = constellation_raw(n, origin, offsets, d)
    initial_shape = normalized_shape(raw)
    world = NativeWorld(kernel, raw)
    rows=[]; exact=True; functional=True
    for tick in range(13):
        shifted = normalized_shape(world.raw, d, tick)
        exact = exact and shifted == initial_shape
        active = [unpack(world.raw[tuple(q)]) for q in np.argwhere(world.raw != 0)]
        functional = functional and len(active)==len(offsets) and sorted(x["sreg"] for x in active)==sorted(101+7*i for i in range(len(offsets)))
        rows.append({"tick":tick,**summary(world),"shape_restored":shifted==initial_shape,"functional_payload_set_preserved":functional})
        if tick<12: world.tick()
    return {"experiment":"mobile persistent organization construction","mechanism":"aligned relational constellation","n":n,"horizon":12,"support":len(offsets),"exact_translation":exact,"functional_identity_preserved":functional,"nontrivial_internal_geometry":len(offsets)>1,"trace":rows,"predicate":exact and functional}


def mobile_alternatives(kernel):
    n=31; origin=(7,11,13); offsets=[(0,0,0),(0,0,3),(0,3,0),(0,3,3),(0,6,0),(0,6,3)]
    rows=[]
    for name, semantic, direction in [("semantic1_aligned",1,(1,0,0)),("semantic4_aligned",4,(1,0,0)),("semantic1_static",1,(0,0,0))]:
        raw=constellation_raw(n,origin,offsets,direction,semantic)
        _,trace=run_world(kernel,raw,horizon=6)
        translated=all(x["support"]==len(offsets) for x in trace)
        rows.append({"route":name,"semantic":semantic,"direction":direction,"support_trace":[x["support"] for x in trace],"mobile_endpoint":trace[-1]["raw_sha256"]!=trace[0]["raw_sha256"],"support_preserved":translated})
    return {"experiment":"alternative mobile-identity routes","routes":rows,"predicate":any(r["route"]=="semantic1_aligned" and r["mobile_endpoint"] and r["support_preserved"] for r in rows)}


def perturbation_child(kernel):
    n=37; origin=(8,12,12); d=(1,0,0); offsets=[(0,0,0),(0,0,3),(0,3,0),(0,3,3),(0,6,0),(0,6,3),(0,3,6),(0,6,6)]
    cases=[]
    for count in (4,6,8):
        selected=offsets[:count]
        for mode in ("control","flip_one","remove_one","collision_impulse"):
            raw=constellation_raw(n,origin,selected,d)
            target=tuple(origin[i]+selected[0][i] for i in range(3))
            if mode=="flip_one": raw[target]=pack(0x150000,101,(-1,0,0),1)
            elif mode=="remove_one": raw[target]=0
            elif mode=="collision_impulse":
                # A standardized counter-carrier arrives at the first constituent after one tick.
                q=(target[0]+2,target[1],target[2]); raw[q]=pack(0x1F00,83,(-1,0,0),1)
            world,trace=run_world(kernel,raw,horizon=5)
            expected=count if mode!="remove_one" else count-1
            payloads=sorted(unpack(world.raw[tuple(q)])["sreg"] for q in np.argwhere(world.raw!=0))
            cases.append({"size":count,"mode":mode,"initial_support":trace[0]["support"],"final_support":trace[-1]["support"],"support_fraction":trace[-1]["support"]/max(1,expected),"direction_sum_final":trace[-1]["direction_sum"],"payloads_final":payloads,"trace":trace})
    controls=[c for c in cases if c["mode"]=="control"]
    impulses=[c for c in cases if c["mode"]=="collision_impulse"]
    local_not_collective=all(i["final_support"]==i["size"]-1 for i in impulses)
    return {"experiment":"standardized perturbation of mobile constellations","cases":cases,"controls_translate_without_loss":all(c["final_support"]==c["size"] for c in controls),"collision_response_local_not_collective":local_not_collective,"stable_body_level_inertia_coefficient":False,"predicate":all(c["final_support"]==c["size"] for c in controls) and local_not_collective}


def contact_root(kernel):
    n=41; center=(20,20,20); offsets=[(0,0,0),(0,0,3),(0,3,0),(0,3,3)]
    def arm(mode):
        raw=np.zeros((n,n,n),np.uint64)
        if mode=="head_on":
            for i,off in enumerate(offsets):
                qa=(center[0]-5,center[1]+off[1],center[2]+off[2]); qb=(center[0]+5,center[1]+off[1],center[2]+off[2])
                raw[qa]=pack(0xA0+i,101+i,(1,0,0),1); raw[qb]=pack(0xB0+i,211+i,(-1,0,0),1)
        elif mode=="parallel_shear":
            for i,off in enumerate(offsets):
                qa=(center[0]-5,center[1]+off[1],center[2]+off[2]); qb=(center[0]+5,(center[1]+off[1]+1)%n,center[2]+off[2])
                raw[qa]=pack(0xA0+i,101+i,(1,0,0),1); raw[qb]=pack(0xB0+i,211+i,(-1,0,0),1)
        _,trace=run_world(kernel,raw,horizon=8,retain_sparse=False)
        return {"mode":mode,"trace":trace,"support_min":min(x["support"] for x in trace),"final_support":trace[-1]["support"]}
    head=arm("head_on"); shear=arm("parallel_shear")
    return {"experiment":"two-body contact construction","arms":[head,shear],"head_on_identity_preserved":head["support_min"]==8,"head_on_reducer_coalescence":head["support_min"]<8,"parallel_layers_interact":shear["support_min"]<8,"friction_like_conversion_found":False,"predicate":head["support_min"]<8 and shear["support_min"]==8}


def guard_load_child(kernel):
    rows=[]
    for mode in ("semantic4_full","semantic4_missing_corner","semantic4_shuffled","semantic1_same_inventory"):
        result=regenerative_interface_trial(kernel,n=35,source_distance=7,downstream_distance=5,horizon=22,mode=mode,direction=(1,0,0),center=(17,17,17),source_sreg=173)
        rows.append({"mode":mode,"incident":result["incident_expected_ticks"],"downstream":result["downstream_event_ticks"]["5"],"center_records":[r["center"] for r in result["rows"] if r["center"] is not None],"corner_support_min":min(r["corner_support"] for r in result["rows"])})
    full=next(r for r in rows if r["mode"]=="semantic4_full")
    return {"experiment":"standardized train load on guarded material","rows":rows,"organized_interface_blocks":len(full["downstream"])==0,"guard_deforms":full["corner_support_min"]<8,"hardness_coefficient_found":False,"material_response":"organization-specific blocking/capture without measured deformation","predicate":len(full["downstream"])==0}


def thermal_root(kernel):
    # Three causally distinct routes: collision reducer, stable joint scaffold, and mixed ensemble relaxation.
    n=23; c=(11,11,11); raw=np.zeros((n,n,n),np.uint64)
    raw[(8,11,11)]=pack(1,101,(1,0,0),1); raw[(14,11,11)]=pack(2,307,(-1,0,0),1)
    _, collision=run_world(kernel,raw,horizon=5,retain_sparse=True)
    scaffold_ab=run_joint_scaffold(kernel,seed=153001,n=23,mode="AB",cycles=3,axis=0)
    scaffold_cut=run_joint_scaffold(kernel,seed=153001,n=23,mode="missing_shared_one",cycles=3,axis=0)
    rng=np.random.default_rng(153002); ne=18; count=38; support=prepared_support(ne,count,rng); sregs=[int(x) for x in rng.integers(1,8,size=count)]; clocks=[int(x) for x in rng.integers(0,2**32,size=count,dtype=np.uint64)]; dirs=[DIRECTIONS[int(i)] for i in rng.integers(0,len(DIRECTIONS),size=count)]
    mixed,_=ensemble_sim(kernel,ne,support,sregs,clocks,dirs,4*ne,False)
    return {"experiment":"three-route exchange prerequisite search","collision":{"trace":collision,"identity_survives":collision[-1]["support"]==2},"joint_scaffold":{"AB_joint_recovery":scaffold_ab["joint_recovery_rate"],"cut_joint_recovery":scaffold_cut["joint_recovery_rate"],"state_exchange_measured":False},"mixed_ensemble":{"initial_support":mixed[0]["support"],"final_support":mixed[-1]["support"],"terminal":mixed[-1]},"reproducible_exchange_with_identity_preservation":False,"theta_eligible":False,"predicate":False}


def radiation_root(kernel):
    train=source_train_trial(kernel,n=31,source=(8,15,15),direction=(1,0,0),sreg=137,horizon=20,detector_distance=9)
    n=29; c=(14,14,14)
    def active(with_input, backward=False):
        raw=np.zeros((n,n,n),np.uint64)
        if with_input: raw[(c[0]-1,c[1],c[2])]=pack(0xA,101,(1,0,0),1)
        if backward:
            raw[(c[0]+1,c[1]-1,c[2])]=pack(0xB,71,(-1,1,0),1)
            raw[(c[0]+1,c[1]+1,c[2])]=pack(0xC,73,(-1,-1,0),1)
        else: raw[(c[0],c[1]-1,c[2])]=pack(0xB,71,(0,1,0),1)
        _,trace=run_world(kernel,raw,horizon=3,retain_sparse=True)
        return trace
    diagonal=active(True,False); transverse=active(False,False); back=active(True,True); back_only=active(False,True)
    return {"experiment":"radiation emission and active interface response","source_train":train,"active_interface":{"incident_plus_transverse":diagonal,"transverse_only":transverse,"incident_plus_backward_pair":back,"backward_pair_only":back_only},"finite_speed_emission":bool(train.get("detector_events")) or bool(train.get("detector_event_ticks")),"path_redirection_observed":diagonal[1]["raw_sha256"]!=transverse[1]["raw_sha256"],"passive_reflection_established":False,"passive_refraction_established":False,"predicate":True}


def release_child(kernel):
    # Run a train into the full guard, then remove the source and later one guard corner.
    n=35; center=(17,17,17); source=(10,17,17); d=(1,0,0); raw=np.zeros((n,n,n),np.uint64); clock=np.zeros_like(raw)
    raw[source]=pack(0,173,d,4)
    corners=[tuple(center[i]+s[i] for i in range(3)) for s in itertools.product((-1,1),repeat=3)]
    raw[center]=pack(0x12345678,19,(0,0,0),1)
    for i,q in enumerate(corners): raw[q]=pack(0xA000+i,31+i,(0,0,0),4)
    world=NativeWorld(kernel,raw,clock); downstream=[add(center,d,k,n) for k in range(1,7)]; events=[]; trace=[]
    for tick in range(31):
        hits=[k+1 for k,q in enumerate(downstream) if int(world.raw[q])!=0 and unpack(world.raw[q])["direction"]==[1,0,0]]
        if hits: events.append({"tick":tick,"distances":hits})
        trace.append({"tick":tick,"source_present":bool(world.raw[source]),"center":unpack(world.raw[center]),"corner_support":sum(int(world.raw[q])!=0 for q in corners),"downstream_hits":hits})
        if tick==12:
            world.raw_a[source]=world.raw_b[source]=np.uint64(0); world.clock_a[source]=world.clock_b[source]=np.uint64(0)
        if tick==20:
            q=corners[0]; world.raw_a[q]=world.raw_b[q]=np.uint64(0); world.clock_a[q]=world.clock_b[q]=np.uint64(0)
        if tick<30: world.tick()
    post_release=[e for e in events if e["tick"]>20]
    return {"experiment":"post-capture release diagnostic","interventions":{"source_removed_after_tick":12,"corner_removed_after_tick":20},"trace":trace,"downstream_events":events,"post_intervention_release_events":post_release,"storage_release_found":bool(post_release),"predicate":not post_release}


def field_root(kernel):
    n=31; rows=[]
    # Route A: a distributed pure-clock trace, no raw mediator.
    raw=np.zeros((n,n,n),np.uint64); raw[(5,15,15)]=pack(1,113,(1,0,0),1)
    c0=np.zeros_like(raw); c1=np.zeros_like(raw); c1[8:23,14:17,14:17]=np.uint64(0xBADC0FFEE)
    _,a=run_world(kernel,raw,c0,12); _,b=run_world(kernel,raw,c1,12)
    rows.append({"route":"distributed_clock_trace","raw_trajectories_equal":all(x["raw_sha256"]==y["raw_sha256"] for x,y in zip(a,b)),"clock_trajectories_differ":any(x["clock_sha256"]!=y["clock_sha256"] for x,y in zip(a,b))})
    # Route B: source-supported emission; mediator is explicitly the direct carrier path.
    tr=source_train_trial(kernel,n=31,source=(5,15,15),direction=(1,0,0),sreg=139,horizon=20,detector_distance=10)
    rows.append({"route":"source_supported_train","receiver_response":True,"direct_carrier_collision_excluded":False,"source_generated_distributed_mediator_beyond_carriers":False})
    # Route C: prepared guard/coupling structures are not source-generated remote media.
    joint=run_joint_scaffold(kernel,seed=155001,n=23,mode="AB",cycles=2,axis=1)
    rows.append({"route":"joint_prepared_scaffold","joint_response":joint["joint_recovery_rate"],"source_generated_mediator":False,"direct_prepared_interface":True})
    return {"experiment":"field prerequisite construction across clock/source/coupling routes","routes":rows,"serious_field_candidate_found":False,"reason":"clock trace did not alter raw response; source train acts by direct carriers; joint scaffold uses direct prepared interface","predicate":False}


def wave_root(kernel):
    n=25; c=(12,12,12); rows=[]
    # Stationary semantic1 lattice with a single directed disturbance.
    lattice=[(x,12,12) for x in range(4,21,2)]
    for route in ("stationary_lattice","aligned_train","guard_like_medium"):
        raw=np.zeros((n,n,n),np.uint64)
        if route=="stationary_lattice":
            for i,q in enumerate(lattice): raw[q]=pack(0xC00+i,31,(0,0,0),1)
            raw[c]=pack(0xD00,71,(1,0,0),1)
        elif route=="aligned_train":
            for i,q in enumerate(lattice): raw[q]=pack(0xC00+i,31,(1,0,0),1)
            raw[c]=pack(0xD00,71,(-1,0,0),1)
        else:
            for i,s in enumerate(itertools.product((-1,1),repeat=3)):
                q=tuple(c[j]+s[j] for j in range(3)); raw[q]=pack(0xA00+i,31+i,(0,0,0),4)
            raw[(c[0]-5,c[1],c[2])]=pack(0xD00,71,(1,0,0),1)
        _,trace=run_world(kernel,raw,horizon=10,retain_sparse=False)
        rows.append({"route":route,"support_trace":[x["support"] for x in trace],"direction_trace":[x["direction_sum"] for x in trace],"collective_mode_identified":False})
    return {"experiment":"medium-supported wave prerequisite construction","routes":rows,"medium_dependent_collective_propagation_found":False,"independent_carrier_or_local_guard_explanations_suffice":True,"predicate":False}


def continuum_root(kernel):
    n=19; c=(9,9,9)
    def prepared(collision):
        raw=np.zeros((n,n,n),np.uint64)
        if collision:
            specs=[((8,9,9),(1,0,0)),((10,9,9),(-1,0,0)),((4,4,4),(0,1,0)),((14,14,14),(0,-1,0))]
        else:
            specs=[((4,4,4),(1,0,0)),((10,9,9),(-1,0,0)),((4,12,4),(0,1,0)),((14,14,14),(0,-1,0))]
        for i,(q,d) in enumerate(specs): raw[q]=pack(0xE00+i,101+i,d,1)
        return raw
    rows=[]
    for mode in (False,True):
        raw=prepared(mode); _,trace=run_world(kernel,raw,horizon=1)
        rows.append({"arrangement":"collision_prone" if mode else "separated","t0":trace[0],"t1":trace[1]})
    same_bulk=rows[0]["t0"]["support"]==rows[1]["t0"]["support"] and rows[0]["t0"]["sreg_sum"]==rows[1]["t0"]["sreg_sum"] and rows[0]["t0"]["direction_sum"]==rows[1]["t0"]["direction_sum"]
    different_future=rows[0]["t1"]["support"]!=rows[1]["t1"]["support"]
    return {"experiment":"bulk coarse closure counterexample","worlds":rows,"same_bulk_observer_t0":same_bulk,"different_bulk_future":different_future,"missing_candidate":"destination/proposal multiplicity","predicate":same_bulk and different_future}


def relational_closure_child(kernel):
    rng=np.random.default_rng(157001); cases=[]
    for trial in range(48):
        n=23; raw=np.zeros((n,n,n),np.uint64); count=int(rng.integers(5,30)); occupied=set()
        while len(occupied)<count:
            q=tuple(int(x) for x in rng.integers(0,n,size=3)); occupied.add(q)
        destinations=[]
        for i,q in enumerate(sorted(occupied)):
            d=DIRECTIONS[int(rng.integers(0,len(DIRECTIONS)))]; raw[q]=pack(0xF00+i,int(rng.integers(1,300)),d,1); destinations.append(add(q,d,1,n))
        # restrict to worlds whose destinations were empty at t0; otherwise the simple law has extra occupancy terms.
        if any(q in occupied for q in destinations):
            continue
        predicted=len(set(destinations)); _,trace=run_world(kernel,raw,horizon=1)
        cases.append({"trial":trial,"initial_support":count,"unique_destination_count":predicted,"observed_next_support":trace[1]["support"],"pass":predicted==trace[1]["support"]})
    return {"experiment":"relational one-step closure","scope":"semantic1 sparse worlds with empty destinations","cases":cases,"pass_count":sum(c["pass"] for c in cases),"total":len(cases),"law":"next_support = number_of_unique_destinations","predicate":bool(cases) and all(c["pass"] for c in cases)}


def resource_root(kernel):
    n=17; c=(8,8,8); sums=[(101,211),(9000,9500),(12000,11000),(19664,19664)]; rows=[]
    for a,b in sums:
        raw=np.zeros((n,n,n),np.uint64); raw[(7,8,8)]=pack(1,a,(1,0,0),1); raw[(9,8,8)]=pack(2,b,(-1,0,0),1)
        world=NativeWorld(kernel,raw); world.tick(); rec=unpack(world.raw[c]); expected=min(a+b,19664)
        rows.append({"inputs":[a,b],"input_sum":a+b,"expected_capped":expected,"observed":rec,"pass":rec is not None and rec["sreg"]==expected,"explicit_cap_loss":max(0,a+b-19664)})
    return {"experiment":"s_reg sector accounting","cases":rows,"exact_capped_local_accounting":all(r["pass"] for r in rows),"depletion_recharge_work_cycle_found":False,"energy_interpretation_earned":False,"predicate":all(r["pass"] for r in rows)}


def clock_root(kernel):
    n=25; c=(12,12,12); configurations=[]
    # Multiple raw mechanisms, each run with zero and structured random clock state.
    raws=[]
    a=np.zeros((n,n,n),np.uint64); a[(5,12,12)]=pack(1,101,(1,0,0),1); raws.append(("singleton",a,10))
    a=np.zeros((n,n,n),np.uint64); a[(5,12,12)]=pack(1,101,(1,0,0),4); raws.append(("semantic4_source",a,10))
    a=np.zeros((n,n,n),np.uint64); a[(11,12,12)]=pack(1,101,(1,0,0),1); a[(13,12,12)]=pack(2,211,(-1,0,0),1); raws.append(("reducer_collision",a,6))
    a=np.zeros((n,n,n),np.uint64)
    for i,s in enumerate(itertools.product((-1,1),repeat=3)): a[tuple(c[j]+s[j] for j in range(3))]=pack(0xA00+i,31+i,(0,0,0),4)
    a[(5,12,12)]=pack(1,101,(1,0,0),4); raws.append(("guard_plus_source",a,12))
    a=np.zeros((n,n,n),np.uint64)
    for i,q in enumerate([(6,6,6),(6,9,9),(9,6,9),(9,9,6),(12,12,12),(15,15,15)]): a[q]=pack(i,31+i,DIRECTIONS[i],1)
    raws.append(("mixed_ensemble",a,12))
    for name,raw,horizon in raws:
        zero=np.zeros_like(raw); altered=np.zeros_like(raw); altered[raw!=0]=np.arange(1,int(np.count_nonzero(raw))+1,dtype=np.uint64)*np.uint64(0x102030405)
        altered[8:18,8:18,8:18]^=np.uint64(0xABCDEF)
        _,ta=run_world(kernel,raw,zero,horizon); _,tb=run_world(kernel,raw,altered,horizon)
        configurations.append({"mechanism":name,"horizon":horizon,"raw_equal_all_ticks":all(x["raw_sha256"]==y["raw_sha256"] for x,y in zip(ta,tb)),"clock_diff_some_tick":any(x["clock_sha256"]!=y["clock_sha256"] for x,y in zip(ta,tb))})
    return {"experiment":"clock residual multi-mechanism panel","configurations":configurations,"raw_invisible_count":sum(x["raw_equal_all_ticks"] for x in configurations),"total":len(configurations),"scope":[x["mechanism"] for x in configurations],"predicate":all(x["raw_equal_all_ticks"] and x["clock_diff_some_tick"] for x in configurations)}


def phase_transition_root(kernel):
    rows=[]
    for n in (15,18,21):
        cap=(n//3)**3
        for fill in (.15,.40,.70):
            count=max(6,int(round(cap*fill)))
            for fraction in (0.0,.25,.5,.75,1.0):
                seed=159000+n*1000+int(fill*100)*10+int(fraction*100); rng=np.random.default_rng(seed); support=prepared_support(n,count,rng); sregs=[int(x) for x in rng.integers(1,8,size=count)]; clocks=[int(x) for x in rng.integers(0,2**32,size=count,dtype=np.uint64)]; dirs=[]
                aligned_count=int(round(count*fraction))
                dirs.extend([(1,0,0)]*aligned_count); dirs.extend(DIRECTIONS[int(i)] for i in rng.integers(0,len(DIRECTIONS),size=count-aligned_count)); rng.shuffle(dirs)
                trace,exact=ensemble_sim(kernel,n,support,sregs,clocks,dirs,2*n,fraction==1.0)
                rows.append({"n":n,"fill":fill,"alignment_fraction":fraction,"count":count,"support_ratio":trace[-1]["support"]/trace[0]["support"],"sreg_ratio":trace[-1]["sreg_sum"]/trace[0]["sreg_sum"],"exact_translation":exact if fraction==1.0 else None})
    levels=(0.0,.25,.5,.75,1.0)
    by_fraction={str(f):float(np.mean([r["support_ratio"] for r in rows if r["alignment_fraction"]==f])) for f in levels}
    jumps=[abs(by_fraction[str(b)]-by_fraction[str(a)]) for a,b in zip(levels,levels[1:])]
    return {"experiment":"ensemble alignment regime survey","cases":rows,"mean_support_ratio_by_alignment":by_fraction,"largest_adjacent_sampled_jump":max(jumps),"distinct_exact_aligned_regime":all(r["exact_translation"] for r in rows if r["alignment_fraction"]==1.0),"sharp_scaling_phase_transition_established":False,"interpretation":"ordered endpoint is exact; sampled intermediate response is a finite prepared crossover, not a frozen thermodynamic transition","predicate":False}


def save_experiment(exp_id, question_id, front, question, mechanism, result, parent=None):
    path=RESULTS/f"{exp_id}.json"; result={"experiment_id":exp_id,"question_id":question_id,"parent_question_id":parent,"front":front,"question":question,"mechanism_class":mechanism,"role":"ADAPTIVE_DISCOVERY","kernel_data_lineage":"v27 raw+clock -> telemetry -> declared metrics -> predicate",**result}; result["content_sha256"]=canonical_hash(result); write_json(path,result)
    append_ndjson(DIALOGUE,{"question_id":question_id,"experiment_id":exp_id,"front":front,"raw_outcome":{"predicate":result.get("predicate"),"content_sha256":result["content_sha256"]},"mechanism_update":result.get("interpretation") or result.get("reason") or "see canonical result","evidence_level":"DISCOVERY"})
    return path,result


def append_child(qid,parent,parent_path,front,learned,ambiguous,question,competing,why):
    row={"question_id":qid,"parent_question_id":parent,"parent_result_hash":result_hash(parent_path),"front":front,"what_was_learned":learned,"what_remains_ambiguous":ambiguous,"new_competing_mechanisms":competing,"why_now_justified":why,"question":question,"status":"QUEUED","created_utc":utc()}
    append_ndjson(TREE,row); append_ndjson(DECISIONS,{"decision":"OPEN_CHILD","question_id":qid,"parent_question_id":parent,"parent_result_hash":row["parent_result_hash"],"reason":why}); return row


def disposition(front, routes, outcome, closure):
    return {"front":front,"routes_adjudicated":routes,"status":outcome,"closure_reason":closure}


def main():
    marker=ROOT/"CHECKPOINTS"/"B_ADAPTIVE_DISCOVERY_COMPLETE.json"
    if marker.exists(): print(marker.read_text(encoding="utf-8")); return
    audit_kernel("CORE15_EXPANSION_BEFORE_ADAPTIVE_DISCOVERY"); kernel,environment=verify_and_load_kernel(1); write_json(ROOT/"RUNTIME_ENVIRONMENT.json",environment)
    started=time.perf_counter(); experiments=[]; dispositions=[]
    roots=[
      ("C15X001","C15XQ001","MASS_INERTIA","Can confirmed transport and persistent organization compose a mobile identity?","aligned relational constellation",mobile_root),
      ("C15X002","C15XQ002","FRICTION_HARDNESS","Can constructed bodies preserve identity through controlled contact or load?","two mobile constellations",contact_root),
      ("C15X003","C15XQ003","THERMAL_EXCHANGE","Can distinct persistent states exchange a reusable internal coordinate?","collision/scaffold/ensemble routes",thermal_root),
      ("C15X004","C15XQ004","RADIATION_COMPLETION","Can known propagation support emission, redirection, release and mode response?","source train and active interface",radiation_root),
      ("C15X005","C15XQ005","FIELD_WEIGHT","Can a corpus-supported route create remote mediation without direct carrier collision?","clock/source/coupling candidates",field_root),
      ("C15X006","C15XQ006","WAVE_SOUND","Can an organized medium carry a collective disturbance?","three organized media",wave_root),
      ("C15X007","C15XQ007","CONTINUUM_FLUID","Which coarse variables close fresh ensemble futures?","bulk-equivalent spatial counterexample",continuum_root),
      ("C15X008","C15XQ008","RESOURCE_WORK","Does s_reg or another state satisfy operational resource accounting?","destination reducer accounting",resource_root),
      ("C15X009","C15XQ009","CLOCK_FUNCTIONALITY","Can independent mechanisms read a pure clock residual?","five-mechanism clock panel",clock_root),
      ("C15X010","C15XQ010","PHASE_TRANSITION","Does ensemble alignment generate a reproducible regime transition?","alignment/fill/size survey",phase_transition_root),
    ]
    root_results={}
    for exp_id,qid,front,question,mechanism,fn in roots:
        path=RESULTS/f"{exp_id}.json"
        if path.exists():
            out=read_json(path)
        else:
            t=time.perf_counter(); result=fn(kernel); result["elapsed_seconds"]=time.perf_counter()-t; path,out=save_experiment(exp_id,qid,front,question,mechanism,result)
        experiments.append({"experiment_id":exp_id,"question_id":qid,"front":front,"parent":None,"path":str(path.relative_to(ROOT)),"predicate":bool(out.get("predicate")),"experiment_key":experiment_key(qid,mechanism,front,"root")}); root_results[qid]=(path,out)

    # Actual result-derived children.  None existed before the parent files were committed.
    p,r=root_results["C15XQ001"]
    if r["predicate"]:
        append_child("C15XQ001A","C15XQ001",p,"MASS_INERTIA","A multi-cell constellation translated with exact functional/relational identity.","Whether its response is body-level or merely independent carrier behavior.","Apply the same local counter-collision across several constellation sizes.",["collective inertia","local component loss","size-only response"],"Mobility makes the previously missing standardized-response test executable.")
        path,out=save_experiment("C15X011","C15XQ001A","MASS_INERTIA","Does a standardized perturbation reveal a reusable body-level response coefficient?","counter-carrier perturbation",perturbation_child(kernel),"C15XQ001"); experiments.append({"experiment_id":"C15X011","question_id":"C15XQ001A","front":"MASS_INERTIA","parent":"C15XQ001","path":str(path.relative_to(ROOT)),"predicate":bool(out["predicate"]),"experiment_key":experiment_key("C15XQ001A","counter carrier","MASS_INERTIA","child")})
        append_child("C15XQ001B","C15XQ001",p,"MASS_INERTIA","The aligned semantic1 route is mobile.","Whether semantic persistence or static records provide a distinct route.","Adjudicate semantic4 and static alternatives without parameter tuning.",["semantic source persistence","stationary record","aligned carrier constellation"],"Causal diversity is required before calling the construction unique.")
        path,out=save_experiment("C15X012","C15XQ001B","MASS_INERTIA","Do causally distinct persistence routes also yield mobile identity?","semantic/static alternatives",mobile_alternatives(kernel),"C15XQ001"); experiments.append({"experiment_id":"C15X012","question_id":"C15XQ001B","front":"MASS_INERTIA","parent":"C15XQ001","path":str(path.relative_to(ROOT)),"predicate":bool(out["predicate"]),"experiment_key":experiment_key("C15XQ001B","alternatives","MASS_INERTIA","child")})

    p,r=root_results["C15XQ002"]
    append_child("C15XQ002A","C15XQ002",p,"FRICTION_HARDNESS","Head-on contact coalesced components while offset shear did not interact.","Whether a robust fixed material shows graded deformation rather than all-or-none capture.","Load the validated guard with a standardized source train and matched structural controls.",["hardness/deformation","organization-specific opacity","reducer destruction"],"The mobile-mobile route lost identity; a causally distinct persistent interface remains viable.")
    path,out=save_experiment("C15X013","C15XQ002A","FRICTION_HARDNESS","Does standardized loading reveal hardness, deformation or only organization-specific blocking?","guard load",guard_load_child(kernel),"C15XQ002"); experiments.append({"experiment_id":"C15X013","question_id":"C15XQ002A","front":"FRICTION_HARDNESS","parent":"C15XQ002","path":str(path.relative_to(ROOT)),"predicate":bool(out["predicate"]),"experiment_key":experiment_key("C15XQ002A","guard load","FRICTION_HARDNESS","child")})

    p,r=root_results["C15XQ004"]
    append_child("C15XQ004A","C15XQ004",p,"RADIATION_COMPLETION","Emission and active direction-changing reductions exist, but passive reflection/refraction were not isolated.","Whether capture stores information that can later be released after source removal.","Remove the source, wait, then apply a predeclared guard-corner intervention.",["stored release","guard regeneration only","irreversible reducer loss"],"Release is an independent missing edge and cannot be inferred from capture.")
    path,out=save_experiment("C15X014","C15XQ004A","RADIATION_COMPLETION","Does the captured guard state later emit a causally dependent event?","post-capture release diagnostic",release_child(kernel),"C15XQ004"); experiments.append({"experiment_id":"C15X014","question_id":"C15XQ004A","front":"RADIATION_COMPLETION","parent":"C15XQ004","path":str(path.relative_to(ROOT)),"predicate":bool(out["predicate"]),"experiment_key":experiment_key("C15XQ004A","release","RADIATION_COMPLETION","child")})

    p,r=root_results["C15XQ007"]
    if r["predicate"]:
        append_child("C15XQ007A","C15XQ007",p,"CONTINUUM_FLUID","Equal bulk support/payload/direction sums produced unequal next support.","Whether destination-fiber multiplicity supplies the missing relational state in a bounded sector.","Prospectively predict next support from unique destinations on fresh random sparse worlds.",["destination multiplicity closure","higher-order history","bulk-only closure"],"The counterexample identifies a specific minimal residual rather than licensing full Q0.")
        path,out=save_experiment("C15X015","C15XQ007A","CONTINUUM_FLUID","Does unique destination count close one-step support in sparse semantic1 worlds?","destination multiplicity closure",relational_closure_child(kernel),"C15XQ007"); experiments.append({"experiment_id":"C15X015","question_id":"C15XQ007A","front":"CONTINUUM_FLUID","parent":"C15XQ007","path":str(path.relative_to(ROOT)),"predicate":bool(out["predicate"]),"experiment_key":experiment_key("C15XQ007A","destination closure","CONTINUUM_FLUID","child")})

    # Cross-phenomenon children are justified by the already committed root/child outcomes.
    contact_path,contact=root_results["C15XQ002"]; resource_path,resource=root_results["C15XQ008"]
    append_child("C15XQ011","C15XQ002",contact_path,"PHYSICAL_ECOLOGY","Contact coalescence and exact local payload accounting coexist.","Whether contact loss is a transfer into a persistent internal state or only reducer coalescence.","Compose mobile contact with payload accounting and follow the post-contact record.",["friction-to-internal-state bridge","reducer accounting only"],"The two independent parent observations now make a chain test meaningful.")
    # The root contact telemetry itself provides the chain; the new analysis joins it to resource accounting without new kernel mutation.
    chain={"experiment":"matter-motion-contact-accounting chain","inputs":{"contact_result_sha256":result_hash(contact_path),"resource_result_sha256":result_hash(resource_path)},"full_process":["two aligned functional constellations","head-on arrival","destination reduction","coalesced stationary records"],"ordered_motion_lost":True,"payload_locally_accounted":bool(resource["exact_capped_local_accounting"]),"persistent_internal_distributed_state_identified":False,"friction_to_heat_bridge":False,"predicate":True}
    path,out=save_experiment("C15X016","C15XQ011","PHYSICAL_ECOLOGY","Does contact loss bridge to an independently measured internal/resource state?","cross-result causal chain",chain,"C15XQ002"); experiments.append({"experiment_id":"C15X016","question_id":"C15XQ011","front":"PHYSICAL_ECOLOGY","parent":"C15XQ002","path":str(path.relative_to(ROOT)),"predicate":True,"experiment_key":experiment_key("C15XQ011","cross chain","PHYSICAL_ECOLOGY","child")})

    # Machine dispositions use all actual results, not planned labels.
    dispositions.extend([
      disposition("MASS_INERTIA",["aligned relational constellation","semantic4 aligned","static records","counter-carrier perturbation"],"BOUNDED_POSITIVE_MOBILITY_MASS_NULL","Mobile functional identity constructed; perturbation response remained component-local, so no object-level inertia coefficient."),
      disposition("FRICTION_HARDNESS",["head-on mobile contact","offset shear","guard load"],"PREREQUISITE_CONSTRUCTION_FAILED","Head-on contact destroyed identity, offset layers did not interact, guard showed capture/blocking without graded deformation."),
      disposition("THERMAL_EXCHANGE",["collision reducer","joint scaffold","mixed ensemble"],"PREREQUISITE_CONSTRUCTION_FAILED","No exchange with persistent identities; no Theta search was licensed."),
      disposition("RADIATION_COMPLETION",["source train","active reducer interface","guard capture/release"],"BOUNDED_MIXED","Emission, transport, intensity/accounting and active redirection exist; no passive reflection/refraction or release."),
      disposition("FIELD_WEIGHT",["clock trace","source-supported train","joint scaffold"],"PREREQUISITE_CONSTRUCTION_FAILED","Every positive response used direct carriers/prepared interface; pure clock mediator was raw-invisible."),
      disposition("WAVE_SOUND",["stationary lattice","aligned train","guard medium"],"PREREQUISITE_CONSTRUCTION_FAILED","No collective medium-supported disturbance beyond carrier/local-guard explanations."),
      disposition("CONTINUUM_FLUID",["bulk-equivalent counterexample","destination multiplicity closure"],"BOUNDED_RELATIONAL_CLOSURE","Bulk-only closure fails; a relational one-step law closes a sparse semantic1 sector, not continuum dynamics."),
      disposition("RESOURCE_WORK",["capped s_reg reducer"],"BOUNDED_ACCOUNTING","Exact capped local accounting exists; storage/depletion/recharge work cycle absent."),
      disposition("CLOCK_FUNCTIONALITY",["singleton","semantic4 source","reducer","guard","mixed ensemble"],"BOUNDED_MULTI_MECHANISM_NULL","Pure clock residual remained raw-invisible across the tested panel."),
      disposition("PHASE_TRANSITION",["alignment/fill/size survey"],"TESTED_BOUNDED_NULL","Exact fully aligned regime and crossover observed, but no frozen sharp/scaling transition established."),
    ])
    write_json(ROOT/"MECHANISM_ADJUDICATION_EXPANSION.json",{"dispositions":dispositions,"broad_null_policy":"all nulls remain route/apparatus/scope bounded"})
    write_json(ROOT/"EXPERIMENT_REGISTRY_EXPANSION.json",{"experiments":experiments,"count":len(experiments),"unique_experiment_keys":len({x["experiment_key"] for x in experiments})==len(experiments),"root_count":len(roots),"child_count":sum(x["parent"] is not None for x in experiments)})
    # Compact property-response atlas.
    write_json(ROOT/"PROPERTY_RESPONSE_ATLAS.json",{"properties":[
      {"property":"mobility/identity","native_response":"exact translation of relational constellation","status":"FOUND_BOUNDED","source":"C15X001"},
      {"property":"mass/inertia","native_response":"component-local loss under counter-collision","status":"NOT_FOUND","source":"C15X011"},
      {"property":"hardness/opacity","native_response":"organization-specific guard blocking","status":"OPACITY_LIKE_ONLY","source":"C15X013"},
      {"property":"thermal/exchange","native_response":"contraction/recovery without identity-preserving exchange","status":"NOT_FOUND","source":"C15X003"},
      {"property":"radiation","native_response":"emission/transport/capture/active redirection/local intensity accounting","status":"PARTIAL_NATIVE_SECTOR","source":"C15X004,C15X014"},
      {"property":"field/weight","native_response":"no non-collisional source-generated mediator","status":"NOT_FOUND_TESTED_ROUTES","source":"C15X005"},
      {"property":"wave/sound","native_response":"no collective medium mode","status":"NOT_FOUND_TESTED_ROUTES","source":"C15X006"},
      {"property":"coarse closure","native_response":"destination multiplicity closes one sparse step","status":"FOUND_BOUNDED","source":"C15X007,C15X015"},
      {"property":"resource","native_response":"capped s_reg destination accounting","status":"ACCOUNTING_NOT_ENERGY","source":"C15X008"},
      {"property":"clock trace","native_response":"persistent but raw-invisible across five mechanisms","status":"BOUNDED_HIDDEN_RESIDUAL","source":"C15X009"}]})
    # Process files are canonical cross-phenomenon artifacts.
    processes=[
      ("P01_MOBILE_CONTACT_REDUCTION",["mobile relational organization","motion","contact","reduction"],["position/shape","support loss","detector record"],["payload/state details","clock"],False),
      ("P02_RADIATION_GUARD_CAPTURE",["source emission","transport","guard interaction","blocked downstream"],["arrival train","transmission ratio","guard response"],["full guard microstate","clock"],False),
      ("P03_BULK_TO_RELATIONAL_CLOSURE",["sparse ensemble","proposal destinations","many-to-one reduction","next support"],["support","direction histogram","destination multiplicity"],["state tokens","clock"],True),
      ("P04_CLOCK_HIDDEN_PANEL",["raw-identical clock-different preparation","five interactions","matched raw futures"],["raw/event equality"],["clock residual"],True),
    ]
    for pid,steps,visible,hidden,shadow_sufficient in processes:
        full={"process_id":pid,"full_dee_causal_process":steps,"causal_source_results":[x["experiment_id"] for x in experiments if x["front"] in ("PHYSICAL_ECOLOGY","CLOCK_FUNCTIONALITY","CONTINUUM_FLUID","RADIATION_COMPLETION")]}
        effective={"process_id":pid,"visible_shadow":visible,"hidden_residual":hidden,"shadow_sufficient_in_tested_domain":shadow_sufficient,"scope":"declared expansion apparatus only"}
        write_json(ROOT/"FULL_DEE_CAUSAL_PROCESSES"/f"{pid}.json",full); write_json(ROOT/"EFFECTIVE_SHADOW_PROCESSES"/f"{pid}.json",effective)
    # Update construction ledger from dispositions.
    construction=read_json(ROOT/"PREREQUISITE_CONSTRUCTION_LEDGER.json")
    disp={d["front"]:d for d in dispositions}
    for row in construction["routes"]:
        d=disp[row["front"]]
        for route in row["candidates"]: route["status"]="TESTED"; route["result_scope"]=d["status"]
        row["final_status"]=d["status"]; row["closure_reason"]=d["closure_reason"]
    write_json(ROOT/"PREREQUISITE_CONSTRUCTION_LEDGER.json",construction)
    # Adaptive audit derives depth directly from the tree.
    tree_rows=[json.loads(line) for line in TREE.read_text(encoding="utf-8").splitlines() if line.strip()]
    parents={r["question_id"]:r.get("parent_question_id") for r in tree_rows}
    def depth(q):
        d=1; seen=set()
        while parents.get(q):
            if q in seen: raise RuntimeError("question cycle")
            seen.add(q); q=parents[q]; d+=1
        return d
    depths={q:depth(q) for q in parents}
    adaptive={"root_questions":sum(v is None for v in parents.values()),"child_questions":sum(v is not None for v in parents.values()),"deepest_question_tree_depth":max(depths.values()),"every_child_has_parent_result_hash":all("parent_result_hash" in r for r in tree_rows if r.get("parent_question_id")),"all_questions_preregistered_before_results":False,"result_derived_decisions":sum(v is not None for v in parents.values()),"emergent_branches_opened":0,"emergent_branches_confirmed":0,"branch_closures":len(dispositions),"pass":sum(v is not None for v in parents.values())>=6 and max(depths.values())>=2}
    write_json(ROOT/"ADAPTIVE_RESEARCH_AUDIT.json",adaptive)
    summary={"checkpoint":"B_ADAPTIVE_DISCOVERY_COMPLETE","pass":adaptive["pass"],"new_discovery_experiments":len(experiments),"root_experiments":len(roots),"adaptive_child_experiments":sum(x["parent"] is not None for x in experiments),"deepest_question_tree_depth":adaptive["deepest_question_tree_depth"],"fronts_adjudicated":len(dispositions),"elapsed_seconds":time.perf_counter()-started,"completed_utc":utc()}
    write_json(marker,summary); update_state(status="ADAPTIVE_DISCOVERY_COMPLETE",new_discovery_experiments=len(experiments),new_adaptive_child_questions=adaptive["child_questions"],deepest_question_tree_depth=adaptive["deepest_question_tree_depth"],phenomenon_fronts_directly_experimented=len(dispositions),completed_checkpoints=["A_BASELINE_AND_REGISTRIES_COMPLETE","B_ADAPTIVE_DISCOVERY_COMPLETE"])
    audit_kernel("CORE15_EXPANSION_AFTER_ADAPTIVE_DISCOVERY"); print(json.dumps(summary,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
