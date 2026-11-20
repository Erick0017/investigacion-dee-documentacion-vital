from __future__ import annotations

"""Scientific preparation and CLI for Mente Basal Persistente 2.

The persistence machinery is inherited from ``habitat_base``.  This module
replaces only the preparation, observers and diagnostics.  No kernel rule is
implemented here: every transition is executed by DEE thinking 2.2.0 / v27.
"""

import argparse
import csv
import json
import os
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import habitat_base as base

dee = base.dee
N = 127
APP_VERSION = "2.0.0"
WORLD_SCHEMA = "mente-basal-persistente-2.world.v1"
BASE_LOAD = 11
BASE_STATE = 1
BASE_DIRECTION = (1, 0, 0)
BASE_SITE = (10, 10, 63)
COMPANION_LOAD = 17
COMPANION_OFFSET = (0, 70, 37)


Coord = tuple[int, int, int]
Direction = tuple[int, int, int]


@dataclass(frozen=True)
class Geometry:
    basal_site: Coord = BASE_SITE
    companion_site: Coord = (10, 80, 100)
    contacts: tuple[Coord, ...] = (
        (26, 10, 63),
        (90, 74, 63),
    )


def wrap(value: int) -> int:
    return value % N


def plus(q: Coord, d: Direction, scale: int = 1) -> Coord:
    return tuple(wrap(q[i] + d[i] * scale) for i in range(3))  # type: ignore[return-value]


def linear_index(q: Coord) -> int:
    return int(dee.linear_index(q[0], q[1], q[2], N))


def geometry() -> Geometry:
    return Geometry()


def condition_spec(condition: str) -> dict[str, Any]:
    condition = condition.upper()
    if condition not in {"A", "B", "C"}:
        raise ValueError("condition must be A, B or C")
    return {
        "A": {
            "name": "AISLAMIENTO",
            "question": "basal drift without the additional environmental inventory",
            "environment": False,
            "contingency": "none",
        },
        "B": {
            "name": "INTERACTIVO",
            "question": "two generic environmental carriers form a causally chained sequence of contacts",
            "environment": True,
            "contingency": "contact at nominal ticks 16 and 80; the first direction enables the second",
        },
        "C": {
            "name": "CONTROL",
            "question": "same inventory; first contingency is z-separated while the second carrier is unchanged",
            "environment": True,
            "contingency": "E1 uses z=66; E2 is byte-identical to B but unreachable without E1",
        },
    }[condition]


def default_config() -> dict[str, Any]:
    return {
        "schema": WORLD_SCHEMA,
        "application_version": APP_VERSION,
        "campaign_id": "MBP2-UNSET",
        "world_id": "MBP2-UNSET",
        "condition": "A",
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
        "t_ref": 0,
        "start_paused": True,
    }


def place(raw: list[int], q: Coord, load: int, direction: Direction,
          semantic: int = 1, state: int = BASE_STATE) -> None:
    if raw[linear_index(q)] != 0:
        raise RuntimeError(f"preparation overlap at {q}")
    raw[linear_index(q)] = int(dee.pack_record(
        int(state), int(load), int(direction[0]), int(direction[1]),
        int(direction[2]), int(semantic)))


def environmental_preparation(condition: str, g: Geometry) -> list[dict[str, Any]]:
    if condition == "A":
        return []
    # Each item is a generic carrier. B's geometry makes a chained sequence:
    # the direction created at one encounter makes the following one reachable.
    # C changes only E1 accessibility. E2 is identical, but without E1 the
    # basal trajectory never reaches it. This controls the chained contingency.
    definitions = [
        ("E1", 2, (0, 1, 0), 16, (26, 121, 63)),
        ("E2", 3, (0, -1, 0), 80, (90, 27, 63)),
    ]
    prepared: list[dict[str, Any]] = []
    for index, (name, load, direction, arrival, source) in enumerate(definitions):
        target = g.contacts[index]
        if condition == "C":
            if index == 0:
                source = (source[0], source[1], 66)
            target = plus(source, direction, arrival)
        prepared.append({
            "id": name,
            "load": load,
            "direction": list(direction),
            "source": list(source),
            "nominal_arrival_tick": arrival,
            "nominal_target": list(target),
            "semantic": 1,
        })
    return prepared


