"""Passive paired/desynchrony contrast. Requires both terminal closed runs."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_"


def load(role):
    result_path = ROOT / f"evidencia/CONTROL_{role}_R01/RESULTADO.json"
    result_bytes = result_path.read_bytes()
    result = json.loads(result_bytes)
    if result["owner_closed"] is not True or result["life_id"] != PREFIX + role:
        raise ValueError("Exact closed control required")
    primary_dir = ROOT / "native" / role / "sistema/estado/servicios_locales" / (PREFIX + role) / "RBX02_NATIVE_C02/functions"
    primaries = sorted([json.loads(p.read_bytes()) for p in primary_dir.glob("*.json")],
                       key=lambda p: p["context"]["sequence"])
    return result, primaries, {"path": str(result_path.relative_to(ROOT)), "bytes": len(result_bytes),
                               "sha256": hashlib.sha256(result_bytes).hexdigest()}


def before_signature(primary):
    native = primary["native_function"]
    return native[0]["native_lesson"]["before"] if isinstance(native, list) else native["recall"]["native_word"]["before"]


def numeric_observable(primary):
    native = primary["native_function"]
    if isinstance(native, list):
        return {"lessons": [{"form": row["form"], "observed_sign": row["observed_sign"],
                              "input_tick": row["native_lesson"]["input_tick"],
                              "teacher_tick": row["native_lesson"]["teacher_tick"],
                              "actual_delay": row["native_lesson"]["teacher_tick"] - row["native_lesson"]["input_tick"]}
                             for row in native]}
    return {"native_sign": native["recall"]["native_sign"], "operation": native["operation"],
            "numeric_result": native["numeric_result"], "status": native["status"]}


def main():
    required = [ROOT / f"evidencia/CONTROL_{role}_R01/RESULTADO.json" for role in ("MEMPAIR", "MEMCTRL")]
    if not all(path.is_file() for path in required):
        print(json.dumps({"status": "PENDING_TERMINAL_CONTROL", "missing": [str(p.relative_to(ROOT)) for p in required if not p.is_file()]}))
        return
    a, pa, sa = load("MEMPAIR"); b, pb, sb = load("MEMCTRL")
    rows = []
    for index in range(max(len(pa), len(pb))):
        left = pa[index] if index < len(pa) else None
        right = pb[index] if index < len(pb) else None
        row = {"opportunity": index + 1, "paired_primary_present": left is not None,
               "desync_primary_present": right is not None}
        if left is not None and right is not None:
            row.update(visible_tool_equal=left["visible_tool"] == right["visible_tool"],
                       paired_visible_tool=left["visible_tool"], desync_visible_tool=right["visible_tool"],
                       before_physical_signature_equal=before_signature(left) == before_signature(right),
                       paired_before=before_signature(left), desync_before=before_signature(right),
                       paired_function_T=[left["before_tick"], left["after_tick"]],
                       desync_function_T=[right["before_tick"], right["after_tick"]],
                       paired_actual=numeric_observable(left), desync_actual=numeric_observable(right),
                       paired_input_counts=left["Native_inputs"], desync_input_counts=right["Native_inputs"])
        rows.append(row)
    report = {"schema": "DEE.RBX01.C02.focal_memory.paired_desync_contrast.R01",
              "inspection_utc": datetime.now(timezone.utc).isoformat(),
              "mode": "Passive contrast of frozen results and complete function primaries; no Native rerun",
              "sources": [sa, sb], "same_frozen_protocol": a["protocol_sha256"] == b["protocol_sha256"],
              "same_source_T": a["source_tick"] == b["source_tick"],
              "same_completed_opportunity_count": a["opportunities_completed"] == b["opportunities_completed"],
              "paired_after_opportunity_ticks": [row["after_tick"] for row in a["rows"]],
              "desync_after_opportunity_ticks": [row["after_tick"] for row in b["rows"]],
              "same_boundary_age_schedule": [r["after_tick"] for r in a["rows"]] == [r["after_tick"] for r in b["rows"]],
              "rows": rows,
              "limits": ["Paired shared-prefix control trajectories, not independent organisms or population estimates.",
                         "Matching requested dose is not automatically matching admitted dose; actual counts and rejections are retained above.",
                         "Generic failure and later operands may legitimately diverge after different Native outputs; do not impose identical endogenous futures.",
                         "Function opportunities and order remain prepared. This is not a Roblox route or Native planner comparison."],
              "subagent_native_ticks": 0}
    target = ROOT / "analisis/CONTROLES_MEMORIA_CONTRASTE_R01.json"
    with target.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(target.relative_to(ROOT)), "comparisons": len(rows),
                      "baseline_before_equal": [row.get("before_physical_signature_equal") for row in rows[:3]],
                      "same_boundary_age_schedule": report["same_boundary_age_schedule"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
