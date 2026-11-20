from __future__ import annotations

"""Supervisor and immutable finalizer for the MBP2 A/B/C campaign.

All mutations of a world go through ``app/mbp2.py``.  The supervisor owns
wall-clock policy, starts the three workers through ``launch_process.py``,
requests one midpoint save, and seals every world with a deterministic
``collect_stop`` request.  Once the terminal evidence has been validated the
worlds are never started or commanded again; only atomic packaging may be
retried.

The same implementation is used for the two-hour campaign and the 60-second
trial.  ``--trial`` only changes defaults (root, id, duration and ZIP name).
Importing this module has no side effects.
"""

import argparse
import concurrent.futures
import ctypes
import datetime as dtm
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable, Sequence


SCHEMA = "mbp2.campaign.v1"
TERMINAL_VALIDATION_SCHEMA = "mbp2.terminal-validation.v1"
ANALYSIS_SCHEMA = "mbp2.campaign-analysis.v1"
PACKAGE_SCHEMA = "mbp2.campaign-package.v1"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MBP2_SCRIPT = Path(__file__).resolve().with_name("mbp2.py")
ANALYZE_SCRIPT = Path(__file__).resolve().with_name("analyze.py")
LAUNCH_SCRIPT = Path(__file__).resolve().with_name("launch_process.py")
DEFAULT_PYTHON = Path(r"D:\Descargas\ANACONDA MINICONDA\python.exe")
MAIN_OUTPUT_NAME = "MENTE_BASAL_PERSISTENTE_2_ABC_2H_RESULTADOS.zip"
TRIAL_OUTPUT_NAME = "MENTE_BASAL_PERSISTENTE_2_ABC_TRIAL_60S_RESULTADOS.zip"
ARCHIVE_ROOT_MAIN = "MENTE_BASAL_PERSISTENTE_2_ABC_2H_RESULTADOS"
WORLD_SPECS: dict[str, dict[str, str]] = {
    "A": {"world_id": "MBP2-A-AISLAMIENTO", "name": "AISLAMIENTO"},
    "B": {"world_id": "MBP2-B-INTERACTIVO", "name": "INTERACTIVO"},
    "C": {"world_id": "MBP2-C-CONTROL", "name": "CONTROL"},
}
TERMINAL_STATES = {"STOPPED", "STOPPED_SAFE"}
SEALED_PHASES = {
    "TERMINAL_VALIDATED", "ANALYZED", "PACKAGING", "PACKAGE_FAILED", "FINAL_READY"
}


def utc_now() -> dtm.datetime:
    return dtm.datetime.now(dtm.timezone.utc)


def iso_utc(value: dtm.datetime | None = None) -> str:
    return (value or utc_now()).astimezone(dtm.timezone.utc).isoformat(
        timespec="milliseconds")


def iso_local(value: dtm.datetime | None = None) -> str:
    return (value or utc_now()).astimezone().isoformat(timespec="milliseconds")


def parse_utc(value: str) -> dtm.datetime:
    parsed = dtm.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("UTC timestamps must include a timezone")
    return parsed.astimezone(dtm.timezone.utc)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        last_error: OSError | None = None
        for attempt in range(40):
            try:
                os.replace(temporary, path)
                return
            except PermissionError as error:
                last_error = error
                time.sleep(min(0.01 * (attempt + 1), 0.10))
        assert last_error is not None
        raise last_error
    finally:
        temporary.unlink(missing_ok=True)


def atomic_json(path: Path, value: Any) -> None:
    atomic_text(path, json.dumps(value, indent=2, ensure_ascii=False,
                                 sort_keys=True) + "\n")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_relative(root: Path, relative: str | Path, *, require_file: bool = True) -> Path:
    value = Path(relative)
    if value.is_absolute() or ".." in value.parts:
        raise RuntimeError(f"unsafe relative path: {relative}")
    root = root.resolve()
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise RuntimeError(f"path escapes root: {relative}") from error
    if require_file and not candidate.is_file():
        raise FileNotFoundError(candidate)
    return candidate


def safe_token(value: str, *, maximum: int = 64) -> str:
    token = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-.")
    if not token:
        token = "MBP2"
    if ".." in token:
        token = token.replace("..", ".")
    if len(token) <= maximum:
        return token
    suffix = hashlib.sha256(token.encode("utf-8")).hexdigest()[:12]
    return f"{token[:maximum - len(suffix) - 1]}-{suffix}"


def final_request_id(campaign_id: str, condition: str) -> str:
    condition = condition.upper()
    if condition not in WORLD_SPECS:
        raise ValueError("condition must be A, B or C")
    return safe_token(f"FINAL_{campaign_id}_{condition}")


@dataclass(frozen=True)
class Layout:
    project_root: Path
    campaign_root: Path
    campaign_id: str
    duration_seconds: float
    output: Path
    python: Path
    worlds: dict[str, Path]
    trial: bool

    @property
    def supervisor(self) -> Path:
        return self.campaign_root / "supervisor"

    @property
    def state_path(self) -> Path:
        return self.supervisor / "campaign.json"

    @property
    def terminal_validation_path(self) -> Path:
        return self.supervisor / "terminal_validation.json"

    @property
    def analysis_path(self) -> Path:
        return self.campaign_root / "analysis" / "FINAL_ANALYSIS.json"


def layout_from_args(args: argparse.Namespace) -> Layout:
    trial = bool(args.trial)
    campaign_root = (args.campaign_root or
                     (PROJECT_ROOT / "test_campaign" if trial else PROJECT_ROOT)).resolve()
    duration = args.duration_seconds
    if duration is None:
        duration = 60.0 if trial else 7200.0
    if not (0 < float(duration) <= 7 * 24 * 3600):
        raise ValueError("duration must be in (0, 604800] seconds")
    campaign_id = str(args.campaign_id or
                      ("MBP2-ABC-TRIAL-60S" if trial else "MBP2-ABC-2H"))
    campaign_id = safe_token(campaign_id)
    output = (args.output or campaign_root /
              (TRIAL_OUTPUT_NAME if trial else MAIN_OUTPUT_NAME)).resolve()
    explicit_worlds = {
        "A": args.world_a_root,
        "B": args.world_b_root,
        "C": args.world_c_root,
    }
    worlds = {
        condition: (explicit_worlds[condition] or
                    campaign_root / "worlds" / condition).resolve()
        for condition in WORLD_SPECS
    }
    if len({str(path).casefold() for path in worlds.values()}) != 3:
        raise ValueError("A, B and C must use three distinct world roots")
    return Layout(
        project_root=PROJECT_ROOT.resolve(),
        campaign_root=campaign_root,
        campaign_id=campaign_id,
        duration_seconds=float(duration),
        output=output,
        python=Path(args.python).resolve(),
        worlds=worlds,
        trial=trial,
    )


def _state_event(state: dict[str, Any], event: str, **details: Any) -> None:
    record = {"utc": iso_utc(), "event": event, **details}
    events = state.setdefault("events", [])
    events.append(record)
    if len(events) > 512:
        del events[:-512]
    state["updated_utc"] = record["utc"]


def _save_state(layout: Layout, state: dict[str, Any]) -> None:
    state["updated_utc"] = iso_utc()
    atomic_json(layout.state_path, state)


def _load_state(layout: Layout) -> dict[str, Any]:
    if not layout.state_path.is_file():
        raise RuntimeError(f"campaign is not prepared: {layout.state_path}")
    state = load_json(layout.state_path)
    if state.get("schema") != SCHEMA:
        raise RuntimeError("unsupported campaign state schema")
    _assert_layout_matches_state(layout, state)
    return state


def _assert_layout_matches_state(layout: Layout, state: dict[str, Any]) -> None:
    errors: list[str] = []
    if state.get("campaign_id") != layout.campaign_id:
        errors.append("campaign_id")
    if Path(state.get("campaign_root", "")).resolve() != layout.campaign_root:
        errors.append("campaign_root")
    if Path(state.get("output", "")).resolve() != layout.output:
        errors.append("output")
    for condition, root in layout.worlds.items():
        recorded = state.get("worlds", {}).get(condition, {}).get("root", "")
        if Path(recorded).resolve() != root:
            errors.append(f"world_{condition}_root")
    if errors:
        raise RuntimeError(f"CLI configuration disagrees with campaign state: {errors}")


