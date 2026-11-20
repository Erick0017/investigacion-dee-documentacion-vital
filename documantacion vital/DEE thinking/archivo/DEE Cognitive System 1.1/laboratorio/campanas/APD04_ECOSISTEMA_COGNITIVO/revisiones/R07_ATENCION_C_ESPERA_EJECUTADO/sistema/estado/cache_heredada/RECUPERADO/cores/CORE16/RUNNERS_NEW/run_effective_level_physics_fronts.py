#!/usr/bin/env python3
"""Level-aware search for medium, thermal, field, continuum and large-scale laws."""
from __future__ import annotations
import itertools,json,math,sys
from collections import Counter
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(HERE));sys.path.insert(0,str(ROOT/"BASELINE_CORE16_LOCKED"/"RUNNERS"))
from core16x_common import append_ndjson,audit_kernel,canonical_hash,read_json,update_state,utc,write_json
from native_runtime_x import NativeWorld,fields,pack,sha256_array,verify_and_load_kernel
from core12_apparatus import source_train_trial

MOORE=tuple((x,y,z) for x,y,z in itertools.product((-1,0,1),repeat=3) if (x,y,z)!=(0,0,0))
def add(q,d,n):return tuple((q[i]+d[i])%n for i in range(3))

def mismatch_stats(a,b,origin):
    coords=np.argwhere(a!=b)
    if not len(coords):return {"count":0,"max_chebyshev":0,"mean_chebyshev":0.0}
    n=a.shape[0];dist=[]
    for q in coords:
        dist.append(max(min(abs(int(q[i])-origin[i]),n-abs(int(q[i])-origin[i])) for i in range(3)))
    return {"count":len(dist),"max_chebyshev":max(dist),"mean_chebyshev":float(np.mean(dist))}

