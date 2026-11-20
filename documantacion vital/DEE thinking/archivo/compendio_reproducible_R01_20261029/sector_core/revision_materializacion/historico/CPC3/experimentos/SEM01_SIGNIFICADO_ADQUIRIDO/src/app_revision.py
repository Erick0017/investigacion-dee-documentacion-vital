"""Application adapter of the measured finite phase-1 reexposure protocol.

This is the EXTERNAL experience generator, not the participant or decoder.
It continues the supplied T129 world; never creates, forks, edits or reinstalls
the body. The query process does not import this module or receive its pairing.
"""
from pathlib import Path

from . import experiment, habitat, memory
from .common import append, digest, receipt

SLOTS = (("S1", 151), ("S2", 179), ("S1", 218), ("S2", 246))


def reexpose(world, pairing, output):
    """Same sequence and phase as reversal02_phase/FULL_REVERSE, no test data."""
    if world.runtime.current_tick != 129:
        raise ValueError("Finite reexposure requires this same individual's used T129 boundary")
    if pairing != {"S1": "V", "S2": "U"}:
        raise ValueError("Only the measured finite V/U reexposure is published by this application")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    banks = experiment.descriptors((0, 0, 0))
    before = digest(world)
    initial_diagnostic_count = len(world.diagnostic_edits)
    all_ids = []
    experiences = []
    for signal, sensor_tick in SLOTS:
        bank = banks["train." + signal]
        launch = sensor_tick - 14
        event_tick = launch - 1
        # Fixed timing is selected by the measured phase variant, never from
        # a response, requested correct answer or error in a query.
        world.run_until(event_tick)
        event_request = world.submit(bank["prefix"] + "." + pairing[signal], 11, event_tick)
        world.run_until(launch)
        resources = habitat.submit_resources(world, bank, launch)
        ids = [r.id for r in resources] + [event_request.id]
        world.run_until(sensor_tick)
        sensor = experiment.current_outcome_sensor(world, bank)
        # The actual native supply effect supplies the report. The event label
        # chooses the physical generator ONLY, not the sensory report contents.
        outcome_reports = memory.broadcast_outcome(world, sensor["observed_class"], sensor_tick)
        signal_request = world.submit("signal." + signal, 5, sensor_tick)
        ids.extend(r.id for r in outcome_reports)
        ids.append(signal_request.id)
        world.run_until(sensor_tick + 2)
        before_meeting = {s: memory.read_emission(world, s) for s in ("S1", "S2")}
        world.run_until(sensor_tick + 3)
        after_meeting = {s: memory.read_emission(world, s) for s in ("S1", "S2")}
        row = {"signal": signal, "sensor_tick": sensor_tick, "physical_event_tick": event_tick,
               "external_generator_event": pairing[signal], "present_sensor": sensor,
               "report_contents_from_current_sensor": True,
               "before_meeting": before_meeting, "after_meeting": after_meeting,
               "actual_receipts": [receipt(world, identity) for identity in ids]}
        append(output / "REEXPERIENCIAS.jsonl", row)
        experiences.append(row)
        all_ids.extend(ids)
    world.run_until(284)
    if len(world.diagnostic_edits) != initial_diagnostic_count:
        raise RuntimeError("Reexposure must not perform diagnostic physical edits")
    return {"modality": "EXPERIENCE_PROTOCOL_ON_THE_SAME_MAIN", "before": before, "after": digest(world),
            "experiences": experiences, "actual_receipts": [receipt(world, identity) for identity in all_ids],
            "new_body": False, "new_diagnostic_edits": 0,
            "scope": "Finite phase-1 physical reexposure. Revised expression is measured later; no incremental utility benefit is presumed."}
