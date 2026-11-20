from __future__ import annotations

import argparse
import array
import gzip
import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path
from typing import Any

import dee_thinking as dee


SECTION = "24_CONTEXTUAL_CAUSAL_MECHANISM"
PARENT_SHA256 = "10c0cd5754b71d9c865de983c64f8ffc989cb8da4d33c61d804c1429416b310e"
N = 47
BASE_ORIGIN = (15, 15, 15)
HORIZON = 170
WRAPPER = "MENTE_BASAL_4_ORGANIZACION_BASAL_PERSISTENTE_VALIDACION_RESULTADOS"


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_section23(package_root: Path) -> Any:
    runner = package_root / "23_NATIVE_FEEDBACK_RELATIONAL_REWRITE" / "RUNNER"
    if str(runner) not in sys.path:
        sys.path.insert(0, str(runner))
    import run_feedback_rewrite
    return run_feedback_rewrite


def translate(site: tuple[int, int, int], origin: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple((site[i] + origin[i] - BASE_ORIGIN[i]) % N for i in range(3))  # type: ignore[return-value]


def clone_with_edit(runtime: Any, site: tuple[int, int, int], operation: str,
                    s23: Any) -> tuple[Any, dict[str, Any]]:
    if runtime.channel_names or runtime.receipts:
        raise RuntimeError("diagnostic import would discard live channels/receipts")
    raw, clocks = list(runtime.raw_copy()), list(runtime.clock_copy())
    linear = s23.index(site)
    before_raw = int(raw[linear])
    before = s23.record(before_raw)
    if before is None:
        raise RuntimeError(f"intervention target absent at {site}")
    if operation in {"ACT_REMOVE", "ENV42_REMOVE"}:
        raw[linear] = 0
    else:
        state = int(before["state"])
        load = int(before["s_reg"])
        direction = tuple(int(x) for x in before["direction"])
        semantic = int(before["semantic"])
        if operation == "ACT_LOAD_MINUS":
            load -= 1
        elif operation == "ACT_LOAD_PLUS":
            load += 1
        elif operation == "ACT_DIRECTION":
            direction = (1, 0, 0)
        elif operation == "SHAM_EXACT":
            pass
        else:
            raise ValueError(operation)
        raw[linear] = int(dee.pack_record(state, load, *direction, semantic))
    fork = dee.Runtime.import_research_state(N, int(runtime.current_tick), raw, clocks)
    fork.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)
    return fork, {
        "diagnostic_write_count": 1,
        "site": list(site),
        "field_policy": "clock preserved; one RAW record changed",
        "operation": operation,
        "before_raw": before_raw,
        "before": before,
        "after_raw": int(raw[linear]),
        "after": s23.record(int(raw[linear])),
        "clock": int(clocks[linear]),
        "channels_preserved": [],
        "receipts_preserved": [],
    }


def field_diff(before: int, after: int, s23: Any) -> list[str]:
    if before == after:
        return []
    a, b = s23.record(before), s23.record(after)
    if a is None or b is None:
        return ["presence"]
    changed = []
    for key in ("state", "s_reg", "direction", "semantic"):
        if a[key] != b[key]:
            changed.append(key)
    return changed


def difference_summary(reference: Any, test: Any, s23: Any,
                       ports: Any) -> dict[str, Any]:
    ref_raw, test_raw = list(reference.raw_copy()), list(test.raw_copy())
    ref_clock, test_clock = list(reference.clock_copy()), list(test.clock_copy())
    sites = []
    fields: dict[str, int] = {}
    for linear, (left, right) in enumerate(zip(ref_raw, test_raw)):
        if int(left) == int(right):
            continue
        x, rem = divmod(linear, N * N)
        y, z = divmod(rem, N)
        diff_fields = field_diff(int(left), int(right), s23)
        for key in diff_fields:
            fields[key] = fields.get(key, 0) + 1
        if len(sites) < 24:
            sites.append({"site": [x, y, z], "fields": diff_fields,
                          "reference": s23.record(int(left)), "test": s23.record(int(right))})
    b_neighbour = []
    for offset in s23.MOORE:
        site = s23.add(ports.b, offset)
        i = s23.index(site)
        if int(ref_raw[i]) != int(test_raw[i]) or int(ref_clock[i]) != int(test_clock[i]):
            b_neighbour.append({
                "offset": list(offset), "site": list(site),
                "reference": s23.record(int(ref_raw[i])), "test": s23.record(int(test_raw[i])),
                "reference_clock": int(ref_clock[i]), "test_clock": int(test_clock[i]),
            })
    return {
        "raw_different_sites": sum(int(a) != int(b) for a, b in zip(ref_raw, test_raw)),
        "clock_different_sites": sum(int(a) != int(b) for a, b in zip(ref_clock, test_clock)),
        "field_counts": fields, "site_sample": sites,
        "b_neighbour_differences": b_neighbour,
    }


def compact_gate(gate: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in gate.items() if key != "neighbors"}


