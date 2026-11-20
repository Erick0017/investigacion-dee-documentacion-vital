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
    p=argparse.ArgumentParser(); p.add_argument("--case", type=Path); p.add_argument("--output", type=Path, required=True)
    p.add_argument("--technical",action="store_true"); p.add_argument("--continue-public",type=Path)
    p.add_argument("--audit-root",type=Path); p.add_argument("--trace-parent",type=Path)
    a=p.parse_args()
    if a.audit_root:
        print(json.dumps(audit_language(a.audit_root))); return
    if a.trace_parent:
        print(json.dumps(trace_case(a.trace_parent,a.output))); return
    if a.technical:
        result=technical_checks(a.output,a.continue_public)
        print(json.dumps(result)); return
    if a.case is None: p.error("--case required for physical case")
    result=run_case(json.loads(a.case.read_text(encoding="utf-8-sig")), a.output)
    print(json.dumps({"case":result["case"]["id"],"calculations":result["calculations"],"tick":result["final"]["tick"]}))


def local_context(world,hub):
    return {"center":record(world,hub),"neighbors":[record(world,moved(hub,(x,y,z)))
        for x in (-1,0,1) for y in (-1,0,1) for z in (-1,0,1) if (x,y,z)!=(0,0,0)]}


def technical_checks(output,parent=None):
    """Finite public API/save-load; no scientific sample count added."""
    output=Path(output); output.mkdir(parents=True,exist_ok=True)
    if parent is not None:
        session=LexicalSession.load(parent); before=digest(session.world)
        response=session.query("L1",7); session.save(output/"OTHER_PROCESS_CONTINUED.deetsnap")
        result={"kind":"TECHNICAL_OTHER_PROCESS", "before":before,"response":response,"after":digest(session.world),
                "no_external_teaching_map_loaded":True}
        put(output/"TECHNICAL_CONTINUED.json",result); return result
    session=LexicalSession.create(); exposures=[]
    for i in range(8): exposures.append(session.experience("L"+str(i+1),1 if i%2==0 else -1,8*i))
    session.save(output/"PUBLIC_AFTER_EIGHT_EXPERIENCES.deetsnap")
    before=digest(session.world); repeated=[session.observe() for _ in range(3)]
    passive_same=before==digest(session.world)
    responses=[]
    for i in range(8): responses.append(session.query("L"+str(i+1),5))
    session.save(output/"PUBLIC_AFTER_FIRST_PANEL.deetsnap")
    clone=LexicalSession.load(output/"PUBLIC_AFTER_FIRST_PANEL.deetsnap")
    equal_restore=digest(session.world)==digest(clone.world)
    direct=session.query("L1",7); restored=clone.query("L1",7)
    equal_future=digest(session.world)==digest(clone.world)
    result={"kind":"TECHNICAL_PUBLIC_API", "exposures":exposures,"responses":responses,
            "passive_observation_no_mutation":passive_same,"save_load_physical_operative_equal":equal_restore,
            "new_question_after_restore_same_future":equal_future,"direct":direct,"restored":restored,
            "all_eight_physical_first_queries":all(x["decoder_valid"] for x in responses),
            "no_answer_map_in_metadata":True,"public_session_metadata":json.loads(session.world.runtime.snapshot_metadata(LexicalSession.SESSION_KEY))}
    assert passive_same and equal_restore and equal_future and result["all_eight_physical_first_queries"]
    put(output/"TECHNICAL_PUBLIC_API.json",result); return result


