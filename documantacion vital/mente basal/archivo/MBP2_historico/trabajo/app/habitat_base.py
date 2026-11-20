from __future__ import annotations

import argparse
import csv
import ctypes
import datetime as dtm
import hashlib
import json
import msvcrt
import os
import shutil
import sys
import tempfile
import time
import traceback
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

# The active worker uses a local wheel installation, not the user's historical
# environment.  A clean extraction may instead run from its own venv.
_BUNDLED_SITE = Path(__file__).resolve().parents[1] / "baseline" / "python_site"
if _BUNDLED_SITE.exists():
    sys.path.insert(0, str(_BUNDLED_SITE))

import dee_thinking as dee


APP_VERSION = "1.0.0"
WORLD_SCHEMA = "mente-basal.habitat.v1"
DEFAULT_WORLD_ID = "MENTE-BASAL-001"
N = 127
T_REF = 64


def utc_now() -> dtm.datetime:
    return dtm.datetime.now(dtm.timezone.utc)


def iso_utc(value: dtm.datetime | None = None) -> str:
    return (value or utc_now()).astimezone(dtm.timezone.utc).isoformat(timespec="milliseconds")


def iso_local(value: dtm.datetime | None = None) -> str:
    return (value or utc_now()).astimezone().isoformat(timespec="milliseconds")


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{uuid.uuid4().hex}.tmp")
    temporary.write_text(text, encoding="utf-8")
    # Windows readers may briefly hold the destination without FILE_SHARE_DELETE.
    # A status/panel read must not kill the sole writer because of that transient
    # sharing violation. The temporary file remains complete while we retry.
    last_error: OSError | None = None
    for attempt in range(40):
        try:
            os.replace(temporary, path)
            return
        except PermissionError as error:
            last_error = error
            time.sleep(min(0.01 * (attempt + 1), 0.10))
    temporary.unlink(missing_ok=True)
    assert last_error is not None
    raise last_error