def run_intervention(package_root: Path, operation: str,
                     origin: tuple[int, int, int] = BASE_ORIGIN) -> dict[str, Any]:
    s23 = load_section23(package_root)
    _, body_sample, _ = s23.load_section22(package_root)
    reference, ports, metadata = s23.build_feedback_candidate(package_root, "FULL", "lazy", origin)
    intervention_tick = 65 if operation == "ENV42_REMOVE" else 18
    reference.advance(intervention_tick)
    target = translate((42, 42, 4), origin) if operation == "ENV42_REMOVE" else tuple(metadata["action_site"])
    test, edit = clone_with_edit(reference, target, operation, s23)
    control = reference.fork()
    first_raw_difference = intervention_tick
    first_b_guard_difference = None
    rows = []
    for relative_tick in range(intervention_tick, HORIZON + 1):
        ref_raw, ref_clocks = list(control.raw_copy()), list(control.clock_copy())
        test_raw, test_clocks = list(test.raw_copy()), list(test.clock_copy())
        ref_gate = s23.sample_write_gate(ref_raw, ref_clocks, ports.b)
        test_gate = s23.sample_write_gate(test_raw, test_clocks, ports.b)
        guard_keys = ("n_active", "sum_direction", "tetra_pattern", "rule_value",
                      "write_protected", "period", "phase_remainder", "write_gate_open")
        if first_b_guard_difference is None and any(ref_gate[key] != test_gate[key] for key in guard_keys):
            first_b_guard_difference = relative_tick
        if (relative_tick in range(120, 134) or relative_tick in {intervention_tick, 66, 100, 150, 170}
                or ref_gate["write_gate_open"] or test_gate["write_gate_open"]):
            rows.append({
                "relative_tick": relative_tick,
                "absolute_tick": int(control.current_tick),
                "reference": body_sample(control, ports, relative_tick),
                "test": body_sample(test, ports, relative_tick),
                "reference_b_gate": compact_gate(ref_gate),
                "test_b_gate": compact_gate(test_gate),
                "difference": difference_summary(control, test, s23, ports),
            })
        if relative_tick < HORIZON:
            control.advance(1)
            test.advance(1)
    return {
        "operation": operation, "origin": list(origin), "intervention_relative_tick": intervention_tick,
        "edit": edit, "first_raw_difference": first_raw_difference,
        "first_b_guard_difference": first_b_guard_difference,
        "rows": rows,
        "final_difference": difference_summary(control, test, s23, ports),
        "final_reference": body_sample(control, ports, HORIZON),
        "final_test": body_sample(test, ports, HORIZON),
    }


def intact_context(package_root: Path, control: str = "FULL",
                   origin: tuple[int, int, int] = BASE_ORIGIN) -> dict[str, Any]:
    s23 = load_section23(package_root)
    _, body_sample, _ = s23.load_section22(package_root)
    runtime, ports, metadata = s23.build_feedback_candidate(package_root, control, "lazy", origin)
    rows = []
    for relative_tick in range(HORIZON + 1):
        if relative_tick in range(120, 134) or relative_tick in {0, 1, 18, 65, 150, 170}:
            raw, clocks = list(runtime.raw_copy()), list(runtime.clock_copy())
            a = s23.sample_write_gate(raw, clocks, ports.a)
            b = s23.sample_write_gate(raw, clocks, ports.b)
            rows.append({
                "relative_tick": relative_tick, "absolute_tick": int(runtime.current_tick),
                "sample": body_sample(runtime, ports, relative_tick),
                "a_gate": compact_gate(a), "b_gate": compact_gate(b),
                "b_all_offsets": b["neighbors"],
            })
        if relative_tick < HORIZON:
            runtime.advance(1)
    return {"control": control, "origin": list(origin), "metadata": metadata, "rows": rows}


def discovery(package_root: Path) -> dict[str, Any]:
    section = package_root / SECTION
    intact = intact_context(package_root, "FULL")
    comparisons = {
        "NO_ACTION": intact_context(package_root, "NO_ACTION"),
        "PHASE_MISS": intact_context(package_root, "PHASE_MISS"),
    }
    interventions = {}
    for operation in ("SHAM_EXACT", "ACT_REMOVE", "ACT_LOAD_MINUS", "ACT_LOAD_PLUS",
                      "ACT_DIRECTION", "ENV42_REMOVE"):
        interventions[operation] = run_intervention(package_root, operation)
    result = {"intact": intact, "preparation_comparisons": comparisons,
              "interventions": interventions}
    write_json(section / "TELEMETRY" / "DISCOVERY_CAUSAL_BATTERY.json", result)
    print(json.dumps({
        key: {
            "first_b_guard_difference": value["first_b_guard_difference"],
            "final_reference_delta": value["final_reference"]["delta"],
            "final_test_delta": value["final_test"]["delta"],
            "final_raw_different_sites": value["final_difference"]["raw_different_sites"],
        }
        for key, value in interventions.items()
    }, sort_keys=True))
    return result


