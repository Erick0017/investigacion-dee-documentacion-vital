"""Two sequential owned worker processes; one advancing AUX at a time."""
import json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2];S=ROOT/'sistema';TESTS=ROOT.parents[4]
sys.path.insert(0,str(S))
from app.process_control import spawn_owned,job_resources,terminate_job,close_job
EV=ROOT/'evidencia/campanas/APD02_CONTINUIDAD_CALIDAD_ADAPTACION/OBJETIVO_NATIVO_R03'
def main():
    records=[];started=time.monotonic()
    for phase in('prefix','suffix'):
        argv=[str(TESTS/'_dcs11_env_20261020_002458/Scripts/python.exe'),'-I','-B','-X','utf8',str(HERE/'ensayar_objetivo_nativo_r03.py'),'--phase',phase]
        with(EV/(phase+'_STDOUT.txt')).open('xb')as out,(EV/(phase+'_STDERR.txt')).open('xb')as err:
            p,job,name=spawn_owned(argv,cwd=str(TESTS),stdout=out,stderr=err,memory_limit=536870912);forced=False
            while p.poll()is None:
                if time.monotonic()-started>570:terminate_job(job,124);forced=True;break
                time.sleep(.25)
            rc=p.wait(timeout=20)
            for _ in range(250):
                resource=job_resources(job)
                if resource.get('job_active_processes')==0:break
                time.sleep(.02)
            close_job(job)
        row={'phase':phase,'exit_code':rc,'forced':forced,'job':name,'resources':resource,'argv':argv,'host_seconds_since_start':time.monotonic()-started}
        records.append(row)
        with(EV/(phase+'_SUPERVISION.json')).open('x',encoding='utf8')as f:json.dump(row,f,ensure_ascii=False,indent=2)
        if rc:break
    with(EV/'SUPERVISION.json').open('x',encoding='utf8')as f:json.dump({'workers':records,'host_seconds':time.monotonic()-started},f,ensure_ascii=False,indent=2)
    print(json.dumps(records,ensure_ascii=False));raise SystemExit(next((x['exit_code']for x in records if x['exit_code']),0))
if __name__=='__main__':main()
