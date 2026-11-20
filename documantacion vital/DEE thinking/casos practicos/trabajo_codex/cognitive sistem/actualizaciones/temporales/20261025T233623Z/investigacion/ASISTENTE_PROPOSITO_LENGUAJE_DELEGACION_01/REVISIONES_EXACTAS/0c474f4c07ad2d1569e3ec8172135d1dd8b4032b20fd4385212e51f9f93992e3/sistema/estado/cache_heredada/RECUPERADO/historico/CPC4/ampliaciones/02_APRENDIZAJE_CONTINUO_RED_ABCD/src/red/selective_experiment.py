"""A NEW common physical reader/bank context, never a rescore of old worlds."""
from datetime import datetime,timezone
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/"src"))
from red import recipe_v3 as r
import supervision

VARIANTS=(("FULL",{}),("D_LATE_CUT",{"diagnostic_control":"D_LATE_REMOVE"}),
          ("A_OPPOSITE_CONTEXT",{"A_history":-1}),("C_OPPOSITE_ALTERNATIVE_B",{"C_history":1}),
          ("SHAM_MESSAGE_DUMMY",{"diagnostic_control":"SHAM_REMOVE"}),
          ("RESERVED_NEW_TRANSLATION",{"translation":[13,27,41]}))


def freeze():
    out=ROOT/"resultados/red/selective_negative01";out.mkdir(parents=True,exist_ok=True)
    target=out/"EXPERIMENT_CONFIG.json"
    if target.exists():return out,json.loads(target.read_text(encoding="utf-8"))
    cases=[]
    for name,extra in VARIANTS:
        c={"id":name,"roles":True,"A_history":1,"B_history":1,"C_history":-1,"D_history":1,"event":"U","translation":[0,0,0],**extra}
        cases.append(c);r.put(out/"casos"/(name+".json"),c)
    names=("recipe_v3.py","selective_session.py","run_selective.py","common_helpers.py","selective_experiment.py")
    config={"frozen_utc":datetime.now(timezone.utc).isoformat(),"case_count_limit":6,"architecture_family":1,
            "type":"NEW_CONTEXT_EXTENSION_NOT_OLD_RESULT_CORRECTION","cases":cases,
            "source_sha256":{name:r.sha(Path(__file__).with_name(name)) for name in names},
            "physical_change":"At T0 add B.query_negative(0,0,-1); later B query414 uses it. The prepared bank action is(-1,+1,-1), resource(1,0,+1), supply+y.",
            "question":"Does a common physical negative-z query reveal a distinction between a D-derived stored B89xy and the alternative retained B37xyz under a correspondingly physical bank?",
            "evaluation_only_prediction":{"D_derived":[94,[-1,1,-1]],"retained_B_alternative":[42,[-1,1,0]]},
            "execution_policy":"Run FULL discovery first. If its measured physical output does not fit the proposed reader/bank path, preserve the boundary and execute no further variants. No alternative search in this extension.",
            "interpretation_boundary":"The reader and bank context are externally requested/prepared. This is not native autonomous selection of attention, a learned optimal routing policy, or a retrospective change to V3 utility criteria."}
    r.put(target,config);frozen=out/"EXECUTED_SOURCE";frozen.mkdir()
    for name in names:(frozen/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    return out,config


def main():
    out,config=freeze();rows=[]
    for case in config["cases"]:
        argv=[str(r.BASE/".venv/Scripts/python.exe"),"-I","-B",str(Path(__file__).with_name("run_selective.py")),
              "--case",str(out/"casos"/(case["id"]+".json")),"--output",str(out/case["id"])]
        row=supervision.run(ROOT,"red_selective_negative_"+case["id"],argv,180,str(ROOT));rows.append(row)
        r.put(out/"EXECUTION_INDEX.json",rows);print(json.dumps(row),flush=True)
        if case["id"]=="FULL":
            path=out/"FULL/MEASUREMENTS.json"
            if row["exit_code"]!=0 or not path.exists():break
            data=json.loads(path.read_text(encoding="utf-8"))
            gate=data["B_future_read"]["active"] and data["B_future_read"]["s_reg"]==94 and data["B_future_read"]["direction"]==[-1,1,-1] and data["task_profile"]==[1,0]
            r.put(out/"DISCOVERY_FOLLOWUP_SELECTION.json",{"measurement":str(path.relative_to(ROOT)),
                "technical_followup_gate":gate,"scope":"External budget allocation after the first physical run, not a response sent to the world and not a global verdict"})
            if not gate:break


if __name__=="__main__":main()
