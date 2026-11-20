#!/usr/bin/env python3
"""Validate, manifest and atomically publish the single official CORE16 ZIP."""
from __future__ import annotations

import json
import os
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "RUNNERS"))
from core16_common import (OFFICIAL, ROOT, EXPECTED, audit_kernel, kernel_paths,
                           read_json, sha, update_state, utc, write_json, write_text)


REQUIRED_MACHINE = [
    "REALITY_LADDER.json", "LEVEL_DISCOVERY_REGISTRY.json", "LEVEL_SELECTION_HOLDOUTS.json",
    "PROPERTY_RESPONSE_SPACE.json", "CROSS_SCALE_INFORMATION_FLOW.json", "HIDDEN_STATE_RESURRECTION.json",
    "CROSS_LEVEL_COMMUTATION.json", "RENORMALIZATION_FLOW.json", "EFFECTIVE_PROBABILITY_ATLAS.json",
    "QUANTUM_LIKE_LEVEL_ATLAS.json", "PHASE_COHERENCE_ATLAS.json", "CONTEXTUALITY_TESTS.json",
    "MEASUREMENT_BACKACTION.json", "MULTILEVEL_BELL_AUDIT.json", "BELL_ASSUMPTION_AUDIT.json",
    "DECOHERENCE_CLASSICALIZATION.json", "MACRO_QUANTUM_SURVIVAL.json", "CLASSICAL_EMERGENCE.json",
    "CAPABILITY_ATLAS.json", "TRANSFER_REINSTANTIATION_TAXONOMY.json", "CONFIGURATION_TRANSFORMATION.json",
    "MACRO_AMPLIFICATION.json", "UNCLASSIFIED_NATIVE_PHENOMENA.json", "CROSS_SCALE_CAUSAL_GRAPH.json",
    "MULTILEVEL_ROSETTA.json", "EXTERNAL_UNUSED_PREDICTIONS.json", "QUESTION_TREE.ndjson",
    "KERNEL_DIALOGUE.ndjson", "RESEARCH_DECISION_LOG.ndjson", "CLAIM_LEDGER.json",
    "HOLDOUT_REGISTRY.json", "CANARY_REGISTRY.json", "KERNEL_IMMUTABILITY_AUDIT.json",
    "PARENT_CHAIN.json", "SOURCE_FREEZE.json", "FROZEN_CLAIM_CONTRACTS.json",
    "REPORT_CONSISTENCY_AUDIT.json", "CORE16_COMPLETENESS_AUDIT.json", "STATE.json",
]
REQUIRED_REPORTS = [
    "EXECUTIVE_VERDICT.md", "WHAT_LEVELS_OF_REALITY_EXIST.md", "WHAT_INFORMATION_AN_OBSERVER_LOSES.md",
    "WHAT_HIDDEN_INFORMATION_CAN_RETURN.md", "WHERE_QUANTUM_LIKE_BEHAVIOR_APPEARS.md", "BELL_REASSESSMENT.md",
    "HOW_CLASSICAL_REALITY_EMERGES.md", "DO_QUANTUM_PROPERTIES_SURVIVE_MACROSCOPICALLY.md",
    "INFORMATION_TO_EFFECTIVE_PHYSICS.md", "DEE_CAPABILITIES_BEYOND_CURRENT_PHYSICAL_LABELS.md",
    "SCIENCE_FICTION_LIKE_EFFECTS_MECHANISTICALLY_DECOMPOSED.md", "UNCLASSIFIED_NATIVE_PHYSICS.md",
    "WHERE_KNOWN_PHYSICAL_THEORIES_FIT.md", "MULTILEVEL_ROSETTA_STATUS.md", "ADVERSARIAL_REVIEW.md",
    "FINAL_FRONTIER.md", "FINAL_REPORT.md",
]


def payload_files():
    excluded_roots = {"PARENT_CORE15_LOCKED", "output", "__pycache__"}
    excluded_names = {"MANIFEST.json", "HASHES.sha256"}
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if rel.parts[0] in excluded_roots or "__pycache__" in rel.parts or path.name in excluded_names or path.suffix == ".tmp":
            continue
        files.append(path)
    return sorted(files, key=lambda p: p.relative_to(ROOT).as_posix())


