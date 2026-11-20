"""Bounded operational pilot in one explicit full MA02 fork. Not a new cognition test."""
import argparse,gzip,hashlib,json,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cola_local import QueueDB


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True)
    p.add_argument('--salida',type=Path,required=True);p.add_argument('--vida',required=True)
    a=p.parse_args();root=a.sistema.resolve();out=a.salida.resolve();out.mkdir(parents=True,exist_ok=False)
    code=Path(__file__).resolve().parent;copies=[]
    for f in sorted(code.glob('*.py')):
        dst=out/'codigo'/f.name;dst.parent.mkdir(exist_ok=True);shutil.copyfile(f,dst)
        copies.append({'file':f.name,'sha256':sha(f),'bytes':f.stat().st_size})
    parent=root/'estado/vidas/MA02_MAIN_5/VIDA.json';parent_data=json.loads(parent.read_bytes())
    snapshot=root/parent_data['snapshot'];protected={str(parent):sha(parent),str(snapshot):sha(snapshot),str(root/'estado/ACTIVO.json'):sha(root/'estado/ACTIVO.json')}
    if parent_data['physical']['tick']!=11196:raise ValueError('Explicit documented parent differs; do not substitute silently.')
    commands=[];checks=[];records={};started=time.monotonic();process=None
    def check(label,value):checks.append({'check':label,'observed':bool(value)})
    def command(argv,timeout=30):
        t=time.monotonic();r=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8',timeout=timeout)
        commands.append({'argv':argv,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'host_seconds':time.monotonic()-t})
        return r
    def wait(identifier,seconds=15):
        limit=time.monotonic()+seconds
        while time.monotonic()<limit:
            row=q.get(identifier)
            if row and row['status']in('completed','failed_preserved','uncertain'):
                records[identifier]=row
                if row['status']!='completed':raise RuntimeError('Material/control operation failed: '+json.dumps(row))
                return json.loads(row['result'])
            time.sleep(.03)
        raise TimeoutError(identifier)
    try:
        r=command([sys.executable,'-I','-B','-X','utf8',str(root/'gestionar.py'),'bifurcar','MA02_MAIN_5',a.vida,'--modalidad','DIAGNOSTIC_COPY'])
        if r.returncode:raise RuntimeError(r.stderr)
        queue_path=root/'estado/servicios_persistentes'/a.vida/'cola.sqlite3'
        serve=[sys.executable,'-I','-B','-X','utf8',str(code/'servicio_persistente.py'),'--sistema',str(root),'--vida',a.vida,
            '--intervalo','0.05','--guardar-cada','0.5','--max-segundos','20']
        process=subprocess.Popen(serve,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8')
        limit=time.monotonic()+12
        while time.monotonic()<limit:
            if process.poll()is not None:raise RuntimeError('Owner failed before readiness: '+str(process.communicate()))
            if queue_path.is_file():
                q=QueueDB(queue_path)
                if q.get_meta('owner'):break
            time.sleep(.03)
        else:raise TimeoutError('Initial service readiness')
        initial=q.get_meta('owner');records['initial_status']=initial
        # Second owner must fail at the existing world lock before loading a
        # second native adapter for this world. No lock is broken or removed.
        second=command(serve,timeout=10);check('second owner rejected by world lock',second.returncode!=0 and 'FileExistsError'in second.stderr)
        q.put('first',{'operacion':'sesion','situaciones':[{'contexto':'gamma'}]});first=wait('first')
        first_sign=first['result']['rows'][0]['reader']['formed_native_command'];check('gamma physical output+at fixed native reader',first_sign==1)
        time.sleep(.8);idle=q.get_meta('owner');records['idle_between_requests']=idle
        check('world ticks advanced between material requests',idle['tick']>first['after_tick'])
        q.put('pause',{'operacion':'pausar'});pause=wait('pause');time.sleep(.7)
        paused=q.get_meta('owner');records['paused_status']=paused
        check('pause conserves tick without hidden idle advance',paused['tick']==pause['after_tick'])
        request={'operacion':'sesion','situaciones':[{'contexto':'epsilon'}]}
        q.put('second',request);time.sleep(.15);check('material input waits while paused',q.get('second')['status']=='queued')
        q.put('resume',{'operacion':'reanudar'});wait('resume');second_result=wait('second')
        check('epsilon physical output−after resume',second_result['result']['rows'][0]['reader']['formed_native_command']==-1)
        duplicate=q.put('second',request);records['duplicate_transport_receipt']=duplicate
        check('duplicate ID returns prior record without a second material call',duplicate['admission']=='existing_same_transport_request'and duplicate['request']['status']=='completed')
        q.put('save',{'operacion':'guardar'});saved=wait('save');records['before_stop']=q.get_meta('owner')
        q.put('stop',{'operacion':'detener'});wait('stop');stdout,stderr=process.communicate(timeout=10)
        commands.append({'argv':serve,'returncode':process.returncode,'stdout':stdout,'stderr':stderr});process=None
        final=q.get_meta('owner');records['first_process_final']=final
        check('two material calls only',final['material_calls']==2)
        # Same life, later process. No fork or source snapshot restoration.
        again=serve[:-1]+['2']
        r=command(again,timeout=15);check('second process continuation succeeded',r.returncode==0)
        last=q.get_meta('owner');records['second_process_final']=last
        check('same identity later process and later physical tick',last['life_id']==a.vida and last['pid']!=final['pid']and last['tick']>final['tick'])
        check('graceful owner stopped and no new autostart',last['running']is False)
        card=root/'estado/vidas'/a.vida/'VIDA.json';vida=json.loads(card.read_bytes())
        records['final_full_state']={'record':str(card),'record_sha256':sha(card),'snapshot':vida['snapshot'],
            'snapshot_sha256':vida['snapshot_sha256'],'physical':vida['physical']}
        check('full snapshot exists and matches pointer',sha(root/vida['snapshot'])==vida['snapshot_sha256'])
        check('all protected source bytes unchanged',all(sha(Path(k))==v for k,v in protected.items()))
    except Exception as error:
        records['harness_error']={'type':type(error).__name__,'detail':str(error)}
        if process and process.poll()is None:
            # Ask the owner to stop; never terminate unrelated processes.
            try:q.put('harness_stop',{'operacion':'detener'});process.communicate(timeout=12)
            except Exception:
                process.terminate();process.communicate(timeout=5)
                records['own_owner_forced_termination']=True
    result={'schema':'DEE.unified.persistent_operational_pilot.v1','life':a.vida,'parent':'MA02_MAIN_5',
        'parent_tick':11196,'commands':commands,'checks':checks,'records':records,'code':copies,
        'protected_before':protected,'protected_after':{k:sha(Path(k))for k in protected},
        'host_seconds':time.monotonic()-started,'new_cognitive_claim':False,
        'scope':'Short operational copy test, not60minutes and not improved cognition. Prepared context addressing remains MA02 assistance.'}
    target=out/'PILOTO.json.gz'
    with gzip.GzipFile(filename=str(target),mode='wb',mtime=0)as f:f.write((json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8'))
    print(json.dumps({'primary':str(target),'sha256':sha(target),'host_seconds':result['host_seconds'],
        'checks':checks,'error':records.get('harness_error')},ensure_ascii=False))
    return 1 if records.get('harness_error')or not all(x['observed']for x in checks)else 0


if __name__=='__main__':raise SystemExit(main())
