"""Portable passive C02 arm comparison. Explicit frozen files only.

Never imports DEE, opens SQLite, calls a model/MCP/HTTP, or simulates a world.
Shares canonical event parsing and CSV formatting with the existing recalc.
"""
from __future__ import annotations
import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("_C02_passive_shared", HERE / "RECALCULO_FUNCIONES_Y_MUNDO_C02.py")
CORE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CORE)
ARMS = ("LIVE_NATIVE", "PROGRAMMED", "CONVENTIONAL_AI")
FINGERPRINT = "562d277322ab2a2094bc34009aad03b352d151b2865f4843965e6eb1bc6964d7"
PERIODS = ((1, 6), (7, 12), (13, 18))
OP_KINDS = {"OBSERVATION", "ACTION_EXECUTED", "PHYSICAL_TOLL_CONTACT", "PHYSICAL_CONTACT",
            "PAID_LOCAL_PANEL", "FUNCTION_SUBMITTED", "FUNCTION_APPLIED", "FUNCTION_ACKNOWLEDGED",
            "FUNCTION_COMPLETED", "TOOL_NOT_INVOKED", "NUMERIC_OBJECT_REPLACED", "EVALUATOR_LOCK_CHECK",
            "FEEDBACK_SUBMITTED", "FEEDBACK_COMPLETED"}


def integer(value):
    return type(value) is int


def journal(paths, manifest, issues):
    completed = {}; model = {}; aliases = 0
    for path in paths:
        value = CORE.read_input(path, manifest, issues)
        for row in CORE.event_rows(value):
            if row.get("kind") == "COMPLETED" and isinstance(row.get("operation_id"), str):
                key = (row.get("run_id"), row["operation_id"])
                if key in completed:
                    aliases += 1
                    if completed[key] != row:
                        issues.append({"issue": "CONFLICTING_POLICY_OPERATION", "operation_id": key[1]})
                else:
                    completed[key] = row
            if row.get("kind") == "MODEL_RESPONSE":
                key = (row.get("run_id"), row.get("call"), row.get("kind_requested"))
                if key in model and model[key] != row:
                    issues.append({"issue": "CONFLICTING_MODEL_CALL", "call": key[1]})
                else:
                    model[key] = row
    by_operation = {}
    for (_, operation), row in completed.items():
        if operation in by_operation and by_operation[operation] != row:
            issues.append({"issue": "AMBIGUOUS_OPERATION_ACROSS_RUNS", "operation_id": operation})
        else:
            by_operation[operation] = row
    return by_operation, {"unique_policy_completed": len(completed), "policy_aliases": aliases,
                          "unique_model_responses": len(model),
                          "model_invalid_or_unparsed_responses": sum(r.get("choice") is None for r in model.values()),
                          "model_wall_seconds_reported": sum(r.get("wall_seconds", 0) for r in model.values() if type(r.get("wall_seconds")) in (int, float)),
                          "scope": "Own frozen policy/model journals; counts are not Native events or independent trials."}


def action_unique(events, issues):
    result = {}
    for event in events:
        if event["kind"] != "ACTION_EXECUTED":
            continue
        item = event["data"]; identifier = item.get("action", {}).get("actionId")
        if not isinstance(identifier, str):
            issues.append({"issue": "ACTION_WITHOUT_ID", "seq": event["seq"]}); continue
        if identifier in result and result[identifier]["data"] != item:
            issues.append({"issue": "CONFLICTING_ACTION_ID", "action_id": identifier})
        else:
            result[identifier] = event
    return list(result.values())


