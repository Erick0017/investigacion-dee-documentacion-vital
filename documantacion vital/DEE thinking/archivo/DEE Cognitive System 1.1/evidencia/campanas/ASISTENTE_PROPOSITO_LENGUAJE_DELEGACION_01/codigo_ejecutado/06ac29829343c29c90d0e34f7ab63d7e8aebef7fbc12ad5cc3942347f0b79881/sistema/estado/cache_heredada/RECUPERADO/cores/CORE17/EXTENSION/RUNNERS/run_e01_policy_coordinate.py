#!/usr/bin/env python3
"""New discriminating panel: isolate the coordinate carrying learned policy."""
from __future__ import annotations

import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from core17e_common import PACKAGE_ROOT, ROOT, append_ndjson, audit_kernel, seal, utc, verify_and_load_kernel, write_json

BASE = PACKAGE_ROOT / "RUNNERS" / "VENDORED_CORE16" / "BASELINE_RUNNERS"
sys.path.insert(0, str(BASE))
from core10_apparatus import run_learned_policy_transfer  # noqa: E402


FRAMES = [
    ((0, 1, 2), (1, 1, 1)),
    ((1, 2, 0), (1, -1, 1)),
    ((2, 0, 1), (-1, 1, 1)),
    ((0, 2, 1), (-1, -1, 1)),
]


def main() -> None:
    audit_kernel("CORE17E_POLICY_COORDINATE_BEFORE")
    kernel, runtime = verify_and_load_kernel(1)
    modes = ("trained", "untrained", "memory_ablation", "history_reset", "direction_ablation", "sreg_nuisance")
    rows = []
    for i in range(8):
        permutation, signs = FRAMES[i % len(FRAMES)]
        common = {
            "seed": 171800 + i * 173,
            "n": (23, 27)[i % 2],
            "distance": (4, 6, 8, 5)[i % 4],
            "permutation": permutation,
            "signs": signs,
        }
        cases = {mode: run_learned_policy_transfer(kernel, mode=mode, **common) for mode in modes}
        trained_memory = cases["trained"]["memory_after_experience"]
        untrained_memory = cases["untrained"]["memory_after_experience"]
        coordinate_delta = {
            key: (None if trained_memory is None or untrained_memory is None else trained_memory[key] != untrained_memory[key])
            for key in ("state", "sreg", "direction", "semantic")
        }
        rows.append(
            {
                "case": i,
                "setup": common,
                "trained_memory": trained_memory,
                "untrained_memory": untrained_memory,
                "trained_vs_untrained_coordinate_delta": coordinate_delta,
                "functional": {mode: cases[mode]["functional_policy_reinstantiated"] for mode in modes},
                "source_depleted": {mode: cases[mode]["source_depleted_after_launch"] for mode in modes},
                "arrival": {mode: cases[mode]["arrival_record"] for mode in modes},
                "query": {mode: cases[mode]["query_record"] for mode in modes},
            }
        )
    summary = {
        "cases": len(rows),
        "trained_all": all(row["functional"]["trained"] for row in rows),
        "untrained_none": all(not row["functional"]["untrained"] for row in rows),
        "memory_ablation_none": all(not row["functional"]["memory_ablation"] for row in rows),
        "history_reset_none": all(not row["functional"]["history_reset"] for row in rows),
        "direction_ablation_none": all(not row["functional"]["direction_ablation"] for row in rows),
        "sreg_nuisance_all": all(row["functional"]["sreg_nuisance"] for row in rows),
        "only_direction_differs_trained_untrained": all(
            row["trained_vs_untrained_coordinate_delta"] == {"state": False, "sreg": True, "direction": True, "semantic": False}
            or row["trained_vs_untrained_coordinate_delta"] == {"state": False, "sreg": False, "direction": True, "semantic": False}
            for row in rows
        ),
    }
    summary["direction_necessary_sreg_not_specific"] = (
        summary["trained_all"] and summary["history_reset_none"] and summary["direction_ablation_none"] and summary["sreg_nuisance_all"]
    )
    result = seal({"schema": "dee.v27.core17.extension.policy_coordinate.v1", "created_utc": utc(), "runtime": runtime, "rows": rows, "summary": summary})
    write_json(ROOT / "DISCOVERY" / "C17E01_POLICY_COORDINATE.json", result)
    append_ndjson(ROOT / "QUESTION_TREE.ndjson", {"question_id": "C17EQ001", "result_hash": result["content_sha256"], "result": summary, "status": "ANSWERED", "child_question": "Can direction-bearing learned memory be redundantly reconstructed after receiver damage?"})
    append_ndjson(ROOT / "QUESTION_TREE.ndjson", {"question_id": "C17EQ002", "parent": "C17EQ001", "parent_result_hash": result["content_sha256"], "question": "Can a native redundant carrier restore the policy-bearing direction after damage?", "competing": ["policy coordinate recoverable by causal redundancy", "canonical regeneration only", "external rewrite artifact"], "next_experiment": "two-memory source-supported repair with path and policy controls", "status": "OPEN"})
    append_ndjson(ROOT / "KERNEL_DIALOGUE.ndjson", {"question_id": "C17EQ001", "kernel_response": summary, "interpretation": "direction/history coordinate is necessary; s_reg magnitude is nuisance within the tested transfer grammar", "next": "construct policy-bearing redundancy"})
    audit_kernel("CORE17E_POLICY_COORDINATE_AFTER")
    print(json.dumps({"hash": result["content_sha256"], **summary}, indent=2))


if __name__ == "__main__":
    main()