def _decode_json_output(completed: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    if completed.returncode != 0:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {completed.args}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}")
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"command did not emit JSON: {completed.args}\n{completed.stdout}\n"
            f"{completed.stderr}") from error
    if not isinstance(value, dict):
        raise RuntimeError("command JSON result must be an object")
    return value


def _run_json_command(command: Sequence[str], *, timeout: float) -> dict[str, Any]:
    completed = subprocess.run(
        list(command), capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=timeout, check=False)
    return _decode_json_output(completed)


def _mbp2(layout: Layout, arguments: Sequence[str], *, timeout: float = 180.0) -> dict[str, Any]:
    if not layout.python.is_file():
        raise FileNotFoundError(layout.python)
    if not MBP2_SCRIPT.is_file():
        raise FileNotFoundError(MBP2_SCRIPT)
    return _run_json_command(
        [str(layout.python), str(MBP2_SCRIPT), *[str(item) for item in arguments]],
        timeout=timeout,
    )


def _world_status(layout: Layout, condition: str) -> dict[str, Any] | None:
    status_path = layout.worlds[condition] / "world" / "status.json"
    if not status_path.is_file():
        return None
    # Status is intentionally obtained through the public world CLI.
    # On Windows the atomic status publication can produce a very short
    # sharing/access-denied window while os.replace completes.  A health
    # sampler must not kill the independent supervisor because one passive
    # read raced that boundary.  Only this diagnosed transient is retried;
    # malformed JSON, a missing process, or another command failure still
    # propagates.
    last_error: Exception | None = None
    for attempt in range(8):
        try:
            return _mbp2(layout, [
                "status", "--root", str(layout.worlds[condition])], timeout=60.0)
        except RuntimeError as error:
            last_error = error
            text = str(error)
            if "PermissionError" not in text and "Access is denied" not in text:
                raise
            time.sleep(0.05 * (attempt + 1))
    assert last_error is not None
    raise last_error


def _world_command(
    layout: Layout,
    condition: str,
    operation: str,
    arguments: dict[str, Any],
    *,
    timeout: float,
) -> dict[str, Any]:
    return _mbp2(layout, [
        "command", "--root", str(layout.worlds[condition]),
        "--operation", operation,
        "--arguments", json.dumps(arguments, ensure_ascii=False, sort_keys=True),
        "--timeout", str(timeout),
    ], timeout=timeout + 30.0)


def _parallel(
    function: Callable[[str], Any], conditions: Iterable[str] = WORLD_SPECS,
) -> tuple[dict[str, Any], dict[str, str]]:
    results: dict[str, Any] = {}
    errors: dict[str, str] = {}
    selected = list(conditions)
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(selected)) as executor:
        futures = {executor.submit(function, condition): condition for condition in selected}
        for future in concurrent.futures.as_completed(futures):
            condition = futures[future]
            try:
                results[condition] = future.result()
            except Exception as error:
                errors[condition] = f"{type(error).__name__}: {error}"
    return results, errors


def _initial_state(layout: Layout) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "campaign_id": layout.campaign_id,
        "mode": "trial" if layout.trial else "main",
        "campaign_root": str(layout.campaign_root),
        "project_root": str(layout.project_root),
        "python": str(layout.python),
        "duration_seconds": layout.duration_seconds,
        "output": str(layout.output),
        "phase": "PREPARING",
        "sealed": False,
        "created_utc": iso_utc(),
        "updated_utc": iso_utc(),
        "started_utc": None,
        "midpoint_utc": None,
        "deadline_utc": None,
        "midpoint": {"attempted": False, "responses": {}, "errors": {}},
        "final_request_ids": {
            condition: final_request_id(layout.campaign_id, condition)
            for condition in WORLD_SPECS
        },
        "worlds": {
            condition: {
                "condition": condition,
                "name": spec["name"],
                "world_id": spec["world_id"],
                "root": str(layout.worlds[condition]),
                "config": str(layout.campaign_root / "config" /
                              f"mbp2_{condition}.json"),
                "initialized": False,
                "launches": [],
                "final_command_submitted_utc": None,
                "final_response": None,
                "descriptor": None,
            }
            for condition, spec in WORLD_SPECS.items()
        },
        "events": [],
        "package_attempts": [],
        "final_package": None,
    }


def _valid_existing_package(layout: Layout) -> dict[str, Any] | None:
    if not layout.output.is_file():
        return None
    try:
        return verify_zip(layout.output, expected_campaign_id=layout.campaign_id,
                          extract_to=None, layout=None)
    except Exception:
        return None


def prepare(layout: Layout) -> dict[str, Any]:
    """Create and initialize the three worlds without starting workers."""
    if _valid_existing_package(layout) is not None:
        existing = _valid_existing_package(layout)
        return {"status": "ALREADY_FINAL_READY", **(existing or {}),
                "output": str(layout.output), "new_collect_stop_commands": 0}
    layout.campaign_root.mkdir(parents=True, exist_ok=True)
    for name in ("config", "worlds", "supervisor", "analysis", "validation"):
        (layout.campaign_root / name).mkdir(parents=True, exist_ok=True)
    if layout.state_path.exists():
        state = _load_state(layout)
        if state.get("phase") != "PREPARING":
            return {"status": "ALREADY_PREPARED", "phase": state.get("phase"),
                    "state": str(layout.state_path)}
    else:
        state = _initial_state(layout)
        _state_event(state, "preparation_started")
        _save_state(layout, state)

    for condition, spec in WORLD_SPECS.items():
        world_root = layout.worlds[condition]
        world_root.parent.mkdir(parents=True, exist_ok=True)
        config_path = Path(state["worlds"][condition]["config"])
        config = {
            "schema": "mente-basal-persistente-2.world.v1",
            "application_version": "2.0.0",
            "campaign_id": layout.campaign_id,
            "world_id": spec["world_id"],
            "condition": condition,
            # The supervisor owns the exact common deadline.  This internal
            # bound is deliberately later and remains a fail-safe only.
            "max_autonomous_hours": max(1.0, layout.duration_seconds / 3600.0 + 1.0),
            "start_paused": True,
        }
        if config_path.exists():
            existing_config = load_json(config_path)
            for key in ("campaign_id", "world_id", "condition"):
                if existing_config.get(key) != config[key]:
                    raise RuntimeError(f"existing {config_path} has wrong {key}")
        else:
            atomic_json(config_path, config)
        instance_path = world_root / "world" / "instance.json"
        if instance_path.exists():
            instance = load_json(instance_path)
            for key, expected in {
                "campaign_id": layout.campaign_id,
                "world_id": spec["world_id"],
                "condition": condition,
            }.items():
                if instance.get(key) != expected:
                    raise RuntimeError(f"existing world {condition} has wrong {key}")
        else:
            instance = _mbp2(layout, [
                "init", "--root", str(world_root), "--config", str(config_path)
            ], timeout=900.0)
        state["worlds"][condition]["initialized"] = True
        state["worlds"][condition]["instance"] = instance
        _state_event(state, "world_initialized", condition=condition,
                     world_id=spec["world_id"])
        _save_state(layout, state)
    state["phase"] = "PREPARED"
    _state_event(state, "preparation_completed")
    _save_state(layout, state)
    return {
        "status": "PREPARED",
        "campaign_id": layout.campaign_id,
        "duration_seconds": layout.duration_seconds,
        "state": str(layout.state_path),
        "worlds": {key: str(value) for key, value in layout.worlds.items()},
        "output": str(layout.output),
    }


