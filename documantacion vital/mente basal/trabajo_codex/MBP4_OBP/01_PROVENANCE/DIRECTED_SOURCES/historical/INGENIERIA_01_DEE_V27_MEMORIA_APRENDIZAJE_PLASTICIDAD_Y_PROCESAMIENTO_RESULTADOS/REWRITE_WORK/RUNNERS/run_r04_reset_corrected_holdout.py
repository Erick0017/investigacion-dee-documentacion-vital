#!/usr/bin/env python3
"""Corrected fresh holdout: recurrent law and causal canaries only."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from reset_apparatus_v1 import run_reset_case
from rewrite_common import WORK, load_kernel, seal, write_json


def main():
    challenge_path = WORK / "CHALLENGES" / "R04_RESET_CORRECTED_CHALLENGES.json"
    freeze_path = WORK / "FREEZE" / "R04_RESET_CORRECTED_LOCK.json"
    if not challenge_path.exists() or not freeze_path.exists():
        raise RuntimeError("freeze and challenges required")
    challenges = json.loads(challenge_path.read_text(encoding="utf-8"))
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    kernel, runtime = load_kernel(1)
    rows = [run_reset_case(kernel, challenge) for challenge in challenges["challenges"]]
    treatments = [row for row in rows if row["mode"] == "treatment"]
    canaries = [row for row in rows if row["mode"] != "treatment"]
    passed = all(row["all_exact"] for row in treatments) and all(
        (not row["all_exact"]) and row["first_failure_tick"] <= 3 for row in canaries
    )
    out = seal(
        {
            "schema": "dee.v27.ing01.rewrite.reset_corrected_holdout.v1",
            "freeze_content_sha256": freeze["content_sha256"],
            "challenge_content_sha256": challenges["content_sha256"],
            "rows": rows,
            "summary": {
                "passed": passed,
                "treatment_worlds": len(treatments),
                "treatment_exact": sum(row["all_exact"] for row in treatments),
                "fresh_exact_cycles": sum(row["complete_cycles"] for row in treatments),
                "canary_worlds": len(canaries),
                "canaries_triggered": sum(not row["all_exact"] for row in canaries),
                "maximum_treatment_cycles": max(row["complete_cycles"] for row in treatments),
            },
            "explicitly_excluded_prediction": "Full source state bit-exactness is false because clocks obey c(t)=c(0)+t mod 2^64; only semantic-4 raw is invariant.",
            "runtime": runtime,
        }
    )
    write_json(WORK / "HOLDOUT" / "R04_RESET_CORRECTED_HOLDOUT.json", out)
    print(json.dumps({"hash": out["content_sha256"], **out["summary"]}, sort_keys=True))


if __name__ == "__main__":
    main()