def build_x0(config: dict[str, Any]) -> tuple[Any, Geometry, dict[str, dict[str, Any]]]:
    condition = str(config["condition"]).upper()
    g = geometry()
    raw = [0] * (N ** 3)
    clock = [0] * (N ** 3)
    place(raw, g.basal_site, BASE_LOAD, BASE_DIRECTION)
    place(raw, g.companion_site, COMPANION_LOAD, BASE_DIRECTION)
    environment = environmental_preparation(condition, g)
    for item in environment:
        place(raw, tuple(item["source"]), int(item["load"]),
              tuple(item["direction"]))
    runtime = dee.Runtime.import_research_state(N, 0, raw, clock)
    runtime.execution_options = dee.TickOptions(dee.Backend.LAZY, int(config["threads"]))
    runtime.protocol_phase = "MBP2_PREPARED_T0"
    for key, value in {
        "habitat.schema": WORLD_SCHEMA,
        "habitat.world_id": str(config["world_id"]),
        "habitat.campaign_id": str(config["campaign_id"]),
        "habitat.condition": condition,
        "habitat.kernel": "DEE v27",
        "habitat.product": "DEE thinking 2.2.0",
        "habitat.host_inputs_after_t0": "0",
    }.items():
        runtime.set_snapshot_metadata(key, value)
    registry = {
        "basal.primary": {
            "site": list(g.basal_site), "load": BASE_LOAD,
            "direction": list(BASE_DIRECTION), "role": "common_mobile_lineage",
        },
        "basal.companion": {
            "site": list(g.companion_site), "load": COMPANION_LOAD,
            "direction": list(BASE_DIRECTION), "role": "common_relative_companion",
        },
        "environment": {
            "condition": condition,
            "specification": condition_spec(condition),
            "carriers": environment,
        },
    }
    return runtime, g, registry


def predicted_primary(condition: str, tick: int) -> tuple[Coord, int, Direction]:
    """Frozen prediction used as an observer, never as a transition engine."""
    if condition != "B" or tick < 16:
        return plus(BASE_SITE, BASE_DIRECTION, tick), BASE_LOAD, BASE_DIRECTION
    stages: list[tuple[int, Coord, int, Direction]] = [
        (16, (26, 10, 63), 13, (1, 1, 0)),
        (80, (90, 74, 63), 16, (1, 0, 0)),
    ]
    selected = stages[0]
    for stage in stages:
        if tick >= stage[0]:
            selected = stage
    start_tick, start, load, direction = selected
    return plus(start, direction, tick - start_tick), load, direction


def condition_from_runtime(runtime: Any) -> str:
    value = runtime.snapshot_metadata("habitat.condition")
    return str(value or "A").upper()


def observe_site(runtime: Any, q: Coord) -> dict[str, Any]:
    return base.observe_site(runtime, q)


def science_observations(runtime: Any, g: Geometry, tick: int) -> dict[str, Any]:
    condition = condition_from_runtime(runtime)
    site, expected_load, expected_direction = predicted_primary(condition, tick)
    result: dict[str, Any] = {
        "primary_prediction": {
            "condition": condition,
            "site": list(site),
            "expected_load": expected_load,
            "expected_direction": list(expected_direction),
            "observed": observe_site(runtime, site),
        },
        "companion_prediction": {
            "site": list(plus(geometry().companion_site, BASE_DIRECTION, tick)),
            "observed": observe_site(runtime, plus(geometry().companion_site,
                                                    BASE_DIRECTION, tick)),
        },
    }
    for item in environmental_preparation(condition, g):
        q = plus(tuple(item["source"]), tuple(item["direction"]), tick)
        result[f"environment_{item['id']}"] = {
            "predicted_free_site": list(q),
            "observed": observe_site(runtime, q),
        }
    return result


