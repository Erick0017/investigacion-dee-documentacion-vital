"""At most three CPython-pass Job-accounting fixtures; zero DEE Runtimes."""
import argparse,hashlib,importlib.util,json,subprocess,sys,time
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();out=a.salida;out.mkdir(exist_ok=False);source=a.sistema/'app/process_control.py';spec=importlib.util.spec_from_file_location('existing_owned_job_only',source);pc=importlib.util.module_from_spec(spec);spec.loader.exec_module(pc);deadline=time.monotonic()+15;cases=[]
    for index in range(3):
        if deadline-time.monotonic()<1:break
        job=None;proc=None;item={'index':index,'native_Runtimes':0,'argv':[sys.executable,'-I','-B','-c','pass']};begin=time.monotonic()
        try:
            proc,job,name=pc.spawn_owned(item['argv'],cwd=a.sistema,stdout=(out/('PASS_'+str(index)+'.stdout')).open('x'),stderr=(out/('PASS_'+str(index)+'.stderr')).open('x'),memory_limit=536870912);item.update(launcher_pid=proc.pid,job_name=name);proc.wait(timeout=max(.1,min(5,deadline-time.monotonic())));item['returncode']=proc.returncode;observed=[];end=min(deadline,time.monotonic()+5)
            while True:
                resource=pc.job_resources(job);observed.append({'elapsed_after_begin':time.monotonic()-begin,'resource':resource})
                if resource.get('job_active_processes')==0 or time.monotonic()>=end:break
                time.sleep(.02)
            item['observations']=observed;item['final_resource']=observed[-1]['resource'];item['zero_before_close']=item['final_resource'].get('job_active_processes')==0
        except Exception as error:item['error']={'type':type(error).__name__,'detail':str(error)}
        finally:
            if job is not None:
                if proc is not None and proc.poll()is None:item['forced_fixture_only']=True;pc.terminate_job(job,125);proc.wait(timeout=max(.1,min(1,deadline-time.monotonic())))
                pc.close_job(job)
        item['seconds']=time.monotonic()-begin;cases.append(item)
    result={'schema':'DEE.APD01.Job_accounting.CPython_pass.N0.v1','native_ticks':0,'native_Runtimes':0,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'cases':cases,'total_seconds':sum(x['seconds']for x in cases),'scope':'Only three own bounded CPython pass processes; no system-wide inventory, state mutation, Runtime or hidden action retry. Fixtures cannot establish the historical cause of the R03 active1 receipt.'}
    with(out/'RESULTADO.json').open('x',encoding='utf8')as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'cases':len(cases),'seconds':result['total_seconds'],'immediate_active':[x.get('observations',[{}])[0].get('resource',{}).get('job_active_processes')for x in cases],'zero_before_close':[x.get('zero_before_close')for x in cases]}))
if __name__=='__main__':main()
