from __future__ import annotations

import argparse
import gc
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any


N = 127
MASK64 = (1 << 64) - 1
MOORE = tuple(
    (dx, dy, dz)
    for dx in (-1, 0, 1)
    for dy in (-1, 0, 1)
    for dz in (-1, 0, 1)
    if (dx, dy, dz) != (0, 0, 0)
)
SUPPORT_OFFSETS = (
    (1, -1, -1), (1, -1, 0), (1, -1, 1),
    (1, 0, -1), (1, 0, 0), (1, 0, 1),
)


def add(a: tuple[int, int, int], b: tuple[int, int, int], scale: int = 1) -> tuple[int, int, int]:
    return tuple((a[i] + b[i] * scale) % N for i in range(3))  # type: ignore[return-value]


def idx(q: tuple[int, int, int]) -> int:
    return (q[0] * N + q[1]) * N + q[2]


def xyz(index: int) -> tuple[int, int, int]:
    x, rest = divmod(index, N * N)
    y, z = divmod(rest, N)
    return x, y, z


def record_dict(dee: Any, raw: int, coordinate: tuple[int, int, int], clock: int) -> dict[str, Any]:
    record = dee.decode_record(int(raw))
    return {
        "coordinate": list(coordinate), "raw": int(raw), "clock": int(clock),
        "state": int(record.state), "s_reg": int(record.s_reg),
        "direction": [int(record.dx), int(record.dy), int(record.dz)],
        "semantic": int(record.semantic), "occupied": bool(record.occupied),
        "raw_present": int(raw) != 0,
    }


def observe(dee: Any, runtime: Any, q: tuple[int, int, int]) -> dict[str, Any]:
    value = runtime.observe(dee.Coordinate(*q))
    record = value.record
    return {
        "coordinate": list(q), "raw": int(value.raw), "clock": int(value.clock),
        "state": int(record.state), "s_reg": int(record.s_reg),
        "direction": [int(record.dx), int(record.dy), int(record.dz)],
        "semantic": int(record.semantic), "occupied": bool(record.occupied),
        "raw_present": int(value.raw) != 0,
    }


def find_anchor(dee: Any, runtime: Any, load: int, expected_direction: tuple[int, int, int]) -> list[dict[str, Any]]:
    raw = runtime.raw_copy()
    clock = runtime.clock_copy()
    found: list[dict[str, Any]] = []
    for linear, value in enumerate(raw):
        if not value:
            continue
        record = dee.decode_record(int(value))
        direction = (int(record.dx), int(record.dy), int(record.dz))
        if int(record.s_reg) == load and direction == expected_direction:
            found.append(record_dict(dee, int(value), xyz(linear), int(clock[linear])))
    return found


def make_channel(dee: Any, name: str, site: tuple[int, int, int], state: int,
                 travel_direction: tuple[int, int, int], semantic: int = 1) -> Any:
    channel = dee.ChannelSpec()
    channel.name = name
    channel.injection_site = dee.Coordinate(*site)
    channel.state = state
    channel.direction = dee.Direction(*travel_direction)
    channel.semantic = semantic
    channel.allow_experience = True
    channel.allow_probe = False
    return channel


def schedule(dee: Any, runtime: Any, name: str, target: tuple[int, int, int],
             arrival: int, injection: int, direction: tuple[int, int, int],
             state: int, load: int) -> Any:
    source = add(target, direction, -(arrival - injection))
    runtime.register_channel(make_channel(dee, name, source, state, direction))
    return runtime.experience(name, injection, load)


def receipt_dict(runtime: Any, receipt: Any) -> dict[str, Any]:
    final = runtime.receipt(receipt.id)
    return {
        "id": int(final.id), "kind": str(final.kind), "status": str(final.status),
        "requested_tick": int(final.requested_tick),
        "effective_tick": None if final.effective_tick is None else int(final.effective_tick),
        "channels": list(final.channels), "reason": str(final.reason),
    }


def load_physical_arrays(dee: Any, checkpoint: Path) -> tuple[int, list[int], list[int]]:
    runtime = dee.Runtime.load_snapshot(str(checkpoint))
    return int(runtime.current_tick), runtime.raw_copy(), runtime.clock_copy()


def imported_runtime(dee: Any, tick: int, raw: list[int], clock: list[int], backend: str) -> Any:
    runtime = dee.Runtime.import_research_state(N, tick, raw, clock)
    selected = dee.Backend.LAZY if backend == "lazy" else dee.Backend.DENSE_SEQUENTIAL
    runtime.execution_options = dee.TickOptions(selected, 1)
    runtime.protocol_phase = "OBSERVACION_ACOPLAMIENTO_003_DIAGNOSTIC"
    runtime.resume()
    return runtime


