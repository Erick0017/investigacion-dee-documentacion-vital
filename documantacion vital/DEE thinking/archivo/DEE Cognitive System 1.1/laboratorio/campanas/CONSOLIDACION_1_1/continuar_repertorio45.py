from pathlib import Path
import json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'sistema'))
from app.process_control import spawn_owned,job_resources,terminate_job,close_job
from app.native_tools import atomic_json,digest_file
def main():
    out=ROOT/'evidencia/telemetria/REPERTORIO45_ACCESO_SEPARADO_R2';out.mkdir(parents=True,exist_ok=False);events=ROOT/'sistema/documentacion/ejemplos/repertorio65_acceso_separado.eventos';argv=[sys.executable,'-I','-B','-X','utf8',str(ROOT/'sistema/gestionar.py'),'eventos',str(events)];start=time.perf_counter()
    with(out/'EVENTOS.stdout.json').open('w',encoding='utf8')as stdout,(out/'EVENTOS.stderr.log').open('w',encoding='utf8')as stderr:
        proc,job,name=spawn_owned(argv,cwd=out,stdout=stdout,stderr=stderr)
        try:code=proc.wait(timeout=900)
        except BaseException:terminate_job(job);proc.wait();raise
        finally:resources=job_resources(job);close_job(job)
    rows=json.loads((out/'EVENTOS.stdout.json').read_bytes())if code==0 else[];summaries=[]
    for x in rows:
        v=x.get('result',{}).get('result',{})
        if'responses'not in v:continue
        rr=v['responses'];summaries.append({'read_tick':v['read_tick'],'n':len(rr),'covered':sum(z['covered']for z in rr),'correct':sum(z['covered']and z['value']==(-1 if(int(z['form'][1:])-1)%3==1 else 1)for z in rr)})
    atomic_json(out/'EJECUCION.json',{'schema':'DCS1.1.same_life.phase_access.r2','event_file_sha256':digest_file(events),'exit_code':code,'argv':argv,'reads':summaries,'seconds':time.perf_counter()-start,'resources':resources,'owned_job':name,'same_life_no_reteaching':True});print(json.dumps({'code':code,'reads':summaries}))
if __name__=='__main__':main()
