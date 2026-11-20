"""Synthesize terminal focal-control evidence; all code is stdlib/passive."""
import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_"


def read(relative):
    path = ROOT / relative
    raw = path.read_bytes()
    return json.loads(raw), {"path_relative_R05": relative, "bytes": len(raw),
                             "sha256": hashlib.sha256(raw).hexdigest()}


def summarize(role):
    result, rs = read(f"evidencia/CONTROL_{role}_R01/RESULTADO.json")
    recalculo, rcs = read(f"analisis/CONTROL_{role}_RECALCULO_R01/RECALCULO.json")
    queue, qs = read(f"analisis/CONTROL_{role}_RECALCULO_R01/COLA_TERMINAL.json")
    life = PREFIX + role
    if result["life_id"] != life or result["owner_closed"] is not True:
        raise ValueError("Exact terminal control required")
    protocol_path = ROOT / "protocolo/CONTROL_MEMORIA_RESERVA_C02.json"
    protocol_sha = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
    if result["protocol_sha256"] != protocol_sha:
        raise ValueError("Frozen protocol changed")
    primary_dir = ROOT / "native" / role / "sistema/estado/servicios_locales" / life / "RBX02_NATIVE_C02/functions"
    functions = []
    lesson = None
    sources = [rs, rcs, qs]
    for path in sorted(primary_dir.glob("*.json")):
        primary, item = read(str(path.relative_to(ROOT)))
        if primary["life_id"] != life or primary["context"]["session_id"] != result["session"]:
            raise ValueError("Mixed control life/session")
        sources.append(item)
        native = primary["native_function"]
        actual = {"operation_id": primary["context"]["operation_id"],
                  "before_T": primary["before_tick"], "after_function_T": primary["after_tick"],
                  "visible_tool": primary["visible_tool"], "Native_inputs": primary["Native_inputs"],
                  "primary_sha256": item["sha256"]}
        if isinstance(native, list):
            lesson = actual
            actual["lessons"] = [{"form": row["form"], "observed_sign": row["observed_sign"],
                                    "before_T": row["before_tick"], "after_T": row["after_tick"],
                                    "cue_tick": row["native_lesson"]["input_tick"],
                                    "teacher_tick": row["native_lesson"]["teacher_tick"],
                                    "teacher_delay": row["native_lesson"]["teacher_tick"] - row["native_lesson"]["input_tick"]}
                                   for row in native]
        else:
            actual.update(memory_value=native["recall"]["native_sign"], operation=native["operation"],
                          numeric_result=native["numeric_result"],
                          native_word_reading=native["recall"]["native_word"], status=native["status"])
        functions.append(actual)
    focal_requests = [row for table in queue["requests"].values() for row in table["focal_requests"]]
    statuses = dict(Counter(row["status"] for row in focal_requests))
    card, cs = read(f"native/{role}/sistema/estado/vidas/{life}/VIDA.json")
    sources.append(cs)
    row_values = [{"index": row["index"], "tool": row["tool"],
                   "memory_value": (row.get("tool_result") or {}).get("memory_value"),
                   "operation": (row.get("tool_result") or {}).get("operation"),
                   "actual_numeric": row["actual_numeric"], "after_T": row["after_tick"],
                   "actual_intermediate_used": row["actual_intermediate_used"],
                   "generic_material_failure": row["generic_material_failure"],
                   "Native_Q1_NULL": row["Native_Q1_NULL"]} for row in result["rows"]]
    numeric = [row for row in result["rows"] if row["tool"] and row["tool"]["kind"] == "CALCULATE"]
    facts = {
        "schema": "DEE.RBX01.C02.focal_memory.terminal_facts.R01", "inspection_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "Recalculation of completed legal Native run by Root; this script executes no Native",
        "life_id": life, "N": card["physical"]["N"], "source_T": result["source_tick"],
        "final_T": card["physical"]["tick"], "new_ticks": card["physical"]["tick"] - result["source_tick"],
        "teacher_mode": result["teacher_mode"], "protocol_sha256": protocol_sha,
        "completed_opportunities": result["opportunities_completed"],
        "formed_numeric_outputs": sum(row["formed"] for row in numeric), "numeric_opportunities": len(numeric),
        "Native_Q1_NULL_count": sum(row["Native_Q1_NULL"] for row in result["rows"]),
        "generic_material_failures": sum(row["generic_material_failure"] for row in result["rows"]),
        "actual_opportunity_rows": row_values, "functions": functions,
        "Native_input_coverage": recalculo["coverage"], "recalculation_issues": recalculo["issues"],
        "focal_queue_status_counts": statuses, "focal_queue_rows": len(focal_requests),
        "queue_unchanged_during_readonly_inspection": queue["queue_sha256_before"] == queue["queue_sha256_after"],
        "final_physical": card["physical"], "final_snapshot_storage": card["storage"],
        "owner_closed": result["owner_closed"], "adopted": result["adopted"],
        "Roblox_executed": result["Roblox_executed"], "autonomous_plan_demonstrated": result["autonomous_plan_demonstrated"],
        "interpretation": [
            "Same control life used word memory to choose arithmetic before and after a legal reversed lesson. The actual first numeric product was transported into the second call.",
            "Fixed common36 word reader and prepared sign-to-opcode mapping; no expected numeric response entered the participant.",
            "The lesson has formedFalse because no word was queried at teaching time. Subsequent fixed-reader use is the content test.",
            "Do not interpret this as Native planning or Roblox navigation: opportunities and tool order were supplied by the focal protocol.",
            "An intact before/after sequence is not yet exclusive evidence for paired teaching causality; matched desynchrony/age/material-dose contrast remains separate.",
            "This branch is not principal and its experience must not be merged into R02 or protected REAL2.",
        ],
        "sources": sources, "subagent_native_ticks": 0,
    }
    target = ROOT / f"analisis/CONTROL_{role}_RECALCULO_R01/HECHOS_Y_ATRIBUCION.json"
    with target.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(facts, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(target.relative_to(ROOT)), "life": life, "final_T": facts["final_T"],
                      "Native_input_coverage": facts["Native_input_coverage"], "queue_statuses": statuses,
                      "numeric_outputs": [(r["index"], r["memory_value"], r["actual_numeric"]) for r in row_values],
                      "issues": facts["recalculation_issues"]}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", choices=("MEMPAIR", "MEMCTRL"))
    summarize(parser.parse_args().role)
