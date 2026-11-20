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

VERSION = "PI04.C2B.symmetric_current_native_coordination.R01_DRAFT"
KEY = "DEE.Cognitive.PI04.C2B.coordination.R01"
FOLDER = "PI04_C2B_COORDINACION_R01"
PROTOCOL = Path(__file__).with_name("PROTOCOLO_PI04_C2B_R01.json")
PREFIX = "ECI02_PI03_REPRO_PI04_"
PREPARE = "eci01-pi04-c2b-preparar"
CALIBRATE = "eci01-pi04-c2b-calibrar"
ADMIT = "eci01-pi04-c2b-admitir"
OPPORTUNITY = "eci01-pi04-c2b-oportunidad"
STATE = "eci01-pi04-c2b-estado"
CUT_CONTEXT = "eci01-pi04-c2b-cortar-contexto"
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
    return _module("pi04_sensor_simetrico_C2B_R01")


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
    if set(p) != required or p["schema"] != "DEE.PI04.C2B.protocol.R01":
        raise ValueError("Exact C2 protocol fields required; no dynamic reader or response override")
    if p["status"] not in {"DRAFT", "SEALED_FOR_CALIBRATION", "SEALED_FOR_EVALUATION"}:
        raise ValueError("Explicit draft/calibration/evaluation status required")
    if material and p["status"] == "DRAFT":
        raise ValueError("Draft C2 protocol cannot execute; root must freeze it")
    if evaluation and p["status"] != "SEALED_FOR_EVALUATION":
        raise ValueError("Evaluation requires a separately frozen evaluation protocol")
    if p["N"] != 67 or p["origin"] != [19, 54, 5] or p["base_prefix"] != "PI03.TC.R01":
        raise ValueError("Inherited N67/Q/eligibility prefix only; no substitute organization")
    if p["calibration_values"] != [0, 4, 6]:
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
        if type(row["valor"]) is int and row["valor"] in (0, 4, 6):
            return
        raise ValueError("Only preregistered0/4/6 calibration values")
    if mode == ADMIT:
        if row.get("brazo") in ARMS - {"yoked", "context_cut"} and set(row) == {"modo", "brazo"}:
            return
        if row.get("brazo") == "yoked" and set(row) == {"modo", "brazo", "plan"}:
            _pure().validate_plan(_pure().unpack_plan(row["plan"]))
            return
        raise ValueError("Fixed real/none/link_cut/actuator_null arm or a sealed yoked plan only")
    raise ValueError("Unknown C2 operation/fields; no target, action, answer, path or reader argument")


def _identity(a, directory=None):
    p, ph = protocol(material=True)
    r01, _ = _hardware().protocol()
    identity = _hardware()._identity(a, r01, directory)
    if not identity["life_id"].startswith(PREFIX) or int(a.world.runtime.dimension) != 67:
        raise ValueError("Only an explicit inherited PI04 clone, never current protected MAIN")
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