def run_until_traced(runtime: Any, dee: Any, end_tick: int,
                     sites: dict[str, tuple[int, int, int]], key_ticks: set[int]) -> tuple[dict[str, Any], dict[str, int]]:
    trace: dict[str, Any] = {}
    counters = {"overflows": 0, "genesis": 0, "evaluated": 0, "fallback_ticks": 0}
    while int(runtime.current_tick) <= end_tick:
        current = int(runtime.current_tick)
        if current in key_ticks:
            trace[str(current)] = {name: observe(dee, runtime, q) for name, q in sites.items()}
        if current == end_tick:
            break
        info = runtime.advance(1)
        counters["overflows"] += int(info.overflows)
        counters["genesis"] += int(info.genesis)
        counters["evaluated"] += int(info.evaluated)
        counters["fallback_ticks"] += int(bool(info.fallback))
    return trace, counters


def functional_40_case(dee: Any, parent: Path, output_dir: Path, case: str,
                       backend: str, save_snapshot: bool) -> dict[str, Any]:
    tick, raw, clock = load_physical_arrays(dee, parent)
    parent_runtime = dee.Runtime.load_snapshot(str(parent))
    anchors = find_anchor(dee, parent_runtime, 40, (1, 0, 1))
    if len(anchors) != 1:
        raise RuntimeError(f"expected one mobile 40 anchor, found {len(anchors)}")
    p = tuple(anchors[0]["coordinate"])
    q = add(p, (1, 0, 1), 4)
    r = add(q, (1, 1, 1), 4)
    interventions: list[dict[str, Any]] = []
    if case == "MEDIATOR_ABSENT":
        raw[idx(p)] = 0
        interventions.append({"type": "diagnostic_ablation", "coordinate": list(p), "removed": "mobile content 40"})
    runtime = imported_runtime(dee, tick, raw, clock, backend)
    receipts = []
    probe_arrival = tick + (5 if case == "TEMPORAL_SHAM" else 4)
    probe_load = 0 if case == "ZERO_SHAM" else 7
    receipts.append(schedule(dee, runtime, f"f40.{case}.probe", q, probe_arrival, tick,
                             (0, 1, 0), 99101, probe_load))
    receipts.append(schedule(dee, runtime, f"f40.{case}.use", r, tick + 8, tick,
                             (-1, 0, 0), 99102, 5))
    sites = {"P": p, "Q": q, "R": r}
    trace, counters = run_until_traced(runtime, dee, tick + 9, sites,
                                       {tick, tick + 4, tick + 5, tick + 8, tick + 9})
    final_receipts = [receipt_dict(runtime, item) for item in receipts]
    snapshot = None
    if save_snapshot:
        snapshot_path = output_dir / f"functional40_{case}_{backend}_t{tick + 9}.deetsnap"
        runtime.save_snapshot(str(snapshot_path))
        snapshot = str(snapshot_path)
    return {
        "case": case, "backend": backend, "parent_tick": tick,
        "mode": "diagnostic branch; externally prepared query; HOST_STOP after scheduling",
        "anchor": anchors[0], "P": list(p), "Q": list(q), "R": list(r),
        "interventions": interventions, "receipts": final_receipts,
        "trace": trace, "tick_counters": counters, "snapshot": snapshot,
    }


