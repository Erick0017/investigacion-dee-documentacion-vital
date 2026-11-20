#!/usr/bin/env python3
"""Technical assertions for the isolated CORE17 repair candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "result_path", nargs="?", type=Path,
        default=ROOT / "results" / "repair_results.json")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    result_path = args.result_path.resolve()
    value = json.loads(result_path.read_text(encoding="utf-8"))
    expected = {
        "treatment": 2,
        "offpath_cut": 2,
        "backup_untrained": 0,
        "backup_direction_reset": 0,
        "no_backup": 0,
        "path_cut": 0,
        "wrong_receiver": 0,
    }
    checks = {
        "fourteen_executions": len(value["rows"]) == 14,
        "expected_functional_counts": value["counts_functional"] == expected,
        "runner_expectation_matched": value["technical_expectation_matched"] is True,
        "treatment_and_offpath_reconstruct": all(
            row["reconstructed_at_arrival"] and row["fresh_function"]
            for row in value["rows"]
            if row["mode"] in {"treatment", "offpath_cut"}
        ),
        "causal_controls_do_not_reconstruct": all(
            not row["reconstructed_at_arrival"] and not row["fresh_function"]
            for row in value["rows"]
            if row["mode"] not in {"treatment", "offpath_cut"}
        ),
        "untrained_backup_identified": all(
            not row["backup_learned"]
            for row in value["rows"] if row["mode"] == "backup_untrained"
        ),
        "no_acquired_replication_claim": (
            "separately trained" in value["copy_semantics"]
            and "no acquired replication" in value["copy_semantics"]
        ),
    }
    rendered = json.dumps(
        {
            "schema": "dee-thinking-repair-candidate-check-v1",
            "checks": checks,
            "all_checks": all(checks.values()),
            "repair_results_sha256": hashlib.sha256(result_path.read_bytes()).hexdigest(),
        },
        indent=2,
        sort_keys=True,
    ) + "\n"
    output = (args.output or (ROOT / "results" / "repair_validation.json")).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
