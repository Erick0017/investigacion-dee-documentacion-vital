from __future__ import annotations

"""Independent one-lineage supervisor and atomic MBP3 finalizer."""

import argparse
import ctypes
import datetime as dtm
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

APP = Path(__file__).resolve().parent
PROJECT_ROOT = APP.parent
sys.path.insert(0, str(APP))
import habitat_base as base
import launch_process
import mbp3
import analyze

SCHEMA = "mbp3.campaign.v1"
PYTHON = Path(r"D:\Descargas\ANACONDA MINICONDA\python.exe")
MAIN_ZIP = "MENTE_BASAL_PERSISTENTE_3_CURRICULUM_NATIVO_2H_RESULTADOS.zip"
TRIAL_ZIP = "MENTE_BASAL_PERSISTENTE_3_TRIAL_60S_RESULTADOS.zip"
ARCHIVE_ROOT = "MENTE_BASAL_PERSISTENTE_3_CURRICULUM_NATIVO_2H_RESULTADOS"


def utc_now() -> dtm.datetime:
    return dtm.datetime.now(dtm.timezone.utc)


def iso_utc(value: dtm.datetime | None = None) -> str:
    return (value or utc_now()).astimezone(dtm.timezone.utc).isoformat(timespec="milliseconds")


def iso_local(value: dtm.datetime | None = None) -> str:
    return (value or utc_now()).astimezone().isoformat(timespec="milliseconds")


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(text); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def atomic_json(path: Path, value: Any) -> None:
    atomic_text(path, json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n")


def load_json(path: Path) -> Any:
    last: Exception | None = None
    for attempt in range(20):
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (PermissionError, json.JSONDecodeError) as error:
            last = error; time.sleep(min(0.02 * (attempt + 1), 0.2))
    assert last is not None
    raise last


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def process_alive(pid: Any) -> bool:
    try:
        value = int(pid)
    except (TypeError, ValueError):
        return False
    if value <= 0:
        return False
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, value)
    if not handle:
        return False
    try:
        code = ctypes.c_ulong()
        if not ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
            return False
        return code.value == 259
    finally:
        ctypes.windll.kernel32.CloseHandle(handle)


@dataclass(frozen=True)
class Layout:
    campaign_root: Path
    world_root: Path
    output: Path
    duration_seconds: float
    campaign_id: str
    trial: bool

    @property
    def supervisor(self) -> Path:
        return self.campaign_root / "supervisor"

    @property
    def state(self) -> Path:
        return self.supervisor / "campaign.json"

    @property
    def validation(self) -> Path:
        return self.supervisor / "terminal_validation.json"


def make_layout(args: argparse.Namespace) -> Layout:
    trial = bool(args.trial)
    root = (args.campaign_root or (PROJECT_ROOT / "test_campaign" if trial else PROJECT_ROOT)).resolve()
    duration = float(args.duration if args.duration is not None else (60.0 if trial else 7200.0))
    if not 1 <= duration <= 7 * 24 * 3600:
        raise ValueError("duration must be 1..604800 seconds")
    campaign_id = str(args.campaign_id or ("MBP3-TRIAL-60S" if trial else mbp3.CAMPAIGN_ID))
    output = (args.output or root / (TRIAL_ZIP if trial else MAIN_ZIP)).resolve()
    return Layout(root, root / "worlds" / "MAIN", output, duration, campaign_id, trial)


def _save(layout: Layout, state: dict[str, Any]) -> None:
    state["updated_utc"] = iso_utc()
    atomic_json(layout.state, state)


def _event(state: dict[str, Any], kind: str, **values: Any) -> None:
    state.setdefault("events", []).append({"utc": iso_utc(), "event": kind, **values})
    state["events"] = state["events"][-512:]


def run_json(command: list[str], timeout: float = 900.0) -> dict[str, Any]:
    completed = subprocess.run(command, text=True, capture_output=True, timeout=timeout,
                               cwd=str(PROJECT_ROOT), check=False)
    if completed.returncode != 0:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {command!r}\n"
            f"stdout={completed.stdout[-4000:]}\nstderr={completed.stderr[-4000:]}")
    text = completed.stdout.strip()
    return json.loads(text) if text else {"status": "OK"}


