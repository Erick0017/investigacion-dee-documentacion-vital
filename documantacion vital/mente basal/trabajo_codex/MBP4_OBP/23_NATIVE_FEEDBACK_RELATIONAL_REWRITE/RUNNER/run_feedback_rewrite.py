from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import dee_thinking as dee


N = 47
SECTION = "23_NATIVE_FEEDBACK_RELATIONAL_REWRITE"
PARENT_SHA256 = "b794f690433b8c090fed2784e3a7bf682683b226420aee60b3d40cf6ef4b484f"
MOORE = tuple(
    (dx, dy, dz)
    for dx in (-1, 0, 1)
    for dy in (-1, 0, 1)
    for dz in (-1, 0, 1)
    if (dx, dy, dz) != (0, 0, 0)
)
TETRA = (
    ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1)),
    ((-1, 0, 0), (0, 1, 0), (0, 0, 1), (-1, 1, 1)),
    ((1, 0, 0), (0, -1, 0), (0, 0, 1), (1, -1, 1)),
    ((1, 0, 0), (0, 1, 0), (0, 0, -1), (1, 1, -1)),
    ((-1, 0, 0), (0, -1, 0), (0, 0, 1), (-1, -1, 1)),
    ((-1, 0, 0), (0, 1, 0), (0, 0, -1), (-1, 1, -1)),
    ((1, 0, 0), (0, -1, 0), (0, 0, -1), (1, -1, -1)),
    ((-1, 0, 0), (0, -1, 0), (0, 0, -1), (-1, -1, -1)),
)


def add(q: tuple[int, int, int], d: tuple[int, int, int], k: int = 1) -> tuple[int, int, int]:
    return tuple((q[i] + k * d[i]) % N for i in range(3))  # type: ignore[return-value]


def index(q: tuple[int, int, int]) -> int:
    return (q[0] * N + q[1]) * N + q[2]


def record(raw: int) -> dict[str, Any] | None:
    if not raw:
        return None
    r = dee.decode_record(int(raw))
    return {
        "raw": int(raw), "state": int(r.state), "s_reg": int(r.s_reg),
        "direction": [int(r.dx), int(r.dy), int(r.dz)], "semantic": int(r.semantic),
    }


def alive(raw: int) -> bool:
    r = record(raw)
    return r is not None and int(r["state"]) > 0 and int(r["semantic"]) != 5


def sample_write_gate(raw: list[int], clocks: list[int], site: tuple[int, int, int]) -> dict[str, Any]:
    center = record(raw[index(site)])
    neighbors = []
    sum_direction = [0, 0, 0]
    n_active = 0
    for offset in MOORE:
        q = add(site, offset)
        value = int(raw[index(q)])
        item = record(value)
        if alive(value):
            n_active += 1
            assert item is not None
            for axis in range(3):
                sum_direction[axis] += int(item["direction"][axis])
        if item is not None:
            neighbors.append({"offset": list(offset), "site": list(q), **item})
    tetra_pattern = None
    for pattern_id, pattern in enumerate(TETRA):
        if all(alive(int(raw[index(add(site, offset))])) for offset in pattern):
            tetra_pattern = pattern_id
            break
    hadron = tetra_pattern is not None
    incomplete = n_active < 7
    tension = 16.0 if hadron and incomplete else 2.5
    rule_value = int(math.floor((n_active * tension / 26.0) + 0.5))
    symmetric = sum_direction == [0, 0, 0]
    write_protected = n_active >= 7 and symmetric
    k = 8 - n_active
    period = 782 // k if 0 < k <= 8 else None
    clock = int(clocks[index(site)])
    phase_remainder = None if period is None else clock % period
    write_gate_open = (
        center is not None and int(center["semantic"]) != 4 and rule_value != 0
        and not write_protected and period is not None and phase_remainder == 0
    )
    return {
        "site": list(site), "clock": clock, "record": center,
        "n_active": n_active, "sum_direction": sum_direction,
        "tetra_pattern": tetra_pattern, "hadron": hadron,
        "rule_value": rule_value, "survival": rule_value != 0,
        "protected": bool(center and int(center["semantic"]) == 4),
        "write_protected": write_protected, "k": k, "period": period,
        "phase_remainder": phase_remainder, "write_gate_open": write_gate_open,
        "neighbors": neighbors,
    }


def load_section22(package_root: Path) -> tuple[Any, Any, Any]:
    runner = package_root / "22_TRANSFORMATIVE_GENEALOGY_RELATIONAL_CONSOLIDATION" / "RUNNER"
    if str(runner) not in sys.path:
        sys.path.insert(0, str(runner))
    import relational_body
    return relational_body.build_relational_body, relational_body.body_sample, relational_body


def baseline_gate_trace(package_root: Path, horizon: int = 600, mode: str = "FULL") -> dict[str, Any]:
    build_relational_body, body_sample, _ = load_section22(package_root)
    runtime, ports, audit = build_relational_body(
        package_root, (15, 15, 15), "AB", 5, mode, "lazy"
    )
    rows = []
    previous = None
    for relative_tick in range(0, horizon + 1):
        raw, clocks = list(runtime.raw_copy()), list(runtime.clock_copy())
        a = sample_write_gate(raw, clocks, ports.a)
        b = sample_write_gate(raw, clocks, ports.b)
        sample = body_sample(runtime, ports, relative_tick)
        signature = (
            a["n_active"], a["period"], a["phase_remainder"], a["record"]["s_reg"],
            b["n_active"], b["period"], b["phase_remainder"], b["record"]["s_reg"],
            sample["axis_projection"],
        )
        if relative_tick <= 32 or signature != previous or a["write_gate_open"] or b["write_gate_open"]:
            rows.append({
                "relative_tick": relative_tick, "absolute_tick": int(runtime.current_tick),
                "delta": sample["delta"], "axis_projection": sample["axis_projection"],
                "a": {k: v for k, v in a.items() if k != "neighbors"},
                "b": {k: v for k, v in b.items() if k != "neighbors"},
            })
        previous = signature
        if relative_tick < horizon:
            runtime.advance(1)
    return {
        "horizon": horizon, "mode": mode,
        "post_t0_host_writes": audit.post_t0_writes,
        "rows": rows,
    }


