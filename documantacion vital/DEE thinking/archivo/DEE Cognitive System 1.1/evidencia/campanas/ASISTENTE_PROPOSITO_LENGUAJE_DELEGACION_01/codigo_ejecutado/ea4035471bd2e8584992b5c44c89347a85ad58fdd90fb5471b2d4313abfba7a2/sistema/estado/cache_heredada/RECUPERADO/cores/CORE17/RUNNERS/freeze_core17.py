#!/usr/bin/env python3
"""Freeze CORE17 confirmatory apparatus before challenge generation."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from core17_common import ROOT, audit_kernel, canonical_hash, read_json, sha256_file, utc, write_json


SOURCES = (
    "RUNNERS/core17_common.py",
    "RUNNERS/run_d03_probability_quantum.py",
    "RUNNERS/run_d05_emergent_physics.py",
    "RUNNERS/run_s01_model_selection.py",
    "RUNNERS/run_final_holdouts.py",
    "RUNNERS/VENDORED_CORE16/RUNNERS_NEW/occupancy_operator.py",
    "RUNNERS/VENDORED_CORE16/BASELINE_RUNNERS/core10_apparatus.py",
    "RUNNERS/VENDORED_CORE16/BASELINE_RUNNERS/core10_common.py",
    "RUNNERS/VENDORED_CORE16/BASELINE_RUNNERS/core12_apparatus.py",
    "RUNNERS/VENDORED_CORE16/BASELINE_RUNNERS/core12_common.py",
)


def main():
    audit_kernel("CORE17_SOURCE_FREEZE")
    challenge_path = ROOT / "FRESH_CHALLENGES" / "CORE17_FINAL_CHALLENGES.json"
    if challenge_path.exists():
        raise RuntimeError("fresh challenges already exist; source freeze must precede them")
    source_hashes = {rel: sha256_file(ROOT / rel) for rel in SOURCES}
    selection = read_json(ROOT / "MODEL_SELECTION" / "C17S01_MODEL_SELECTION.json")
    lock = {
        "schema": "dee.v27.core17.lock.v1", "lock_id": "CORE17_FINAL_LOCK", "frozen_utc": utc(),
        "source_hashes": source_hashes,
        "selection_result_sha256": selection["content_sha256"],
        "claims": [
            {"claim_id": "C17R01", "prediction": "Prepared and wrong receivers share the routed pre-arrival event but diverge functionally; matched integrated train counts retain distinct timing.", "metric": "all pairwise separators true", "threshold": "100% fresh cases"},
            {"claim_id": "C17R02", "prediction": "A raw-hidden local clock class returns only at the period gate and the changed-center count equals independent module count.", "metric": "changed centers", "threshold": "positive=modules; equal/off-gate=0"},
            {"claim_id": "C17R03", "prediction": "Binary hidden clock classes push forward exactly to P(R=r)=C(k,r)p^r(1-p)^(k-r).", "metric": "complete enumeration and weighted error", "threshold": "exact uniform counts; max error <1e-12"},
            {"claim_id": "C17R04", "prediction": "At the sealed k5/k6 interface one guard cell selects a repeated train: k5=max(0,floor((h-10)/2)), k6=0.", "metric": "distance-5 downstream events", "threshold": "exact count in all fresh cases"},
            {"claim_id": "C17R05", "prediction": "The occupancy-aware R0 operator reproduces native raw and clock buffers multistep.", "metric": "cell mismatches", "threshold": "zero across every fresh tick"},
        ],
        "bounded_nonpromoted": [
            {"id": "C17N01", "statement": "No compressed R* beyond R0 plus task/measure was found; scope is the tested collision matrix."},
            {"id": "C17N02", "statement": "No quantum-specific probability, interference, contextuality, noncommuting algebra or new valid Bell sector was found."},
            {"id": "C17N03", "statement": "The fixed XNOR scaffold does not regenerate a transferred learned policy."},
        ],
        "canaries": [
            {"claim": "C17R02", "prerequisite": "clock difference and on-period branch", "intervention": "equal-clock and off-gate controls", "expected": "zero changed centers"},
            {"claim": "C17R04", "prerequisite": "ordered semantic4 guard boundary", "intervention": "k5 versus k6", "expected": "transmission versus blocking"},
            {"claim": "C17R05", "prerequisite": "incumbent branch priority", "intervention": "occupied destination with incoming carrier", "expected": "not naive overwrite"},
            {"claim": "C17R01", "prerequisite": "causal route and prepared receiver", "intervention": "corridor cut versus offpath cut", "expected": "only corridor cut destroys function"},
        ],
        "data_partition": "DISCOVERY -> MODEL_SELECTION -> POST_FREEZE_FINAL_HOLDOUT",
    }
    lock["lock_sha256"] = canonical_hash(lock)
    write_json(ROOT / "HOLDOUT_LOCKS" / "CORE17_FINAL_LOCK.json", lock)
    print(json.dumps({"lock_sha256": lock["lock_sha256"], "sources": len(source_hashes), "claims": len(lock["claims"])}, indent=2))


if __name__ == "__main__":
    main()