def _write_lock_hashes() -> dict[str, str]:
    hashes = {path.name: sha256(path) for path in sorted((PROJECT_ROOT / "locks").glob("*.json"))}
    atomic_text(PROJECT_ROOT / "locks" / "LOCKS.sha256",
                "".join(f"{value}  {name}\n" for name, value in hashes.items()))
    return hashes


def prepare(layout: Layout) -> dict[str, Any]:
    if layout.state.is_file():
        state = load_json(layout.state)
        return {"status": "ALREADY_PREPARED", "phase": state.get("phase"),
                "world_root": str(layout.world_root)}
    required = [
        PROJECT_ROOT / "validation" / "SELF_TEST.json",
        PROJECT_ROOT / "validation" / "C10H02_MINIMAL_REVALIDATION.json",
        PROJECT_ROOT / "pilots" / "CURRICULUM_PILOT.json",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"prepare requires completed validation: {missing}")
    selftest = load_json(required[0])
    c10 = load_json(required[1])
    pilot = load_json(required[2])
    if not selftest.get("all_passed") or c10.get("verdict") != "PASS" or not all(pilot["criteria"].values()):
        raise RuntimeError("frozen validation does not pass")
    layout.supervisor.mkdir(parents=True, exist_ok=True)
    for name in ("analysis", "validation", "docs"):
        (layout.campaign_root / name).mkdir(parents=True, exist_ok=True)
    config = dict(load_json(PROJECT_ROOT / "config" / "main.json"))
    config.update({"campaign_id": layout.campaign_id,
                   "world_id": "MBP3-TRIAL-MAIN" if layout.trial else mbp3.WORLD_ID,
                   "max_autonomous_hours": max(layout.duration_seconds / 3600.0 + 0.25, 0.1)})
    config_path = layout.campaign_root / "config" / "active.json"
    atomic_json(config_path, config)
    init = run_json([str(PYTHON), "-B", str(APP / "mbp3.py"), "init",
                     "--root", str(layout.world_root), "--config", str(config_path)])
    now = utc_now()
    state = {
        "schema": SCHEMA, "campaign_id": layout.campaign_id,
        "world_id": config["world_id"], "trial": layout.trial,
        "phase": "PREPARED", "sealed": False,
        "created_utc": iso_utc(now), "created_local": iso_local(now),
        "duration_seconds": layout.duration_seconds, "world_root": str(layout.world_root),
        "output": str(layout.output), "python": str(PYTHON),
        "parent_sha256": mbp3.PARENT_SHA256, "parent_tick": mbp3.PARENT_TICK,
        "lock_hashes": _write_lock_hashes(), "init": init, "events": [],
        "worker_pid": None, "supervisor_pid": os.getpid(), "midpoint_saved": False,
        "package_attempts": [],
    }
    _event(state, "prepared", world_root=str(layout.world_root))
    _save(layout, state)
    return {"status": "PREPARED", "world_root": str(layout.world_root),
            "parent_tick": mbp3.PARENT_TICK, "parent_sha256": mbp3.PARENT_SHA256}


def _status(layout: Layout) -> dict[str, Any]:
    path = base.root_paths(layout.world_root)["status"]
    return load_json(path) if path.is_file() else {}


def _launch_worker(layout: Layout, state: dict[str, Any]) -> dict[str, Any]:
    paths = base.root_paths(layout.world_root)
    handshake = layout.supervisor / "worker_launch.json"
    result = launch_process.launch(
        python=PYTHON, script=APP / "mbp3.py",
        script_args=["worker", "--root", str(layout.world_root)],
        cwd=PROJECT_ROOT, stdout_path=paths["stdout"], stderr_path=paths["stderr"],
        handshake_path=handshake, startup_probe_seconds=0.5,
        # A supervisor already detached from the Codex job may receive
        # ERROR_ACCESS_DENIED if CREATE_BREAKAWAY_FROM_JOB is requested again.
        # Falling back here does not tie it to Codex: there is then no
        # kill-on-close job to inherit, and the launcher records the path used.
        allow_job_inheritance=True)
    state["worker_pid"] = result["child_pid"]
    _event(state, "worker_launched", pid=result["child_pid"])
    _save(layout, state)
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        status = _status(layout)
        if status.get("pid") == result["child_pid"] and status.get("state") in {"PAUSED", "RUNNING"}:
            return result
        if not process_alive(result["child_pid"]):
            break
        time.sleep(0.2)
    raise RuntimeError(f"worker failed startup handshake: {_status(layout)}")


