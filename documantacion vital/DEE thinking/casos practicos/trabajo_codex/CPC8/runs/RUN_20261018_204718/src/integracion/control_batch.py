"""Serial task coordinator; every native child gets the common CPC8 supervisor.

This process itself is run as a bounded non-native owned job. It never imports
the engine or reads observations to choose scientific inputs or a control arm.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[2]


def put(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_name(path.name+'.pending.'+str(os.getpid()))
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8');os.replace(temp,path)


def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);a=p.parse_args()
    tasks=json.loads(a.manifest.read_text(encoding='utf8'))['tasks'];rows=[];started=time.monotonic()
    for task in tasks:
        out=ROOT/'resultados/integracion'/task['id'];record=out/'MEASUREMENTS.json'
        if record.exists():
            existing=json.loads(record.read_text(encoding='utf8'))
            if existing.get('status')=='MEASURED' or existing.get('technical_status')=='PASS':
                rows.append({'id':task['id'],'status':'EXISTING_COMPLETED_NOT_REEXECUTED'});continue
            raise RuntimeError('Existing incomplete target requires explicit reconciliation, not blind rerun: '+task['id'])
        command=[sys.executable,'-I','-B',str(ROOT/'src/integracion'/task['script']),
            '--config',str(ROOT/'configuraciones/integracion'/task['config']),
            '--case-id',task.get('case_id',task['id']),'--out',str(out)]
        for key in('parent','initial','reference'):
            if key in task:command+=['--'+key,str(ROOT/'resultados/integracion'/task[key])]
        if 'diagnostic'in task:command+=['--diagnostic',task['diagnostic']]
        wrapped=[sys.executable,'-I','-B',str(ROOT/'tools/supervisor.py'),'--name','integration_batchA_'+task['id'],'--timeout','600','--',*command]
        result=subprocess.run(wrapped,cwd=ROOT,timeout=720,check=False)
        row={'id':task['id'],'exit_code':result.returncode,'status':'COMPLETED' if result.returncode==0 else'TECHNICAL_ERROR'};rows.append(row)
        put(ROOT/'resultados/integracion/BATCH_A_PROGRESS.json',{'tasks':rows,'elapsed_seconds':time.monotonic()-started,'independent_native_evolutions_by_this_coordinator':0})
        if result.returncode:raise SystemExit(result.returncode)
    put(ROOT/'resultados/integracion/BATCH_A_PROGRESS.json',{'tasks':rows,'elapsed_seconds':time.monotonic()-started,'status':'COMPLETED','independent_native_evolutions_by_this_coordinator':0})


if __name__=='__main__':main()
