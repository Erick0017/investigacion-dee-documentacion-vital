"""Frozen-capable CORE15 shadow predicates. Observations always come from v27 telemetry."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from native_core import NativeWorld, fields, pack
from core12_apparatus import convergent_phase_paths, regenerative_interface_trial
from run_c6h01_associative_plasticity_holdout import BASE as ASSOC_BASE, simulate as assoc_sim, transform as assoc_transform
from run_c6h08_dissipative_ensemble_holdout import DIRECTIONS, prepared_support, simulate as ensemble_sim


def add(q, d, k, n):
    return tuple((q[i] + k * d[i]) % n for i in range(3))


def record(value):
    if int(value) == 0:
        return None
    a = np.array([value], dtype=np.uint64); fs = fields(a)
    return {"state": int(fs["state"][0]), "sreg": int(fs["sreg"][0]), "direction": [int(fs[k][0]) for k in ("dx", "dy", "dz")], "semantic": int(fs["semantic"][0])}


def raw_trace(kernel, raw, clock, horizon):
    w = NativeWorld(kernel, raw, clock); out=[]
    for tick in range(horizon+1):
        out.append({"tick":tick,"raw_hash":hashlib.sha256(w.raw.tobytes()).hexdigest(),"clock_hash":hashlib.sha256(w.clock.tobytes()).hexdigest(),"support":int(np.count_nonzero(w.raw))})
        if tick<horizon:w.tick()
    return out


def direction_trial(kernel, cfg, canary=False):
    n=cfg["n"];q=tuple(cfg["q"]);d1=tuple(cfg["d1"]);d2=d1 if canary else tuple(cfg["d2"])
    def run(d):
        raw=np.zeros((n,n,n),np.uint64);clock=np.zeros_like(raw);raw[q]=pack(cfg["state"],cfg["sreg"],d,1);return raw_trace(kernel,raw,clock,2)
    a,b=run(d1),run(d2); observed=a[1]["raw_hash"]!=b[1]["raw_hash"]; expected=not canary
    return {"family":"direction","canary":canary,"config":cfg,"observed_divergence":observed,"expected_divergence":expected,"pass":observed==expected,"A":a,"B":b}


def payload_trial(kernel,cfg,canary=False):
    n=cfg["n"];center=tuple(cfg["center"]);d=cfg["distance"]
    def run(second):
        raw=np.zeros((n,n,n),np.uint64);clock=np.zeros_like(raw);raw[add(center,(-1,0,0),d,n)]=pack(11,cfg["sreg_a"],(1,0,0),1);raw[add(center,(1,0,0),d,n)]=pack(17,second,(-1,0,0),1);w=NativeWorld(kernel,raw,clock);seen=[]
        for tick in range(d+2):
            if int(w.raw[center]):seen.append({"tick":tick,"record":record(w.raw[center])})
            if tick<d+1:w.tick()
        return seen
    second_b=cfg["sreg_b1"] if canary else cfg["sreg_b2"];a,b=run(cfg["sreg_b1"]),run(second_b);observed=a!=b;expected=not canary
    return {"family":"payload","canary":canary,"config":cfg,"observed_divergence":observed,"expected_divergence":expected,"pass":observed==expected,"A":a,"B":b}


def semantic_trial(kernel,cfg,canary=False):
    n=cfg["n"];source=tuple(cfg["source"]);direction=tuple(cfg["direction"]);detector=add(source,direction,cfg["distance"],n);h=cfg["distance"]+10
    def run(semantic):
        raw=np.zeros((n,n,n),np.uint64);clock=np.zeros_like(raw);raw[source]=pack(0,cfg["sreg"],direction,semantic);w=NativeWorld(kernel,raw,clock);events=[]
        for tick in range(h+1):
            if int(w.raw[detector]):events.append({"tick":tick,"record":record(w.raw[detector])})
            if tick<h:w.tick()
        return events
    sem_b=1 if canary else 4;a,b=run(1),run(sem_b);observed=a!=b;expected=not canary
    return {"family":"semantic","canary":canary,"config":cfg,"observed_divergence":observed,"expected_divergence":expected,"pass":observed==expected,"A":a,"B":b}


def clock_trial(kernel,cfg,canary=False):
    n=cfg["n"];q=tuple(cfg["q"]);d1=tuple(cfg["direction"]);d2=tuple(cfg["canary_direction"]) if canary else d1
    raw_a=np.zeros((n,n,n),np.uint64);raw_b=np.zeros_like(raw_a);raw_a[q]=pack(cfg["state"],cfg["sreg"],d1,1);raw_b[q]=pack(cfg["state"],cfg["sreg"],d2,1)
    c0=np.zeros_like(raw_a);c1=np.zeros_like(raw_a);c1[q]=np.uint64(cfg["clock"]);a=raw_trace(kernel,raw_a,c0,cfg["horizon"]);b=raw_trace(kernel,raw_b,c1,cfg["horizon"])
    raw_equal=all(x["raw_hash"]==y["raw_hash"] for x,y in zip(a,b));clock_diff=any(x["clock_hash"]!=y["clock_hash"] for x,y in zip(a,b));expected_raw_equal=not canary
    return {"family":"clock","canary":canary,"config":cfg,"raw_trajectory_equal":raw_equal,"clock_trajectory_different":clock_diff,"expected_raw_equal":expected_raw_equal,"pass":raw_equal==expected_raw_equal and clock_diff,"A":a,"B":b}


def guard_trial(kernel,cfg,canary=False):
    args=(cfg["n"],cfg["source_distance"],cfg["downstream_distance"],cfg["horizon"]);d=tuple(cfg["direction"]);center=tuple(cfg["center"])
    a=regenerative_interface_trial(kernel,*args,"semantic4_full",d,center,cfg["sreg"])
    b=regenerative_interface_trial(kernel,*args,"semantic4_full" if canary else "semantic4_shuffled",d,center,cfg["sreg"])
    key=str(cfg["downstream_distance"]);ea=a["downstream_event_ticks"][key];eb=b["downstream_event_ticks"][key];observed=ea!=eb;expected=not canary
    return {"family":"guard_geometry","canary":canary,"config":cfg,"organized_events":ea,"comparison_events":eb,"observed_divergence":observed,"expected_divergence":expected,"pass":observed==expected and (canary or (not ea and bool(eb)))}


def ensemble_trial(kernel,cfg,canary=False):
    n=cfg["n"];rng=np.random.default_rng(cfg["seed"]);cap=(n//3)**3;count=max(8,int(round(cap*cfg["fill"])));support=prepared_support(n,count,rng);sregs=[int(x) for x in rng.integers(1,8,size=count)];clocks=[int(x) for x in rng.integers(0,2**32,size=count,dtype=np.uint64)];mixed=[DIRECTIONS[int(i)] for i in rng.integers(0,len(DIRECTIONS),size=count)];aligned=[tuple(cfg["direction"])]*count;h=5*n
    at,exact=ensemble_sim(kernel,n,support,sregs,clocks,aligned,h,True);bt,bexact=ensemble_sim(kernel,n,support,sregs,clocks,aligned if canary else mixed,h,True if canary else False)
    observed=(at[-1]["support"],at[-1]["sreg_sum"])!=(bt[-1]["support"],bt[-1]["sreg_sum"]);expected=not canary
    mixed_contract=(bt[-1]["support"]<bt[0]["support"]) if not canary else False
    return {"family":"ensemble_direction","canary":canary,"config":cfg,"observed_divergence":observed,"expected_divergence":expected,"aligned_translation_exact":exact,"comparison_translation_exact":bexact,"mixed_contracts":mixed_contract,"pass":observed==expected and exact and (canary or mixed_contract),"aligned":at,"comparison":bt}


def phase_trial(kernel,cfg,canary=False):
    args=(cfg["n"],cfg["path_length"]);center=tuple(cfg["center"]);sregs=tuple(cfg["sregs"]);frame=tuple(cfg["frame"]);h=cfg["path_length"]+12
    a=convergent_phase_paths(kernel,*args,"AB_coherent",center,sregs,h,frame);b=convergent_phase_paths(kernel,*args,"AB_coherent" if canary else "AB_phase_shifted",center,sregs,h,frame)
    ea=(a["detector_event_ticks"],a["detector_event_sregs"],a["detector_event_directions"]);eb=(b["detector_event_ticks"],b["detector_event_sregs"],b["detector_event_directions"]);observed=ea!=eb;expected=not canary
    return {"family":"phase_history","canary":canary,"config":cfg,"observed_divergence":observed,"expected_divergence":expected,"pass":observed==expected,"coherent":ea,"comparison":eb}


def assoc_cell(cfg):
    index=cfg["index"];n=cfg["n"];rng=np.random.default_rng(cfg["seed"]);junction=tuple(cfg["junction"]);frame=(tuple(cfg["frame_axes"]),tuple(cfg["frame_signs"]));vectors={k:list(assoc_transform(v,*frame)) for k,v in ASSOC_BASE.items()}
    return {"cell_id":cfg["trial_id"],"n":n,"junction":list(junction),"train_tick":cfg["train_tick"],"delay":cfg["delay"],"query_path":3,"vectors":vectors,"cue_sreg":7+index,"teacher_sreg":13+index,"query_sreg":19+index,"eraser_sreg":23,"states":cfg["states"],"clocks":cfg["clocks"]}


def history_trial(kernel,cfg,canary=False):
    cell=assoc_cell(cfg);a=assoc_sim(kernel,cell,"trained_pair");b=assoc_sim(kernel,cell,"trained_pair" if canary else "history_shuffled");observed=bool(a["trained_exact"])!=bool(b["trained_exact"]);expected=not canary
    return {"family":"ordered_history","canary":canary,"config":cfg,"trained_exact_A":bool(a["trained_exact"]),"trained_exact_B":bool(b["trained_exact"]),"observed_divergence":observed,"expected_divergence":expected,"pass":observed==expected and bool(a["trained_exact"]) and (canary or not bool(b["trained_exact"])),"A":a,"B":b}


RUNNERS={"direction":direction_trial,"payload":payload_trial,"semantic":semantic_trial,"clock":clock_trial,"guard_geometry":guard_trial,"ensemble_direction":ensemble_trial,"phase_history":phase_trial,"ordered_history":history_trial}


def execute(kernel, trial, canary=False):
    return RUNNERS[trial["family"]](kernel,trial["config"],canary)
