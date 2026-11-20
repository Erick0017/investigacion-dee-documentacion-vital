"""Same C6 genealogy, two further cycles, supplied physical reader, no reset.

The expected participation load26+10*j qualifies the physical result only; it
never produces that result or chooses a form. All four input waveforms remain
identical at the two candidate lexical regions.
"""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from src.continuidad.common import FORMS,PARENT,digest,identity,inherited_channel,load,put,resource_sensor,sha,until

KEY="cpc4.ampliacion02.renewed_reader.neutral.v1"


def run_case(world,spec,case,out):
    if world.runtime.current_tick!=267:raise ValueError("Continue the actual first-access267 state")
    channel=inherited_channel();initial=digest(world);rows=[]
    for cycle in (1,2):
        bank=case["banks"][cycle-1];expected=26+10*cycle
        for slot,base in enumerate((236,264)):
            tick=base+67*cycle+case.get("phase_shift",0)
            world.runtime.set_snapshot_metadata(KEY,json.dumps({"version":1,"cycle":cycle,"slot":slot,
                "next_input_tick":tick,"signal_load":5,"report_load":5,"decoder_expected_participation_load":expected},separators=(",",":")))
            until(world,tick)
            sensor=resource_sensor(world,spec,bank);suffix="plus" if sensor["present"] else "minus"
            ids={}
            for form in ("W1","W2"):
                ids[form]=[world.probe("lex."+form+".signal",5,tick).id]
                if case.get("report",True):ids[form].append(world.probe("lex."+form+".outcome."+suffix,5,tick).id)
            until(world,tick+3)
            observations={}
            for form,identities in ids.items():
                r=channel.observe(world,spec["lexical_hubs"][form]);receipts=[channel.receipt(world,x) for x in identities]
                valid=(case.get("report",True) and all(x["status"]=="applied" for x in receipts)
                    and r["active"] and r["semantic"]==1 and r["s_reg"]==expected and r["direction"] in ([0,1,0],[0,-1,0]))
                observations[form]={"physical_output":r,"receipts":receipts,"qualified":bool(valid),
                                    "emitted_form":FORMS[form] if valid else None,
                                    "actual_vertical_candidate":bool(r["active"] and r["direction"] in ([0,1,0],[0,-1,0])),
                                    "expected_participation_load":expected,
                                    "decoder":"Read actual vertical carrier; qualification load26+10*j tracks the acquired16 plus all supplied5+5 probes. No output generation from cycle index."}
            rows.append({"cycle":cycle,"slot":slot,"input_tick":tick,"read_tick":world.runtime.current_tick,
                         "actual_sensor":sensor,"observations":observations})
            world.runtime.set_snapshot_metadata(KEY,json.dumps({"version":1,"cycle":cycle,"slot":slot+1,
                "last_completed_tick":world.runtime.current_tick,"signal_load":5,"report_load":5,
                "decoder_expected_participation_load":expected},separators=(",",":")))
            world.save_snapshot(str(out/("SAME_MAIN_READ"+str(world.runtime.current_tick)+".deetsnap")))
    result={"case":case,"initial":initial,"final":digest(world),"windows":rows,
            "forms_by_cycle":{str(c):[x["emitted_form"] for row in rows if row["cycle"]==c for x in row["observations"].values() if x["qualified"]] for c in (1,2)},
            "modality":"RENEWED_PHYSICAL_READER_PLUS_EXTERNAL_CURRENT_CLASS_TRANSDUCER",
            "same_main_continued":True,"raw_edits":[],"clock_edits":[],"reconstructions":[],"transplants":[],
            "reader_supplied_by_protocol_not_learned_self_regulation":True,
            "new_meanings_claimed":0,"full_NSM_semantics":False}
    put(out/"MEASUREMENTS.json",result)
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--child");args=parser.parse_args()
    out=ROOT/"resultados/continuidad/M1_RENEWED_CYCLES";file=out/"EXPERIMENT_CONFIG.json"
    if args.child:
        config=json.loads(file.read_text());assert all(sha(ROOT/n)==v for n,v in config["sources"].items())
        case=next(c for c in config["cases"] if c["id"]==args.child);path=ROOT/case["parent"]
        assert sha(path)==case["parent_sha256"]
        world,spec,neutral=load(path);destination=out/case["id"];destination.mkdir(parents=True,exist_ok=True)
        result=run_case(world,spec,case,destination);result["identity"]=identity();put(destination/"MEASUREMENTS.json",result)
        print(json.dumps({"id":case["id"],"forms_by_cycle":result["forms_by_cycle"]}));return
    if file.exists():config=json.loads(file.read_text())
    else:
        cases=[]
        for name,parent,banks,report,phase in (("PLUS_STABLE","MAIN_PLUS_EVENT",["plus","plus"],True,0),("MINUS_STABLE","MAIN_MINUS_EVENT",["minus","minus"],True,0),
                ("PLUS_TO_MINUS","MAIN_PLUS_EVENT",["minus","minus"],True,0),("REPORT_OMITTED","MAIN_PLUS_EVENT",["plus","plus"],False,0),
                ("NO_ACQUIRED_WORD_HISTORY","NO_ACQUIRED_WORD_SIGNALS",["plus","plus"],True,0),("PHASE_MISS_PLUS1","MAIN_PLUS_EVENT",["plus","plus"],True,1),
                ("KNOWN_GEOMETRY_NEW_CYCLES","OTHER_GEOMETRY_PREVIOUSLY_OBSERVED",["plus","plus"],True,0)):
            path=Path("resultados/continuidad/M1_TEMPORAL_ACCESS")/parent/"CURRENT_READ267.deetsnap"
            cases.append({"id":name,"parent":path.as_posix(),"parent_sha256":sha(ROOT/path),"banks":banks,"report":report,"phase_shift":phase})
        names=("src/continuidad/common.py","src/continuidad/renewed_access.py")
        config={"frozen_utc":datetime.now(timezone.utc).isoformat(),"sources":{n:sha(ROOT/n) for n in names},"cases":cases,
                "cycles_after_already_executed_first":2,"same_interfaces":"All inherited/preT0; no new channels/matter installed",
                "inputs":[303,331,370,398],"readouts":[306,334,373,401],"decoder":"actual26+10*j vertical carrier, same for both regions",
                "history_control_original_signal_omitted":True,"known_geometry_is_not_new_world_holdout":True,"native_workers":1,
                "inherited_channel_sha256":sha(PARENT/"src/channel.py")}
        put(file,config)
        for n in names:
            target=out/"EXECUTED_SOURCE"/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/n,target)
    from src.supervision import run
    rows=[]
    for case in config["cases"]:
        target=out/case["id"]/"MEASUREMENTS.json"
        if not target.exists():
            job=run(ROOT,"continuity_renew_"+case["id"].lower(),[sys.executable,"-I","-B",str(Path(__file__).resolve()),"--child",case["id"]],180)
            if job["exit_code"]!=0:raise RuntimeError("Preserved renewed-reader error")
        result=json.loads(target.read_text());rows.append({"id":case["id"],"forms_by_cycle":result["forms_by_cycle"],"evidence":target.relative_to(ROOT).as_posix()})
        put(out/"RUN_SUMMARY.json",{"config_sha256":sha(file),"cases":rows,"reader_fixed_and_supplied_not_learned":True})


if __name__=="__main__":main()
