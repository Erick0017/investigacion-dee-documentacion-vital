from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import dee_thinking as dee

Direction = tuple[int, int, int]
Coord = tuple[int, int, int]

A: Direction = (1, 0, 0)
B: Direction = (0, 1, 0)
SENSOR: Direction = (-1, 0, 1)
NORMALIZER: Direction = (1, 0, -1)
PENALTY0: Direction = (-1, 1, 0)
ACTION0: Direction = (0, 0, 1)
ACTION1: Direction = (-1, 1, 1)

RESET_P: Direction = (1, 0, 0)
RESET_S1: Direction = (-1, 1, 0)
RESET_S2: Direction = (-1, -1, 0)
RESET_N1: Direction = (1, 0, 1)
RESET_N2: Direction = (1, 0, -1)


def add(q: Coord, d: Direction, k: int, n: int) -> Coord:
    return tuple((q[i] + k * d[i]) % n for i in range(3))  # type: ignore[return-value]


def transform(v: Direction, permutation=(0, 1, 2), signs=(1, 1, 1)) -> Direction:
    return tuple(int(signs[i]) * int(v[int(permutation[i])]) for i in range(3))  # type: ignore[return-value]


def idx(q: Coord, n: int) -> int:
    return int(q[0]) * n * n + int(q[1]) * n + int(q[2])


def pack(state: int, sreg: int, direction: Direction, semantic: int = 1) -> int:
    return int(dee.pack_record(int(state), int(sreg), *map(int, direction), int(semantic)))


def decode(value: int) -> dict[str, Any] | None:
    if not value:
        return None
    rec = dee.decode_record(int(value))
    return {
        "raw": int(value),
        "state": int(rec.state),
        "s_reg": int(rec.s_reg),
        "direction": [int(rec.dx), int(rec.dy), int(rec.dz)],
        "semantic": int(rec.semantic),
    }


def observe(runtime: Any, q: Coord) -> dict[str, Any] | None:
    observation = runtime.observe(dee.Coordinate(*q))
    return decode(int(observation.raw))


def put(raw: list[int], clock: list[int], n: int, q: Coord, state: int, sreg: int,
        direction: Direction, semantic: int = 1, clock_value: int = 0,
        label: str = "") -> None:
    i = idx(q, n)
    if raw[i]:
        raise RuntimeError(f"preparation overlap {label!r} at {q}")
    raw[i] = pack(state, sreg, direction, semantic)
    clock[i] = int(clock_value) & ((1 << 64) - 1)


def place_arrival(raw: list[int], clock: list[int], n: int, target: Coord,
                  tick: int, direction: Direction, state: int, sreg: int,
                  semantic: int = 1, label: str = "") -> Coord:
    source = add(target, direction, -int(tick), n)
    put(raw, clock, n, source, state, sreg, direction, semantic,
        state * 1009 + tick, label)
    return source


def make_runtime(n: int, raw: list[int], clock: list[int], tick: int = 0,
                 backend: str = "dense") -> Any:
    runtime = dee.Runtime.import_research_state(n, tick, raw, clock)
    choice = dee.Backend.DENSE_SEQUENTIAL if backend == "dense" else dee.Backend.LAZY
    runtime.execution_options = dee.TickOptions(choice, 1)
    return runtime


@dataclass(frozen=True)
class ResetGeometry:
    q: Coord
    qp: Coord
    p: Direction
    source_sites: tuple[Coord, ...]


def install_reset(raw: list[int], clock: list[int], n: int, q: Coord,
                  permutation=(0, 1, 2), signs=(1, 1, 1),
                  mode: str = "treatment", state_base: int = 2000) -> ResetGeometry:
    p, s1, s2, n1, n2 = (transform(v, permutation, signs) for v in
                          (RESET_P, RESET_S1, RESET_S2, RESET_N1, RESET_N2))
    qp = add(q, p, 1, n)
    put(raw, clock, n, q, state_base - 1, 7, p, 1, 11, "reset.policy")
    specs = [
        (add(qp, s1, -1, n), s1, 11),
        (add(qp, s2, -1, n), s2, 13),
        (add(q, n1, -2, n), n1, 17),
        (add(q, n2, -2, n), n2, 19),
    ]
    sources: list[Coord] = []
    for i, (site, direction, sreg) in enumerate(specs):
        if mode == "missing_source" and i == 0:
            continue
        actual = transform((0, 1, 1), permutation, signs) if mode == "wrong_writer" and i == 0 else direction
        semantic = 1 if mode == "finite_sources" else 4
        put(raw, clock, n, site, state_base + i, sreg, actual, semantic,
            100000 + state_base + i, f"reset.source.{i}")
        sources.append(site)
    return ResetGeometry(q, qp, p, tuple(sources))