def atomic_json(path: Path, value: Any) -> None:
    atomic_text(path, json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n")


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def root_paths(root: Path) -> dict[str, Path]:
    root = root.resolve()
    return {
        "root": root,
        "world": root / "world",
        "checkpoints": root / "world" / "checkpoints",
        "pending": root / "world" / "commands" / "pending",
        "processed": root / "world" / "commands" / "processed",
        "responses": root / "world" / "commands" / "responses",
        "history": root / "history" / "segments",
        "telemetry": root / "history" / "telemetry",
        "collections": root / "history" / "collections",
        "analysis": root / "analysis",
        "validation": root / "validation",
        "config": root / "config" / "habitat.json",
        "instance": root / "world" / "instance.json",
        "controller": root / "world" / "controller.json",
        "status": root / "world" / "status.json",
        "latest": root / "world" / "latest_checkpoint.txt",
        "lock": root / "world" / "writer.lock",
        "pid": root / "world" / "worker.pid",
        "stdout": root / "world" / "worker.stdout.log",
        "stderr": root / "world" / "worker.stderr.log",
    }


def ensure_layout(paths: dict[str, Path]) -> None:
    for key in ("world", "checkpoints", "pending", "processed", "responses",
                "history", "telemetry", "collections", "analysis", "validation"):
        paths[key].mkdir(parents=True, exist_ok=True)


Coord = tuple[int, int, int]
Direction = tuple[int, int, int]


@dataclass(frozen=True)
class Geometry:
    junction: Coord
    consequence: Coord
    program: Coord
    redirect: Coord
    response1: Coord
    revision1: Coord
    response2: Coord
    revision2: Coord
    response3: Coord
    update_redirect: Coord
    demux: tuple[Coord, Coord, Coord, Coord]
    environment: tuple[Coord, Coord, Coord, Coord]
    aux_hub_initial: Coord
    aux_hub_context: Coord


K_CUE: Direction = (1, 0, 0)
K_TEACHER: Direction = (-1, 1, 0)
K_MEMORY: Direction = (0, 1, 0)
K_PROGRAMMER: Direction = (1, -1, 0)
K_PROGRAMMED: Direction = (1, 0, 0)
K_REDIRECT: Direction = (-1, 1, 0)
K_RESPONSE: Direction = (1, 1, 0)
K_QUERY_REDIRECT: Direction = (-1, 0, 0)
K_MARKER: Direction = (0, -1, 0)
K_ENV_A: Direction = (1, 1, 0)
K_ENV_B: Direction = (0, -1, 0)
K_UPDATE: Direction = (0, 0, 1)
K_UPDATE_REDIRECT: Direction = (-1, 0, -1)


def wrap(value: int) -> int:
    return value % N


def plus(q: Coord, direction: Direction, scale: int = 1) -> Coord:
    return tuple(wrap(q[i] + direction[i] * scale) for i in range(3))  # type: ignore[return-value]


def plus_coord(a: Coord, b: Coord) -> Coord:
    return tuple(wrap(a[i] + b[i]) for i in range(3))  # type: ignore[return-value]


def source_for(target: Coord, travel: int, direction: Direction) -> Coord:
    return plus(target, direction, -(travel % N))


def coordinate(q: Coord) -> Any:
    return dee.Coordinate(*q)


def direction(d: Direction) -> Any:
    return dee.Direction(*d)


def geometry() -> Geometry:
    junction = (63, 63, 63)
    program = plus(junction, K_MEMORY, 7)
    consequence = plus(program, K_PROGRAMMER, -4)
    redirect = plus(program, K_PROGRAMMED, 6)
    response1 = plus(redirect, K_MEMORY, 16)
    revision1 = plus(response1, K_RESPONSE, 4)
    response2 = plus(revision1, K_MEMORY, 8)
    revision2 = plus(response2, K_RESPONSE, 4)
    response3 = plus(revision2, K_MEMORY, 8)
    update_redirect = plus(revision1, (1, 0, 0), 8)
    update_ticks = (14, 18, 22, 26)
    demux: list[Coord] = []
    environment: list[Coord] = []
    for update_tick in update_ticks:
        site = plus(update_redirect, K_UPDATE, -(30 - update_tick))
        demux.append(site)
        environment.append(plus_coord(site, (1, 1, 1)))
    return Geometry(
        junction, consequence, program, redirect, response1, revision1,
        response2, revision2, response3, update_redirect,
        tuple(demux), tuple(environment), (28, 91, 34), (94, 27, 88),
    )  # type: ignore[arg-type]


def linear_index(q: Coord) -> int:
    return int(dee.linear_index(q[0], q[1], q[2], N))


def install_observer_support(raw: list[int], clock: list[int], center: Coord,
                             phase: int, tag: int) -> None:
    clock[linear_index(center)] = phase
    offsets: tuple[Coord, ...] = (
        (1, -1, -1), (1, -1, 0), (1, -1, 1),
        (1, 0, -1), (1, 0, 0), (1, 0, 1),
    )
    for i, offset in enumerate(offsets):
        site = plus_coord(center, offset)
        raw[linear_index(site)] = int(dee.pack_record(tag + i, 0, 0, 0, 0, 4))


def make_channel(name: str, site: Coord, state: int, travel_direction: Direction,
                 allow_probe: bool = False) -> Any:
    channel = dee.ChannelSpec()
    channel.name = name
    channel.injection_site = coordinate(site)
    channel.state = state
    channel.direction = direction(travel_direction)
    channel.semantic = 1
    channel.allow_experience = True
    channel.allow_probe = allow_probe
    return channel


def register_arrival(runtime: Any, registry: dict[str, dict[str, Any]], name: str,
                     target: Coord, arrival_tick: int, travel_direction: Direction,
                     state: int, injection_tick: int = 0,
                     role: str = "experience") -> None:
    site = source_for(target, arrival_tick - injection_tick, travel_direction)
    runtime.register_channel(make_channel(name, site, state, travel_direction))
    registry[name] = {
        "site": list(site), "target": list(target), "arrival_tick": arrival_tick,
        "injection_tick": injection_tick, "direction": list(travel_direction),
        "state": state, "role": role,
    }


def register_fixed(runtime: Any, registry: dict[str, dict[str, Any]], name: str,
                   site: Coord, travel_direction: Direction, state: int,
                   role: str) -> None:
    runtime.register_channel(make_channel(name, site, state, travel_direction))
    registry[name] = {
        "site": list(site), "direction": list(travel_direction),
        "state": state, "role": role,
    }


def build_x0(config: dict[str, Any]) -> tuple[Any, Geometry, dict[str, dict[str, Any]]]:
    g = geometry()
    total = N * N * N
    raw = [0] * total
    clock = [0] * total
    update_ticks = (14, 18, 22, 26)
    for i, update_tick in enumerate(update_ticks):
        merge_tick = update_tick - 1
        install_observer_support(raw, clock, g.environment[i], 391 - merge_tick,
                                 9300 + i * 10)
    # A remote, physically co-resident support field makes the second route
    # observable without being a second Runtime or a copied output.
    install_observer_support(raw, clock, plus(g.aux_hub_context, (2, 0, 0)),
                             211, 9700)
    runtime = dee.Runtime.import_research_state(N, 0, raw, clock)
    runtime.execution_options = dee.TickOptions(dee.Backend.LAZY, int(config["threads"]))
    runtime.protocol_phase = "MENTE_BASAL_X0"
    runtime.set_snapshot_metadata("habitat.schema", WORLD_SCHEMA)
    runtime.set_snapshot_metadata("habitat.world_id", config["world_id"])
    runtime.set_snapshot_metadata("habitat.kernel", "DEE v27")
    runtime.set_snapshot_metadata("habitat.product", "DEE thinking 2.2.0")
    runtime.set_snapshot_metadata("habitat.t_ref", str(config["t_ref"]))

    channels: dict[str, dict[str, Any]] = {}
    register_arrival(runtime, channels, "base.training.cue", g.junction, 5,
                     K_CUE, 91001, role="prepared_relation")
    register_arrival(runtime, channels, "base.training.teacher", g.junction, 5,
                     K_TEACHER, 91002, role="prepared_relation")
    register_arrival(runtime, channels, "base.bridge.supply", g.consequence, 8,
                     K_PROGRAMMER, 91003, role="general_supply")
    register_arrival(runtime, channels, "base.bridge.marker", g.consequence, 8,
                     K_MARKER, 91004, role="prepared_marker")
    register_arrival(runtime, channels, "base.lineage.redirect0", g.redirect, 18,
                     K_REDIRECT, 91005, role="lineage_route")
    register_arrival(runtime, channels, "evaluation.query1", g.response1, 34,
                     K_CUE, 91101, role="baseline_query")
    for i, update_tick in enumerate(update_ticks):
        merge_tick = update_tick - 1
        register_arrival(runtime, channels, f"environment.e{i + 1}.a",
                         g.environment[i], merge_tick, K_ENV_A, 92000 + i * 2,
                         role="environment_regular_a")
        register_arrival(runtime, channels, f"environment.e{i + 1}.b",
                         g.environment[i], merge_tick, K_ENV_B, 92001 + i * 2,
                         role="environment_regular_b")
    register_arrival(runtime, channels, "learning.update_carrier", g.demux[0], 14,
                     K_UPDATE, 92501, role="reusable_update_carrier")
    register_arrival(runtime, channels, "learning.update_redirect", g.update_redirect,
                     30, K_UPDATE_REDIRECT, 92502, role="update_route")
    register_arrival(runtime, channels, "evaluation.query2", g.response2, 46,
                     K_CUE, 91102, injection_tick=40, role="late_query")
    register_arrival(runtime, channels, "evaluation.redirect2", g.revision2, 50,
                     K_QUERY_REDIRECT, 91202, injection_tick=40, role="late_route")
    register_arrival(runtime, channels, "evaluation.query3", g.response3, 58,
                     K_CUE, 91103, injection_tick=40, role="late_query")

    register_arrival(runtime, channels, "matter.route.alpha", g.aux_hub_initial, 16,
                     (1, 0, 1), 96001, role="mobile_matter_alpha")
    register_arrival(runtime, channels, "matter.route.beta", g.aux_hub_initial, 16,
                     (-1, 1, 0), 96002, role="mobile_matter_beta")
    register_arrival(runtime, channels, "context.supply", g.aux_hub_context, 48,
                     (0, 1, 1), 96003, role="context_general_supply")
    register_arrival(runtime, channels, "context.experience", g.aux_hub_context, 48,
                     (1, -1, 0), 96004, injection_tick=40,
                     role="late_context_experience")
    register_fixed(runtime, channels, "external.port.alpha", (10, 10, 10),
                   (1, 0, 0), 98001, "coupled_generic_input")
    return runtime, g, channels


INITIAL_INPUTS: tuple[tuple[str, int, int, str], ...] = (
    ("base.training.cue", 4083, 0, "prepared_relation"),
    ("base.training.teacher", 19, 0, "prepared_relation"),
    ("base.bridge.supply", 23, 0, "general_supply"),
    ("base.bridge.marker", 17, 0, "prepared_marker"),
    ("base.lineage.redirect0", 0, 0, "lineage_route"),
    ("evaluation.query1", 7, 0, "baseline_query"),
    ("environment.e1.a", 4149, 0, "regularity_a"),
    ("environment.e1.b", 15515, 0, "regularity_a"),
    ("environment.e2.a", 4149, 0, "regularity_a"),
    ("environment.e2.b", 15515, 0, "regularity_a"),
    ("environment.e3.a", 4149, 0, "regularity_a"),
    ("environment.e3.b", 15515, 0, "regularity_a"),
    ("environment.e4.a", 4149, 0, "regularity_a"),
    ("environment.e4.b", 15515, 0, "regularity_a"),
    ("learning.update_carrier", 23, 0, "reusable_carrier"),
    ("learning.update_redirect", 0, 0, "update_route"),
    ("matter.route.alpha", 31, 0, "mobile_matter"),
    ("matter.route.beta", 37, 0, "mobile_matter"),
    ("context.supply", 29, 0, "context_supply"),
)


LATE_INPUTS: tuple[tuple[str, int, int, str], ...] = (
    ("evaluation.query2", 5, 40, "late_query"),
    ("evaluation.redirect2", 0, 40, "late_route"),
    ("evaluation.query3", 3, 40, "late_query"),
    ("context.experience", 11, 40, "context_experience"),
)


SCIENCE_TICKS = (13, 14, 16, 17, 18, 21, 22, 25, 26, 30, 34, 38, 40,
                 46, 48, 50, 58, 60, 64)


def default_config() -> dict[str, Any]:
    return {
        "schema": WORLD_SCHEMA,
        "application_version": APP_VERSION,
        "world_id": DEFAULT_WORLD_ID,
        "dimension": N,
        "backend": "lazy",
        "threads": 1,
        "block_ticks": 8,
        "idle_sleep_seconds": 0.5,
        "checkpoint_interval_seconds": 1800,
        "telemetry_interval_ticks": 64,
        "max_autonomous_hours": 16,
        "max_ticks_after_reference": 900000,
        "max_archive_bytes": 1500000000,
        "min_free_disk_bytes": 2147483648,
        "max_working_set_bytes": 1073741824,
        "t_ref": T_REF,
        "start_paused": True,
    }


def append_jsonl(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def append_csv(path: Path, header: list[str], row: list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        if not exists:
            writer.writerow(header)
        writer.writerow(row)
        stream.flush()
        os.fsync(stream.fileno())


def active_segment(paths: dict[str, Path], state: dict[str, Any]) -> Path:
    return paths["history"] / f"segment_{state['segment_index']:03d}.active.jsonl"


def active_telemetry(paths: dict[str, Path], state: dict[str, Any]) -> Path:
    return paths["telemetry"] / f"telemetry_{state['segment_index']:03d}.active.csv"


def log_event(paths: dict[str, Path], state: dict[str, Any], event: dict[str, Any]) -> None:
    event = dict(event)
    event.setdefault("utc", iso_utc())
    event.setdefault("world_id", state["world_id"])
    event.setdefault("session_id", state["session_id"])
    append_jsonl(active_segment(paths, state), event)
    state["log_records"] = int(state.get("log_records", 0)) + 1


def schedule_input(runtime: Any, paths: dict[str, Path], state: dict[str, Any],
                   channel: str, load: int, at_tick: int, origin: str,
                   command_id: str) -> Any:
    receipt = runtime.experience(channel, at_tick, load)
    log_event(paths, state, {
        "type": "input_scheduled", "command_tick": int(runtime.current_tick),
        "command_id": command_id, "origin": origin, "channel": channel,
        "load": load, "requested_tick": at_tick, "receipt_id": int(receipt.id),
        "status": str(receipt.status), "reason": receipt.reason,
    })
    state.setdefault("receipt_status", {})[str(receipt.id)] = str(receipt.status)
    return receipt


def save_checkpoint(runtime: Any, paths: dict[str, Path], state: dict[str, Any],
                    reason: str, exact_verify: bool = False) -> Path:
    tick = int(runtime.current_tick)
    token = uuid.uuid4().hex[:8]
    safe_reason = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in reason)
    final = paths["checkpoints"] / f"tick_{tick:012d}_{safe_reason}_{token}.deetsnap"
    temporary = final.with_suffix(final.suffix + ".tmp")
    runtime.protocol_phase = f"MENTE_BASAL_{safe_reason.upper()}"
    runtime.set_snapshot_metadata("habitat.last_checkpoint_reason", reason)
    runtime.set_snapshot_metadata("habitat.session_id", state["session_id"])
    runtime.set_snapshot_metadata("habitat.segment_index", str(state["segment_index"]))
    runtime.set_snapshot_metadata("habitat.log_records", str(state.get("log_records", 0)))
    runtime.save_snapshot(str(temporary))
    loaded = dee.Runtime.load_snapshot(str(temporary))
    if int(loaded.current_tick) != tick or int(loaded.dimension) != N:
        temporary.unlink(missing_ok=True)
        raise RuntimeError("checkpoint verification failed")
    if exact_verify and (loaded.raw_copy() != runtime.raw_copy() or
                         loaded.clock_copy() != runtime.clock_copy()):
        temporary.unlink(missing_ok=True)
        raise RuntimeError("checkpoint RAW/clock verification failed")
    os.replace(temporary, final)
    state["last_checkpoint"] = str(final.relative_to(paths["root"]))
    state["last_checkpoint_tick"] = tick
    state["current_tick"] = tick
    state["last_checkpoint_utc"] = iso_utc()
    state["last_checkpoint_wall"] = time.time()
    metadata = {
        "schema": WORLD_SCHEMA, "world_id": state["world_id"],
        "session_id": state["session_id"], "tick": tick, "reason": reason,
        "created_utc": state["last_checkpoint_utc"], "created_local": iso_local(),
        "snapshot": final.name, "bytes": final.stat().st_size,
        "sha256": sha256(final), "segment_index": state["segment_index"],
        "log_records": state.get("log_records", 0),
        "controller_state": json.loads(json.dumps(state)),
    }
    atomic_json(final.with_suffix(final.suffix + ".json"), metadata)
    atomic_text(paths["latest"], str(final.relative_to(paths["root"])) + "\n")
    atomic_json(paths["controller"], state)
    return final


def load_latest_runtime(paths: dict[str, Path]) -> Any:
    if not paths["latest"].exists():
        raise FileNotFoundError("no valid latest checkpoint pointer")
    relative = paths["latest"].read_text(encoding="utf-8").strip()
    checkpoint = (paths["root"] / relative).resolve()
    if paths["checkpoints"].resolve() not in checkpoint.parents:
        raise RuntimeError("latest checkpoint escapes checkpoint directory")
    if not checkpoint.exists():
        raise FileNotFoundError(checkpoint)
    return dee.Runtime.load_snapshot(str(checkpoint))


def recover_controller_for_latest(paths: dict[str, Path], state: dict[str, Any]) -> dict[str, Any]:
    relative = paths["latest"].read_text(encoding="utf-8").strip()
    if (state.get("last_checkpoint") == relative and
            int(state.get("current_tick", -1)) ==
            int(state.get("last_checkpoint_tick", -2))):
        return state
    checkpoint = paths["root"] / relative
    sidecar = checkpoint.with_suffix(checkpoint.suffix + ".json")
    metadata = load_json(sidecar)
    recovered = metadata.get("controller_state")
    if not isinstance(recovered, dict):
        raise RuntimeError("latest checkpoint/controller mismatch without recoverable sidecar")
    current_deadline = state.get("autonomous_deadline_utc")
    recovered_deadline = recovered.get("autonomous_deadline_utc")
    if current_deadline and (not recovered_deadline or current_deadline < recovered_deadline):
        recovered["autonomous_deadline_utc"] = current_deadline
        recovered["worker_started_utc"] = state.get("worker_started_utc")
    # Preserve, but never replay automatically, the mutable tail written after
    # the checkpoint being restored. This prevents duplicated experiences.
    old_index = int(state.get("segment_index", recovered.get("segment_index", 0)))
    orphaned: list[str] = []
    for directory, stem, suffix in (
            (paths["history"], "segment", ".jsonl"),
            (paths["telemetry"], "telemetry", ".csv")):
        active = directory / f"{stem}_{old_index:03d}.active{suffix}"
        if active.exists():
            orphan = directory / (
                f"{stem}_{old_index:03d}_orphan_after_t{metadata['tick']}_"
                f"{uuid.uuid4().hex[:8]}{suffix}")
            os.replace(active, orphan)
            orphaned.append(str(orphan.relative_to(paths["root"])))
    recovered["recovery_orphan_segments"] = orphaned
    recovered["segment_index"] = max(old_index, int(recovered.get("segment_index", 0))) + 1
    recovered["segment_start_tick"] = int(metadata["tick"])
    recovered["current_tick"] = int(metadata["tick"])
    recovered["last_error"] = {
        "message": "controller recovered from latest checkpoint sidecar",
        "recovered_utc": iso_utc(),
    }
    atomic_json(paths["controller"], recovered)
    return recovered


def update_receipts(runtime: Any, paths: dict[str, Path], state: dict[str, Any]) -> None:
    known = state.setdefault("receipt_status", {})
    for receipt in runtime.receipts:
        key = str(receipt.id)
        status = str(receipt.status)
        effective = None if receipt.effective_tick is None else int(receipt.effective_tick)
        signature = f"{status}:{effective}:{receipt.reason}"
        if known.get(key) == signature:
            continue
        log_event(paths, state, {
            "type": "receipt_status", "tick": int(runtime.current_tick),
            "receipt_id": int(receipt.id), "kind": str(receipt.kind),
            "status": status, "requested_tick": int(receipt.requested_tick),
            "effective_tick": effective, "channels": list(receipt.channels),
            "reason": receipt.reason,
        })
        known[key] = signature


def observe_site(runtime: Any, q: Coord) -> dict[str, Any]:
    obs = runtime.observe(coordinate(q))
    rec = obs.record
    return {
        "site": list(q), "raw": int(obs.raw), "clock": int(obs.clock),
        "state": int(rec.state), "s_reg": int(rec.s_reg),
        "direction": [int(rec.dx), int(rec.dy), int(rec.dz)],
        "semantic": int(rec.semantic), "occupied": bool(rec.occupied),
        "raw_present": bool(rec.raw_present),
    }


def science_observations(runtime: Any, g: Geometry, tick: int) -> dict[str, Any]:
    sites: dict[str, Coord] = {}
    for i, update_tick in enumerate((14, 18, 22, 26)):
        if tick == update_tick - 1:
            sites[f"environment_{i + 1}"] = g.environment[i]
        if tick == update_tick:
            sites[f"carrier_{i + 1}"] = g.demux[i]
    fixed = {
        16: {"aux_initial_merge": g.aux_hub_initial},
        30: {"carrier_redirect": g.update_redirect},
        34: {"response_before_environmental_revision": g.response1},
        38: {"environmental_revision": g.revision1},
        46: {"response_use_1": g.response2},
        48: {"context_merge": g.aux_hub_context},
        50: {"query_redirect": g.revision2},
        58: {"response_use_2": g.response3},
    }
    sites.update(fixed.get(tick, {}))
    return {name: observe_site(runtime, q) for name, q in sites.items()}


def process_working_set() -> int:
    class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
        ]
    counters = PROCESS_MEMORY_COUNTERS()
    counters.cb = ctypes.sizeof(counters)
    ctypes.windll.kernel32.GetCurrentProcess.restype = ctypes.c_void_p
    handle = ctypes.windll.kernel32.GetCurrentProcess()
    ctypes.windll.psapi.GetProcessMemoryInfo.argtypes = [
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32]
    ctypes.windll.psapi.GetProcessMemoryInfo.restype = ctypes.c_int
    ok = ctypes.windll.psapi.GetProcessMemoryInfo(
        handle, ctypes.byref(counters), counters.cb)
    return int(counters.WorkingSetSize) if ok else 0


def tree_bytes(root: Path) -> int:
    total = 0
    for base, _, files in os.walk(root):
        for name in files:
            try:
                total += (Path(base) / name).stat().st_size
            except OSError:
                pass
    return total


def write_telemetry(runtime: Any, paths: dict[str, Path], state: dict[str, Any],
                    g: Geometry, note: str = "periodic") -> None:
    metrics = runtime.metrics()
    disk = shutil.disk_usage(paths["root"])
    header = [
        "utc", "tick", "note", "raw_support", "occupied", "s_reg_sum",
        "working_set_bytes", "archive_bytes", "disk_free_bytes",
        "pending_receipts", "applied_receipts", "rejected_receipts",
        "response1", "response2", "response3", "context_hub",
    ]
    receipts = list(runtime.receipts)
    pending = sum(item.status == dee.EventStatus.SCHEDULED for item in receipts)
    applied = sum(item.status == dee.EventStatus.APPLIED for item in receipts)
    rejected = len(receipts) - pending - applied
    row = [
        iso_utc(), int(runtime.current_tick), note, int(metrics.raw_support),
        int(metrics.occupied), int(metrics.s_reg_sum), process_working_set(),
        tree_bytes(paths["world"]) + tree_bytes(paths["history"]), disk.free,
        pending, applied, rejected,
        observe_site(runtime, g.response1)["s_reg"],
        observe_site(runtime, g.response2)["s_reg"],
        observe_site(runtime, g.response3)["s_reg"],
        observe_site(runtime, g.aux_hub_context)["s_reg"],
    ]
    append_csv(active_telemetry(paths, state), header, row)
    state["last_telemetry_tick"] = int(runtime.current_tick)


class WriterLock:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.stream = path.open("a+b")
        self.stream.seek(0, os.SEEK_END)
        if self.stream.tell() == 0:
            self.stream.write(b"0")
            self.stream.flush()
        self.stream.seek(0)
        try:
            msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as error:
            self.stream.close()
            raise RuntimeError("another writer owns this lineage") from error

    def close(self) -> None:
        if not self.stream.closed:
            self.stream.seek(0)
            try:
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_UNLCK, 1)
            finally:
                self.stream.close()

    def __enter__(self) -> "WriterLock":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()


