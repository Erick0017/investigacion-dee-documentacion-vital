#!/usr/bin/env python3
"""Validate and freeze the sealed CORE16 baseline before expanded work."""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core16x_common import (
    ARCHIVE,
    BASELINE,
    BASELINE_SHA256,
    OFFICIAL,
    ROOT,
    append_ndjson,
    audit_kernel,
    read_json,
    sha256_file,
    update_state,
    utc,
    write_json,
)


def validate_extracted_hashes() -> dict:
    hash_path = BASELINE / "HASHES.sha256"
    mismatches = []
    checked = 0
    for line in hash_path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        expected, rel = line.split(maxsplit=1)
        rel = rel.lstrip("* ").replace("/", str(Path("/")).replace("/", "\\"))
        target = BASELINE / Path(rel)
        observed = sha256_file(target) if target.is_file() else None
        checked += 1
        if observed != expected.lower():
            mismatches.append({"path": rel, "expected": expected.lower(), "observed": observed})
    return {"entries_checked": checked, "mismatches": mismatches, "pass": not mismatches}


def main() -> None:
    prior_sha = sha256_file(OFFICIAL)
    if prior_sha != BASELINE_SHA256:
        raise RuntimeError(f"Prior CORE16 ZIP is not the expected sealed baseline: {prior_sha}")
    with zipfile.ZipFile(OFFICIAL) as archive:
        bad_crc = archive.testzip()
        member_count = len(archive.infolist())
    internal = validate_extracted_hashes()
    if bad_crc is not None or not internal["pass"]:
        raise RuntimeError(f"Baseline validation failed: crc={bad_crc}, hashes={internal}")
    manifest = read_json(BASELINE / "MANIFEST.json")
    ledger = read_json(BASELINE / "CLAIM_LEDGER.json")
    kernel = read_json(BASELINE / "KERNEL_IMMUTABILITY_AUDIT.json")
    holdouts = read_json(BASELINE / "HOLDOUT_REGISTRY.json")
    canaries = read_json(BASELINE / "CANARY_REGISTRY.json")
    summary = read_json(BASELINE / "CORE16_CANONICAL_SUMMARY.json")
    kernel_row = audit_kernel("CORE16X_BASELINE_PREFLIGHT")
    claim_lists = {k: len(v) for k, v in ledger.items() if isinstance(v, list)}
    payload = {
        "baseline_status": "BASELINE_CORE16_LOCKED",
        "campaign_premise_correction": "P0_FIXED_DEE_IS_THE_REPRESENTATION_OF_THE_REALITY_BEING_STUDIED",
        "created_utc": utc(),
        "prior_zip": OFFICIAL.name,
        "prior_zip_sha256": prior_sha,
        "prior_zip_bytes": OFFICIAL.stat().st_size,
        "prior_manifest_status": manifest.get("status", manifest.get("canonical_summary", {}).get("status")),
        "prior_internal_hash_status": internal,
        "prior_zip_crc_pass": bad_crc is None,
        "prior_zip_members": member_count,
        "prior_kernel_identity": kernel.get("expected"),
        "current_kernel_preflight": kernel_row,
        "prior_claim_containers": claim_lists,
        "prior_claim_ledger_sha256": sha256_file(BASELINE / "CLAIM_LEDGER.json"),
        "prior_holdout_registry_sha256": sha256_file(BASELINE / "HOLDOUT_REGISTRY.json"),
        "prior_canary_registry_sha256": sha256_file(BASELINE / "CANARY_REGISTRY.json"),
        "prior_canonical_summary": summary,
        "prior_limitations": [
            "Parent claim ingestion recorded zero CORE15 claims because it assumed one claims schema.",
            "E1/E2/E3 were useful task-relative levels but were not rebuilt from the complete CORE01-CORE15 plus MASTER corpus.",
            "The sparse destination operator failed occupied-destination multistep cases and was not mechanistically repaired.",
            "Quantum-like and cross-scale searches did not exhaust all justified effective levels or macroscopic organizations.",
            "Native capabilities were reported under a conditional epistemic frame superseded by fixed campaign premise P0.",
        ],
        "reason_for_reopening": "Correct the campaign premise and parent-ingestion defect; empirically rebuild levels, occupied-destination dynamics, cross-scale information, native capabilities, and multilevel Rosetta without discarding valid computational evidence.",
        "baseline_preservation_rule": "Files under BASELINE_CORE16_LOCKED are evidence imported from the sealed prior ZIP and are not new confirmation.",
    }
    write_json(ROOT / "SUPERSEDED_CORE16_BASELINE.json", payload)
    write_json(ROOT / "SCIENTIFIC_BOUNDARIES.json", {
        "campaign_premise": payload["campaign_premise_correction"],
        "do_not_test_or_downgrade_P0": True,
        "native_facts_precede_external_labels": True,
        "unresolved_external_correspondence_is_not_native_falsification": True,
        "P0_is_not_a_license_to_force_fit": True,
        "confirmation_requires_freeze_then_fresh_worlds": True,
        "previous_core16_is_locked_baseline": True,
    })
    append_ndjson(ROOT / "QUESTION_TREE.ndjson", {
        "question_id": "C16X-Q000",
        "parent_id": None,
        "phase": "BOUNDARY",
        "question": "What information and mechanisms are missing from the prior CORE16 interpretation because parent claims were not ingested schema-aware?",
        "decision_rule": "Complete corpus ingestion before interpreting or extending effective levels.",
        "status": "OPEN",
    })
    append_ndjson(ROOT / "RESEARCH_DECISION_LOG.ndjson", {
        "decision_id": "C16X-D000",
        "basis": "Superseding prompt plus verified sealed baseline",
        "decision": "Preserve prior results as locked evidence and repair full parent ingestion before new science.",
        "baseline_sha256": prior_sha,
    })
    update_state(
        status="BASELINE_LOCKED_VALIDATED",
        prior_core16_sha256=prior_sha,
        baseline_internal_hashes_pass=True,
        baseline_zip_crc_pass=True,
        kernel_pass=True,
        current_phase="FULL_PARENT_CLAIM_INGESTION",
        completed_checkpoints=["BASELINE_AUDIT"],
    )
    print(json.dumps({"baseline_sha256": prior_sha, "members": member_count, "internal_hashes": internal["entries_checked"], "kernel": kernel_row["observed"]}, indent=2))


if __name__ == "__main__":
    main()