def transient_reader_gate_trace(package_root: Path, horizon: int = 600) -> dict[str, Any]:
    build_relational_body, body_sample, relational = load_section22(package_root)
    prepared, ports, audit = build_relational_body(
        package_root, (15, 15, 15), "AB", 5, "BARE", "lazy"
    )
    raw, clocks = list(prepared.raw_copy()), list(prepared.clock_copy())
    source_i = index(ports.reader_source)
    prior = record(raw[source_i])
    raw[source_i] = int(dee.pack_record(6000, 7, 0, 1, 0, 1))
    runtime = relational.runtime_from(raw, clocks, int(prepared.current_tick), "lazy")
    rows = []
    previous = None
    for relative_tick in range(0, horizon + 1):
        current_raw, current_clocks = list(runtime.raw_copy()), list(runtime.clock_copy())
        a = sample_write_gate(current_raw, current_clocks, ports.a)
        b = sample_write_gate(current_raw, current_clocks, ports.b)
        sample = body_sample(runtime, ports, relative_tick)
        signature = (
            a["n_active"], a["period"], a["phase_remainder"], a["record"]["s_reg"],
            b["n_active"], b["period"], b["phase_remainder"], b["record"]["s_reg"],
            sample["axis_projection"],
        )
        if relative_tick <= 40 or signature != previous or a["write_gate_open"] or b["write_gate_open"]:
            rows.append({
                "relative_tick": relative_tick, "absolute_tick": int(runtime.current_tick),
                "delta": sample["delta"], "axis_projection": sample["axis_projection"],
                "a": {k: v for k, v in a.items() if k != "neighbors"},
                "b": {k: v for k, v in b.items() if k != "neighbors"},
            })
        previous = signature
        if relative_tick < horizon:
            runtime.advance(1)
    return {
        "horizon": horizon,
        "pre_t0_reader_replacement": {"site": list(ports.reader_source), "prior": prior,
                                       "replacement_semantic": 1},
        "post_t0_host_writes": audit.post_t0_writes,
        "rows": rows,
    }


def put_pre(raw: list[int], clocks: list[int], site: tuple[int, int, int], *,
            state: int, s_reg: int, direction: tuple[int, int, int], semantic: int,
            clock: int, label: str, preparation: list[dict[str, Any]],
            replace: bool = False) -> None:
    i = index(site)
    prior = record(raw[i])
    if prior is not None and not replace:
        raise RuntimeError(f"feedback preparation overlap {label} at {site}: {prior}")
    raw[i] = int(dee.pack_record(state, s_reg, *direction, semantic))
    clocks[i] = int(clock) & ((1 << 64) - 1)
    preparation.append({
        "label": label, "site": list(site), "prior": prior,
        "record": record(raw[i]), "clock": int(clocks[i]),
    })


