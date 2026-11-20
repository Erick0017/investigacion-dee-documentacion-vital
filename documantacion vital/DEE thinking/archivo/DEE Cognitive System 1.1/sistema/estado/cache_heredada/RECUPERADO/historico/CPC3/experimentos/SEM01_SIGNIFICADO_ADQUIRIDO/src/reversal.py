"""Finite SEM01 reversal continuation, with no new body or physical edits.

Three cohorts load the same acquired-and-used T129 parent and remain on their
own single MAIN. All cohorts receive the same four physical outcome episodes.
They differ only in which declared sensory inputs are omitted. Outcome report
content always comes from the present native supply detector, never from the
requested event label. Core SEM01 modules are imported unchanged.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import experiment, habitat, memory, participant
from src.common import append, digest, identity, obs, put, receipt, sha

ARMS = ("FULL_REVERSE", "SIGNAL_INPUT_ONLY", "OUTCOME_REPORT_ONLY")
EXPERIENCES = (
    {"signal": "S1", "sensor_tick": 151, "event": "V", "round": 1},
    {"signal": "S2", "sensor_tick": 179, "event": "U", "round": 1},
    {"signal": "S1", "sensor_tick": 218, "event": "V", "round": 2},
    {"signal": "S2", "sensor_tick": 246, "event": "U", "round": 2},
)
QUERIES = (("S1", 285, "V"), ("S2", 313, "U"))


def panel(world, translation=(0, 0, 0), neighborhood=False):
    rows = {}
    for signal in memory.HUBS:
        center = memory.hub(signal, translation)
        item = {"center": memory.read_emission(world, signal, translation)}
        if neighborhood:
            item["moore_26"] = [obs(world, memory.plus(center, (x, y, z)))
                for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1)
                if (x, y, z) != (0, 0, 0)]
        rows[signal] = item
    return {"tick": world.runtime.current_tick, "scope": "Passive declared center and optional local-neighborhood panel", "signals": rows}


def configuration(root, parent, training_event_offset=1):
    if training_event_offset not in (1, -1):
        raise ValueError("Only the original and the deduced two-tick-earlier training phases are admitted")
    arms = ARMS if training_event_offset == 1 else ("FULL_REVERSE", "SIGNAL_INPUT_ONLY")
    return {
        "id": "SEM01_REVERSAL_FROM_USED_MAIN129_V1" if training_event_offset == 1 else "SEM01_REVERSAL_EARLY_TRAINING_EVENT_PHASE_V2",
        "parent_snapshot": parent.resolve().relative_to(root.resolve()).as_posix(),
        "parent_sha256": sha(parent), "parent_tick": 129,
        "arms": list(arms), "translation": [0, 0, 0], "signal_payload": 5,
        "training_event_offset_from_resource_launch": training_event_offset,
        "evaluation_event_offset_from_antecedent_emission": 1,
        "variant_reason": "Original phase" if training_event_offset == 1 else "Directed replay showed returning oldV and newU co-arrive at interception173. Advance all teaching U/V events by2 equally, keep resources, current sensors, cues, queries and post-forecast evaluation events unchanged.",
        "new_experiences": list(EXPERIENCES),
        "query_protocol": [{"signal": signal, "input_tick": tick, "emission_tick": tick + 3,
                            "independent_later_event": event} for signal, tick, event in QUERIES],
        "controls": {
            "FULL_REVERSE": "All four native outcome banks and actual sensory reports, plus all four fixed signal inputs",
            "SIGNAL_INPUT_ONLY": "Same native banks/resources/events, omit only outcome-report input; physical consequences are not omitted",
            "OUTCOME_REPORT_ONLY": "Same native banks/resources/events and their present sensory reports, omit only signal input",
        },
        "all_native_interfaces_already_present_in_parent": True,
        "new_body_preparation": False, "clock_edits": False, "raw_edits": False,
        "maximum_native_trajectories": len(arms), "final_tick": 330,
        "signal_semantics": "Signal accompanies present supply effect, not the earlier threat launch",
        "main_scope": "S1's earlier useful action may have consumed its carrier, so later expression may be reacquisition. S2's surviving carrier must be inspected; no conclusion is inferred from the term reversal.",
        "fixed_actuator_scope": "Utility coupling is prepared. No independent utility-learning claim.",
        "source_sha256": {name: sha(root / "src" / name) for name in
            ("reversal.py", "memory.py", "habitat.py", "participant.py", "experiment.py", "common.py")},
        "configuration_frozen_before_execution": True,
    }


def continuation(config, root, arm, output):
    import dee_thinking as d
    parent = root / config["parent_snapshot"]
    assert sha(parent) == config["parent_sha256"]
    world = d.OrganizationalWorld.load_snapshot(str(parent))
    assert world.runtime.current_tick == config["parent_tick"] == 129
    translation = tuple(config["translation"])
    banks = experiment.descriptors(translation)
    initial = digest(world)
    receipt_ids_before = {r.id for r in world.runtime.receipts}
    diagnostic_count_before = len(world.diagnostic_edits)
    world.save_snapshot(str(output / "CONTINUATION_T129.deetsnap"))
    append(output / "LOCAL_TRACE.jsonl", panel(world, translation, True))
    # These inert fields carry only schedule/lifecycle, no acquired class or
    # requested assignment. They never feed F_v27 or the physical decoder.
    world.runtime.set_snapshot_metadata("sem01.reversal.neutral_protocol", json.dumps({
        "version": 1, "translation": list(translation), "current_phase": "reexposure",
        "signal_slots": [[x["signal"], x["sensor_tick"]] for x in config["new_experiences"]],
        "query_slots": [[x["signal"], x["input_tick"]] for x in config["query_protocol"]]}, separators=(",", ":")))
    operational_metadata_calls = [{"operation": "set_snapshot_metadata", "key": "sem01.reversal.neutral_protocol",
        "tick": 129, "scope": "OPERATIVE_METADATA_NON_RAW; schedule only, no event class or target"}]
    experiences = []
    for item in config["new_experiences"]:
        signal, sensor_tick, event = item["signal"], item["sensor_tick"], item["event"]
        launch = sensor_tick - 14
        bank = banks["train." + signal]
        event_tick = launch + config.get("training_event_offset_from_resource_launch", 1)
        if event_tick < launch:
            # New phase was deduced before this configuration was run. The
            # physical event is submitted at its actual future boundary, never
            # inserted into the past and never timed from an output or target.
            world.run_until(event_tick)
            event_request = world.submit(bank["prefix"] + "." + event, 11, event_tick)
        world.run_until(launch)
        resources = habitat.submit_resources(world, bank, launch)
        ids = [x.id for x in resources]
        resource_requests = [receipt(world, x.id) for x in resources]
        if event_tick >= launch:
            world.run_until(event_tick)
            event_request = habitat.submit_event(world, bank, event, launch)
        ids.append(event_request.id)
        world.run_until(sensor_tick)
        sensed = experiment.current_outcome_sensor(world, bank)
        before = panel(world, translation, True)
        report_ids, signal_id = [], None
        if arm != "SIGNAL_INPUT_ONLY":
            reports = memory.broadcast_outcome(world, sensed["observed_class"], sensor_tick)
            report_ids = [r.id for r in reports]
            ids.extend(report_ids)
        if arm != "OUTCOME_REPORT_ONLY":
            value = world.submit("signal." + signal, config["signal_payload"], sensor_tick)
            signal_id = value.id
            ids.append(value.id)
        row = {"signal": signal, "round": item["round"], "sensor_tick": sensor_tick,
               "generator_requested_physical_event": event, "training_event_tick": event_tick,
               "present_sensor": sensed,
               "requested_event_agrees_with_observed_sensor": event == sensed["observed_class"],
               "same_environmental_exposure_in_all_arms": True,
               "mode": arm, "resource_request_receipts": resource_requests,
               "outcome_report_receipt_ids": report_ids, "signal_receipt_id": signal_id,
               "before_sensory_inputs": before,
               "selection": "Omissions fixed by arm; report content is solely present native supply state"}
        world.run_until(sensor_tick + 2)
        before_meeting = panel(world, translation, True)
        append(output / "LOCAL_TRACE.jsonl", before_meeting)
        world.save_snapshot(str(output / (signal + "_ROUND" + str(item["round"]) + "_BEFORE_MEETING.deetsnap")))
        world.run_until(sensor_tick + 3)
        after_meeting = panel(world, translation, True)
        append(output / "LOCAL_TRACE.jsonl", after_meeting)
        world.save_snapshot(str(output / (signal + "_ROUND" + str(item["round"]) + "_AFTER_MEETING.deetsnap")))
        row["after_meeting"] = after_meeting
        row["actual_receipts"] = [receipt(world, x) for x in ids]
        append(output / "EXPERIENCIAS.jsonl", row)
        experiences.append(row)
    uses = []
    for item in config["query_protocol"]:
        signal, tick = item["signal"], item["input_tick"]
        world.run_until(tick - 1)
        world.save_snapshot(str(output / ("BEFORE_SIGNAL_" + signal + ".deetsnap")))
        append(output / "LOCAL_TRACE.jsonl", panel(world, translation, True))
        anticipation = participant.signal_only(world, signal, tick, translation, config["signal_payload"])
        emit = anticipation["emission_tick"]
        assert emit == item["emission_tick"]
        append(output / "PREDICCIONES.jsonl", anticipation)
        world.save_snapshot(str(output / ("EMISSION_" + signal + ".deetsnap")))
        bank = banks["use." + signal]
        ids = [x.id for x in habitat.submit_resources(world, bank, emit)]
        captures, trace = {}, []
        for now in range(emit, emit + 15):
            if now == emit + 1:
                # The future event is introduced after the actual native
                # emission; no predictive output is read to choose it.
                value = habitat.submit_event(world, bank, item["independent_later_event"], emit)
                ids.append(value.id)
            trace.append(habitat.read_bank(world, bank, emit, captures))
            if now < emit + 14:
                world.advance()
        actual_class = anticipation["emission"]["anticipated_class"]
        row = {"signal": signal, "anticipation": anticipation,
               "later_generator_event": item["independent_later_event"],
               "prediction_correct": None if actual_class is None else actual_class == item["independent_later_event"],
               "trace": trace, "evaluation": habitat.evaluate_captures(captures),
               "actual_receipts": [receipt(world, x) for x in ids]}
        append(output / "USES.jsonl", row)
        uses.append(row)
    assert world.runtime.current_tick == config["final_tick"]
    assert len(world.diagnostic_edits) == diagnostic_count_before
    world.runtime.set_snapshot_metadata("sem01.reversal.neutral_protocol", json.dumps({
        "version": 1, "translation": list(translation), "current_phase": "finite_continuation_complete",
        "last_tick": world.runtime.current_tick}, separators=(",", ":")))
    operational_metadata_calls.append({"operation": "set_snapshot_metadata", "key": "sem01.reversal.neutral_protocol",
        "tick": world.runtime.current_tick, "scope": "OPERATIVE_METADATA_NON_RAW; lifecycle only"})
    world.save_snapshot(str(output / "MAIN_FINAL.deetsnap"))
    new_receipts = [receipt(world, r.id) for r in world.runtime.receipts if r.id not in receipt_ids_before]
    result = {"id": arm, "kind": "SAME_MAIN_CONTINUATION_COHORT_FROM_USED_PARENT129",
              "parent_snapshot_sha256": config["parent_sha256"], "initial": initial,
              "experiences": experiences, "uses": uses, "final": digest(world),
              "all_new_receipts": new_receipts, "external_operations_actual": list(world.external_operations),
              "operational_metadata_calls": operational_metadata_calls,
              "new_diagnostic_edits": len(world.diagnostic_edits) - diagnostic_count_before,
              "scope": config["main_scope"], "fixed_actuator_scope": config["fixed_actuator_scope"]}
    put(output / "MEASUREMENTS.json", result)
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True, type=Path)
    p.add_argument("--wheel", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--parent", type=Path)
    p.add_argument("--child", choices=ARMS)
    p.add_argument("--training-event-offset", type=int, choices=(1, -1), default=1,
                   help="Original+1 or deduced two-tick-earlier teaching phase-1; evaluation events stay post-forecast+1")
    a = p.parse_args()
    a.root, a.output = a.root.resolve(), a.output.resolve()
    config_path = a.output / "CONFIG.json"
    if a.child:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        folder = a.output / a.child
        folder.mkdir(parents=True, exist_ok=True)
        put(folder / "IDENTITY.json", identity(a.wheel))
        started = time.monotonic()
        result = continuation(config, a.root, a.child, folder)
        put(folder / "ELAPSED.json", {"elapsed_seconds": time.monotonic() - started})
        print(json.dumps({"id": result["id"], "tick": result["final"]["tick"]}))
        return
    if a.parent is None:
        p.error("A preserved acquired-and-used parent snapshot must be named explicitly")
    a.output.mkdir(parents=True, exist_ok=True)
    frozen = configuration(a.root, a.parent, a.training_event_offset)
    if config_path.exists():
        assert json.loads(config_path.read_text(encoding="utf-8")) == frozen, "Frozen reversal cut differs"
    else:
        put(config_path, frozen)
    sys.path.insert(0, str(a.root))
    from supervise import run
    completed = []
    for arm in frozen["arms"]:
        folder = a.output / arm
        if not (folder / "MEASUREMENTS.json").exists():
            name = a.output.name + "_" + arm.lower()
            if (a.root / "jobs" / name).exists():
                raise RuntimeError("An earlier instrumental attempt must be diagnosed and preserved before retry")
            row = run(a.root, name, [sys.executable, "-I", "-B", str(Path(__file__).resolve()),
                      "--root", str(a.root), "--wheel", str(a.wheel.resolve()), "--output", str(a.output), "--child", arm], 180)
            if row["exit_code"] != 0:
                raise RuntimeError("Finite reversal child failed: " + arm)
        data = json.loads((folder / "MEASUREMENTS.json").read_text(encoding="utf-8"))
        completed.append({"id": arm, "evidence": arm + "/MEASUREMENTS.json",
                          "sensor_classes": [x["present_sensor"]["observed_class"] for x in data["experiences"]],
                          "predictions": [x["anticipation"]["emission"] for x in data["uses"]],
                          "native_function_resource": [x["evaluation"]["profile"] for x in data["uses"]],
                          "receipt_status_counts": {status: sum(r["status"] == status for r in data["all_new_receipts"])
                              for status in sorted({r["status"] for r in data["all_new_receipts"]})},
                          "final": data["final"]})
        put(a.output / "RESULTS.json", {"config_sha256": sha(config_path), "cohorts": completed})


if __name__ == "__main__":
    main()
