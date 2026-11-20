from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import json
import sys
from pathlib import Path


def coordinate(index: int, n: int) -> tuple[int, int, int]:
    plane = n * n
    return index // plane, (index % plane) // n, index % n


def record_dict(dee, raw: int, index: int, n: int) -> dict:
    record = dee.decode_record(raw)
    return {
        "index": index,
        "coordinate": list(coordinate(index, n)),
        "raw": int(raw),
        "state": int(record.state),
        "s_reg": int(record.s_reg),
        "direction": [int(record.dx), int(record.dy), int(record.dz)],
        "semantic": int(record.semantic),
        "occupied": bool(record.occupied),
        "raw_present": bool(record.raw_present),
    }


def active_records(dee, raw: list[int], n: int) -> list[dict]:
    return [record_dict(dee, value, index, n)
            for index, value in enumerate(raw) if value != 0]


def profile(records: list[dict]) -> dict:
    return {
        "raw_support": len(records),
        "occupied": sum(bool(item["occupied"]) for item in records),
        "s_reg_sum": sum(int(item["s_reg"]) for item in records),
        "s_reg_values": sorted(int(item["s_reg"]) for item in records),
        "directions": dict(sorted(collections.Counter(
            str(tuple(item["direction"])) for item in records).items())),
        "semantics": dict(sorted(collections.Counter(
            str(item["semantic"]) for item in records).items())),
        "states": dict(sorted(collections.Counter(
            str(item["state"]) for item in records).items())),
    }


def find_component(records: list[dict], s_reg: int, direction: tuple[int, int, int]) -> list[dict]:
    return [item for item in records
            if item["s_reg"] == s_reg and tuple(item["direction"]) == direction]