def write_telemetry(runtime: Any, paths: dict[str, Path], state: dict[str, Any],
                    g: Geometry, note: str = "periodic") -> None:
    metrics = runtime.metrics()
    disk = base.shutil.disk_usage(paths["root"])
    condition = condition_from_runtime(runtime)
    tick = int(runtime.current_tick)
    site, expected_load, expected_direction = predicted_primary(condition, tick)
    observed = observe_site(runtime, site)
    receipts = list(runtime.receipts)
    header = [
        "utc", "tick", "note", "condition", "raw_support", "occupied",
        "s_reg_sum", "working_set_bytes", "archive_bytes", "disk_free_bytes",
        "receipts_total", "receipts_applied", "receipts_rejected",
        "lineage_x", "lineage_y", "lineage_z", "lineage_expected_load",
        "lineage_observed_load", "lineage_observed_raw", "lineage_expected_direction",
        "lineage_observed_direction", "lineage_match",
    ]
    row = [
        base.iso_utc(), tick, note, condition, int(metrics.raw_support),
        int(metrics.occupied), int(metrics.s_reg_sum), base.process_working_set(),
        base.tree_bytes(paths["world"]) + base.tree_bytes(paths["history"]), disk.free,
        len(receipts),
        sum(item.status == dee.EventStatus.APPLIED for item in receipts),
        sum(item.status not in (dee.EventStatus.APPLIED, dee.EventStatus.SCHEDULED)
            for item in receipts),
        site[0], site[1], site[2], expected_load, observed["s_reg"], observed["raw"],
        json.dumps(expected_direction), json.dumps(observed["direction"]),
        bool(observed["s_reg"] == expected_load and
             observed["direction"] == list(expected_direction)),
    ]
    base.append_csv(base.active_telemetry(paths, state), header, row)
    state["last_telemetry_tick"] = tick


SCIENCE_TICKS = (0, 1, 15, 16, 17, 32, 64, 79, 80, 81, 127, 144, 300)
INITIAL_INPUTS: tuple[tuple[str, int, int, str], ...] = ()
LATE_INPUTS: tuple[tuple[str, int, int, str], ...] = ()


