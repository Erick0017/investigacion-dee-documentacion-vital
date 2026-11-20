"""Research-only owned process-tree accounting; never selects a DEE response."""
import argparse, ctypes, datetime, hashlib, importlib.util, json, os
from pathlib import Path
import shutil, subprocess, sys, time

def emit(path,value):
    with Path(path).open('x',encoding='utf8',newline='\n') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--root-go',choices=['APD03_TOTAL_JOB_R01'],required=True)
    args=parser.parse_args();root=args.root.resolve();here=Path(__file__).resolve().parent
    evidence=root/'evidencia/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION'
    out=evidence/'SUPERVISION_MAIN_R01';out.mkdir(parents=True,exist_ok=False)
    childout=evidence/'MAIN_INTEGRADO_R01'
    if childout.exists():raise FileExistsError('Existing MAIN trial preserved, no retry')
    source=root/'sistema/app/process_control.py'
    spec=importlib.util.spec_from_file_location('apd03_total_resources',source)
    pc=importlib.util.module_from_spec(spec);spec.loader.exec_module(pc)
    command=[sys.executable,'-I','-B','-X','utf8',str(here/'ejecutar_main_integrado_apd03_r01.py'),
             '--root',str(root),'--out',str(childout),'--root-go','APD03_MAIN_R01_REVIEWED_ONLY']
    sources=[]
    for path in (Path(__file__),source):
        target=out/path.name;shutil.copyfile(path,target)
        sources.append({'path':str(path),'copy':target.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    emit(out/'ANTES_DE_INICIAR.json',{'command':command,'sources':sources,
        'memory_limit_total_bytes':1073741824,'native_owner_limit_bytes':536870912,
        'one_native_owner_at_a_time':True,'energy':'NO MEDIDA',
        'scope':'The outer Job includes driver, manager clients, UI and Native owners/workers. Nested Native-only accounting is NOT added to this total.'})
    began=time.monotonic();cpu=time.process_time_ns();samples=[];error=None
    with (out/'STDOUT.txt').open('xb') as stdout,(out/'STDERR.txt').open('xb') as stderr:
        proc,job,name=pc.spawn_owned(command,cwd=Path(sys.executable).parent,
            stdout=stdout,stderr=stderr,memory_limit=1073741824)
        try:
            while True:
                measurement=pc.job_resources(job);extended=pc.Extended()
                if pc.K.QueryInformationJobObject(job,9,ctypes.byref(extended),ctypes.sizeof(extended),None):
                    measurement['io']={k:int(getattr(extended.IoInfo,k))for k,_ in pc.IO._fields_}
                sample={'elapsed_seconds':time.monotonic()-began,
                    'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),**measurement}
                samples.append(sample)
                with (out/'MUESTRAS_RECURSOS.jsonl').open('a',encoding='utf8') as stream:
                    stream.write(json.dumps(sample,ensure_ascii=False)+'\n')
                if proc.poll() is not None and not measurement.get('job_active_processes'):break
                if time.monotonic()-began>=5400:
                    error='Own process tree exceeded the predeclared90minute guard; this is a host/process limit, not a cognitive verdict.'
                    pc.terminate_job(job,124);proc.wait(timeout=15);break
                time.sleep(5)
            result={'command':command,'pid':proc.pid,'job_name':name,'returncode':proc.returncode,
                'wall_seconds':time.monotonic()-began,'monitor_cpu_ns':time.process_time_ns()-cpu,
                'final_job':pc.job_resources(job),'sample_count':len(samples),'error':error,
                'energy':'NO MEDIDA','no_decisional_intervention':True,
                'source_hashes_unchanged':all(hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256']for r in sources)}
            emit(out/'RESULTADO_SUPERVISION.json',result)
            print(json.dumps(result,ensure_ascii=False),flush=True)
        finally:pc.close_job(job)
    return 1 if error or proc.returncode else 0

if __name__=='__main__':raise SystemExit(main())
