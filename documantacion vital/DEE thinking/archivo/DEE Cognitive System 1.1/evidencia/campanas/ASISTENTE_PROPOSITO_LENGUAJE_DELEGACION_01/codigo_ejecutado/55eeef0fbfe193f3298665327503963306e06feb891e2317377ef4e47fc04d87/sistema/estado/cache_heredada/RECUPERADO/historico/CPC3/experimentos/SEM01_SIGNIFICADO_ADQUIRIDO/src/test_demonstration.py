"""Bounded technical UI qualification. Existing physical witnesses are reused.

No new scientific method or result is claimed by replaying a saved boundary.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.app_worker import APP_KEY, PROTOCOL_KEY, put, sha


def rows(folder):
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(folder.glob("llamada_*/RESULT.json"))]


def measured(folder, operation):
    return [x for x in rows(folder) if x.get("operation") == operation and x.get("completed")]


def loader_checks(output):
    """Small closure qualification after independent readonly review, no replay."""
    import dee_thinking as d
    output.mkdir(parents=True, exist_ok=False)
    spec = importlib.util.spec_from_file_location("sem01_demo_loader_check", ROOT / "demostracion.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    initial = measured(ROOT / "resultados/demostracion_A", "train")[0]["snapshot"]["path"]
    app = module.Demonstration(sys.executable, output / "CONTROLADOR")
    result = app.worker("validate", mutates=False, snapshot=initial)
    original_path = app.current
    original_sha = sha(original_path)
    checks = {"valid_snapshot_loads_without_advance": result["after"]["tick"] == 83,
              "valid_snapshot_no_pending_input": result["after"]["pending_external_receipt_count"] == 0}
    accepted_before = app.counter
    rejected = app.run_line("enseña zuvi V")
    checks["closed_teaching_rejected_without_native_call_or_map"] = rejected.startswith("INTERFAZ RECHAZA") and not app.generator and app.counter == accepted_before
    for case in ("queued_teacher", "uppercase_alias"):
        world = d.OrganizationalWorld.load_snapshot(str(initial))
        if case == "queued_teacher":
            request = world.submit("outcome.S1.U", 11, 84)
            assert str(world.runtime.receipt(request.id).status) == "scheduled"
        else:
            value = json.loads(world.runtime.snapshot_metadata(APP_KEY))
            value["aliases"] = {"ZUVI": "S1", "pako": "S2"}
            world.runtime.set_snapshot_metadata(APP_KEY, json.dumps(value))
        bad = output / ("DIAGNOSTIC_" + case + ".deetsnap")
        world.save_snapshot(str(bad))
        try:
            app.worker("validate", mutates=False, snapshot=bad)
            rejected = False
        except RuntimeError:
            rejected = True
        checks[case + "_rejected_transactionally"] = rejected and app.current == original_path and sha(original_path) == original_sha
    report = {"verified": all(checks.values()), "checks": checks, "checks_count": len(checks),
              "modality": "TECHNICAL_ADVERSARIAL_METADATA_AND_QUEUE_CHECK; no Native evolution or new scientific sample",
              "source_sha256": {"demostracion.py": sha(ROOT / "demostracion.py"), "src/app_worker.py": sha(ROOT / "src/app_worker.py"), "src/test_demonstration.py": sha(__file__)}}
    put(output / "RESULTS.json", report)
    print(json.dumps(report))
    assert report["verified"]


def queued_witness(output):
    """Reconstruct the actual pre-guard interface hole, then its rejection."""
    import dee_thinking as d
    from src import participant
    from src.app_worker import application
    output.mkdir(parents=True, exist_ok=False)
    training = measured(ROOT / "resultados/demostracion_A", "train")[0]
    reference = measured(ROOT / "resultados/demostracion_A", "query")[0]
    world = d.OrganizationalWorld.load_snapshot(training["snapshot"]["path"])
    scheduled = world.submit("outcome.S1.V", 11, 84)
    queued = output / "DIAGNOSTIC_QUEUED_TEACHER_BEFORE_SIGNAL.deetsnap"
    world.save_snapshot(str(queued))
    old_source = next((ROOT / "resultados/UI_TECHNICAL02").glob("**/741f030f3938c004e87f719cd5c558966caca103dce31c4c887f4799c5954b65/app_worker.py"))
    spec = importlib.util.spec_from_file_location("sem01_pre_guard_interface", old_source)
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    accepted_before = old.application(world)["phase"] == "READY"
    try:
        application(world)
        rejected_after = False
    except ValueError as exc:
        rejected_after = "Pending external inputs" in str(exc)
    # Explicit DIAGNOSTIC bypass of application admission; not MAIN, not a
    # permitted query. The historical small function is the SAME frozen helper.
    probe = participant.signal_only(world, "S1", 84)
    state = probe["emission"]["physical"]
    expected = reference["query"]["emission"]["physical"]
    checks = {"old_application_accepted_scheduled_teacher": accepted_before,
              "current_application_rejects_before_evolution": rejected_after,
              "diagnostic_query_and_teacher_applied": probe["receipt"]["status"] == "applied" and str(world.runtime.receipt(scheduled.id).status) == "applied",
              "actual_query_emission_changed": state["raw"] != expected["raw"]}
    report = {"verified": all(checks.values()), "checks": checks,
              "modality": "DIAGNOSTIC_INTERFACE_HOLE_RECONSTRUCTION_NOT_AUTONOMOUS_SIGNAL_ONLY_RESULT",
              "old_worker_sha256": sha(old_source), "new_worker_sha256": sha(ROOT / "src/app_worker.py"),
              "snapshot_before_signal": str(queued), "teacher_channel": "outcome.S1.V", "teacher_tick": 84,
              "baseline_actual_emission": expected, "diagnostic_actual_emission": state,
              "probe_receipt": probe["receipt"], "teacher_receipt_status": str(world.runtime.receipt(scheduled.id).status),
              "scope": "The public app now blocks this state. Teacher and event are not allowed during an operational signal-only query."}
    world.save_snapshot(str(output / "DIAGNOSTIC_AFTER_FORBIDDEN_QUERY.deetsnap"))
    put(output / "RESULTS.json", report)
    print(json.dumps(report))
    assert report["verified"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--reanalizar", type=Path, help="Correct an instrumental path-filter false positive without rerunning Native")
    parser.add_argument("--loader-checks", action="store_true")
    parser.add_argument("--queued-witness", action="store_true")
    args = parser.parse_args()
    if args.reanalizar:
        original_path = args.reanalizar.resolve()
        result = json.loads(original_path.read_text(encoding="utf-8"))
        paths = result["no_teaching_map_in_query_call_graph"]["python_read_paths"]
        result["checks"]["query_no_history_file_reads"] = not any(
            Path(p).name == "EXPERIENCIAS.jsonl" or "GENERADOR_EXTERNO" in Path(p).parts for p in paths)
        result["verified"] = all(result["checks"].values())
        result["instrumental_correction"] = {"original_report_sha256": sha(original_path),
            "original_report_preserved": str(original_path), "new_native_executions": 0,
            "reason": "The old substring GENERADOR matched the deliberately empty folder SIN_GENERADOR_NI_HISTORIAL, not a generator/history file. Actual read paths are retained unchanged.",
            "corrected_filter": "basename EXPR history or exact GENERADOR_EXTERNO directory component, not arbitrary substring",
            "reviewer_source_sha256": sha(__file__)}
        target = original_path.with_name("RESULTS_REVIEWED.json")
        if target.exists():
            raise FileExistsError(target)
        put(target, result)
        print(json.dumps({"verified": result["verified"], "checks_count": len(result["checks"]), "new_native_executions": 0}))
        assert result["verified"]
        return
    if args.output is None:
        parser.error("--output or --reanalizar is required")
    if args.loader_checks:
        loader_checks(args.output)
        return
    if args.queued_witness:
        queued_witness(args.output)
        return
    args.output.mkdir(parents=True, exist_ok=False)
    spec = importlib.util.spec_from_file_location("sem01_demo_test", ROOT / "demostracion.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    import dee_thinking as d
    original = ROOT / "resultados/demostracion_A"
    historic = measured(original, "query")
    reveal_reference = measured(original, "reveal")
    training = measured(original, "train")[0]
    isolated = args.output / "SIN_GENERADOR_NI_HISTORIAL"
    isolated.mkdir()
    snapshot = isolated / "ESTADO_OPACO.deetsnap"
    shutil.copyfile(training["snapshot"]["path"], snapshot)
    assert list(isolated.iterdir()) == [snapshot]
    app = module.Demonstration(sys.executable, isolated)
    checks = {}
    loaded = app.worker("validate", mutates=False, snapshot=snapshot)
    checks["snapshot_only_no_external_history_present"] = len(list(isolated.glob("*.deetsnap"))) == 1
    checks["restored_training_boundary"] = loaded["after"]["physical_digest"] == training["after"]["physical_digest"]
    first = app.worker("query", ["--signal", "S1"])
    checks["first_query_applied"] = first["query_admitted"]
    checks["first_query_same_physical_state_as_original"] = first["after"]["physical_digest"] == historic[0]["after"]["physical_digest"]
    checks["first_query_native_U"] = first["query"]["emission"]["anticipated_class"] == "U"
    checks["query_does_not_import_generator"] = "src.experiment" not in first["query_isolation"]["imported_local_modules"]
    checks["no_map_or_target_in_query_arguments"] = all("--pairing" not in json.loads(p.read_text(encoding="utf-8"))["argv"] and "--event" not in json.loads(p.read_text(encoding="utf-8"))["argv"] for p in isolated.glob("llamada_*query*/PROCESS.json"))
    checks["query_no_history_file_reads"] = not any(Path(p).name == "EXPERIENCIAS.jsonl" or "GENERADOR_EXTERNO" in Path(p).parts for p in first["query_isolation"]["python_read_paths"])
    app.command("guardar CONTINUIDAD.deetsnap")
    saved = isolated / "CONTINUIDAD.deetsnap"
    reloaded = module.Demonstration(sys.executable, args.output / "SEGUNDO_CONTROLADOR")
    reloaded.worker("validate", mutates=False, snapshot=saved)
    after_first = reloaded.worker("reveal", ["--event", "U"])
    checks["reload_same_main_then_real_consequence"] = after_first["after"]["physical_digest"] == reveal_reference[0]["after"]["physical_digest"]
    checks["native_function_and_cost_after_reload"] = after_first["evaluation"]["profile"] == [1, 0]
    second = reloaded.worker("query", ["--signal", "S2"])
    checks["new_question_after_reload_native_V"] = second["query_admitted"] and second["query"]["emission"]["anticipated_class"] == "V"
    checks["new_question_same_physical_state_as_original"] = second["after"]["physical_digest"] == historic[1]["after"]["physical_digest"]
    final = reloaded.worker("reveal", ["--event", "V"])
    checks["full_continuation_same_physical_state"] = final["after"]["physical_digest"] == reveal_reference[1]["after"]["physical_digest"]
    before_path = reloaded.current
    before_sha = sha(before_path)
    observed = reloaded.worker("observe", mutates=False)
    checks["passive_observation_does_not_modify_snapshot"] = sha(before_path) == before_sha and observed["before"]["physical_digest"] == observed["after"]["physical_digest"]
    checks["unsupported_command_rejected_no_reset"] = reloaded.run_line("invierte memoria") .startswith("INTERFAZ RECHAZA") and reloaded.current == before_path and sha(before_path) == before_sha
    # Adversarial metadata edits are diagnostic in separate clones, never MAIN.
    for case in ("translation", "answer_in_metadata", "cursor"):
        world = d.OrganizationalWorld.load_snapshot(str(snapshot))
        if case == "translation":
            value = json.loads(world.runtime.snapshot_metadata(PROTOCOL_KEY))
            value["translation"] = [1, 0, 0]
            world.runtime.set_snapshot_metadata(PROTOCOL_KEY, json.dumps(value))
        else:
            value = json.loads(world.runtime.snapshot_metadata(APP_KEY))
            if case == "answer_in_metadata":
                value["expected_answer"] = "U"
            else:
                value["next_index"] = 1
            world.runtime.set_snapshot_metadata(APP_KEY, json.dumps(value))
        bad = args.output / ("DIAGNOSTIC_" + case + ".deetsnap")
        world.save_snapshot(str(bad))
        try:
            reloaded.worker("validate", mutates=False, snapshot=bad)
            rejected = False
        except RuntimeError:
            rejected = True
        checks[case + "_rejected_transactionally"] = rejected and reloaded.current == before_path and sha(before_path) == before_sha
    alias_app = module.Demonstration(sys.executable, args.output / "ALIAS_ONLY")
    alias_app.worker("validate", mutates=False, snapshot=snapshot)
    changed = alias_app.worker("alias", ["--signal", "S1", "--alias", "bruma"])
    alias_restored = alias_app.worker("validate", mutates=False, snapshot=alias_app.current)
    checks["alias_only_is_persisted_not_a_function_map"] = alias_restored["after"]["aliases"]["bruma"] == "S1" and changed["before"]["physical_digest"] == changed["after"]["physical_digest"]
    # A historical rejected presentation is a contract/UI witness, not a fresh
    # acquisition experiment; no reset or repair of the occupied port occurs.
    signal_control = ROOT / "resultados/confirmacion/signals_only_UV/BEFORE_FIRST_SIGNAL.deetsnap"
    if signal_control.exists():
        world = d.OrganizationalWorld.load_snapshot(str(signal_control))
        meta = json.loads(d.OrganizationalWorld.load_snapshot(str(snapshot)).runtime.snapshot_metadata(APP_KEY))
        world.runtime.set_snapshot_metadata(APP_KEY, json.dumps(meta))
        path = args.output / "DIAGNOSTIC_REJECTED_PORT.deetsnap"
        world.save_snapshot(str(path))
        reject_app = module.Demonstration(sys.executable, args.output / "REJECTION_READOUT")
        reject_app.worker("validate", mutates=False, snapshot=path)
        refused = reject_app.worker("query", ["--signal", "S1"])
        rendered = reject_app.render(refused)
        checks["rejected_signal_not_reported_as_prediction_or_forgetting"] = not refused["query_admitted"] and rendered.startswith("INSTRUMENTO:") and "olvido" in rendered
    # Query signature refuses an externally supplied future label before Native.
    try:
        alias_app.worker("query", ["--signal", "S1", "--event", "U"])
        checks["query_future_event_argument_rejected"] = False
    except RuntimeError:
        checks["query_future_event_argument_rejected"] = True
    result = {"verified": all(checks.values()), "checks": checks, "checks_count": len(checks),
              "modality": "TECHNICAL_REPLAY_AND_UI_PERSISTENCE_QUALIFICATION_NOT_NEW_SCIENTIFIC_SAMPLES",
              "source_sha256": {"demostracion.py": sha(ROOT / "demostracion.py"), "src/app_worker.py": sha(ROOT / "src/app_worker.py"), "src/test_demonstration.py": sha(__file__)},
              "source_witness_training_snapshot_sha256": sha(snapshot),
              "no_teaching_map_in_query_call_graph": first["query_isolation"],
              "final_snapshot": str(reloaded.current), "final_snapshot_sha256": sha(reloaded.current)}
    put(args.output / "RESULTS.json", result)
    print(json.dumps(result, ensure_ascii=False))
    assert result["verified"], checks


if __name__ == "__main__":
    main()
