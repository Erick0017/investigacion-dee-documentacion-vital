from pathlib import Path
import json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'sistema'))
from app.process_control import spawn_owned,terminate_job,close_job,job_resources
from app.native_tools import atomic_json
def main():
    plan=json.loads(Path(__file__).with_name('LECTURA_TARDIA_PLAN_R1.json').read_bytes());out=ROOT/'evidencia/telemetria/LECTURA_TARDIA_R1';out.mkdir(parents=True,exist_ok=True);rows=[]
    for case in plan['cases']:
        budget=json.loads((ROOT/'PROYECTO.json').read_bytes())['budget'];remaining=budget['budget_seconds']-(time.perf_counter()-budget['start_monotonic']/budget['monotonic_frequency'])
        if remaining<4140:raise TimeoutError('Original campaign closure reserve reached; no new worker launched')
        target=out/case['id'];argv=[sys.executable,'-I','-B','-X','utf8',str(Path(__file__).with_name('ensayo_lectura_tardia.py')),'--case',case['id'],'--out',str(target)];start=time.perf_counter()
        with(out/(case['id']+'.stdout.log')).open('w',encoding='utf8')as stdout,(out/(case['id']+'.stderr.log')).open('w',encoding='utf8')as stderr:
            proc,job,name=spawn_owned(argv,cwd=ROOT,stdout=stdout,stderr=stderr)
            try:code=proc.wait(timeout=900)
            except BaseException:terminate_job(job);proc.wait();raise
            finally:resources=job_resources(job);close_job(job)
        row={'case':case['id'],'pid':proc.pid,'exit_code':code,'seconds':time.perf_counter()-start,'owned_job':name,'job_closed':True,'resources':resources,'argv':argv};rows.append(row);atomic_json(out/'PROCESOS.json',rows);print(json.dumps(row),flush=True)
if __name__=='__main__':main()
