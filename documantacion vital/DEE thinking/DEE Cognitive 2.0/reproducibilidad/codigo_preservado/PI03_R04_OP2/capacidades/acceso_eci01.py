"""Opt-in ECI01 P0 early-emission transducer; no new anatomy or policy.

The existing Genesis owner/QueueDB remains authoritative. Importing this module
does not import DEE, construct a world, read evidence or advance Native time.
The external balancing environment is a declared discrete two-container model,
not Pendulum, metabolism or a cognitive memory. Its state is snapshot metadata.
"""
from __future__ import annotations
import hashlib
import json

VERSION = "ECI01.early_access.P0.R1"
KEY = "DEE.Cognitive.ECI01.external_balancing.P0.R1"
E = (15, 15, 15)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf8")


def proposed_protocol():
    return {"version": VERSION, "interface": "explicit_opt_in_existing_Genesis_owner",
            "reader": {"time": "effective q+4", "site": list(E),
                       "admitted": "state>0, SEM1, direction[x,1,z], x in -1/0/+1 and z in 0/-1",
                       "choice": "the observed direction x; absent/invalid remain NULL",
                       "arguments_not_available_to_decoder": ["operands", "reference", "expected result", "history label"]},
            "comparison": "existing APD04.balance with unchanged FI128 codec, owner calendar and native reference",
            "transduction": {"1": "move one unit left to right", "-1": "move one unit right to left",
                             "0": "hold", "NULL": "no external action"},
            "environment": "fixed two-container integer loads0..20; empty donor or full receiver makes a declared blocked action",
            "return": "The resulting external loads are the next literal observation; no R04 SUCCESS pulse or memory correction",
            "literal_modes": {"eci01-balance": ["modo", "izquierda", "derecha"],
                              "eci01-entorno-iniciar": ["modo", "izquierda", "derecha"],
                              "eci01-entorno-paso": ["modo"], "eci01-entorno-estado": ["modo"]},
            "actuator_controls": ["closed", "nulled"],
            "initiative": "Each opportunity is explicitly requested by the operator, not initiated by E1",
            "persistence": "environment, transaction progress and pending uncertainty in native snapshot metadata, plus existing paired QueueDB",
            "attribution": "Prepared P0 instrument and environmental transduction; neither reader acquisition nor R2"}


def decode_emission(observation):
    """Frozen six-class decoder. NULL has no arithmetic interpretation."""
    x, y, z = observation["direction"]
    valid = (observation["state"] > 0 and observation["semantic"] == 1
             and x in (-1, 0, 1) and y == 1 and z in (0, -1))
    return x if valid else None


def _read_E(a):
    from dee_thinking import Coordinate
    from capacidades import mente_unificada_01 as mu
    o = mu.observation(a, E)
    # The generic capability view retains exact RAW/clock integers as strings.
    # Recheck its physical point; no expected-answer or operand test occurs.
    actual = a.world.runtime.observe(Coordinate(*E))
    if str(actual.raw) != str(o["raw"]) or str(actual.clock) != str(o["clock"]):
        raise RuntimeError("Early physical observation changed during same-owner read")
    return o


class _EarlyAdapter:
    def __init__(self, base, q):
        self.base, self.q, self.observation = base, int(q), None
    @property
    def world(self):
        return self.base.world
    @property
    def tick(self):
        return int(self.base.tick)
    def run_until(self, tick):
        tick = int(tick)
        if tick < self.tick:
            raise ValueError("No rewind or earlier-state substitution")
        boundary = self.q + 4
        if self.observation is None and self.tick < boundary <= tick:
            self.base.run_until(boundary)
            self.observation = _read_E(self.base)
        if self.tick < tick:
            return self.base.run_until(tick)
        return None


def _loads(left, right):
    if any(type(x) is not int or not 0 <= x <= 20 for x in (left, right)):
        raise ValueError("Two literal, independent integer loads0..20 required")