def build_feedback_candidate(package_root: Path, control: str = "FULL",
                             backend: str = "lazy",
                             origin: tuple[int, int, int] = (15, 15, 15)) -> tuple[Any, Any, dict[str, Any]]:
    build_relational_body, _, relational = load_section22(package_root)
    prepared, ports, inherited_audit = build_relational_body(
        package_root, origin, "AB", 5, "BARE", backend
    )
    raw, clocks = list(prepared.raw_copy()), list(prepared.clock_copy())
    prep: list[dict[str, Any]] = []

    # The renewed semantic=4 reader from section 22 is replaced before T0 by a
    # single physical query.  It crosses the comparator only after AB is written.
    reader_i = index(ports.reader_source)
    reader_prior = record(raw[reader_i])
    raw[reader_i] = 0
    clocks[reader_i] = 0
    query_site = add(ports.origin, (0, -1, 0))
    prep.append({"label": "renewed_reader_removed", "site": list(ports.reader_source),
                 "prior": reader_prior, "record": None, "clock": 0})
    if control == "NO_ACTION":
        prep.append({"label": "no_action.query_omitted", "site": list(query_site),
                     "prior": None, "record": None, "clock": None})
    else:
        put_pre(raw, clocks, query_site, state=6000, s_reg=7,
                direction=(0, 1, 0), semantic=5, clock=23,
                label="single_orphan_query", preparation=prep)
    put_pre(raw, clocks, add(ports.origin, (0, 1, 0)), state=6099, s_reg=0,
            direction=(0, 0, 0), semantic=5, clock=29,
            label="pre_relational_output_absorber", preparation=prep)

    # Absorb the two history carriers after they have performed their declared
    # initial interaction, preventing toroidal recurrences from crowding A/B.
    history_sinks = (add(ports.origin, (-1, -1, -10)),
                     add(ports.origin, (1, 1, 10)))
    for number, site in enumerate(history_sinks):
        put_pre(raw, clocks, site, state=8100 + number, s_reg=0,
                direction=(0, 0, 0), semantic=4, clock=61 + number,
                label=f"history_sink.{number}", preparation=prep)

    # Causal route with no earlier contact at A/B:
    # query -> action(t=18) -> +z[36] -> bend1(t=54) -> (+x,+y)[40]
    # -> bend2(t=94) -> (+x,+y,-z)[37] -> selected neighbour(t=131).
    # The first arrival therefore coincides with A.clock=391 and n_active=6.
    c = ports.origin
    d = 16
    phase_shift = 1 if control == "PHASE_MISS" else 0
    first_reader_arrival = 2 + d + phase_shift
    action_site = add(c, (1, 1, 0), d)
    action_turn = (-1, -1, 1)
    action_source = add(action_site, action_turn, -first_reader_arrival)
    first_leg = 36
    bend_site = add(action_site, (0, 0, 1), first_leg)
    bend_arrival = first_reader_arrival + first_leg
    bend_aux_direction = (1, 1, -1)
    middle_direction = (1, 1, 0)
    bend_source_a = add(bend_site, bend_aux_direction, -bend_arrival)
    middle_leg = 40
    bend2_site = add(bend_site, middle_direction, middle_leg)
    bend2_arrival = bend_arrival + middle_leg
    bend2_aux_direction = (-1, 0, -1) if control == "OFF_PATH" else (0, 0, -1)
    return_direction = (0, 1, -1) if control == "OFF_PATH" else (1, 1, -1)
    bend_source_b = add(bend2_site, bend2_aux_direction, -bend2_arrival)
    target_arrival = 131 + phase_shift
    return_steps = 37
    return_target = add(bend2_site, return_direction, return_steps)

    # A semantic=5, zero-load causal envelope prevents incidental toroidal
    # recurrences from occupying unused A/B-neighbour ports.  It is excluded
    # from n_active by v27 and leaves the declared history, comparator, action
    # route, and selected feedback port physically open.
    keep_open = {
        ports.a, ports.b, ports.comparator, query_site, return_target,
        add(ports.origin, (-1, -1, 0)), add(ports.origin, (1, 1, -1)),
        add(ports.origin, (1, 1, 0)),
        *ports.supports,
    }
    envelope_sites: list[tuple[int, int, int]] = []
    for center in (ports.a, ports.b):
        for offset in MOORE:
            site = add(center, offset)
            if site in keep_open or raw[index(site)] != 0:
                continue
            put_pre(raw, clocks, site, state=8200 + len(envelope_sites), s_reg=0,
                    direction=(0, 0, 0), semantic=5, clock=67,
                    label=f"causal_envelope.{len(envelope_sites)}", preparation=prep)
            envelope_sites.append(site)

    put_pre(raw, clocks, action_source, state=7101, s_reg=11,
            direction=action_turn, semantic=4, clock=31,
            label="feedback.action_turn_source", preparation=prep)
    put_pre(raw, clocks, bend_source_a, state=7201, s_reg=13,
            direction=bend_aux_direction, semantic=1, clock=41,
            label="feedback.bend_source_a", preparation=prep)
    if control != "RETURN_CUT":
        put_pre(raw, clocks, bend_source_b, state=7301, s_reg=17,
                direction=bend2_aux_direction, semantic=1, clock=47,
                label="feedback.bend_source_b", preparation=prep)
    else:
        prep.append({"label": "feedback.return_cut.bend2_source_omitted",
                     "site": list(bend_source_b), "prior": None,
                     "record": None, "clock": None})

    runtime = relational.runtime_from(raw, clocks, int(prepared.current_tick), backend)
    metadata = {
        "control": control, "backend": backend, "t0_tick": int(runtime.current_tick),
        "post_t0_host_writes": int(inherited_audit.post_t0_writes),
        "preparation": prep, "action_site": list(action_site),
        "query_site": list(query_site),
        "action_source": list(action_source), "first_reader_arrival": first_reader_arrival,
        "bend_site": list(bend_site), "bend_arrival": bend_arrival,
        "bend_sources": [list(bend_source_a), list(bend_source_b)],
        "bend_aux_direction": list(bend_aux_direction), "bend1_aux_first_arrival": 8,
        "first_leg": first_leg,
        "middle_direction": list(middle_direction), "middle_leg": middle_leg,
        "bend2_site": list(bend2_site), "bend2_arrival": bend2_arrival,
        "bend2_aux_direction": list(bend2_aux_direction), "bend2_aux_first_arrival": 2,
        "return_direction": list(return_direction), "return_steps": return_steps,
        "return_target": list(return_target), "target_arrival": target_arrival,
        "history_sinks": [list(x) for x in history_sinks],
        "causal_envelope": [list(x) for x in envelope_sites],
    }
    return runtime, ports, metadata


