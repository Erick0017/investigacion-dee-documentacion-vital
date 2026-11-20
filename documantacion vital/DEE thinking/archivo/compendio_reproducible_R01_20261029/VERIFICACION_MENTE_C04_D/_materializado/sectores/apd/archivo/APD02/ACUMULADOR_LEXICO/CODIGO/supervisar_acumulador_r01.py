"""Reuse owned Windows Job,512MiB,600s, no kill except own timeout."""
import json
import os
import sys
import time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];SYSTEM=ROOT/'sistema'
sys.path.insert(0,str(SYSTEM))
from app.process_control import spawn_owned,job_resources,terminate_job,close_job
TESTS=ROOT.parents[4]
PY=TESTS/'_dcs11_env_20261020_002458/Scripts/python.exe'
OUT=ROOT/'evidencia/campanas/APD02_CONTINUIDAD_CALIDAD_ADAPTACION/acumulador/R01'
def main():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    if OUT.exists():raise FileExistsError('No overwrite or automatic rerun')
    stdout=OUT.parent/'R01_STDOUT.txt';stderr=OUT.parent/'R01_STDERR.txt'
    if stdout.exists()or stderr.exists():raise FileExistsError('Previous process logs preserved')
    command=[str(PY),'-I','-B','-X','utf8',str(HERE/'ensayar_acumulador_r01.py'),'--out',str(OUT)]
    with stdout.open('xb')as out,stderr.open('xb')as err:
        proc,job,name=spawn_owned(command,cwd=str(TESTS),stdout=out,stderr=err,memory_limit=536870912)
        started=time.monotonic();forced=False
        while proc.poll()is None:
            if time.monotonic()-started>=600:
                terminate_job(job,124);forced=True;break
            time.sleep(.25)
        rc=proc.wait(timeout=20)
        for _ in range(250):
            resources=job_resources(job)
            if resources.get('job_active_processes')==0:break
            time.sleep(.02)
        close_job(job)
    report={'command':command,'exit_code':rc,'forced_own_timeout':forced,'job':name,
        'resources_before_close':resources,'host_seconds':time.monotonic()-started,
        'stdout':str(stdout),'stderr':str(stderr)}
    with(OUT.parent/'R01_SUPERVISION.json').open('x',encoding='utf8')as f:json.dump(report,f,ensure_ascii=False,indent=2)
    print(json.dumps(report,ensure_ascii=False))
    raise SystemExit(rc)
if __name__=='__main__':main()
