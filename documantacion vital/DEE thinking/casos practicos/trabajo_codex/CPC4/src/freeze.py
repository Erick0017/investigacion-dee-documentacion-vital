"""Freeze the finite CPC4 confirmatory cut before any reserved world is run."""
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.common import put,sha,WHEEL_SHA,NATIVE_SHA,KERNEL_SHA,PARENT_SHA


def freeze():
    destination=ROOT/"EXPERIMENT_CONFIG.json"
    if destination.exists(): raise FileExistsError("Do not overwrite a frozen configuration")
    cases=[]
    def native(identifier,sign=-1,**parameters):
        cases.append({"id":identifier,"kind":"native","A_history":sign,"B_policy":1,
                      "receiver_basis":"z","snapshot_policy":"none",**parameters})
    native("MAIN_MINUS",language={"mode":"full","word_order":["W1","W2"]},snapshot_policy="central")
    native("FULL_PLUS",1,language={"mode":"full","word_order":["W1","W2"]},snapshot_policy="central")
    for sign,name in ((-1,"MINUS"),(1,"PLUS")):
        native("CUT_"+name,sign,cut=True,snapshot_policy="central")
    native("B_NAIVE",receiver_untrained=True)
    native("B_WRONG_RELATION",B_policy=-1)
    native("B_UNPAIRED",receiver_unpaired=True)
    native("B_TEACHER_ONLY",receiver_teacher_only=True)
    native("A_UNPAIRED",A_unpaired=True)
    native("A_NAIVE",A_untrained=True)
    native("A_QUERY_OMITTED",no_A_query=True)
    native("MESSAGE_CONSTANT_PLUS",message_control="force_plus")
    native("MESSAGE_OFF_DIRECTION",message_control="z_miss")
    native("B_ROUTE_COMPONENT_REMOVED",receiver_flatten=True)
    native("B_ACQUIRED_COMPONENT_REMOVED",receiver_z_remove=True)
    native("SHAM_DUMMY_REMOVAL",sham_remove=True)
    native("CUT_WITH_ACTUATOR_REFERENCE",cut=True,direct_actuator=True)
    for sign,name in ((-1,"MINUS"),(1,"PLUS")):
        for policy in ("none","plus","minus","both"):
            native("WORLD_"+name+"_FIXED_"+policy.upper(),sign,
                   A_untrained=True,receiver_untrained=True,no_A_query=True,
                   instrument_action=policy,role="INSTRUMENTAL_HABITAT_CALIBRATION_NOT_ACQUIRED_POLICY")
    native("RESERVED_TRANSLATION_PLUS",1,translation=[7,5,9],
           reserved=True,language={"mode":"full","word_order":["W1","W2"]})
    native("RESERVED_TRANSLATION_MINUS_SWAPPED",-1,translation=[13,11,3],
           reserved=True,language={"mode":"full","word_order":["W2","W1"]})
    parent="resultados/confirmacion/MAIN_MINUS/LENGUAJE/MAIN_BEFORE_GROUNDING169.deetsnap"
    for mode in ("signal_omitted","report_omitted","unpaired","memory_cut","sham"):
        cases.append({"id":"LEX_"+mode.upper(),"kind":"language_control","parent":parent,
                      "language":{"mode":mode,"word_order":["W1","W2"]},
                      "role":"DIAGNOSTIC_COHORT_FROM_IDENTICAL_NATIVE169_NOT_NEW_INDEPENDENT_HISTORY"})
    cases.append({"id":"LEX_NAMES_SWAPPED","kind":"language_control","parent":parent,
                  "language":{"mode":"full","word_order":["W2","W1"]}})
    sources=["ejecutar.py","src/common.py","src/channel.py","src/channel_dual.py","src/phase_language.py","src/freeze.py"]
    value={"campaign":"CPC4 COMUNICACION NATIVA Y META ROSETTA",
           "author":"Ivan Erick Tlaltecatl Morales","frozen_utc":datetime.now(timezone.utc).isoformat(),
           "instrument":{"version":"4.0.0","kernel":27,"wheel_sha256":WHEEL_SHA,"native_sha256":NATIVE_SHA,"kernel_source_sha256":KERNEL_SHA},
           "historical_CPC3_sha256":PARENT_SHA,"budget_record":"BUDGET.json",
           "architecture_family":"M1 finite mobile relations; R2 orthogonal receiver z memory separates learned resource-use component from native message xy route",
           "discovery_correction":"R1 y-memory/z-probe permitted a naive receiver to act directly. Its measured counterexample is preserved; confirmatory R2 probes add y, not the acquired z component.",
           "runtime":{"dimension":67,"topology":"periodic torus","backend":"LAZY","native_threads":1,"workers":2},
           "native_boundaries":{"T0":0,"A_acquired":3,"B_acquired":[15,21],"A_emission":70,"contacts":[82,88],"B_common_query_emissions":[149,155],"native_end":169},
           "language_boundaries":{"teaching":[169,197],"common_signal_queries":[236,264],"emissions":[239,267],"minimum_retention_ticks":67},
           "native_function_metric":{"panel":["primary_summand_S7_available_in_each_bank","optional_resource_R3_available_in_each_bank"],
                                     "external_utility":"2*sum(primary)+sum(optional)",
                                     "scope":"Two fixed resource contexts requiring opposite physical routes; metric reads actual current resource/function packets, not a chosen shield coordinate. Cost is loss of optional R3.",
                                     "no_reward_to_participant":True},
           "observers":{"O1":"finite published sites and receipts","O2":"integer unpacked fields and Moore26",
                        "O3":"declared segments with actual pre/post observations; stop certification at unreconstructed transformations",
                        "O4":"periodic connectivity/geometry, refined by direction and time; optional PH only if actually available",
                        "raw_uint64_as_float_distance":False},
           "language":{"forms":["HAY","NO"],"fixed_ports":["W1","W2"],"signals_load":5,"teacher_load":11,
                       "sensor":"fixed external current resource-packet presence/absence window; same report broadcast to both lexical regions",
                       "decoder":"physical load21 and (-1,+/-1,0), same for every form/history; no word->answer map",
                       "full_NSM_semantics":False},
           "followup_priority_rule":"A causal effect, one reserved realization, at most two deeper extensions; bidirectional retrieval is a separately frozen finite extension, never retroactively a forward criterion",
           "timeout_per_case_seconds":240,"cases":cases,"source_sha256":{x:sha(ROOT/x) for x in sources}}
    put(destination,value)
    print("Frozen",len(cases),"cases;",sha(destination))
    return value


if __name__=="__main__":freeze()
