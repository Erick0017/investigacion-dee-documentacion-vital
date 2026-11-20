"""Supervised immutable source capture before any PC01 native worker."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,subprocess,sys,time
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--script',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--cases',required=True);p.add_argument('--timeout',type=int,default=900);a=p.parse_args()
sys.path.insert(0,str(a.system));from app.process_control import spawn_owned,terminate_job,close_job,job_resources
a.out.mkdir(parents=True,exist_ok=False);objects=Path(__file__).parent/'versiones_codigo/objetos';objects.mkdir(parents=True,exist_ok=True)
sources={}
for base in (a.system,Path(__file__).parent):
    for path in base.rglob('*.py'):
        if 'versiones_codigo'in path.parts or '__pycache__'in path.parts:continue
        b=path.read_bytes();h=hashlib.sha256(b).hexdigest();dest=objects/(h+'.py')
        if not dest.exists():dest.write_bytes(b)
        if hashlib.sha256(dest.read_bytes()).hexdigest()!=h:raise RuntimeError('Frozen source object mismatch')
        sources[str(path)]={'sha256':h,'bytes':len(b),'object':str(dest)}
(a.out/'FUENTES_EJECUTADAS.json').write_text(json.dumps({'created_utc':datetime.now(timezone.utc).isoformat(),'sources':sources,'script':str(a.script),'no_hash_only_revisions':True},indent=2)+'\n',encoding='utf8')
rows=[]
for case in a.cases.split(','):
    dest=a.out/case;argv=[sys.executable,'-I','-B','-X','utf8',str(a.script),'--system',str(a.system),'--out',str(dest),'--case',case];start=time.perf_counter()
    with(a.out/(case+'.stdout.log')).open('wb')as out,(a.out/(case+'.stderr.log')).open('wb')as err:
        proc,job,name=spawn_owned(argv,cwd=a.out,stdout=out,stderr=err,memory_limit=4*1024**3)
        try:
            try:code=proc.wait(timeout=a.timeout)
            except subprocess.TimeoutExpired:terminate_job(job);code=proc.wait(timeout=20)
            row={'case':case,'argv':argv,'exit_code':code,'seconds':time.perf_counter()-start,'pid':proc.pid,'job':name,'resources':job_resources(job),'stdout':case+'.stdout.log','stderr':case+'.stderr.log','owned_process_waited':True,'owned_job_closed':True}
        finally:close_job(job)
    rows.append(row);(a.out/'EJECUCION.json').write_text(json.dumps({'cases':rows,'no_global_process_termination':True},indent=2)+'\n',encoding='utf8');print(json.dumps({'case':case,'exit_code':code,'seconds':row['seconds']}),flush=True)