def trace_case(parent,output):
    """Forward replay local windows; passive inspector invokes no ablation."""
    import dee_thinking as d
    parent=Path(parent); output=Path(output); output.mkdir(parents=True,exist_ok=True)
    m=json.loads((parent/"MEASUREMENTS.json").read_text(encoding="utf-8")); world=d.OrganizationalWorld.load_snapshot(str(parent/"INITIAL_T0.deetsnap"))
    spec=m["geometry"]; samples=[]; logs=[]; by_call={}
    for call in m["calls"]: by_call.setdefault(call["call_tick"],[]).append(call)
    for tick in range(m["final"]["tick"]+1):
        until(world,tick)
        for call in by_call.get(tick,[]):
            fn=world.probe if call["modality"]=="PHYSICAL_PROBE" else world.submit
            r=fn(call["port"],call["payload"],call["tick_requested"])
            logs.append({"expected_id":call["id"],"actual_id":int(r.id),"same_id":int(r.id)==call["id"]})
        if tick in (0,1,2,3,66,67,68,69,70,71,132,133,134,135,136,137,200,201,202,203,204,205):
            samples.append({"tick":tick,"lane":"L1","context":local_context(world,spec["hubs"]["L1"])})
    actual=digest(world); expected=m["final"]
    physical_equal=all(actual[k]==expected[k] for k in ("tick","raw_sha256","clock_sha256"))
    operational_equal=all(actual[k]==expected[k] for k in ("channel_names","receipts"))
    # Exact sparse observer of all nonzero cells, disaggregated into physical
    # fields. No uint64 is converted to float; inactive records are retained.
    sparse=[]
    for index,raw in enumerate(world.runtime.raw_copy()):
        if raw:
            q=(index//(N*N),(index//N)%N,index%N)
            sparse.append(record(world,q))
    result={"kind":"TECHNICAL_REPLAY_AND_LOCAL_OBSERVER", "parent_case":m["case"]["id"],
            "parent_measurements_sha256":sha(parent/"MEASUREMENTS.json"),"local_windows":samples,
            "replayed_inputs":logs,"physical_equal":physical_equal,"operational_equal":operational_equal,
            "actual":actual,"expected":expected,"sparse_final_nonzero_records":sparse,
            "inactive_orphan_records_preserved":True,"source_sha256":sha(__file__),
            "scope":"Reconstruction of observed transitions and global sparse currentstate, notcounterfactualnecessity oruniquegenealogy"}
    assert physical_equal and operational_equal and all(x["same_id"] for x in logs)
    put(output/"TRACE.json",result)
    return {"physical_equal":physical_equal,"operational_equal":operational_equal,"nonzero_records":len(sparse),"windows":len(samples)}


def audit_language(root):
    root=Path(root); rows=[]
    for path in sorted((root/"resultados").glob("language*/MEASUREMENTS.json")):
        m=json.loads(path.read_text(encoding="utf-8")); rows.append({"id":m["case"]["id"],
            "phase":m["case"].get("phase"),"mode":m["case"].get("mode"),"file":path.relative_to(root).as_posix(),
            "sha256":sha(path),"individual_preparations":1,"same_RUNTIME":m["same_RUNTIME"],
            "queries":len(m["readouts"]),"calculations":m["calculations"],"tick_final":m["final"]["tick"],
            "host_RAW_writes_after_T0":m["host_RAW_writes_after_T0"],"host_clock_writes_after_T0":m["host_clock_writes_after_T0"]})
    data={x["id"]:json.loads((root/x["file"]).read_text(encoding="utf-8")) for x in rows}
    base=data["LANGUAGE_D01_EIGHT_LANES"]; inv=data["LANGUAGE_C01_INVERSE_HISTORY"]
    opposed=[]
    for a,b in zip(base["readouts"],inv["readouts"]):
        opposed.append({"form":a["form"],"cycle":a["cycle"],"same_tick":a["tick"]==b["tick"],
                        "base_physical":a["physical"],"inverse_physical":b["physical"],
                        "opposed_decoded_directions":bool(a["decoder_valid"] and b["decoder_valid"] and a["decoded_direction"]==-b["decoded_direction"])})
    put(root/"resultados/language_SUMMARY.json",{"schema":"CPC5.lexical_audit.v1","cases":rows,
        "complete_physical_trajectories":len(rows),"technical_partial_attempts":["jobs/language_d01","resultados/language_report_omitted"],
        "independent_preparations_not_statistical_replicates":len(rows),"queries_not_independent_worlds":sum(x["queries"] for x in rows),
        "opposed_history_panel":opposed,"same_MAIN_repertoire":8,"direction_content_classes":2,
        "first_query_without_symbol_experience":data["LANGUAGE_C03_NO_SYMBOL_EXPERIENCE"]["calculations"]["1"],
        "later_query_induced_acquisition_without_initial_symbol":data["LANGUAGE_C03_NO_SYMBOL_EXPERIENCE"]["calculations"],
        "provisional":"Eight paired opaque mappings retained in one world across further acquisition and three queries. Queries themselves also acquire content in controls; Applied, silence, and occupied rejection remain separate."})
    catalog_path=root/"referencias/NSM65_CATALOGO_CPC4.json"
    catalog=json.loads(catalog_path.read_text(encoding="utf-8")); evidence=[]
    ids=[x["id"] for x in rows]
    for entry in catalog["entries"]:
        identifier=entry["id"]; record_e={"id":identifier,"forma_es":entry["forma_es"],"fuentes":entry.get("fuentes",[]),
            "catalogo_heredado": "referencias/NSM65_CATALOGO_CPC4.json", "catalogo_sha256":sha(catalog_path),
            "estado_heredado":entry.get("dimensiones_independientes",{}),
            "CPC5":{"catalogada":True,"funcion_candidata":None,"experiencias":[],"asociacion_funcional_local":False,
                    "retencion_local":False,"reserva_local":False,"uso_consecuencia":False,"emision_inversa":False,
                    "composicion":False,"semantica_primitiva_general":False,
                    "estado":"NO_EJECUTADO_COMO_SIGNIFICADO_NSM_EN_ESTA_FAMILIA","causa_local":"La API ejecutada codifica direcciones; esta relación NSM necesita otro contraste específico."}}
        if identifier in ("NSM65.ABOVE","NSM65.BELOW"):
            record_e["CPC5"].update({"funcion_candidata":"Signo de la dirección y respecto al marco reticular declarado.",
                "experiencias":["LANGUAGE_D01_EIGHT_LANES","LANGUAGE_C01_INVERSE_HISTORY","LANGUAGE_H01_ORDER_QUERY_GEOMETRY","LANGUAGE_H02_NEW_HISTORY_ORDER"],
                "asociacion_funcional_local":True,"retencion_local":True,"reserva_local":True,
                "estado":"CORRESPONDENCIA_DIRECCIONAL_ACUMULADA; ALIAS_HUMANO_NO_ES_SEMANTICA_ESPACIAL_GENERAL",
                "individuo":"LANGUAGE_D01_EIGHT_LANES; ocho formas opacas, dos clases de contenido, MAIN 0→260.",
                "causa_local":"No se probaron marcos relativos, figura/fondo, gravedad, ni todas las funciones del primitivo."})
        elif identifier in ("NSM65.BEFORE","NSM65.AFTER"):
            record_e["CPC5"].update({"funcion_candidata":"Sensibilidad al orden y coincidencia física de eventos opuestos.",
                "experiencias":["LANGUAGE_T01_FIRST_PAIRED_EVENT","LANGUAGE_T02_FIRST_EVENT_INVERTED","LANGUAGE_T03_NEW_GAP_ORDER"],
                "estado":"ORDEN_FISICO_Y_ASOCIACION_TEMPORAL_MEDIDOS; PALABRA_ANTES_DESPUES_NO_ENTRENADA",
                "causa_local":"El primer acontecimiento estaba emparejado con la señal; no es un comparador general antes/después."})
        elif identifier in ("NSM65.THE_SAME","NSM65.OTHER"):
            record_e["CPC5"].update({"funcion_candidata":"Igualdad de contenido frente a diferencia de historia y acceso.",
                "experiencias":["LANGUAGE_D01_EIGHT_LANES","LANGUAGE_C01_INVERSE_HISTORY","LANGUAGE_C05_PHASE_MISS"],
                "estado":"COMPARACION_DEL_OBSERVADOR_EJECUTADA; RESPUESTA_NATIVA_MISMO_OTRO_NO_CONSTRUIDA",
                "causa_local":"El auditor compara direcciones y estado; no se atribuye esa comparación al participante."})
        evidence.append(record_e)
    summary={"schema":"CPC5.NSM65.evidence.v1","registered_entries":len(evidence),"new_full_NSM_meanings_claimed":0,
        "new_scoped_directional_function_candidates":2,"opaque_correspondences_retained_same_MAIN":8,
        "physical_content_classes_in_repertoire":2,"simultaneously_retained_general_NSM_meanings":0,
        "cases":rows,"source_catalog_sha256":sha(catalog_path),"entries":evidence,
        "counting_rule":"Do not sum eight ports as eight NSM meanings; do not sum worlds or queries as independent replicates; inherited evidence remains at its original scope."}
    put(root/"revision/NSM65_EVIDENCIAS.json",summary)
    return {"cases":len(rows),"NSM_catalog_entries":len(evidence),"same_MAIN_opaque_correspondences":8,"NSM_full_claims":0}


if __name__ == "__main__": main()
