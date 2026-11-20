"""A second content domain after two task-profile forms, same native MAIN.

ARRIBA/DEBAJO are explicitly restricted to the sign of a current packet's dz
in this declared lattice frame.  This is neither gravity nor the general human
semantics of ABOVE/BELOW.  A fixed external sensor provides the actual sign;
the learned form relation and subsequent response remain physical v27 events.
"""
from pathlib import Path
import json
import time
from .protocol import observe, digest, until, receipt, put

FORMS = {"L3": "ARRIBA", "L4": "DEBAJO"}
KEY = "cpc4.extension02.direction_forms.neutral.v1"


def run(network, case, output):
    output = Path(output); output.mkdir(parents=True, exist_ok=True); started = time.monotonic()
    base = network.world.runtime.current_tick
    if base not in (529, 1529): raise ValueError("Continue the actual two-form MAIN after both queries")
    if network.world.runtime.paused: raise ValueError("Paused MAIN")
    source = case.get("source", "D"); payload = case.get("source_payload", 13)
    order = case.get("word_order", ["L3", "L4"]); mode = case.get("teaching", "paired")
    if source not in ("C", "D") or type(payload) is not int or not 1 <= payload <= 65535: raise ValueError("Declared physical source required")
    if sorted(order) != ["L3", "L4"] or mode not in ("paired", "unpaired", "signal_omitted", "report_omitted"): raise ValueError("Finite form protocol required")
    initial = digest(network.world); calls = []; experiences = []; reads = []; old_probes = []
    network.save(output / f"SAME_MAIN_BEFORE_DIRECTION_FORMS{base}.deetsnap")
    # All stimuli are external experiences. No output, class or alias is copied
    # to the physical state; the sign is sampled only after native propagation.
    events = {}
    for slot, sign in enumerate((1, -1)):
        trigger = base + 4 + 28 * slot
        events[trigger] = ("stimulus", slot, sign)
        events[trigger + 3] = ("teach", slot, sign)
        events[trigger + 6] = ("after_teach", slot, sign)
        query = trigger + 70
        events[query] = ("query", slot, sign)
        events[query + 3] = ("read", slot, sign)
    if case.get("old_retention_panel", True):
        events[base + 36] = ("old_query", "L1", None)
        events[base + 39] = ("old_read", "L1", None)
        events[base + 64] = ("old_query", "L2", None)
        events[base + 67] = ("old_read", "L2", None)
    pending_queries = {}; pending_old = {}; stimuli = {}
    def commit(phase):
        network.world.runtime.set_snapshot_metadata(KEY, json.dumps({"version": 1, "base_tick": base,
            "tick": network.world.runtime.current_tick, "phase": phase, "form_identities": FORMS,
            "source_port": source, "source_payload": payload, "word_order": order,
            "call_ids": [x["id"] for x in calls], "scope": "Progress only; no stored answers or form-to-class map"}, separators=(",", ":")))
    for tick, (kind, slot, sign) in sorted(events.items()):
        until(network, tick)
        if kind == "stimulus":
            port = source + ".report." + ("plus" if sign == 1 else "minus")
            rr = network.world.submit(port, payload, tick)
            stimuli[slot] = rr.id
            calls.append({"id": rr.id, "channel": port, "load": payload, "requested_tick": tick,
                          "call_tick": tick, "modality": "EXPERIENCE_PROTOCOL"})
        elif kind == "teach":
            actual = observe(network.world, network.spec["centers"][source])
            source_receipt = receipt(network.world, stimuli[slot])
            observed_sign = actual["direction"][2] if (actual["active"] and actual["semantic"] == 1
                              and actual["direction"][2] in (-1, 1) and source_receipt["status"] == "applied") else None
            ids = []
            if observed_sign is not None:
                if mode != "report_omitted":
                    suffix = "plus" if observed_sign == 1 else "minus"
                    for lane in network.spec["lexical_hubs"]:
                        rr = network.world.submit(f"lex.{lane}.report.{suffix}", 11, tick); ids.append(rr.id)
                        calls.append({"id": rr.id, "channel": f"lex.{lane}.report.{suffix}", "load": 11,
                                      "requested_tick": tick, "call_tick": tick, "modality": "EXPERIENCE_PROTOCOL"})
                if mode != "signal_omitted":
                    at = tick + (mode == "unpaired"); rr = network.world.submit(f"lex.{order[slot]}.signal", 5, at); ids.append(rr.id)
                    calls.append({"id": rr.id, "channel": f"lex.{order[slot]}.signal", "load": 5,
                                  "requested_tick": at, "call_tick": tick, "modality": "EXPERIENCE_PROTOCOL"})
            experiences.append({"tick": tick, "form": order[slot], "external_form": FORMS[order[slot]],
                                "actual_source": actual, "observed_sign": observed_sign, "receipt_ids": ids,
                                "source_receipt": source_receipt,
                                "sensor_modality": "EXTERNAL_CURRENT_DZ_TRANSDUCER", "status": "PRESENTED" if observed_sign else "NO_CURRENT_DIRECTION_CLASS"})
        elif kind == "after_teach":
            experiences[slot]["actual_hubs"] = {lane: observe(network.world, hub) for lane, hub in network.spec["lexical_hubs"].items()}
            experiences[slot]["receipts"] = [receipt(network.world, i) for i in experiences[slot]["receipt_ids"]]
            commit(kind); network.save(output / f"AFTER_DIRECTION_EXPERIENCE{tick}.deetsnap")
        elif kind == "query":
            rr = network.world.probe(f"lex.{order[slot]}.signal", 5, tick); pending_queries[slot] = rr.id
            calls.append({"id": rr.id, "channel": f"lex.{order[slot]}.signal", "load": 5, "requested_tick": tick,
                          "call_tick": tick, "modality": "PHYSICAL_PROBE"})
        elif kind == "read":
            actual = observe(network.world, network.spec["lexical_hubs"][order[slot]]); rr = receipt(network.world, pending_queries[slot])
            valid = (rr["status"] == "applied" and actual["active"] and actual["semantic"] == 1
                     and actual["s_reg"] == 21 and actual["direction"] in ([-1, 1, 0], [-1, -1, 0]))
            reads.append({"tick": tick, "form": order[slot], "external_form": FORMS[order[slot]], "physical": actual,
                          "receipt": rr, "valid": bool(valid), "class_sign": actual["direction"][1] if valid else None,
                          "scope": "Readout y sign reports the acquired external dz class, not geometric y=above"})
            commit(kind); network.save(output / f"DIRECTION_READ{tick}.deetsnap")
        elif kind == "old_query":
            rr = network.world.probe(f"lex.{slot}.signal", 5, tick); pending_old[slot] = rr.id
            calls.append({"id": rr.id, "channel": f"lex.{slot}.signal", "load": 5, "requested_tick": tick,
                          "call_tick": tick, "modality": "PHYSICAL_RETENTION_PROBE"})
        elif kind == "old_read":
            actual = observe(network.world, network.spec["lexical_hubs"][slot]); rr = receipt(network.world, pending_old[slot])
            possible = (rr["status"] == "applied" and actual["active"] and actual["semantic"] == 1 and actual["s_reg"] == 26
                        and actual["direction"] in ([-1, 1, 0], [-1, -1, 0]))
            old_probes.append({"tick": tick, "form": slot, "receipt": rr, "actual": actual,
                               "participation26_diagonal": bool(possible), "scope": "A common additional physical probe, not a claim of unique ancestry"})
        commit(kind)
        put(output / "INCREMENTAL.json", {"experiences": experiences, "readouts": reads, "old_retention_panel": old_probes})
    commit("COMPLETE_FINITE_DOMAIN"); network.save(output / f"MAIN_FINAL{network.world.runtime.current_tick}.deetsnap")
    result = {"case": case, "initial": initial, "final": digest(network.world), "experiences": experiences,
              "readouts": reads, "old_retention_panel": old_probes, "calls": calls,
              "receipts": [receipt(network.world, x["id"]) for x in calls], "host_raw_clock_edits": [],
              "elapsed_seconds": time.monotonic() - started,
              "scope": "New direction-content associations on the same post-profile native world. ABOVE/BELOW are restricted aliases for dz in one lattice frame; no gravity, general spatial semantics or four simultaneous retained meanings is asserted."}
    put(output / "MEASUREMENTS.json", result); return network, result
