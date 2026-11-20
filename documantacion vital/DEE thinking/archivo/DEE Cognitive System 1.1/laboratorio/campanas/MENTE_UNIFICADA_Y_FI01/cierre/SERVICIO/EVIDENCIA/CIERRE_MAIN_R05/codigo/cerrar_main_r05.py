"""Complete already queued technical controls, never repeat the R04 actions."""
import argparse,gzip,hashlib,json,shutil,subprocess,sys,time
from datetime import datetime
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cola_local import QueueDB
from importacion_emparejada import verify_export


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    system=a.sistema.resolve();out=a.salida.resolve();out.mkdir(parents=True,exist_ok=False);q=QueueDB(system/'estado/servicios_persistentes/MU_MAIN/cola.sqlite3')
    if q.get('mu_a50_pause')['status']!='queued':raise ValueError('Original pending pause differs; do not repeat or replace it')
    initial=q.get_meta('owner');commands=[];records={'before':initial};checks=[];process=None;started=time.monotonic()
    for relative in('gestionar.py','app/servicio_persistente.py','app/cola_local.py','app/finalizar_protocolo.py','app/lives.py'):
        target=out/'codigo'/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(system/relative,target)
    shutil.copyfile(Path(__file__),out/'codigo/cerrar_main_r05.py')
    def wait(identifier):
        limit=time.monotonic()+65
        while time.monotonic()<limit:
            row=q.get(identifier)
            if row and row['status']in('completed','failed_preserved','uncertain','rejected_invalid'):
                records[identifier]=row
                if row['status']!='completed':raise RuntimeError(json.dumps(row))
                return json.loads(row['result'])
            time.sleep(.1)
        raise TimeoutError(identifier)
    def submit(identifier,op):q.put(identifier,{'operacion':op});return wait(identifier)
    def check(label,value):checks.append({'check':label,'observed':bool(value)})
    try:
        argv=[sys.executable,'-I','-B','-X','utf8',str(system/'gestionar.py'),'mente-unificada-iniciar','--vida','MU_MAIN','--backend','mente_unificada','--intervalo','0.1','--guardar-cada','3600','--max-segundos','180']
        process=subprocess.Popen(argv,text=True,encoding='utf8',stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        pause=wait('mu_a50_pause');check('original pause resumed exactly once',pause['before_tick']==pause['after_tick']==initial['tick'])
        time.sleep(.7);check('pause remains physically stationary',q.get_meta('owner')['tick']==initial['tick'])
        export=submit('mu_a51_export','exportar');root,manifest,verified=verify_export(export['paired_export']['directory'])
        records['export']={'manifest':manifest,'verification':verified};check('native tick unchanged in paired export',manifest['physical']['tick']==initial['tick'])
        submit('mu_a51_save','guardar');submit('mu_a51_stop','detener');stdout,stderr=process.communicate(timeout=65)
        commands.append({'argv':argv,'returncode':process.returncode,'stdout':stdout,'stderr':stderr});process=None
        records['stopped']=q.get_meta('owner');check('no repeated work or memory request',records['stopped']['material_calls']==initial['material_calls'])
        argv=[sys.executable,'-I','-B','-X','utf8',str(system/'gestionar.py'),'mente-unificada-finalizar-protocolo','--vida','MU_MAIN']
        r=subprocess.run(argv,text=True,encoding='utf8',capture_output=True,timeout=90);commands.append({'argv':argv,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
        if r.returncode:raise RuntimeError(r.stderr)
        records['explicit_epoch_close']=json.loads(r.stdout);check('explicit closure changed no native physical fields',records['explicit_epoch_close']['result']['physical_before']==records['explicit_epoch_close']['result']['physical_after'])
        check('transport closed without pending or uncertain rows',not q.outstanding()and q.get_meta('protocol_admission_closed')is True)
    except Exception as error:
        records['harness_error']={'type':type(error).__name__,'detail':str(error)}
        if process and process.poll()is None:
            # A late stop has its own ID. Never replay work, remove a lock or rewind.
            q.put('mu_a51_emergency_stop',{'operacion':'detener'})
            try:stdout,stderr=process.communicate(timeout=65);commands.append({'kind':'OWN_OWNER_STOP','returncode':process.returncode,'stdout':stdout,'stderr':stderr})
            except Exception:records['owner_still_finishing_uninterrupted_operation']=True
    value={'schema':'DEE.unified.service.technical_closure.v1','records':records,'checks':checks,'commands':commands,'host_seconds':time.monotonic()-started,
        'no_new_material_requests':True,'scope':'Continuation of already queued pause and technical save/export/stop/explicit epoch closure only. Not new learning, no original action retry and no silent rollback.'}
    target=out/'CIERRE_MAIN.json.gz'
    with gzip.GzipFile(filename=str(target),mode='wb',mtime=0)as f:f.write((json.dumps(value,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps({'primary':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'checks':checks,'error':records.get('harness_error'),'host_seconds':value['host_seconds']},ensure_ascii=False))
    return bool(records.get('harness_error'))or not all(c['observed']for c in checks)


if __name__=='__main__':raise SystemExit(main())
