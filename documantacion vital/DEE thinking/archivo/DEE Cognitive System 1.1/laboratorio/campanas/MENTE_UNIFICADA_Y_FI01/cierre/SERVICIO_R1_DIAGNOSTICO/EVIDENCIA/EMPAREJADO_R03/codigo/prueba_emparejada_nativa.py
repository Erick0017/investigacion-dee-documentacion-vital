"""Bounded existing-manager test of a complete native+transport export/import."""
import argparse,gzip,hashlib,json,shutil,subprocess,sys,time
from datetime import datetime
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cola_local import QueueDB
from importacion_emparejada import verify_export


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
    p.add_argument('--origen',default='MU_SVC_PILOT_R01');p.add_argument('--importada',default='MU_SVC_PAIR_R02');a=p.parse_args()
    system=a.sistema.resolve();out=a.salida.resolve();out.mkdir(parents=True,exist_ok=False);script=system/'gestionar.py';process=None;q=None
    commands=[];records={};checks=[];started=time.monotonic()
    protected={str(p):sha(p)for p in(system/'estado/ACTIVO.json',system/'estado/vidas/MA02_MAIN_5/VIDA.json')}
    card=json.loads((system/'estado/vidas/MA02_MAIN_5/VIDA.json').read_bytes());protected[str(system/card['snapshot'])]=sha(system/card['snapshot'])
    executed=[]
    for relative in('gestionar.py','app/servicio_persistente.py','app/cola_local.py','app/cliente_mente_unificada.py','app/importacion_emparejada.py','capacidades/mente_acumulativa_r02.py','capacidades/eo02_trabajador_local.py'):
        source=system/relative;target=out/'codigo'/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        executed.append({'file':relative,'bytes':source.stat().st_size,'sha256':sha(source)})
    shutil.copyfile(Path(__file__),out/'codigo/prueba_emparejada_nativa.py')
    def check(label,value):checks.append({'check':label,'observed':bool(value)})
    def command(args,timeout=20):
        argv=[sys.executable,'-I','-B','-X','utf8',str(script),*args];r=subprocess.run(argv,text=True,encoding='utf8',capture_output=True,timeout=timeout)
        commands.append({'argv':argv,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
        if r.returncode:raise RuntimeError('Manager command failed: '+r.stderr)
        return json.loads(r.stdout)
    def launch(life,seconds=25):
        nonlocal process,q
        argv=[sys.executable,'-I','-B','-X','utf8',str(script),'mente-unificada-iniciar','--vida',life,'--intervalo','0.1','--guardar-cada','2','--max-segundos',str(seconds)]
        launched_wall=time.time();process=subprocess.Popen(argv,text=True,encoding='utf8',stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        limit=time.monotonic()+10;path=system/'estado/servicios_persistentes'/life/'cola.sqlite3'
        while time.monotonic()<limit:
            if process.poll()is not None:raise RuntimeError('Owner startup failed: '+str(process.communicate()))
            if path.is_file():
                q=QueueDB(path);owner=q.get_meta('owner')
                if owner and owner.get('running')and owner.get('wall_utc')and datetime.fromisoformat(owner['wall_utc']).timestamp()>=launched_wall:
                    return argv,{**owner,'instrument_launcher_pid':process.pid,'instrument_pid_scope':'Windows venv launcher PID can differ from the actual interpreter owner PID; fresh heartbeat and live launcher establish this start.'}
            time.sleep(.03)
        raise TimeoutError('Owner readiness')
    def wait(identifier):
        limit=time.monotonic()+15
        while time.monotonic()<limit:
            row=q.get(identifier)
            if row and row['status']in('completed','failed_preserved','uncertain','rejected_invalid'):
                records[identifier]=row;return row
            time.sleep(.03)
        raise TimeoutError(identifier)
    def submit(identifier,payload,status='completed'):
        q.put(identifier,payload);row=wait(identifier)
        if row['status']!=status:raise RuntimeError('Unexpected transport result: '+json.dumps(row))
        return json.loads(row['result'])if row.get('result')else row
    def close(argv,identifier):
        nonlocal process
        submit(identifier,{'operacion':'detener'});stdout,stderr=process.communicate(timeout=10)
        commands.append({'argv':argv,'returncode':process.returncode,'stdout':stdout,'stderr':stderr});process=None
    try:
        argv,initial=launch(a.origen);records['initial']=initial
        pause=submit('pair_r02_pause',{'operacion':'pausar'})
        req={'operacion':'sesion','situaciones':[{'contexto':'epsilon'}]}
        q.put('pair_r02_pending',req)
        export=submit('pair_r02_export',{'operacion':'exportar'});directory=Path(export['paired_export']['directory'])
        check('material remains queued in source pause',q.get('pair_r02_pending')['status']=='queued')
        root,manifest,verified=verify_export(directory);records['export']={'manifest':manifest,'verification':verified}
        check('export has complete paused native tick',manifest['physical']['tick']==pause['after_tick'])
        close(argv,'pair_r02_stop_source')
        imported=command(['mente-unificada-importar','--paquete',str(directory),'--vida',a.importada]);records['import']=imported
        check('import explicitly distinct identity',imported['life_id']==a.importada and imported['identity']['source_life_id']==a.origen)
        check('no physical tick or content changed by import',all(imported['physical'][k]==manifest['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')))
        argv,initial_copy=launch(a.importada);records['import_initial']=initial_copy
        check('imported service retains paused world and literal queue',initial_copy['paused']and initial_copy['tick']==manifest['physical']['tick']and q.get('pair_r02_pending')['status']=='queued')
        check('export receipt reconciled without repeated export',q.get('pair_r02_export')['status']=='completed')
        submit('pair_r02_resume',{'operacion':'reanudar'})
        pending=json.loads(wait('pair_r02_pending')['result']);check('queued inherited epsilon remains functional',pending['result']['rows'][0]['reader']['formed_native_command']==-1)
        duplicate=q.put('pair_r02_pending',req);records['duplicate']=duplicate
        check('imported ID deduplicates without another material call',duplicate['admission']=='existing_same_transport_request')
        unknown=submit('pair_r02_unknown',{'operacion':'sesion','situaciones':[{'contexto':'not_admitted'}]},status='rejected_invalid')
        check('unadmitted interface rejected before native input',json.loads(unknown['error'])['native_tick_unchanged'])
        gamma=submit('pair_r02_gamma',{'operacion':'sesion','situaciones':[{'contexto':'gamma'}]})
        check('second context functional in imported continuation',gamma['result']['rows'][0]['reader']['formed_native_command']==1)
        records['before_final_close']=q.get_meta('owner');close(argv,'pair_r02_stop_copy');before=q.get_meta('owner');records['first_copy_process_final']=before
        argv,last_start=launch(a.importada,2);stdout,stderr=process.communicate(timeout=12)
        commands.append({'argv':argv,'returncode':process.returncode,'stdout':stdout,'stderr':stderr});process=None
        final=q.get_meta('owner');records['second_copy_process_final']=final
        check('another process continues imported world without replay',final['life_id']==a.importada and final['pid']!=before['pid']and final['tick']>before['tick']and final['material_calls']==before['material_calls'])
        card=json.loads((system/'estado/vidas'/a.importada/'VIDA.json').read_bytes());records['final_card']=card
        check('final native snapshot hash matches pointer',sha(system/card['snapshot'])==card['snapshot_sha256'])
        check('all source protected hashes unchanged',all(sha(Path(k))==v for k,v in protected.items()))
    except Exception as error:
        records['harness_error']={'type':type(error).__name__,'detail':str(error)}
        if process and process.poll()is None:
            try:
                q.put('pair_r02_emergency_stop',{'operacion':'detener'});stdout,stderr=process.communicate(timeout=12)
                commands.append({'kind':'OWN_OWNER_EMERGENCY_STOP','returncode':process.returncode,'stdout':stdout,'stderr':stderr})
            except Exception:process.terminate();process.communicate(timeout=5);records['own_process_terminated']=True
    result={'schema':'DEE.persistent_service.paired_native_test.v1','new_cognitive_claim':False,'commands':commands,'checks':checks,'records':records,
        'executed_source':executed,'protected_before':protected,'protected_after':{k:sha(Path(k))for k in protected},'host_seconds':time.monotonic()-started,
        'scope':'A native operational continuation test of two inherited contents and transport completeness; not new learning, not an independent replica, not the final sixty-minute run.'}
    target=out/'EMPAREJADO.json.gz'
    with gzip.GzipFile(filename=str(target),mode='wb',mtime=0)as f:f.write((json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps({'primary':str(target),'sha256':sha(target),'checks':checks,'error':records.get('harness_error'),'host_seconds':result['host_seconds']},ensure_ascii=False))
    return bool(records.get('harness_error'))or not all(c['observed']for c in checks)


if __name__=='__main__':raise SystemExit(main())
