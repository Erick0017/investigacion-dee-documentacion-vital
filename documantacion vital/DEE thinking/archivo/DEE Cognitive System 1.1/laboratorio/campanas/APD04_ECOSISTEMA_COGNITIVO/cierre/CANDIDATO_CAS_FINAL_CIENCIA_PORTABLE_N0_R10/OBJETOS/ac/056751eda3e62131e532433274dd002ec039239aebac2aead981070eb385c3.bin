"""Close only C's owned supervisor/job after Root's explicit budget reassignment."""
from pathlib import Path
from datetime import datetime, timezone
import ctypes
from ctypes import wintypes
import importlib.util
import json
import shutil
import sqlite3
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/ATENCION_SENSOR02_C_R03'
LIFE = 'APD04_ATENCION_SENSOR02_AUX'
ID = 'apd04_attention_C_STOP_BUDGET_213241_R01'


def write(name, value):
    with (OUT / name).open('x', encoding='utf8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def main():
    if (OUT / 'CIERRE_REASIGNACION_ROOT.json').exists():
        raise FileExistsError('The owned closure already exists; never repeat STOP')
    start = json.loads((OUT / 'REVISION_SUPERVISION_ANTES_MATERIAL.json').read_text(encoding='utf8'))
    spec = importlib.util.spec_from_file_location('owned_C_job_control_only', ROOT / 'sistema/app/process_control.py')
    pc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pc)
    K = pc.K
    N = ctypes.WinDLL('ntdll')
    class Basic(ctypes.Structure):
        _fields_ = [('reserved1', ctypes.c_void_p), ('peb', ctypes.c_void_p),
            ('reserved2', ctypes.c_void_p * 2), ('pid', ctypes.c_size_t), ('parent', ctypes.c_size_t)]
    class Unicode(ctypes.Structure):
        _fields_ = [('length', wintypes.USHORT), ('maximum', wintypes.USHORT), ('buffer', ctypes.c_void_p)]
    K.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    K.OpenProcess.restype = wintypes.HANDLE
    K.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    K.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    K.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    N.NtQueryInformationProcess.argtypes = [wintypes.HANDLE, wintypes.ULONG, ctypes.c_void_p, wintypes.ULONG, ctypes.POINTER(wintypes.ULONG)]
    N.NtQueryInformationProcess.restype = wintypes.LONG
    N.NtSuspendProcess.argtypes = [wintypes.HANDLE]
    N.NtSuspendProcess.restype = wintypes.LONG
    owner = K.OpenProcess(0x1000 | 0x100000, False, start['pid'])
    if not owner:
        raise ctypes.WinError(ctypes.get_last_error())
    basic = Basic()
    size = wintypes.ULONG()
    status = N.NtQueryInformationProcess(owner, 0, ctypes.byref(basic), ctypes.sizeof(basic), ctypes.byref(size))
    if status < 0 or basic.pid != start['pid']:
        raise RuntimeError('Cannot resolve the verified owned owner parent')
    driver_pid = int(basic.parent)
    driver = K.OpenProcess(0x1000 | 0x800 | 1 | 0x100000, False, driver_pid)
    if not driver:
        raise ctypes.WinError(ctypes.get_last_error())
    needed = wintypes.ULONG()
    N.NtQueryInformationProcess(driver, 60, None, 0, ctypes.byref(needed))
    if not 16 < needed.value < 1048576:
        raise RuntimeError('Bounded command-line identity unavailable; do not suspend another process')
    buffer = ctypes.create_string_buffer(needed.value)
    status = N.NtQueryInformationProcess(driver, 60, buffer, len(buffer), ctypes.byref(needed))
    if status < 0:
        raise RuntimeError('Own driver command line could not be verified')
    command = Unicode.from_buffer(buffer)
    command_line = ctypes.wstring_at(command.buffer, command.length // 2)
    normalized_command = command_line.lower().replace('/', '\\')
    expected_relative = 'laboratorio\\campanas\\apd04_ecosistema_cognitivo\\native_candidates\\ejecutar_atencion_c_apd04_r03.py'
    if expected_relative not in normalized_command:
        raise RuntimeError('The owner parent is not the exact declared C driver: ' + command_line)
    job = K.OpenJobObjectW(0x0004 | 0x0008, False, start['job_name'])
    if not job:
        raise ctypes.WinError(ctypes.get_last_error())
    write('CIERRE_REASIGNACION_INTENCION.json', {'Root_decision_utc': '2026-10-26T21:32:41+00:00',
        'actual_close_started_utc': datetime.now(timezone.utc).isoformat(), 'driver_pid': driver_pid,
        'driver_command_line': command_line, 'owner_launcher_pid': start['pid'], 'owner_job': start['job_name'],
        'reason': 'Reassign finite campaign resources, not cognitive error or completion of the planned horizon.',
        'no_Native_restart_rewind_or_pending_clear': True})
    shutil.copy2(Path(__file__).with_name('ejecutar_atencion_c_apd04_r03.py'), OUT / 'DRIVER_C_EJECUTADO.py')
    if N.NtSuspendProcess(driver) < 0:
        raise RuntimeError('Could not pause the own supervisor; no owner command was sent')
    # Only the Python plan supervisor is paused. Native owner remains running.
    database = ROOT / 'sistema/estado/servicios_persistentes' / LIFE / 'cola.sqlite3'
    with sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True) as connection:
        exists = connection.execute('select status from requests where id=?', (ID,)).fetchone()
    argv = [sys.executable, '-I', '-B', '-X', 'utf8', str(ROOT / 'sistema/gestionar.py'),
            'mente-unificada-detener', '--vida', LIFE, '--id', ID, '--esperar', '120']
    if exists:
        argv = [sys.executable, '-I', '-B', '-X', 'utf8', str(ROOT / 'sistema/gestionar.py'),
                'mente-unificada-resultado', '--vida', LIFE, '--id', ID]
    stopped = subprocess.run(argv, capture_output=True, timeout=150)
    for name, encoded in (('CIERRE_STOP_STDOUT.json', stopped.stdout), ('CIERRE_STOP_STDERR.txt', stopped.stderr)):
        with (OUT / name).open('xb') as stream:
            stream.write(encoded)
    code = wintypes.DWORD()
    K.GetExitCodeProcess(owner, ctypes.byref(code))
    before = pc.job_resources(job)
    forced = code.value == 259
    if forced:
        pc.terminate_job(job, 124)
    K.WaitForSingleObject(owner, 10000)
    K.GetExitCodeProcess(owner, ctypes.byref(code))
    resources = pc.job_resources(job)
    until = time.monotonic() + 10
    while resources.get('job_active_processes') and time.monotonic() < until:
        time.sleep(.05)
        resources = pc.job_resources(job)
    # Prevent any queued next block or a second STOP from the paused plan.
    if not K.TerminateProcess(driver, 125):
        raise ctypes.WinError(ctypes.get_last_error())
    K.WaitForSingleObject(driver, 10000)
    driver_code = wintypes.DWORD()
    K.GetExitCodeProcess(driver, ctypes.byref(driver_code))
    with sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True) as connection:
        connection.row_factory = sqlite3.Row
        rows = [dict(row) for row in connection.execute(
            'select id,status,started_utc,finished_utc,payload,error from requests where id like ? order by seq',
            ('apd04_attention_C_%',))]
    write('CIERRE_REASIGNACION_ROOT.json', {'Root_decision_utc': '2026-10-26T21:32:41+00:00',
        'closed_utc': datetime.now(timezone.utc).isoformat(), 'one_STOP_id': ID,
        'driver_exit_code_by_explicit_budget_close': int(driver_code.value),
        'owner_launcher_exit_code': int(code.value), 'owner_Job_terminated_for_budget': forced,
        'owner_resources_before_close': before, 'owner_resources_after_close': resources,
        'transport_rows_read_only_after_close': rows, 'STOP_process_return_code': stopped.returncode,
        'owner_closed_confirmed': not resources.get('job_active_processes'),
        'no_cognitive_failure_verdict': True, 'no_kernel_or_snapshot_edit': True})
    for handle in (driver, owner, job):
        K.CloseHandle(handle)
    print(json.dumps({'owner_closed_confirmed': not resources.get('job_active_processes'),
        'owner_exit_code': int(code.value), 'forced_budget_close': forced,
        'driver_exit_code': int(driver_code.value), 'resources': resources}, indent=2))


if __name__ == '__main__':
    main()
