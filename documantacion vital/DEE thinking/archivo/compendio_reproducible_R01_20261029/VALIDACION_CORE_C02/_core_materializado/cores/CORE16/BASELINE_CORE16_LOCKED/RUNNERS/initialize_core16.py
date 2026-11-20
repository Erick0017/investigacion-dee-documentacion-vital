#!/usr/bin/env python3
"""Initialize CORE16 from the sealed CORE15 parent without modifying it."""
from __future__ import annotations

import json
import shutil
import sys
import zipfile
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core16_common import (
    ROOT, TESTS, PARENT_ZIP, PARENT_SHA, append_ndjson, audit_kernel,
    read_json, sha, utc, update_state, write_json, write_text,
)


PARENT_WORK = TESTS / "DEE_V27_CORE15_EXPANDED_MULTIPHYSICS_WORK"
SOURCE_RUNNERS = PARENT_WORK / "NEW_RUNNERS"
RUNNER_NAMES = (
    "native_core.py", "core08_common.py", "core10_common.py", "core10_apparatus.py",
    "core12_common.py", "core12_apparatus.py", "run_c6h01_associative_plasticity_holdout.py",
    "run_c6h08_dissipative_ensemble_holdout.py", "run_c8h02_repeated_scaffold_regeneration.py",
)


def safe_extract_parent() -> dict:
    target = ROOT / "PARENT_CORE15_LOCKED"
    extracted = 0
    with zipfile.ZipFile(PARENT_ZIP) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f"parent ZIP CRC failure: {bad}")
        names = archive.namelist()
        for name in names:
            part = PurePosixPath(name)
            if part.is_absolute() or ".." in part.parts:
                raise RuntimeError(f"unsafe parent member: {name}")
        # The research copy is local and read-only by protocol. It is excluded from CORE16 packaging.
        archive.extractall(target)
        extracted = len(names)
    hashes = target / "HASHES.sha256"
    checked = 0
    mismatches = []
    if hashes.exists():
        for line in hashes.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if not line:
                continue
            expected, rel = line.split(None, 1)
            rel = rel.strip().lstrip("*").replace("/", "\\")
            candidate = target / rel
            if candidate.resolve() == hashes.resolve():
                continue
            checked += 1
            if not candidate.is_file() or sha(candidate) != expected.lower():
                mismatches.append(rel)
    return {
        "zip_crc_pass": True,
        "members": extracted,
        "internal_hash_entries_checked": checked,
        "internal_hash_mismatches": mismatches,
        "internal_hashes_pass": not mismatches,
    }


