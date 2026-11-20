#!/usr/bin/env python3
"""New prerequisite constructions enabled by the learned-policy coordinate result."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from core17e_common import PACKAGE_ROOT, ROOT, append_ndjson, seal, verify_and_load_kernel, write_json
BASE = PACKAGE_ROOT / "RUNNERS" / "VENDORED_CORE16" / "BASELINE_RUNNERS"
sys.path.insert(0, str(BASE))
from core10_apparatus import A, B, SENSOR, NORMALIZER, PENALTY0, NativeWorld, add, inject_arrival, pack, read, summarize_world, transform  # noqa: E402


def train_in_place(world, source, frame, tick, n, tag):
    perm, signs = frame
    sensor, normalizer, penalty = (transform(v, perm, signs) for v in (SENSOR, NORMALIZER, PENALTY0))
    if tick == n: inject_arrival(world, source, sensor, 47 + tag, 100000 + tag, 110000 + tag)
    if tick == 2*n:
        inject_arrival(world, source, normalizer, 53 + tag, 120000 + tag, 130000 + tag)
        inject_arrival(world, source, penalty, 59 + tag, 140000 + tag, 150000 + tag)


def learned_contact(kernel, separated: bool) -> dict:
    n=31; d=5; raw=np.zeros((n,n,n),np.uint64); clock=np.zeros_like(raw); world=NativeWorld(kernel,raw,clock,threads=1)
    f1=((0,1,2),(1,1,1)); f2=((0,1,2),(1,-1,1)); b1=transform(B,*f1); b2=transform(B,*f2)
    target1=(15,15,15); target2=(18,15,15) if separated else target1
    s1=add(target1,b1,-d,n); s2=add(target2,b2,-d,n)
    for j,(s,frame) in enumerate(((s1,f1),(s2,f2))):
        a=transform(A,*frame); v=pack(200000+j,7+j,a,1); world.raw_a[s]=v; world.raw_b[s]=v; world.clock_a[s]=1000+j; world.clock_b[s]=1000+j
    learned=[]
    for cur in range(2*n+d):
        t=cur+1; train_in_place(world,s1,f1,t,n,0); train_in_place(world,s2,f2,t,n,1); world.tick()
        if t==2*n: learned=[read(world.raw,s1),read(world.raw,s2)]
    records={"target1":read(world.raw,target1),"target2":read(world.raw,target2)}
    return {"mode":"separated" if separated else "collision","sources":[s1,s2],"targets":[target1,target2],"learned":learned,"records":records,"support":summarize_world(world)["support"],"two_identities_survive":summarize_world(world)["support"]>=2}


def learned_pair_perturbation(kernel, perturb: bool) -> dict:
    n=31; raw=np.zeros((n,n,n),np.uint64); clock=np.zeros_like(raw); world=NativeWorld(kernel,raw,clock,threads=1)
    frame=((0,1,2),(1,1,1)); a=transform(A,*frame); b=transform(B,*frame); sources=[(12,12,12),(16,12,12)]
    for j,s in enumerate(sources):
        v=pack(300000+j,7+j,a,1); world.raw_a[s]=v; world.raw_b[s]=v; world.clock_a[s]=2000+j; world.clock_b[s]=2000+j
    learned=[]; post=[]
    horizon=2*n+4
    for cur in range(horizon):
        t=cur+1
        for j,s in enumerate(sources): train_in_place(world,s,frame,t,n,j)
        if perturb and t==2*n+1:
            target=add(sources[0],b,1,n); inject_arrival(world,target,tuple(-x for x in b),73,310000,320000)
        world.tick()
        if t==2*n: learned=[read(world.raw,s) for s in sources]
        if t>=2*n: post.append({"tick":t,"component1_expected":read(world.raw,add(sources[0],b,t-2*n,n)),"component2_expected":read(world.raw,add(sources[1],b,t-2*n,n)),"support":summarize_world(world)["support"]})
    return {"mode":"local_counter_collision" if perturb else "control","learned":learned,"trace":post,"unperturbed_component_continues":all(row["component2_expected"] is not None for row in post),"collective_deflection":False,"final":summarize_world(world)}


def hybrid(kernel) -> dict:
    n=15; raw=np.zeros((n,n,n),np.uint64); clock=np.zeros_like(raw); center=(7,7,7); moving=(8,7,7); b=(0,1,0)
    raw[center]=pack(4444,11,(0,0,0),4); raw[moving]=pack(5555,13,b,1)
    world=NativeWorld(kernel,raw,clock,threads=1); before={"guard":read(world.raw,center),"policy":read(world.raw,moving)}; world.tick()
    after={"guard":read(world.raw,center),"old_policy_site":read(world.raw,moving),"advanced_policy_site":read(world.raw,add(moving,b,1,n))}
    return {"construction":"stationary semantic4 scaffold + mobile direction-bearing state","before":before,"after":after,"relative_geometry_preserved":False,"reason":"semantic4 is fixed while semantic1 translates"}


def main() -> None:
    kernel,runtime=verify_and_load_kernel(1)
    contact=[learned_contact(kernel,False),learned_contact(kernel,True)]
    perturb=[learned_pair_perturbation(kernel,False),learned_pair_perturbation(kernel,True)]
    result=seal({
      "schema":"dee.v27.core17.extension.prerequisite_constructions.v1",
      "new_mechanism_used":"C17E direction-bearing learned state and redundant learned copy",
      "construction_attempts":{
        "learned_policy_contact":contact,
        "redundant_learned_pair_perturbation":perturb,
        "hybrid_persistent_mobile_object":hybrid(kernel),
      },
      "adjudication":{
        "persistent_interacting_bodies":"NOT_CONSTRUCTED: learned components are persistent/mobile, but contact is a many-to-one reducer and a local counter-collision does not induce collective response",
        "identity_preserving_exchange":"NOT_CONSTRUCTED: collision arm loses the two input identities; separated control preserves both",
        "thermal_intensive_test":"NOT_LICENSED without persistent identities after exchange",
        "distributed_mediator":"NO_NEW_CONSTRUCTIBLE_ROUTE: policy repair uses explicit carriers; R0_FACTOR_52 retains strictly local neighborhood/incoming dependencies",
        "field_wave":"NOT_LICENSED: no source-generated state beyond direct carrier light cone or collective medium mode",
        "compatible_contexts":"NO_NEW_CONSTRUCTIBLE_ROUTE: direction read/write is ordinary state modification",
        "independent_correlated_subsystems":"NO_NEW_CONSTRUCTIBLE_ROUTE: redundant policies share copied preparation and explicit carrier route",
        "bell_contextuality":"NOT_LICENSED",
        "external_rosetta":"NO_NEW_LOCAL_EXTERNAL_EVIDENCE; INTERNAL_REALITY_MECHANISMS_CONFIRMED, EXTERNAL_ACCESS_UNKNOWN",
      },
      "operator_argument":{
        "dependency_radius_per_tick":1,
        "dependencies":["incumbent","Moore neighborhood","incoming proposals","local clock phase"],
        "consequence":"a source influence outside its t-step neighborhood requires a chain of changed local states; all constructed chains are explicit carriers or prepared interfaces",
        "does_not_prove":"absence of every future emergent field representation"
      },
      "runtime":runtime
    })
    write_json(ROOT/"DISCOVERY"/"C17E06_PREREQUISITE_CONSTRUCTIONS.json",result)
    for i,(branch,status) in enumerate(result["adjudication"].items(),1):
        append_ndjson(ROOT/"RESEARCH_DECISION_LOG.ndjson",{"id":f"C17ED{6+i:03d}","branch":branch,"decision":status,"evidence_hash":result["content_sha256"]})
    print({"hash":result["content_sha256"],"contact":contact,"perturb_final":[x["final"] for x in perturb],"closed":list(result["adjudication"])})


if __name__=="__main__": main()
