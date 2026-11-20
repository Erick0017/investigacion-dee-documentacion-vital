#!/usr/bin/env python3
"""Freeze compact CORE17 as baseline and rank only its live frontier branches."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from core17e_common import (
    OFFICIAL_CORE17,
    PRE_EXTENSION_SHA256,
    ROOT,
    append_ndjson,
    audit_kernel,
    seal,
    sha256_file,
    utc,
    write_json,
)


def main() -> None:
    observed = sha256_file(OFFICIAL_CORE17)
    if observed != PRE_EXTENSION_SHA256:
        raise RuntimeError(f"CORE17 baseline mismatch: {observed}")
    kernel = audit_kernel("CORE17_DEFINITIVE_EXTENSION_BASELINE_FREEZE")
    baseline = seal(
        {
            "schema": "dee.v27.core17.definitive.baseline.v1",
            "created_utc": utc(),
            "status": "CORE17_BASELINE_LOCKED",
            "filename": OFFICIAL_CORE17.name,
            "bytes": OFFICIAL_CORE17.stat().st_size,
            "sha256": observed,
            "kernel": kernel,
            "completed_results_not_to_repeat": [
                "hidden-clock delay/return panel",
                "binomial probability pushforward panel",
                "k5/k6 macro-control law",
                "46-world final confirmation",
                "R0 exact operator holdout",
                "prior R* separator matrix",
            ],
        }
    )
    write_json(ROOT / "PRE_EXTENSION_CORE17_BASELINE.json", baseline)
    branches = [
        {"id": "F01_POLICY_REGENERATION", "value": 5, "constructibility": 5, "novelty": 5, "discrimination": 5, "cost": 3, "redundancy_risk": 1, "priority": 1, "next": "localize policy-bearing coordinate"},
        {"id": "F02_R0_COMPRESSION_LIMIT", "value": 5, "constructibility": 5, "novelty": 4, "discrimination": 5, "cost": 3, "redundancy_risk": 2, "priority": 2, "next": "test factorized bit-level quotient and lower-bound witnesses"},
        {"id": "F03_PERSISTENT_BODIES", "value": 4, "constructibility": 3, "novelty": 4, "discrimination": 4, "cost": 3, "redundancy_risk": 2, "priority": 3, "next": "hybrid mobility/regeneration compatibility attempts"},
        {"id": "F04_DISTRIBUTED_MEDIATOR", "value": 4, "constructibility": 2, "novelty": 3, "discrimination": 5, "cost": 2, "redundancy_risk": 4, "priority": 4, "next": "formal propagation audit plus constructible source-written background routes"},
        {"id": "F05_IDENTITY_EXCHANGE_THERMAL", "value": 4, "constructibility": 2, "novelty": 4, "discrimination": 4, "cost": 4, "redundancy_risk": 2, "priority": 5, "next": "reuse only if bodies or durable ports survive exchange"},
        {"id": "F06_QUANTUM_PREREQUISITES", "value": 5, "constructibility": 1, "novelty": 5, "discrimination": 5, "cost": 5, "redundancy_risk": 5, "priority": 6, "next": "mechanism-graph prerequisite audit; no nominal Bell/context test"},
        {"id": "F07_EXTERNAL_ROSETTA", "value": 5, "constructibility": 1, "novelty": 5, "discrimination": 2, "cost": 5, "redundancy_risk": 5, "priority": 7, "next": "only reopen if a new shared low-parameter internal law appears"},
    ]
    write_json(ROOT / "FRONTIER_PRIORITY.json", seal({"schema": "dee.v27.core17.frontier_priority.v1", "created_utc": utc(), "branches": branches}))
    append_ndjson(ROOT / "QUESTION_TREE.ndjson", {"question_id": "C17EQ001", "parent": "CORE17_FINAL_FRONTIER/F01", "question": "Which coordinate is necessary and sufficient for the transferred learned policy?", "competing": ["direction/history", "s_reg", "state payload", "clock", "distributed organization"], "next_experiment": "coordinate-specific intervention panel", "status": "OPEN"})
    append_ndjson(ROOT / "RESEARCH_DECISION_LOG.ndjson", {"decision_id": "C17ED001", "created_utc": utc(), "decision": "Prioritize policy coordinate and R0 compression; gate all human-category sectors on constructed prerequisites.", "basis": "frontier information-gain matrix"})
    append_ndjson(ROOT / "KERNEL_DIALOGUE.ndjson", {"question_id": "C17EQ001", "kernel_response": "PENDING", "status": "OPEN"})
    print(json.dumps({"baseline": baseline["sha256"], "branches": len(branches), "first": branches[0]["id"]}, indent=2))


if __name__ == "__main__":
    main()
