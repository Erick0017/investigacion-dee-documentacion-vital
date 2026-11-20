"""One actual APD05_MAIN continuation. Existing single-owner/queue semantics.

The JSON is a fixed curriculum, never a runtime decision policy. Native output
is authoritative; this driver does not choose an alternative after failure.
"""
import argparse,json,sys,time,hashlib,shutil,os,traceback
from pathlib import Path
from datetime import datetime,timezone

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
SYSTEM=ROOT/'sistema'
PLAN=HERE/'PROTOCOLO_MAIN_VIGENCIA_R02.json'

def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,value):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
def append(p,v):
    with Path(p).open('a',encoding='utf8',newline='\n')as f:f.write(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n')

def worker(a):
    plan=read(PLAN);out=SYSTEM/'estado/observatorios/APD05_MAIN_VIGENCIA_R02';out.mkdir(parents=True,exist_ok=False)
    code_hash=sha(__file__);plan_hash=sha(PLAN)
    sys.path[:0]=[str(SYSTEM),str(SYSTEM/'app')]
    for v in('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[v]='1'
    from app import process_control as pc
    pc.protect_current(output=out/'RECURSOS_NATIVE.json',memory_limit=plan['native_owner_memory_bytes'])
    from app.mundo_genesis_apd05 import GenesisNativeWorld
    from app.servicio_persistente import PersistentService
    from app.cola_local import QueueDB
    from app.lives import Store
    store=Store(SYSTEM);card=store.record(plan['life'])
    if card['snapshot_sha256']!=plan['opening_snapshot_sha256']or card['physical']['tick']!=plan['opening_last_STOP_tick']:
        raise ValueError('Actual MAIN already continued or differs; no earlier snapshot substituted')
    put(out/'FUENTES_PREVIAS.json',{'driver_sha256':code_hash,'plan_sha256':plan_hash,'source':{str(p.relative_to(SYSTEM)):sha(p)for p in(SYSTEM/'app/mundo_genesis_apd05.py',SYSTEM/'capacidades/percepcion_vigencia_apd05.py',SYSTEM/'capacidades/percepcion_cruda_fi01.py')},'starting_record':card})
    world=GenesisNativeWorld(SYSTEM,plan['life'],'mente_unificada').open();queue=QueueDB(world.folder/'cola.sqlite3')
    service=PersistentService(world,queue,start_paused=True,idle_ticks=1,idle_seconds=.1,save_seconds=3600)
    service.restore_transport();service.publish();rows=[]
    def perform(payload,label,n):
        identifier='apd05_main_version_r02_'+str(n).zfill(3)
        world.atomic_json(out/'PROGRESO.json',{'label':label,'id':identifier,'wall_monotonic':time.monotonic(),'tick':world.tick,'completed':False})
        admission=queue.put(identifier,payload)
        if admission.get('admission')!='queued':raise ValueError('No new single admission: '+str(admission))
        row=queue.next(paused=False)
        if row is None or row['id']!=identifier:raise ValueError('Unexpected queue order; no retry')
        service.perform(row);receipt=queue.get(identifier);value={'label':label,'id':identifier,'literal_payload':payload,'admission':admission,'transport':receipt}
        append(out/'EVENTOS.jsonl',value);rows.append(value)
        world.atomic_json(out/'PROGRESO.json',{'label':label,'id':identifier,'wall_monotonic':time.monotonic(),'tick':world.tick,'completed':True})
        if receipt['status']!='completed':raise RuntimeError('Preserved status '+receipt['status'])
    try:
        if queue.outstanding():raise ValueError('MAIN has pending/uncertain transport; no new events')
        put(out/'ESTADO_INICIAL.json',world.fingerprint())
        for n,event in enumerate(plan['fixed_events'],1):
            perform({'operacion':'sesion','situaciones':[event['row']],'retorno':'omit','actuador':'closed'},event['label'],n)
        perform({'operacion':'guardar'},'save',101);perform({'operacion':'detener'},'stop',102)
        service.checkpoint({'kind':'PERSISTENT_GRACEFUL_CLOSE','source':'APD05_MAIN_VERSION_R02'});service.publish()
        exported=world.export_pair('APD05_MAIN_VERSION_R02_COMPLETO_POSTSTOP',queue)
        put(out/'RESULTADO.json',{'life':world.life,'physical':world.fingerprint(),'complete_pair':exported,'events_completed':len(rows),'stop_confirmed':service.stop,'world_id':world.rec['world_id'],'no_reimport_or_restore':True,'not_a_scientific_PASS':True})
    except BaseException as exc:
        failure={'error':repr(exc),'traceback':traceback.format_exc(),'tick':world.tick,'events_completed':len(rows),'no_restore':True}
        try:
            service.stop=True;failure['checkpoint']=service.checkpoint({'kind':'FAILED_APD05_VERSION_PRESERVED'});service.publish()
            failure['pair']=world.export_pair('APD05_MAIN_VERSION_R02_FALLO_COMPLETO',queue)
        except Exception as save:failure['preservation_error']=repr(save)
        put(out/'FALLO_PRESERVADO.json',failure);raise
    finally:world.close()

def main():
    p=argparse.ArgumentParser();p.add_argument('--worker',action='store_true');p.add_argument('--root-go',required=True);a=p.parse_args()
    if a.root_go!='APD05_MAIN_VERSION_ACCESS_R02_APPROVED':raise ValueError('Explicit RootGO required')
    if a.worker:return worker(a)
    plan=read(PLAN);out=ROOT/'evidencia/campanas/APD05_GENESIS_SIN_LLM/MAIN_VIGENCIA_R02';out.mkdir(parents=True,exist_ok=False)
    for source in(Path(__file__),PLAN,SYSTEM/'app/mundo_genesis_apd05.py',SYSTEM/'capacidades/percepcion_vigencia_apd05.py',SYSTEM/'app/cola_local.py',SYSTEM/'app/protocolo_apd05.py'):
        shutil.copy2(source,out/source.name)
    sys.path.insert(0,str(SYSTEM));from app import process_control as pc
    started=time.monotonic();timeout=None
    with(out/'STDOUT.txt').open('x',encoding='utf8')as stdout,(out/'STDERR.txt').open('x',encoding='utf8')as stderr:
        proc,job,name=pc.spawn_owned([sys.executable,'-I','-B',str(Path(__file__)),'--worker','--root-go',a.root_go],cwd=ROOT,stdout=stdout,stderr=stderr,memory_limit=plan['outer_tree_memory_bytes'])
        try:
            progress_path=SYSTEM/'estado/observatorios/APD05_MAIN_VIGENCIA_R02/PROGRESO.json'
            while proc.poll()is None:
                elapsed=time.monotonic()-started;current=read(progress_path)if progress_path.exists()else{}
                if elapsed>plan['whole_prefix_guard_seconds']:timeout='whole_prefix'
                if current and not current.get('completed')and time.monotonic()-current['wall_monotonic']>plan['per_operation_guard_seconds']:timeout='per_operation'
                if timeout:pc.terminate_job(job,124);proc.wait(30);break
                append(out/'RECURSOS_ARBOLES.jsonl',{'wall_seconds':elapsed,**pc.job_resources(job)});time.sleep(2)
            result={'exit_code':proc.returncode,'timeout':timeout,'wall_seconds':time.monotonic()-started,'resources':pc.job_resources(job),'job':name,'energy':'NO_MEDIDA','nested_scope_not_added':True}
            put(out/'SUPERVISION.json',result)
        finally:pc.close_job(job)
    source=SYSTEM/'estado/observatorios/APD05_MAIN_VIGENCIA_R02'
    if source.exists():shutil.copytree(source,out/'PRIMARIOS')
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
