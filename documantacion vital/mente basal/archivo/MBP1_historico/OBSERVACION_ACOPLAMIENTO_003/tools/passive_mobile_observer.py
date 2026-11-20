from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any


N = 127
ANCHORS = {
    "REL4184": {"tick": 64, "site": (83, 116, 63), "raw": 1157724549354094593, "direction": (1, 1, 0)},
    "MAT68": {"tick": 64, "site": (28, 12, 82), "raw": 1229482990329921537, "direction": (0, 1, 1)},
    "CTX40": {"tick": 64, "site": (110, 27, 104), "raw": 1225260745420177409, "direction": (1, 0, 1)},
}
RESIDUES = ((82, 91, 48), (82, 91, 52), (82, 91, 56), (82, 91, 60))


def predicted(anchor: dict[str, Any], tick: int) -> tuple[int, int, int]:
    elapsed = tick - int(anchor["tick"])
    return tuple((anchor["site"][i] + anchor["direction"][i] * elapsed) % N
                 for i in range(3))  # type: ignore[return-value]


def observation_dict(item: Any) -> dict[str, Any]:
    record = item.record
    return {
        "tick": int(item.tick),
        "coordinate": [int(item.coordinate.x), int(item.coordinate.y), int(item.coordinate.z)],
        "raw": int(item.raw), "clock": int(item.clock),
        "state": int(record.state), "s_reg": int(record.s_reg),
        "direction": [int(record.dx), int(record.dy), int(record.dz)],
        "semantic": int(record.semantic), "occupied": bool(record.occupied),
        "raw_present": bool(record.raw_present),
    }


def sample(dee: Any, checkpoint: Path, validate_passivity: bool = False) -> dict[str, Any]:
    runtime = dee.Runtime.load_snapshot(str(checkpoint))
    tick = int(runtime.current_tick)
    sites = [predicted(anchor, tick) for anchor in ANCHORS.values()] + list(RESIDUES)
    before = None
    if validate_passivity:
        before = (runtime.raw_copy(), runtime.clock_copy(), tick)
    started = time.perf_counter_ns()
    values = runtime.observe_many([dee.Coordinate(*site) for site in sites])
    elapsed = time.perf_counter_ns() - started
    after_exact = None
    if validate_passivity and before is not None:
        after_exact = (before[0] == runtime.raw_copy() and
                       before[1] == runtime.clock_copy() and
                       before[2] == int(runtime.current_tick))
    mobile: dict[str, Any] = {}
    for index, (name, anchor) in enumerate(ANCHORS.items()):
        item = observation_dict(values[index])
        if item["raw"] == anchor["raw"]:
            status = "ENDPOINT_EXACT_TRANSPORT"
        elif item["raw"] == 0:
            status = "NOT_OBSERVED_EXPECTED"
        else:
            status = "TRANSFORMATION_OR_COLLISION_CANDIDATE"
        mobile[name] = {
            "anchor": {**anchor, "site": list(anchor["site"]), "direction": list(anchor["direction"])},
            "predicted_site": list(sites[index]), "observation": item, "status": status,
            "continuity_limit": "endpoint evidence; tickwise continuity requires replay",
        }
    residues = []
    for index, site in enumerate(RESIDUES, start=len(ANCHORS)):
        residues.append({"slot": index - len(ANCHORS) + 1, "site": list(site),
                         "observation": observation_dict(values[index])})
    return {
        "schema": "mente-basal.passive-mobile-observer.v1",
        "checkpoint": str(checkpoint), "checkpoint_tick": tick,
        "sample_tick": tick, "coverage": "3 predicted mobile sites + 4 fixed residue sites",
        "mobile": mobile, "residues": residues,
        "observe_many_elapsed_ns": elapsed, "passivity_exact": after_exact,
        "writes_to_world": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--validate-passivity", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root / "app"))
    import habitat
    result = sample(habitat.dee, args.checkpoint.resolve(), args.validate_passivity)
    habitat.atomic_json(args.output.resolve(), result)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
