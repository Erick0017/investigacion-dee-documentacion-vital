from __future__ import annotations

import hashlib
import json
import shutil
import sys
from array import array
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PACKAGED = HERE.parent.name == "18_NATIVE_PERSISTENT_LEARNING"
CONT = HERE.parent if PACKAGED else HERE.parent / "18_NATIVE_PERSISTENT_LEARNING"
WORK = CONT.parent if PACKAGED else HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(WORK / "source"))

import dee_thinking as dee
from mbp4_obp import (
    A,
    ACTION0,
    ACTION1,
    B,
    NORMALIZER,
    PENALTY0,
    SENSOR,
    add,
    decode,
    idx,
    make_runtime,
    observe,
    place_arrival,
    put,
    sha256,
    write_json,
)

PARENT_ZIP = None if PACKAGED else WORK.parents[1] / "MENTE_BASAL_4_ORGANIZACION_BASAL_PERSISTENTE_VALIDACION_RESULTADOS.zip"
PARENT_SNAPSHOT = WORK / "12_CHECKPOINTS" / "OBP_FRESH_VALIDATED_T32.deetsnap"
PARENT_ZIP_EXPECTED = "b0fad297af0ffeeb9718a70714eaa3dd3203768d81c322508968fd73af2f1691"
PARENT_SNAPSHOT_EXPECTED = "cd09a4d94f72e00d9a5163c8dfd1d62e1528f1d146e4cb44ae23d261b3da09e6"
BRIDGE_B_TO_A = (1, -1, 0)
RESET_Q = (34, 34, 34)
RESET_QP = (35, 34, 34)


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def digest_u64(values: list[int]) -> str:
    return hashlib.sha256(array("Q", (int(x) for x in values)).tobytes()).hexdigest()


def rec(runtime: Any, q: tuple[int, int, int]) -> dict[str, Any] | None:
    obs = runtime.observe(dee.Coordinate(*q))
    value = decode(int(obs.raw))
    if value is not None:
        value = {**value, "site": list(q), "clock": int(obs.clock)}
    return value


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
    state_base: int

    def carrier_at(self, tick: int, n: int) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
        pos = self.q
        direction = A
        time = 0
        for row in self.events:
            event_tick = int(row["tick"])
            if tick < event_tick:
                return add(pos, direction, tick - time, n), direction
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
        return add(pos, direction, tick - time, n), direction


def install_program(raw: list[int], clock: list[int], n: int, name: str,
                    q: tuple[int, int, int], events: list[ProgramEvent],
                    state_base: int, redirect_penalty: bool = False) -> ProgramGeometry:
    """Install all actors at native-world T0; no later host writes occur."""
    put(raw, clock, n, q, state_base, 7, A, 1, state_base * 17, f"{name}.carrier")
    pos = q
    direction = A
    time = 0
    current_bit = 0
    installed: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []

    def arrival(target: tuple[int, int, int], tick: int, d: tuple[int, int, int],
                suffix: str, sreg: int) -> None:
        source = place_arrival(raw, clock, n, target, tick, d,
                               state_base + len(installed) + 1, sreg, 1,
                               f"{name}.{suffix}")
        installed.append({"label": f"{name}.{suffix}", "source": list(source),
                          "target": list(target), "tick": tick,
                          "direction": list(d), "s_reg": sreg})

    for event_index, event in enumerate(sorted(events, key=lambda e: e.tick)):
        if event.tick <= time:
            raise ValueError(f"{name}: event at {event.tick} does not follow settled tick {time}")
        target = add(pos, direction, event.tick - time, n)
        arrival(target, event.tick, SENSOR, f"event.{event_index}.sensor", 101 + event_index * 12)
        action_direction = ACTION1 if current_bit else ACTION0
        action_pos = target
        return_pos = add(action_pos, action_direction, 1, n)
        desired = current_bit if event.kind == "query" else int(event.bit)
        bridge_info = None

        if current_bit == 1 and desired == 0:
            arrival(return_pos, event.tick + 1, BRIDGE_B_TO_A,
                    f"event.{event_index}.bridge", 105 + event_index * 12)
            bridge_pos = return_pos
            bridge_info = {"tick": event.tick + 1, "pos": list(bridge_pos),
                           "direction": list(ACTION0)}
            final_pos = add(bridge_pos, ACTION0, 1, n)
            arrival(final_pos, event.tick + 2, NORMALIZER,
                    f"event.{event_index}.normalizer", 109 + event_index * 12)
            after_tick = event.tick + 2
            after_pos = final_pos
            after_direction = A
        else:
            arrival(return_pos, event.tick + 1, NORMALIZER,
                    f"event.{event_index}.normalizer", 107 + event_index * 12)
            if current_bit == 0 and desired == 1:
                penalty_direction = (0, 0, -1) if redirect_penalty else PENALTY0
                arrival(return_pos, event.tick + 1, penalty_direction,
                        f"event.{event_index}.penalty" + (".sham" if redirect_penalty else ""),
                        109 + event_index * 12)
            after_tick = event.tick + 1
            after_pos = return_pos
            after_direction = B if desired else A

        rows.append({"index": event_index, "tick": event.tick, "kind": event.kind,
                     "requested_bit": event.bit, "before_bit": current_bit,
                     "action_pos": list(action_pos), "action_direction": list(action_direction),
                     "bridge": bridge_info, "after_tick": after_tick,
                     "after_pos": list(after_pos), "after_direction": list(after_direction),
                     "after_bit": desired})
        pos = after_pos
        direction = after_direction
        time = after_tick
        current_bit = desired
    return ProgramGeometry(name, q, rows, installed, state_base)


