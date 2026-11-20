"""Exploratory METHOD2: transversal existing outcome ports, new frozen decoder.

This does NOT repair or relabel the original inverse experiment. It is an
explicit diagnostic access protocol, never autonomous symbol production MAIN.
"""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.common import put,sha


def access(parent,spec,mode,out):
    from src import channel
    from src.phase_language import FORMS,current_resource_sensor
    from src.inverse_language import remove_one_retained_word
    initial=channel.digest(parent)
    if mode=="memory_cut":world,edit=remove_one_retained_word(parent,spec)
    elif mode=="full":world,edit=parent.fork(),None
    else:raise ValueError("Frozen METHOD2 mode")
    windows=[]
    for tick,read_tick in ((303,306),(331,334)):
        world.run_until(tick)
        sensor=current_resource_sensor(world,spec,"plus")
        suffix="plus" if sensor["resource_present"] else "minus"
        ids={form:world.probe("lex."+form+".outcome."+suffix,5,tick).id for form in ("W1","W2")}
        world.run_until(read_tick)
        observations={}
        for form,identity in ids.items():
            current=channel.observe(world,spec["lexical_hubs"][form]);receipt=channel.receipt(world,identity)
            valid=(receipt["status"]=="applied" and current["active"] and current["semantic"]==1
                   and current["s_reg"]==26 and current["direction"] in ([0,1,0],[0,-1,0]))
            observations[form]={"physical_output":current,"receipt":receipt,"available":valid,
                                "symbol":FORMS[form] if valid else None,
                                "decoder":"METHOD2 ONLY: admitted physical load26 and direction(0,+/-1,0) at that lexical region; 5/21 are never symbols"}
        windows.append({"external_current_sensor":sensor,"input_tick":tick,"read_tick":read_tick,"observations":observations})
        out.mkdir(parents=True,exist_ok=True);world.save_snapshot(str(out/("METHOD2_WINDOW"+str(read_tick)+".deetsnap")))
    symbols=[item["symbol"] for window in windows for item in window["observations"].values() if item["available"]]
    assert channel.digest(parent)==initial
    return {"windows":windows,"symbols":symbols,"available":len(symbols)==1,"unique_symbol":symbols[0] if len(symbols)==1 else None,
            "diagnostic_edit":edit,"parent_unchanged":True,"final":channel.digest(world),
            "modality":"DIAGNOSTIC_ACCESS_WITH_EXTERNAL_CURRENT_CLASS_SENSOR",
            "full_NSM_semantics":False,"native_main_symbol_emission_claim":False}


