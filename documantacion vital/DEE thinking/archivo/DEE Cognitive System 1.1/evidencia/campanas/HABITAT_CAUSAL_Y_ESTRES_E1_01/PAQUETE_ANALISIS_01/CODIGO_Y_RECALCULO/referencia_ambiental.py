"""Prospective native addition to an existing E1 acquired reference.

No world load/fork/advance, no memory editing, no calculation of an action or
comparison target. Addition is environmental material, not a reference setter.
"""
from copy import deepcopy
from hashlib import sha256
import json

from dee_thinking.consolidated import exact_receipt


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf8")


def plan(a, episode_id, *, actual_addition=11, mode="paired", lead=5):
    if int(a.world.runtime.dimension) != 67 or not hasattr(a, "quantity"):
        raise ValueError("Existing N67 E1 quantity component required")
    if type(actual_addition) is not int or not 0 <= actual_addition <= 19600:
        raise ValueError("Actual material addition must be a legal exact integer")
    if type(lead) is not int or lead < 5:
        raise ValueError("Leave at least five ticks for the prospective schedule")
    if mode not in ("paired", "no_cue", "unpaired", "offpath", "no_addition"):
        raise ValueError("Declared finite intervention mode required")
    tick = ((int(a.tick) + lead + 66) // 67) * 67
    events = []
    prefix = "quantity.other." if mode == "offpath" else "quantity.reference."
    if mode != "no_cue":
        events.append({"port": prefix + "cue", "payload": 0,
                       "tick": tick + int(mode == "unpaired"), "kind": "experience"})
    if mode != "no_addition":
        events.append({"port": prefix + ("event" if mode == "offpath" else "resource"),
                       "payload": actual_addition, "tick": tick, "kind": "experience"})
    by_name = {p.name: p for p in a.world.interfaces}
    if any(event["port"] not in by_name for event in events):
        raise ValueError("Existing reference/auxiliary interfaces required")
    result = {"schema": "DCS1.1.habitat.native_reference_addition.v1",
              "episode_id": episode_id, "created_tick": int(a.tick),
              "mode": mode, "actual_addition": actual_addition,
              "reference_input_tick": tick, "events": events,
              "suggested_passive_boundaries": [tick - 1, tick, tick + 1, tick + 2,
                                                tick + 3, tick + 4, tick + 67, tick + 70],
              "reference_hub": list(a.quantity.geometry["reference_hub"]),
              "reference_site": list(a.quantity.geometry["reference_site"]),
              "comparison_center": list(a.quantity.geometry["center"]),
              "attribution": "Native additional resource experience under prepared phase and geometry; no promise that the current changed landscape retains the historical sum mechanism.",
              "not_a_setter": "Do not interpret actual_addition Q as replacing the previous reference by Q. Earlier valid experiment used addition11 and cue0 to change67 to78.",
              "controls": {"paired": "Zero-load physical cue plus actual addition, phase0.",
                           "no_cue": "Same additional material, no zero-load cue; state-carrying cue omission is a real structural intervention.",
                           "unpaired": "Same quantity and zero-load cue, cue delayed one tick; fixed phase challenge, not a target correction.",
                           "offpath": "Same zero cue and quantity, existing auxiliary cue/event ports, not the acquired reference route.",
                           "no_addition": "Zero cue only; omits extra resource and changes total material dose."}}
    result["plan_sha256"] = sha256(canonical(result)).hexdigest()
    return result


def schedule(a, frozen_plan):
    copy = deepcopy(frozen_plan)
    expected = copy.pop("plan_sha256")
    if sha256(canonical(copy)).hexdigest() != expected:
        raise ValueError("Reference-addition plan changed")
    if int(a.tick) != frozen_plan["created_tick"]:
        raise ValueError("Reference plan starting tick differs")
    # QuantitySession.input appends the real request and receipt identity to its
    # operative child state; the existing owner saver preserves that state.
    requests = []
    for event in frozen_plan["events"]:
        receipt = a.quantity.input(event["port"], event["payload"], event["tick"])
        requests.append({**deepcopy(event), "initial_receipt": receipt})
    return {"plan": deepcopy(frozen_plan), "requests": requests,
            "native_ticks_advanced_by_this_function": 0,
            "continuation": "Advance only through the existing owner a.run_until and save through the existing Store; evaluate later comparison inputs identically in all arms."}

