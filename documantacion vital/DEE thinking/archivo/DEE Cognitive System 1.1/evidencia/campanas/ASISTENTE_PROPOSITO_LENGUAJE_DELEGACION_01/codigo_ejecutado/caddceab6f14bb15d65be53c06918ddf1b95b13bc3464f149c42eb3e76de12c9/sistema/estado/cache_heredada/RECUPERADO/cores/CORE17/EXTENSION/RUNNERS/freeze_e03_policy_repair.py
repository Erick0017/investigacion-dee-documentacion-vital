#!/usr/bin/env python3
"""Freeze the redundant learned-policy reconstruction protocol before challenge generation."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from core17e_common import ROOT, append_ndjson, audit_kernel, seal, sha256_file, write_json


def main() -> None:
    discovery = ROOT / "DISCOVERY" / "C17E02_REDUNDANT_POLICY_REPAIR.json"
    runner = HERE / "run_e02_redundant_policy_repair.py"
    lock = seal({
        "schema": "dee.v27.core17.extension.policy_repair.freeze.v1",
        "claim_id": "C17E-CLAIM-001",
        "claim": "A causally intact redundant learned direction-state can carrier-reconstruct a damaged receiver policy and restore its fresh functional response.",
        "scope_guard": "Carrier-mediated redundant reconstruction; not autonomous local regeneration, nonlocal transfer, or restoration from occupancy alone.",
        "apparatus": {"runner_sha256": sha256_file(runner), "discovery_sha256": sha256_file(discovery)},
        "representation": "semantic-1 learned state; policy coordinate is direction; s_reg is nuisance-tested but retained by kernel",
        "prediction": {
            "treatment": "12/12 functional",
            "offpath_cut": "12/12 functional",
            "backup_untrained": "0/12 functional",
            "backup_direction_reset": "0/12 functional",
            "no_backup": "0/12 functional",
            "path_cut": "0/12 functional",
            "wrong_receiver": "0/12 functional"
        },
        "metric": "query direction equals frame-transformed ACTION1",
        "falsifier": "any treatment/offpath failure or any causal-negative success",
        "canaries": [
            {"id": "C17E-CAN-001", "prerequisite": "learned direction coordinate", "mode": "backup_direction_reset", "expected": "all fail"},
            {"id": "C17E-CAN-002", "prerequisite": "intact carrier path", "mode": "path_cut", "expected": "all fail"},
            {"id": "C17E-CAN-003", "prerequisite": "spatially specific path", "mode": "offpath_cut", "expected": "all pass"}
        ],
        "fresh_worlds": 12,
        "challenge_generation": "separate post-freeze OS entropy; seed and complete geometry preserved",
        "kernel": audit_kernel("CORE17E_POLICY_REPAIR_FREEZE")
    })
    write_json(ROOT / "FREEZE" / "C17E03_POLICY_REPAIR_LOCK.json", lock)
    append_ndjson(ROOT / "RESEARCH_DECISION_LOG.ndjson", {"id": "C17ED003", "decision": "Freeze C17E-CLAIM-001 before fresh challenge generation", "lock_hash": lock["content_sha256"]})
    print(lock["content_sha256"])


if __name__ == "__main__":
    main()
