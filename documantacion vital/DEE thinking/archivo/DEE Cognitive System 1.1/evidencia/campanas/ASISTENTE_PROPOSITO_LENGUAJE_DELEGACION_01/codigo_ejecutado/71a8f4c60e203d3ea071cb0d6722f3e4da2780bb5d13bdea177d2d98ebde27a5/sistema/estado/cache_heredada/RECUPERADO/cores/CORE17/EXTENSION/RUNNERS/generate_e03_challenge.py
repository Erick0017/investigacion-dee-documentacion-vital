#!/usr/bin/env python3
"""Generate the frozen policy-repair challenge after the lock exists."""
from __future__ import annotations

import json
import secrets
import sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from core17e_common import ROOT, seal, sha256_file, write_json


def main() -> None:
    lock_path = ROOT / "FREEZE" / "C17E03_POLICY_REPAIR_LOCK.json"
    if not lock_path.exists():
        raise RuntimeError("freeze lock missing")
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    entropy = secrets.token_bytes(32)
    root_seed = int.from_bytes(entropy, "big")
    rng = np.random.default_rng(root_seed)
    cases = []
    for i in range(12):
        perm = tuple(int(x) for x in rng.permutation(3))
        signs = tuple(int(x) for x in rng.choice(np.array([-1, 1], dtype=np.int8), size=3))
        cases.append({
            "case_id": f"C17E03-{i:02d}",
            "seed": int(rng.integers(2_000_000, 2_147_000_000)),
            "n": int(rng.choice(np.array([31, 37, 41]))),
            "d1": int(rng.integers(4, 8)),
            "d2": int(rng.integers(6, 11)),
            "permutation": list(perm),
            "signs": list(signs),
        })
    challenge = seal({
        "schema": "dee.v27.core17.extension.policy_repair.challenge.v1",
        "lock_content_sha256": lock["content_sha256"],
        "lock_file_sha256": sha256_file(lock_path),
        "os_entropy_hex": entropy.hex(),
        "root_seed": root_seed,
        "cases": cases,
    })
    write_json(ROOT / "CHALLENGES" / "C17E03_POLICY_REPAIR_CHALLENGE.json", challenge)
    print(challenge["content_sha256"])


if __name__ == "__main__":
    main()
