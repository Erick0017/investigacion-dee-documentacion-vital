"""Mechanism-derived environmental rescue in explicit forks, never MAIN repair."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.common import put,sha


def child(config,case,out):
    import dee_thinking as d
    from src import channel
    from src.phase_language import KEY, metadata, query_word
    from src.inverse_language import inverse
    parent_path=ROOT/case["parent"]
    assert sha(parent_path)==case["parent_sha256"]
    source=d.OrganizationalWorld.load_snapshot(str(parent_path))
    assert source.runtime.current_tick==200
    spec=channel.describe_dual()
    source_before=channel.digest(source)
    neutral=json.loads(source.runtime.snapshot_metadata(KEY))
    assert neutral["word_order"]==["W1","W2"]
    edit=None
    if case["cut"]=="orphan_teacher":
        site=spec["lexical_hubs"]["W1"]
        actual=channel.observe(source,site)
        if not(actual["active"] and actual["semantic"]==1 and actual["s_reg"]==11
               and actual["direction"][0]==1 and abs(actual["direction"][1])==1 and actual["direction"][2]==0):
            raise ValueError("Actual orphan teacher11 not present at declared200 environmental site; no rescue fabricated")
        world,edit=channel.diagnostic_record_edit(source,site,"ENVIRONMENTAL_ORPHAN_BROADCAST_TEACHER_REMOVAL_200",raw=0,expected_load=11)
    elif case["cut"]=="sham":
        site=channel.moved(spec["sham_source"],(1,0,0),200)
        actual=channel.observe(source,site)
        if actual["direction"]!=[1,0,0]:raise ValueError("Actual sham missing")
        world,edit=channel.diagnostic_record_edit(source,site,"ENVIRONMENTAL_RESCUE_SHAM_DUMMY13_REMOVAL_200",raw=0,expected_load=13)
    elif case["cut"]=="none":world=source
    else:raise ValueError("Unknown frozen environmental intervention")
    out.mkdir(parents=True,exist_ok=True)
    world.save_snapshot(str(out/"DIAGNOSTIC_PRE_QUERY200.deetsnap"))
    world.run_until(235)
    metadata(world,spec,("W1","W2"),"BEFORE_WORD_QUERY",0)
    queries=[]
    for index,(form,tick) in enumerate((("W1",236),("W2",264))):
        metadata(world,spec,("W1","W2"),"QUERYING",index)
        queries.append(query_word(world,spec,form,tick))
        metadata(world,spec,("W1","W2"),"WORD_QUERY_RETAINED",index+1)
    metadata(world,spec,("W1","W2"),"FINITE_FORWARD_COMPLETE",2)
    at267=channel.digest(world)
    world.save_snapshot(str(out/"DIAGNOSTIC_FORWARD267.deetsnap"))
    replay_equal=None
    if case["id"]=="REFERENCE_UNCUT":
        original=d.OrganizationalWorld.load_snapshot(str(ROOT/"resultados/confirmacion/MAIN_MINUS/LENGUAJE/MAIN_FINAL267.deetsnap"))
        replay_equal=channel.digest(original)==at267
        assert replay_equal
    try:
        final,backward=inverse(world,spec,{"bank":"plus","mode":"memory_cut" if case.get("memory_cut267") else "full"},out/"INVERSE")
        final_digest=channel.digest(final)
    except ValueError as error:
        backward={"status":"INTERVENTION_NOT_APPLICABLE","reason":str(error),"emitted_symbols":[],"available":None}
        final_digest=None
    preserved=(channel.digest(source)==source_before) if edit else None
    if edit:assert preserved
    result={"case":case,"modality":"DIAGNOSTIC_ENVIRONMENTAL_RESCUE_NOT_NATIVE_MAIN",
            "source200":source_before,"original_source_preserved":preserved,"environmental_edit":edit,
            "forward_queries":queries,"forward267":at267,"reference_replay_equal":replay_equal,
            "inverse":backward,"final334":final_digest,"native_main_symbol_emissions_claimed":0,
            "full_NSM_semantics":False,
            "scope":"Conditional environmental sufficiency after removing actual unpaired teacher11, with original geometry, clocks, word signals and decoder. Not autonomous repair, not main bidirectionality, not universal semantics."}
    put(out/"MEASUREMENTS.json",result)
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path,required=True);parser.add_argument("--child");args=parser.parse_args()
    out=args.output.resolve();file=out/"RESCUE_CONFIG.json"
    if args.child:
        config=json.loads(file.read_text(encoding="utf-8"))
        assert all(sha(ROOT/name)==value for name,value in config["sources"].items())
        case=next(x for x in config["cases"] if x["id"]==args.child)
        result=child(config,case,out/case["id"])
        print(json.dumps({"id":case["id"],"symbols":result["inverse"]["emitted_symbols"],"available":result["inverse"]["available"]}))
        return
    if file.exists():config=json.loads(file.read_text(encoding="utf-8"))
    else:
        paths={name:ROOT/"resultados/confirmacion"/name/"LENGUAJE/AFTER_W2_EXPERIENCE.deetsnap" for name in ("MAIN_MINUS","FULL_PLUS")}
        cases=[]
        for name,parent,cut,memory in (("REFERENCE_UNCUT","MAIN_MINUS","none",False),("SHAM_DUMMY13","MAIN_MINUS","sham",False),
                                      ("RESCUE_ORPHAN11","MAIN_MINUS","orphan_teacher",False),("OPPOSITE_HISTORY_RESCUE","FULL_PLUS","orphan_teacher",False),
                                      ("RESCUE_THEN_W1_MEMORY_CUT","MAIN_MINUS","orphan_teacher",True)):
            cases.append({"id":name,"parent":paths[parent].relative_to(ROOT).as_posix(),"parent_sha256":sha(paths[parent]),"cut":cut,"memory_cut267":memory})
        names=("src/channel.py","src/common.py","src/phase_language.py","src/inverse_language.py","src/rescue_inverse.py")
        config={"frozen_utc":datetime.now(timezone.utc).isoformat(),"sources":{n:sha(ROOT/n) for n in names},"cases":cases,
                "reason":"Followup after direct observation of W1+orphan-teacher collision253; original inverse negative is preserved",
                "physical_intervention":"T200 remove only actual orphan teacher11 atW1hub OR sham13; RAW one site, clocks none, acquired W1memory16 elsewhere preserved",
                "queries_unchanged":[236,264],"inverse_inputs_unchanged":[303,331],"inverse_readouts_unchanged":[306,334],
                "opposite_history_previously_observed_not_new_holdout":True,"full_NSM_semantics":False,"native_workers":1}
        put(file,config)
        for name in names:
            target=out/"EXECUTED_SOURCE"/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
    from supervise import run
    rows=[]
    for case in config["cases"]:
        target=out/case["id"]/"MEASUREMENTS.json"
        if not target.exists():
            job=run(ROOT,"inverse_rescue_"+case["id"].lower(),[sys.executable,"-I","-B",str(Path(__file__).resolve()),"--output",str(out),"--child",case["id"]],180)
            if job["exit_code"]!=0:raise RuntimeError("Preserved finite rescue error")
        result=json.loads(target.read_text(encoding="utf-8"))
        rows.append({"id":case["id"],"symbols":result["inverse"]["emitted_symbols"],"available":result["inverse"]["available"],
                     "forward_classes":[x["resource_class"] for x in result["forward_queries"]],
                     "reference_replay_equal":result["reference_replay_equal"],"modality":result["modality"],"evidence":target.relative_to(ROOT).as_posix()})
        put(out/"RESULTS.json",{"config_sha256":sha(file),"cases":rows,"native_main_symbol_emissions_claimed":0})


if __name__=="__main__":main()
