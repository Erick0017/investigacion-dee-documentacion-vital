"""CPC5 bounded physical lexical acquisition and longitudinal access.

No expected response is used by prepare, experience, or query.  Eight opaque
forms designate eight fixed physical ports; a paired environmental carrier
provides direction.  The persistent v27 carrier is the only learned state.
This apparatus is a component repertoire, not eight full NSM meanings.
"""
from __future__ import annotations

from array import array
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time

N = 67
KEY = "cpc5.lexical.neutral.v1"
WHEEL_SHA = "17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623"
NATIVE_SHA = "20d7c764dbc22d1f110ba255f92073b4f64c744c91f6980335a4e08dd61fe066"


def put(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1048576), b""): h.update(b)
    return h.hexdigest()


def identity():
    import dee_thinking as d
    actual = {"version": d.__version__, "kernel": d.kernel_identity()["kernel_version"],
              "module": d.__file__, "python": sys.executable,
              "native_sha256": sha(d._native.__file__)}
    if actual["version"] != "4.0.0" or actual["kernel"] != 27 or actual["native_sha256"] != NATIVE_SHA:
        raise RuntimeError("Frozen official DEE4/v27 required")
    return actual


def moved(site, direction, count=1, translation=(0, 0, 0)):
    return tuple((site[i] + count * direction[i] + translation[i]) % N for i in range(3))


def interface(name, site, direction):
    import dee_thinking as d
    ch = d.ChannelSpec(); ch.name = name; ch.injection_site = d.Coordinate(*site)
    ch.direction = d.Direction(*direction); ch.state = 1; ch.semantic = 1
    ch.allow_experience = True; ch.allow_probe = True
    item = d.InterfaceSpec(); item.name = name; item.channel = ch
    return item


def record(world, site):
    import dee_thinking as d
    o = world.runtime.observe(d.Coordinate(*site)); r = o.record
    return {"tick": int(o.tick), "site": list(site), "raw": str(o.raw), "clock": str(o.clock),
            "state": r.state, "semantic": r.semantic, "s_reg": r.s_reg,
            "direction": [r.dx, r.dy, r.dz], "active": bool(r.state > 0 and r.semantic != 5)}


def digest(world):
    rt = world.runtime
    return {"tick": int(rt.current_tick), "raw_sha256": hashlib.sha256(array("Q", rt.raw_copy()).tobytes()).hexdigest(),
            "clock_sha256": hashlib.sha256(array("Q", rt.clock_copy()).tobytes()).hexdigest(),
            "channel_names": list(rt.channel_names),
            "receipts": [{"id": int(x.id), "status": str(x.status), "requested_tick": int(x.requested_tick),
                          "effective_tick": None if x.effective_tick is None else int(x.effective_tick), "kind": str(x.kind), "reason": x.reason} for x in rt.receipts]}


def receipt(world, identifier):
    r = world.runtime.receipt(identifier)
    return {"id": int(r.id), "status": str(r.status), "requested_tick": int(r.requested_tick),
            "effective_tick": None if r.effective_tick is None else int(r.effective_tick), "kind": str(r.kind), "channels": list(r.channels), "reason": r.reason}


def until(world, tick):
    if world.runtime.paused: raise ValueError("Paused trajectory")
    world.run_until(tick)
    if world.runtime.current_tick != tick: raise RuntimeError("Actual boundary not reached")


def prepare(case):
    import dee_thinking as d
    translation = tuple(case.get("translation", [0, 0, 0]))
    hubs = {f"L{i+1}": moved((30, 30, 4+8*i), (0, 0, 0), translation=translation) for i in range(8)}
    ports = []
    for name, hub in hubs.items():
        ports.append(interface(name+".signal", moved(hub, (-1, 0, 0), -3), (-1, 0, 0)))
        for sign, label in ((1, "plus"), (-1, "minus")):
            direction = (1, sign, 0)
            ports.append(interface(name+".event."+label, moved(hub, direction, -3), direction))
    recipe = d.OrganizationRecipe.research(N, [], 0); recipe.interfaces = ports
    recipe.execution = d.TickOptions(d.Backend.LAZY, 1)
    return d.OrganizationalWorld.create(recipe), {"N": N, "hubs": hubs, "translation": translation,
            "preinstalled_material_sites": 0, "ports": [p.name for p in ports],
            "physical_recipes": {"signal_direction": [-1, 0, 0], "event_directions": [[1, 1, 0], [1, -1, 0]],
                                 "source_distance": 3, "state": 1, "semantic": 1}}