def initial_controller(config: dict[str, Any], session_id: str) -> dict[str, Any]:
    now = utc_now()
    return {
        "schema": WORLD_SCHEMA,
        "world_id": config["world_id"],
        "session_id": session_id,
        "created_utc": iso_utc(now),
        "created_local": iso_local(now),
        "current_tick": 0,
        "segment_index": 0,
        "segment_start_tick": 0,
        "log_records": 0,
        "receipt_status": {},
        "recorded_science_ticks": [],
        "last_telemetry_tick": -1,
        "last_checkpoint": "",
        "last_checkpoint_tick": 0,
        "last_checkpoint_utc": "",
        "last_checkpoint_wall": 0.0,
        "last_collection_checkpoint": "",
        "last_collection_tick": 0,
        "manual_paused": bool(config.get("start_paused", True)),
        "stop_requested": False,
        "stop_reason": "",
        "autonomy_released": False,
        "reference_tick": None,
        "worker_started_utc": None,
        "autonomous_started_utc": None,
        "autonomous_deadline_utc": None,
        "tick_budget_end": None,
        "last_activity_utc": iso_utc(now),
        "total_kernel_ns": 0,
        "total_advance_calls": 0,
        "last_error": None,
    }


def initialize(root: Path, config_override: Path | None = None) -> dict[str, Any]:
    paths = root_paths(root)
    ensure_layout(paths)
    if paths["instance"].exists() or paths["latest"].exists():
        raise RuntimeError("world already exists; initialization never overwrites a lineage")
    config = default_config()
    if config_override is not None:
        config.update(load_json(config_override))
    if int(config["dimension"]) != N:
        raise ValueError("this validated habitat contract requires N=127")
    atomic_json(paths["config"], config)
    session_id = f"SESSION-001-{utc_now().strftime('%Y%m%dT%H%M%SZ')}"
    state = initial_controller(config, session_id)
    runtime, g, channels = build_x0(config)

    x0 = paths["checkpoints"] / "X0_MENTE_BASAL.deetsnap"
    x0_tmp = x0.with_suffix(x0.suffix + ".tmp")
    runtime.save_snapshot(str(x0_tmp))
    checked = dee.Runtime.load_snapshot(str(x0_tmp))
    if int(checked.current_tick) != 0 or checked.raw_copy() != runtime.raw_copy() or \
            checked.clock_copy() != runtime.clock_copy():
        x0_tmp.unlink(missing_ok=True)
        raise RuntimeError("X0 verification failed")
    os.replace(x0_tmp, x0)
    x0_meta = {
        "schema": WORLD_SCHEMA, "world_id": config["world_id"],
        "session_id": session_id, "tick": 0, "role": "X0_before_inputs",
        "created_utc": iso_utc(), "created_local": iso_local(),
        "bytes": x0.stat().st_size, "sha256": sha256(x0),
        "channels": channels, "kernel": "DEE v27", "product": "DEE thinking 2.2.0",
    }
    atomic_json(x0.with_suffix(x0.suffix + ".json"), x0_meta)
    state["x0_checkpoint"] = str(x0.relative_to(paths["root"]))
    log_event(paths, state, {
        "type": "lineage_created", "tick": 0, "x0": state["x0_checkpoint"],
        "dimension": N, "backend": config["backend"], "threads": config["threads"],
        "installed_capabilities": [
            "prepared_C7H03_lineage", "four_phase_coincidence_stations",
            "reusable_update_carrier", "two_mobile_matter_routes",
            "late_context_port",
        ],
    })
    for channel, load, at_tick, origin in INITIAL_INPUTS:
        schedule_input(runtime, paths, state, channel, load, at_tick, origin,
                       "INITIAL_PREPARATION")
    runtime.protocol_phase = "MENTE_BASAL_INITIAL_INPUTS_PENDING"
    seeded = save_checkpoint(runtime, paths, state, "seeded_t0", exact_verify=True)
    state["last_collection_checkpoint"] = str(x0.relative_to(paths["root"]))
    instance = {
        "schema": WORLD_SCHEMA, "application_version": APP_VERSION,
        "world_id": config["world_id"], "session_id": session_id,
        "created_utc": state["created_utc"], "created_local": state["created_local"],
        "dimension": N, "kernel": "DEE v27", "product": "DEE thinking 2.2.0",
        "x0": str(x0.relative_to(paths["root"])),
        "seeded_checkpoint": str(seeded.relative_to(paths["root"])),
        "configuration": str(paths["config"].relative_to(paths["root"])),
        "channels": channels,
        "provenance": {
            "base": "DEE_thinking_ENTREGA_02_DEFINITIVA_RESULTADOS.zip",
            "scientific_antecedent": "DEE_thinking_ENTREGA_03_APRENDIZAJE_NATIVO_RESULTADOS.zip",
        },
    }
    atomic_json(paths["instance"], instance)
    atomic_json(paths["controller"], state)
    write_status(paths, state, runtime, "STOPPED_READY", "initialized; worker not running")
    return instance