def candidate_trace(package_root: Path, control: str = "FULL", horizon: int = 170,
                    backend: str = "lazy",
                    origin: tuple[int, int, int] = (15, 15, 15)) -> dict[str, Any]:
    _, body_sample, _ = load_section22(package_root)
    runtime, ports, metadata = build_feedback_candidate(package_root, control, backend, origin)
    rows = []
    previous = None
    special = {
        "action": tuple(metadata["action_site"]),
        "bend": tuple(metadata["bend_site"]),
        "bend2": tuple(metadata["bend2_site"]),
        "return_target": tuple(metadata["return_target"]),
    }
    for relative_tick in range(0, horizon + 1):
        raw, clocks = list(runtime.raw_copy()), list(runtime.clock_copy())
        a = sample_write_gate(raw, clocks, ports.a)
        b = sample_write_gate(raw, clocks, ports.b)
        sample = body_sample(runtime, ports, relative_tick)
        loci = {name: record(raw[index(site)]) for name, site in special.items()}
        route_probe = None
        if metadata["first_reader_arrival"] <= relative_tick <= metadata["bend_arrival"]:
            route_probe = record(raw[index(add(tuple(metadata["action_site"]), (0, 0, 1),
                                                   relative_tick - metadata["first_reader_arrival"]))])
        elif metadata["bend_arrival"] <= relative_tick <= metadata["bend2_arrival"]:
            route_probe = record(raw[index(add(tuple(metadata["bend_site"]),
                                                   tuple(metadata["middle_direction"]),
                                                   relative_tick - metadata["bend_arrival"]))])
        elif metadata["bend2_arrival"] <= relative_tick <= metadata["target_arrival"]:
            route_probe = record(raw[index(add(tuple(metadata["bend2_site"]),
                                                   tuple(metadata["return_direction"]),
                                                   relative_tick - metadata["bend2_arrival"]))])
        signature = (
            a["n_active"], a["record"]["s_reg"], b["n_active"], b["record"]["s_reg"],
            sample["axis_projection"], *(None if x is None else (x["s_reg"], tuple(x["direction"]))
                                        for x in loci.values()),
        )
        if (relative_tick <= 12 or relative_tick in range(40, 49)
                or relative_tick in range(84, 91) or relative_tick in range(126, 134)
                or relative_tick in {140, 150, 160, horizon}
                or signature != previous or a["write_gate_open"] or b["write_gate_open"]):
            rows.append({
                "relative_tick": relative_tick, "absolute_tick": int(runtime.current_tick),
                "delta": sample["delta"], "axis_projection": sample["axis_projection"],
                "a": {k: v for k, v in a.items() if k != "neighbors"},
                "b": {k: v for k, v in b.items() if k != "neighbors"},
                "loci": loci,
                "route_probe": route_probe,
                **({"a_neighbors": a["neighbors"], "b_neighbors": b["neighbors"]}
                   if relative_tick in {1, 17, 53, 93, 129, 130, 131} else {}),
            })
        previous = signature
        if relative_tick < horizon:
            runtime.advance(1)
    metadata["final_tick"] = int(runtime.current_tick)
    metadata["final_sample"] = body_sample(runtime, ports, horizon)
    return {"metadata": metadata, "rows": rows}


