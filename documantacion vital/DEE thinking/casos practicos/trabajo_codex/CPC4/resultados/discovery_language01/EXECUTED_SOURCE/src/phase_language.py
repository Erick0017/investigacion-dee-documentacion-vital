"""Finite grounding after native communication, on the SAME complete Runtime.

An explicit fixed external sensor observes the PRESENT optional-resource path.
Its class is broadcast identically to both predeclared lexical regions. Only a
physically coincident word acquires the tested relation. Neither the word ID nor
the sender's lesson/history selects a response. No CPC3 module is imported.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import channel
from src.common import put, sha

KEY = "cpc4.lexical.neutral.v1"
FORMS = {"W1": "HAY", "W2": "NO"}  # Phonology->port only, NEVER function.
NSM_IDS = {"W1": "NSM65.THERE_IS", "W2": "NSM65.NOT"}
TEACHING_TICKS = (169, 197)
QUERY_TICKS = (236, 264)
MODES = ("full", "report_omitted", "signal_omitted", "unpaired", "memory_cut", "sham")


def append(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False) + "\n")
        stream.flush()


def metadata(world, spec, order, phase, cursor):
    """Lifecycle only: no class, A/B history, sensor result or answer table."""
    value = {"version": 1, "translation": list(spec["translation"]),
             "word_order": list(order), "teaching_ticks": list(TEACHING_TICKS),
             "query_ticks": list(QUERY_TICKS), "signal_payload": 5,
             "phase": phase, "cursor": cursor}
    world.runtime.set_snapshot_metadata(KEY, json.dumps(value, separators=(",", ":")))


def current_resource_sensor(world, spec, bank_name):
    """Current measurement, not a stored capture or a hidden history label.

    A missing expected load3/direction packet means absence IN THIS OBSERVER'S
    PREDECLARED WINDOW. It is an external absence transducer, not proof that
    DEE natively perceives absence or that the resource was destroyed.
    """
    bank = spec["banks"][bank_name]
    tick = world.runtime.current_tick
    displacement = tick - (bank["emission_tick"] + 4)
    if tick < 169 or displacement < 0:
        raise ValueError("Resource sensor requested before the native consequence phase")
    site = channel.moved(bank["cost_meeting"], bank["resource_direction"], displacement)
    observation = channel.observe(world, site)
    present = (observation["active"] and observation["semantic"] == 1 and observation["s_reg"] == 3
               and observation["direction"] == list(bank["resource_direction"]))
    source_receipts = [channel.receipt(world, r.id) for r in world.runtime.receipts
                       if bank["prefix"] + ".resource" in r.channels]
    if len(source_receipts) != 1 or source_receipts[0]["status"] != "applied":
        raise ValueError("The finite actual-resource source contract is not present")
    return {"modality": "EXTERNAL_FIXED_CURRENT_RESOURCE_SENSOR", "tick": tick,
            "bank": bank_name, "actual_observation": observation, "resource_present": bool(present),
            "teacher_sign_from_current_measurement": 1 if present else -1,
            "prepared_source_receipts": source_receipts,
            "scope": "Expected native resource packet at its current path position; external windowed absence classification; no word->function lookup",
            "lineage_scope": "Known two-source finite preparation plus actual segment observation, not a universal genealogy certificate"}


def read_word(world, spec, form, receipt_id=None):
    observation = channel.observe(world, spec["lexical_hubs"][form])
    receipt = channel.receipt(world, receipt_id) if receipt_id is not None else None
    admitted = receipt is None or receipt.get("status") == "applied"
    direction = observation["direction"]
    valid = (admitted and observation["active"] and observation["semantic"] == 1
             and observation["s_reg"] == 21 and direction in ([-1, 1, 0], [-1, -1, 0]))
    return {"attribution": "ENTE" if valid else "INSTRUMENTO", "form_id": form,
            "text_form": FORMS[form], "documentary_nsm_id": NSM_IDS[form],
            "physical_output": observation, "receipt": receipt, "available": bool(valid),
            "resource_class": ("PRESENTE_EN_VENTANA" if direction[1] == 1 else "AUSENTE_EN_VENTANA") if valid else None,
            "decoder": "Fixed load21 and direction(-1,+/-1,0); same for BOTH forms and ALL histories",
            "full_NSM_semantics": False,
            "scope": "Specific acquired relation to a windowed resource consequence; no existential or universal-negation mastery claim"}


def late_lexical_cut(world, spec, mode):
    """Declared diagnostic fork only; FULL and operational UI never call this."""
    import dee_thinking as d
    if world.runtime.current_tick != 172 or mode not in ("memory_cut", "sham"):
        raise ValueError("Diagnostic lexical cut has a fixed T172 boundary")
    form = "W1" if mode == "memory_cut" else "W2"
    site = spec["lexical_hubs"][form]
    before = channel.observe(world, site)
    expected_load = 16 if mode == "memory_cut" else 11
    expected_dx = 0 if mode == "memory_cut" else 1
    if not before["active"] or before["s_reg"] != expected_load or before["direction"][0] != expected_dx or abs(before["direction"][1]) != 1:
        raise ValueError("The actual candidate is absent; no diagnostic carrier is fabricated")
    parent_raw, parent_clocks = world.runtime.raw_copy(), world.runtime.clock_copy()
    parent_receipts = [channel.receipt(world, r.id) for r in world.runtime.receipts]
    edit = d.ResearchStateEdit()
    edit.coordinate = d.Coordinate(*site)
    edit.raw = 0
    edit.label = "CPC4_LEXICAL_MEMORY_REMOVAL" if mode == "memory_cut" else "CPC4_UNPAIRED_BROADCAST_CARRIER_SHAM_REMOVAL"
    child = world.diagnostic_fork([edit], True)
    changed = [i for i, (left, right) in enumerate(zip(parent_raw, child.runtime.raw_copy())) if left != right]
    assert changed == [(site[0] * channel.N + site[1]) * channel.N + site[2]]
    assert child.runtime.clock_copy() == parent_clocks
    assert [channel.receipt(child, r.id) for r in child.runtime.receipts] == parent_receipts
    assert world.runtime.raw_copy() == parent_raw and world.runtime.clock_copy() == parent_clocks
    return child, {"modality": "EXPLICIT_DIAGNOSTIC_FORK", "kind": mode, "tick": 172,
                   "site": list(site), "pre": before, "raw_sites_changed": 1, "clock_sites_changed": 0,
                   "parent_unchanged": True,
                   "scope": "Remove acquired W1 memory versus an actual unpaired W2 broadcast carrier. Sham functional comparability is measured, not assumed."}


def teach_slot(world, spec, output, form, bank, tick, mode="full"):
    """External experience protocol; the participant receives no association map."""
    if mode not in MODES:
        raise ValueError("Unknown frozen experience mode")
    world.run_until(tick)
    sensor = current_resource_sensor(world, spec, bank)
    ids = []
    if mode != "report_omitted":
        ids.extend(r.id for r in channel.lexical_outcome_broadcast(world, sensor["teacher_sign_from_current_measurement"], tick))
    if mode != "signal_omitted":
        at = tick + (1 if mode == "unpaired" else 0)
        ids.append(channel.lexical_signal(world, form, at).id)
    world.run_until(tick + 3 + (1 if mode == "unpaired" else 0))
    row = {"form_id": form, "text_form": FORMS[form], "current_sensor": sensor,
           "mode": mode, "receipts": [channel.receipt(world, identity) for identity in ids],
           "post_current": {f: channel.observe(world, q) for f, q in spec["lexical_hubs"].items()},
           "full_NSM_semantics": False,
           "scope": "External current-outcome teaching; fixed word waveform; broadcast teacher identical at both lexical regions"}
    append(Path(output) / "EXPERIENCIAS_LINGUISTICAS.jsonl", row)
    return row


def query_word(world, spec, form, tick):
    """The complete query signature: current world, neutral geometry, form, time.

    No lesson, class, resource target, sender history or expected response enters.
    """
    world.run_until(tick)
    before = channel.digest(world)
    receipt = channel.lexical_signal(world, form, tick)
    world.run_until(tick + 3)
    value = read_word(world, spec, form, receipt.id)
    value.update(input_tick=tick, emission_tick=tick + 3, before=before,
                 after=channel.digest(world), query_modality="PHYSICAL_IDENTICAL_WORD_SIGNAL_ON_SAME_MAIN")
    return value


def forward(world, spec, case, output):
    # Case IDs, A/B histories and expected outcomes are NEVER consulted here.
    # Only this explicit experience protocol is read; the sensor reads RAW.
    order = tuple(case.get("word_order", ("W1", "W2")))
    mode = case.get("mode", "full")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    if world.runtime.current_tick != 169 or sorted(order) != ["W1", "W2"] or mode not in MODES:
        raise ValueError("Forward grounding must continue the same completed native consequence world at169")
    if mode in ("memory_cut", "sham") and tuple(order) != ("W1", "W2"):
        raise ValueError("Localized control is frozen for the principal order only")
    metadata(world, spec, order, "BEFORE_WORD_EXPERIENCE", 0)
    initial = channel.digest(world)
    world.save_snapshot(str(output / "MAIN_BEFORE_GROUNDING169.deetsnap"))
    lessons, diagnostics = [], []
    for index, (form, bank, tick) in enumerate(zip(order, ("plus", "minus"), TEACHING_TICKS)):
        lesson = teach_slot(world, spec, output, form, bank, tick, mode)
        lessons.append(lesson)
        metadata(world, spec, order, "EXPERIENCE_RETAINED", index + 1)
        world.save_snapshot(str(output / ("AFTER_" + form + "_EXPERIENCE.deetsnap")))
        if index == 0 and mode in ("memory_cut", "sham"):
            world, diagnostic = late_lexical_cut(world, spec, mode)
            diagnostics.append(diagnostic)
    world.run_until(235)
    metadata(world, spec, order, "BEFORE_WORD_QUERY", 0)
    world.save_snapshot(str(output / "OPAQUE_RESTORE_BEFORE_QUERY235.deetsnap"))
    queries = []
    for index, (form, tick) in enumerate(zip(order, QUERY_TICKS)):
        metadata(world, spec, order, "QUERYING", index)
        response = query_word(world, spec, form, tick)
        # This comparison belongs ONLY to the external post-hoc evaluator.
        response["evaluation_only_matches_own_past_sensor"] = None if not response["available"] else (response["resource_class"] == ("PRESENTE_EN_VENTANA" if lessons[index]["current_sensor"]["resource_present"] else "AUSENTE_EN_VENTANA"))
        append(output / "RESPUESTAS_PALABRAS.jsonl", response)
        queries.append(response)
        metadata(world, spec, order, "WORD_QUERY_RETAINED", index + 1)
        world.save_snapshot(str(output / ("WORD_EMISSION_" + form + ".deetsnap")))
    metadata(world, spec, order, "FINITE_FORWARD_COMPLETE", 2)
    world.save_snapshot(str(output / "MAIN_FINAL267.deetsnap"))
    return world, {"initial": initial, "final": channel.digest(world), "lessons": lessons,
                   "queries": queries, "diagnostics": diagnostics, "word_order": list(order),
                   "full_NSM_semantics": False,
                   "scope": "Two forms associated with measured resource presence/absence in this finite apparatus. Same Runtime after communication; no65primes or universal-negation claim."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    case = json.loads(args.case.read_text(encoding="utf-8"))
    from src.channel_dual import run
    world, spec, body = run(case["body"], args.output / "CUERPO", return_world=True)
    world, lexical = forward(world, spec, case, args.output / "LENGUAJE")
    result = {"case": case, "body": {"final": body["final"], "external_utility": body["external_utility"],
               "primary_sum": body["primary_sum"], "optional_sum": body["optional_sum"]},
              "language": lexical,
              "source_sha256": {name: sha(ROOT / "src" / name) for name in ("channel.py", "channel_dual.py", "phase_language.py")}}
    put(args.output / "MEASUREMENTS.json", result)
    print(json.dumps({"tick": world.runtime.current_tick, "forms": [x["text_form"] for x in lexical["queries"]],
                      "classes": [x["resource_class"] for x in lexical["queries"]],
                      "available": [x["available"] for x in lexical["queries"]]}))


if __name__ == "__main__":
    main()
