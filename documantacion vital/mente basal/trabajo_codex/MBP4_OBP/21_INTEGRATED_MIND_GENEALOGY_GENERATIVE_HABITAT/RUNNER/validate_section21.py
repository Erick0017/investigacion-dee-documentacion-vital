from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import dee_thinking as dee


SECTION = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_json(relative: str) -> Any:
    return json.loads((SECTION / relative).read_text(encoding="utf-8"))


def main() -> None:
    summary = load_json("RUN_SUMMARY.json")
    main_run = load_json("TELEMETRY/MAIN_CONTINUITY.json")
    controls = load_json("TELEMETRY/CAUSAL_CONTROLS.json")
    holdouts = load_json("TELEMETRY/HOLDOUTS.json")
    two_body = load_json("TELEMETRY/TWO_BODY_EXTENSION.json")
    backend = load_json("TELEMETRY/BACKEND_EQUIVALENCE.json")
    resume = load_json("TELEMETRY/RESUME_EQUIVALENCE.json")
    tracker = load_json("TELEMETRY/GENEALOGY_TRACKER_VALIDATION.json")

    checkpoint_checks = []
    for item in summary["checkpoints"]:
        path = SECTION / item["path"]
        runtime = dee.Runtime.load_snapshot(str(path))
        before_tick = int(runtime.current_tick)
        before_raw = list(runtime.raw_copy())
        before_clock = list(runtime.clock_copy())
        runtime.advance(0)
        expected_tick = item.get("tick")
        checkpoint_checks.append({
            "path": item["path"],
            "hash_equal": sha256(path) == item["sha256"],
            "loaded_tick": before_tick,
            "expected_tick": expected_tick,
            "tick_equal_when_declared": expected_tick is None or before_tick == int(expected_tick),
            "advance_zero_raw_equal": before_raw == list(runtime.raw_copy()),
            "advance_zero_clock_equal": before_clock == list(runtime.clock_copy()),
            "advance_zero_tick_equal": before_tick == int(runtime.current_tick),
            "dimension": int(runtime.dimension),
        })

    complete = main_run["complete_episodes"]
    event_reader_consistent = (
        len(complete) == int(main_run["complete_episode_count"])
        and all(row["action"]["matches_frozen_lineage_phase"] for row in complete)
        and all(row["return"]["matches_frozen_lineage_phase"] for row in complete)
    )
    no_post_t0_writes = (
        int(main_run["host_writes_after_t0"]) == 0
        and all(int(row["host_writes_after_t0"]) == 0 for row in controls.values())
        and all(int(row["host_writes_after_t0"]) == 0 for row in holdouts)
        and all(int(row["host_writes_after_t0"]) == 0 for row in two_body)
    )
    technical_equalities = {
        "backend_raw": bool(backend["raw_equal"]),
        "backend_clock": bool(backend["clock_equal"]),
        "resume_raw": bool(resume["raw_equal"]),
        "resume_clock": bool(resume["clock_equal"]),
        "tracker_raw_enabled_disabled": bool(tracker["tracker_vs_unobserved_raw_equal"]),
        "tracker_clock_enabled_disabled": bool(tracker["tracker_vs_unobserved_clock_equal"]),
    }
    validation = {
        "schema": "mbp4.integrated-mind.technical-validation.v1",
        "checkpoint_checks": checkpoint_checks,
        "event_reader_consistent": event_reader_consistent,
        "complete_episode_count": len(complete),
        "no_post_t0_host_writes": no_post_t0_writes,
        "controls_present": sorted(controls) == sorted(summary["controls_executed"]),
        "holdout_count": len(holdouts),
        "two_body_world_count": len(two_body),
        "technical_equalities": technical_equalities,
    }
    validation["all_technical_checks_true"] = (
        all(
            row["hash_equal"]
            and row["tick_equal_when_declared"]
            and row["advance_zero_raw_equal"]
            and row["advance_zero_clock_equal"]
            and row["advance_zero_tick_equal"]
            for row in checkpoint_checks
        )
        and event_reader_consistent
        and no_post_t0_writes
        and validation["controls_present"]
        and len(holdouts) == 2
        and len(two_body) == 4
        and all(technical_equalities.values())
    )
    output = SECTION / "TELEMETRY" / "TECHNICAL_VALIDATION.json"
    output.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not validation["all_technical_checks_true"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
