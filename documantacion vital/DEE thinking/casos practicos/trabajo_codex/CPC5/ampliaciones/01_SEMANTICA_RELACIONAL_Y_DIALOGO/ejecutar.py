"""Single finite public entry. Each mutable Runtime has one owned worker."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from supervisor import module as frozen_supervisor

def main():
    p=argparse.ArgumentParser(description='CPC5 ampliacion: ejecucion real y consultas estructuradas')
    p.add_argument('modo',choices=['demostracion','orden','dialogo','capacidad','arquitectura'])
    p.add_argument('--eventos',type=Path);p.add_argument('--config',type=Path);p.add_argument('--caso',type=Path);p.add_argument('--checkpoint',type=Path)
    p.add_argument('--salida',type=Path,required=True);p.add_argument('--timeout',type=int,default=900)
    a=p.parse_args()
    if not 1<=a.timeout<=1800:raise ValueError('Timeout local1..1800segundos')
    if a.salida.exists():raise FileExistsError('Conserve la salida anterior; elija otra ruta')
    if a.modo=='demostracion':
        argv=[str(ROOT/'demostracion.py'),'--salida',str(a.salida.resolve())]
        if a.eventos:argv+=['--eventos',str(a.eventos.resolve())]
        if a.checkpoint:argv+=['--checkpoint',str(a.checkpoint.resolve())]
    elif a.modo in ('orden','dialogo'):
        if not a.config:raise ValueError('--config requerido')
        argv=[str(ROOT/'src/portable_batch.py'),'--mode',a.modo,'--config',str(a.config.resolve()),'--output',str(a.salida.resolve())]
    else:
        if not a.caso:raise ValueError('--caso requerido')
        argv=[str(ROOT/'src/portable_batch.py'),'--mode',a.modo,'--case',str(a.caso.resolve()),'--output',str(a.salida.resolve())]
    started=time.monotonic();child=subprocess.Popen([sys.executable,'-I','-B',*argv],cwd=ROOT,
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1'),creationflags=subprocess.CREATE_NO_WINDOW)
    try:job=frozen_supervisor.OwnedJob(child)
    except Exception:
        child.kill();child.wait(timeout=15);raise
    status='COMPLETED'
    try:child.wait(timeout=a.timeout)
    except subprocess.TimeoutExpired:
        status='TIMEOUT';job.terminate();child.wait(timeout=30)
    finally:job.close()
    report={'schema':'CPC5.extension.public.command.v1','argv':[sys.executable,*argv],'owned_pid':child.pid,'status':status,
            'exit_code':child.returncode,'elapsed_seconds':time.monotonic()-started,'timeout_seconds':a.timeout,
            'scope':'User-authorized new finite execution, not a reset of the historical campaign BUDGET'}
    if a.salida.exists():(a.salida/'PUBLIC_COMMAND.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False));raise SystemExit(child.returncode)

if __name__=='__main__':main()
