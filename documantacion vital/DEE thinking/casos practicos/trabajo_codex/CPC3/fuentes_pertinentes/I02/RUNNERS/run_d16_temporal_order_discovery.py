#!/usr/bin/env python3
"""Discovery panel for native AB/BA memory and functional action."""
from __future__ import annotations

import json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from ing02_common import ROOT,load_kernel,seal,write_json
from temporal_order_apparatus_v1 import run_case


def trace_at(row,tick):return next(r for r in row["trace"] if r["tick"]==tick)


def main():
    kernel,runtime=load_kernel(1);rows=[]
    modes=("AB","BA","simultaneous_early","simultaneous_late","no_events","route_cut","finite_reader")
    for n in (17,23,29):
        for mode in modes:rows.append(run_case(kernel,{"challenge_id":f"D16-{n}-{mode}","n":n,"origin":(n//2,)*3,"mode":mode,"horizon":128}))
    adjudication=[]
    for row in rows:
        r1=trace_at(row,1);r7=trace_at(row,7);expected=1 if row["mode"]=="AB" else -1 if row["mode"]=="BA" else 0
        adjudication.append({"n":row["n"],"mode":row["mode"],"tick1_delta":r1["delta"],"tick7_x":r7["x"],
            "expected":expected,"exact":r1["delta"]==expected and (r7["x"]==expected if row["mode"] not in {"route_cut"} else r7["x"] is None)})
    result=seal({"schema":"dee.v27.ing02.discovery.temporal_order.v1",
        "question":"Can the same two event identities write AB versus BA as opposite relative states and drive opposite native actions without Python history decoding?",
        "anti_cheating":"Both events and clocks are frozen at t0; late events are state0 carriers that become active after one native tick; Python neither reads nor acts during episodes.",
        "rows":rows,"adjudication":adjudication,
        "summary":{"AB_exact":sum(a["mode"]=="AB" and a["exact"] for a in adjudication),"BA_exact":sum(a["mode"]=="BA" and a["exact"] for a in adjudication),
            "simultaneous_zero_exact":sum(a["mode"] in {"simultaneous_early","simultaneous_late"} and a["exact"] for a in adjudication)},"runtime":runtime})
    output=ROOT/"DISCOVERY"/"ING02_D16_TEMPORAL_ORDER.json";write_json(output,result)
    print(json.dumps({"output":str(output),"summary":result["summary"],"hash":result["content_sha256"]},indent=2))


if __name__=="__main__":main()
