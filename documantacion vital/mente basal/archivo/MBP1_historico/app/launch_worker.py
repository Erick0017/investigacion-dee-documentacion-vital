from __future__ import annotations

import argparse
import ctypes
import json
import os
import subprocess
import sys
import time
from pathlib import Path


CREATE_BREAKAWAY_FROM_JOB = 0x01000000
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_NO_WINDOW = 0x08000000
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JOB_OBJECT_LIMIT_BREAKAWAY_OK = 0x00000800
JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK = 0x00001000


def parent_job_flags() -> tuple[bool, int | None]:
    kernel32 = ctypes.windll.kernel32
    kernel32.GetCurrentProcess.restype = ctypes.c_void_p
    kernel32.IsProcessInJob.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                        ctypes.POINTER(ctypes.c_int)]
    kernel32.IsProcessInJob.restype = ctypes.c_int
    in_job = ctypes.c_int(0)
    process = kernel32.GetCurrentProcess()
    if not kernel32.IsProcessInJob(process, None,
                                   ctypes.byref(in_job)):
        raise ctypes.WinError()
    if not in_job.value:
        return False, None

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
    if not kernel32.QueryInformationJobObject(None, 9, ctypes.byref(info),
                                               ctypes.sizeof(info), None):
        raise ctypes.WinError()
    return True, int(info.BasicLimitInformation.LimitFlags)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()
    root = args.root.resolve()
    script = root / "app" / "habitat.py"
    site = root / "baseline" / "python_site"
    status = root / "world" / "status.json"
    stdout_path = root / "world" / "worker.stdout.log"
    stderr_path = root / "world" / "worker.stderr.log"
    if not script.exists() or not site.exists():
        raise RuntimeError("application or local wheel installation is missing")

    in_job, flags = parent_job_flags()
    creationflags = CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW
    if in_job and flags is not None and flags & JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE:
        if flags & (JOB_OBJECT_LIMIT_BREAKAWAY_OK | JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK):
            creationflags |= CREATE_BREAKAWAY_FROM_JOB
        else:
            raise RuntimeError("parent job kills children and does not permit breakaway")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(site)
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    with stdout_path.open("ab", buffering=0) as stdout, \
            stderr_path.open("ab", buffering=0) as stderr:
        process = subprocess.Popen(
            [str(args.python), "-B", "-u", str(script), "worker", "--root", str(root)],
            cwd=str(root), env=env, stdin=subprocess.DEVNULL, stdout=stdout,
            stderr=stderr, close_fds=True, creationflags=creationflags,
        )

    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"worker exited during handshake: {process.returncode}")
        if status.exists():
            try:
                payload = json.loads(status.read_text(encoding="utf-8"))
                payload_pid = payload.get("pid")
                if payload_pid is not None and int(payload_pid) == process.pid:
                    job = payload.get("job", {})
                    if job.get("kill_on_job_close"):
                        process.terminate()
                        raise RuntimeError("worker remained in a kill-on-close job")
                    result = {
                        "spawn_pid": process.pid,
                        "worker_pid": payload["pid"],
                        "state": payload["state"],
                        "tick": payload["tick"],
                        "parent_job": {"in_job": in_job, "limit_flags": flags},
                        "worker_job": job,
                        "independent_handshake": True,
                    }
                    print(json.dumps(result, indent=2))
                    return 0
            except (json.JSONDecodeError, OSError, TypeError, ValueError):
                pass
        time.sleep(0.2)
    process.terminate()
    raise TimeoutError("worker did not publish an independent handshake")


if __name__ == "__main__":
    raise SystemExit(main())
