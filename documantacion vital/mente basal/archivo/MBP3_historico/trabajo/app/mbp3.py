from __future__ import annotations

"""MBP3 native curriculum on the immutable final MBP2-B checkpoint.

Only DEE v27 advances physical state.  This module prepares a finite set of
generic carriers at the campaign boundary, observes the resulting lineages,
and runs destructive questions only on diagnostic forks.  Human-facing names
remain metadata and are never encoded in RAW or clocks.
"""

import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import habitat_base as base

dee = base.dee
N = 127
APP_VERSION = "3.0.0"
WORLD_SCHEMA = "mente-basal-persistente-3.world.v1"
CAMPAIGN_ID = "MBP3-NATIVE-CURRICULUM-2H"
WORLD_ID = "MBP3-MAIN-B-CONTINUACION"
PARENT_TICK = 87_176
PARENT_SHA256 = "a76ef04bb773a1f671dff382e38d64f8b67acd2084ea6a14e0e4bfd948fd1a39"
PARENT_RELATIVE = Path("parent") / "MBP2_B_FINAL_T87176.deetsnap"
PRIMARY_START = (64, 74, 63)
COMPANION_START = (64, 80, 100)

Coord = tuple[int, int, int]
Direction = tuple[int, int, int]


@dataclass(frozen=True)
class Geometry:
    primary_start: Coord = PRIMARY_START
    companion_start: Coord = COMPANION_START


def geometry() -> Geometry:
    return Geometry()


def plus(q: Coord, d: Direction, scale: int = 1) -> Coord:
    return tuple((q[i] + d[i] * scale) % N for i in range(3))  # type: ignore[return-value]


def sign_sum(a: Direction, b: Direction) -> Direction:
    values = tuple(a[i] + b[i] for i in range(3))
    return tuple(0 if v == 0 else (1 if v > 0 else -1) for v in values)  # type: ignore[return-value]


def linear_index(q: Coord) -> int:
    return int(dee.linear_index(q[0], q[1], q[2], N))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parent_path() -> Path:
    return project_root() / PARENT_RELATIVE


def default_config() -> dict[str, Any]:
    return {
        "schema": WORLD_SCHEMA,
        "application_version": APP_VERSION,
        "campaign_id": CAMPAIGN_ID,
        "world_id": WORLD_ID,
        "condition": "MAIN",
        "dimension": N,
        "backend": "lazy",
        "threads": 1,
        "block_ticks": 8,
        "idle_sleep_seconds": 0.05,
        "checkpoint_interval_seconds": 3600,
        "telemetry_interval_ticks": 512,
        "max_autonomous_hours": 3.0,
        "max_ticks_after_reference": 2_000_000,
        "max_archive_bytes": 2_000_000_000,
        "min_free_disk_bytes": 2_147_483_648,
        "max_working_set_bytes": 1_073_741_824,
        "t_ref": PARENT_TICK,
        "start_paused": True,
        "parent_checkpoint": str(PARENT_RELATIVE).replace("\\", "/"),
        "parent_sha256": PARENT_SHA256,
        "curriculum_variant": "MAIN",
    }


def _carrier(identifier: str, load: int, direction: Direction, arrival: int,
             target: Coord, fiber: str) -> dict[str, Any]:
    return {
        "id": identifier,
        "load": load,
        "direction": list(direction),
        "relative_arrival_tick": arrival,
        "absolute_arrival_tick": PARENT_TICK + arrival,
        "target": list(target),
        "source": list(plus(target, direction, -arrival)),
        "fiber": fiber,
        "state": 1,
        "semantic": 1,
    }


def environment_spec(variant: str = "MAIN") -> list[dict[str, Any]]:
    """Frozen finite physical inventory installed at campaign relative t0."""
    variant = variant.upper()
    if variant not in {"MAIN", "REVERSE", "NO_FIRST", "NO_MEDIATOR", "SHAM"}:
        raise ValueError(f"unknown curriculum variant: {variant}")
    if variant == "REVERSE":
        first = _carrier("P1", 5, (0, 0, -1), 32, (96, 74, 63), "primary")
        second = _carrier("P2", 4, (0, 0, 1), 96, (33, 74, 126), "primary")
    else:
        first_target = (96, 74, 66) if variant == "SHAM" else (96, 74, 63)
        first = _carrier("P1", 4, (0, 0, 1), 32, first_target, "primary")
        second = _carrier("P2", 5, (0, 0, -1), 96, (33, 74, 0), "primary")
    items = [
        first,
        second,
        _carrier("P3", 6, (0, 1, 0), 160, (97, 74, 0), "primary"),
        # The initially proposed arrival at r224 crossed the primary at r34
        # because of the torus.  Four direction controls at r190 were run and
        # frozen before MAIN; this first successful direction is retained.
        _carrier("P4", 1, (-1, -1, 1), 190, (0, 104, 0), "primary"),
        _carrier("P5", 2, (1, 0, -1), 222, (0, 104, 32), "primary"),
        _carrier("C1", 3, (0, 1, 0), 48, (112, 80, 100), "companion"),
        _carrier("C2", 2, (0, -1, 0), 112, (49, 17, 100), "companion"),
        _carrier("C3", 4, (0, 0, 1), 176, (113, 17, 100), "companion"),
        _carrier("C4", 1, (0, 0, -1), 240, (50, 17, 37), "companion"),
    ]
    if variant == "NO_FIRST":
        items = [item for item in items if item["id"] != "P1"]
    if variant == "NO_MEDIATOR":
        items = [item for item in items if item["id"] != "P4"]
    return items