def local_fork(package_root: Path, operation: str,
               origin: tuple[int, int, int] = BASE_ORIGIN) -> dict[str, Any]:
    s23 = load_section23(package_root)
    _, body_sample, _ = s23.load_section22(package_root)
    baseline, ports, _ = s23.build_feedback_candidate(package_root, "FULL", "lazy", origin)
    baseline.advance(131)
    raw, clocks = list(baseline.raw_copy()), list(baseline.clock_copy())
    if baseline.channel_names or baseline.receipts:
        raise RuntimeError("local fork cannot discard channels/receipts")
    sites = {
        "dynamic": translate((15, 16, 15), origin),
        "comparator": origin,
        "b": translate((16, 15, 15), origin),
        "support": translate((16, 14, 15), origin),
    }
    if operation.startswith("LOCAL_DYNAMIC"):
        site = sites["dynamic"]
    elif operation == "LOCAL_COMPARATOR_REMOVE":
        site = sites["comparator"]
    elif operation == "SUPPORT_REMOVE":
        site = sites["support"]
    elif operation == "B_CLOCK_PLUS1":
        site = sites["b"]
    else:
        raise ValueError(operation)
    linear = s23.index(site)
    before_raw, before_clock = int(raw[linear]), int(clocks[linear])
    before = s23.record(before_raw)
    if operation in {"LOCAL_DYNAMIC_REMOVE", "LOCAL_COMPARATOR_REMOVE", "SUPPORT_REMOVE"}:
        raw[linear] = 0
    elif operation == "B_CLOCK_PLUS1":
        clocks[linear] = (int(clocks[linear]) + 1) & ((1 << 64) - 1)
    else:
        if before is None:
            raise RuntimeError(f"missing local target {site}")
        direction = tuple(int(x) for x in before["direction"])
        load = int(before["s_reg"])
        semantic = int(before["semantic"])
        if operation == "LOCAL_DYNAMIC_SEM5":
            semantic = 5
        elif operation == "LOCAL_DYNAMIC_DIRECTION_ZERO":
            direction = (0, 0, 0)
        elif operation == "LOCAL_DYNAMIC_LOAD_ZERO":
            load = 0
        else:
            raise ValueError(operation)
        raw[linear] = int(dee.pack_record(int(before["state"]), load, *direction, semantic))
    test = dee.Runtime.import_research_state(N, int(baseline.current_tick), raw, clocks)
    test.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)
    reference = baseline.fork()
    rows = []
    first_guard_difference = None
    for relative_tick in range(131, HORIZON + 1):
        ref_raw, ref_clocks = list(reference.raw_copy()), list(reference.clock_copy())
        test_raw, test_clocks = list(test.raw_copy()), list(test.clock_copy())
        ref_gate = s23.sample_write_gate(ref_raw, ref_clocks, ports.b)
        test_gate = s23.sample_write_gate(test_raw, test_clocks, ports.b)
        guard_keys = ("n_active", "sum_direction", "tetra_pattern", "rule_value",
                      "write_protected", "period", "phase_remainder", "write_gate_open")
        if first_guard_difference is None and any(ref_gate[k] != test_gate[k] for k in guard_keys):
            first_guard_difference = relative_tick
        if relative_tick in {131, 132, 133, 150, 170} or ref_gate["write_gate_open"] or test_gate["write_gate_open"]:
            rows.append({
                "relative_tick": relative_tick,
                "reference": body_sample(reference, ports, relative_tick),
                "test": body_sample(test, ports, relative_tick),
                "reference_b_gate": compact_gate(ref_gate),
                "test_b_gate": compact_gate(test_gate),
                "difference": difference_summary(reference, test, s23, ports),
            })
        if relative_tick < HORIZON:
            reference.advance(1)
            test.advance(1)
    return {
        "operation": operation, "origin": list(origin), "intervention_relative_tick": 131,
        "edit": {"site": list(site), "before_raw": before_raw, "after_raw": int(raw[linear]),
                 "before_clock": before_clock, "after_clock": int(clocks[linear]),
                 "before": before, "after": s23.record(int(raw[linear])),
                 "changed_raw_sites": int(before_raw != int(raw[linear])),
                 "changed_clock_sites": int(before_clock != int(clocks[linear]))},
        "first_b_guard_difference": first_guard_difference,
        "rows": rows,
        "final_reference": body_sample(reference, ports, HORIZON),
        "final_test": body_sample(test, ports, HORIZON),
        "final_difference": difference_summary(reference, test, s23, ports),
    }


def region_around_b(s23: Any, ports: Any, include_local_core: bool) -> list[tuple[int, int, int]]:
    excluded = {ports.a, ports.b}
    if not include_local_core:
        excluded.add(ports.comparator)
        excluded.update(ports.supports)
    return [s23.add(ports.b, offset) for offset in s23.MOORE
            if s23.add(ports.b, offset) not in excluded]


def rescue_fork(package_root: Path, operation: str,
                origin: tuple[int, int, int] = BASE_ORIGIN) -> dict[str, Any]:
    s23 = load_section23(package_root)
    _, body_sample, _ = s23.load_section22(package_root)
    full, full_ports, _ = s23.build_feedback_candidate(package_root, "FULL", "lazy", origin)
    blocked, blocked_ports, _ = s23.build_feedback_candidate(package_root, "NO_ACTION", "lazy", origin)
    full.advance(120)
    blocked.advance(120)
    include_local_core = operation in {"LOCAL_RAW_RESCUE", "LOCAL_RAW_CLOCK_RESCUE"}
    sites = region_around_b(s23, full_ports, include_local_core)
    if operation == "FULL_IDENTITY_COPY":
        donor, recipient, recipient_ports = full, full, full_ports
    elif operation == "INVERSE_FULL_FROM_NO_ACTION":
        donor, recipient, recipient_ports = blocked, full, full_ports
    else:
        donor, recipient, recipient_ports = full, blocked, blocked_ports
    donor_raw, donor_clocks = list(donor.raw_copy()), list(donor.clock_copy())
    raw, clocks = list(recipient.raw_copy()), list(recipient.clock_copy())
    edits = []
    copy_clocks = operation == "LOCAL_RAW_CLOCK_RESCUE"
    for site in sites:
        linear = s23.index(site)
        before_raw, before_clock = int(raw[linear]), int(clocks[linear])
        raw[linear] = int(donor_raw[linear])
        if copy_clocks:
            clocks[linear] = int(donor_clocks[linear])
        if before_raw != int(raw[linear]) or before_clock != int(clocks[linear]):
            edits.append({"site": list(site), "before_raw": before_raw, "after_raw": int(raw[linear]),
                          "before_clock": before_clock, "after_clock": int(clocks[linear])})
    test = dee.Runtime.import_research_state(N, int(recipient.current_tick), raw, clocks)
    test.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)
    reference = recipient.fork()
    rows = []
    for relative_tick in range(120, HORIZON + 1):
        if relative_tick in range(120, 134) or relative_tick in {150, 170}:
            ref_raw, ref_clocks = list(reference.raw_copy()), list(reference.clock_copy())
            test_raw, test_clocks = list(test.raw_copy()), list(test.clock_copy())
            rows.append({
                "relative_tick": relative_tick,
                "reference": body_sample(reference, recipient_ports, relative_tick),
                "test": body_sample(test, recipient_ports, relative_tick),
                "reference_b_gate": compact_gate(s23.sample_write_gate(ref_raw, ref_clocks, recipient_ports.b)),
                "test_b_gate": compact_gate(s23.sample_write_gate(test_raw, test_clocks, recipient_ports.b)),
                "difference": difference_summary(reference, test, s23, recipient_ports),
            })
        if relative_tick < HORIZON:
            reference.advance(1)
            test.advance(1)
    return {
        "operation": operation, "origin": list(origin), "intervention_relative_tick": 120,
        "region_definition": "26-neighbour Moore shell of B excluding A/B"
                             + ("" if include_local_core else ", comparator and four supports"),
        "region_sites": [list(site) for site in sites],
        "copied_clocks": copy_clocks, "edits": edits,
        "final_reference": body_sample(reference, recipient_ports, HORIZON),
        "final_test": body_sample(test, recipient_ports, HORIZON),
        "rows": rows,
        "final_difference": difference_summary(reference, test, s23, recipient_ports),
    }


