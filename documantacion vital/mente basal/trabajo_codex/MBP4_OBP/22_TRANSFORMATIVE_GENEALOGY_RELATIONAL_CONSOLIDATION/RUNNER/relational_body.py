from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import dee_thinking as dee


N = 47
FRESH_SHA256 = "cd09a4d94f72e00d9a5163c8dfd1d62e1528f1d146e4cb44ae23d261b3da09e6"
PATTERN_A = ((-1, 0, 0), (-1, 1, 1), (0, 0, 1), (0, 1, 0))
PATTERN_B = ((0, -1, 0), (0, 0, -1), (1, -1, -1), (1, 0, 0))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def add(q: tuple[int, int, int], d: tuple[int, int, int], k: int = 1,
        n: int = N) -> tuple[int, int, int]:
    return tuple((q[i] + d[i] * k) % n for i in range(3))  # type: ignore[return-value]


def index(q: tuple[int, int, int], n: int = N) -> int:
    return (q[0] * n + q[1]) * n + q[2]


def decode_raw(value: int, clock: int | None = None,
               site: tuple[int, int, int] | None = None) -> dict[str, Any] | None:
    if not value:
        return None
    record = dee.decode_record(int(value))
    out: dict[str, Any] = {
        "raw": int(value), "state": int(record.state), "s_reg": int(record.s_reg),
        "direction": [int(record.dx), int(record.dy), int(record.dz)],
        "semantic": int(record.semantic),
    }
    if clock is not None:
        out["clock"] = int(clock)
    if site is not None:
        out["site"] = list(site)
    return out


def observe(runtime: Any, q: tuple[int, int, int]) -> dict[str, Any] | None:
    item = runtime.observe(dee.Coordinate(*q))
    return decode_raw(int(item.raw), int(item.clock), q)


class MutationAudit:
    def __init__(self) -> None:
        self.frozen = False
        self.pre_t0_writes = 0
        self.post_t0_writes = 0

    def write(self) -> None:
        if self.frozen:
            self.post_t0_writes += 1
            raise RuntimeError("host mutation attempted after relational T0")
        self.pre_t0_writes += 1


def put(raw: list[int], clocks: list[int], q: tuple[int, int, int], state: int,
        s_reg: int, direction: tuple[int, int, int], semantic: int, clock: int,
        label: str, audit: MutationAudit) -> None:
    audit.write()
    i = index(q)
    if raw[i]:
        raise RuntimeError(f"preparation overlap {label} at {q}: {decode_raw(raw[i], clocks[i], q)}")
    raw[i] = int(dee.pack_record(state, s_reg, *direction, semantic))
    clocks[i] = int(clock) & ((1 << 64) - 1)


def runtime_from(raw: list[int], clocks: list[int], tick: int,
                 backend: str = "lazy", n: int = N) -> Any:
    runtime = dee.Runtime.import_research_state(n, int(tick), raw, clocks)
    selected = dee.Backend.DENSE_SEQUENTIAL if backend == "dense" else dee.Backend.LAZY
    runtime.execution_options = dee.TickOptions(selected, 1)
    return runtime


def load_fresh(package_root: Path, backend: str = "lazy") -> Any:
    path = package_root / "12_CHECKPOINTS" / "OBP_FRESH_VALIDATED_T32.deetsnap"
    if sha256(path) != FRESH_SHA256:
        raise RuntimeError("OBP fresh checkpoint mismatch")
    runtime = dee.Runtime.load_snapshot(str(path))
    selected = dee.Backend.DENSE_SEQUENTIAL if backend == "dense" else dee.Backend.LAZY
    runtime.execution_options = dee.TickOptions(selected, 1)
    if int(runtime.dimension) != N or int(runtime.current_tick) != 32:
        raise RuntimeError("unexpected OBP fresh boundary")
    return runtime


