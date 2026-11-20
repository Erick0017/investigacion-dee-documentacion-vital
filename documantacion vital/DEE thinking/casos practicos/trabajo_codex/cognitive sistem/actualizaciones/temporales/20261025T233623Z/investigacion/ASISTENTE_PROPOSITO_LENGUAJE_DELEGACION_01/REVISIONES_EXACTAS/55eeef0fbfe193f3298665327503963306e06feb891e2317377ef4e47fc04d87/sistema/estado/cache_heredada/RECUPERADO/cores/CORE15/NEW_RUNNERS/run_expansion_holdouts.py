#!/usr/bin/env python3
"""Frozen fresh-world confirmation engine for promoted CORE15 expansion claims."""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extension_common import ROOT, audit_kernel, canonical_hash, read_json, sha, utc, write_json
from native_core import NativeWorld, fields, pack, verify_and_load_kernel
from core12_apparatus import regenerative_interface_trial, source_train_trial
from run_c6h01_associative_plasticity_holdout import BASE as ASSOC_BASE, simulate as assoc_sim, transform as assoc_transform


OUT=ROOT/"NEW_RAW_TELEMETRY"; CHALLENGE=ROOT/"NEW_FRESH_CHALLENGES"/"CHALLENGE_MANIFEST.json"; FREEZE=ROOT/"SOURCE_FREEZE_EXPANSION.json"
DIRECTIONS=[d for d in itertools.product((-1,0,1),repeat=3) if d!=(0,0,0)]


def add(q,d,k,n): return tuple((q[i]+k*d[i])%n for i in range(3))


def unpack(value):
    if int(value)==0: return None
    f=fields(np.array([value],dtype=np.uint64)); return {"state":int(f["state"][0]),"sreg":int(f["sreg"][0]),"direction":[int(f[k][0]) for k in ("dx","dy","dz")],"semantic":int(f["semantic"][0])}


def raw_hash(a): return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def normalized(raw,d,tick):
    n=raw.shape[0]; return sorted(tuple((int(q[i])-tick*d[i])%n for i in range(3)) for q in np.argwhere(raw!=0))


def tick_trace(kernel,raw,clock,horizon):
    w=NativeWorld(kernel,raw,clock); trace=[]
    for t in range(horizon+1):
        trace.append({"tick":t,"raw_sha256":raw_hash(w.raw),"clock_sha256":raw_hash(w.clock),"support":int(np.count_nonzero(w.raw))})
        if t<horizon: w.tick()
    return trace


def verify_freeze():
    freeze=read_json(FREEZE); bad=[]
    for rel,expected in freeze["source_hashes"].items():
        p=ROOT/rel
        if not p.is_file() or sha(p)!=expected: bad.append(rel)
    if bad: raise RuntimeError(f"source freeze mismatch: {bad}")
    return freeze


def mobile_trial(kernel,cfg,canary):
    n=cfg["n"]; d=tuple(cfg["direction"]); origin=tuple(cfg["origin"]); offsets=[tuple(x) for x in cfg["offsets"]]; raw=np.zeros((n,n,n),np.uint64); payloads=[]
    for i,off in enumerate(offsets):
        q=tuple((origin[j]+off[j])%n for j in range(3)); dd=(-d[0],-d[1],-d[2]) if canary and i==0 else d; s=cfg["sreg_base"]+i*cfg["sreg_step"]; payloads.append(s); raw[q]=pack(cfg["state_base"]+i,s,dd,1)
    initial=normalized(raw,d,0); w=NativeWorld(kernel,raw); exact=True
    for t in range(cfg["horizon"]+1):
        exact=exact and normalized(w.raw,d,t)==initial
        if t<cfg["horizon"]: w.tick()
    observed=exact and int(np.count_nonzero(w.raw))==len(offsets)
    expected=not canary
    return {"observed_exact_mobile_identity":observed,"expected":expected,"pass":observed==expected,"generic_readout":{"final_support":int(np.count_nonzero(w.raw)),"raw_sha256":raw_hash(w.raw)}}