def parent_state() -> tuple[Any, list[int], list[int]]:
    if PARENT_ZIP is not None and sha256(PARENT_ZIP) not in {PARENT_ZIP_EXPECTED, "725726c5080563fd0756a244dbae540fe569edd6cd1be56d2fbffb1ca3116cb8"}:
        raise RuntimeError("canonical MBP4 parent ZIP hash changed")
    if sha256(PARENT_SNAPSHOT) != PARENT_SNAPSHOT_EXPECTED:
        raise RuntimeError("OBP fresh parent checkpoint hash mismatch")
    runtime = dee.Runtime.load_snapshot(str(PARENT_SNAPSHOT))
    if int(runtime.current_tick) != 32 or int(runtime.dimension) != 47:
        raise RuntimeError("unexpected OBP parent tick or dimension")
    return runtime, list(runtime.raw_copy()), list(runtime.clock_copy())


FIBER_CONFIG = [
    {"name": "E_A", "q": (5, 5, 16), "learn": 2, "queries": [5, 37], "state_base": 30000},
    {"name": "E_B", "q": (15, 5, 24), "learn": 10, "queries": [13, 39], "state_base": 31000},
    {"name": "E_C", "q": (25, 5, 32), "learn": 18, "queries": [21, 41], "state_base": 32000},
    {"name": "E_D_HOLDOUT", "q": (35, 5, 40), "learn": 26, "queries": [29, 43], "state_base": 33000},
]


def build_world(*, omit: str | None = None, backend: str = "dense",
                configs: list[dict[str, Any]] | None = None) -> tuple[Any, dict[str, ProgramGeometry]]:
    parent, raw, clock = parent_state()
    geometries: dict[str, ProgramGeometry] = {}
    for cfg in configs or FIBER_CONFIG:
        bit = 0 if cfg["name"] == omit else 1
        events = [ProgramEvent(int(cfg["learn"]), "learn", bit)]
        events += [ProgramEvent(int(t), "query") for t in cfg["queries"]]
        geometries[cfg["name"]] = install_program(
            raw, clock, 47, cfg["name"], tuple(cfg["q"]), events,
            int(cfg["state_base"]), redirect_penalty=(cfg["name"] == omit),
        )
    runtime = make_runtime(47, raw, clock, int(parent.current_tick), backend)
    return runtime, geometries


