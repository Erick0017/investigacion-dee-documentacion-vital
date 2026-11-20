from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


CENTERS = ((82, 91, 48), (82, 91, 52), (82, 91, 56), (82, 91, 60))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--to", required=True, type=int)
    parser.add_argument("--backend", choices=("lazy", "dense"), default="lazy")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root / "app"))
    import habitat
    dee = habitat.dee
    runtime = dee.Runtime.load_snapshot(str(args.checkpoint.resolve()))
    start_tick = int(runtime.current_tick)
    if args.to < start_tick:
        raise ValueError("target precedes checkpoint")
    runtime.execution_options = dee.TickOptions(
        dee.Backend.LAZY if args.backend == "lazy" else dee.Backend.DENSE_SEQUENTIAL, 1)
    runtime.resume()
    coordinates = [dee.Coordinate(*site) for site in CENTERS]
    previous = [int(item.record.s_reg) for item in runtime.observe_many(coordinates)]
    events = []
    counters = {"overflows": 0, "genesis": 0}
    while int(runtime.current_tick) < args.to:
        info = runtime.advance(1)
        counters["overflows"] += int(info.overflows)
        counters["genesis"] += int(info.genesis)
        values = [int(item.record.s_reg) for item in runtime.observe_many(coordinates)]
        if values != previous:
            events.append({"tick": int(runtime.current_tick), "before": previous,
                           "after": values, "sites": [list(site) for site in CENTERS]})
            previous = values
    result = {
        "schema": "mente-basal.residue-window-replay.v1",
        "checkpoint": str(args.checkpoint.resolve()), "start_tick": start_tick,
        "end_tick": int(runtime.current_tick), "backend": args.backend,
        "events": events, "counters": counters, "external_inputs_injected": 0,
        "main_world_modified": False,
    }
    habitat.atomic_json(args.output.resolve(), result)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