def _place(raw: list[int], clock: list[int], item: dict[str, Any]) -> None:
    q = tuple(item["source"])
    index = linear_index(q)
    if raw[index] != 0:
        raise RuntimeError(f"environment preparation overlaps occupied site {q}")
    d = item["direction"]
    raw[index] = int(dee.pack_record(
        int(item["state"]), int(item["load"]), int(d[0]), int(d[1]), int(d[2]),
        int(item["semantic"])))
    # A newly installed participant starts with campaign-relative age zero.
    clock[index] = 0


def verify_parent(runtime: Any, checkpoint: Path) -> dict[str, Any]:
    if sha256(checkpoint) != PARENT_SHA256:
        raise RuntimeError("MBP2-B parent SHA-256 mismatch")
    if int(runtime.current_tick) != PARENT_TICK or int(runtime.dimension) != N:
        raise RuntimeError("MBP2-B parent tick/dimension mismatch")
    if len(runtime.receipts) != 0:
        raise RuntimeError("MBP2-B parent unexpectedly has pending/recorded receipts")
    primary = base.observe_site(runtime, PRIMARY_START)
    companion = base.observe_site(runtime, COMPANION_START)
    if primary["s_reg"] != 16 or primary["direction"] != [1, 0, 0]:
        raise RuntimeError(f"MBP2-B parent primary anchor mismatch: {primary}")
    if companion["s_reg"] != 17 or companion["direction"] != [1, 0, 0]:
        raise RuntimeError(f"MBP2-B parent companion anchor mismatch: {companion}")
    return {
        "checkpoint": str(checkpoint),
        "sha256": PARENT_SHA256,
        "tick": PARENT_TICK,
        "raw_support": int(runtime.metrics().raw_support),
        "occupied": int(runtime.metrics().occupied),
        "s_reg_sum": int(runtime.metrics().s_reg_sum),
        "receipts": 0,
        "primary": primary,
        "companion": companion,
    }


def build_from_parent(config: dict[str, Any], variant: str | None = None
                      ) -> tuple[Any, Geometry, dict[str, Any]]:
    checkpoint = parent_path()
    parent = dee.Runtime.load_snapshot(str(checkpoint))
    parent_evidence = verify_parent(parent, checkpoint)
    raw = parent.raw_copy()
    clock = parent.clock_copy()
    items = environment_spec(variant or str(config.get("curriculum_variant", "MAIN")))
    for item in items:
        _place(raw, clock, item)
    runtime = dee.Runtime.import_research_state(N, PARENT_TICK, raw, clock)
    runtime.execution_options = dee.TickOptions(dee.Backend.LAZY, int(config["threads"]))
    runtime.pause()
    runtime.protocol_phase = "MBP3_ENVIRONMENT_PREPARED_T0"
    for key, value in {
        "habitat.schema": WORLD_SCHEMA,
        "habitat.world_id": str(config["world_id"]),
        "habitat.campaign_id": str(config["campaign_id"]),
        "habitat.kernel": "DEE v27",
        "habitat.product": "DEE thinking 2.2.0",
        "habitat.parent_world_id": "MBP2-B-INTERACTIVO",
        "habitat.parent_tick": str(PARENT_TICK),
        "habitat.parent_sha256": PARENT_SHA256,
        "habitat.curriculum_variant": str(variant or config.get("curriculum_variant", "MAIN")),
        "habitat.host_inputs_after_t0": "0",
    }.items():
        runtime.set_snapshot_metadata(key, value)
    return runtime, geometry(), {
        "parent": parent_evidence,
        "environment": items,
        "installation": "declared raw/clock preparation at campaign t0; not learning",
        "host_inputs_after_t0": 0,
    }


