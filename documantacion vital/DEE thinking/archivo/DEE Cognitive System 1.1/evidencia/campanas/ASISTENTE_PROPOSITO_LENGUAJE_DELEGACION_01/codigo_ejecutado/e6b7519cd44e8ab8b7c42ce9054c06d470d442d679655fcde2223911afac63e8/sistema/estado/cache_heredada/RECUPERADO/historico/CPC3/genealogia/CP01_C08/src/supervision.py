"""Bounded child-process supervision using the single campaign monotonic budget."""
import ctypes
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def monotonic_ms():
    k=ctypes.WinDLL('kernel32');k.GetTickCount64.restype=ctypes.c_ulonglong
    return int(k.GetTickCount64())


def atomic_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.tmp');tmp.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8');os.replace(tmp,path)


class Budget:
    def __init__(self,root):
        self.root=Path(root).resolve();self.data=json.loads((self.root/'CAMPAIGN_BUDGET.json').read_text(encoding='utf-8-sig'))
    def elapsed(self):
        now=monotonic_ms()
        if now<self.data['monotonic_start_ms']:raise RuntimeError('Host reboot changed monotonic origin; original deadline must not be reset')
        return (now-self.data['monotonic_start_ms'])/1000
    def remaining(self):
        wall=(datetime.fromisoformat(self.data['deadline_utc'])-datetime.now(timezone.utc)).total_seconds()
        return max(0,min((self.data['monotonic_deadline_ms']-monotonic_ms())/1000,wall))


def stop_own_tree(process):
    if process.poll() is not None:return
    subprocess.run(['taskkill.exe','/PID',str(process.pid),'/T','/F'],capture_output=True,text=True)
    try:process.wait(timeout=10)
    except subprocess.TimeoutExpired:process.kill();process.wait(timeout=10)


def creation_time(handle):
    class FT(ctypes.Structure):_fields_=[('lo',ctypes.c_ulong),('hi',ctypes.c_ulong)]
    values=[FT() for _ in range(4)];k=ctypes.WinDLL('kernel32');k.GetProcessTimes.argtypes=[ctypes.c_void_p,*([ctypes.POINTER(FT)]*4)]
    if not k.GetProcessTimes(handle,*[ctypes.byref(v) for v in values]):return None
    return (values[0].hi<<32)|values[0].lo


def run_child(root,name,argv,timeout=240,reserve=900,cwd=None):
    root=Path(root).resolve();budget=Budget(root);logs=root/'resultados/supervision';logs.mkdir(parents=True,exist_ok=True)
    limit=min(float(timeout),budget.remaining()-reserve)
    if limit<=0:
        record={'name':name,'status':'NO_EJECUTADO_POR_PRESUPUESTO','argv':list(map(str,argv)),'elapsed_campaign_seconds':budget.elapsed()}
        atomic_json(logs/(name+'.json'),record);return record
    original=name;attempt=1
    while (logs/(name+'.json')).exists():attempt+=1;name=original+'_attempt'+str(attempt)
    stdout=logs/(name+'.stdout.log');stderr=logs/(name+'.stderr.log');start=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    with stdout.open('w',encoding='utf-8') as out,stderr.open('w',encoding='utf-8') as err:
        p=subprocess.Popen(list(map(str,argv)),cwd=str(cwd or root),stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
        atomic_json(root/'resultados/ACTIVE_TASK.json',{'name':name,'pid':p.pid,'parent_pid':os.getpid(),'creation_filetime':creation_time(int(p._handle)),'started_utc':started,'timeout_seconds':limit,'argv':list(map(str,argv))})
        timed_out=False
        while p.poll() is None:
            if time.monotonic()-start>=limit or budget.remaining()<=reserve:
                timed_out=True;stop_own_tree(p);break
            time.sleep(.2)
        record={'name':name,'attempt':attempt,'pid':p.pid,'argv':list(map(str,argv)),'cwd':str(cwd or root),'started_utc':started,'duration_seconds':time.monotonic()-start,
                'elapsed_campaign_seconds':budget.elapsed(),'exit_code':p.returncode,'timed_out':timed_out,'status':'TIMEOUT' if timed_out else 'COMPLETED' if p.returncode==0 else 'TECHNICAL_ERROR',
                'stdout':str(stdout.relative_to(root)),'stderr':str(stderr.relative_to(root))}
    atomic_json(logs/(name+'.json'),record);atomic_json(root/'resultados/ACTIVE_TASK.json',{'status':'IDLE','last_task':name,'owned_child_stopped':True})
    return record


def launch_guard(root):
    root=Path(root).resolve();p=subprocess.Popen([sys.executable,'-I','-B',str(Path(__file__).with_name('deadline_guard.py')),'--root',str(root)],cwd=root,creationflags=subprocess.CREATE_NO_WINDOW)
    atomic_json(root/'resultados/SUPERVISOR.json',{'pid':p.pid,'parent_pid':os.getpid(),'deadline_utc':Budget(root).data['deadline_utc'],'status':'RUNNING','scope':'owned campaign children only; monotonic global deadline; no automatic restart'})
    return p.pid
