from pathlib import Path
import json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'sistema'))
from app.process_control import spawn_owned,job_resources,terminate_job,close_job
from app.native_tools import atomic_json,digest_file
def main():
    out=ROOT/'evidencia/telemetria/REPERTORIO45_VIVIDO';out.mkdir(parents=True,exist_ok=False);events=ROOT/'sistema/documentacion/ejemplos/repertorio65_32_mas33.eventos';argv=[sys.executable,'-I','-B','-X','utf8',str(ROOT/'sistema/gestionar.py'),'eventos',str(events)];start=time.perf_counter()
    with(out/'EVENTOS.stdout.json').open('w',encoding='utf8')as stdout,(out/'EVENTOS.stderr.log').open('w',encoding='utf8')as stderr:
        proc,job,name=spawn_owned(argv,cwd=out,stdout=stdout,stderr=stderr)
        try:code=proc.wait(timeout=900)
        except BaseException:terminate_job(job);proc.wait();raise
        finally:resources=job_resources(job);close_job(job)
    rows=json.loads((out/'EVENTOS.stdout.json').read_bytes())if code==0 else[];reads=[x for x in rows if isinstance(x.get('result'),dict)and x['result'].get('INSTRUMENTO',{}).get('operation')=='MATERIAL_QUERY'];actual=[1 if i%3!=1 else-1 for i in range(65)];summaries=[]
    for row in reads:
        result=row['result']['result'];response=result['responses'];summaries.append({'read_tick':result['read_tick'],'rows':len(response),'covered':sum(x['covered']for x in response),'matches_auditor':sum(x['covered']and x['value']==actual[int(x['form'][1:])-1]for x in response)})
    atomic_json(out/'EJECUCION.json',{'schema':'DCS1.1.managed65.v1','event_file_sha256':digest_file(events),'argv':argv,'exit_code':code,'seconds':time.perf_counter()-start,'resources':resources,'owned_job':name,'job_closed':True,'reads':summaries,'claims':'A new T0life, own actual32+33experience, opaque directionalforms only, not integratedE1 or65meanings.'});print(json.dumps({'exit_code':code,'reads':summaries,'seconds':time.perf_counter()-start}))
if __name__=='__main__':main()
