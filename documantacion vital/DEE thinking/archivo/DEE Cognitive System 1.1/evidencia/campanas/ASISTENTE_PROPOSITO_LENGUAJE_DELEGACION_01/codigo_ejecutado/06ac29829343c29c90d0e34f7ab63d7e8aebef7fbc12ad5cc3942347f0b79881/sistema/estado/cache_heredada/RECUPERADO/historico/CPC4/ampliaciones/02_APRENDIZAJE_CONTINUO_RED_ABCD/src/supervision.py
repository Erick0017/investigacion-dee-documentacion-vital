"""Campaign-local supervision; reuse the audited owned-process primitive only."""
from pathlib import Path
import argparse, ctypes, importlib.util, json, time, os
os.environ['PYTHONDONTWRITEBYTECODE']='1'

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT.parents[1]
spec = importlib.util.spec_from_file_location('cpc4_owned_supervision', PARENT / 'supervise.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

def budget_path(root):
    return Path(root) / 'BUDGET.json'

def remaining(root=ROOT):
    from datetime import datetime, timezone
    b = json.loads(budget_path(root).read_text(encoding='utf-8-sig'))
    counter=ctypes.windll.kernel32.GetTickCount64;counter.restype=ctypes.c_ulonglong
    return max(0, min((datetime.fromisoformat(b['deadline_utc'])-datetime.now(timezone.utc)).total_seconds(),
                      (b['monotonic_deadline_ms']-int(counter()))/1000))

base.remaining = remaining
base.budget_path = budget_path
run = base.run
owned_job = base.owned_job
put = base.put

def guard():
    base.put(ROOT/'GUARD.json', {'status':'ACTIVE', 'scope':'this campaign owned jobs only', 'remaining':remaining()})
    while remaining()>1200 and not (ROOT/'CLOSED.json').exists():
        time.sleep(1)
    base.put(ROOT/'GUARD.json', {'status':'CLOSED' if (ROOT/'CLOSED.json').exists() else 'DEADLINE_CLOSE', 'remaining':remaining()})

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--guard',action='store_true');p.add_argument('--name');p.add_argument('--timeout',type=int,default=600);p.add_argument('argv',nargs=argparse.REMAINDER);a=p.parse_args()
    if a.guard: guard()
    else:
        args=a.argv[1:] if a.argv and a.argv[0]=='--' else a.argv
        r=run(ROOT,a.name,args,a.timeout,cwd=str(ROOT));print(json.dumps(r));raise SystemExit(r['exit_code'])
