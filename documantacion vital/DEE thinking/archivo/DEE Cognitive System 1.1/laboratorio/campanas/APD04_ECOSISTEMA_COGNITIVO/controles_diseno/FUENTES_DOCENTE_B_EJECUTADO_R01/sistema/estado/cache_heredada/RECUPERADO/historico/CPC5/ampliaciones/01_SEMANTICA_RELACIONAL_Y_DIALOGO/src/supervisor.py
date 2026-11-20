"""Reuse the frozen owned-process supervisor with this extension's fixed budget."""
import importlib.util
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
BASE=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('cpc5_frozen_supervisor',BASE/'src/supervisor.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.ROOT=ROOT
run=module.run
remaining=module.remaining
put=module.put
sha=module.sha

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--name',required=True)
    parser.add_argument('--timeout',type=int,default=600)
    parser.add_argument('--closing',action='store_true')
    parser.add_argument('argv',nargs=argparse.REMAINDER)
    args=parser.parse_args()
    command=args.argv[1:] if args.argv[:1]==['--'] else args.argv
    result=run(args.name,command,args.timeout,reserve=0 if args.closing else 1200)
    raise SystemExit(result['exit_code'])