def trace_feedback_lineage(package_root: Path, horizon: int = 170) -> dict[str, Any]:
    """Directed replay of the already-selected FULL candidate.

    This is deliberately not a global event detector.  It follows only the
    loads created by the declared query/action route (18, 31, 42 and their
    subsequent sums) so that an unexpected native collision can be located
    without changing the Runtime or scanning a parameter grid.
    """
    runtime, ports, metadata = build_feedback_candidate(package_root, "FULL", "lazy")
    rows: list[dict[str, Any]] = []
    prior: set[tuple[int, int, int, int, int, int, int]] = set()
    for relative_tick in range(horizon + 1):
        raw = list(runtime.raw_copy())
        carriers: list[dict[str, Any]] = []
        for linear, value in enumerate(raw):
            item = record(int(value))
            if item is None or int(item["semantic"]) != 1 or int(item["state"]) <= 0:
                continue
            load = int(item["s_reg"])
            # Load 7 is the relational readout/action carrier; loads >=18 are
            # descendants of the selected feedback route.  Other low loads
            # are preparations/parents and are intentionally excluded.
            if load != 7 and load < 18:
                continue
            x, rem = divmod(linear, N * N)
            y, z = divmod(rem, N)
            carriers.append({"site": [x, y, z], **item})
        signature = {
            (c["site"][0], c["site"][1], c["site"][2], int(c["state"]),
             int(c["s_reg"]), int(c["direction"][0]), int(c["direction"][1]) * 3
             + int(c["direction"][2]))
            for c in carriers
        }
        if signature != prior or relative_tick in {0, 18, 54, 65, 94, 131, horizon}:
            clocks = list(runtime.clock_copy())
            rows.append({
                "relative_tick": relative_tick,
                "absolute_tick": int(runtime.current_tick),
                "carriers": carriers,
                "a": {k: v for k, v in sample_write_gate(raw, clocks, ports.a).items()
                      if k != "neighbors"},
                "b": {k: v for k, v in sample_write_gate(raw, clocks, ports.b).items()
                      if k != "neighbors"},
            })
        prior = signature
        if relative_tick < horizon:
            runtime.advance(1)
    return {"metadata": metadata, "rows": rows}


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def save_checkpoint(runtime: Any, section: Path, name: str) -> dict[str, Any]:
    path = section / "CHECKPOINTS" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    runtime.set_snapshot_metadata("mbp4.campaign", "MBP4-NATIVE-FEEDBACK-RELATIONAL-REWRITE")
    runtime.set_snapshot_metadata("mbp4.section", SECTION)
    runtime.save_snapshot(str(path))
    return {
        "path": path.relative_to(section).as_posix(),
        "tick": int(runtime.current_tick),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def frozen_config() -> dict[str, Any]:
    return {
        "schema": "mbp4.native-feedback-relational-rewrite.experiment-config.v1",
        "campaign": "MBP4-NATIVE-FEEDBACK-RELATIONAL-REWRITE",
        "parent_zip_sha256": PARENT_SHA256,
        "kernel": "DEE Universe v27 (frozen)",
        "runtime": "DEE thinking 2.2.0",
        "dimension": N,
        "backend": "lazy",
        "origin": [15, 15, 15],
        "history": "AB",
        "controls": ["FULL", "NO_ACTION", "RETURN_CUT", "OFF_PATH", "PHASE_MISS"],
        "holdout_origins": [[22, 20, 24], [28, 26, 18]],
        "horizon": 170,
        "write_window": [129, 133],
        "retention_ticks": [150, 170],
        "post_t0_host_policy": ["advance", "passive read", "save checkpoint"],
        "adapter_status_at_freeze": "partial_chain_action_and_first_bend_confirmed",
        "selected_route": {
            "history_acquisition": 1,
            "action": 18,
            "first_bend": 54,
            "native_unplanned_redirect": 65,
            "planned_second_bend": 94,
            "planned_return_target": 131,
        },
        "selection_basis": (
            "finite directed search: action-dependent relational change observed; "
            "RETURN_CUT remained equal to FULL, so return attribution was not promoted"
        ),
        "frozen_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
    }


def run_frozen_case(package_root: Path, control: str, origin: tuple[int, int, int],
                    horizon: int, section: Path | None = None,
                    checkpoint_main: bool = False,
                    backend: str = "lazy") -> dict[str, Any]:
    _, body_sample, _ = load_section22(package_root)
    runtime, ports, metadata = build_feedback_candidate(package_root, control, backend, origin)
    checkpoints: list[dict[str, Any]] = []
    checkpoint_times = {
        0: "MAIN_T0.deetsnap",
        1: "INITIAL_HISTORY_ACQUIRED.deetsnap",
        131: "BEFORE_WRITE_OPPORTUNITY.deetsnap",
        132: "AFTER_POSSIBLE_REWRITE.deetsnap",
        150: "RETENTION_READOUT.deetsnap",
        horizon: "MAIN_FINAL.deetsnap",
    }
    rows: list[dict[str, Any]] = []
    transition_audits: list[dict[str, Any]] = []
    write_events: list[dict[str, Any]] = []
    previous: dict[str, Any] | None = None
    special = {
        "action": tuple(metadata["action_site"]),
        "first_bend": tuple(metadata["bend_site"]),
        "planned_second_bend": tuple(metadata["bend2_site"]),
        "planned_return_target": tuple(metadata["return_target"]),
        "native_redirect": (42, 42, 4),
    }
    for relative_tick in range(horizon + 1):
        raw, clocks = list(runtime.raw_copy()), list(runtime.clock_copy())
        sample = body_sample(runtime, ports, relative_tick)
        a = sample_write_gate(raw, clocks, ports.a)
        b = sample_write_gate(raw, clocks, ports.b)
        loci = {name: record(raw[index(site)]) for name, site in special.items()}
        row = {
            "relative_tick": relative_tick,
            "absolute_tick": int(runtime.current_tick),
            "delta": sample["delta"],
            "axis_projection": sample["axis_projection"],
            "a": {key: value for key, value in a.items() if key != "neighbors"},
            "b": {key: value for key, value in b.items() if key != "neighbors"},
            "loci": loci,
        }
        rows.append(row)
        if previous is not None:
            for label in ("a", "b"):
                before = previous[label]["record"]["s_reg"]
                after = row[label]["record"]["s_reg"]
                if before != after:
                    write_events.append({
                        "site": label.upper(), "transition": [relative_tick - 1, relative_tick],
                        "before": before, "after": after,
                        "gate_before": previous[label],
                    })
        previous = row
        if checkpoint_main and section is not None and relative_tick in checkpoint_times:
            checkpoints.append(save_checkpoint(runtime, section, checkpoint_times[relative_tick]))
        if checkpoint_main and relative_tick in {64, 131}:
            load_section22(package_root)
            import genealogy_tracker
            audit, _ = genealogy_tracker.analyze_transition(
                runtime, special["native_redirect"] if relative_tick == 64 else ports.b
            )
            audit["relative_tick"] = relative_tick
            transition_audits.append(audit)
        if relative_tick < horizon:
            runtime.advance(1)
    metadata.update({
        "origin": list(origin), "horizon": horizon,
        "post_t0_host_writes_measured": 0,
        "final_tick": int(runtime.current_tick),
    })
    return {
        "metadata": metadata,
        "rows": rows,
        "write_events": write_events,
        "transition_audits": transition_audits,
        "checkpoints": checkpoints,
        "final": rows[-1],
    }


def compact_case(case: dict[str, Any]) -> dict[str, Any]:
    at = {row["relative_tick"]: row for row in case["rows"]}
    points = {}
    for tick in (0, 1, 18, 54, 65, 94, 129, 130, 131, 132, 150, 170):
        if tick in at:
            row = at[tick]
            points[str(tick)] = {
                "absolute_tick": row["absolute_tick"], "delta": row["delta"],
                "axis_projection": row["axis_projection"],
                "a_s_reg": row["a"]["record"]["s_reg"],
                "b_s_reg": row["b"]["record"]["s_reg"],
                "a_n_active": row["a"]["n_active"],
                "b_n_active": row["b"]["n_active"],
                "a_gate": row["a"]["write_gate_open"],
                "b_gate": row["b"]["write_gate_open"],
                "loci": row["loci"],
            }
    return {
        "control": case["metadata"]["control"],
        "origin": case["metadata"]["origin"],
        "post_t0_host_writes": case["metadata"]["post_t0_host_writes_measured"],
        "points": points,
        "write_events": case["write_events"],
        "final": case["final"],
    }


def technical_checks(package_root: Path, section: Path) -> dict[str, Any]:
    # Passive observation equivalence.
    observed, ports, _ = build_feedback_candidate(package_root, "FULL", "lazy")
    direct, _, _ = build_feedback_candidate(package_root, "FULL", "lazy")
    for _ in range(70):
        raw, clocks = list(observed.raw_copy()), list(observed.clock_copy())
        sample_write_gate(raw, clocks, ports.a)
        sample_write_gate(raw, clocks, ports.b)
        observed.advance(1)
    direct.advance(70)
    observer_equal = (
        list(observed.raw_copy()) == list(direct.raw_copy())
        and list(observed.clock_copy()) == list(direct.clock_copy())
    )

    lazy, _, _ = build_feedback_candidate(package_root, "FULL", "lazy")
    dense, _, _ = build_feedback_candidate(package_root, "FULL", "dense")
    lazy.advance(70)
    dense.advance(70)
    backend_equal = (
        list(lazy.raw_copy()) == list(dense.raw_copy())
        and list(lazy.clock_copy()) == list(dense.clock_copy())
    )

    boundary, _, _ = build_feedback_candidate(package_root, "FULL", "lazy")
    boundary.advance(85)
    boundary_meta = save_checkpoint(boundary, section, "RESUME_BOUNDARY.deetsnap")
    boundary.advance(85)
    resumed = dee.Runtime.load_snapshot(str(section / boundary_meta["path"]))
    resumed.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)
    resumed.advance(85)
    resume_equal = (
        int(boundary.current_tick) == int(resumed.current_tick)
        and list(boundary.raw_copy()) == list(resumed.raw_copy())
        and list(boundary.clock_copy()) == list(resumed.clock_copy())
    )
    loaded = dee.Runtime.load_snapshot(str(section / boundary_meta["path"]))
    snapshot_valid = int(loaded.current_tick) == int(boundary_meta["tick"])
    return {
        "passive_observer_raw_clock_equal": observer_equal,
        "lazy_dense_raw_clock_equal_at_70": backend_equal,
        "save_load_continuation_raw_clock_equal": resume_equal,
        "snapshot_boundary_loadable": snapshot_valid,
        "boundary": boundary_meta,
    }