def reducer_trial(kernel,cfg,canary):
    n=cfg["n"]; c=tuple(cfg["center"]); raw=np.zeros((n,n,n),np.uint64); directions=[tuple(d) for d in cfg["directions"]]; loads=cfg["loads"]
    for i,(d,s) in enumerate(zip(directions,loads)):
        distance=2 if canary and i==0 else 1; raw[add(c,d,-distance,n)]=pack(cfg["state_base"]+i,s,d,1)
    w=NativeWorld(kernel,raw); w.tick(); rec=unpack(w.raw[c]); expected_sreg=min(sum(loads),19664)
    observed=rec is not None and rec["sreg"]==expected_sreg
    expected=not canary
    return {"observed_simultaneous_capped_sum":observed,"expected":expected,"pass":observed==expected,"generic_readout":{"center_tick1":rec,"raw_sha256":raw_hash(w.raw)}}


def closure_trial(kernel,cfg,canary):
    rng=np.random.default_rng(cfg["seed"]); n=cfg["n"]; raw=np.zeros((n,n,n),np.uint64); occ=set()
    while len(occ)<cfg["count"]: occ.add(tuple(int(x) for x in rng.integers(0,n,size=3)))
    dest=[]
    if canary:
        c=tuple(sorted(occ)[0]); d=(1,0,0); raw[c]=pack(1,31,d,1); target=add(c,d,1,n); raw[target]=pack(2,41,(0,0,0),1); dest=[target,target]
    else:
        for attempt in range(100):
            raw.fill(0); dest=[]
            for i,q in enumerate(sorted(occ)):
                d=DIRECTIONS[int(rng.integers(0,len(DIRECTIONS)))]; raw[q]=pack(100+i,int(rng.integers(1,500)),d,1); dest.append(add(q,d,1,n))
            if not any(q in occ for q in dest): break
        else: raise RuntimeError("could not generate empty-destination closure case")
    predicted=len(set(dest)); w=NativeWorld(kernel,raw); w.tick(); observed=int(np.count_nonzero(w.raw)); relation=predicted==observed; expected=not canary
    return {"predicted_unique_destinations":predicted,"observed_next_support":observed,"observed_relation":relation,"expected":expected,"pass":relation==expected,"generic_readout":{"raw_sha256":raw_hash(w.raw)}}


def clock_raw(cfg):
    n=cfg["n"]; c=tuple(cfg["center"]); raw=np.zeros((n,n,n),np.uint64); kind=cfg["mechanism"]
    if kind=="singleton": raw[add(c,(1,0,0),-5,n)]=pack(1,101,(1,0,0),1)
    elif kind=="source": raw[add(c,(1,0,0),-5,n)]=pack(1,101,(1,0,0),4)
    elif kind=="collision": raw[add(c,(1,0,0),-1,n)]=pack(1,101,(1,0,0),1); raw[add(c,(-1,0,0),-1,n)]=pack(2,211,(-1,0,0),1)
    elif kind=="guard":
        for i,s in enumerate(itertools.product((-1,1),repeat=3)): raw[tuple(c[j]+s[j] for j in range(3))]=pack(100+i,31+i,(0,0,0),4)
        raw[add(c,(1,0,0),-6,n)]=pack(1,101,(1,0,0),4)
    elif kind=="ensemble":
        for i,d in enumerate(DIRECTIONS[:10]): raw[((3*i+2)%n,(5*i+3)%n,(7*i+4)%n)]=pack(10+i,31+i,d,1)
    else: raise ValueError(kind)
    return raw


def clock_trial(kernel,cfg,canary):
    raw=clock_raw(cfg); zero=np.zeros_like(raw); altered=np.zeros_like(raw); altered[raw!=0]=np.arange(1,np.count_nonzero(raw)+1,dtype=np.uint64)*np.uint64(0x102030405)
    raw_b=raw.copy()
    if canary:
        q=tuple(np.argwhere(raw_b!=0)[0]); rec=unpack(raw_b[q]); raw_b[q]=pack(rec["state"],rec["sreg"],(-1,0,0),rec["semantic"])
    ta=tick_trace(kernel,raw,zero,cfg["horizon"]); tb=tick_trace(kernel,raw_b,altered,cfg["horizon"]); equal=all(a["raw_sha256"]==b["raw_sha256"] for a,b in zip(ta,tb)); expected=not canary
    return {"observed_raw_trajectory_equal":equal,"expected":expected,"pass":equal==expected,"generic_readout":{"trace_A":ta,"trace_B":tb}}


