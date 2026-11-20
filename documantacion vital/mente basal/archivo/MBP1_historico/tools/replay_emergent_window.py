from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--to", type=int, default=900)
    parser.add_argument("--backend", choices=("dense", "lazy"), default="dense")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root / "app"))
    import habitat

    runtime = habitat.dee.Runtime.load_snapshot(str(args.checkpoint))
    selected_backend = (habitat.dee.Backend.DENSE_SEQUENTIAL
                        if args.backend == "dense" else habitat.dee.Backend.LAZY)
    runtime.execution_options = habitat.dee.TickOptions(selected_backend, 1)
    runtime.resume()
    sites = list(habitat.geometry().environment)
    previous = [habitat.observe_site(runtime, site)["s_reg"] for site in sites]
    events = []
    while int(runtime.current_tick) < args.to:
        runtime.advance(1)
        values = [habitat.observe_site(runtime, site)["s_reg"] for site in sites]
        if values != previous:
            events.append({
                "tick": int(runtime.current_tick), "before": previous,
                "after": values, "sites": [list(site) for site in sites],
                "source": "directed diagnostic replay from immutable T64 checkpoint",
            })
            previous = values
    result = {
        "schema": "mente-basal.emergent-window-replay.v1",
        "start_tick": 64, "end_tick": int(runtime.current_tick),
        "backend": ("DenseSequential" if args.backend == "dense" else "Lazy"),
        "external_inputs": 0,
        "events": events,
        "main_world_modified": False,
    }
    habitat.atomic_json(args.output, result)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
