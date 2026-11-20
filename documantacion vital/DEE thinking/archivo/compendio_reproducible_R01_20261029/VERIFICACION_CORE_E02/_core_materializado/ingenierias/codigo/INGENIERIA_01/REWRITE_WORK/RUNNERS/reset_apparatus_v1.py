#!/usr/bin/env python3
"""Frozen v1 apparatus for the native two-tick recycle law."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from rewrite_common import NativeWorld, add, pack, read, transform

P = (1, 0, 0)
S1 = (-1, 1, 0)
S2 = (-1, -1, 0)
N1 = (1, 0, 1)
N2 = (1, 0, -1)


def _source(raw, clock, pos, direction, state, sreg, semantic=4):
    if int(raw[pos]):
        raise RuntimeError(f"source overlap at {pos}")
    raw[pos] = pack(state, sreg, direction, semantic)
    clock[pos] = np.uint64(100000 + state)


def run_reset_case(kernel, challenge):
    n = int(challenge["n"])
    cycles = int(challenge["cycles"])
    mode = challenge["mode"]
    q = tuple(int(x) % n for x in challenge["q"])
    perm = tuple(challenge["permutation"])
    signs = tuple(challenge["signs"])
    p, s1, s2, n1, n2 = (transform(v, perm, signs) for v in (P, S1, S2, N1, N2))
    qp = add(q, p, 1, n)
    raw = np.zeros((n, n, n), np.uint64)
    clock = np.zeros_like(raw)
    raw[q] = pack(1, 7, p, 1)
    clock[q] = np.uint64(11)
    specs = [
        (add(qp, s1, -1, n), s1, 11),
        (add(qp, s2, -1, n), s2, 13),
        (add(q, n1, -2, n), n1, 17),
        (add(q, n2, -2, n), n2, 19),
    ]
    initial_sources = []
    for i, (pos, direction, sreg) in enumerate(specs):
        if mode == "missing_source" and i == 0:
            continue
        semantic = 1 if mode == "finite_sources" else 4
        actual_direction = transform((0, 1, 1), perm, signs) if mode == "wrong_writer" and i == 0 else direction
        _source(raw, clock, pos, actual_direction, 2000 + i, sreg, semantic)
        initial_sources.append((pos, int(raw[pos]), int(clock[pos])))
    world = NativeWorld(kernel, raw, clock, threads=1)
    first_failure_tick = None
    trace = []
    exact_half_cycles = 0
    trace_ticks = set(range(1, 9)) | {16, 32, 64, 128, 256, 512, 1024, 2 * cycles}
    for tick in range(1, 2 * cycles + 1):
        world.tick()
        target = qp if tick % 2 else q
        expected = tuple(-x for x in p) if tick % 2 else p
        record = read(world.raw, target)
        ok = record is not None and tuple(record["direction"]) == expected
        if ok:
            exact_half_cycles += 1
        elif first_failure_tick is None:
            first_failure_tick = tick
        if tick in trace_ticks:
            trace.append(
                {
                    "tick": tick,
                    "target": list(target),
                    "expected_direction": list(expected),
                    "record": record,
                    "ok": ok,
                    "support": int(np.count_nonzero(world.raw)),
                }
            )
    fixed = []
    for pos, raw0, clock0 in initial_sources:
        fixed.append(int(world.raw[pos]) == raw0 and int(world.clock_a[pos]) == clock0)
    return {
        "challenge_id": challenge["challenge_id"],
        "mode": mode,
        "n": n,
        "cycles_requested": cycles,
        "q": list(q),
        "permutation": list(perm),
        "signs": list(signs),
        "policy_direction": list(p),
        "first_failure_tick": first_failure_tick,
        "exact_half_cycles": exact_half_cycles,
        "complete_cycles": cycles if first_failure_tick is None else (first_failure_tick - 1) // 2,
        "all_exact": first_failure_tick is None,
        "persistent_sources_bit_exact": all(fixed) if mode == "treatment" else None,
        "terminal_support": int(np.count_nonzero(world.raw)),
        "trace": trace,
    }
