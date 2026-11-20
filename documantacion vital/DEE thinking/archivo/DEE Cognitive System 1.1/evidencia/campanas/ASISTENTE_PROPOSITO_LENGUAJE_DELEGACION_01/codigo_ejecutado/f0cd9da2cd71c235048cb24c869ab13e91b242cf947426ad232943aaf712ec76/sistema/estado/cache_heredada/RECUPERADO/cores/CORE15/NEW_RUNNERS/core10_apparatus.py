"""Reusable v27 apparatus for coupled policies, learned-policy transfer and joint scaffolds."""
from __future__ import annotations

import itertools
import hashlib
from typing import Iterable

import numpy as np

from core10_common import NativeWorld, fields, pack, unpack_scalar

A = (1, 0, 0)
B = (0, 1, 0)
SENSOR = (-1, 0, 1)
NORMALIZER = (1, 0, -1)
PENALTY0 = (-1, 1, 0)
ACTION0 = (0, 0, 1)
ACTION1 = (-1, 1, 1)


def add(q: tuple[int, int, int], d: tuple[int, int, int], k: int, n: int) -> tuple[int, int, int]:
    return tuple((q[i] + k * d[i]) % n for i in range(3))


def neg(d: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(-x for x in d)


def transform(v: tuple[int, int, int], permutation=(0, 1, 2), signs=(1, 1, 1)) -> tuple[int, int, int]:
    return tuple(signs[i] * v[permutation[i]] for i in range(3))


def read(raw: np.ndarray, q: tuple[int, int, int]):
    return unpack_scalar(raw[q]) if int(raw[q]) else None


def inject_arrival(world: NativeWorld, target, direction, sreg, state, clock, semantic=1) -> None:
    port = add(target, direction, -1, world.n)
    world.inject(port, pack(state, sreg, direction, semantic), clock)


def place_arrival(raw, clock, target, tick, direction, state, sreg, semantic=1):
    n = raw.shape[0]
    port = add(target, direction, -tick, n)
    if int(raw[port]):
        raise RuntimeError(f"initial trajectory collision at {port}")
    raw[port] = pack(state, sreg, direction, semantic)
    clock[port] = np.uint64(state * 1009 + tick)


def summarize_world(world: NativeWorld) -> dict:
    f = fields(world.raw)
    return {
        "support": int(np.count_nonzero(world.raw)),
        "sreg_total": int(f["sreg"].astype(np.uint64).sum()),
        "state_xor": int(np.bitwise_xor.reduce(f["state"].reshape(-1), initial=np.uint32(0))),
    }


def observer_snapshot(raw: np.ndarray, ports: dict[str, tuple[int, int, int]]) -> dict:
    """Neutral fingerprints used by the conditional dimensional-observer branch."""
    n = raw.shape[0]
    f = fields(raw)
    boundary_mask = np.zeros(raw.shape, dtype=bool)
    for axis in range(3):
        sl0 = [slice(None)] * 3; sl0[axis] = 0; boundary_mask[tuple(sl0)] = True
        sl1 = [slice(None)] * 3; sl1[axis] = n - 1; boundary_mask[tuple(sl1)] = True
    boundary = np.ascontiguousarray(raw[boundary_mask])
    rr = np.random.default_rng(17011 + n)
    random_coordinates = []
    while len(random_coordinates) < len(ports):
        q = tuple(int(x) for x in rr.integers(0, n, size=3))
        if q not in ports.values() and q not in random_coordinates:
            random_coordinates.append(q)
    projections = {}
    for axis in range(3):
        occupancy = np.count_nonzero(raw, axis=axis).astype(np.uint16)
        dirs = [np.sign(np.sum(f[key], axis=axis)).astype(np.int8) for key in ("dx", "dy", "dz")]
        projections[str(axis)] = {
            "occupancy_sha256": hashlib.sha256(np.ascontiguousarray(occupancy).tobytes()).hexdigest(),
            "direction_sha256": hashlib.sha256(b"".join(np.ascontiguousarray(x).tobytes() for x in dirs)).hexdigest(),
        }
    port_views = {}
    for name, q in ports.items():
        views = []
        for axis in range(3):
            index = tuple(q[i] for i in range(3) if i != axis)
            vector = [int(np.sign(np.sum(f[key], axis=axis)[index])) for key in ("dx", "dy", "dz")]
            views.append(vector)
        port_views[name] = views
    return {
        "full_raw_sha256": hashlib.sha256(np.ascontiguousarray(raw).tobytes()).hexdigest(),
        "bulk_inventory": summarize_raw(raw),
        "outer_boundary_nonzero": int(np.count_nonzero(boundary)),
        "outer_boundary_sha256": hashlib.sha256(boundary.tobytes()).hexdigest(),
        "projections": projections,
        "projected_direction_at_ports": port_views,
        "endpoint_records": {name: read(raw, q) for name, q in ports.items()},
        "equal_cell_random_observer": [{"coordinate": q, "raw": int(raw[q])} for q in random_coordinates],
    }


def summarize_raw(raw: np.ndarray) -> dict:
    f = fields(raw)
    return {
        "support": int(np.count_nonzero(raw)),
        "sreg_total": int(f["sreg"].astype(np.uint64).sum()),
        "semantic_counts": {str(k): int(np.sum(f["semantic"] == k)) for k in range(1, 16) if np.any(f["semantic"] == k)},
    }


def run_bidirectional_exchange(
    kernel,
    seed: int,
    n: int = 23,
    distance: int = 6,
    mode: str = "AB",
    permutation=(0, 1, 2),
    signs=(1, 1, 1),
    query_cycles: int = 1,
) -> dict:
    """Two independent lanes exchange policy carriers between two-port systems A and B."""
    if distance < 3 or 2 * distance + 12 >= n * 3:
        raise ValueError("distance outside audited local range")
    rng = np.random.default_rng(seed)
    raw = np.zeros((n, n, n), dtype=np.uint64)
    clock = np.zeros_like(raw)
    world = NativeWorld(kernel, raw, clock)
    a, b, sensor, action0, action1 = (transform(v, permutation, signs) for v in (A, B, SENSOR, ACTION0, ACTION1))
    t_ab = tuple(a[i] + b[i] for i in range(3))
    t_ba = neg(t_ab)
    zsep = transform((0, 0, 4), permutation, signs)
    origin = tuple(int(x) for x in (rng.integers(4, 7), rng.integers(4, 7), rng.integers(4, 7)))
    A_out = origin
    B_in = add(A_out, t_ab, distance, n)
    A_in = add(A_out, zsep, 1, n)
    B_out = add(B_in, zsep, 1, n)
    includes_A = mode not in {"B_only", "empty", "no_A"}
    includes_B = mode not in {"A_only", "empty", "no_B"}
    connected = mode != "no_connection"

    # At the first update each policy meets its local interface and enters a lane.
    if includes_A:
        place_arrival(raw, clock, A_out, 1, b, 1000 + seed, 7)
        if connected:
            place_arrival(raw, clock, A_out, 1, a, 1100 + seed, 11)
    if includes_B:
        place_arrival(raw, clock, B_out, 1, a, 2000 + seed, 13)
        if connected:
            place_arrival(raw, clock, B_out, 1, neg(t_ab), 2100 + seed, 17)
            place_arrival(raw, clock, B_out, 1, neg(a), 2200 + seed, 19)
    world = NativeWorld(kernel, raw, clock)
    initial = summarize_world(world)
    arrival_tick = 1 + distance
    query_tick = arrival_tick + query_cycles * n
    mid = max(2, distance // 2)
    trace = []
    endpoint_at_arrival = {}
    arrival_observers = {}
    total_genesis = 0
    boundary_history_digest = hashlib.sha256()
    boundary_history_nonzero = 0
    boundary_history_snapshots = 0
    for current in range(query_tick):
        next_tick = current + 1
        if next_tick == 1 + mid and mode in {"block_A_path", "block_B_path"}:
            lane_direction = t_ab if mode == "block_A_path" else t_ba
            junction = A_out if mode == "block_A_path" else B_out
            target = add(junction, lane_direction, mid, n)
            inject_arrival(world, target, neg(lane_direction), 23, 3000 + seed, 3100 + seed)
        if next_tick == 1 + mid and mode == "offpath_cut":
            target = add(add(A_out, t_ab, mid, n), transform((0, 0, 7), permutation, signs), 1, n)
            inject_arrival(world, target, neg(t_ab), 23, 3200 + seed, 3300 + seed)
        if next_tick == arrival_tick:
            if mode != "receiver_none":
                conv_B = neg(a) if mode != "wrong_receivers" else neg(b)
                inject_arrival(world, B_in, conv_B, 29, 4000 + seed, 4100 + seed)
                inject_arrival(world, A_in, t_ab, 31, 4200 + seed, 4300 + seed)
                inject_arrival(world, A_in, a, 37, 4400 + seed, 4500 + seed)
        if next_tick == query_tick:
            inject_arrival(world, A_in, sensor, 41, 5000 + seed, 5100 + seed)
            inject_arrival(world, B_in, sensor, 43, 5200 + seed, 5300 + seed)
        info = world.tick()
        total_genesis += int(info.get("genesis_count", 0))
        if next_tick in {1, 1 + mid, arrival_tick, query_tick}:
            trace.append({
                "tick": next_tick,
                "A_out": read(world.raw, A_out),
                "B_out": read(world.raw, B_out),
                "A_lane": read(world.raw, add(A_out, t_ab, min(mid, distance), n)),
                "B_lane": read(world.raw, add(B_out, t_ba, min(mid, distance), n)),
                "A_in": read(world.raw, A_in),
                "B_in": read(world.raw, B_in),
                "world": summarize_world(world),
            })
        if next_tick == arrival_tick:
            endpoint_at_arrival = {"A_in": read(world.raw, A_in), "B_in": read(world.raw, B_in)}
            arrival_observers = observer_snapshot(world.raw, {"A_in": A_in, "B_in": B_in})
            if mode == "reset_A_after_arrival":
                world.raw_a[A_in] = np.uint64(0); world.raw_b[A_in] = np.uint64(0)
                world.clock_a[A_in] = np.uint64(0); world.clock_b[A_in] = np.uint64(0)
            elif mode == "reset_B_after_arrival":
                world.raw_a[B_in] = np.uint64(0); world.raw_b[B_in] = np.uint64(0)
                world.clock_a[B_in] = np.uint64(0); world.clock_b[B_in] = np.uint64(0)
            elif mode == "reset_both_after_arrival":
                for q in (A_in, B_in):
                    world.raw_a[q] = np.uint64(0); world.raw_b[q] = np.uint64(0)
                    world.clock_a[q] = np.uint64(0); world.clock_b[q] = np.uint64(0)
            elif mode == "clear_lanes_after_arrival":
                for step in range(1, distance):
                    for q in (add(A_out, t_ab, step, n), add(B_out, t_ba, step, n)):
                        if q not in (A_in, B_in):
                            world.raw_a[q] = np.uint64(0); world.raw_b[q] = np.uint64(0)
                            world.clock_a[q] = np.uint64(0); world.clock_b[q] = np.uint64(0)
        if next_tick >= arrival_tick:
            mask = np.zeros(world.raw.shape, dtype=bool)
            for axis in range(3):
                low = [slice(None)] * 3; low[axis] = 0; mask[tuple(low)] = True
                high = [slice(None)] * 3; high[axis] = n - 1; mask[tuple(high)] = True
            boundary = np.ascontiguousarray(world.raw[mask])
            boundary_history_digest.update(boundary.tobytes())
            boundary_history_nonzero += int(np.count_nonzero(boundary))
            boundary_history_snapshots += 1
    A_query = read(world.raw, A_in)
    B_query = read(world.raw, B_in)
    direction_A = None if A_query is None else tuple(A_query["direction"])
    direction_B = None if B_query is None else tuple(B_query["direction"])
    return {
        "seed": seed,
        "n": n,
        "distance": distance,
        "mode": mode,
        "frame": {"permutation": list(permutation), "signs": list(signs)},
        "query_cycles": query_cycles,
        "ports": {"A_out": A_out, "A_in": A_in, "B_out": B_out, "B_in": B_in},
        "initial": initial,
        "arrival_tick": arrival_tick,
        "query_tick": query_tick,
        "endpoint_at_arrival": endpoint_at_arrival,
        "arrival_observers": arrival_observers,
        "outer_boundary_history": {"sha256": boundary_history_digest.hexdigest(), "snapshots": boundary_history_snapshots, "nonzero_cell_time_events": boundary_history_nonzero, "dense_raw_bits": boundary_history_snapshots * (6 * n * n - 12 * n + 8) * 64},
        "query": {"A": A_query, "B": B_query},
        "functional": {"A_received_B_policy": direction_A == action0, "B_received_A_policy": direction_B == action1},
        "source_depleted": {"A_out": read(world.raw, A_out) is None, "B_out": read(world.raw, B_out) is None},
        "trace": trace,
        "total_genesis": total_genesis,
        "final": summarize_world(world),
    }


def run_learned_policy_transfer(
    kernel,
    seed: int,
    n: int = 23,
    distance: int = 6,
    mode: str = "trained",
    permutation=(0, 1, 2),
    signs=(1, 1, 1),
) -> dict:
    """Acquire the CORE09 A->B policy by consequence, route it, then query B."""
    rng = np.random.default_rng(seed)
    raw = np.zeros((n, n, n), dtype=np.uint64)
    clock = np.zeros_like(raw)
    world = NativeWorld(kernel, raw, clock)
    a, b, sensor, normalizer, penalty0, action1 = (
        transform(v, permutation, signs) for v in (A, B, SENSOR, NORMALIZER, PENALTY0, ACTION1)
    )
    # The relay must be distinguishable from both possible policy directions;
    # otherwise the untrained a-policy and the relay demand the same arrival cell.
    # Its inverse receiver converter plus SENSOR is deliberately not ACTION1;
    # therefore a receiver without the transferred carrier cannot answer.
    relay = transform((1, -1, 1), permutation, signs)
    route = tuple(relay[i] + b[i] for i in range(3))
    source = tuple(int(x) for x in (rng.integers(5, 8), rng.integers(5, 8), rng.integers(5, 8)))
    receiver = add(source, route, distance, n)
    world.raw_a[source] = pack(6000 + seed, 7, a, 1)
    world.raw_b[source] = world.raw_a[source]
    world.clock_a[source] = np.uint64(7000 + seed)
    world.clock_b[source] = world.clock_a[source]
    initial = summarize_world(world)
    learned_tick = 2 * n
    launch_tick = 3 * n
    arrival_tick = launch_tick + distance
    query_tick = arrival_tick + n
    mid = max(2, distance // 2)
    memory_after_experience = None
    launch_record = None
    arrival_record = None
    source_after_launch = None
    corridor_trace = []
    total_genesis = 0
    for current in range(query_tick):
        next_tick = current + 1
        if next_tick == n:
            inject_arrival(world, source, sensor, 47, 8000 + seed, 8100 + seed)
        if next_tick == learned_tick:
            inject_arrival(world, source, normalizer, 53, 8200 + seed, 8300 + seed)
            if mode != "untrained":
                inject_arrival(world, source, penalty0, 59, 8400 + seed, 8500 + seed)
        if next_tick == launch_tick and mode != "no_relay":
            inject_arrival(world, source, relay, 61, 8600 + seed, 8700 + seed)
        if next_tick == launch_tick + mid and mode == "corridor_cut":
            target = add(source, route, mid, n)
            inject_arrival(world, target, neg(route), 67, 8800 + seed, 8900 + seed)
        if next_tick == launch_tick + mid and mode == "offpath_cut":
            target = add(add(source, route, mid, n), transform((0, 0, 7), permutation, signs), 1, n)
            inject_arrival(world, target, neg(route), 67, 9000 + seed, 9100 + seed)
        if next_tick == arrival_tick and mode != "receiver_none":
            converter = neg(relay) if mode != "wrong_receiver" else neg(b)
            inject_arrival(world, receiver, converter, 71, 9200 + seed, 9300 + seed)
        if next_tick == query_tick:
            inject_arrival(world, receiver, sensor, 101, 9400 + seed, 9500 + seed)
        info = world.tick()
        total_genesis += int(info.get("genesis_count", 0))
        if next_tick == learned_tick:
            memory_after_experience = read(world.raw, source)
            if mode == "memory_ablation":
                world.raw_a[source] = np.uint64(0); world.raw_b[source] = np.uint64(0)
                world.clock_a[source] = np.uint64(0); world.clock_b[source] = np.uint64(0)
            elif mode == "history_reset" and memory_after_experience is not None:
                m = memory_after_experience
                world.raw_a[source] = pack(m["state"], m["sreg"], a, m["semantic"]); world.raw_b[source] = world.raw_a[source]
            elif mode == "direction_ablation" and memory_after_experience is not None:
                m = memory_after_experience
                world.raw_a[source] = pack(m["state"], m["sreg"], (0, 0, 0), m["semantic"]); world.raw_b[source] = world.raw_a[source]
            elif mode == "sreg_nuisance" and memory_after_experience is not None:
                m = memory_after_experience
                world.raw_a[source] = pack(m["state"], min(19664, m["sreg"] + 97), tuple(m["direction"]), m["semantic"]); world.raw_b[source] = world.raw_a[source]
        if next_tick == launch_tick:
            launch_record = read(world.raw, source)
        if next_tick == launch_tick + 1:
            source_after_launch = read(world.raw, source)
        if launch_tick <= next_tick <= arrival_tick:
            expected = add(source, route, next_tick - launch_tick, n)
            rec = read(world.raw, expected)
            if rec is not None:
                corridor_trace.append({"tick": next_tick, "distance_from_source": next_tick - launch_tick, "coordinate": expected, "record": rec})
        if next_tick == arrival_tick:
            arrival_record = read(world.raw, receiver)
    query = read(world.raw, receiver)
    qdir = None if query is None else tuple(query["direction"])
    return {
        "seed": seed,
        "n": n,
        "distance": distance,
        "mode": mode,
        "frame": {"permutation": list(permutation), "signs": list(signs)},
        "source": source,
        "receiver": receiver,
        "initial": initial,
        "ticks": {"learned": learned_tick, "launch": launch_tick, "arrival": arrival_tick, "query": query_tick},
        "memory_after_experience": memory_after_experience,
        "launch_record": launch_record,
        "source_after_launch": source_after_launch,
        "arrival_record": arrival_record,
        "query_record": query,
        "functional_policy_reinstantiated": qdir == action1,
        "source_depleted_after_launch": source_after_launch is None,
        "corridor_trace": corridor_trace,
        "corridor_all_intermediate_ticks_observed": len({r["distance_from_source"] for r in corridor_trace}) >= distance,
        "total_genesis": total_genesis,
        "final": summarize_world(world),
    }


def _plane_corners(center, x_offset, n):
    return [((center[0] + x_offset) % n, (center[1] + dy) % n, (center[2] + dz) % n) for dy, dz in itertools.product((-1, 1), repeat=2)]


def run_joint_scaffold(kernel, seed: int, n: int = 23, mode: str = "AB", cycles: int = 3, axis: int = 0) -> dict:
    """Two damaged centers share the four-corner interface needed by both XNOR guards."""
    rng = np.random.default_rng(seed)
    raw = np.zeros((n, n, n), dtype=np.uint64)
    clock = np.zeros_like(raw)
    base = [n // 2] * 3
    center_A = tuple(base)
    base[axis] = (base[axis] + 2) % n
    center_B = tuple(base)

    def corners(center, side):
        out = []
        for u, v in itertools.product((-1, 1), repeat=2):
            q = list(center); q[axis] = (q[axis] + side) % n
            other = [i for i in range(3) if i != axis]
            q[other[0]] = (q[other[0]] + u) % n; q[other[1]] = (q[other[1]] + v) % n
            out.append(tuple(q))
        return out

    outer_A = corners(center_A, -1)
    shared = corners(center_A, +1)
    outer_B = corners(center_B, +1)
    A_owned = outer_A + shared[:2]
    B_owned = outer_B + shared[2:]
    selected: list[tuple[int, int, int]]
    if mode in {"AB", "offpath_cut"}:
        selected = outer_A + shared + outer_B
    elif mode == "A_only":
        selected = A_owned
    elif mode == "B_only":
        selected = B_owned
    elif mode == "empty":
        selected = []
    elif mode == "missing_shared_one":
        selected = outer_A + shared[1:] + outer_B
    elif mode == "full_A_only":
        selected = outer_A + shared
    elif mode == "full_B_only":
        selected = shared + outer_B
    elif mode == "shuffled_same_inventory":
        forbidden = set(outer_A + shared + outer_B + [center_A, center_B])
        candidates = [q for q in itertools.product(range(n), repeat=3) if q not in forbidden]
        chosen = rng.choice(len(candidates), size=12, replace=False)
        selected = [candidates[int(i)] for i in chosen]
    else:
        raise ValueError(mode)
    for index, q in enumerate(selected):
        raw[q] = pack(int(rng.integers(1, 2**32)), int(rng.integers(1, 19665)), (0, 0, 0), 4)
        clock[q] = np.uint64(rng.bit_generator.random_raw())
    if mode == "offpath_cut":
        # Deleting a matched irrelevant vacant cell changes nothing and is the positive intervention control.
        q = tuple((x + 6) % n for x in center_A)
        raw[q] = np.uint64(0); clock[q] = np.uint64(0)
    world = NativeWorld(kernel, raw, clock)
    scaffold_initial = {str(q): int(world.raw[q]) for q in selected}
    observations = []
    total_genesis = 0
    for cycle in range(cycles):
        world.raw_a[center_A] = np.uint64(0); world.raw_b[center_A] = np.uint64(0)
        world.raw_a[center_B] = np.uint64(0); world.raw_b[center_B] = np.uint64(0)
        world.clock_a[center_A] = np.uint64(0); world.clock_b[center_A] = np.uint64(0)
        world.clock_a[center_B] = np.uint64(0); world.clock_b[center_B] = np.uint64(0)
        before = summarize_world(world)
        info = world.tick(); total_genesis += int(info.get("genesis_count", 0))
        after_A = read(world.raw, center_A); after_B = read(world.raw, center_B)
        observations.append({"cycle": cycle, "before": before, "A_restored": after_A is not None, "B_restored": after_B is not None, "A_record": after_A, "B_record": after_B, "kernel": {str(k): int(v) if isinstance(v, (int, np.integer)) else v for k, v in info.items()}})
    scaffold_unchanged = all(int(world.raw[eval(q)]) == value for q, value in scaffold_initial.items())
    return {
        "seed": seed,
        "n": n,
        "axis": axis,
        "mode": mode,
        "cycles": cycles,
        "centers": {"A": center_A, "B": center_B},
        "ownership": {"A_cells": len(A_owned), "B_cells": len(B_owned), "shared_interface_cells_when_AB": len(shared)},
        "selected_support": len(selected),
        "cycle_results": observations,
        "A_recovery_rate": float(np.mean([r["A_restored"] for r in observations])),
        "B_recovery_rate": float(np.mean([r["B_restored"] for r in observations])),
        "joint_recovery_rate": float(np.mean([r["A_restored"] and r["B_restored"] for r in observations])),
        "scaffold_unchanged": scaffold_unchanged,
        "total_genesis": total_genesis,
        "final": summarize_world(world),
    }