def predicted_primary(relative_tick: int, variant: str = "MAIN") -> tuple[Coord, int, Direction]:
    variant = variant.upper()
    if variant != "MAIN":
        # Controls are located by scan rather than by a favorable prediction.
        return plus(PRIMARY_START, (1, 0, 0), relative_tick), 16, (1, 0, 0)
    stages: list[tuple[int, Coord, int, Direction]] = [
        (0, PRIMARY_START, 16, (1, 0, 0)),
        (32, (96, 74, 63), 20, (1, 0, 1)),
        (96, (33, 74, 0), 25, (1, 0, 0)),
        (160, (97, 74, 0), 31, (1, 1, 0)),
        (190, (0, 104, 0), 32, (0, 0, 1)),
        (222, (0, 104, 32), 34, (1, 0, 0)),
    ]
    selected = stages[0]
    for stage in stages:
        if relative_tick >= stage[0]:
            selected = stage
    start, site, load, direction = selected
    return plus(site, direction, relative_tick - start), load, direction


def predicted_companion(relative_tick: int) -> tuple[Coord, int, Direction]:
    stages: list[tuple[int, Coord, int, Direction]] = [
        (0, COMPANION_START, 17, (1, 0, 0)),
        (48, (112, 80, 100), 20, (1, 1, 0)),
        (112, (49, 17, 100), 22, (1, 0, 0)),
        (176, (113, 17, 100), 26, (1, 0, 1)),
        (240, (50, 17, 37), 27, (1, 0, 0)),
    ]
    selected = stages[0]
    for stage in stages:
        if relative_tick >= stage[0]:
            selected = stage
    start, site, load, direction = selected
    return plus(site, direction, relative_tick - start), load, direction


RELATIVE_SCIENCE_TICKS = (0, 1, 31, 32, 33, 47, 48, 49, 95, 96, 97, 111,
                          112, 113, 159, 160, 161, 175, 176, 177, 189, 190,
                          191, 221, 222, 223, 239, 240, 241, 300)
SCIENCE_TICKS = tuple(PARENT_TICK + value for value in RELATIVE_SCIENCE_TICKS)
CHECKPOINT_RELATIVE_TICKS = {32, 48, 96, 112, 160, 176, 190, 222, 240, 300}
INITIAL_INPUTS: tuple[tuple[str, int, int, str], ...] = ()
LATE_INPUTS: tuple[tuple[str, int, int, str], ...] = ()


def science_observations(runtime: Any, _g: Geometry, tick: int) -> dict[str, Any]:
    relative = tick - PARENT_TICK
    variant = str(runtime.snapshot_metadata("habitat.curriculum_variant") or "MAIN")
    p_site, p_load, p_direction = predicted_primary(relative, variant)
    c_site, c_load, c_direction = predicted_companion(relative)
    return {
        "relative_tick": relative,
        "primary": {
            "predicted_site": list(p_site), "predicted_load": p_load,
            "predicted_direction": list(p_direction),
            "observed": base.observe_site(runtime, p_site),
        },
        "companion": {
            "predicted_site": list(c_site), "predicted_load": c_load,
            "predicted_direction": list(c_direction),
            "observed": base.observe_site(runtime, c_site),
        },
    }


def write_telemetry(runtime: Any, paths: dict[str, Path], state: dict[str, Any],
                    g: Geometry, note: str = "periodic") -> None:
    tick = int(runtime.current_tick)
    relative = tick - PARENT_TICK
    p_site, p_load, p_direction = predicted_primary(relative)
    c_site, c_load, c_direction = predicted_companion(relative)
    p_obs = base.observe_site(runtime, p_site)
    c_obs = base.observe_site(runtime, c_site)
    metrics = runtime.metrics()
    disk = shutil.disk_usage(paths["root"])
    header = [
        "utc", "tick", "relative_tick", "note", "raw_support", "occupied",
        "s_reg_sum", "working_set_bytes", "archive_bytes", "disk_free_bytes",
        "primary_x", "primary_y", "primary_z", "primary_expected_load",
        "primary_observed_load", "primary_expected_direction", "primary_observed_direction",
        "primary_match", "companion_x", "companion_y", "companion_z",
        "companion_expected_load", "companion_observed_load",
        "companion_expected_direction", "companion_observed_direction", "companion_match",
    ]
    row = [
        base.iso_utc(), tick, relative, note, int(metrics.raw_support),
        int(metrics.occupied), int(metrics.s_reg_sum), base.process_working_set(),
        base.tree_bytes(paths["world"]) + base.tree_bytes(paths["history"]), disk.free,
        *p_site, p_load, p_obs["s_reg"], json.dumps(p_direction),
        json.dumps(p_obs["direction"]),
        bool(p_obs["s_reg"] == p_load and p_obs["direction"] == list(p_direction)),
        *c_site, c_load, c_obs["s_reg"], json.dumps(c_direction),
        json.dumps(c_obs["direction"]),
        bool(c_obs["s_reg"] == c_load and c_obs["direction"] == list(c_direction)),
    ]
    base.append_csv(base.active_telemetry(paths, state), header, row)
    state["last_telemetry_tick"] = tick


