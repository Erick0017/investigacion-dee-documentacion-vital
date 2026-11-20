#!/usr/bin/env python3
"""Generate untouched operator challenges from OS entropy after source freeze."""
from __future__ import annotations

import json
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core16x_common import ROOT, canonical_hash, read_json, update_state, utc, write_json


def main() -> None:
    lock = read_json(ROOT / "HOLDOUT_LOCKS" / "OCCUPANCY_OPERATOR_LOCK.json")
    if not lock.get("challenge_instances_exist_at_freeze") is False:
        raise RuntimeError("invalid freeze boundary")
    challenges = []
    for index in range(24):
        challenges.append({
            "challenge_id": f"C16X-OP-{index:03d}",
            "seed": secrets.randbits(64),
            "n": (7, 8, 9)[index % 3],
            "density": (0.035, 0.07, 0.12, 0.18)[index % 4],
            "ticks": 3 + (index % 5),
            "include_fusion": index % 2 == 0,
            "clock_shift_multiple": 1 + secrets.randbelow(31),
        })
    payload = {
        "challenge_set_id": "C16X-OPERATOR-FINAL-UNTOUCHED-V1",
        "generated_utc": utc(),
        "entropy_source": "Python secrets backed by OS entropy",
        "lock_id": lock["lock_id"],
        "lock_sha256": lock["lock_sha256"],
        "challenges": challenges,
    }
    payload["challenge_sha256"] = canonical_hash({k: v for k, v in payload.items() if k != "challenge_sha256"})
    write_json(ROOT / "FINAL_HOLDOUTS" / "OPERATOR_CHALLENGES.json", payload)
    update_state(status="OPERATOR_CHALLENGES_GENERATED", current_phase="RUN_OPERATOR_FINAL_HOLDOUT", operator_challenge_sha256=payload["challenge_sha256"])
    print(json.dumps({"challenges": len(challenges), "challenge_sha256": payload["challenge_sha256"], "generated_utc": payload["generated_utc"]}, indent=2))


if __name__ == "__main__":
    main()