def parse_utc(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--previous", type=Path, required=True)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root / "app"))
    import habitat

    previous = habitat.load_json(args.previous)
    current = habitat.load_json(args.current)
    start_path = root / current["start_checkpoint"]
    end_path = root / current["end_checkpoint"]
    start = habitat.dee.Runtime.load_snapshot(str(start_path))
    end = habitat.dee.Runtime.load_snapshot(str(end_path))
    n = int(start.dimension)
    if int(end.dimension) != n:
        raise RuntimeError("dimension changed across cut")
    raw_start = start.raw_copy()
    raw_end = end.raw_copy()
    clock_start = start.clock_copy()
    clock_end = end.clock_copy()
    start_records = active_records(habitat.dee, raw_start, n)
    end_records = active_records(habitat.dee, raw_end, n)

    changed_raw: list[int] = []
    added: list[int] = []
    removed: list[int] = []
    transformed: list[int] = []
    for index, (before, after) in enumerate(zip(raw_start, raw_end)):
        if before == after:
            continue
        changed_raw.append(index)
        if before == 0:
            added.append(index)
        elif after == 0:
            removed.append(index)
        else:
            transformed.append(index)
    modulus = int(habitat.dee.KERNEL_MODULUS)
    clock_delta = collections.Counter(
        (int(after) - int(before)) % modulus
        for before, after in zip(clock_start, clock_end)
    )
    clock_changed = sum(before != after for before, after in zip(clock_start, clock_end))

    history_path = root / current["history_segment"]
    events = [json.loads(line) for line in history_path.read_text(encoding="utf-8").splitlines()
              if line.strip()]
    event_types = collections.Counter(str(item.get("type", "")) for item in events)
    advances = [item for item in events if item.get("type") == "advance"]
    advances.sort(key=lambda item: (int(item["from_tick"]), int(item["to_tick"])))
    gaps = []
    cursor = int(current["start_tick"])
    for item in advances:
        before = int(item["from_tick"])
        after = int(item["to_tick"])
        if before != cursor:
            gaps.append({"expected_from": cursor, "actual_from": before, "to": after})
        cursor = max(cursor, after)
    if cursor != int(current["end_tick"]):
        gaps.append({"expected_end": int(current["end_tick"]), "logged_end": cursor})
    inputs = [item for item in events if item.get("type") == "input_scheduled"]
    receipt_updates = [item for item in events if item.get("type") == "receipt_status"]
    commands = [item for item in events if item.get("type") == "command_received"]
    errors = [item for item in events if item.get("type") in
              ("command_rejected", "safe_stop", "worker_failure")]
    restarts = [item for item in events if item.get("type") in
                ("worker_started", "worker_stopped")]

    telemetry_path = root / current["telemetry_segment"]
    with telemetry_path.open("r", encoding="utf-8", newline="") as stream:
        telemetry = list(csv.DictReader(stream))
    telemetry_changes = []
    previous_sum = None
    for row in telemetry:
        value = int(row["s_reg_sum"])
        if previous_sum is None or value != previous_sum:
            telemetry_changes.append({
                "tick": int(row["tick"]), "s_reg_sum": value,
                "raw_support": int(row["raw_support"]),
                "occupied": int(row["occupied"]), "note": row["note"],
            })
        previous_sum = value

    start_utc = parse_utc(previous["created_utc"])
    end_utc = parse_utc(current["created_utc"])
    elapsed = (end_utc - start_utc).total_seconds()
    tick_delta = int(current["end_tick"]) - int(current["start_tick"])
    checkpoint_sidecars = []
    for sidecar in (root / "world" / "checkpoints").glob("*.deetsnap.json"):
        metadata = habitat.load_json(sidecar)
        created = parse_utc(metadata["created_utc"])
        if start_utc < created <= end_utc:
            checkpoint_sidecars.append({
                "path": str(sidecar.relative_to(root)).replace("\\", "/"),
                "tick": int(metadata["tick"]), "reason": metadata["reason"],
                "created_utc": metadata["created_utc"],
            })
    checkpoint_sidecars.sort(key=lambda item: (item["created_utc"], item["path"]))

    support_states = set(range(9300, 9336)) | set(range(9700, 9706))
    start_support = [item for item in start_records if item["state"] in support_states]
    end_support = [item for item in end_records if item["state"] in support_states]
    start_environment = [item for item in start_records
                         if item["coordinate"] in [[82, 91, 48], [82, 91, 52],
                                                    [82, 91, 56], [82, 91, 60]]]
    end_environment = [item for item in end_records
                       if item["coordinate"] in [[82, 91, 48], [82, 91, 52],
                                                  [82, 91, 56], [82, 91, 60]]]
    components = {
        "relational_lineage_4184": {
            "start": find_component(start_records, 4184, (1, 1, 0)),
            "end": find_component(end_records, 4184, (1, 1, 0)),
        },
        "mobile_matter_result_68": {
            "start": find_component(start_records, 68, (0, 1, 1)),
            "end": find_component(end_records, 68, (0, 1, 1)),
        },
        "context_result_40": {
            "start": find_component(start_records, 40, (1, 0, 1)),
            "end": find_component(end_records, 40, (1, 0, 1)),
        },
        "stationary_environment_residues": {
            "start": start_environment, "end": end_environment,
        },
        "semantic4_support": {
            "start_count": len(start_support), "end_count": len(end_support),
            "exact_records_preserved": start_support == end_support,
        },
    }
    result = {
        "schema": "mente-basal.cut-interval-analysis.v1",
        "world_id": current["world_id"], "session_id": current["session_id"],
        "start": {"tick": current["start_tick"], "utc": previous["created_utc"],
                  "local": previous["created_local"], "checkpoint": current["start_checkpoint"]},
        "end": {"tick": current["end_tick"], "utc": current["created_utc"],
                "local": current["created_local"], "checkpoint": current["end_checkpoint"]},
        "elapsed_human_seconds": elapsed,
        "ticks_elapsed": tick_delta,
        "average_ticks_per_second": tick_delta / elapsed,
        "raw_comparison": {
            "total_sites": len(raw_start), "changed_sites": len(changed_raw),
            "unchanged_sites": len(raw_start) - len(changed_raw),
            "added_sites": len(added), "removed_sites": len(removed),
            "transformed_in_place": len(transformed),
            "changed_coordinates": [list(coordinate(index, n)) for index in changed_raw],
            "added_coordinates": [list(coordinate(index, n)) for index in added],
            "removed_coordinates": [list(coordinate(index, n)) for index in removed],
            "transformed_coordinates": [list(coordinate(index, n)) for index in transformed],
        },
        "clock_comparison": {
            "changed_sites": clock_changed,
            "unchanged_sites": len(clock_start) - clock_changed,
            "modulo": modulus,
            "modular_delta_histogram": dict(sorted(
                ((str(key), value) for key, value in clock_delta.items()),
                key=lambda item: int(item[0]))),
            "interpretation_guard": "uniform clock advance is not counted as learning",
        },
        "start_profile": profile(start_records), "end_profile": profile(end_records),
        "start_active_records": start_records, "end_active_records": end_records,
        "components": components,
        "history": {
            "path": current["history_segment"], "event_count": len(events),
            "event_types": dict(sorted(event_types.items())),
            "advance_records": len(advances),
            "first_advance_tick": int(advances[0]["from_tick"]) if advances else None,
            "last_advance_tick": int(advances[-1]["to_tick"]) if advances else None,
            "advance_gaps_or_overlaps": gaps,
            "kernel_total_ns": sum(int(item["kernel_total_ns"]) for item in advances),
            "wall_ns_logged": sum(int(item["wall_ns"]) for item in advances),
            "inputs_scheduled": len(inputs), "receipt_updates": len(receipt_updates),
            "commands": [{"tick": item.get("tick"), "operation": item.get("operation"),
                          "utc": item.get("utc")} for item in commands],
            "errors": errors, "worker_start_stop_events": restarts,
        },
        "telemetry": {
            "path": current["telemetry_segment"], "rows": len(telemetry),
            "first": telemetry[0] if telemetry else None,
            "last": telemetry[-1] if telemetry else None,
            "s_reg_change_points": telemetry_changes,
        },
        "checkpoints_created_in_interval": checkpoint_sidecars,
        "checkpoint_count": len(checkpoint_sidecars),
        "external_physical_inputs_after_Tref": len(inputs),
        "receipt_changes_after_Tref": len(receipt_updates),
        "operational_interventions": [item.get("operation") for item in commands],
        "classification": {
            "persistence": ["relational load 4184", "mobile-matter load 68",
                            "context load 40", "30 semantic-4 supports"],
            "displacement": ["4184, 68 and 40 followed their declared toroidal directions"],
            "reorganization": ["four stationary environmental residues changed s_reg 0 to 344"],
            "loss": [], "new_external_experience": [],
            "functional_change": ["recurrent in-place accumulation at four environment residues"],
            "learning_claim": "not established by this interval analysis",
        },
    }
    habitat.atomic_json(args.output, result)
    print(json.dumps({
        "output": str(args.output), "ticks_elapsed": tick_delta,
        "changed_raw_sites": len(changed_raw), "clock_changed_sites": clock_changed,
        "inputs_after_Tref": len(inputs), "checkpoint_count": len(checkpoint_sidecars),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
