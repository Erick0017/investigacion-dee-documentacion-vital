"""Finite private-B -> E1 opportunity, on an existing complete owner world.

This module never loads, constructs, forks, promotes or commits a life. The
caller owns the Runtime and must call Store.mutate/commit around it. It never
computes the answer from B's private object. All E1 banks receive identical
resources and fixed readers. Mode names describe interventions, not success.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json

from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation, exact_receipt
from dee_thinking.persistence import encode_metadata, decode_metadata

ROOT = Path(__file__).resolve().parents[3]
KEY = "DEE.Cognitive.System.1.1.HABITAT.social.v1"
MODES = ("full", "no_partner", "message_cut", "message_sham", "unpaired_message")


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf8")


def observe(a, site):
    return exact_observation(a.world.runtime.observe(d.Coordinate(*site)))


def _state(a):
    values = dict(a.world.runtime.snapshot_metadata_entries)
    return decode_metadata(values[KEY]) if KEY in values else {
        "schema": "DCS1.1.habitat.private_B.v1", "episodes": {}}


def _store(a, state):
    a.world.runtime.set_snapshot_metadata(KEY, encode_metadata(state))


def _ports(a):
    return {p.name: p for p in a.world.interfaces}


def _declare_interceptor(a, name, site):
    existing = _ports(a).get(name)
    if existing is not None:
        ch = existing.channel
        actual = [ch.injection_site.x, ch.injection_site.y, ch.injection_site.z]
        direction = [ch.direction.dx, ch.direction.dy, ch.direction.dz]
        if actual != list(site) or direction != [0, 0, 0] or ch.semantic != 4 or ch.state != 1:
            raise ValueError("Existing interceptor interface is incompatible")
        return
    ch = d.ChannelSpec()
    ch.name = name
    ch.injection_site = d.Coordinate(*site)
    ch.direction = d.Direction(0, 0, 0)
    ch.semantic = 4
    ch.state = 1
    ch.allow_experience = True
    ch.allow_probe = False
    spec = d.InterfaceSpec()
    spec.name = name
    spec.channel = ch
    a.world.declare_interface(spec)


def make_plan(a, episode_id, *, mode="full", values=(18, 45),
              phase_offset=0, spacing_periods=3, first_round=None):
    """Freeze a complete schedule before observing its future outputs.

    phase_offset 0 is the historical comparator cadence; 1 and 3 are declared
    phase challenges, not fitted rescue windows. The B operand reference was
    acquired historically, not presented again. Values 18/45 straddle the
    documented reference36. Values50/82, if requested, are not opposite classes.
    """
    if mode not in MODES:
        raise ValueError("Unsupported social mode")
    if int(a.world.runtime.dimension) != 67 or not hasattr(a, "transferred_quantity"):
        raise ValueError("Requires existing N67 owner with transferred B comparator")
    if not isinstance(episode_id, str) or not episode_id or any(
            c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-" for c in episode_id):
        raise ValueError("Explicit ASCII episode identity required")
    if type(phase_offset) is not int or phase_offset not in (0, 1, 3):
        raise ValueError("Predeclared phase offsets are 0,1,3 only")
    if type(spacing_periods) is not int or spacing_periods < 2:
        raise ValueError("At least two periods avoid overlap of the fixed78-tick return")
    values = list(values)
    if not values or any(type(v) is not int or not 0 <= v <= 19600 for v in values):
        raise ValueError("Exact private material quantities required")
    banks = deepcopy(a.geometry["cpc9_return"]["banks"])
    if {b["id"] for b in banks} != {"minus", "plus"}:
        raise ValueError("Both pre-existing return banks are required")
    available = _ports(a)
    required = ["B.quantity.object.cue", "B.quantity.object.resource", "B.quantity.reader"]
    required += ["back." + b["id"] + "." + role for b in banks
                 for role in ("record", "read", "use")]
    if any(name not in available for name in required):
        raise ValueError("Pre-existing private-B/return interface is missing")
    # object input=142+67*k+offset; read=146+67*k+offset;
    # B output=147+67*k+offset, matching the existing reference_time77.
    minimum_round = max(0, (int(a.tick) - 142 - phase_offset) // 67 + 1)
    first_round = minimum_round if first_round is None else first_round
    if type(first_round) is not int or first_round < minimum_round:
        raise ValueError("Plan cannot submit retrospective inputs")
    trials = []
    for index, value in enumerate(values):
        round_index = first_round + index * spacing_periods
        source = 147 + 67 * round_index + phase_offset
        inputs = []
        if mode != "no_partner":
            inputs += [{"port": "B.quantity.object.cue", "payload": 5, "tick": source - 5,
                        "kind": "experience", "role": "PRIVATE_B_CURRENT_OBJECT_FORMAT"},
                       {"port": "B.quantity.object.resource", "payload": value, "tick": source - 5,
                        "kind": "experience", "role": "PRIVATE_B_CURRENT_OBJECT_MATERIAL"},
                       {"port": "B.quantity.reader", "payload": 7, "tick": source - 1,
                        "kind": "probe", "role": "FIXED_B_CURRENT_USE_OPPORTUNITY"}]
        for bank in banks:
            prefix = "back." + bank["id"] + "."
            inputs += [{"port": prefix + "record", "payload": 5,
                        "tick": source - 1 + int(mode == "unpaired_message"),
                        "kind": "experience", "role": "E1_GENERIC_ASSOCIATION_RESOURCE_BOTH_BANKS"},
                       {"port": prefix + "read", "payload": 7, "tick": source + 66,
                        "kind": "probe", "role": "E1_COMMON_LATER_READER_BOTH_BANKS"},
                       {"port": prefix + "use", "payload": 13, "tick": source + 71,
                        "kind": "experience", "role": "E1_COMMON_CURRENT_ACTION_RESOURCE_BOTH_BANKS"}]
        interceptors = []
        if mode in ("message_cut", "message_sham"):
            for bank in banks:
                site = list(bank["message_site"])
                if mode == "message_sham":
                    site = [site[0], (site[1] + 9) % 67, (site[2] + 7) % 67]
                interceptors.append({"port": "HABITAT.social." + episode_id + ".t" + str(index) + "." + bank["id"],
                                     "site": site, "payload": 0, "tick": source,
                                     "semantic": 4, "state": 1, "direction": [0, 0, 0]})
        trials.append({"index": index, "private_object_value": value,
                       "round_index": round_index, "B_source_tick": source,
                       "inputs": sorted(inputs, key=lambda e: (e["tick"], e["port"])),
                       "interceptors": interceptors,
                       "boundaries": [{"tick": source - 1, "stage": "before_B_reader"},
                                      {"tick": source, "stage": "B_source_formed_before_cut"},
                                      {"tick": source + 1, "stage": "message_at_one_step"},
                                      {"tick": source + 2, "stage": "E1_record_arrival"},
                                      {"tick": source + 3, "stage": "after_record"},
                                      {"tick": source + 69, "stage": "E1_later_read"},
                                      {"tick": source + 74, "stage": "E1_current_use"},
                                      {"tick": source + 78, "stage": "E1_delivery"}],
                       "end_tick": source + 78})
    plan = {"schema": "DCS1.1.habitat.private_B.frozen_plan.v1", "episode_id": episode_id,
            "mode": mode, "N": 67, "created_tick": int(a.tick), "phase_offset": phase_offset,
            "spacing_periods": spacing_periods, "values": values, "trials": trials,
            "B_center": list(a.transferred_quantity.geometry["center"]),
            "B_reference_site": list(a.transferred_quantity.geometry["reference_site"]),
            "B_object_site": list(a.transferred_quantity.geometry["object_site"]),
            "E1_banks": banks,
            "host_information": "Private object magnitude is sent only to B object input; E1 receives no correct relation, label or selected bank.",
            "no_partner_scope": "Withhold B current object and reader participation. Existing B matter is NOT removed; this is not absence of the physical body.",
            "cut_scope": "Both one-step message sites receive the same fixed interceptor only AFTER B output is formed and recorded. Nearby prepared matter can also change later B evolution; compare source frames and sham, not just final answer.",
            "state_zero_contract": "RAW==0 required at interceptor admission boundary; state==0 with residual RAW is not treated as vacant.",
            "not_claimed": ["communication success", "autonomous interlocutor selection", "negotiation", "new Spanish meaning", "learned comparison operation"]}
    plan["plan_sha256"] = sha256(canonical(plan)).hexdigest()
    return plan


def schedule(a, plan):
    original = deepcopy(plan)
    expected = original.pop("plan_sha256")
    if sha256(canonical(original)).hexdigest() != expected:
        raise ValueError("Frozen social plan changed")
    if int(a.tick) != plan["created_tick"]:
        raise ValueError("Plan belongs to a different starting boundary")
    state = _state(a)
    episode_id = plan["episode_id"]
    if episode_id in state["episodes"]:
        raise ValueError("Episode already registered; continue it, never reset it")
    record = {"plan": deepcopy(plan), "requests": [], "captures": [],
              "interceptions": [], "last_tick": int(a.tick), "status": "SCHEDULED"}
    # Registration adds interfaces only; it inserts no RAW or clocks.
    for trial in plan["trials"]:
        for cut in trial["interceptors"]:
            _declare_interceptor(a, cut["port"], cut["site"])
        for event in trial["inputs"]:
            receipt = (a.world.probe if event["kind"] == "probe" else a.world.submit)(
                event["port"], event["payload"], event["tick"])
            record["requests"].append({**deepcopy(event), "id": int(receipt.id),
                                        "initial_receipt": exact_receipt(receipt)})
    state["episodes"][episode_id] = record
    _store(a, state)
    return deepcopy(record)


def _capture(a, plan, trial, boundary):
    result = {"trial": trial["index"], **boundary,
              "B_center": observe(a, plan["B_center"]),
              "B_reference": observe(a, plan["B_reference_site"]),
              "B_object": observe(a, plan["B_object_site"]), "E1": []}
    for bank in plan["E1_banks"]:
        result["E1"].append({"bank": bank["id"], **{
            name: observe(a, bank[name]) for name in ("message_site", "hub", "use_site", "delivery_site")}})
    return result


def advance(a, episode_id, *, through_tick=None):
    """Advance through the owner, preserving queues and resumable protocol state."""
    state = _state(a)
    record = state["episodes"][episode_id]
    plan = record["plan"]
    if int(a.tick) < record["last_tick"]:
        raise ValueError("Cannot rewind a social episode")
    end = plan["trials"][-1]["end_tick"]
    target = end if through_tick is None else through_tick
    if type(target) is not int or not int(a.tick) <= target <= end:
        raise ValueError("Requested boundary outside this finite protocol")
    completed = {(c["trial"], c["stage"]) for c in record["captures"]}
    for trial in plan["trials"]:
        for boundary in trial["boundaries"]:
            key = (trial["index"], boundary["stage"])
            if key in completed or boundary["tick"] > target:
                continue
            if boundary["tick"] < int(a.tick):
                raise ValueError("Owner advanced past an uncaptured protocol boundary")
            a.run_until(boundary["tick"])
            record["captures"].append(_capture(a, plan, trial, boundary))
            if boundary["stage"] == "B_source_formed_before_cut" and trial["interceptors"]:
                before = [{**deepcopy(c), "pre_admission": observe(a, c["site"])}
                          for c in trial["interceptors"]]
                # Fixed both-bank intervention; no selection by B's answer.
                # If either site is not truly empty the whole cut is unsupported.
                vacant = all(int(c["pre_admission"]["raw"]) == 0 for c in before)
                intervention = {"trial": trial["index"], "tick": int(a.tick),
                                "status": "SUBMITTED_FIXED_BOTH_BANKS" if vacant else "UNSUPPORTED_OCCUPIED_FIXED_SITE",
                                "sites": before, "requests": [], "does_not_overwrite": True}
                if vacant:
                    for cut in trial["interceptors"]:
                        r = a.world.submit(cut["port"], 0, cut["tick"])
                        intervention["requests"].append({**deepcopy(cut), "id": int(r.id),
                                                         "initial_receipt": exact_receipt(r)})
                record["interceptions"].append(intervention)
            record["last_tick"] = int(a.tick)
            # Save progress before any later owner advance; the caller saves the
            # complete native world through its existing Store after return.
            _store(a, state)
    if int(a.tick) < target:
        a.run_until(target)
    record["last_tick"] = int(a.tick)
    record["status"] = "COMPLETED_FIXED_HORIZON" if int(a.tick) == end else "IN_PROGRESS"
    for request in record["requests"]:
        request["receipt"] = exact_receipt(a.world.runtime.receipt(request["id"]))
    for intervention in record["interceptions"]:
        for request in intervention["requests"]:
            request["receipt"] = exact_receipt(a.world.runtime.receipt(request["id"]))
    _store(a, state)
    return deepcopy(record)


def run(a, plan):
    schedule(a, plan)
    return advance(a, plan["episode_id"])


def planned_variants(a, prefix="HAB_BPRIVATE"):
    """Prospective alternatives, not trials executed or independent replicas."""
    return [make_plan(a, prefix + "." + mode + ".p" + str(offset), mode=mode,
                      values=(18, 45), phase_offset=offset)
            for offset in (0, 1, 3) for mode in MODES]

