"""Immutable four-hour budget and owned, process-isolated jobs for DEE4."""
import argparse,ctypes,json,os,subprocess,sys,time,uuid
from pathlib import Path
from datetime import datetime,timezone
ctypes.windll.kernel32.GetTickCount64.restype=ctypes.c_uint64
def put(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix('.'+uuid.uuid4().hex+'.tmp');q.write_text(json.dumps(x,indent=2,default=str),encoding='utf-8');os.replace(q,p)
def remaining(root):
    x=json.loads((Path(root)/'BUDGET.json').read_text());return max(0,min((datetime.fromisoformat(x['deadline_utc'])-datetime.now(timezone.utc)).total_seconds(),(x['monotonic_deadline_ms']-int(ctypes.windll.kernel32.GetTickCount64()))/1000))
def run(root,name,argv,timeout=600,cwd=None):
    root=Path(root);folder=root/'jobs'/name;folder.mkdir(parents=True,exist_ok=False);budget=min(timeout,remaining(root)-600)
    if budget<=0:raise TimeoutError('Global budget closure reserve')
    with (folder/'stdout.log').open('w',encoding='utf-8') as out,(folder/'stderr.log').open('w',encoding='utf-8') as err:
        p=subprocess.Popen(argv,cwd=cwd,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW);started=time.monotonic();row={'name':name,'pid':p.pid,'argv':argv,'cwd':cwd,'status':'RUNNING','timeout':budget,'start_utc':datetime.now(timezone.utc).isoformat()};put(folder/'job.json',row)
        while p.poll() is None:
            if time.monotonic()-started>=budget or remaining(root)<600:
                subprocess.run(['taskkill.exe','/PID',str(p.pid),'/T','/F'],capture_output=True,timeout=20);break
            time.sleep(.2)
        p.wait(timeout=20);row.update(status='COMPLETED' if p.returncode==0 else 'ERROR',exit_code=p.returncode,elapsed=time.monotonic()-started);put(folder/'job.json',row);return row
def guard(root):
    root=Path(root);put(root/'GUARD.json',{'pid':os.getpid(),'status':'ACTIVE'})
    while remaining(root)>600 and not (root/'CLOSED.json').exists():time.sleep(1)
    # Every job supervisor owns its exact child handle. Never kill by name/PID
    # read from an old ledger; no action against unrelated processes.
    put(root/'GUARD.json',{'pid':os.getpid(),'status':'CLOSED' if (root/'CLOSED.json').exists() else 'DEADLINE_CLOSE','remaining':remaining(root)})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--guard',action='store_true');p.add_argument('--name');p.add_argument('--timeout',type=int,default=600);p.add_argument('--cwd');p.add_argument('argv',nargs=argparse.REMAINDER);a=p.parse_args()
    if a.guard:guard(a.root)
    else:
        args=a.argv[1:] if a.argv and a.argv[0]=='--' else a.argv;r=run(a.root,a.name,args,a.timeout,a.cwd);print(json.dumps(r));raise SystemExit(r['exit_code'])
