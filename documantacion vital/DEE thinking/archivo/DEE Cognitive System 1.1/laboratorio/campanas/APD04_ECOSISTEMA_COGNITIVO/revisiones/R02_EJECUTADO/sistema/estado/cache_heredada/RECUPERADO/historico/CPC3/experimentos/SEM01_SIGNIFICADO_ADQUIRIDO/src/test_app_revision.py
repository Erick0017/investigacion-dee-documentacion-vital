"""Finite application adapter qualification, not a new scientific branch."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common import digest, put, sha
from src.app_worker import APP_KEY, PROTOCOL_KEY


def completed(folder, operation):
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(folder.glob("llamada_*/RESULT.json"))
            if json.loads(path.read_text(encoding="utf-8")).get("operation") == operation
            and json.loads(path.read_text(encoding="utf-8")).get("completed")]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    import dee_thinking as d
    spec = importlib.util.spec_from_file_location("finite_revision_app_test", ROOT / "demostracion.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    observed = ROOT / "resultados/demostracion_revision"
    reference = ROOT / "resultados/reversal02_phase/FULL_REVERSE"
    oracle = json.loads((reference / "MEASUREMENTS.json").read_text(encoding="utf-8"))
    revision = completed(observed, "revise")[0]
    queries = completed(observed, "query")
    consequences = completed(observed, "reveal")
    checks = {}
    parent129 = ROOT / "resultados/demostracion_A/MAIN_FINAL.deetsnap"
    checks["same_used_parent129_hash"] = revision["loaded_snapshot_sha256"] == sha(parent129)
    checks["parent129_physical_matches_reversal_reference"] = revision["revision"]["before"] == oracle["initial"]
    boundary = d.OrganizationalWorld.load_snapshot(str(observed / "REVISION284.deetsnap"))
    ref_boundary = d.OrganizationalWorld.load_snapshot(str(reference / "BEFORE_SIGNAL_S1.deetsnap"))
    checks["trained284_raw_clocks_equal_reference"] = digest(boundary) == digest(ref_boundary)
    checks["present_sensor_sequence_not_requested_teacher_label"] = [r["present_sensor"]["observed_class"] for r in revision["revision"]["experiences"]] == [r["present_sensor"]["observed_class"] for r in oracle["experiences"]]
    checks["no_new_diagnostic_edits"] = revision["revision"]["new_diagnostic_edits"] == 0
    checks["aliases_conserved_through_revision"] = revision["before"]["aliases"] == revision["after"]["aliases"]
    for index, signal in enumerate(("S1", "S2")):
        ref_world = d.OrganizationalWorld.load_snapshot(str(reference / ("EMISSION_" + signal + ".deetsnap")))
        checks[signal + "_emission_raw_clocks_equal_reference"] = queries[index]["after"]["physical_digest"] == digest(ref_world)
        checks[signal + "_query_applied"] = queries[index]["query_admitted"]
        checks[signal + "_current_native_direction_equal_reference"] = queries[index]["query"]["emission"]["physical"] == oracle["uses"][index]["anticipation"]["emission"]["physical"]
        checks[signal + "_future_event_not_queued_at_emission"] = queries[index]["after"]["pending_external_receipt_count"] == 0
    final_world = d.OrganizationalWorld.load_snapshot(str(observed / "MAIN_FINAL330.deetsnap"))
    checks["final330_raw_clocks_equal_reference"] = digest(final_world) == oracle["final"]
    checks["actual_function_resource_profiles_equal_reference"] = [r["evaluation"]["profile"] for r in consequences] == [r["evaluation"]["profile"] for r in oracle["uses"]]
    checks["native_revised_expression_V_U"] = [r["query"]["emission"]["anticipated_class"] for r in queries] == ["V", "U"]
    isolated = args.output / "SOLO_ESTADO_OPACO"
    isolated.mkdir()
    snapshot = isolated / "ESTADO.deetsnap"
    shutil.copyfile(observed / "REVISION284.deetsnap", snapshot)
    app = module.Demonstration(sys.executable, args.output / "CONTROLADOR_AISLADO")
    app.worker("validate", mutates=False, snapshot=snapshot)
    independent_query = app.worker("query", ["--signal", "S1"])
    checks["separate_process_snapshot_only_reproduces_new_question"] = independent_query["query_admitted"] and independent_query["after"]["physical_digest"] == queries[0]["after"]["physical_digest"]
    checks["query_imports_neither_generator_nor_revision"] = not {"src.experiment", "src.app_revision", "src.reversal"}.intersection(independent_query["query_isolation"]["imported_local_modules"])
    checks["isolated_query_does_not_read_history"] = not any(Path(p).name in ("EXPERIENCIAS.jsonl", "REEXPERIENCIAS.jsonl") or "GENERADOR_REVISION_EXTERNO" in Path(p).parts for p in independent_query["query_isolation"]["python_read_paths"])
    old_path, old_sha = app.current, sha(app.current)
    for case in ("pending_teacher285", "revision_phase", "extra_assignment"):
        world = d.OrganizationalWorld.load_snapshot(str(snapshot))
        if case == "pending_teacher285":
            world.submit("outcome.S1.U", 11, 285)
        else:
            meta = json.loads(world.runtime.snapshot_metadata(PROTOCOL_KEY))
            if case == "revision_phase":
                meta["revision_slots"][0][1] += 1
            else:
                meta["pairing"] = {"S1": "V", "S2": "U"}
            world.runtime.set_snapshot_metadata(PROTOCOL_KEY, json.dumps(meta))
        bad = args.output / ("DIAGNOSTIC_" + case + ".deetsnap")
        world.save_snapshot(str(bad))
        try:
            app.worker("validate", mutates=False, snapshot=bad)
            rejected = False
        except RuntimeError:
            rejected = True
        checks[case + "_rejected_transactionally"] = rejected and app.current == old_path and sha(old_path) == old_sha
    out_of_domain = module.Demonstration(sys.executable, args.output / "CONTROLADOR_LIMITES")
    out_of_domain.worker("validate", mutates=False, snapshot=observed / "MAIN_FINAL330.deetsnap")
    old_path, old_sha = out_of_domain.current, sha(out_of_domain.current)
    revision_answer = out_of_domain.run_line("revisar V U")
    query_answer = out_of_domain.run_line("señal zuvi")
    checks["second_revision_and_fifth_query_rejected_no_reset"] = revision_answer.startswith("INTERFAZ RECHAZA") and query_answer.startswith("INTERFAZ RECHAZA") and out_of_domain.current == old_path and sha(old_path) == old_sha
    reserved = ROOT / "resultados/demostracion_reservada/MAIN_FINAL.deetsnap"
    out_of_domain.worker("validate", mutates=False, snapshot=reserved)
    old_path, old_sha = out_of_domain.current, sha(out_of_domain.current)
    rejected = out_of_domain.run_line("revisar V U")
    checks["revision_on_reserved_geometry_rejected_no_reset"] = rejected.startswith("INTERFAZ RECHAZA") and out_of_domain.current == old_path and sha(old_path) == old_sha
    result = {"verified": all(checks.values()), "checks_count": len(checks), "checks": checks,
              "modality": "TECHNICAL_APPLICATION_PROTOCOL_EQUIVALENCE_AND_PERSISTENCE_NOT_NEW_SCIENTIFIC_CASES",
              "source_sha256": {name: sha(ROOT / name) for name in ("demostracion.py", "src/app_worker.py", "src/app_revision.py", "src/test_app_revision.py")},
              "reference_measurements_sha256": sha(reference / "MEASUREMENTS.json"),
              "main129_parent_sha256": sha(parent129), "revision284_snapshot_sha256": sha(observed / "REVISION284.deetsnap"),
              "main330_snapshot_sha256": sha(observed / "MAIN_FINAL330.deetsnap"),
              "physical_final": digest(final_world), "isolated_query_proof": independent_query["query_isolation"],
              "interpretation_limit": "Revised native expression V/U; incremental utility after reexposure is not established, since U function was already protected in the control."}
    put(args.output / "RESULTS.json", result)
    print(json.dumps({"verified": result["verified"], "checks_count": len(checks)}))
    assert result["verified"], checks


if __name__ == "__main__":
    main()