def compare_preparations(package_root: Path) -> dict[str, Any]:
    s23 = load_section23(package_root)
    full, ports, _ = s23.build_feedback_candidate(package_root, "FULL", "lazy", BASE_ORIGIN)
    no_action, _, _ = s23.build_feedback_candidate(package_root, "NO_ACTION", "lazy", BASE_ORIGIN)
    first_global = None
    first_local_raw = None
    first_b_guard = None
    rows = []
    region = {ports.b, *[s23.add(ports.b, offset) for offset in s23.MOORE]}
    guard_keys = ("n_active", "sum_direction", "tetra_pattern", "rule_value",
                  "write_protected", "period", "phase_remainder", "write_gate_open")
    for relative_tick in range(132):
        f_raw, f_clock = list(full.raw_copy()), list(full.clock_copy())
        n_raw, n_clock = list(no_action.raw_copy()), list(no_action.clock_copy())
        fg = s23.sample_write_gate(f_raw, f_clock, ports.b)
        ng = s23.sample_write_gate(n_raw, n_clock, ports.b)
        if first_global is None and (f_raw != n_raw or f_clock != n_clock):
            first_global = relative_tick
        if first_local_raw is None and any(
            f_raw[s23.index(site)] != n_raw[s23.index(site)]
            or f_clock[s23.index(site)] != n_clock[s23.index(site)] for site in region
        ):
            first_local_raw = relative_tick
        if first_b_guard is None and any(fg[k] != ng[k] for k in guard_keys):
            first_b_guard = relative_tick
        if relative_tick <= 6 or relative_tick in range(118, 132):
            rows.append({"relative_tick": relative_tick,
                         "FULL_b_gate": compact_gate(fg), "NO_ACTION_b_gate": compact_gate(ng),
                         "difference": difference_summary(full, no_action, s23, ports)})
        if relative_tick < 131:
            full.advance(1)
            no_action.advance(1)
    return {"first_global_difference": first_global, "first_local_difference": first_local_raw,
            "first_b_guard_difference": first_b_guard, "rows": rows}


def local_discovery(package_root: Path) -> dict[str, Any]:
    section = package_root / SECTION
    local = {operation: local_fork(package_root, operation) for operation in (
        "LOCAL_DYNAMIC_REMOVE", "LOCAL_DYNAMIC_SEM5", "LOCAL_DYNAMIC_DIRECTION_ZERO",
        "LOCAL_DYNAMIC_LOAD_ZERO", "LOCAL_COMPARATOR_REMOVE", "B_CLOCK_PLUS1", "SUPPORT_REMOVE"
    )}
    rescue = {operation: rescue_fork(package_root, operation) for operation in (
        "ENV_RAW_RESCUE", "LOCAL_RAW_RESCUE", "LOCAL_RAW_CLOCK_RESCUE",
        "FULL_IDENTITY_COPY", "INVERSE_FULL_FROM_NO_ACTION"
    )}
    result = {"preparation_divergence": compare_preparations(package_root),
              "local_interventions": local, "rescues": rescue}
    write_json(section / "TELEMETRY" / "DISCOVERY_LOCAL_AND_RESCUE.json", result)
    print(json.dumps({
        "local": {key: {"final_delta": value["final_test"]["delta"],
                         "first_b_guard_difference": value["first_b_guard_difference"]}
                  for key, value in local.items()},
        "rescue": {key: {"reference_delta": value["final_reference"]["delta"],
                          "test_delta": value["final_test"]["delta"],
                          "edits": len(value["edits"])} for key, value in rescue.items()},
        "preparation": result["preparation_divergence"],
    }, sort_keys=True))
    return result


def all_offsets(s23: Any, raw: list[int], clocks: list[int],
                center: tuple[int, int, int]) -> list[dict[str, Any]]:
    """Return all 26 Moore offsets, including zero and inactive RAW."""
    rows = []
    for offset in s23.MOORE:
        site = s23.add(center, offset)
        linear = s23.index(site)
        packed = int(raw[linear])
        item = s23.record(packed)
        active = bool(item is not None and int(item["state"]) > 0 and int(item["semantic"]) != 5)
        rows.append({
            "offset": list(offset), "site": list(site), "raw": packed,
            "clock": int(clocks[linear]), "record": item,
            "raw_nonzero": packed != 0, "active_predicate": active,
        })
    return rows


