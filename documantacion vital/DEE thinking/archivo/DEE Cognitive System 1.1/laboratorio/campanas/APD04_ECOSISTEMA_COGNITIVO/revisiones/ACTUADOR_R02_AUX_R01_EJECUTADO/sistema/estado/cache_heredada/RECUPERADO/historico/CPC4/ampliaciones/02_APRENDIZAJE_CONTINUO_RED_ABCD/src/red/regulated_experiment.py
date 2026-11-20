"""Finite frozen response to a confirmed residual-carrier mechanism, not search."""
from datetime import datetime,timezone
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/"src"))
from red import recipe_v3 as r
import supervision

CASES=(("FILTER_FLAT",{"C_history":1}),
       ("NO_FILTER_FLAT",{"C_history":1,"neutralizer":"none"}),
       ("SHAM_ZERO_FLAT",{"C_history":1,"neutralizer":"sham"}),
       ("FILTER_N",{}),
       ("FILTER_BENIGN_C_MINUS",{"A_history":-1}),
       ("FILTER_BENIGN_C_PLUS",{"A_history":-1,"C_history":1}),
       ("RESERVED_FILTER_FLAT",{"C_history":1,"translation":[37,9,53]}))


def main():
    folder=ROOT/"resultados/red/fixed_counterflow01";folder.mkdir(parents=True,exist_ok=False)
    names=("recipe_v3.py","common_helpers.py","dual_session.py","dual_habitat.py","residual_diagnostic.py","regulated_session.py","regulated_habitat.py","regulated_experiment.py")
    cases=[]
    for name,delta in CASES:
        case={"id":name,"roles":True,"A_history":1,"B_history":1,"C_history":-1,"D_history":1,"neutralizer":"counterflow","translation":[0,0,0],**delta}
        cases.append(case);r.put(folder/"casos"/(name+".json"),case)
    prior=ROOT/"resultados/red/residual425_diagnostic01/MEASUREMENTS.json"
    config={"frozen_utc":datetime.now(timezone.utc).isoformat(),"source_sha256":{n:r.sha(Path(__file__).with_name(n)) for n in names},
       "source_mechanism":str(prior.relative_to(ROOT)),"source_mechanism_sha256":r.sha(prior),"cases":cases,
       "hypothesis":"A zero+Z carrier from R-5Z at290 meets unused5-Z atR-2Z293. The sum5dir0 has no neighbors and disappears294. If D already consumed the useful relay, zero continues alone and should not change D-to-B89xy.",
       "modality":"Fixed physical regulation with experience protocol, not learned regulation or a diagnostic MAIN deletion",
       "selection":"Run FILTER_FLAT once. If Native outputs or admissions do not support its intended profile, stop and preserve. No geometry/timing/decoder search. Otherwise run6 frozen contrasts/reserve exactly once.",
       "evaluation_only":{"FILTER_FLAT":5,"NO_FILTER_FLAT":4,"SHAM_ZERO_FLAT":4,"FILTER_N":5,"FILTER_BENIGN_C_MINUS":6,"FILTER_BENIGN_C_PLUS":6,"RESERVED_FILTER_FLAT":5},
       "controls":"Both physical interfaces are preT0 in every condition. None omits only the counterflow packet; sham supplies load0 with same direction/time on a declared displaced route. The sham is measured, not presumed irrelevant.",
       "resource_bound":"Seven fresh finite preparations at most; one one-site diagnostic was already preserved separately. No fourth alternative or parameter search."}
    r.put(folder/"EXPERIMENT_CONFIG.json",config);capsule=folder/"EXECUTED_SOURCE";capsule.mkdir()
    for name in names:(capsule/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    py=str(r.BASE/".venv/Scripts/python.exe");worker=str(Path(__file__).with_name("regulated_habitat.py"));jobs=[]
    for case in cases:
        job=supervision.run(ROOT,"red_fixed_counterflow_"+case["id"],[py,"-I","-B",worker,"--case",str(folder/"casos"/(case["id"]+".json")),"--output",str(folder/case["id"])],180,str(ROOT))
        jobs.append(job);r.put(folder/"EXECUTION_INDEX.json",jobs);print(json.dumps(job),flush=True)
        if case["id"]=="FILTER_FLAT":
            path=folder/case["id"]/"MEASUREMENTS.json"
            measured=json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
            select=bool(job["exit_code"]==0 and measured and measured["external_utility"]==5 and all(x["status"]=="applied" for x in measured["receipts"]))
            r.put(folder/"FOLLOWUP_SELECTION.json",{"continue_frozen_set":select,"scope":"External bounded experimental allocation only; no score enters an organization."})
            if not select:break


if __name__=="__main__":main()