def opportunity(arm, cycle, events, policies, closed, issues):
    observations = [r for r in events if r["kind"] == "OBSERVATION"]
    actions = action_unique(events, issues)
    functions = [r for r in events if r["kind"] == "FUNCTION_APPLIED"]
    feedback = [r for r in events if r["kind"] == "FEEDBACK_COMPLETED"]
    submitted = [r for r in events if r["kind"] == "FEEDBACK_SUBMITTED"]
    locks = [r["data"] for r in events if r["kind"] == "EVALUATOR_LOCK_CHECK"]
    calc = []; lessons = []; null_wait = voluntary_wait = unknown_wait = 0
    for event in functions:
        request = event["data"].get("request", {}); output = event["data"].get("output", {})
        if request.get("kind") == "LESSON":
            # formedFalse means no recall at teaching time; only explicit
            # admission failure is a failed lesson, never infer from formed.
            lessons.append({"request": request, "reason": output.get("reason"),
                            "partial_admission": output.get("reason") == "NATIVE_PARTIAL_ADMISSION" or output.get("capability_execution_admitted") is False})
        elif request.get("kind") == "CALCULATE":
            actual = output.get("numeric_result")
            formed = integer(actual) and output.get("formed") is not False
            left, right, operation = request.get("left"), request.get("right"), output.get("operation")
            reference = None
            if integer(left) and integer(right) and operation in ("suma", "diferencia"):
                reference = left + right if operation == "suma" else left - right
            calc.append({"slot": request.get("slot"), "form": request.get("form"), "left": left, "right": right,
                         "memory_value": output.get("memory_value"), "operation": operation,
                         "actual_numeric_result": actual, "formed_integer": formed,
                         "arithmetic_reference_auditor_only": reference,
                         "arithmetic_correct_for_actual_opcode": actual == reference if formed and reference is not None else None,
                         "reason": output.get("reason"), "admission_explicitly_false": output.get("capability_execution_admitted") is False})
    for event in actions:
        action = event["data"]["action"]
        if action.get("name") != "SAFE_WAIT":
            continue
        record = policies.get(action.get("actionId"), {}).get("result", {})
        evidence = record.get("evidence", {})
        if action.get("null") is True or record.get("null") is True or evidence.get("invalid_model_output") is True:
            null_wait += 1
        elif evidence.get("voluntary_wait") is True:
            voluntary_wait += 1
        else:
            unknown_wait += 1
    first = observations[0] if observations else None
    last = feedback[-1] if feedback else events[-1] if events else None
    native_start = native_end = native_delta = None
    if arm == "LIVE_NATIVE" and actions:
        action = actions[0]["data"]["action"]
        if integer(action.get("nativeTick")) and integer(action.get("nativeTicks")):
            native_start = action["nativeTick"] - action["nativeTicks"]
        if feedback and integer(feedback[-1]["data"].get("nativeTick")):
            native_end = feedback[-1]["data"]["nativeTick"]
        if native_start is not None and native_end is not None:
            native_delta = native_end - native_start
    wall_seconds = None
    logical_seconds = None
    if first and last:
        if integer(first.get("wallUnixMs")) and integer(last.get("wallUnixMs")):
            wall_seconds = (last["wallUnixMs"] - first["wallUnixMs"]) / 1000
        if integer(first.get("worldTimeMs")) and integer(last.get("worldTimeMs")):
            logical_seconds = (last["worldTimeMs"] - first["worldTimeMs"]) / 1000
    results = [r["data"].get("result", {}) for r in actions]
    outcome = submitted[-1]["data"] if submitted else {}
    return {"arm": arm, "cycle": cycle, "period": (cycle - 1) // 6 + 1, "completed": closed,
            "session_id": events[0].get("sessionId") if events else None,
            "observations": len(observations), "actual_unique_actions": len(actions),
            "actions": [r["data"]["action"].get("name") for r in actions],
            "action_NULL_count": sum(r["data"]["action"].get("null") is True for r in actions),
            "SAFE_WAIT_from_NULL_or_invalid": null_wait, "SAFE_WAIT_explicit_voluntary_policy": voluntary_wait,
            "SAFE_WAIT_intention_unknown": unknown_wait,
            "query_actions": sum(r["data"]["action"].get("name") == "ASK_STATION" for r in actions),
            "skip_actions": sum(r["data"]["action"].get("name") == "SKIP_STATION" for r in actions),
            "route_actions": sum(r["data"]["action"].get("name") in ("EXIT_0", "EXIT_1") for r in actions),
            "function_contacts": len(functions), "lessons": lessons, "calculations": calc,
            "calculation_opportunities": len(calc), "numeric_formed": sum(r["formed_integer"] for r in calc),
            "numeric_valid_zero": sum(r["formed_integer"] and r["actual_numeric_result"] == 0 for r in calc),
            "numeric_NULL_or_absent": sum(not integer(r["actual_numeric_result"]) for r in calc),
            "numeric_present_but_not_admitted": sum(integer(r["actual_numeric_result"]) and not r["formed_integer"] for r in calc),
            "arithmetic_correct": sum(r["arithmetic_correct_for_actual_opcode"] is True for r in calc),
            "arithmetic_incorrect": sum(r["arithmetic_correct_for_actual_opcode"] is False for r in calc),
            "arithmetic_not_evaluable": sum(r["arithmetic_correct_for_actual_opcode"] is None for r in calc),
            "partial_lesson_admissions": sum(r["partial_admission"] for r in lessons),
            "tools_not_invoked": [r["data"] for r in events if r["kind"] == "TOOL_NOT_INVOKED"],
            "lock_checks": locks, "codes_accepted": sum(r.get("accepted") is True for r in locks),
            "codes_rejected": sum(r.get("accepted") is False for r in locks),
            "resources_collected": sum(r.get("resourceCollected") is True for r in results),
            "resources_delivered": sum(r.get("resourceDelivered") is True for r in results),
            "collisions": sum(r.get("collision") is True for r in results),
            "query_denials": sum(r.get("queryDenied") is True for r in results),
            "permission_spent": sum(r.get("permissionSpent", 0) for r in results),
            "query_spent": sum(r.get("querySpent", 0) for r in results),
            "toll_spent": sum(r.get("tollSpent", 0) for r in results),
            "feedback_outcome": outcome.get("outcome"), "generic_material_failure": outcome.get("materialConsequence"),
            "Native_start_tick_observed": native_start, "Native_end_tick_observed": native_end,
            "Native_tick_delta_observed": native_delta, "wall_seconds_observed": wall_seconds,
            "world_logical_seconds_observed": logical_seconds,
            "S_observation_before_partial": first["data"].get("sensors") if first else None,
            "event_hashes": [r["source_sha256"] for r in events]}


