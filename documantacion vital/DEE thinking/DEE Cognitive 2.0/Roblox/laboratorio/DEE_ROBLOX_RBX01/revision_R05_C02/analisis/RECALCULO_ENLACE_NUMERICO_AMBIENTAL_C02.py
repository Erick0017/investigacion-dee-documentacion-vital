"""Read-only recalculation of two completed Studio environment-only replays."""
from __future__ import annotations
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MISSING = {"__audit_absent_key__": True}


def canon(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def differences(a, b, path=""):
    if type(a) is not type(b):
        return [{"path": path or "/", "left": a, "right": b}]
    if isinstance(a, dict):
        rows = []
        for key in sorted(set(a) | set(b)):
            at = path + "/" + key.replace("~", "~0").replace("/", "~1")
            if key not in a or key not in b:
                rows.append({"path": at, "left": a.get(key, MISSING), "right": b.get(key, MISSING)})
            else:
                rows.extend(differences(a[key], b[key], at))
        return rows
    if isinstance(a, list):
        rows = []
        for i in range(max(len(a), len(b))):
            at = path + "/" + str(i)
            if i >= len(a) or i >= len(b):
                rows.append({"path": at, "left": a[i] if i < len(a) else MISSING,
                             "right": b[i] if i < len(b) else MISSING})
            else:
                rows.extend(differences(a[i], b[i], at))
        return rows
    return [] if a == b else [{"path": path or "/", "left": a, "right": b}]


def load_arm(name):
    path = ROOT / f"evidencia/CONTROL_ENLACE_NUMERICO_{name}_R02/RESULTADO_AMBIENTAL_REPLAY_C02.json"
    before = path.read_bytes()
    data = json.loads(before)
    if path.read_bytes() != before:
        raise RuntimeError("Source changed during passive read")
    if data["NativeExecuted"] is not False or data["hostSelectedAllActions"] is not True:
        raise RuntimeError("Unexpected replay provenance")
    events = data["events"]
    start = [i for i, row in enumerate(events) if row["kind"] == "ENV_REPLAY_BEGIN"]
    if len(start) != 1:
        raise RuntimeError("One explicit replay segment required")
    new_events = events[start[0]:]
    action_rows = [r for r in new_events if r["kind"] == "ACTION_EXECUTED"]
    actions = [{k: r["data"]["action"].get(k) for k in
                ("name", "sourceActionId", "sourceNativeTick", "sourceNativeTicks", "NativeExecuted")}
               for r in action_rows]
    final = data["final"]; initial = data["initial"]
    deltas = {key: final[key] - initial[key] for key in
              ("resourceCount", "resourceUnits", "permissionStock", "queries", "tollSpent",
               "codeRejected", "collisions", "moves", "delivered", "worldTime", "nativeTick")}
    locks = [r["data"] for r in new_events if r["kind"] == "EVALUATOR_LOCK_CHECK"]
    controls = data["controls"]
    facts = {
        "condition": data["condition"], "schema": data["schema"],
        "source_file": str(path.relative_to(ROOT)), "bytes": len(before),
        "sha256": hashlib.sha256(before).hexdigest(), "NativeExecuted": data["NativeExecuted"],
        "NativeContinuationCheckpoint": data["NativeContinuationCheckpoint"],
        "hostSelectedAllActions": data["hostSelectedAllActions"],
        "sourceNativeLifeId": data["sourceNativeLifeId"], "sourceNativeTick": data["sourceNativeTick"],
        "archivedNativeCompletedCycles": data["archivedNativeCompletedCycles"],
        "environmentReplayCompletedCycles": data["environmentReplayCompletedCycles"],
        "new_event_count": len(new_events), "new_event_kinds": dict(Counter(r["kind"] for r in new_events)),
        "replayed_actions": actions, "deltas": deltas, "lock_checks": locks,
        "functionResults": data["functionResults"],
        "control_cycles": [{"cycle": r["cycle"], "queryResult": r["queryResult"],
                            "routeResult": r["routeResult"], "environmentalConsequence": r["environmentalConsequence"],
                            "NativeFeedbackSent": r["NativeFeedbackSent"]} for r in controls],
        "all_control_feedback_not_sent_to_Native": all(r["NativeFeedbackSent"] is False for r in controls),
        "initial_to_final_state_differences": differences(initial, final),
        "provenance": data["sourceProvenance"],
    }
    return data, facts


def main():
    output = ROOT / "analisis/CONTROL_ENLACE_NUMERICO_RECALCULO_R02"
    if output.exists():
        raise RuntimeError("New absent output directory required; no report overwrite")
    intact, intact_facts = load_arm("INTACT")
    cut, cut_facts = load_arm("CUT_B")
    provenance = intact["sourceProvenance"]
    checks = []
    for file_key, sha_key in (("primary_path", "primary_sha256"), ("world_path", "world_sha256"),
                              ("world_final_path", "world_final_sha256")):
        path = Path(provenance[file_key]).resolve(strict=True)
        if not path.is_relative_to(ROOT):
            raise RuntimeError("Referenced source outside scoped R05")
        raw = path.read_bytes(); actual = hashlib.sha256(raw).hexdigest()
        checks.append({"path": str(path.relative_to(ROOT)), "bytes": len(raw), "sha256": actual,
                       "reference_sha256": provenance[sha_key], "matches": actual == provenance[sha_key]})
    equal_initial = intact["initial"] == cut["initial"]
    equal_actions = intact_facts["replayed_actions"] == cut_facts["replayed_actions"]
    equal_costs = {key: intact_facts["deltas"][key] == cut_facts["deltas"][key]
                   for key in ("permissionStock", "queries", "tollSpent", "collisions", "moves", "worldTime", "nativeTick")}
    facts = {
        "schema": "DEE.RBX01.C02.environmental_numeric_link.passive_recalculation.R02",
        "inspection_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "Recalculation of frozen completed Studio environmental replays; no Native import, no simulation rerun",
        "arms": {"INTACT": intact_facts, "CUT_B": cut_facts},
        "paired_comparability": {"initial_state_exact_equal": equal_initial,
                                 "same_recorded_action_sequence": equal_actions,
                                 "equal_actual_cost_time_dose_deltas": equal_costs,
                                 "same_source_provenance": intact["sourceProvenance"] == cut["sourceProvenance"]},
        "cross_arm_initial_state_differences": differences(intact["initial"], cut["initial"]),
        "cross_arm_final_state_differences": differences(intact["final"], cut["final"]),
        "cross_arm_final_physical_differences": differences(intact["physical"], cut["physical"]),
        "source_hash_checks": checks,
        "interpretation_supported": "Under this prepared Body/lock and the same recorded action sequence, transporting the recorded actual Native integer5 permits the resource contact/inventory effect. Cutting B preserves movement/query costs but prevents code acceptance and resource pickup. This isolates a necessary environmental numeric-result link for this recorded case.",
        "interpretation_not_supported": [
            "New Native learning, new Native decisions or Native response to the cut: NativeExecuted is false and no Native feedback was sent.",
            "A general policy comparison or independent replication: both arms replay the same archived trajectory.",
            "A coherent continuation checkpoint: archived Native remains at T950523/completed2 while environment reaches completed4.",
            "An energetic/metabolic resource or subjective pain claim.",
        ],
        "downstream_differences_expected": "After B is cut, lastFailure and later observations/consequences legitimately diverge. Equal exogenous conditions do not require forcing identical endogenous observations.",
        "subagent_native_ticks": 0,
    }
    output.mkdir()
    (output / "RECALCULO.json").write_text(json.dumps(facts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (output / "TODAS_DIFERENCIAS_ESTADO.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("comparison", "path", "left", "right")); writer.writeheader()
        groups = {"INTACT_initial_to_final": intact_facts["initial_to_final_state_differences"],
                  "CUT_B_initial_to_final": cut_facts["initial_to_final_state_differences"],
                  "cross_arm_initial": facts["cross_arm_initial_state_differences"],
                  "cross_arm_final": facts["cross_arm_final_state_differences"],
                  "cross_arm_final_physical": facts["cross_arm_final_physical_differences"]}
        for group, rows in groups.items():
            for row in rows:
                writer.writerow({"comparison": group, "path": row["path"],
                                 "left": canon(row["left"]), "right": canon(row["right"])})
    print(json.dumps({"output": str(output.relative_to(ROOT)), "initial_equal": equal_initial,
                      "actions_equal": equal_actions, "equal_cost_deltas": equal_costs,
                      "INTACT": intact_facts["deltas"], "CUT_B": cut_facts["deltas"],
                      "final_S_differences": len(facts["cross_arm_final_state_differences"]),
                      "final_physical_differences": len(facts["cross_arm_final_physical_differences"]),
                      "provenance_hashes_match": all(r["matches"] for r in checks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