def save_section24_checkpoint(runtime: Any, section: Path, name: str) -> dict[str, Any]:
    path = section / "CHECKPOINTS" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    runtime.set_snapshot_metadata("mbp4.campaign", "MBP4-CONTEXTUAL-CAUSAL-MECHANISM")
    runtime.set_snapshot_metadata("mbp4.section", SECTION)
    runtime.save_snapshot(str(path))
    return {"path": path.relative_to(section).as_posix(), "tick": int(runtime.current_tick),
            "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def checkpoint_state_equal(left: Any, right: Any) -> bool:
    return (int(left.current_tick) == int(right.current_tick)
            and list(left.raw_copy()) == list(right.raw_copy())
            and list(left.clock_copy()) == list(right.clock_copy()))


def replay_main(package_root: Path) -> dict[str, Any]:
    section = package_root / SECTION
    s23 = load_section23(package_root)
    _, body_sample, _ = s23.load_section22(package_root)
    source = package_root / "23_NATIVE_FEEDBACK_RELATIONAL_REWRITE" / "CHECKPOINTS" / "MAIN_T0.deetsnap"
    runtime = dee.Runtime.load_snapshot(str(source))
    runtime.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)
    built, ports, _ = s23.build_feedback_candidate(package_root, "FULL", "lazy", BASE_ORIGIN)
    t0_equal = checkpoint_state_equal(runtime, built)
    historical = {
        0: "MAIN_T0.deetsnap", 131: "BEFORE_WRITE_OPPORTUNITY.deetsnap",
        132: "AFTER_POSSIBLE_REWRITE.deetsnap", 150: "RETENTION_READOUT.deetsnap",
        170: "MAIN_FINAL.deetsnap",
    }
    rows: list[dict[str, Any]] = []
    historical_checks: list[dict[str, Any]] = []
    checkpoints: list[dict[str, Any]] = []
    binary_path = section / "TELEMETRY" / "LOCAL_WINDOW_120_133.u64.gz"
    binary_path.parent.mkdir(parents=True, exist_ok=True)
    binary_frames: list[dict[str, Any]] = []
    with gzip.open(binary_path, "wb", compresslevel=6) as binary:
        for relative_tick in range(HORIZON + 1):
            raw, clocks = list(runtime.raw_copy()), list(runtime.clock_copy())
            if relative_tick in range(120, 134):
                frame = array.array("Q", (int(x) for x in raw))
                if sys.byteorder != "little":
                    frame.byteswap()
                binary.write(frame.tobytes())
                frame = array.array("Q", (int(x) for x in clocks))
                if sys.byteorder != "little":
                    frame.byteswap()
                binary.write(frame.tobytes())
                a_gate = s23.sample_write_gate(raw, clocks, ports.a)
                b_gate = s23.sample_write_gate(raw, clocks, ports.b)
                rows.append({
                    "relative_tick": relative_tick, "absolute_tick": int(runtime.current_tick),
                    "sample": body_sample(runtime, ports, relative_tick),
                    "a_gate": compact_gate(a_gate), "b_gate": compact_gate(b_gate),
                    "b_offsets_26": all_offsets(s23, raw, clocks, ports.b),
                })
                binary_frames.append({"frame": len(binary_frames), "relative_tick": relative_tick,
                                      "absolute_tick": int(runtime.current_tick)})
            if relative_tick in historical:
                old_path = package_root / "23_NATIVE_FEEDBACK_RELATIONAL_REWRITE" / "CHECKPOINTS" / historical[relative_tick]
                old = dee.Runtime.load_snapshot(str(old_path))
                historical_checks.append({
                    "relative_tick": relative_tick, "historical_path": old_path.relative_to(package_root).as_posix(),
                    "historical_sha256": sha256_file(old_path), "raw_clock_tick_equal": checkpoint_state_equal(runtime, old),
                })
            if relative_tick == 131:
                checkpoints.append(save_section24_checkpoint(runtime, section, "MAIN_REPLAY_T131.deetsnap"))
            if relative_tick == HORIZON:
                checkpoints.append(save_section24_checkpoint(runtime, section, "MAIN_REPLAY_FINAL.deetsnap"))
            if relative_tick < HORIZON:
                runtime.advance(1)
    index_data = {
        "schema": "mbp4.local-window-u64.v1", "encoding": "gzip concatenated little-endian uint64",
        "dimension": N, "records_per_field": N ** 3, "fields_per_frame": ["RAW", "clock"],
        "bytes_per_field_uncompressed": N ** 3 * 8, "frames": binary_frames,
        "sha256": sha256_file(binary_path),
    }
    write_json(section / "TELEMETRY" / "LOCAL_WINDOW_120_133_INDEX.json", index_data)
    return {
        "source": source.relative_to(package_root).as_posix(), "source_sha256": sha256_file(source),
        "source_equals_fresh_FULL_builder": t0_equal, "historical_checkpoint_checks": historical_checks,
        "local_window": rows, "binary_window": index_data, "checkpoints": checkpoints,
        "final": body_sample(runtime, ports, HORIZON), "host_writes_to_main_replay": 0,
    }


def run_frozen_replications(package_root: Path) -> dict[str, Any]:
    origins = ((22, 20, 24), (28, 26, 18))
    result: dict[str, Any] = {}
    for origin in origins:
        key = "origin_" + "_".join(str(x) for x in origin)
        result[key] = {
            "origin": list(origin),
            "B_CLOCK_PLUS1": local_fork(package_root, "B_CLOCK_PLUS1", origin),
            "LOCAL_DYNAMIC_REMOVE": local_fork(package_root, "LOCAL_DYNAMIC_REMOVE", origin),
            "INVERSE_FULL_FROM_NO_ACTION": rescue_fork(package_root, "INVERSE_FULL_FROM_NO_ACTION", origin),
        }
    return result


def extract_point(rows: list[dict[str, Any]], tick: int, side: str = "test") -> dict[str, Any] | None:
    for row in rows:
        if int(row["relative_tick"]) == tick:
            sample = row.get(side)
            if sample is None and side == "sample":
                sample = row.get("sample")
            return sample
    return None


