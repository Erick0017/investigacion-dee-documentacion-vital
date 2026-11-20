"""CPC8 finite original budget, named two-slot semaphore and bounded owned jobs."""
from __future__ import annotations
import argparse
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
BUDGET = json.loads((ROOT / 'BUDGET.json').read_text(encoding='utf-8-sig'))
K = ctypes.WinDLL('kernel32', use_last_error=True)
SIZE_T = ctypes.c_size_t
ULONG_PTR = ctypes.c_size_t

class BASIC_LIMIT(ctypes.Structure):
    _fields_ = [('PerProcessUserTimeLimit',ctypes.c_longlong),('PerJobUserTimeLimit',ctypes.c_longlong),
        ('LimitFlags',wintypes.DWORD),('MinimumWorkingSetSize',SIZE_T),('MaximumWorkingSetSize',SIZE_T),
        ('ActiveProcessLimit',wintypes.DWORD),('Affinity',ULONG_PTR),('PriorityClass',wintypes.DWORD),('SchedulingClass',wintypes.DWORD)]

class IO_COUNTERS(ctypes.Structure):
    _fields_ = [(n,ctypes.c_ulonglong) for n in ('ReadOperationCount','WriteOperationCount','OtherOperationCount','ReadTransferCount','WriteTransferCount','OtherTransferCount')]

class EXTENDED_LIMIT(ctypes.Structure):
    _fields_ = [('BasicLimitInformation',BASIC_LIMIT),('IoInfo',IO_COUNTERS),('ProcessMemoryLimit',SIZE_T),
        ('JobMemoryLimit',SIZE_T),('PeakProcessMemoryUsed',SIZE_T),('PeakJobMemoryUsed',SIZE_T)]

class MEMORY(ctypes.Structure):
    _fields_ = [('dwLength',wintypes.DWORD),('dwMemoryLoad',wintypes.DWORD)] + [(n,ctypes.c_ulonglong) for n in
        ('ullTotalPhys','ullAvailPhys','ullTotalPageFile','ullAvailPageFile','ullTotalVirtual','ullAvailVirtual','ullAvailExtendedVirtual')]

K.CreateJobObjectW.argtypes=[ctypes.c_void_p,wintypes.LPCWSTR];K.CreateJobObjectW.restype=wintypes.HANDLE
K.SetInformationJobObject.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD]
K.QueryInformationJobObject.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD,ctypes.c_void_p]
K.AssignProcessToJobObject.argtypes=[wintypes.HANDLE,wintypes.HANDLE]
K.TerminateJobObject.argtypes=[wintypes.HANDLE,wintypes.UINT]
K.CloseHandle.argtypes=[wintypes.HANDLE]
K.CreateSemaphoreW.argtypes=[ctypes.c_void_p,wintypes.LONG,wintypes.LONG,wintypes.LPCWSTR];K.CreateSemaphoreW.restype=wintypes.HANDLE
K.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD]
K.ReleaseSemaphore.argtypes=[wintypes.HANDLE,wintypes.LONG,ctypes.c_void_p]

def remaining():
    q = ctypes.c_longlong()
    if not K.QueryPerformanceCounter(ctypes.byref(q)):
        raise ctypes.WinError(ctypes.get_last_error())
    elapsed = (q.value - BUDGET['start_qpc']) / BUDGET['qpc_frequency']
    wall_left = (datetime.fromisoformat(BUDGET['deadline_utc']) - datetime.now(timezone.utc)).total_seconds()
    return min(BUDGET['budget_seconds'] - elapsed, wall_left)

def put(path, data):
    path = Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    temp = path.with_name(path.name + '.pending.' + str(os.getpid()))
    temp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    os.replace(temp,path)

def free_memory():
    m = MEMORY();m.dwLength=ctypes.sizeof(m)
    if not K.GlobalMemoryStatusEx(ctypes.byref(m)):
        raise ctypes.WinError(ctypes.get_last_error())
    return m.ullAvailPhys

