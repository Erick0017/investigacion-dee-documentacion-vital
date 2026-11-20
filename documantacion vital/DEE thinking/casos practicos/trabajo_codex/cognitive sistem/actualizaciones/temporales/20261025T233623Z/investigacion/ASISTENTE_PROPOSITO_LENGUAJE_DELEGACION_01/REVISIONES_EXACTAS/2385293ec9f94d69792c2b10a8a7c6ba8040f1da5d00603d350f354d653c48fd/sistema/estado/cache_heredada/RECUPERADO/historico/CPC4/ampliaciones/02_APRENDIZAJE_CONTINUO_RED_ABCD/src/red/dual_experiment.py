"""Last bounded habitat extension: calibrate once, then eight frozen networks."""
from datetime import datetime,timezone
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/"src"))
from red import recipe_v3 as r
import supervision

VARIANTS=(("A_PLUS_C_MINUS_N",{}),("A_PLUS_C_PLUS_FLAT",{"C_history":1}),
          ("A_MINUS_C_MINUS_BENIGN",{"A_history":-1}),
          ("A_MINUS_C_PLUS_BENIGN",{"A_history":-1,"C_history":1}),
          ("D_LATE_CUT_N",{"diagnostic_control":"D_LATE_REMOVE"}),
          ("D_UNPAIRED_FLAT",{"C_history":1,"D_unpaired":True}),
          ("RESERVED_N",{"translation":[23,31,47]}),
          ("RESERVED_FLAT",{"C_history":1,"translation":[19,43,7]}))


def freeze():
    out=ROOT/"resultados/red/dual_habitat01";out.mkdir(parents=True,exist_ok=True);path=out/"EXPERIMENT_CONFIG.json"
    if path.exists():return out,json.loads(path.read_text(encoding="utf-8"))
    cases=[]
    for name,change in VARIANTS:
        case={"id":name,"roles":True,"A_history":1,"B_history":1,"C_history":-1,"D_history":1,"translation":[0,0,0],**change}
        cases.append(case);r.put(out/"casos"/(name+".json"),case)
    names=("recipe_v3.py","dual_session.py","dual_habitat.py","common_helpers.py","dual_experiment.py")
    config={"frozen_utc":datetime.now(timezone.utc).isoformat(),"architecture_family":1,
            "extension_of_observed_alternative_path":2,"last_refinement_of_this_family":True,
            "new_task_not_rescore":"The old single-bank V3/selective contexts and their metrics remain unchanged.",
            "source_sha256":{name:r.sha(Path(__file__).with_name(name)) for name in names},
            "cases":cases,"calibration":{"contexts":[[-1,-1],[-1,1],[1,-1],[1,1]],
                 "fixed_policies":["None","N","Flat","Both"],"parent":"Empty Research preparation advanced to416, not an erased organism"},
            "environment_law":"x=A external current property. If x=-1, both events benignV. If x=+1, c=-1 threatens N withU and c=+1 threatens Flat withU; the other bank getsV. No response is read to choose events.",
            "inventory":"Every context supplies one load3 resource, one load7 supply and one load11 U/V event per bank. The reference policy inputs are explicit external actuator calibration, not learned organization outputs.",
            "score":"External 2*(F_N+F_Flat)+R_N+R_Flat, never fed back into the network",
            "followup":"If calibration predictions or admissions differ, preserve the result and stop without another geometry search. Otherwise execute the eight frozen contexts once.",
            "scope":"Prepared dual routes and a requested negative-z reader with acquired histories. No learned attention selection or learned general utility optimization is claimed."}
    r.put(path,config);frozen=out/"EXECUTED_SOURCE";frozen.mkdir()
    for name in names:(frozen/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    return out,config


def main():
    out,config=freeze();worker=str(Path(__file__).with_name("dual_habitat.py"));py=str(r.BASE/".venv/Scripts/python.exe")
    calibration=supervision.run(ROOT,"red_dual_habitat_calibration",[py,"-I","-B",worker,"--calibration","--output",str(out/"CALIBRATION")],180,str(ROOT))
    r.put(out/"CALIBRATION_JOB.json",calibration)
    selection=out/"CALIBRATION/FOLLOWUP_SELECTION.json"
    if calibration["exit_code"]!=0 or not selection.exists() or not json.loads(selection.read_text(encoding="utf-8"))["continue_network"]:
        r.put(out/"CLOSURE.json",{"status":"CALIBRATION_BOUNDARY_PRESERVED_NO_NEW_SEARCH","job":calibration});return
    rows=[]
    for case in config["cases"]:
        argv=[py,"-I","-B",worker,"--case",str(out/"casos"/(case["id"]+".json")),"--output",str(out/case["id"])]
        row=supervision.run(ROOT,"red_dual_"+case["id"],argv,180,str(ROOT));rows.append(row)
        r.put(out/"EXECUTION_INDEX.json",rows);print(json.dumps(row),flush=True)
        if case["id"]=="A_PLUS_C_MINUS_N" and row["exit_code"]!=0:
            r.put(out/"CLOSURE.json",{"status":"FULL_NETWORK_TECHNICAL_BOUNDARY_NO_REDESIGN","job":row});break


if __name__=="__main__":main()