def build_causal_graph(discovery_a: dict[str, Any], discovery_b: dict[str, Any],
                       replay: dict[str, Any], replications: dict[str, Any]) -> dict[str, Any]:
    actions = discovery_a["interventions"]
    rescues = discovery_b["rescues"]
    nodes = [
        {"id": "Q0", "tick": 0, "kind": "prepared query", "site": [15, 14, 15]},
        {"id": "LOCAL_DIVERGENCE", "tick": 1, "kind": "first B-guard divergence FULL/NO_ACTION"},
        {"id": "COMPARATOR", "tick": 131, "kind": "active local record", "site": [15, 15, 15]},
        {"id": "DYNAMIC_NEIGHBOR", "tick": 131, "kind": "active local record", "site": [15, 16, 15]},
        {"id": "B_CLOCK_PHASE", "tick": 131, "kind": "clock condition", "value": 391},
        {"id": "B_GATE", "tick": 131, "kind": "ordinary write opportunity", "n_active": 6,
         "k": 2, "period": 391, "phase_remainder": 0},
        {"id": "B_REWRITE", "tick": 132, "kind": "observed relation write", "before": 100, "after": 101},
        {"id": "DELTA_READOUT", "tick": 132, "kind": "relational readout", "before": 1, "after": 0},
        {"id": "ACTION18", "tick": 18, "kind": "external action product", "site": [31, 31, 15]},
        {"id": "ENV42", "tick": 65, "kind": "environment product", "site": [42, 42, 4]},
        {"id": "NO_ACTION_CROWDING", "tick": 131, "kind": "alternative local context", "n_active": 9},
    ]
    edges = [
        {"source": "Q0", "target": "LOCAL_DIVERGENCE", "status": "observed_temporal_preparation_difference",
         "evidence": "FULL/NO_ACTION first B-guard difference at t_rel=1; internal route not fully decomposed"},
        {"source": "COMPARATOR", "target": "B_GATE", "status": "intervention_effect_observed",
         "evidence": "removal at 131 suppressed B 100->101 and retained delta=1"},
        {"source": "DYNAMIC_NEIGHBOR", "target": "B_GATE", "status": "active_presence_effect_observed",
         "evidence": "removal or semantic=5 suppressed; load 7->0 and direction->0 preserved write"},
        {"source": "B_CLOCK_PHASE", "target": "B_GATE", "status": "intervention_effect_observed",
         "evidence": "clock 391->392 at t_rel=131 suppressed the write"},
        {"source": "B_GATE", "target": "B_REWRITE", "status": "executed_rule_and_transition_observed"},
        {"source": "B_REWRITE", "target": "DELTA_READOUT", "status": "observed_field_relation"},
        {"source": "ACTION18", "target": "B_GATE", "status": "not_necessary_under_tested_interventions",
         "evidence": "remove/load +/-1 did not change B guard/write; direction edit propagated elsewhere but not to B guard"},
        {"source": "ENV42", "target": "B_GATE", "status": "not_necessary_under_tested_intervention",
         "evidence": "single-site removal at 65 converged and preserved write"},
        {"source": "NO_ACTION_CROWDING", "target": "B_GATE", "status": "inhibitory_context_observed",
         "evidence": "n_active=9 gives no ordinary period; inverse environmental transplant at 120 suppressed FULL"},
    ]
    replication_compact = {}
    for key, arms in replications.items():
        replication_compact[key] = {
            "B_CLOCK_PLUS1_final_delta": arms["B_CLOCK_PLUS1"]["final_test"]["delta"],
            "LOCAL_DYNAMIC_REMOVE_final_delta": arms["LOCAL_DYNAMIC_REMOVE"]["final_test"]["delta"],
            "INVERSE_final_reference_delta": arms["INVERSE_FULL_FROM_NO_ACTION"]["final_reference"]["delta"],
            "INVERSE_final_test_delta": arms["INVERSE_FULL_FROM_NO_ACTION"]["final_test"]["delta"],
        }
    return {
        "question": "dependencies producing B:100->101 and delta:+1->0 at t_rel 131->132",
        "nodes": nodes, "edges": edges,
        "field_specific_dependence": {
            "dynamic_neighbor_active_presence": "changed outcome",
            "dynamic_neighbor_load_7_to_0": "did_not_change_write",
            "dynamic_neighbor_direction_to_zero": "did_not_change_write",
            "B_clock_391_to_392": "changed outcome",
            "comparator_presence": "changed outcome",
            "one_support_removal": "destructive_nonselective; not used as minimal attribution",
        },
        "action_environment_arms": {
            key: {"final_delta": value["final_test"]["delta"],
                  "first_b_guard_difference": value["first_b_guard_difference"],
                  "final_raw_different_sites": value["final_difference"]["raw_different_sites"]}
            for key, value in actions.items()
        },
        "rescue_asymmetry": {
            key: {"reference_delta": value["final_reference"]["delta"],
                  "test_delta": value["final_test"]["delta"], "edited_sites": len(value["edits"])}
            for key, value in rescues.items()
        },
        "replications": replication_compact,
        "unresolved": [
            "the internal transition chain from Q0 to the t1 local divergence was not decomposed into every microscopic reducer dependency",
            "FULL local environment copied into the NO_ACTION background at t120 did not rescue the write, so the sufficient enabling state extends beyond that copied shell and/or predates t120",
            "the inverse transplant establishes conditional inhibitory sufficiency, not a unique environmental route",
            "no tested selective intervention made ACTION18 or ENV42 necessary for the t131->132 write",
        ],
    }


