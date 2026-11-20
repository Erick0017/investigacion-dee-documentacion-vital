#!/usr/bin/env python3
"""Search recurrent relative-memory regimes with and without replenished action/read traffic."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from ing02_common import ROOT,load_kernel,read,seal,summarize,write_json
from paired_relative_apparatus_v2 import construct
from run_d09_relative_readout_longevity import PATTERN_A,PATTERN_B


def rle(v):
    out=[];s=1;p=v[0]
    for i,x in enumerate(v[1:],start=2):
        if x!=p:out.append([s,i-1,p]);s=i;p=x
    out.append([s,len(v),p]);return out


def sgn(x):return None if x is None else (1 if x>0 else -1 if x<0 else 0)


def run(kernel,offset,active,horizon=2048):
    mode="experience_a" if active else "no_reader"
    world,ports=construct(kernel,{"n":17,"origin":(8,8,8),"mode":mode,"experience_a":True,
        "memory_phase_a":260,"memory_phase_b":260+offset,"persistent_reader_source":active,"reader_enabled":active,
        "support_pattern_a":PATTERN_A,"support_pattern_b":PATTERN_B})
    ds=[];xs=[];support=[];centers=True
    source0=int(world.raw[ports["reader_source"]]) if active else 0;source_fixed=True
    for _ in range(horizon):
        world.tick();a,b,c=(read(world.raw,ports[k]) for k in ("a","b","comparator"))
        if a is None or b is None:centers=False
        ds.append(None if a is None or b is None else a["sreg"]-b["sreg"])
        xs.append(None if c is None else c["direction"][0]);support.append(int(np.count_nonzero(world.raw)))
        if active and int(world.raw[ports["reader_source"]])!=source0:source_fixed=False
    dsign=[sgn(v) for v in ds];xsign=[sgn(v) for v in xs]
    return {"offset":offset,"active":active,"horizon":horizon,"centers_survive":centers,"source_raw_fixed":source_fixed if active else None,
        "delta_rle":rle(ds),"x_rle":rle(xs),"delta_sign_transitions":sum(dsign[i]!=dsign[i-1] for i in range(1,horizon)),
        "x_sign_transitions":sum(xsign[i]!=xsign[i-1] for i in range(1,horizon)),"support_max":max(support),
        "terminal":summarize(world.raw,world.clock_a),"python_interventions_after_t0":0}


def main():
    kernel,runtime=load_kernel(1);rows=[]
    for offset in range(-20,21):
        rows.append(run(kernel,offset,True));rows.append(run(kernel,offset,False))
    paired=[]
    for offset in range(-20,21):
        a=next(r for r in rows if r["offset"]==offset and r["active"]);c=next(r for r in rows if r["offset"]==offset and not r["active"])
        paired.append({"offset":offset,"trajectory_changed":a["delta_rle"]!=c["delta_rle"],"active_delta_transitions":a["delta_sign_transitions"],
            "cut_delta_transitions":c["delta_sign_transitions"],"active_x_transitions":a["x_sign_transitions"],"support_max":a["support_max"],
            "candidate":a["centers_survive"] and a["source_raw_fixed"] and a["delta_sign_transitions"]>=4 and a["x_sign_transitions"]>=4})
    result=seal({"schema":"dee.v27.ing02.discovery.recurrent_feedback_phase_search.v1",
        "question":"Can replenished native read/action traffic drive repeated organization-level policy transitions?",
        "search":"B clock offset -20..20; paired persistent semantic4 reader/action source and route-cut worlds.",
        "rows":rows,"paired":paired,"candidate_offsets":[p["offset"] for p in paired if p["candidate"]],"runtime":runtime})
    output=ROOT/"DISCOVERY"/"ING02_D15_RECURRENT_FEEDBACK_PHASE_SEARCH.json";write_json(output,result)
    print(json.dumps({"output":str(output),"candidates":result["candidate_offsets"],"hash":result["content_sha256"]},indent=2))


if __name__=="__main__":main()
