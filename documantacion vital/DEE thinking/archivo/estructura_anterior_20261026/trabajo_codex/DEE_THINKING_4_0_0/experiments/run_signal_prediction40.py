"""Six frozen current-signal experiments using the installed public DEE4 API.

The N35 carrier world and N47 relational body have separate Runtimes. Their
coupling is an explicitly external local sensor at ticks32 and33. No future
rollout, case label, or evaluator value chooses the body input or its output.
"""
from __future__ import annotations

import argparse
from array import array
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time
import zipfile


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def qualify(path):
    """Verify the installation before constructing either experimental world."""
    import dee_thinking as dee
    seal = json.loads(Path(path).read_text(encoding="utf-8"))
    assert seal["qualified"] is True and seal["version"] == "4.0.0" and seal["kernel"] == 27
    assert dee.__version__ == "4.0.0" and dee.kernel_identity()["kernel_version"] == 27
    assert Path(sys.executable).resolve() == Path(seal["python_executable"]).resolve()
    assert Path(dee.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
    assert "site-packages" in str(Path(dee.__file__).resolve())
    assert sha(dee._native.__file__) == seal["native_sha256"]
    wheel = Path(path).resolve().parent.parent / "wheel/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl"
    assert sha(wheel) == seal["wheel_sha256"]
    hashes = {}
    with zipfile.ZipFile(wheel) as archive:
        for member in archive.namelist():
            if member.startswith("dee_thinking/") and member.endswith((".py", ".pyi")):
                expected = hashlib.sha256(archive.read(member)).hexdigest()
                installed = Path(dee.__file__).parent / Path(member).relative_to("dee_thinking")
                assert sha(installed) == expected, member
                hashes[member] = expected
    return {"qualified_gate_utc": now(), "qualification_sha256": sha(path),
            "wheel_sha256": seal["wheel_sha256"], "native_sha256": seal["native_sha256"],
            "version": dee.__version__, "kernel": 27, "python": sys.executable,
            "module": dee.__file__, "installed_python_member_hashes": hashes}


def observation(value):
    r = value.record
    return {"tick": value.tick, "site": [value.coordinate.x, value.coordinate.y, value.coordinate.z],
            "raw": value.raw, "clock": value.clock, "state": r.state,
            "s_reg": r.s_reg, "semantic": r.semantic, "direction": [r.dx, r.dy, r.dz],
            "active": r.state > 0 and r.semantic != 5}


def digest(world):
    return {"tick": world.runtime.current_tick,
            "raw_sha256": hashlib.sha256(array("Q", world.runtime.raw_copy()).tobytes()).hexdigest(),
            "clock_sha256": hashlib.sha256(array("Q", world.runtime.clock_copy()).tobytes()).hexdigest()}


def build_world(dee, spec):
    d = spec["detector"]
    direction = spec["direction"]
    source = [(x + spec["source_offset"] * v) % 35 for x, v in zip(d, direction)]
    carrier = dee.InitialPlacement()
    carrier.site = dee.Coordinate(*source)
    carrier.raw = dee.pack_record(1, 7, *direction, 1)
    carrier.clock = 0
    carrier.role = "Normal carrier, not a body answer or future report"
    placements = [carrier]
    if spec.get("obstacle"):
        obstacle = dee.InitialPlacement()
        obstacle.site = dee.Coordinate(*[(x + 8*v) % 35 for x, v in zip(d, direction)])
        obstacle.raw = dee.pack_record(1, 0, 0, 0, 0, 4)
        obstacle.clock = 0
        obstacle.role = "Fixed route obstacle prepared before T0; not an input label"
        placements.append(obstacle)
    recipe = dee.OrganizationRecipe.research(35, placements, 32)
    recipe.execution = dee.TickOptions(dee.Backend.LAZY, 1)
    return dee.OrganizationalWorld.create(recipe)


def execute_case(dee, spec, output):
    seed = Path(dee.__file__).parent / "data/OBP_FRESH_VALIDATED_T32.deetsnap"
    p = dee.CognitiveParameters()
    p.seed_path = str(seed)
    p.profile = "continuity"
    p.initial_open = False
    p.change_tick = None
    p.execution = dee.TickOptions(dee.Backend.LAZY, 1)
    body = dee.CognitiveSession.create(p)
    world = build_world(dee, spec)
    detector = dee.Coordinate(*spec["detector"])
    assert body.tick == world.runtime.current_tick == 32
    operations = [{"tick": 32, "operation": "prepare", "modality": "PRE_T0_CONFIGURATION",
                   "scope": "Two independent Runtimes: N35 physical signal world, N47 H0 body"}]
    snapshots = []

    def save(tick):
        assert body.tick == world.runtime.current_tick == tick
        for name, obj in (("BODY", body), ("WORLD", world)):
            path = output / (name + "_T" + str(tick) + ("_PENDING" if tick == 37 else "") + ".deetsnap")
            obj.save_snapshot(str(path))
            snapshots.append({"file": path.name, "sha256": sha(path), "tick": tick,
                              "kind": "CognitiveSession" if name == "BODY" else "OrganizationalWorld"})

    save(32)
    samples, inputs, local_trace = [], [], []
    for tick in (32, 33):
        world.run_until(tick)
        current = observation(world.runtime.observe(detector))
        before = digest(world)
        assert observation(world.runtime.observe(detector)) == current
        assert digest(world) == before
        samples.append(current)
        # Fixed external sensor codec reads only the CURRENT local observation.
        # The source offset, obstacle flag, case ID, and future target are absent.
        symbol = "A" if current["active"] else "B"
        if not spec.get("omit_experience"):
            assert body.tick == tick
            received = body.experience(symbol)
            inputs.append({"source_observation": current, "symbol": symbol, "native_result": received})
            operations.append({"tick": tick, "operation": "experience", "symbol": symbol,
                               "modality": "EXTERNAL_CURRENT_LOCAL_SENSOR_CODEC",
                               "receipt_statuses": [r["status"] for r in received["receipts"]]})
    if spec.get("omit_experience"):
        body.run_until(34)
        operations.append({"tick": 32, "operation": "experience_omitted", "modality": "OMISSION_CONTROL"})
    world.run_until(34)
    assert body.tick == 34
    before_prediction = body.observe()
    save(34)
    prediction = body.predict(30)
    assert body.tick == prediction["emission_tick"] == 37
    assert prediction["target_tick"] == 67
    # No world has advanced past37 before recording this pending emission.
    world.run_until(37)
    save(37)
    pending = {"recorded_utc": now(), "body_tick": body.tick,
               "world_tick": world.runtime.current_tick, "target_tick": 67,
               "source_samples_only": samples, "prediction": prediction,
               "body_digest": digest(body.world), "world_digest": digest(world),
               "target_not_yet_evolved_in_either_main": True,
               "body_evaluator": "NO_APLICA_OTRO_ENTORNO",
               "horizon": "Prepared 30-tick forecast after emission37; torus period35 is NOT learned here"}
    write(output / "EMISSION_T37_BEFORE_TARGET.json", pending)
    operations.append({"tick": 37, "operation": "record_pending_prediction_before_outcome",
                       "modality": "PASSIVE_OBSERVATION", "target": 67})
    emitted_before_advance_sha = sha(output / "EMISSION_T37_BEFORE_TARGET.json")
    body_after = body.run_until(67)
    # Physical world evolves tick by tick solely for a small local trace. No input
    # is chosen, scheduled, or changed by this later observer.
    for tick in range(38, 68):
        world.run_until(tick)
        current = observation(world.runtime.observe(detector))
        if current["active"] or tick in (39, 40, 41, 66, 67):
            local_trace.append(current)
    actual = observation(world.runtime.observe(detector))
    assert sha(output / "EMISSION_T37_BEFORE_TARGET.json") == emitted_before_advance_sha
    save(67)
    predicted = prediction["prediction_set"]
    measured = {"actual_local_detector": actual, "prediction_set": predicted,
                "singleton": len(predicted) == 1,
                "singleton_correct": predicted[0] == actual["active"] if len(predicted) == 1 else None,
                "set_contains_observed": actual["active"] in predicted,
                "body_delta_before_prediction": before_prediction["delta"],
                "body_at_emission": prediction["observation"], "body_after": body_after["observation"],
                "external_truth_source": "Current passive local observation of N35 world at67, not body barrier or scenario label",
                "body_evaluator": {"status": "NO_APLICA_OTRO_ENTORNO",
                                   "raw_unrelated_evaluations": body_after["evaluations"],
                                   "used_for_input_or_comparison": False}}
    restoration = None
    if spec.get("restore_witness"):
        restored_body = dee.CognitiveSession.load_snapshot(str(output / "BODY_T37_PENDING.deetsnap"))
        restored_world = dee.OrganizationalWorld.load_snapshot(str(output / "WORLD_T37_PENDING.deetsnap"))
        pending_body = restored_body.predictions
        assert pending_body[0]["evaluated"] is False
        restored_body.run_until(67)
        restored_world.run_until(67)
        restoration = {"type": "TECHNICAL_CONTINUATION_FROM_PENDING37_NOT_NEW_INDEPENDENT_CASE",
                       "restored_pending_predictions": pending_body,
                       "body_physical_equal": digest(restored_body.world) == digest(body.world),
                       "world_physical_equal": digest(restored_world) == digest(world),
                       "body_readout_equal": restored_body.observe() == body.observe(),
                       "detector_equal": observation(restored_world.runtime.observe(detector)) == actual,
                       "predictions_equal": restored_body.predictions == body.predictions}
        assert all(restoration[k] for k in ("body_physical_equal", "world_physical_equal", "body_readout_equal", "detector_equal", "predictions_equal"))
        write(output / "RESTORE37_TECHNICAL_CONTINUATION.json", restoration)
    return {"modality": "EXTERNAL_SENSOR_COUPLING_OF_TWO_NATIVE_RUNTIMES",
            "case": spec, "observations32_33": samples, "external_inputs": inputs,
            "physical_prediction_before_target": prediction,
            "pending_record_sha256": emitted_before_advance_sha,
            "measurements": measured, "local_detector_trace38_67": local_trace,
            "operations": operations, "body_native_journal": body.journal,
            "snapshots": snapshots, "restoration": restoration,
            "final": {"body": digest(body.world), "world": digest(world)},
            "limits": ["No learned estimate of period35; forecast horizon is a prepared protocol parameter",
                       "External current-activity codec, not native absence detection or one-Runtime sensor integration",
                       "Unseen prepared obstacle is not passed to the body",
                       "Body evaluator belongs to a different barrier environment and is explicitly not applied"]}


def frozen_config():
    return {"schema": "dee4.signal_prediction.frozen.v1", "frozen_utc": now(),
            "cases": [
                {"id": "present_then_absent", "detector": [12, 12, 12], "direction": [1, 0, 0], "source_offset": 0, "restore_witness": True},
                {"id": "absent_then_present", "detector": [12, 12, 12], "direction": [1, 0, 0], "source_offset": -1},
                {"id": "omitted_history_same_present_world", "detector": [12, 12, 12], "direction": [1, 0, 0], "source_offset": 0, "omit_experience": True},
                {"id": "present_future_route_obstacle", "detector": [12, 12, 12], "direction": [1, 0, 0], "source_offset": 0, "obstacle": True},
                {"id": "reserved_present_minusY", "detector": [18, 16, 20], "direction": [0, -1, 0], "source_offset": 0, "reserved": True},
                {"id": "reserved_absent_minusY", "detector": [18, 16, 20], "direction": [0, -1, 0], "source_offset": -1, "reserved": True}],
            "physical_world": {"N": 35, "initial_tick": 32, "state": 1, "semantic": 1, "s_reg": 7,
                               "local_clock": 0, "obstacle_offset": 8, "obstacle_semantic": 4},
            "body": {"profile": "continuity", "history": "H0 before sensor experiences", "N": 47,
                     "initial_tick": 32, "initial_open": False, "change_tick": None},
            "sensor": {"times": [32, 33], "codec": "current active -> A; current inactive -> B",
                       "active_predicate": "state>0 and semantic!=5", "mode": "EXTERNAL_LOCAL_OBSERVER_AND_INPUT"},
            "prediction": {"query_tick": 34, "emission_tick": 37, "horizon": 30, "target_tick": 67,
                           "period35": "Prepared geometric context, not acquired period estimate"},
            "comparison": {"truth": "ONLY local detector observation at67", "ambiguous": "null singleton correctness; not numeric zero",
                           "matched_control": "same current32/33 observations for obstacle and no obstacle",
                           "reserved": "fixed translation and minusY orientation; no refit"},
            "resource_limit": {"cases": 6, "process_timeout_seconds": 180, "threads_per_runtime": 1,
                               "maximum_technical_corrections": 2},
            "attribution": "Native acquired relation and prior physical emission; external inter-Runtime sensor and target evaluation",
            "no_main_operational_fork": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--qualification", type=Path, required=True)
    parser.add_argument("--python", type=Path)
    parser.add_argument("--child", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    if args.child:
        start = time.monotonic()
        product = qualify(args.qualification)
        import dee_thinking as dee
        case = json.loads(args.child.read_text(encoding="utf-8"))
        args.output.mkdir(parents=True, exist_ok=True)
        result = execute_case(dee, case, args.output)
        result.update(product=product, runner_sha256=sha(__file__),
                      elapsed_seconds=time.monotonic()-start, completed_utc=now())
        write(args.output / "MEASUREMENTS.json", result)
        return
    assert args.python
    seal = json.loads(args.qualification.read_text(encoding="utf-8"))
    assert seal["qualified"] is True
    assert args.python.resolve() == Path(seal["python_executable"]).resolve()
    sys.path.insert(0, str(root))
    from supervise40 import run
    output = root / "experiments/SIGNAL_PREDICTION"
    output.mkdir(parents=True, exist_ok=True)
    config_path = output / "EXPERIMENT_CONFIG.json"
    if not config_path.exists():
        write(config_path, frozen_config())
    config = json.loads(config_path.read_text(encoding="utf-8"))
    assert len(config["cases"]) == 6
    assert datetime.fromisoformat(config["frozen_utc"]) > datetime.fromisoformat(seal["utc"])
    rows = []
    for spec in config["cases"]:
        case_dir = output / spec["id"]
        case_dir.mkdir(parents=True, exist_ok=True)
        case_path = case_dir / "CASE.json"
        if case_path.exists():
            assert json.loads(case_path.read_text()) == spec
        else:
            write(case_path, spec)
        measurements = case_dir / "MEASUREMENTS.json"
        if measurements.exists():
            row = json.loads(measurements.read_text(encoding="utf-8"))
            assert row["case"] == spec and row["product"]["wheel_sha256"] == seal["wheel_sha256"]
        else:
            job_name = "signal_prediction_" + spec["id"]
            attempt = 1
            while (root / "jobs" / job_name).exists():
                attempt += 1
                job_name = "signal_prediction_" + spec["id"] + "_attempt" + str(attempt)
            assert attempt <= 3, "Maximum two technical corrections; preserve failures"
            job = run(root, job_name, [str(args.python), "-I", "-B", str(Path(__file__).resolve()),
                       "--root", str(root), "--qualification", str(args.qualification.resolve()),
                       "--child", str(case_path.resolve()), "--output", str(case_dir.resolve())], 180, cwd=str(output))
            row = json.loads(measurements.read_text(encoding="utf-8")) if job["exit_code"] == 0 else {"case": spec, "status": "TECHNICAL_ERROR", "job": job}
            with (output / "CASE_LEDGER.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps({"case": spec["id"], "job": job, "measurement": str(measurements)}) + "\n")
        rows.append(row)
        write(output / "RESULTS.json", {"cases": rows, "config_sha256": sha(config_path), "coverage": "finite6, deterministic worlds not statistical repetitions"})
    lookup = {row["case"]["id"]: row for row in rows if "measurements" in row}
    matched = None
    if all(key in lookup for key in ("present_then_absent", "present_future_route_obstacle")):
        a = lookup["present_then_absent"]
        b = lookup["present_future_route_obstacle"]
        matched = {"samples32_33_equal": a["observations32_33"] == b["observations32_33"],
                   "native_body_emission_equal": a["physical_prediction_before_target"] == b["physical_prediction_before_target"],
                   "body_physical_digest_at67_equal": a["final"]["body"] == b["final"]["body"],
                   "actual67_by_world": [a["measurements"]["actual_local_detector"], b["measurements"]["actual_local_detector"]]}
        assert matched["samples32_33_equal"] and matched["native_body_emission_equal"]
    write(output / "RESULTS.json", {"cases": rows, "config_sha256": sha(config_path),
           "matched_route_control": matched,
           "scientific_scope": "History-dependent native physical emission before actual local world observation, prepared periodic context and withheld future route control",
           "no_claims": ["learned period35", "native one-Runtime sensor integration", "unseen obstacle prediction", "precognition"],
           "technical_restore_continuation_count": sum(row.get("restoration") is not None for row in rows),
           "independent_fresh_preparations": len(lookup), "closed_utc": now()})


if __name__ == "__main__":
    main()
