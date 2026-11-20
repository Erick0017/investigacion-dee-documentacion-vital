"""Passive saved-state coverage only: no advance, input, edit or fork call."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import memory
from src.common import digest, identity, obs, put, sha


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--wheel", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    import dee_thinking as d
    instrument = identity(a.wheel)
    root = a.root.resolve()
    base = root / "resultados" / "confirmacion" / "A_future_UV"
    files = [base / name for name in ("EMISSION_S2.deetsnap", "S2_USE_T119.deetsnap",
                                      "S2_USE_T123.deetsnap", "MAIN_FINAL.deetsnap")]
    for arm in ("FULL_REVERSE", "SIGNAL_INPUT_ONLY", "OUTCOME_REPORT_ONLY"):
        folder = root / "resultados" / "reversal01" / arm
        files += [folder / name for name in ("CONTINUATION_T129.deetsnap", "S1_ROUND1_BEFORE_MEETING.deetsnap",
                                             "S2_ROUND1_BEFORE_MEETING.deetsnap")]
    rows = []
    for path in files:
        world = d.OrganizationalWorld.load_snapshot(str(path))
        before = digest(world)
        tick = world.runtime.current_tick
        candidate = memory.plus(memory.hub("S2"), (-1, -1, 0), tick - 115)
        sample = obs(world, candidate)
        around = [obs(world, memory.plus(candidate, (x, y, z)))
                  for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1)
                  if (x, y, z) != (0, 0, 0)]
        assert digest(world) == before
        rows.append({"snapshot": path.relative_to(root).as_posix(), "snapshot_sha256": sha(path),
                     "tick": tick, "old_S2_ballistic_candidate": sample,
                     "candidate_active_neighbors": [x for x in around if x["active"]],
                     "scope": "Candidate projected from native emission115 direction(-1,-1,0); a mismatch terminates this simple tracking hypothesis and is not proof of destruction",
                     "observation_passive_digest_unchanged": True})
    put(a.output, {"instrument": instrument, "native_advances": 0, "native_inputs": 0,
                   "native_edits": 0, "native_forks": 0, "snapshots": rows,
                   "scope": "Passive inspection of already saved states only; not a fourth reversal trajectory"})


if __name__ == "__main__":
    main()
