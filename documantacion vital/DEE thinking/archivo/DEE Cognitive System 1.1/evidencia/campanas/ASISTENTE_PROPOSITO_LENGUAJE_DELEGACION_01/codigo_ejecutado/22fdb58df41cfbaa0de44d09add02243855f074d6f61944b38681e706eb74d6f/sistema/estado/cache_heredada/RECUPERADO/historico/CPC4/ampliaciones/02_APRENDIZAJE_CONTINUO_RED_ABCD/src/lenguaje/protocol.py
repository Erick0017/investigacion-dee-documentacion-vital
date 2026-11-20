"""Two new task-relative forms after ABCD experience, in the SAME Runtime.

The fixed external transducer samples CURRENT native resource/function packets.
Its sign is broadcast identically to four lexical regions.  Only the external
teaching protocol chooses a word form; no form-to-answer map is stored or used
by the querier.  Both query decoders operate on current physical fields only.
"""
from __future__ import annotations

from array import array
import hashlib
import json
from pathlib import Path
import time

KEY = "cpc4.extension02.grounded_forms.neutral.v1"
FORMS = {"L1": "BUENO", "L2": "MALO", "L3": "zumi", "L4": "paku"}
LESSONS = (431, 459)
QUERIES = (498, 526)
READOUTS = (501, 529)
N = 67


def put(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""): h.update(block)
    return h.hexdigest()


def moved(site, direction, count=1):
    return tuple((site[i] + count * direction[i]) % N for i in range(3))


def observe(world, site):
    import dee_thinking as d
    value = world.runtime.observe(d.Coordinate(*site)); r = value.record
    return {"tick": value.tick, "site": list(site), "raw": value.raw, "clock": value.clock,
            "state": r.state, "semantic": r.semantic, "s_reg": r.s_reg,
            "direction": [r.dx, r.dy, r.dz], "active": r.state > 0 and r.semantic != 5}


def digest(world):
    rt = world.runtime
    return {"tick": rt.current_tick,
            "raw_sha256": hashlib.sha256(array("Q", rt.raw_copy()).tobytes()).hexdigest(),
            "clock_sha256": hashlib.sha256(array("Q", rt.clock_copy()).tobytes()).hexdigest()}


def receipt(world, identifier):
    r = world.runtime.receipt(identifier)
    if r is None: return {"id": identifier, "status": "MISSING"}
    return {"id": r.id, "requested_tick": r.requested_tick, "effective_tick": r.effective_tick,
            "status": str(r.status), "kind": str(r.kind), "channels": list(r.channels), "reason": r.reason}


def until(session, tick):
    if session.world.runtime.paused: raise ValueError("Paused MAIN must not be relabelled as evolved")
    session.run_until(tick)
    if session.world.runtime.current_tick != tick: raise RuntimeError("Actual native boundary not reached")


def profile(world, bank, emission_tick):
    """A finite external sensor, not a stored task label or native perception."""
    tick = world.runtime.current_tick
    if tick < emission_tick + 14: raise ValueError("Current packet window not yet available")
    rp = moved(bank["resource_receiver"], bank["resource_direction"], tick - emission_tick - 7)
    fp = moved(bank["function_receiver"], bank["supply_direction"], tick - emission_tick - 14)
    resource, function = observe(world, rp), observe(world, fp)
    def matches(record, load, direction):
        return bool(record["active"] and record["semantic"] == 1 and record["s_reg"] == load
                    and record["direction"] == list(direction))
    R = matches(resource, 3, bank["resource_direction"])
    F = matches(function, 7, bank["supply_direction"])
    sign = 1 if F and not R else (-1 if R and not F else None)
    return {"tick": tick, "function": function, "resource": resource, "profile": [int(F), int(R)],
            "class_sign": sign, "modality": "EXTERNAL_FIXED_CURRENT_PACKET_TRANSDUCER",
            "scope": "Task-relative F7/R3 availability; not universal good/bad or native absence detection"}


def _commit(session, state):
    state["tick"] = session.world.runtime.current_tick
    session.world.runtime.set_snapshot_metadata(KEY, json.dumps(state, separators=(",", ":")))


