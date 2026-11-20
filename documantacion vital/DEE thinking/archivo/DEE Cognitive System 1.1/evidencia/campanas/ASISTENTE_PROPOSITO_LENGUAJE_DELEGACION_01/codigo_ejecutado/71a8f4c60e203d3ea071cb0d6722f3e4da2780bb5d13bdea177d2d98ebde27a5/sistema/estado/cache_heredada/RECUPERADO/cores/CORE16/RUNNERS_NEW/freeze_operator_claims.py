#!/usr/bin/env python3
"""Freeze occupied-operator and exact causal-quotient claims before challenges."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core16x_common import ROOT, audit_kernel, canonical_hash, read_json, sha256_file, update_state, utc, write_json


def main() -> None:
    audit_kernel("CORE16X_OPERATOR_SOURCE_FREEZE")
    discovery = read_json(ROOT / "DISCOVERY" / "OCCUPANCY_OPERATOR_DISCOVERY.json")
    selected = discovery["model_competition"][2]
    if selected["disposition"] != "SELECTED_FOR_FREEZE":
        raise RuntimeError("Operator was not selected")
    sources = {}
    for name in (
        "occupancy_operator.py",
        "native_runtime_x.py",
        "run_occupied_operator_discovery.py",
        "run_operator_holdouts.py",
    ):
        path = ROOT / "RUNNERS_NEW" / name
        if not path.is_file():
            raise FileNotFoundError(path)
        sources[name] = sha256_file(path)
    lock = {
        "lock_id": "C16X-LOCK-OCCUPANCY-OPERATOR-V1",
        "frozen_utc": utc(),
        "discovery_result_sha256": canonical_hash(discovery),
        "source_hashes": sources,
        "challenge_instances_exist_at_freeze": False,
        "claims": [
            {
                "claim_id": "C16X001",
                "claim": "The incumbent-priority local specification including empty incoming reduction, semantic4 protection, matter response, XNOR birth and post-update fusion deltas exactly predicts v27 raw and clock evolution over fresh multistep worlds.",
                "apparatus": "24 OS-entropy worlds, N in {7,8,9}, sparse-to-moderate mixed semantics, fusion-enabled cases, 3-7 ticks",
                "observer": "dual raw grid and clock grid SHA/equality at every tick",
                "metric": "all raw arrays and all clock arrays exact at every tick",
                "threshold": "24/24 worlds exact; zero cell mismatches",
                "prediction": "PASS",
                "time_window": "3-7 ticks fixed per challenge",
                "canary": "branch-priority reversal must disagree in targeted occupied-arrival cases",
            },
            {
                "claim_id": "C16X002",
                "claim": "For native evolution, non-semantic4 state payload compresses exactly to existence and local clock compresses to residue modulo 304980 (absent uint64 wrap); semantic4 raw remains explicit.",
                "apparatus": "paired fresh worlds: original versus canonical non-semantic4 state payload plus independent clock shifts by multiples of 304980",
                "observer": "raw equality plus effective clock-residue equality at every tick",
                "metric": "paired raw arrays exact and clock residues exact for all ticks",
                "threshold": "24/24 paired worlds exact",
                "prediction": "PASS",
                "time_window": "3-7 ticks; clocks chosen without uint64 wrap",
                "canary": "clock +1 in reachable period-195 tetrahedral gate must change raw; semantic4 payload removal must change observer raw",
            },
        ],
        "predeclared_scope": [
            "Hash-pinned v27 kernel only",
            "No claim across uint64 clock wrap for modulo-304980 equivalence",
            "External interventions that explicitly inspect or rewrite discarded payload are outside native equivalence",
            "Semantic4 raw is not compressed because it is an exact fixed native invariant",
        ],
        "negative_anchor": "Naive proposal-always-overwrites-incumbent must fail a targeted occupied-destination case.",
    }
    lock["lock_sha256"] = canonical_hash({k: v for k, v in lock.items() if k != "lock_sha256"})
    write_json(ROOT / "HOLDOUT_LOCKS" / "OCCUPANCY_OPERATOR_LOCK.json", lock)
    write_json(ROOT / "SOURCE_FREEZE_OPERATOR.json", {
        "freeze_id": lock["lock_id"],
        "frozen_utc": lock["frozen_utc"],
        "lock_sha256": lock["lock_sha256"],
        "source_hashes": sources,
        "challenge_instances_exist_at_freeze": False,
    })
    update_state(status="OPERATOR_FROZEN", current_phase="GENERATE_OPERATOR_FRESH_CHALLENGES", operator_lock_sha256=lock["lock_sha256"])
    print(json.dumps({"lock": lock["lock_id"], "sha256": lock["lock_sha256"], "sources": sources}, indent=2))


if __name__ == "__main__":
    main()