@dataclass(frozen=True)
class FeedbackGeometry:
    q: Coord
    bit: int
    mode: str
    frame: dict[str, list[int]]
    t1: Coord
    t2: Coord
    policy_targets: dict[int, list[Coord]]
    action_targets: dict[int, list[Coord]]
    return_targets: dict[int, list[Coord]]
    query_ticks: tuple[int, ...]
    installed: tuple[dict[str, Any], ...]


def install_feedback_loop(raw: list[int], clock: list[int], n: int, q: Coord,
                          bit: int, query_ticks: Iterable[int] = (8, 16, 24),
                          permutation=(0, 1, 2), signs=(1, 1, 1),
                          mode: str = "treatment", state_base: int = 10000) -> FeedbackGeometry:
    """Install a finite action/environment/return chain entirely at t0.

    The first R14 event writes A or B.  At every frozen query tick SENSOR turns
    that policy into ACTION0 or ACTION1.  At the following tick a prepared
    NORMALIZER maps the action back to A/B.  Thus the action selects the
    environmental branch whose consequence becomes the next policy.  Unused
    symmetric branch resources are also present and are checked for crosstalk.
    """
    query_ticks = tuple(int(x) for x in query_ticks)
    if not query_ticks or query_ticks[0] <= 2 or any(b <= a + 1 for a, b in zip(query_ticks, query_ticks[1:])):
        raise ValueError("query ticks must be increasing and leave a return step")
    a, b, sensor, normalizer, penalty, action0, action1 = (
        transform(v, permutation, signs) for v in
        (A, B, SENSOR, NORMALIZER, PENALTY0, ACTION0, ACTION1)
    )
    installed: list[dict[str, Any]] = []

    def arrival(target: Coord, tick: int, direction: Direction, state: int,
                sreg: int, label: str) -> None:
        if mode == "no_return" and label.startswith("return."):
            return
        if mode == "no_input" and label == "experience.sensor":
            return
        if mode == "no_internal_mediation" and label == "environment.normalizer":
            return
        if mode == "route_cut" and label == "return.0.1":
            direction = transform((1, 1, 0), permutation, signs)
        source = place_arrival(raw, clock, n, target, tick, direction, state,
                               sreg, 1, label)
        installed.append({"label": label, "source": list(source), "target": list(target),
                          "tick": tick, "direction": list(direction), "s_reg": sreg})

    if mode != "no_action":
        put(raw, clock, n, q, state_base, 7, a, 1, 11, "feedback.initial_policy")
    t1 = add(q, a, 1, n)
    arrival(t1, 1, sensor, state_base + 1, 47, "experience.sensor")
    t2 = add(t1, action0, 1, n)
    consequence = transform((0, -1, -1), permutation, signs) if mode == "no_environment_change" else normalizer
    arrival(t2, 2, consequence, state_base + 2, 53, "environment.normalizer")
    if bit and mode not in {"sham", "no_environment_change"}:
        arrival(t2, 2, penalty, state_base + 3, 59, "environment.penalty")

    policy_targets: dict[int, list[Coord]] = {0: [], 1: []}
    action_targets: dict[int, list[Coord]] = {0: [], 1: []}
    return_targets: dict[int, list[Coord]] = {0: [], 1: []}
    policy_pos = {0: t2, 1: t2}
    policy_time = 2
    directions = {0: a, 1: b}
    actions = {0: action0, 1: action1}
    for cycle, query_tick in enumerate(query_ticks):
        next_policy_pos: dict[int, Coord] = {}
        for branch in (0, 1):
            target = add(policy_pos[branch], directions[branch], query_tick - policy_time, n)
            policy_targets[branch].append(target)
            arrival(target, query_tick, sensor, state_base + 100 + cycle * 20 + branch,
                    101 + cycle * 8 + branch * 2, f"query.{cycle}.{branch}")
            action_targets[branch].append(target)
            ret = add(target, actions[branch], 1, n)
            return_targets[branch].append(ret)
            arrival(ret, query_tick + 1, normalizer,
                    state_base + 110 + cycle * 20 + branch,
                    131 + cycle * 8 + branch * 2, f"return.{cycle}.{branch}")
            next_policy_pos[branch] = ret
        policy_pos = next_policy_pos
        policy_time = query_tick + 1
    return FeedbackGeometry(q, int(bit), mode,
                            {"permutation": list(permutation), "signs": list(signs)},
                            t1, t2, policy_targets, action_targets, return_targets,
                            query_ticks, tuple(installed))