def _submit(world, name, load, tick, kind, calls):
    r = getattr(world, kind)(name, load, tick)
    calls.append({"id": r.id, "channel": name, "load": load, "requested_tick": tick,
                  "call_tick": world.runtime.current_tick, "modality": "EXPERIENCE_PROTOCOL" if kind == "submit" else "PHYSICAL_PROBE"})
    return r.id


def teach(session, form, sensor, tick, mode, calls):
    if form not in FORMS or tick != session.world.runtime.current_tick: raise ValueError("Declared form/current lesson required")
    if mode not in ("paired", "unpaired", "signal_omitted", "report_omitted"): raise ValueError("Unknown teaching mode")
    ids = []
    if sensor["class_sign"] is None:
        return {"form": form, "status": "NO_CLASS_CONTRACT", "sensor": sensor, "receipts": []}
    if mode != "report_omitted":
        suffix = "plus" if sensor["class_sign"] == 1 else "minus"
        for lane in FORMS:
            ids.append(_submit(session.world, f"lex.{lane}.report.{suffix}", 11, tick, "submit", calls))
    if mode != "signal_omitted":
        ids.append(_submit(session.world, f"lex.{form}.signal", 5, tick + (mode == "unpaired"), "submit", calls))
    until(session, tick + 3 + (mode == "unpaired"))
    return {"form": form, "status": "PHYSICAL_EXPERIENCE_PRESENTED", "sensor": sensor,
            "receipts": [receipt(session.world, x) for x in ids],
            "actual_hubs": {lane: observe(session.world, p) for lane, p in session.spec["lexical_hubs"].items()}}


def decode_word_readout(actual, receipts):
    applied = bool(receipts) and all(x["status"] == "applied" for x in receipts)
    valid = applied and actual["active"] and actual["semantic"] == 1 and actual["s_reg"] == 21 and actual["direction"] in ([-1, 1, 0], [-1, -1, 0])
    return {"valid": bool(valid), "class_sign": actual["direction"][1] if valid else None,
            "modality": "NATIVE_WORD_TO_TASK_PROFILE_READOUT", "physical": actual,
            "scope": "Fixed directional decoder; not a dictionary or the universal semantics of a prime"}


def query_word(session, form, tick, calls):
    until(session, tick)
    identifier = _submit(session.world, f"lex.{form}.signal", 5, tick, "probe", calls)
    until(session, tick + 3)
    rec = receipt(session.world, identifier); actual = observe(session.world, session.spec["lexical_hubs"][form])
    return {"form": form, "external_form": FORMS[form], "tick": tick + 3, "receipts": [rec],
            "readout": decode_word_readout(actual, [rec])}


def name_current_profile(session, bank, emission_tick, tick, calls):
    until(session, tick); sensed = profile(session.world, bank, emission_tick); ids = []
    # Both the signal and class report are identical at every region.  Neither
    # the host nor the decoder chooses a word lane based on the actual class.
    for lane in FORMS:
        ids.append(_submit(session.world, f"lex.{lane}.signal", 5, tick, "probe", calls))
        if sensed["class_sign"] is not None:
            suffix = "plus" if sensed["class_sign"] == 1 else "minus"
            ids.append(_submit(session.world, f"lex.{lane}.report.{suffix}", 5, tick, "probe", calls))
    until(session, tick + 3)
    receipts = [receipt(session.world, i) for i in ids]
    all_applied = bool(receipts) and all(x["status"] == "applied" for x in receipts)
    actual = {lane: observe(session.world, hub) for lane, hub in session.spec["lexical_hubs"].items()}
    candidates = [lane for lane, rec in actual.items() if all_applied and rec["active"] and rec["semantic"] == 1
                  and rec["s_reg"] == 26 and rec["direction"] in ([0, 1, 0], [0, -1, 0])]
    return {"tick": tick + 3, "sensor": sensed, "receipts": receipts, "actual": actual,
            "candidate_lanes": candidates, "emitted_forms": [FORMS[x] for x in candidates],
            "modality": "NATIVE_COMMON_PHYSICAL_PROFILE_TO_FORM_PANEL",
            "scope": "Only actual 26-vertical fields with Applied inputs qualify; labels denote the physical region, not expected answers"}


