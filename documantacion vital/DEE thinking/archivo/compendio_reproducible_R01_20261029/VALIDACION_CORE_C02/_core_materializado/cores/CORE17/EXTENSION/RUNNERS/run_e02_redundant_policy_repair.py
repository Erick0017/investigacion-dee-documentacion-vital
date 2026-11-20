#!/usr/bin/env python3
"""Discovery: can a second learned native copy reconstruct a damaged policy?"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from core17e_common import PACKAGE_ROOT, ROOT, append_ndjson, audit_kernel, seal, verify_and_load_kernel, write_json

BASE = PACKAGE_ROOT / "RUNNERS" / "VENDORED_CORE16" / "BASELINE_RUNNERS"
sys.path.insert(0, str(BASE))
from core10_apparatus import (  # noqa: E402
    A, B, SENSOR, NORMALIZER, PENALTY0, ACTION1,
    NativeWorld, add, inject_arrival, neg, pack, read, summarize_world, transform,
)
import numpy as np  # noqa: E402


FRAMES = [
    ((0, 1, 2), (1, 1, 1)),
    ((1, 2, 0), (1, -1, 1)),
    ((2, 0, 1), (-1, 1, 1)),
    ((0, 2, 1), (-1, -1, 1)),
]


def run_case(kernel, seed: int, permutation, signs, mode: str, n: int = 37, d1: int = 5, d2: int = 7) -> dict:
    rng = np.random.default_rng(seed)
    raw = np.zeros((n, n, n), dtype=np.uint64)
    clock = np.zeros_like(raw)
    world = NativeWorld(kernel, raw, clock)
    a, b, sensor, normalizer, penalty0, action1 = (
        transform(v, permutation, signs) for v in (A, B, SENSOR, NORMALIZER, PENALTY0, ACTION1)
    )
    relay1 = transform((1, -1, 1), permutation, signs)
    relay2 = transform((-1, -1, 1), permutation, signs)
    route1 = tuple(relay1[i] + b[i] for i in range(3))
    route2 = tuple(relay2[i] + b[i] for i in range(3))
    receiver = tuple(int(x) for x in rng.integers(14, 23, size=3))
    source1 = add(receiver, route1, -d1, n)
    source2 = add(receiver, route2, -d2, n)
    if source1 == source2:
        raise RuntimeError("degenerate redundant sources")

    for j, source in enumerate((source1, source2)):
        initial = pack(610000 + seed + j, 7 + j, a, 1)
        world.raw_a[source] = initial; world.raw_b[source] = initial
        world.clock_a[source] = np.uint64(710000 + seed + j); world.clock_b[source] = world.clock_a[source]

    learned_tick = 2 * n
    launch1 = 3 * n
    arrival1 = launch1 + d1
    damage_tick = arrival1 + 1
    launch2 = 5 * n
    arrival2 = launch2 + d2
    query2 = arrival2 + n
    cut_offset = max(2, d2 // 2)
    events = []
    first_arrival = None
    damaged_coordinate = None
    backup_after_learning = None
    second_arrival = None

    for current in range(query2):
        next_tick = current + 1
        if next_tick == n:
            for j, source in enumerate((source1, source2)):
                inject_arrival(world, source, sensor, 47 + j, 720000 + seed + j, 730000 + seed + j)
        if next_tick == learned_tick:
            for j, source in enumerate((source1, source2)):
                inject_arrival(world, source, normalizer, 53 + j, 740000 + seed + j, 750000 + seed + j)
                if j == 0 or mode != "backup_untrained":
                    inject_arrival(world, source, penalty0, 59 + j, 760000 + seed + j, 770000 + seed + j)
        if next_tick == launch1:
            inject_arrival(world, source1, relay1, 61, 780000 + seed, 790000 + seed)
        if next_tick == arrival1:
            inject_arrival(world, receiver, neg(relay1), 71, 800000 + seed, 810000 + seed)
        if next_tick == launch2 and mode != "no_backup":
            inject_arrival(world, source2, relay2, 67, 820000 + seed, 830000 + seed)
        if next_tick == launch2 + cut_offset and mode in {"path_cut", "offpath_cut"}:
            target = add(source2, route2, cut_offset, n)
            if mode == "offpath_cut":
                target = add(target, transform((0, 0, 5), permutation, signs), 1, n)
            inject_arrival(world, target, neg(route2), 73, 840000 + seed, 850000 + seed)
        if next_tick == arrival2 and mode != "receiver_none":
            converter = neg(relay2) if mode != "wrong_receiver" else neg(b)
            inject_arrival(world, receiver, converter, 79, 860000 + seed, 870000 + seed)
        if next_tick == query2:
            inject_arrival(world, receiver, sensor, 101, 880000 + seed, 890000 + seed)

        world.tick()

        if next_tick == learned_tick:
            backup_after_learning = read(world.raw, source2)
            if mode == "backup_direction_reset" and backup_after_learning is not None:
                m = backup_after_learning
                replacement = pack(m["state"], m["sreg"], a, m["semantic"])
                world.raw_a[source2] = replacement; world.raw_b[source2] = replacement
            elif mode == "no_backup":
                world.raw_a[source2] = np.uint64(0); world.raw_b[source2] = np.uint64(0)
                world.clock_a[source2] = np.uint64(0); world.clock_b[source2] = np.uint64(0)
        if next_tick == arrival1:
            first_arrival = read(world.raw, receiver)
        if next_tick == damage_tick:
            # The transferred policy has advanced one native step along b.
            damaged_coordinate = add(receiver, b, 1, n)
            before = read(world.raw, damaged_coordinate)
            world.raw_a[damaged_coordinate] = np.uint64(0); world.raw_b[damaged_coordinate] = np.uint64(0)
            world.clock_a[damaged_coordinate] = np.uint64(0); world.clock_b[damaged_coordinate] = np.uint64(0)
            events.append({"tick": next_tick, "event": "policy_damage", "coordinate": damaged_coordinate, "before": before})
        if next_tick == arrival2:
            second_arrival = read(world.raw, receiver)

    query = read(world.raw, receiver)
    qdir = None if query is None else tuple(query["direction"])
    return {
        "seed": seed,
        "mode": mode,
        "n": n,
        "frame": {"permutation": list(permutation), "signs": list(signs)},
        "geometry": {"source1": source1, "source2": source2, "receiver": receiver, "route1": route1, "route2": route2, "d1": d1, "d2": d2},
        "ticks": {"learned": learned_tick, "launch1": launch1, "arrival1": arrival1, "damage": damage_tick, "launch2": launch2, "arrival2": arrival2, "query2": query2},
        "backup_after_learning": backup_after_learning,
        "first_arrival": first_arrival,
        "damaged_coordinate": damaged_coordinate,
        "events": events,
        "second_arrival": second_arrival,
        "query": query,
        "reconstructed_policy_at_arrival": second_arrival is not None and tuple(second_arrival["direction"]) == b,
        "fresh_function_after_reconstruction": qdir == action1,
        "source1_depleted": read(world.raw, source1) is None,
        "source2_depleted": read(world.raw, source2) is None,
        "final": summarize_world(world),
    }


def main() -> None:
    audit_kernel("CORE17E_REDUNDANT_POLICY_REPAIR_BEFORE")
    kernel, runtime = verify_and_load_kernel(1)
    modes = ["treatment", "backup_untrained", "backup_direction_reset", "no_backup", "path_cut", "offpath_cut", "wrong_receiver"]
    rows = []
    for i, (permutation, signs) in enumerate(FRAMES):
        for j, mode in enumerate(modes):
            rows.append(run_case(kernel, 1721000 + i * 1009 + j * 37, permutation, signs, mode))
    by_mode = {mode: [r for r in rows if r["mode"] == mode] for mode in modes}
    summary = {
        "cases": len(rows),
        "treatment_all": all(r["fresh_function_after_reconstruction"] for r in by_mode["treatment"]),
        "offpath_all": all(r["fresh_function_after_reconstruction"] for r in by_mode["offpath_cut"]),
        "untrained_none": not any(r["fresh_function_after_reconstruction"] for r in by_mode["backup_untrained"]),
        "direction_reset_none": not any(r["fresh_function_after_reconstruction"] for r in by_mode["backup_direction_reset"]),
        "no_backup_none": not any(r["fresh_function_after_reconstruction"] for r in by_mode["no_backup"]),
        "path_cut_none": not any(r["fresh_function_after_reconstruction"] for r in by_mode["path_cut"]),
        "wrong_receiver_none": not any(r["fresh_function_after_reconstruction"] for r in by_mode["wrong_receiver"]),
    }
    result = seal({
        "schema": "dee.v27.core17.extension.redundant_policy_repair.discovery.v1",
        "interpretation_guard": "This is carrier-mediated reconstruction from a redundant learned copy, not autonomous local regeneration or nonlocal transfer.",
        "rows": rows,
        "summary": summary,
        "runtime": runtime,
    })
    write_json(ROOT / "DISCOVERY" / "C17E02_REDUNDANT_POLICY_REPAIR.json", result)
    append_ndjson(ROOT / "QUESTION_TREE.ndjson", {
        "id": "C17EQ003", "parent_question": "C17EQ002", "parent_result_hash": result["content_sha256"],
        "question": "Does the carrier-mediated redundant policy reconstruction survive a preregistered fresh holdout?",
        "competing_hypotheses": ["causal redundant learned copy + intact route + converter is sufficient", "discovery geometry artifact"],
        "discriminating_next_action": "Freeze apparatus, thresholds and canaries before OS-entropy challenge generation.",
    })
    print({"hash": result["content_sha256"], **summary})


if __name__ == "__main__":
    main()