def process_is_alive(pid: int | None) -> bool:
    """Return whether *pid* currently denotes a live process.

    A stale worker PID is part of the terminal evidence, so access failures are
    treated conservatively as "alive" rather than accidentally sealing a world
    whose writer might still exist.
    """
    if pid is None or int(pid) <= 0:
        return False
    pid = int(pid)
    if pid == os.getpid():
        return True
    if os.name == "nt":
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        STILL_ACTIVE = 259
        # use_last_error is required: ctypes.windll.GetLastError may otherwise
        # expose a stale error from an unrelated call and turn a dead PID into
        # a false positive.
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
        kernel32.OpenProcess.restype = ctypes.c_void_p
        kernel32.GetExitCodeProcess.argtypes = [ctypes.c_void_p,
                                                ctypes.POINTER(ctypes.c_uint32)]
        kernel32.GetExitCodeProcess.restype = ctypes.c_int
        kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, 0, pid)
        if not handle:
            error = int(ctypes.get_last_error())
            # ERROR_INVALID_PARAMETER means there is no process with this PID.
            return error not in (87, 1168)
        try:
            exit_code = ctypes.c_uint32(0)
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                return True
            return int(exit_code.value) == STILL_ACTIVE
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def writer_lock_available(path: Path) -> tuple[bool, str]:
    """Probe the habitat's byte-range writer lock without changing its data."""
    if not path.is_file():
        return False, "writer lock file is missing"
    try:
        stream = path.open("r+b", buffering=0)
    except OSError as error:
        return False, f"writer lock cannot be opened yet: {error}"
    try:
        stream.seek(0)
        if os.name == "nt":
            import msvcrt
            try:
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as error:
                return False, f"writer lock is held: {error}"
            try:
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            finally:
                stream.seek(0)
            return True, "writer lock is free"
        import fcntl
        try:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            return False, f"writer lock is held: {error}"
        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        return True, "writer lock is free"
    finally:
        stream.close()


def _pid_from_file(path: Path) -> int | None:
    try:
        value = int(path.read_text(encoding="utf-8").strip())
        return value if value > 0 else None
    except (FileNotFoundError, OSError, ValueError):
        return None


def _launch_worker(layout: Layout, state: dict[str, Any], condition: str) -> dict[str, Any]:
    existing_status = _world_status(layout, condition)
    lock_free, lock_detail = writer_lock_available(
        layout.worlds[condition] / "world" / "writer.lock")
    if (existing_status and existing_status.get("state") in {"RUNNING", "PAUSED"} and
            process_is_alive(existing_status.get("pid")) and not lock_free and
            "held" in lock_detail.lower()):
        return {"status": "ALREADY_RUNNING", "pid": existing_status.get("pid"),
                "writer_lock": lock_detail}
    launch_number = len(state["worlds"][condition].setdefault("launches", [])) + 1
    handshake = layout.supervisor / f"launch_{condition}_{launch_number:02d}.json"
    world_root = layout.worlds[condition]
    command = [
        str(layout.python), str(LAUNCH_SCRIPT),
        "--python", str(layout.python),
        "--script", str(MBP2_SCRIPT),
        "--cwd", str(layout.project_root),
        "--stdout", str(world_root / "world" / "worker.stdout.log"),
        "--stderr", str(world_root / "world" / "worker.stderr.log"),
        "--handshake", str(handshake),
        # The supervisor itself is already a detached independent process. On
        # Windows, requesting BREAKAWAY again from a process outside a job may
        # return ACCESS_DENIED; the launcher then safely retries without it.
        "--allow-job-inheritance",
        "--", "worker", "--root", str(world_root),
    ]
    result = _run_json_command(command, timeout=60.0)
    if result.get("status") != "STARTED" or not result.get("child_pid"):
        raise RuntimeError(f"worker {condition} did not start: {result}")
    record = {
        "utc": iso_utc(), "handshake": str(handshake),
        "pid": int(result["child_pid"]), "result": result,
    }
    state["worlds"][condition]["launches"].append(record)
    _state_event(state, "worker_launched", condition=condition,
                 pid=int(result["child_pid"]))
    _save_state(layout, state)
    return result


