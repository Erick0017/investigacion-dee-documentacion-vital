#!/usr/bin/env python3
"""Freeze CORE16 claims, analysis sources and thresholds before final challenges."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core16_common import ROOT, audit_kernel, sha, utc, update_state, write_json


def main():
    target = ROOT / "SOURCE_FREEZE.json"
    if target.exists(): print(target.read_text(encoding="utf-8")); return
    audit_kernel("CORE16_SOURCE_FREEZE")
    contracts = {
        "schema": "dee.v27.core16.frozen_claim_contracts.v1",
        "frozen_before_final_challenges": True,
        "claims": [
            {"claim_id": "C16C001", "claim": "Within sparse semantic1 worlds with destinations empty at t0, next support equals unique destination count.", "level": "ROUTED_CAUSAL_STATE", "metric": "exact equality", "canary": "occupied destination must be detected out of scope"},
            {"claim_id": "C16C002", "claim": "Payload-to-relative-position assignment hidden by an unlabeled object shadow becomes visible under matched lane-selective collision.", "level": "RELATIONAL_RESPONSE_STATE", "metric": "64/64 exact payload predictions and pair divergence", "canary": "unlabeled multiset cannot predict lane response"},
            {"claim_id": "C16C003", "claim": "Compatible microstates induce a nondegenerate bulk outcome distribution while destination fibers remain exact.", "level": "STATISTICAL_ENSEMBLE", "metric": ">=3 outcomes, entropy>=0.5 bit, fiber error=0", "canary": "fiber conditioning removes uncertainty"},
            {"claim_id": "C16C004", "claim": "At fixed density coarse one-step response fluctuations concentrate with component count.", "level": "STATISTICAL_ENSEMBLE", "metric": "alpha in [-0.8,-0.2] and CV ratio<=0.65", "canary": "none; fresh scale transform"},
            {"claim_id": "C16C005", "claim": "Sequential reducer interventions are order-sensitive under the frozen directional operator.", "level": "RELATIONAL_RESPONSE_STATE", "metric": "all transformed AB!=BA", "canary": "identical intervention sequences equal"},
            {"claim_id": "C16C006", "claim": "Event count alone is insufficient for phase/path composition; payload readout distinguishes coherent and shifted apparatuses.", "level": "EVENT_RESPONSE_STATE", "metric": "equal counts and unequal payload sequences", "canary": "closed source has zero events"},
            {"claim_id": "C16C007", "claim": "Learned policy is destructively and functionally reconstructed through an explicit corridor and prepared receiver.", "level": "FUNCTIONAL_ORGANIZATION", "metric": "trained/offpath positives; all causal breaks negative; corridor and depletion visible", "canary": "remove training, relay, corridor, receiver or memory"},
            {"claim_id": "C16C008", "claim": "One semantic4 guard cell at the k5/k6 threshold amplifies into a train-level transmission/blocking difference.", "level": "MACROSCOPIC_RESPONSE", "metric": "k5 events>0 and k6 events=0", "canary": "k5 transmitting arm"},
            {"claim_id": "C16C009", "claim": "The tested Bell apparatus remains within CHSH<=2 under independent external and DEE-local-generated settings.", "level": "LOCAL_COLLISION_OUTCOME", "metric": "balanced complete trials; CHSH<=2; generator records valid", "canary": "measurement-dependent setting schedule must be flagged"},
        ],
        "explicit_nonclaims": [
            "no Born rule", "no quantum interference beyond capped reducer", "no Kochen-Specker contextuality", "no quantum Bell violation",
            "no universal multistep fiber closure", "no external DEE identification", "no mediator-free teleportation",
        ],
        "created_utc": utc(),
    }
    write_json(ROOT / "FROZEN_CLAIM_CONTRACTS.json", contracts)
    sources = [
        "RUNNERS/core16_common.py", "RUNNERS/native_core.py", "RUNNERS/core12_common.py", "RUNNERS/core12_apparatus.py",
        "RUNNERS/core10_common.py", "RUNNERS/core10_apparatus.py", "RUNNERS/run_discovery_roots.py",
        "RUNNERS/run_adaptive_children.py", "RUNNERS/run_adaptive_grandchildren.py",
        "RUNNERS/generate_final_challenges.py", "RUNNERS/run_final_holdouts.py", "FROZEN_CLAIM_CONTRACTS.json",
    ]
    files = [{"path": rel, "sha256": sha(ROOT / rel)} for rel in sources]
    freeze = {"schema": "dee.v27.core16.source_freeze.v1", "frozen_utc": utc(), "files": files, "file_count": len(files), "final_challenges_existed_at_freeze": (ROOT / "FINAL_HOLDOUTS" / "FINAL_CHALLENGE_MANIFEST.json").exists(), "pass": True}
    if freeze["final_challenges_existed_at_freeze"]:
        raise RuntimeError("final challenges existed before source freeze")
    write_json(target, freeze)
    write_json(ROOT / "CHECKPOINTS" / "CP04_SOURCE_FREEZE.json", {"status": "PASS", "source_freeze_sha256": sha(target), "files": len(files), "utc": utc()})
    update_state(status="SOURCE_FROZEN_READY_FOR_OS_CHALLENGES", source_freeze_sha256=sha(target), final_holdout_generated=False)
    print(json.dumps({"status": "FROZEN", "source_freeze_sha256": sha(target), "files": len(files)}, indent=2))


if __name__ == "__main__": main()
