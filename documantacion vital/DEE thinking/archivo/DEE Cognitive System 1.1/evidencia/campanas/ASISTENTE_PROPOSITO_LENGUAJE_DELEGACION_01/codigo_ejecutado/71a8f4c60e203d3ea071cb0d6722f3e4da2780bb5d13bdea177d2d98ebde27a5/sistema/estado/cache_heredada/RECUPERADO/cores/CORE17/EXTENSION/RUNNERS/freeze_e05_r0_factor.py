#!/usr/bin/env python3
"""Freeze R0_FACTOR_52 before final worlds."""
from __future__ import annotations
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from core17e_common import ROOT, append_ndjson, audit_kernel, seal, sha256_file, write_json


def main() -> None:
    discovery = ROOT / "DISCOVERY" / "C17E04_R0_FACTOR_COMPRESSION.json"
    runner = HERE / "run_e04_r0_compression_discovery.py"
    lock = seal({
        "schema": "dee.v27.core17.extension.r0_factor.freeze.v1",
        "claim_id": "C17E-CLAIM-002",
        "claim": "R0_FACTOR_52 is an exact multistep reduced quotient of the hash-pinned kernel in the stated well-formed domain.",
        "domain": "raw=0 or state>0; s_reg<=19664; clocks sufficiently far from uint64 wrap for the tested horizon",
        "apparatus": {"runner_sha256": sha256_file(runner), "discovery_sha256": sha256_file(discovery)},
        "frozen_encoding": {"ordinary_bits": 52, "semantic4_bits": 64, "clock_modulus": 304980, "ordinary_state": "existence bit", "semantic4_clock": "discarded"},
        "prediction": "10/10 fresh worlds, every tick, zero reduced raw and reduced clock mismatches",
        "metric": "cellwise equality after canonical reduction at every tick",
        "falsifier": "any mismatch",
        "canaries": [
            {"id": "C17E-CAN-004", "prerequisite": "direction retained", "ablation": "zero directions", "expected": "representation changes and causal trajectory diverges"},
            {"id": "C17E-CAN-005", "prerequisite": "semantic4 full raw retained", "ablation": "collapse its state magnitude", "expected": "exact reduced state mismatches"}
        ],
        "fresh_worlds": 10,
        "kernel": audit_kernel("CORE17E_R0_FACTOR_FREEZE")
    })
    write_json(ROOT / "FREEZE" / "C17E05_R0_FACTOR_LOCK.json", lock)
    append_ndjson(ROOT / "RESEARCH_DECISION_LOG.ndjson", {"id": "C17ED005", "decision": "Freeze R0_FACTOR_52", "lock_hash": lock["content_sha256"]})
    print(lock["content_sha256"])


if __name__ == "__main__": main()
