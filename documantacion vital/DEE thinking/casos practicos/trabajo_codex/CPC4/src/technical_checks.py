"""Finite, explicit technical checks on the actual CPC4 continuation states."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common import digest, identity, put, receipt, sha


def operational(world):
    rt = world.runtime
    return {"physics": digest(world), "channels": list(rt.channel_names),
            "receipts": [receipt(world, r.id) for r in rt.receipts],
            "metadata": dict(rt.snapshot_metadata_entries),
            "interfaces": [x.name for x in world.interfaces],
            "external_operations": list(world.external_operations)}


def run(parent, output, wheel):
    import dee_thinking as d
    from src import channel, channel_dual
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    instrument = identity(wheel)
    original = d.OrganizationalWorld.load_snapshot(str(parent))
    spec = channel.describe_dual()
    pre = operational(original)
    for _ in range(12):
        channel_dual.panel(original, spec)
    assert operational(original) == pre
    fork = original.fork()
    assert operational(fork) == pre
    if fork.runtime.current_tick >= 155:
        raise ValueError("Use the pre-common-query checkpoint, not a terminal fixture")
    intermediate = output / "ROUNDTRIP_WITH_PENDING_INPUTS.deetsnap"
    fork.save_snapshot(str(intermediate))
    loaded = d.OrganizationalWorld.load_snapshot(str(intermediate))
    assert operational(loaded) == operational(fork)
    modes = {}
    for name, backend in (("lazy", d.Backend.LAZY),
                          ("dense", d.Backend.DENSE_SEQUENTIAL),
                          ("parallel", d.Backend.DENSE_PARALLEL)):
        world = loaded.fork()
        world.runtime.execution_options = d.TickOptions(backend, 1 if name != "parallel" else 2)
        world.run_until(155)
        modes[name] = operational(world)
    assert modes["lazy"] == modes["dense"] == modes["parallel"]
    original.run_until(155)
    assert operational(original) == modes["lazy"]
    assert loaded.runtime.current_tick == pre["physics"]["tick"]
    # A physical diagnostic occurs in a distinct full fork, never MAIN.
    q = spec["sham_source"]
    site = channel.moved(q, (1, 0, 0), loaded.runtime.current_tick)
    before = channel.observe(loaded, site)
    child, edit = channel.diagnostic_record_edit(loaded, site, "TECHNICAL_FORK_ISOLATION", raw=0, expected_load=13)
    assert operational(loaded) == pre
    assert digest(child) != digest(loaded)
    value = {"instrument": instrument, "source_checkpoint": str(Path(parent).name),
             "source_sha256": sha(parent), "start_tick": pre["physics"]["tick"],
             "end_tick": 155, "passive_observation_unchanged": True,
             "full_operational_roundtrip": True, "direct_save_load_same_future": True,
             "lazy_dense_parallel_same_future": True, "deep_fork_isolation": True,
             "pending_receipts_at_boundary": [r for r in pre["receipts"] if r["status"] == "scheduled"],
             "diagnostic_edit": edit, "dummy_pre": before,
             "mode_results": modes, "elapsed_seconds": time.monotonic()-started}
    put(output / "TECHNICAL_CHECKS.json", value)
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--wheel", type=Path, default=ROOT/"runtime"/"dee_thinking-4.0.0-cp313-cp313-win_amd64.whl")
    args = parser.parse_args()
    result = run(args.parent, args.output, args.wheel)
    print(json.dumps({"technical_checks": "completed", "elapsed_seconds": result["elapsed_seconds"]}))
