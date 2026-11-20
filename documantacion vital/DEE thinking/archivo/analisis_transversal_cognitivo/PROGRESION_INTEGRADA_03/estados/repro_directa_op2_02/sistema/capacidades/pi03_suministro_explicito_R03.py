"""Explicit bounded external resupply AFTER PI03 R02's completed reserve.

Separate extension: does not edit frozen R01/R02. It appends offers/resources,
never resets a counter, creates a life, selects an action or promotes a main.
The default reuses bytes from a documented actual Native arithmetic product;
optional recalculation is a separate prepared Native use before eligibility.
Import/literal/core validation use no DEE. The existing owner must checkpoint
the changed full world/metadata, task/device files and transport coherently.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import zlib

VERSION = "PI03.explicit_bounded_environment_supply.R03_DRAFT"
MODE = "eci01-pi03-tarea-suministrar"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def _canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def validate_literal(row):
    base = {"modo", "cantidad", "conexion", "demora_periodos"}
    if not isinstance(row, dict) or set(row) not in (base, base | {"recalcular_fuente"}) or row["modo"] != MODE:
        raise ValueError("Exact explicit supply fields; no answer/route/reader or arbitrary resource path")
    if type(row["cantidad"]) is not int or not 1 <= row["cantidad"] <= 4:
        raise ValueError("Only1..4 explicitly supplied new external offers")
    if type(row["conexion"]) is not int or row["conexion"] not in (-1, 1):
        raise ValueError("Fixed external conduit configuration -1/+1; not a Native answer")
    if type(row["demora_periodos"]) is not int or not 1 <= row["demora_periodos"] <= 4:
        raise ValueError("Declared physical delay1..4 laps only")
    if "recalcular_fuente" in row and type(row["recalcular_fuente"]) is not bool:
        raise ValueError("Optional source recalculation flag must be an exact bool")


def _source_from_state(m):
    if "current_resource_source" in m:
        return m["current_resource_source"]
    if "resource_source" in m and "data_source" in m and m["resource_source"] != m["data_source"]:
        raise ValueError("Ambiguous historical source aliases; do not choose a favorable one")
    if "resource_source" in m:
        return m["resource_source"]
    if "data_source" in m:
        return m["data_source"]
    raise ValueError("No preserved actual Native resource provenance; no expected7/fixture fallback")


def payload_from_actual_source(source):
    """Fixed transport of a recorded real result, never an expected answer."""
    if not isinstance(source, dict) or source.get("kind") != "assisted_native_arithmetic_data_chain":
        raise ValueError("This supply extension requires the documented actual Native arithmetic chain")
    first, second = source.get("first"), source.get("second")
    if not isinstance(first, dict) or not isinstance(second, dict):
        raise ValueError("Complete preserved first/second Native results are required")
    intermediate = first.get("numeric_result")
    result = second.get("numeric_result")
    if type(intermediate) is not int or not 0 <= intermediate <= 32 or type(result) is not int or not 0 <= result <= 65535:
        raise ValueError("Actual source NULL/outside the frozen literal codec; no fallback")
    if source.get("actual_final_result") != result or second["literal_operator_request"]["izquierda"] != intermediate:
        raise ValueError("Actual first-to-second source transport is not coherent")
    for trial in (first, second):
        reader = trial.get("numeric_reader", {})
        if reader.get("fixed_site_direction_valid") is not True or reader.get("numeric_result") != trial["numeric_result"]:
            raise ValueError("Preserved fixed Native numeric reader does not substantiate the source")
    payload = result.to_bytes(2, "little", signed=False) + bytes(62)
    if source.get("payload_bytes") != len(payload) or source.get("payload_sha256") != sha(payload):
        raise ValueError("Source bytes/hash differ from the recorded actual-result codec")
    return payload


def preflight(m, device, row):
    validate_literal(row)
    d = device.m
    if m.get("control") != "real" or m.get("serie") != "continuous" or not m.get("ready"):
        raise ValueError("Only the completed real continuous candidate can receive post-reserve supply")
    if m.get("uncertain") or m.get("pending") or m.get("halted_reason") or m.get("supply_pending"):
        raise ValueError("Task has an uncertain/pending/halted operation; never refill to hide it")
    if d.get("uncertain") or d.get("pending") or d.get("feedback_pending") or d.get("supply_pending"):
        raise ValueError("Device or generic feedback remains pending/uncertain")
    if m["opportunity"] != d["opportunity"] or len(m["schedule"]) != len(d["capsules"]):
        raise ValueError("Complete task/device progress is incoherent")
    if sum(b["opportunities"] for b in d["blocks"]) != len(d["capsules"]):
        raise ValueError("External connection blocks and actual resources have different denominators")
    if len(m["rows"]) != m["opportunity"] or len(d["products"]) + len(d["rejections"]) != d["opportunity"]:
        raise ValueError("Completed actual effects/task rows do not match opportunity progress")
    if m["opportunity"] < 14 or len(m["schedule"]) < 14:
        raise ValueError("Original six-development/eight-reserved opportunities must finish first")
    prefix = m["schedule"][:14]
    if [x["series"] for x in prefix] != ["development"] * 6 + ["reserved"] * 8:
        raise ValueError("Do not relabel another trajectory as the completed R02 reserve")
    remaining = len(m["schedule"]) - m["opportunity"]
    if remaining < 0 or remaining + row["cantidad"] > 4:
        raise ValueError("At most four explicitly outstanding external offers; no unlimited refill")
    source = _source_from_state(m)
    payload = payload_from_actual_source(source)
    if not any(c["decoded_bytes"] == len(payload) and c["decoded_sha256"] == sha(payload) for c in d["capsules"]):
        raise ValueError("Recorded current source has no matching preserved real device resource")
    # Every old resource must remain at exactly one bounded location.
    for c in d["capsules"]:
        if Path(c["name"]).name != c["name"]:
            raise ValueError("Unbounded old resource filename")
        files = [device.home / f / c["name"] for f in
                 ("reservoir", "inflight_minus", "inflight_plus", "inflight_silence", "products", "rejected")]
        present = [f for f in files if f.is_file()]
        if len(present) != 1 or present[0].stat().st_size != c["compressed_bytes"] or sha(present[0].read_bytes()) != c["compressed_sha256"]:
            raise ValueError("Old material resource missing/duplicated/altered; supply cannot repair it")
    for product in d["products"]:
        relative = Path(product["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Only bounded preserved product paths")
        file = device.home / relative
        if file.parent.resolve() != (device.home / "products").resolve() or not file.is_file() or file.stat().st_size != product["bytes"] or sha(file.read_bytes()) != product["sha256"]:
            raise ValueError("Old useful product missing/altered; new supply cannot hide that loss")
    return source, payload


def append_supply(m, device, row, commit_task, *, recalculate_source=None):
    """Pure core; commit_task(event) persists this same mutable task dictionary.

    It performs actual bounded file supply but no Native import, event, query,
    clock/RAW edit or decision. A recalculation callback is explicitly supplied
    by the existing owner, before any new eligibility has been introduced.
    Partial failures remain uncertain and are never retried automatically.
    """
    source, payload = preflight(m, device, row)
    if not callable(commit_task):
        raise TypeError("Durable existing-owner task journal callback required")
    if row.get("recalcular_fuente", False) and not callable(recalculate_source):
        raise ValueError("Explicit source recalculation needs the existing owned Native callback")
    old = {"task_opportunity": m["opportunity"], "device_opportunity": device.m["opportunity"],
           "task_schedule": json.loads(json.dumps(m["schedule"])),
           "device_blocks": json.loads(json.dumps(device.m["blocks"])),
           "device_capsules": json.loads(json.dumps(device.m["capsules"])),
           "task_rows": json.loads(json.dumps(m["rows"])),
           "products": json.loads(json.dumps(device.m["products"])),
           "rejections": json.loads(json.dumps(device.m["rejections"]))}
    history = m.setdefault("resource_supply_history", [])
    supply_id = "SUPPLY_%04d" % (len(history) + 1)
    intent = {"id": supply_id, "quantity": row["cantidad"], "connection": row["conexion"],
              "delay_laps": row["demora_periodos"], "first_resource_index": len(device.m["capsules"]),
              "source_mode": "new_actual_native_use" if row.get("recalcular_fuente", False) else "reuse_recorded_actual_native_product"}
    m["uncertain"] = True
    m["pending"] = {"phase": "explicit_external_supply", "id": supply_id}
    m["supply_pending"] = dict(intent, phase="before_source_or_files")
    commit_task({"kind": "EXPLICIT_SUPPLY_INTENT", "intent": intent,
                 "scope": "Operator supplies external resources/configuration; no learned initiative or Native response is implied"})
    device.m["uncertain"] = True
    device.m["supply_pending"] = dict(intent, phase="before_source_or_files")
    device._record({"kind": "EXPLICIT_SUPPLY_INTENT", "intent": intent})
    if row.get("recalcular_fuente", False):
        payload, source = recalculate_source()
        if not isinstance(payload, bytes) or payload != payload_from_actual_source(source):
            raise ValueError("New actual Native source failed its frozen codec; no old-payload fallback")
    encoded = zlib.compress(payload, level=6)
    additions = []
    start = len(device.m["capsules"])
    for offset in range(row["cantidad"]):
        name = "%04d.zlib" % (start + offset)
        file = device.home / "reservoir" / name
        if any((device.home / folder / name).exists() for folder in
               ("reservoir", "inflight_minus", "inflight_plus", "inflight_silence", "products", "rejected")):
            raise ValueError("New supply index already exists; no overwrite or implicit retry")
        with file.open("xb") as out:
            out.write(encoded)
            out.flush()
            os.fsync(out.fileno())
        additions.append({"name": name, "compressed_bytes": len(encoded), "compressed_sha256": sha(encoded),
                          "decoded_bytes": len(payload), "decoded_sha256": sha(payload)})
    device.m["blocks"].append({"opportunities": row["cantidad"], "connected_motor": row["conexion"]})
    device.m["capsules"].extend(additions)
    device.m["supply_pending"]["phase"] = "resources_staged"
    device._record({"kind": "EXPLICIT_SUPPLY_RESOURCES_STAGED", "intent": intent, "resources": additions})
    base_supply = sum(x["series"] == "explicit_supply" for x in m["schedule"])
    offers = [{"series": "explicit_supply", "index_within_series": base_supply + k,
               "delay_laps": row["demora_periodos"], "supply_id": supply_id}
              for k in range(row["cantidad"])]
    m["schedule"].extend(offers)
    item = {**intent, "resources": additions, "source": source,
            "payload_sha256": sha(payload), "payload_bytes": len(payload),
            "prefix_before_sha256": sha(_canonical(old)),
            "not_reserved_evaluation": True}
    history.append(item)
    m["current_resource_source"] = source
    m["supply_pending"]["phase"] = "task_schedule_staged"
    commit_task({"kind": "EXPLICIT_SUPPLY_TASK_STAGED", "supply": item})
    # Original biography, products, rows, resources and counters are prefixes,
    # not values reconstructed or reset from expected results.
    preserved = (m["opportunity"] == old["task_opportunity"]
                 and device.m["opportunity"] == old["device_opportunity"]
                 and m["schedule"][:len(old["task_schedule"])] == old["task_schedule"]
                 and device.m["blocks"][:len(old["device_blocks"])] == old["device_blocks"]
                 and device.m["capsules"][:len(old["device_capsules"])] == old["device_capsules"]
                 and m["rows"] == old["task_rows"] and device.m["products"] == old["products"]
                 and device.m["rejections"] == old["rejections"])
    if not preserved:
        raise RuntimeError("Supply changed historical prefixes; preserve uncertain future")
    device.m["supply_pending"] = None
    device.m["uncertain"] = False
    device._record({"kind": "EXPLICIT_SUPPLY_DEVICE_COMPLETED", "id": supply_id, "historical_prefix_preserved": True})
    m["supply_pending"] = None
    m["pending"] = None
    m["uncertain"] = False
    commit_task({"kind": "EXPLICIT_SUPPLY_COMPLETED", "id": supply_id, "historical_prefix_preserved": True})
    return {"version": VERSION, "supply": item, "old_opportunity_unchanged": m["opportunity"],
            "total_prepared_offers": len(m["schedule"]), "remaining_offers": len(m["schedule"]) - m["opportunity"],
            "historical_prefix_preserved": True,
            "scope": "Explicit operator-provided external resources and private device connection; no policy selection, memory transfer, automatic replenishment, reset or promotion"}


def _task():
    file = Path(__file__).with_name("pi03_tarea_diferida_R02.py")
    spec = importlib.util.spec_from_file_location("pi03_supply_frozen_task", file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(a, row, *, directory=None):
    validate_literal(row)
    task = _task()
    # Supply itself does not query Native: read-only identity guards permit an
    # adopted main while leaving all reproduction/calibration guards intact.
    task._guard(a, directory, material=False)
    if row.get("recalcular_fuente", False):
        # The optional source uses the inherited FI128 reader. A paused but
        # unfinished old job is still a real pending job, never empty space.
        entries = dict(a.world.runtime.snapshot_metadata_entries)
        key = "DEE.Cognitive.PI02.continuous_workbench.R04"
        if key in entries:
            old = task._decode(entries[key])
            if old.get("enabled") or old.get("active") is not None:
                raise ValueError("Optional Native source recalculation requires an explicitly paused PI02 bridge with no unfinished FI job")
    m = task._get(a)
    if directory is not None:
        preflight(m, task._device(directory), row)


def dispatch(a, row, *, directory=None, actuator="closed"):
    if directory is None or actuator != "closed":
        raise ValueError("Existing owned work directory and explicit supply operation required")
    validate(a, row, directory=directory)
    task = _task()
    p, _, r01, _ = task._guard(a, directory, material=False)
    m = task._get(a)
    device = task._device(directory)
    from app.native_tools import physical
    before = physical(a.world)
    start = int(a.tick)
    def commit(event):
        task._record(a, m, directory, event)
    def recalculate():
        # No eligibility or work is outstanding. Recalculation uses the same
        # correct owner; its real Native ticks and all outcomes are recorded.
        task._record(a, m, directory, task._r1()._frame(a, r01, "before_explicit_supply_native_source"))
        payload, source = task._source_payload(a, p)
        task._record(a, m, directory, task._r1()._frame(a, r01, "after_explicit_supply_native_source"))
        return payload, source
    result = append_supply(m, device, row, commit,
                recalculate_source=recalculate if row.get("recalcular_fuente", False) else None)
    after = physical(a.world)
    if not row.get("recalcular_fuente", False) and before != after:
        raise RuntimeError("Pure external resupply unexpectedly altered Native RAW/clocks/tick; preserve and diagnose")
    result.update({"before": before, "after": after, "new_native_ticks": int(a.tick) - start,
                   "source_recalculated": row.get("recalcular_fuente", False),
                   "checkpoint_requirement": "Existing owner must save this exact full Native state, task/device resources/journals and transport together before another process continues"})
    return result