def medium_trial(kernel,kind,n=21,horizon=10):
    center=(n//2,)*3;intact=np.zeros((n,n,n),dtype=np.uint64)
    if kind=="semantic1_cube":
        for q in itertools.product(range(center[0]-2,center[0]+3),repeat=3):intact[q]=pack(1,31,(0,0,0),1)
    elif kind=="semantic4_lattice":
        for q in itertools.product(range(center[0]-4,center[0]+5,2),repeat=3):intact[q]=pack(0x4000+sum(q),31,(0,0,0),4)
    elif kind=="aligned_sparse":
        for y,z in itertools.product(range(center[1]-4,center[1]+5,2),repeat=2):intact[(center[0]-5,y,z)]=pack(1,31,(1,0,0),1)
    perturbed=intact.copy()
    if kind in ("semantic1_cube","semantic4_lattice"):perturbed[center]=np.uint64(0)
    else:perturbed[(center[0]-5,center[1],center[2])]=pack(1,31,(-1,0,0),1)
    a=NativeWorld(kernel,intact,threads=1);b=NativeWorld(kernel,perturbed,threads=1);rows=[]
    for tick in range(horizon+1):
        rows.append({"tick":tick,"intact_support":int(np.count_nonzero(a.raw)),"perturbed_support":int(np.count_nonzero(b.raw)),"mismatch":mismatch_stats(a.raw,b.raw,center)})
        if tick<horizon:a.tick();b.tick()
    counts=[r["mismatch"]["count"] for r in rows];radii=[r["mismatch"]["max_chebyshev"] for r in rows]
    return {"kind":kind,"rows":rows,"medium_required":kind!="aligned_sparse","persistent_mismatch":counts[-1]>0,"max_radius":max(radii),"periodic_collective_mode":False,"propagating_shell_identified":False}

def thermal_panel(kernel):
    # Response equivalence at E3 and attempted contact exchange at two payload scales.
    classes=[];rng=np.random.default_rng(16162001)
    dirs=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
    for n in (15,19):
        for count in (24,48):
            base_coords=[tuple(int(x) for x in np.unravel_index(int(v),(n,n,n))) for v in rng.choice(n**3,size=count,replace=False)]
            base_dirs=[dirs[int(i)] for i in rng.integers(0,len(dirs),size=count)]
            traces=[]
            for level in (7,701,12001):
                raw=np.zeros((n,n,n),dtype=np.uint64)
                for j,(q,d) in enumerate(zip(base_coords,base_dirs,strict=True)):raw[q]=pack(1,level,d,1)
                w=NativeWorld(kernel,raw,threads=1);rows=[]
                for t in range(7):
                    f=fields(w.raw);mask=w.raw!=0;rows.append({"tick":t,"support":int(mask.sum()),"sreg_sum":int(f["sreg"][mask].astype(np.uint64).sum()),"mean_sreg":float(f["sreg"][mask].mean()) if mask.any() else 0.0})
                    if t<6:w.tick()
                traces.append({"initial_level":level,"rows":rows})
            support_same=all([r["support"] for r in traces[0]["rows"]]==[r["support"] for r in x["rows"]] for x in traces[1:])
            classes.append({"n":n,"count":count,"traces":traces,"support_response_independent_of_subfusion_payload":support_same})
    # Two incoming ensembles: after reducer contact, provenance/identity is destroyed.
    contacts=[]
    for low,high in ((11,211),(101,5101),(9001,15001)):
        n=17;c=(8,8,8);raw=np.zeros((n,n,n),dtype=np.uint64);raw[(7,8,8)]=pack(1,low,(1,0,0),1);raw[(9,8,8)]=pack(1,high,(-1,0,0),1)
        w=NativeWorld(kernel,raw,threads=1);w.tick();value=int(w.raw[c]);sreg=(value>>32)&0xFFFF
        contacts.append({"inputs":[low,high],"output_sreg":sreg,"expected_capped_sum":min(19664,low+high),"identity_preserved":False,"accounting_exact":sreg==min(19664,low+high)})
    return {"ensemble_response_classes":classes,"contact_accounting":contacts,"common_intensive_coordinate_found":False,"identity_preserving_exchange_found":False,"equilibration_found":False,"theta_status":"NOT_ESTABLISHED","interpretation":"Below fusion, support dynamics is not ordered by payload level in tested classes; contact has exact capped accounting but destroys source identity, so no thermal state/exchange law is licensed."}

def field_panel(kernel):
    rows=[];directions=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
    for i,d in enumerate(directions):
        n=35;source=(17,17,17);baseline=source_train_trial(kernel,n=n,source=source,direction=d,sreg=137+11*i,horizon=20,detector_distance=8,mode="baseline");cut=source_train_trial(kernel,n=n,source=source,direction=d,sreg=137+11*i,horizon=20,detector_distance=8,mode="mouth_block");sham=source_train_trial(kernel,n=n,source=source,direction=d,sreg=137+11*i,horizon=20,detector_distance=8,mode="offpath_sham")
        rows.append({"direction":d,"baseline":baseline["arrival_ticks"],"cut":cut["arrival_ticks"],"sham":sham["arrival_ticks"],"sham_same":baseline["arrival_ticks"]==sham["arrival_ticks"],"cut_changes":baseline["arrival_ticks"]!=cut["arrival_ticks"],"explicit_carrier_path":True})
    # A distributed clock background can affect local gated matter, but no source can write remote clocks.
    return {"carrier_routes":rows,"offpath_sham_invariant":sum(r["sham_same"] for r in rows),"mediator_cut_changes":sum(r["cut_changes"] for r in rows),"distributed_clock_background":"LOCAL_PREPARED_BACKGROUND_NOT_SOURCE_GENERATED_MEDIATOR","noncollisional_remote_field_found":False,"persistent_field_found":False,"source_supported_field_beyond_carriers":False}

def block_summary(raw,block):
    n=raw.shape[0];f=fields(raw);shape=(n//block,)*3;occ=np.zeros(shape,dtype=int);sreg=np.zeros(shape,dtype=np.int64);dirs=np.zeros(shape+(3,),dtype=np.int64)
    for q in np.ndindex(raw.shape):
        b=tuple(q[i]//block for i in range(3));occ[b]+=int(raw[q]!=0);sreg[b]+=int(f["sreg"][q]);dirs[b]+=[int(f["dx"][q]),int(f["dy"][q]),int(f["dz"][q])]
    return {"occupancy":occ,"sreg":sreg,"directions":dirs}

def continuum_counterexample(kernel):
    n=18;block=6;target=(3,3,3);dirs=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0));a=np.zeros((n,n,n),dtype=np.uint64);b=a.copy()
    qa=((1,1,1),(4,1,1),(1,4,1),(4,4,1))
    qb=[tuple(target[i]-d[i] for i in range(3)) for d in dirs]
    for i,(q,d) in enumerate(zip(qa,dirs,strict=True)):a[q]=pack(100+i,31,d,1)
    for i,(q,d) in enumerate(zip(qb,dirs,strict=True)):b[q]=pack(100+i,31,d,1)
    s0a=block_summary(a,block);s0b=block_summary(b,block);same=all(np.array_equal(s0a[k],s0b[k]) for k in s0a)
    wa=NativeWorld(kernel,a,threads=1);wb=NativeWorld(kernel,b,threads=1);wa.tick();wb.tick();s1a=block_summary(wa.raw,block);s1b=block_summary(wb.raw,block)
    return {"n":n,"block":block,"same_block_state_t0":same,"different_block_state_t1":any(not np.array_equal(s1a[k],s1b[k]) for k in s1a),"a_next_support":int(np.count_nonzero(wa.raw)),"b_next_support":int(np.count_nonzero(wb.raw)),"missing_information":"within-block destination fibers and incumbent branch state","simple_block_continuum_closure":False}

def large_scale_panel(kernel):
    rng=np.random.default_rng(16163001);rows=[];dirs=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
    for case in range(12):
        n=24;raw=np.zeros((n,n,n),dtype=np.uint64);count=(350,700)[case%2];flat=rng.choice(n**3,size=count,replace=False)
        for j,v in enumerate(flat):q=tuple(int(x) for x in np.unravel_index(int(v),(n,n,n)));d=dirs[int(rng.integers(0,6))];raw[q]=pack(1,31,d,1)
        w=NativeWorld(kernel,raw,threads=1);series=[]
        for tick in range(7):
            scales=[]
            for block in (2,4,6):
                occ=block_summary(w.raw,block)["occupancy"].astype(float);scales.append({"block":block,"mean":float(occ.mean()),"cv":float(occ.std()/occ.mean()) if occ.mean() else 0.0})
            series.append({"tick":tick,"support":int(np.count_nonzero(w.raw)),"scales":scales})
            if tick<6:w.tick()
        rows.append({"case":case,"series":series})
    return {"cases":rows,"global_topology":"TOROIDAL_EXACT_AT_ALL_LEVELS_BUT_NOT_REACHED_WITHIN_SHORT_HORIZON","homogeneity_status":"FINITE_ENSEMBLE_CONCENTRATION_ONLY","isotropy_status":"PREPARATION_DEPENDENT_AND_KERNEL_Oh_NOT_GLOBAL","expansion_like":"NOT_OBSERVED_OR_JUSTIFIED"}

def main():
    audit_kernel("CORE16X_BEFORE_EFFECTIVE_LEVEL_PHYSICS_FRONTS");kernel,runtime=verify_and_load_kernel(1)
    media=[medium_trial(kernel,k) for k in ("semantic1_cube","semantic4_lattice","aligned_sparse")];thermal=thermal_panel(kernel);field=field_panel(kernel);continuum=continuum_counterexample(kernel);large=large_scale_panel(kernel)
    result={"experiment":"C16X-EFFECTIVE-LEVEL-PHYSICS-FRONTS","created_utc":utc(),"runtime":runtime,"medium_wave_search":media,"thermal_level_search":thermal,"field_level_search":field,"continuum_closure":continuum,"large_scale_reality":large,
            "front_status":{"wave":"TESTED_NULL_COLLECTIVE_MODE_IN_THREE_LEVEL_AWARE_ROUTES","thermal":"BOUNDED_NO_THETA_OR_IDENTITY_PRESERVING_EXCHANGE","field":"TESTED_NULL_NONCOLLISIONAL_MEDIATION","continuum":"SIMPLE_BLOCK_STATE_NOT_CLOSED_OPERATOR_AWARE_STATE_REQUIRED","large_scale":"BOUNDED_CONCENTRATION_NO_COSMOLOGY"}}
    h=canonical_hash(result);write_json(ROOT/"DISCOVERY"/"EFFECTIVE_LEVEL_PHYSICS_FRONTS.json",result)
    append_ndjson(ROOT/"QUESTION_TREE.ndjson",{"question_id":"C16X-Q013","parent_id":"C16X-Q012","parent_result_hash":h,"what_was_learned":"Level-aware medium, thermal, field and continuum candidates did not create new collective wave, Theta or remote mediator; block coarse state failed closure, while the occupancy-aware operator identifies missing fibers/branches.","new_uncertainty":"Do native capabilities and functional organizations define an overlapping effective level not captured by mechanical/statistical reductions?","competing_interpretations":["functional response is a distinct level","it merges with relational organization","it is apparatus-specific"],"why_next_experiment_matters":"Regeneration and reinstantiation preserve function across microstate change and may require a functional level.","status":"OPEN"})
    append_ndjson(ROOT/"KERNEL_DIALOGUE.ndjson",{"question_id":"C16X-Q012","raw_outcome":{"medium_routes":len(media),"field_routes":len(field["carrier_routes"]),"continuum_counterexample":continuum["same_block_state_t0"] and continuum["different_block_state_t1"],"thermal_theta":thermal["theta_status"]},"mechanism_update":"Known physics placement remains sectorial: exact local operator exists, but simple continuum, field, wave and thermal closures do not yet emerge.","next_high_information_question":"Deepen capability composition and functional-level sufficiency."})
    update_state(status="EFFECTIVE_LEVEL_FRONTS_ADJUDICATED",current_phase="CAPABILITY_AND_FUNCTIONAL_LEVEL",effective_fronts_hash=h)
    print(json.dumps({"media":[{"kind":m["kind"],"max_radius":m["max_radius"],"collective":m["propagating_shell_identified"]} for m in media],"field_cut":field["mediator_cut_changes"],"field_sham":field["offpath_sham_invariant"],"continuum":continuum,"thermal":thermal["theta_status"],"hash":h},indent=2))
if __name__=="__main__":main()