def _command(layout: Layout, operation: str, arguments: dict[str, Any],
             timeout: float = 600.0) -> dict[str, Any]:
    return base.submit_command(layout.world_root, operation, arguments, timeout)


def _lock_available(path: Path) -> bool:
    try:
        with base.WriterLock(path):
            return True
    except RuntimeError:
        return False


def validate_terminal(layout: Layout, descriptor_relative: str) -> dict[str, Any]:
    paths = base.root_paths(layout.world_root)
    descriptor = layout.world_root / descriptor_relative
    cut = load_json(descriptor)
    checkpoint = layout.world_root / cut["end_checkpoint"]
    sidecar = checkpoint.with_suffix(checkpoint.suffix + ".json")
    runtime = mbp3.dee.Runtime.load_snapshot(str(checkpoint))
    status = _status(layout)
    pid = status.get("pid")
    checks = {
        "descriptor_schema": cut.get("schema") == "mente-basal.collection.v1",
        "stop_after": cut.get("stop_after") is True,
        "status_stopped_safe": status.get("state") == "STOPPED_SAFE",
        "pid_dead": not process_alive(pid),
        "writer_lock_free": _lock_available(paths["lock"]),
        "checkpoint_exists": checkpoint.is_file(),
        "sidecar_exists": sidecar.is_file(),
        "checkpoint_tick_exact": int(runtime.current_tick) == int(cut["end_tick"]),
        "checkpoint_sha_exact": sha256(checkpoint) == load_json(sidecar)["sha256"],
        "no_receipts": len(runtime.receipts) == 0,
        "world_id": cut.get("world_id") == status.get("world_id"),
    }
    result = {
        "schema": "mbp3.terminal-validation.v1", "created_utc": iso_utc(),
        "all_valid": all(checks.values()), "checks": checks,
        "descriptor": descriptor_relative, "checkpoint": cut["end_checkpoint"],
        "checkpoint_sha256": sha256(checkpoint), "tick": int(runtime.current_tick),
        "status": status,
    }
    atomic_json(layout.validation, result)
    if not result["all_valid"]:
        raise RuntimeError(f"terminal validation failed: {checks}")
    return result


def _blocked(relative: Path, output: Path, source: Path) -> bool:
    parts = {part.casefold() for part in relative.parts}
    if parts.intersection({"__pycache__", ".runtime", "python_site", "selftest_scratch"}):
        return True
    if source.suffix.casefold() in {".pyc", ".pyo", ".tmp", ".zip"}:
        return True
    try:
        return source.resolve() == output.resolve()
    except OSError:
        return False


