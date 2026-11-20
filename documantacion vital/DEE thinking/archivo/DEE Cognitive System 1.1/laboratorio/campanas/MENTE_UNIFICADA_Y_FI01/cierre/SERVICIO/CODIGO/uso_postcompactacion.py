"""One new generic native-use request after the zero-tick ledger migration."""
import argparse,gzip,hashlib,json,shutil,subprocess,sys,time
from datetime import datetime
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cola_local import QueueDB
from importacion_emparejada import verify_export


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();s=a.sistema.resolve();out=a.salida.resolve();out.mkdir(parents=True,exist_ok=False)
    before=json.loads((s/'estado/vidas/MU_MAIN/VIDA.json').read_bytes());before={k:before[k]for k in('life_id','world_id','parent','physical','snapshot','snapshot_sha256','operation_count_offset')}
    q=QueueDB(s/'estado/servicios_persistentes/MU_MAIN/cola.sqlite3');records={'before':before};checks=[];commands=[];process=None;start=time.monotonic()
    for rel in('gestionar.py','app/lives.py','app/servicio_persistente.py','app/cola_local.py','app/finalizar_protocolo.py','app/compactar_historia_operativa.py','capacidades/mente_unificada_01.py','capacidades/selector_acrecion_nativo.py'):
        t=out/'codigo'/rel;t.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(s/rel,t)
    shutil.copyfile(Path(__file__),out/'codigo/uso_postcompactacion.py')
    def check(k,v):checks.append({'check':k,'observed':bool(v)})
    def submit(identifier,op):
        payload={'operacion':op}
        if op=='sesion':payload['situaciones']=[{'modo':'usar'}]
        admission=q.put(identifier,payload);limit=time.monotonic()+12
        if admission['admission'].startswith('rejected'):raise RuntimeError(json.dumps(admission))
        while time.monotonic()<limit:
            row=q.get(identifier)
            if row and row['status']in('completed','failed_preserved','uncertain','rejected_invalid'):
                records[identifier]=row
                if row['status']!='completed':raise RuntimeError(json.dumps(row))
                return json.loads(row['result'])
            time.sleep(.03)
        raise TimeoutError(identifier)
    try:
        argv=[sys.executable,'-I','-B','-X','utf8',str(s/'gestionar.py'),'mente-unificada-iniciar','--vida','MU_MAIN','--backend','mente_unificada','--intervalo','0.1','--guardar-cada','15','--max-segundos','25']
        launched=time.time();process=subprocess.Popen(argv,text=True,encoding='utf8',stdout=subprocess.PIPE,stderr=subprocess.PIPE);limit=time.monotonic()+10
        while time.monotonic()<limit:
            owner=q.get_meta('owner')
            if owner and owner.get('running')and owner.get('wall_utc')and datetime.fromisoformat(owner['wall_utc']).timestamp()>=launched:break
            if process.poll()is not None:raise RuntimeError(str(process.communicate()))
            time.sleep(.03)
        else:raise TimeoutError('New epoch owner readiness')
        records['new_epoch']=owner;check('explicit new epoch retains identity',owner['life_id']=='MU_MAIN'and owner['epoch']==2 and owner['backend']=='mente_unificada')
        use=submit('mu_a52_use','sesion');records['native_use_result']=use
        check('exactly one new generic use and no task replay',q.get_meta('owner')['material_calls']==5)
        check('no external worker for generic use',not use['result']['INSTRUMENTO_FENCE']['exact_environment_processes'])
        pause=submit('mu_a52_pause','pausar');export=submit('mu_a52_export','exportar');root,m,v=verify_export(export['paired_export']['directory']);records['paired_export']={'manifest':m,'verification':v}
        submit('mu_a52_stop','detener');stdout,stderr=process.communicate(timeout=12);commands.append({'argv':argv,'returncode':process.returncode,'stdout':stdout,'stderr':stderr});process=None
        argv=[sys.executable,'-I','-B','-X','utf8',str(s/'gestionar.py'),'mente-unificada-finalizar-protocolo','--vida','MU_MAIN']
        done=subprocess.run(argv,text=True,encoding='utf8',capture_output=True,timeout=20);commands.append({'argv':argv,'returncode':done.returncode,'stdout':done.stdout,'stderr':done.stderr})
        if done.returncode:raise RuntimeError(done.stderr)
        records['closed_epoch']=json.loads(done.stdout);final=json.loads((s/'estado/vidas/MU_MAIN/VIDA.json').read_bytes());records['final']={k:final[k]for k in('life_id','world_id','parent','physical','snapshot','snapshot_sha256','operation_count_offset')}
        check('closed epoch retains new actual future',records['closed_epoch']['result']['physical_before']==records['closed_epoch']['result']['physical_after']and records['final']['physical']['tick']>before['physical']['tick'])
        check('closed transport has no uncertain or pending requests',not q.outstanding()and q.get_meta('protocol_admission_closed')is True)
        check('archived operation-count prefix retained',final['operation_count_offset']==before['operation_count_offset'])
    except Exception as error:
        records['harness_error']={'type':type(error).__name__,'detail':str(error)}
        if process and process.poll()is None:
            q.put('mu_a52_emergency_stop',{'operacion':'detener'})
            try:process.communicate(timeout=20)
            except Exception:records['owner_still_finishing_uninterrupted_operation']=True
    value={'schema':'DEE.unified.service.post_compaction_new_use.v1','records':records,'checks':checks,'commands':commands,'host_seconds':time.monotonic()-start,
        'scope':'One newly initiated generic native query, not a replay of old jobs or a new policy-learning experiment; new transport epoch explicitly retains the same physical life.'}
    target=out/'USO_POSTCOMPACTACION.json.gz'
    with gzip.GzipFile(filename=str(target),mode='wb',mtime=0)as f:f.write((json.dumps(value,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps({'primary':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'checks':checks,'error':records.get('harness_error'),'host_seconds':value['host_seconds'],'final':records.get('final')},ensure_ascii=False))
    return bool(records.get('harness_error'))or not all(x['observed']for x in checks)


if __name__=='__main__':raise SystemExit(main())