def summarize_rows(arm, label, rows, start, end, checkpoints):
    selected = [r for r in rows if start <= r["cycle"] <= end]
    completed = [r for r in selected if r["completed"]]
    fields = ("actual_unique_actions", "action_NULL_count", "SAFE_WAIT_from_NULL_or_invalid", "SAFE_WAIT_explicit_voluntary_policy",
              "SAFE_WAIT_intention_unknown", "query_actions", "skip_actions", "route_actions", "function_contacts",
              "calculation_opportunities", "numeric_formed", "numeric_valid_zero", "numeric_NULL_or_absent",
              "numeric_present_but_not_admitted", "arithmetic_correct", "arithmetic_incorrect", "arithmetic_not_evaluable",
              "partial_lesson_admissions", "codes_accepted", "codes_rejected", "resources_collected", "resources_delivered",
              "collisions", "query_denials", "permission_spent", "query_spent", "toll_spent")
    summary = {"arm": arm, "scope": label, "cycle_start": start, "cycle_end": end,
               "observed_opportunities": len(selected), "completed_opportunities": len(completed),
               "unoffered_or_unobserved_not_scored": max(0, end - start + 1 - len(selected))}
    summary.update({key: sum(row[key] for row in selected) for key in fields})
    for key in ("Native_inputs_requested", "Native_inputs_applied", "Native_inputs_rejected", "Native_inputs_other"):
        values = [r.get(key) for r in selected if r.get(key) is not None]
        summary[key] = sum(values) if values else None
        summary[key + "_covered_rows"] = len(values)
    for key in ("Native_tick_delta_observed", "wall_seconds_observed", "world_logical_seconds_observed"):
        values = [r[key] for r in selected if r[key] is not None]
        summary[key] = sum(values) if values else None
        summary[key + "_covered_rows"] = len(values)
    summary["S_before_actual_checkpoint"] = checkpoints.get(start - 1)
    summary["S_after_actual_checkpoint"] = checkpoints.get(end)
    summary["S_endpoint_scope"] = "Only literal supplied checkpoint S; missing endpoints stay NULL, never inferred full state."
    return summary