def _wait_worker_ready(
    layout: Layout, condition: str, *, timeout: float = 120.0,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    last: dict[str, Any] | None = None
    while time.monotonic() < deadline:
        try:
            last = _world_status(layout, condition)
        except Exception:
            last = None
        if last and process_is_alive(last.get("pid")) and last.get("state") in {
                "PAUSED", "RUNNING"}:
            return last
        time.sleep(0.25)
    raise TimeoutError(f"worker {condition} did not become ready; last status={last}")


def _start_worlds(
    layout: Layout, state: dict[str, Any], *, command_timeout: float,
    release: bool,
) -> dict[str, Any]:
    launches: dict[str, Any] = {}
    for condition in WORLD_SPECS:
        launches[condition] = _launch_worker(layout, state, condition)
    ready, ready_errors = _parallel(lambda c: _wait_worker_ready(layout, c))
    if ready_errors:
        raise RuntimeError(f"workers failed readiness: {ready_errors}")
    responses: dict[str, Any] = {}
    if release:
        responses, errors = _parallel(lambda c: _world_command(
            layout, c, "release_autonomy", {}, timeout=command_timeout))
        bad = {key: value for key, value in responses.items() if not value.get("ok")}
        if errors or bad:
            raise RuntimeError(f"autonomy release failed: errors={errors}, responses={bad}")
        _state_event(state, "autonomy_released", responses=responses)
        _save_state(layout, state)
    return {"launches": launches, "ready": ready, "release": responses}


def _descriptor_candidates(world_root: Path, request_id: str) -> list[Path]:
    return sorted((world_root / "history" / "collections").glob(
        f"cut_{request_id}_t*.json"))


def _descriptor_for(world_root: Path, request_id: str) -> Path | None:
    candidates = _descriptor_candidates(world_root, request_id)
    if len(candidates) > 1:
        raise RuntimeError(f"multiple descriptors for permanent request {request_id}")
    return candidates[0] if candidates else None


def validate_terminal_world(
    world_root: Path,
    *,
    condition: str,
    campaign_id: str,
    request_id: str,
) -> dict[str, Any]:
    """Validate the complete immutable/OS terminal boundary for one world."""
    world_root = world_root.resolve()
    errors: list[str] = []
    checks: dict[str, Any] = {}
    descriptor_path: Path | None = None
    descriptor: dict[str, Any] = {}
    checkpoint: Path | None = None
    sidecar: Path | None = None
    status: dict[str, Any] = {}
    instance: dict[str, Any] = {}
    try:
        descriptor_path = _descriptor_for(world_root, request_id)
        if descriptor_path is None:
            raise FileNotFoundError(f"descriptor for {request_id}")
        descriptor = load_json(descriptor_path)
        checks["descriptor"] = str(descriptor_path)
        if descriptor.get("schema") != "mente-basal.collection.v1":
            errors.append("descriptor schema is not mente-basal.collection.v1")
        if descriptor.get("request_id") != request_id:
            errors.append("descriptor request_id mismatch")
        if descriptor.get("stop_after") is not True:
            errors.append("descriptor is not a collect_stop boundary")
    except Exception as error:
        errors.append(f"descriptor invalid: {error}")

    try:
        instance = load_json(world_root / "world" / "instance.json")
        checks["instance"] = {
            "campaign_id": instance.get("campaign_id"),
            "world_id": instance.get("world_id"),
            "condition": instance.get("condition"),
            "session_id": instance.get("session_id"),
        }
        expected_world_id = WORLD_SPECS[condition]["world_id"]
        if instance.get("campaign_id") != campaign_id:
            errors.append("instance campaign_id mismatch")
        if instance.get("condition") != condition:
            errors.append("instance condition mismatch")
        if instance.get("world_id") != expected_world_id:
            errors.append("instance world_id mismatch")
        if descriptor and descriptor.get("world_id") != expected_world_id:
            errors.append("descriptor world_id mismatch")
        if descriptor and descriptor.get("session_id") != instance.get("session_id"):
            errors.append("descriptor session_id mismatch")
    except Exception as error:
        errors.append(f"instance invalid: {error}")

    if descriptor:
        try:
            end_relative = str(descriptor["end_checkpoint"])
            checkpoint = safe_relative(world_root, end_relative)
            if (world_root / "world" / "checkpoints").resolve() not in checkpoint.parents:
                errors.append("end checkpoint is outside world/checkpoints")
            sidecar = Path(str(checkpoint) + ".json")
            if not sidecar.is_file():
                raise FileNotFoundError(sidecar)
            metadata = load_json(sidecar)
            actual_hash = sha256(checkpoint)
            checks["checkpoint"] = {
                "relative": end_relative,
                "bytes": checkpoint.stat().st_size,
                "sha256": actual_hash,
                "sidecar": str(sidecar),
                "tick": metadata.get("tick"),
            }
            if metadata.get("sha256") != actual_hash:
                errors.append("checkpoint SHA-256 differs from sidecar")
            if int(metadata.get("bytes", -1)) != checkpoint.stat().st_size:
                errors.append("checkpoint byte count differs from sidecar")
            if metadata.get("world_id") != descriptor.get("world_id"):
                errors.append("checkpoint sidecar world_id mismatch")
            if metadata.get("session_id") != descriptor.get("session_id"):
                errors.append("checkpoint sidecar session_id mismatch")
            if int(metadata.get("tick", -1)) != int(descriptor.get("end_tick", -2)):
                errors.append("checkpoint tick differs from descriptor")
            frozen_pointer = safe_relative(
                world_root, str(descriptor["latest_pointer_snapshot"]))
            if frozen_pointer.read_text(encoding="utf-8").strip() != end_relative:
                errors.append("frozen latest pointer differs from end checkpoint")
            live_pointer = world_root / "world" / "latest_checkpoint.txt"
            if live_pointer.read_text(encoding="utf-8").strip() != end_relative:
                errors.append("live latest pointer differs from end checkpoint")
            for key in ("controller_snapshot", "status_snapshot",
                        "history_segment", "telemetry_segment"):
                safe_relative(world_root, str(descriptor[key]))
            for member in descriptor.get("immutable_files", []):
                safe_relative(world_root, str(member))
        except Exception as error:
            errors.append(f"checkpoint evidence invalid: {error}")

    try:
        status = load_json(world_root / "world" / "status.json")
        checks["status"] = status
        if status.get("state") not in TERMINAL_STATES:
            errors.append(f"status is not terminal: {status.get('state')}")
        if descriptor and status.get("last_checkpoint") != descriptor.get("end_checkpoint"):
            errors.append("terminal status checkpoint differs from descriptor")
        if instance and status.get("session_id") != instance.get("session_id"):
            errors.append("terminal status session_id mismatch")
    except Exception as error:
        errors.append(f"terminal status invalid: {error}")

    pids: set[int] = set()
    for candidate in (status.get("pid") if status else None,
                      _pid_from_file(world_root / "world" / "worker.pid")):
        try:
            if candidate is not None and int(candidate) > 0:
                pids.add(int(candidate))
        except (TypeError, ValueError):
            errors.append(f"invalid worker PID: {candidate!r}")
    pid_states = {str(pid): process_is_alive(pid) for pid in sorted(pids)}
    checks["pid_alive"] = pid_states
    if any(pid_states.values()):
        errors.append(f"worker PID is still alive: {pid_states}")
    lock_free, lock_detail = writer_lock_available(world_root / "world" / "writer.lock")
    checks["writer_lock"] = {"available": lock_free, "detail": lock_detail}
    if not lock_free:
        errors.append(lock_detail)

    return {
        "ok": not errors,
        "condition": condition,
        "world_root": str(world_root),
        "request_id": request_id,
        "descriptor": (str(descriptor_path.relative_to(world_root))
                       if descriptor_path else None),
        "end_checkpoint": descriptor.get("end_checkpoint"),
        "end_tick": descriptor.get("end_tick"),
        "checks": checks,
        "errors": errors,
    }


def _terminal_validations(layout: Layout, state: dict[str, Any]) -> dict[str, Any]:
    results = {
        condition: validate_terminal_world(
            layout.worlds[condition], condition=condition,
            campaign_id=layout.campaign_id,
            request_id=state["final_request_ids"][condition])
        for condition in WORLD_SPECS
    }
    return {
        "schema": TERMINAL_VALIDATION_SCHEMA,
        "created_utc": iso_utc(),
        "campaign_id": layout.campaign_id,
        "all_valid": all(item["ok"] for item in results.values()),
        "worlds": results,
    }


def _diagnose_checkpoint(
    layout: Layout, condition: str, checkpoint: Path, output: Path,
) -> dict[str, Any]:
    output.parent.mkdir(parents=True, exist_ok=True)
    return _mbp2(layout, [
        "diagnose", "--checkpoint", str(checkpoint), "--output", str(output),
        "--condition", condition,
    ], timeout=900.0)


def build_analysis(
    layout: Layout, state: dict[str, Any], validation: dict[str, Any],
) -> dict[str, Any]:
    """Run the dedicated offline analyzer against the frozen A/B/C cuts."""
    if not validation.get("all_valid"):
        raise RuntimeError("analysis requires three validated terminal worlds")
    if not ANALYZE_SCRIPT.is_file():
        raise FileNotFoundError(ANALYZE_SCRIPT)
    explicit_paths: list[str] = []
    for condition in WORLD_SPECS:
        item = validation["worlds"][condition]
        explicit_paths.append(str(safe_relative(
            layout.worlds[condition], item["descriptor"])))
        explicit_paths.extend(str(path.resolve()) for path in sorted(
            (layout.worlds[condition] / "world" / "checkpoints").glob("*.deetsnap")))
    cuts_path = layout.supervisor / "analysis_cuts.json"
    atomic_json(cuts_path, {
        "schema": "mbp2.analysis-cuts.v1", "campaign_id": layout.campaign_id,
        "terminal_request_ids": state["final_request_ids"],
        "paths": sorted(set(explicit_paths)),
    })
    result = _run_json_command([
        str(layout.python), str(ANALYZE_SCRIPT),
        "--campaign-root", str(layout.campaign_root),
        "--cuts-json", str(cuts_path),
    ], timeout=1800.0)
    if not layout.analysis_path.is_file():
        raise RuntimeError("analyze.py did not publish FINAL_ANALYSIS.json")
    analysis = load_json(layout.analysis_path)
    if analysis.get("campaign_id") != layout.campaign_id:
        raise RuntimeError("offline analysis campaign_id mismatch")
    state["analysis_cli_result"] = result
    return analysis


def _blocked_package_path(relative: Path, output: Path, source: Path) -> bool:
    lowered = {part.casefold() for part in relative.parts}
    if lowered.intersection({"__pycache__", ".runtime", "python_site"}):
        return True
    if source.suffix.casefold() in {".pyc", ".pyo", ".tmp", ".zip"}:
        return True
    try:
        if source.resolve() == output.resolve():
            return True
    except OSError:
        pass
    return False


def _package_sources(
    layout: Layout, state: dict[str, Any], validation: dict[str, Any],
) -> dict[str, Path]:
    sources: dict[str, Path] = {}

    def add(archive_relative: str | Path, source: Path) -> None:
        archive_path = PurePosixPath(str(archive_relative).replace("\\", "/"))
        if archive_path.is_absolute() or ".." in archive_path.parts:
            raise RuntimeError(f"unsafe archive path: {archive_relative}")
        key = archive_path.as_posix()
        source = source.resolve()
        if not source.is_file():
            raise FileNotFoundError(source)
        previous = sources.get(key)
        if previous is not None and previous != source:
            raise RuntimeError(f"archive path collision: {key}")
        sources[key] = source

    def add_tree(archive_base: str, source_root: Path) -> None:
        if not source_root.is_dir():
            return
        for source in sorted(source_root.rglob("*")):
            if not source.is_file():
                continue
            relative = source.relative_to(source_root)
            if _blocked_package_path(relative, layout.output, source):
                continue
            add(PurePosixPath(archive_base) / PurePosixPath(relative.as_posix()), source)

    # Runtime code and the immutable wheel always come from the project root,
    # including in trial mode where campaign data lives below test_campaign.
    add_tree("app", layout.project_root / "app")
    wheel = layout.project_root / "baseline" / "dee_thinking-2.2.0-cp313-cp313-win_amd64.whl"
    add("baseline/dee_thinking-2.2.0-cp313-cp313-win_amd64.whl", wheel)
    for name in ("tools", "docs"):
        add_tree(name, layout.project_root / name)
    for name in ("config", "analysis", "validation"):
        add_tree(name, layout.campaign_root / name)
    campaign_report = layout.campaign_root / "docs" / "INFORME_INTEGRADO.md"
    if campaign_report.is_file():
        sources.pop("docs/INFORME_INTEGRADO.md", None)
        add("docs/INFORME_INTEGRADO.md", campaign_report)

    # Only stable supervisor evidence is packaged.  Temporary staging trees and
    # prior ZIPs are excluded by construction.
    for source in sorted(layout.supervisor.glob("*")):
        if source.is_file() and source.suffix.casefold() != ".tmp":
            add(PurePosixPath("supervisor") / source.name, source)
    for condition in WORLD_SPECS:
        add_tree(f"worlds/{condition}", layout.worlds[condition])

    if not layout.trial:
        trial_root = layout.project_root / "test_campaign"
        required_trial = [
            trial_root / "supervisor" / "campaign.json",
            trial_root / "supervisor" / "terminal_validation.json",
            trial_root / "analysis" / "FINAL_ANALYSIS.json",
            trial_root / "validation" / "PACKAGE_VALIDATION.json",
        ]
        missing_trial = [str(path) for path in required_trial if not path.is_file()]
        if missing_trial:
            raise RuntimeError(
                "main package requires completed trial evidence: " + repr(missing_trial))
        add("trial_evidence/supervisor/campaign.json", required_trial[0])
        add("trial_evidence/supervisor/terminal_validation.json", required_trial[1])
        add_tree("trial_evidence/analysis", trial_root / "analysis")
        add_tree("trial_evidence/validation", trial_root / "validation")
        trial_report = trial_root / "docs" / "INFORME_INTEGRADO.md"
        if trial_report.is_file():
            add("trial_evidence/docs/INFORME_INTEGRADO.md", trial_report)

    if not layout.state_path.is_file() or not layout.terminal_validation_path.is_file():
        raise RuntimeError("package requires campaign and terminal validation records")
    if not layout.analysis_path.is_file():
        raise RuntimeError("package requires completed analysis")
    for condition, item in validation["worlds"].items():
        expected = f"worlds/{condition}/{Path(item['descriptor']).as_posix()}"
        if expected not in sources:
            raise RuntimeError(f"descriptor omitted from package: {expected}")
    return sources


def _archive_root(layout: Layout) -> str:
    if not layout.trial and layout.output.name == MAIN_OUTPUT_NAME:
        return ARCHIVE_ROOT_MAIN
    return safe_token(layout.output.stem, maximum=120)


def _manifest(
    layout: Layout,
    state: dict[str, Any],
    validation: dict[str, Any],
    archive_root: str,
    staged_root: Path,
    payload_names: Sequence[str],
) -> dict[str, Any]:
    files = [{
        "path": name,
        "bytes": (staged_root / Path(name)).stat().st_size,
        "sha256": sha256(staged_root / Path(name)),
    } for name in sorted(payload_names)]
    worlds: dict[str, Any] = {}
    for condition, item in validation["worlds"].items():
        descriptor = load_json(safe_relative(layout.worlds[condition], item["descriptor"]))
        worlds[condition] = {
            "world_id": WORLD_SPECS[condition]["world_id"],
            "request_id": item["request_id"],
            "descriptor": f"worlds/{condition}/{Path(item['descriptor']).as_posix()}",
            "start_checkpoint": (
                f"worlds/{condition}/{Path(descriptor['start_checkpoint']).as_posix()}"),
            "end_checkpoint": (
                f"worlds/{condition}/{Path(descriptor['end_checkpoint']).as_posix()}"),
            "start_tick": descriptor["start_tick"],
            "end_tick": descriptor["end_tick"],
            "end_checkpoint_sha256": item["checks"]["checkpoint"]["sha256"],
        }
    return {
        "schema": PACKAGE_SCHEMA,
        "created_utc": iso_utc(),
        "campaign_id": layout.campaign_id,
        "mode": "trial" if layout.trial else "main",
        "duration_seconds": state["duration_seconds"],
        "archive_root": archive_root,
        "source_policy": "three terminal immutable collect_stop boundaries",
        "worlds": worlds,
        "files": files,
    }


def _safe_zip_names(archive: zipfile.ZipFile) -> list[str]:
    names = archive.namelist()
    if len(names) != len(set(names)):
        raise RuntimeError("ZIP contains duplicate names")
    for name in names:
        pure = PurePosixPath(name)
        if pure.is_absolute() or ".." in pure.parts or "\\" in name:
            raise RuntimeError(f"unsafe ZIP member: {name}")
    return names


def verify_zip(
    archive_path: Path,
    *,
    expected_campaign_id: str,
    extract_to: Path | None,
    layout: Layout | None,
) -> dict[str, Any]:
    """Check CRC, MANIFEST/HASHES, optional extraction and checkpoint loads."""
    with zipfile.ZipFile(archive_path) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"ZIP CRC failure: {bad}")
        names = _safe_zip_names(archive)
        manifest_names = [name for name in names if name.endswith("/MANIFEST.json")]
        hash_names = [name for name in names if name.endswith("/HASHES.sha256")]
        if len(manifest_names) != 1 or len(hash_names) != 1:
            raise RuntimeError("ZIP requires one MANIFEST.json and one HASHES.sha256")
        prefix = manifest_names[0][:-len("/MANIFEST.json")]
        if hash_names[0] != f"{prefix}/HASHES.sha256":
            raise RuntimeError("MANIFEST/HASHES roots differ")
        manifest = json.loads(archive.read(manifest_names[0]).decode("utf-8"))
        if manifest.get("schema") != PACKAGE_SCHEMA:
            raise RuntimeError("unsupported package manifest")
        if manifest.get("campaign_id") != expected_campaign_id:
            raise RuntimeError("package campaign_id mismatch")
        hash_text = archive.read(hash_names[0]).decode("utf-8")
        recorded: dict[str, str] = {}
        for line in hash_text.splitlines():
            if not line:
                continue
            digest, separator, relative = line.partition("  ")
            if not separator or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise RuntimeError(f"invalid HASHES line: {line!r}")
            if relative in recorded:
                raise RuntimeError(f"duplicate HASHES entry: {relative}")
            recorded[relative] = digest
        expected_hashed = {item["path"] for item in manifest.get("files", [])}
        expected_hashed.add("MANIFEST.json")
        if set(recorded) != expected_hashed:
            raise RuntimeError("HASHES entries differ from MANIFEST payload")
        for relative, digest in recorded.items():
            member = f"{prefix}/{relative}"
            if member not in names:
                raise RuntimeError(f"hashed member missing from ZIP: {member}")
            if hashlib.sha256(archive.read(member)).hexdigest() != digest:
                raise RuntimeError(f"ZIP member hash mismatch: {member}")
        expected_names = {f"{prefix}/{item}" for item in recorded}
        expected_names.add(f"{prefix}/HASHES.sha256")
        if set(names) != expected_names:
            extras = sorted(set(names) - expected_names)
            missing = sorted(expected_names - set(names))
            raise RuntimeError(f"ZIP inventory mismatch: extras={extras}, missing={missing}")
        if extract_to is not None:
            extract_to.mkdir(parents=True, exist_ok=False)
            archive.extractall(extract_to)

    loaded: dict[str, Any] = {}
    if extract_to is not None:
        extracted_root = extract_to / prefix
        for relative, digest in recorded.items():
            item = safe_relative(extracted_root, relative)
            if sha256(item) != digest:
                raise RuntimeError(f"extracted member hash mismatch: {relative}")
        if layout is None:
            raise RuntimeError("layout is required for extracted checkpoint loading")
        for condition, world in manifest["worlds"].items():
            checkpoint = safe_relative(extracted_root, world["end_checkpoint"])
            output = extract_to / f"loaded_checkpoint_{condition}.json"
            diagnostic = _diagnose_checkpoint(layout, condition, checkpoint, output)
            loaded[condition] = {
                "checkpoint": world["end_checkpoint"],
                "tick": diagnostic.get("tick"),
                "observer_passive": diagnostic.get("observer_passive"),
            }
            if int(diagnostic.get("tick", -1)) != int(world["end_tick"]):
                raise RuntimeError(f"loaded checkpoint tick mismatch for {condition}")
            if diagnostic.get("observer_passive") is not True:
                raise RuntimeError(f"checkpoint observer mutated state for {condition}")
    return {
        "path": str(archive_path),
        "bytes": archive_path.stat().st_size,
        "sha256": sha256(archive_path),
        "entries": len(names),
        "archive_root": prefix,
        "campaign_id": manifest["campaign_id"],
        "worlds": manifest["worlds"],
        "loaded_checkpoints": loaded,
    }