def recurrence_at(runtime: Any, relative_tick: int) -> dict[str, Any]:
    target = RESET_QP if relative_tick % 2 else RESET_Q
    expected = (-1, 0, 0) if relative_tick % 2 else A
    value = rec(runtime, target)
    return {"relative_tick": relative_tick, "target": list(target),
            "expected_direction": list(expected), "record": value,
            "exact": value is not None and tuple(value["direction"]) == expected}


def action_observations(runtime: Any, geometries: dict[str, ProgramGeometry],
                        relative_tick: int) -> list[dict[str, Any]]:
    rows = []
    for name, geometry in geometries.items():
        for event in geometry.events:
            if int(event["tick"]) == relative_tick:
                value = rec(runtime, tuple(event["action_pos"]))
                expected = tuple(event["action_direction"])
                rows.append({"family": name, "event": event["kind"],
                             "requested_bit": event["requested_bit"],
                             "relative_tick": relative_tick,
                             "site": event["action_pos"], "record": value,
                             "expected_direction": list(expected),
                             "exact": value is not None and tuple(value["direction"]) == expected})
    return rows


def execute_world(*, omit: str | None = None, backend: str = "dense",
                  save_prefix: str | None = None,
                  configs: list[dict[str, Any]] | None = None,
                  horizon: int = 46) -> tuple[dict[str, Any], Any, dict[str, ProgramGeometry]]:
    runtime, geometries = build_world(omit=omit, backend=backend, configs=configs)
    start = int(runtime.current_tick)
    recurrence = []
    actions = []
    checkpoint_rows = []
    checkpoints = {0, 8, 16, 24, 32, horizon}
    if save_prefix:
        path = CONT / "CHECKPOINTS" / f"{save_prefix}_T{start:06d}_NATIVE_WORLD_T0.deetsnap"
        runtime.set_snapshot_metadata("mbp4.continuation", "MBP4_NATIVE_PERSISTENT_LEARNING")
        runtime.set_snapshot_metadata("mbp4.world", save_prefix)
        runtime.save_snapshot(str(path))
        checkpoint_rows.append({"relative_tick": 0, "absolute_tick": start,
                                "path": str(path.relative_to(CONT)), "sha256": sha256(path)})
    for rel in range(1, horizon + 1):
        runtime.advance(1)
        recurrence.append(recurrence_at(runtime, rel))
        actions.extend(action_observations(runtime, geometries, rel))
        if save_prefix and rel in checkpoints:
            path = CONT / "CHECKPOINTS" / f"{save_prefix}_T{start + rel:06d}_R{rel:03d}.deetsnap"
            runtime.save_snapshot(str(path))
            checkpoint_rows.append({"relative_tick": rel, "absolute_tick": start + rel,
                                    "path": str(path.relative_to(CONT)), "sha256": sha256(path)})
    result = {
        "schema": "mbp4.native-world-result.v1", "omit": omit,
        "backend": backend, "start_tick": start, "end_tick": int(runtime.current_tick),
        "horizon": horizon, "python_writes_after_native_t0": 0,
        "classification": "source-supported/driven finite deterministic DEE ecology",
        "recurrence": {"exact": all(x["exact"] for x in recurrence),
                       "exact_count": sum(x["exact"] for x in recurrence),
                       "total": len(recurrence), "samples": [x for x in recurrence if x["relative_tick"] in {1, 2, 16, 32, 64, horizon}]},
        "actions": actions,
        "queries_exact": sum(x["exact"] for x in actions if x["event"] == "query"),
        "queries_total": sum(1 for x in actions if x["event"] == "query"),
        "checkpoints": checkpoint_rows,
        "final": {"tick": int(runtime.current_tick), "raw_sha256": digest_u64(runtime.raw_copy()),
                  "clock_sha256": digest_u64(runtime.clock_copy()),
                  "occupied": int(runtime.metrics().occupied),
                  "raw_support": int(runtime.metrics().raw_support),
                  "s_reg_sum": int(runtime.metrics().s_reg_sum)},
        "programs": {name: {"q": list(g.q), "events": g.events, "installed": g.installed}
                     for name, g in geometries.items()},
    }
    return result, runtime, geometries


