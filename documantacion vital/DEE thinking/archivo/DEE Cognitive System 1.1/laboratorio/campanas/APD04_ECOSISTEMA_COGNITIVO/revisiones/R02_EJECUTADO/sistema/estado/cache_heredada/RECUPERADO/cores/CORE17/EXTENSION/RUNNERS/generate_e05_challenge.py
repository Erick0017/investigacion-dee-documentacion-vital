#!/usr/bin/env python3
"""Post-freeze OS-entropy challenge for R0_FACTOR_52."""
from __future__ import annotations
import json, secrets, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from core17e_common import ROOT, seal, sha256_file, write_json


def main() -> None:
    lock_path = ROOT / "FREEZE" / "C17E05_R0_FACTOR_LOCK.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    entropy = secrets.token_bytes(32); root_seed = int.from_bytes(entropy, "big"); rng = np.random.default_rng(root_seed)
    cases = []
    for i in range(10):
        cases.append({"case_id": f"C17E05-{i:02d}", "seed": int(rng.integers(20_000_000, 2_000_000_000)), "n": int(rng.choice(np.array([6, 8, 10, 12]))), "density": float(rng.uniform(0.025, 0.22)), "ticks": int(rng.integers(28, 57))})
    challenge = seal({"schema": "dee.v27.core17.extension.r0_factor.challenge.v1", "lock_content_sha256": lock["content_sha256"], "lock_file_sha256": sha256_file(lock_path), "os_entropy_hex": entropy.hex(), "root_seed": root_seed, "cases": cases})
    write_json(ROOT / "CHALLENGES" / "C17E05_R0_FACTOR_CHALLENGE.json", challenge)
    print(challenge["content_sha256"])


if __name__ == "__main__": main()
