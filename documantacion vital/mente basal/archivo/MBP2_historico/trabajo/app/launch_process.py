from __future__ import annotations

"""Start an independent Python child on Windows.

The launcher is deliberately generic: it knows nothing about MBP2 and only
turns ``python + script + arguments`` into a detached process.  When requested,
it publishes an atomic JSON handshake after ``Popen`` succeeds.  The handshake
is useful to a supervisor because it records the child PID without relying on
shell parsing or a transient console window.

This module does not launch anything when imported.
"""

import argparse
import datetime as dtm
import json
import os
import subprocess
import sys
import time
import traceback
import uuid
from pathlib import Path
from typing import Any, BinaryIO, Sequence


SCHEMA = "mbp2.independent-process-handshake.v1"
CREATE_NEW_PROCESS_GROUP = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
DETACHED_PROCESS = getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
CREATE_BREAKAWAY_FROM_JOB = getattr(subprocess, "CREATE_BREAKAWAY_FROM_JOB", 0x01000000)


def utc_now() -> str:
    return dtm.datetime.now(dtm.timezone.utc).isoformat(timespec="milliseconds")


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    """Publish JSON without exposing a partially-written handshake."""
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def parse_environment(items: Sequence[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"environment override must be NAME=VALUE: {item!r}")
        name, value = item.split("=", 1)
        if not name or "\x00" in name or "=" in name or "\x00" in value:
            raise ValueError(f"invalid environment override: {item!r}")
        result[name] = value
    return result


def _open_log(path: Path | None) -> tuple[int | BinaryIO, Path | None]:
    if path is None:
        return subprocess.DEVNULL, None
    resolved = path.resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved.open("ab", buffering=0), resolved


def launch(
    *,
    python: Path,
    script: Path,
    script_args: Sequence[str],
    cwd: Path | None = None,
    stdout_path: Path | None = None,
    stderr_path: Path | None = None,
    handshake_path: Path | None = None,
    environment: dict[str, str] | None = None,
    startup_probe_seconds: float = 0.25,
    allow_job_inheritance: bool = False,
) -> dict[str, Any]:
    """Launch one detached child and optionally publish its PID.

    ``CREATE_BREAKAWAY_FROM_JOB`` is essential when the launcher itself lives in
    a Windows job configured with kill-on-close.  Falling back to job
    inheritance is therefore opt-in and is recorded in the handshake.
    """
    if os.name != "nt":
        raise RuntimeError("launch_process.py requires Windows")
    if startup_probe_seconds < 0:
        raise ValueError("startup probe must be nonnegative")
    python = python.resolve()
    script = script.resolve()
    workdir = (cwd or script.parent).resolve()
    if not python.is_file():
        raise FileNotFoundError(python)
    if not script.is_file():
        raise FileNotFoundError(script)
    if not workdir.is_dir():
        raise NotADirectoryError(workdir)

    command = [str(python), str(script), *[str(item) for item in script_args]]
    child_environment = os.environ.copy()
    child_environment.update(environment or {})
    stdout_target, stdout_resolved = _open_log(stdout_path)
    stderr_target, stderr_resolved = _open_log(stderr_path)
    opened = [item for item in (stdout_target, stderr_target) if hasattr(item, "close")]
    flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_BREAKAWAY_FROM_JOB
    inherited_job = False
    started = time.monotonic()
    try:
        try:
            child = subprocess.Popen(
                command,
                cwd=str(workdir),
                env=child_environment,
                stdin=subprocess.DEVNULL,
                stdout=stdout_target,
                stderr=stderr_target,
                close_fds=True,
                creationflags=flags,
            )
        except OSError as error:
            if not (allow_job_inheritance and getattr(error, "winerror", None) == 5):
                raise
            inherited_job = True
            flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
            child = subprocess.Popen(
                command,
                cwd=str(workdir),
                env=child_environment,
                stdin=subprocess.DEVNULL,
                stdout=stdout_target,
                stderr=stderr_target,
                close_fds=True,
                creationflags=flags,
            )
    except Exception as error:
        failure = {
            "schema": SCHEMA,
            "status": "ERROR",
            "created_utc": utc_now(),
            "launcher_pid": os.getpid(),
            "command": command,
            "cwd": str(workdir),
            "error": str(error),
            "traceback": traceback.format_exc(),
        }
        if handshake_path is not None:
            atomic_json(handshake_path, failure)
        raise
    finally:
        for stream in opened:
            stream.close()

    if startup_probe_seconds:
        deadline = time.monotonic() + startup_probe_seconds
        while child.poll() is None and time.monotonic() < deadline:
            time.sleep(min(0.025, max(0.0, deadline - time.monotonic())))
    return_code = child.poll()
    result = {
        "schema": SCHEMA,
        "status": "STARTED" if return_code is None else "EXITED_EARLY",
        "created_utc": utc_now(),
        "launcher_pid": os.getpid(),
        "child_pid": child.pid,
        "child_returncode": return_code,
        "python": str(python),
        "script": str(script),
        "arguments": [str(item) for item in script_args],
        "command": command,
        "cwd": str(workdir),
        "stdout": str(stdout_resolved) if stdout_resolved else None,
        "stderr": str(stderr_resolved) if stderr_resolved else None,
        "creation_flags": flags,
        "breakaway_requested": True,
        "inherited_parent_job": inherited_job,
        "probe_seconds": startup_probe_seconds,
        "launch_elapsed_seconds": time.monotonic() - started,
    }
    if handshake_path is not None:
        atomic_json(handshake_path, result)
    if return_code is not None:
        raise RuntimeError(f"child {child.pid} exited during startup with code {return_code}")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Launch an independent Python script on Windows")
    parser.add_argument("--python", type=Path, default=Path(sys.executable))
    parser.add_argument("--script", type=Path, required=True)
    parser.add_argument("--cwd", type=Path)
    parser.add_argument("--stdout", type=Path)
    parser.add_argument("--stderr", type=Path)
    parser.add_argument("--handshake", type=Path)
    parser.add_argument("--env", action="append", default=[], metavar="NAME=VALUE")
    parser.add_argument("--startup-probe-seconds", type=float, default=0.25)
    parser.add_argument(
        "--allow-job-inheritance",
        action="store_true",
        help="allow a non-independent fallback if Windows denies job breakaway",
    )
    parser.add_argument("script_args", nargs=argparse.REMAINDER)
    return parser


def cli(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    script_args = list(args.script_args)
    if script_args[:1] == ["--"]:
        script_args = script_args[1:]
    result = launch(
        python=args.python,
        script=args.script,
        script_args=script_args,
        cwd=args.cwd,
        stdout_path=args.stdout,
        stderr_path=args.stderr,
        handshake_path=args.handshake,
        environment=parse_environment(args.env),
        startup_probe_seconds=args.startup_probe_seconds,
        allow_job_inheritance=args.allow_job_inheritance,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(cli())
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
