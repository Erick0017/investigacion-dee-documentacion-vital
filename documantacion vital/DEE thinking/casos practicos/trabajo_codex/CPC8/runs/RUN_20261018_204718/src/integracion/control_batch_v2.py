"""Bounded serial batch B; no engine imports or result-based design choices."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[2]


def put(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);temporary=path.with_name(path.name+'.pending.'+str(os.getpid()))
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8');os.replace(temporary,path)


def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);a=p.parse_args()
    config=json.loads(a.manifest.read_text(encoding='utf8'));batch=config['batch'];rows=[];started=time.monotonic()
    for task in config['tasks']:
        out=ROOT/'resultados/integracion'/task['id'];record=out/'MEASUREMENTS.json'
        if record.exists():
            previous=json.loads(record.read_text(encoding='utf8'))
            if previous.get('status')=='MEASURED':rows.append({'id':task['id'],'status':'EXISTING_COMPLETED_NOT_REEXECUTED'});continue
            raise RuntimeError('Incomplete target requires reconciliation: '+task['id'])
        command=[sys.executable,'-I','-B',str(ROOT/'src/integracion'/task['script']),'--config',str(ROOT/'configuraciones/integracion'/task['config']),'--case-id',task['id'],'--out',str(out)]
        if 'reference'in task:command+=['--reference',str(ROOT/'resultados/integracion'/task['reference'])]
        wrapped=[sys.executable,'-I','-B',str(ROOT/'tools/supervisor.py'),'--name','integration_batch'+batch+'_'+task['id'],'--timeout','600','--',*command]
        result=subprocess.run(wrapped,cwd=ROOT,timeout=720,check=False)
        rows.append({'id':task['id'],'exit_code':result.returncode,'status':'COMPLETED' if result.returncode==0 else'TECHNICAL_ERROR'})
        put(ROOT/('resultados/integracion/BATCH_'+batch+'_PROGRESS.json'),{'tasks':rows,'elapsed_seconds':time.monotonic()-started})
        if result.returncode:raise SystemExit(result.returncode)
    put(ROOT/('resultados/integracion/BATCH_'+batch+'_PROGRESS.json'),{'tasks':rows,'elapsed_seconds':time.monotonic()-started,'status':'COMPLETED'})


if __name__=='__main__':main()
