"""Close the measured CPC4 cut, preserving the single original budget."""
import ctypes
from datetime import datetime,timezone
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.common import put,sha,WHEEL_SHA,NATIVE_SHA,PARENT_SHA,KERNEL_SHA


def main():
    clean=json.loads((ROOT/"resultados"/"CLEAN_REPRODUCTION.json").read_text(encoding="utf-8"))
    assert clean["completed"] is True
    extracted=Path(clean["extracted_package"])
    keys=["ejecutar.py","demostracion.py","supervise.py","src/common.py","src/channel.py","src/channel_dual.py",
          "src/phase_language.py","src/language.py","src/app_worker.py","src/observers.py","src/inverse_language.py",
          "src/inverse_access2.py","src/demo_validation.py","NSM65_CATALOGO.json","EXPERIMENT_CONFIG.json"]
    equivalence=[]
    for name in keys:
        assert sha(ROOT/name)==sha(extracted/name),(name,"implementation changed after clean execution")
        equivalence.append({"path":name,"sha256":sha(ROOT/name),"same_as_executed_clean_candidate":True})
    preserved={"CPC3":ROOT.parents[1]/"CPC3_ENTE_COGNITIVO_CAUSAL_DEE_3_5_0_RESULTADOS.zip",
               "original_WHL4":ROOT.parents[2]/"4.0"/"dee_thinking-4.0.0-cp313-cp313-win_amd64.whl",
               "original_product4":ROOT.parents[2]/"4.0"/"DEE_thinking_4_0_0_ENTREGA_FINAL_RESULTADOS.zip"}
    expected={"CPC3":PARENT_SHA,"original_WHL4":WHEEL_SHA,
              "original_product4":"c78609a7d0d501324324408ed955f60f127965c77efbcbe3b3d04fc14dbb16cf"}
    identities={name:{"path":str(p),"sha256":sha(p),"unchanged":sha(p)==expected[name]} for name,p in preserved.items()}
    assert all(x["unchanged"] for x in identities.values())
    budget=json.loads((ROOT/"BUDGET.json").read_text(encoding="utf-8"))
    ctypes.windll.kernel32.GetTickCount64.restype=ctypes.c_uint64
    elapsed=(int(ctypes.windll.kernel32.GetTickCount64())-budget["monotonic_start_ms"])/1000
    assert elapsed<budget["budget_seconds"]-300
    value={"campaign":"CPC4","state":"MEASURED_CUT_READY_FOR_ATOMIC_PUBLICATION_WITH_SCOPED_PARTIALS",
           "source_implementation_same_as_clean_execution":equivalence,"preserved_originals":identities,
           "instrument":{"version":"4.0.0","kernel":27,"wheel_sha256":WHEEL_SHA,"native_sha256":NATIVE_SHA,"kernel_source_sha256":KERNEL_SHA},
           "coverage":{"frozen_cases":33,"fresh_native_worlds_within_frozen_cases":27,"language_shared_parent_cohorts":6,
                       "observer_prospective_new_worlds":2,"observer_field_predictions_exact":34,
                       "historical_SEM01_snapshots_reanalyzed":6,"CPC4_observer_rereads":11,
                       "inverse_method1_planned":5,"inverse_method1_measured":3,"inverse_method1_nonapplicable_cuts":2,
                       "environmental_rescue_cohorts":5,"inverse_access2_cases":4,"fresh_worlds_in_access2":1,
                       "native_main_situation_to_symbol_forms":0,"diagnostically_rescued_forms":1},
           "counts_note":"Nested traces, replays, snapshots, fields and shared-parent cohorts are not counted as additional independent acquired histories",
           "remaining":{"joint_convention_update":"NOT_TESTED","unassisted_bidirectional_translation":"NO_SYMBOL_IN_THE_TESTED_MAIN",
                        "NSM_general_semantics":"65 documentary entries,2limited acquired forms,0general meanings claimed",
                        "persistent_homology":"NOT_EXECUTED_NETWORK_PERMISSION"},
           "clean_validation":"resultados/CLEAN_REPRODUCTION.json","elapsed_before_packaging_seconds":elapsed,
           "deadline_utc":budget["deadline_utc"],"closed_utc":datetime.now(timezone.utc).isoformat(),
           "publication_note":"Final package adds reproduction proofs/closure documents only. Experimental implementation, wheel, configuration and participant readouts match the executed clean candidate."}
    put(ROOT/"RUN_SUMMARY.json",value)
    put(ROOT/"CLOSED.json",{"status":"SCIENCE_AND_CLEAN_REPRODUCTION_CLOSED","utc":value["closed_utc"],"elapsed_before_packaging_seconds":elapsed})
    print(json.dumps({"closed":True,"elapsed_seconds":elapsed,"immutable_implementation_files":len(equivalence),"originals_unchanged":True}))


if __name__=="__main__":main()