def technical_checks_final(package_root: Path, replay: dict[str, Any]) -> dict[str, Any]:
    s23 = load_section23(package_root)
    source = package_root / "23_NATIVE_FEEDBACK_RELATIONAL_REWRITE" / "CHECKPOINTS"
    section = package_root / SECTION
    observed = dee.Runtime.load_snapshot(str(source / "MAIN_T0.deetsnap"))
    direct = dee.Runtime.load_snapshot(str(source / "MAIN_T0.deetsnap"))
    _, ports, _ = s23.build_feedback_candidate(package_root, "FULL", "lazy", BASE_ORIGIN)
    observed.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)
    direct.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)
    for _ in range(20):
        s23.sample_write_gate(list(observed.raw_copy()), list(observed.clock_copy()), ports.b)
        observed.advance(1)
    direct.advance(20)
    passive_equal = checkpoint_state_equal(observed, direct)
    lazy = dee.Runtime.load_snapshot(str(source / "BEFORE_WRITE_OPPORTUNITY.deetsnap"))
    dense = dee.Runtime.load_snapshot(str(source / "BEFORE_WRITE_OPPORTUNITY.deetsnap"))
    lazy.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)
    dense.execution_options = dee.TickOptions(dee.Backend.DENSE_SEQUENTIAL, 1)
    lazy.advance(1)
    dense.advance(1)
    historical_after = dee.Runtime.load_snapshot(str(source / "AFTER_POSSIBLE_REWRITE.deetsnap"))
    backend_equal = checkpoint_state_equal(lazy, dense) and checkpoint_state_equal(lazy, historical_after)
    boundary = dee.Runtime.load_snapshot(str(section / "CHECKPOINTS" / "MAIN_REPLAY_T131.deetsnap"))
    boundary.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)
    resumed = dee.Runtime.load_snapshot(str(section / "CHECKPOINTS" / "MAIN_REPLAY_T131.deetsnap"))
    resumed.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)
    boundary.advance(39)
    resumed.advance(39)
    continuation_equal = checkpoint_state_equal(boundary, resumed)
    final_saved = dee.Runtime.load_snapshot(str(section / "CHECKPOINTS" / "MAIN_REPLAY_FINAL.deetsnap"))
    final_equal = checkpoint_state_equal(boundary, final_saved)
    return {
        "parent_zip_expected_sha256": PARENT_SHA256,
        "section23_t0_equals_builder": replay["source_equals_fresh_FULL_builder"],
        "all_historical_checkpoint_states_match": all(x["raw_clock_tick_equal"] for x in replay["historical_checkpoint_checks"]),
        "passive_observer_raw_clock_equal": passive_equal,
        "lazy_dense_decisive_transition_equal": backend_equal,
        "save_load_continuation_equal": continuation_equal,
        "new_final_equals_direct_continuation": final_equal,
        "main_replay_channels": list(final_saved.channel_names),
        "main_replay_receipt_count": len(final_saved.receipts),
        "snapshot_checks": [
            {"path": x["path"], "sha256": x["sha256"], "tick": x["tick"],
             "loadable_tick": int(dee.Runtime.load_snapshot(str(section / x["path"])).current_tick)}
            for x in replay["checkpoints"]
        ],
    }


def post_write_readouts(discovery_a: dict[str, Any], discovery_b: dict[str, Any],
                        replay: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "FULL": {str(t): next((row["sample"] for row in replay["local_window"]
                                if row["relative_tick"] == t), replay["final"] if t == 170 else None)
                 for t in (132, 150, 170)}
    }
    for name, value in discovery_a["interventions"].items():
        result[name] = {str(t): extract_point(value["rows"], t) for t in (132, 150, 170)}
    for name, value in discovery_b["local_interventions"].items():
        result[name] = {str(t): extract_point(value["rows"], t) for t in (132, 150, 170)}
    return result


def write_reproduction(section: Path) -> None:
    text = """# Reproducción técnica — sección 24

Use el Python donde está instalado `dee_thinking==2.2.0`. Desde la raíz
extraída del paquete, el replay y los contrastes pueden reconstruirse con:

```powershell
python -I -B .\\24_CONTEXTUAL_CAUSAL_MECHANISM\\RUNNER\\run_contextual_mechanism.py `
  --package-root . --reproduce
```

`--reproduce` escribe en una copia de la sección 24; no debe ejecutarse contra
el ZIP canónico montado como evidencia. Las intervenciones son forks
diagnósticos. El replay MAIN parte del checkpoint heredado y no recibe
escrituras del host.

La ventana binaria `LOCAL_WINDOW_120_133.u64.gz` contiene, por frame, primero
47^3 uint64 RAW y luego 47^3 uint64 clock, little-endian. Su índice JSON asocia
cada frame con tick relativo y absoluto.
"""
    (section / "README_REPRODUCCION.md").write_text(text, encoding="utf-8")