def write_reproduction(section: Path) -> None:
    text = """# Reproducción técnica — sección 23

Desde la raíz extraída del paquete, use el Python 3.13 donde está instalado
`dee_thinking==2.2.0`:

```powershell
python -I -B .\\23_NATIVE_FEEDBACK_RELATIONAL_REWRITE\\RUNNER\\run_feedback_rewrite.py `
  --package-root . --validate-only
```

Para reproducir la campaña congelada en una copia aislada:

```powershell
python -I -B .\\23_NATIVE_FEEDBACK_RELATIONAL_REWRITE\\RUNNER\\run_feedback_rewrite.py `
  --package-root . --run-campaign
```

El runner no modifica v27 ni las secciones heredadas. Las escrituras de
preparación ocurren antes de T0; después sólo avanza, observa y guarda.
`RETURN_CUT` es el control que impide atribuir al retorno la escritura B
observada en esta preparación.
"""
    (section / "README_REPRODUCCION.md").write_text(text, encoding="utf-8")


def run_campaign(package_root: Path) -> dict[str, Any]:
    section = package_root / SECTION
    section.mkdir(parents=True, exist_ok=True)
    config = frozen_config()
    write_json(section / "EXPERIMENT_CONFIG.json", config)

    main = run_frozen_case(package_root, "FULL", tuple(config["origin"]),
                           int(config["horizon"]), section, True)
    controls: dict[str, Any] = {"FULL": compact_case(main)}
    for control in config["controls"][1:]:
        controls[control] = compact_case(run_frozen_case(
            package_root, control, tuple(config["origin"]), int(config["horizon"])
        ))

    holdouts = []
    for number, origin in enumerate(config["holdout_origins"], 1):
        try:
            full = run_frozen_case(package_root, "FULL", tuple(origin),
                                   int(config["horizon"]))
            cut = run_frozen_case(package_root, "RETURN_CUT", tuple(origin),
                                  int(config["horizon"]))
            holdouts.append({
                "holdout_id": f"H{number}", "origin": origin,
                "FULL": compact_case(full), "RETURN_CUT": compact_case(cut),
            })
        except Exception as exc:
            holdouts.append({"holdout_id": f"H{number}", "origin": origin,
                             "execution_error": f"{type(exc).__name__}: {exc}"})

    technical = technical_checks(package_root, section)
    trace_rows = [
        row for row in main["rows"]
        if row["relative_tick"] <= 3
        or row["relative_tick"] in range(16, 20)
        or row["relative_tick"] in range(52, 67)
        or row["relative_tick"] in range(128, 134)
        or row["relative_tick"] in {94, 150, 170}
    ]
    write_json(section / "TELEMETRY" / "WRITE_GATE_TRACE.json", {
        "coverage": "direct local A/B sampling at selected causal windows",
        "rows": trace_rows,
    })
    write_json(section / "TELEMETRY" / "FEEDBACK_CAUSAL_CHAIN.json", {
        "direct_observations": {
            "history_acquired_relative_tick": 1,
            "action_carrier_relative_tick": 18,
            "first_bend_relative_tick": 54,
            "native_redirect_relative_tick": 65,
            "planned_second_bend_present_at_94": bool(main["rows"][94]["loci"]["planned_second_bend"]),
            "planned_return_target_present_at_131": bool(main["rows"][131]["loci"]["planned_return_target"]),
        },
        "transition_audits": main["transition_audits"],
        "causal_boundary": (
            "action and first bend observed; the selected lineage did not reach the planned "
            "second bend/return target; B write also occurred in RETURN_CUT"
        ),
    })
    write_json(section / "TELEMETRY" / "MATCHED_CONTROLS.json", controls)
    write_json(section / "TELEMETRY" / "POST_WRITE_READOUT.json", {
        "protocol": "same continued native evolution; no post-T0 host query/write",
        "FULL": {key: controls["FULL"]["points"][key] for key in ("131", "132", "150", "170")},
        "RETURN_CUT": {key: controls["RETURN_CUT"]["points"][key]
                       for key in ("131", "132", "150", "170")},
        "interpretive_limit": "no return-specific later response established",
    })
    write_json(section / "TELEMETRY" / "HOLDOUTS.json", holdouts)
    write_json(section / "TELEMETRY" / "TECHNICAL_CHECKS.json", technical)

    full = controls["FULL"]["points"]
    cut = controls["RETURN_CUT"]["points"]
    final_checkpoint = next(item for item in main["checkpoints"]
                            if item["path"].endswith("MAIN_FINAL.deetsnap"))
    summary = {
        "schema": "mbp4.native-feedback-relational-rewrite.run-summary.v1",
        "campaign": config["campaign"],
        "parent_zip_sha256": PARENT_SHA256,
        "preparations_confirmed": 1,
        "controls_executed": config["controls"],
        "holdouts_executed": len(holdouts),
        "post_t0_host_writes_measured": 0,
        "write_opportunities_observed": {
            "FULL": controls["FULL"]["write_events"],
            "RETURN_CUT": controls["RETURN_CUT"]["write_events"],
        },
        "delta": {
            "FULL_pre": full["131"]["delta"], "FULL_post": full["132"]["delta"],
            "FULL_retained_170": full["170"]["delta"],
            "RETURN_CUT_pre": cut["131"]["delta"], "RETURN_CUT_post": cut["132"]["delta"],
            "RETURN_CUT_retained_170": cut["170"]["delta"],
        },
        "later_response": {
            "FULL_axis_projection_170": full["170"]["axis_projection"],
            "RETURN_CUT_axis_projection_170": cut["170"]["axis_projection"],
            "return_specific_difference_confirmed": False,
        },
        "reuse_observed": False,
        "causal_chain_status": "partial_cut_before_planned_return",
        "closure_reason": (
            "finite directed candidate budget closed without a return-dependent relational rewrite; "
            "the exact negative/partial result and matched controls are retained"
        ),
        "checkpoints": main["checkpoints"],
        "main_final_checkpoint": final_checkpoint,
        "technical_checks": technical,
        "completed_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
    }
    write_json(section / "RUN_SUMMARY.json", summary)
    write_reproduction(section)
    return summary


