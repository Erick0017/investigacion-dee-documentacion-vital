"""New external experiences on one restored live ABCD session, without resets.

The curriculum is an explicit finite EXPERIENCE_PROTOCOL, not a response table.
Old matter remains. Reacquisition, interference, rejected admission and lingering
old expressions are all preserved. Neither this script nor the metadata select
the native response from the case or copy an old result into RAW.
"""
from __future__ import annotations
from datetime import datetime,timezone
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/"src"))
from red.session import NetworkSession,protocol
from red import recipe as r

KEY="cpc4.extension02.abcd.curriculum.v1"


def present_epoch(session,conditions,offset):
    if type(offset) is not int or offset<=session.world.runtime.current_tick or session.world.runtime.paused:
        raise ValueError("A new finite external experience must start in the future of the same unpaused world")
    if not conditions.get("roles"):raise ValueError("This curriculum uses the prepared D-to-B role route")
    before=r.digest(session.world);receipts=[]
    for item in protocol(conditions):
        if item["channel"]=="instrument.sham":continue
        at=item["tick"]+offset
        receipt=session.world.submit(item["channel"],item["load"],at)
        receipts.append({**item,"requested_tick":at,"receipt_id":receipt.id,"call_tick":session.world.runtime.current_tick,
                         "modality":"EXPERIENCE_PROTOCOL"})
    after=r.digest(session.world)
    if before!=after:raise RuntimeError("Scheduling future experience changed current physical state")
    prior=session.world.runtime.snapshot_metadata(KEY)
    history=json.loads(prior) if prior else {"version":1,"episodes":[]}
    history["episodes"].append({"offset":offset,"external_conditions":conditions,"input_calls":receipts,
                                "current_physical_unchanged_when_scheduled":True})
    session.world.runtime.set_snapshot_metadata(KEY,json.dumps(history,separators=(",",":")))
    return receipts


def freeze(parent,output):
    config={"frozen_utc":datetime.now(timezone.utc).isoformat(),"parent_checkpoint":str(parent.resolve()),
            "parent_sha256":r.sha(parent),"parent_tick":431,"source_sha256":r.sha(__file__),
            "same_Runtime_after_load":True,"operational_forks":0,"new_preparations":0,
            "architecture_family":1,"origin_of_conditions":"Explicit synthetic external experiences, not a decoded answer or reward",
            "episodes":[
                {"offset":500,"conditions":{"id":"C_CONTEXT_REVERSED_SAME_MAIN","roles":True,"A_history":1,"B_history":1,"C_history":-1,"D_history":-1,"event":"U"}},
                {"offset":1000,"conditions":{"id":"C_CONTEXT_REEXPERIENCED_DIFFERENT_RELEVANCE","roles":True,"A_history":1,"B_history":1,"C_history":1,"D_history":-1,"event":"V"}},
            ],
            "scope":"The four previous cores are not cleared, moved, reset or replaced. The incoming experience can acquire another relation in a region whose previous carrier was consumed; this is not automatically reversal of a preserved prior memory."}
    r.put(output/"EXPERIMENT_CONFIG.json",config)
    (output/"EXECUTED_SOURCE.py").write_bytes(Path(__file__).read_bytes())
    return config


def run(config,output):
    parent=Path(config["parent_checkpoint"])
    if r.sha(parent)!=config["parent_sha256"] or r.sha(__file__)!=config["source_sha256"]:
        raise ValueError("Frozen curriculum provenance changed")
    session=NetworkSession.load(parent)
    if session.world.runtime.current_tick!=431:raise ValueError("Exact identified continuing individual required")
    before=r.digest(session.world);session.save(output/"SAME_MAIN_START431.deetsnap")
    episodes=[]
    for episode in config["episodes"]:
        offset=episode["offset"];calls=present_epoch(session,episode["conditions"],offset)
        trace=[]
        for rel in (3,13,15,27,70,80,82,86,94,161,228,291,350,417,424,431):
            trace.append(session.run_until(offset+rel))
            if rel in (3,13,94,161,228,350,417,431):session.save(output/("T"+str(offset+rel)+".deetsnap"))
            r.put(output/"PROGRESS.json",{"current_tick":session.world.runtime.current_tick,"episodes_completed":len(episodes),"current_episode":episode,"trace":trace})
        by_tick={row["tick"]:row for row in trace}
        resource=by_tick[offset+424]["role_samples"]["resource_receiver"]
        function=by_tick[offset+431]["role_samples"]["function_receiver"]
        R=int(resource["active"] and resource["s_reg"]==3 and resource["direction"]==[1,-1,-1])
        F=int(function["active"] and function["s_reg"]==7 and function["direction"]==[1,0,0])
        record={"episode":episode,"trace":trace,"receipts":[r.receipt(session.world,x["receipt_id"]) for x in calls],
                "D_first":by_tick[offset+161]["samples"]["D"],"D_reused":by_tick[offset+228]["samples"]["D"],
                "B_social":by_tick[offset+350]["samples"]["B"],"B_later_query":by_tick[offset+417]["samples"]["B"],
                "task_profile":[F,R],"external_utility":2*F+R,"current_physical":r.digest(session.world)}
        episodes.append(record);r.put(output/"MEASUREMENTS.json",{"config":config,"initial":before,"episodes":episodes,
            "final":r.digest(session.world),"operational_forks":0,"new_preparations":0,
            "scope":"One native continuing world. Entries are newly presented synthetic experiences; no old carrier was removed to make room. Interpretation distinguishes new acquisition from retained-history overwrite."})
    return session,episodes


def main():
    p=argparse.ArgumentParser();p.add_argument("--parent",type=Path,required=True);p.add_argument("--output",type=Path,required=True);p.add_argument("--freeze-only",action="store_true")
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    cpath=a.output/"EXPERIMENT_CONFIG.json"
    config=json.loads(cpath.read_text(encoding="utf-8")) if cpath.exists() else freeze(a.parent,a.output)
    if a.freeze_only:print(json.dumps({"frozen":True,"parent_sha256":config["parent_sha256"]}));return
    session,episodes=run(config,a.output)
    print(json.dumps({"tick":session.world.runtime.current_tick,"episode_profiles":[x["task_profile"] for x in episodes],
                      "D_reads":[[x["D_first"],x["D_reused"]] for x in episodes]}))


if __name__=="__main__":main()
