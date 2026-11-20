"""Immutable four-hour budget and owned, process-isolated jobs for DEE4."""
import argparse,ctypes,json,os,subprocess,sys,time,uuid
from ctypes import wintypes
from pathlib import Path
from datetime import datetime,timezone
ctypes.windll.kernel32.GetTickCount64.restype=ctypes.c_uint64
class _BasicLimits(ctypes.Structure):
    _fields_=[('ProcessTime',ctypes.c_int64),('JobTime',ctypes.c_int64),('Flags',wintypes.DWORD),('MinWS',ctypes.c_size_t),('MaxWS',ctypes.c_size_t),('Active',wintypes.DWORD),('Affinity',ctypes.c_size_t),('Priority',wintypes.DWORD),('Scheduling',wintypes.DWORD)]
class _IOCounters(ctypes.Structure):
    _fields_=[(name,ctypes.c_uint64) for name in ('ReadOps','WriteOps','OtherOps','ReadBytes','WriteBytes','OtherBytes')]
class _ExtendedLimits(ctypes.Structure):
    _fields_=[('Basic',_BasicLimits),('IO',_IOCounters),('ProcessMemory',ctypes.c_size_t),('JobMemory',ctypes.c_size_t),('PeakProcess',ctypes.c_size_t),('PeakJob',ctypes.c_size_t)]
def owned_job(process):
    """A new Windows job owns only this live child and descendants, no PID scan."""
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.CreateJobObjectW.argtypes=[ctypes.c_void_p,wintypes.LPCWSTR];k.CreateJobObjectW.restype=wintypes.HANDLE
    k.SetInformationJobObject.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD];k.SetInformationJobObject.restype=wintypes.BOOL
    k.AssignProcessToJobObject.argtypes=[wintypes.HANDLE,wintypes.HANDLE];k.AssignProcessToJobObject.restype=wintypes.BOOL
    k.CloseHandle.argtypes=[wintypes.HANDLE];k.CloseHandle.restype=wintypes.BOOL
    k.TerminateJobObject.argtypes=[wintypes.HANDLE,wintypes.UINT];k.TerminateJobObject.restype=wintypes.BOOL
    handle=k.CreateJobObjectW(None,None)
    if not handle:return None,{'assigned':False,'error':ctypes.get_last_error()}
    limits=_ExtendedLimits();limits.Basic.Flags=0x2000 # KILL_ON_JOB_CLOSE
    if not k.SetInformationJobObject(handle,9,ctypes.byref(limits),ctypes.sizeof(limits)) or not k.AssignProcessToJobObject(handle,wintypes.HANDLE(int(process._handle))):
        error=ctypes.get_last_error();k.CloseHandle(handle);return None,{'assigned':False,'error':error}
    return (k,handle),{'assigned':True,'kill_on_close':True,'scope':'live owned Popen child and descendants'}
def put(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix('.'+uuid.uuid4().hex+'.tmp');q.write_text(json.dumps(x,indent=2,default=str),encoding='utf-8');os.replace(q,p)
def budget_path(root):
    root=Path(root);active=root/'ACTIVE_BUDGET.json'
    if active.exists():
        name=json.loads(active.read_text())['record']
        if Path(name).name!=name:raise ValueError('budget record must be local basename')
        return root/name
    return root/'BUDGET.json'
def remaining(root):
    x=json.loads(budget_path(root).read_text());return max(0,min((datetime.fromisoformat(x['deadline_utc'])-datetime.now(timezone.utc)).total_seconds(),(x['monotonic_deadline_ms']-int(ctypes.windll.kernel32.GetTickCount64()))/1000))
def run(root,name,argv,timeout=600,cwd=None):
    root=Path(root);folder=root/'jobs'/name;folder.mkdir(parents=True,exist_ok=False);budget=min(timeout,remaining(root)-1200)
    if budget<=0:raise TimeoutError('Global budget closure reserve')
    with (folder/'stdout.log').open('w',encoding='utf-8') as out,(folder/'stderr.log').open('w',encoding='utf-8') as err:
        p=subprocess.Popen(argv,cwd=cwd,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW);job,job_info=owned_job(p);started=time.monotonic();row={'name':name,'pid':p.pid,'argv':argv,'cwd':cwd,'status':'RUNNING','timeout':budget,'start_utc':datetime.now(timezone.utc).isoformat(),'owned_windows_job':job_info};put(folder/'job.json',row)
        while p.poll() is None:
            if time.monotonic()-started>=budget or remaining(root)<1200:
                # This is the live owned Popen handle, not a recycled ledger PID.
                if job:job[0].TerminateJobObject(job[1],124)
                else:p.kill()
                break
            time.sleep(.2)
        p.wait(timeout=20)
        if job:job[0].CloseHandle(job[1])
        row.update(status='COMPLETED' if p.returncode==0 else 'ERROR',exit_code=p.returncode,elapsed=time.monotonic()-started);put(folder/'job.json',row);return row
def guard(root):
    root=Path(root);active=root/'ACTIVE_BUDGET.json';marker=json.loads(active.read_text()).get('closed_marker','CLOSED.json') if active.exists() else 'CLOSED.json';guard_name='GUARD_RESUMPTION.json' if active.exists() else 'GUARD.json';put(root/guard_name,{'pid':os.getpid(),'status':'ACTIVE','budget_record':str(budget_path(root))})
    while remaining(root)>1200 and not (root/marker).exists():time.sleep(1)
    # Every job supervisor owns its exact child handle. Never kill by name/PID
    # read from an old ledger; no action against unrelated processes.
    put(root/guard_name,{'pid':os.getpid(),'status':'CLOSED' if (root/marker).exists() else 'DEADLINE_CLOSE','remaining':remaining(root)})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--guard',action='store_true');p.add_argument('--name');p.add_argument('--timeout',type=int,default=600);p.add_argument('--cwd');p.add_argument('argv',nargs=argparse.REMAINDER);a=p.parse_args()
    if a.guard:guard(a.root)
    else:
        args=a.argv[1:] if a.argv and a.argv[0]=='--' else a.argv;r=run(a.root,a.name,args,a.timeout,a.cwd);print(json.dumps(r));raise SystemExit(r['exit_code'])
