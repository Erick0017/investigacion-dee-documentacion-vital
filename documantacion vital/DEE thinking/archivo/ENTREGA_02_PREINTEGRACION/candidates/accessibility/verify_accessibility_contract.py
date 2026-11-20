#!/usr/bin/env python3
"""Verify the bounded H4 accessibility contract against reduced primary facts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load(name: str) -> dict:
    value = json.loads((ROOT / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{name} must contain an object")
    return value


def main() -> int:
    contract = load("CONTRACT.json")
    evidence = load("primary_evidence_summary.json")
    checks = {
        "contract_not_exported": contract["status"] == "CONTRACT_ONLY_NOT_A_STABLE_BUILDER",
        "nrd01_response_delta_candidate": (
            evidence["nrd01"]["candidate"] is True
            and evidence["nrd01"]["persistent_signal_count"] == 36
            and evidence["nrd01"]["pair_canonicalization_applied_exactly"] is True
        ),
        "nrd02_three_fresh_configurations": (
            evidence["nrd02"]["status"] == "FRESH_CONFIRMED"
            and len(evidence["nrd02"]["configurations"]) == 3
            and all(row["pass"] and row["local_control_signal_count"] == 6
                    for row in evidence["nrd02"]["configurations"])
        ),
        "post_history_coupling_preserved": (
            evidence["post045_u1_p01r"]["corrected_history_conditioned_coupling"] is True
            and evidence["post045_u1_p01r"]["periods"]
                == {"intact": 1, "broken": 2, "no_B": 2}
        ),
        "post_does_not_become_reinstantiation": (
            evidence["post045_u1_p01r"]["functional_class_reinstantiated"] is False
            and evidence["post045_u1_p01r"]
                ["functional_refractory_to_functional_competent_demonstrated"] is False
        ),
        "native_and_diagnostic_layers_separated": (
            "clones" in contract["diagnostic_layer"]
            and evidence["post045_u1_p01r"]["host_edits_after_experimental_t0"] == 0
        ),
    }
    rendered = json.dumps(
        {
            "schema": "dee-thinking-accessibility-contract-check-v1",
            "checks": checks,
            "all_checks": all(checks.values()),
            "contract_sha256": hashlib.sha256(
                (ROOT / "CONTRACT.json").read_bytes()).hexdigest(),
            "evidence_summary_sha256": hashlib.sha256(
                (ROOT / "primary_evidence_summary.json").read_bytes()).hexdigest(),
        },
        indent=2,
        sort_keys=True,
    ) + "\n"
    results = ROOT / "results"
    results.mkdir(exist_ok=True)
    (results / "accessibility_contract_check.json").write_text(
        rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
