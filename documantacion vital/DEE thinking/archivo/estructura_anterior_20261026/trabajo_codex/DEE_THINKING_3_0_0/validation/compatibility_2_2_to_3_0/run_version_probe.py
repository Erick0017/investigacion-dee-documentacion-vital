from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from array import array
from pathlib import Path
from typing import Any

import dee_thinking as dt


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def uint64_digest(values: list[int]) -> dict[str, Any]:
    payload = array("Q", (int(value) for value in values))
    if sys.byteorder != "little":
        payload.byteswap()
    raw = payload.tobytes()
    return {
        "length": len(values),
        "encoding": "uint64-little-endian",
        "sha256": hashlib.sha256(raw).hexdigest(),
        "nonzero": sum(value != 0 for value in values),
    }


def state_signature(world: Any) -> dict[str, Any]:
    raw = list(world.raw_copy())
    clock = list(world.clock_copy())
    return {
        "tick": int(world.current_tick),
        "raw": uint64_digest(raw),
        "clock": uint64_digest(clock),
    }


def legacy_channel_protocol() -> dict[str, Any]:
    world = dt.Runtime(11)
    world.execution_options = dt.TickOptions(dt.Backend.LAZY, 1)

    channel = dt.ChannelSpec()
    channel.name = "compat_input"
    channel.injection_site = dt.Coordinate(3, 4, 5)
    channel.state = 101
    channel.direction = dt.Direction(1, 0, 0)
    channel.semantic = 1
    channel.allow_experience = True
    channel.allow_probe = True
    world.register_channel(channel)

    first = world.experience("compat_input", 0, 17)
    world.advance(1)
    second = world.experience("compat_input", 1, 19)
    world.run_until(6)

    result = state_signature(world)
    result.update(
        {
            "dimension": 11,
            "backend": "LAZY",
            "threads": 1,
            "horizon_tick": 6,
            "requested_inputs": [
                {"tick": 0, "s_reg": 17, "status": str(first.status)},
                {"tick": 1, "s_reg": 19, "status": str(second.status)},
            ],
            "receipt_count": len(world.receipts),
            "observed_site_raw": int(
                world.observe(dt.Coordinate(3, 4, 5)).raw
            ),
            "observed_site_clock": int(
                world.observe(dt.Coordinate(3, 4, 5)).clock
            ),
        }
    )
    return result


def legacy_snapshot_protocol(snapshot: Path) -> dict[str, Any]:
    world = dt.Runtime.load_snapshot(str(snapshot))
    world.execution_options = dt.TickOptions(dt.Backend.LAZY, 1)
    start = state_signature(world)
    world.advance(32)
    end = state_signature(world)
    return {
        "snapshot_path": str(snapshot.resolve()),
        "snapshot_sha256": sha256_file(snapshot),
        "backend": "LAZY",
        "threads": 1,
        "advance_ticks": 32,
        "start": start,
        "end": end,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = {
        "schema": "dee_thinking.compatibility_probe.v1",
        "runtime_version": str(dt.__version__),
        "module_file": str(Path(dt.__file__).resolve()),
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "kernel_modulus": int(dt.KERNEL_MODULUS),
        "reducer_cap": int(dt.REDUCER_CAP),
        "build_info": dict(dt.build_info()),
        "cases": {
            "legacy_channel_protocol": legacy_channel_protocol(),
            "legacy_snapshot_seed": legacy_snapshot_protocol(args.snapshot),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"version": dt.__version__, "output": str(args.output)}))


if __name__ == "__main__":
    main()
