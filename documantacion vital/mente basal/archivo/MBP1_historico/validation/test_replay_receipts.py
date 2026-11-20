"""Focused replay regression, including an input accepted at the end boundary."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


HABITAT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HABITAT_ROOT))

from app import habitat  # noqa: E402


def main(output: Path) -> int:
    with tempfile.TemporaryDirectory(prefix="mente-basal-replay-test-") as temporary:
        directory = Path(temporary)
        runtime, _, _ = habitat.build_x0(habitat.default_config())
        start = directory / "start.deetsnap"
        expected = directory / "expected.deetsnap"
        replayed = directory / "replayed.deetsnap"
        segment = directory / "segment.jsonl"
        runtime.save_snapshot(str(start))
        for command_tick, load in ((0, 5), (1, 7), (2, 9)):
            if int(runtime.current_tick) < command_tick:
                runtime.run_until(command_tick)
            receipt = runtime.experience("external.port.alpha", command_tick, load)
            habitat.append_jsonl(segment, {
                "type": "input_scheduled", "command_tick": command_tick,
                "receipt_id": int(receipt.id), "channel": "external.port.alpha",
                "load": load, "requested_tick": command_tick,
            })
        runtime.save_snapshot(str(expected))
        result = habitat.replay(HABITAT_ROOT, start, segment, 2, replayed, expected)
    checks = {
        "raw_exact": result["raw_exact"] is True,
        "clock_exact": result["clock_exact"] is True,
        "tick_exact": result["tick_exact"] is True,
        "receipts_exact": result["receipts_exact"] is True,
        "receipt_ids_exact": result["receipt_ids_exact"] is True,
        "end_boundary_input_replayed": result["events_replayed"] == 3,
    }
    report = {"schema": "mente-basal.replay-regression.v1",
              "checks": checks, "all_passed": all(checks.values()),
              "result": result}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
