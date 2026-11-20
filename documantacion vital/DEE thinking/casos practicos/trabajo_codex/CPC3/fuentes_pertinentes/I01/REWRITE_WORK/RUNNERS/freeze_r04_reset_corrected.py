#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from rewrite_common import WORK, seal, sha256_file, write_json


def main():
    files = [HERE / "reset_apparatus_v1.py", HERE / "run_r04_reset_corrected_holdout.py"]
    out = seal(
        {
            "schema": "dee.v27.ing01.rewrite.reset_corrected_lock.v1",
            "model_revision_from_R03": "Semantic-4 raw is invariant (CORE01 E8), but every clock advances rigidly (CORE01 E1). The false full-state-invariance conjunct is removed, not hidden.",
            "claim": "Four persistent semantic-4 raw sources replenish writer carriers that recycle one semantic-1 policy carrier through an exact two-tick directional cycle.",
            "prediction": "Every treatment half-cycle has the frozen alternating direction for the entire horizon; missing, finite, and wrong-writer canaries fail by tick 3.",
            "metric": "zero direction mismatches over all requested treatment cycles; causal canary failure tick <=3",
            "falsifier": "any treatment mismatch or any canary surviving exact beyond tick 3",
            "scope": "Prepared L2 recurrent execution. No claim of feedback learning, damage repair, self-selected reset, or semantic-4 clock invariance.",
            "frozen_files": [{"path": str(p.relative_to(WORK)), "sha256": sha256_file(p)} for p in files],
            "fresh_dimensions": ["N", "position", "signed-permuted frame", "horizon", "canary mode"],
        }
    )
    write_json(WORK / "FREEZE" / "R04_RESET_CORRECTED_LOCK.json", out)
    print(out["content_sha256"])


if __name__ == "__main__":
    main()