def balance(a, left, right):
    """One existing physical balance frame with an additional passive q4 read.

    The owning NativeWorld must call before_mutation and later checkpoint.
    This function never selects another reader after inspecting correctness.
    """
    _loads(left, right)
    from capacidades import percepcion_cruda_fi01 as perception
    from capacidades import mente_unificada_01 as mu
    from capacidades import acciones_nativas_apd04 as actions
    g = perception.geometry(perception.get(a)["level"])
    if int(a.world.runtime.dimension) != 67 or perception.get(a)["level"] != 128:
        raise ValueError("Only the inherited N67 FI128 domain is admitted")
    requested_q = int(a.tick + 2 - g["raw_relative_tick"] + 35)
    q = int(mu.query_timing(a, requested_q)["effective_query_tick"])
    wrapper = _EarlyAdapter(a, q)
    original = actions.balance(wrapper, left, right, detail=False)
    actual_q = original["native_trial"]["query_tick"]
    if actual_q != q or wrapper.observation is None:
        raise RuntimeError("Preserved physical future: the fixed q4 boundary was not observed")
    early = decode_emission(wrapper.observation)
    return {"version": VERSION, "early_physical_choice": early,
            "early_observation": wrapper.observation, "early_tick": q + 4,
            "old_q6_choice": original["native_trial"]["reader"]["choice"],
            "query_tick": q, "original_result": original,
            "all_material_receipts": original["native_trial"]["requests"],
            "NULL_is_not_zero": True, "new_R04_return_delivered": False,
            "initiative": "operator-requested use; no learned reader selection",
            "scope": "Prospective prepared P0 physical transduction; contents remain DEE-produced"}


def _get(a):
    from dee_thinking.persistence import decode_metadata
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:
        raise ValueError("No admitted ECI01 balancing environment; use explicit environment start")
    return decode_metadata(entries[KEY])


def _save(a, state):
    from dee_thinking.persistence import encode_metadata
    a.world.runtime.set_snapshot_metadata(KEY, encode_metadata(state))


def environment_start(a, left, right):
    _loads(left, right)
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    if KEY in entries:
        prior = _get(a)
        if prior.get("pending") or prior.get("uncertain"):
            raise ValueError("Cannot replace an unfinished external transaction")
        if prior.get("started"):
            raise ValueError("Environment already exists; continue its trajectory rather than silently reset")
    m = {"version": VERSION, "started": True, "left": left, "right": right,
         "steps": 0, "pending": None, "uncertain": False,
         "model": "two integer containers with one-unit directed transfer",
         "transduction": "+1:left-to-right;-1:right-to-left;0:hold;NULL:no-action",
         "history_not_cognitive_memory": True}
    _save(a, m)
    return m


def apply_fixed_action(left, right, physical_choice):
    """External actuator law; it never computes which action would be useful."""
    _loads(left, right)
    if physical_choice not in (-1, 0, 1, None):
        raise ValueError("Undeclared physical output class")
    if physical_choice is None:
        return left, right, "no_emission_no_action"
    if physical_choice == 0:
        return left, right, "physical_zero_hold"
    if physical_choice == 1:
        return (left - 1, right + 1, "left_to_right") if left > 0 and right < 20 else (left, right, "left_to_right_blocked")
    return (left + 1, right - 1, "right_to_left") if right > 0 and left < 20 else (left, right, "right_to_left_blocked")