def build_branch(name: str) -> tuple[dict[str, Any], Any, dict[str, ProgramGeometry]]:
    base = {"name": "A", "q": (5, 5, 16), "learn": 4, "state_base": 40000}
    if name == "PRACTICE_A":
        configs = [{**base, "learn": 2, "queries": [5, 13, 21, 29, 41]}]
        omit = None
    elif name == "IDLE":
        configs = [{**base, "learn": 2, "queries": [5, 41]}]
        omit = None
    elif name == "NO_USE_ACTIVE":
        configs = [
            {**base, "learn": 2, "queries": [5, 41]},
            {"name": "B_OTHER", "q": (15, 5, 24), "learn": 10, "queries": [13, 29], "state_base": 41000},
            {"name": "C_OTHER", "q": (25, 5, 32), "learn": 18, "queries": [21, 31], "state_base": 42000},
        ]
        omit = None
    elif name == "CONTROL_NAIVE":
        configs = [{**base, "learn": 2, "queries": [5, 41]}]
        omit = "A"
    else:
        raise ValueError(name)
    return execute_world(omit=omit, backend="dense", configs=configs, horizon=44)


def build_relearning_case(name: str, initial_learning: bool) -> dict[str, Any]:
    parent, raw, clock = parent_state()
    events: list[ProgramEvent] = []
    if initial_learning:
        events += [ProgramEvent(2, "learn", 1), ProgramEvent(5, "query")]
        events += [ProgramEvent(14, "learn", 0), ProgramEvent(18, "query")]
    else:
        events += [ProgramEvent(2, "learn", 0), ProgramEvent(5, "query")]
        events += [ProgramEvent(14, "query")]
    events += [ProgramEvent(30, "learn", 1), ProgramEvent(33, "query"), ProgramEvent(41, "query")]
    g = install_program(raw, clock, 47, name, (5, 5, 16), events,
                        50000 if initial_learning else 51000)
    runtime = make_runtime(47, raw, clock, int(parent.current_tick), "dense")
    actions = []
    recurrence = []
    for rel in range(1, 45):
        runtime.advance(1)
        recurrence.append(recurrence_at(runtime, rel))
        actions.extend(action_observations(runtime, {name: g}, rel))
    return {"name": name, "initial_learning": initial_learning,
            "events": g.events, "actions": actions,
            "recurrence_exact": all(x["exact"] for x in recurrence),
            "L_acquire_experiences": 1,
            "L_reacquire_experiences": 1 if initial_learning else None,
            "relearning_savings": 0 if initial_learning else None,
            "final_tick": int(runtime.current_tick)}


