"""Finish the ORIGINAL frozen inverse plan; absence guards remain negative data.

The first controller stopped on an absent-segment ValueError. It completed
PLUS_FULL/MINUS_FULL; those trajectories are NOT reexecuted here.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common import put, sha


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--child", action="store_true")
    args = parser.parse_args()
    out = args.output.resolve()
    original = json.loads((out / "INVERSE_CONFIG.json").read_text(encoding="utf-8"))
    continuation_path = out / "INSTRUMENTAL_COMPLETION_CONFIG.json"
    if not args.child:
        if continuation_path.exists(): raise FileExistsError(continuation_path)
        continuation = {"reason": "Original controller stopped on missing actual retained segment. Preserve original failed attempt, never fabricate cut, never rerun measured full trajectories.",
                        "original_config_sha256": sha(out / "INVERSE_CONFIG.json"),
                        "completion_source_sha256": sha(__file__), "remaining_plan_unchanged": True,
                        "new_native_future_trajectories_at_most": 1, "passive_guard_reconstruction": ["PLUS_MEMORY_CUT_W1", "MINUS_MEMORY_CUT_W1"]}
        put(continuation_path, continuation)
        from supervise import run
        row = run(ROOT, "inverse_instrumental_completion", [sys.executable, "-I", "-B", str(Path(__file__).resolve()), "--output", str(out), "--child"], 180)
        assert row["exit_code"] == 0
        return
    continuation = json.loads(continuation_path.read_text(encoding="utf-8"))
    assert sha(__file__) == continuation["completion_source_sha256"]
    for name, expected in original["sources"].items():
        assert sha(ROOT / name) == expected
    import dee_thinking as d
    from src import channel
    from src.inverse_language import inverse
    from src.phase_language import KEY
    parent = ROOT / original["parent"]
    assert sha(parent) == original["parent_sha256"]
    rows = []
    for case in original["cases"]:
        file = out / case["id"] / "MEASUREMENTS.json"
        if file.exists():
            value = json.loads(file.read_text(encoding="utf-8"))
        else:
            world = d.OrganizationalWorld.load_snapshot(str(parent))
            spec = channel.describe_dual()
            try:
                child, value = inverse(world, spec, case, out / case["id"])
            except ValueError as error:
                # Guard aborts are measurements of applicability, not a new
                # physical counterfactual and not a claim of causal necessity.
                neutral = json.loads(world.runtime.snapshot_metadata(KEY))
                age = 267 - (239 if neutral["word_order"][0] == "W1" else 267)
                sites = [channel.moved(spec["lexical_hubs"]["W1"], (-1, sign, 0), age) for sign in (-1, 1)]
                value = {"status": "INTERVENTION_NOT_APPLICABLE", "reason": str(error),
                         "initial_parent": channel.digest(world), "final_child": None,
                         "emitted_symbols": [], "available": None, "parent_unchanged": True,
                         "new_future_trajectory_executed": False, "diagnostic_raw_writes": 0,
                         "candidate_current_observations": [channel.observe(world, site) for site in sites],
                         "full_NSM_semantics": False,
                         "scope": "The actual segment required by the frozen local removal was not reconstructed; no fabricated carrier or cut and no inference of causal irrelevance."}
                put(file, value)
        rows.append({"id": case["id"], "status": value.get("status", "MEASURED"),
                     "symbols": value["emitted_symbols"], "available": value["available"],
                     "parent_unchanged": value["parent_unchanged"],
                     "evidence": file.relative_to(ROOT).as_posix()})
        put(out / "RESULTS_COMPLETED.json", {"original_config_sha256": sha(out / "INVERSE_CONFIG.json"),
                                              "instrumental_completion_sha256": sha(continuation_path), "cases": rows})
    print(json.dumps(rows))


if __name__ == "__main__": main()
