"""Directed replay154..181 of the saved FULL reversal, without interventions."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import experiment, habitat, memory
from src.common import digest, identity, obs, put, receipt, sha


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True, type=Path)
    p.add_argument("--wheel", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    import dee_thinking as d
    root = a.root.resolve()
    folder = root / "resultados" / "reversal01" / "FULL_REVERSE"
    start_path = folder / "S1_ROUND1_AFTER_MEETING.deetsnap"
    expected_path = folder / "S2_ROUND1_BEFORE_MEETING.deetsnap"
    world = d.OrganizationalWorld.load_snapshot(str(start_path))
    assert world.runtime.current_tick == 154
    expected = d.OrganizationalWorld.load_snapshot(str(expected_path))
    assert expected.runtime.current_tick == 181
    bank = experiment.descriptors()["train.S2"]
    interception = tuple(bank["interception"])
    frames = []
    ids = []
    for tick in range(154, 182):
        if tick == 165:
            ids.extend(x.id for x in habitat.submit_resources(world, bank, 165))
        if tick == 166:
            ids.append(habitat.submit_event(world, bank, "U", 165).id)
        if tick == 179:
            actual = experiment.current_outcome_sensor(world, bank)
            ids.extend(x.id for x in memory.broadcast_outcome(world, actual["observed_class"], 179))
            ids.append(memory.present_signal(world, "S2", 179).id)
        if tick in (165, 166, 170, 171, 172, 173, 174, 176, 177, 178, 179, 181):
            around = [obs(world, memory.plus(interception, (x, y, z)))
                for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1)
                if (x, y, z) != (0, 0, 0)]
            frames.append({"tick": tick,
                "event_U_source": obs(world, bank["event_U_source"]),
                "event_V_source": obs(world, bank["event_V_source"]),
                "interception": obs(world, interception),
                "interception_active_neighbors": [x for x in around if x["active"]],
                "supply_source": obs(world, bank["supply_source"]),
                "supply_meeting": obs(world, bank["supply_meeting"]),
                "function_receiver": obs(world, bank["function_receiver"]),
                "diverted_UV_candidate": obs(world, memory.plus(interception, (0, -1, 1), max(0, tick - 173)))})
        if tick < 181:
            world.advance()
    assert world.runtime.raw_copy() == expected.runtime.raw_copy()
    assert world.runtime.clock_copy() == expected.runtime.clock_copy()
    actual_receipts = [receipt(world, x) for x in ids]
    result = {"scope": "One directed replay of an already measured window; no diagnostic edits, new hypothesis search, or fourth full reversal cohort",
              "identity": identity(a.wheel), "start": {"path": start_path.relative_to(root).as_posix(), "sha256": sha(start_path)},
              "expected_end": {"path": expected_path.relative_to(root).as_posix(), "sha256": sha(expected_path)},
              "start_tick": 154, "end_tick": 181, "replay_raw_clocks_equal_saved_end": True,
              "native_diagnostic_edits": 0, "bank": bank, "frames": frames,
              "actual_receipts": actual_receipts, "final_digest": digest(world),
              "source_sha256": sha(__file__)}
    put(a.output, result)


if __name__ == "__main__":
    main()
