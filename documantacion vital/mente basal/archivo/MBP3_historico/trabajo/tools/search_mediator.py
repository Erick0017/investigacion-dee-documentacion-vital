from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
import mbp3


def run(direction: tuple[int, int, int], arrival: int = 190) -> dict:
    parent = mbp3.dee.Runtime.load_snapshot(str(mbp3.parent_path()))
    raw = parent.raw_copy()
    clock = parent.clock_copy()
    base_items = [x for x in mbp3.environment_spec("MAIN") if x["id"] not in {"P4", "P5"}]
    for item in base_items:
        mbp3._place(raw, clock, item)
    target = mbp3.plus((97, 74, 0), (1, 1, 0), arrival - 160)
    item = mbp3._carrier("P4_SEARCH", 1, direction, arrival, target, "primary")
    mbp3._place(raw, clock, item)
    runtime = mbp3.dee.Runtime.import_research_state(mbp3.N, mbp3.PARENT_TICK, raw, clock)
    runtime.execution_options = mbp3.dee.TickOptions(mbp3.dee.Backend.LAZY, 1)
    runtime.run_until(mbp3.PARENT_TICK + arrival)
    expected_direction = mbp3.sign_sum((1, 1, 0), direction)
    observed = mbp3.base.observe_site(runtime, target)
    return {
        "direction": list(direction), "arrival": arrival, "target": list(target),
        "source": item["source"], "expected_load": 32,
        "expected_direction": list(expected_direction), "observed": observed,
        "success": observed["s_reg"] == 32 and observed["direction"] == list(expected_direction),
    }


def main() -> int:
    candidates = [(-1, -1, 1), (-1, 0, 1), (0, -1, 1), (-1, -1, -1)]
    result = {
        "schema": "mbp3.mediator-search.v1",
        "fixed_arrival": 190,
        "motivation": "avoid the observed t34 toroidal pre-collision while changing one causal direction",
        "cases": [run(value) for value in candidates],
    }
    output = ROOT / "pilots" / "MEDIATOR_VARIANTS.json"
    mbp3.base.atomic_json(output, result)
    print(json.dumps(result, indent=2))
    return 0 if any(x["success"] for x in result["cases"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
