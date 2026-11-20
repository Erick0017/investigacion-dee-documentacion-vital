from pathlib import Path
import argparse,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'sistema'))
from app.process_control import spawn_owned,terminate_job,close_job,job_resources
from app.native_tools import atomic_json
def main():
    p=argparse.ArgumentParser();p.add_argument('--plan',type=Path,default=Path(__file__).with_name('CONTINUIDAD_FUNCIONAL_PLAN_R2.json'));p.add_argument('--group',default='CONTINUIDAD_FUNCIONAL_R2');a=p.parse_args();out=ROOT/'evidencia/telemetria'/a.group;out.mkdir(parents=True,exist_ok=True);rows=[]
    for case in json.loads(a.plan.read_bytes())['cases']:
        b=json.loads((ROOT/'PROYECTO.json').read_bytes())['budget']
        if b['budget_seconds']-(time.perf_counter()-b['start_monotonic']/b['monotonic_frequency'])<4140:raise TimeoutError('Closure reserve')
        argv=[sys.executable,'-I','-B','-X','utf8',str(Path(__file__).with_name('continuidad_funcional.py')),'--case',case['id'],'--out',str(out/case['id']),'--plan',str(a.plan)];start=time.perf_counter()
        with(out/(case['id']+'.stdout.log')).open('w',encoding='utf8')as stdout,(out/(case['id']+'.stderr.log')).open('w',encoding='utf8')as stderr:
            proc,job,name=spawn_owned(argv,cwd=ROOT,stdout=stdout,stderr=stderr)
            try:code=proc.wait(timeout=900)
            except BaseException:terminate_job(job);proc.wait();raise
            finally:resources=job_resources(job);close_job(job)
        rows.append({'case':case['id'],'exit_code':code,'seconds':time.perf_counter()-start,'owned_job':name,'closed':True,'resources':resources,'argv':argv});atomic_json(out/'PROCESOS.json',rows);print(json.dumps(rows[-1]),flush=True)
if __name__=='__main__':main()
