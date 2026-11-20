"""Passive analysis of completed C2CAL_R02 primary JSON and journal only."""
from pathlib import Path
import hashlib,json

if __name__=="__main__":
    p=Path(__file__).resolve().parent.parent
    journal=p/"estados/candidato_R02/sistema/estado/servicios_locales/ECI02_PI03_REPRO_PI04_C2CAL_01/PI04_C2_COORDINACION_R01/eventos.jsonl"
    intents={}
    if journal.is_file():
        for line in journal.read_text(encoding="utf8").splitlines():
            row=json.loads(line)
            if row.get("kind")=="C2_CALIBRATION_INTENT":intents[row["value"]]=row
    results=[];ids=set()
    for value in (0,1,4,44,47,50):
        file=p/"ensayos"/("PI04_C2CAL_R02_Q_%d.json"%value)
        root=json.loads(file.read_text(encoding="utf8"));native=json.loads(root["result"])
        row=native["result"]["rows"][0]
        requests=row["requests"]
        for req in requests:ids.add(req["id"])
        before=intents.get(value,{}).get("before",{}).get("fields",{})
        after=row["after"]["fields"]
        results.append({"value":value,"primary":str(file),"primary_sha256":hashlib.sha256(file.read_bytes()).hexdigest(),
            "before_tick":row["before_tick"],"after_tick":row["after_tick"],"reader_tick":row["reader"]["tick"],
            "choice":row["reader"]["choice"],"candidates":row["reader"]["candidates"],
            "active_outputs":[o for o in row["reader"]["observations"]if o["physical"]["state"]>0],
            "bank_before":{k:before.get(k)for k in("A","B")},"bank_after":{k:after[k]for k in("A","B")},
            "datum_after_settling":after["datum"],"requests":requests,
            "all_applied":all(r["receipt"]["status"]=="applied"for r in requests),
            "feedback_inserted":row["feedback_inserted"],"efference_inserted":row["efference_inserted"]})
    report={"schema":"PI04.C2CAL_R02.passive_read.R01","records":results,
        "new_Native_executed_by_this_analysis":0,"unique_native_ids_in_six_primaries":len(ids),
        "actual_choices":[r["choice"]for r in results],
        "all_inputs_applied":all(r["all_applied"]for r in results),
        "observed":"All six documented scalar values have the same +1 x-class in this exact Q0 calibration. Inputs were admitted; that alone does not establish a useful scalar threshold. Active output s_reg and direction are recorded rather than inferred.",
        "limits":"Only q+6 and settled fields plus optional before-journal were recorded. No intermediate q+3 datum/Q encounter is recovered here. Do not claim absence of encounter or global incapacity. The query carrier has payload0 whereas the documented MU.current sensory protocol uses5; R03 is a new controlled apparatus revision, not a reinterpretation of these results."}
    target=p/"control/C2CAL_R02_ANALISIS_PASIVO_R01.json"
    if target.exists():raise ValueError("Preserve previous analysis")
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"report":str(target),"choices":report["actual_choices"],"unique_inputs":len(ids),
        "active_outputs":[[{"direction":o["physical"]["direction"],"s_reg":o["physical"]["s_reg"]}for o in r["active_outputs"]]for r in results],
        "bank_before":[[r["bank_before"][k]["s_reg"]if r["bank_before"][k]else None for k in("A","B")]for r in results],
        "Native_ticks_in_analysis":0},ensure_ascii=False,indent=2))