def _package_campaign_once(
    layout: Layout, state: dict[str, Any], validation: dict[str, Any],
) -> dict[str, Any]:
    existing = _valid_existing_package(layout)
    if existing is not None:
        return {"status": "ALREADY_FINAL_READY", **existing,
                "new_collect_stop_commands": 0}
    if layout.output.exists():
        raise RuntimeError(
            f"refusing to overwrite an invalid or foreign output: {layout.output}")
    if not validation.get("all_valid") or not state.get("sealed"):
        raise RuntimeError("packaging requires a sealed, terminal-valid campaign")

    attempt = {"started_utc": iso_utc(), "status": "RUNNING"}
    state.setdefault("package_attempts", []).append(attempt)
    state["phase"] = "PACKAGING"
    _state_event(state, "packaging_started",
                 attempt=len(state["package_attempts"]))
    _save_state(layout, state)
    sources = _package_sources(layout, state, validation)
    archive_root = _archive_root(layout)
    layout.output.parent.mkdir(parents=True, exist_ok=True)
    candidate = layout.output.with_name(f".{layout.output.name}.{uuid.uuid4().hex}.tmp")
    try:
        with tempfile.TemporaryDirectory(
                prefix="mbp2-stage-", dir=str(layout.supervisor)) as temporary_text:
            temporary = Path(temporary_text)
            staged_root = temporary / archive_root
            staged_root.mkdir()
            for relative, source in sorted(sources.items()):
                destination = staged_root / Path(relative)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            manifest = _manifest(layout, state, validation, archive_root,
                                 staged_root, sorted(sources))
            atomic_json(staged_root / "MANIFEST.json", manifest)
            hashes = {
                relative: sha256(staged_root / Path(relative))
                for relative in sorted(sources)
            }
            hashes["MANIFEST.json"] = sha256(staged_root / "MANIFEST.json")
            atomic_text(staged_root / "HASHES.sha256", "".join(
                f"{digest}  {relative}\n" for relative, digest in sorted(hashes.items())))

            with zipfile.ZipFile(candidate, "x", zipfile.ZIP_DEFLATED,
                                 compresslevel=9, allowZip64=True) as archive:
                for source in sorted(staged_root.rglob("*")):
                    if source.is_file():
                        archive.write(source, source.relative_to(temporary).as_posix())

            extraction = temporary / "extracted-verification"
            verified = verify_zip(
                candidate, expected_campaign_id=layout.campaign_id,
                extract_to=extraction, layout=layout)
            if layout.trial and not state.get("trial_packaging_failure_injected"):
                state["trial_packaging_failure_injected"] = True
                state["trial_packaging_failure_injected_utc"] = iso_utc()
                _state_event(state, "trial_packaging_failure_injected",
                             point="after_crc_extract_checkpoint_load_before_publish")
                _save_state(layout, state)
                raise RuntimeError(
                    "intentional trial packaging failure after immutable-cut verification")
            if layout.output.exists():
                raise RuntimeError(f"output appeared during packaging: {layout.output}")
            os.replace(candidate, layout.output)
        published = verify_zip(
            layout.output, expected_campaign_id=layout.campaign_id,
            extract_to=None, layout=None)
        attempt.update({"completed_utc": iso_utc(), "status": "OK",
                        "result": published,
                        "checkpoint_loads": verified["loaded_checkpoints"]})
        state["phase"] = "FINAL_READY"
        state["final_package"] = published
        _state_event(state, "final_package_published", output=str(layout.output),
                     sha256=published["sha256"])
        _save_state(layout, state)
        atomic_json(layout.campaign_root / "validation" / "PACKAGE_VALIDATION.json", {
            "schema": "mbp2.package-validation.v1",
            "created_utc": iso_utc(), "campaign_id": layout.campaign_id,
            "output": published, "checkpoint_loads": verified["loaded_checkpoints"],
            "package_attempts": state["package_attempts"],
            "terminal_validation": str(layout.terminal_validation_path),
        })
        return {"status": "FINAL_READY", **published,
                "loaded_checkpoints": verified["loaded_checkpoints"],
                "new_collect_stop_commands": 0}
    except Exception as error:
        candidate.unlink(missing_ok=True)
        attempt.update({"completed_utc": iso_utc(), "status": "FAILED",
                        "error": str(error), "traceback": traceback.format_exc()})
        state["phase"] = "PACKAGE_FAILED"
        _state_event(state, "packaging_failed", error=str(error))
        _save_state(layout, state)
        raise


