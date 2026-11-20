"""External host-only handle monitor, no engine/import/ticks or process control."""
from pathlib import Path
from datetime import datetime, timezone
import ctypes
from ctypes import wintypes
import importlib.util
import json
import time

ROOT = Path(__file__).resolve().parents[4]
FOLDER = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/ATENCION_SENSOR02_C_R03'
START = FOLDER / 'REVISION_SUPERVISION_ANTES_MATERIAL.json'
DEADLINE = datetime(2026, 10, 26, 22, 0, tzinfo=timezone.utc)


def main():
    while not START.exists() and datetime.now(timezone.utc) < DEADLINE:
        time.sleep(.5)
    if not START.exists():
        raise TimeoutError('No owner start before the fixed front deadline')
    entry = json.loads(START.read_text(encoding='utf8'))
    spec = importlib.util.spec_from_file_location('host_job_query_only', ROOT / 'sistema/app/process_control.py')
    pc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pc)
    kernel = pc.K
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    process = kernel.OpenProcess(0x1000, False, entry['pid'])
    job = kernel.OpenJobObjectW(0x0004, False, entry['job_name'])
    if not process or not job:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        with (FOLDER / 'HOST_HANDLE_MUESTRAS_PASIVAS.jsonl').open('x', encoding='utf8', buffering=1) as stream:
            while datetime.now(timezone.utc) < DEADLINE:
                code = wintypes.DWORD()
                ok = kernel.GetExitCodeProcess(process, ctypes.byref(code))
                resources = pc.job_resources(job)
                value = {'wall_utc': datetime.now(timezone.utc).isoformat(), 'launcher_pid': entry['pid'],
                    'launcher_exit_code': int(code.value) if ok else None,
                    'resources': resources, 'no_process_termination_or_DEE_interaction': True}
                stream.write(json.dumps(value, separators=(',', ':')) + '\n')
                if ok and code.value != 259 and not resources.get('job_active_processes'):
                    break
                time.sleep(1)
    finally:
        kernel.CloseHandle(process)
        kernel.CloseHandle(job)


if __name__ == '__main__':
    main()
