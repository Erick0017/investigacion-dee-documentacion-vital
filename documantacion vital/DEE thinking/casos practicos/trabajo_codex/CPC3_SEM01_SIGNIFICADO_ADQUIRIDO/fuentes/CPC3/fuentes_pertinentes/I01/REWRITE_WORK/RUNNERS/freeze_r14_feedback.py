#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from rewrite_common import WORK, seal, sha256_file, write_json


def main():
    files = [HERE / "feedback_apparatus_v1.py", HERE / "run_r14_feedback_holdout.py"]
    out = seal(
        {
            "schema": "dee.v27.ing01.rewrite.feedback_holdout_lock.v1",
            "claim": "Within one continuing preloaded world, a native action is causally required for an environmental reducer event that writes policy B; unbiased dual probes then produce a different later action. Python makes no intervention after t0.",
            "prediction": "All treatments produce exact action0, policy A/B according to consequence, and decoded later action; no-action, no-penalty, and wrong-consequence canaries fail the intended bit1 output.",
            "metric": "exact directions at action, policy, and both symmetric output probes",
            "falsifier": "any treatment mismatch or any canary reproducing bit1",
            "autonomy_adjudication": "L3_FINITE_PREPARED",
            "scope": "Finite three-tick causal adaptation. Inputs, environmental rule, and both probes are initialized at t0; resources are consumed. L4 persistent adaptation is not claimed.",
            "frozen_files": [{"path": str(p.relative_to(WORK)), "sha256": sha256_file(p)} for p in files],
            "fresh_dimensions": ["N", "position", "signed-permuted frame", "policy bit", "canary mode"],
        }
    )
    write_json(WORK / "FREEZE" / "R14_FEEDBACK_HOLDOUT_LOCK.json", out)
    print(out["content_sha256"])


if __name__ == "__main__":
    main()