def package_campaign(
    layout: Layout, state: dict[str, Any], validation: dict[str, Any],
    *, max_attempts: int = 3,
) -> dict[str, Any]:
    """Publish atomically, retrying packaging only on the same frozen cuts."""
    if max_attempts < 1:
        raise ValueError("max_attempts must be positive")
    failures: list[str] = []
    for local_attempt in range(1, max_attempts + 1):
        try:
            result = _package_campaign_once(layout, state, validation)
            result["packaging_attempts_this_run"] = local_attempt
            result["packaging_failures_this_run"] = failures
            return result
        except Exception as error:
            failures.append(f"{type(error).__name__}: {error}")
            existing = _valid_existing_package(layout)
            if existing is not None:
                return {"status": "ALREADY_FINAL_READY", **existing,
                        "new_collect_stop_commands": 0,
                        "packaging_attempts_this_run": local_attempt,
                        "packaging_failures_this_run": failures}
            if local_attempt >= max_attempts:
                raise RuntimeError(
                    f"packaging failed after {max_attempts} attempts on the same cuts: "
                    f"{failures}") from error
            _state_event(state, "packaging_retry_scheduled",
                         failed_local_attempt=local_attempt,
                         next_local_attempt=local_attempt + 1,
                         error=str(error))
            _save_state(layout, state)
            time.sleep(min(0.25 * local_attempt, 0.5))
    raise AssertionError("unreachable packaging retry loop")


def _issue_midpoint(
    layout: Layout, state: dict[str, Any], *, command_timeout: float,
) -> dict[str, Any]:
    midpoint = state.setdefault("midpoint", {})
    if midpoint.get("attempted"):
        return midpoint
    midpoint.update({"attempted": True, "submitted_utc": iso_utc(),
                     "responses": {}, "errors": {}})
    _state_event(state, "midpoint_save_submitted")
    _save_state(layout, state)
    reason = safe_token(f"campaign_midpoint_{layout.campaign_id}")
    responses, errors = _parallel(lambda c: _world_command(
        layout, c, "save", {"reason": reason}, timeout=command_timeout))
    midpoint["responses"] = responses
    midpoint["errors"] = errors
    midpoint["completed_utc"] = iso_utc()
    midpoint["ok"] = not errors and all(item.get("ok") for item in responses.values())
    _state_event(state, "midpoint_save_completed", ok=midpoint["ok"],
                 errors=errors)
    _save_state(layout, state)
    return midpoint


def _ensure_workers_for_final(
    layout: Layout, state: dict[str, Any], *, command_timeout: float,
) -> None:
    for condition in WORLD_SPECS:
        request_id = state["final_request_ids"][condition]
        if _descriptor_for(layout.worlds[condition], request_id) is not None:
            continue
        status = _world_status(layout, condition)
        if not status or not process_is_alive(status.get("pid")):
            _launch_worker(layout, state, condition)
            _wait_worker_ready(layout, condition)


def _submit_final_collects(
    layout: Layout, state: dict[str, Any], *, command_timeout: float,
) -> tuple[dict[str, Any], dict[str, str]]:
    missing: list[str] = []
    for condition in WORLD_SPECS:
        request_id = state["final_request_ids"][condition]
        descriptor = _descriptor_for(layout.worlds[condition], request_id)
        if descriptor is not None:
            state["worlds"][condition]["descriptor"] = str(
                descriptor.relative_to(layout.worlds[condition]))
            continue
        if state["worlds"][condition].get("final_command_submitted_utc"):
            raise RuntimeError(
                f"final command for {condition} was already submitted but its "
                "descriptor is absent; simulation commands are never retried")
        missing.append(condition)
    if not missing:
        _save_state(layout, state)
        return {}, {}

    _ensure_workers_for_final(layout, state, command_timeout=command_timeout)
    submitted = iso_utc()
    for condition in missing:
        state["worlds"][condition]["final_command_submitted_utc"] = submitted
    _state_event(state, "final_collect_stop_submitted", conditions=missing,
                 request_ids={c: state["final_request_ids"][c] for c in missing})
    _save_state(layout, state)
    responses, errors = _parallel(lambda c: _world_command(
        layout, c, "collect_stop",
        {"request_id": state["final_request_ids"][c]},
        timeout=command_timeout), missing)
    for condition in missing:
        state["worlds"][condition]["final_response"] = responses.get(condition)
        if condition in errors:
            state["worlds"][condition]["final_response_error"] = errors[condition]
    _state_event(state, "final_collect_stop_commands_returned",
                 response_conditions=sorted(responses), errors=errors)
    _save_state(layout, state)
    # A CLI timeout can occur after the worker has committed the descriptor.
    # Therefore errors are recorded but terminal evidence, not the transient
    # command return channel, decides whether finalization succeeded.
    return responses, errors


