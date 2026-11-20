"""Read-only scientific-data audit; writes one derived scope review, no DEE calls."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def load(path):return json.loads(Path(path).read_text(encoding="utf-8"))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def relative(path):return Path(path).relative_to(ROOT).as_posix()


def artifact(path):
    path=Path(path)
    return {"path":relative(path),"size":path.stat().st_size,"sha256":sha(path)}


def core_row(case):
    folder=ROOT/"resultados/confirmacion"/case["id"]
    path=folder/"MEASUREMENTS.json";m=load(path);uses=m["uses"]
    predictions=[u["anticipation"]["emission"] for u in uses]
    receipts=list(m["teaching"]["actual_receipts"])
    receipts += [r for u in uses for r in u["actual_receipts"]]
    receipts += [u["anticipation"]["receipt"] for u in uses]
    assert len(receipts)==len(set(r["id"] for r in receipts))
    return {"id":case["id"],"type":case["type"],"history_mode":case.get("mode","paired"),
        "classification":"FRESH_PREPARATION_WITH_EXPLICIT_LATE_DIAGNOSTIC_FORKS" if case.get("control") else "FRESH_PREPARATION_NATIVE_MAIN",
        "signal_order":[u["signal"] for u in uses],"observed_teacher_classes":[x["present_sensor"]["observed_class"] for x in m["teaching"]["experiences"]],
        "classes":[x["anticipated_class"] for x in predictions],"directions":[x["physical"]["direction"] for x in predictions],
        "loads":[x["physical"]["s_reg"] for x in predictions],
        "prediction_slots":len(uses),"resolved":sum(x["available"] for x in predictions),
        "correct_against_actual_later_event":sum(u["prediction_correct"] is True for u in uses),
        "incorrect_against_actual_later_event":sum(u["prediction_correct"] is False for u in uses),
        "unresolved":sum(u["prediction_correct"] is None for u in uses),
        "query_admission":[u["anticipation"]["receipt"] for u in uses],
        "emission_ticks":[u["anticipation"]["emission_tick"] for u in uses],
        "later_actual_events":[u["generator_later_event"] for u in uses],
        "physical_function_optional_profiles":[u["evaluation"]["profile"] for u in uses],
        "primary_deliveries":sum(u["evaluation"]["function_delivery"] for u in uses),
        "optional_deliveries":sum(u["evaluation"]["resource_delivery"] for u in uses),
        "external_utility_sum":sum(u["evaluation"]["external_utility_for_this_task"] for u in uses),
        "actual_unique_request_count":len(receipts),"admission_counts":dict(Counter(r["status"] for r in receipts)),
        "diagnostic_forks_after_emission":sum(u["diagnostic"] is not None for u in uses),
        "shared_memory_product_removed_in_action_cut":bool(case.get("control")),
        "configuration":artifact(ROOT/"configuraciones/casos"/(case["id"]+".json")),
        "reserved_parameters":{k:case[k] for k in ("translation","signal_payload","signal_order") if k in case},
        "initial":m["initial"],"final":m["final"],"measurement":artifact(path),
        "final_snapshot":artifact(folder/"MAIN_FINAL.deetsnap"),
        "frozen_source_hashes_equal_case":m["source_hashes"]==CONFIG["source_hashes"],
        "frozen_config_hash_equal_case":m["config_sha256"]==sha(ROOT/"configuraciones/EXPERIMENT_CONFIG.json")}


def repertoire_row(case):
    folder=ROOT/"resultados/repertorio4"/case["id"]
    path=folder/"MEASUREMENTS.json";m=load(path);uses=m["uses"]
    receipts=m["actual_teaching_receipts"]+[r for u in uses for r in u["receipt_after_advance"]]+[u["prediction"]["receipt"] for u in uses]
    assert len(receipts)==len(set(r["id"] for r in receipts))
    return {"id":case["id"],"classification":"FRESH_PREPARATION_NATIVE_MAIN",
        "signal_order":[u["signal"] for u in uses],"observed_teacher_classes":[x["sensor"]["observed_class"] for x in m["teaching"]],
        "classes":[u["prediction"]["anticipated_class"] for u in uses],
        "directions":[u["prediction"]["physical"]["direction"] for u in uses],
        "loads":[u["prediction"]["physical"]["s_reg"] for u in uses],
        "prediction_slots":len(uses),"resolved":sum(u["prediction"]["coverage"] for u in uses),
        "correct_against_actual_later_event":sum(u["prediction_correct"] is True for u in uses),
        "unresolved":sum(u["prediction_correct"] is None for u in uses),
        "query_admission":[u["prediction"]["receipt"]["status"] for u in uses],
        "emission_ticks":[u["prediction"]["emission_tick"] for u in uses],
        "physical_function_optional_profiles":[u["evaluation"]["profile"] for u in uses],
        "primary_deliveries":sum(u["evaluation"]["function_delivery"] for u in uses),
        "optional_deliveries":sum(u["evaluation"]["resource_delivery"] for u in uses),
        "actual_unique_request_count":len(receipts),"admission_counts":dict(Counter(r["status"] for r in receipts)),
        "operational_forks":m["operational_forks"],"external_diagnostic_edits":m["external_diagnostic_edits"],
        "configuration":artifact(folder/"CASE.json"),"translation":case.get("translation",[0,0,0]),
        "initial":m["initial"],"final":m["final"],"measurement":artifact(path),
        "final_snapshot":artifact(folder/"MAIN_FINAL.deetsnap"),
        "executed_runner_sha256":m["runner_sha256"]}


CONFIG=load(ROOT/"configuraciones/EXPERIMENT_CONFIG.json")


def main():
    core=[core_row(case) for case in CONFIG["cases"]]
    config4=load(ROOT/"configuraciones/REPERTOIRE4_CONFIG.json")
    rep=[repertoire_row(case) for case in config4["cases"]]
    assert len(core)==14 and len(rep)==4
    by_id={row["id"]:row for row in core}
    review={"schema":"SEM01.independent_functional_scope_review.v1","generated_utc":datetime.now(timezone.utc).isoformat(),
        "operation":"READ_ONLY_ANALYSIS_OF_PRIMARY_MEASUREMENTS_AND_FILE_HASHES_NO_NATIVE_REEXECUTION",
        "core":{"configuration":artifact(ROOT/"configuraciones/EXPERIMENT_CONFIG.json"),"case_records":14,"fresh_preparations":14,
            "unforked_native_cohorts":10,"cohorts_with_late_diagnostic_forks":4,
            "late_diagnostic_descendant_forks":sum(r["diagnostic_forks_after_emission"] for r in core),
            "prediction_slots_all_strata":sum(r["prediction_slots"] for r in core),
            "unique_requests_across_cohorts":sum(r["actual_unique_request_count"] for r in core),
            "admission_counts_all_strata":dict(sum((Counter(r["admission_counts"]) for r in core),Counter())),
            "frozen_sources_current_bytes_equal":{p:sha(ROOT/p)==h for p,h in CONFIG["source_hashes"].items()},
            "rows":core,"no_pooled_accuracy_claim":"History controls, intentionally reversed future contexts and action-cut prefixes answer different questions; do not pool them into a generic task-accuracy percentage",
            "matched_native_main_ids":["A_future_UV","B_future_VU"],
            "matched_native_main":{"resolved":4,"correct":4,"slots":4,"primary_deliveries":4,"optional_deliveries":2,"utilities":[5,5]},
            "unmatched_future_context_ids":["A_future_VU","B_future_UV"],
            "unmatched_future_context":{"classes_remain_history_dependent":True,"correct":0,"incorrect":4,"slots":4,"utilities":[3,3],"scope":"Future environmental reassignment is made after the same acquired history. The emitted class does not silently read that future target."},
            "unpaired":{"id":"unpaired_UV","query_admission":[r["status"] for r in by_id["unpaired_UV"]["query_admission"]],"resolved":0,"slots":2,"profile":[[0,1],[1,1]],"utility":4},
            "empty":{"id":"empty_UV","query_admission":[r["status"] for r in by_id["empty_UV"]["query_admission"]],"resolved":0,"slots":2,"profile":[[0,1],[1,1]],"utility":4},
            "signals_only_access_limit":{"id":"signals_only_UV","query_admission":[r["status"] for r in by_id["signals_only_UV"]["query_admission"]],"reason":"Old signal returns to its same inlet after67ticks; both new requests are rejected_occupied. This row is not an equal-admission learning or forgetting control."},
            "outcomes_only":{"id":"outcomes_only_UV","query_admission":[r["status"] for r in by_id["outcomes_only_UV"]["query_admission"]],"resolved":0,"slots":2,"scope":"Present historical carriers16,+/-y lack the fixed acquired-query diagonal signature; history can exist without this tested expression."},
            "action_cut_scope":"The measured emission is removed after it forms, preserving clock, in explicit diagnostic descendants. Because the mobile learned product is also removed, this is not a claim of selectively cutting an actuator while leaving that same moving memory untouched.",
            "action_contrasts":{"learned_matched_each_history":{"primary":2,"optional":1,"utility":5},"no_action_each_history":{"primary":1,"optional":2,"utility":4},"always_protect_each_history":{"primary":2,"optional":0,"utility":4},"effect":"U action restores primary delivery while consuming optional resource. V action consumes optional resource without improving already available primary delivery."},
            "reserved_ids":["RESERVED_A_codec7_shift","RESERVED_B_codec7_order_shift"],
            "reserved":{"slots":4,"resolved":4,"correct":4,"emission_loads":25,"utilities":[5,5],"variations":"Translations, payload7 and the B signal orderS2,S1; same direction decoder and action geometry"}},
        "repertoire4":{"configuration":artifact(ROOT/"configuraciones/REPERTOIRE4_CONFIG.json"),"fresh_cohorts":4,"rows":rep,
            "paired_and_reserved_classes_correct":12,"paired_and_reserved_slots":12,"paired_and_reserved_cohorts":3,
            "all_cohort_requests":192,"all_applied":all(r["admission_counts"]=={"applied":48} for r in rep),
            "executed_runner_bytes_equal_current":all(r["executed_runner_sha256"]==sha(ROOT/"src/repertoire4.py") for r in rep),
            "not_independent_replications":"These12readouts are four episodes in each of three coexisting-memory worlds, not12independent replicates, functions or bits",
            "selective_assignment":"A=[U,U,V,V],B=[U,V,U,V]:S1/S4 stay fixed whileS2/S3 change, with twoU/twoV and the same finalV. This is not a global inversion.",
            "resource_scope":"Same N67 but four identity memory regions and eight training/use banks instead of two/four; enlarged-resource arm, not equal-resource efficiency",
            "control":"UnpairedA receives the same32teaching requests Applied; four load16 axial readouts are unresolved, with two primary/four optional deliveries, versus four/two in each paired cohort",
            "restore":artifact(ROOT/"resultados/repertorio4/RESTORE_TECHNICAL.json"),"technical_continuations_not_added_to_fresh_count":1},
        "additional_causal_evidence_not_added_to_18_case_count":{
            "summary":artifact(ROOT/"resultados/causal_memory02/SUMMARY.json"),
            "scope":"Three explicit diagnostic branches and two fresh memory-only reserved preparations, indexed separately from this core14/repertoire4 review",
            "selective_memory_effect":"Removing one actual S1 historical carrier changes S1 to unacquired -x/query and profile[0,1], while S2 retains V/profile[1,1]; a matched actual-carrier sham preserves both tested functions.",
            "direct_action":"After memory cut, a separately requested action one tick later yields profile[1,0], showing native bank/actuator availability in that background, not restoration of the association"},
        "host_scope":{"native":"All state transitions and action encounters are v27 evolution in one Runtime per cohort",
            "external":"Scenario generation, current-function/absence sensor, finite signal presentation, fixed decoding, utility evaluation, explicit diagnostics and textual aliases",
            "prepared_not_acquired":"Toroidal return timing and utility of the action coupling",
            "acquired":"Signal-specific directional consequence response under paired experience; common decoder is unchanged across histories",
            "snapshot_metadata":"Neutral geometry/cursors/alias are distinguished from external teaching map. Runtime receipts retain history for audit; the native dynamics and participant decoder do not query those receipts to choose a response."},
        "technical_closure_review":{"packager":artifact(ROOT/"src/package_append.py"),"verifier":artifact(ROOT/"src/verify_append.py"),
            "confirmed_by_source_reading":["Parent SHA checked before packaging","Duplicate member names rejected","All inherited uncompressed member bytes checked","Inherited compressed local-data prefix checked","Only the new SEM01 prefix may be added","New HASHES and MANIFEST coverage checked with section-relative roots","Temporary ZIP is verified before atomic replacement","Official-name publication requires explicit --publish-atomic","Historical manifests are not overwritten","Exact parent ZIP nesting is rejected"],
            "caller_must_close":["Stop native writers and confirm owned scientific jobs are not RUNNING before sealing; packager itself has no job liveness gate","Check required code/configuration/WHL/docs/checkpoints, since byte-manifest completeness is not scientific/artifact completeness","Reject or separately handle files created after the inventory pass; final hashing only covers files already selected","Write the final external package-verification report outside the included section or document that it is generated after packaging","Keep candidate/extraction staging excluded and re-verify the final published ZIP after closing handles"],
            "metadata_consistency_recommendation":"Verifier checks PARENT_PACKAGE SHA/member count/prefix, but should additionally compare MANIFEST.parent_sha256 and PARENT_MEMBERS.prefix to the same expected identity if strict metadata consistency is promised.",
            "root_resolution":{"actual_parent_prefix":"CPC3/","new_section":"CPC3/experimentos/SEM01_SIGNIFICADO_ADQUIRIDO/","new_hashes_scope":"Paths relative to the new section, not to CPC3 root","clean_proof_prefix":"clean_reproduction.py currently hardcodesCPC3/, which matches this sealed parent; it is not a generic wrapper detector"},
            "public_loader_current_boundary":{"source":artifact(ROOT/"src/app_worker.py"),"checks":artifact(ROOT/"resultados/UI_LOADER_CLOSURE/RESULTS.json"),"checks_count":5,
                "scope":"Explicit metadata/phase/tick/channel validation and rejection of Scheduled future external inputs at public signal-only boundaries. The earlier queue hole remains as diagnostic evidence, not operative behavior."},
            "CLI_notes":["package_append.py requires --parent --section-root --output --parent-sha256; official publication also --publish-atomic","verify_append.py requires --parent (sealed original) --candidate (distinct final) --parent-sha256; use saved parent rather than overwritten official as both arguments","ejecutar.py --run --case reuses a completed case; it is not a fresh reproduction. clean_reproduction.py performs a bounded fresh child from extracted source and opens reference only after evolution.","The demonstrator has its own bounded workers and remains usable after the campaign deadline; the campaign supervisor deliberately does not reset its historical budget."]}}
    assert all(r["frozen_source_hashes_equal_case"] and r["frozen_config_hash_equal_case"] for r in core)
    destination=ROOT/"resultados/REVIEW_SCOPE_FUNCTIONAL.json"
    destination.write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"output":str(destination),"sha256":sha(destination),"core_rows":len(core),"repertoire_rows":len(rep)}))


if __name__=="__main__":main()