def opacity_trial(kernel,cfg,canary):
    mode="semantic4_shuffled" if canary else "semantic4_full"
    r=regenerative_interface_trial(kernel,n=cfg["n"],source_distance=cfg["source_distance"],downstream_distance=cfg["downstream_distance"],horizon=cfg["horizon"],mode=mode,direction=tuple(cfg["direction"]),center=tuple(cfg["center"]),source_sreg=cfg["sreg"])
    events=r["downstream_event_ticks"][str(cfg["downstream_distance"])]; blocked=not events; expected=not canary
    return {"observed_blocked":blocked,"expected":expected,"pass":blocked==expected,"generic_readout":{"downstream_events":events,"incident_expected":r["incident_expected_ticks"]}}


def dispersion_trial(kernel,cfg,canary):
    n=cfg["n"]; d=tuple(cfg["direction"]); source=tuple(cfg["source"]); raw=np.zeros((n,n,n),np.uint64); raw[source]=pack(1,cfg["sreg"],d,1)
    if canary: raw[add(source,d,1,n)]=pack(2,29,(0,0,0),1)
    detector=add(source,d,cfg["distance"],n); w=NativeWorld(kernel,raw); arrivals=[]
    for t in range(cfg["distance"]+5):
        if int(w.raw[detector])!=0: arrivals.append(t)
        if t<cfg["distance"]+4: w.tick()
    relation=arrivals==[cfg["distance"]]; expected=not canary
    return {"arrivals":arrivals,"observed_unit_delay":relation,"expected":expected,"pass":relation==expected,"generic_readout":{"final_raw_sha256":raw_hash(w.raw)}}


def main():
    marker=ROOT/"CHECKPOINTS"/"E_FRESH_CONFIRMATION_COMPLETE.json"
    if marker.exists(): print(marker.read_text(encoding="utf-8")); return
    freeze=verify_freeze(); audit_kernel("CORE15_EXPANSION_BEFORE_FRESH_CONFIRMATION"); kernel,environment=verify_and_load_kernel(1); manifest=read_json(CHALLENGE); dispatch={"C15XC01":mobile_trial,"C15XC02":reducer_trial,"C15XC03":closure_trial,"C15XC04":clock_trial,"C15XC05":opacity_trial,"C15XC06":dispersion_trial}; trials=[]
    for case in manifest["cases"]:
        fn=dispatch[case["claim_id"]]; result=fn(kernel,case["configuration"],case["role"]=="CANARY"); trials.append({"trial_id":case["trial_id"],"claim_id":case["claim_id"],"role":case["role"],"configuration_hash":case["configuration_hash"],**result})
    by_claim={}
    for claim in dispatch:
        rows=[x for x in trials if x["claim_id"]==claim]; positives=[x for x in rows if x["role"]=="POSITIVE"]; canaries=[x for x in rows if x["role"]=="CANARY"]
        by_claim[claim]={"positive_pass":sum(x["pass"] for x in positives),"positive_total":len(positives),"canary_correct":sum(x["pass"] for x in canaries),"canary_total":len(canaries),"fresh_status":"FRESH_CONFIRMED" if all(x["pass"] for x in rows) else "FRESH_FAIL"}
    summary={"schema":"dee.v27.core15.expansion.fresh.v1","source_freeze_sha256":freeze["freeze_sha256"],"challenge_manifest_sha256":sha(CHALLENGE),"environment":environment,"trials":trials,"by_claim":by_claim,"totals":{"positive_pass":sum(v["positive_pass"] for v in by_claim.values()),"positive_total":sum(v["positive_total"] for v in by_claim.values()),"canary_correct":sum(v["canary_correct"] for v in by_claim.values()),"canary_total":sum(v["canary_total"] for v in by_claim.values())},"post_hoc_repairs":0,"completed_utc":utc()}; summary["verdict"]="PASS" if summary["totals"]["positive_pass"]==summary["totals"]["positive_total"] and summary["totals"]["canary_correct"]==summary["totals"]["canary_total"] else "FAIL"; summary["content_sha256"]=canonical_hash(summary); write_json(OUT/"EXPANSION_FRESH_CONFIRMATION.json",summary); write_json(marker,{"checkpoint":"E_FRESH_CONFIRMATION_COMPLETE","pass":summary["verdict"]=="PASS","verdict":summary["verdict"],**summary["totals"],"completed_utc":utc()}); audit_kernel("CORE15_EXPANSION_AFTER_FRESH_CONFIRMATION"); print(json.dumps({"verdict":summary["verdict"],**summary["totals"],"by_claim":by_claim},indent=2,sort_keys=True)); raise SystemExit(0 if summary["verdict"]=="PASS" else 2)


if __name__=="__main__": main()

