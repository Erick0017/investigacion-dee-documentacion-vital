"""Keep post-seal job logs OUTSIDE the immutable candidate, same original budget.

Not a new budget or a bypass of scientific job closure: the publisher checks all
scientific source jobs, and this ledger records its own finite delivery workers.
"""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import supervisor

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--log-root',required=True);p.add_argument('--name',required=True)
 p.add_argument('--timeout',type=float,default=900);p.add_argument('--native',action='store_true')
 p.add_argument('--cwd');p.add_argument('argv',nargs=argparse.REMAINDER);a=p.parse_args()
 original=supervisor.ROOT.resolve();out=Path(a.log_root).resolve()
 if out==original or out.is_relative_to(original):raise ValueError('Post-seal logs must be outside the candidate/source')
 argv=a.argv[1:] if a.argv and a.argv[0]=='--' else a.argv
 if not argv:raise ValueError('Missing owned command')
 supervisor.ROOT=out
 result=supervisor.run(a.name,argv,a.timeout,cwd=a.cwd,native=a.native,closing=True)
 print(json.dumps(result,ensure_ascii=False))
 return 0 if result.get('exit_code')==0 else 1
if __name__=='__main__':raise SystemExit(main())
