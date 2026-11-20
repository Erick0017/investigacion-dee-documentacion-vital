"""Explicit instrument test runner; not used to answer participant queries."""
from pathlib import Path
import json,sys,time
from .native_tools import atomic_json
from .process_control import spawn_owned,job_resources,terminate_job,close_job
def run_validation(system_root,out,level='A'):
    root=Path(system_root).resolve();out=Path(out).resolve()
    if out.exists():raise FileExistsError('Use a new validation output directory')
    out.mkdir(parents=True);argv=[sys.executable,'-I','-B','-X','utf8',str(root/'pruebas_minimas/probar_sistema.py'),'--system-root',str(root),'--out',str(out/'pruebas'),'--level',level];start=time.perf_counter()
    with(out/'stdout.log').open('w',encoding='utf8')as stdout,(out/'stderr.log').open('w',encoding='utf8')as stderr:
        proc,job,name=spawn_owned(argv,cwd=out,stdout=stdout,stderr=stderr)
        try:code=proc.wait(timeout={'A':900,'B':1800,'C':2700}[level])
        except BaseException:terminate_job(job);proc.wait();raise
        finally:resources=job_resources(job);close_job(job)
    result={'schema':'DCS1.1.explicit_validation.v1','level':level,'exit_code':code,'seconds':time.perf_counter()-start,'argv':argv,'owned_job':name,'resources':resources,'active_life_modified':False,'proof':'pruebas/RESULTADOS.json'};atomic_json(out/'EJECUCION.json',result)
    return result
