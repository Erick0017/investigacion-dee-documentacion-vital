"""Frozen first coverage of inherited continuous access, one worker at a time."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from src.continuidad.common import PARENT,identity,load,put,sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--child");args=parser.parse_args()
    output=ROOT/"resultados/continuidad/M1_TEMPORAL_ACCESS";file=output/"EXPERIMENT_CONFIG.json"
    if args.child:
        config=json.loads(file.read_text(encoding="utf-8"));assert all(sha(ROOT/n)==v for n,v in config["sources"].items())
        assert sha(PARENT/"src/channel.py")==config["inherited_channel_sha256"]
        case=next(c for c in config["cases"] if c["id"]==args.child);path=PARENT/case["parent"]
        assert sha(path)==case["parent_sha256"]
        from src.continuidad.temporal_access import run
        world,spec,neutral=load(path)
        _,result=run(world,spec,case,output/case["id"])
        result.update(case=case,identity=identity(),neutral_protocol=neutral)
        put(output/case["id"]/"MEASUREMENTS.json",result)
        print(json.dumps({"id":case["id"],"forms":result["emitted_forms"]}));return
    if file.exists():config=json.loads(file.read_text(encoding="utf-8"))
    else:
        cases=[]
        for name,parent,bank,report,phase in (("MAIN_PLUS_EVENT","MAIN_MINUS","plus",True,0),("MAIN_MINUS_EVENT","MAIN_MINUS","minus",True,0),
                                             ("REPORT_OMITTED","MAIN_MINUS","plus",False,0),("NO_ACQUIRED_WORD_SIGNALS","LEX_SIGNAL_OMITTED","plus",True,0),
                                             ("PHASE_MISS_PLUS1","MAIN_MINUS","plus",True,1),("OTHER_GEOMETRY_PREVIOUSLY_OBSERVED","RESERVED_TRANSLATION_PLUS","plus",True,0)):
            path=Path("resultados/confirmacion")/parent/"LENGUAJE/OPAQUE_RESTORE_BEFORE_QUERY235.deetsnap"
            cases.append({"id":name,"parent":path.as_posix(),"parent_sha256":sha(PARENT/path),"bank":bank,"report":report,"phase_shift":phase})
        names=("src/continuidad/common.py","src/continuidad/temporal_access.py","src/continuidad/run_temporal.py")
        config={"frozen_utc":datetime.now(timezone.utc).isoformat(),"cases":cases,"sources":{n:sha(ROOT/n) for n in names},
                "inherited_channel_sha256":sha(PARENT/"src/channel.py"),"inputs":[236,264],"readouts":[239,267],
                "criterion":"Physical26vertical+Applied in same MAIN; word region not selected by actual class",
                "geometry_control_not_unseen_fresh_world":True,"new_NSM_meanings_claimed":0,"native_workers":1}
        put(file,config)
        for n in names:
            target=output/"EXECUTED_SOURCE"/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/n,target)
    from src.supervision import run
    rows=[]
    for case in config["cases"]:
        target=output/case["id"]/"MEASUREMENTS.json"
        if not target.exists():
            job=run(ROOT,"continuity_m1_"+case["id"].lower(),[sys.executable,"-I","-B",str(Path(__file__).resolve()),"--child",case["id"]],180)
            if job["exit_code"]!=0:raise RuntimeError("Preserved temporal-access error")
        result=json.loads(target.read_text(encoding="utf-8"));rows.append({"id":case["id"],"forms":result["emitted_forms"],"evidence":target.relative_to(ROOT).as_posix()})
        put(output/"RUN_SUMMARY.json",{"config_sha256":sha(file),"cases":rows,"same_genealogy_no_state_edits":True})


if __name__=="__main__":main()