def main() -> None:
    observed_parent = sha(PARENT_ZIP)
    if observed_parent != PARENT_SHA:
        raise RuntimeError(f"CORE15 parent mismatch: {observed_parent}")
    kernel = audit_kernel("CORE16_PARENT_PREFLIGHT")
    validation = safe_extract_parent()
    if not validation["internal_hashes_pass"]:
        raise RuntimeError(f"CORE15 internal hash mismatches: {validation['internal_hash_mismatches'][:5]}")

    runner_hashes = {}
    for name in RUNNER_NAMES:
        source = SOURCE_RUNNERS / name
        destination = ROOT / "RUNNERS" / name
        if not source.is_file():
            raise RuntimeError(f"missing inherited runner: {source}")
        shutil.copy2(source, destination)
        runner_hashes[name] = {"source_sha256": sha(source), "copied_sha256": sha(destination)}

    parent_state = read_json(ROOT / "PARENT_CORE15_LOCKED" / "STATE.json")
    parent_manifest = read_json(ROOT / "PARENT_CORE15_LOCKED" / "MANIFEST.json")
    parent_claims = read_json(ROOT / "PARENT_CORE15_LOCKED" / "CLAIM_LEDGER.json")
    chain = {
        "core": "CORE16",
        "parent": "CORE15_EXPANDED",
        "parent_zip": PARENT_ZIP.name,
        "parent_zip_sha256": observed_parent,
        "parent_state": parent_state.get("status"),
        "parent_manifest_status": parent_manifest.get("status", parent_manifest.get("state")),
        "parent_claim_count": len(parent_claims.get("claims", [])),
        "validation": validation,
        "kernel_preflight": kernel,
        "parent_files_modified": False,
        "parent_embedded_in_final_zip": False,
        "runner_provenance": runner_hashes,
        "created_utc": utc(),
    }
    write_json(ROOT / "PARENT_CHAIN.json", chain)

    boundaries = {
        "campaign": "CORE16_MULTISCALE_REALITY_LADDER",
        "hypothesis": "H_DEE_CONDITIONAL",
        "discovery_may_adapt": True,
        "confirmation_may_adapt": False,
        "partitions": ["DISCOVERY", "MODEL_LEVEL_SELECTION", "FINAL_UNTOUCHED_HOLDOUT"],
        "promotion_requires": [
            "frozen_apparatus", "frozen_observer", "frozen_level_mapping", "frozen_metric",
            "frozen_threshold", "frozen_prediction", "fresh_world", "causal_canary_when_meaningful",
        ],
        "forbidden": [
            "kernel_modification", "parent_modification", "holdout_repair", "postselection",
            "Born_rule_assumption", "quantum_label_from_resemblance", "external_identity_from_internal_law",
        ],
    }
    write_json(ROOT / "SCIENTIFIC_BOUNDARIES.json", boundaries)

    candidates = {
        "status": "DISCOVERY_CANDIDATES_NOT_LEVELS",
        "strategies": [
            {"id": "R_FULL", "kind": "full_state_reference", "features": ["raw", "clock"]},
            {"id": "R_BULK", "kind": "manual_causal", "features": ["support", "sreg_total", "direction_sum", "semantic_counts"]},
            {"id": "R_FIBER", "kind": "causal_equivalence", "features": ["destination_fibers", "destination_multiplicity", "reducer_inputs"]},
            {"id": "R_EVENT", "kind": "event_coarse_graining", "features": ["arrival_tick", "direction", "semantic", "sreg", "relative_history"]},
            {"id": "R_RELATIONAL_OBJECT", "kind": "relational_graph", "features": ["relative_shape", "labeled_payload_assignment", "functional_response"]},
            {"id": "R_RESPONSE", "kind": "interaction_response_equivalence", "features": ["standardized_intervention_responses"]},
            {"id": "R_HISTORY_PHASE", "kind": "temporal_history_aware", "features": ["phase", "ordered_history", "clock_residual"]},
            {"id": "R_ENSEMBLE", "kind": "predictive_state_clustering", "features": ["occupancy_fraction", "direction_distribution", "destination_collision_rate"]},
            {"id": "R_TOPOLOGY", "kind": "topological_summary", "features": ["guard_topology", "interfaces", "accessibility"]},
            {"id": "R_HIERARCHICAL", "kind": "hierarchical_combination", "features": ["task_relative_small_family"]},
        ],
        "selection_criteria": ["compression", "predictive_sufficiency", "causal_closure", "fresh_generalization", "nontriviality"],
    }
    write_json(ROOT / "LEVEL_DISCOVERY_REGISTRY.json", candidates)

    roots = [
        ("C16Q001", "Which reduced descriptions form nontrivial predictive levels rather than labels?"),
        ("C16Q002", "Can information hidden by a coarse observer later become operationally visible?"),
        ("C16Q003", "Does limited access induce useful probability and classical concentration?"),
        ("C16Q004", "At which valid level do phase, measurement and order effects remain predictive?"),
        ("C16Q005", "What does a loophole-audited Bell apparatus show at each supported level?"),
        ("C16Q006", "Which extraordinary capabilities compose from confirmed native mechanisms?"),
        ("C16Q007", "Does any reproducible cross-scale law resist the existing mechanism taxonomy?"),
    ]
    question_path = ROOT / "QUESTION_TREE.ndjson"
    write_text(question_path, "")
    for qid, question in roots:
        append_ndjson(question_path, {
            "question_id": qid,
            "parent_question": None,
            "parent_result_hash": None,
            "stage": "INITIAL_ROOT",
            "question": question,
            "candidate_explanations": ["task_relative_closure", "missing_hidden_state", "apparatus_specific_effect", "bounded_null"],
            "expected_information_gain": "high",
        })
    write_text(ROOT / "KERNEL_DIALOGUE.ndjson", "")
    write_text(ROOT / "RESEARCH_DECISION_LOG.ndjson", "")
    write_json(ROOT / "HOLDOUT_REGISTRY.json", {"partitions": {}, "final_holdout_generated": False})
    write_json(ROOT / "CANARY_REGISTRY.json", {"canaries": []})
    write_json(ROOT / "CLAIM_LEDGER.json", {"core": "CORE16", "claims": [], "status": "DISCOVERY_OPEN"})
    update_state(
        status="PARENT_AUDITED_DISCOVERY_READY",
        phase="PHASE_A",
        parent_sha256=observed_parent,
        completed_checkpoints=["PARENT_AUDIT", "INITIAL_REPRESENTATION_REGISTRY", "INITIAL_QUESTION_ROOTS"],
        final_holdout_generated=False,
    )
    write_json(ROOT / "CHECKPOINTS" / "CP00_PARENT_AUDIT.json", {
        "status": "PASS", "parent_sha256": observed_parent, "kernel": kernel, "validation": validation, "utc": utc(),
    })
    print(json.dumps({"status": "PARENT_AUDITED_DISCOVERY_READY", "parent_sha256": observed_parent, "kernel": kernel["pass"], "questions": len(roots)}, indent=2))


if __name__ == "__main__":
    main()