def _sources(layout: Layout) -> dict[str, Path]:
    sources: dict[str, Path] = {}

    def add(name: str | PurePosixPath, source: Path) -> None:
        key = PurePosixPath(str(name).replace("\\", "/")).as_posix()
        if key.startswith("/") or ".." in PurePosixPath(key).parts:
            raise RuntimeError(f"unsafe archive name {key}")
        source = source.resolve()
        if not source.is_file():
            raise FileNotFoundError(source)
        if key in sources and sources[key] != source:
            raise RuntimeError(f"archive collision {key}")
        sources[key] = source

    def tree(prefix: str, root: Path) -> None:
        if not root.is_dir():
            return
        for source in sorted(root.rglob("*")):
            if source.is_file():
                relative = source.relative_to(root)
                if not _blocked(relative, layout.output, source):
                    add(PurePosixPath(prefix) / PurePosixPath(relative.as_posix()), source)

    for name in ("app", "tools", "baseline", "locks", "parent", "pilots", "provenance"):
        tree(name, PROJECT_ROOT / name)
    # Project validation contains pre-launch scientific validation. Campaign
    # validation/analysis/docs may live in the trial subroot or project root.
    tree("validation", PROJECT_ROOT / "validation")
    tree("config", PROJECT_ROOT / "config")
    tree("docs", PROJECT_ROOT / "docs")
    if layout.campaign_root != PROJECT_ROOT:
        tree("campaign/analysis", layout.campaign_root / "analysis")
        tree("campaign/validation", layout.campaign_root / "validation")
        tree("campaign/config", layout.campaign_root / "config")
        tree("campaign/docs", layout.campaign_root / "docs")
    else:
        tree("analysis", layout.campaign_root / "analysis")
    tree("supervisor", layout.supervisor)
    tree("worlds/MAIN", layout.world_root)
    if not layout.trial:
        trial = PROJECT_ROOT / "test_campaign"
        for relative in (
                Path("supervisor/campaign.json"), Path("supervisor/terminal_validation.json"),
                Path("analysis/FINAL_ANALYSIS.json"), Path("analysis/CAPABILITY_PROFILE.json"),
                Path("validation/PACKAGE_VALIDATION.json")):
            source = trial / relative
            if not source.is_file():
                raise RuntimeError(f"main package requires completed trial evidence: {source}")
            add(PurePosixPath("trial_evidence") / PurePosixPath(relative.as_posix()), source)
    return sources


def verify_zip(path: Path, expected_campaign: str | None = None) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f"CRC failure: {bad}")
        names = archive.namelist()
        if any(name.casefold().endswith(".zip") for name in names):
            raise RuntimeError("nested ZIP detected")
        manifest_name = next((name for name in names if name.endswith("/MANIFEST.json")), None)
        hashes_name = next((name for name in names if name.endswith("/HASHES.sha256")), None)
        if not manifest_name or not hashes_name:
            raise RuntimeError("manifest or hashes absent")
        manifest = json.loads(archive.read(manifest_name))
        if expected_campaign and manifest.get("campaign_id") != expected_campaign:
            raise RuntimeError("campaign id mismatch")
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path),
            "entries": len(names), "crc": "PASS", "manifest": manifest_name}


def package(layout: Layout, validation: dict[str, Any]) -> dict[str, Any]:
    if layout.output.is_file():
        return {"status": "ALREADY_FINAL_READY", **verify_zip(layout.output, layout.campaign_id)}
    sources = _sources(layout)
    prefix = ARCHIVE_ROOT if not layout.trial else "MENTE_BASAL_PERSISTENTE_3_TRIAL_60S_RESULTADOS"
    with tempfile.TemporaryDirectory(prefix="mbp3-package-") as text:
        temp = Path(text)
        stage = temp / prefix
        for name, source in sorted(sources.items()):
            destination = stage / Path(name)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        files = []
        for item in sorted(stage.rglob("*")):
            if item.is_file():
                files.append({"path": item.relative_to(stage).as_posix(),
                              "bytes": item.stat().st_size, "sha256": sha256(item)})
        manifest = {
            "schema": "mbp3.package.v1", "campaign_id": layout.campaign_id,
            "world_id": load_json(layout.world_root / "world" / "instance.json")["world_id"],
            "created_utc": iso_utc(), "trial": layout.trial,
            "parent_tick": mbp3.PARENT_TICK, "parent_sha256": mbp3.PARENT_SHA256,
            "terminal_tick": validation["tick"],
            "terminal_checkpoint": validation["checkpoint"], "files": files,
        }
        atomic_json(stage / "MANIFEST.json", manifest)
        hash_lines = [f"{entry['sha256']}  {entry['path']}\n" for entry in files]
        atomic_text(stage / "HASHES.sha256", "".join(hash_lines))
        candidate = temp / layout.output.name
        with zipfile.ZipFile(candidate, "w", zipfile.ZIP_DEFLATED, compresslevel=9,
                             allowZip64=True) as archive:
            for item in sorted(stage.rglob("*")):
                if item.is_file():
                    archive.write(item, item.relative_to(temp).as_posix())
        verify_zip(candidate, layout.campaign_id)
        # Clean extraction: load the delivered terminal snapshot and verify CRC.
        extract = temp / "extract"
        with zipfile.ZipFile(candidate) as archive:
            archive.extractall(extract)
        checkpoint = extract / prefix / "worlds" / "MAIN" / validation["checkpoint"]
        runtime = mbp3.dee.Runtime.load_snapshot(str(checkpoint))
        if int(runtime.current_tick) != int(validation["tick"]):
            raise RuntimeError("clean-extraction terminal checkpoint tick mismatch")
        sibling = layout.output.with_name(f".{layout.output.name}.{uuid.uuid4().hex}.tmp")
        layout.output.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(candidate, sibling)
            verify_zip(sibling, layout.campaign_id)
            if layout.output.exists():
                raise RuntimeError(f"refusing to overwrite {layout.output}")
            os.replace(sibling, layout.output)
        finally:
            sibling.unlink(missing_ok=True)
    published = verify_zip(layout.output, layout.campaign_id)
    package_validation = {
        "schema": "mbp3.package-validation.v1", "created_utc": iso_utc(),
        "all_passed": True, "published": published,
        "clean_extraction_checkpoint_loaded": True,
        "terminal_tick": validation["tick"],
    }
    atomic_json(layout.campaign_root / "validation" / "PACKAGE_VALIDATION.json",
                package_validation)
    return {"status": "FINAL_READY", **published}


