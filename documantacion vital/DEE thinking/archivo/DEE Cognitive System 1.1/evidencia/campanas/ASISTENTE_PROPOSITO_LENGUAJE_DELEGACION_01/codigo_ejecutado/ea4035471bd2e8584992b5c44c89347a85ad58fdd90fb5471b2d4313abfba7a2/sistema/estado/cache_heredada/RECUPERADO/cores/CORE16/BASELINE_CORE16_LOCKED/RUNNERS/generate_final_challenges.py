#!/usr/bin/env python3
"""Generate CORE16 final untouched challenges only after verified source freeze."""
from __future__ import annotations

import hashlib
import json
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core16_common import ROOT, read_json, sha, utc, update_state, write_json


def derived_seed(entropy: bytes, label: str, index: int) -> int:
    digest = hashlib.sha256(entropy + label.encode("utf-8") + index.to_bytes(4, "big")).digest()
    return int.from_bytes(digest[:8], "big") & ((1 << 63) - 1)


def main():
    target = ROOT / "FINAL_HOLDOUTS" / "FINAL_CHALLENGE_MANIFEST.json"
    if target.exists():
        print(target.read_text(encoding="utf-8")); return
    freeze = read_json(ROOT / "SOURCE_FREEZE.json")
    mismatches = []
    for item in freeze["files"]:
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]:
            mismatches.append(item["path"])
    if mismatches:
        raise RuntimeError(f"source freeze mismatch before challenge generation: {mismatches}")
    entropy = secrets.token_bytes(64)
    labels_counts = {
        "fiber": 128, "resurrection": 64, "probability": 256,
        "classical": 4, "order": 12, "phase": 6,
        "transfer": 4, "amplification": 6, "bell_order": 512,
    }
    seeds = {label: [derived_seed(entropy, label, i) for i in range(count)] for label, count in labels_counts.items()}
    # Balanced Bell cells preserve measurement independence while OS entropy fixes only their fresh order.
    bell_cells = [(li, a, b) for _ in range(16) for li in range(8) for a in range(2) for b in range(2)]
    import random
    random.Random(seeds["bell_order"][0]).shuffle(bell_cells)
    manifest = {
        "schema": "dee.v27.core16.final_challenges.v1",
        "generated_after_source_freeze": True,
        "source_freeze_sha256": sha(ROOT / "SOURCE_FREEZE.json"),
        "os_entropy_sha256": hashlib.sha256(entropy).hexdigest(),
        "raw_entropy_not_retained": True,
        "created_utc": utc(),
        "seeds": {k: v for k, v in seeds.items() if k != "bell_order"},
        "bell_balanced_random_order": [{"lambda_index": li, "a": a, "b": b} for li, a, b in bell_cells],
        "untouched_at_generation": True,
    }
    write_json(target, manifest)
    write_json(ROOT / "CHECKPOINTS" / "CP05_FINAL_CHALLENGES_GENERATED.json", {"status": "COMPLETE", "manifest_sha256": sha(target), "source_freeze_sha256": manifest["source_freeze_sha256"], "utc": utc()})
    update_state(status="FINAL_CHALLENGES_GENERATED_UNTOUCHED", final_holdout_generated=True, challenge_manifest_sha256=sha(target))
    print(json.dumps({"status": "GENERATED", "manifest_sha256": sha(target), "counts": labels_counts}, indent=2))


if __name__ == "__main__":
    main()
