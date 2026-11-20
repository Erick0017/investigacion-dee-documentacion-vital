from __future__ import annotations

import sys
from pathlib import Path

import dee_thinking as dt


def _same_receipt(left: dt.EventReceipt, right: dt.EventReceipt) -> bool:
    return (
        left.id == right.id
        and left.kind == right.kind
        and left.status == right.status
        and left.requested_tick == right.requested_tick
        and left.effective_tick == right.effective_tick
        and left.channels == right.channels
        and left.reason == right.reason
    )


def _prepared_world() -> dt.Runtime:
    world = dt.Runtime(11)
    channel = dt.ChannelSpec()
    channel.name = "bridge_input"
    channel.injection_site = dt.Coordinate(3, 4, 5)
    channel.state = 101
    channel.direction = dt.Direction(1, 0, 0)
    channel.semantic = 1
    channel.allow_experience = True
    channel.allow_probe = True
    world.register_channel(channel)
    assert world.experience("bridge_input", 0, 17).status == dt.EventStatus.SCHEDULED
    world.advance(1)
    assert world.experience("bridge_input", 1, 19).status == dt.EventStatus.SCHEDULED
    world.set_snapshot_metadata("bridge.origin", "python")
    world.protocol_phase = "bridge.pending_second_input"
    return world


def produce(checkpoint: Path, future: Path) -> None:
    world = _prepared_world()
    world.save_snapshot(str(checkpoint))
    world.run_until(6)
    world.save_snapshot(str(future))
    print("python_produce tick=1 future_tick=6 pending=true")


def consume(checkpoint: Path, future: Path) -> None:
    resumed = dt.Runtime.load_snapshot(str(checkpoint))
    expected = dt.Runtime.load_snapshot(str(future))
    assert resumed.current_tick < expected.current_tick
    resumed.run_until(expected.current_tick)
    assert resumed.raw_copy() == expected.raw_copy()
    assert resumed.clock_copy() == expected.clock_copy()
    actual_receipts = resumed.receipts
    expected_receipts = expected.receipts
    assert len(actual_receipts) == len(expected_receipts)
    assert all(_same_receipt(a, b) for a, b in zip(actual_receipts, expected_receipts))
    assert resumed.protocol_phase == expected.protocol_phase
    print(f"python_consume raw_clock_receipts_exact=true tick={resumed.current_tick}")


def main() -> None:
    if len(sys.argv) != 4 or sys.argv[1] not in {"produce", "consume"}:
        raise SystemExit(
            "usage: cross_language_bridge.py produce|consume CHECKPOINT FUTURE"
        )
    mode, checkpoint, future = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    (produce if mode == "produce" else consume)(checkpoint, future)


if __name__ == "__main__":
    main()
