"""Prospective short service window of the actual shared MU_MAIN trajectory."""
import argparse,gzip,hashlib,json,shutil,subprocess,sys,time
from datetime import datetime
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cola_local import QueueDB
from importacion_emparejada import verify_export


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def card_summary(path):
    j=json.loads(path.read_bytes());return {k:j[k]for k in('life_id','world_id','profile','parent','snapshot','snapshot_sha256','physical')}|{'operations_count':len(j.get('operations',[]))}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    system=a.sistema.resolve();out=a.salida.resolve();out.mkdir(parents=True,exist_ok=False);script=system/'gestionar.py';life='MU_MAIN';process=None;q=None
    if(system/'estado/locks/MU_MAIN.lock').exists():raise ValueError('Another writer still owns MU_MAIN; do not replace or interrupt it')
    pre=card_summary(system/'estado/vidas/MU_MAIN/VIDA.json');sources=[]
    for relative in('gestionar.py','app/lives.py','app/servicio_persistente.py','app/cola_local.py','app/cliente_mente_unificada.py','app/importacion_emparejada.py','capacidades/mente_acumulativa_r02.py','capacidades/mente_unificada_01.py','capacidades/selector_acrecion_nativo.py','capacidades/eo02_trabajador_local.py'):
        f=system/relative;target=out/'codigo'/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,target);sources.append({'file':relative,'bytes':f.stat().st_size,'sha256':sha(f)})
    shutil.copyfile(Path(__file__),out/'codigo/prueba_main_unificada.py')
    protected={str(p):sha(p)for p in(system/'estado/ACTIVO.json',system/'estado/vidas/MA02_MAIN_5/VIDA.json',system/'estado/vidas/E1_SOCIAL_11/VIDA.json')}
    protocol={'schema':'DEE.unified.service.prospective_main_window.v1','life_id':life,'pre':pre,'backend':'mente_unificada',
        'fixed_order':[{'modo':'trabajo','valores':[3,11]},{'modo':'memoria','contexto':'zeta'},'>=10 real idle ticks',{'modo':'trabajo','valores':[8,19]},{'modo':'memoria','contexto':'alfa'},{'modo':'memoria','contexto':'gamma'},'pause','paired export','save','stop'],
        'host_min_window_seconds':25,'max_owner_seconds':50,'interval_seconds':.1,'idle_quantum_ticks':1,'checkpoint_seconds':10,
        'no_teaching_or_target_supplied':True,'assistance':'Host offers literal public work values and explicitly initiates three old-context memory queries; selector choice is read from fixed physical actuator sites. Calendar and phase are prepared technical controls.'}
    (out/'PROTOCOLO.json').write_text(json.dumps(protocol,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    records={};checks=[];started=time.monotonic();commands=[]
    def check(label,value):checks.append({'check':label,'observed':bool(value)})
    def wait(identifier):
        limit=time.monotonic()+20
        while time.monotonic()<limit:
            row=q.get(identifier)
            if row and row['status']in('completed','failed_preserved','uncertain','rejected_invalid'):
                records[identifier]=row
                if row['status']!='completed':raise RuntimeError('Service request not completed: '+json.dumps(row))
                return json.loads(row['result'])
            time.sleep(.03)
        raise TimeoutError(identifier)
    def submit(identifier,payload):q.put(identifier,payload);return wait(identifier)
    try:
        argv=[sys.executable,'-I','-B','-X','utf8',str(script),'mente-unificada-iniciar','--vida',life,'--backend','mente_unificada','--intervalo','0.1','--guardar-cada','10','--max-segundos','50']
        launched=time.time();process=subprocess.Popen(argv,text=True,encoding='utf8',stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        path=system/'estado/servicios_persistentes'/life/'cola.sqlite3';limit=time.monotonic()+12
        while time.monotonic()<limit:
            if process.poll()is not None:raise RuntimeError('Owner failed: '+str(process.communicate()))
            if path.is_file():
                q=QueueDB(path);owner=q.get_meta('owner')
                if owner and owner.get('running')and owner.get('wall_utc')and datetime.fromisoformat(owner['wall_utc']).timestamp()>=launched:break
            time.sleep(.03)
        else:raise TimeoutError('Main service readiness')
        records['owner_initial']=owner;check('exact main identity loaded',owner['life_id']==life and owner['tick']==pre['physical']['tick'])
        submit('mu_a50_work1',{'operacion':'sesion','situaciones':[{'modo':'trabajo','valores':[3,11]}]})
        submit('mu_a50_zeta',{'operacion':'sesion','situaciones':[{'modo':'memoria','contexto':'zeta'}]})
        idle_before=q.get_meta('owner')['idle_ticks'];limit=time.monotonic()+8
        while time.monotonic()<limit:
            if q.get_meta('owner')['idle_ticks']>=idle_before+10:break
            time.sleep(.1)
        records['idle_after_zeta']=q.get_meta('owner');check('at least ten real native idle ticks',records['idle_after_zeta']['idle_ticks']>=idle_before+10)
        submit('mu_a50_work2',{'operacion':'sesion','situaciones':[{'modo':'trabajo','valores':[8,19]}]})
        submit('mu_a50_old_memory',{'operacion':'sesion','situaciones':[{'modo':'memoria','contexto':'alfa'},{'modo':'memoria','contexto':'gamma'}]})
        while time.monotonic()-started<25:time.sleep(.2)
        pause=submit('mu_a50_pause',{'operacion':'pausar'});time.sleep(.7);records['paused']=q.get_meta('owner')
        check('pause exact tick stable',pause['before_tick']==pause['after_tick']==records['paused']['tick'])
        exported=submit('mu_a50_export',{'operacion':'exportar'});directory=Path(exported['paired_export']['directory']);root,m,v=verify_export(directory)
        records['paired_export']={'manifest':m,'verification':v};check('complete paired snapshot at real main tick',m['physical']['tick']==pause['after_tick']and m['life_id']==life)
        submit('mu_a50_save',{'operacion':'guardar'});submit('mu_a50_stop',{'operacion':'detener'})
        stdout,stderr=process.communicate(timeout=12);commands.append({'argv':argv,'returncode':process.returncode,'stdout':stdout,'stderr':stderr});process=None
        records['owner_final']=q.get_meta('owner');final=card_summary(system/'estado/vidas/MU_MAIN/VIDA.json');records['final']=final
        check('world never reinitialised or forked during window',final['life_id']==pre['life_id']and final['parent']==pre['parent']and final['physical']['tick']>pre['physical']['tick'])
        check('all requests finished and no uncertain outcomes',not q.outstanding()and not records['owner_final']['uncertain_external_result'])
        check('full final snapshot hash correct',sha(system/final['snapshot'])==final['snapshot_sha256'])
        check('protected defaults and source lives unchanged',all(sha(Path(k))==v for k,v in protected.items()))
    except Exception as error:
        records['harness_error']={'type':type(error).__name__,'detail':str(error)}
        if process and process.poll()is None:
            try:
                q.put('mu_a50_emergency_stop',{'operacion':'detener'});stdout,stderr=process.communicate(timeout=12)
                commands.append({'kind':'OWN_OWNER_EMERGENCY_STOP','returncode':process.returncode,'stdout':stdout,'stderr':stderr})
            except Exception:process.terminate();process.communicate(timeout=5);records['forced_own_process_stop']=True
    value={'schema':'DEE.unified.service.actual_main_window.v1','protocol':protocol,'records':records,'checks':checks,'commands':commands,'source':sources,
        'host_seconds':time.monotonic()-started,'protected_before':protected,'protected_after':{k:sha(Path(k))for k in protected},
        'scope':'One actual continuous MU_MAIN window, not two replicas. Host initiates requests and memory contexts, native selector determines actuator. This is not the final sixty-minute trial. Success/usefulness must be recalculated from native RAW and actual worker receipts, not these operational checks.'}
    target=out/'MAIN_SERVICIO.json.gz'
    with gzip.GzipFile(filename=str(target),mode='wb',mtime=0)as f:f.write((json.dumps(value,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps({'primary':str(target),'sha256':sha(target),'checks':checks,'error':records.get('harness_error'),'host_seconds':value['host_seconds'],'final':records.get('final')},ensure_ascii=False))
    return bool(records.get('harness_error'))or not all(c['observed']for c in checks)


if __name__=='__main__':raise SystemExit(main())
