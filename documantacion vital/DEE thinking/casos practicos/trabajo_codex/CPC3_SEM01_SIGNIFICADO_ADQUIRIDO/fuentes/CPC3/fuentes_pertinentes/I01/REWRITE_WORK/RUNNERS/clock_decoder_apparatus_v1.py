#!/usr/bin/env python3
"""Native distributed clock-phase decoder with routed s_reg output."""
from __future__ import annotations

import itertools

import numpy as np

from rewrite_common import NativeWorld, add, pack, read, transform

TETRA = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1))
INPUT_DIRECTION = (-1, -1, 0)
ROUTED_DIRECTION = (-1, -1, -1)


def _centers(n, count, origin, permutation, signs):
    width = int(np.ceil(count ** (1 / 3)))
    while width ** 3 < count:
        width += 1
    offsets = [(4 * i, 4 * j, 4 * k) for i, j, k in itertools.product(range(width), repeat=3)]
    return [add(origin, transform(offset, permutation, signs), 1, n) for offset in offsets[:count]]


def run_decoder_case(kernel, challenge):
    n = int(challenge["n"])
    classes = int(challenge["classes"])
    input_class = int(challenge["input_class"])
    mode = challenge["mode"]
    origin = tuple(int(x) % n for x in challenge["origin"])
    permutation = tuple(challenge["permutation"])
    signs = tuple(challenge["signs"])
    centers = _centers(n, classes, origin, permutation, signs)
    tetra = [transform(v, permutation, signs) for v in TETRA]
    input_direction = transform(INPUT_DIRECTION, permutation, signs)
    routed_direction = transform(ROUTED_DIRECTION, permutation, signs)
    raw = np.zeros((n, n, n), np.uint64)
    clock = np.zeros_like(raw)
    for bias, q in enumerate(centers):
        if mode == "treatment":
            phase = (input_class - bias) % 195
        elif mode == "clock_equal":
            phase = input_class % 195
        elif mode == "destroyed":
            phase = 1
        elif mode == "sham_nonzero":
            phase = ((input_class - bias) % 194) + 1
        else:
            raise ValueError(mode)
        if int(raw[q]):
            raise RuntimeError("decoder center overlap")
        raw[q] = pack(1, 10, input_direction, 1)
        clock[q] = np.uint64(phase)
        for offset in tetra:
            p = add(q, offset, 1, n)
            if int(raw[p]):
                raise RuntimeError("decoder neighbor overlap")
            raw[p] = pack(1, 3, (0, 0, 0), 1)
            clock[p] = np.uint64(17)
    world = NativeWorld(kernel, raw, clock, threads=1)
    world.tick()
    gate_records = [read(world.raw, q) for q in centers]
    gate_directions_exact = all(record is not None and tuple(record["direction"]) == routed_direction for record in gate_records)
    gate_sregs = [record["sreg"] if record else None for record in gate_records]
    world.tick()
    output_positions = [add(q, routed_direction, 1, n) for q in centers]
    output_records = [read(world.raw, q) for q in output_positions]
    output_sregs = [record["sreg"] if record else None for record in output_records]
    active_gate = [i for i, value in enumerate(gate_sregs) if value == 11]
    active_output = [i for i, value in enumerate(output_sregs) if value == 11]
    expected = [input_class] if mode == "treatment" else None
    return {
        "challenge_id": challenge["challenge_id"],
        "mode": mode,
        "n": n,
        "classes": classes,
        "input_class": input_class,
        "origin": list(origin),
        "permutation": list(permutation),
        "signs": list(signs),
        "input_direction": list(input_direction),
        "routed_direction": list(routed_direction),
        "gate_directions_exact": gate_directions_exact,
        "active_gate_indices": active_gate,
        "active_output_indices": active_output,
        "gate_sreg_vector": gate_sregs,
        "output_sreg_vector": output_sregs,
        "gate_one_hot_exact": active_gate == expected if expected is not None else None,
        "routed_one_hot_exact": active_output == expected if expected is not None else None,
        "output_records_present": sum(record is not None for record in output_records),
    }

