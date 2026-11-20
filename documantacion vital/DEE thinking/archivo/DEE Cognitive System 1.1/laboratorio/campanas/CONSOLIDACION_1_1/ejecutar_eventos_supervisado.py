from pathlib import Path
import argparse,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'sistema'))
from app.process_control import spawn_owned,job_resources,terminate_job,close_job
from app.native_tools import atomic_json,digest_file
def main():
    p=argparse.ArgumentParser();p.add_argument('--eventos',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);argv=[sys.executable,'-I','-B','-X','utf8',str(ROOT/'sistema/gestionar.py'),'eventos',str(a.eventos)];start=time.perf_counter()
    with(a.out/'EVENTOS.stdout.json').open('w',encoding='utf8')as stdout,(a.out/'EVENTOS.stderr.log').open('w',encoding='utf8')as stderr:
        proc,job,name=spawn_owned(argv,cwd=a.out,stdout=stdout,stderr=stderr)
        try:code=proc.wait(timeout=900)
        except BaseException:terminate_job(job);proc.wait();raise
        finally:resources=job_resources(job);close_job(job)
    atomic_json(a.out/'EJECUCION.json',{'schema':'DCS1.1.common_interface.events.v1','event_file':str(a.eventos.relative_to(ROOT)),'event_file_sha256':digest_file(a.eventos),'argv':argv,'exit_code':code,'seconds':time.perf_counter()-start,'resources':resources,'owned_job':name,'owned_job_closed':True,'primary':'EVENTOS.stdout.json'});print(json.dumps({'exit_code':code,'seconds':time.perf_counter()-start}))
if __name__=='__main__':main()
