from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


N = 127
MASK64 = (1 << 64) - 1


def xyz(index: int) -> list[int]:
    x, rest = divmod(index, N * N)
    y, z = divmod(rest, N)
    return [x, y, z]


def rec(dee: Any, raw: int) -> dict[str, Any]:
    value = dee.decode_record(int(raw))
    return {
        "raw": int(raw), "state": int(value.state), "s_reg": int(value.s_reg),
        "direction": [int(value.dx), int(value.dy), int(value.dz)],
        "semantic": int(value.semantic), "occupied": bool(value.occupied),
        "raw_present": int(raw) != 0,
    }


def summarize(dee: Any, raw: list[int] | tuple[int, ...]) -> dict[str, Any]:
    occupied = 0
    s_reg_sum = 0
    semantic = Counter()
    directions = Counter()
    for item in raw:
        if not item:
            continue
        value = dee.decode_record(int(item))
        occupied += int(bool(value.occupied))
        s_reg_sum += int(value.s_reg)
        semantic[str(int(value.semantic))] += 1
        directions[str((int(value.dx), int(value.dy), int(value.dz)))] += 1
    return {
        "raw_support": sum(1 for item in raw if item), "occupied": occupied,
        "s_reg_sum": s_reg_sum, "semantic_counts_on_raw_support": dict(semantic),
        "direction_counts_on_raw_support": dict(directions),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--start", required=True, type=Path)
    parser.add_argument("--end", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root / "app"))
    import habitat
    dee = habitat.dee
    before_rt = dee.Runtime.load_snapshot(str(args.start.resolve()))
    after_rt = dee.Runtime.load_snapshot(str(args.end.resolve()))
    before_raw = before_rt.raw_copy()
    after_raw = after_rt.raw_copy()
    before_clock = before_rt.clock_copy()
    after_clock = after_rt.clock_copy()
    delta_tick = int(after_rt.current_tick) - int(before_rt.current_tick)
    clock_histogram = Counter()
    anomalies = []
    changed = []
    for index, (r0, r1, c0, c1) in enumerate(zip(before_raw, after_raw, before_clock, after_clock)):
        delta = (int(c1) - int(c0)) & MASK64
        clock_histogram[str(delta)] += 1
        if delta != delta_tick and len(anomalies) < 32:
            anomalies.append({"coordinate": xyz(index), "before": int(c0), "after": int(c1), "delta": delta})
        if int(r0) != int(r1):
            changed.append({
                "coordinate": xyz(index), "before": rec(dee, int(r0)),
                "after": rec(dee, int(r1)), "clock_before": int(c0), "clock_after": int(c1),
            })
    result = {
        "schema": "mente-basal.checkpoint-interval-audit.v1",
        "start_checkpoint": str(args.start.resolve()), "end_checkpoint": str(args.end.resolve()),
        "start_tick": int(before_rt.current_tick), "end_tick": int(after_rt.current_tick),
        "delta_tick": delta_tick, "site_count": len(before_raw),
        "lengths_equal": len(before_raw) == len(after_raw) == len(before_clock) == len(after_clock),
        "clock_delta_histogram": dict(clock_histogram),
        "all_clock_deltas_exact": not anomalies and set(clock_histogram) == {str(delta_tick)},
        "clock_anomalies_first_32": anomalies,
        "raw_changed_count": len(changed), "raw_changes": changed,
        "start_summary": summarize(dee, before_raw), "end_summary": summarize(dee, after_raw),
        "external_inputs_injected_by_analyzer": 0, "main_world_modified": False,
    }
    habitat.atomic_json(args.output.resolve(), result)
    print(json.dumps({
        "output": str(args.output.resolve()), "delta_tick": delta_tick,
        "raw_changed_count": len(changed), "all_clock_deltas_exact": result["all_clock_deltas_exact"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