def supervise(layout: Layout) -> dict[str, Any]:
    prepare(layout)
    state = load_json(layout.state)
    if state.get("phase") == "FINAL_READY" and layout.output.is_file():
        return {"status": "ALREADY_FINAL_READY", **verify_zip(layout.output, layout.campaign_id)}
    state["supervisor_pid"] = os.getpid()
    state["phase"] = "STARTING"
    _save(layout, state)
    status = _status(layout)
    if status.get("state") in {"PAUSED", "RUNNING"} and process_alive(status.get("pid")):
        worker_launch = {"child_pid": status["pid"], "status": "ALREADY_RUNNING"}
    else:
        worker_launch = _launch_worker(layout, state)
    release = _command(layout, "release_autonomy", {})
    if not release.get("ok"):
        raise RuntimeError(f"release autonomy failed: {release}")
    started = utc_now()
    deadline = started + dtm.timedelta(seconds=layout.duration_seconds)
    midpoint = started + dtm.timedelta(seconds=layout.duration_seconds / 2)
    state.update({
        "phase": "RUNNING", "started_utc": iso_utc(started),
        "started_local": iso_local(started), "deadline_utc": iso_utc(deadline),
        "deadline_local": iso_local(deadline), "worker_launch": worker_launch,
        "worker_pid": worker_launch["child_pid"], "release": release,
    })
    _event(state, "autonomy_released", tick=release.get("tick_after"),
           deadline_utc=state["deadline_utc"])
    _save(layout, state)
    last_save = 0.0
    while utc_now() < deadline:
        status = _status(layout)
        if not status or status.get("state") not in {"RUNNING", "PAUSED"}:
            raise RuntimeError(f"worker left active state before deadline: {status}")
        if not process_alive(status.get("pid")):
            raise RuntimeError(f"worker exited before deadline: {status}")
        now = utc_now()
        if now >= midpoint and not state.get("midpoint_saved"):
            saved = _command(layout, "save", {"reason": "campaign_1h"})
            if not saved.get("ok"):
                raise RuntimeError(f"midpoint save failed: {saved}")
            state["midpoint_saved"] = True
            state["midpoint"] = saved
            _event(state, "midpoint_saved", tick=saved.get("tick_after"))
            _save(layout, state)
        if time.monotonic() - last_save >= 10:
            state["last_status"] = status
            _save(layout, state)
            last_save = time.monotonic()
        time.sleep(min(1.0, max(0.05, (deadline - now).total_seconds())))

    state["phase"] = "FINALIZING"
    _save(layout, state)
    request_id = "FINAL_MBP3_TRIAL" if layout.trial else "FINAL_MBP3_NATIVE_CURRICULUM_2H"
    response = _command(layout, "collect_stop", {"request_id": request_id}, 900.0)
    if not response.get("ok"):
        raise RuntimeError(f"terminal collect_stop failed: {response}")
    descriptor_relative = str(response["descriptor"])
    wait_deadline = time.monotonic() + 900
    while time.monotonic() < wait_deadline:
        status = _status(layout)
        if status.get("state") == "STOPPED_SAFE" and not process_alive(status.get("pid")):
            break
        time.sleep(0.25)
    else:
        raise RuntimeError(f"worker did not reach STOPPED_SAFE: {_status(layout)}")
    validation = validate_terminal(layout, descriptor_relative)
    state["phase"] = "TERMINAL_VALIDATED"; state["terminal"] = validation
    _save(layout, state)
    descriptor = layout.world_root / descriptor_relative
    analysis_result = analyze.build(layout.campaign_root, descriptor)
    state["phase"] = "ANALYZED"; state["analysis_tick"] = analysis_result["terminal"]["tick"]
    _save(layout, state)
    state["phase"] = "PACKAGING"; _save(layout, state)
    attempt = {"started_utc": iso_utc(), "status": "RUNNING"}
    state.setdefault("package_attempts", []).append(attempt); _save(layout, state)
    try:
        packaged = package(layout, validation)
        attempt.update({"completed_utc": iso_utc(), "status": "OK", "result": packaged})
        state["phase"] = "FINAL_READY"; state["sealed"] = True; state["package"] = packaged
        _event(state, "final_package_published", path=str(layout.output),
               sha256=packaged["sha256"])
        _save(layout, state)
        return packaged
    except Exception as error:
        attempt.update({"completed_utc": iso_utc(), "status": "FAILED", "error": str(error)})
        state["phase"] = "PACKAGE_FAILED"; state["sealed"] = True
        _save(layout, state)
        raise