def current_job_flags() -> dict[str, Any]:
    kernel32 = ctypes.windll.kernel32
    kernel32.GetCurrentProcess.restype = ctypes.c_void_p
    kernel32.IsProcessInJob.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                        ctypes.POINTER(ctypes.c_int)]
    kernel32.IsProcessInJob.restype = ctypes.c_int
    in_job = ctypes.c_int(0)
    process = kernel32.GetCurrentProcess()
    if not kernel32.IsProcessInJob(process, None, ctypes.byref(in_job)):
        raise ctypes.WinError()
    flags = None
    if in_job.value:
        class BASIC_LIMIT(ctypes.Structure):
            _fields_ = [
                ("PerProcessUserTimeLimit", ctypes.c_longlong),
                ("PerJobUserTimeLimit", ctypes.c_longlong),
                ("LimitFlags", ctypes.c_uint32),
                ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t),
                ("ActiveProcessLimit", ctypes.c_uint32),
                ("Affinity", ctypes.c_size_t),
                ("PriorityClass", ctypes.c_uint32),
                ("SchedulingClass", ctypes.c_uint32),
            ]
        class IO_COUNTERS(ctypes.Structure):
            _fields_ = [(name, ctypes.c_ulonglong) for name in (
                "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
                "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]
        class EXTENDED(ctypes.Structure):
            _fields_ = [
                ("BasicLimitInformation", BASIC_LIMIT), ("IoInfo", IO_COUNTERS),
                ("ProcessMemoryLimit", ctypes.c_size_t),
                ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t),
                ("PeakJobMemoryUsed", ctypes.c_size_t),
            ]
        info = EXTENDED()
        if kernel32.QueryInformationJobObject(None, 9, ctypes.byref(info),
                                              ctypes.sizeof(info), None):
            flags = int(info.BasicLimitInformation.LimitFlags)
    return {
        "in_job": bool(in_job.value),
        "limit_flags": flags,
        "kill_on_job_close": bool(flags is not None and flags & 0x2000),
        "breakaway_ok": bool(flags is not None and flags & 0x0800),
    }


def write_status(paths: dict[str, Path], state: dict[str, Any], runtime: Any,
                 operating_state: str, detail: str = "") -> None:
    now = utc_now()
    deadline = state.get("autonomous_deadline_utc")
    remaining = None
    if deadline:
        remaining = max(0.0, (dtm.datetime.fromisoformat(deadline) - now).total_seconds())
    metrics = runtime.metrics()
    disk = shutil.disk_usage(paths["root"])
    receipts = list(runtime.receipts)
    payload = {
        "schema": WORLD_SCHEMA, "application_version": APP_VERSION,
        "world_id": state["world_id"], "session_id": state["session_id"],
        "pid": os.getpid(), "state": operating_state, "detail": detail,
        "tick": int(runtime.current_tick), "paused": bool(runtime.paused),
        "manual_paused": bool(state.get("manual_paused")),
        "autonomy_released": bool(state.get("autonomy_released")),
        "reference_tick": state.get("reference_tick"),
        "worker_started_utc": state.get("worker_started_utc"),
        "autonomous_started_utc": state.get("autonomous_started_utc"),
        "now_utc": iso_utc(now), "now_local": iso_local(now),
        "autonomous_deadline_utc": deadline,
        "autonomous_seconds_remaining": remaining,
        "tick_budget_end": state.get("tick_budget_end"),
        "last_checkpoint": state.get("last_checkpoint"),
        "last_checkpoint_tick": state.get("last_checkpoint_tick"),
        "last_checkpoint_utc": state.get("last_checkpoint_utc"),
        "last_activity_utc": state.get("last_activity_utc"),
        "raw_support": int(metrics.raw_support), "occupied": int(metrics.occupied),
        "s_reg_sum": int(metrics.s_reg_sum),
        "receipts_total": len(receipts),
        "receipts_applied": sum(r.status == dee.EventStatus.APPLIED for r in receipts),
        "receipts_rejected": sum(r.status not in (dee.EventStatus.APPLIED,
                                                   dee.EventStatus.SCHEDULED)
                                 for r in receipts),
        "working_set_bytes": process_working_set(),
        "archive_bytes": tree_bytes(paths["world"]) + tree_bytes(paths["history"]),
        "disk_free_bytes": disk.free,
        "backend": str(runtime.execution_options.backend),
        "threads": int(runtime.execution_options.threads),
        "job": current_job_flags(),
        "source_policy": "prepared finite inputs; free evolution after pending events exhaust",
    }
    atomic_json(paths["status"], payload)


def record_science_tick(runtime: Any, paths: dict[str, Path], state: dict[str, Any],
                        g: Geometry) -> None:
    tick = int(runtime.current_tick)
    key = str(tick)
    recorded = state.setdefault("recorded_science_ticks", [])
    if tick not in SCIENCE_TICKS or key in recorded:
        return
    observations = science_observations(runtime, g, tick)
    log_event(paths, state, {
        "type": "scientific_observation", "tick": tick,
        "observation_mode": "passive", "readings": observations,
    })
    recorded.append(key)


def advance_runtime(runtime: Any, count: int, paths: dict[str, Path],
                    state: dict[str, Any], g: Geometry, reason: str) -> None:
    if count < 0:
        raise ValueError("advance count must be nonnegative")
    start = int(runtime.current_tick)
    target = start + count
    runtime.resume()
    while int(runtime.current_tick) < target:
        tick = int(runtime.current_tick)
        record_science_tick(runtime, paths, state, g)
        next_boundaries = [value for value in SCIENCE_TICKS if tick < value <= target]
        until_boundary = min(next_boundaries) - tick if next_boundaries else target - tick
        step = min(int(load_json(paths["config"])["block_ticks"]), until_boundary)
        if step <= 0:
            step = 1
        before = int(runtime.current_tick)
        wall_start = time.perf_counter_ns()
        info = runtime.advance(step)
        wall_ns = time.perf_counter_ns() - wall_start
        after = int(runtime.current_tick)
        state["total_kernel_ns"] = int(state.get("total_kernel_ns", 0)) + int(info.total_ns)
        state["total_advance_calls"] = int(state.get("total_advance_calls", 0)) + 1
        state["last_activity_utc"] = iso_utc()
        state["current_tick"] = after
        log_event(paths, state, {
            "type": "advance", "reason": reason, "from_tick": before,
            "to_tick": after, "count": after - before, "wall_ns": wall_ns,
            "kernel_total_ns": int(info.total_ns), "overflows": int(info.overflows),
            "genesis": int(info.genesis), "evaluated": int(info.evaluated),
            "active_raw": int(info.active_raw), "backend": str(info.used_backend),
            "threads": int(info.used_threads), "fallback": bool(info.fallback),
        })
        update_receipts(runtime, paths, state)
    record_science_tick(runtime, paths, state, g)
    if state.get("manual_paused", False):
        runtime.pause()


def close_segment(runtime: Any, paths: dict[str, Path], state: dict[str, Any],
                  reason: str, open_next: bool = True) -> tuple[Path, Path]:
    tick = int(runtime.current_tick)
    history_active = active_segment(paths, state)
    telemetry_active = active_telemetry(paths, state)
    log_event(paths, state, {
        "type": "segment_closed", "tick": tick, "reason": reason,
        "segment_start_tick": state["segment_start_tick"],
    })
    history_final = paths["history"] / (
        f"segment_{state['segment_index']:03d}_t{state['segment_start_tick']}_t{tick}.jsonl")
    telemetry_final = paths["telemetry"] / (
        f"telemetry_{state['segment_index']:03d}_t{state['segment_start_tick']}_t{tick}.csv")
    if history_final.exists() or telemetry_final.exists():
        raise RuntimeError("segment closure would overwrite history")
    os.replace(history_active, history_final)
    if telemetry_active.exists():
        os.replace(telemetry_active, telemetry_final)
    else:
        telemetry_final.write_text("utc,tick,note\n", encoding="utf-8")
    state["segment_index"] = int(state["segment_index"]) + 1
    state["segment_start_tick"] = tick
    state["current_tick"] = tick
    if open_next:
        log_event(paths, state, {
            "type": "segment_opened", "tick": tick,
            "parent_segment": history_final.name, "reason": reason,
        })
    return history_final, telemetry_final


def make_collection_cut(runtime: Any, paths: dict[str, Path], state: dict[str, Any],
                        request_id: str, stop_after: bool) -> Path:
    if (not 1 <= len(request_id) <= 64 or ".." in request_id or
            any(not (character.isalnum() or character in "-_.")
                for character in request_id)):
        raise ValueError("collection request_id must be 1-64 safe characters without '..'")
    # IDs are permanent historical identities. A second command may not reuse
    # one and silently replace frozen control files or a same-tick descriptor.
    if any(paths["collections"].glob(f"cut_{request_id}_*")):
        raise FileExistsError(f"collection request_id already exists: {request_id}")
    interval_start_tick = int(state.get("last_collection_tick", 0))
    interval_start_checkpoint = state.get("last_collection_checkpoint")
    write_telemetry(runtime, paths, state, geometry(), "collection_cut")
    history_segment, telemetry_segment = close_segment(
        runtime, paths, state, f"collect:{request_id}", open_next=not stop_after)
    # The checkpoint is published after rotation so its controller sidecar
    # resumes into the new mutable segment, never into the immutable one.
    checkpoint = save_checkpoint(runtime, paths, state, f"collect_{request_id}",
                                 exact_verify=True)
    state["last_collection_checkpoint"] = str(checkpoint.relative_to(paths["root"]))
    state["last_collection_tick"] = int(runtime.current_tick)
    if state.get("reference_tick") is None:
        state["reference_tick"] = int(runtime.current_tick)
    state["current_tick"] = int(runtime.current_tick)
    frozen_controller = paths["collections"] / f"cut_{request_id}_controller.json"
    frozen_status = paths["collections"] / f"cut_{request_id}_status.json"
    frozen_latest = paths["collections"] / f"cut_{request_id}_latest_checkpoint.txt"
    atomic_json(frozen_controller, state)
    atomic_json(frozen_status, {
        "schema": WORLD_SCHEMA, "world_id": state["world_id"],
        "session_id": state["session_id"], "state": "CUT_NOT_RUNNING",
        "detail": "immutable collection boundary; start worker explicitly to continue",
        "tick": int(runtime.current_tick), "pid": None, "paused": bool(runtime.paused),
        "last_checkpoint": state["last_checkpoint"], "cut_utc": iso_utc(),
    })
    atomic_text(frozen_latest, str(checkpoint.relative_to(paths["root"])) + "\n")
    atomic_json(paths["controller"], state)
    descriptor = {
        "schema": "mente-basal.collection.v1",
        "request_id": request_id,
        "world_id": state["world_id"], "session_id": state["session_id"],
        "created_utc": iso_utc(), "created_local": iso_local(),
        "start_tick": interval_start_tick,
        "end_tick": int(runtime.current_tick),
        "start_checkpoint": interval_start_checkpoint,
        "end_checkpoint": str(checkpoint.relative_to(paths["root"])),
        "history_segment": str(history_segment.relative_to(paths["root"])),
        "telemetry_segment": str(telemetry_segment.relative_to(paths["root"])),
        "controller_snapshot": str(frozen_controller.relative_to(paths["root"])),
        "status_snapshot": str(frozen_status.relative_to(paths["root"])),
        "latest_pointer_snapshot": str(frozen_latest.relative_to(paths["root"])),
        "stop_after": stop_after,
        "immutable_files": [
            str(checkpoint.relative_to(paths["root"])),
            str(checkpoint.with_suffix(checkpoint.suffix + ".json").relative_to(paths["root"])),
            str(history_segment.relative_to(paths["root"])),
            str(telemetry_segment.relative_to(paths["root"])),
            str(frozen_controller.relative_to(paths["root"])),
            str(frozen_status.relative_to(paths["root"])),
            str(frozen_latest.relative_to(paths["root"])),
        ],
    }
    descriptor_path = paths["collections"] / f"cut_{request_id}_t{int(runtime.current_tick)}.json"
    atomic_json(descriptor_path, descriptor)
    return descriptor_path


def command_response(paths: dict[str, Path], command_id: str,
                     payload: dict[str, Any]) -> None:
    payload = dict(payload)
    payload.setdefault("command_id", command_id)
    payload.setdefault("completed_utc", iso_utc())
    atomic_json(paths["responses"] / f"{command_id}.json", payload)


def process_command(command_path: Path, runtime: Any, paths: dict[str, Path],
                    state: dict[str, Any], g: Geometry) -> None:
    command = load_json(command_path)
    command_id = str(command.get("id") or command_path.stem)
    operation = str(command.get("operation", ""))
    result: dict[str, Any] = {"ok": True, "operation": operation,
                             "tick_before": int(runtime.current_tick)}
    completion_key = f"command.completed.{command_id}"
    if runtime.snapshot_metadata(completion_key) == "1":
        result.update({"idempotent_recovery": True,
                       "tick_after": int(runtime.current_tick)})
        if operation in ("collect", "collect_stop"):
            request_id = str(command.get("arguments", {}).get("request_id") or command_id)
            descriptors = sorted(paths["collections"].glob(f"cut_{request_id}_t*.json"))
            if descriptors:
                result["descriptor"] = str(descriptors[-1].relative_to(paths["root"]))
                if operation == "collect_stop":
                    state["stop_requested"] = True
                    state["stop_reason"] = "collect_and_stop"
            elif operation in ("collect", "collect_stop"):
                raise RuntimeError(
                    "command metadata says complete but no immutable collection descriptor exists")
        command_response(paths, command_id, result)
        processed = paths["processed"] / f"{command_id}.json"
        os.replace(command_path, processed)
        return
    try:
        log_event(paths, state, {
            "type": "command_received", "tick": int(runtime.current_tick),
            "command_id": command_id, "operation": operation,
            "arguments": command.get("arguments", {}),
        })
        arguments = command.get("arguments", {})
        if operation == "pause":
            state["manual_paused"] = True
            runtime.pause()
        elif operation == "resume":
            state["manual_paused"] = False
            runtime.resume()
        elif operation == "release_autonomy":
            if int(runtime.current_tick) < int(load_json(paths["config"])["t_ref"]):
                raise RuntimeError("cannot release autonomy before T_ref")
            state["autonomy_released"] = True
            state["manual_paused"] = False
            if state.get("autonomous_deadline_utc") is None:
                state["autonomous_started_utc"] = iso_utc()
                state["autonomous_deadline_utc"] = iso_utc(
                    utc_now() + dtm.timedelta(
                        hours=float(load_json(paths["config"])["max_autonomous_hours"])))
            if state.get("reference_tick") is None:
                state["reference_tick"] = int(runtime.current_tick)
            state["tick_budget_end"] = int(state["reference_tick"]) + int(
                load_json(paths["config"])["max_ticks_after_reference"])
            runtime.resume()
        elif operation == "advance":
            count = int(arguments.get("count", 0))
            if count <= 0:
                raise ValueError("advance requires positive count")
            was_paused = bool(state.get("manual_paused", False))
            state["manual_paused"] = False
            advance_runtime(runtime, count, paths, state, g, f"command:{command_id}")
            state["manual_paused"] = was_paused
            if was_paused:
                runtime.pause()
        elif operation == "experience_profile":
            profile = str(arguments.get("profile", ""))
            if profile != "late_context":
                raise ValueError("unknown experience profile")
            if int(runtime.current_tick) != 40:
                raise RuntimeError("late_context profile requires tick 40")
            receipts = []
            for channel, load, at_tick, origin in LATE_INPUTS:
                receipt = schedule_input(runtime, paths, state, channel, load,
                                         at_tick, origin, command_id)
                receipts.append(int(receipt.id))
            result["receipts"] = receipts
        elif operation == "experience":
            channel = str(arguments["channel"])
            load = int(arguments["load"])
            requested = int(arguments.get("tick", int(runtime.current_tick)))
            if requested < int(runtime.current_tick):
                raise ValueError("late input rejected; requested tick is in the past")
            receipt = schedule_input(runtime, paths, state, channel, load, requested,
                                     str(arguments.get("origin", "user")), command_id)
            result["receipt_id"] = int(receipt.id)
            result["receipt_status"] = str(receipt.status)
        elif operation == "save":
            pass
        elif operation in ("collect", "collect_stop"):
            request_id = str(arguments.get("request_id") or command_id)
            if operation == "collect_stop":
                # The frozen controller and snapshot sidecar must describe the
                # terminal intent, not the pre-stop state.
                state["stop_requested"] = True
                state["stop_reason"] = "collect_and_stop"
                log_event(paths, state, {
                    "type": "terminal_cut_intent", "tick": int(runtime.current_tick),
                    "request_id": request_id, "reason": "collect_and_stop",
                })
            runtime.set_snapshot_metadata(completion_key, "1")
            descriptor = make_collection_cut(runtime, paths, state, request_id,
                                             operation == "collect_stop")
            result["descriptor"] = str(descriptor.relative_to(paths["root"]))
        elif operation == "stop":
            runtime.set_snapshot_metadata(completion_key, "1")
            checkpoint = save_checkpoint(runtime, paths, state, "normal_stop",
                                         exact_verify=True)
            state["stop_requested"] = True
            state["stop_reason"] = str(arguments.get("reason", "user_stop"))
            result["checkpoint"] = str(checkpoint.relative_to(paths["root"]))
        else:
            raise ValueError(f"unsupported operation: {operation}")
        if operation not in ("collect", "collect_stop", "stop"):
            runtime.set_snapshot_metadata(completion_key, "1")
            reason = (str(arguments.get("reason", "manual")) if operation == "save"
                      else f"command_{operation}_{command_id}")
            checkpoint = save_checkpoint(runtime, paths, state, reason,
                                         exact_verify=operation in ("save", "pause"))
            result["checkpoint"] = str(checkpoint.relative_to(paths["root"]))
        state["current_tick"] = int(runtime.current_tick)
        completed = state.setdefault("completed_commands", [])
        completed.append(command_id)
        if len(completed) > 1024:
            del completed[:-1024]
        result["tick_after"] = int(runtime.current_tick)
    except Exception as error:
        result.update({"ok": False, "error": str(error),
                       "tick_after": int(runtime.current_tick)})
        log_event(paths, state, {
            "type": "command_rejected", "tick": int(runtime.current_tick),
            "command_id": command_id, "operation": operation, "reason": str(error),
        })
        state["current_tick"] = int(runtime.current_tick)
        state["manual_paused"] = True
        runtime.pause()
    atomic_json(paths["controller"], state)
    command_response(paths, command_id, result)
    processed = paths["processed"] / f"{command_id}.json"
    if processed.exists():
        processed = paths["processed"] / f"{command_id}_{uuid.uuid4().hex[:6]}.json"
    os.replace(command_path, processed)


def resource_violation(config: dict[str, Any], paths: dict[str, Path],
                       state: dict[str, Any], runtime: Any) -> str | None:
    now = utc_now()
    deadline = state.get("autonomous_deadline_utc")
    if deadline and now >= dtm.datetime.fromisoformat(deadline):
        return "max_autonomous_hours_reached"
    tick_budget = state.get("tick_budget_end")
    if tick_budget is not None and int(runtime.current_tick) >= int(tick_budget):
        return "max_ticks_after_reference_reached"
    if process_working_set() > int(config["max_working_set_bytes"]):
        return "max_working_set_bytes_reached"
    archive = tree_bytes(paths["world"]) + tree_bytes(paths["history"])
    if archive > int(config["max_archive_bytes"]):
        return "max_archive_bytes_reached"
    disk = shutil.disk_usage(paths["root"])
    last_size = 64 * 1024 * 1024
    last = state.get("last_checkpoint")
    if last and (paths["root"] / last).exists():
        last_size = (paths["root"] / last).stat().st_size
    reserve = max(int(config["min_free_disk_bytes"]), last_size * 2)
    if disk.free < reserve:
        return "checkpoint_disk_reserve_reached"
    return None


def worker(root: Path) -> int:
    paths = root_paths(root)
    ensure_layout(paths)
    config = load_json(paths["config"])
    state = load_json(paths["controller"])
    g = geometry()
    with WriterLock(paths["lock"]):
        runtime = load_latest_runtime(paths)
        state = recover_controller_for_latest(paths, state)
        runtime.execution_options = dee.TickOptions(dee.Backend.LAZY, int(config["threads"]))
        now = utc_now()
        if state.get("worker_started_utc") is None:
            state["worker_started_utc"] = iso_utc(now)
        state["stop_requested"] = False
        state["stop_reason"] = ""
        state["last_error"] = None
        atomic_text(paths["pid"], str(os.getpid()) + "\n")
        log_event(paths, state, {
            "type": "worker_started", "tick": int(runtime.current_tick),
            "pid": os.getpid(), "job": current_job_flags(),
        })
        operating = "PAUSED" if state.get("manual_paused") else "RUNNING"
        if state.get("manual_paused"):
            runtime.pause()
        else:
            runtime.resume()
        write_status(paths, state, runtime, operating, "worker owns mutable Runtime")
        atomic_json(paths["controller"], state)
        try:
            while not state.get("stop_requested", False):
                for command_path in sorted(paths["pending"].glob("*.json")):
                    process_command(command_path, runtime, paths, state, g)
                    atomic_json(paths["controller"], state)
                    if state.get("stop_requested"):
                        break
                if state.get("stop_requested"):
                    break
                violation = resource_violation(config, paths, state, runtime)
                if violation:
                    state["manual_paused"] = True
                    runtime.pause()
                    checkpoint = save_checkpoint(runtime, paths, state,
                                                 f"safe_pause_{violation}",
                                                 exact_verify=True)
                    state["stop_requested"] = True
                    state["stop_reason"] = violation
                    log_event(paths, state, {
                        "type": "safe_stop", "tick": int(runtime.current_tick),
                        "reason": violation,
                        "checkpoint": str(checkpoint.relative_to(paths["root"])),
                    })
                    break
                if not state.get("manual_paused", False):
                    count = int(config["block_ticks"])
                    tick_budget = state.get("tick_budget_end")
                    if tick_budget is not None:
                        count = min(count, max(0, int(tick_budget) - int(runtime.current_tick)))
                    if count > 0:
                        advance_runtime(runtime, count, paths, state, g, "autonomous")
                    last_telemetry = int(state.get("last_telemetry_tick", -1))
                    if int(runtime.current_tick) - last_telemetry >= int(config["telemetry_interval_ticks"]):
                        write_telemetry(runtime, paths, state, g)
                    if time.time() - float(state.get("last_checkpoint_wall", 0.0)) >= float(
                            config["checkpoint_interval_seconds"]):
                        save_checkpoint(runtime, paths, state, "periodic", exact_verify=False)
                    operating = "RUNNING"
                else:
                    operating = "PAUSED"
                state["last_activity_utc"] = iso_utc()
                atomic_json(paths["controller"], state)
                write_status(paths, state, runtime, operating, "boundary complete")
                time.sleep(float(config["idle_sleep_seconds"]))
        except Exception as error:
            state["last_error"] = {"message": str(error), "traceback": traceback.format_exc()}
            state["stop_reason"] = "worker_failure"
            try:
                checkpoint = save_checkpoint(runtime, paths, state, "worker_failure",
                                             exact_verify=True)
                state["last_error"]["checkpoint"] = str(checkpoint.relative_to(paths["root"]))
            except Exception as checkpoint_error:
                state["last_error"]["checkpoint_error"] = str(checkpoint_error)
            atomic_json(paths["controller"], state)
            write_status(paths, state, runtime, "FAILED_SAFE", str(error))
            return 1
        finally:
            try:
                update_receipts(runtime, paths, state)
                atomic_json(paths["controller"], state)
            except Exception:
                pass
        final_state = "STOPPED_SAFE"
        reason = state.get("stop_reason") or "normal"
        # collect_stop closed the final immutable segment after recording the
        # terminal intent.  Do not create a new mutable tail merely to repeat
        # that fact after the cut.
        if reason != "collect_and_stop":
            log_event(paths, state, {
                "type": "worker_stopped", "tick": int(runtime.current_tick),
                "reason": reason, "pid": os.getpid(),
            })
        atomic_json(paths["controller"], state)
        write_status(paths, state, runtime, final_state, reason)
        return 0


def submit_command(root: Path, operation: str, arguments: dict[str, Any],
                   timeout: float = 120.0) -> dict[str, Any]:
    paths = root_paths(root)
    if not paths["instance"].exists():
        raise RuntimeError("habitat is not initialized")
    command_id = f"{utc_now().strftime('%Y%m%dT%H%M%S%fZ')}_{uuid.uuid4().hex[:8]}"
    command = {
        "schema": "mente-basal.command.v1", "id": command_id,
        "submitted_utc": iso_utc(), "operation": operation,
        "arguments": arguments,
    }
    temporary = paths["pending"] / f".{command_id}.tmp"
    final = paths["pending"] / f"{command_id}.json"
    atomic_json(temporary, command)
    os.replace(temporary, final)
    response = paths["responses"] / f"{command_id}.json"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if response.exists():
            return load_json(response)
        time.sleep(0.2)
    raise TimeoutError(f"worker did not answer command {command_id}")


def package_collection(root: Path, descriptor_path: Path, output: Path,
                       first_session: bool = False) -> dict[str, Any]:
    paths = root_paths(root)
    root_resolved = paths["root"].resolve()
    descriptor_path = descriptor_path.resolve()
    if root_resolved not in descriptor_path.parents:
        raise RuntimeError("collection descriptor escapes habitat root")
    descriptor = load_json(descriptor_path)
    if descriptor.get("schema") != "mente-basal.collection.v1":
        raise RuntimeError("unsupported collection descriptor")
    if output.exists():
        raise RuntimeError(f"refusing to overwrite collection: {output}")

    def source_for(relative: str) -> Path:
        candidate_relative = Path(relative)
        if candidate_relative.is_absolute() or ".." in candidate_relative.parts:
            raise RuntimeError(f"unsafe collection member: {relative}")
        candidate = (root_resolved / candidate_relative).resolve()
        if root_resolved not in candidate.parents:
            raise RuntimeError(f"collection member escapes habitat root: {relative}")
        if not candidate.exists() or not candidate.is_file():
            raise FileNotFoundError(candidate)
        return candidate

    def portable(relative: str) -> str:
        value = Path(relative)
        if value.is_absolute() or ".." in value.parts:
            raise RuntimeError(f"unsafe archive path: {relative}")
        return value.as_posix()

    relative_files: set[str] = set(descriptor["immutable_files"])
    start_checkpoint = descriptor.get("start_checkpoint")
    end_checkpoint = descriptor.get("end_checkpoint")
    if not start_checkpoint or not end_checkpoint:
        raise RuntimeError("collection requires start and end checkpoints")
    for checkpoint_relative in (str(start_checkpoint), str(end_checkpoint)):
        relative_files.add(checkpoint_relative)
        sidecar = checkpoint_relative + ".json"
        source_for(sidecar)
        relative_files.add(sidecar)
    relative_files.add(str(descriptor_path.relative_to(paths["root"])))

    # Every cut is independently runnable from its start/end boundary.  The
    # large Python target directory and prior ZIPs are deliberately excluded;
    # bootstrap installs the one immutable local wheel included below.
    instance = load_json(paths["instance"])
    relative_files.add(str(paths["instance"].relative_to(paths["root"])))
    static_roots = ["app", "tools", "config", "docs"]
    if first_session:
        relative_files.add(instance["x0"])
        relative_files.add(instance["x0"] + ".json")
        static_roots.extend(["analysis", "validation"])
    for name in static_roots:
        base = paths["root"] / name
        if not base.exists():
            continue
        for item in base.rglob("*"):
            relative = item.relative_to(paths["root"])
            blocked_part = any(part in ("__pycache__", ".runtime", "python_site")
                               for part in relative.parts)
            if (item.is_file() and not blocked_part and
                    item.suffix.lower() not in (".pyc", ".pyo", ".zip")):
                relative_files.add(str(relative))
    wheel = paths["root"] / "baseline" / "dee_thinking-2.2.0-cp313-cp313-win_amd64.whl"
    if not wheel.exists():
        raise FileNotFoundError(wheel)
    relative_files.add(str(wheel.relative_to(paths["root"])))

    archive_sources: dict[str, Path] = {}

    def add_archive_source(archive_relative: str, source: Path) -> None:
        archive_relative = portable(archive_relative)
        previous = archive_sources.get(archive_relative)
        if previous is not None and previous != source:
            raise RuntimeError(f"archive path collision: {archive_relative}")
        archive_sources[archive_relative] = source

    for relative in sorted(relative_files):
        add_archive_source(relative, source_for(relative))

    # Frozen cut-state files are also installed at the canonical paths used by
    # the worker.  Their originals remain beside the descriptor as immutable
    # evidence of exactly which files were remapped.
    canonical_control = {
        "world/controller.json": descriptor["controller_snapshot"],
        "world/status.json": descriptor["status_snapshot"],
        "world/latest_checkpoint.txt": descriptor["latest_pointer_snapshot"],
    }
    for archive_relative, source_relative in canonical_control.items():
        add_archive_source(archive_relative, source_for(str(source_relative)))

    prefix = ("MENTE_BASAL_HABITAT_PERSISTENTE_SESION_001" if first_session else
              f"MENTE_BASAL_COLLECTION_{descriptor['request_id']}")
    if any(not (character.isalnum() or character in "-_.") for character in prefix):
        raise RuntimeError("unsafe package prefix")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mente-basal-package-") as temporary:
        temporary_root = Path(temporary)
        staged_root = temporary_root / prefix
        staged_root.mkdir(parents=True)
        for archive_relative, source in sorted(archive_sources.items()):
            destination = staged_root / Path(archive_relative)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

        manifest_files = [{
            "path": archive_relative,
            "bytes": (staged_root / Path(archive_relative)).stat().st_size,
            "sha256": sha256(staged_root / Path(archive_relative)),
        } for archive_relative in sorted(archive_sources)]
        manifest = {
            "schema": "mente-basal.package.v1", "created_utc": iso_utc(),
            "world_id": descriptor["world_id"], "session_id": descriptor["session_id"],
            "start_tick": descriptor["start_tick"], "end_tick": descriptor["end_tick"],
            "start_checkpoint": str(start_checkpoint).replace("\\", "/"),
            "end_checkpoint": str(end_checkpoint).replace("\\", "/"),
            "first_session": first_session, "archive_root": prefix,
            "canonical_control_files": canonical_control,
            "files": manifest_files,
        }
        atomic_json(staged_root / "MANIFEST.json", manifest)

        candidate = temporary_root / output.name
        with zipfile.ZipFile(candidate, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for item in sorted(staged_root.rglob("*")):
                if item.is_file():
                    archive.write(item, item.relative_to(temporary_root).as_posix())
        with zipfile.ZipFile(candidate) as archive:
            bad = archive.testzip()
            if bad is not None:
                raise RuntimeError(f"corrupt archive member: {bad}")
            names = archive.namelist()
            if any(name.lower().endswith(".zip") for name in names):
                raise RuntimeError("nested ZIP detected")
            if any(".runtime/" in name or "python_site/" in name or
                   "__pycache__/" in name for name in names):
                raise RuntimeError("runtime/cache leaked into package")
            required_names = {
                f"{prefix}/MANIFEST.json",
                f"{prefix}/world/controller.json",
                f"{prefix}/world/status.json",
                f"{prefix}/world/latest_checkpoint.txt",
                f"{prefix}/{str(start_checkpoint).replace(os.sep, '/')}",
                f"{prefix}/{str(end_checkpoint).replace(os.sep, '/')}",
            }
            missing = sorted(required_names.difference(names))
            if missing:
                raise RuntimeError(f"package missing required members: {missing}")

        # Copy across volumes to a sibling temporary, verify that copy, then
        # atomically publish.  A failed build cannot leave a partial official
        # archive at the requested name.
        sibling = output.with_name(f".{output.name}.{uuid.uuid4().hex}.tmp")
        try:
            with candidate.open("rb") as source_stream, sibling.open("xb") as target_stream:
                shutil.copyfileobj(source_stream, target_stream, 1024 * 1024)
                target_stream.flush()
                os.fsync(target_stream.fileno())
            with zipfile.ZipFile(sibling) as archive:
                bad = archive.testzip()
                if bad is not None:
                    raise RuntimeError(f"corrupt staged publication member: {bad}")
            if output.exists():
                raise RuntimeError(f"refusing to overwrite collection: {output}")
            os.replace(sibling, output)
        finally:
            sibling.unlink(missing_ok=True)
    with zipfile.ZipFile(output) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"corrupt published archive member: {bad}")
    return {"path": str(output), "bytes": output.stat().st_size,
            "sha256": sha256(output), "entries": len(manifest["files"]) + 1,
            "start_tick": descriptor["start_tick"], "end_tick": descriptor["end_tick"]}


def replay(root: Path, start_checkpoint: Path, segment: Path, target_tick: int,
           output_checkpoint: Path, expected_checkpoint: Path | None = None) -> dict[str, Any]:
    runtime = dee.Runtime.load_snapshot(str(start_checkpoint))
    runtime.resume()
    start_tick = int(runtime.current_tick)
    if target_tick < start_tick:
        raise ValueError("target tick precedes replay checkpoint")
    events: list[dict[str, Any]] = []
    seen_receipt_ids: set[int] = set()
    with segment.open("r", encoding="utf-8") as stream:
        for line in stream:
            item = json.loads(line)
            if item.get("type") == "input_scheduled":
                command_tick = int(item["command_tick"])
                receipt_id = int(item["receipt_id"])
                if receipt_id in seen_receipt_ids:
                    raise RuntimeError(f"duplicate scheduled receipt in replay segment: {receipt_id}")
                seen_receipt_ids.add(receipt_id)
                # An input accepted exactly at the closing boundary belongs to
                # that cut even though it has not yet caused another tick.
                if start_tick <= command_tick <= target_tick:
                    events.append(item)
    events.sort(key=lambda value: (int(value["command_tick"]), int(value["receipt_id"])))
    scheduled = 0
    replayed_receipt_ids: list[int] = []
    logged_receipt_ids: list[int] = []
    for event in events:
        command_tick = int(event["command_tick"])
        if int(runtime.current_tick) < command_tick:
            runtime.run_until(command_tick)
        receipt = runtime.experience(str(event["channel"]), int(event["requested_tick"]),
                                     int(event["load"]))
        replayed_receipt_ids.append(int(receipt.id))
        logged_receipt_ids.append(int(event["receipt_id"]))
        scheduled += 1
    if int(runtime.current_tick) < target_tick:
        runtime.run_until(target_tick)
    if output_checkpoint.exists():
        raise RuntimeError(f"refusing to overwrite replay output: {output_checkpoint}")
    output_checkpoint.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_checkpoint.with_name(
        output_checkpoint.name + f".{uuid.uuid4().hex}.tmp")
    try:
        runtime.save_snapshot(str(temporary))
        verified = dee.Runtime.load_snapshot(str(temporary))
        if (int(verified.current_tick) != int(runtime.current_tick) or
                verified.raw_copy() != runtime.raw_copy() or
                verified.clock_copy() != runtime.clock_copy()):
            raise RuntimeError("replay snapshot verification failed")
        os.replace(temporary, output_checkpoint)
    finally:
        temporary.unlink(missing_ok=True)
    result: dict[str, Any] = {
        "start_tick": start_tick,
        "target_tick": int(runtime.current_tick), "events_replayed": scheduled,
        "logged_receipt_ids": logged_receipt_ids,
        "replayed_receipt_ids": replayed_receipt_ids,
        "receipt_ids_exact": logged_receipt_ids == replayed_receipt_ids,
        "output_checkpoint": str(output_checkpoint), "raw_exact": None,
        "clock_exact": None, "tick_exact": None, "receipts_exact": None,
    }
    if expected_checkpoint is not None:
        expected = dee.Runtime.load_snapshot(str(expected_checkpoint))
        def receipt_signature(item: Any) -> tuple[Any, ...]:
            return (int(item.id), str(item.kind), str(item.status),
                    int(item.requested_tick),
                    None if item.effective_tick is None else int(item.effective_tick),
                    tuple(item.channels), str(item.reason))
        result.update({
            "raw_exact": runtime.raw_copy() == expected.raw_copy(),
            "clock_exact": runtime.clock_copy() == expected.clock_copy(),
            "tick_exact": int(runtime.current_tick) == int(expected.current_tick),
            "receipts_exact": ([receipt_signature(item) for item in runtime.receipts] ==
                               [receipt_signature(item) for item in expected.receipts]),
        })
    return result


def evaluate_checkpoint(checkpoint: Path, output: Path) -> dict[str, Any]:
    runtime = dee.Runtime.load_snapshot(str(checkpoint))
    before_raw = runtime.raw_copy()
    before_clock = runtime.clock_copy()
    g = geometry()
    tick = int(runtime.current_tick)
    observations = {
        "response1": observe_site(runtime, g.response1),
        "response2": observe_site(runtime, g.response2),
        "response3": observe_site(runtime, g.response3),
        "context_hub": observe_site(runtime, g.aux_hub_context),
    }
    passive = before_raw == runtime.raw_copy() and before_clock == runtime.clock_copy()
    result = {
        "checkpoint": str(checkpoint), "tick": tick,
        "observer_passive": passive, "observations": observations,
        "interpretation": "diagnostic reading only; no claim of new learning",
    }
    atomic_json(output, result)
    return result


def self_test(root: Path, output: Path) -> dict[str, Any]:
    config = default_config()
    config["threads"] = 1
    runtime, g, _ = build_x0(config)
    # Schedule the same physical history without using a production tree.
    x0_raw = runtime.raw_copy()
    x0_clock = runtime.clock_copy()
    with tempfile.TemporaryDirectory(prefix="mente-basal-selftest-") as temporary:
        temp = Path(temporary)
        x0_clean = temp / "x0_clean.deetsnap"
        runtime.save_snapshot(str(x0_clean))
        segment = temp / "real_window.jsonl"
        receipt_sequence = 0
        for channel, load, at_tick, origin in INITIAL_INPUTS:
            receipt_sequence += 1
            append_jsonl(segment, {
                "type": "input_scheduled", "command_tick": 0,
                "receipt_id": receipt_sequence, "channel": channel,
                "load": load, "requested_tick": at_tick, "origin": origin,
            })
            runtime.experience(channel, at_tick, load)
        queued = temp / "queued_t0.deetsnap"
        runtime.save_snapshot(str(queued))

        continuous = dee.Runtime.load_snapshot(str(queued))
        continuous.run_until(34)
        science = {"response_before": int(
            continuous.observe(coordinate(g.response1)).record.s_reg)}
        continuous.run_until(38)
        science["environmental_revision"] = int(
            continuous.observe(coordinate(g.revision1)).record.s_reg)
        continuous.run_until(40)
        for channel, load, at_tick, origin in LATE_INPUTS:
            receipt_sequence += 1
            append_jsonl(segment, {
                "type": "input_scheduled", "command_tick": 40,
                "receipt_id": receipt_sequence, "channel": channel,
                "load": load, "requested_tick": at_tick, "origin": origin,
            })
            continuous.experience(channel, at_tick, load)
        middle = temp / "middle_t40.deetsnap"
        continuous.save_snapshot(str(middle))
        continuous.run_until(46)
        science["response_use1"] = int(
            continuous.observe(coordinate(g.response2)).record.s_reg)
        continuous.run_until(48)
        science["context_merge"] = int(
            continuous.observe(coordinate(g.aux_hub_context)).record.s_reg)
        continuous.run_until(58)
        science["response_use2"] = int(
            continuous.observe(coordinate(g.response3)).record.s_reg)
        continuous.run_until(T_REF)
        continuous_final = temp / "continuous_t64.deetsnap"
        continuous.save_snapshot(str(continuous_final))

        resumed = dee.Runtime.load_snapshot(str(middle))
        resumed.run_until(T_REF)
        a_exact = (continuous.raw_copy() == resumed.raw_copy() and
                   continuous.clock_copy() == resumed.clock_copy() and
                   int(continuous.current_tick) == int(resumed.current_tick) and
                   [(r.id, str(r.status), r.effective_tick) for r in continuous.receipts] ==
                   [(r.id, str(r.status), r.effective_tick) for r in resumed.receipts])

        replay_output = temp / "replay_t64.deetsnap"
        replay_result = replay(root, x0_clean, segment, T_REF, replay_output,
                               continuous_final)
        b_exact = bool(replay_result["raw_exact"] and replay_result["clock_exact"]
                       and replay_result["tick_exact"] and
                       replay_result["events_replayed"] == len(INITIAL_INPUTS) + len(LATE_INPUTS))

        # A new input during an established session is scheduled and applied.
        session = dee.Runtime.load_snapshot(str(queued))
        session.run_until(3)
        receipt = session.experience("external.port.alpha", 3, 41)
        session.advance(1)
        receipt_after = session.receipt(receipt.id)
        c_applied = (receipt_after is not None and
                     receipt_after.status == dee.EventStatus.APPLIED)

        session.pause()
        paused_tick = int(session.current_tick)
        pause_rejected = False
        try:
            session.advance(3)
        except RuntimeError as error:
            pause_rejected = "paused" in str(error).lower()
        time.sleep(0.05)
        d_paused = pause_rejected and int(session.current_tick) == paused_tick
        session.resume()

        first = temp / "first.deetsnap"
        second = temp / "second.deetsnap"
        session.save_snapshot(str(first))
        session.advance(1)
        session.save_snapshot(str(second))
        e_archive = first.exists() and second.exists() and first.read_bytes() != second.read_bytes()

        main_before = session.raw_copy(), session.clock_copy(), int(session.current_tick)
        branch = session.fork()
        branch.experience("external.port.alpha", int(branch.current_tick), 43)
        branch.advance(1)
        f_isolated = (session.raw_copy() == main_before[0] and
                      session.clock_copy() == main_before[1] and
                      int(session.current_tick) == main_before[2])

        invalid = temp / "invalid.deetsnap"
        invalid.write_bytes(b"not a DEE snapshot")
        latest_pointer = temp / "latest.txt"
        latest_pointer.write_text(str(first), encoding="utf-8")
        invalid_rejected = False
        try:
            dee.Runtime.load_snapshot(str(invalid))
        except Exception:
            invalid_rejected = True
        valid_path_after = Path(latest_pointer.read_text(encoding="utf-8"))
        valid_survives = (valid_path_after == first and
                          int(dee.Runtime.load_snapshot(str(valid_path_after)).current_tick) ==
                          int(session.current_tick) - 1)
        g_invalid = invalid_rejected and valid_survives

        before = session.raw_copy(), session.clock_copy(), int(session.current_tick)
        _ = session.observe(coordinate(g.response1))
        h_passive = (before[0] == session.raw_copy() and before[1] == session.clock_copy()
                     and before[2] == int(session.current_tick))

        dense = dee.Runtime.load_snapshot(str(queued))
        dense.execution_options = dee.TickOptions(dee.Backend.DENSE_SEQUENTIAL, 1)
        dense.run_until(40)
        for channel, load, at_tick, _ in LATE_INPUTS:
            dense.experience(channel, at_tick, load)
        dense.run_until(T_REF)
        backend_exact = (dense.raw_copy() == continuous.raw_copy() and
                         dense.clock_copy() == continuous.clock_copy())
    checks = {
        "A_continuous_equals_save_load_continue": a_exact,
        "B_replay_window_no_duplicate_inputs": b_exact,
        "C_session_input_receipt_applied": c_applied,
        "D_pause_does_not_advance": d_paused,
        "E_archive_does_not_overwrite_prior": e_archive,
        "F_diagnostic_branch_isolated": f_isolated,
        "G_invalid_checkpoint_rejected_valid_preserved": g_invalid,
        "H_observe_passive": h_passive,
        "dense_matches_lazy_at_T_ref": backend_exact,
        "X0_arrays_retained_before_scheduling": len(x0_raw) == N ** 3 and len(x0_clock) == N ** 3,
    }
    result = {
        "schema": "mente-basal.selftest.v1", "created_utc": iso_utc(),
        "product": "DEE thinking 2.2.0", "kernel": "DEE v27",
        "checks": checks, "all_passed": all(checks.values()),
        "science_readings": science,
    }
    atomic_json(output, result)
    return result


def cli() -> int:
    parser = argparse.ArgumentParser(description="Mente Basal persistent DEE habitat")
    sub = parser.add_subparsers(dest="command", required=True)
    init_p = sub.add_parser("init")
    init_p.add_argument("--root", type=Path, required=True)
    init_p.add_argument("--config", type=Path)
    worker_p = sub.add_parser("worker")
    worker_p.add_argument("--root", type=Path, required=True)
    command_p = sub.add_parser("command")
    command_p.add_argument("--root", type=Path, required=True)
    command_p.add_argument("--operation", required=True)
    command_p.add_argument("--arguments", default="{}")
    command_p.add_argument("--timeout", type=float, default=120.0)
    status_p = sub.add_parser("status")
    status_p.add_argument("--root", type=Path, required=True)
    replay_p = sub.add_parser("replay")
    replay_p.add_argument("--root", type=Path, required=True)
    replay_p.add_argument("--start", type=Path, required=True)
    replay_p.add_argument("--segment", type=Path, required=True)
    replay_p.add_argument("--to", type=int, required=True)
    replay_p.add_argument("--output", type=Path, required=True)
    replay_p.add_argument("--expected", type=Path)
    eval_p = sub.add_parser("evaluate")
    eval_p.add_argument("--checkpoint", type=Path, required=True)
    eval_p.add_argument("--output", type=Path, required=True)
    test_p = sub.add_parser("self-test")
    test_p.add_argument("--root", type=Path, required=True)
    test_p.add_argument("--output", type=Path, required=True)
    package_p = sub.add_parser("package")
    package_p.add_argument("--root", type=Path, required=True)
    package_p.add_argument("--descriptor", type=Path, required=True)
    package_p.add_argument("--output", type=Path, required=True)
    package_p.add_argument("--first-session", action="store_true")
    args = parser.parse_args()
    if args.command == "init":
        print(json.dumps(initialize(args.root, args.config), indent=2, ensure_ascii=False))
        return 0
    if args.command == "worker":
        return worker(args.root)
    if args.command == "command":
        arguments = json.loads(args.arguments)
        result = submit_command(args.root, args.operation, arguments, args.timeout)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result.get("ok") else 1
    if args.command == "status":
        print(json.dumps(load_json(root_paths(args.root)["status"]), indent=2,
                         ensure_ascii=False))
        return 0
    if args.command == "replay":
        result = replay(args.root, args.start, args.segment, args.to, args.output,
                        args.expected)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        exact_fields = ("raw_exact", "clock_exact", "tick_exact", "receipts_exact",
                        "receipt_ids_exact")
        return 0 if all(result.get(name) is not False for name in exact_fields) else 1
    if args.command == "evaluate":
        print(json.dumps(evaluate_checkpoint(args.checkpoint, args.output), indent=2,
                         ensure_ascii=False))
        return 0
    if args.command == "self-test":
        result = self_test(args.root, args.output)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["all_passed"] else 1
    if args.command == "package":
        result = package_collection(args.root, args.descriptor, args.output,
                                    args.first_session)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    try:
        raise SystemExit(cli())
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise
