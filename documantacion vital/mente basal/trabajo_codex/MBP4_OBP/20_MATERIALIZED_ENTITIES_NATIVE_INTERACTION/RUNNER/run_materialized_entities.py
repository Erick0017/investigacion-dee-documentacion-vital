from __future__ import annotations

import csv
import hashlib
import json
from array import array
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import dee_thinking as dee


SECTION = Path(__file__).resolve().parents[1]
WORK = SECTION.parent
ROOT = WORK.parents[1]
PARENT_ZIP = ROOT / "MENTE_BASAL_4_ORGANIZACION_BASAL_PERSISTENTE_VALIDACION_RESULTADOS.zip"
PARENT_ZIP_SHA = "da23fcb06ac3c26ca16ab443762a49e38d2303c015a69d9d70afe23daafd0c4f"
FRESH = WORK / "12_CHECKPOINTS" / "OBP_FRESH_VALIDATED_T32.deetsnap"
FRESH_SHA = "cd09a4d94f72e00d9a5163c8dfd1d62e1528f1d146e4cb44ae23d261b3da09e6"

CAMPAIGN = "MBP4-MATERIALIZED-ENTITIES-NATIVE-INTERACTION"
N = 47
CAP = 19664

A = (1, 0, 0)
B = (0, 1, 0)
C = (0, 0, 1)
SENSOR_A = (-1, 0, 1)
ACTION_A = (0, 0, 1)
PROGRAM_ACTION1 = (-1, 1, 1)
NORMALIZER_A = (1, 0, -1)
SENSOR_B = (1, -1, 0)
ACTION_B = (1, 0, 0)
NORMALIZER_B = (-1, 1, 0)
SENSOR_C = (1, 0, -1)
ACTION_C = (1, 0, 0)
NORMALIZER_C = (-1, 0, 1)
PENALTY = (-1, 1, 0)
BRIDGE_B_TO_A = (1, -1, 0)
SENSOR_LOAD = 4000
NORMALIZER_LOAD = 3000
SOURCE_OFFSET = 8