def main():
    missing = [name for name in REQUIRED_MACHINE + REQUIRED_REPORTS if not (ROOT / name).is_file()]
    if missing:
        raise RuntimeError(f"required artifacts missing: {missing}")
    if not read_json(ROOT / "CORE16_COMPLETENESS_AUDIT.json")["pass"]:
        raise RuntimeError("completeness audit failed")
    if not read_json(ROOT / "REPORT_CONSISTENCY_AUDIT.json")["pass"]:
        raise RuntimeError("report consistency audit failed")
    if read_json(ROOT / "LEVEL_SELECTION_HOLDOUTS.json")["status"] != "PASS":
        raise RuntimeError("final holdouts not all PASS")
    audit_kernel("CORE16_BEFORE_FINAL_PACKAGE")
    update_state(status="COMPLETE_SEALED", phase="COMPLETE", official_zip=OFFICIAL.name, package_manifest_pending=False)

    files = payload_files()
    manifest = {
        "schema": "dee.v27.core16.package_manifest.v1",
        "core": "CORE16", "status": "COMPLETE_SEALED", "created_utc": utc(),
        "official_name": OFFICIAL.name,
        "parent": {"name": "CORE15_EXPANDED", "sha256": read_json(ROOT / "PARENT_CHAIN.json")["parent_zip_sha256"], "embedded": False},
        "kernel": {"expected": EXPECTED, "immutability_pass": read_json(ROOT / "KERNEL_IMMUTABILITY_AUDIT.json")["all_pass"]},
        "source_freeze_sha256": sha(ROOT / "SOURCE_FREEZE.json"),
        "challenge_manifest_sha256": sha(ROOT / "FINAL_HOLDOUTS" / "FINAL_CHALLENGE_MANIFEST.json"),
        "canonical_summary": read_json(ROOT / "CORE16_CANONICAL_SUMMARY.json"),
        "required_machine_artifacts": REQUIRED_MACHINE,
        "required_reports": REQUIRED_REPORTS,
        "payload_file_count": len(files),
        "payload_bytes": sum(p.stat().st_size for p in files),
        "files": [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p), "bytes": p.stat().st_size} for p in files],
        "excluded_research_cache": ["PARENT_CORE15_LOCKED/", "output/"],
        "contains_parent_zip": False,
    }
    write_json(ROOT / "MANIFEST.json", manifest)
    all_files = payload_files() + [ROOT / "MANIFEST.json"]
    lines = [f"{sha(p)} *{p.relative_to(ROOT).as_posix()}" for p in sorted(all_files, key=lambda x: x.relative_to(ROOT).as_posix())]
    write_text(ROOT / "HASHES.sha256", "\n".join(lines) + "\n")

    # Verify filesystem payload before compression.
    for line in (ROOT / "HASHES.sha256").read_text(encoding="utf-8").splitlines():
        expected, rel = line.split(" *", 1)
        path = ROOT / Path(rel)
        if not path.is_file() or sha(path) != expected:
            raise RuntimeError(f"prepackage hash mismatch: {rel}")

    temporary = OFFICIAL.with_suffix(OFFICIAL.suffix + ".tmp")
    if temporary.exists():
        temporary.unlink()
    package_files = payload_files() + [ROOT / "MANIFEST.json", ROOT / "HASHES.sha256"]
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True) as archive:
        for path in sorted(package_files, key=lambda x: x.relative_to(ROOT).as_posix()):
            archive.write(path, path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(temporary) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f"ZIP CRC failure: {bad}")
        names = archive.namelist()
        if any(name.startswith("PARENT_CORE15_LOCKED/") or name.lower().endswith(".zip") for name in names):
            raise RuntimeError("parent or nested ZIP embedded")
        state = json.loads(archive.read("STATE.json").decode("utf-8-sig"))
        zipped_manifest = json.loads(archive.read("MANIFEST.json").decode("utf-8-sig"))
        if state["status"] != "COMPLETE_SEALED" or zipped_manifest["status"] != "COMPLETE_SEALED":
            raise RuntimeError("sealed state/manifest mismatch")
        hashes = archive.read("HASHES.sha256").decode("utf-8-sig").splitlines()
        for line in hashes:
            expected, rel = line.split(" *", 1)
            if hashlib_sha256(archive.read(rel)) != expected:
                raise RuntimeError(f"internal ZIP hash mismatch: {rel}")
    OFFICIAL.parent.mkdir(parents=True, exist_ok=True)
    os.replace(temporary, OFFICIAL)

    # Final read-only identity and package verification.
    observed_kernel = {name: sha(path) for name, path in kernel_paths().items()}
    if observed_kernel != EXPECTED:
        raise RuntimeError(f"postpackage kernel mismatch: {observed_kernel}")
    with zipfile.ZipFile(OFFICIAL) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("official ZIP CRC failed after atomic replace")
    result = {"status": "COMPLETE_SEALED", "zip_path": str(OFFICIAL), "zip_sha256": sha(OFFICIAL), "zip_bytes": OFFICIAL.stat().st_size, "members": len(zipfile.ZipFile(OFFICIAL).namelist()), "kernel": observed_kernel}
    write_json(ROOT / "output" / "FINAL_PACKAGE_RESULT.json", result)
    print(json.dumps(result, indent=2))


def hashlib_sha256(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()


if __name__ == "__main__": main()