def initialize(root: Path, config_override: Path | None = None) -> dict[str, Any]:
    paths = base.root_paths(root)
    base.ensure_layout(paths)
    if paths["instance"].exists() or paths["latest"].exists():
        raise RuntimeError("world already exists; initialization never overwrites a lineage")
    config = default_config()
    if config_override is not None:
        config.update(base.load_json(config_override))
    if int(config["dimension"]) != N:
        raise ValueError("MBP2 validated preparation requires N=127")
    condition = str(config["condition"]).upper()
    condition_spec(condition)
    config["condition"] = condition
    base.atomic_json(paths["config"], config)
    session_id = f"{config['campaign_id']}-{condition}-{base.utc_now().strftime('%Y%m%dT%H%M%SZ')}"
    state = base.initial_controller(config, session_id)
    runtime, g, registry = build_x0(config)
    x0 = paths["checkpoints"] / f"X0_MBP2_{condition}.deetsnap"
    temporary = x0.with_suffix(x0.suffix + ".tmp")
    runtime.save_snapshot(str(temporary))
    checked = dee.Runtime.load_snapshot(str(temporary))
    if (int(checked.current_tick) != 0 or checked.raw_copy() != runtime.raw_copy() or
            checked.clock_copy() != runtime.clock_copy()):
        temporary.unlink(missing_ok=True)
        raise RuntimeError("X0 verification failed")
    os.replace(temporary, x0)
    base.atomic_json(x0.with_suffix(x0.suffix + ".json"), {
        "schema": WORLD_SCHEMA, "world_id": config["world_id"],
        "campaign_id": config["campaign_id"], "condition": condition,
        "session_id": session_id, "tick": 0, "role": "complete_prepared_t0",
        "created_utc": base.iso_utc(), "created_local": base.iso_local(),
        "bytes": x0.stat().st_size, "sha256": base.sha256(x0),
        "preparation": registry, "kernel": "DEE v27", "product": "DEE thinking 2.2.0",
        "host_inputs_after_t0": 0,
    })
    state["x0_checkpoint"] = str(x0.relative_to(paths["root"]))
    base.log_event(paths, state, {
        "type": "lineage_created", "tick": 0, "x0": state["x0_checkpoint"],
        "campaign_id": config["campaign_id"], "condition": condition,
        "dimension": N, "backend": config["backend"], "threads": config["threads"],
        "preparation": registry,
        "intervention_contract": "all physical participants installed at t0; no adaptive host inputs",
    })
    runtime.protocol_phase = "MBP2_T0_READY"
    seeded = base.save_checkpoint(runtime, paths, state, "seeded_t0", exact_verify=True)
    state["last_collection_checkpoint"] = str(x0.relative_to(paths["root"]))
    instance = {
        "schema": WORLD_SCHEMA, "application_version": APP_VERSION,
        "campaign_id": config["campaign_id"], "world_id": config["world_id"],
        "condition": condition, "condition_spec": condition_spec(condition),
        "session_id": session_id, "created_utc": state["created_utc"],
        "created_local": state["created_local"], "dimension": N,
        "kernel": "DEE v27", "product": "DEE thinking 2.2.0",
        "x0": str(x0.relative_to(paths["root"])),
        "seeded_checkpoint": str(seeded.relative_to(paths["root"])),
        "configuration": str(paths["config"].relative_to(paths["root"])),
        "preparation": registry,
        "provenance": {
            "infrastructure": "MENTE_BASAL_CORTE_FINAL_1000_RESULTADOS.zip",
            "scientific_design": "new MBP2 A/B/C preparation; not a continuation of MENTE-BASAL-001",
        },
    }
    base.atomic_json(paths["instance"], instance)
    base.atomic_json(paths["controller"], state)
    base.write_status(paths, state, runtime, "STOPPED_READY", "initialized; worker not running")
    return instance


_base_record_science_tick = base.record_science_tick


def record_science_tick(runtime: Any, paths: dict[str, Path], state: dict[str, Any],
                        g: Geometry) -> None:
    tick = int(runtime.current_tick)
    key = str(tick)
    already = key in state.setdefault("recorded_science_ticks", [])
    _base_record_science_tick(runtime, paths, state, g)
    if tick in (64, 144, 300) and not already:
        checkpoint = base.save_checkpoint(runtime, paths, state,
                                          f"common_tick_{tick}", exact_verify=True)
        base.log_event(paths, state, {
            "type": "common_tick_checkpoint", "tick": tick,
            "checkpoint": str(checkpoint.relative_to(paths["root"])),
        })


def locate_primary(runtime: Any, condition: str, tick: int) -> dict[str, Any]:
    predicted_site, predicted_load, predicted_direction = predicted_primary(condition, tick)
    predicted = observe_site(runtime, predicted_site)
    if predicted["s_reg"] == predicted_load and predicted["direction"] == list(predicted_direction):
        return {"method": "frozen_prediction", "ambiguous": False,
                "site": list(predicted_site), "observation": predicted}
    candidates: list[dict[str, Any]] = []
    raw = runtime.raw_copy()
    for index, value in enumerate(raw):
        if not value:
            continue
        rec = dee.decode_record(int(value))
        if int(rec.semantic) != 1:
            continue
        if int(rec.s_reg) < BASE_LOAD:
            continue
        x = index // (N * N)
        remainder = index % (N * N)
        y = remainder // N
        z = remainder % N
        candidates.append({"site": [x, y, z], "raw": int(value),
                           "s_reg": int(rec.s_reg),
                           "direction": [int(rec.dx), int(rec.dy), int(rec.dz)]})
    return {"method": "global_candidate_scan", "ambiguous": len(candidates) != 1,
            "predicted_site": list(predicted_site), "candidates": candidates}


