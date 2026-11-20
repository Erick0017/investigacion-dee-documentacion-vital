"""Small evidence index from saved data only; no Runtime import or evolution."""
from collections import Counter
from datetime import datetime,timezone
import json
from pathlib import Path
from .protocol import sha,put

ROOT=Path(__file__).resolve().parents[2];PARENT=ROOT.parents[1]


def load(path):return json.loads(Path(path).read_text(encoding="utf-8"))


def receipts(value,out=None):
    """Keep one copy of an ID within this trajectory, never across branches."""
    out={} if out is None else out
    if isinstance(value,dict):
        if "id" in value and "status" in value and ("requested_tick" in value or "kind" in value):out[value["id"]]=value
        for item in value.values():receipts(item,out)
    elif isinstance(value,list):
        for item in value:receipts(item,out)
    return out


def case_row(family,case,path,kind):
    data=load(path);rr=receipts(data)
    windows=[]
    for window in data.get("windows",[]):
        actuals=window["observations"]
        windows.append({"input_tick":window["input_tick"],"actual_read_tick":window["read_tick"],
                        "qualified_forms":[x["emitted_form"] for x in actuals.values() if x["emitted_form"]],
                        "actual_region_fields":{key:{"load":value["physical_output"]["s_reg"],"direction":value["physical_output"]["direction"]}
                                                for key,value in actuals.items()}})
    for response in data.get("readouts",[]):
        if "readout" in response:
            actual=response["readout"]["physical"]
            windows.append({"form_id":response["form"],"actual_read_tick":actual["tick"],
                            "qualified":response["readout"]["valid"],"actual_load":actual["s_reg"],
                            "actual_direction":actual["direction"],"decoded_sign":response["readout"]["class_sign"]})
        elif "physical" in response:
            actual=response["physical"]
            windows.append({"form_id":response["form"],"actual_read_tick":actual["tick"],
                            "qualified":response["valid"],"actual_load":actual["s_reg"],
                            "actual_direction":actual["direction"],"decoded_sign":response["class_sign"]})
        else:
            windows.append({"actual_read_tick":response["tick"],"current_sensor_profile":response["sensor"]["profile"],
                            "qualified_forms":response.get("locally_emitted_forms",response.get("emitted_forms",[])),
                            "actual_region_fields":{key:{"load":value["s_reg"],"direction":value["direction"]}
                                                    for key,value in response["actual"].items()}})
    evidence=path.relative_to(ROOT).as_posix()
    return {"id":case["id"],"case_uid":family+"/"+case["id"],"family":family,"type":kind,"phase": "DISCOVERY" if family=="discovery01" else "FROZEN_CONTROLLED_PANEL",
            "actual_boundaries":{"initial":data["initial"]["tick"],"final":data["final"]["tick"],"windows":windows},
            "recorded_receipts":{"count_unique_in_recorded_windows":len(rr),"status_counts":dict(Counter(x["status"] for x in rr.values())),
                                 "ids":sorted(rr),"scope":"Counts only the receipts present in this measurement JSON; complete operative history remains in checkpoints."},
            "evidence":{"path":evidence,"sha256":sha(path)},
            "case_config":case,"new_native_individual":bool(case.get("fresh",False)),
            "raw_clock_assisted_edits_in_this_scientific_trajectory":False,
            "independent_ticks_not_claimed":True,
            "checkpoints":{"directory":path.parent.relative_to(ROOT).as_posix(),"names":[x.name for x in sorted(path.parent.glob("*.deetsnap"))]}}


