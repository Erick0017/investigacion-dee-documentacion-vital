#!/usr/bin/env python3
"""Prepared native action-consequence-policy-action apparatus with unbiased probes."""
from __future__ import annotations

import numpy as np

from rewrite_common import (
    A,
    ACTION0,
    ACTION1,
    B,
    NORMALIZER,
    PENALTY0,
    SENSOR,
    NativeWorld,
    add,
    pack,
    read,
    transform,
)


def _place(raw, clock, target, tick, direction, state, sreg):
    n = raw.shape[0]
    source = add(target, direction, -tick, n)
    if int(raw[source]):
        raise RuntimeError(f"preloaded overlap at {source}")
    raw[source] = pack(state, sreg, direction, 1)
    clock[source] = np.uint64(0)


def run_feedback_case(kernel, challenge):
    n = int(challenge["n"])
    bit = int(challenge["bit"])
    mode = challenge["mode"]
    q = tuple(int(x) % n for x in challenge["q"])
    permutation = tuple(challenge["permutation"])
    signs = tuple(challenge["signs"])
    a, b, sensor, normalizer, penalty, action0, action1 = (
        transform(v, permutation, signs) for v in (A, B, SENSOR, NORMALIZER, PENALTY0, ACTION0, ACTION1)
    )
    raw = np.zeros((n, n, n), np.uint64)
    clock = np.zeros_like(raw)
    if mode != "no_action":
        raw[q] = pack(1, 7, a, 1)
        clock[q] = np.uint64(11)
    t1 = add(q, a, 1, n)
    _place(raw, clock, t1, 1, sensor, 1001, 47)
    t2 = add(t1, action0, 1, n)
    consequence_normalizer = transform((0, -1, -1), permutation, signs) if mode == "wrong_consequence" else normalizer
    _place(raw, clock, t2, 2, consequence_normalizer, 1002, 53)
    if bit and mode != "no_penalty":
        _place(raw, clock, t2, 2, penalty, 1003, 59)
    target_a = add(t2, a, 1, n)
    target_b = add(t2, b, 1, n)
    _place(raw, clock, target_a, 3, sensor, 1004, 101)
    _place(raw, clock, target_b, 3, sensor, 1005, 103)
    world = NativeWorld(kernel, raw, clock, threads=1)
    world.tick()
    r1 = read(world.raw, t1)
    world.tick()
    r2 = read(world.raw, t2)
    world.tick()
    ra = read(world.raw, target_a)
    rb = read(world.raw, target_b)
    hit0 = ra is not None and tuple(ra["direction"]) == action0
    hit1 = rb is not None and tuple(rb["direction"]) == action1
    decoded = 0 if hit0 and not hit1 else 1 if hit1 and not hit0 else -1
    expected = bit if mode == "treatment" else None
    return {
        "challenge_id": challenge["challenge_id"],
        "bit": bit,
        "mode": mode,
        "n": n,
        "q": list(q),
        "permutation": list(permutation),
        "signs": list(signs),
        "records": {"action": r1, "updated_policy": r2, "probe0": ra, "probe1": rb},
        "action0_exact": r1 is not None and tuple(r1["direction"]) == action0,
        "policy_exact": r2 is not None and tuple(r2["direction"]) == (b if bit else a),
        "decoded": decoded,
        "expected": expected,
        "end_to_end_exact": decoded == expected if expected is not None else None,
        "python_interventions_after_t0": 0,
    }

