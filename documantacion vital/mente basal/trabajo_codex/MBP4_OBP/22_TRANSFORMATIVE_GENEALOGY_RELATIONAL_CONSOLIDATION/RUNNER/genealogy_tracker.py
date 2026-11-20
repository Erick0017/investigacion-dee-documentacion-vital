from __future__ import annotations

import hashlib
from array import array
from pathlib import Path
from typing import Any, Iterable

import dee_thinking as dee


MOORE = tuple(
    (dx, dy, dz)
    for dx in (-1, 0, 1)
    for dy in (-1, 0, 1)
    for dz in (-1, 0, 1)
    if (dx, dy, dz) != (0, 0, 0)
)


def add(q: tuple[int, int, int], d: tuple[int, int, int], n: int) -> tuple[int, int, int]:
    return tuple((q[i] + d[i]) % n for i in range(3))  # type: ignore[return-value]


def index(q: tuple[int, int, int], n: int) -> int:
    return (q[0] * n + q[1]) * n + q[2]


def coordinate(i: int, n: int) -> tuple[int, int, int]:
    x, rem = divmod(i, n * n)
    y, z = divmod(rem, n)
    return x, y, z


def decode(value: int, clock: int | None = None,
           site: tuple[int, int, int] | None = None) -> dict[str, Any] | None:
    if not value:
        return None
    item = dee.decode_record(int(value))
    out: dict[str, Any] = {
        "raw": int(value), "state": int(item.state), "s_reg": int(item.s_reg),
        "direction": [int(item.dx), int(item.dy), int(item.dz)],
        "semantic": int(item.semantic),
    }
    if clock is not None:
        out["clock"] = int(clock)
    if site is not None:
        out["site"] = list(site)
    return out


def runtime_from(raw: list[int], clocks: list[int], tick: int, n: int,
                 backend: str = "lazy") -> Any:
    runtime = dee.Runtime.import_research_state(n, int(tick), raw, clocks)
    selected = dee.Backend.DENSE_SEQUENTIAL if backend == "dense" else dee.Backend.LAZY
    runtime.execution_options = dee.TickOptions(selected, 1)
    return runtime


def digest(values: Iterable[int]) -> str:
    return hashlib.sha256(array("Q", (int(x) for x in values)).tobytes()).hexdigest()


def incoming_sources(raw: list[int], target: tuple[int, int, int], n: int) -> list[dict[str, Any]]:
    rows = []
    for offset in MOORE:
        source = add(target, tuple(-v for v in offset), n)
        value = int(raw[index(source, n)])
        record = decode(value, site=source)
        if record is None:
            continue
        direction = tuple(int(x) for x in record["direction"])
        if direction == (0, 0, 0):
            continue
        if add(source, direction, n) == target:
            rows.append(record)
    return rows


def classify_branch(before_target: dict[str, Any] | None,
                    sources: list[dict[str, Any]]) -> str:
    if before_target is not None and int(before_target["semantic"]) == 4:
        return "semantic4_protection"
    if before_target is not None:
        return "occupied_destination_material_update_precedence"
    if len(sources) > 1:
        return "empty_destination_demux_multi_source"
    if len(sources) == 1:
        return "empty_destination_demux_single_source"
    return "empty_destination_nontransport_rule"


def analyze_transition(runtime: Any, target: tuple[int, int, int],
                       tracked_sources: Iterable[tuple[int, int, int]] = ()) -> tuple[dict[str, Any], Any]:
    n = int(runtime.dimension)
    tick_before = int(runtime.current_tick)
    before_raw, before_clock = list(runtime.raw_copy()), list(runtime.clock_copy())
    before_target = decode(before_raw[index(target, n)], before_clock[index(target, n)], target)
    sources = incoming_sources(before_raw, target, n)
    full = runtime_from(before_raw, before_clock, tick_before, n)
    full.advance(1)
    full_raw, full_clock = list(full.raw_copy()), list(full.clock_copy())
    after_target = decode(full_raw[index(target, n)], full_clock[index(target, n)], target)

    causal = []
    for source in sources:
        q = tuple(int(x) for x in source["site"])
        test_raw = before_raw.copy()
        test_raw[index(q, n)] = 0
        ablated = runtime_from(test_raw, before_clock, tick_before, n)
        ablated.advance(1)
        ablated_raw = list(ablated.raw_copy())
        causal.append({
            "site": list(q), "record": source,
            "target_changed_without_source": ablated_raw[index(target, n)] != full_raw[index(target, n)],
            "global_changed_sites_without_source": sum(a != b for a, b in zip(ablated_raw, full_raw)),
        })

    tracked_rows = []
    for q in tracked_sources:
        test_raw = before_raw.copy()
        if not test_raw[index(q, n)]:
            tracked_rows.append({"site": list(q), "present": False})
            continue
        test_raw[index(q, n)] = 0
        ablated = runtime_from(test_raw, before_clock, tick_before, n)
        ablated.advance(1)
        changed = [
            coordinate(i, n) for i, (a, b) in enumerate(zip(ablated.raw_copy(), full_raw)) if int(a) != int(b)
        ]
        tracked_rows.append({
            "site": list(q), "present": True, "changed_sites_count": len(changed),
            "changed_sites_sample": [list(x) for x in changed[:32]],
            "target_changed": target in changed,
        })

    row = {
        "tick_before": tick_before, "tick_after": tick_before + 1,
        "target": list(target), "branch": classify_branch(before_target, sources),
        "before_target": before_target, "after_target": after_target,
        "incoming_sources": sources, "source_ablation": causal,
        "tracked_source_ablation": tracked_rows,
        "full_after_raw_sha256": digest(full_raw),
        "full_after_clock_sha256": digest(full_clock),
    }
    return row, full


def trace_from_target(runtime: Any, first_target: tuple[int, int, int],
                      end_tick: int) -> dict[str, Any]:
    rows = []
    target = first_target
    while int(runtime.current_tick) < int(end_tick):
        sources = incoming_sources(list(runtime.raw_copy()), target, int(runtime.dimension))
        tracked = [tuple(int(x) for x in row["site"]) for row in sources]
        row, runtime = analyze_transition(runtime, target, tracked)
        rows.append(row)
        record = row["after_target"]
        if record is None:
            break
        direction = tuple(int(x) for x in record["direction"])
        if direction == (0, 0, 0):
            break
        target = add(target, direction, int(runtime.dimension))
    return {
        "start_target": list(first_target), "end_tick_requested": int(end_tick),
        "end_tick_reached": int(runtime.current_tick), "transitions": rows,
        "terminal_observed_site": rows[-1]["target"] if rows else None,
        "next_target_prediction": list(target),
        "terminal_target_prediction": list(target),
        "terminal_raw_sha256": digest(runtime.raw_copy()),
        "terminal_clock_sha256": digest(runtime.clock_copy()),
    }