def _wait_for_terminal_evidence(
    layout: Layout,
    state: dict[str, Any],
    *,
    timeout: float,
    poll_seconds: float,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    last: dict[str, Any] | None = None
    while True:
        last = _terminal_validations(layout, state)
        if last["all_valid"]:
            for condition, item in last["worlds"].items():
                state["worlds"][condition]["descriptor"] = item["descriptor"]
            return last
        if time.monotonic() >= deadline:
            errors = {key: value["errors"] for key, value in last["worlds"].items()}
            raise TimeoutError(f"terminal validation timed out: {errors}")
        time.sleep(min(max(poll_seconds, 0.1),
                       max(0.0, deadline - time.monotonic())))


def _seal_and_package(
    layout: Layout,
    state: dict[str, Any],
    validation: dict[str, Any],
) -> dict[str, Any]:
    if not validation.get("all_valid"):
        raise RuntimeError("cannot seal invalid terminal evidence")
    atomic_json(layout.terminal_validation_path, validation)
    state["sealed"] = True
    state["sealed_utc"] = iso_utc()
    state["phase"] = "TERMINAL_VALIDATED"
    _state_event(state, "terminal_evidence_validated")
    _save_state(layout, state)
    analysis = build_analysis(layout, state, validation)
    state["analysis"] = str(layout.analysis_path)
    state["analysis_summary"] = {
        "selected_cut_count": analysis.get("selected_cut_count"),
        "common_ticks": analysis.get("common_age_comparison", {}).get(
            "exact_common_ticks"),
        "queries": sorted({
            query_name
            for cut in analysis.get("selected_cuts", [])
            for query_name in cut.get("queries", {})
        }),
    }
    state["phase"] = "ANALYZED"
    _state_event(state, "analysis_completed", path=str(layout.analysis_path))
    _save_state(layout, state)
    return package_campaign(layout, state, validation)


def finalize(
    layout: Layout,
    state: dict[str, Any],
    *,
    command_timeout: float,
    terminal_timeout: float,
    poll_seconds: float,
) -> dict[str, Any]:
    existing = _valid_existing_package(layout)
    if existing is not None:
        if state.get("phase") != "FINAL_READY":
            state["phase"] = "FINAL_READY"
            state["sealed"] = True
            state["final_package"] = existing
            _state_event(state, "existing_final_package_recognized")
            _save_state(layout, state)
        return {"status": "ALREADY_FINAL_READY", **existing,
                "new_collect_stop_commands": 0}

    if state.get("sealed") or state.get("phase") in SEALED_PHASES:
        validation = _terminal_validations(layout, state)
        if not validation["all_valid"]:
            raise RuntimeError(
                "sealed campaign lost terminal evidence: " +
                repr({c: item["errors"] for c, item in validation["worlds"].items()}))
        if not layout.terminal_validation_path.exists():
            atomic_json(layout.terminal_validation_path, validation)
        if not layout.analysis_path.exists():
            raise RuntimeError(
                "sealed campaign has no analysis; repackage retries packaging only")
        state["sealed"] = True
        return package_campaign(layout, state, validation)

    state["phase"] = "STOPPING"
    state["stop_started_utc"] = state.get("stop_started_utc") or iso_utc()
    _state_event(state, "terminal_stop_started")
    _save_state(layout, state)
    _submit_final_collects(layout, state, command_timeout=command_timeout)
    validation = _wait_for_terminal_evidence(
        layout, state, timeout=terminal_timeout, poll_seconds=poll_seconds)
    return _seal_and_package(layout, state, validation)


def _begin_running(
    layout: Layout,
    state: dict[str, Any],
    *,
    deadline_utc: str | None,
    command_timeout: float,
) -> None:
    if state.get("phase") != "PREPARED":
        return
    # Workers first acquire their independent writer locks and remain PAUSED.
    # Only after all three report readiness is the shared wall-clock epoch fixed.
    readiness = _start_worlds(
        layout, state, command_timeout=command_timeout, release=False)
    started = utc_now()
    deadline = (parse_utc(deadline_utc) if deadline_utc else
                started + dtm.timedelta(seconds=float(state["duration_seconds"])))
    if deadline <= started:
        raise ValueError("common deadline must be later than campaign start")
    midpoint = started + (deadline - started) / 2
    state["started_utc"] = iso_utc(started)
    state["started_local"] = iso_local(started)
    state["deadline_utc"] = iso_utc(deadline)
    state["deadline_local"] = iso_local(deadline)
    state["midpoint_utc"] = iso_utc(midpoint)
    state["midpoint_local"] = iso_local(midpoint)
    state["phase"] = "STARTING"
    _state_event(state, "common_schedule_fixed",
                 midpoint_utc=state["midpoint_utc"],
                 deadline_utc=state["deadline_utc"])
    _save_state(layout, state)

    def release(condition: str) -> dict[str, Any]:
        submitted = utc_now()
        response = _world_command(
            layout, condition, "release_autonomy", {}, timeout=command_timeout)
        completed = utc_now()
        return {
            "submitted_utc": iso_utc(submitted),
            "submitted_local": iso_local(submitted),
            "completed_utc": iso_utc(completed),
            "tick_before": response.get("tick_before"),
            "tick_after": response.get("tick_after"),
            "response": response,
        }

    releases, errors = _parallel(release)
    bad = {condition: item for condition, item in releases.items()
           if not item.get("response", {}).get("ok")}
    if errors or bad:
        state["phase"] = "START_FAILED"
        state["release_errors"] = errors
        state["release_bad_responses"] = bad
        _state_event(state, "autonomy_release_failed", errors=errors)
        _save_state(layout, state)
        raise RuntimeError(f"autonomy release failed: errors={errors}, responses={bad}")
    submitted_times = [parse_utc(item["submitted_utc"]) for item in releases.values()]
    release_skew = ((max(submitted_times) - min(submitted_times)).total_seconds()
                    if submitted_times else 0.0)
    state["release"] = {
        "worlds": releases,
        "submission_skew_seconds": release_skew,
        "ready_ticks": {
            condition: item.get("tick")
            for condition, item in readiness["ready"].items()
        },
    }
    _state_event(state, "autonomy_released", release_skew_seconds=release_skew,
                 release_ticks={c: item.get("tick_after")
                                for c, item in releases.items()})
    state["phase"] = "RUNNING"
    _state_event(state, "campaign_running")
    _save_state(layout, state)


def _health_snapshot(layout: Layout) -> tuple[dict[str, Any], dict[str, str]]:
    return _parallel(lambda c: _world_status(layout, c))


def supervise(
    layout: Layout,
    *,
    deadline_utc: str | None,
    poll_seconds: float,
    command_timeout: float,
    terminal_timeout: float,
) -> dict[str, Any]:
    if poll_seconds <= 0:
        raise ValueError("poll interval must be positive")
    state = _load_state(layout)
    existing = _valid_existing_package(layout)
    if existing is not None:
        return {"status": "ALREADY_FINAL_READY", **existing,
                "new_collect_stop_commands": 0}
    if state.get("sealed") or state.get("phase") in SEALED_PHASES:
        return finalize(layout, state, command_timeout=command_timeout,
                        terminal_timeout=terminal_timeout,
                        poll_seconds=poll_seconds)
    if state.get("phase") == "STOPPING":
        # A resumed supervisor may wait for already-submitted commands, but it
        # does not submit them again.
        validation = _wait_for_terminal_evidence(
            layout, state, timeout=terminal_timeout, poll_seconds=poll_seconds)
        return _seal_and_package(layout, state, validation)
    if state.get("phase") == "STARTING":
        raise RuntimeError(
            "campaign was interrupted while starting; inspect status and use stop")
    if state.get("phase") != "RUNNING":
        _begin_running(layout, state, deadline_utc=deadline_utc,
                       command_timeout=command_timeout)

    midpoint = parse_utc(state["midpoint_utc"])
    deadline = parse_utc(state["deadline_utc"])
    last_health_write = 0.0
    while True:
        now = utc_now()
        if now >= deadline:
            break
        if now >= midpoint and not state.get("midpoint", {}).get("attempted"):
            _issue_midpoint(layout, state, command_timeout=command_timeout)
        statuses, errors = _health_snapshot(layout)
        if errors:
            raise RuntimeError(f"world status checks failed: {errors}")
        unhealthy = {
            condition: status for condition, status in statuses.items()
            if not status or status.get("state") not in {"RUNNING", "PAUSED"} or
            not process_is_alive(status.get("pid"))
        }
        if unhealthy:
            raise RuntimeError(f"world stopped before common deadline: {unhealthy}")
        if time.monotonic() - last_health_write >= 60.0:
            state["last_health_utc"] = iso_utc(now)
            state["last_status"] = statuses
            _save_state(layout, state)
            last_health_write = time.monotonic()
        next_boundary = deadline
        if not state.get("midpoint", {}).get("attempted"):
            next_boundary = min(next_boundary, midpoint)
        wait = min(poll_seconds, max(0.05, (next_boundary - utc_now()).total_seconds()))
        time.sleep(wait)
    state["deadline_reached_utc"] = iso_utc()
    _state_event(state, "common_deadline_reached")
    _save_state(layout, state)
    return finalize(layout, state, command_timeout=command_timeout,
                    terminal_timeout=terminal_timeout,
                    poll_seconds=poll_seconds)


def stop(
    layout: Layout,
    *,
    poll_seconds: float,
    command_timeout: float,
    terminal_timeout: float,
) -> dict[str, Any]:
    state = _load_state(layout)
    existing = _valid_existing_package(layout)
    if existing is not None:
        return {"status": "ALREADY_FINAL_READY", **existing,
                "new_collect_stop_commands": 0}
    if state.get("phase") == "PREPARED":
        # A deliberate stop before supervise produces a valid tick-zero cut.
        _start_worlds(layout, state, command_timeout=command_timeout, release=False)
    if state.get("phase") == "STOPPING":
        validation = _wait_for_terminal_evidence(
            layout, state, timeout=terminal_timeout, poll_seconds=poll_seconds)
        return _seal_and_package(layout, state, validation)
    return finalize(layout, state, command_timeout=command_timeout,
                    terminal_timeout=terminal_timeout,
                    poll_seconds=poll_seconds)


def repackage(layout: Layout) -> dict[str, Any]:
    """Retry only immutable analysis/package publication; never command worlds."""
    state = _load_state(layout)
    existing = _valid_existing_package(layout)
    if existing is not None:
        return {"status": "ALREADY_FINAL_READY", **existing,
                "new_collect_stop_commands": 0}
    validation = _terminal_validations(layout, state)
    if not validation["all_valid"]:
        raise RuntimeError(
            "repackage requires three existing terminal cuts: " +
            repr({c: item["errors"] for c, item in validation["worlds"].items()}))
    if not state.get("sealed"):
        state["sealed"] = True
        state["sealed_utc"] = iso_utc()
        state["phase"] = "TERMINAL_VALIDATED"
        atomic_json(layout.terminal_validation_path, validation)
        _state_event(state, "terminal_evidence_recovered_for_repackage")
        _save_state(layout, state)
    if not layout.analysis_path.is_file():
        raise RuntimeError("repackage does not retry missing analysis")
    return package_campaign(layout, state, validation)


def campaign_status(layout: Layout) -> dict[str, Any]:
    state: dict[str, Any] | None = None
    state_error: str | None = None
    try:
        state = _load_state(layout)
    except Exception as error:
        state_error = str(error)
    worlds: dict[str, Any] = {}
    for condition, root in layout.worlds.items():
        try:
            status = _world_status(layout, condition)
            pid = status.get("pid") if status else _pid_from_file(
                root / "world" / "worker.pid")
            lock_free, lock_detail = writer_lock_available(root / "world" / "writer.lock")
            request_id = (state or {}).get("final_request_ids", {}).get(
                condition, final_request_id(layout.campaign_id, condition))
            descriptor = _descriptor_for(root, request_id)
            worlds[condition] = {
                "root": str(root), "status": status, "pid": pid,
                "pid_alive": process_is_alive(pid),
                "writer_lock_available": lock_free,
                "writer_lock_detail": lock_detail,
                "final_descriptor": (str(descriptor) if descriptor else None),
            }
        except Exception as error:
            worlds[condition] = {"root": str(root), "error": str(error)}
    package = _valid_existing_package(layout)
    now = utc_now()
    remaining = None
    if state and state.get("deadline_utc"):
        remaining = max(0.0, (parse_utc(state["deadline_utc"]) - now).total_seconds())
    return {
        "schema": "mbp2.campaign-status.v1",
        "now_utc": iso_utc(now),
        "campaign_id": layout.campaign_id,
        "phase": state.get("phase") if state else "NOT_PREPARED",
        "sealed": bool(state and state.get("sealed")),
        "state_error": state_error,
        "deadline_utc": state.get("deadline_utc") if state else None,
        "seconds_remaining": remaining,
        "worlds": worlds,
        "output": str(layout.output),
        "package": package,
        "result": "ALREADY_FINAL_READY" if package else None,
    }


def _add_layout_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--trial", action="store_true",
        help="use test_campaign, a 60 s duration and a trial ZIP by default")
    parser.add_argument("--campaign-root", type=Path)
    parser.add_argument("--campaign-id")
    parser.add_argument("--duration-seconds", "--duration", type=float)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--python", type=Path, default=DEFAULT_PYTHON)
    parser.add_argument("--world-a-root", "--world-a", type=Path)
    parser.add_argument("--world-b-root", "--world-b", type=Path)
    parser.add_argument("--world-c-root", "--world-c", type=Path)