def observe_panel(world, spec):
    return {name: record(world, hub) for name, hub in spec["hubs"].items()}


class LexicalSession:
    """Coordinate-free public finite apparatus; phase is explicit, not reset.

    Metadata contains geometry and protocol timing only.  In particular it
    contains no sign/class/word-to-response mapping.  The decoder samples RAW.
    """
    SESSION_KEY = "cpc5.lexical.public_session.v1"

    def __init__(self, world, spec, phases=None):
        self.world = world; self.spec = spec; self.phases = dict(phases or {})

    @classmethod
    def create(cls, translation=(0,0,0)):
        identity(); world, spec = prepare({"translation": list(translation)})
        return cls(world, spec)

    @property
    def tick(self): return int(self.world.runtime.current_tick)

    def observe(self, form=None):
        if form is None: return observe_panel(self.world, self.spec)
        if form not in self.spec["hubs"]: raise ValueError("Fixed form L1..L8 required")
        return record(self.world, self.spec["hubs"][form])

    def advance(self, ticks):
        if type(ticks) is not int or ticks < 0: raise ValueError("Nonnegative integer ticks required")
        until(self.world, self.tick+ticks)

    def experience(self, form, physical_direction, tick=None, mode="paired"):
        if form not in self.spec["hubs"] or form in self.phases: raise ValueError("New fixed form L1..L8 required")
        if physical_direction not in (-1,1) or type(physical_direction) is not int: raise ValueError("Physical direction must be -1 or+1")
        if mode not in ("paired", "unpaired", "signal_omitted", "report_omitted"): raise ValueError("Unknown finite experience protocol")
        at = self.tick if tick is None else tick
        if type(at) is not int or at < self.tick: raise ValueError("Present/future absolute tick required")
        until(self.world, at); ids=[]
        if mode != "report_omitted":
            ids.append(self.world.submit(form+".event."+("plus" if physical_direction==1 else "minus"),11,at).id)
        if mode != "signal_omitted":
            ids.append(self.world.submit(form+".signal",5,at+(mode=="unpaired")).id)
        self.phases[form] = at % N
        until(self.world, at+3+(mode=="unpaired"))
        return {"kind":"EXPERIENCE_PROTOCOL", "form":form, "event_direction":physical_direction,
                "readout":self.observe(form), "receipts":[receipt(self.world,x) for x in ids]}

    def query(self, form, payload=5):
        if form not in self.phases: raise ValueError("A prior presented experience is required; no response is assumed")
        if type(payload) is not int or not 0<=payload<=65535: raise ValueError("uint16 query payload required")
        at=self.tick+(self.phases[form]-self.tick)%N
        # Timing follows the declared toroidal return; it never uses the
        # acquired sign or an expected answer.  The delay is returned openly.
        before=self.tick; until(self.world,at)
        identifier=self.world.probe(form+".signal",payload,at).id; until(self.world,at+3)
        actual=self.observe(form); rr=receipt(self.world,identifier)
        valid=bool(rr["status"]=="applied" and actual["active"] and actual["semantic"]==1
                   and actual["s_reg"]>payload and actual["direction"] in ([-1,1,0],[-1,-1,0]))
        return {"form":form,"tick_before":before,"input_tick":at,"tick":self.tick,"phase_wait_ticks":at-before,
                "physical":actual,"receipt":rr,"decoder_valid":valid,
                "decoded_direction":actual["direction"][1] if valid else None,"origin":"ENTE"}

    def save(self,path):
        value={"schema":1,"geometry":self.spec,"port_phase_residues":self.phases,"tick":self.tick,
               "scope":"No acquired direction map; phases refer to supplied input timing only"}
        self.world.runtime.set_snapshot_metadata(self.SESSION_KEY,json.dumps(value,separators=(",",":")))
        self.world.save_snapshot(str(path))

    @classmethod
    def load(cls,path):
        import dee_thinking as d
        identity(); world=d.OrganizationalWorld.load_snapshot(str(path))
        text=world.runtime.snapshot_metadata(cls.SESSION_KEY)
        if not text: raise ValueError("Public lexical session metadata absent")
        value=json.loads(text)
        if value.get("schema")!=1 or world.runtime.dimension!=N or value["tick"]!=world.runtime.current_tick:
            raise ValueError("Foreign or inconsistent lexical session")
        phases=value["port_phase_residues"]
        if any(k not in value["geometry"]["hubs"] or type(v) is not int or not 0<=v<N for k,v in phases.items()):
            raise ValueError("Malformed phase timing")
        if set(world.runtime.channel_names)!=set(value["geometry"]["ports"]): raise ValueError("Interfaces not preserved")
        return cls(world,value["geometry"],phases)