def arm_data(arm, world_paths, journal_paths, manifest, issues, technical):
    checkpoints = {}; files = []; fingerprints = set()
    for path in world_paths:
        value = CORE.read_input(path, manifest, issues)
        if not isinstance(value, dict) or value.get("schema") != "DEE.RBX01.C02.world_checkpoint.v1" or not isinstance(value.get("events"), list):
            raise ValueError("Full literal World checkpoint required, never a Tail/summary: " + str(path))
        fingerprints.add(value.get("scenario_sha256"))
        if not technical and value.get("scenario_sha256") != FINGERPRINT:
            raise ValueError("Final scenario fingerprint mismatch")
        state = value.get("S", {}); cursor = state.get("completedCycles")
        if integer(cursor):
            if cursor in checkpoints and checkpoints[cursor] != state:
                issues.append({"arm": arm, "issue": "CONFLICTING_CHECKPOINT_S_AT_CURSOR", "cursor": cursor})
            else:
                checkpoints[cursor] = state
        files.append(path)
    events, aliases, views = CORE.parse_world(files, manifest, issues)
    policies, policy_counts = journal(journal_paths, manifest, issues)
    sessions = {r.get("sessionId") for r in events if r.get("sessionId")}
    participants = {r.get("participant") for r in events if r.get("participant")}
    if len(sessions) > 1:
        raise ValueError("Do not merge different session histories for one arm")
    if participants - {arm}:
        raise ValueError("World participant does not match arm; do not merge environmental replay")
    grouped = {}; pending = []
    for event in events:
        if event["kind"] in OP_KINDS:
            pending.append(event)
        if event["kind"] == "FEEDBACK_COMPLETED":
            cycle = event["data"].get("cycle")
            if not integer(cycle) or cycle < 1:
                issues.append({"arm": arm, "issue": "FEEDBACK_WITHOUT_ACTUAL_CYCLE"}); continue
            if cycle in grouped:
                issues.append({"arm": arm, "issue": "DUPLICATE_COMPLETED_CYCLE", "cycle": cycle})
            else:
                grouped[cycle] = opportunity(arm, cycle, pending, policies, True, issues)
            pending = []
    completed_prefix = 0
    while completed_prefix + 1 in grouped:
        completed_prefix += 1
    rows = [grouped[k] for k in sorted(grouped)]
    if pending:
        rows.append(opportunity(arm, max(grouped, default=0) + 1, pending, policies, False, issues))
    stated = max(checkpoints, default=0)
    if stated != len(grouped):
        issues.append({"arm": arm, "issue": "CHECKPOINT_CURSOR_EVENT_COUNT_DIFFER", "S_completed": stated, "event_completed": len(grouped)})
    return {"arm": arm, "world_files": [str(p) for p in world_paths], "world_views": views,
            "fingerprints": sorted(str(f) for f in fingerprints), "world_event_aliases_deduplicated": aliases,
            "unique_world_events": len(events), "session_ids": sorted(sessions), "policy_journals": policy_counts,
            "completed_opportunities": len(grouped), "completed_contiguous_prefix": completed_prefix,
            "maximum_checkpoint_cursor": stated, "truncated_against_18": completed_prefix < 18,
            "checkpoints": checkpoints, "rows": rows}


