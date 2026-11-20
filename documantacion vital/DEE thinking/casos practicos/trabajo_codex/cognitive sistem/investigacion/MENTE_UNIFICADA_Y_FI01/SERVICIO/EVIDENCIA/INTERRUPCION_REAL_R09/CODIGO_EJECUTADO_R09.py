"""Bounded post-write worker interruption in explicitly imported diagnostic worlds.

Preparation copies only the existing Cognitive code; the official WHL is linked
read-only by convention, not rebuilt or installed. The original worker is never
edited. The diagnostic copy pauses AFTER actual output/readback and BEFORE its
receipt, allowing a known partial external effect without a blind native retry.
"""
import argparse,gzip,hashlib,json,os,shutil,signal,subprocess,sys,time
from datetime import datetime
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cola_local import QueueDB
from importacion_emparejada import verify_export


HOOK='''readback=path.read_bytes();assert readback==output
    # DIAGNOSTIC COPY ONLY. No original worker or native record is edited.
    import os as diagnostic_os
    diagnostic_delay=diagnostic_os.environ.get('MUFI_DIAGNOSTIC_PAUSE_AFTER_WRITE_SECONDS')
    if diagnostic_delay is not None:
        diagnostic_marker=folder/'FI01_DIAGNOSTIC_AFTER_WRITE.json'
        if diagnostic_marker.exists():raise FileExistsError('Preserve previous diagnostic marker')
        diagnostic_marker.write_text(json.dumps({'pid':diagnostic_os.getpid(),'native_tick':q['native_tick'],'worker':worker,'raw_observations':public,'output_name':name,'output_bytes':len(readback),'output_sha256':hashlib.sha256(readback).hexdigest(),'actual_write_and_readback_already_occurred':True,'started_ns':time.time_ns(),'scope':'Diagnostic external pause before acknowledgement, not a decision or an input to DEE'}),encoding='utf8')
        time.sleep(float(diagnostic_delay))'''


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(system,paired,out):
    system=system.resolve();paired=paired.resolve();out=out.resolve();out.mkdir(parents=True,exist_ok=False);source,m,v=verify_export(paired)
    fixture=out/'sistema';(fixture/'estado/checkpoints').mkdir(parents=True);(fixture/'runtime').mkdir()
    files=[]
    for group in('app','capacidades'):
        for p in sorted((system/group).glob('*.py')):
            target=fixture/group/p.name;target.parent.mkdir(exist_ok=True);shutil.copyfile(p,target);files.append({'file':target.relative_to(fixture).as_posix(),'original_sha256':sha(p),'copied_sha256':sha(target)})
    for p in sorted((system/'contratos').glob('*.json')):
        target=fixture/'contratos'/p.name;target.parent.mkdir(exist_ok=True);shutil.copyfile(p,target)
    shutil.copyfile(system/'gestionar.py',fixture/'gestionar.py')
    wheel='dee_thinking-4.5.0-cp313-cp313-win_amd64.whl';os.link(system/'runtime'/wheel,fixture/'runtime'/wheel)
    worker=fixture/'capacidades/eo02_trabajador_local.py';before=worker.read_text(encoding='utf8');needle='readback=path.read_bytes();assert readback==output'
    if before.count(needle)!=1:raise ValueError('Worker changed: no approximate injection or altered environmental law is permitted')
    worker.write_text(before.replace(needle,HOOK),encoding='utf8')
    packet=out/'padre_emparejado';shutil.copytree(paired,packet)
    info={'schema':'DEE.unified.worker_interrupt_fixture.v1','system':str(fixture),'paired_source':str(paired),'paired_manifest_sha256':sha(paired/'EXPORTACION_SERVICIO.json'),
        'paired_snapshot_sha256':m['snapshot_sha256'],'backend':m['backend'],'source_physical':m['physical'],'source_verification':v,
        'copied_code':files,'original_worker_sha256':sha(system/'capacidades/eo02_trabajador_local.py'),'instrumented_copy_worker_sha256':sha(worker),
        'original_wheel_sha256':sha(system/'runtime'/wheel),'fixture_wheel_sha256':sha(fixture/'runtime'/wheel),'wheel_physical_hardlink':True,
        'native_ticks':0,'scope':'Test preparation only. Same original installed interpreter/native instrument; a diagnostic script copy delays acknowledgement after real bounded output. No original life, worker, kernel or WHL is changed.'}
    (out/'PREPARACION.json').write_text(json.dumps(info,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8');return info


def run_fixture(folder,output):
    folder=folder.resolve();output=output.resolve();output.mkdir(parents=True,exist_ok=False);info=json.loads((folder/'PREPARACION.json').read_bytes());system=folder/'sistema';script=system/'gestionar.py';pair=folder/'padre_emparejado';arms=[];started=time.monotonic()
    if info['backend']!='mente_unificada':raise ValueError('This diagnostic protocol requires the explicitly admitted unified backend')
    def cli(args,timeout=35):
        argv=[sys.executable,'-I','-B','-X','utf8',str(script),*args];r=subprocess.run(argv,capture_output=True,text=True,encoding='utf8',timeout=timeout)
        if r.returncode:raise RuntimeError(r.stderr)
        return {'argv':argv,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
    def arm(label,cut):
        life='MU_WORKER_'+label;records={'label':label,'cut_after_actual_output':cut};commands=[];owner=None;db=None;start=time.monotonic()
        try:
            commands.append(cli(['mente-unificada-importar','--paquete',str(pair),'--vida',life]))
            env=dict(os.environ);env['MUFI_DIAGNOSTIC_PAUSE_AFTER_WRITE_SECONDS']='3'
            argv=[sys.executable,'-I','-B','-X','utf8',str(script),'mente-unificada-iniciar','--vida',life,'--backend','mente_unificada','--pausado','--intervalo','0.1','--guardar-cada','60','--max-segundos','40']
            launched=time.time();owner=subprocess.Popen(argv,env=env,stdout=(output/(label+'_OWNER.txt')).open('x',encoding='utf8'),stderr=(output/(label+'_ERROR.txt')).open('x',encoding='utf8'))
            deadline=time.monotonic()+15;path=system/'estado/servicios_persistentes'/life/'cola.sqlite3'
            while time.monotonic()<deadline:
                if owner.poll()is not None:raise RuntimeError('Diagnostic owner failed at startup')
                if path.is_file():
                    db=QueueDB(path);status=db.get_meta('owner')
                    if status and status.get('running')and status.get('wall_utc')and datetime.fromisoformat(status['wall_utc']).timestamp()>=launched:break
                time.sleep(.05)
            else:raise TimeoutError('Diagnostic owner readiness')
            def wait(identifier):
                limit=time.monotonic()+20
                while time.monotonic()<limit:
                    row=db.get(identifier)
                    if row and row['status']in('completed','uncertain','failed_preserved','rejected_invalid'):return row
                    time.sleep(.05)
                raise TimeoutError(identifier)
            payload={'operacion':'sesion','situaciones':[{'modo':'trabajo','valores':[3,11]}],'retorno':'omit'}
            records['initial_owner']=status;records['work_admission']=db.put('diag_work',payload);db.put('diag_resume',{'operacion':'reanudar'});records['resume']=wait('diag_resume')
            work=system/'estado/servicios_locales'/life;deadline=time.monotonic()+15;marker=None
            while time.monotonic()<deadline:
                matches=list(work.rglob('FI01_DIAGNOSTIC_AFTER_WRITE.json'))if work.exists()else[]
                if matches:
                    if len(matches)!=1:raise ValueError('Ambiguous diagnostic worker marker')
                    marker=matches[0];break
                row=db.get('diag_work')
                if row and row['status']in('completed','uncertain','failed_preserved','rejected_invalid'):break
                time.sleep(.03)
            if marker is None:raise RuntimeError('No real worker write was observed; do not claim an interruption test occurred')
            partial=json.loads(marker.read_bytes());actual=marker.parent/partial['output_name'];records['partial_worker_receipt']=partial
            records['actual_file_before_cut']={'bytes':actual.stat().st_size,'sha256':sha(actual)}
            db.put('diag_pause_after_work',{'operacion':'pausar'})
            if cut:os.kill(partial['pid'],signal.SIGTERM);records['own_worker_pid_terminated']=partial['pid']
            records['work_terminal']=wait('diag_work');records['pause_terminal']=wait('diag_pause_after_work')
            records['duplicate_same_id']=db.put('diag_work',payload)
            records['before_stop']=db.get_meta('owner');db.put('diag_stop',{'operacion':'detener'});records['stop']=wait('diag_stop');owner.wait(timeout=20)
            records['owner_returncode']=owner.returncode;owner=None
            records['after_stop']=db.get_meta('owner');records['output_files_after_first_process']=[{'file':p.relative_to(work).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(work.rglob('*'))if p.is_file()]
            # Same imported diagnostic life, not another import or old-state retry.
            records['next_process']=cli(['mente-unificada-iniciar','--vida',life,'--backend','mente_unificada','--pausado','--max-segundos','2'],timeout=15)
            records['after_reload']=db.get_meta('owner');records['work_after_reload']=db.get('diag_work')
            records['output_files_after_reload']=[{'file':p.relative_to(work).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(work.rglob('*'))if p.is_file()]
            artifact=output/(label+'_'+actual.name);shutil.copyfile(actual,artifact)
            records['exported_actual_worker_output']={'file':artifact.name,'bytes':artifact.stat().st_size,'sha256':sha(artifact)}
        except Exception as error:
            records['error']={'type':type(error).__name__,'detail':str(error)}
            if owner and owner.poll()is None and db:
                try:db.put('diag_emergency_stop',{'operacion':'detener'});owner.wait(timeout=25)
                except Exception:records['owner_still_finishing_preserved_operation']=True
        records['commands']=commands;records['host_seconds']=time.monotonic()-start;return records
    arms.append(arm('CUT',True));arms.append(arm('SHAM',False))
    result={'schema':'DEE.unified.actual_worker_interruption.v1','fixture':info,'arms':arms,'host_seconds':time.monotonic()-started,
        'scope':'Diagnostic imported worlds, never MAIN. Actual file written before selective external worker termination; matched sham acknowledges normally. Fixed omitted native outcome return in both arms isolates transport fault, not cognitive learning. Uncertain outcome must remain paused and unretried after reload.'}
    target=output/'INTERRUPCION.json.gz'
    with gzip.GzipFile(filename=str(target),mode='wb',mtime=0)as f:f.write((json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps({'primary':str(target),'sha256':sha(target),'arm_errors':[x.get('error')for x in arms]}));return any('error'in x for x in arms)


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    q=sub.add_parser('preparar');q.add_argument('--sistema',type=Path,required=True);q.add_argument('--par',type=Path,required=True);q.add_argument('--salida',type=Path,required=True)
    q=sub.add_parser('ejecutar');q.add_argument('--fixture',type=Path,required=True);q.add_argument('--salida',type=Path,required=True)
    a=p.parse_args()
    if a.command=='preparar':print(json.dumps(prepare(a.sistema,a.par,a.salida),ensure_ascii=False));return 0
    return run_fixture(a.fixture,a.salida)


if __name__=='__main__':raise SystemExit(main())
