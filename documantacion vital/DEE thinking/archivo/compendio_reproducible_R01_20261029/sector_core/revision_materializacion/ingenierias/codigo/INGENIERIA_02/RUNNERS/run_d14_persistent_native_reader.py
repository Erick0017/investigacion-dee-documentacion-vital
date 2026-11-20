#!/usr/bin/env python3
"""Construct a semantic4-replenished reader for the integrated relative memory."""
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


def rle(values):
    out=[];start=1;prev=values[0]
    for i,v in enumerate(values[1:],start=2):
        if v!=prev:out.append([start,i-1,prev]);start=i;prev=v
    out.append([start,len(values),prev]);return out


def run(kernel,n,mode,horizon=2000):
    effective_mode="experience_a" if mode in {"treatment","finite_reader_source"} else mode
    world,ports=construct(kernel,{"n":n,"origin":(n//2,)*3,"mode":effective_mode,
        "experience_a":mode in {"treatment","finite_reader_source"},
        "persistent_reader_source":mode!="no_reader","reader_enabled":mode!="no_reader",
        "support_pattern_a":PATTERN_A,"support_pattern_b":PATTERN_B})
    # finite_reader_source must be selected by the apparatus mode itself.
    if mode=="finite_reader_source":
        # Reconstruct with the mode recognized by construct while explicitly retaining experience.
        world,ports=construct(kernel,{"n":n,"origin":(n//2,)*3,"mode":"finite_reader_source","experience_a":True,
            "persistent_reader_source":True,"support_pattern_a":PATTERN_A,"support_pattern_b":PATTERN_B})
    deltas=[];xs=[];source_raw0=int(world.raw[ports["reader_source"]]) if mode!="no_reader" else 0
    source_raw_fixed=True;supports=[]
    for _ in range(horizon):
        world.tick();a,b,c=(read(world.raw,ports[k]) for k in ("a","b","comparator"))
        deltas.append(None if a is None or b is None else a["sreg"]-b["sreg"])
        xs.append(None if c is None else c["direction"][0]);supports.append(int(np.count_nonzero(world.raw)))
        if mode!="no_reader" and int(world.raw[ports["reader_source"]])!=source_raw0:source_raw_fixed=False
    return {"n":n,"mode":mode,"horizon":horizon,"delta_rle":rle(deltas),"x_rle":rle(xs),
        "positive_x_ticks":sum(v is not None and v>0 for v in xs),"zero_x_ticks":sum(v==0 for v in xs),
        "x_transitions":sum(xs[i]!=xs[i-1] for i in range(1,len(xs))),
        "source_raw_fixed":source_raw_fixed if mode!="no_reader" else None,"support_max":max(supports),
        "terminal":summarize(world.raw,world.clock_a),"python_interventions_after_t0":0}


def main():
    kernel,runtime=load_kernel(1);rows=[]
    for n in (17,23,29):
        for mode in ("treatment","no_experience","no_reader","finite_reader_source"):
            rows.append(run(kernel,n,mode))
    result=seal({"schema":"dee.v27.ing02.discovery.persistent_native_reader.v1",
        "question":"Can invariant semantic4 replenishment repeatedly recreate the read interaction without host reset?",
        "apparatus":"Relative memory plus semantic4 reader source two cells upstream; finite semantic1 source and route cut are canaries.",
        "rows":rows,"runtime":runtime})
    output=ROOT/"DISCOVERY"/"ING02_D14_PERSISTENT_NATIVE_READER.json";write_json(output,result)
    print(json.dumps({"output":str(output),"hash":result["content_sha256"]},indent=2))


if __name__=="__main__":main()
