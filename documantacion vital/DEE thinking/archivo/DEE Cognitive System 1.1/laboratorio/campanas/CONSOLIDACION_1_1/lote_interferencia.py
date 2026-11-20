from pathlib import Path
import json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'sistema'))
from app.legacy import owned_memory
from app.process_control import spawn_owned,job_resources,terminate_job,close_job
def main():
    source=Path(__file__).with_name('ensayo_interferencia.py');plan=json.loads(source.with_name('INTERFERENCIA_PLAN_R1.json').read_bytes());base=ROOT/'evidencia/telemetria/INTERFERENCIA_R1';base.mkdir(parents=True,exist_ok=True);rows=[]
    for case in plan['cases']:
        budget=json.loads((ROOT/'PROYECTO.json').read_bytes())['budget'];remaining=budget['budget_seconds']-(time.perf_counter()-budget['start_monotonic']/budget['monotonic_frequency'])
        if remaining<3840:raise TimeoutError('Campaign closure reserve reached; no further native worker started')
        target=base/case['id'];argv=[sys.executable,'-I','-B',str(source),'--case',case['id'],'--out',str(target)];start=time.perf_counter()
        with(base/(case['id']+'.stdout.log')).open('w',encoding='utf8')as stdout,(base/(case['id']+'.stderr.log')).open('w',encoding='utf8')as stderr:
            proc,job,job_name=spawn_owned(argv,cwd=ROOT,stdout=stdout,stderr=stderr)
            peak=0;limit=None
            try:
                while proc.poll()is None:
                    mem=owned_memory(proc)
                    if mem:peak=max(peak,mem['peak_working_set'])
                    if time.perf_counter()-start>600:limit='TIME_LIMIT'
                    if mem and mem['private_bytes']>4*1024**3:limit='MEMORY_LIMIT'
                    if limit:terminate_job(job);break
                    time.sleep(1)
                code=proc.wait()
            finally:
                if proc.poll()is None:terminate_job(job);proc.wait()
                resources=job_resources(job);close_job(job)
        row={'case':case['id'],'owned_pid':proc.pid,'owned_job':job_name,'exit_code':code,'seconds':time.perf_counter()-start,'launcher_peak_working_set':peak,'actual_job_resources':resources,'limit':limit,'owned_process_waited':True,'owned_job_closed':True,'argv':argv};rows.append(row);(base/'PROCESOS.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf8');print(json.dumps(row),flush=True)
    print('ALL_DECLARED_CASES_ATTEMPTED',flush=True)
if __name__=='__main__':main()