def initialize(root: Path, config_override: Path | None = None) -> dict[str, Any]:
    paths = base.root_paths(root)
    base.ensure_layout(paths)
    if paths["instance"].exists() or paths["latest"].exists():
        raise RuntimeError("world already exists; initialization never overwrites a lineage")
    config = default_config()
    if config_override is not None:
        config.update(base.load_json(config_override))
    if int(config["dimension"]) != N:
        raise ValueError("MBP3 requires the inherited N=127 parent")
    if str(config.get("curriculum_variant", "MAIN")).upper() != "MAIN":
        raise ValueError("production MAIN accepts only the frozen MAIN curriculum")
    base.atomic_json(paths["config"], config)
    session_id = f"{config['campaign_id']}-MAIN-{base.utc_now().strftime('%Y%m%dT%H%M%SZ')}"
    state = base.initial_controller(config, session_id)
    state.update({
        "current_tick": PARENT_TICK,
        "segment_start_tick": PARENT_TICK,
        "last_checkpoint_tick": PARENT_TICK,
        "last_collection_tick": PARENT_TICK,
        "reference_tick": PARENT_TICK,
        "parent_world_id": "MBP2-B-INTERACTIVO",
        "parent_tick": PARENT_TICK,
        "parent_sha256": PARENT_SHA256,
    })
    parent = dee.Runtime.load_snapshot(str(parent_path()))
    parent_evidence = verify_parent(parent, parent_path())

    immutable_parent = paths["checkpoints"] / "PADRE_B_INMUTABLE_T87176.deetsnap"
    shutil.copy2(parent_path(), immutable_parent)
    if sha256(immutable_parent) != PARENT_SHA256:
        raise RuntimeError("immutable parent copy verification failed")
    base.atomic_json(immutable_parent.with_suffix(immutable_parent.suffix + ".json"), {
        "schema": WORLD_SCHEMA, "role": "immutable_parent_B", "tick": PARENT_TICK,
        "sha256": PARENT_SHA256, "source": str(PARENT_RELATIVE).replace("\\", "/"),
        "parent_world_id": "MBP2-B-INTERACTIVO", "verified": parent_evidence,
    })
    main_pre_env = paths["checkpoints"] / "MAIN_PRE_ENV_T87176.deetsnap"
    shutil.copy2(parent_path(), main_pre_env)
    base.atomic_json(main_pre_env.with_suffix(main_pre_env.suffix + ".json"), {
        "schema": WORLD_SCHEMA, "role": "main_before_environment", "tick": PARENT_TICK,
        "sha256": sha256(main_pre_env), "byte_identical_to_parent": True,
    })

    runtime, g, registry = build_from_parent(config, "MAIN")
    post_env = paths["checkpoints"] / "MAIN_POST_ENV_T0_T87176.deetsnap"
    temporary = post_env.with_suffix(post_env.suffix + ".tmp")
    runtime.save_snapshot(str(temporary))
    checked = dee.Runtime.load_snapshot(str(temporary))
    if (int(checked.current_tick) != PARENT_TICK or
            checked.raw_copy() != runtime.raw_copy() or
            checked.clock_copy() != runtime.clock_copy()):
        temporary.unlink(missing_ok=True)
        raise RuntimeError("MAIN_POST_ENV_T0 exact verification failed")
    os.replace(temporary, post_env)
    base.atomic_json(post_env.with_suffix(post_env.suffix + ".json"), {
        "schema": WORLD_SCHEMA, "role": "main_after_declared_environment_preparation",
        "tick": PARENT_TICK, "sha256": sha256(post_env), "preparation": registry,
        "learning_started": False, "host_inputs_after_t0": 0,
    })
    state["x0_checkpoint"] = str(main_pre_env.relative_to(paths["root"]))
    state["last_checkpoint"] = str(post_env.relative_to(paths["root"]))
    state["last_collection_checkpoint"] = str(post_env.relative_to(paths["root"]))
    state["last_checkpoint_utc"] = base.iso_utc()
    state["last_checkpoint_wall"] = 0.0
    base.atomic_text(paths["latest"], str(post_env.relative_to(paths["root"])) + "\n")
    base.log_event(paths, state, {
        "type": "lineage_continued", "tick": PARENT_TICK,
        "parent_world_id": "MBP2-B-INTERACTIVO", "parent_sha256": PARENT_SHA256,
        "parent_checkpoint": str(immutable_parent.relative_to(paths["root"])),
        "main_pre_env": str(main_pre_env.relative_to(paths["root"])),
        "main_post_env_t0": str(post_env.relative_to(paths["root"])),
        "environment": registry["environment"],
        "intervention_contract": "finite participants installed at campaign t0; no adaptive host inputs",
    })
    instance = {
        "schema": WORLD_SCHEMA, "application_version": APP_VERSION,
        "campaign_id": config["campaign_id"], "world_id": config["world_id"],
        "session_id": session_id, "created_utc": state["created_utc"],
        "created_local": state["created_local"], "dimension": N,
        "kernel": "DEE v27", "product": "DEE thinking 2.2.0",
        "genealogy": ["MBP2-B-INTERACTIVO", config["world_id"]],
        "parent_checkpoint": str(immutable_parent.relative_to(paths["root"])),
        "parent_sha256": PARENT_SHA256,
        "main_pre_env": str(main_pre_env.relative_to(paths["root"])),
        "main_post_env_t0": str(post_env.relative_to(paths["root"])),
        "configuration": str(paths["config"].relative_to(paths["root"])),
        "preparation": registry,
    }
    base.atomic_json(paths["instance"], instance)
    base.atomic_json(paths["controller"], state)
    base.write_status(paths, state, runtime, "STOPPED_READY",
                      "inherited B and frozen environment prepared; worker not running")
    return instance


