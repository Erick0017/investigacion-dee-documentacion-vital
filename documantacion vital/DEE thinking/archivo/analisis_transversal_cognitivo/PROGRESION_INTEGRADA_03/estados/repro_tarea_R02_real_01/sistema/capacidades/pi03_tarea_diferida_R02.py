"""Draft PI03 useful delayed task through the existing owned ECI02 world.

No Native import or execution at module import. Uses R01's prepared physical
banks but never modifies its sealed code, protocol or progress. Geometry,
decoder, inverse efference and generic outcome ports are fixed before reserve.
The host offers opportunities and models a device; it never chooses DEE's
action, the useful route or the bank to update after a consequence.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import os

VERSION = "PI03.useful_delayed_task.R02_DRAFT"
KEY = "DEE.Cognitive.PI03.useful_delayed_task.R02"
FOLDER = "PI03_TAREA_DIFERIDA_R02"
PROTOCOL = Path(__file__).with_name("PROTOCOLO_PI03_TAREA_R02.json")
ADMIT = "eci01-pi03-tarea-admitir"
OPPORTUNITY = "eci01-pi03-tarea-oportunidad"
STATE = "eci01-pi03-tarea-estado"
MODES = {ADMIT, OPPORTUNITY, STATE}
CONTROLS = {"real", "return_nonfailure", "actuator_null"}
_MODULES = {}


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _module(name):
    if name not in _MODULES:
        file = Path(__file__).with_name(name + ".py")
        spec = importlib.util.spec_from_file_location("pi03_task_" + name, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _MODULES[name] = module
    return _MODULES[name]


def _r1():
    return _module("progresion_integrada_03_R01")


def _helper():
    return _r1()._helper()


def _device(directory):
    return _module("pi03_dispositivo_diferido_R02_PROPUESTA").DelayedFeeder(Path(directory) / FOLDER / "dispositivo")


def _decode(value):
    from dee_thinking.persistence import decode_metadata
    return decode_metadata(value)


def _save(a, m):
    from dee_thinking.persistence import encode_metadata
    a.world.runtime.set_snapshot_metadata(KEY, encode_metadata(m))


def _get(a):
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:
        raise ValueError("Task has not been admitted; no implicit device or resource reset")
    m = _decode(entries[KEY])
    if m["version"] != VERSION:
        raise ValueError("Task snapshot revision differs from code")
    return m


def protocol(*, executable=True):
    data = PROTOCOL.read_bytes()
    p = json.loads(data)
    required = {"schema", "status", "r01_protocol_sha256", "device_sha256", "fixtures",
                "max_ticks_per_opportunity", "resource_source", "native_arithmetic",
                "null_stop", "attribution"}
    if set(p) != required or p["schema"] != "PI03.useful_delayed_task.protocol.v1":
        raise ValueError("Exact fixed task protocol only; no target/action/reader override")
    if executable and p["status"] != "SEALED_FOR_TASK":
        raise ValueError("Task draft is not executable; freeze protocol after R01 calibration")
    if p["resource_source"] not in ("fixture", "native_arithmetic_chain"):
        raise ValueError("One declared resource source, no fallback between sources")
    if p["native_arithmetic"] != {"first_operation": "suma", "first_operands": [4, 5], "second_operation": "diferencia", "second_right_operand": 2, "codec": "actual_final_uint16_little_endian_plus_62_zero_bytes"}:
        raise ValueError("This draft has one fixed bounded arithmetic data transport")
    if p["null_stop"] != "after_preserving_first_null_opportunity" or p["max_ticks_per_opportunity"] != 1500:
        raise ValueError("Frozen finite budget and no-silence-rescue criterion only")
    if set(p["fixtures"]) != {"development", "reserved"}:
        raise ValueError("Separate finite development and reserved fixture laws required")
    for series, count, delays in (("development", 6, (1, 2)), ("reserved", 8, (3, 4))):
        f = p["fixtures"][series]
        if set(f) != {"blocks", "delay_laps"} or len(f["delay_laps"]) != count or any(type(k) is not int or k not in delays for k in f["delay_laps"]):
            raise ValueError("Frozen six-development/eight-reserved delay law only")
        if sum(b["opportunities"] for b in f["blocks"]) != count:
            raise ValueError("Device block and opportunity denominators differ")
        for b in f["blocks"]:
            if set(b) != {"opportunities", "connected_motor"} or type(b["opportunities"]) is not int or not 1 <= b["opportunities"] <= count or type(b["connected_motor"]) is not int or b["connected_motor"] not in (-1, 1):
                raise ValueError("Invalid bounded physical environment law")
    if executable:
        _, r01_sha = _r1().protocol()
        if r01_sha != p["r01_protocol_sha256"]:
            raise ValueError("Task does not identify the exact sealed R01 hardware protocol")
        file = Path(__file__).with_name("pi03_dispositivo_diferido_R02_PROPUESTA.py")
        if _hash(file.read_bytes()) != p["device_sha256"]:
            raise ValueError("Device source differs from frozen task protocol")
    return p, _hash(data)


def validate_literal(row):
    mode = row.get("modo") if isinstance(row, dict) else None
    if mode == ADMIT:
        if set(row) != {"modo", "serie", "control"} or row["serie"] not in ("continuous", "development") or row["control"] not in CONTROLS:
            raise ValueError("Admit one finite continuous or development-only trajectory and fixed control; no target/action")
        return
    if mode in (OPPORTUNITY, STATE):
        if set(row) != {"modo"}:
            raise ValueError("Only modo; next opportunity, delays and observations follow frozen protocol")
        return
    raise ValueError("Unknown PI03 delayed-task operation")


def _guard(a, directory=None, *, material=True):
    p, ph = protocol()
    r01, _ = _r1().protocol()
    if material:
        identity = _r1()._identity(a, r01, directory)
    else:
        entries = dict(a.world.runtime.snapshot_metadata_entries)
        if _r1().SYSTEM_KEY not in entries:
            raise ValueError("Complete existing Cognitive identity metadata required")
        identity = _decode(entries[_r1().SYSTEM_KEY])
        if not identity["life_id"].startswith(r01["diagnostic_life_prefix"]) or int(a.world.runtime.dimension) != r01["N"]:
            raise ValueError("Read-only dependency identity differs from the inherited task life")
    if directory is not None and Path(directory).resolve().name != identity["life_id"]:
        raise ValueError("Task directory must identify this exact owned life")
    hardware = _r1()._get(a)
    if not hardware.get("ready") or hardware.get("uncertain") or hardware.get("pending") or hardware.get("calibrations"):
        raise ValueError("Use a complete unlearned prepared R01 prefix, not a calibrated/control memory")
    return p, ph, r01, identity


def validate(a, row):
    validate_literal(row)
    if row["modo"] == STATE:
        return
    p, ph, r01, identity = _guard(a)
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    if row["modo"] == ADMIT:
        if KEY in entries:
            raise ValueError("Task/resources already admitted; preserve cumulative history, never reset")
        return
    m = _get(a)
    if m["protocol_sha256"] != ph or not m["ready"]:
        raise ValueError("Installed finite task and exact sealed protocol differ")
    if m.get("pending") or m.get("uncertain") or m.get("halted_reason"):
        raise ValueError("Pending, uncertain or halted task; no replay or silent rescue")
    if m["opportunity"] >= len(m["schedule"]):
        raise ValueError("Prepared stock/opportunities exhausted; no automatic replenishment")


def _record(a, m, directory, event):
    home = Path(directory) / FOLDER
    home.mkdir(parents=True, exist_ok=True)
    event = {"index": m["log_count"], "tick": int(a.tick), **event}
    data = (json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    with (home / "eventos.jsonl").open("ab") as out:
        out.write(data)
        out.flush()
        os.fsync(out.fileno())
    m["log_count"] += 1
    m["log_chain_sha256"] = _hash(bytes.fromhex(m["log_chain_sha256"]) + data)
    _save(a, m)


def _source_payload(a, p):
    """Actual Native output transported by a fixed codec; no expected number."""
    if p["resource_source"] == "fixture":
        return None, {"kind": "external_fixture", "native_acquisition_claim": False}
    from capacidades import aritmetica_directa_eci02 as arithmetic
    config = p["native_arithmetic"]
    first = arithmetic.execute(a, {"modo": arithmetic.MODE, "operacion": config["first_operation"],
                                   "izquierda": config["first_operands"][0], "derecha": config["first_operands"][1]})
    intermediate = first["numeric_result"]
    if type(intermediate) is not int or not 0 <= intermediate <= 32:
        raise ValueError("Actual first Native arithmetic result is NULL/outside next operand domain; no expected-result fallback")
    second = arithmetic.execute(a, {"modo": arithmetic.MODE, "operacion": config["second_operation"],
                                    "izquierda": intermediate, "derecha": config["second_right_operand"]})
    result = second["numeric_result"]
    if type(result) is not int or not 0 <= result <= 65535:
        raise ValueError("Actual final Native arithmetic result is NULL/outside literal payload codec; no fixture fallback")
    payload = result.to_bytes(2, "little", signed=False) + bytes(62)
    return payload, {"kind": "assisted_native_arithmetic_data_chain", "first": first, "second": second,
                     "actual_final_result": result, "payload_bytes": len(payload), "payload_sha256": _hash(payload),
                     "scope": "Operator-prepared arithmetic requests; real first output feeds second and real final output feeds external resources. Not a discovered plan."}


def admit(a, row, directory):
    p, ph, r01, identity = _guard(a, directory)
    home = Path(directory) / FOLDER
    if home.exists():
        raise ValueError("Unmatched existing task files are preserved, never overwritten")
    series = ["development", "reserved"] if row["serie"] == "continuous" else ["development"]
    schedule = [{"series": s, "index_within_series": k, "delay_laps": delay}
                for s in series for k, delay in enumerate(p["fixtures"][s]["delay_laps"])]
    blocks = [dict(b) for s in series for b in p["fixtures"][s]["blocks"]]
    m = {"version": VERSION, "protocol_sha256": ph, "life_id": identity["life_id"],
         "admitted_tick": int(a.tick), "serie": row["serie"], "control": row["control"],
         "schedule": schedule, "opportunity": 0, "ready": False, "uncertain": True,
         "pending": {"phase": "preparing_actual_resource_source"}, "halted_reason": None,
         "products": [], "rejections": [], "rows": [], "log_count": 0,
         "log_chain_sha256": "00" * 32,
         "attribution": "External task/progress only; actor choices are never read from this capsule"}
    _save(a, m)
    _record(a, m, directory, {"kind": "TASK_ADMISSION_INTENT", "protocol": p, "identity": identity,
                            "series": row["serie"], "control": row["control"]})
    # No eligibility is outstanding during this assisted source preparation.
    _record(a, m, directory, _r1()._frame(a, r01, "before_actual_resource_source"))
    payload, source = _source_payload(a, p)
    _record(a, m, directory, _r1()._frame(a, r01, "after_actual_resource_source"))
    payloads = None if payload is None else [payload for _ in schedule]
    device_class = _module("pi03_dispositivo_diferido_R02_PROPUESTA").DelayedFeeder
    device_class.prepare(home / "dispositivo", blocks, fixture_id="PI03.R02.fixed_task", payloads=payloads)
    m["resource_source"] = source
    m["ready"] = True
    m["uncertain"] = False
    m["pending"] = None
    _record(a, m, directory, {"kind": "FINITE_DEVICE_ADMITTED", "opportunities": len(schedule),
                            "resource_source": source, "actual_native_source_consumes_ticks": p["resource_source"] != "fixture"})
    return {"version": VERSION, "admitted": True, "new_native_ticks": int(a.tick) - m["admitted_tick"],
            "opportunities": len(schedule), "resource_source": source,
            "scope": "Finite external apparatus/source preparation. No route taught or selected by this operation."}


def _bank_observations(a, r01):
    from app.native_tools import observe
    return [observe(a.world, _helper().at(r01["origin"], delta)) for delta in ((-1, -1, 0), (1, -1, 0))]


def opportunity(a, directory):
    p, ph, r01, identity = _guard(a, directory)
    m = _get(a)
    device = _device(directory)
    if device.m["opportunity"] != m["opportunity"] or device.m["pending"] is not None or device.m["feedback_pending"] is not None or device.m["uncertain"]:
        raise ValueError("Full task/device progress is not coherent; no reset or resend")
    start = int(a.tick)
    before_banks = _bank_observations(a, r01)
    if int(before_banks[0]["clock"]) % 782 != int(before_banks[1]["clock"]) % 782:
        raise ValueError("Acquired bank clocks diverged; no phase repair")
    spec = m["schedule"][m["opportunity"]]
    helper = _helper()
    calendar = helper.schedule_trial(start, int(before_banks[0]["clock"]), spec["delay_laps"])
    ready_tick = calendar["outcome_injection_tick"] - 1
    end_tick = calendar["contact_tick"] + 2
    if end_tick - start > p["max_ticks_per_opportunity"]:
        raise ValueError("Fixed useful opportunity exceeds finite1500tick bound")
    m["uncertain"] = True
    m["pending"] = {"phase": "query_planned", "calendar": calendar, "spec": spec,
                    "opportunity": m["opportunity"], "request_ids": []}
    _record(a, m, directory, {"kind": "OPPORTUNITY_INTENT", "calendar": calendar,
                            "spec": spec, "bank_before": before_banks})
    requests = helper.submit_query(a.world, calendar["query_tick"], prefix=r01["prefix"])
    m["pending"]["request_ids"] = [r["id"] for r in requests]
    _save(a, m)
    a.run_until(calendar["query_read_tick"])
    reader = helper.read_fixed(a.world, r01["origin"])
    choice = reader["choice"]
    emitted_motor = r01["zero_motor"] if choice == 0 else choice
    if type(emitted_motor) is not int or emitted_motor not in (-1, 1):
        emitted_motor = None
    applied_motor = None if m["control"] == "actuator_null" else emitted_motor
    action = device.begin(applied_motor, int(a.tick), ready_tick)
    copy = None
    if emitted_motor is not None:
        # Fixed efference copies the material motor command BEFORE the declared
        # downstream actuator-null cut; it never substitutes an optimal action.
        copy = helper.submit_motor_copy(a.world, emitted_motor, calendar["seed_tick"], prefix=r01["prefix"])
        requests.append(copy)
    m["pending"] = {"phase": "actual_effect_inflight", "calendar": calendar,
                    "spec": spec, "opportunity": m["opportunity"],
                    "request_ids": [r["id"] for r in requests]}
    _record(a, m, directory, {"kind": "ACTUAL_MOTOR_AND_EFFERENCE", "reader": reader,
                            "emitted_motor": emitted_motor, "applied_motor": applied_motor,
                            "material_zero_default": choice == 0, "action": action, "copy_request": copy,
                            "scope": "Zero is a declared fixed actuator default; NULL remains no-action. Consequence path stores no chosen bank."})
    frames = {calendar["seed_tick"] + 1: "eligibility_first_step",
              calendar["seed_tick"] + 33: "eligibility_half_lap",
              ready_tick: "actual_delayed_environment_consequence",
              calendar["outcome_injection_tick"]: "generic_future_input_boundary",
              calendar["collision_tick"]: "native_hub_composition",
              calendar["contact_tick"]: "native_bank_contact",
              calendar["contact_tick"] + 1: "bank_update_and_disposal",
              end_tick: "settled_contact_context"}
    if spec["delay_laps"] > 1:
        frames[calendar["seed_tick"] + 67] = "eligibility_one_lap"
    effect = None
    returned_failed = None
    outcome = None
    for tick, label in sorted(frames.items()):
        a.run_until(tick)
        if tick == ready_tick:
            effect = device.complete_due(tick)
            # Only actual generic consequence (or declared constant control).
            # There is no motor/route lookup, expected value or bank parameter.
            returned_failed = False if m["control"] == "return_nonfailure" else effect["failed"]
            outcome = helper.submit_generic_outcome(a.world, returned_failed,
                        calendar["outcome_injection_tick"], prefix=r01["prefix"])
            requests.append(outcome)
            device.mark_feedback_scheduled(outcome["id"], outcome["requested_tick"])
            m["pending"] = {"phase": "generic_outcome_scheduled", "calendar": calendar,
                            "spec": spec, "opportunity": m["opportunity"],
                            "request_ids": [r["id"] for r in requests],
                            "generic_failed": returned_failed}
            _record(a, m, directory, {"kind": "ACTUAL_DELAYED_EFFECT_AND_GENERIC_RETURN", "effect": effect,
                                    "returned_failed": returned_failed, "outcome_request": outcome})
        _record(a, m, directory, _r1()._frame(a, r01, label))
    receipts = _r1()._receipts(a, requests)
    if outcome is None:
        raise RuntimeError("Frozen consequence boundary was not executed; preserve pending future")
    outcome_receipt = next(r["receipt"] for r in receipts if r["id"] == outcome["id"])
    reconciliation = device.reconcile_feedback(outcome_receipt)
    admitted = all(r["receipt"]["status"] == "applied" for r in receipts)
    after_banks = _bank_observations(a, r01)
    result = {"version": VERSION, "opportunity": m["opportunity"], "spec": spec,
              "control": m["control"], "before_tick": start, "after_tick": int(a.tick),
              "new_native_ticks": int(a.tick) - start, "calendar": calendar,
              "reader": reader, "emitted_motor": emitted_motor, "applied_motor": applied_motor,
              "actual_effect": effect, "returned_failed": returned_failed,
              "requests": receipts, "reconciliation": reconciliation,
              "bank_before": before_banks, "bank_after": after_banks,
              "useful_product": bool(effect and not effect["failed"]),
              "attribution": "Native relative-bank selection and eligibility interaction; offered query/calendar, inverse efference, zero default, device law and transduction prepared. Useful learning requires controls."}
    m["opportunity"] += 1
    m["rows"].append({"opportunity": result["opportunity"], "spec": spec,
                      "reader_choice": choice, "useful_product": result["useful_product"],
                      "effect_sha256": effect["actual_product_sha256"], "after_tick": int(a.tick)})
    m["products"] = list(device.m["products"])
    m["rejections"] = list(device.m["rejections"])
    m["uncertain"] = not admitted or not reconciliation["finished"]
    m["pending"] = None if not m["uncertain"] else {"phase": "rejected_or_unreconciled_preserved", "request_ids": [r["id"] for r in requests]}
    if choice is None:
        m["halted_reason"] = "First NULL reader preserved, actual no-action/rejection and generic return recorded; diagnostic required before new opportunities"
    _record(a, m, directory, {"kind": "OPPORTUNITY_COMPLETED", "result": result})
    return result


def state(a, directory=None):
    from app.native_tools import physical
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    result = {"version": VERSION, "admitted": KEY in entries, "new_native_ticks": 0,
              "physical": physical(a.world, occupation=True),
              "scope": "Passive instrument/progress; no material query or automatic repair"}
    if KEY in entries:
        m = _get(a)
        result["progress"] = m
        result["remaining_opportunities"] = len(m["schedule"]) - m["opportunity"]
        if directory is not None:
            result["device"] = _device(directory).m
    return result


def dispatch(a, row, *, directory=None, actuator="closed"):
    validate(a, row)
    if row["modo"] == STATE:
        return state(a, directory)
    if directory is None or actuator != "closed":
        raise ValueError("Explicit owned diagnostic directory; actuator control is frozen at task admission")
    if row["modo"] == ADMIT:
        return admit(a, row, directory)
    return opportunity(a, directory)


def uncertain(a):
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    return KEY in entries and bool(_get(a).get("uncertain"))


def operational_dependencies(a, directory):
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:
        return {"version": VERSION, "admitted": False, "new_native_ticks": 0}
    p, ph, r01, identity = _guard(a, directory, material=False)
    m = _get(a)
    if m["protocol_sha256"] != ph:
        raise ValueError("Exact task code/protocol differs from snapshot")
    home = Path(directory) / FOLDER
    journal = home / "eventos.jsonl"
    chain = "00" * 32
    count = 0
    with journal.open("rb") as rows:
        for line in rows:
            json.loads(line)
            chain = _hash(bytes.fromhex(chain) + line)
            count += 1
    if count != m["log_count"] or chain != m["log_chain_sha256"]:
        raise ValueError("Task snapshot/journal mismatch; preserve and reconcile without replay")
    device = _device(directory)
    if device.m["opportunity"] != m["opportunity"] and not m["pending"]:
        raise ValueError("Task/device opportunity mismatch outside a preserved in-flight operation")
    verified = []
    for product in device.m["products"]:
        relative = Path(product["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Only bounded relative device product paths")
        file = home / "dispositivo" / relative
        if file.parent.resolve() != (home / "dispositivo" / "products").resolve() or not file.is_file() or file.stat().st_size != product["bytes"] or _hash(file.read_bytes()) != product["sha256"]:
            raise ValueError("Missing/altered useful product; no counter-only success")
        verified.append({"path": str(file), "bytes": product["bytes"], "sha256": product["sha256"]})
    # Validate each complete finite encoded resource. Exactly one physical
    # location is legitimate, including during an in-flight continuation.
    resource_rows = []
    for capsule in device.m["capsules"]:
        if Path(capsule["name"]).name != capsule["name"]:
            raise ValueError("Invalid stored capsule name")
        candidates = [home / "dispositivo" / folder / capsule["name"] for folder in
                      ("reservoir", "inflight_minus", "inflight_plus", "inflight_silence", "products", "rejected")]
        present = [file for file in candidates if file.is_file()]
        if len(present) != 1 or present[0].stat().st_size != capsule["compressed_bytes"] or _hash(present[0].read_bytes()) != capsule["compressed_sha256"]:
            raise ValueError("Incomplete, duplicated or altered actual device resource; no regenerated substitute")
        resource_rows.append({"path": str(present[0]), "bytes": capsule["compressed_bytes"], "sha256": capsule["compressed_sha256"]})
    device_events = home / "dispositivo" / "EVENTOS_DISPOSITIVO.jsonl"
    event_count = 0
    if device_events.is_file():
        with device_events.open("rb") as lines:
            for line in lines:
                json.loads(line)
                event_count += 1
    if event_count != device.m["events"]:
        raise ValueError("Device event journal and progress count differ")
    # R01 preparation journal remains necessary and unchanged. Validate its
    # bytes/chain read-only without calling its material main-life guard.
    hardware = _r1()._get(a)
    hardware_journal = Path(directory) / _r1().FOLDER / "eventos.jsonl"
    hardware_chain = "00" * 32
    hardware_count = 0
    with hardware_journal.open("rb") as lines:
        for line in lines:
            json.loads(line)
            hardware_chain = _hash(bytes.fromhex(hardware_chain) + line)
            hardware_count += 1
    if hardware_count != hardware["log_count"] or hardware_chain != hardware["log_chain_sha256"]:
        raise ValueError("R01 prepared-prefix snapshot/journal mismatch")
    return {"version": VERSION, "admitted": True, "protocol_sha256": ph,
            "journal": str(journal), "journal_sha256": _hash(journal.read_bytes()),
            "device_state": str(device.statefile), "device_state_sha256": _hash(device.statefile.read_bytes()),
            "opportunity": m["opportunity"], "remaining": len(m["schedule"]) - m["opportunity"],
            "pending": m["pending"], "generic_feedback_pending": device.m["feedback_pending"],
            "uncertain": m["uncertain"] or device.m["uncertain"], "actual_verified_products": verified,
            "actual_verified_resources": resource_rows,
            "prepared_R01_journal": str(hardware_journal), "prepared_R01_journal_sha256": _hash(hardware_journal.read_bytes()),
            "complete_state_requirement": "Preserve entire task folder/device/artifacts with complete Native snapshot/interfaces/agenda/receipts and existing owner SQLite/outbox transport. Do not copy a live database incoherently."}
