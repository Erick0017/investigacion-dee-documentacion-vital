"""Windows owned-job limits and actual worker resource accounting.

venv python.exe may be a waiting launcher; its working set is not the native
worker's memory. This module measures the job tree and the actual PythonPID.
No scientific field or clock is changed.
"""
import atexit,ctypes,json,os,sys,time,uuid
import hashlib,subprocess
from ctypes import wintypes
from pathlib import Path

K=ctypes.WinDLL('kernel32',use_last_error=True)
class Basic(ctypes.Structure):
    _fields_=[('PerProcessUserTimeLimit',ctypes.c_longlong),('PerJobUserTimeLimit',ctypes.c_longlong),('LimitFlags',wintypes.DWORD),('MinimumWorkingSetSize',ctypes.c_size_t),('MaximumWorkingSetSize',ctypes.c_size_t),('ActiveProcessLimit',wintypes.DWORD),('Affinity',ctypes.c_size_t),('PriorityClass',wintypes.DWORD),('SchedulingClass',wintypes.DWORD)]
class IO(ctypes.Structure):
    _fields_=[(n,ctypes.c_ulonglong)for n in('ReadOperationCount','WriteOperationCount','OtherOperationCount','ReadTransferCount','WriteTransferCount','OtherTransferCount')]
class Extended(ctypes.Structure):
    _fields_=[('BasicLimitInformation',Basic),('IoInfo',IO),('ProcessMemoryLimit',ctypes.c_size_t),('JobMemoryLimit',ctypes.c_size_t),('PeakProcessMemoryUsed',ctypes.c_size_t),('PeakJobMemoryUsed',ctypes.c_size_t)]
class Accounting(ctypes.Structure):
    _fields_=[('TotalUserTime',ctypes.c_longlong),('TotalKernelTime',ctypes.c_longlong),('ThisPeriodTotalUserTime',ctypes.c_longlong),('ThisPeriodTotalKernelTime',ctypes.c_longlong),('TotalPageFaultCount',wintypes.DWORD),('TotalProcesses',wintypes.DWORD),('ActiveProcesses',wintypes.DWORD),('TotalTerminatedProcesses',wintypes.DWORD)]
class Memory(ctypes.Structure):
    _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(n,ctypes.c_size_t)for n in('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage')]
K.CreateJobObjectW.argtypes=[ctypes.c_void_p,wintypes.LPCWSTR];K.CreateJobObjectW.restype=wintypes.HANDLE
K.OpenJobObjectW.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.LPCWSTR];K.OpenJobObjectW.restype=wintypes.HANDLE
K.GetCurrentProcess.restype=wintypes.HANDLE
K.SetInformationJobObject.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD]
K.QueryInformationJobObject.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD,ctypes.c_void_p]
K.AssignProcessToJobObject.argtypes=[wintypes.HANDLE,wintypes.HANDLE]
K.IsProcessInJob.argtypes=[wintypes.HANDLE,wintypes.HANDLE,ctypes.POINTER(wintypes.BOOL)]
K.TerminateJobObject.argtypes=[wintypes.HANDLE,wintypes.UINT]
K.CloseHandle.argtypes=[wintypes.HANDLE]
PS=ctypes.WinDLL('psapi',use_last_error=True);PS.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.c_void_p,wintypes.DWORD]
_self_job=None

def new_job(name=None,memory_limit=4*1024**3):
    name=name or('Local\\DEE_DCS11_JOB_'+uuid.uuid4().hex);handle=K.CreateJobObjectW(None,name)
    if not handle:raise ctypes.WinError(ctypes.get_last_error())
    limits=Extended();limits.BasicLimitInformation.LimitFlags=0x2000|0x100|0x200;limits.ProcessMemoryLimit=memory_limit;limits.JobMemoryLimit=memory_limit
    if not K.SetInformationJobObject(handle,9,ctypes.byref(limits),ctypes.sizeof(limits)):
        error=ctypes.WinError(ctypes.get_last_error());K.CloseHandle(handle);raise error
    return handle,name