_base_record_science_tick = base.record_science_tick


def record_science_tick(runtime: Any, paths: dict[str, Path], state: dict[str, Any],
                        g: Geometry) -> None:
    tick = int(runtime.current_tick)
    key = str(tick)
    already = key in state.setdefault("recorded_science_ticks", [])
    _base_record_science_tick(runtime, paths, state, g)
    relative = tick - PARENT_TICK
    if relative in CHECKPOINT_RELATIVE_TICKS and not already:
        checkpoint = base.save_checkpoint(
            runtime, paths, state, f"curriculum_r{relative}", exact_verify=True)
        base.log_event(paths, state, {
            "type": "curriculum_boundary_checkpoint", "tick": tick,
            "relative_tick": relative,
            "checkpoint": str(checkpoint.relative_to(paths["root"])),
        })


def _scan(runtime: Any, loads: set[int] | None = None) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for index, value in enumerate(runtime.raw_copy()):
        if not value:
            continue
        rec = dee.decode_record(int(value))
        if int(rec.semantic) != 1:
            continue
        if loads is not None and int(rec.s_reg) not in loads:
            continue
        x = index // (N * N)
        rest = index % (N * N)
        y = rest // N
        z = rest % N
        result.append({
            "site": [x, y, z], "raw": int(value), "state": int(rec.state),
            "s_reg": int(rec.s_reg),
            "direction": [int(rec.dx), int(rec.dy), int(rec.dz)],
            "semantic": int(rec.semantic),
            "clock": int(runtime.clock_copy()[index]),
        })
    return result


def locate_lineage(runtime: Any, role: str) -> dict[str, Any]:
    relative = int(runtime.current_tick) - PARENT_TICK
    if role == "primary":
        site, load, direction = predicted_primary(relative)
    elif role == "companion":
        site, load, direction = predicted_companion(relative)
    else:
        raise ValueError(role)
    observed = base.observe_site(runtime, site)
    if observed["s_reg"] == load and observed["direction"] == list(direction):
        return {"role": role, "method": "frozen_trajectory", "ambiguous": False,
                "site": list(site), "expected_load": load,
                "expected_direction": list(direction), "observation": observed}
    candidates = _scan(runtime, {load})
    return {"role": role, "method": "global_load_scan", "ambiguous": len(candidates) != 1,
            "predicted_site": list(site), "expected_load": load,
            "expected_direction": list(direction), "candidates": candidates}


