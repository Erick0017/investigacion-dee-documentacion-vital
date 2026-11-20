"""Affected public system entry checks; no inherited suites."""
from pathlib import Path
import argparse,json,sys,time,subprocess
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
sys.path.insert(0,str(a.system));from app.process_control import spawn_owned,close_job,terminate_job,job_resources
rows=[];commands=[
 ['bifurcar','ES01_MAIN_01','ES01_API_01','--modalidad','CANDIDATE'],
 ['experiencia','--vida','ES01_API_01','espanol-preparar'],
 ['experiencia','--vida','ES01_API_01','espanol-contexto','--parametros',json.dumps({'value':83,'method':'B'})],
 ['guardar','--vida','ES01_API_01'],
 ['restaurar','ES01_API_01'],
 ['experiencia','--vida','ES01_API_01','espanol-contexto','--parametros',json.dumps({'value':104,'method':'B'})],
 ['experiencia','--vida','ES01_API_01','espanol-formas'],
 ['estado','--vida','ES01_MAIN_01'],['estado']]
for i,command in enumerate(commands):
 argv=[sys.executable,'-I','-B','-X','utf8',str(a.system/'gestionar.py'),*command];begin=time.perf_counter()
 with(a.out/(str(i)+'.stdout.json')).open('wb')as f,(a.out/(str(i)+'.stderr.txt')).open('wb')as e:
  proc,job,name=spawn_owned(argv,cwd=a.out,stdout=f,stderr=e)
  try:
   try:code=proc.wait(timeout=180)
   except subprocess.TimeoutExpired:terminate_job(job);code=proc.wait(timeout=20)
   row={'command':argv,'exit_code':code,'seconds':time.perf_counter()-begin,'resources':job_resources(job),'stdout':str(i)+'.stdout.json','stderr':str(i)+'.stderr.txt','owned_job_closed':True}
  finally:close_job(job)
 rows.append(row);(a.out/'COMANDOS.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'step':i,'exit_code':code,'seconds':row['seconds']}),flush=True)
 if code:break

