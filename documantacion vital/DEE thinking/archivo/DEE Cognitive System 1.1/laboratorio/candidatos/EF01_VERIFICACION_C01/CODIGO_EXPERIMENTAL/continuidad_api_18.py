"""Actual public CLI, separate owned process for each interaction/load."""
from pathlib import Path
import argparse,json,sys,time,subprocess,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
sys.path.insert(0,str(a.system));from app.process_control import spawn_owned,close_job,terminate_job,job_resources
life='E1_ESPANOL_01';base=['experiencia','--vida',life]
def op(name,options):return base+[name,'--parametros',json.dumps(options)]
commands=[['version'],['bifurcar','ES01_LANGUAGE13_social_full',life,'--modalidad','CANDIDATE'],['restaurar',life],
 op('espanol-relaciones-producir',{'frame':'lexical05','bridge':'near5Bridge','parameter':-3,'load':5}),
 ['guardar','--vida',life],['restaurar',life],
 op('espanol-relaciones-producir',{'frame':'lexical05','bridge':'near5Bridge','parameter':5,'load':5}),
 op('espanol-lexico-contexto',{'frame':'lexical05','parameter':3,'load':5,'emit_word_queries':False}),
 op('espanol-puente-forma',{'bridge':'near5Bridge'}),op('espanol-contacto-consultar',{'frame':'contactoA'}),
 op('espanol-contacto-consultar',{'frame':'freeRepair5'}),op('espanol-igual-forma',{}),op('espanol-formas',{}),
 ['estado','--vida',life],['estado']]
rows=[]
for i,command in enumerate(commands):
 argv=[sys.executable,'-I','-B','-X','utf8',str(a.system/'gestionar.py'),*command];begin=time.perf_counter()
 with(a.out/(str(i)+'.stdout.json')).open('wb')as f,(a.out/(str(i)+'.stderr.txt')).open('wb')as e:
  proc,job,name=spawn_owned(argv,cwd=a.out,stdout=f,stderr=e)
  try:
   try:code=proc.wait(timeout=180)
   except subprocess.TimeoutExpired:terminate_job(job);code=proc.wait(timeout=20)
   row={'step':i,'command':argv,'exit_code':code,'seconds':time.perf_counter()-begin,'resources':job_resources(job),'stdout':str(i)+'.stdout.json','stderr':str(i)+'.stderr.txt','owned_job_closed':True}
  finally:close_job(job)
 rows.append(row);(a.out/'COMANDOS.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'step':i,'exit_code':code,'seconds':row['seconds']}),flush=True)
 if code:break