def diagnostic_evaluate(checkpoint: Path, output: Path, condition: str | None = None) -> dict[str, Any]:
    runtime = dee.Runtime.load_snapshot(str(checkpoint))
    tick = int(runtime.current_tick)
    condition = (condition or condition_from_runtime(runtime)).upper()
    before_raw = runtime.raw_copy()
    before_clock = runtime.clock_copy()
    located = locate_primary(runtime, condition, tick)
    passive = before_raw == runtime.raw_copy() and before_clock == runtime.clock_copy()
    result: dict[str, Any] = {
        "schema": "mbp2.diagnostic.v1", "checkpoint": str(checkpoint),
        "condition": condition, "tick": tick, "observer_passive": passive,
        "located_primary": located,
        "queries": {"executed": False, "reason": "primary lineage ambiguous"},
        "interpretation_limit": "A branch response measures functional availability of retained physical history; it is not by itself learning.",
    }
    if not located.get("ambiguous") and located.get("site"):
        site = tuple(located["site"])
        observation = located["observation"]
        direction_now: Direction = tuple(observation["direction"])

        def sign_direction(a: Direction, b: Direction) -> Direction:
            values = tuple(a[i] + b[i] for i in range(3))
            return tuple(0 if value == 0 else (1 if value > 0 else -1)
                         for value in values)  # type: ignore[return-value]

        def two_use_query(name: str, first_load: int, first_direction: Direction,
                          second_load: int, second_direction: Direction) -> dict[str, Any]:
            branch = runtime.fork()
            control = runtime.fork()
            first_target = plus(site, direction_now, 4)
            after_first_direction = sign_direction(direction_now, first_direction)
            second_target = plus(first_target, after_first_direction, 4)
            first_source = plus(first_target, first_direction, -4)
            second_source = plus(second_target, second_direction, -8)
            receipts: list[int] = []
            for suffix, source, load, query_direction in (
                    ("first", first_source, first_load, first_direction),
                    ("second", second_source, second_load, second_direction)):
                channel = dee.ChannelSpec()
                channel.name = f"diagnostic.{name}.{suffix}"
                channel.injection_site = base.coordinate(source)
                channel.state = 1
                channel.direction = base.direction(query_direction)
                channel.semantic = 1
                channel.allow_experience = True
                channel.allow_probe = False
                branch.register_channel(channel)
                receipt = branch.experience(channel.name, tick, load)
                receipts.append(int(receipt.id))
            branch.advance(4)
            control.advance(4)
            first_observation = observe_site(branch, first_target)
            first_control = observe_site(control, first_target)
            branch.advance(4)
            control.advance(4)
            second_observation = observe_site(branch, second_target)
            second_control = observe_site(control, second_target)
            return {
                "mode": "isolated diagnostic forks; both query carriers installed at branch t0",
                "receipts": receipts,
                "first": {"load": first_load, "direction": list(first_direction),
                          "source": list(first_source), "target": list(first_target),
                          "with_query": first_observation, "same_history_no_query": first_control},
                "second": {"load": second_load, "direction": list(second_direction),
                           "source": list(second_source), "target": list(second_target),
                           "with_query": second_observation, "same_history_no_query": second_control},
                "main_checkpoint_unmodified": (before_raw == runtime.raw_copy() and
                                                before_clock == runtime.clock_copy()),
            }

        result["queries"] = {
            "executed": True,
            "Q_XY": two_use_query("q_xy", 7, (0, 1, 0), 5, (0, -1, 0)),
            "Q_XZ_RESERVED": two_use_query("q_xz", 4, (0, 0, 1), 6, (0, 0, -1)),
        }
    base.atomic_json(output, result)
    return result