def run():
    rows=[];configs=[]
    for prefix,family in (("continuidad","M1_TEMPORAL_ACCESS"),("continuidad","M1_RENEWED_CYCLES"),
                          ("lenguaje","discovery01"),("lenguaje","continuous02"),("lenguaje","direction03")):
        folder=ROOT/"resultados"/prefix/family;configfile=folder/"EXPERIMENT_CONFIG.json";config=load(configfile)
        configs.append({"family":family,"path":configfile.relative_to(ROOT).as_posix(),"sha256":sha(configfile)})
        for case in config["cases"]:
            kind="NEW_PREPARATION_WITH_CONTINUITY" if case.get("fresh") else "CONTINUATION_FROM_IDENTIFIED_CHECKPOINT"
            rows.append(case_row(family,case,folder/case["id"]/"MEASUREMENTS.json",kind))
    technical=[]
    folder=ROOT/"resultados/lenguaje/TECHNICAL_CHECKS"
    for name,kind in (("FIRST_PROCESS.json","TECHNICAL_REPLAY_AND_NEW_FUTURE"),("SECOND_PROCESS.json","TECHNICAL_RESTORE_AND_NEW_QUESTION"),
                      ("GUARDS.json","TECHNICAL_DIAGNOSTIC_STATE_BRANCHES")):
        path=folder/name;data=load(path)
        technical.append({"id":name[:-5],"type":kind,"path":path.relative_to(ROOT).as_posix(),"sha256":sha(path),
                          "checks":data["checks"],"scientific_samples_added":0})
    for name,relative,kind in (("LOADER_HARDENING","resultados/lenguaje/LOADER_HARDENING/RESULTS.json","TECHNICAL_DIAGNOSTIC_METADATA_AND_QUEUE"),
                               ("UI_PASSIVE_REVIEW","resultados/lenguaje/UI_REVIEW.json","PASSIVE_OBSERVATION_NO_ADVANCE")):
        path=ROOT/relative;data=load(path)
        technical.append({"id":name,"type":kind,"path":relative,"sha256":sha(path),
                          "checks":data.get("checks",data.get("proofs")),"scientific_samples_added":0})
    original=PARENT/"NSM65_CATALOGO.json";evolved=ROOT/"resultados/lenguaje/NSM65_EVOLUCION.json";table=load(evolved)
    source_files={}
    for folder in (ROOT/"src/continuidad",ROOT/"src/lenguaje"):
        for file in sorted(folder.glob("*.py")):source_files[file.relative_to(ROOT).as_posix()]=sha(file)
    public_files={n:sha(ROOT/n) for n in ("demostracion.py","src/interactive_worker.py","ejecutar.py","iniciar_cpc4.ps1")}
    index={"schema":"CPC4.AMPLIACION02.language_final_evidence_index.v1","generated_utc":datetime.now(timezone.utc).isoformat(),
           "counts":{"physical_trajectories":len(rows),"continuity":13,"language":19,
                     "new_preparations_inside_the_language_cohort":2,"technical_processes":4,"passive_review_jobs":1,
                     "technical_assertions":20,"tick_frames_not_counted_as_replicas":True},
           "configurations":configs,"cases":rows,"technical_and_passive_proofs":technical,
           "four_new_forms":{"BUENO":{"port":"L1","domain":"Actual F7present/R3absent or its taught inversion"},
                             "MALO":{"port":"L2","domain":"Actual F7absent/R3present or its taught inversion"},
                             "ARRIBA":{"port":"L3","domain":"Positive current dz in a declared lattice frame, or its taught inversion"},
                             "DEBAJO":{"port":"L4","domain":"Negative current dz in a declared lattice frame, or its taught inversion"}},
           "retention":{"inherited_matched_access_loads":[26,36,46],"fixed_supplied_reader_not_learned_self_regulation":True,
                        "new_form_preprobe_retention_ticks":64,"new_form_acquisition_to_readout_ticks":67,
                        "after_new_direction_content_old_profile_panel":{"ticks":[1568,1596],"qualified26":[False,False]},
                        "simultaneous_four_or_six_available_meanings_claimed":False,
                        "no_qualified_old_signature_does_not_prove_complete_state_erasure":True},
           "NSM65_matrix":{"original_path_relative_to_parent":"NSM65_CATALOGO.json","original_sha256":sha(original),
                           "new_path":evolved.relative_to(ROOT).as_posix(),"new_sha256":sha(evolved),"rows":len(table["entries"]),
                           "independent_dimensions":table["status_dimensions_independent"],"counts_separated":table["counts_separated"],
                           "primary_sources_inherited_not_rewritten":True,
                           "rows_compact":[{"id":x["id"],"forma_es":x["forma_es"],"full_NSM_semantics":False,
                                            "dimensions":{key:value["estado"] for key,value in x["dimensiones_independientes"].items()}}
                                           for x in table["entries"]]},
           "sources_current":source_files,"public_sources_reviewed":public_files,
           "scope":"All primary measurements remain separate. The index supplies locations, identities and actual boundaries; it is not a response table and is never read by the participant/decoder."}
    assert len(rows)==32 and len(table["entries"])==65
    put(ROOT/"resultados/lenguaje/FINAL_EVIDENCE_INDEX.json",index)
    return index


if __name__=="__main__":run()