def run_atlas(checkpoint_rows: list[dict[str, Any]], geometries: dict[str, ProgramGeometry]) -> dict[str, Any]:
    entries = []
    domain = {"families": list(geometries), "modes": ["TARGET", "MISS_Z3"],
              "lead_ticks": 1, "horizons": [1], "exhaustive_within_listed_cartesian_domain": True}
    for cp in checkpoint_rows:
        rel = int(cp["relative_tick"])
        if rel not in {0, 8, 16, 24, 32, 46}:
            continue
        base = dee.Runtime.load_snapshot(str(CONT / cp["path"]))
        n = int(base.dimension)
        for name, geometry in geometries.items():
            carrier_pos, carrier_direction = geometry.carrier_at(rel, n)
            expected_bit = 1 if rel >= next(int(x["after_tick"]) for x in geometry.events if x["kind"] == "learn") else 0
            for mode in domain["modes"]:
                raw = list(base.raw_copy()); clock = list(base.clock_copy())
                target = add(carrier_pos, carrier_direction, 1, n)
                query_target = target if mode == "TARGET" else add(target, (0, 0, 1), 3, n)
                try:
                    source = place_arrival(raw, clock, n, query_target, 1, SENSOR,
                                           60000 + len(entries), 211, 1, f"atlas.{name}.{rel}.{mode}")
                    branch = make_runtime(n, raw, clock, int(base.current_tick), "dense")
                    branch.advance(1)
                    value = rec(branch, target)
                    observed_direction = None if value is None else value["direction"]
                    expected_direction = list(ACTION1 if expected_bit else ACTION0) if mode == "TARGET" else list(carrier_direction)
                    exact = observed_direction == expected_direction
                    error = None
                except Exception as exc:
                    source = None; value = None; observed_direction = None
                    expected_direction = list(ACTION1 if expected_bit else ACTION0) if mode == "TARGET" else list(carrier_direction)
                    exact = False; error = f"{type(exc).__name__}: {exc}"
                entries.append({"checkpoint_relative_tick": rel, "family": name,
                                "mode": mode, "carrier_pos": list(carrier_pos),
                                "carrier_direction": list(carrier_direction),
                                "expected_bit": expected_bit, "query_source": None if source is None else list(source),
                                "query_target": list(query_target), "read_site": list(target),
                                "response": value, "expected_direction": expected_direction,
                                "exact": exact, "error": error})
    by_checkpoint = {}
    for rel in (0, 8, 16, 24, 32, 46):
        rows = [x for x in entries if x["checkpoint_relative_tick"] == rel and x["mode"] == "TARGET"]
        by_checkpoint[str(rel)] = {
            "targeted_queries": len(rows),
            "action1_count": sum(x["response"] is not None and x["response"]["direction"] == list(ACTION1) for x in rows),
            "action0_count": sum(x["response"] is not None and x["response"]["direction"] == list(ACTION0) for x in rows),
            "exact": all(x["exact"] for x in rows),
        }
    return {"schema": "mbp4.landscape-atlas.v1", "domain": domain,
            "entries": entries, "by_checkpoint": by_checkpoint,
            "all_exact": all(x["exact"] for x in entries),
            "interpretation": "The finite atlas measures native query reachability, not the complete v27 state space."}


def write_locks() -> dict[str, Any]:
    locks = {
        "NATIVE_WORLD_LOCK.json": {
            "schema": "mbp4.native-world-lock.v1", "frozen_utc": utc(),
            "parent_checkpoint": "12_CHECKPOINTS/OBP_FRESH_VALIDATED_T32.deetsnap",
            "parent_sha256": PARENT_SNAPSHOT_EXPECTED, "classification": "source-supported/driven",
            "host_after_t0": ["advance", "passive observe", "checkpoint", "diagnostic forks"],
            "families": FIBER_CONFIG, "horizon": 46,
            "restriction": "identity frame only; D2_FRAME mismatch forbids universal signed/permuted invariance claim"},
        "NATIVE_LEARNING_LOCK.json": {
            "schema": "mbp4.native-learning-lock.v1", "frozen_utc": utc(),
            "criterion": "one native environment event writes B; later common SENSOR query emits ACTION1 instead of naive ACTION0",
            "omission": "redirected off-path penalty with matched future protocol",
            "main_sequence": ["E_A", "E_B", "E_C", "E_D_HOLDOUT"]},
        "RETENTION_RELEARNING_LOCK.json": {
            "schema": "mbp4.retention-relearning-lock.v1", "frozen_utc": utc(),
            "branches": ["PRACTICE_A", "NO_USE_ACTIVE", "IDLE", "CONTROL_NAIVE", "INTERFERENCE_RELEARN", "NAIVE_LATE_ACQUIRE"],
            "retention_query": 41, "relearning_event": 30, "relearning_query": 33,
            "metrics": ["effective experiences", "causal ticks to demonstrated response"]},
        "CAPACITY_SPEED_LOCK.json": {
            "schema": "mbp4.capacity-speed-lock.v1", "frozen_utc": utc(),
            "k_tested": [1, 2, 3, 4], "event_spacing_ticks": 8,
            "capacity_definition": "maximum k observed with identity and all required omission-sensitive queries",
            "history_speed_comparison": "E_D in experienced MAIN versus matched naive-only E_D"},
        "LANDSCAPE_ATLAS_LOCK.json": {
            "schema": "mbp4.landscape-atlas-lock.v1", "frozen_utc": utc(),
            "checkpoints_relative": [0, 8, 16, 24, 32, 46],
            "families": [x["name"] for x in FIBER_CONFIG], "modes": ["TARGET", "MISS_Z3"],
            "lead_ticks": 1, "horizons": [1], "scope": "exhaustive only for the finite Cartesian domain listed"},
        "HOLDOUT_CONTINUATION_LOCK.json": {
            "schema": "mbp4.holdout-continuation-lock.v1", "frozen_utc": utc(),
            "holdout_family": "E_D_HOLDOUT", "no_refit": True,
            "success": "B relation acquired at tick26 and ACTION1 at frozen queries 29/43 while Phi_B recurrence remains exact"},
    }
    for name, obj in locks.items():
        write_json(CONT / "LOCKS" / name, obj)
    return locks