def coupling_case(dee: Any, parent: Path, output_dir: Path, case: str,
                  backend: str, save_snapshot: bool) -> dict[str, Any]:
    tick, raw, clock = load_physical_arrays(dee, parent)
    parent_runtime = dee.Runtime.load_snapshot(str(parent))
    anchors = find_anchor(dee, parent_runtime, 40, (1, 0, 1))
    if len(anchors) != 1:
        raise RuntimeError("mobile content 40 is not uniquely identifiable")
    p = tuple(anchors[0]["coordinate"])
    # At an untouched empty site clock==global tick.  Nine steps reach the
    # next multiple of 391 for the OBS_003_REF parent.
    phase_delay = (-int(clock[idx(p)])) % 391
    if phase_delay == 0:
        phase_delay = 391
    environment = add(p, (1, 0, 1), phase_delay)
    demux = add(environment, (-1, -1, -1))
    query_target = add(demux, (0, 4, 0)) if case == "QUERY_SHAM" else demux
    return_site = add(demux, (0, 0, 4))
    use1_site = add(return_site, (4, 0, 4))
    redirect_site = add(use1_site, (4, 4, 4))
    use2_site = add(redirect_site, (0, 4, 4))
    support_sites = [add(environment, offset) for offset in SUPPORT_OFFSETS]
    if any(raw[idx(site)] != 0 for site in [environment, demux, return_site, use1_site, redirect_site, use2_site] + support_sites):
        raise RuntimeError("coupling preparation is not empty in parent state")
    installed_supports = support_sites if case != "SUPPORT_CUT" else support_sites[:-1]
    for i, site in enumerate(installed_supports):
        raw[idx(site)] = int(dee.pack_record(99300 + i, 0, 0, 0, 0, 4))
    runtime = imported_runtime(dee, tick, raw, clock, backend)
    event_tick = tick + phase_delay + 1
    bias_load = 19623 if case == "SUBTHRESHOLD" else 19624
    bias_arrival = tick + phase_delay
    receipts = [
        schedule(dee, runtime, f"coupling.{case}.bias", environment, bias_arrival, tick,
                 (0, 0, -1), 99201, bias_load),
        schedule(dee, runtime, f"coupling.{case}.query", query_target, event_tick, tick,
                 (0, 0, 1), 99202, 23),
        schedule(dee, runtime, f"coupling.{case}.partner", return_site, event_tick + 4, tick,
                 (1, 0, 0), 99203, 31),
        schedule(dee, runtime, f"coupling.{case}.use1", use1_site, event_tick + 8, tick,
                 (0, 1, 0), 99204, 7),
        schedule(dee, runtime, f"coupling.{case}.redirect", redirect_site, event_tick + 12, tick,
                 (-1, 0, 0), 99205, 0),
        schedule(dee, runtime, f"coupling.{case}.use2", use2_site, event_tick + 16, tick,
                 (1, 0, 0), 99206, 5),
    ]
    sites = {
        "P": p, "environment": environment, "demux": demux,
        "query_target": query_target, "return": return_site,
        "use1": use1_site, "redirect": redirect_site, "use2": use2_site,
    }
    key_ticks = {
        tick, bias_arrival, event_tick, event_tick + 1,
        event_tick + 4, event_tick + 8, event_tick + 12, event_tick + 16,
    }
    trace, counters = run_until_traced(runtime, dee, event_tick + 17, sites, key_ticks)
    final_receipts = [receipt_dict(runtime, item) for item in receipts]
    snapshot = None
    if save_snapshot:
        snapshot_path = output_dir / f"coupling_{case}_{backend}_t{event_tick + 17}.deetsnap"
        runtime.save_snapshot(str(snapshot_path))
        snapshot = str(snapshot_path)
    return {
        "case": case, "backend": backend, "parent_tick": tick,
        "mode": "diagnostic branch with declared generic support/participants; HOST_STOP after scheduling",
        "mobile_40_anchor": anchors[0], "phase_delay": phase_delay,
        "bias_arrival_tick": bias_arrival, "demux_event_tick": event_tick,
        "sites": {name: list(site) for name, site in sites.items()},
        "installed_supports": [list(site) for site in installed_supports],
        "support_count": len(installed_supports), "bias_load": bias_load,
        "receipts": final_receipts, "trace": trace,
        "tick_counters": counters, "snapshot": snapshot,
        "interpretation_guard": "supports and participants were installed by the investigator; only subsequent transitions are native v27",
    }


def clock_audit(dee: Any, start_checkpoint: Path, end_checkpoint: Path) -> dict[str, Any]:
    start = dee.Runtime.load_snapshot(str(start_checkpoint))
    end = dee.Runtime.load_snapshot(str(end_checkpoint))
    start_tick, end_tick = int(start.current_tick), int(end.current_tick)
    expected = end_tick - start_tick
    before, after = start.clock_copy(), end.clock_copy()
    histogram: Counter[int] = Counter()
    anomalies: list[dict[str, int]] = []
    for linear, (a, b) in enumerate(zip(before, after)):
        delta = (int(b) - int(a)) & MASK64
        histogram[delta] += 1
        if delta != expected and len(anomalies) < 32:
            anomalies.append({"index": linear, "before": int(a), "after": int(b), "delta": delta})
    return {
        "start_tick": start_tick, "end_tick": end_tick, "expected_full_delta": expected,
        "site_count": len(before), "lengths_equal": len(before) == len(after),
        "full_uint64_delta_histogram": {str(k): v for k, v in sorted(histogram.items())},
        "all_exact": len(histogram) == 1 and histogram.get(expected) == len(before),
        "anomalies_first_32": anomalies,
        "p_kernel": int(dee.KERNEL_MODULUS),
        "contextual_phase_residue_only": expected % int(dee.KERNEL_MODULUS),
        "correction": "P_KERNEL is not the clock modulus; the previous 16802 value was only a contextual residue",
    }


