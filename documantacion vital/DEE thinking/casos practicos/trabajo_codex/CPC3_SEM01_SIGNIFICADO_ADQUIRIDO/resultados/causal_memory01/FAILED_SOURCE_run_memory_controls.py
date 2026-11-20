"""SEM01 finite memory-selective contrasts and reserved inverse-order panels.

This is external experimental instrumentation. It never supplies the predictive
decoder with a teaching map or chooses a native action. Main confirmations are
owned by experiment.py; this runner consumes a named full snapshot for explicit
diagnostic branches and runs two separately identified memory-only reserves.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import experiment, habitat, memory, memory_counterfactuals, participant
from src.common import append, digest, identity, obs, put, receipt, sha


RESERVES = [
    {"id": "MEM_RESERVED_INVERSE_ORDER_A", "translation": [4, 7, 5],
     "pairing": {"S1": "U", "S2": "V"}, "order": ["S2", "S1"]},
    {"id": "MEM_RESERVED_INVERSE_ORDER_B", "translation": [-7, 4, -5],
     "pairing": {"S1": "V", "S2": "U"}, "order": ["S2", "S1"]},
]


def immutable_config(root, snapshot, reference):
    return {
        "purpose": "SELECTIVE_MEMORY_DIAGNOSTICS_AND_TWO_MEMORY_ONLY_RESERVED_PREPARATIONS",
        "scope": "No new reversal family; reserves test signal identity/order/translation and current-physical-outcome acquisition, not independent functional-use closure",
        "parent_snapshot": snapshot.resolve().relative_to(root.resolve()).as_posix(), "parent_snapshot_sha256": sha(snapshot),
        "reference_measurements": reference.resolve().relative_to(root.resolve()).as_posix(), "reference_sha256": sha(reference),
        "parent_relative_tick": 83,
        "arms": ["MEM_REMOVE", "SHAM_REMOVE", "DIRECT_ACTION_RESCUE"],
        "cut": "one actual learned S1 carrier RAW set0; clock field absent from edit",
        "sham": "one actual unpaired second-broadcast carrier in S1 region RAW set0; clock unchanged",
        "direct_action": "same S1 cut; after observing the failed diagonal read at87, advance1 so the ordinary query vacates the fixed port; fixed direct-action input21 and matched resources at88, event89; diagnostic actuator-availability control, not acquired response",
        "decisive_samples": {"S1": 87, "S2": 115},
        "reserve_specifications": RESERVES,
        "source_sha256": {name: sha(root / "src" / name) for name in
                          ("memory.py", "memory_counterfactuals.py", "participant.py", "experiment.py", "habitat.py", "run_memory_controls.py")},
        "configuration_frozen_before_execution": True,
    }


def one_fork(config, arm, output, root):
    import dee_thinking as d
    source = root / config["parent_snapshot"]
    assert sha(source) == config["parent_snapshot_sha256"]
    reference_path = root / config["reference_measurements"]
    reference = __import__("json").loads(reference_path.read_text(encoding="utf-8"))
    assert sha(reference_path) == config["reference_sha256"]
    world = d.OrganizationalWorld.load_snapshot(str(source))
    assert world.runtime.current_tick == 83
    original = digest(world)
    translation = tuple(reference["case"].get("translation", (0, 0, 0)))
    first_class = reference["teaching"]["experiences"][0]["present_sensor"]["observed_class"]
    second_class = reference["teaching"]["experiences"][1]["present_sensor"]["observed_class"]
    signs = {"U": 1, "V": -1}
    if arm == "SHAM_REMOVE":
        center = memory.hub("S1", translation)
        direction = (1, signs[second_class], 0)
        site = memory.plus(center, direction, 83 - 48)
        expected_load = memory.OUTCOME_LOAD
    else:
        direction = (0, signs[first_class], 0)
        site = memory_counterfactuals.mobile_memory_site("S1", 20, 83, signs[first_class], translation)
        expected_load = memory.SIGNAL_LOAD + memory.OUTCOME_LOAD
    branch, edit = memory_counterfactuals.remove_one_record(
        world, site, arm, expected_direction=direction, expected_load=expected_load)
    branch.save_snapshot(str(output / "AFTER_DIAGNOSTIC_EDIT_T83.deetsnap"))
    banks = experiment.descriptors(translation)
    if arm != "DIRECT_ACTION_RESCUE":
        branch, uses = experiment.execute_uses(branch, banks,
            reference["case"].get("future_events", reference["case"]["pairing"]), output, translation)
    else:
        # A direct input after a lost memory readout checks the actuator/bank,
        # never the association. It is deliberately identified as external.
        anticipation = participant.signal_only(branch, "S1", 84, translation)
        assert anticipation["emission_tick"] == 87
        bank = banks["use.S1"]
        # The unacquired -x query still occupies the emitter at87. Do not erase
        # it to admit a replacement. One ordinary tick vacates that fixed port.
        branch.advance()
        assert branch.runtime.current_tick == 88
        challenge_tick = 88
        challenge = memory_counterfactuals.present_reference_action(branch, bank["prefix"] + ".reference_action", challenge_tick)
        ids = [challenge["receipt_id"]]
        ids.extend(r.id for r in habitat.submit_resources(branch, bank, challenge_tick))
        captures, trace = {}, []
        for now in range(challenge_tick, challenge_tick + 15):
            if now == challenge_tick + 1:
                value = habitat.submit_event(branch, bank, reference["case"]["future_events"]["S1"], challenge_tick)
                ids.append(value.id)
            trace.append(habitat.read_bank(branch, bank, challenge_tick, captures))
            if now < challenge_tick + 14:
                branch.advance()
        uses = [{"signal": "S1", "anticipation": anticipation,
                 "direct_action_challenge": challenge, "challenge_emission_tick": challenge_tick,
                 "one_native_tick_wait_to_admit_fixed_port": True, "trace": trace,
                 "evaluation": habitat.evaluate_captures(captures),
                 "actual_receipts": [receipt(branch, x) for x in ids],
                 "scope": "Direct external actuator availability after memory ablation, not restoration of the association"}]
    assert digest(world) == original
    branch.save_snapshot(str(output / "DIAGNOSTIC_FINAL.deetsnap"))
    result = {"id": arm, "modality": "DIAGNOSTIC_FORK", "edit": edit,
              "reference_parent": original, "parent_unchanged_after_all_branch_evolution": digest(world) == original,
              "uses": uses, "final": digest(branch),
              "external_operations_actual": list(branch.external_operations),
              "scope": "Counterfactual branch; the operational parent is never resumed from this result"}
    put(output / "MEASUREMENTS.json", result)
    return result


def memory_reserve(spec, output):
    import dee_thinking as d
    translation = tuple(spec["translation"])
    world, banks = experiment.prepare(d, translation)
    initial = digest(world)
    world.save_snapshot(str(output / "T0_BEFORE_ASSIGNMENT.deetsnap"))
    # Pairing belongs solely to the experience generator after preparation.
    assigned = dict(spec["pairing"])
    inputs, training = [], []
    training_ticks = {}
    for signal, launch, sensor_tick in zip(spec["order"], (3, 31), (17, 45)):
        bank = banks["train." + signal]
        world.run_until(launch)
        inputs.extend(r.id for r in habitat.submit_resources(world, bank, launch))
        world.run_until(launch + 1)
        inputs.append(habitat.submit_event(world, bank, assigned[signal], launch).id)
        world.run_until(sensor_tick)
        sensed = experiment.current_outcome_sensor(world, bank)
        outcome_receipts = memory.broadcast_outcome(world, sensed["observed_class"], sensor_tick)
        signal_receipt = memory.present_signal(world, signal, sensor_tick)
        inputs.extend(r.id for r in outcome_receipts)
        inputs.append(signal_receipt.id)
        training_ticks[signal] = sensor_tick
        row = {"signal": signal, "signal_tick": sensor_tick, "present_sensor": sensed,
               "outcome_receipts": [r.id for r in outcome_receipts], "signal_receipt": signal_receipt.id,
               "modality": "EXPERIENCE_PROTOCOL_CURRENT_PHYSICAL_OUTCOME_SENSOR"}
        append(output / "EXPERIENCIAS.jsonl", row)
        training.append(row)
        world.run_until(sensor_tick + 5)
    predictions = []
    for signal in spec["order"]:
        query_tick = training_ticks[signal] + memory.N
        world.run_until(query_tick - 1)
        world.save_snapshot(str(output / ("BEFORE_" + signal + ".deetsnap")))
        value = participant.signal_only(world, signal, query_tick, translation)
        predictions.append(value)
        append(output / "PREDICCIONES.jsonl", value)
        world.save_snapshot(str(output / ("AFTER_" + signal + ".deetsnap")))
    world.save_snapshot(str(output / "MAIN_FINAL.deetsnap"))
    result = {"id": spec["id"], "scope": "MEMORY_ONLY_RESERVED; no future U/V or utility-use bank event is supplied during the signal-only panel",
              "configuration": spec, "initial_before_assignment": initial, "training": training,
              "predictions": predictions, "actual_receipts": [receipt(world, x) for x in inputs],
              "query_schedule_neutral_metadata": training_ticks,
              "future_consequences_during_query": [], "operational_forks": 0,
              "final": digest(world), "external_operations_actual": list(world.external_operations)}
    put(output / "MEASUREMENTS.json", result)
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True, type=Path)
    p.add_argument("--wheel", required=True, type=Path)
    p.add_argument("--snapshot", type=Path)
    p.add_argument("--reference", type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--child")
    p.add_argument("--reserves-only", action="store_true")
    a = p.parse_args()
    a.root = a.root.resolve()
    a.output = a.output.resolve()
    if a.child:
        import json
        config = json.loads((a.output / "CONFIG.json").read_text(encoding="utf-8"))
        folder = a.output / a.child
        folder.mkdir(parents=True, exist_ok=True)
        put(folder / "IDENTITY.json", identity(a.wheel))
        started = time.monotonic()
        if a.child in config["arms"]:
            result = one_fork(config, a.child, folder, a.root)
        else:
            spec = next(x for x in config["reserve_specifications"] if x["id"] == a.child)
            result = memory_reserve(spec, folder)
        put(folder / "ELAPSED.json", {"elapsed_seconds": time.monotonic() - started})
        print(result["id"])
        return
    if not a.snapshot or not a.reference:
        p.error("A named full parent snapshot and reference measurements are required before freezing")
    a.output.mkdir(parents=True, exist_ok=True)
    frozen = a.output / "CONFIG.json"
    config = immutable_config(a.root, a.snapshot, a.reference)
    if frozen.exists():
        import json
        assert json.loads(frozen.read_text(encoding="utf-8")) == config, "Frozen configuration mismatch"
    else:
        put(frozen, config)
    sys.path.insert(0, str(a.root))
    from supervise import run
    names = [] if a.reserves_only else list(config["arms"])
    names += [x["id"] for x in config["reserve_specifications"]]
    for name in names:
        folder = a.output / name
        if (folder / "MEASUREMENTS.json").exists():
            continue
        job_name = "memory_causal_" + name.lower()
        if (a.root / "jobs" / job_name).exists():
            raise RuntimeError("Previous job exists without a completed measurement; diagnose rather than silently retry")
        value = run(a.root, job_name, [sys.executable, "-I", "-B", str(Path(__file__).resolve()),
                    "--root", str(a.root), "--wheel", str(a.wheel.resolve()), "--output", str(a.output), "--child", name],
                    timeout=180)
        if value["exit_code"] != 0:
            raise RuntimeError("Owned finite diagnostic child failed: " + name)


if __name__ == "__main__":
    main()
