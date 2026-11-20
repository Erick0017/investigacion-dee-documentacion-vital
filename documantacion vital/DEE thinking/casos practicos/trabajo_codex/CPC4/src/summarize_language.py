"""Evidence index only; no Native execution, no operational response lookup."""
from datetime import datetime,timezone
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.common import put,sha


def read(path):return json.loads((ROOT/path).read_text(encoding="utf-8"))


def main():
    catalogue=read("NSM65_CATALOGO.json")
    names=("MAIN_MINUS","FULL_PLUS","LEX_NAMES_SWAPPED","LEX_SIGNAL_OMITTED","LEX_UNPAIRED","LEX_REPORT_OMITTED","LEX_MEMORY_CUT","LEX_SHAM","RESERVED_TRANSLATION_PLUS","RESERVED_TRANSLATION_MINUS_SWAPPED")
    tables={}
    for name in names:
        path="resultados/confirmacion/"+name+"/MEASUREMENTS.json"
        row=read(path)["language"]
        tables[name]={"path":path,"sha256":sha(ROOT/path),"responses":[{"form":q["form_id"],"available":q["available"],"class":q["resource_class"],"receipt":q["receipt"]["status"],"physical":q["physical_output"]} for q in row["queries"]]}
    principal=read("resultados/confirmacion/MAIN_MINUS/MEASUREMENTS.json")["language"]
    durations=[]
    for lesson,query in zip(principal["lessons"],principal["queries"]):
        acquired=lesson["post_current"][lesson["form_id"]]["tick"]
        durations.append({"form":lesson["form_id"],"acquired_tick":acquired,"probe_tick":query["input_tick"],"read_tick":query["emission_tick"],"ticks_before_probe":query["input_tick"]-acquired,"ticks_to_readout":query["emission_tick"]-acquired})
    m1=read("resultados/inverse01/RESULTS_COMPLETED.json")
    rescue=read("resultados/inverse_rescue01/RESULTS.json")
    m2=read("resultados/inverse_access2/RESULTS.json")
    assert len(m1["cases"])==5 and len(m2["cases"])==4
    direct_symbols=m2["cases"][0]["symbols"]
    assert direct_symbols==[]
    files=("demostracion.py","src/app_worker.py","src/language.py","src/demo_validation.py","src/phase_language.py","src/inverse_language.py","src/inverse_access2.py","src/channel.py","src/channel_dual.py","src/observers.py","NSM65_CATALOGO.json")
    result={"schema":"CPC4.LANGUAGE_EVIDENCE_INDEX.v1","generated_utc":datetime.now(timezone.utc).isoformat(),
            "not_a_runtime_decoder":True,"no_new_native_jobs":True,
            "independent_counts":{"documentary_inventory_forms":65,"limited_trained_forms":2,"other_forms_documentary_only":63,
                                  "native_main_situation_to_symbol_forms":0,"diagnostic_rescued_situation_to_symbol_forms":1,
                                  "NSM_semantic_composition_demonstrated":0,"general_NSM_meanings_claimed":0},
            "documentary_provenance":{"catalogue":"NSM65_CATALOGO.json","sha256":sha(ROOT/"NSM65_CATALOGO.json"),"version":catalogue["catalogue_version"],
                                      "full_NSM_semantics":False,"class_scope":"External fixed current-resource3 presence/absence window, not universal there-is or negation"},
            "retention_and_expression":durations,"word_to_class_cases":tables,
            "inverse_original":{"planned":len(m1["cases"]),"measured_future_trajectories":sum(c["status"]=="MEASURED" for c in m1["cases"]),
                                 "local_cuts_not_applicable":sum(c["status"]=="INTERVENTION_NOT_APPLICABLE" for c in m1["cases"]),
                                 "symbols":0,"evidence":"resultados/inverse01/RESULTS_COMPLETED.json",
                                 "scope":"Original failed controller guard preserved; measured FULL trajectories not rerun during instrumental completion"},
            "environmental_rescue_method1":{"cases":rescue["cases"],"symbols":0,"scope":"Removing actual orphan teacher11 preserves W1output21 but collinear input303 is rejected occupied; 21 is not relabelled a symbol"},
            "diagnostic_access_method2":{"cases":m2["cases"],"evidence":"resultados/inverse_access2/RESULTS.json",
                                         "fresh_world_count":1,"native_main_symbol_emission":False,
                                         "scope":"New preregistered transversal access on existing outcome ports. Only26vertical identifies a symbol; HAY observed after environmental rescue and in a fresh reserved world with the same rescue; memory cut abolishes it."},
            "public_interface":{"main_witness":"resultados/demo02/DEMONSTRATION_SUMMARY.json",
                                 "new_question_after_explicit_load":read("resultados/demo02/DEMONSTRATION_SUMMARY.json")["new_question_after_explicit_restore"],
                                 "diagnostic_witness":"resultados/DEMO_DIAGNOSTIC/RESULTS.json","diagnostic_checks":read("resultados/DEMO_DIAGNOSTIC/RESULTS.json")["count"],
                                 "contracts":"resultados/DEMO_CONTRACTS/RESULTS.json","contract_checks":read("resultados/DEMO_CONTRACTS/RESULTS.json")["count"],
                                 "pause_and_observers":"resultados/DEMO_PAUSE_AND_OBSERVERS/RESULTS.json","pause_observer_checks":read("resultados/DEMO_PAUSE_AND_OBSERVERS/RESULTS.json")["count"],
                                 "separate_attributions":["ENTE","INSTRUMENTO","INTERFAZ","GENERADOR_EXTERNO","EXPLICACION_DOCUMENTAL"],
                                 "finite_domain":"Two word experiences, two consuming word queries; optional explicit diagnostic copies at172 never rejoin MAIN; no unlimited conversation or hidden resets",
                                 "technical_reproductions_are_not_independent_scientific_samples":True,
                                 "preserved_first_error":"resultados/demo01; Windows pipe encoding CP1252/UTF8 mismatch before acquisition, corrected explicitly"},
            "limitations":["The two forms are a directional relation family, not arbitrary lexical meanings.","Swapped names/ordering leave second HAY inaccessible despite Applied admission; no repair after seeing reservations.","Report omission blocks later probes by occupation and is not a valid forgetting measurement.","Original inverse gives no symbol; conditional access2 requires diagnostic environmental rescue and an external actual-class sensor.","O4 graph quantities are not persistent homology, certified genealogy or causal necessity.","No full_NSM_semantics, general negation or existential syntax demonstrated."],
            "source_sha256":{name:sha(ROOT/name) for name in files},"scientific_extension_closed":True}
    put(ROOT/"resultados/LANGUAGE_SUMMARY.json",result)
    print(json.dumps({"counts":result["independent_counts"],"summary_sha256":sha(ROOT/"resultados/LANGUAGE_SUMMARY.json")}))


if __name__=="__main__":main()
