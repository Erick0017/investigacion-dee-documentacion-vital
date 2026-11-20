import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from supervision import run_child
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--name',required=True);p.add_argument('--timeout',type=float,default=240);p.add_argument('--cwd');p.add_argument('argv',nargs=argparse.REMAINDER);a=p.parse_args()
    arguments=a.argv[1:] if a.argv and a.argv[0]=='--' else a.argv
    result=run_child(a.root,a.name,arguments,a.timeout,cwd=a.cwd);print(result);raise SystemExit(0 if result['status']=='COMPLETED' else 1)
