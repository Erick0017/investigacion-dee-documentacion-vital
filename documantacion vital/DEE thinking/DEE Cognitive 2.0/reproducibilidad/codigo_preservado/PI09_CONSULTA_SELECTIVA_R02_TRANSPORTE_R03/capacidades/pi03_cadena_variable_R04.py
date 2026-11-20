"""Prepared variable arithmetic chain -> explicit resource supply for PI03.

Separate R04; frozen R01/R02/R03 are never changed. No DEE import on module
import, no expected8/13, host sum/difference, fixture fallback, action selection,
automatic replenishment or promotion. Arithmetic and its ordering are assisted
uses of existing Native functions. Learned feeder selection remains separate.
"""
from pathlib import Path
import importlib.util

VERSION = "PI03.actual_variable_chain_resource_supply.R04_DRAFT"
SUPPLY = "eci01-pi03-tarea-suministrar-cadena"
CUT = "eci01-pi03-tarea-cadena-corte"
STATE = "eci01-pi03-tarea-cadena-estado"
MODES = {SUPPLY, CUT, STATE}
CONTROL_PREFIX = "ECI02_PI03_CONTROL_CADENA_"
_MODULES = {}


def _module(name):
    if name not in _MODULES:
        file = Path(__file__).with_name(name + ".py")
        spec = importlib.util.spec_from_file_location("pi03_r04_" + name, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _MODULES[name] = module
    return _MODULES[name]


def _task():
    return _module("pi03_tarea_diferida_R02")


def _supply():
    return _module("pi03_suministro_explicito_R03")


def validate_literal(row):
    if not isinstance(row, dict):
        raise ValueError("One exact R04 literal required")
    mode = row.get("modo")
    if mode == STATE:
        if set(row) != {"modo"}:
            raise ValueError("Read-only chain state takes only modo")
        return
    if mode == SUPPLY:
        if set(row) != {"modo", "cantidad", "conexion", "demora_periodos", "izquierda", "derecha", "restar"}:
            raise ValueError("Exact explicit supply and independent arithmetic operands; no expected result or reader")
        _supply().validate_literal(_supply_row(row))
    elif mode == CUT:
        if set(row) != {"modo", "izquierda", "derecha", "restar"}:
            raise ValueError("Cut is an explicit first-link diagnostic, never a supply")
    else:
        raise ValueError("Unknown R04 operation")
    if any(type(row[k]) is not int or not 0 <= row[k] <= 32 for k in ("izquierda", "derecha", "restar")):
        raise ValueError("Each independent public literal operand must be an exact integer0..32")


def _supply_row(row):
    return {"modo": _supply().MODE, "cantidad": row["cantidad"], "conexion": row["conexion"],
            "demora_periodos": row["demora_periodos"], "recalcular_fuente": True}


def actual_chain(a, row, arithmetic_api):
    """Pure orchestration over an explicitly passed API; result is never solved here.

    Real use passes the existing direct Native arithmetic capability. Pure tests
    pass a visibly MOCK API. The actual first output is the second operand input.
    """
    first = arithmetic_api.execute(a, {"modo": arithmetic_api.MODE, "operacion": "suma",
                                      "izquierda": row["izquierda"], "derecha": row["derecha"]})
    intermediate = first.get("numeric_result")
    if type(intermediate) is not int or not 0 <= intermediate <= 32:
        raise ValueError("Actual first Native result is NULL/outside second-input0..32; no expected-result fallback")
    second = arithmetic_api.execute(a, {"modo": arithmetic_api.MODE, "operacion": "diferencia",
                                       "izquierda": intermediate, "derecha": row["restar"]})
    result = second.get("numeric_result")
    if type(result) is not int or not 0 <= result <= 32:
        raise ValueError("Actual second Native result is NULL/outside prepared resource0..32; no fixture/old-payload fallback")
    payload = result.to_bytes(2, "little", signed=False) + bytes(62)
    source = {"kind": "assisted_native_arithmetic_data_chain", "version": VERSION,
              "first": first, "second": second, "actual_final_result": result,
              "payload_bytes": len(payload), "payload_sha256": _supply().sha(payload),
              "literal_public_operands": {k: row[k] for k in ("izquierda", "derecha", "restar")},
              "codec": "actual_final_uint16_little_endian_plus_62_zero_bytes",
              "scope": "Prepared assisted chain; first actual Native output feeds next actual Native operation, then fixed external byte transport. No discovered plan or learned arithmetic algorithm."}
    # Reuse the old strict proof of actual reader and first-to-second transport.
    if _supply().payload_from_actual_source(source) != payload:
        raise ValueError("Actual variable source failed the preserved fixed transport contract")
    return payload, source


def cut_first_link(a, row, arithmetic_api):
    """Always cut after the first actual call; never wait for an expected13."""
    first = arithmetic_api.execute(a, {"modo": arithmetic_api.MODE, "operacion": "suma",
                                      "izquierda": row["izquierda"], "derecha": row["derecha"]})
    return {"version": VERSION, "kind": "explicit_diagnostic_link_cut", "first_native_operation": first,
            "actual_first_result": first.get("numeric_result"), "second_operation_called": False,
            "supply_performed": False, "new_resources": 0, "payload": None,
            "scope": "Intervention on an explicitly identified control only; no replacement result, second call or resource. NULL/zero retain their actual meanings."}


def _completed_pre_window(a, directory, *, cut=False):
    task = _task()
    p, ph, r01, identity = task._guard(a, directory, material=False)
    m = task._get(a)
    d = task._device(directory)
    if m.get("control") != "real" or m.get("serie") != "continuous" or not m.get("ready"):
        raise ValueError("R04 requires the real continuous R02 genealogy")
    if m.get("uncertain") or m.get("pending") or m.get("halted_reason") or m.get("supply_pending"):
        raise ValueError("No eligibility/task/source operation may be pending")
    if d.m.get("uncertain") or d.m.get("pending") or d.m.get("feedback_pending") or d.m.get("supply_pending"):
        raise ValueError("No unfinished external action/return may precede the source")
    if m["opportunity"] < 14 or [x["series"] for x in m["schedule"][:14]] != ["development"] * 6 + ["reserved"] * 8:
        raise ValueError("Complete the original reserve before this distinct additional stage")
    if m["opportunity"] != d.m["opportunity"] or len(m["schedule"]) != len(d.m["capsules"]):
        raise ValueError("Existing task/device progress differs")
    # New data cannot be silently labeled onto an older unconsumed capsule.
    if not cut and m["opportunity"] != len(m["schedule"]):
        raise ValueError("Consume previous offers before a variable-data supply block; no relabeling old payloads")
    if cut:
        if not identity["life_id"].startswith(CONTROL_PREFIX):
            raise ValueError("Causal cut requires a distinct explicit ECI02_PI03_CONTROL_CADENA_* life")
        task._r1()._identity(a, r01, directory)  # Material guard rejects ACTIVO.
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    key = "DEE.Cognitive.PI02.continuous_workbench.R04"
    if key in entries:
        old = task._decode(entries[key])
        if old.get("enabled") or old.get("active") is not None:
            raise ValueError("Explicitly pause PI02 and finish any old FI job before Native source use")
    task.operational_dependencies(a, directory)
    return task, p, r01, identity, m, d


def validate(a, row, *, directory=None):
    validate_literal(row)
    if row["modo"] == STATE:
        return
    if directory is None:
        # Owner validation before dispatch cannot invent an operational path.
        # Full resource/life/state guards run with the actual path at dispatch.
        return
    _completed_pre_window(a, directory, cut=row["modo"] == CUT)
    if row["modo"] == SUPPLY:
        _supply().validate(a, _supply_row(row), directory=directory)


def dispatch(a, row, *, directory=None, actuator="closed"):
    validate_literal(row)
    if row["modo"] == STATE:
        value = _task().state(a, directory)
        value.update({"variable_chain_version": VERSION, "new_native_ticks": 0,
                      "scope": "Read-only progress, no arithmetic, query, supply or life creation"})
        return value
    if directory is None or actuator != "closed":
        raise ValueError("Existing owned directory and explicit fixed actuator contract required")
    validate(a, row, directory=directory)
    task, p, r01, identity, m, d = _completed_pre_window(a, directory, cut=row["modo"] == CUT)
    from app.native_tools import physical
    from capacidades import aritmetica_directa_eci02 as arithmetic
    start = int(a.tick)
    before = physical(a.world)
    if row["modo"] == CUT:
        m["uncertain"] = True
        m["pending"] = {"phase": "explicit_R04_control_first_link_cut", "literal": dict(row)}
        task._record(a, m, directory, {"kind": "R04_DIAGNOSTIC_CUT_INTENT", "literal": row,
                                     "control_life": identity["life_id"]})
        task._record(a, m, directory, task._r1()._frame(a, r01, "before_R04_first_link_cut"))
        result = cut_first_link(a, row, arithmetic)
        task._record(a, m, directory, task._r1()._frame(a, r01, "after_R04_first_link_cut"))
        m.setdefault("chain_cut_diagnostics", []).append(result)
        m["pending"] = None
        m["uncertain"] = False
        m["halted_reason"] = "Explicit R04 diagnostic link-cut control; terminal for task opportunities, never promoted as learning"
        task._record(a, m, directory, {"kind": "R04_DIAGNOSTIC_CUT_COMPLETED", "result": result})
    else:
        def commit(event):
            task._record(a, m, directory, event)
        def source_callback():
            task._record(a, m, directory, {"kind": "R04_PUBLIC_VARIABLE_OPERANDS", "literal": dict(row),
                                         "scope": "Public source operands/configuration, never a Native action target"})
            task._record(a, m, directory, task._r1()._frame(a, r01, "before_R04_actual_variable_chain"))
            payload, source = actual_chain(a, row, arithmetic)
            task._record(a, m, directory, task._r1()._frame(a, r01, "after_R04_actual_variable_chain"))
            return payload, source
        result = _supply().append_supply(m, d, _supply_row(row), commit, recalculate_source=source_callback)
    result.update({"version_R04": VERSION, "before": before, "after": physical(a.world),
                   "new_native_ticks": int(a.tick) - start,
                   "literal_public_operands": {k: row[k] for k in ("izquierda", "derecha", "restar")},
                   "checkpoint_requirement": "Save exact full Native owner/agenda/receipts, task/device files and SQLite transport together. Additional offers are not part of the original R02 reserve."})
    return result
