#!/usr/bin/env python3
"""Final audits, reproducible manifest, ZIP validation, and atomic publication."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core16x_common import (  # noqa: E402
    ARCHIVE,
    BASELINE,
    BASELINE_SHA256,
    EXPECTED_KERNEL,
    OFFICIAL,
    OFFICIAL_NAME,
    ROOT,
    audit_kernel,
    canonical_hash,
    read_json,
    sha256_file,
    update_state,
    utc,
    write_json,
    write_text,
)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def iter_package_files() -> list[Path]:
    out = []
    excluded_dirs = {"PACKAGE_STAGING", "REPORTS", "__pycache__"}
    excluded_files = {"OFFICIAL_ZIP_SEAL.json", "HASHES.sha256", "MANIFEST.json"}
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        rp = p.relative_to(ROOT)
        if any(part in excluded_dirs for part in rp.parts):
            continue
        if p.name in excluded_files or p.suffix == ".pyc" or p.name.endswith(".tmp"):
            continue
        out.append(p)
    return sorted(out, key=lambda x: rel(x).lower())


def hashes_root(rows: list[dict]) -> str:
    return canonical_hash([{"path": x["path"], "sha256": x["sha256"]} for x in rows])


def validate_json_tree() -> dict:
    parsed_json = 0
    parsed_ndjson = 0
    errors = []
    for p in iter_package_files():
        try:
            if p.suffix.lower() == ".json":
                json.loads(p.read_text(encoding="utf-8-sig"))
                parsed_json += 1
            elif p.suffix.lower() == ".ndjson":
                for i, line in enumerate(p.read_text(encoding="utf-8-sig").splitlines(), 1):
                    if line.strip():
                        json.loads(line)
                parsed_ndjson += 1
        except Exception as exc:
            errors.append({"path": rel(p), "error": str(exc)})
    return {"json": parsed_json, "ndjson": parsed_ndjson, "errors": errors, "pass": not errors}


def validate_baseline() -> dict:
    failures = []
    checked = 0
    for line in (BASELINE / "HASHES.sha256").read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        digest, name = line.split(maxsplit=1)
        name = name.lstrip("*")
        p = BASELINE / Path(name.replace("/", os.sep))
        if not p.exists() or sha256_file(p) != digest:
            failures.append(name)
        checked += 1
    return {"checked": checked, "failures": failures, "pass": not failures}


def required_files() -> tuple[list[str], list[str]]:
    machine = [
        "SUPERSEDED_CORE16_BASELINE.json", "FULL_PARENT_CLAIM_INGESTION.json", "CORE01_16_COMPLETE_CLAIM_GRAPH.json",
        "CORE01_16_COMPLETE_MECHANISM_GRAPH.json", "DEE_FULL_STATE_SCHEMA.json", "DEE_INFORMATION_CAUSAL_ATLAS.json",
        "REALITY_LEVEL_GRAPH.json", "REALITY_LADDER.json", "OBSERVER_ACCESSIBILITY_MATRIX.json", "CROSS_SCALE_INFORMATION_FLOW.json",
        "HIDDEN_STATE_RESURRECTION.json", "DELAYED_OBSERVABILITY.json", "CROSS_SCALE_MEMORY.json", "EFFECTIVE_PROBABILITY_ATLAS.json",
        "EFFECTIVE_PROBABILITY_MEASURE_SEARCH.json", "QUANTUM_LIKE_LEVEL_ATLAS.json", "MACRO_QUANTUM_SURVIVAL.json",
        "MULTILEVEL_BELL_AUDIT.json", "BELL_ASSUMPTION_AUDIT.json", "MEASUREMENT_BACKACTION.json", "CONTEXTUALITY_TESTS.json",
        "EFFECTIVE_NONCOMMUTATIVITY.json", "CLASSICAL_EMERGENCE.json", "THERMODYNAMIC_LEVEL_SEARCH.json", "FIELD_LEVEL_SEARCH.json",
        "WAVE_LEVEL_SEARCH.json", "OCCUPANCY_AWARE_DESTINATION_OPERATOR.json", "MULTISTEP_EFFECTIVE_DYNAMICS.json",
        "LARGE_SCALE_REALITY.json", "CAPABILITY_ATLAS.json", "REALITY_ENGINEERING_ACCESS.json",
        "TRANSFER_REINSTANTIATION_TAXONOMY.json", "PROGRAMMABILITY_SEARCH.json", "UNCLASSIFIED_NATIVE_REALITY.json",
        "PHYSICS_PLACEMENT_ATLAS.json", "MULTILEVEL_ROSETTA.json", "EXTERNAL_ACCESS_PROTOCOLS.json",
        "EXTERNAL_UNUSED_PREDICTIONS.json", "QUESTION_TREE.ndjson", "KERNEL_DIALOGUE.ndjson", "RESEARCH_DECISION_LOG.ndjson",
        "CLAIM_LEDGER.json", "HOLDOUT_REGISTRY.json", "CANARY_REGISTRY.json", "CORE16_COMPLETENESS_AUDIT.json",
        "REPORT_CONSISTENCY_AUDIT.json", "KERNEL_IMMUTABILITY_AUDIT.json", "PARENT_CHAIN.json", "SOURCE_FREEZE.json",
    ]
    reports = [
        "EXECUTIVE_VERDICT.md", "WHAT_REALITY_IS_IN_DEE.md", "THE_DISCOVERED_LEVELS_OF_REALITY.md",
        "WHAT_HUMANS_ACTUALLY_OBSERVE.md", "WHAT_INFORMATION_IS_HIDDEN_FROM_PHYSICS.md",
        "WHAT_HIDDEN_INFORMATION_CAN_RETURN.md", "WHERE_QUANTUM_PHYSICS_FITS.md",
        "DO_QUANTUM_PROPERTIES_SURVIVE_AT_LARGE_SCALE.md", "HOW_CLASSICAL_PHYSICS_EMERGES.md",
        "HOW_STATISTICAL_PHYSICS_EMERGES.md", "HOW_THERMODYNAMICS_COULD_EMERGE.md",
        "FIELDS_AND_WAVES_AT_EFFECTIVE_LEVELS.md", "MULTISTEP_EFFECTIVE_PHYSICS.md", "BELL_REASSESSMENT.md",
        "KNOWN_PHYSICS_INSIDE_DEE.md", "DEE_BEYOND_KNOWN_PHYSICS.md", "CAPABILITIES_OF_THE_REPRESENTED_REALITY.md",
        "SCIENCE_FICTION_LIKE_CAPABILITIES_DECOMPOSED.md", "WHAT_COULD_IN_PRINCIPLE_BE_ENGINEERED.md",
        "WHAT_HUMAN_TECHNOLOGY_CANNOT_CURRENTLY_ACCESS.md", "UNCLASSIFIED_NATIVE_REALITY.md",
        "MULTILEVEL_ROSETTA_STATUS.md", "UNRESOLVED_EXTERNAL_CORRESPONDENCES.md", "ADVERSARIAL_REVIEW.md",
        "FINAL_FRONTIER.md", "FINAL_REPORT.md",
    ]
    return machine, reports


audit_kernel("prepackage_final")
previous_observed = sha256_file(OFFICIAL)
trusted_predecessors = {BASELINE_SHA256}
prior_seal_path = ROOT / "OFFICIAL_ZIP_SEAL.json"
if prior_seal_path.exists():
    prior_seal = read_json(prior_seal_path)
    if prior_seal.get("NEW_CORE16_SHA256"):
        trusted_predecessors.add(prior_seal["NEW_CORE16_SHA256"])
if previous_observed not in trusted_predecessors:
    raise RuntimeError(f"Official predecessor is not a trusted sealed image: {previous_observed}")

json_audit = validate_json_tree()
baseline_audit = validate_baseline()
machine_required, reports_required = required_files()
missing = [x for x in machine_required + reports_required if not (ROOT / x).exists()]

ingestion = read_json(ROOT / "FULL_PARENT_CLAIM_INGESTION.json")
completeness = read_json(ROOT / "CORE16_COMPLETENESS_AUDIT.json")
report_consistency = read_json(ROOT / "REPORT_CONSISTENCY_AUDIT.json")
kernel = read_json(ROOT / "KERNEL_IMMUTABILITY_AUDIT.json")
holdouts = read_json(ROOT / "HOLDOUT_REGISTRY.json")
canaries = read_json(ROOT / "CANARY_REGISTRY.json")

holdout_pass = all(x.get("status") == "PASS" for x in holdouts["expansion"])
canary_pass = canaries.get("all_expansion_canaries_pass") is True
locks_valid = True
lock_checks = []
for item in holdouts["expansion"]:
    result = read_json(ROOT / item["result"])
    observed_lock = sha256_file(ROOT / item["lock"])
    expected_lock = result.get("lock_sha256")
    lock_payload = read_json(ROOT / item["lock"])
    observed_lock = canonical_hash({k: v for k, v in lock_payload.items() if k != "lock_sha256"})
    ok = expected_lock == observed_lock == lock_payload.get("lock_sha256")
    locks_valid &= ok
    lock_checks.append({"id": item["id"], "expected": expected_lock, "observed": observed_lock, "pass": ok})

gates = {
    "official_predecessor_trusted": previous_observed in trusted_predecessors,
    "baseline_internal_hashes": baseline_audit["pass"],
    "json_ndjson_parse": json_audit["pass"],
    "required_outputs_present": not missing,
    "full_parent_coverage": ingestion.get("coverage_pass") is True and ingestion.get("source_count") == 17,
    "completion_audit": completeness.get("status") == "PASS" and all(completeness.get("gates", {}).values()),
    "report_consistency": report_consistency.get("status") == "PASS",
    "kernel_immutable": kernel.get("all_pass") is True,
    "expansion_holdouts": holdout_pass,
    "expansion_canaries": canary_pass,
    "lock_result_binding": locks_valid,
}
prepackage_pass = all(gates.values())
write_json(ROOT / "PREPACKAGE_AUDIT.json", {
    "schema": "dee.v27.core16x.prepackage_audit.v1",
    "created_utc": utc(),
    "status": "PASS" if prepackage_pass else "FAIL",
    "gates": gates,
    "baseline_hash_audit": baseline_audit,
    "json_audit": json_audit,
    "missing": missing,
    "lock_checks": lock_checks,
})
if not prepackage_pass:
    raise RuntimeError(f"Prepackage gates failed: {gates}, missing={missing}")

state = read_json(ROOT / "STATE.json")
checkpoints = list(dict.fromkeys(state.get("completed_checkpoints", []) + [
    "BASELINE_AUDIT", "FULL_PARENT_CLAIM_INGESTION", "FULL_STATE_CAUSAL_AUDIT",
    "OCCUPANCY_OPERATOR_DISCOVERY", "OCCUPANCY_OPERATOR_HOLDOUT", "HIDDEN_ACCESSIBILITY_DISCOVERY",
    "PROBABILITY_MEASURE_DISCOVERY", "PROBABILITY_HOLDOUT", "QUANTUM_MULTILEVEL_DISCOVERY",
    "QUANTUM_SCALE_HOLDOUT", "EFFECTIVE_LEVEL_PHYSICS_FRONTS", "FUNCTIONAL_CAPABILITY_HOLDOUT",
    "CANONICAL_SYNTHESIS", "COMPLETENESS_AUDIT", "REPORT_CONSISTENCY_AUDIT", "PREPACKAGE_AUDIT",
]))
update_state(
    status="COMPLETE",
    current_phase="SEALED_PACKAGE_IMAGE_PENDING_ARCHIVE_DIGEST",
    level_graph_status="FINAL",
    completed_checkpoints=checkpoints,
    prepackage_audit="PASS",
    official_zip=str(OFFICIAL),
    official_zip_sha256=None,
    archive_digest_note="Recorded after atomic seal in OFFICIAL_ZIP_SEAL.json; a ZIP cannot contain its own full-file SHA-256.",
)

# A ZIP cannot contain its own exact full-file SHA-256 without changing it.  The
# exact archive digest is therefore placed in the post-seal ledger beside the
# work product; the archive contains the prior digest and the scientific content
# root, plus an explicit self-reference note.
science_files = [p for p in iter_package_files() if p.name not in {"PACKAGE_PROVENANCE.json", "PREPACKAGE_AUDIT.json", "STATE.json"}]
content_rows = [{"path": rel(p), "sha256": sha256_file(p), "bytes": p.stat().st_size} for p in science_files]
scientific_root = hashes_root(content_rows)
write_json(ROOT / "PACKAGE_PROVENANCE.json", {
    "schema": "dee.v27.core16x.package_provenance.v1",
    "created_utc": utc(),
    "PREVIOUS_CORE16_SHA256": BASELINE_SHA256,
    "NEW_CORE16_SHA256": None,
    "NEW_CORE16_SCIENTIFIC_CONTENT_SHA256": scientific_root,
    "new_archive_sha_location": "post-seal OFFICIAL_ZIP_SEAL.json and final console summary",
    "self_reference_note": "An archive cannot truthfully contain its own full-file SHA-256; embedding that digest changes the digest.",
    "baseline_preserved_at": "BASELINE_CORE16_LOCKED/",
})

content_files = iter_package_files()
content_rows = [{"path": rel(p), "sha256": sha256_file(p), "bytes": p.stat().st_size} for p in content_files]
manifest = {
    "schema": "dee.v27.core16x.manifest.v2",
    "created_utc": utc(),
    "core": "CORE16_CORRECTED_EXPANDED_SUPERSEDING",
    "campaign_premise": "P0_FIXED_DEE_IS_THE_REPRESENTATION_OF_THE_REALITY_BEING_STUDIED",
    "status": "COMPLETE",
    "official_filename": OFFICIAL_NAME,
    "previous_core16_sha256": BASELINE_SHA256,
    "scientific_content_sha256": scientific_root,
    "content_member_count_excluding_manifest_and_hashlist": len(content_rows),
    "content_bytes_excluding_manifest_and_hashlist": sum(x["bytes"] for x in content_rows),
    "baseline_files": 123,
    "baseline_claims_preserved": 9,
    "new_claims_fresh_confirmed": 8,
    "parent_claim_records": 4357,
    "reduced_levels": 4,
    "kernel": EXPECTED_KERNEL,
    "required_machine_outputs": machine_required,
    "required_reports": reports_required,
    "prepackage_audit": "PASS",
}
write_json(ROOT / "MANIFEST.json", manifest)

# Hash list covers every member except itself.  It is checked from inside the
# temporary archive before the official file is replaced.
hash_files = iter_package_files() + [ROOT / "MANIFEST.json"]
hash_files = sorted({p.resolve(): p for p in hash_files}.values(), key=lambda x: rel(x).lower())
hash_lines = [f"{sha256_file(p)} *{rel(p)}" for p in hash_files]
write_text(ROOT / "HASHES.sha256", "\n".join(hash_lines) + "\n")

package_files = hash_files + [ROOT / "HASHES.sha256"]
package_files = sorted({p.resolve(): p for p in package_files}.values(), key=lambda x: rel(x).lower())
staging = ROOT / "PACKAGE_STAGING"
staging.mkdir(parents=True, exist_ok=True)
temp_zip = staging / (OFFICIAL_NAME + ".tmp")
if temp_zip.exists():
    temp_zip.unlink()
with zipfile.ZipFile(temp_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True) as zf:
    for p in package_files:
        zf.write(p, rel(p))

# Verify CRC, exact member set, nested ZIP exclusion, required files, and every
# internal digest before atomic replacement.
with zipfile.ZipFile(temp_zip, "r") as zf:
    bad_crc = zf.testzip()
    names = zf.namelist()
    expected_names = [rel(p) for p in package_files]
    if bad_crc is not None:
        raise RuntimeError(f"ZIP CRC failed at {bad_crc}")
    if names != expected_names:
        raise RuntimeError("ZIP member set/order mismatch")
    if any(name.lower().endswith(".zip") for name in names):
        raise RuntimeError("Nested ZIP detected")
    inside_hashes = zf.read("HASHES.sha256").decode("utf-8").splitlines()
    for line in inside_hashes:
        digest, name = line.split(maxsplit=1)
        name = name.lstrip("*")
        observed = hashlib.sha256(zf.read(name)).hexdigest()
        if observed != digest:
            raise RuntimeError(f"Internal hash mismatch: {name}")
    for name in machine_required + reports_required:
        if name not in names:
            raise RuntimeError(f"Required member missing: {name}")

temp_sha = sha256_file(temp_zip)
temp_bytes = temp_zip.stat().st_size
ARCHIVE.mkdir(parents=True, exist_ok=True)
os.replace(temp_zip, OFFICIAL)
official_sha = sha256_file(OFFICIAL)
if official_sha != temp_sha or OFFICIAL.stat().st_size != temp_bytes:
    raise RuntimeError("Atomic replacement post-check failed")
with zipfile.ZipFile(OFFICIAL, "r") as zf:
    if zf.testzip() is not None:
        raise RuntimeError("Official ZIP CRC failed after replacement")

audit_kernel("postpackage_final")
ended = utc()
started = parse_time(state["started_utc"])
elapsed = (parse_time(ended) - started).total_seconds()
seal = {
    "schema": "dee.v27.core16x.official_zip_seal.v1",
    "sealed_utc": ended,
    "PREVIOUS_CORE16_SHA256": BASELINE_SHA256,
    "NEW_CORE16_SHA256": official_sha,
    "NEW_CORE16_SCIENTIFIC_CONTENT_SHA256": scientific_root,
    "official_path": str(OFFICIAL),
    "bytes": temp_bytes,
    "members": len(package_files),
    "crc_pass": True,
    "internal_hashes_pass": True,
    "atomic_replacement": True,
    "elapsed_seconds": elapsed,
}
write_json(ROOT / "OFFICIAL_ZIP_SEAL.json", seal)
update_state(
    status="COMPLETE",
    current_phase="SEALED",
    official_zip=str(OFFICIAL),
    official_zip_sha256=official_sha,
    official_zip_bytes=temp_bytes,
    official_zip_members=len(package_files),
    elapsed_seconds=elapsed,
    completed_checkpoints=checkpoints + ["ATOMIC_PACKAGE_SEAL"],
)

siblings = sorted(p.name for p in ARCHIVE.glob("16_DEE_V27_*RESULTADOS.zip"))
summary = {
    "status": "COMPLETE",
    "previous_core16_sha256": BASELINE_SHA256,
    "new_core16_sha256": official_sha,
    "kernel_sha256": EXPECTED_KERNEL["kernel"],
    "elapsed_seconds": elapsed,
    "baseline_claims_preserved": 9,
    "new_claims": 8,
    "parent_claim_records": 4357,
    "reduced_levels": 4,
    "new_holdouts": 4,
    "new_canaries": 8,
    "occupied_operator": "24/24 worlds; 118 ticks; 0 mismatches",
    "probability": "576/576 exact; classical measure-conditioned",
    "macro_phase": "survives/recoverable through size 30; not quantum-specific",
    "bell": "CHSH=-2 in only valid constructed apparatus",
    "rosetta": "MULTILEVEL_INTERNAL_INFORMATION_ROSETTA_NO_FROZEN_EXTERNAL_MAP",
    "official_zip": str(OFFICIAL),
    "bytes": temp_bytes,
    "members": len(package_files),
    "core16_named_archives": siblings,
}
print(json.dumps(summary, indent=2, ensure_ascii=False))
