from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE.parent
sys.path.insert(0, str(WORK / "source"))
sys.path.insert(0, str(HERE))

import dee_thinking as dee
from mbp4_obp import ACTION1, observe, sha256, write_json
from run_mbp4 import build_case, digest_u64, rec_summary


def state(runtime):
    return {
        "tick": int(runtime.current_tick),
        "raw_sha256": digest_u64(runtime.raw_copy()),
        "clock_sha256": digest_u64(runtime.clock_copy()),
        "receipts": len(runtime.receipts),
        "raw_support": int(runtime.metrics().raw_support),
    }


def main() -> None:
    tests = WORK / "tests"
    replay_dir = WORK / "13_REPLAY"
    tests.mkdir(parents=True, exist_ok=True)
    replay_dir.mkdir(parents=True, exist_ok=True)
    runtime, reset, feedback, config = build_case(
        n=47, bit=1, mode="treatment", q_reset=(34, 34, 34),
        q_feedback=(8, 8, 8), permutation=(0, 1, 2), signs=(1, 1, 1), backend="dense")
    t0 = WORK / "12_CHECKPOINTS" / "OBP_FRESH_LOCKED_T0.deetsnap"
    runtime.set_snapshot_metadata("mbp4.phase", "LOCKED_T0")
    runtime.save_snapshot(str(t0))
    initial = state(runtime)
    passive_before = state(runtime)
    _ = runtime.observe(dee.Coordinate(34, 34, 34))
    passive_after = state(runtime)
    trace = []
    for rel in range(1, 33):
        runtime.advance(1)
        target = reset.qp if rel % 2 else reset.q
        expected = tuple(-x for x in reset.p) if rel % 2 else reset.p
        row = {"tick": rel, "recurrence_target": list(target),
               "recurrence": rec_summary(runtime, target),
               "recurrence_exact": observe(runtime, target) is not None and tuple(observe(runtime, target)["direction"]) == expected}
        if rel in feedback.query_ticks:
            cycle = feedback.query_ticks.index(rel)
            row["action"] = rec_summary(runtime, feedback.action_targets[1][cycle])
            row["action_exact"] = row["action"] is not None and tuple(row["action"]["direction"]) == ACTION1
        trace.append(row)
    reconstructed = state(runtime)
    main_path = WORK / "12_CHECKPOINTS" / "OBP_FRESH_VALIDATED_T32.deetsnap"
    delivered = dee.Runtime.load_snapshot(str(main_path))
    delivered_state = state(delivered)
    final_match = reconstructed == delivered_state
    # Two independent continuations from one byte checkpoint.
    a = dee.Runtime.load_snapshot(str(main_path)); b = dee.Runtime.load_snapshot(str(main_path))
    a.execution_options = dee.TickOptions(dee.Backend.DENSE_SEQUENTIAL, 1)
    b.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)
    a.advance(16); b.advance(16)
    continuation = {"dense": state(a), "lazy": state(b),
                    "raw_equal": a.raw_copy() == b.raw_copy(),
                    "clock_equal": a.clock_copy() == b.clock_copy()}
    # Invalid snapshot rejection without touching the valid checkpoint.
    corrupt = tests / "INVALID_TRUNCATED.deetsnap"
    data = main_path.read_bytes()
    corrupt.write_bytes(data[: max(1, len(data) // 3)])
    rejected = False; error = None
    try:
        dee.Runtime.load_snapshot(str(corrupt))
    except Exception as exc:
        rejected = True; error = f"{type(exc).__name__}: {exc}"
    report = {
        "schema": "mbp4.validation.v1",
        "config": config,
        "t0": {**initial, "checkpoint": str(t0.relative_to(WORK)), "sha256": sha256(t0)},
        "observe_passive": passive_before == passive_after,
        "reconstructed_t32": reconstructed,
        "delivered_t32": {**delivered_state, "checkpoint": str(main_path.relative_to(WORK)), "sha256": sha256(main_path)},
        "replay_exact": final_match,
        "restore_continue": continuation,
        "invalid_snapshot_rejected": rejected,
        "invalid_snapshot_error": error,
        "valid_snapshot_preserved_sha256": sha256(main_path),
        "pass": all([passive_before == passive_after, final_match, continuation["raw_equal"], continuation["clock_equal"], rejected]),
    }
    write_json(replay_dir / "REPLAY_T0_T32.json", {"schema": "mbp4.replay.v1", "trace": trace,
                                                    "final": reconstructed, "matches_delivered_checkpoint": final_match})
    write_json(tests / "VALIDATION_RESULTS.json", report)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
