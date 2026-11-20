"""Supervised workers and immutable source bytes, using the existing job API."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ast,hashlib,json,subprocess,sys,time
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--script',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--cases',required=True);p.add_argument('--timeout',type=int,default=900);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.process_control import spawn_owned,terminate_job,close_job,job_resources
lab=Path(__file__).parent;budget=json.loads((a.system.parent/'evidencia/campanas/ACCESO_ADAPTATIVO_01/PRESUPUESTO.json').read_bytes());a.out.mkdir(parents=True,exist_ok=False);objects=lab/'versiones_codigo/objetos';objects.mkdir(parents=True,exist_ok=True);sources={}
paths=set(a.system.rglob('*.py'))|set(lab.rglob('*.py'))|{a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01'/n for n in('instrumentos_pc01.py','agenda_binaria_pc01.py')}
for path in sorted(paths):
    if'versiones_codigo'in path.parts or'__pycache__'in path.parts:continue
    b=path.read_bytes();h=hashlib.sha256(b).hexdigest();dest=objects/(h+'.py')
    if not dest.exists():dest.write_bytes(b)
    if hashlib.sha256(dest.read_bytes()).hexdigest()!=h:raise ValueError('Source preservation mismatch')
    sources[str(path)]={'sha256':h,'bytes':len(b),'object':str(dest)}
(a.out/'FUENTES_EJECUTADAS.json').write_text(json.dumps({'created_utc':datetime.now(timezone.utc).isoformat(),'sources':sources,'script':str(a.script),'captured_not_a_claim_every_function_executed':True},indent=2)+'\n',encoding='utf8')
for path in(a.script,*lab.glob('*.py'),*a.system.joinpath('capacidades').glob('*.py')):ast.parse(path.read_bytes(),filename=str(path))
rows=[]
for case in a.cases.split(','):
    if time.perf_counter()>budget['monotonic_deadline']-budget['closure_reserve_seconds']:raise TimeoutError('Closing reserve reached; no new worker')
    dest=a.out/case;argv=[sys.executable,'-I','-B','-X','utf8',str(a.script),'--system',str(a.system),'--out',str(dest),'--case',case];start=time.perf_counter()
    with(a.out/(case+'.stdout.log')).open('wb')as out,(a.out/(case+'.stderr.log')).open('wb')as err:
        proc,job,name=spawn_owned(argv,cwd=a.out,stdout=out,stderr=err,memory_limit=budget['worker_memory_limit_bytes'])
        try:
            try:code=proc.wait(timeout=min(a.timeout,max(1,budget['monotonic_deadline']-time.perf_counter()-budget['closure_reserve_seconds'])))
            except subprocess.TimeoutExpired:terminate_job(job);code=proc.wait(timeout=20)
            row={'case':case,'argv':argv,'exit_code':code,'seconds':time.perf_counter()-start,'pid':proc.pid,'job':name,'resources':job_resources(job),'owned_process_waited':True,'owned_job_closed':True}
        finally:close_job(job)
    rows.append(row);(a.out/'EJECUCION.json').write_text(json.dumps({'cases':rows,'no_global_process_termination':True},indent=2)+'\n',encoding='utf8');print(json.dumps({'case':case,'exit_code':code,'seconds':row['seconds']}),flush=True)
    if code:break