def pilot(output: Path) -> dict[str, Any]:
    cases: dict[str, Any] = {}
    snapshots: dict[str, Any] = {}
    for condition in ("A", "B", "C"):
        cfg = default_config()
        cfg.update({"world_id": f"PILOT-{condition}", "campaign_id": "MBP2-PILOT",
                    "condition": condition})
        runtime, g, _ = build_x0(cfg)
        trace: list[dict[str, Any]] = []
        for tick in range(0, 301):
            if tick in SCIENCE_TICKS:
                trace.append({"tick": tick, "readings": science_observations(runtime, g, tick)})
            if tick < 300:
                runtime.advance(1)
        metrics = runtime.metrics()
        cases[condition] = {
            "trace": trace,
            "tick": int(runtime.current_tick), "raw_support": int(metrics.raw_support),
            "occupied": int(metrics.occupied), "s_reg_sum": int(metrics.s_reg_sum),
            "located_primary": locate_primary(runtime, condition, 300),
        }
        snapshots[condition] = (runtime.raw_copy(), runtime.clock_copy())
    basal_same = True
    cfg_a, cfg_b, cfg_c = (dict(default_config(), condition=value, world_id=f"P-{value}")
                           for value in ("A", "B", "C"))
    ra, _, _ = build_x0(cfg_a)
    rb, _, _ = build_x0(cfg_b)
    rc, _, _ = build_x0(cfg_c)
    for q in (geometry().basal_site, geometry().companion_site):
        basal_same &= (observe_site(ra, q) == observe_site(rb, q) == observe_site(rc, q))
    def reading(case: str, tick: int) -> dict[str, Any]:
        entry = next(item for item in cases[case]["trace"] if item["tick"] == tick)
        return entry["readings"]["primary_prediction"]["observed"]

    b_contacts = (
        reading("B", 15)["s_reg"] == 11 and
        reading("B", 16)["s_reg"] == 13 and
        reading("B", 16)["direction"] == [1, 1, 0] and
        reading("B", 79)["s_reg"] == 13 and
        reading("B", 80)["s_reg"] == 16 and
        reading("B", 80)["direction"] == [1, 0, 0]
    )
    a_control = all(reading("A", tick)["s_reg"] == 11 for tick in (16, 80, 144, 300))
    c_control = all(reading("C", tick)["s_reg"] == 11 for tick in (16, 80, 144, 300))
    inventory_match = (
        cases["B"]["s_reg_sum"] == cases["C"]["s_reg_sum"] == 33 and
        cases["B"]["raw_support"] == cases["C"]["raw_support"] + 2
    )
    result = {
        "schema": "mbp2.pilot.v1", "created_utc": base.iso_utc(),
        "kernel": "DEE v27", "product": "DEE thinking 2.2.0",
        "basal_initial_state_exact_at_declared_sites": basal_same,
        "cases": cases,
        "criteria": {
            "B_contact_chain_predicted": b_contacts,
            "A_isolated_lineage_retained": a_control,
            "C_same_inventory_without_contact": c_control and inventory_match,
            "B_and_C_total_s_reg_equal_after_chain": cases["B"]["s_reg_sum"] == cases["C"]["s_reg_sum"],
            "no_host_inputs_after_t0": True,
        },
        "scientific_limit": "Pilot validates physical contact and interpretable controls, not learning.",
    }
    base.atomic_json(output, result)
    return result


