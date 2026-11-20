#!/usr/bin/env python3
"""Remove payload-gradient contamination from the AB/BA order apparatus."""
from __future__ import annotations

import json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from ing02_common import ROOT,load_kernel,seal,write_json
from temporal_order_apparatus_v1 import run_case


def at(row,tick):return next(r for r in row["trace"] if r["tick"]==tick)


def main():
    kernel,runtime=load_kernel(1);rows=[];modes=("AB","BA","simultaneous_early","simultaneous_late","no_events","route_cut","finite_reader")
    for n in (17,23,29):
        for mode in modes:rows.append(run_case(kernel,{"challenge_id":f"D17-{n}-{mode}","n":n,"origin":(n//2,)*3,"mode":mode,"event_sreg":0,"horizon":128}))
    adjud=[]
    for r in rows:
        expected=1 if r["mode"]=="AB" else -1 if r["mode"]=="BA" else 0
        samples=[at(r,t)["x"] for t in (16,32,64,128)]
        delta=at(r,1)["delta"]
        exact=delta==expected and (all(x==expected for x in samples) if r["mode"]!="route_cut" else all(x is None for x in samples))
        adjud.append({"n":r["n"],"mode":r["mode"],"expected":expected,"tick1_delta":delta,"sample_x":samples,"terminal_support":r["terminal"]["support"],"exact":exact})
    result=seal({"schema":"dee.v27.ing02.discovery.temporal_order_zero_payload.v1",
        "question":"Does order decoding survive removal of event payload gradients, leaving active timing as the causal writer?",
        "change_from_D16":"event s_reg 3 -> 0; schedule, clocks, geometry and reader source unchanged.",
        "rows":rows,"adjudication":adjud,"summary":{"AB_exact":sum(a["mode"]=="AB" and a["exact"] for a in adjud),"BA_exact":sum(a["mode"]=="BA" and a["exact"] for a in adjud),"controls_exact":sum(a["mode"] in {"simultaneous_early","simultaneous_late","no_events"} and a["exact"] for a in adjud)},"runtime":runtime})
    output=ROOT/"DISCOVERY"/"ING02_D17_TEMPORAL_ORDER_ZERO_PAYLOAD.json";write_json(output,result)
    print(json.dumps({"output":str(output),"summary":result["summary"],"hash":result["content_sha256"]},indent=2))


if __name__=="__main__":main()
