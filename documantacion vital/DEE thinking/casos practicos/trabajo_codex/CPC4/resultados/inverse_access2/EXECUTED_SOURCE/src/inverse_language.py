"""Finite diagnostic event->word access, distinct from forward word queries.

The external sensor encodes an ACTUAL current resource observation identically
at both lexical regions. Native direction composition selects any matching
stored relation; the application never looks up class->word associations.
"""
from __future__ import annotations

from pathlib import Path
import json

from . import channel
from .common import put, sha
from .phase_language import FORMS, KEY, current_resource_sensor

INPUT_TICKS = (303, 331)
READ_TICKS = (306, 334)


def observe_symbol(world, spec, form, receipt_id):
    physical = channel.observe(world, spec["lexical_hubs"][form])
    receipt = channel.receipt(world, receipt_id)
    valid = (receipt["status"] == "applied" and physical["active"]
             and physical["semantic"] == 1 and physical["s_reg"] == 26
             and physical["direction"] in ([-1, 1, 0], [-1, -1, 0]))
    return {"attribution": "ENTE" if valid else "INSTRUMENTO", "physical_output": physical,
            "receipt": receipt, "symbol_emitted": FORMS[form] if valid else None,
            "form_id": form if valid else None, "available": valid,
            "decoder": "Only native load26 diagonal at this physical lexical region identifies its text form. Load5 and flat load26 are not words.",
            "full_NSM_semantics": False}


def remove_one_retained_word(parent, spec):
    """Explicit diagnostic fork at267; identify by actual segment, not a map."""
    if parent.runtime.current_tick != 267:
        raise ValueError("Inverse memory cut has its declared T267 boundary")
    neutral = json.loads(parent.runtime.snapshot_metadata(KEY) or "null")
    if not isinstance(neutral, dict) or sorted(neutral.get("word_order", [])) != ["W1", "W2"]:
        raise ValueError("Neutral forward chronology unavailable")
    age = 267 - (239 if neutral["word_order"][0] == "W1" else 267)
    candidates = []
    for sign in (-1, 1):
        q = channel.moved(spec["lexical_hubs"]["W1"], (-1, sign, 0), age)
        r = channel.observe(parent, q)
        if r["active"] and r["semantic"] == 1 and r["s_reg"] == 21 and r["direction"] == [-1, sign, 0]:
            candidates.append(q)
    if len(candidates) != 1:
        raise ValueError("Unique observed W1 retained segment not reconstructed; no cut fabricated")
    return channel.diagnostic_record_edit(parent, candidates[0], "INVERSE_W1_RETAINED_SEGMENT_REMOVAL", raw=0, expected_load=21)


def inverse(parent, spec, case, output):
    """Return a DIAGNOSTIC child and evidence; never merge into the parent MAIN.

    case selects only which actual resource-path sensor to inspect and whether
    a declared local memory cut is requested. It contains no class->word map.
    """
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    bank = case.get("bank", "plus")
    mode = case.get("mode", "full")
    if parent.runtime.current_tick != 267 or bank not in ("plus", "minus") or mode not in ("full", "memory_cut", "sham"):
        raise ValueError("Inverse access requires a completed finite forward parent at267")
    names = set(parent.runtime.channel_names)
    required = {"lex." + f + ".inverse." + suffix for f in ("W1", "W2") for suffix in ("plus", "minus")}
    if not required <= names:
        raise ValueError("Inverse interfaces were not prepared before T0; load does not install matter or channels")
    neutral = json.loads(parent.runtime.snapshot_metadata(KEY) or "null")
    if not isinstance(neutral, dict) or sorted(neutral.get("word_order", [])) != ["W1", "W2"]:
        raise ValueError("Neutral forward chronology unavailable")
    initial = channel.digest(parent)
    entry_sources = {name: sha(Path(__file__).with_name(name)) for name in ("channel.py", "phase_language.py", "inverse_language.py")}
    if mode == "memory_cut":
        world, edit = remove_one_retained_word(parent, spec)
    elif mode == "sham":
        site = channel.moved(spec["sham_source"], (1, 0, 0), 267)
        current = channel.observe(parent, site)
        if current["direction"] != [1, 0, 0]:
            raise ValueError("Common dummy sham not reconstructed; no carrier fabricated")
        world, edit = channel.diagnostic_record_edit(parent, site, "INVERSE_COMMON_DUMMY_SHAM_REMOVAL", raw=0, expected_load=13)
    else:
        world, edit = parent.fork(), None
    assert channel.digest(parent) == initial
    world.save_snapshot(str(output / "DIAGNOSTIC_CHILD267.deetsnap"))
    windows = []
    for requested_form, tick, read_tick in zip(neutral["word_order"], INPUT_TICKS, READ_TICKS):
        world.run_until(tick)
        sensor = current_resource_sensor(world, spec, bank)
        suffix = "plus" if sensor["resource_present"] else "minus"
        # Exactly the same physical sensor report reaches BOTH candidate
        # regions, independent of which text form might eventually respond.
        ids = {form: world.probe("lex." + form + ".inverse." + suffix, 5, tick).id for form in ("W1", "W2")}
        world.run_until(read_tick)
        observations = {form: observe_symbol(world, spec, form, identity) for form, identity in ids.items()}
        windows.append({"sensor": sensor, "input_tick": tick, "read_tick": read_tick,
                        "retained_region_due_at_this_window": requested_form,
                        "observations": observations})
        world.save_snapshot(str(output / ("INVERSE_WINDOW" + str(read_tick) + ".deetsnap")))
    emitted = [r["symbol_emitted"] for window in windows for r in window["observations"].values() if r["available"]]
    final = channel.digest(world)
    assert channel.digest(parent) == initial
    result = {"modality": "EXPLICIT_DIAGNOSTIC_FORK_PLUS_PHYSICAL_SENSOR_PROBES",
              "bank_sensor": bank, "mode": mode, "initial_parent": initial, "final_child": final,
              "parent_unchanged": True, "diagnostic_edit": edit, "windows": windows,
              "emitted_symbols": emitted, "unique_symbol": emitted[0] if len(emitted) == 1 else None,
              "available": len(emitted) == 1, "source_sha256_at_entry": entry_sources,
              "full_NSM_semantics": False,
              "scope": "Conditional inverse accessibility of the two acquired physical relations. Current class sensor is external; Native direction/load participation chooses a region. No universal existential or negation semantics."}
    put(output / "MEASUREMENTS.json", result)
    return world, result
