from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import dee_thinking as dee


SECTION = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    summary = load_json(SECTION / "RUN_SUMMARY.json")
    checkpoints = summary["checkpoints"]
    checkpoint_checks = []
    for item in checkpoints:
        path = SECTION / item["path"]
        actual = sha256(path)
        runtime = dee.Runtime.load_snapshot(str(path))
        before = int(runtime.current_tick)
        runtime.advance(0)
        after = int(runtime.current_tick)
        checkpoint_checks.append({
            "path": item["path"],
            "expected_sha256": item["sha256"],
            "actual_sha256": actual,
            "hash_equal": actual == item["sha256"],
            "expected_tick": item["tick"],
            "loaded_tick": before,
            "tick_equal": before == int(item["tick"]),
            "advance_zero_preserved_tick": before == after,
            "dimension": int(runtime.dimension),
        })

    histories = load_json(SECTION / "TELEMETRY" / "B1_HISTORY_PANEL.json")
    history_checks = {
        name: {
            "probe20_prediction_exact": bool(row["common_probe_t20"]["prediction_exact"]),
            "reexpression40_prediction_exact": bool(row["reexpression_t40"]["prediction_exact"]),
        }
        for name, row in histories.items()
    }
    backend = load_json(SECTION / "TELEMETRY" / "BACKEND_EQUIVALENCE.json")
    mediated = load_json(SECTION / "TELEMETRY" / "MEDIATED_INTERACTION.json")
    direct = load_json(SECTION / "TELEMETRY" / "DIRECT_CONTACT.json")
    validation = {
        "schema": "mbp4.materialized-entities.technical-validation.v1",
        "checkpoint_checks": checkpoint_checks,
        "history_checks": history_checks,
        "backend_raw_equal": bool(backend["raw_equal"]),
        "backend_clock_equal": bool(backend["clock_equal"]),
        "mediated_treatment_records_present": sum(
            row["B2_interaction_tick30"] is not None
            for row in mediated if row["mode"] == "TREATMENT"
        ),
        "direct_treatment_records_present": sum(
            row["record_at_contact"] is not None
            for row in direct if row["mode"] == "TREATMENT"
        ),
        "candidate_descendant_records": sum(
            bool(row["candidate_descendant"])
            for row in direct if row["mode"] == "TREATMENT"
        ),
    }
    validation["all_technical_checks_true"] = (
        all(row["hash_equal"] and row["tick_equal"] and row["advance_zero_preserved_tick"]
            for row in checkpoint_checks)
        and all(row["probe20_prediction_exact"] and row["reexpression40_prediction_exact"]
                for row in history_checks.values())
        and validation["backend_raw_equal"]
        and validation["backend_clock_equal"]
        and validation["mediated_treatment_records_present"] == 2
        and validation["direct_treatment_records_present"] == 2
        and validation["candidate_descendant_records"] == 2
    )
    path = SECTION / "TELEMETRY" / "VALIDATION.json"
    path.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not validation["all_technical_checks_true"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
