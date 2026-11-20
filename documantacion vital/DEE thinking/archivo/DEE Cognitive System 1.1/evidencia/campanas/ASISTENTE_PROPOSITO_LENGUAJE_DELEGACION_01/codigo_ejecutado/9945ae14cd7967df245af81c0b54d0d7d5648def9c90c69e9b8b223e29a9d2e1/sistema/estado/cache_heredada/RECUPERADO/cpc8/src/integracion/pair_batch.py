"""Serial coordinator; every finite native child uses the new campaign supervisor."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2]


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--batch',required=True);p.add_argument('--cases',required=True);p.add_argument('--runner',choices=('run_pair.py','run_pair_v2.py'),default='run_pair.py');a=p.parse_args()
    for name in a.cases.split(','):
        out=ROOT/'resultados/integracion'/name
        if out.exists():raise FileExistsError('Existing case protected: '+str(out))
        command=[sys.executable,'-I','-B',str(ROOT/'tools/supervisor.py'),'--name','capacity_'+a.batch+'_'+name,'--timeout','300','--',sys.executable,'-I','-B',str(ROOT/'src/integracion'/a.runner),'--config',str(a.config.resolve()),'--case-id',name,'--out',str(out)]
        result=subprocess.run(command,cwd=ROOT,timeout=360,check=False)
        if result.returncode:raise SystemExit(result.returncode)


if __name__=='__main__':main()