def environment_step(a, *, actuator="closed"):
    if actuator not in ("closed", "nulled"):
        raise ValueError("Explicit closed or action-nullified control only")
    m = _get(a)
    if m.get("pending") or m.get("uncertain"):
        raise ValueError("Pending/uncertain environment; no retry or implicit reconstruction")
    before = {"left": m["left"], "right": m["right"], "step": m["steps"], "tick": int(a.tick)}
    m["pending"] = {"step": m["steps"] + 1, "inputs": [m["left"], m["right"]],
                    "stage": "submitted_to_DEE", "actuator": actuator}
    _save(a, m)
    try:
        trial = balance(a, m["left"], m["right"])
        choice = trial["early_physical_choice"]
        if actuator == "nulled":
            left, right, outcome = m["left"], m["right"], "output_formed_action_nullified_control"
        else:
            left, right, outcome = apply_fixed_action(m["left"], m["right"], choice)
        # Commit the actual actuator outcome before any evaluator computes a gap.
        m.update(left=left, right=right, steps=m["steps"] + 1, pending=None,
                 last_physical_choice=choice, last_actuator_outcome=outcome,
                 last_native_tick=int(a.tick), uncertain=False)
        _save(a, m)
    except BaseException:
        m["uncertain"] = True
        m["pending"]["stage"] = "preserved_unresolved_native_future"
        _save(a, m)
        raise
    return {"version": VERSION, "before_environment": before,
            "after_environment": {"left": left, "right": right, "step": m["steps"], "tick": int(a.tick)},
            "actuator": actuator, "actuator_outcome": outcome,
            "physical_choice": choice, "trial": trial,
            "correct_or_useful_action_computed_by_host": False,
            "consequence": "New external loads are observable on the next explicit opportunity; no solution-specific teacher or memory edit"}


def validate_literal(row):
    """Strict transport-only preflight. This function never imports Native."""
    if not isinstance(row, dict):
        raise ValueError("ECI01 requires one literal request object")
    mode = row.get("modo")
    if mode in ("eci01-balance", "eci01-entorno-iniciar"):
        if set(row) != {"modo", "izquierda", "derecha"}:
            raise ValueError("ECI01 accepts exactly modo/izquierda/derecha; no target, teacher, expected choice or history identifier")
        _loads(row["izquierda"], row["derecha"])
    elif mode in ("eci01-entorno-paso", "eci01-entorno-estado"):
        if set(row) != {"modo"}:
            raise ValueError("ECI01 continuation/state accept only modo, never replacement content or action")
    else:
        raise ValueError("Unknown ECI01 literal mode; no aliases or normalization")


def validate(a, row):
    validate_literal(row)
    mode = row.get("modo")
    if mode == "eci01-balance":
        _loads(row.get("izquierda"), row.get("derecha"))
    elif mode == "eci01-entorno-iniciar":
        _loads(row.get("izquierda"), row.get("derecha"))
    elif mode == "eci01-entorno-paso":
        m = _get(a)
        if m.get("pending") or m.get("uncertain"):
            raise ValueError("Unfinished actual transaction is preserved")
    elif mode != "eci01-entorno-estado":
        raise ValueError("Unknown explicit ECI01 operation")


def dispatch(a, row, *, actuator="closed"):
    validate(a, row)
    mode = row["modo"]
    if mode == "eci01-balance":
        return balance(a, row["izquierda"], row["derecha"])
    if mode == "eci01-entorno-iniciar":
        return environment_start(a, row["izquierda"], row["derecha"])
    if mode == "eci01-entorno-paso":
        return environment_step(a, actuator=actuator)
    return {"version": VERSION, "environment": _get(a), "passive_metadata_read": True}


def extend_operational_dependencies(a, result):
    """Owner witness only; external metadata never chooses the DEE readout."""
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:
        return result
    state = _get(a)
    return {**result, "ECI01_environment": {
        "sha256": hashlib.sha256(canonical(state)).hexdigest(),
        "pending": bool(state.get("pending")), "uncertain": bool(state.get("uncertain")),
        "state_location": "full native snapshot metadata: " + KEY,
        "model_state_is_external_not_cognitive_memory": True}}


def external_uncertainty(a):
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    return KEY in entries and bool(_get(a).get("uncertain"))


if __name__ == "__main__":
    print(json.dumps({"protocol": proposed_protocol(),
                      "sha256": hashlib.sha256(canonical(proposed_protocol())).hexdigest(),
                      "native_execution": False}, ensure_ascii=False, indent=2))
