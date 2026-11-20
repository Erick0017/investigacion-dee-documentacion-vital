#!/usr/bin/env python3
"""Integrated write-then-read organization with spatially separated support roles."""
from __future__ import annotations

import itertools
import numpy as np

from ing02_common import NativeWorld, add, pack, read, summarize, transform


MEMORY_TETRA = ((-1, 0, 0), (0, 1, 0), (0, 0, 1), (-1, 1, 1))
COMPARATOR_ANCHORS = (
    ((1, 0, 0), 90),
    ((1, -1, 0), 10),
    ((1, -1, -1), 0),
    ((1, 0, 1), 0),
    ((1, 0, -1), 0),
    ((1, 1, 1), 0),
)
EXPERIENCE_OFFSET = (0, -1, 0)
EXPERIENCE_DIRECTION = (0, -1, 0)
READER_TRAVEL_DIRECTION = (0, -1, 0)
CONTROL_POLICY = (0, 1, 0)
TREATMENT_POLICY = (1, 1, 0)
LOCK_OFFSETS = ((1, -1, 0), (1, 0, -1), (1, -1, -1))


def _put(raw, clock, q, state, sreg, direction, semantic):
    if int(raw[q]):
        raise RuntimeError(f"apparatus overlap at {q}: {read(raw, q)}")
    raw[q] = pack(state, sreg, direction, semantic)
    clock[q] = np.uint64(10000 + state)