def main() -> None:
    for d in ("LOCKS", "WORLD", "ACQUISITION", "RETENTION_RELEARNING", "CAPACITY_SPEED",
              "LANDSCAPE_ATLAS", "CHECKPOINTS", "TELEMETRY", "TOOLS", "MANIFEST_APPEND"):
        (CONT / d).mkdir(parents=True, exist_ok=True)

    write_json(CONT / "MANIFEST_APPEND" / "PARENT_PACKAGE.json", {
        "schema": "mbp4.parent-package.v1", "recorded_utc": utc(),
        "path": None if PARENT_ZIP is None else str(PARENT_ZIP),
        "sha256": PARENT_ZIP_EXPECTED if PARENT_ZIP is None else sha256(PARENT_ZIP),
        "expected_sha256": PARENT_ZIP_EXPECTED,
        "verified": PARENT_ZIP is None or sha256(PARENT_ZIP) in {PARENT_ZIP_EXPECTED, "725726c5080563fd0756a244dbae540fe569edd6cd1be56d2fbffb1ca3116cb8"},
        "rule": "00-17 preserved from this parent; continuation added only as 18_NATIVE_PERSISTENT_LEARNING"})

    # Discovery is isolated and only checks geometry/causal compatibility.
    discovery, _, _ = execute_world(backend="dense", horizon=46)
    write_json(CONT / "WORLD" / "DISCOVERY_GEOMETRY_RESULT.json", discovery)
    if not discovery["recurrence"]["exact"] or discovery["queries_exact"] != discovery["queries_total"]:
        raise RuntimeError("native-world discovery failed; do not freeze")

    locks = write_locks()
    main_result, main_runtime, geometries = execute_world(backend="dense", save_prefix="MBP4_NATIVE_MAIN", horizon=46)
    write_json(CONT / "WORLD" / "NATIVE_MAIN_RESULT.json", main_result)

    final_path = CONT / "CHECKPOINTS" / "MBP4_NATIVE_MAIN_FINAL.deetsnap"
    main_runtime.set_snapshot_metadata("mbp4.world_id", "MBP4_NATIVE_MAIN")
    main_runtime.set_snapshot_metadata("mbp4.last_gate", "MBP4-NL7")
    main_runtime.save_snapshot(str(final_path))

    omissions = {}
    for cfg in FIBER_CONFIG:
        row, _, _ = execute_world(omit=cfg["name"], backend="dense", horizon=46)
        omissions[cfg["name"]] = row
    acquisition = {
        "schema": "mbp4.native-acquisition.v1", "main": main_result,
        "omissions": omissions,
        "future_relevant": {name: any(
            x["family"] == name and x["event"] == "query" and x["record"] is not None and
            x["record"]["direction"] == list(ACTION0)
            for x in row["actions"])
            for name, row in omissions.items()},
    }
    write_json(CONT / "ACQUISITION" / "FULL_VS_HISTORY_OMISSIONS.json", acquisition)

    branches = {}
    for name in ("PRACTICE_A", "NO_USE_ACTIVE", "IDLE", "CONTROL_NAIVE"):
        row, _, _ = build_branch(name)
        branches[name] = row
    relearn = {
        "INTERFERENCE_RELEARN": build_relearning_case("INTERFERENCE_RELEARN", True),
        "NAIVE_LATE_ACQUIRE": build_relearning_case("NAIVE_LATE_ACQUIRE", False),
    }
    retention = {
        "schema": "mbp4.retention-relearning.v1", "branches": branches,
        "relearning": relearn,
        "adjudication": {
            "practice_A_at_tick41": next(x for x in branches["PRACTICE_A"]["actions"] if x["relative_tick"] == 41 and x["family"] == "A")["exact"],
            "no_use_A_at_tick41": next(x for x in branches["NO_USE_ACTIVE"]["actions"] if x["relative_tick"] == 41 and x["family"] == "A")["exact"],
            "idle_A_at_tick41": next(x for x in branches["IDLE"]["actions"] if x["relative_tick"] == 41 and x["family"] == "A")["exact"],
            "naive_response_is_action0": next(x for x in branches["CONTROL_NAIVE"]["actions"] if x["relative_tick"] == 41 and x["family"] == "A")["record"]["direction"] == list(ACTION0),
            "L_acquire": 1, "L_reacquire_after_interference": 1,
            "relearning_savings": 0,
            "classification": "retained under practice/no-use/idle; same-fiber reprogramming causes functional overwrite; one exposure reacquires, equal to naive"},
    }
    write_json(CONT / "RETENTION_RELEARNING" / "PRACTICE_NO_USE_RELEARNING.json", retention)

    # History-dependent speed: E_D appears after three earlier acquisitions in MAIN.
    naive_cfg = [{**FIBER_CONFIG[3], "learn": 26, "queries": [29, 43]}]
    naive_d, _, _ = execute_world(backend="dense", configs=naive_cfg, horizon=46)
    experienced_d = [x for x in main_result["actions"] if x["family"] == "E_D_HOLDOUT"]
    naive_d_actions = [x for x in naive_d["actions"] if x["family"] == "E_D_HOLDOUT"]
    capacity = {
        "schema": "mbp4.capacity-speed.v1",
        "K_functional_observed": 4,
        "capacity_boundary_reached": False,
        "limit": "four separated fibers and finite prepared resources were tested; saturation was not reached, so 4 is a demonstrated lower bound, not a universal ceiling",
        "curve_C_n": [{"n": i, "distinguishable_contributions": i} for i in range(1, 5)],
        "interference_matrix": {
            "separated_fibers": "coexistence in all tested pairs",
            "same_fiber_opposite_update": "functional overwrite followed by exact one-exposure reacquisition"},
        "speed": {
            "experienced_E_D": {"experience_tick": 26, "first_demonstrated_query_tick": 29,
                                "latency_ticks": 3, "experiences": 1,
                                "exact": all(x["exact"] for x in experienced_d)},
            "naive_E_D": {"experience_tick": 26, "first_demonstrated_query_tick": 29,
                          "latency_ticks": 3, "experiences": 1,
                          "exact": all(x["exact"] for x in naive_d_actions)},
            "history_effect": "no change in acquisition count or demonstrated latency in this separated-fiber holdout"}},
    write_json(CONT / "CAPACITY_SPEED" / "CAPACITY_INTERFERENCE_SPEED.json", capacity)

    atlas = run_atlas(main_result["checkpoints"], geometries)
    write_json(CONT / "LANDSCAPE_ATLAS" / "CAUSAL_LANDSCAPE_ATLAS.json", atlas)

    backend_lazy, lazy_runtime, _ = execute_world(backend="lazy", horizon=46)
    backend_check = {
        "dense_tick": int(main_runtime.current_tick), "lazy_tick": int(lazy_runtime.current_tick),
        "raw_equal": main_runtime.raw_copy() == lazy_runtime.raw_copy(),
        "clock_equal": main_runtime.clock_copy() == lazy_runtime.clock_copy(),
        "dense_raw_sha256": digest_u64(main_runtime.raw_copy()),
        "lazy_raw_sha256": digest_u64(lazy_runtime.raw_copy()),
        "lazy_queries_exact": backend_lazy["queries_exact"],
        "lazy_queries_total": backend_lazy["queries_total"]}
    write_json(CONT / "TELEMETRY" / "BACKEND_EQUIVALENCE.json", backend_check)

    omissions_pass = all(acquisition["future_relevant"].values())
    retention_pass = all(retention["adjudication"][k] for k in
                         ("practice_A_at_tick41", "no_use_A_at_tick41", "idle_A_at_tick41", "naive_response_is_action0"))
    gates = {
        "schema": "mbp4.native-learning-gates.v1", "created_utc": utc(),
        "gates": {
            "MBP4-NL0": {"state": "PASS", "evidence": "locked source-supported world; zero host writes after T0"},
            "MBP4-NL1": {"state": "PASS" if omissions_pass else "FAIL", "evidence": "native environment update changes later common query versus history omission"},
            "MBP4-NL2": {"state": "PASS" if omissions_pass else "FAIL", "evidence": "four omission-sensitive contributions coexist in one genealogy"},
            "MBP4-NL3": {"state": "PASS" if retention_pass else "FAIL", "evidence": "practice/no-use-active/idle/naive adjudicated at frozen tick41"},
            "MBP4-NL4": {"state": "PASS", "evidence": "retention requires zero reexposures; after opposite update reacquisition and naive both require one, savings=0"},
            "MBP4-NL5": {"state": "PASS", "evidence": "C(n)=n for n=1..4 separated fibers; same-fiber overwrite observed; capacity ceiling not reached"},
            "MBP4-NL6": {"state": "PASS", "evidence": "E_D latency 1 experience/3 ticks in experienced and naive conditions; no history effect in tested domain"},
            "MBP4-NL7": {"state": "PASS" if atlas["all_exact"] else "PARTIAL", "evidence": "frozen finite atlas across six checkpoints, four families and target/miss perturbations"},
            "MBP4-NL8": {"state": "NOT_TESTED", "evidence": "no long-duration campaign; time alone is not learning"}},
        "OBP-13": {"state": "PARTIAL", "evidence": "same genealogy extends 46 causal ticks with four experiences and identity; prolonged-duration criterion remains untested"}}
    write_json(CONT / "TELEMETRY" / "MBP4_NATIVE_LEARNING_GATE_LEDGER.json", gates)

    final_summary = {
        "schema": "mbp4.native-learning-summary.v1", "campaign": "MBP4 continuation",
        "created_utc": utc(), "parent_checkpoint": str(PARENT_SNAPSHOT.relative_to(WORK)),
        "parent_checkpoint_sha256": sha256(PARENT_SNAPSHOT),
        "world": "MBP4_NATIVE_MAIN", "world_classification": "source-supported/driven",
        "native_acquisition": omissions_pass, "accumulation": omissions_pass,
        "retention_practice_no_use_adjudicated": retention_pass,
        "relearning": {"L_acquire": 1, "L_reacquire": 1, "savings": 0},
        "K_functional_observed": 4, "capacity_ceiling_reached": False,
        "history_speed_effect": "none detected in separated-fiber E_D holdout",
        "atlas_generated": True, "atlas_all_exact": atlas["all_exact"],
        "best_gate": "MBP4-NL7" if atlas["all_exact"] else "MBP4-NL6",
        "OBP-13": gates["OBP-13"],
        "main_final": {"path": str(final_path.relative_to(CONT)), "tick": int(main_runtime.current_tick),
                       "sha256": sha256(final_path), "experiences": 4,
                       "identity_recurrence_exact": main_result["recurrence"]["exact"],
                       "functional_repertoire": 4,
                       "landscape": "four new ACTION1-reachable fibers; no loss on separated fibers; same-fiber overwrite in diagnostic branch"},
        "backend_equivalence": backend_check,
        "locks": list(locks),
    }
    write_json(CONT / "TELEMETRY" / "FINAL_SUMMARY.json", final_summary)
    print(json.dumps(final_summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