TOTAL_TICKS = 0


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def digest_u64(values: Iterable[int]) -> str:
    return hashlib.sha256(array("Q", (int(x) for x in values)).tobytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def add(q: tuple[int, int, int], d: tuple[int, int, int], k: int = 1) -> tuple[int, int, int]:
    return tuple((q[i] + d[i] * k) % N for i in range(3))  # type: ignore[return-value]


def plus(q: tuple[int, int, int], delta: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple((q[i] + delta[i]) % N for i in range(3))  # type: ignore[return-value]


def ix(q: tuple[int, int, int]) -> int:
    return (q[0] * N + q[1]) * N + q[2]


def decode(raw: int, clock: int | None = None,
           site: tuple[int, int, int] | None = None) -> dict[str, Any] | None:
    if not raw:
        return None
    r = dee.decode_record(int(raw))
    out: dict[str, Any] = {
        "raw": int(raw),
        "state": int(r.state),
        "s_reg": int(r.s_reg),
        "direction": [int(r.dx), int(r.dy), int(r.dz)],
        "semantic": int(r.semantic),
    }
    if clock is not None:
        out["clock"] = int(clock)
    if site is not None:
        out["site"] = list(site)
    return out


def observation(runtime: Any, q: tuple[int, int, int]) -> dict[str, Any] | None:
    o = runtime.observe(dee.Coordinate(*q))
    return decode(int(o.raw), int(o.clock), q)


def put(raw: list[int], clocks: list[int], q: tuple[int, int, int], sreg: int,
        direction: tuple[int, int, int], semantic: int, label: str,
        state: int = 1) -> None:
    i = ix(q)
    if raw[i]:
        raise RuntimeError(f"preparation overlap {label!r} at {q}")
    raw[i] = int(dee.pack_record(int(state), int(sreg), *direction, int(semantic)))
    clocks[i] = 900000 + (sum(ord(c) for c in label) * 17) % 100000


def place_arrival(raw: list[int], clocks: list[int], target: tuple[int, int, int],
                  tick: int, direction: tuple[int, int, int], sreg: int,
                  semantic: int, label: str, state: int) -> tuple[int, int, int]:
    source = add(target, direction, -tick)
    put(raw, clocks, source, sreg, direction, semantic, label, state)
    return source


def runtime_from(raw: list[int], clocks: list[int], tick: int,
                 backend: str = "lazy") -> Any:
    r = dee.Runtime.import_research_state(N, int(tick), raw, clocks)
    choice = dee.Backend.DENSE_SEQUENTIAL if backend == "dense" else dee.Backend.LAZY
    r.execution_options = dee.TickOptions(choice, 1)
    return r


def load_parent(backend: str = "lazy") -> Any:
    if sha256(PARENT_ZIP) != PARENT_ZIP_SHA:
        raise RuntimeError("canonical MBP4 parent ZIP does not match the requested lineage")
    if sha256(FRESH) != FRESH_SHA:
        raise RuntimeError("fresh parent checkpoint hash mismatch")
    r = dee.Runtime.load_snapshot(str(FRESH))
    if int(r.dimension) != N or int(r.current_tick) != 32:
        raise RuntimeError("unexpected fresh parent dimension or tick")
    choice = dee.Backend.DENSE_SEQUENTIAL if backend == "dense" else dee.Backend.LAZY
    r.execution_options = dee.TickOptions(choice, 1)
    return r


def advance(runtime: Any, ticks: int) -> None:
    global TOTAL_TICKS
    ticks = int(ticks)
    if ticks < 0:
        raise ValueError("negative advance")
    runtime.advance(ticks)
    TOTAL_TICKS += ticks


def state_summary(runtime: Any) -> dict[str, Any]:
    raw = list(runtime.raw_copy())
    clocks = list(runtime.clock_copy())
    occupied = 0
    semantic_counts: dict[str, int] = {}
    for value in raw:
        if not value:
            continue
        occupied += 1
        rec = dee.decode_record(int(value))
        key = str(int(rec.semantic))
        semantic_counts[key] = semantic_counts.get(key, 0) + 1
    return {
        "tick": int(runtime.current_tick),
        "occupied": occupied,
        "semantic_counts": semantic_counts,
        "raw_sha256": digest_u64(raw),
        "clock_sha256": digest_u64(clocks),
    }


def save_snapshot(runtime: Any, name: str) -> dict[str, Any]:
    path = SECTION / "CHECKPOINTS" / name
    runtime.set_snapshot_metadata("mbp4.campaign", CAMPAIGN)
    runtime.set_snapshot_metadata("mbp4.section", "20_MATERIALIZED_ENTITIES_NATIVE_INTERACTION")
    runtime.save_snapshot(str(path))
    return {
        "path": str(path.relative_to(SECTION)).replace("\\", "/"),
        "tick": int(runtime.current_tick),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
    }


@dataclass(frozen=True)
class ProgramEvent:
    tick: int
    kind: str
    bit: int | None = None


@dataclass
class ProgramGeometry:
    name: str
    q: tuple[int, int, int]
    events: list[dict[str, Any]]
    installed: list[dict[str, Any]]

    def carrier_at(self, tick: int) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
        pos = self.q
        direction = A
        time = 0
        for row in self.events:
            event_tick = int(row["tick"])
            if tick < event_tick:
                return add(pos, direction, tick - time), direction
            if tick == event_tick:
                return tuple(row["action_pos"]), tuple(row["action_direction"])
            after_tick = int(row["after_tick"])
            if tick < after_tick:
                bridge = row.get("bridge")
                if bridge and tick == int(bridge["tick"]):
                    return tuple(bridge["pos"]), tuple(bridge["direction"])
            pos = tuple(row["after_pos"])
            direction = tuple(row["after_direction"])
            time = after_tick
        return add(pos, direction, tick - time), direction


def install_program(raw: list[int], clocks: list[int], name: str,
                    q: tuple[int, int, int], events: list[ProgramEvent],
                    state_base: int) -> ProgramGeometry:
    """Install the finite native actors at T0; there are no later host writes."""
    put(raw, clocks, q, 7, A, 1, f"{name}.carrier", state_base)
    pos = q
    direction = A
    time = 0
    current_bit = 0
    installed: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []

    def arrival(target: tuple[int, int, int], tick: int,
                vector: tuple[int, int, int], suffix: str, sreg: int) -> None:
        source = place_arrival(raw, clocks, target, tick, vector, sreg, 1,
                               f"{name}.{suffix}", state_base + len(installed) + 1)
        installed.append({
            "label": f"{name}.{suffix}", "source": list(source),
            "target": list(target), "tick": tick,
            "direction": list(vector), "s_reg": sreg,
        })

    for event_index, event in enumerate(sorted(events, key=lambda e: e.tick)):
        if event.tick <= time:
            raise ValueError(f"{name}: event {event.tick} does not follow settled tick {time}")
        target = add(pos, direction, event.tick - time)
        arrival(target, event.tick, SENSOR_A, f"event.{event_index}.sensor", 101 + event_index * 12)
        action_direction = PROGRAM_ACTION1 if current_bit else ACTION_A
        return_pos = add(target, action_direction)
        desired = current_bit if event.kind == "query" else int(event.bit)
        bridge_info = None
        if current_bit == 1 and desired == 0:
            arrival(return_pos, event.tick + 1, BRIDGE_B_TO_A,
                    f"event.{event_index}.bridge", 105 + event_index * 12)
            bridge_info = {"tick": event.tick + 1, "pos": list(return_pos),
                           "direction": list(ACTION_A)}
            final_pos = add(return_pos, ACTION_A)
            arrival(final_pos, event.tick + 2, NORMALIZER_A,
                    f"event.{event_index}.normalizer", 109 + event_index * 12)
            after_tick = event.tick + 2
            after_pos = final_pos
            after_direction = A
        else:
            arrival(return_pos, event.tick + 1, NORMALIZER_A,
                    f"event.{event_index}.normalizer", 107 + event_index * 12)
            if current_bit == 0 and desired == 1:
                arrival(return_pos, event.tick + 1, PENALTY,
                        f"event.{event_index}.penalty", 109 + event_index * 12)
            after_tick = event.tick + 1
            after_pos = return_pos
            after_direction = B if desired else A
        rows.append({
            "index": event_index, "tick": event.tick, "kind": event.kind,
            "requested_bit": event.bit, "before_bit": current_bit,
            "action_pos": list(target), "action_direction": list(action_direction),
            "bridge": bridge_info, "after_tick": after_tick,
            "after_pos": list(after_pos), "after_direction": list(after_direction),
            "after_bit": desired,
        })
        pos = after_pos
        direction = after_direction
        time = after_tick
        current_bit = desired
    return ProgramGeometry(name, q, rows, installed)


HISTORY_EVENTS: dict[str, list[ProgramEvent]] = {
    "H0": [ProgramEvent(4, "query"), ProgramEvent(12, "query"),
           ProgramEvent(20, "query"), ProgramEvent(40, "query")],
    "E_A": [ProgramEvent(4, "learn", 1), ProgramEvent(12, "query"),
            ProgramEvent(20, "query"), ProgramEvent(40, "query")],
    "E_B": [ProgramEvent(4, "learn", 0), ProgramEvent(12, "query"),
            ProgramEvent(20, "query"), ProgramEvent(40, "query")],
    "E_A_E_B": [ProgramEvent(4, "learn", 1), ProgramEvent(12, "learn", 0),
                 ProgramEvent(20, "query"), ProgramEvent(40, "query")],
    "E_B_E_A": [ProgramEvent(4, "learn", 0), ProgramEvent(12, "learn", 1),
                 ProgramEvent(20, "query"), ProgramEvent(40, "query")],
}


def mobile_trace(runtime: Any, geometry: ProgramGeometry, until: int,
                 selected: set[int] | None = None) -> list[dict[str, Any]]:
    selected = selected or set(range(1, until + 1))
    rows: list[dict[str, Any]] = []
    current = 0
    for rel in range(1, until + 1):
        advance(runtime, 1)
        current = rel
        if rel not in selected:
            continue
        site, expected_direction = geometry.carrier_at(rel)
        record = observation(runtime, site)
        rows.append({
            "relative_tick": rel,
            "absolute_tick": int(runtime.current_tick),
            "predicted_site": list(site),
            "unwrap_prediction": [geometry.q[i] + sum(
                int(row["after_direction"][i]) * max(0, rel - int(row["after_tick"]))
                for row in geometry.events[-1:]) for i in range(3)],
            "expected_direction": list(expected_direction),
            "record": record,
            "prediction_exact": record is not None and record["direction"] == list(expected_direction),
        })
    if current != until:
        raise RuntimeError("mobile observer did not reach requested horizon")
    return rows


def build_program_world(history: str, q: tuple[int, int, int], backend: str,
                        state_base: int) -> tuple[Any, ProgramGeometry]:
    parent = load_parent(backend)
    raw, clocks = list(parent.raw_copy()), list(parent.clock_copy())
    geometry = install_program(raw, clocks, f"B1.{history}", q,
                               HISTORY_EVENTS[history], state_base)
    return runtime_from(raw, clocks, int(parent.current_tick), backend), geometry


def run_history(history: str, q: tuple[int, int, int], backend: str,
                state_base: int, save_key_checkpoints: bool = False) -> dict[str, Any]:
    runtime, geometry = build_program_world(history, q, backend, state_base)
    checkpoints: list[dict[str, Any]] = []
    if save_key_checkpoints:
        checkpoints.append(save_snapshot(runtime, "B1_T0.deetsnap"))
    selected = {1, 3, 4, 5, 11, 12, 13, 14, 19, 20, 21, 22, 39, 40, 41, 42, 44}
    trace: list[dict[str, Any]] = []
    for rel in range(1, 45):
        advance(runtime, 1)
        if save_key_checkpoints and history == "E_A_E_B" and rel == 14:
            checkpoints.append(save_snapshot(runtime, "B1_AFTER_HISTORY.deetsnap"))
        if save_key_checkpoints and history == "E_A_E_B" and rel == 19:
            checkpoints.append(save_snapshot(runtime, "B1_BEFORE_COMMON_PROBE.deetsnap"))
        if rel in selected:
            site, direction = geometry.carrier_at(rel)
            rec = observation(runtime, site)
            trace.append({
                "relative_tick": rel, "absolute_tick": int(runtime.current_tick),
                "predicted_site": list(site), "expected_direction": list(direction),
                "record": rec,
                "prediction_exact": rec is not None and rec["direction"] == list(direction),
            })
    event20 = next(row for row in trace if row["relative_tick"] == 20)
    event40 = next(row for row in trace if row["relative_tick"] == 40)
    support_records = []
    raw = list(runtime.raw_copy())
    clocks = list(runtime.clock_copy())
    for installed in geometry.installed:
        source = tuple(installed["source"])
        support_records.append({"label": installed["label"],
                                "source": installed["source"],
                                "record_at_horizon": decode(raw[ix(source)], clocks[ix(source)], source)})
    return {
        "history": history,
        "backend": backend,
        "q": list(q),
        "host_writes_after_t0": 0,
        "events": geometry.events,
        "common_probe_t20": event20,
        "reexpression_t40": event40,
        "mobile_observer_trace": trace,
        "installed_actor_count": len(geometry.installed) + 1,
        "support_records_at_horizon": support_records,
        "checkpoints": checkpoints,
        "final": state_summary(runtime),
    }


@dataclass(frozen=True)
class LoopGeometry:
    q: tuple[int, int, int]
    policy: tuple[int, int, int]
    sensor: tuple[int, int, int]
    action: tuple[int, int, int]
    normalizer: tuple[int, int, int]
    sensor_source: tuple[int, int, int]
    normalizer_seed: tuple[int, int, int]
    normalizer_source: tuple[int, int, int]
    sensor_load: int
    normalizer_load: int

    def action_site(self, cycle: int) -> tuple[int, int, int]:
        return add(add(self.q, self.policy), self.sensor, cycle)

    def return_site(self, cycle: int) -> tuple[int, int, int]:
        return add(self.action_site(cycle), self.action)


def install_loop(raw: list[int], clocks: list[int], q: tuple[int, int, int],
                 policy: tuple[int, int, int], sensor: tuple[int, int, int],
                 action: tuple[int, int, int], normalizer: tuple[int, int, int],
                 sensor_load: int, normalizer_load: int, prefix: str) -> LoopGeometry:
    a0 = add(q, policy)
    r0 = add(a0, action)
    ss = add(a0, sensor, -1)
    seed = add(r0, normalizer, -2)
    ns = add(r0, normalizer, -SOURCE_OFFSET)
    put(raw, clocks, q, 7, policy, 1, f"{prefix}.plastic_policy")
    put(raw, clocks, ss, sensor_load, sensor, 4, f"{prefix}.persistent_input_support")
    put(raw, clocks, seed, normalizer_load, normalizer, 1, f"{prefix}.return_seed")
    put(raw, clocks, ns, normalizer_load, normalizer, 4, f"{prefix}.persistent_return_support")
    return LoopGeometry(q, policy, sensor, action, normalizer, ss, seed, ns,
                        sensor_load, normalizer_load)


def loop_phi(runtime: Any, g: LoopGeometry, cycle: int) -> dict[str, Any]:
    return {
        "cycle": cycle,
        "action_site": list(g.action_site(cycle)),
        "action_record": observation(runtime, g.action_site(cycle)),
        "return_site": list(g.return_site(cycle)),
        "return_record": observation(runtime, g.return_site(cycle)),
        "persistent_input_support": observation(runtime, g.sensor_source),
        "persistent_return_support": observation(runtime, g.normalizer_source),
    }


def validate_loop_entity(name: str, q: tuple[int, int, int], frame: str,
                         save_t0: str | None = None) -> dict[str, Any]:
    parent = load_parent("lazy")
    raw, clocks = list(parent.raw_copy()), list(parent.clock_copy())
    if frame == "A":
        vectors = (A, SENSOR_A, ACTION_A, NORMALIZER_A)
    elif frame == "C":
        vectors = (C, SENSOR_C, ACTION_C, NORMALIZER_C)
    else:
        raise ValueError(frame)
    g = install_loop(raw, clocks, q, *vectors, SENSOR_LOAD, NORMALIZER_LOAD, name)
    runtime = runtime_from(raw, clocks, int(parent.current_tick), "lazy")
    checkpoint = save_snapshot(runtime, save_t0) if save_t0 else None
    advance(runtime, 1)
    phi_action_1 = loop_phi(runtime, g, 0)
    advance(runtime, 1)
    phi_return_1 = loop_phi(runtime, g, 0)
    advance(runtime, 46)
    phi_action_2 = loop_phi(runtime, g, 1)
    advance(runtime, 1)
    phi_return_2 = loop_phi(runtime, g, 1)
    return {
        "entity": name, "q": list(q), "frame": frame,
        "roles": {
            "S": ["persistent_input_support", "persistent_return_support", "mobile_policy_lineage"],
            "P": ["mobile_policy_s_reg", "mobile_policy_direction", "phase_relation_to_supports"],
            "Gamma_in": "persistent_input_support -> mobile_policy",
            "Gamma_out": "mobile_policy -> action route outside support sites",
            "R": "toroidal return plus persistent input/return supports",
            "Phi": ["support records", "action record", "return record", "reexpression at next cycle"],
        },
        "checkpoint_t0": checkpoint,
        "phi": [phi_action_1, phi_return_1, phi_action_2, phi_return_2],
        "final": state_summary(runtime),
    }


def install_relay(raw: list[int], clocks: list[int], target: tuple[int, int, int],
                  tick: int, load: int, prefix: str) -> tuple[int, int, int]:
    return place_arrival(raw, clocks, target, tick, B, load, 1,
                         f"{prefix}.environmental_relay", 75000)


def mediated_world(offset: tuple[int, int, int], mode: str,
                   save_checkpoints: bool = False) -> tuple[dict[str, Any], Any]:
    parent = load_parent("lazy")
    raw, clocks = list(parent.raw_copy()), list(parent.clock_copy())
    t1 = plus((24, 20, 20), offset)
    t2 = add(t1, (1, 1, 0), 10)
    b1_return0 = add(t1, A, -18)
    q1 = add(add(b1_return0, A, -1), ACTION_A, -1)
    b2_return0 = add(t2, C, -28)
    q2 = add(add(b2_return0, C, -1), ACTION_C, -1)
    b1_load = SENSOR_LOAD if mode not in {"NO_B1_EFFECT", "NO_B1"} else 0
    b1_norm = NORMALIZER_LOAD if mode not in {"NO_B1_EFFECT", "NO_B1"} else 0
    g1 = None
    if mode != "NO_B1":
        g1 = install_loop(raw, clocks, q1, A, SENSOR_A, ACTION_A, NORMALIZER_A,
                          b1_load, b1_norm, f"MEDIATED.{mode}.B1")
    g2 = install_loop(raw, clocks, q2, C, SENSOR_C, ACTION_C, NORMALIZER_C,
                      2000, 3000, f"MEDIATED.{mode}.B2")
    relay_source = None
    if mode != "ROUTE_CUT":
        relay_source = install_relay(raw, clocks, t1, 20, 500, f"MEDIATED.{mode}")
    runtime = runtime_from(raw, clocks, int(parent.current_tick), "lazy")
    advance(runtime, 19)
    pre = {
        "B1": None if g1 is None else observation(runtime, add(t1, A, -1)),
        "relay": None if relay_source is None else observation(runtime, add(t1, B, -1)),
        "B2": observation(runtime, add(t2, C, -11)),
    }
    pre_cp = save_snapshot(runtime, "B1_B2_PRE_MEDIATED.deetsnap") if save_checkpoints else None
    advance(runtime, 1)
    m1 = observation(runtime, t1)
    advance(runtime, 9)
    before_b2 = observation(runtime, add(t2, (1, 1, 0), -1))
    advance(runtime, 1)
    at_b2 = observation(runtime, t2)
    post_cp = save_snapshot(runtime, "B1_B2_POST_MEDIATED.deetsnap") if save_checkpoints else None
    advance(runtime, 8)
    follow_site = add(t2, (1, 1, 1), 8)
    return ({
        "offset": list(offset), "mode": mode,
        "host_writes_after_t0": 0,
        "B1_q": None if g1 is None else list(q1), "B2_q": list(q2),
        "M1_target": list(t1), "B2_target": list(t2),
        "relay_source": None if relay_source is None else list(relay_source),
        "pre": pre, "M1_at_tick20": m1,
        "M1_before_B2": before_b2, "B2_interaction_tick30": at_b2,
        "descendant_followup": {"site": list(follow_site), "record": observation(runtime, follow_site)},
        "pre_checkpoint": pre_cp, "post_checkpoint": post_cp,
        "final": state_summary(runtime),
    }, runtime)


def direct_world(offset: tuple[int, int, int], mode: str,
                 save_checkpoints: bool = False) -> tuple[dict[str, Any], Any, bool]:
    parent = load_parent("lazy")
    raw, clocks = list(parent.raw_copy()), list(parent.clock_copy())
    q1 = plus((10, 10, 10), offset)
    q2_base = plus((28, 38, 11), offset)
    q2 = add(q2_base, (0, 0, 1)) if mode == "NO_CONTACT" else q2_base
    g1 = None if mode == "B2_ONLY" else install_loop(
        raw, clocks, q1, A, SENSOR_A, ACTION_A, NORMALIZER_A,
        SENSOR_LOAD, NORMALIZER_LOAD, f"DIRECT.{mode}.B1")
    g2 = None if mode == "B1_ONLY" else install_loop(
        raw, clocks, q2, B, SENSOR_B, ACTION_B, NORMALIZER_B,
        2000, 3000, f"DIRECT.{mode}.B2")
    runtime = runtime_from(raw, clocks, int(parent.current_tick), "lazy")
    target = plus((29, 10, 11), offset)
    advance(runtime, 19)
    pre = {
        "B1": None if g1 is None else observation(runtime, plus((28, 10, 11), offset)),
        "B2": None if g2 is None else observation(runtime, add(plus((29, 9, 11), offset), (0, 0, 1)) if mode == "NO_CONTACT" else plus((29, 9, 11), offset)),
    }
    pre_cp = save_snapshot(runtime, "B1_B2_PRE_CONTACT.deetsnap") if save_checkpoints else None
    advance(runtime, 1)
    at_contact = observation(runtime, target)
    post_cp = save_snapshot(runtime, "B1_B2_POST_CONTACT.deetsnap") if save_checkpoints else None
    descendant_direction = (1, 1, 0)
    descendant = at_contact is not None and at_contact["direction"] == list(descendant_direction)
    follow_rows = []
    current = 20
    for rel in (21, 28, 52):
        advance(runtime, rel - current)
        current = rel
        site = add(target, descendant_direction, rel - 20)
        follow_rows.append({"relative_tick": rel, "site": list(site),
                            "record": observation(runtime, site)})
    follow_cp = save_snapshot(runtime, "B12_FOLLOWUP.deetsnap") if save_checkpoints and descendant else None
    return ({
        "offset": list(offset), "mode": mode, "host_writes_after_t0": 0,
        "B1_q": None if g1 is None else list(q1),
        "B2_q": None if g2 is None else list(q2),
        "contact_target": list(target), "pre_contact": pre,
        "record_at_contact": at_contact,
        "candidate_descendant": descendant,
        "descendant_trace": follow_rows,
        "pre_checkpoint": pre_cp, "post_checkpoint": post_cp,
        "followup_checkpoint": follow_cp,
        "final": state_summary(runtime),
    }, runtime, descendant)


def main() -> None:
    for directory in ("CHECKPOINTS", "TELEMETRY", "RUNNER"):
        (SECTION / directory).mkdir(parents=True, exist_ok=True)

    config = {
        "schema": "mbp4.materialized-entities.experiment-config.v1",
        "campaign": CAMPAIGN,
        "frozen_utc": utc(),
        "parent_zip_sha256": PARENT_ZIP_SHA,
        "parent_checkpoint": str(FRESH.relative_to(WORK)).replace("\\", "/"),
        "parent_checkpoint_sha256": FRESH_SHA,
        "dimension": N,
        "backend_confirmatory": "lazy",
        "backend_reference": "dense_sequential",
        "host_writes_after_t0": 0,
        "B1_history_q": [6, 6, 6],
        "B1_fresh_holdouts": [[6, 6, 6], [16, 12, 18]],
        "history_panel": list(HISTORY_EVENTS),
        "common_probe_ticks": [20, 40],
        "materialized_entity_roles": ["S", "P", "Gamma_in", "Gamma_out", "R", "Phi"],
        "mediated_offsets": [[0, 0, 0], [5, 7, 9]],
        "direct_offsets": [[0, 0, 0], [5, 7, 9]],
        "direct_followup_ticks": [21, 28, 52],
        "autonomous_followup_ticks": 64,
        "scientist_mobile_observer": "passive predicted relational site plus full record/clock",
    }
    write_json(SECTION / "EXPERIMENT_CONFIG.json", config)

    checkpoints: list[dict[str, Any]] = []
    histories: dict[str, Any] = {}
    for index, history in enumerate(HISTORY_EVENTS):
        result = run_history(history, (6, 6, 6), "lazy", 40000 + index * 1000,
                             save_key_checkpoints=history == "E_A_E_B")
        histories[history] = result
        checkpoints.extend(result["checkpoints"])

    holdouts = [
        run_history("E_A_E_B", (6, 6, 6), "lazy", 50000, False),
        run_history("E_A_E_B", (16, 12, 18), "lazy", 51000, False),
    ]
    dense_reference = run_history("E_A_E_B", (6, 6, 6), "dense", 52000, False)
    backend_equivalence = {
        "lazy_final": histories["E_A_E_B"]["final"],
        "dense_final": dense_reference["final"],
        "raw_equal": histories["E_A_E_B"]["final"]["raw_sha256"] == dense_reference["final"]["raw_sha256"],
        "clock_equal": histories["E_A_E_B"]["final"]["clock_sha256"] == dense_reference["final"]["clock_sha256"],
    }
    write_json(SECTION / "TELEMETRY" / "B1_HISTORY_PANEL.json", histories)
    write_json(SECTION / "TELEMETRY" / "B1_FRESH_HOLDOUTS.json", holdouts)
    write_json(SECTION / "TELEMETRY" / "BACKEND_EQUIVALENCE.json", backend_equivalence)

    b1_identity = validate_loop_entity("B1", (10, 10, 10), "A")
    b2_identity = validate_loop_entity("B2", (28, 38, 11), "C", "B2_T0.deetsnap")
    if b2_identity["checkpoint_t0"]:
        checkpoints.append(b2_identity["checkpoint_t0"])
    write_json(SECTION / "TELEMETRY" / "B1_B2_IDENTITY_PANELS.json",
               {"B1": b1_identity, "B2": b2_identity})

    mediated: list[dict[str, Any]] = []
    mediated_contacts = 0
    for world_index, offset in enumerate(((0, 0, 0), (5, 7, 9))):
        for mode in ("TREATMENT", "NO_B1_EFFECT", "ROUTE_CUT"):
            row, _ = mediated_world(offset, mode,
                                    save_checkpoints=world_index == 0 and mode == "TREATMENT")
            mediated.append(row)
            checkpoints.extend(x for x in (row["pre_checkpoint"], row["post_checkpoint"]) if x)
            if mode == "TREATMENT" and row["B2_interaction_tick30"] is not None:
                mediated_contacts += 1
    write_json(SECTION / "TELEMETRY" / "MEDIATED_INTERACTION.json", mediated)

    direct: list[dict[str, Any]] = []
    direct_contacts = 0
    descendants = 0
    main_runtime = None
    for world_index, offset in enumerate(((0, 0, 0), (5, 7, 9))):
        for mode in ("TREATMENT", "B1_ONLY", "B2_ONLY", "NO_CONTACT"):
            row, runtime, descendant = direct_world(
                offset, mode, save_checkpoints=world_index == 0 and mode == "TREATMENT")
            direct.append(row)
            checkpoints.extend(x for x in (row["pre_checkpoint"], row["post_checkpoint"],
                                             row["followup_checkpoint"]) if x)
            if mode == "TREATMENT" and row["record_at_contact"] is not None:
                direct_contacts += 1
            if mode == "TREATMENT" and descendant:
                descendants += 1
            if world_index == 0 and mode == "TREATMENT":
                main_runtime = runtime
    write_json(SECTION / "TELEMETRY" / "DIRECT_CONTACT.json", direct)

    if main_runtime is None:
        raise RuntimeError("main direct-contact runtime was not produced")
    autonomous_start = state_summary(main_runtime)
    advance(main_runtime, int(config["autonomous_followup_ticks"]))
    autonomous_end = state_summary(main_runtime)
    main_cp = save_snapshot(main_runtime, "MAIN_FINAL.deetsnap")
    checkpoints.append(main_cp)
    write_json(SECTION / "TELEMETRY" / "AUTONOMOUS_SHORT_ARM.json", {
        "host_writes_after_t0": 0,
        "relative_ticks": config["autonomous_followup_ticks"],
        "start": autonomous_start,
        "end": autonomous_end,
    })

    events_count = sum(
        1 for history in histories.values()
        for event in history["events"] if event["kind"] == "learn"
    ) + sum(
        1 for history in holdouts
        for event in history["events"] if event["kind"] == "learn"
    )

    causal_rows: list[dict[str, Any]] = []
    for name, result in histories.items():
        for event in result["events"]:
            causal_rows.append({
                "tick": 32 + int(event["tick"]), "source": f"environment.{name}",
                "target": "B1", "event_type": event["kind"],
                "pre_state": event["before_bit"], "post_state": event["after_bit"],
                "history_branch": name, "position": json.dumps(event["action_pos"]),
            })
    for row in mediated:
        if row["mode"] == "TREATMENT":
            causal_rows.append({
                "tick": 52, "source": "B1", "target": "environment.M1",
                "event_type": "mediated_origin", "pre_state": "mobile lineage + relay",
                "post_state": json.dumps(row["M1_at_tick20"]),
                "history_branch": f"mediated.offset={row['offset']}",
                "position": json.dumps(row["M1_target"]),
            })
            causal_rows.append({
                "tick": 62, "source": "environment.M1", "target": "B2",
                "event_type": "mediated_contact", "pre_state": json.dumps(row["M1_before_B2"]),
                "post_state": json.dumps(row["B2_interaction_tick30"]),
                "history_branch": f"mediated.offset={row['offset']}",
                "position": json.dumps(row["B2_target"]),
            })
    for row in direct:
        if row["mode"] == "TREATMENT":
            causal_rows.append({
                "tick": 52, "source": "B1+B2", "target": "candidate.B12",
                "event_type": "direct_contact", "pre_state": json.dumps(row["pre_contact"]),
                "post_state": json.dumps(row["record_at_contact"]),
                "history_branch": f"direct.offset={row['offset']}",
                "position": json.dumps(row["contact_target"]),
            })
    with (SECTION / "CAUSAL_EVENTS.csv").open("w", newline="", encoding="utf-8") as f:
        columns = ["tick", "source", "target", "event_type", "pre_state", "post_state",
                   "history_branch", "position"]
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(causal_rows)

    summary = {
        "schema": "mbp4.materialized-entities.run-summary.v1",
        "campaign": CAMPAIGN,
        "parent_zip_sha256": PARENT_ZIP_SHA,
        "kernel_version": "DEE Universe v27 frozen",
        "runtime_version": str(getattr(dee, "__version__", "2.2.0")),
        "backend": {"confirmatory": "lazy", "reference": "dense_sequential"},
        "B1_configuration": b1_identity,
        "B2_configuration": b2_identity,
        "host_writes_after_t0": 0,
        "experiences_presented": events_count,
        "experiences_breakdown": {
            "primary_B1_history_panel": 6,
            "fresh_B1_holdouts": 4,
            "queries_not_counted_as_experiences": True,
        },
        "mediated_contacts_count": mediated_contacts,
        "direct_contacts_count": direct_contacts,
        "candidate_descendants": descendants,
        "checkpoints": checkpoints,
        "holdout_ids": ["B1_FRESH_1", "B1_FRESH_2", "B1_B2_MEDIATED_1",
                        "B1_B2_MEDIATED_2", "B1_B2_DIRECT_1", "B1_B2_DIRECT_2"],
        "total_ticks_executed_across_all_worlds": TOTAL_TICKS,
        "runtime_errors": [],
        "technical_hotfixes": [],
        "completion_status": "EXECUTION_COMPLETED",
        "main_final_checkpoint": main_cp,
        "created_utc": utc(),
    }
    write_json(SECTION / "RUN_SUMMARY.json", summary)


if __name__ == "__main__":
    main()