def stop(layout: Layout) -> dict[str, Any]:
    state = load_json(layout.state)
    if state.get("phase") == "FINAL_READY":
        return {"status": "ALREADY_FINAL_READY", **verify_zip(layout.output, layout.campaign_id)}
    status = _status(layout)
    if not process_alive(status.get("pid")):
        raise RuntimeError("worker is not active; automatic restart is forbidden")
    response = _command(layout, "collect_stop", {"request_id": "MANUAL_MBP3_STOP"}, 900)
    return {"status": "STOP_REQUESTED", "response": response}


def repackage(layout: Layout) -> dict[str, Any]:
    state = load_json(layout.state)
    validation = load_json(layout.validation)
    if not validation.get("all_valid"):
        raise RuntimeError("repackage requires validated terminal cut")
    if not (layout.campaign_root / "analysis" / "FINAL_ANALYSIS.json").is_file():
        raise RuntimeError("repackage never reruns missing analysis")
    result = package(layout, validation)
    state["phase"] = "FINAL_READY"; state["sealed"] = True; state["package"] = result
    _save(layout, state)
    return result


def status(layout: Layout) -> dict[str, Any]:
    state = load_json(layout.state) if layout.state.is_file() else None
    world = _status(layout) if layout.world_root.exists() else None
    return {
        "schema": "mbp3.campaign-status.v1", "campaign": state,
        "world": world,
        "worker_alive": bool(world and process_alive(world.get("pid"))),
        "supervisor_alive": bool(state and process_alive(state.get("supervisor_pid"))),
        "output": verify_zip(layout.output, layout.campaign_id) if layout.output.is_file() else None,
    }


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("prepare", "supervise", "status", "stop", "repackage"):
        child = sub.add_parser(name)
        child.add_argument("--trial", action="store_true")
        child.add_argument("--campaign-root", type=Path)
        child.add_argument("--campaign-id")
        child.add_argument("--duration", type=float)
        child.add_argument("--output", type=Path)
    return p


def main() -> int:
    args = parser().parse_args()
    layout = make_layout(args)
    if args.command == "prepare": result = prepare(layout)
    elif args.command == "supervise": result = supervise(layout)
    elif args.command == "status": result = status(layout)
    elif args.command == "stop": result = stop(layout)
    elif args.command == "repackage": result = repackage(layout)
    else: raise AssertionError(args.command)
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"status": "ERROR", "type": type(error).__name__,
                          "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
