"""Two frozen diagnostic localizations of an already observed access limit.

No parameter search, new learning, RAW edit or replacement reader. The second
window replays only probes actually present in the completed inverse branch's
native operation journal. Hypotheses can be falsified and are not forced.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src import channel
from src.common import put,sha
from src.channel_analysis import reconstruct_empty_destination


def parse_probes(world):
    pattern=re.compile(r"^PHYSICAL_PROBE interface=(.*?) at=(\d+) load=(\d+) receipt=(\d+)$")
    result=[]
    for text in world.external_operations:
        match=pattern.match(text)
        if match:
            name,tick,load,identity=match.groups()
            result.append({"channel":name,"tick":int(tick),"load":int(load),"id":int(identity)})
    return result


def investigate(root,config,output):
    import dee_thinking as d
    if d.__version__!="4.0.0" or sha(d._native.__file__)!=channel.NATIVE_SHA256:
        raise RuntimeError("Immutable qualified Native instrument required")
    rows=[]
    for case in config["windows"]:
        folder=output/case["id"];folder.mkdir(parents=True,exist_ok=True)
        source=root/case["source"]
        world=d.OrganizationalWorld.load_snapshot(str(source))
        initial=channel.digest(world)
        if initial["tick"]!=case["start_tick"]:raise ValueError("Identified checkpoint tick differs")
        probes=[]
        if case.get("actual_probe_journal"):
            actual=d.OrganizationalWorld.load_snapshot(str(root/case["actual_probe_journal"]))
            probes=[r for r in parse_probes(actual) if case["start_tick"]<r["tick"]<=case["end_tick"]]
        samples=[];replayed=[];pre=None;post=None;reconstruction=None
        while world.runtime.current_tick<=case["end_tick"]:
            tick=world.runtime.current_tick
            for event in probes:
                if event["tick"]==tick:
                    result=world.probe(event["channel"],event["load"],tick)
                    if result.id!=event["id"]:raise AssertionError("Actual inverse probe receipt sequence differs")
                    replayed.append({**event,"actual_receipt":channel.receipt(world,result.id)})
            forward_site=channel.moved(case["hub"],case["forward_direction"],tick-case["forward_birth"])
            teacher_site=channel.moved(case["hub"],case["teacher_direction"],tick-case["teacher_birth"])
            samples.append({"tick":tick,"forward_candidate":channel.observe(world,forward_site),
                            "teacher_candidate":channel.observe(world,teacher_site),
                            "candidate_meeting":channel.observe(world,case["meeting"] )})
            if tick in (case["collision_tick"]-1,case["collision_tick"],case["collision_tick"]+1):
                world.save_snapshot(str(folder/("T"+str(tick)+".deetsnap")))
            if tick==case["collision_tick"]-1:pre=world.fork()
            if tick==case["collision_tick"]:
                post=channel.observe(world,case["meeting"])
                reconstruction=reconstruct_empty_destination(d,pre,case["meeting"],post)
            if tick==case["end_tick"]:break
            world.advance()
        source_loads=sorted(r["s_reg"] for r in reconstruction.get("sources",[]))
        next_record=channel.observe(world,case["meeting"])
        confirmed=(source_loads==[11,21] and post["active"] and post["s_reg"]==32 and post["direction"]==[0,0,0]
                   and not next_record["active"] and next_record["raw"]==0)
        result={"classification":"DIAGNOSTIC_REPLAY_OF_EXISTING_TRAJECTORY_NOT_ANOTHER_ACQUIRED_CASE",
                "frozen_hypothesis":case,"source_sha256":sha(source),"initial":initial,"final":channel.digest(world),
                "native_ticks_advanced":case["end_tick"]-case["start_tick"],"actual_probes_replayed":replayed,
                "samples":samples,"local_reconstruction":reconstruction,"next_tick_record":next_record,
                "predicted_two_carrier_cancellation_confirmed":confirmed,
                "host_RAW_clock_edits":[],
                "interpretation_boundary":"A confirmed local cancellation/destruction concerns the observed load21 candidate, not proof that all historical information in the entire world is destroyed. An unconfirmed hypothesis remains false/ambiguous; no replacement carrier is installed."}
        put(folder/"MECHANISM.json",result);rows.append(result)
    summary={"windows":rows,"physical_learning_cases_added":0,"new_method_searches":0,
             "scope":"Two explicitly authorized finite retrospective localizations, after the inverse readout failure was already saved"}
    put(output/"SUMMARY.json",summary)
    return summary


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--root",type=Path,default=ROOT);parser.add_argument("--config",type=Path,required=True);parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args();config=json.loads(args.config.read_text(encoding="utf-8"));args.output.mkdir(parents=True,exist_ok=True)
    investigate(args.root.resolve(),config,args.output)


if __name__=="__main__":main()
