"""Summaries preserve values, modalities and adverse cases; no cognitive verdict."""
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.common import put,sha


def summarize():
    config=json.loads((ROOT/"EXPERIMENT_CONFIG.json").read_text(encoding="utf-8"))
    rows=[];messages=[];words=[]
    for case in config["cases"]:
        path=ROOT/"resultados"/"confirmacion"/case["id"]/"MEASUREMENTS.json"
        if not path.exists():
            rows.append({"id":case["id"],"status":"NO_MEASUREMENT_FILE","expected_kind":case["kind"]})
            continue
        x=json.loads(path.read_text(encoding="utf-8"));p=x.get("physical",{});lex=x.get("language",{})
        row={"id":case["id"],"kind":case["kind"],"reserved":case.get("reserved",False),
             "status":"MEASURED","evidence":path.relative_to(ROOT).as_posix(),"sha256":sha(path),
             "elapsed_seconds":x["elapsed_seconds"],"operation_journal":x["operation_journal"]}
        if p:
            receipts=p["receipts"]
            row.update(native_tick=p["final"]["tick"],delivery_panel={k:v["profile"] for k,v in p["evaluations"].items()},
                       external_utility=p["external_utility"],primary_sum=p["primary_sum"],optional_sum=p["optional_sum"],
                       A_emission=p["A_emission"],B_contacts=p["B_contacts"],B_responses=p["B_common_responses"],
                       input_calls=len(receipts),applied=sum(r["status"]=="applied" for r in receipts),
                       diagnostic_edits=p["diagnostic_edits"],scope=p["scope"])
            messages.append({"case":case["id"],"modality":"DIAGNOSTIC_FORK" if p["diagnostic_edits"] else "EXPERIENCE_PROTOCOL_PLUS_NATIVE_CHANNEL",
                             "A_emission":p["A_emission"],"after_explicit_intervention":p["A_current_after_intervention"],
                             "B_contacts":p["B_contacts"],"B_later_queries":p["B_common_responses"],
                             "consequences":p["evaluations"],"evidence":row["evidence"]})
        if lex:
            row["language"]={"scope":lex["scope"],"full_NSM_semantics":False,"start":lex["initial"],"end":lex["final"],
                             "queries":[{"form":q["text_form"],"resource_class":q["resource_class"],"physical":q["physical_output"],
                                         "receipt":q["receipt"],"available":q["available"],"matched_own_past_sensor":q["evaluation_only_matches_own_past_sensor"]} for q in lex["queries"]]}
            for q in lex["queries"]:
                words.append({"case":case["id"],"attribution":q["attribution"],"form":q["text_form"],
                              "input_tick":q["input_tick"],"emission_tick":q["emission_tick"],"physical_output":q["physical_output"],
                              "resource_class":q["resource_class"],"available":q["available"],"receipt":q["receipt"],"evidence":row["evidence"]})
        rows.append(row)
    value={"campaign":"CPC4","instrument":"DEE thinking4.0.0 / kernel27 frozen",
           "case_count":len(rows),"completed_measurement_files":sum(x["status"]=="MEASURED" for x in rows),
           "native_cases":sum(x["kind"]=="native" for x in config["cases"]),
           "language_cohorts_from_shared_native169":sum(x["kind"]=="language_control" for x in config["cases"]),
           "independence_note":"Deterministic replays, local windows and shared-parent language forks are not independent learned histories. Calibration and discovery are identified separately.",
           "case_rows":rows,"config_sha256":sha(ROOT/"EXPERIMENT_CONFIG.json")}
    put(ROOT/"resultados"/"CONFIRMATORY_SUMMARY.json",value)
    for name,records in (("MENSAJES.jsonl",messages),("DIALOGOS.jsonl",words)):
        (ROOT/name).write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in records),encoding="utf-8")
    # Prospective emissions are already stored before the world delivery event;
    # this file is an index, not extra predictions or independent evidence.
    predictions=[{"case":r["case"],"attribution":"ENTE", "type":"PRECONSEQUENCE_ACTION_EMISSION_NOT_A_FORMAL_FORECAST", "emissions":r["B_later_queries"],
                  "task":"Known physical direction of the current native product determines its later bank encounter; external evaluator scores delivery after this emission", "evidence":r["evidence"]} for r in messages]
    prospective=ROOT/"configuraciones"/"OBSERVER_RESERVED_CONFIG.json"
    if prospective.exists():
        frozen=json.loads(prospective.read_text(encoding="utf-8"))
        predictions += [{"case":r["id"],"attribution":"INSTRUMENTO","type":"PROSPECTIVE_FROZEN_OBSERVER_PREDICTION_NOT_PARTICIPANT_POLICY",
                         "prediction":r,"frozen_configuration_sha256":sha(prospective),"evidence":"configuraciones/OBSERVER_RESERVED_CONFIG.json"} for r in frozen["cases"]]
    (ROOT/"PREDICCIONES.jsonl").write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in predictions),encoding="utf-8")
    print(json.dumps({k:value[k] for k in ("case_count","completed_measurement_files","native_cases","language_cohorts_from_shared_native169")}))
    return value


if __name__=="__main__":summarize()
