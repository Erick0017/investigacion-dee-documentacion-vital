"""R03 opt-in early balance readout INSIDE the existing APD05 procedure.

No new world, anatomy, references, source policy, teacher or reward is created.
The inherited version sensor, lexical queries, environment and action mapping
remain unchanged. Only a balance operation's fixed read time/site is extended.
Imports are lazy: this file alone never imports DEE or advances a tick.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

VERSION = "ECI01.integrated_version_balance_access.P0.R03"
MODE = "eci01-vigencia-vivir"
_ACTIVE_PATCH = False


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf8")


def proposed_protocol():
    return {"version": VERSION, "mode": MODE,
            "literal_fields": ["modo", "oportunidades", "lexico"],
            "opportunities": "exact integer1..4", "lexicon": "explicit boolean",
            "transport_admission": "one exact eci01-vigencia-vivir branch before the unchanged R02 prefix validator; no generic JSON bypass",
            "base_procedure": "unchanged percepcion_vigencia_apd05.live on the same adapter/environment",
            "override_scope": "only acciones_nativas_apd04.balance during this explicit call",
            "decoder": "unchanged R01 early E at effective q+4; SEM1, state>0, direction[x,1,z], x in -1/0/+1,z in0/-1",
            "balance_output": "physical_choice receives early physical class; original q6 preserved separately and in native_trial.reader",
            "no_operand_or_expected_answer_in_decoder": True,
            "version_access_and_lexicon": "unchanged original APD05 selection and inherited lexical queries",
            "effect": "existing APD05 environment action executes before its unchanged auditor evaluates usefulness",
            "reward": "no new R04 feedback, SUCCESS pulse, target or memory edit",
            "actuator": "closed only for integrated version procedure; old ECI01 modes retain their own contract",
            "default_APD05": "unchanged q6; no global replacement outside the explicit ECI01 call",
            "resource_and_directory": "same native material protocol; existing owner directly supplies its operational work_directory for artifacts",
            "scope": "Prepared P0 interface; an actual zero/HOLD is distinct from NULL/no-action, even when both leave zero gap unchanged",
            "not_claimed": ["learned reader", "P2/R2", "new anatomy", "general equality meaning", "greater control merely because gap0 remains0"]}


def _old():
    from capacidades import acceso_eci01
    return acceso_eci01


def validate_literal(row):
    if isinstance(row, dict) and row.get("modo") == MODE:
        if set(row) != {"modo", "oportunidades", "lexico"}:
            raise ValueError("Integrated ECI01 requires exactly modo/oportunidades/lexico, without targets or replacement content")
        if type(row["oportunidades"]) is not int or not 1 <= row["oportunidades"] <= 4:
            raise ValueError("One to four exact literal opportunities required")
        if type(row["lexico"]) is not bool:
            raise ValueError("Explicit lexical-use boolean required")
        return
    return _old().validate_literal(row)


def validate(a, row):
    validate_literal(row)
    if row.get("modo") != MODE:
        return _old().validate(a, row)
    from capacidades import percepcion_vigencia_apd05 as sensor
    sensor.validate(a, {"modo": "apd05-vigencia-vivir",
                        "oportunidades": row["oportunidades"], "lexico": row["lexico"]})


def _capture_with_original(a, left, right, detail, original_balance):
    old = _old()
    old._loads(left, right)
    from capacidades import percepcion_cruda_fi01 as perception
    from capacidades import mente_unificada_01 as mu
    if int(a.world.runtime.dimension) != 67 or perception.get(a)["level"] != 128:
        raise ValueError("Only the inherited N67 FI128 domain is admitted")
    geometry = perception.geometry(perception.get(a)["level"])
    requested_q = int(a.tick + 2 - geometry["raw_relative_tick"] + 35)
    q = int(mu.query_timing(a, requested_q)["effective_query_tick"])
    adapter = old._EarlyAdapter(a, q)
    # This is the previously saved ORIGINAL function, never tools.balance here.
    result = original_balance(adapter, left, right, detail=detail)
    if result["native_trial"]["query_tick"] != q or adapter.observation is None:
        raise RuntimeError("Preserve attempted future: the frozen early boundary was not observed")
    early = old.decode_emission(adapter.observation)
    return {**result, "physical_choice": early,
            "original_q6_physical_choice": result["physical_choice"],
            "early_E_q4_observation": adapter.observation, "early_E_q4_tick": q + 4,
            "access_override": VERSION, "NULL_is_not_zero": True,
            "prepared_interface_not_acquired_reader": True,
            "scope": "Original balance physics and original q6 evidence preserved; only the explicit P0 action transduction uses early E q4"}


def live(a, count, directory, *, use_lexicon=True, detailed=False):
    global _ACTIVE_PATCH
    validate(a, {"modo": MODE, "oportunidades": count, "lexico": use_lexicon})
    from capacidades import percepcion_vigencia_apd05 as sensor
    from capacidades import acciones_nativas_apd04 as tools
    if _ACTIVE_PATCH:
        raise RuntimeError("One owner and one integrated operation at a time; no reentrant override")
    original = tools.balance
    _ACTIVE_PATCH = True
    def early_balance(adapter, left, right, detail=False):
        return _capture_with_original(adapter, left, right, detail, original)
    tools.balance = early_balance
    try:
        result = sensor.live(a, count, directory, use_lexicon=use_lexicon, detailed=detailed)
    finally:
        tools.balance = original
        _ACTIVE_PATCH = False
    return {**result, "explicit_opt_in_access_extension": VERSION,
            "original_balance_function_restored": tools.balance is original,
            "attribution": "Inherited same-life APD05 sequence with prepared early balance readout; not learned selection of this reader or an R2 policy"}


def dispatch(a, row, *, actuator="closed", directory=None):
    validate(a, row)
    if row.get("modo") != MODE:
        return _old().dispatch(a, row, actuator=actuator)
    if actuator != "closed":
        raise ValueError("Integrated APD05 procedure admits its original closed actuator only")
    if directory is None:
        raise ValueError("Existing owner must supply its operational work_directory; no path is guessed")
    home = Path(directory)
    return live(a, row["oportunidades"], home, use_lexicon=row["lexico"], detailed=False)


if __name__ == "__main__":
    print(json.dumps({"protocol": proposed_protocol(),
                      "sha256": hashlib.sha256(canonical(proposed_protocol())).hexdigest(),
                      "native_execution": False}, ensure_ascii=False, indent=2))