def run_case(case, output):
    """One new physical MAIN, staggered acquisition, three same-main queries.

    case contains environmental experiences, not decoded targets.  Evaluator
    calculations are performed afterwards from observed training directions.
    """
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic(); engine = identity(); world, spec = prepare(case)
    if Path(__file__).resolve() != (output/"EXECUTED_SOURCE.py").resolve():
        shutil.copyfile(__file__, output/"EXECUTED_SOURCE.py")
    lesson_order = case.get("lesson_order", [f"L{i+1}" for i in range(8)])
    if sorted(lesson_order) != [f"L{i+1}" for i in range(8)]: raise ValueError("Permutation of eight fixed forms required")
    signs = case.get("event_directions", [1, -1, -1, 1, -1, 1, 1, -1])
    if len(signs) != 8 or any(x not in (-1, 1) for x in signs): raise ValueError("Eight physical event directions required")
    mode = case.get("mode", "paired")
    if mode not in ("paired", "unpaired", "signal_omitted", "report_omitted", "event_order"):
        raise ValueError("Unknown finite exposure protocol")
    calls = []; snapshots = []; lessons = []; reads = []; windows = []
    config = {"schema": "CPC5.lexical_case.v1", "case": case, "geometry": spec, "engine": engine,
              "criterion_frozen": {"acquired_direction": "actual trained carrier y; no word-to-answer decoder",
                "retained": "Applied query; actual load greater than query; actual direction[-1,sign,0]",
                "horizon": 260, "scope": "8 opaque directional correspondences in separated lanes; not8NSM semantics"},
              "source_sha256": sha(__file__)}
    put(output/"CONFIG.json", config)
    def save(label):
        name = f"{label}.deetsnap"; world.save_snapshot(str(output/name)); snapshots.append({"file": name, "sha256": sha(output/name), "state": digest(world)})
    def submit(name, payload, tick, kind, origin):
        r = getattr(world, kind)(name, payload, tick)
        calls.append({"id": int(r.id), "origin": origin, "port": name, "tick_requested": tick,
                      "payload": payload, "call_tick": int(world.runtime.current_tick),
                      "modality": "PHYSICAL_PROBE" if kind == "probe" else "EXPERIENCE_PROTOCOL"})
        return r.id
    def neutral(phase):
        world.runtime.set_snapshot_metadata(KEY, json.dumps({"schema": 1, "phase": phase,
            "case_id": case["id"], "geometry": spec, "call_ids": [x["id"] for x in calls],
            "tick": int(world.runtime.current_tick), "scope": "No answer map; fixed port identities only"}, separators=(",", ":")))
    neutral("INITIAL"); save("INITIAL_T0")
    pending = {}
    events = {}
    for slot, form in enumerate(lesson_order):
        base = 8*slot
        events[base] = ("teach", form, slot, 0)
        events[base+3+(mode=="unpaired")] = ("learn_read", form, slot, 0)
        for cycle in (1, 2, 3):
            at = base+N*cycle+case.get("query_phase_offset", 0)
            events[at] = ("query", form, slot, cycle)
            events[at+3] = ("query_read", form, slot, cycle)
    for tick, (kind, form, slot, cycle) in sorted(events.items()):
        until(world, tick)
        if kind == "teach":
            sign = signs[slot]; ids = []
            if mode != "report_omitted":
                ids.append(submit(form+".event."+("plus" if sign==1 else "minus"), 11, tick, "submit", "ENVIRONMENTAL_DIRECTION_EVENT"))
            if mode != "signal_omitted":
                ids.append(submit(form+".signal", 5, tick+(mode=="unpaired"), "submit", "OPAQUE_SYMBOL_EXPOSURE"))
            if mode == "event_order":
                ids.append(submit(form+".event."+("minus" if sign==1 else "plus"), 11,
                                  tick+case.get("second_event_gap",1), "submit", "SECOND_OPPOSED_DIRECTION_EVENT"))
            pending[("teach", form)] = ids
            lessons.append({"slot": slot, "form": form, "tick": tick, "direction_event": sign,
                            "port_event": form+".event."+("plus" if sign==1 else "minus"),
                            "mode": mode, "hubs_before": observe_panel(world, spec),
                            "note": "Physical environmental direction supplied by declared experience, not semantic target"})
        elif kind == "learn_read":
            lessons[slot]["physical_after"] = record(world, spec["hubs"][form])
            lessons[slot]["receipts"] = [receipt(world, x) for x in pending[("teach", form)]]
            neutral("ACQUISITION_"+str(slot+1))
            if slot in (0, 3, 7): save("AFTER_ACQUISITION"+str(slot+1)+"_T"+str(tick))
        elif kind == "query":
            if form == lesson_order[0]:
                neutral("BEFORE_QUERY_CYCLE"+str(cycle)); save("BEFORE_QUERY_CYCLE"+str(cycle)+"_T"+str(tick))
            payload = case.get("query_payloads", [5, 5, 5])[cycle-1]
            pending[("query", form, cycle)] = submit(form+".signal", payload, tick, "probe", "COMMON_QUERY_NO_ENVIRONMENTAL_REPORT")
            windows.append({"tick": tick, "kind": "PRE_QUERY", "form": form, "cycle": cycle,
                            "center": record(world, spec["hubs"][form]),
                            "source": record(world, moved(spec["hubs"][form], (-1, 0, 0), -3))})
        else:
            rr = receipt(world, pending[("query", form, cycle)])
            actual = record(world, spec["hubs"][form]); payload = case.get("query_payloads", [5,5,5])[cycle-1]
            # Fixed decoder uses the current physical carrier only.  No lookup
            # of training sign, case ID, requested answer, or previous output.
            valid = bool(rr["status"] == "applied" and actual["active"] and actual["semantic"] == 1
                         and actual["s_reg"] > payload and actual["direction"] in ([-1,1,0],[-1,-1,0]))
            reads.append({"form": form, "slot": slot, "cycle": cycle, "tick": tick,
                          "physical": actual, "receipt": rr, "admitted": rr["status"] == "applied",
                          "decoder_valid": valid, "decoded_direction": actual["direction"][1] if valid else None,
                          "query_payload": payload, "origin": "ENTE_PHYSICAL_CARRIER",
                          "assessor_relation": "evaluated only after trajectory; not consulted by query"})
            neutral("AFTER_QUERY"); put(output/"INCREMENTAL.json", {"lessons": lessons, "readouts": reads})
    neutral("COMPLETE"); save("MAIN_FINAL_T"+str(world.runtime.current_tick))
    # Calculations are deliberately downstream of all physical evolution.
    learned = {x["form"]: x["physical_after"]["direction"][1] if x["physical_after"]["active"] else None for x in lessons}
    for row in reads:
        row["auditor_matches_training_direction"] = bool(row["decoder_valid"] and learned[row["form"]] == row["decoded_direction"])
    calculations = {str(cycle): {"queries": sum(x["cycle"]==cycle for x in reads),
        "applied": sum(x["cycle"]==cycle and x["admitted"] for x in reads),
        "physically_decoded": sum(x["cycle"]==cycle and x["decoder_valid"] for x in reads),
        "matches_acquired_direction": sum(x["cycle"]==cycle and x["auditor_matches_training_direction"] for x in reads)} for cycle in (1,2,3)}
    result = {"schema": "CPC5.lexical_measurements.v1", "case": case, "engine": engine, "geometry": spec,
        "lessons": lessons, "readouts": reads, "calls": calls,
        "receipts": [receipt(world, x["id"]) for x in calls], "snapshots": snapshots,
        "local_windows": windows, "final": digest(world), "calculations": calculations,
        "host_RAW_writes_after_T0": [], "host_clock_writes_after_T0": [], "operative_forks": 0,
        "new_preparations": 1, "same_RUNTIME": True, "elapsed_seconds": time.monotonic()-started,
        "scope": "Physically accumulated opaque direction associations. All ports/geometry beforeT0. Query changes load and direction. No inference of65human semantic meanings."}
    put(output/"MEASUREMENTS.json", result)
    return result


def main():
    p=argparse.ArgumentParser(); p.add_argument("--case", type=Path, required=True); p.add_argument("--output", type=Path, required=True)
    a=p.parse_args(); result=run_case(json.loads(a.case.read_text(encoding="utf-8-sig")), a.output)
    print(json.dumps({"case":result["case"]["id"],"calculations":result["calculations"],"tick":result["final"]["tick"]}))


if __name__ == "__main__": main()