def _two_use_query_at(runtime: Any, role: str, name: str, site: Coord,
                      direction_now: Direction, located: dict[str, Any],
                      first_load: int, first_direction: Direction,
                      second_load: int, second_direction: Direction) -> dict[str, Any]:
    """Apply a frozen two-contact question to an explicitly identified lineage."""
    tick = int(runtime.current_tick)
    branch = runtime.fork()
    control = runtime.fork()
    first_target = plus(site, direction_now, 6)
    after_first = sign_sum(direction_now, first_direction)
    second_target = plus(first_target, after_first, 6)
    first_source = plus(first_target, first_direction, -6)
    second_source = plus(second_target, second_direction, -12)
    receipts: list[int] = []
    for suffix, source, load, direction in (
            ("first", first_source, first_load, first_direction),
            ("second", second_source, second_load, second_direction)):
        channel = dee.ChannelSpec()
        channel.name = f"diagnostic.{name}.{suffix}"
        channel.injection_site = base.coordinate(source)
        channel.state = 1
        channel.direction = base.direction(direction)
        channel.semantic = 1
        channel.allow_experience = True
        channel.allow_probe = False
        branch.register_channel(channel)
        receipts.append(int(branch.experience(channel.name, tick, load).id))
    branch.resume(); control.resume()
    branch.advance(6); control.advance(6)
    first = base.observe_site(branch, first_target)
    first_control = base.observe_site(control, first_target)
    branch.advance(6); control.advance(6)
    second = base.observe_site(branch, second_target)
    second_control = base.observe_site(control, second_target)
    return {
        "executed": True,
        "mode": "diagnostic forks; query carriers installed only in treatment branch",
        "role": role, "located": located, "receipts": receipts,
        "first": {"source": list(first_source), "target": list(first_target),
                  "load": first_load, "direction": list(first_direction),
                  "with_query": first, "same_history_no_query": first_control},
        "second": {"source": list(second_source), "target": list(second_target),
                   "load": second_load, "direction": list(second_direction),
                   "with_query": second, "same_history_no_query": second_control},
    }


def _two_use_query(runtime: Any, role: str, name: str, first_load: int,
                   first_direction: Direction, second_load: int,
                   second_direction: Direction) -> dict[str, Any]:
    located = locate_lineage(runtime, role)
    if located.get("ambiguous") or not located.get("site"):
        return {"executed": False, "reason": "lineage ambiguous", "located": located}
    return _two_use_query_at(
        runtime, role, name, tuple(located["site"]),
        tuple(located["observation"]["direction"]), located,
        first_load, first_direction, second_load, second_direction)


def diagnostic_evaluate(checkpoint: Path, output: Path) -> dict[str, Any]:
    runtime = dee.Runtime.load_snapshot(str(checkpoint))
    before = (runtime.raw_copy(), runtime.clock_copy(), int(runtime.current_tick))
    result = {
        "schema": "mbp3.capability-interrogation.v1",
        "checkpoint": str(checkpoint), "tick": int(runtime.current_tick),
        "relative_tick": int(runtime.current_tick) - PARENT_TICK,
        "primary": locate_lineage(runtime, "primary"),
        "companion": locate_lineage(runtime, "companion"),
        "queries": {
            "Q_PREV_XY": _two_use_query(runtime, "primary", "q_prev_xy", 7,
                                         (0, 1, 0), 5, (0, -1, 0)),
            "Q_HOLDOUT_XZ": _two_use_query(runtime, "primary", "q_holdout_xz", 4,
                                            (0, 0, 1), 6, (0, 0, -1)),
            "Q_SEPARATE_FIBER": _two_use_query(runtime, "companion", "q_companion", 3,
                                                (0, 1, 0), 2, (0, -1, 0)),
        },
        "main_checkpoint_unmodified": (
            before[0] == runtime.raw_copy() and before[1] == runtime.clock_copy() and
            before[2] == int(runtime.current_tick)),
        "limits": [
            "fork queries are diagnostic and never return to MAIN",
            "a positive response is bounded functional access, not language or universal intelligence",
            "load accumulation alone is not treated as composition",
        ],
    }
    base.atomic_json(output, result)
    return result


