"""Owned Job512MiB/600s; uses only the original campaign deadline."""
import json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];SYSTEM=ROOT/'sistema';TESTS=ROOT.parents[4]
sys.path.insert(0,str(SYSTEM))
from app.process_control import spawn_owned,job_resources,terminate_job,close_job
OUT=ROOT/'evidencia/campanas/APD02_CONTINUIDAD_CALIDAD_ADAPTACION/acumulador/R02'
def main():
    if OUT.exists():raise FileExistsError('Preserve executed run')
    outlog=OUT.parent/'R02_STDOUT.txt';errlog=OUT.parent/'R02_STDERR.txt'
    argv=[str(TESTS/'_dcs11_env_20261020_002458/Scripts/python.exe'),'-I','-B','-X','utf8',str(HERE/'ensayar_acumulador_r02.py'),'--out',str(OUT)]
    with outlog.open('xb')as out,errlog.open('xb')as err:
        p,job,name=spawn_owned(argv,cwd=str(TESTS),stdout=out,stderr=err,memory_limit=536870912)
        started=time.monotonic();forced=False
        while p.poll()is None:
            if time.monotonic()-started>=600:terminate_job(job,124);forced=True;break
            time.sleep(.25)
        rc=p.wait(timeout=20)
        for _ in range(250):
            resource=job_resources(job)
            if resource.get('job_active_processes')==0:break
            time.sleep(.02)
        close_job(job)
    record={'argv':argv,'exit_code':rc,'forced':forced,'job':name,'resources':resource,'host_seconds':time.monotonic()-started}
    with(OUT.parent/'R02_SUPERVISION.json').open('x',encoding='utf8')as f:json.dump(record,f,ensure_ascii=False,indent=2)
    print(json.dumps(record,ensure_ascii=False));raise SystemExit(rc)
if __name__=='__main__':main()
