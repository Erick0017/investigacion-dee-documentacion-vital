"""Frozen narrow confirmation of V3 D social path, with new translation reserves."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/"src"))
from red import recipe_v3 as r
import supervision

VARIANTS=(("FULL_U",{}),("D_UNPAIRED_U",{"D_unpaired":True}),
          ("D_SOURCE_LATE_CUT",{"diagnostic_control":"D_LATE_REMOVE"}),
          ("C_OPPOSITE_ALTERNATIVE_PATH",{"C_history":1}),
          ("SHAM_DUMMY_REMOVE",{"diagnostic_control":"SHAM_REMOVE"}),
          ("RESERVED_FRESH_TRANSLATION_A",{"translation":[5,17,29]}),
          ("RESERVED_FRESH_TRANSLATION_B",{"translation":[43,3,11]}))


def freeze():
    folder=ROOT/"resultados/red/confirmacion03";folder.mkdir(parents=True,exist_ok=True)
    target=folder/"EXPERIMENT_CONFIG.json"
    if target.exists():return json.loads(target.read_text(encoding="utf-8"))
    cases=[]
    for name,extra in VARIANTS:
        case={"id":name,"roles":True,"A_history":1,"B_history":1,"C_history":-1,"D_history":1,"event":"U","translation":[0,0,0],**extra}
        r.put(folder/"casos"/(name+".json"),case);cases.append(case)
    names=("recipe_v3.py","session_v3.py","run_roles_v3.py","common_helpers.py","curriculum_v3.py","confirm_v3.py")
    config={"frozen_utc":datetime.now(timezone.utc).isoformat(),"architecture_family":1,"version":3,
            "cases":cases,"source_sha256":{name:r.sha(Path(__file__).with_name(name)) for name in names},
            "reserves_not_used_in_V2":[[5,17,29],[43,3,11]],"native_threads":1,"max_workers":2,
            "scope":"D social path and selective common two-probe panel. The original bank also accepts an alternative retained B path when C does not join; this measured alternative is preserved, not scored away.",
            "fixed_panel":{"D_first":{"tick":158,"direction":[1,0,0]},"D_second":{"tick":225,"direction":[-1,0,0]}},
            "counterfactual_boundary":"Late cuts/shams are complete diagnostic child worlds, never merged back into operational MAIN."}
    r.put(target,config);frozen=folder/"EXECUTED_SOURCE";frozen.mkdir()
    for name in names:(frozen/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    return config


def main():
    p=argparse.ArgumentParser();p.add_argument("--freeze-only",action="store_true");p.add_argument("--workers",type=int,choices=(1,2),default=1);a=p.parse_args()
    config=freeze();folder=ROOT/"resultados/red/confirmacion03"
    if a.freeze_only:print(json.dumps({"frozen":True,"cases":len(config["cases"])}));return
    def launch(case):
        target=folder/case["id"]
        if (target/"MEASUREMENTS.json").exists():return {"id":case["id"],"status":"PREVIOUSLY_MEASURED_NOT_REPEATED"}
        argv=[str(r.BASE/".venv/Scripts/python.exe"),"-I","-B",str(Path(__file__).with_name("run_roles_v3.py")),"--case",str(folder/"casos"/(case["id"]+".json")),"--output",str(target)]
        return {"id":case["id"],"job":supervision.run(ROOT,"red_v3_confirm_"+case["id"],argv,180,str(ROOT))}
    rows=[]
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        for future in as_completed([pool.submit(launch,c) for c in config["cases"]]):
            row=future.result();rows.append(row);r.put(folder/"EXECUTION_INDEX.json",rows);print(json.dumps(row),flush=True)


if __name__=="__main__":main()
