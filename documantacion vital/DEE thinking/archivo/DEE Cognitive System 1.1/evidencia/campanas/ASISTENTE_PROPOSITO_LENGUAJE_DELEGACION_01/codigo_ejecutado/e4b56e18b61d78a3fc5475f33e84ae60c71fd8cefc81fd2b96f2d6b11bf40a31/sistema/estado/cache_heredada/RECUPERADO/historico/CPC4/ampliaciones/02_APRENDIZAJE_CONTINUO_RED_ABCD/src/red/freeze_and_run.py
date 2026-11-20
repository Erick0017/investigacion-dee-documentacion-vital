"""Finite configuration freeze and supervised two-worker ABCD02 battery."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/"src"))
from red import recipe as r
import supervision

CASE_VARIANTS=(
    ("FULL_U",{}),("FULL_V",{"event":"V"}),
    ("A_MINUS_U",{"A_history":-1}),("C_MINUS_U",{"C_history":-1}),
    ("B_WRONG_U",{"B_history":-1}),("D_NAIVE_U",{"D_naive":True}),
    ("D_NAIVE_V",{"D_naive":True,"event":"V"}),("D_WRONG_U",{"D_history":1}),
    ("C_UNPAIRED_U",{"C_unpaired":True}),("D_UNPAIRED_U",{"D_unpaired":True}),
    ("D_SOURCE_LATE_CUT",{"diagnostic_control":"D_LATE_REMOVE"}),
    ("D_SOURCE_DZ_ZERO",{"diagnostic_control":"D_DZ_ZERO"}),
    ("SHAM_DUMMY_REMOVE",{"diagnostic_control":"SHAM_REMOVE"}),
    ("PREPARED_ROLE_RELAY_OMITTED",{"omit_role_relay":True}),
    ("RESERVED_TRANSLATION_1",{"translation":[7,11,5]}),
    ("RESERVED_TRANSLATION_2",{"translation":[31,19,23]}),
)


def freeze():
    output=ROOT/"resultados/red/confirmacion02";output.mkdir(parents=True,exist_ok=True)
    config_path=output/"EXPERIMENT_CONFIG.json"
    if config_path.exists():return json.loads(config_path.read_text(encoding="utf-8"))
    cases=[]
    for name,change in CASE_VARIANTS:
        case={"id":name,"roles":True,"A_history":1,"B_history":1,"C_history":1,"D_history":-1,"event":"U","translation":[0,0,0],**change}
        cases.append(case);r.put(output/"casos"/(name+".json"),case)
    names=("recipe.py","session.py","run_roles.py","freeze_and_run.py")
    sources={name:r.sha(Path(__file__).with_name(name)) for name in names}
    frozen=output/"EXECUTED_SOURCE";frozen.mkdir()
    for name in names:(frozen/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    config={"frozen_utc":datetime.now(timezone.utc).isoformat(),"architecture_family":1,
            "phase":"Finite confirmation after two explicitly preserved discovery realizations",
            "cases":cases,"source_sha256":sources,"max_native_workers":2,"native_threads_each":1,
            "timeout_per_trajectory":180,"end_tick":431,"reserved_ids":["RESERVED_TRANSLATION_1","RESERVED_TRANSLATION_2"],
            "observations_frozen":{"A_emission":70,"B_contact":82,"C_emission":80,"joint":86,"D_social":94,
                                   "D_reads":[161,228],"D_to_B_turn":291,"B_social":350,"B_read":417,"bank":[424,431]},
            "evaluation_only_not_implemented_response":{"native_full":{"D_reads":[79,84],"B_social":89,"B_read":94},
                                                       "utility":"External score2*F+R, never supplied to Runtime"},
            "scope":"Prepared topology with acquired component relations. C-minus has a physically distinct off-route product, not a same-destination negative message. D role reversal uses a prepared native turner, not a learned routing rule."}
    r.put(config_path,config);return config


def main():
    p=argparse.ArgumentParser();p.add_argument("--freeze-only",action="store_true");p.add_argument("--workers",type=int,choices=(1,2),default=2)
    a=p.parse_args();config=freeze()
    if a.freeze_only:print(json.dumps({"frozen":True,"cases":len(config["cases"])}));return
    output=ROOT/"resultados/red/confirmacion02"
    def launch(case):
        target=output/case["id"]
        if (target/"MEASUREMENTS.json").exists():return {"id":case["id"],"status":"PREVIOUSLY_MEASURED_NOT_REPEATED"}
        command=[str(r.BASE/".venv/Scripts/python.exe"),"-I","-B",str(Path(__file__).with_name("run_roles.py")),
                 "--case",str(output/"casos"/(case["id"]+".json")),"--output",str(target)]
        return {"id":case["id"],"job":supervision.run(ROOT,"red_confirm_"+case["id"],command,180,str(ROOT))}
    rows=[]
    with ThreadPoolExecutor(max_workers=a.workers) as executor:
        for future in as_completed([executor.submit(launch,c) for c in config["cases"]]):
            row=future.result();rows.append(row);r.put(output/"EXECUTION_INDEX.json",rows);print(json.dumps(row),flush=True)


if __name__=="__main__":main()