def reset_panel(runtime: Any, g: ResetGeometry, start_tick: int,
                horizon: int) -> dict[str, Any]:
    trace: list[dict[str, Any]] = []
    mismatches: list[int] = []
    for rel in range(1, horizon + 1):
        runtime.advance(1)
        target = g.qp if rel % 2 else g.q
        expected = tuple(-x for x in g.p) if rel % 2 else g.p
        rec = observe(runtime, target)
        ok = rec is not None and tuple(rec["direction"]) == expected
        if not ok:
            mismatches.append(rel)
        if rel <= 8 or rel in {16, 24, 32, 48, 64, horizon}:
            trace.append({"relative_tick": rel, "absolute_tick": start_tick + rel,
                          "target": list(target), "expected_direction": list(expected),
                          "record": rec, "ok": ok})
    raw = runtime.raw_copy()
    source_records = [{"site": list(site), "record": decode(int(raw[idx(site, int(runtime.dimension))]))}
                      for site in g.source_sites]
    return {"horizon": horizon, "all_exact": not mismatches,
            "mismatch_ticks": mismatches, "trace": trace,
            "source_records": source_records}


def feedback_panel(runtime: Any, g: FeedbackGeometry, start_tick: int,
                   final_relative_tick: int = 32) -> dict[str, Any]:
    checkpoints = {1, 2, *g.query_ticks, *(x + 1 for x in g.query_ticks), final_relative_tick}
    trace: list[dict[str, Any]] = []
    while int(runtime.current_tick) < start_tick + final_relative_tick:
        runtime.advance(1)
        rel = int(runtime.current_tick) - start_tick
        if rel in checkpoints:
            trace.append({
                "relative_tick": rel,
                "absolute_tick": int(runtime.current_tick),
                "t1": observe(runtime, g.t1),
                "t2": observe(runtime, g.t2),
                "policy0": [observe(runtime, q) for q in g.policy_targets[0]],
                "policy1": [observe(runtime, q) for q in g.policy_targets[1]],
                "return0": [observe(runtime, q) for q in g.return_targets[0]],
                "return1": [observe(runtime, q) for q in g.return_targets[1]],
                "metrics": {
                    "occupied": int(runtime.metrics().occupied),
                    "raw_support": int(runtime.metrics().raw_support),
                    "s_reg_sum": int(runtime.metrics().s_reg_sum),
                },
            })
    expected_branch = int(g.bit)
    expected_action = transform(ACTION1 if g.bit else ACTION0,
                                tuple(g.frame["permutation"]), tuple(g.frame["signs"]))
    cycle_results = []
    for i, tick in enumerate(g.query_ticks):
        row = next(x for x in trace if x["relative_tick"] == tick)
        rec = row[f"policy{expected_branch}"][i]
        cycle_results.append({"cycle": i, "tick": tick, "record": rec,
                              "expected_direction": list(expected_action),
                              "exact": rec is not None and tuple(rec["direction"]) == expected_action})
    return {"mode": g.mode, "bit": g.bit, "trace": trace,
            "cycle_results": cycle_results,
            "cycles_exact": sum(x["exact"] for x in cycle_results),
            "all_cycles_exact": all(x["exact"] for x in cycle_results),
            "python_interventions_after_t0": 0}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
