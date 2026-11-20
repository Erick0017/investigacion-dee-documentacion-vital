from pathlib import Path
import argparse,sys,time,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--script',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--cases',required=True);p.add_argument('--timeout',type=int,default=600);a=p.parse_args()
sys.path.insert(0,str(a.system));from app.process_control import spawn_owned,terminate_job,close_job,job_resources
a.out.mkdir(parents=True,exist_ok=False);rows=[]
for case in a.cases.split(','):
    dest=a.out/case;args=[sys.executable,'-I','-B','-X','utf8',str(a.script),'--system',str(a.system),'--out',str(dest),'--case',case];start=time.perf_counter()
    with(a.out/(case+'.stdout.log')).open('wb')as out,(a.out/(case+'.stderr.log')).open('wb')as err:
        proc,job,name=spawn_owned(args,cwd=a.out,stdout=out,stderr=err)
        try:
            try:code=proc.wait(timeout=a.timeout)
            except __import__('subprocess').TimeoutExpired:terminate_job(job);code=proc.wait(timeout=20)
            row={'case':case,'argv':args,'exit_code':code,'seconds':time.perf_counter()-start,'pid':proc.pid,'job':name,'resources':job_resources(job),'stdout':case+'.stdout.log','stderr':case+'.stderr.log','owned_process_waited':True,'owned_job_closed':True}
        finally:close_job(job)
    rows.append(row);(a.out/'EJECUCION.json').write_text(json.dumps({'cases':rows,'no_global_process_termination':True},ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'case':case,'exit_code':code,'seconds':row['seconds']}),flush=True)