def write_hashes(section: Path) -> list[dict[str, Any]]:
    entries = []
    for path in sorted(p for p in section.rglob("*") if p.is_file() and p.name != "HASHES.sha256"):
        relative = path.relative_to(section).as_posix()
        entries.append({"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    (section / "HASHES.sha256").write_text(
        "".join(f"{item['sha256']}  {item['path']}\n" for item in entries), encoding="utf-8"
    )
    return entries


def execute_final(package_root: Path) -> dict[str, Any]:
    section = package_root / SECTION
    discovery_a = json.loads((section / "TELEMETRY" / "DISCOVERY_CAUSAL_BATTERY.json").read_text(encoding="utf-8"))
    discovery_b = json.loads((section / "TELEMETRY" / "DISCOVERY_LOCAL_AND_RESCUE.json").read_text(encoding="utf-8"))
    replay = replay_main(package_root)
    write_json(section / "TELEMETRY" / "INTACT_REPLAY_AND_GATE.json", replay)
    replications = run_frozen_replications(package_root)
    write_json(section / "TELEMETRY" / "REPLICATIONS.json", replications)
    graph = build_causal_graph(discovery_a, discovery_b, replay, replications)
    write_json(section / "TELEMETRY" / "CAUSAL_GRAPH.json", graph)
    write_json(section / "TELEMETRY" / "POST_WRITE_READOUT.json",
               post_write_readouts(discovery_a, discovery_b, replay))
    write_json(section / "TELEMETRY" / "ACTION_ENVIRONMENT_INTERVENTIONS.json",
               discovery_a["interventions"])
    write_json(section / "TELEMETRY" / "LOCAL_INTERVENTIONS_AND_RESCUE.json",
               {"preparation_divergence": discovery_b["preparation_divergence"],
                "local_interventions": discovery_b["local_interventions"],
                "rescues": discovery_b["rescues"]})
    checks = technical_checks_final(package_root, replay)
    write_json(section / "TELEMETRY" / "TECHNICAL_CHECKS.json", checks)
    final_checkpoint = next(x for x in replay["checkpoints"] if x["path"].endswith("MAIN_REPLAY_FINAL.deetsnap"))
    summary = {
        "campaign": "MBP4 — MECANISMO CAUSAL DE LA REESCRITURA OBSERVADA",
        "parent_zip_sha256": PARENT_SHA256,
        "kernel": "DEE Universe v27 (frozen)", "runtime": "DEE thinking 2.2.0",
        "main_replay": {"relative_ticks": [0, 170], "absolute_ticks": [32, 202],
                        "host_writes": 0, "event": "B 100->101; delta +1->0 on 131->132"},
        "diagnostic_trajectories": {"discovery": 18, "frozen_replications": 6, "total": 24},
        "tested_external_products": {
            "action_t18": ["remove", "load_minus", "load_plus", "direction_change", "identity_sham"],
            "environment_t65": ["remove"],
        },
        "measured_local_dependencies": graph["field_specific_dependence"],
        "rescue_measurements": graph["rescue_asymmetry"],
        "replication_measurements": graph["replications"],
        "uncertainties": graph["unresolved"],
        "final_checkpoint": final_checkpoint,
        "technical_checks": checks,
        "completion_status": "FINITE_EVIDENCE_CUT_PACKAGED_WITHOUT_AUTOMATIC_SCIENTIFIC_VERDICT",
    }
    write_json(section / "RUN_SUMMARY.json", summary)
    write_reproduction(section)
    write_hashes(section)
    return summary


def package_append(package_root: Path, canonical_zip: Path) -> dict[str, Any]:
    if sha256_file(canonical_zip) != PARENT_SHA256:
        raise RuntimeError("canonical parent hash changed before packaging")
    section = package_root / SECTION
    expected_hashes = {}
    for line in (section / "HASHES.sha256").read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        expected_hashes[relative] = digest
    temp = canonical_zip.with_name(canonical_zip.name + ".section24.tmp")
    if temp.exists():
        temp.unlink()
    inherited: dict[str, bytes] = {}
    with zipfile.ZipFile(canonical_zip, "r") as source:
        infos = source.infolist()
        if len(infos) != 276:
            raise RuntimeError(f"expected 276 inherited members, found {len(infos)}")
        if any(f"/{SECTION}/" in info.filename for info in infos):
            raise RuntimeError("parent already contains section 24")
        for info in infos:
            inherited[info.filename] = source.read(info.filename)
        with zipfile.ZipFile(temp, "w", allowZip64=True) as target:
            target.comment = source.comment
            for info in infos:
                target.writestr(info, inherited[info.filename])
            for path in sorted(p for p in section.rglob("*") if p.is_file()):
                relative = path.relative_to(section).as_posix()
                name = f"{WRAPPER}/{SECTION}/{relative}"
                target.write(path, name, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
    with zipfile.ZipFile(temp, "r") as check:
        bad = check.testzip()
        if bad is not None:
            raise RuntimeError(f"ZIP CRC failure: {bad}")
        for name, payload in inherited.items():
            if check.read(name) != payload:
                raise RuntimeError(f"inherited member changed: {name}")
        for relative, digest in expected_hashes.items():
            name = f"{WRAPPER}/{SECTION}/{relative}"
            if hashlib.sha256(check.read(name)).hexdigest() != digest:
                raise RuntimeError(f"section hash mismatch: {relative}")
        hashes_payload = check.read(f"{WRAPPER}/{SECTION}/HASHES.sha256")
        member_count = len(check.infolist())
    os.replace(temp, canonical_zip)
    return {
        "path": str(canonical_zip), "sha256": sha256_file(canonical_zip),
        "member_count": member_count, "inherited_member_count": len(inherited),
        "inherited_members_byte_exact": True, "section_hash_entries_verified": len(expected_hashes),
        "hashes_member_present": bool(hashes_payload), "zip_crc_ok": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--discover", action="store_true")
    parser.add_argument("--discover-local", action="store_true")
    parser.add_argument("--execute-final", action="store_true")
    parser.add_argument("--reproduce", action="store_true")
    parser.add_argument("--canonical-zip", type=Path)
    args = parser.parse_args()
    package_root = args.package_root.resolve()
    if args.discover:
        discovery(package_root)
        return
    if args.discover_local:
        local_discovery(package_root)
        return
    if args.execute_final or args.reproduce:
        summary = execute_final(package_root)
        output: dict[str, Any] = {"summary": summary}
        if args.canonical_zip is not None:
            output["package"] = package_append(package_root, args.canonical_zip.resolve())
        print(json.dumps(output, indent=2, sort_keys=True))
        return
    parser.error("select an execution mode")


if __name__ == "__main__":
    main()
