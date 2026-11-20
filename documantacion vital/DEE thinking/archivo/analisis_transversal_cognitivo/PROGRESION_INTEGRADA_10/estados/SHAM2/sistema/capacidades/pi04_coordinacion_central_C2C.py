"""PI04 C2/I4: candidate contextual capability choice in ONE inherited world.

No DEE import, owner, execution, files or life selection at module import.
The first physical output selects one prepared Native arithmetic function;
its ACTUAL result enters the inherited Native scalar comparator, whose output
selects a bounded device conduit. The host prepares this sequence, fixed
codecs and opportunities. The environmental law is used only to evaluate the
actual device effect; it never selects an actor operation or conduit.

This is unverified until the root executes its sealed protocol. Read-only state
and dependency checks do not advance a world. Uncertain futures never retry.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import importlib.util
import json
import os

# Technical OP2 only: restore fixed empty filesystem scaffold at an explicit material boundary; never from read-only modes. Scientific VERSION/protocol/Native laws are unchanged.
VERSION = "PI04.C2C.single_current_early_Q_read_hold_q6.R01_DRAFT"
KEY = "DEE.Cognitive.PI04.C2C.coordination.R01"
FOLDER = "PI04_C2C_COORDINACION_R01"
PROTOCOL = Path(__file__).with_name("PROTOCOLO_PI04_C2C_R01.json")
PREFIX = "ECI02_PI03_REPRO_PI04_"
PREPARE = "eci01-pi04-c2c-preparar"
CALIBRATE = "eci01-pi04-c2c-calibrar"
ADMIT = "eci01-pi04-c2c-admitir"
OPPORTUNITY = "eci01-pi04-c2c-oportunidad"
STATE = "eci01-pi04-c2c-estado"
CUT_CONTEXT = "eci01-pi04-c2c-cortar-contexto"
MODES = {PREPARE, CALIBRATE, ADMIT, OPPORTUNITY, STATE, CUT_CONTEXT}
ARMS = {"real", "none", "yoked", "link_cut", "actuator_null", "context_cut"}
_MODULES = {}


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _jsonsafe(value):
    # Encode/decode converts tuples in inherited instrumentation to JSON arrays
    # BEFORE Native metadata encoding. No state, sign or result is changed.
    return json.loads(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                 separators=(",", ":"), allow_nan=False))


def _module(name):
    if name not in _MODULES:
        file = Path(__file__).with_name(name + ".py")
        if not file.is_file():
            raise ValueError("Missing preserved scientific dependency: " + str(file))
        spec = importlib.util.spec_from_file_location("PI04_C2_" + name, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _MODULES[name] = module
    return _MODULES[name]


def _sensor():
    return _module("pi04_sensor_central_C2C_R01")


def _hardware():
    return _module("progresion_integrada_03_R01")


def _helper():
    return _hardware()._helper()


def _pure():
    return _module("e3_retorno_desacoplado_R01")


def _entries(a):
    return dict(a.world.runtime.snapshot_metadata_entries)


def _decode(value):
    from dee_thinking.persistence import decode_metadata
    return decode_metadata(value)


def _get(a):
    entries = _entries(a)
    if KEY not in entries:
        raise ValueError("Explicit C2 sensory preparation required; no implicit install")
    m = _decode(entries[KEY])
    if m["version"] != VERSION:
        raise ValueError("Exact C2 revision required; never reinterpret an earlier future")
    return m


def _save(a, m):
    from dee_thinking.persistence import encode_metadata
    a.world.runtime.set_snapshot_metadata(KEY, _checked_metadata(m, encode_metadata))


def _checked_metadata(m, encoder):
    safe = _jsonsafe(m)
    if len(json.dumps(safe, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf8")) > 65536:
        raise ValueError("C2 progress exceeds frozen64KB capsule; full Native frames belong only in external evidence")
    return encoder(safe)


def protocol(*, material=False, evaluation=False):
    data = PROTOCOL.read_bytes()
    p = json.loads(data)
    required = {"schema", "status", "N", "origin", "base_prefix", "calibration_values",
                "delay_laps", "max_ticks_per_opportunity", "processing_budget_ticks",
                "first_action_codec", "second_zero_motor", "environment",
                "schedule", "dependencies_sha256", "null_stop", "attribution"}
    if set(p) != required or p["schema"] != "DEE.PI04.C2C.protocol.R01":
        raise ValueError("Exact C2 protocol fields required; no dynamic reader or response override")
    if p["status"] not in {"DRAFT", "SEALED_FOR_CALIBRATION", "SEALED_FOR_EVALUATION"}:
        raise ValueError("Explicit draft/calibration/evaluation status required")
    if material and p["status"] == "DRAFT":
        raise ValueError("Draft C2 protocol cannot execute; root must freeze it")
    if evaluation and p["status"] != "SEALED_FOR_EVALUATION":
        raise ValueError("Evaluation requires a separately frozen evaluation protocol")
    if p["N"] != 67 or p["origin"] != [19, 54, 5] or p["base_prefix"] != "PI03.TC.R01":
        raise ValueError("Inherited N67/Q/eligibility prefix only; no substitute organization")
    if p["calibration_values"] != [0, 4, 5]:
        raise ValueError("Finite preregistered calibration values only")
    if type(p["delay_laps"]) is not int or p["delay_laps"] != 4:
        raise ValueError("Four prepared67-tick circuits only in this revision")
    if type(p["max_ticks_per_opportunity"]) is not int or p["max_ticks_per_opportunity"] != 1500:
        raise ValueError("Fixed finite1500-tick horizon required")
    if type(p["processing_budget_ticks"]) is not int or not 220 <= p["processing_budget_ticks"] <= 250:
        raise ValueError("Declare220..250 ticks for one FI128 call plus MU sensor before fixed return")
    if p["first_action_codec"] != {"1": "suma", "0": "diferencia", "-1": "diferencia", "NULL": None}:
        raise ValueError("Frozen first physical-output to arithmetic codec required")
    if p["second_zero_motor"] != -1 or type(p["second_zero_motor"]) is not int:
        raise ValueError("Material zero to motor-1 fixed; NULL never acts")
    env = p["environment"]
    if env != {"context_cut": 4, "low_operation": "diferencia", "high_operation": "suma",
               "numeric_cut": 20, "low_route": -1, "high_route": 1, "resource_bytes": 64}:
        raise ValueError("Fixed private device law only; no per-case favourable result table")
    if p["null_stop"] != "preserve_first_NULL_after_actual_failure_and_generic_return":
        raise ValueError("Preserve first NULL; no adaptive reading or retry")
    if type(p["schedule"]) is not list or not 2 <= len(p["schedule"]) <= 32:
        raise ValueError("One bounded2..32-opportunity schedule required")
    seen_reserved = False
    for i, row in enumerate(p["schedule"]):
        if set(row) != {"stage", "context", "left", "right"} or row["stage"] not in {"development", "reserved", "retention"}:
            raise ValueError("Only stage and three public exact scalars in an opportunity")
        if row["stage"] != "development":
            seen_reserved = True
        elif seen_reserved:
            raise ValueError("No development fitting after a reserved/retention opportunity")
        if type(row["context"]) is not int or not 0 <= row["context"] <= 512:
            raise ValueError("Public context identity scalar0..512 only")
        if any(type(row[k]) is not int or not 0 <= row[k] <= 32 for k in ("left", "right")):
            raise ValueError("Two independent exact FI128 operands0..32 required")
    if type(p["dependencies_sha256"]) is not dict or not p["dependencies_sha256"]:
        raise ValueError("Preserved dependency identities required")
    for name, expected in p["dependencies_sha256"].items():
        if Path(name).name != name or not name.endswith(".py") or len(expected) != 64:
            raise ValueError("Only exact local scientific source identities")
        if material and _sha(Path(__file__).with_name(name).read_bytes()) != expected:
            raise ValueError("Scientific dependency source differs from sealed protocol: " + name)
    return p, _sha(data)


def validate_literal(row):
    if type(row) is not dict:
        raise ValueError("One explicit exact C2 operation required")
    mode = row.get("modo")
    if mode in {PREPARE, OPPORTUNITY, STATE, CUT_CONTEXT} and set(row) == {"modo"}:
        return
    if mode == CALIBRATE and set(row) == {"modo", "valor"}:
        if type(row["valor"]) is int and row["valor"] in (0, 4, 5):
            return
        raise ValueError("Only preregistered0/1/4/44/47/50 calibration values")
    if mode == ADMIT:
        if row.get("brazo") in ARMS - {"yoked", "context_cut"} and set(row) == {"modo", "brazo"}:
            return
        if row.get("brazo") == "yoked" and set(row) == {"modo", "brazo", "plan"}:
            _pure().validate_plan(_pure().unpack_plan(row["plan"]))
            return
        raise ValueError("Fixed real/none/link_cut/actuator_null arm or a sealed yoked plan only")
    raise ValueError("Unknown C2 operation/fields; no target, action, answer, path or reader argument")



OPERATIONAL_GUARD_REVISION = "PI04.C2C.permission.OP1_CANDIDATE"
OPERATIONAL_LIFE_ID = "ECI02_PI03_REPRO_PI04_MAIN_02"

def _system_root():
    return Path(__file__).resolve().parents[1]

def _selected_life_id():
    active = _system_root() / "estado" / "ACTIVO.json"
    if not active.is_file():
        return None
    selected = json.loads(active.read_text(encoding="utf-8-sig"))
    return selected.get("life_id", selected.get("preferred_life"))

def _require_adopted_C2C_use(a, identity, p, ph, operation, directory):
    # Permission only: no RAW/clock, response, reference or protocol edit.
    if identity["life_id"] != OPERATIONAL_LIFE_ID or operation not in (OPPORTUNITY, STATE):
        raise ValueError("ACTIVO permits only exact adopted C2C opportunity/state; preparation/admission/cuts/calibration remain forbidden")
    m = _get(a)
    if (not m.get("ready") or not m.get("admitted") or m.get("arm") != "real"
            or m.get("life_id") != OPERATIONAL_LIFE_ID
            or any(m.get(k) for k in ("pending", "uncertain", "halted_reason"))
            or m.get("calibrations") or m.get("protocol_sha256") != ph
            or p.get("status") != "SEALED_FOR_EVALUATION"):
        raise ValueError("Exact adopted C2C must be admitted real, ready, closed and protocol-consistent")
    if directory is not None:
        raw = Path(directory).absolute()
        expected = _system_root() / "estado" / "servicios_locales" / OPERATIONAL_LIFE_ID
        if not raw.is_dir() or raw.resolve() != expected.resolve():
            raise ValueError("Exact existing owned local-service home required for adopted C2C")
        for part in (raw, *raw.parents):
            if part.exists() and (part.is_symlink() or getattr(part.lstat(), "st_file_attributes", 0) & 1024):
                raise ValueError("No symlink/junction home for adopted C2C")
            if part == _system_root():
                break
    return m

def _identity(a, directory=None, *, operation=None):
    p, ph = protocol(material=True)
    r01, _ = _hardware().protocol()
    # Keep the frozen hardware source unchanged. Its directory=None path
    # validates physical identity without its blanket no-ACTIVO home check.
    identity = _hardware()._identity(a, r01)
    if not identity["life_id"].startswith(PREFIX) or int(a.world.runtime.dimension) != 67:
        raise ValueError("Only an explicit inherited PI04 N67 life")
    selected = _selected_life_id()
    if selected == identity["life_id"]:
        _require_adopted_C2C_use(a, identity, p, ph, operation, directory)
    elif directory is not None:
        # Diagnostic controls preserve their original directory/main refusal.
        identity = _hardware()._identity(a, r01, directory)
    if directory is not None and Path(directory).resolve().name != identity["life_id"]:
        raise ValueError("Exact existing owned-life directory required")
    hardware = _hardware()._get(a)
    if not hardware.get("ready") or hardware.get("pending") or hardware.get("uncertain"):
        raise ValueError("Inherited eligibility apparatus is not complete and closed")
    old = _entries(a).get("DEE.Cognitive.PI02.continuous_workbench.R04")
    if old is not None:
        old = _decode(old)
        if old.get("enabled") or old.get("active") is not None:
            raise ValueError("Explicitly pause inherited O/H bridge and close its job first")
    for key in ("DEE.Cognitive.PI03.useful_delayed_task.R02", "DEE.Cognitive.PI04.E3.contingency.R01"):
        if key in _entries(a):
            state = _decode(_entries(a)[key])
            if state.get("pending") or state.get("uncertain") or state.get("supply_pending") or state.get("halted_reason"):
                raise ValueError("An inherited task/E3 operation is not closed: " + key)
    return p, ph, identity


def _require_closed_predecessors(a, directory=None):
    """Read the two actual adverse futures, without changing their keys/logs."""
    old = _module("pi04_coordinacion_adquirida")
    former = old._get(a)
    if not former.get("admitted") or former.get("arm") != "real" or former.get("ordinal") != 11:
        raise ValueError("Actual old C2 real eleven-opportunity prefix required")
    if former.get("pending") or former.get("uncertain") or not str(former.get("halted_reason", "")).startswith("First NULL/"):
        raise ValueError("Old C2 firstNULL must remain closed/coherent and halted")
    if len(former.get("rows", [])) != 11 or former["rows"][-1].get("first_choice") is not None:
        raise ValueError("Old C2 last firstNULL row missing")
    b = _module("pi04_coordinacion_simetrica_C2B")
    bs = b._get(a)
    if not bs.get("admitted") or bs.get("arm") != "real" or bs.get("ordinal") != 3 or len(bs.get("rows", [])) != 3:
        raise ValueError("Actual C2B three-opportunity future required, not another imported life")
    if any(bs.get(k) for k in ("pending", "uncertain", "halted_reason")):
        raise ValueError("C2B must be coherently closed; no pending cleanup or repeated operation")
    dose = None
    if directory is not None:
        for module in (old, b):
            deps = module.operational_dependencies(a, directory)
            if any(deps.get(k) for k in ("pending", "uncertain", "device_pending", "device_feedback_pending", "device_uncertain")):
                raise ValueError("Predecessor journal/device is not coherent")
        journal = Path(directory) / b.FOLDER / "eventos.jsonl"
        values = []
        with journal.open("r", encoding="utf8") as lines:
            for line in lines:
                item = json.loads(line)
                if item.get("kind") == "C2_OPPORTUNITY_COMPLETED": values.append(item["result"])
        if [v["ordinal"] for v in values] != [0, 1, 2]:
            raise ValueError("All three original C2B completed primaries must be present")
        receipts = {}
        for value in values:
            groups = [value["requests"], value["native_arithmetic"]["native_operation"]["native_trial"]["requests"], value["second_native_use"]["requests"]]
            for items in groups:
                for req in items:
                    r = req["receipt"]; rid = int(req["id"])
                    if rid != r["id"] or (rid in receipts and receipts[rid] != r):
                        raise ValueError("Contradictory predecessor Native receipt alias")
                    if not value["before_tick"] <= r["requested_tick"] <= value["after_tick"]:
                        raise ValueError("Inherited/nonwindow receipt is not a new B input")
                    receipts[rid] = r
        dose = {"requested": len(receipts), "applied": sum(r["status"] == "applied" for r in receipts.values()),
                "rejected": sum(r["status"].startswith("rejected") for r in receipts.values()),
                "other": sum(r["status"] != "applied" and not r["status"].startswith("rejected") for r in receipts.values())}
        if dose != {"requested": 561, "applied": 559, "rejected": 2, "other": 0}:
            raise ValueError("C2B original three-opportunity adverse dose differs: " + repr(dose))
    return {"old_C2_KEY": old.KEY, "old_C2_ordinal": 11, "old_C2_halt": former["halted_reason"],
            "old_C2_state_sha256": _sha(json.dumps(_jsonsafe(former), sort_keys=True, separators=(",", ":")).encode("utf8")),
            "old_C2B_KEY": b.KEY, "old_C2B_ordinal": 3, "old_C2B_last_tick": bs["rows"][-1]["after_tick"],
            "old_C2B_state_sha256": _sha(json.dumps(_jsonsafe(bs), sort_keys=True, separators=(",", ":")).encode("utf8")),
            "old_C2B_actual_Native_dose": dose, "scope": "Both original histories/devices/journals remain intact; no repair/reset/reclassification of old failures"}


def validate(a, row):
    validate_literal(row)
    if row["modo"] == STATE:
        _identity(a, operation=STATE)
        return
    p, ph, identity = _identity(a, operation=row["modo"])
    if row["modo"] == PREPARE:
        _require_closed_predecessors(a)
        if KEY in _entries(a):
            raise ValueError("C2 already prepared; no reinstallation or reference reset")
        return
    m = _get(a)
    if m.get("pending") or m.get("uncertain") or m.get("halted_reason"):
        raise ValueError("Preserve C2 pending/uncertain/halted future; do not resend")
    if not m.get("ready"):
        raise ValueError("C2 sensory preparation is not completely admitted")
    if row["modo"] == CALIBRATE:
        if not identity["life_id"][len(PREFIX):].startswith("C2CCAL") or m.get("admitted"):
            raise ValueError("Sensor calibration only in an explicitly named C2CCAL diagnostic, never candidate/MAIN")
        if p["status"] != "SEALED_FOR_CALIBRATION":
            raise ValueError("Explicit frozen calibration protocol required")
        if len(m.get("calibrations", [])) >= len(p["calibration_values"]):
            raise ValueError("Finite three-call calibration horizon consumed; no unlimited reader search")
        return
    protocol(material=True, evaluation=True)
    if row["modo"] == CUT_CONTEXT:
        _validate_context_cut(p, identity, m)
        return
    if identity["life_id"][len(PREFIX):].startswith("C2CCAL") or m.get("calibrations"):
        raise ValueError("Calibration lives/history cannot be relabelled as a held-out candidate")
    if row["modo"] == ADMIT:
        if m.get("admitted"):
            raise ValueError("C2 already admitted; no reset of finite offers or experience")
        if row["brazo"] == "yoked":
            plan = _pure().validate_plan(_pure().unpack_plan(row["plan"]))
            if len(plan["slots"]) != 20:
                raise ValueError("Yoked control covers exactly the first20 development/reserved opportunities; later continuation stock is not fabricated source data")
        return
    if not m.get("admitted") or m["protocol_sha256"] != ph:
        raise ValueError("C2 evaluation absent or code/protocol changed after admission")
    if m["arm"] == "context_cut" and (not 12 <= m["ordinal"] < 20 or p["schedule"][m["ordinal"]]["stage"] != "reserved"):
        raise ValueError("Context-cut control is limited to the eight reserved opportunities; no retention")
    if m["arm"] == "yoked" and m["ordinal"] >= len(m["plan"]["plan"]["slots"]):
        _module("pi05_yoke_futuros_R01").validate_future(a,m)  # explicit separately registered PI05 ordinals20/21 only
    if m["ordinal"] >= len(p["schedule"]):
        raise ValueError("Frozen opportunities exhausted; no automatic supply or restart")


def _validate_context_cut(p, identity, m):
    """Pure administrative guard; not a sensor/reader or learned decision."""
    life = identity["life_id"]
    if not life.startswith(PREFIX) or "CTX_CUT_" not in life[len(PREFIX):] or life.endswith("CTX_CUT_"):
        raise ValueError("Only an explicitly named PI04_*CTX_CUT_* diagnostic clone")
    if m.get("arm") != "real" or not m.get("admitted") or not m.get("ready") or m.get("ordinal") != 12:
        raise ValueError("Context cut only after exactly twelve completed real training opportunities")
    if any(m.get(k) for k in ("pending", "uncertain", "halted_reason")) or "context_cut_provenance" in m:
        raise ValueError("Cut requires a closed, uncut future; no overwrite/retry")
    if len(m.get("rows", [])) != 12 or any(row.get("stage") != "development" for row in m["rows"]):
        raise ValueError("Twelve actually recorded development rows required")
    if len(p["schedule"]) < 20 or any(row["stage"] != "reserved" for row in p["schedule"][12:20]):
        raise ValueError("Exactly the following eight reserved opportunities must be available")


def cut_context(a, directory):
    """Explicit zero-tick diagnostic lesion, never a Native learned action.

    The existing hardware identity guard with the exact owned directory rejects
    ACTIVO. No RAW/clocks/reader/port/resource is edited, and no datum is emitted.
    """
    validate(a, {"modo": CUT_CONTEXT})
    p, ph, identity = _identity(a, directory)  # Includes inherited no-ACTIVO guard.
    m = _get(a); _validate_context_cut(p, identity, m)
    deps = operational_dependencies(a, directory)
    if deps.get("device_pending") or deps.get("device_feedback_pending") or deps.get("device_uncertain"):
        raise ValueError("Device must be closed before diagnostic cut")
    file = _home(directory) / "CORTE_CONTEXTO.json"
    if file.exists() or file.with_name(file.name + ".pending").exists():
        raise ValueError("Existing context lesion proof preserved; no overwrite")
    before = _physical(a)
    m["arm"] = "context_cut"
    m["context_cut_provenance"] = {"source_arm": "real", "source_ordinal": 12,
        "source_tick": int(a.tick), "relative_proof": file.name,
        "scope": "External diagnostic omission of current context only; not acquired sensor selection"}
    _save(a, m)
    after = _physical(a)
    proof = {"version": VERSION, "life_id": identity["life_id"], "protocol_sha256": ph,
        "ordinal": 12, "arm_before": "real", "arm_after": "context_cut", "before": before, "after": after,
        "physical_equal": before == after, "new_native_ticks": int(a.tick)-before["tick"],
        "omitted": "Only the later per-opportunity scalar context datum event; no material replacement0",
        "preserved": "All query/support events, six-site q+6 reader, efference, actual FI/MU, device and generic real return"}
    _atomic(file, proof)
    _record(a, m, directory, {"kind": "C2_CONTEXT_DIAGNOSTIC_CUT", "proof": proof,
                            "relative_file": file.name, "sha256": _sha(file.read_bytes())})
    if before != after:
        raise RuntimeError("Unexpected physical change in administrative lesion; preserve and stop")
    return proof


def _home(directory):
    return Path(directory) / FOLDER


def _record(a, m, directory, event):
    home = _home(directory)
    home.mkdir(parents=True, exist_ok=True)
    value = _jsonsafe({"index": m["log_count"], "tick": int(a.tick), **event})
    data = (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf8")
    count = m["log_count"] + 1
    chain = _sha(bytes.fromhex(m["log_chain_sha256"]) + data)
    # Validate the next metadata capsule BEFORE appending the audit journal.
    from dee_thinking.persistence import encode_metadata
    _checked_metadata(dict(m, log_count=count, log_chain_sha256=chain), encode_metadata)
    with (home / "eventos.jsonl").open("ab") as out:
        out.write(data); out.flush(); os.fsync(out.fileno())
    m["log_count"] = count; m["log_chain_sha256"] = chain
    _save(a, m)


def _banks(a):
    from app.native_tools import observe
    return [observe(a.world, _helper().at([19, 54, 5], p)) for p in ((-1, -1, 0), (1, -1, 0))]


def _physical(a):
    from app.native_tools import physical
    return physical(a.world)


def _frame(a, label):
    from app.native_tools import observe
    helper = _helper(); origin = [19, 54, 5]
    points = {"A": (-1,-1,0), "B": (1,-1,0), "Q": (0,0,0), "datum": (-1,0,1),
              "eligibility_hub": (0,-1,-2), "postread_support": (0,3,0)}
    return {"label": label, "physical": _physical(a),
            "fields": {name: observe(a.world, helper.at(origin, offset)) for name, offset in points.items()}}


def prepare(a, directory):
    p, ph, identity = _identity(a, directory)
    home = _home(directory)
    if home.exists() or KEY in _entries(a):
        raise ValueError("Existing C2 state/files preserved; never overwrite or silently retry")
    predecessors = _require_closed_predecessors(a, directory)
    before = _physical(a)
    m = {"version": VERSION, "life_id": identity["life_id"], "prepared_tick": int(a.tick),
         "prepared_physical": None, "ready": False, "admitted": False, "calibrations": [],
         "pending": {"phase":"explicit_sensor_preparation"}, "uncertain": True, "halted_reason": None,
         "log_count": 0, "log_chain_sha256": "00"*32,
         "predecessors_preserved": predecessors,
         "attribution": "External fixed earlier reader and two-tick hold only; all inherited physical banks/history/interfaces preserved"}
    _save(a, m)
    _record(a,m,directory,{"kind":"C2_SENSORY_PREPARATION_INTENT","before":before,"protocol_sha256":ph})
    preparation = _sensor().prepare(a)
    m.update({"prepared_physical":_physical(a),"ready":True,"pending":None,"uncertain":False})
    _record(a, m, directory, {"kind": "C2_SENSORY_PREPARATION", "before": before,
                            "protocol_sha256_at_preparation": ph, "preparation": preparation})
    return {"version": VERSION, "prepared": True, "new_native_ticks": int(a.tick)-before["tick"],
            "preparation": preparation, "physical": _physical(a), "acquisition_claim": False}


def calibrate(a, row, directory):
    validate(a, row); p, ph, identity = _identity(a, directory); m = _get(a)
    from capacidades import mente_unificada_01 as mu
    start = int(a.tick)
    timing = mu.calendar_query_timing(start+8, True)
    q = timing["effective_query_tick"]
    m["uncertain"] = True; m["pending"] = {"phase": "calibration_query", "q": q, "value": row["valor"]}
    _save(a, m)
    _record(a, m, directory, {"kind": "C2_CALIBRATION_INTENT", "value": row["valor"],
                            "timing": timing, "protocol_sha256": ph, "before": _frame(a, "before")})
    requests = _helper().submit_query(a.world, q, prefix=p["base_prefix"])
    requests.append(_sensor().submit_datum(a, row["valor"], q))
    a.run_until(q+4); reader = _sensor().read_fixed(a, q)
    a.run_until(q+6)  # Hold observed command; downstream age/copy calendar unchanged.
    # Prepared comparable settling horizon; no efference or outcome is inserted.
    a.run_until(q+8+2*67)
    requests = _hardware()._receipts(a, requests)
    result = {"version": VERSION, "kind": "sensor_calibration_only", "before_tick": start,
              "after_tick": int(a.tick), "value": row["valor"], "reader": reader,
              "timing": timing, "requests": requests, "feedback_inserted": False,
              "efference_inserted": False, "after": _frame(a, "after")}
    m["calibrations"].append({"value": row["valor"], "before_tick": start,
                              "after_tick": int(a.tick), "choice": reader["choice"]})
    applied = all(r["receipt"]["status"] == "applied" for r in requests)
    m["uncertain"] = not applied
    m["pending"] = None if applied else {"phase": "calibration_rejected_preserved"}
    _record(a, m, directory, {"kind": "C2_CALIBRATION_COMPLETED", "result": result})
    return result


def _atomic(path, value):
    path = Path(path); pending = path.with_name(path.name+".pending")
    if pending.exists():
        raise ValueError("Uncertain external write preserved; no overwrite")
    with pending.open("x", encoding="utf8") as out:
        json.dump(_jsonsafe(value), out, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        out.write("\n"); out.flush(); os.fsync(out.fileno())
    os.replace(pending, path)


class Device:
    """Finite external apparatus. No Native policy, actor callback or shell."""
    @classmethod
    def prepare(cls, home, count, environment):
        home = Path(home)
        if home.exists():
            raise ValueError("Device destination already exists; no resets")
        home.mkdir()
        for folder in ("reservoir", "inflight_minus", "inflight_plus", "inflight_silence", "consumed", "rejected", "products"):
            (home/folder).mkdir()
        resources = []
        for i in range(count):
            content = hashlib.sha256(("PI04.C2.resource."+str(i)).encode("ascii")).digest()*2
            name = "%04d.resource" % i
            with (home/"reservoir"/name).open("xb") as out:
                out.write(content); out.flush(); os.fsync(out.fileno())
            resources.append({"name": name, "bytes": 64, "sha256": _sha(content)})
        _atomic(home/"ESTADO_DISPOSITIVO.json", {"version": VERSION, "environment": environment,
                "resources": resources, "ordinal": 0, "pending": None, "feedback_pending": None,
                "products": [], "rejections": [], "uncertain": False,
                "scope": "Private environment/progress, never an actor policy or accessible decision memory"})
        return cls(home)

    def __init__(self, home):
        self.home = Path(home)
        self.m = json.loads((self.home/"ESTADO_DISPOSITIVO.json").read_text(encoding="utf8"))
        if self.m["version"] != VERSION:
            raise ValueError("Exact external device revision required")

    def ensure_schema_directories(self):
        """P0 transport scaffold, only called at an explicit material boundary.

        All existing resources/products must already be intact. Only the seven
        fixed directory entries may be created; never a file, resource, state,
        snapshot, counter, memory, response or clock. Not autonomous recovery.
        """
        folders = ("reservoir", "inflight_minus", "inflight_plus", "inflight_silence", "consumed", "rejected", "products")
        if self.m.get("pending") or self.m.get("feedback_pending") or self.m.get("uncertain"):
            raise ValueError("No scaffold action on an unresolved device future")
        home = self.home.absolute()
        for node in (home, *home.parents):
            if node.is_symlink() or (node.exists() and getattr(node.lstat(), "st_file_attributes", 0) & 0x400):
                raise ValueError("No linked/reparse device scaffold")
        if not home.is_dir():
            raise ValueError("The original device/state must already exist")
        state = home / "ESTADO_DISPOSITIVO.json"
        state_hash = _sha(state.read_bytes())
        missing = []
        for name in folders:
            node = home / name
            if node.is_symlink() or (node.exists() and getattr(node.lstat(), "st_file_attributes", 0) & 0x400):
                raise ValueError("No linked/reparse fixed device directory")
            if node.exists():
                if not node.is_dir():
                    raise ValueError("A regular file occupies a fixed device directory")
            else:
                missing.append(name)
        resources = self.m.get("resources")
        ordinal = self.m.get("ordinal")
        if not isinstance(resources, list) or type(ordinal) is not int or not 0 <= ordinal <= len(resources):
            raise ValueError("The original finite resource state is required")
        for index, resource in enumerate(resources):
            if resource.get("name") != "%04d.resource" % index or type(resource.get("bytes")) is not int:
                raise ValueError("Only exact original resource filenames/sizes")
            locations = [home / folder / resource["name"] for folder in folders[:-1]]
            for file in locations:
                if file.is_symlink() or (file.exists() and getattr(file.lstat(), "st_file_attributes", 0) & 0x400):
                    raise ValueError("No linked/reparse resource")
            present = [file for file in locations if file.is_file()]
            if len(present) != 1 or present[0].stat().st_size != resource["bytes"] or _sha(present[0].read_bytes()) != resource["sha256"]:
                raise ValueError("Missing/altered/duplicated original resource; no regeneration")
            allowed = {"consumed", "rejected"} if index < ordinal else {"reservoir"}
            if present[0].parent.name not in allowed:
                raise ValueError("Resource placement disagrees with the closed device progress")
        products = self.m.get("products")
        if not isinstance(products, list):
            raise ValueError("Original products list is required")
        for product in products:
            relative = Path(product["path"])
            if relative.is_absolute() or len(relative.parts) != 2 or relative.parts[0] != "products" or relative.name in (".", ".."):
                raise ValueError("Only original local product filenames")
            file = home / relative
            if file.is_symlink() or (file.exists() and getattr(file.lstat(), "st_file_attributes", 0) & 0x400):
                raise ValueError("No linked/reparse product")
            if not file.is_file() or file.stat().st_size != product["bytes"] or _sha(file.read_bytes()) != product["sha256"]:
                raise ValueError("Missing/altered original product; no regeneration")
        # Validate every original file before the first mkdir. No exist_ok,
        # deletion, file write or counter adjustment masks a concurrent change.
        for name in missing:
            (home / name).mkdir()
        if _sha(state.read_bytes()) != state_hash:
            raise ValueError("Device state changed during scaffold preparation")
        return {"technical_revision": "C2C.OP2.fixed_device_directory_schema",
                "created_directories": missing, "fixed_directories": list(folders),
                "resource_files_verified": len(resources), "product_files_verified": len(products),
                "device_state_sha256_before": state_hash, "device_state_sha256_after": _sha(state.read_bytes()),
                "files_or_contents_recreated": False, "scope": "Prepared P0 transport scaffold, not learned regulation or repair"}

    def save(self):
        _atomic(self.home/"ESTADO_DISPOSITIVO.json", self.m)

    def begin(self, actual_route, actual_operation, actual_value, context, tick, ready_tick):
        # No correct route is computed here to replace the actor's route.
        if actual_route is not None and (type(actual_route) is not int or actual_route not in (-1,1)):
            raise ValueError("Actual binary route or NULL only")
        if actual_operation not in (None,"suma","diferencia") or (actual_value is not None and type(actual_value) is not int):
            raise ValueError("Actual called operation/result or NULL only")
        if type(context) is not int or not 0 <= context <= 512 or type(tick) is not int or type(ready_tick) is not int or ready_tick <= tick:
            raise ValueError("Exact current context and future fixed deadline required")
        if self.m["pending"] or self.m["feedback_pending"] or self.m["uncertain"]:
            raise ValueError("One coherent device operation only")
        i = self.m["ordinal"]; resource = self.m["resources"][i]
        source = self.home/"reservoir"/resource["name"]
        if source.stat().st_size != resource["bytes"] or _sha(source.read_bytes()) != resource["sha256"]:
            raise ValueError("Missing/altered real resource; do not regenerate")
        folder = "inflight_minus" if actual_route == -1 else "inflight_plus" if actual_route == 1 else "inflight_silence"
        target = self.home/folder/resource["name"]
        if target.exists():
            raise ValueError("Prior inflight resource preserved")
        self.m["uncertain"] = True
        self.m["pending"] = {"ordinal": i, "actual_route": actual_route, "actual_operation": actual_operation,
                              "actual_value": actual_value, "public_context": context, "folder": folder,
                              "action_tick": tick, "ready_tick": ready_tick, "phase": "before_move"}
        self.save(); source.replace(target)
        self.m["pending"]["phase"] = "inflight"; self.m["uncertain"] = False; self.save()
        return _jsonsafe(self.m["pending"])

    def complete(self, tick):
        p = self.m["pending"]
        if not p or self.m["uncertain"] or p["phase"] != "inflight" or tick != p["ready_tick"]:
            raise ValueError("Exact predeclared due boundary and certain inflight resource required")
        i = p["ordinal"]; r = self.m["resources"][i]; env = self.m["environment"]
        source = self.home/p["folder"]/r["name"]; content = source.read_bytes()
        if len(content) != r["bytes"] or _sha(content) != r["sha256"]:
            raise ValueError("Actual resource changed; preserve failed device")
        # PRIVATE DEVICE LAW. Its outputs never enter an actor/selector call.
        wanted_operation = env["low_operation"] if p["public_context"] <= env["context_cut"] else env["high_operation"]
        value_valid = type(p["actual_value"]) is int and 0 <= p["actual_value"] <= 65535
        connected_route = (env["low_route"] if p["actual_value"] <= env["numeric_cut"] else env["high_route"]) if value_valid else None
        accepted = value_valid and p["actual_operation"] == wanted_operation and p["actual_route"] is not None and p["actual_route"] == connected_route
        self.m["uncertain"] = True; self.save()
        product = None
        if accepted:
            # Actual Native result, never the result of Python arithmetic on
            # the operands, is transported into the real64-byte output.
            data = p["actual_value"].to_bytes(2,"little",signed=False)+content[2:]
            file = self.home/"products"/("%04d.bin" % i)
            with file.open("xb") as out:
                out.write(data); out.flush(); os.fsync(out.fileno())
            product = {"path": "products/"+file.name, "bytes": len(data), "sha256": _sha(data),
                       "actual_native_integer": p["actual_value"]}
            self.m["products"].append(product)
            destination = self.home/"consumed"/r["name"]
        else:
            self.m["rejections"].append({"ordinal":i,"route":p["actual_route"],"actual_operation":p["actual_operation"],"actual_value":p["actual_value"]})
            destination = self.home/"rejected"/r["name"]
        if destination.exists():
            raise ValueError("Existing completed resource preserved; no repeat effect")
        source.replace(destination)
        effect = {"ordinal": i, "actual_operation": p["actual_operation"], "actual_value": p["actual_value"],
                  "actual_route": p["actual_route"], "failed": not accepted, "product": product,
                  "private_evaluator_only": {"required_operation": wanted_operation, "connected_route": connected_route},
                  "actual_deadline": tick, "effect_is_real_file": product is not None}
        self.m["pending"] = None; self.m["ordinal"] += 1
        self.m["feedback_pending"] = {"ordinal":i,"actual_failed":not accepted,"request_id":None}
        self.m["uncertain"] = False; self.save()
        return effect

    def feedback(self, request):
        if not self.m["feedback_pending"] or self.m["feedback_pending"]["request_id"] is not None:
            raise ValueError("Exact one feedback receipt reconciliation only")
        self.m["feedback_pending"]["request_id"] = request["id"]; self.save()

    def reconcile(self, receipt):
        p = self.m["feedback_pending"]
        if not p or p["request_id"] != int(receipt["id"]):
            raise ValueError("Device feedback request identity differs")
        ok = receipt["status"] == "applied"
        if ok:
            self.m["feedback_pending"] = None
        else:
            self.m["uncertain"] = True
        self.save()
        return {"finished": ok, "actual_receipt": receipt}


def _device(directory):
    return Device(_home(directory)/"dispositivo")


def admit(a, row, directory):
    validate(a, row); p, ph, identity = _identity(a, directory); m = _get(a)
    if any(m.get(k) for k in ("pending", "uncertain", "halted_reason")) or m.get("admitted"):
        raise ValueError("Existing C2 future cannot be readmitted")
    m["uncertain"] = True; m["pending"] = {"phase":"device_preparation"}; _save(a,m)
    _record(a,m,directory,{"kind":"C2_DEVICE_ADMISSION_INTENT","protocol_sha256":ph,"arm":row["brazo"]})
    device = Device.prepare(_home(directory)/"dispositivo", len(p["schedule"]), p["environment"])
    m.update({"admitted": True, "protocol_sha256": ph, "arm": row["brazo"],
              "plan": _pure().unpack_plan(row["plan"]) if row["brazo"] == "yoked" else None,
              "admitted_tick": int(a.tick), "ordinal": 0, "rows": [],
              "pending": None, "uncertain": False, "halted_reason": None})
    _record(a,m,directory,{"kind":"C2_DEVICE_ADMITTED","resources":len(device.m["resources"]),
                           "protocol":p,"arm":row["brazo"],"new_native_ticks":0,
                           "assistance":"Schedule/sequence/codecs/device prepared; no selected action or acquired reference installed"})
    return {"version":VERSION,"admitted":True,"arm":m["arm"],"opportunities":len(p["schedule"]),"new_native_ticks":0}


def _motor(choice):
    if type(choice) is not int or choice not in (-1,0,1):
        return None
    return -1 if choice == 0 else choice


def _operation(choice):
    # Physical fixed transduction, with no context, target or past-state input.
    if type(choice) is not int:
        return None
    return "suma" if choice == 1 else "diferencia" if choice in (-1,0) else None


def _calendar_view(calendar,banks,start):
    return {k:int(calendar[k]) for k in ("query_tick","query_read_tick","outcome_injection_tick","contact_tick","delay_laps")} | {
        "reference_contact_phase":(int(banks[0]["clock"])+int(calendar["contact_tick"])-start)%782}


def _native_input_summary(outer, arithmetic, second, before_tick, after_tick):
    """Audit only direct new-call receipt groups; never recurse into history.

    Terminal rejection is a known adverse event, distinct from uncertainty.
    A missing/unexecuted stage is not fabricated and contributes zero inputs.
    """
    groups={"outer":outer}
    if arithmetic is not None:
        groups["FI"]=arithmetic["native_operation"]["native_trial"]["requests"]
    if second is not None and "requests"in second:
        groups["MU"]=second["requests"]
    unique={};aliases=0
    for group,items in groups.items():
        for request in items:
            r=request["receipt"];rid=request["id"]
            if type(rid)is not int or r["id"]!=rid:
                raise ValueError("Native input audit ID mismatch")
            if type(r["requested_tick"])is not int or not before_tick<=r["requested_tick"]<=after_tick:
                raise ValueError("Receipt outside this actual call window, not a new input")
            if rid in unique:
                if unique[rid]["receipt"]!=r:raise ValueError("Contradictory Native input alias")
                aliases+=1
            else:unique[rid]={"group":group,"receipt":r}
    counts={}
    for item in unique.values():
        status=item["receipt"]["status"];counts[status]=counts.get(status,0)+1
    rejected=[{"group":v["group"],"receipt":v["receipt"]}for v in unique.values()if v["receipt"]["status"].startswith("rejected")]
    other=[{"group":v["group"],"receipt":v["receipt"]}for v in unique.values()if v["receipt"]["status"]!="applied"and not v["receipt"]["status"].startswith("rejected")]
    return {"unique_requested":len(unique),"applied":counts.get("applied",0),"rejected":len(rejected),
            "pending_or_other":len(other),"status_counts":counts,"aliases_deduplicated":aliases,
            "group_raw_counts":{g:len(v)for g,v in groups.items()},"rejected_receipts":rejected,
            "nonterminal_or_other_receipts":other,"all_terminal":not other,
            "scope":"Only current outer/FI/MU direct receipt lists and call window; no inherited metadata/progress scan"}


# PI05 external-control bridge only: original20 plan stays literal; no Native call/reader/codec change.
def _pi05_yoked_signal(a,m,calendar):
    if m['ordinal']<20:return _pure().replay_signal(m['plan'],m['ordinal'],calendar)
    return _module('pi05_yoke_futuros_R01').replay_signal(a,m,calendar)


def _opportunity_body(a,directory):
    validate(a,{"modo":OPPORTUNITY}); p,ph,identity=_identity(a,directory,operation=OPPORTUNITY); m=_get(a); device=_device(directory)
    if device.m["ordinal"] != m["ordinal"] or device.m["pending"] or device.m["feedback_pending"] or device.m["uncertain"]:
        raise ValueError("Complete C2/device progress mismatch; no counter reset")
    schema_before = _physical(a)
    schema_preparation = device.ensure_schema_directories()
    schema_after = _physical(a)
    if schema_before != schema_after:
        raise RuntimeError("Technical directory preparation changed physical RAW/clocks/tick")
    schema_preparation.update({"physical_before":schema_before,"physical_after":schema_after,"new_native_ticks":0})
    if schema_preparation["created_directories"]:
        _record(a,m,directory,{"kind":"C2_DEVICE_DIRECTORY_SCHEMA_PREPARED_OP2","preparation":schema_preparation})
    start=int(a.tick); banks=_banks(a)
    if int(banks[0]["clock"])%782 != int(banks[1]["clock"])%782:
        raise ValueError("Inherited bank phases differ; no repair")
    cal=_helper().schedule_trial(start,int(banks[0]["clock"]),p["delay_laps"])
    q=cal["query_tick"]; ready=cal["outcome_injection_tick"]-1; end=cal["contact_tick"]+2
    if end-start>p["max_ticks_per_opportunity"] or ready-cal["query_read_tick"]<p["processing_budget_ticks"]:
        raise ValueError("Predeclared calendar cannot contain this finite real processing sequence")
    normalized=_calendar_view(cal,banks,start); _pure().checked_calendar(normalized)
    if m["arm"]=="yoked":
        _pi05_yoked_signal(a,m,normalized) # verify BEFORE material input; original20 or separately declared PI05 future
    spec=p["schedule"][m["ordinal"]]
    m["uncertain"]=True; m["pending"]={"phase":"first_query","ordinal":m["ordinal"],"calendar":cal}
    _save(a,m)
    _record(a,m,directory,{"kind":"C2_OPPORTUNITY_INTENT","spec":spec,"calendar":cal,"arm":m["arm"],"before":_frame(a,"before")})
    requests=_helper().submit_query(a.world,q,prefix=p["base_prefix"])
    if m["arm"] != "context_cut":
        requests.append(_sensor().submit_datum(a,spec["context"],q))
    # context_cut omits ONE datum event entirely: no zero/sham/replacement.
    # All generic queries, six-site reader, real Native functions and feedback remain.
    a.run_until(q+4); first_reader=_sensor().read_fixed(a,q)
    a.run_until(cal["query_read_tick"])  # Prepared two-tick IO hold, never choose another reader.
    first_choice=first_reader["choice"]; first_motor=_motor(first_choice); operation=_operation(first_choice)
    copy=None
    if first_motor is not None:
        copy=_helper().submit_motor_copy(a.world,first_motor,cal["seed_tick"],prefix=p["base_prefix"])
        requests.append(copy)
    m["pending"]={"phase":"first_output_before_native_function","ordinal":m["ordinal"],"calendar":cal,
                  "request_ids":[r["id"]for r in requests]}; _save(a,m)
    _record(a,m,directory,{"kind":"C2_FIRST_NATIVE_CHOICE","reader":first_reader,"first_motor":first_motor,
                          "selected_operation":operation,"copy":copy,
                          "codec":"+1->suma; material0/-1->diferencia; NULL->no function"})
    arithmetic=None; numeric=None; second=None; second_reader=None; second_motor=None
    if operation is not None:
        from capacidades import aritmetica_directa_eci02 as arithmetic_api
        if ready-int(a.tick)<p["processing_budget_ticks"]:
            raise RuntimeError("Fixed processing allowance lost before Native arithmetic; preserve pending future")
        arithmetic=arithmetic_api.execute(a,{"modo":arithmetic_api.MODE,"operacion":operation,
                                            "izquierda":spec["left"],"derecha":spec["right"]})
        numeric=arithmetic.get("numeric_result")
        if int(a.tick)>ready:
            raise RuntimeError("Native arithmetic passed fixed consequence deadline; no past return or adaptive delay")
        _record(a,m,directory,{"kind":"C2_ACTUAL_NATIVE_ARITHMETIC","actual":arithmetic,
                              "after":_frame(a,"after_arithmetic"),"result_not_expected":True})
        if type(numeric) is int and 0<=numeric<=512:
            from capacidades import mente_unificada_01 as mu
            planned=mu.query_timing(a,int(a.tick)+8)
            if planned["effective_query_tick"]+8>=ready:
                raise RuntimeError("Second Native sensor does not fit fixed return calendar; preserve without adaptive pause")
            if m["arm"]=="link_cut":
                # Same planned age, NO second input. It is an explicit link
                # intervention, not a zero datum or an observed zero response.
                a.run_until(planned["effective_query_tick"]+8)
                second={"kind":"actual_result_link_cut","actual_upstream_result":numeric,
                        "second_sensor_called":False,"reader":None,"material_input_count":0,
                        "planned_age_only":planned,"second_choice":None}
            else:
                second=mu.current(a,numeric,detail=False)
                second_reader=second["reader"]; second_motor=_motor(second_reader["choice"])
        else:
            second={"kind":"invalid_or_NULL_actual_arithmetic_result","actual_result":numeric,
                    "second_sensor_called":False,"no_expected_fallback":True}
    if int(a.tick)>=ready:
        raise RuntimeError("Fixed effect boundary reached before real actuator intent; do not reschedule")
    applied_route=None if m["arm"]=="actuator_null" else second_motor
    physical_before_device_begin=_physical(a)  # Passive RAW/clocks witness for the preserved failed-import comparison.
    action=device.begin(applied_route,operation,numeric,spec["context"],int(a.tick),ready)
    m["pending"]={"phase":"actual_second_action_inflight","ordinal":m["ordinal"],"calendar":cal,
                  "request_ids":[r["id"]for r in requests]}; _save(a,m)
    _record(a,m,directory,{"kind":"C2_SECOND_NATIVE_USE_AND_ACTION","second":second,
                          "second_motor":second_motor,"applied_route":applied_route,"action":action,
                          "after":_frame(a,"after_second_decision"),
                          "assistance":"Fixed result identity codec and route transduction; no host numeric threshold or action calculation in actor path"})
    a.run_until(ready); effect=device.complete(ready)
    actual_failed=effect["failed"]
    returned_failed=(False if m["arm"]=="none" else _pi05_yoked_signal(a,m,normalized)
                     if m["arm"]=="yoked" else actual_failed)
    outcome=_helper().submit_generic_outcome(a.world,returned_failed,cal["outcome_injection_tick"],prefix=p["base_prefix"])
    requests.append(outcome); device.feedback(outcome)
    m["pending"]={"phase":"generic_return_scheduled","ordinal":m["ordinal"],"calendar":cal,
                  "request_ids":[r["id"]for r in requests]}; _save(a,m)
    _record(a,m,directory,{"kind":"C2_ACTUAL_EFFECT_AND_GENERIC_RETURN","effect":effect,
                          "actual_failed":actual_failed,"returned_failed":returned_failed,"request":outcome,
                          "scope":"Only generic outcome enters eligibility hub; no chosen bank/context/operation in return API"})
    for tick,label in ((cal["outcome_injection_tick"],"generic_return_boundary"),
                       (cal["collision_tick"],"eligibility_hub_collision"),
                       (cal["contact_tick"],"native_reference_contact"),(end,"settled")):
        a.run_until(tick); _record(a,m,directory,{"kind":"C2_CAUSAL_FRAME","frame":_frame(a,label)})
    requests=_hardware()._receipts(a,requests)
    receipt=next(r["receipt"]for r in requests if r["id"]==outcome["id"])
    reconciliation=device.reconcile(receipt)
    null_seen=first_choice is None or (m["arm"]!="link_cut" and operation is not None and
                   (type(numeric)is not int or second_reader is None or second_reader["choice"] is None))
    quality=_native_input_summary(requests,arithmetic,second,start,int(a.tick))
    first_rejected=quality["rejected"]>0 and quality["all_terminal"]and reconciliation["finished"]
    result={"version":VERSION,"ordinal":m["ordinal"],"spec":spec,"arm":m["arm"],
            "before_tick":start,"after_tick":int(a.tick),"calendar":cal,"normalized_calendar":normalized,
            "context_input_supplied":m["arm"] != "context_cut",
            "technical_device_schema_preparation":schema_preparation,"physical_before_device_begin":physical_before_device_begin,
            "first_reader":first_reader,"first_motor":first_motor,"selected_operation":operation,
            "physical_read_tick":q+4,"actuation_availability_tick":cal["query_read_tick"],
            "native_arithmetic":arithmetic,"actual_numeric_result":numeric,"second_native_use":second,
            "second_motor":second_motor,"applied_route":applied_route,"actual_effect":effect,
            "actual_failed":actual_failed,"returned_failed":returned_failed,"requests":requests,
            "reconciliation":reconciliation,"bank_before":banks,"bank_after":_banks(a),
            "native_input_summary":quality,"first_rejected_preserved":first_rejected,
            "useful_product":effect["product"]is not None,"first_NULL_preserved":null_seen,
            "scope":"Acquired first capability selection requires history controls. Sequence/codec/calendar/device are prepared; actual Native result feeds Native second choice. Not discovered planning or general agency."}
    m["ordinal"]+=1
    m["rows"].append({"ordinal":result["ordinal"],"stage":spec["stage"],"context":spec["context"],
                      "first_choice":first_choice,"operation":operation,"actual_numeric_result":numeric,
                      "second_choice":None if second_reader is None else second_reader["choice"],
                      "useful_product":result["useful_product"],"actual_failed":actual_failed,
                      "returned_failed":returned_failed,"after_tick":int(a.tick)})
    m["rows"][-1]["native_input_counts"]={k:quality[k]for k in("unique_requested","applied","rejected","pending_or_other")}
    m["uncertain"]=not quality["all_terminal"]or not reconciliation["finished"]
    m["pending"]=None if not m["uncertain"] else {"phase":"rejected_or_unreconciled_preserved"}
    if null_seen:
        m["halted_reason"]="First NULL/invalid actual numeric response preserved after actual failure and generic return; no retry"
    if first_rejected:
        m["halted_reason"]="First terminal Native input rejection preserved after actual effect and generic return; outer/FI/MU counted, no repair/retry"
    _record(a,m,directory,{"kind":"C2_OPPORTUNITY_COMPLETED","result":result})
    return result


def opportunity(a,directory):
    try:
        return _opportunity_body(a,directory)
    except Exception as exc:
        # Root owner will also preserve its failed receipt. Do not clear a
        # pending request, undo a consequence, move time or reissue anything.
        if KEY in _entries(a):
            m=_get(a); m["uncertain"]=True
            m["halted_reason"]="Preserved C2 failure: "+type(exc).__name__+": "+str(exc)
            _save(a,m)
            try:
                _record(a,m,directory,{"kind":"C2_FAILURE_PRESERVED","error_type":type(exc).__name__,"error":str(exc)})
            except Exception:
                pass
        raise


def state(a,directory=None):
    _identity(a,directory,operation=STATE)
    result={"version":VERSION,"admitted":KEY in _entries(a),"new_native_ticks":0,
            "physical":_physical(a),"scope":"Passive administrative view, no material query or automatic repair"}
    if KEY in _entries(a):
        m=_get(a); result["progress"]=m
        if directory is not None and m.get("admitted"):
            result["device"]=_device(directory).m
    return result


def dispatch(a,row,*,actuator="closed",directory=None):
    validate(a,row)
    if row["modo"]==STATE:
        return state(a,directory)
    if directory is None or actuator!="closed":
        raise ValueError("Exact owned directory/closed wrapper required; diagnostic action cuts are frozen at admission")
    _identity(a,directory,operation=row["modo"])
    if row["modo"]==PREPARE:return prepare(a,directory)
    if row["modo"]==CALIBRATE:return calibrate(a,row,directory)
    if row["modo"]==ADMIT:return admit(a,row,directory)
    if row["modo"]==CUT_CONTEXT:return cut_context(a,directory)
    return opportunity(a,directory)


def uncertain(a):
    return KEY in _entries(a) and bool(_get(a).get("uncertain"))


def operational_dependencies(a,directory):
    if KEY not in _entries(a):
        return {"version":VERSION,"present":False,"new_native_ticks":0}
    m=_get(a); home=_home(directory); journal=home/"eventos.jsonl"
    count=0; chain="00"*32
    with journal.open("rb")as rows:
        for line in rows:
            json.loads(line); count+=1; chain=_sha(bytes.fromhex(chain)+line)
    if count!=m["log_count"] or chain!=m["log_chain_sha256"]:
        raise ValueError("C2 snapshot/journal mismatch; preserve without replay")
    result={"version":VERSION,"present":True,"admitted":m.get("admitted",False),
            "log_count":count,"log_chain_sha256":chain,"pending":m.get("pending"),
            "uncertain":m.get("uncertain"),"halted_reason":m.get("halted_reason"),"new_native_ticks":0}
    if not m.get("admitted"):
        return result
    p,ph=protocol()
    if ph!=m["protocol_sha256"]:
        raise ValueError("Current C2 protocol differs from inherited evaluated state")
    d=_device(directory)
    if d.m["ordinal"]!=m["ordinal"] and not m.get("pending"):
        raise ValueError("C2/device progress mismatch")
    files=[]
    for resource in d.m["resources"]:
        if Path(resource["name"]).name!=resource["name"]:
            raise ValueError("Invalid relative resource name")
        candidates=[d.home/folder/resource["name"]for folder in
                    ("reservoir","inflight_minus","inflight_plus","inflight_silence","consumed","rejected")]
        present=[f for f in candidates if f.is_file()]
        if len(present)!=1 or present[0].stat().st_size!=resource["bytes"] or _sha(present[0].read_bytes())!=resource["sha256"]:
            raise ValueError("Missing/altered/duplicated actual C2 resource; no automatic repair")
        files.append({"path":str(present[0]),"bytes":resource["bytes"],"sha256":resource["sha256"]})
    products=[]
    for r in d.m["products"]:
        name=Path(r["path"])
        if name.is_absolute() or ".."in name.parts or len(name.parts)!=2 or name.parts[0]!="products":
            raise ValueError("Bounded relative product path required")
        f=d.home/name
        if not f.is_file() or f.stat().st_size!=r["bytes"] or _sha(f.read_bytes())!=r["sha256"]:
            raise ValueError("Missing/altered actual product; no counter-only success")
        products.append({"path":str(f),"bytes":r["bytes"],"sha256":r["sha256"]})
    result.update({"ordinal":m["ordinal"],"prepared_resources":len(d.m["resources"]),
                   "products":products,"resource_files":files,"device_pending":d.m["pending"],
                   "device_feedback_pending":d.m["feedback_pending"],"device_uncertain":d.m["uncertain"]})
    return result