def job_resources(handle):
    m=Extended();a=Accounting();result={}
    if K.QueryInformationJobObject(handle,9,ctypes.byref(m),ctypes.sizeof(m),None):result.update(peak_job_committed_bytes=int(m.PeakJobMemoryUsed),peak_process_committed_bytes=int(m.PeakProcessMemoryUsed),job_memory_limit=int(m.JobMemoryLimit))
    if K.QueryInformationJobObject(handle,1,ctypes.byref(a),ctypes.sizeof(a),None):result.update(cpu_user_seconds=a.TotalUserTime/10000000,cpu_kernel_seconds=a.TotalKernelTime/10000000,job_total_processes=int(a.TotalProcesses),job_active_processes=int(a.ActiveProcesses))
    return result

def current_resources():
    m=Memory();m.cb=ctypes.sizeof(m);result={'actual_python_pid':os.getpid(),'parent_pid':os.getppid()}
    if PS.GetProcessMemoryInfo(K.GetCurrentProcess(),ctypes.byref(m),m.cb):result.update(actual_worker_peak_working_set_bytes=int(m.PeakWorkingSetSize),actual_worker_working_set_bytes=int(m.WorkingSetSize),actual_worker_private_bytes=int(m.PrivateUsage))
    if _self_job:result.update(job_resources(_self_job))
    return result

def protect_current(*,output=None,memory_limit=4*1024**3):
    global _self_job
    if _self_job:return current_resources()
    expected=os.environ.get('DCS_EXPECTED_JOB')
    if expected:
        outer=K.OpenJobObjectW(0x0004,False,expected)
        if not outer:raise RuntimeError('Expected parent-owned job is not accessible')
        flag=wintypes.BOOL();valid=K.IsProcessInJob(K.GetCurrentProcess(),outer,ctypes.byref(flag));K.CloseHandle(outer)
        if not valid or not flag.value:raise RuntimeError('Pythonworker escaped its launcher job; no native Runtime was created')
    _self_job,name=new_job(memory_limit=memory_limit)
    if not K.AssignProcessToJobObject(_self_job,K.GetCurrentProcess()):
        error=ctypes.WinError(ctypes.get_last_error());K.CloseHandle(_self_job);_self_job=None;raise error
    if output is None and'--out'in sys.argv:
        output=Path(sys.argv[sys.argv.index('--out')+1])/'RECURSOS_DEL_TRABAJADOR.json'
    if output:
        path=Path(output)
        entry=Path(sys.argv[0]);entry_sha=hashlib.sha256(entry.read_bytes()).hexdigest()if entry.is_file()else None
        module_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        def finish():
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(json.dumps({'schema':'DCS1.1.actual_worker_resources.v1','source':'Actual Python process and its owned native job, NOT the venv launcher','self_job_name':name,'parent_job_checked':expected,'memory_limit_bytes':memory_limit,'entrypoint_sha256_at_start':entry_sha,'resource_adapter_sha256_at_start':module_sha,**current_resources()},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        atexit.register(finish)
    return current_resources()

def assign_process(job,process):
    if not K.AssignProcessToJobObject(job,wintypes.HANDLE(int(process._handle))):raise ctypes.WinError(ctypes.get_last_error())
def terminate_job(job,code=124):
    if not K.TerminateJobObject(job,code):raise ctypes.WinError(ctypes.get_last_error())
def close_job(job):K.CloseHandle(job)

def spawn_owned(argv,*,cwd,stdout,stderr,memory_limit=4*1024**3):
    job,name=new_job(memory_limit=memory_limit);env=dict(os.environ,DCS_EXPECTED_JOB=name,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1');env.pop('PYTHONPATH',None)
    try:
        process=subprocess.Popen(argv,cwd=cwd,env=env,stdout=stdout,stderr=stderr,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));assign_process(job,process)
        return process,job,name
    except BaseException:
        terminate_job(job,125);close_job(job);raise