def _run_variant(variant: str, horizon: int = 320,
                 backend: Any | None = None) -> dict[str, Any]:
    config = default_config()
    runtime, g, registry = build_from_parent(config, variant)
    runtime.execution_options = dee.TickOptions(
        backend if backend is not None else dee.Backend.LAZY, 1)
    runtime.resume()
    trace: list[dict[str, Any]] = []
    relative_marks = sorted(set(RELATIVE_SCIENCE_TICKS) | {horizon})
    for mark in relative_marks:
        target = PARENT_TICK + min(mark, horizon)
        if int(runtime.current_tick) < target:
            runtime.run_until(target)
        if mark <= horizon:
            trace.append({"relative_tick": mark,
                          "readings": science_observations(runtime, g, int(runtime.current_tick))})
        if mark >= horizon:
            break
    metrics = runtime.metrics()
    if variant == "MAIN":
        qsite, qload, qdirection = predicted_primary(horizon)
    elif variant == "REVERSE":
        qsite, qload, qdirection = plus((33, 74, 126), (1, 0, 0), horizon - 96), 25, (1, 0, 0)
    elif variant in {"NO_FIRST", "SHAM"}:
        qsite, qload, qdirection = plus(PRIMARY_START, (1, 0, 0), horizon), 16, (1, 0, 0)
    else:  # NO_MEDIATOR
        qsite, qload, qdirection = plus((97, 74, 0), (1, 1, 0), horizon - 160), 31, (1, 1, 0)
    qobserved = base.observe_site(runtime, qsite)
    common_query = _two_use_query_at(
        runtime, "primary", "order_common", qsite, qdirection,
        {"method": "frozen_control_trajectory", "site": list(qsite),
         "expected_load": qload, "expected_direction": list(qdirection),
         "observation": qobserved},
        2, (0, 1, 0), 3, (0, -1, 0))
    return {
        "variant": variant, "tick": int(runtime.current_tick),
        "relative_tick": int(runtime.current_tick) - PARENT_TICK,
        "trace": trace, "raw_support": int(metrics.raw_support),
        "occupied": int(metrics.occupied), "s_reg_sum": int(metrics.s_reg_sum),
        "semantic1": _scan(runtime), "preparation": registry,
        "common_query": common_query,
        "raw": runtime.raw_copy(), "clock": runtime.clock_copy(),
    }


def pilot(output: Path) -> dict[str, Any]:
    cases: dict[str, Any] = {}
    raw_states: dict[str, tuple[list[int], list[int]]] = {}
    for variant in ("MAIN", "REVERSE", "NO_FIRST", "NO_MEDIATOR", "SHAM"):
        case = _run_variant(variant)
        raw_states[variant] = (case.pop("raw"), case.pop("clock"))
        cases[variant] = case

    def reading(variant: str, relative: int, role: str) -> dict[str, Any]:
        item = next(x for x in cases[variant]["trace"] if x["relative_tick"] == relative)
        return item["readings"][role]["observed"]

    expected_primary = {
        0: (16, [1, 0, 0]), 32: (20, [1, 0, 1]),
        96: (25, [1, 0, 0]), 160: (31, [1, 1, 0]),
        190: (32, [0, 0, 1]), 222: (34, [1, 0, 0]),
        300: (34, [1, 0, 0]),
    }
    expected_companion = {
        0: (17, [1, 0, 0]), 48: (20, [1, 1, 0]),
        112: (22, [1, 0, 0]), 176: (26, [1, 0, 1]),
        240: (27, [1, 0, 0]), 300: (27, [1, 0, 0]),
    }
    main_primary_exact = all(
        reading("MAIN", t, "primary")["s_reg"] == expected[0] and
        reading("MAIN", t, "primary")["direction"] == expected[1]
        for t, expected in expected_primary.items())
    companion_exact = all(
        reading("MAIN", t, "companion")["s_reg"] == expected[0] and
        reading("MAIN", t, "companion")["direction"] == expected[1]
        for t, expected in expected_companion.items())
    reverse_differs = raw_states["MAIN"] != raw_states["REVERSE"]
    no_first_differs = raw_states["MAIN"] != raw_states["NO_FIRST"]
    no_mediator_differs = raw_states["MAIN"] != raw_states["NO_MEDIATOR"]
    main_common = cases["MAIN"]["common_query"]["second"]["with_query"]
    reverse_common = cases["REVERSE"]["common_query"]["second"]["with_query"]
    order_specific_common_query = (
        main_common["s_reg"] == 39 and reverse_common["s_reg"] == 30 and
        main_common["direction"] == reverse_common["direction"] == [1, 0, 0])
    result = {
        "schema": "mbp3.pilot.v1", "created_utc": base.iso_utc(),
        "kernel": "DEE v27", "product": "DEE thinking 2.2.0",
        "parent": {"tick": PARENT_TICK, "sha256": PARENT_SHA256},
        "cases": cases,
        "criteria": {
            "main_primary_five_contacts_exact": main_primary_exact,
            "separate_companion_four_contacts_exact": companion_exact,
            "same_inventory_reverse_order_differs": reverse_differs,
            "same_query_order_specific_effect": order_specific_common_query,
            "first_contact_causally_relevant": no_first_differs,
            "mediator_causally_relevant": no_mediator_differs,
            "no_host_inputs_after_preparation": True,
        },
        "interpretation_limits": [
            "different terminal state is not alone functional learning",
            "the direct-mediated chain does not by itself prove an environment-stored return",
            "pilot/control worlds never merge into MAIN",
        ],
    }
    base.atomic_json(output, result)
    return result