def _add_runtime_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--poll-seconds", type=float, default=1.0)
    parser.add_argument("--command-timeout", type=float, default=300.0)
    parser.add_argument("--terminal-timeout", type=float, default=900.0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare, supervise and atomically finalize MBP2 A/B/C")
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare_parser = subparsers.add_parser(
        "prepare", help="initialize A/B/C without starting workers")
    _add_layout_arguments(prepare_parser)
    supervise_parser = subparsers.add_parser(
        "supervise", help="run to the shared deadline and finalize")
    _add_layout_arguments(supervise_parser)
    _add_runtime_arguments(supervise_parser)
    supervise_parser.add_argument(
        "--deadline-utc",
        help="explicit common ISO-8601 deadline; otherwise start + duration")
    status_parser = subparsers.add_parser(
        "status", help="read campaign, process, lock and package state")
    _add_layout_arguments(status_parser)
    stop_parser = subparsers.add_parser(
        "stop", help="collect_stop every unsealed world and finalize")
    _add_layout_arguments(stop_parser)
    _add_runtime_arguments(stop_parser)
    repackage_parser = subparsers.add_parser(
        "repackage", help="retry immutable packaging only")
    _add_layout_arguments(repackage_parser)
    return parser


def cli(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    layout = layout_from_args(args)
    if args.command == "prepare":
        result = prepare(layout)
    elif args.command == "supervise":
        result = supervise(
            layout, deadline_utc=args.deadline_utc,
            poll_seconds=args.poll_seconds,
            command_timeout=args.command_timeout,
            terminal_timeout=args.terminal_timeout)
    elif args.command == "status":
        result = campaign_status(layout)
    elif args.command == "stop":
        result = stop(
            layout, poll_seconds=args.poll_seconds,
            command_timeout=args.command_timeout,
            terminal_timeout=args.terminal_timeout)
    elif args.command == "repackage":
        result = repackage(layout)
    else:
        raise AssertionError(args.command)
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(cli())
    except KeyboardInterrupt:
        print(json.dumps({
            "status": "INTERRUPTED",
            "detail": "workers were left untouched; use status or stop",
        }, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(130)
    except Exception as error:
        print(json.dumps({
            "status": "ERROR", "error": str(error),
            "type": type(error).__name__,
        }, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
