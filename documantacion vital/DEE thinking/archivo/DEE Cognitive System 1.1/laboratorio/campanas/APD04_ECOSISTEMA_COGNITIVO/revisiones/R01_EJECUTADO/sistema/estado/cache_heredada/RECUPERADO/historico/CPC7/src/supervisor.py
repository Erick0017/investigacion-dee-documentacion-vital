"""Campaign-owned process supervision, fixed UTC + monotonic budget, no physics."""
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def put(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.pending.' + str(os.getpid()))
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
    os.replace(temporary, path)


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1048576), b''):
            value.update(block)
    return value.hexdigest()


def remaining():
    data = json.loads((ROOT / 'BUDGET.json').read_text(encoding='utf-8-sig'))
    clock = ctypes.windll.kernel32.QueryPerformanceCounter
    current = ctypes.c_longlong()
    if not clock(ctypes.byref(current)):
        raise OSError('Monotonic clock unavailable')
    monotonic = data['budget_seconds'] - (current.value - data['start_qpc']) / data['qpc_frequency']
    wall = (datetime.fromisoformat(data['deadline_utc']) - datetime.now(timezone.utc)).total_seconds()
    return max(0, min(monotonic, wall))


class OwnedJob:
    """Windows JobObject kills only a launched worker and its descendants."""
    def __init__(self, process):
        class Basic(ctypes.Structure):
            _fields_ = [('PerProcessUserTimeLimit', ctypes.c_int64), ('PerJobUserTimeLimit', ctypes.c_int64),
                        ('LimitFlags', wintypes.DWORD), ('MinimumWorkingSetSize', ctypes.c_size_t),
                        ('MaximumWorkingSetSize', ctypes.c_size_t), ('ActiveProcessLimit', wintypes.DWORD),
                        ('Affinity', ctypes.c_size_t), ('PriorityClass', wintypes.DWORD), ('SchedulingClass', wintypes.DWORD)]
        class IO(ctypes.Structure):
            _fields_ = [(name, ctypes.c_uint64) for name in ('ReadOperationCount', 'WriteOperationCount', 'OtherOperationCount',
                                                          'ReadTransferCount', 'WriteTransferCount', 'OtherTransferCount')]
        class Extended(ctypes.Structure):
            _fields_ = [('BasicLimitInformation', Basic), ('IoInfo', IO), ('ProcessMemoryLimit', ctypes.c_size_t),
                        ('JobMemoryLimit', ctypes.c_size_t), ('PeakProcessMemoryUsed', ctypes.c_size_t),
                        ('PeakJobMemoryUsed', ctypes.c_size_t)]
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        self.kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        self.kernel.CreateJobObjectW.restype = wintypes.HANDLE
        self.kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        self.kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        self.kernel.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        self.handle = self.kernel.CreateJobObjectW(None, None)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        config = Extended()
        config.BasicLimitInformation.LimitFlags = 0x2000  # KILL_ON_JOB_CLOSE
        if not self.kernel.SetInformationJobObject(self.handle, 9, ctypes.byref(config), ctypes.sizeof(config)):
            self.close()
            raise ctypes.WinError(ctypes.get_last_error())
        if not self.kernel.AssignProcessToJobObject(self.handle, wintypes.HANDLE(process._handle)):
            self.close()
            raise ctypes.WinError(ctypes.get_last_error())

    def terminate(self):
        if self.handle:
            self.kernel.TerminateJobObject(self.handle, 124)

    def close(self):
        if self.handle:
            self.kernel.CloseHandle(self.handle)
            self.handle = None


def run(name, argv, timeout=600, cwd=None, reserve=1500):
    available = remaining() - reserve
    if available <= 0:
        raise TimeoutError('Campaign closing reserve reached; no new worker launched')
    timeout = min(float(timeout), available)
    target = ROOT / 'jobs' / name
    target.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
    with (target / 'stdout.log').open('w', encoding='utf-8') as stdout, (target / 'stderr.log').open('w', encoding='utf-8') as stderr:
        process = subprocess.Popen([str(x) for x in argv], cwd=str(cwd or ROOT), env=env,
                                   stdout=stdout, stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            job = OwnedJob(process)
        except Exception:
            process.kill()
            process.wait(timeout=15)
            raise
        status = 'COMPLETED'
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            status = 'TIMEOUT'
            job.terminate()
            process.wait(timeout=30)
        finally:
            job.close()
    result = {'name': name, 'argv': [str(x) for x in argv], 'pid': process.pid, 'timeout_seconds': timeout,
              'elapsed_seconds': time.monotonic() - started, 'exit_code': process.returncode,
              'status': status, 'remaining_seconds': remaining(), 'owned_job_kill_on_close': True}
    put(target / 'COMMAND.json', result)
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=True)
    parser.add_argument('--timeout', type=int, default=600)
    parser.add_argument('--closing', action='store_true')
    parser.add_argument('argv', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.argv[1:] if args.argv[:1] == ['--'] else args.argv
    result = run(args.name, command, args.timeout, reserve=0 if args.closing else 1500)
    raise SystemExit(result['exit_code'])