def _require_original_NULL(a, directory=None):
    """Read/verify the old halted future; NEVER edit or reclassify it."""
    old = _module("pi04_coordinacion_adquirida")
    previous = old._get(a)
    if not previous.get("admitted") or previous.get("arm") != "real" or previous.get("ordinal") != 11:
        raise ValueError("C2B preparation requires the actual closed old C2 real ordinal11")
    if previous.get("pending") or previous.get("uncertain") or not str(previous.get("halted_reason", "")).startswith("First NULL/"):
        raise ValueError("Old first-NULL future must remain halted but coherent, with no pending uncertainty")
    rows = previous.get("rows", [])
    if len(rows) != 11 or rows[-1].get("first_choice") is not None or sum(row.get("first_choice") is None for row in rows) != 1:
        raise ValueError("Exactly one first NULL in the last recorded old C2 opportunity required")
    proof = None
    if directory is not None:
        proof = old.operational_dependencies(a, directory)
        if proof.get("pending") or proof.get("uncertain") or proof.get("device_pending") or proof.get("device_feedback_pending") or proof.get("device_uncertain"):
            raise ValueError("Old C2 complete device/journal is not coherent; no repair/clear performed")
    raw = json.dumps(_jsonsafe(previous), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf8")
    return {"old_KEY": old.KEY, "old_folder": old.FOLDER, "old_state_sha256": _sha(raw),
            "old_ordinal": 11, "old_halt_preserved": previous["halted_reason"],
            "old_last_tick": rows[-1]["after_tick"], "dependencies_checked": proof is not None,
            "scope": "Original C2 remains physical/history evidence; no counter, device, log or metadata rewritten"}


def validate(a, row):
    validate_literal(row)
    if row["modo"] == STATE:
        return
    p, ph, identity = _identity(a)
    if row["modo"] == PREPARE:
        _require_original_NULL(a)
        if KEY in _entries(a):
            raise ValueError("C2 already prepared; no reinstallation or reference reset")
        return
    m = _get(a)
    if m.get("pending") or m.get("uncertain") or m.get("halted_reason"):
        raise ValueError("Preserve C2 pending/uncertain/halted future; do not resend")
    if not m.get("ready"):
        raise ValueError("C2 sensory preparation is not completely admitted")
    if row["modo"] == CALIBRATE:
        if not identity["life_id"][len(PREFIX):].startswith("C2BCAL") or m.get("admitted"):
            raise ValueError("Sensor calibration only in an explicitly named C2BCAL diagnostic, never candidate/MAIN")
        if p["status"] != "SEALED_FOR_CALIBRATION":
            raise ValueError("Explicit frozen calibration protocol required")
        if len(m.get("calibrations", [])) >= len(p["calibration_values"]):
            raise ValueError("Finite three-call calibration horizon consumed; no unlimited reader search")
        return
    protocol(material=True, evaluation=True)
    if row["modo"] == CUT_CONTEXT:
        _validate_context_cut(p, identity, m)
        return
    if identity["life_id"][len(PREFIX):].startswith("C2BCAL") or m.get("calibrations"):
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
        raise ValueError("The predeclared20-opportunity yoked control is exhausted; no invented future signals")
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
        "omitted": "Only the later pair of identical symmetric scalar context datum events; no material replacement0",
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
    points = {"A": (-1,-1,0), "B": (1,-1,0), "Q": (0,0,0), "datum": (-1,0,1), "datum_symmetric": (-1,0,-1),
              "eligibility_hub": (0,-1,-2), "postread_support": (0,3,0)}
    return {"label": label, "physical": _physical(a),
            "fields": {name: observe(a.world, helper.at(origin, offset)) for name, offset in points.items()}}


def prepare(a, directory):
    p, ph, identity = _identity(a, directory)
    home = _home(directory)
    if home.exists() or KEY in _entries(a):
        raise ValueError("Existing C2 state/files preserved; never overwrite or silently retry")
    previous_closed = _require_original_NULL(a, directory)
    before = _physical(a)
    m = {"version": VERSION, "life_id": identity["life_id"], "prepared_tick": int(a.tick),
         "prepared_physical": None, "ready": False, "admitted": False, "calibrations": [],
         "pending": {"phase":"explicit_sensor_preparation"}, "uncertain": True, "halted_reason": None,
         "log_count": 0, "log_chain_sha256": "00"*32,
         "previous_C2_preserved": previous_closed,
         "attribution": "External symmetric sensory interface only; same inherited banks/history; no old reset"}
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
    requests.extend(_sensor().submit_datum(a, row["valor"], q))
    a.run_until(q+6); reader = _sensor().read_fixed(a, q)
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


def _opportunity_body(a,directory):
    validate(a,{"modo":OPPORTUNITY}); p,ph,identity=_identity(a,directory); m=_get(a); device=_device(directory)
    if device.m["ordinal"] != m["ordinal"] or device.m["pending"] or device.m["feedback_pending"] or device.m["uncertain"]:
        raise ValueError("Complete C2/device progress mismatch; no counter reset")
    start=int(a.tick); banks=_banks(a)
    if int(banks[0]["clock"])%782 != int(banks[1]["clock"])%782:
        raise ValueError("Inherited bank phases differ; no repair")
    cal=_helper().schedule_trial(start,int(banks[0]["clock"]),p["delay_laps"])
    q=cal["query_tick"]; ready=cal["outcome_injection_tick"]-1; end=cal["contact_tick"]+2
    if end-start>p["max_ticks_per_opportunity"] or ready-cal["query_read_tick"]<p["processing_budget_ticks"]:
        raise ValueError("Predeclared calendar cannot contain this finite real processing sequence")
    normalized=_calendar_view(cal,banks,start); _pure().checked_calendar(normalized)
    if m["arm"]=="yoked":
        _pure().replay_signal(m["plan"],m["ordinal"],normalized) # verify BEFORE material input
    spec=p["schedule"][m["ordinal"]]
    m["uncertain"]=True; m["pending"]={"phase":"first_query","ordinal":m["ordinal"],"calendar":cal}
    _save(a,m)
    _record(a,m,directory,{"kind":"C2_OPPORTUNITY_INTENT","spec":spec,"calendar":cal,"arm":m["arm"],"before":_frame(a,"before")})
    requests=_helper().submit_query(a.world,q,prefix=p["base_prefix"])
    if m["arm"] != "context_cut":
        requests.extend(_sensor().submit_datum(a,spec["context"],q))
    # context_cut omits BOTH symmetric datum events entirely: no zero/sham/replacement.
    # All generic queries, six-site reader, real Native functions and feedback remain.
    a.run_until(cal["query_read_tick"]); first_reader=_sensor().read_fixed(a,q)
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
    action=device.begin(applied_route,operation,numeric,spec["context"],int(a.tick),ready)
    m["pending"]={"phase":"actual_second_action_inflight","ordinal":m["ordinal"],"calendar":cal,
                  "request_ids":[r["id"]for r in requests]}; _save(a,m)
    _record(a,m,directory,{"kind":"C2_SECOND_NATIVE_USE_AND_ACTION","second":second,
                          "second_motor":second_motor,"applied_route":applied_route,"action":action,
                          "after":_frame(a,"after_second_decision"),
                          "assistance":"Fixed result identity codec and route transduction; no host numeric threshold or action calculation in actor path"})
    a.run_until(ready); effect=device.complete(ready)
    actual_failed=effect["failed"]
    returned_failed=(False if m["arm"]=="none" else _pure().replay_signal(m["plan"],m["ordinal"],normalized)
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
    admitted=all(r["receipt"]["status"]=="applied"for r in requests)
    result={"version":VERSION,"ordinal":m["ordinal"],"spec":spec,"arm":m["arm"],
            "before_tick":start,"after_tick":int(a.tick),"calendar":cal,"normalized_calendar":normalized,
            "context_input_supplied":m["arm"] != "context_cut",
            "first_reader":first_reader,"first_motor":first_motor,"selected_operation":operation,
            "native_arithmetic":arithmetic,"actual_numeric_result":numeric,"second_native_use":second,
            "second_motor":second_motor,"applied_route":applied_route,"actual_effect":effect,
            "actual_failed":actual_failed,"returned_failed":returned_failed,"requests":requests,
            "reconciliation":reconciliation,"bank_before":banks,"bank_after":_banks(a),
            "useful_product":effect["product"]is not None,"first_NULL_preserved":null_seen,
            "scope":"Acquired first capability selection requires history controls. Sequence/codec/calendar/device are prepared; actual Native result feeds Native second choice. Not discovered planning or general agency."}
    m["ordinal"]+=1
    m["rows"].append({"ordinal":result["ordinal"],"stage":spec["stage"],"context":spec["context"],
                      "first_choice":first_choice,"operation":operation,"actual_numeric_result":numeric,
                      "second_choice":None if second_reader is None else second_reader["choice"],
                      "useful_product":result["useful_product"],"actual_failed":actual_failed,
                      "returned_failed":returned_failed,"after_tick":int(a.tick)})
    m["uncertain"]=not admitted or not reconciliation["finished"]
    m["pending"]=None if not m["uncertain"] else {"phase":"rejected_or_unreconciled_preserved"}
    if null_seen:
        m["halted_reason"]="First NULL/invalid actual numeric response preserved after actual failure and generic return; no retry"
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
    _identity(a,directory)
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