@dataclass(frozen=True)
class BodyPorts:
    origin: tuple[int, int, int]
    a: tuple[int, int, int]
    b: tuple[int, int, int]
    comparator: tuple[int, int, int]
    reader_source: tuple[int, int, int]
    event_sources: tuple[tuple[int, int, int], ...]
    action_plus: tuple[int, int, int]
    return_plus: tuple[int, int, int]
    action_minus: tuple[int, int, int]
    return_minus: tuple[int, int, int]
    environmental_sources: tuple[tuple[int, int, int], ...]
    supports: tuple[tuple[int, int, int], ...]
    action_distance: int


def _install_event(raw: list[int], clocks: list[int], memory: tuple[int, int, int],
                   target_offset: tuple[int, int, int], direction: tuple[int, int, int],
                   when: str, state: int, audit: MutationAudit, label: str) -> tuple[int, int, int]:
    target = add(memory, target_offset)
    if when == "early":
        put(raw, clocks, target, state, 0, direction, 1, 17, label, audit)
        return target
    if when == "late":
        source = add(target, direction, -1)
        put(raw, clocks, source, 0, 0, direction, 1, 19, label, audit)
        return source
    raise ValueError(when)


def _install_turn_loop(raw: list[int], clocks: list[int], origin: tuple[int, int, int],
                       sign: int, distance: int, audit: MutationAudit, prefix: str,
                       include_action: bool, include_return: bool) -> tuple[
                           tuple[int, int, int], tuple[int, int, int], tuple[tuple[int, int, int], ...]
                       ]:
    # The renewed native reader emits its relational result from the comparator
    # along (axis_projection, +1, 0).  A preregistered environmental stream turns
    # that result into +z at action_site.  A second, spatially separate junction
    # at bend_site turns it back toward the organization.  This avoids colliding
    # the return with the continuing reader path.  No host choice is made after
    # T0.
    route = (sign, 1, 0)
    action_site = add(origin, route, distance)
    first_reader_arrival = 3 + distance
    action_turn = (-sign, -1, 1)
    action_source = add(action_site, action_turn, -first_reader_arrival)
    bend_site = add(action_site, (0, 0, 1), distance)
    bend_arrival = first_reader_arrival + distance
    return_direction = (-sign, -1, -1)
    bend_a = return_direction
    bend_b = (0, 0, -1)
    bend_source_a = add(bend_site, bend_a, -bend_arrival)
    bend_source_b = add(bend_site, bend_b, -bend_arrival)
    return_site = add(bend_site, return_direction, 1)
    installed: list[tuple[int, int, int]] = []
    if include_action:
        put(raw, clocks, action_source, 7100 + sign, 11, action_turn, 4, 31,
            f"{prefix}.action_turn_source", audit)
        put(raw, clocks, bend_source_a, 7200 + sign, 13, bend_a, 4, 41,
            f"{prefix}.bend_source_a", audit)
        put(raw, clocks, bend_source_b, 7300 + sign, 17, bend_b, 4, 47,
            f"{prefix}.bend_source_b", audit)
        installed.extend((action_source, bend_source_a, bend_source_b))
    if include_action and not include_return:
        blocker_steps = max(2, distance // 2)
        blocker = add(bend_site, return_direction, blocker_steps)
        put(raw, clocks, blocker, 7400 + sign, 0, (0, 0, 0), 4, 43,
            f"{prefix}.return_blocker", audit)
        installed.append(blocker)
    return action_site, return_site, tuple(installed)


def build_relational_body(package_root: Path, origin: tuple[int, int, int], history: str,
                          action_distance: int, mode: str = "FULL",
                          backend: str = "lazy") -> tuple[Any, BodyPorts, MutationAudit]:
    parent = load_fresh(package_root, backend)
    raw, clocks = list(parent.raw_copy()), list(parent.clock_copy())
    audit = MutationAudit()
    c = tuple(int(x) % N for x in origin)
    a, b = add(c, (-1, 0, 0)), add(c, (1, 0, 0))
    put(raw, clocks, a, 1000, 100, (0, 0, 0), 1, 260, "memory.a", audit)
    put(raw, clocks, b, 2000, 100, (0, 0, 0), 1, 260, "memory.b", audit)
    supports: list[tuple[int, int, int]] = []
    for i, offset in enumerate(PATTERN_A):
        q = add(a, offset)
        put(raw, clocks, q, 3000 + i, 0, (0, 0, 0), 4, 31 + i,
            f"support.a.{i}", audit)
        supports.append(q)
    for i, offset in enumerate(PATTERN_B):
        q = add(b, offset)
        put(raw, clocks, q, 4000 + i, 0, (0, 0, 0), 4, 41 + i,
            f"support.b.{i}", audit)
        supports.append(q)

    schedule = {
        "AB": ("early", "late"), "BA": ("late", "early"),
        "H0": (None, None), "SIMULTANEOUS": ("early", "early"),
        "SHAM": (None, None),
    }[history]
    events: list[tuple[int, int, int]] = []
    if schedule[0]:
        events.append(_install_event(raw, clocks, a, (0, -1, 0), (0, 0, -1),
                                     schedule[0], 5000, audit, "event.a"))
    if schedule[1]:
        events.append(_install_event(raw, clocks, b, (0, 1, 0), (0, 0, 1),
                                     schedule[1], 5001, audit, "event.b"))
    if history == "SHAM":
        put(raw, clocks, add(c, (0, 0, 6)), 5099, 0, (0, 0, 1), 1, 17,
            "event.sham", audit)

    reader_source = add(c, (0, -2, 0))
    if mode != "READ_CUT":
        put(raw, clocks, reader_source, 6000, 7, (0, 1, 0), 4, 23,
            "reader.source", audit)
    include_action = mode not in {"ACTION_CUT", "BARE"}
    include_return = mode not in {"RETURN_CUT", "BARE"}
    ap, rp, plus_sources = _install_turn_loop(
        raw, clocks, c, 1, action_distance, audit, "environment.plus",
        include_action, include_return)
    am, rm, minus_sources = _install_turn_loop(
        raw, clocks, c, -1, action_distance, audit, "environment.minus",
        include_action, include_return)
    audit.frozen = True
    runtime = runtime_from(raw, clocks, int(parent.current_tick), backend)
    ports = BodyPorts(
        c, a, b, c, reader_source, tuple(events), ap, rp, am, rm,
        plus_sources + minus_sources, tuple(supports), action_distance,
    )
    return runtime, ports, audit


def body_sample(runtime: Any, ports: BodyPorts, relative_tick: int) -> dict[str, Any]:
    a, b, comparator = (observe(runtime, q) for q in (ports.a, ports.b, ports.comparator))
    delta = None if a is None or b is None else int(a["s_reg"]) - int(b["s_reg"])
    action_plus, return_plus, action_minus, return_minus = (
        observe(runtime, q) for q in
        (ports.action_plus, ports.return_plus, ports.action_minus, ports.return_minus)
    )
    return {
        "relative_tick": int(relative_tick), "absolute_tick": int(runtime.current_tick),
        "a": a, "b": b, "delta": delta, "comparator": comparator,
        "axis_projection": None if comparator is None else int(comparator["direction"][0]),
        "action_plus": action_plus, "return_plus": return_plus,
        "action_minus": action_minus, "return_minus": return_minus,
    }


def trace_body(runtime: Any, ports: BodyPorts, horizon: int,
               sample_all: bool = True) -> list[dict[str, Any]]:
    rows = []
    for tick in range(1, int(horizon) + 1):
        runtime.advance(1)
        row = body_sample(runtime, ports, tick)
        if sample_all or tick <= 16 or tick in {32, 64, 128, 256, horizon}:
            rows.append(row)
    return rows


def occupied_sites(runtime: Any) -> list[tuple[int, int, int]]:
    raw = list(runtime.raw_copy())
    out = []
    for i, value in enumerate(raw):
        if not value:
            continue
        x, rem = divmod(i, N * N)
        y, z = divmod(rem, N)
        out.append((x, y, z))
    return out


def count_support(runtime: Any, sites: Iterable[tuple[int, int, int]]) -> int:
    return sum(observe(runtime, q) is not None for q in sites)