def self_test(root: Path, output: Path) -> dict[str, Any]:
    pilot_path = output.with_name(output.stem + "_pilot.json")
    pilot_result = pilot(pilot_path)
    config = default_config()
    runtime, _, _ = build_from_parent(config, "MAIN")
    runtime.resume(); runtime.run_until(PARENT_TICK + 160)
    with tempfile.TemporaryDirectory(prefix="mbp3-selftest-") as text:
        temp = Path(text)
        middle = temp / "middle.deetsnap"
        runtime.save_snapshot(str(middle))
        continuous = runtime.fork(); continuous.run_until(PARENT_TICK + 300)
        resumed = dee.Runtime.load_snapshot(str(middle)); resumed.resume()
        resumed.run_until(PARENT_TICK + 300)
        save_restore = (continuous.raw_copy() == resumed.raw_copy() and
                        continuous.clock_copy() == resumed.clock_copy())
    lazy, _, _ = build_from_parent(config, "MAIN")
    dense, _, _ = build_from_parent(config, "MAIN")
    lazy.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)
    dense.execution_options = dee.TickOptions(dee.Backend.DENSE_SEQUENTIAL, 1)
    lazy.resume(); dense.resume()
    # A full r257 Dense/Lazy comparison passed before the observer-only
    # refactor and is retained as separate evidence.  The current-cut test
    # repeats the first causal contact, keeping launch validation bounded.
    lazy.run_until(PARENT_TICK + 33); dense.run_until(PARENT_TICK + 33)
    dense_exact = lazy.raw_copy() == dense.raw_copy() and lazy.clock_copy() == dense.clock_copy()
    before = (lazy.raw_copy(), lazy.clock_copy(), int(lazy.current_tick))
    _ = locate_lineage(lazy, "primary")
    observer_passive = (before[0] == lazy.raw_copy() and before[1] == lazy.clock_copy() and
                        before[2] == int(lazy.current_tick))
    parent = dee.Runtime.load_snapshot(str(parent_path()))
    qprev = _two_use_query(parent, "primary", "parent_qprev", 7, (0, 1, 0),
                           5, (0, -1, 0))
    checks = {
        **{f"pilot_{k}": bool(v) for k, v in pilot_result["criteria"].items()},
        "save_load_continue_exact": save_restore,
        "dense_matches_lazy_through_first_curriculum_contact": dense_exact,
        "relational_observer_passive": observer_passive,
        "parent_Q_PREV_executed_on_fork": bool(qprev.get("executed")),
        "parent_unmodified_by_Q_PREV": (
            int(parent.current_tick) == PARENT_TICK and sha256(parent_path()) == PARENT_SHA256),
    }
    result = {
        "schema": "mbp3.selftest.v1", "created_utc": base.iso_utc(),
        "checks": checks, "all_passed": all(checks.values()),
        "pilot": str(pilot_path), "parent_qprev": qprev,
    }
    base.atomic_json(output, result)
    return result


def install_hooks() -> None:
    base.APP_VERSION = APP_VERSION
    base.WORLD_SCHEMA = WORLD_SCHEMA
    base.DEFAULT_WORLD_ID = WORLD_ID
    base.N = N
    base.T_REF = PARENT_TICK
    base.Geometry = Geometry
    base.geometry = geometry
    base.default_config = default_config
    base.build_x0 = build_from_parent
    base.science_observations = science_observations
    base.write_telemetry = write_telemetry
    base.INITIAL_INPUTS = INITIAL_INPUTS
    base.LATE_INPUTS = LATE_INPUTS
    base.SCIENCE_TICKS = SCIENCE_TICKS
    base.initialize = initialize
    base.record_science_tick = record_science_tick
    base.evaluate_checkpoint = diagnostic_evaluate
    base.self_test = self_test


def cli() -> int:
    install_hooks()
    if len(sys.argv) > 1 and sys.argv[1] in {"pilot", "diagnose"}:
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="command", required=True)
        p = sub.add_parser("pilot"); p.add_argument("--output", type=Path, required=True)
        d = sub.add_parser("diagnose"); d.add_argument("--checkpoint", type=Path, required=True)
        d.add_argument("--output", type=Path, required=True)
        args = parser.parse_args()
        result = pilot(args.output) if args.command == "pilot" else diagnostic_evaluate(
            args.checkpoint, args.output)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if (args.command == "diagnose" or all(result["criteria"].values())) else 1
    return base.cli()


if __name__ == "__main__":
    raise SystemExit(cli())
