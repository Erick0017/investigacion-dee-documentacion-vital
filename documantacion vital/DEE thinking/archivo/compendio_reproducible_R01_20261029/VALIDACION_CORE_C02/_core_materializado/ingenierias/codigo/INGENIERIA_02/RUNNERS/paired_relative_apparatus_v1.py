#!/usr/bin/env python3
"""Paired relative-memory organization with a later native midpoint readout."""
from __future__ import annotations

import numpy as np

from ing02_common import NativeWorld, add, pack, read, summarize


OUTWARD_PLANE = tuple((1, y, z) for y in (-1, 0, 1) for z in (-1, 0, 1))


def _put(raw, clock, q, state, sreg, direction=(0, 0, 0), semantic=4, phase=0):
    if int(raw[q]):
        raise RuntimeError(f"overlap at {q}: {read(raw, q)}")
    raw[q] = pack(state, sreg, direction, semantic)
    clock[q] = np.uint64(phase)


def construct(kernel, challenge):
    n = int(challenge.get("n", 23))
    c = tuple(int(x) % n for x in challenge.get("origin", (n // 2,) * 3))
    mode = challenge.get("mode", "experience_a")
    support_pattern = tuple(tuple(int(v) for v in q) for q in challenge["support_pattern"])
    a = add(c, (-1, 0, 0), 1, n)
    b = add(c, (1, 0, 0), 1, n)
    raw = np.zeros((n, n, n), np.uint64)
    clock = np.zeros_like(raw)
    phase_a = 261 if mode == "wrong_phase" else 260
    _put(raw, clock, a, 1000, 100, semantic=1, phase=phase_a)
    _put(raw, clock, b, 2000, 100, semantic=1, phase=260)
    # Supports extend away from the midpoint and therefore do not touch the reader/comparator.
    for index, offset in enumerate(support_pattern):
        left = (-1, offset[1], offset[2])
        right = (1, -offset[1], -offset[2])
        _put(raw, clock, add(a, left, 1, n), 3000 + index, 0, semantic=4, phase=31 + index)
        _put(raw, clock, add(b, right, 1, n), 4000 + index, 0, semantic=4, phase=41 + index)
    event_start = add(a, (0, -1, 0), 1, n)
    if mode in {"experience_a", "wrong_phase", "experience_both"}:
        _put(raw, clock, event_start, 5000, 3, (0, -1, 0), semantic=1, phase=17)
    if mode == "experience_both":
        _put(raw, clock, add(b, (0, 1, 0), 1, n), 5001, 3, (0, 1, 0), semantic=1, phase=19)
    reader_start = add(c, (0, -1, 0), 1, n)
    if mode != "no_reader":
        # State zero is routed but does not count as active support during the write.
        _put(raw, clock, reader_start, 0, 7, (0, 1, 0), semantic=1, phase=23)
    return NativeWorld(kernel, raw, clock), {
        "a": a,
        "b": b,
        "comparator": c,
        "reader_start": reader_start,
        "event_start": event_start,
    }


def run_case(kernel, challenge):
    world, ports = construct(kernel, challenge)
    horizon = int(challenge.get("horizon", 8))
    trace = []
    for tick in range(1, horizon + 1):
        info = world.tick()
        ra, rb, rc = (read(world.raw, ports[key]) for key in ("a", "b", "comparator"))
        trace.append(
            {
                "tick": tick,
                "a": ra,
                "b": rb,
                "sreg_delta_a_minus_b": None if ra is None or rb is None else ra["sreg"] - rb["sreg"],
                "comparator": rc,
                "comparator_x": None if rc is None else rc["direction"][0],
                "support": int(np.count_nonzero(world.raw)),
                "kernel": {str(k): int(v) if isinstance(v, (int, np.integer)) else v for k, v in info.items()},
            }
        )
    return {
        "challenge_id": challenge.get("challenge_id"),
        "n": world.n,
        "mode": challenge.get("mode", "experience_a"),
        "support_pattern": challenge["support_pattern"],
        "ports": {key: list(q) for key, q in ports.items()},
        "trace": trace,
        "terminal": summarize(world.raw, world.clock_a),
        "python_interventions_after_t0": 0,
    }