def run(session, case, output):
    """Continue an existing real network MAIN431. No world is created here."""
    started = time.monotonic(); output = Path(output); output.mkdir(parents=True, exist_ok=True)
    if session.world.runtime.current_tick != 431: raise ValueError("Actual inherited/new network MAIN431 required")
    if set(session.world.runtime.channel_names) != {i.name for i in session.world.interfaces}: raise ValueError("Lost physical interface")
    if any(str(r.status) == "scheduled" for r in session.world.runtime.receipts): raise ValueError("Unexpected future input at MAIN431")
    word_order = list(case.get("word_order", ["L1", "L2"]))
    if sorted(word_order) != ["L1", "L2"]: raise ValueError("Finite two-form order required")
    mode = case.get("teaching", "paired"); calls = []; reads = []; lessons = []
    state = {"version": 1, "stage": "BEFORE_NEW_FORMS", "forms": FORMS, "word_order": word_order,
             "lessons": list(LESSONS), "queries": list(QUERIES), "receipts": [],
             "new_world_emission_tick": 438, "scope": "No form-to-class map, hidden target or cached response"}
    _commit(session, state); initial = digest(session.world)
    session.save(output / "SAME_NETWORK_BEFORE_LANGUAGE431.deetsnap")
    sensed = profile(session.world, session.spec["role"], 417)
    lessons.append(teach(session, word_order[0], sensed, 431, mode, calls))
    # External opportunities have a fixed law, independent of readouts/actions.
    if case.get("second_episode", True):
        for channel, load, tick in (("world.resource", 3, 438), ("world.supply", 7, 444), ("world.U", 11, 439)):
            _submit(session.world, channel, load, tick, "submit", calls)
    until(session, 459)
    sensed2 = profile(session.world, session.spec["bank"], 438)
    lessons.append(teach(session, word_order[1], sensed2, 459, mode, calls))
    state["stage"] = "NEW_EXPERIENCES_PRESENTED"; state["receipts"] = [c["id"] for c in calls]
    _commit(session, state); session.save(output / "AFTER_NEW_EXPERIENCES.deetsnap")
    query_mode = case.get("query_mode", "word")
    for slot, tick in enumerate(QUERIES):
        until(session, tick - 1)
        state["stage"] = "BEFORE_COMMON_QUERY"; state["query_slot"] = slot
        _commit(session, state); session.save(output / f"BEFORE_NEW_QUERY{tick-1}.deetsnap")
        if query_mode == "word": reads.append(query_word(session, word_order[slot], tick, calls))
        elif query_mode in ("name_role", "name_second"):
            bank, emission = (session.spec["role"], 417) if query_mode == "name_role" else (session.spec["bank"], 438)
            reads.append(name_current_profile(session, bank, emission, tick, calls))
        else: raise ValueError("Unknown finite physical panel")
        state["stage"] = "AFTER_COMMON_QUERY"; state["receipts"] = [c["id"] for c in calls]
        _commit(session, state); session.save(output / f"ACTUAL_READ{tick+3}.deetsnap")
        put(output / "INCREMENTAL.json", {"lessons": lessons, "readouts": reads})
    state["stage"] = "COMPLETE529"; _commit(session, state)
    session.save(output / "MAIN_FINAL529.deetsnap")
    result = {"case": case, "initial": initial, "final": digest(session.world), "lessons": lessons,
              "readouts": reads, "calls": calls, "receipts": [receipt(session.world, c["id"]) for c in calls],
              "elapsed_seconds": time.monotonic() - started, "host_raw_clock_edits": [],
              "scope": "Same network Runtime after experience and native role reversal. BUENO/MALO mean only two task-relative current F7/R3 profiles; no reward, no universal prime acquisition."}
    put(output / "MEASUREMENTS.json", result)
    return session, result
