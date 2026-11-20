#!/usr/bin/env python3
"""Execute the preregistered fresh policy-repair holdout."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from core17e_common import ROOT, append_ndjson, audit_kernel, seal, sha256_file, verify_and_load_kernel, write_json
from run_e02_redundant_policy_repair import run_case


MODES = ["treatment", "backup_untrained", "backup_direction_reset", "no_backup", "path_cut", "offpath_cut", "wrong_receiver"]


def main() -> None:
    lock_path = ROOT / "FREEZE" / "C17E03_POLICY_REPAIR_LOCK.json"
    challenge_path = ROOT / "CHALLENGES" / "C17E03_POLICY_REPAIR_CHALLENGE.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    challenge = json.loads(challenge_path.read_text(encoding="utf-8"))
    if challenge["lock_content_sha256"] != lock["content_sha256"]:
        raise RuntimeError("challenge/lock mismatch")
    kernel, runtime = verify_and_load_kernel(1)
    rows = []
    for c in challenge["cases"]:
        for j, mode in enumerate(MODES):
            rows.append(run_case(kernel, c["seed"] + j * 7919, tuple(c["permutation"]), tuple(c["signs"]), mode, c["n"], c["d1"], c["d2"]))
    by_mode = {m: [r for r in rows if r["mode"] == m] for m in MODES}
    counts = {m: sum(bool(r["fresh_function_after_reconstruction"]) for r in rs) for m, rs in by_mode.items()}
    passed = counts == {"treatment": 12, "backup_untrained": 0, "backup_direction_reset": 0, "no_backup": 0, "path_cut": 0, "offpath_cut": 12, "wrong_receiver": 0}
    result = seal({
        "schema": "dee.v27.core17.extension.policy_repair.holdout.v1",
        "claim_id": "C17E-CLAIM-001",
        "lock_sha256": sha256_file(lock_path),
        "challenge_sha256": sha256_file(challenge_path),
        "fresh_worlds": len(challenge["cases"]),
        "executions": len(rows),
        "counts_functional": counts,
        "passed": passed,
        "rows": rows,
        "runtime": runtime,
    })
    write_json(ROOT / "HOLDOUT" / "C17E03_POLICY_REPAIR_HOLDOUT.json", result)
    append_ndjson(ROOT / "RESEARCH_DECISION_LOG.ndjson", {"id": "C17ED004", "decision": "Promote C17E-CLAIM-001" if passed else "Reject C17E-CLAIM-001", "result_hash": result["content_sha256"], "counts": counts})
    append_ndjson(ROOT / "KERNEL_DIALOGUE.ndjson", {"id": "C17EK002", "question": "Does direction-bearing redundant policy reconstruction generalize fresh?", "answer": counts, "pass": passed})
    print({"hash": result["content_sha256"], "passed": passed, "counts": counts})
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