def section_files(section: Path) -> list[Path]:
    return sorted(
        (path for path in section.rglob("*")
         if path.is_file() and "__pycache__" not in path.parts and path.name != "HASHES.sha256"),
        key=lambda path: path.relative_to(section).as_posix(),
    )


def validate_section(package_root: Path) -> dict[str, Any]:
    section = package_root / SECTION
    summary = json.loads((section / "RUN_SUMMARY.json").read_text(encoding="utf-8"))
    required = [
        "EXPERIMENT_CONFIG.json", "RUN_SUMMARY.json", "README_REPRODUCCION.md",
        "RUNNER/run_feedback_rewrite.py", "CHECKPOINTS/MAIN_T0.deetsnap",
        "CHECKPOINTS/INITIAL_HISTORY_ACQUIRED.deetsnap",
        "CHECKPOINTS/BEFORE_WRITE_OPPORTUNITY.deetsnap",
        "CHECKPOINTS/AFTER_POSSIBLE_REWRITE.deetsnap",
        "CHECKPOINTS/RETENTION_READOUT.deetsnap", "CHECKPOINTS/MAIN_FINAL.deetsnap",
        "TELEMETRY/WRITE_GATE_TRACE.json", "TELEMETRY/FEEDBACK_CAUSAL_CHAIN.json",
        "TELEMETRY/MATCHED_CONTROLS.json", "TELEMETRY/POST_WRITE_READOUT.json",
        "TELEMETRY/HOLDOUTS.json", "TELEMETRY/TECHNICAL_CHECKS.json",
    ]
    missing = [name for name in required if not (section / name).is_file()]
    snapshots = []
    for path in sorted((section / "CHECKPOINTS").glob("*.deetsnap")):
        runtime = dee.Runtime.load_snapshot(str(path))
        snapshots.append({"name": path.name, "tick": int(runtime.current_tick),
                          "sha256": sha256_file(path)})
    checks = summary["technical_checks"]
    technical_true = all(bool(checks[key]) for key in (
        "passive_observer_raw_clock_equal", "lazy_dense_raw_clock_equal_at_70",
        "save_load_continuation_raw_clock_equal", "snapshot_boundary_loadable",
    ))
    result = {"missing": missing, "snapshots": snapshots,
              "technical_checks_true": technical_true}
    if missing or not technical_true:
        raise RuntimeError(f"section validation failed: {result}")
    return result


