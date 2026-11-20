from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("passive_mobile_observer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load passive observer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--area", required=True, type=Path)
    parser.add_argument("--poll-seconds", type=float, default=15.0)
    args = parser.parse_args()
    root = args.root.resolve()
    area = args.area.resolve()
    runtime_dir = area / "observer_runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    pid_path = runtime_dir / "observer.pid"
    status_path = runtime_dir / "observer_status.json"
    stop_path = runtime_dir / "observer.stop"
    log_path = runtime_dir / "observer_samples.jsonl"
    if pid_path.exists():
        previous = int(pid_path.read_text(encoding="utf-8").strip())
        try:
            os.kill(previous, 0)
        except OSError:
            pass
        else:
            raise RuntimeError(f"observer already running with PID {previous}")
    pid_path.write_text(str(os.getpid()) + "\n", encoding="utf-8")
    stop_path.unlink(missing_ok=True)
    sys.path.insert(0, str(root / "app"))
    import habitat
    observer = load_module(area / "tools" / "passive_mobile_observer.py")
    controller = json.loads((root / "world" / "controller.json").read_text(encoding="utf-8"))
    deadline_text = controller.get("autonomous_deadline_utc")
    deadline = (datetime.fromisoformat(deadline_text) if deadline_text else None)
    last_checkpoint = None
    last_sample_tick = None
    samples = 0
    state = "RUNNING"
    error = None
    try:
        while True:
            now = datetime.now(timezone.utc)
            if stop_path.exists():
                state = "STOPPED_REQUESTED"
                break
            if deadline is not None and now >= deadline:
                state = "STOPPED_DEADLINE"
                break
            pointer = (root / "world" / "latest_checkpoint.txt").read_text(encoding="utf-8").strip()
            checkpoint = (root / pointer).resolve()
            if str(checkpoint) != last_checkpoint:
                result = observer.sample(habitat.dee, checkpoint, False)
                result["observed_utc"] = utc_now()
                result["observer_pid"] = os.getpid()
                with log_path.open("a", encoding="utf-8") as stream:
                    stream.write(json.dumps(result, separators=(",", ":")) + "\n")
                    stream.flush()
                    os.fsync(stream.fileno())
                last_checkpoint = str(checkpoint)
                last_sample_tick = int(result["sample_tick"])
                samples += 1
            world_status = json.loads((root / "world" / "status.json").read_text(encoding="utf-8"))
            atomic_json(status_path, {
                "schema": "mente-basal.passive-observer-status.v1",
                "state": state, "pid": os.getpid(), "observed_utc": utc_now(),
                "world_id": world_status.get("world_id"),
                "session_id": world_status.get("session_id"),
                "world_status": world_status.get("state"),
                "world_tick": world_status.get("tick"),
                "last_checkpoint": last_checkpoint,
                "last_sample_tick": last_sample_tick,
                "samples": samples, "deadline_utc": deadline_text,
                "mode": "read-only checkpoint follower; no access to live mutable arrays",
                "error": error,
            })
            if world_status.get("state") not in ("RUNNING", "PAUSED"):
                state = "STOPPED_WORLD_NOT_RUNNING"
                break
            time.sleep(max(1.0, args.poll_seconds))
    except Exception as exc:
        state = "FAILED"
        error = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        atomic_json(status_path, {
            "schema": "mente-basal.passive-observer-status.v1",
            "state": state, "pid": os.getpid(), "observed_utc": utc_now(),
            "last_checkpoint": last_checkpoint, "last_sample_tick": last_sample_tick,
            "samples": samples, "deadline_utc": deadline_text,
            "mode": "read-only checkpoint follower; no access to live mutable arrays",
            "error": error,
        })
        pid_path.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