def cadence_audit(dee: Any, parent_checkpoint: Path) -> dict[str, Any]:
    runtime = dee.Runtime.load_snapshot(str(parent_checkpoint))
    tick = int(runtime.current_tick)
    centers = ((82, 91, 48), (82, 91, 52), (82, 91, 56), (82, 91, 60))
    rows = []
    for center in centers:
        site = observe(dee, runtime, center)
        neighbors = [observe(dee, runtime, add(center, offset)) for offset in MOORE]
        alive = [item for item in neighbors if item["state"] > 0 and item["semantic"] != 5]
        n_active = len(alive)
        missing = 8 - n_active
        period = 782 // missing if 0 < missing <= 8 else None
        vector_sum = [sum(item["direction"][axis] for item in alive) for axis in range(3)]
        write_protected = n_active >= 7 and vector_sum == [0, 0, 0]
        next_output = None
        if period and not write_protected:
            next_output = tick + ((-site["clock"]) % period) + 1
        remaining_events = 19665 - site["s_reg"]
        overflow_tick = None if next_output is None else next_output + (remaining_events - 1) * period
        rows.append({
            "center": list(center), "record": site, "n_active": n_active,
            "active_neighbors": alive, "vector_sum": vector_sum,
            "write_protected": write_protected, "missing_anchors": missing,
            "period_ticks": period, "next_increment_output_tick": next_output,
            "events_to_overflow": remaining_events,
            "predicted_overflow_tick_if_guards_persist": overflow_tick,
        })
    return {
        "parent_tick": tick, "residues": rows,
        "rule": "period_ticks = 782 // (8 - n_active), with survival and !write_protected guards",
        "world_cycle_claim": False,
    }


def mobile_audit(dee: Any, checkpoints: list[Path]) -> dict[str, Any]:
    specifications = {
        "relational_4184": (4184, (1, 1, 0)),
        "material_68": (68, (0, 1, 1)),
        "context_40": (40, (1, 0, 1)),
    }
    rows = []
    origins: dict[str, tuple[int, tuple[int, int, int]]] = {}
    for checkpoint in checkpoints:
        runtime = dee.Runtime.load_snapshot(str(checkpoint))
        tick = int(runtime.current_tick)
        observations = {}
        for name, (load, direction) in specifications.items():
            found = find_anchor(dee, runtime, load, direction)
            observations[name] = found
            if name not in origins and len(found) == 1:
                origins[name] = (tick, tuple(found[0]["coordinate"]))
            if name in origins and len(found) == 1:
                origin_tick, origin_position = origins[name]
                predicted = add(origin_position, direction, tick - origin_tick)
                found[0]["toroidal_prediction"] = list(predicted)
                found[0]["prediction_exact"] = list(predicted) == found[0]["coordinate"]
        rows.append({"checkpoint": str(checkpoint), "tick": tick, "observations": observations})
    return {"identification": "initial load+direction anchors plus toroidal prediction; external metadata only", "cuts": rows}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--parent", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    parent = args.parent.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(root / "app"))
    import habitat
    dee = habitat.dee

    t64 = root / "world/checkpoints/tick_000000000064_collect_SESSION_001_REF_0853e180.deetsnap"
    tcut2 = root / "world/checkpoints/tick_000000134856_collect_CUT_002_762afc79.deetsnap"
    started = time.perf_counter()
    result: dict[str, Any] = {
        "schema": "mente-basal.observation-coupling-003.v1",
        "world_id": "MENTE-BASAL-001", "parent_checkpoint": str(parent),
        "clock_audit": clock_audit(dee, t64, tcut2),
        "mobile_observer": mobile_audit(dee, [t64, tcut2, parent]),
        "cadence": cadence_audit(dee, parent),
        "functional_40": [], "environmental_coupling": [],
    }
    gc.collect()
    for case in ("INTACT", "TEMPORAL_SHAM", "ZERO_SHAM", "MEDIATOR_ABSENT"):
        result["functional_40"].append(
            functional_40_case(dee, parent, output_dir, case, "lazy", case == "INTACT"))
        gc.collect()
    for case in ("INTACT", "SUBTHRESHOLD", "QUERY_SHAM", "SUPPORT_CUT"):
        result["environmental_coupling"].append(
            coupling_case(dee, parent, output_dir, case, "lazy", case == "INTACT"))
        gc.collect()

    # Dense confirmations use the same frozen parent and protocol.
    result["functional_40"].append(
        functional_40_case(dee, parent, output_dir, "INTACT", "dense", False))
    gc.collect()
    result["environmental_coupling"].append(
        coupling_case(dee, parent, output_dir, "INTACT", "dense", False))
    result["elapsed_seconds"] = time.perf_counter() - started
    output = output_dir / "OBSERVATION_COUPLING_003_RESULTS.json"
    habitat.atomic_json(output, result)
    print(json.dumps({"output": str(output), "elapsed_seconds": result["elapsed_seconds"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