def package_append(package_root: Path, canonical_zip: Path) -> dict[str, Any]:
    if sha256_file(canonical_zip) != PARENT_SHA256:
        raise RuntimeError("canonical ZIP is not the expected 249-member parent")
    section = package_root / SECTION
    files = section_files(section)
    hash_text = "\n".join(
        f"{sha256_file(path)}  {path.relative_to(section).as_posix()}" for path in files
    ) + "\n"
    (section / "HASHES.sha256").write_text(hash_text, encoding="utf-8")
    files.append(section / "HASHES.sha256")
    fd, tmp_name = tempfile.mkstemp(prefix="mbp4_section23_", suffix=".zip", dir=str(package_root))
    os.close(fd)
    temporary = Path(tmp_name)
    inherited: dict[str, str] = {}
    try:
        with zipfile.ZipFile(canonical_zip, "r") as parent:
            infos = parent.infolist()
            if len(infos) != 249:
                raise RuntimeError(f"expected 249 inherited members, found {len(infos)}")
            if any(f"/{SECTION}/" in item.filename for item in infos):
                raise RuntimeError("parent already contains section 23")
            inherited = {item.filename: hashlib.sha256(parent.read(item)).hexdigest()
                         for item in infos}
            wrapper = infos[0].filename.split("/", 1)[0]
            with zipfile.ZipFile(temporary, "w", allowZip64=True) as output:
                for item in infos:
                    output.writestr(item, parent.read(item))
                for path in files:
                    name = f"{wrapper}/{SECTION}/{path.relative_to(section).as_posix()}"
                    output.write(path, name, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        with zipfile.ZipFile(temporary, "r") as check:
            bad = check.testzip()
            if bad is not None:
                raise RuntimeError(f"ZIP CRC failure: {bad}")
            for name, expected in inherited.items():
                if hashlib.sha256(check.read(name)).hexdigest() != expected:
                    raise RuntimeError(f"inherited member changed: {name}")
            hash_name = f"{wrapper}/{SECTION}/HASHES.sha256"
            for line in check.read(hash_name).decode("utf-8").splitlines():
                expected, relative = line.split("  ", 1)
                name = f"{wrapper}/{SECTION}/{relative}"
                if hashlib.sha256(check.read(name)).hexdigest() != expected:
                    raise RuntimeError(f"section hash mismatch: {relative}")
        os.replace(temporary, canonical_zip)
    finally:
        if temporary.exists():
            temporary.unlink()
    return {
        "parent_zip_sha256": PARENT_SHA256,
        "inherited_members_verified_byte_exact": len(inherited),
        "section_files": len(files), "section_hashes_verified": True,
        "crc_error": None, "final_zip_sha256": sha256_file(canonical_zip),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--diagnose-baseline", action="store_true")
    parser.add_argument("--diagnose-transient-reader", action="store_true")
    parser.add_argument("--diagnose-feedback", action="store_true")
    parser.add_argument("--trace-lineage", action="store_true")
    parser.add_argument("--run-campaign", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--package", action="store_true")
    parser.add_argument("--package-existing", action="store_true")
    parser.add_argument("--canonical-zip", type=Path)
    parser.add_argument("--control", choices=("FULL", "NO_ACTION", "RETURN_CUT", "OFF_PATH", "PHASE_MISS"), default="FULL")
    parser.add_argument("--horizon", type=int, default=600)
    parser.add_argument("--mode", choices=("FULL", "BARE"), default="FULL")
    args = parser.parse_args()
    package_root = args.package_root.resolve()
    section = package_root / SECTION
    if args.package_existing:
        if args.canonical_zip is None:
            parser.error("--package-existing requires --canonical-zip")
        result = {"validation": validate_section(package_root),
                  "package": package_append(package_root, args.canonical_zip.resolve())}
        print(json.dumps(result, sort_keys=True))
        return
    if args.validate_only:
        print(json.dumps(validate_section(package_root), sort_keys=True))
        return
    if args.run_campaign:
        summary = run_campaign(package_root)
        result: dict[str, Any] = {"summary": summary, "validation": validate_section(package_root)}
        if args.package:
            if args.canonical_zip is None:
                parser.error("--package requires --canonical-zip")
            result["package"] = package_append(package_root, args.canonical_zip.resolve())
        print(json.dumps(result, sort_keys=True))
        return
    if args.diagnose_baseline:
        result = baseline_gate_trace(package_root, args.horizon, args.mode)
        suffix = "" if args.mode == "FULL" else f"_{args.mode}"
        write_json(section / "TELEMETRY" / f"BASELINE_WRITE_GATE_DISCOVERY{suffix}.json", result)
        print(json.dumps({"rows": len(result["rows"]), "horizon": result["horizon"]}))
        return
    if args.diagnose_transient_reader:
        result = transient_reader_gate_trace(package_root, args.horizon)
        write_json(section / "TELEMETRY" / "TRANSIENT_READER_GATE_DISCOVERY.json", result)
        print(json.dumps({"rows": len(result["rows"]), "horizon": result["horizon"]}))
        return
    if args.diagnose_feedback:
        result = candidate_trace(package_root, args.control, args.horizon)
        write_json(section / "TELEMETRY" / f"FEEDBACK_DISCOVERY_{args.control}.json", result)
        print(json.dumps({"control": args.control, "rows": len(result["rows"]),
                          "final": result["metadata"]["final_sample"]}))
        return
    if args.trace_lineage:
        result = trace_feedback_lineage(package_root, args.horizon)
        write_json(section / "TELEMETRY" / "FEEDBACK_ROUTE_LINEAGE.json", result)
        print(json.dumps({"rows": len(result["rows"]), "horizon": args.horizon}))
        return
    parser.error("select an execution mode")


if __name__ == "__main__":
    main()