def recalculate(arguments, output, technical=False, native_function_paths=(), native_event_paths=()):
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError("New absent output directory required")
    manifest = []; issues = []; arms = {}
    for arm in ARMS:
        world, logs = arguments.get(arm, ([], []))
        arms[arm] = arm_data(arm, world, logs, manifest, issues, technical)
    material_supplied = bool(native_function_paths or native_event_paths)
    native_material = {"supplied": material_supplied, "input_counts": None,
                       "scope": "No Native dose inferred from public toolResult alone."}
    if material_supplied:
        receipts = {}
        functions, _, function_aliases = CORE.parse_functions(CORE.primary_paths(native_function_paths), manifest, issues, receipts)
        native_specs = []
        for item in native_event_paths:
            text = str(item)
            if text.startswith("ECI02_") and "=" in text:
                life, path = text.split("=", 1)
                native_specs.append((life, Path(path)))
            else:
                native_specs.append(Path(item))
        parsed = CORE.parse_native(native_specs, manifest, issues, receipts, functions)
        statuses = dict(Counter(r["receipt"].get("status") for r in receipts.values()))
        assigned = set()
        for row in arms["LIVE_NATIVE"]["rows"]:
            start, end = row["Native_start_tick_observed"], row["Native_end_tick_observed"]
            if not integer(start) or not integer(end):
                continue
            values = []
            for key, receipt in receipts.items():
                tick = receipt.get("requested_tick")
                if integer(tick) and start < tick <= end:
                    assigned.add(key); values.append(receipt)
            row["Native_inputs_requested"] = len(values)
            row["Native_inputs_applied"] = sum(r["receipt"].get("status") == "applied" for r in values)
            row["Native_inputs_rejected"] = sum(str(r["receipt"].get("status", "")).startswith("rejected") for r in values)
            row["Native_inputs_other"] = len(values) - row["Native_inputs_applied"] - row["Native_inputs_rejected"]
            row["Native_input_assignment"] = "Unique(life,id), requested_tick in actual observed Native interval(start,end]."
        native_material = {"supplied": True, "unique_requested_observed": len(receipts), "status_counts": statuses,
                           "function_primaries": len(functions), "function_aliases": function_aliases,
                           "actor_journal_phase_count": len(parsed["completed_phases"]),
                           "unassigned_receipts_preserved": [r for key, r in receipts.items() if key not in assigned],
                           "scope": "Only receipts supplied explicitly; absent primary/journal coverage is not zero dose."}
    common = min(arms[arm]["completed_contiguous_prefix"] for arm in ARMS)
    tables = []; opportunity_rows = []
    for arm in ARMS:
        data = arms[arm]; rows = data["rows"]
        tables.append(summarize_rows(arm, "ALL_ACTUALLY_OBSERVED", rows, 1, max(18, max((r["cycle"] for r in rows), default=0)), data["checkpoints"]))
        for start, end in PERIODS:
            tables.append(summarize_rows(arm, f"PERIOD_{start}_{end}", rows, start, end, data["checkpoints"]))
        tables.append(summarize_rows(arm, "COMMON_COMPLETED_PREFIX", [r for r in rows if r["completed"]], 1, common, data["checkpoints"]))
        opportunity_rows.extend(rows)
    unique_sources = {r["path"] + ":" + r["sha256"]: r for r in manifest}
    report = {"schema": "DEE.RBX01.C02.three_arm.passive_comparison.R01", "Native_executed": False,
              "MCP_HTTP_model_calls": 0, "technical_fixture_only_not_final_benchmark": technical,
              "final_scenario_fingerprint": FINGERPRINT, "planned_opportunities_per_arm": 18,
              "periods": PERIODS, "common_completed_observed_prefix": common,
              "arms": {arm: {k: v for k, v in data.items() if k not in ("rows", "checkpoints")} for arm, data in arms.items()},
              "summary_rows": tables, "opportunity_rows": opportunity_rows, "issues": issues,
              "Native_material_coverage": native_material,
              "sources": list(unique_sources.values()),
              "interpretation_limits": [
                  "One observed history per system; cycles/ticks are not independent organisms. Native branches may share a physical prefix.",
                  "No score for an unoffered/unobserved opportunity. Full arms and the common completed prefix are both reported; a missing arm makes that prefix0.",
                  "Arithmetic correctness evaluates the ACTUAL emitted opcode and operands offline. It is separate from the environmental current-sign lock criterion.",
                  "formedFalse on a LESSON is not failure without explicit partial-admission evidence. Zero integer differs from NULL/absent.",
                  "SAFE_WAIT intention is confirmed only by explicit own-policy evidence; a mandatory neutral action after NULL or invalid output is not voluntary.",
                  "Checkpoint S endpoints are literal; event accounting is not presented as a reconstructed full causal state.",
                  "No unexecuted counterfactual, inferred path, target repair, Native replay, model inference or experimental reproduction is performed."]}
    output.mkdir()
    (output / "RESUMEN_COMPARATIVO.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CORE.csv_write(output / "RESUMEN_BRAZOS.csv", tables)
    CORE.csv_write(output / "OPORTUNIDADES.csv", opportunity_rows)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for prefix in ("native", "programmed", "ai"):
        p.add_argument("--" + prefix + "-world", nargs="*", type=Path, default=[])
        p.add_argument("--" + prefix + "-journal", nargs="*", type=Path, default=[])
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--native-functions", nargs="*", type=Path, default=[])
    p.add_argument("--native-events", nargs="*", default=[])
    p.add_argument("--technical-fixture", action="store_true")
    a = p.parse_args()
    report = recalculate({"LIVE_NATIVE": (a.native_world, a.native_journal),
                          "PROGRAMMED": (a.programmed_world, a.programmed_journal),
                          "CONVENTIONAL_AI": (a.ai_world, a.ai_journal)}, a.output, a.technical_fixture,
                          a.native_functions, a.native_events)
    print(json.dumps({"output": str(a.output), "technical_fixture": a.technical_fixture,
                      "common_prefix": report["common_completed_observed_prefix"],
                      "completed": {arm: data["completed_opportunities"] for arm, data in report["arms"].items()},
                      "issues": report["issues"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