def fresh_reserved(out):
    import dee_thinking as d
    from src import channel
    from src.channel_dual import run_native
    from src.phase_language import metadata,teach_slot,query_word
    translation=(11,22,7)
    world,spec=channel.prepare_dual(d,translation,receiver_basis="z")
    world,body=run_native(world,spec,{"A_history":-1,"B_policy":1,"future_context":-1},out/"NATIVE_BODY")
    metadata(world,spec,("W1","W2"),"BEFORE_WORD_EXPERIENCE",0)
    lessons=[]
    for i,(form,bank,tick) in enumerate((("W1","plus",169),("W2","minus",197))):
        lessons.append(teach_slot(world,spec,out/"WORD_EXPERIENCE",form,bank,tick))
        metadata(world,spec,("W1","W2"),"EXPERIENCE_RETAINED",i+1)
    world.save_snapshot(str(out/"RESERVED_MAIN_BEFORE_ASSISTED_RESCUE200.deetsnap"))
    current=channel.observe(world,spec["lexical_hubs"]["W1"])
    if not(current["active"] and current["s_reg"]==11 and current["direction"]==[1,-1,0]):
        raise ValueError("Frozen fresh reserve lacks the actual teacher candidate; no retuning")
    original=channel.digest(world)
    child,edit=channel.diagnostic_record_edit(world,spec["lexical_hubs"]["W1"],"RESERVED_METHOD2_ENVIRONMENTAL_TEACHER11_REMOVAL",raw=0,expected_load=11)
    queries=[]
    for i,(form,tick) in enumerate((("W1",236),("W2",264))):
        queries.append(query_word(child,spec,form,tick))
        metadata(child,spec,("W1","W2"),"WORD_QUERY_RETAINED",i+1)
    metadata(child,spec,("W1","W2"),"FINITE_FORWARD_COMPLETE",2)
    assert channel.digest(world)==original
    child.save_snapshot(str(out/"RESERVED_DIAGNOSTIC_PARENT267.deetsnap"))
    return child,spec,{"native_body_final":body["final"],"lessons":lessons,"queries":queries,"environmental_edit":edit,
                       "original_main200_preserved":True,"same_world0_to200":True,"fork_after200_not_merged":True}


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path,required=True);parser.add_argument("--child");args=parser.parse_args()
    out=args.output.resolve();file=out/"INVERSE_ACCESS2_CONFIG.json"
    if args.child:
        config=json.loads(file.read_text(encoding="utf-8"));assert all(sha(ROOT/n)==v for n,v in config["sources"].items())
        import dee_thinking as d
        from src import channel
        assert d.__version__=="4.0.0" and d.kernel_identity()["kernel_version"]==27 and sha(d._native.__file__)==channel.NATIVE_SHA256
        case=next(c for c in config["cases"] if c["id"]==args.child);destination=out/case["id"];destination.mkdir(parents=True,exist_ok=True)
        if case.get("fresh"):
            parent,spec,provenance=fresh_reserved(destination)
        else:
            path=ROOT/case["parent"];assert sha(path)==case["parent_sha256"]
            parent=d.OrganizationalWorld.load_snapshot(str(path));spec=channel.describe_dual();provenance={"restored_same_operational_genealogy":True}
        assert parent.runtime.current_tick==267
        result=access(parent,spec,case["mode"],destination)
        result.update(case=case,preparation_provenance=provenance)
        put(destination/"MEASUREMENTS.json",result)
        print(json.dumps({"id":case["id"],"symbols":result["symbols"],"available":result["available"]}))
        return
    if file.exists():config=json.loads(file.read_text(encoding="utf-8"))
    else:
        cases=[]
        for name,path,mode in (("ORIGINAL_MAIN_NO_RESCUE","resultados/confirmacion/MAIN_MINUS/LENGUAJE/MAIN_FINAL267.deetsnap","full"),
                               ("ASSISTED_RESCUE_W1","resultados/inverse_rescue01/RESCUE_ORPHAN11/DIAGNOSTIC_FORWARD267.deetsnap","full"),
                               ("ASSISTED_RESCUE_THEN_MEMORY_CUT","resultados/inverse_rescue01/RESCUE_ORPHAN11/DIAGNOSTIC_FORWARD267.deetsnap","memory_cut")):
            cases.append({"id":name,"parent":path,"parent_sha256":sha(ROOT/path),"mode":mode})
        cases.append({"id":"FRESH_RESERVED_TRANSLATION","fresh":True,"translation":[11,22,7],"A_history":-1,"B_policy":1,"word_order":["W1","W2"],"mode":"full",
                      "scope":"New independent world0→200 then the same declared diagnostic environmental rescue; not native unassisted MAIN symbol emission"})
        names=("src/channel.py","src/channel_dual.py","src/common.py","src/phase_language.py","src/inverse_language.py","src/inverse_access2.py")
        config={"frozen_utc":datetime.now(timezone.utc).isoformat(),"sources":{n:sha(ROOT/n) for n in names},"cases":cases,
                "method":"EXPLORATORY_ACCESS_METHOD2_NOT_REPAIR_OR_RELABEL_OF_METHOD1",
                "input":"Existing preT0 outcome ports probed with load5,(+1,actualsign,0), identical both lexical regions",
                "new_frozen_decoder":"ONLY load26, direction(0,+/-1,0), applied receipt; region identifies its fixed text form",
                "sensor":"External CURRENT resource plus window, no class-to-word map","inputs":[303,331],"readouts":[306,334],
                "native_workers":1,"timeout_seconds_each":180,"native_main_symbol_emission_claim":False,"full_NSM_semantics":False}
        put(file,config)
        for name in names:
            target=out/"EXECUTED_SOURCE"/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
    from supervise import run
    rows=[]
    for case in config["cases"]:
        target=out/case["id"]/"MEASUREMENTS.json"
        if not target.exists():
            job=run(ROOT,"inverse_access2_"+case["id"].lower(),[sys.executable,"-I","-B",str(Path(__file__).resolve()),"--output",str(out),"--child",case["id"]],180)
            if job["exit_code"]!=0:raise RuntimeError("Preserved METHOD2 failure; no automatic retuning")
        result=json.loads(target.read_text(encoding="utf-8"))
        rows.append({"id":case["id"],"symbols":result["symbols"],"available":result["available"],"parent_unchanged":result["parent_unchanged"],
                     "evidence":target.relative_to(ROOT).as_posix(),"modality":result["modality"]})
        put(out/"RESULTS.json",{"config_sha256":sha(file),"cases":rows,"native_main_symbols":0,"full_NSM_semantics":False})


if __name__=="__main__":main()