def self_test(root: Path, output: Path) -> dict[str, Any]:
    pilot_path = output.with_name(output.stem + "_pilot.json")
    pilot_result = pilot(pilot_path)
    cfg = dict(default_config(), campaign_id="MBP2-SELFTEST", world_id="MBP2-SELFTEST-B",
               condition="B")
    runtime, _, _ = build_x0(cfg)
    with tempfile.TemporaryDirectory(prefix="mbp2-selftest-") as temp_text:
        temp = Path(temp_text)
        middle = temp / "middle.deetsnap"
        runtime.advance(16)
        runtime.save_snapshot(str(middle))
        continuous = runtime.fork()
        continuous.advance(48)
        resumed = dee.Runtime.load_snapshot(str(middle))
        resumed.advance(48)
        save_restore_exact = (continuous.raw_copy() == resumed.raw_copy() and
                              continuous.clock_copy() == resumed.clock_copy() and
                              int(continuous.current_tick) == int(resumed.current_tick))
        before = (runtime.raw_copy(), runtime.clock_copy(), int(runtime.current_tick))
        _ = locate_primary(runtime, "B", int(runtime.current_tick))
        observer_passive = (before[0] == runtime.raw_copy() and before[1] == runtime.clock_copy()
                            and before[2] == int(runtime.current_tick))
        dense_cfg = dict(cfg)
        dense, _, _ = build_x0(dense_cfg)
        dense.execution_options = dee.TickOptions(dee.Backend.DENSE_SEQUENTIAL, 1)
        dense.advance(17)
        lazy_reference, _, _ = build_x0(dense_cfg)
        lazy_reference.advance(17)
        dense_exact = (dense.raw_copy() == lazy_reference.raw_copy() and
                       dense.clock_copy() == lazy_reference.clock_copy())
    criteria = pilot_result["criteria"]
    checks = {
        "pilot_B_contact_chain": bool(criteria["B_contact_chain_predicted"]),
        "basal_common": bool(pilot_result["basal_initial_state_exact_at_declared_sites"]),
        "save_load_continue_exact": save_restore_exact,
        "mobile_reader_passive": observer_passive,
        "dense_matches_lazy_t17_contact_boundary": dense_exact,
    }
    result = {"schema": "mbp2.selftest.v1", "created_utc": base.iso_utc(),
              "checks": checks, "all_passed": all(checks.values()),
              "pilot": str(pilot_path)}
    base.atomic_json(output, result)
    return result


def install_hooks() -> None:
    base.APP_VERSION = APP_VERSION
    base.WORLD_SCHEMA = WORLD_SCHEMA
    base.DEFAULT_WORLD_ID = "MBP2-UNSET"
    base.N = N
    base.T_REF = 0
    base.Geometry = Geometry
    base.geometry = geometry
    base.default_config = default_config
    base.build_x0 = build_x0
    base.science_observations = science_observations
    base.write_telemetry = write_telemetry
    base.INITIAL_INPUTS = INITIAL_INPUTS
    base.LATE_INPUTS = LATE_INPUTS
    base.SCIENCE_TICKS = SCIENCE_TICKS
    base.initialize = initialize
    base.record_science_tick = record_science_tick
    base.evaluate_checkpoint = lambda checkpoint, output: diagnostic_evaluate(checkpoint, output)
    base.self_test = self_test


def cli() -> int:
    install_hooks()
    if len(sys.argv) > 1 and sys.argv[1] in {"pilot", "diagnose"}:
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="command", required=True)
        pilot_p = sub.add_parser("pilot")
        pilot_p.add_argument("--output", type=Path, required=True)
        diag_p = sub.add_parser("diagnose")
        diag_p.add_argument("--checkpoint", type=Path, required=True)
        diag_p.add_argument("--output", type=Path, required=True)
        diag_p.add_argument("--condition", choices=("A", "B", "C"))
        args = parser.parse_args()
        if args.command == "pilot":
            result = pilot(args.output)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0 if result["criteria"]["B_contact_chain_predicted"] else 1
        result = diagnostic_evaluate(args.checkpoint, args.output, args.condition)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    return base.cli()


if __name__ == "__main__":
    raise SystemExit(cli())
