#!/usr/bin/env python3
"""Reproducible command harness for DEE thinking 3.0 validation.

The harness deliberately knows nothing about DEE's physics.  It executes a
declared list of external validation commands, captures their complete output,
and writes machine-readable evidence under ``validation/`` (or ``--output``).

Commands may be supplied in either of two ways:

* ``--spec commands.json`` where the root is a list, or an object containing a
  ``commands`` list; or
* repeatable ``--command NAME=COMMAND`` arguments.  The latter can be grouped
  with ``--command-kind NAME=wheel_smoke`` and assigned a specific directory
  with ``--command-cwd NAME=PATH``.

The generic ``kind`` field is intended for the delivery's wheel smoke,
unittest, cross-language, C++ consumer, and benchmark checks.  It is metadata
only; no result is inferred from the name of a command.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = 1
KNOWN_KINDS = {
    "wheel_smoke",
    "unittest",
    "cross_language",
    "consumer",
    "benchmark",
    "other",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_directory(path: Path) -> tuple[str, int, int]:
    """Hash a directory deterministically, including relative names.

    This is a provenance digest, not an archive format.  Symlinks are recorded
    by their link text and never followed.
    """

    digest = hashlib.sha256()
    count = 0
    total_size = 0
    for item in sorted(path.rglob("*"), key=lambda p: p.relative_to(path).as_posix()):
        relative = item.relative_to(path).as_posix()
        if item.is_symlink():
            payload = os.readlink(item)
            digest.update(f"L\0{relative}\0{payload}\n".encode("utf-8"))
            count += 1
        elif item.is_file():
            file_hash = sha256_file(item)
            size = item.stat().st_size
            digest.update(f"F\0{relative}\0{size}\0{file_hash}\n".encode("utf-8"))
            count += 1
            total_size += size
    return digest.hexdigest(), count, total_size


def describe_path(path_value: str | os.PathLike[str]) -> dict[str, Any]:
    path = Path(path_value).expanduser().resolve(strict=False)
    result: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
    }
    if not path.exists():
        return result
    stat = path.stat()
    result["modified_utc"] = datetime.fromtimestamp(
        stat.st_mtime, timezone.utc
    ).isoformat(timespec="seconds").replace("+00:00", "Z")
    if path.is_file():
        result.update(
            {
                "type": "file",
                "size_bytes": stat.st_size,
                "sha256": sha256_file(path),
            }
        )
    elif path.is_dir():
        digest, file_count, size = sha256_directory(path)
        result.update(
            {
                "type": "directory",
                "tree_sha256": digest,
                "file_count": file_count,
                "size_bytes": size,
            }
        )
    else:
        result["type"] = "other"
    return result


def split_assignment(value: str, option: str) -> tuple[str, str]:
    if "=" not in value:
        raise ValueError(f"{option} expects NAME=VALUE, received: {value!r}")
    name, payload = value.split("=", 1)
    name = name.strip()
    if not name or not payload:
        raise ValueError(f"{option} expects non-empty NAME=VALUE")
    return name, payload


def safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    return cleaned or "command"


@dataclass(frozen=True)
class Command:
    name: str
    command: str | list[str]
    cwd: Path
    kind: str = "other"
    timeout_seconds: float | None = None
    required: bool = True
    env: Mapping[str, str] | None = None

    @staticmethod
    def from_mapping(
        raw: Mapping[str, Any], default_cwd: Path, source: str
    ) -> "Command":
        name = str(raw.get("name", "")).strip()
        if not name:
            raise ValueError(f"{source}: command is missing a non-empty 'name'")
        invocation = raw.get("command")
        if not isinstance(invocation, (str, list)) or not invocation:
            raise ValueError(f"{source}/{name}: 'command' must be a string or list")
        if isinstance(invocation, list):
            invocation = [str(part) for part in invocation]
            if any(not part for part in invocation):
                raise ValueError(f"{source}/{name}: command arguments cannot be empty")
        kind = str(raw.get("kind", "other"))
        if kind not in KNOWN_KINDS:
            raise ValueError(
                f"{source}/{name}: unknown kind {kind!r}; expected one of "
                + ", ".join(sorted(KNOWN_KINDS))
            )
        cwd_raw = raw.get("cwd")
        cwd = Path(cwd_raw).expanduser() if cwd_raw else default_cwd
        cwd = cwd.resolve(strict=False)
        timeout_raw = raw.get("timeout_seconds")
        timeout = None if timeout_raw in (None, 0) else float(timeout_raw)
        if timeout is not None and timeout <= 0:
            raise ValueError(f"{source}/{name}: timeout_seconds must be positive")
        env_raw = raw.get("env")
        if env_raw is not None and not isinstance(env_raw, Mapping):
            raise ValueError(f"{source}/{name}: env must be an object")
        env = None if env_raw is None else {str(k): str(v) for k, v in env_raw.items()}
        return Command(
            name=name,
            command=invocation,
            cwd=cwd,
            kind=kind,
            timeout_seconds=timeout,
            required=bool(raw.get("required", True)),
            env=env,
        )


def load_spec(path: Path, default_cwd: Path) -> list[Command]:
    data = json.loads(path.read_text(encoding="utf-8"))
    raw_commands = data.get("commands") if isinstance(data, Mapping) else data
    if not isinstance(raw_commands, list):
        raise ValueError(f"{path}: expected a list or an object with a commands list")
    return [
        Command.from_mapping(item, default_cwd, str(path))
        for item in raw_commands
        if isinstance(item, Mapping)
    ]


def cli_commands(args: argparse.Namespace, default_cwd: Path) -> list[Command]:
    cwd_by_name = dict(split_assignment(v, "--command-cwd") for v in args.command_cwd)
    kind_by_name = dict(split_assignment(v, "--command-kind") for v in args.command_kind)
    commands: list[Command] = []
    for declared in args.command:
        name, invocation = split_assignment(declared, "--command")
        raw = {
            "name": name,
            "command": invocation,
            "cwd": cwd_by_name.get(name, str(default_cwd)),
            "kind": kind_by_name.get(name, "other"),
            "timeout_seconds": args.default_timeout,
        }
        commands.append(Command.from_mapping(raw, default_cwd, "command line"))
    unknown_cwd = sorted(set(cwd_by_name).difference(c.name for c in commands))
    unknown_kind = sorted(set(kind_by_name).difference(c.name for c in commands))
    if unknown_cwd or unknown_kind:
        unknown = ", ".join(unknown_cwd + unknown_kind)
        raise ValueError(f"command metadata refers to undeclared command(s): {unknown}")
    return commands


def display_command(command: str | Sequence[str]) -> str:
    if isinstance(command, str):
        return command
    return subprocess.list2cmdline(list(command)) if os.name == "nt" else shlex.join(command)


def run_one(command: Command, logs: Path, ordinal: int) -> dict[str, Any]:
    basename = f"{ordinal:02d}_{safe_name(command.name)}"
    stdout_path = logs / f"{basename}.stdout.log"
    stderr_path = logs / f"{basename}.stderr.log"
    meta_path = logs / f"{basename}.meta.json"
    start_utc = utc_now()
    started = time.perf_counter()
    exit_code: int | None = None
    timed_out = False
    launch_error: str | None = None
    stdout = ""
    stderr = ""

    environment = os.environ.copy()
    if command.env:
        environment.update(command.env)

    try:
        if not command.cwd.is_dir():
            raise FileNotFoundError(f"working directory does not exist: {command.cwd}")
        completed = subprocess.run(
            command.command,
            cwd=command.cwd,
            env=environment,
            shell=isinstance(command.command, str),
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=command.timeout_seconds,
            check=False,
        )
        exit_code = completed.returncode
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = (exc.stdout or b"").decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = (exc.stderr or b"").decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        stderr += f"\nVALIDATION_HARNESS_TIMEOUT: {command.timeout_seconds} seconds\n"
    except Exception as exc:  # capture infrastructure failures as evidence
        launch_error = f"{type(exc).__name__}: {exc}"
        stderr = launch_error + "\n"

    duration = time.perf_counter() - started
    end_utc = utc_now()
    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    status = "passed" if exit_code == 0 and not timed_out and launch_error is None else "failed"
    result: dict[str, Any] = {
        "name": command.name,
        "kind": command.kind,
        "required": command.required,
        "command": display_command(command.command),
        "command_argv": command.command if isinstance(command.command, list) else None,
        "cwd": str(command.cwd),
        "start_utc": start_utc,
        "end_utc": end_utc,
        "duration_seconds": round(duration, 6),
        "exit_code": exit_code,
        "timed_out": timed_out,
        "launch_error": launch_error,
        "status": status,
        "stdout": stdout,
        "stderr": stderr,
        "stdout_log": stdout_path.relative_to(logs.parent).as_posix(),
        "stderr_log": stderr_path.relative_to(logs.parent).as_posix(),
    }
    atomic_json(meta_path, result)
    return result


def tool_version(path: Path, name: str) -> dict[str, Any]:
    lower = name.lower()
    if lower in {"cl", "cl.exe", "msvc"} or path.name.lower() == "cl.exe":
        arguments = [str(path), "/?"]
    else:
        arguments = [str(path), "--version"]
    try:
        completed = subprocess.run(
            arguments,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15,
            check=False,
        )
        combined = (completed.stdout + "\n" + completed.stderr).strip()
        return {
            "command": display_command(arguments),
            "exit_code": completed.returncode,
            "output": combined[:16000],
        }
    except Exception as exc:
        return {
            "command": display_command(arguments),
            "exit_code": None,
            "error": f"{type(exc).__name__}: {exc}",
        }


def make_provenance(args: argparse.Namespace, output: Path) -> dict[str, Any]:
    inputs = dict(split_assignment(v, "--input") for v in args.input)
    tools = dict(split_assignment(v, "--toolchain") for v in args.toolchain)
    if args.kernel:
        inputs.setdefault("kernel", args.kernel)
    if args.wheel:
        inputs.setdefault("wheel", args.wheel)

    described_tools: dict[str, Any] = {}
    for name, raw_path in sorted(tools.items()):
        path = Path(raw_path).expanduser().resolve(strict=False)
        description = describe_path(path)
        if path.is_file():
            description["version_probe"] = tool_version(path, name)
        described_tools[name] = description

    provenance = {
        "schema_version": SCHEMA_VERSION,
        "generated_utc": utc_now(),
        "generator": str(Path(__file__).resolve()),
        "host": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
            "python_executable": sys.executable,
        },
        "inputs": {name: describe_path(path) for name, path in sorted(inputs.items())},
        "toolchain": described_tools,
    }
    atomic_json(output / "PROVENANCE.json", provenance)
    return provenance


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Run declared DEE thinking 3.0 validation commands and capture evidence."
    )
    result.add_argument(
        "--spec",
        action="append",
        default=[],
        metavar="JSON",
        help="JSON command specification (repeatable).",
    )
    result.add_argument(
        "--command",
        action="append",
        default=[],
        metavar="NAME=COMMAND",
        help="Inline shell command (repeatable).",
    )
    result.add_argument(
        "--command-cwd",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="Working directory for an inline command.",
    )
    result.add_argument(
        "--command-kind",
        action="append",
        default=[],
        metavar="NAME=KIND",
        help="Kind for an inline command: wheel_smoke, unittest, cross_language, consumer, benchmark, other.",
    )
    result.add_argument(
        "--cwd",
        default=os.getcwd(),
        help="Default working directory (default: current directory).",
    )
    result.add_argument(
        "--output",
        default="validation",
        help="Evidence directory (default: validation).",
    )
    result.add_argument(
        "--default-timeout",
        type=float,
        default=None,
        metavar="SECONDS",
        help="Timeout for inline commands; 0 or omission means no timeout.",
    )
    result.add_argument(
        "--provenance",
        action="store_true",
        help="Write PROVENANCE.json (also implied by provenance path arguments).",
    )
    result.add_argument(
        "--input",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="Input artifact or directory to hash in PROVENANCE.json.",
    )
    result.add_argument("--kernel", help="Kernel source/binary path to hash.")
    result.add_argument("--wheel", help="Wheel path to hash.")
    result.add_argument(
        "--toolchain",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="Toolchain executable to hash and query with --version (repeatable).",
    )
    result.add_argument(
        "--provenance-only",
        action="store_true",
        help="Generate provenance without requiring any validation commands.",
    )
    result.add_argument(
        "--always-zero",
        action="store_true",
        help="Return zero even when a required command fails (results still record failure).",
    )
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        default_cwd = Path(args.cwd).expanduser().resolve(strict=False)
        output = Path(args.output).expanduser().resolve(strict=False)
        output.mkdir(parents=True, exist_ok=True)
        logs = output / "logs"
        logs.mkdir(parents=True, exist_ok=True)

        commands: list[Command] = []
        for spec_path in args.spec:
            commands.extend(load_spec(Path(spec_path).expanduser().resolve(), default_cwd))
        commands.extend(cli_commands(args, default_cwd))
        names = [command.name for command in commands]
        duplicates = sorted({name for name in names if names.count(name) > 1})
        if duplicates:
            raise ValueError("duplicate command names: " + ", ".join(duplicates))
        if not commands and not args.provenance_only:
            raise ValueError("no commands declared; use --spec, --command, or --provenance-only")

        provenance_requested = bool(
            args.provenance or args.input or args.kernel or args.wheel or args.toolchain
        )
        if provenance_requested or args.provenance_only:
            make_provenance(args, output)

        suite_start = utc_now()
        started = time.perf_counter()
        results = [run_one(command, logs, index) for index, command in enumerate(commands, 1)]
        duration = time.perf_counter() - started
        suite_end = utc_now()
        failed_required = [
            item for item in results if item["required"] and item["status"] != "passed"
        ]
        summary = {
            "status": "passed" if not failed_required else "failed",
            "total": len(results),
            "passed": sum(item["status"] == "passed" for item in results),
            "failed": sum(item["status"] != "passed" for item in results),
            "required_failed": len(failed_required),
            "by_kind": {
                kind: {
                    "total": sum(item["kind"] == kind for item in results),
                    "passed": sum(
                        item["kind"] == kind and item["status"] == "passed"
                        for item in results
                    ),
                }
                for kind in sorted({item["kind"] for item in results})
            },
        }
        document = {
            "schema_version": SCHEMA_VERSION,
            "harness": str(Path(__file__).resolve()),
            "start_utc": suite_start,
            "end_utc": suite_end,
            "duration_seconds": round(duration, 6),
            "summary": summary,
            "commands": results,
        }
        atomic_json(output / "COMMAND_RESULTS.json", document)
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return 0 if args.always_zero or not failed_required else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"validation harness error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
