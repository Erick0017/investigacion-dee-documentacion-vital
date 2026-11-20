"""CP02 only: immutable global budget, isolated native jobs and benchmark exclusion."""
import contextlib
import ctypes
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid


def monotonic_ms():
    k=ctypes.WinDLL('kernel32');k.GetTickCount64.restype=ctypes.c_ulonglong;return int(k.GetTickCount64())


def atomic_json(path,obj):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
    tmp.write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding='utf-8');os.replace(tmp,p)


class Budget:
    def __init__(self,root):
        self.root=Path(root).resolve();self.data=json.loads((self.root/'compartido/BUDGET.json').read_text(encoding='utf-8-sig'))
    def elapsed(self):
        n=monotonic_ms();assert n>=self.data['monotonic_start_ms'],'Monotonic clock reboot; do not reset original budget'
        return (n-self.data['monotonic_start_ms'])/1000
    def remaining(self):
        wall=(datetime.fromisoformat(self.data['deadline_utc'])-datetime.now(timezone.utc)).total_seconds()
        return max(0,min(wall,(self.data['monotonic_deadline_ms']-monotonic_ms())/1000))


def creation_time(handle):
    class FT(ctypes.Structure):_fields_=[('lo',ctypes.c_ulong),('hi',ctypes.c_ulong)]
    vs=[FT() for _ in range(4)];k=ctypes.WinDLL('kernel32');k.GetProcessTimes.argtypes=[ctypes.c_void_p,*([ctypes.POINTER(FT)]*4)]
    if not k.GetProcessTimes(handle,*[ctypes.byref(v) for v in vs]):return None
    return (vs[0].hi<<32)|vs[0].lo


def stop_child(p):
    if p.poll() is not None:return
    subprocess.run(['taskkill.exe','/PID',str(p.pid),'/T','/F'],capture_output=True,timeout=15)
    try:p.wait(timeout=5)
    except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)


def stop_registered(task):
    pid=task.get('pid');k=ctypes.WinDLL('kernel32');k.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong];k.OpenProcess.restype=ctypes.c_void_p;k.CloseHandle.argtypes=[ctypes.c_void_p]
    h=k.OpenProcess(0x1000,False,pid) if pid else None
    if not h:return False
    same=creation_time(h)==task.get('creation_filetime');k.CloseHandle(h)
    if not same:return False
    subprocess.run(['taskkill.exe','/PID',str(pid),'/T','/F'],capture_output=True,timeout=15);return True


@contextlib.contextmanager
def dispatch(root):
    root=Path(root);lock=root/'compartido/DISPATCH.lock';end=time.monotonic()+15
    while True:
        try:fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);break
        except FileExistsError:
            if time.monotonic()>end:raise TimeoutError('Bounded dispatch lock wait exceeded')
            time.sleep(.1)
    try:os.write(fd,str(os.getpid()).encode());os.close(fd);yield
    finally:lock.unlink(missing_ok=True)


@contextlib.contextmanager
def benchmark_window(root,line):
    """No new other-line native job starts; wait for any existing one to finish."""
    root=Path(root);b=Budget(root);lock=root/'compartido/BENCHMARK.json'
    with dispatch(root):
        if lock.exists():raise RuntimeError('Another benchmark window already reserved')
        atomic_json(lock,{'line':line,'owner_pid':os.getpid(),'started_utc':datetime.now(timezone.utc).isoformat()})
    try:
        while True:
            active=[]
            for p in (root/'compartido/ACTIVE').glob('*.json'):
                x=json.loads(p.read_text(encoding='utf-8'))
                if x.get('status')=='RUNNING' and x.get('line')!=line:active.append(x)
            if not active:break
            if b.remaining()<1000:raise TimeoutError('No remaining benchmark reserve')
            time.sleep(.2)
        yield {'other_line_native_jobs':0,'exclusive_benchmark_window':True}
    finally:lock.unlink(missing_ok=True)


def run_job(root,line,name,argv,timeout=180,kind='native_experiment',cwd=None,reserve=900):
    root=Path(root).resolve();b=Budget(root);logs=root/line/'supervision';logs.mkdir(parents=True,exist_ok=True)
    original=name;attempt=1
    while (logs/(name+'.json')).exists():attempt+=1;name=original+'_attempt'+str(attempt)
    maximum=min(timeout,b.remaining()-reserve)
    if maximum<=0:
        r={'line':line,'name':name,'status':'NO_EJECUTADO_POR_PRESUPUESTO','argv':list(map(str,argv))};atomic_json(logs/(name+'.json'),r);return r
    active_dir=root/'compartido/ACTIVE';active_dir.mkdir(exist_ok=True);ap=active_dir/(line+'_'+uuid.uuid4().hex+'.json');started=time.monotonic()
    outp=logs/(name+'.stdout.log');errp=logs/(name+'.stderr.log')
    with outp.open('w',encoding='utf-8') as out,errp.open('w',encoding='utf-8') as err:
        while True:
            with dispatch(root):
                lock=root/'compartido/BENCHMARK.json'
                owner=json.loads(lock.read_text(encoding='utf-8'))['line'] if lock.exists() else None
                if owner is None or owner==line:
                    p=subprocess.Popen(list(map(str,argv)),cwd=str(cwd or root/line),stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
                    active={'line':line,'name':name,'kind':kind,'pid':p.pid,'creation_filetime':creation_time(int(p._handle)),'status':'RUNNING','argv':list(map(str,argv)),'timeout_seconds':maximum,'started_utc':datetime.now(timezone.utc).isoformat()};atomic_json(ap,active);break
            if b.remaining()<=reserve:raise TimeoutError('Benchmark wait exhausted global reserve')
            time.sleep(.2)
        run_started=time.monotonic();timed=False
        while p.poll() is None:
            if time.monotonic()-run_started>=maximum or b.remaining()<=reserve:timed=True;stop_child(p);break
            time.sleep(.2)
    result={**active,'status':'TIMEOUT' if timed else 'COMPLETED' if p.returncode==0 else 'TECHNICAL_ERROR','exit_code':p.returncode,'attempt':attempt,'duration_seconds':time.monotonic()-run_started,
            'queue_seconds':run_started-started,'elapsed_campaign_seconds':b.elapsed(),'timed_out':timed,'cwd':str(cwd or root/line),'stdout':str(outp.relative_to(root)),'stderr':str(errp.relative_to(root))}
    atomic_json(ap,result);atomic_json(logs/(name+'.json'),result);return result