def construct(kernel, challenge):
    n = int(challenge.get("n", 23))
    origin = tuple(int(x) % n for x in challenge.get("origin", (n // 2,) * 3))
    permutation = tuple(challenge.get("permutation", (0, 1, 2)))
    signs = tuple(challenge.get("signs", (1, 1, 1)))
    mode = challenge.get("mode", "treatment")
    tf = lambda value: transform(value, permutation, signs)
    memory = origin
    comparator = add(memory, tf((1, 0, 0)), 1, n)
    raw = np.zeros((n, n, n), np.uint64)
    clock = np.zeros_like(raw)
    _put(raw, clock, memory, 100, 100, (0, 0, 0), 1)
    clock[memory] = np.uint64(260 if mode != "wrong_phase" else 261)
    for index, offset in enumerate(MEMORY_TETRA):
        if mode == "missing_memory_support" and index == 0:
            continue
        _put(raw, clock, add(memory, tf(offset), 1, n), 1000 + index, 0, (0, 0, 0), 4)
    for index, (offset, sreg) in enumerate(COMPARATOR_ANCHORS):
        if mode == "missing_comparator_support" and index == 2:
            continue
        actual_sreg = 100 if mode == "unbalanced_reference" and index == 0 else sreg
        _put(raw, clock, add(comparator, tf(offset), 1, n), 2000 + index, actual_sreg, (0, 0, 0), 4)

    experience_offset = tf(EXPERIENCE_OFFSET)
    experience_direction = tf(EXPERIENCE_DIRECTION)
    if mode not in {"no_experience", "destroyed_experience"}:
        direction = tf((0, 0, -1)) if mode == "wrong_experience_route" else experience_direction
        _put(raw, clock, add(memory, experience_offset, 1, n), 3000, 3, direction, 1)

    travel = tf(READER_TRAVEL_DIRECTION)
    reader_start = add(comparator, travel, -1, n)
    if mode != "no_reader":
        # state=0 directional raw routes into the empty comparator but does not
        # count as active support during the memory write (CORE01 E15).
        _put(raw, clock, reader_start, 0, 7, travel, 1)
    lock_targets = []
    lock_sources = []
    if challenge.get("consolidate", False) and mode != "no_consolidation":
        directions = [value for value in itertools.product((-1, 0, 1), repeat=3) if value != (0, 0, 0)]
        reserved = {memory, comparator, reader_start}
        for offset in LOCK_OFFSETS:
            target = add(memory, tf(offset), 1, n)
            if int(raw[target]):
                raise RuntimeError(f"lock target occupied: {target}")
            chosen = None
            for base_direction in directions:
                direction = tf(base_direction)
                source = add(target, direction, -1, n)
                if source in reserved or int(raw[source]) or source in lock_sources:
                    continue
                chosen = (source, direction)
                break
            if chosen is None:
                raise RuntimeError("no ghost route for consolidation lock")
            source, direction = chosen
            _put(raw, clock, source, 0, 0, direction, 1)
            reserved.add(target)
            reserved.add(source)
            lock_targets.append(target)
            lock_sources.append(source)
    ports = {
        "memory": memory,
        "comparator": comparator,
        "reader_start": reader_start,
        "control_output": add(comparator, tf(CONTROL_POLICY), 1, n),
        "treatment_output": add(comparator, tf(TREATMENT_POLICY), 1, n),
        "lock_targets": lock_targets,
        "lock_sources": lock_sources,
    }
    return NativeWorld(kernel, raw, clock), ports, {
        "control_policy": tf(CONTROL_POLICY),
        "treatment_policy": tf(TREATMENT_POLICY),
        "reader_travel": travel,
    }


def run_integrated_case_v2(kernel, challenge):
    world, ports, vectors = construct(kernel, challenge)
    horizon = int(challenge.get("horizon", 32))
    trace = []
    first_policy_tick = None
    policy_at_tick2 = None
    functional_output_at_tick3 = None
    for tick in range(1, horizon + 1):
        info = world.tick()
        memory = read(world.raw, ports["memory"])
        comparator = read(world.raw, ports["comparator"])
        direction = None if comparator is None else tuple(comparator["direction"])
        if direction in {vectors["control_policy"], vectors["treatment_policy"]} and first_policy_tick is None:
            if tick >= 2:
                first_policy_tick = tick
        if tick == 2:
            policy_at_tick2 = None if comparator is None else list(comparator["direction"])
        if tick == 3:
            control_record = read(world.raw, ports["control_output"])
            treatment_record = read(world.raw, ports["treatment_output"])
            control_hit = control_record is not None and tuple(control_record["direction"]) == vectors["control_policy"]
            treatment_hit = treatment_record is not None and tuple(treatment_record["direction"]) == vectors["treatment_policy"]
            functional_output_at_tick3 = {
                "control_record": control_record,
                "treatment_record": treatment_record,
                "control_hit": control_hit,
                "treatment_hit": treatment_hit,
                "decoded_policy": "control" if control_hit and not treatment_hit else "treatment" if treatment_hit and not control_hit else "ambiguous",
            }
        if tick <= 10 or tick in {16, 32, 64, 128, 256, 512, 1024, 2048, 4096}:
            trace.append(
                {
                    "tick": tick,
                    "memory": memory,
                    "comparator": comparator,
                    "control_output": read(world.raw, ports["control_output"]),
                    "treatment_output": read(world.raw, ports["treatment_output"]),
                    "support": int(np.count_nonzero(world.raw)),
                    "kernel": {str(k): int(v) if isinstance(v, (int, np.integer)) else v for k, v in info.items()},
                }
            )
    memory = read(world.raw, ports["memory"])
    comparator = read(world.raw, ports["comparator"])
    comparator_direction = None if comparator is None else tuple(comparator["direction"])
    expected_policy = vectors["treatment_policy"] if challenge.get("mode", "treatment") == "treatment" else None
    return {
        "challenge_id": challenge.get("challenge_id", "discovery"),
        "mode": challenge.get("mode", "treatment"),
        "n": world.n,
        "origin": list(ports["memory"]),
        "permutation": list(challenge.get("permutation", (0, 1, 2))),
        "signs": list(challenge.get("signs", (1, 1, 1))),
        "horizon": horizon,
        "vectors": {key: list(value) for key, value in vectors.items()},
        "ports": {
            key: [list(item) for item in value] if key in {"lock_targets", "lock_sources"} else list(value)
            for key, value in ports.items()
        },
        "first_policy_tick": first_policy_tick,
        "terminal_memory": memory,
        "terminal_comparator": comparator,
        "terminal_policy_direction": None if comparator_direction is None else list(comparator_direction),
        "policy_at_tick2": policy_at_tick2,
        "treatment_policy_exact_at_tick2": tuple(policy_at_tick2) == expected_policy if expected_policy is not None and policy_at_tick2 is not None else None,
        "functional_output_at_tick3": functional_output_at_tick3,
        "semantic4_count": summarize(world.raw)["semantic_counts"].get("4", 0),
        "terminal": summarize(world.raw, world.clock_a),
        "trace": trace,
        "python_interventions_after_t0": 0,
    }
