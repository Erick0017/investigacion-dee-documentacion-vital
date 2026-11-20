#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from feedback_apparatus_v1 import run_feedback_case
from rewrite_common import WORK, load_kernel, seal, write_json


def main():
    freeze_path = WORK / "FREEZE" / "R14_FEEDBACK_HOLDOUT_LOCK.json"
    challenge_path = WORK / "CHALLENGES" / "R14_FEEDBACK_HOLDOUT_CHALLENGES.json"
    if not freeze_path.exists() or not challenge_path.exists():
        raise RuntimeError("freeze and challenges required")
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    challenges = json.loads(challenge_path.read_text(encoding="utf-8"))
    kernel, runtime = load_kernel(1)
    rows = [run_feedback_case(kernel, challenge) for challenge in challenges["challenges"]]
    treatments = [row for row in rows if row["mode"] == "treatment"]
    canaries = [row for row in rows if row["mode"] != "treatment"]
    passed = all(row["end_to_end_exact"] and row["action0_exact"] and row["policy_exact"] for row in treatments) and all(row["decoded"] != 1 for row in canaries)
    out = seal(
        {
            "schema": "dee.v27.ing01.rewrite.feedback_holdout.v1",
            "freeze_content_sha256": freeze["content_sha256"],
            "challenge_content_sha256": challenges["content_sha256"],
            "rows": rows,
            "summary": {
                "passed": passed,
                "treatment_worlds": len(treatments),
                "treatment_exact": sum(row["end_to_end_exact"] for row in treatments),
                "canary_worlds": len(canaries),
                "canaries_triggered": sum(row["decoded"] != 1 for row in canaries),
            },
            "runtime": runtime,
        }
    )
    write_json(WORK / "HOLDOUT" / "R14_FEEDBACK_HOLDOUT.json", out)
    print(json.dumps({"hash": out["content_sha256"], **out["summary"]}, sort_keys=True))


if __name__ == "__main__":
    main()

