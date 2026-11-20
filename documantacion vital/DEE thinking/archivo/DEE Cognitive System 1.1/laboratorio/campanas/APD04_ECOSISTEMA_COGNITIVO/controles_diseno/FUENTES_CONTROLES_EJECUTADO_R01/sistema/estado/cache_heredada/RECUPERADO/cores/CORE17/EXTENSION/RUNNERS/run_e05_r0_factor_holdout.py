#!/usr/bin/env python3
"""Execute final R0_FACTOR_52 worlds and causal representation canaries."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from core17e_common import ROOT, append_ndjson, seal, sha256_file, verify_and_load_kernel, write_json
from run_e04_r0_compression_discovery import run_pair, reduce_state


def canaries() -> dict:
    raw = np.zeros((3, 3, 3), dtype=np.uint64); clock = np.zeros_like(raw)
    # Ordinary direction is an explicitly retained coordinate.
    raw[1,1,1] = np.uint64(1 | (9 << 32) | (1 << 48) | (1 << 60))
    rr, rc = reduce_state(raw, clock)
    zero_dir = rr.copy(); zero_dir[1,1,1] &= np.uint64(~(0xFFF << 48) & ((1 << 64) - 1))
    # Semantic-4 magnitude is not collapsed.
    raw4 = np.zeros_like(raw); raw4[1,1,1] = np.uint64(123456 | (4 << 60))
    r4, c4 = reduce_state(raw4, clock)
    collapsed4 = r4.copy(); collapsed4[1,1,1] = np.uint64((int(collapsed4[1,1,1]) & ~0xFFFFFFFF) | 1)
    return {"direction_ablation_detected": bool(np.any(rr != zero_dir)), "semantic4_collapse_detected": bool(np.any(r4 != collapsed4)), "passed": bool(np.any(rr != zero_dir) and np.any(r4 != collapsed4))}


def main() -> None:
    lock_path = ROOT / "FREEZE" / "C17E05_R0_FACTOR_LOCK.json"; challenge_path = ROOT / "CHALLENGES" / "C17E05_R0_FACTOR_CHALLENGE.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8")); challenge = json.loads(challenge_path.read_text(encoding="utf-8"))
    if lock["content_sha256"] != challenge["lock_content_sha256"]: raise RuntimeError("lock mismatch")
    kernel, runtime = verify_and_load_kernel(1)
    rows = [run_pair(kernel, c["seed"], c["n"], c["density"], c["ticks"]) for c in challenge["cases"]]
    cans = canaries(); passed = all(r["passed"] for r in rows) and cans["passed"]
    result = seal({"schema": "dee.v27.core17.extension.r0_factor.holdout.v1", "claim_id": "C17E-CLAIM-002", "lock_sha256": sha256_file(lock_path), "challenge_sha256": sha256_file(challenge_path), "worlds": len(rows), "ticks_compared": sum(r["ticks_compared"] for r in rows), "raw_mismatches": sum(x["mismatch_raw"] for r in rows for x in r["trace"]), "clock_mismatches": sum(x["mismatch_clock"] for r in rows for x in r["trace"]), "canaries": cans, "passed": passed, "rows": rows, "runtime": runtime})
    write_json(ROOT / "HOLDOUT" / "C17E05_R0_FACTOR_HOLDOUT.json", result)
    append_ndjson(ROOT / "RESEARCH_DECISION_LOG.ndjson", {"id": "C17ED006", "decision": "Promote C17E-CLAIM-002" if passed else "Reject C17E-CLAIM-002", "result_hash": result["content_sha256"], "worlds": len(rows), "ticks": result["ticks_compared"]})
    print({k: result[k] for k in ("content_sha256", "worlds", "ticks_compared", "raw_mismatches", "clock_mismatches", "canaries", "passed")})
    if not passed: raise SystemExit(2)


if __name__ == "__main__": main()
