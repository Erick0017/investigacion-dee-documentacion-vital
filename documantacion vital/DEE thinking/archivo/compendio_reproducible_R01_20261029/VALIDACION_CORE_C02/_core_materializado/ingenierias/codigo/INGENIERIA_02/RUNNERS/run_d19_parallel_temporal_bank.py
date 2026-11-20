#!/usr/bin/env python3
"""Parallel bank of independently experience-written temporal-order memories."""
from __future__ import annotations

import json,sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from ing02_common import NativeWorld,ROOT,load_kernel,read,seal,summarize,write_json
from temporal_order_apparatus_v1 import construct


ORIGINS=((12,12,12),(36,12,12),(60,12,12),(12,36,36),(36,36,36),(60,36,36),(12,60,60),(36,60,60))
PATTERN=("AB","BA","BA","AB","AB","BA","AB","BA")


def make_bank(kernel,n=73,modes=PATTERN):
    raw=np.zeros((n,n,n),np.uint64);clock=np.zeros_like(raw);ports=[]
    for index,(origin,mode) in enumerate(zip(ORIGINS,modes)):
        sub,subports=construct(kernel,{"n":n,"origin":origin,"mode":mode,"event_sreg":0})
        mask=sub.raw!=0
        if np.any(raw[mask]!=0):raise RuntimeError(f"bank overlap at organization {index}")
        raw[mask]=sub.raw[mask];clock[mask]=sub.clock_a[mask]
        ports.append({"index":index,"origin":list(origin),"mode":mode,"expected":1 if mode=="AB" else -1,
            "a":subports["a"],"b":subports["b"],"comparator":subports["comparator"]})
    return NativeWorld(kernel,raw,clock),ports


def run(kernel,modes,horizon=32):
    world,ports=make_bank(kernel,modes=modes);telemetry=[]
    for tick in range(1,horizon+1):
        world.tick()
        if tick in {1,2,4,8,16,32}:
            records=[]
            for p in ports:
                a,b,c=(read(world.raw,p[k]) for k in ("a","b","comparator"))
                records.append({"index":p["index"],"mode":p["mode"],"expected":p["expected"],
                    "delta":None if a is None or b is None else a["sreg"]-b["sreg"],"x":None if c is None else c["direction"][0]})
            telemetry.append({"tick":tick,"records":records,"support":int(np.count_nonzero(world.raw))})
    final=next(r for r in telemetry if r["tick"]==32)
    at16=next(r for r in telemetry if r["tick"]==16)
    return {"modes":list(modes),"horizon":horizon,"telemetry":telemetry,
        "tick16_exact":all(r["delta"]==r["expected"] and r["x"]==r["expected"] for r in at16["records"]),
        "tick32_exact":all(r["delta"]==r["expected"] and r["x"]==r["expected"] for r in final["records"]),
        "terminal":summarize(world.raw,world.clock_a),"python_interventions_after_t0":0}


def main():
    kernel,runtime=load_kernel(1)
    patterns=(PATTERN,tuple(reversed(PATTERN)),("AB",)*8,("BA",)*8)
    rows=[run(kernel,p) for p in patterns]
    result=seal({"schema":"dee.v27.ing02.discovery.parallel_temporal_bank.v1",
        "question":"Can multiple experience-written order memories coexist and produce simultaneous independently addressed native actions?",
        "organization_count_per_world":8,"world_n":73,"rows":rows,
        "summary":{"worlds":len(rows),"tick16_exact":sum(r["tick16_exact"] for r in rows),"tick32_exact":sum(r["tick32_exact"] for r in rows),"simultaneous_memories":8},"runtime":runtime})
    output=ROOT/"DISCOVERY"/"ING02_D19_PARALLEL_TEMPORAL_BANK.json";write_json(output,result)
    print(json.dumps({"output":str(output),"summary":result["summary"],"hash":result["content_sha256"]},indent=2))


if __name__=="__main__":main()
