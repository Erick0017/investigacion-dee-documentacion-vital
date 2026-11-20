"""Command-line adapter to the original CPC3 process supervisor."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from supervise import run_job
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--line',default='experimentos');p.add_argument('--name',required=True);p.add_argument('--timeout',type=float,default=180);p.add_argument('--cwd');p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
argv=a.command[1:] if a.command and a.command[0]=='--' else a.command
if not argv:p.error('child command required')
r=run_job(a.root,a.line,a.name,argv,timeout=a.timeout,cwd=a.cwd)
print(json.dumps(r,indent=2));raise SystemExit(0 if r['status']=='COMPLETED' else 1)
