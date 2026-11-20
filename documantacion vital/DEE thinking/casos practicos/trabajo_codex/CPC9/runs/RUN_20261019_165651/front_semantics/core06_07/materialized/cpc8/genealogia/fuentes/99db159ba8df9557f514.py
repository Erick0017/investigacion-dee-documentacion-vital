#!/usr/bin/env python3
"""Relative-memory midpoint readout using only topologically valid tetra supports."""
from __future__ import annotations

import numpy as np

from ing02_common import NativeWorld, add, pack, read, summarize


BASE_TETRA = ((-1, 0, 0), (0, 1, 0), (0, 0, 1), (-1, 1, 1))


def _put(raw, clock, q, state, sreg, direction=(0, 0, 0), semantic=4, phase=0):
    if int(raw[q]):
        raise RuntimeError(f"overlap at {q}: {read(raw, q)}")
    raw[q] = pack(state, sreg, direction, semantic)
    clock[q] = np.uint64(phase)


def construct(kernel, challenge):
    n = int(challenge.get("n", 17))
    c = tuple(int(x) % n for x in challenge.get("origin", (n // 2,) * 3))
    mode = challenge.get("mode", "experience_a")
    pa = tuple(tuple(int(v) for v in q) for q in challenge["support_pattern_a"])
    pb = tuple(tuple(int(v) for v in q) for q in challenge["support_pattern_b"])
    a = add(c, (-1, 0, 0), 1, n)
    b = add(c, (1, 0, 0), 1, n)
    raw = np.zeros((n, n, n), np.uint64)
    clock = np.zeros_like(raw)
    memory_phase = int(challenge.get("memory_phase", 260))
    phase_a = int(challenge.get("memory_phase_a", memory_phase + 1 if mode == "wrong_phase" else memory_phase))
    phase_b = int(challenge.get("memory_phase_b", memory_phase))
    _put(raw, clock, a, 1000, 100, semantic=1, phase=phase_a)
    _put(raw, clock, b, 2000, 100, semantic=1, phase=phase_b)
    for index, offset in enumerate(pa):
        _put(raw, clock, add(a, offset, 1, n), 3000 + index, 0, semantic=4, phase=31 + index)
    for index, offset in enumerate(pb):
        _put(raw, clock, add(b, offset, 1, n), 4000 + index, 0, semantic=4, phase=41 + index)
    event_a = add(a, (0, -1, 0), 1, n)
    if mode in {"experience_a", "wrong_phase", "experience_both"} or bool(challenge.get("experience_a", False)):
        _put(raw, clock, event_a, 5000, 3, (0, -1, 0), semantic=1, phase=17)
    if mode == "experience_both":
        _put(raw, clock, add(b, (0, 1, 0), 1, n), 5001, 3, (0, 1, 0), semantic=1, phase=19)
    reader = add(c, (0, -1, 0), 1, n)
    reader_source = add(c, (0, -2, 0), 1, n)
    if mode != "no_reader" and bool(challenge.get("reader_enabled", True)):
        if bool(challenge.get("persistent_reader_source", False)):
            semantic = 1 if mode == "finite_reader_source" else 4
            _put(raw, clock, reader_source, 6000, 7, (0, 1, 0), semantic=semantic, phase=int(challenge.get("reader_phase", 23)))
        else:
            _put(raw, clock, reader, 0, 7, (0, 1, 0), semantic=1, phase=int(challenge.get("reader_phase", 23)))
    return NativeWorld(kernel, raw, clock), {"a": a, "b": b, "comparator": c, "reader_start": reader, "reader_source": reader_source, "event_a": event_a}


def run_case(kernel, challenge):
    world, ports = construct(kernel, challenge)
    trace = []
    for tick in range(1, int(challenge.get("horizon", 8)) + 1):
        info = world.tick()
        ra, rb, rc = (read(world.raw, ports[key]) for key in ("a", "b", "comparator"))
        trace.append({
            "tick": tick,
            "a": ra,
            "b": rb,
            "delta": None if ra is None or rb is None else ra["sreg"] - rb["sreg"],
            "comparator": rc,
            "x": None if rc is None else rc["direction"][0],
            "support": int(np.count_nonzero(world.raw)),
            "kernel": {str(k): int(v) if isinstance(v, (int, np.integer)) else v for k, v in info.items()},
        })
    return {
        "challenge_id": challenge.get("challenge_id"), "mode": challenge.get("mode"), "n": world.n,
        "support_pattern_a": challenge["support_pattern_a"], "support_pattern_b": challenge["support_pattern_b"],
        "ports": {k: list(v) for k, v in ports.items()}, "trace": trace,
        "terminal": summarize(world.raw, world.clock_a), "python_interventions_after_t0": 0,
    }