def run(name, argv, timeout=900, cwd=None, native=True, closing=False):
    reserve = 0 if closing else BUDGET['closing_reserve_seconds']
    available = remaining()-reserve
    if available <= 0:
        raise TimeoutError('Original campaign closing reserve reached; experiment not launched')
    target=ROOT/'jobs'/name;target.mkdir(parents=True,exist_ok=False)
    sem=None;job=None;process=None;acquired=False;started=time.monotonic()
    record={'name':name,'argv':[str(x) for x in argv],'cwd':str(cwd or ROOT),'started_utc':datetime.now(timezone.utc).isoformat(),
        'timeout_seconds':min(float(timeout),available),'memory_limit_bytes':BUDGET['worker_default_memory_limit_bytes'],
        'native_slot_required':native,'status':'STARTING','remaining_seconds':remaining()}
    try:
        if native:
            sem=K.CreateSemaphoreW(None,2,2,'Local\\DEE_CPC8_20261018_204718_NATIVE_SLOTS')
            if not sem:raise ctypes.WinError(ctypes.get_last_error())
            wait=K.WaitForSingleObject(sem,60000)
            if wait!=0:raise TimeoutError('No free global native slot within60seconds; no worker launched')
            acquired=True
            record['free_RAM_before_launch']=free_memory()
            if record['free_RAM_before_launch']<BUDGET['minimum_free_physical_bytes_before_launch']:
                raise MemoryError('Physical RAM reserve insufficient; no worker launched')
        job=K.CreateJobObjectW(None,None)
        if not job:raise ctypes.WinError(ctypes.get_last_error())
        limits=EXTENDED_LIMIT()
        limits.BasicLimitInformation.LimitFlags=0x2000|0x100|0x200
        limits.ProcessMemoryLimit=record['memory_limit_bytes'];limits.JobMemoryLimit=record['memory_limit_bytes']
        if not K.SetInformationJobObject(job,9,ctypes.byref(limits),ctypes.sizeof(limits)):
            raise ctypes.WinError(ctypes.get_last_error())
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
        env.pop('PYTHONPATH',None)
        with (target/'stdout.log').open('w',encoding='utf-8') as out,(target/'stderr.log').open('w',encoding='utf-8') as err:
            process=subprocess.Popen([str(x) for x in argv],cwd=str(cwd or ROOT),env=env,stdout=out,stderr=err,
                creationflags=subprocess.CREATE_NO_WINDOW)
            record['pid']=process.pid
            if not K.AssignProcessToJobObject(job,wintypes.HANDLE(int(process._handle))):
                process.kill();process.wait(timeout=30)
                raise ctypes.WinError(ctypes.get_last_error())
            record['status']='RUNNING';put(target/'START.json',record)
            try:
                process.wait(timeout=min(record['timeout_seconds'],max(1,remaining()-reserve)))
                record['status']='COMPLETED'
            except subprocess.TimeoutExpired:
                record['status']='TIMEOUT'
                K.TerminateJobObject(job,124);process.wait(timeout=30)
                record['terminated_owned_job']=True
            record['exit_code']=process.returncode;record['owned_worker_waited']=True
        peak=EXTENDED_LIMIT()
        if K.QueryInformationJobObject(job,9,ctypes.byref(peak),ctypes.sizeof(peak),None):
            record['peak_job_memory_bytes']=peak.PeakJobMemoryUsed
            record['peak_process_memory_bytes']=peak.PeakProcessMemoryUsed
    except BaseException as error:
        if process is not None and process.poll() is None:
            if job:K.TerminateJobObject(job,125)
            else:process.kill()
            process.wait(timeout=30)
            record['owned_worker_waited']=True;record['exit_code']=process.returncode
        record['status']='RESOURCE_BLOCKED' if isinstance(error,(MemoryError,TimeoutError)) and process is None else 'ERROR'
        record['error']=repr(error)
    finally:
        if job:
            K.CloseHandle(job);record['owned_job_closed']=True;record['kill_on_job_close']=True
        if acquired:K.ReleaseSemaphore(sem,1,None)
        if sem:K.CloseHandle(sem)
        record['elapsed_seconds']=time.monotonic()-started
        record['remaining_seconds']=remaining()
        record['finished_utc']=datetime.now(timezone.utc).isoformat()
        put(target/'COMMAND.json',record)
    print(json.dumps(record,ensure_ascii=False),flush=True)
    return record

def main():
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--timeout',type=int,default=900)
    p.add_argument('--non-native',action='store_true');p.add_argument('--closing',action='store_true')
    p.add_argument('argv',nargs=argparse.REMAINDER);a=p.parse_args()
    command=a.argv[1:] if a.argv[:1]==['--'] else a.argv
    r=run(a.name,command,a.timeout,native=not a.non_native,closing=a.closing)
    raise SystemExit(r.get('exit_code',125) if r['status']=='COMPLETED' else 124)

if __name__=='__main__':main()
