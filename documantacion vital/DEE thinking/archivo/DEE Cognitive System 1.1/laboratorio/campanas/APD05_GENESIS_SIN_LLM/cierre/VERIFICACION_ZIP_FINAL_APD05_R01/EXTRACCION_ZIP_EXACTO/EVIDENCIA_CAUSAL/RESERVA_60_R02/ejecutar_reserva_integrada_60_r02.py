"""One frozen one-hour curriculum, existing owner/queue and passive viewer.

The producer enqueues fixed literal public events. It never reads an answer to
select the next input. The only owner executes Native operations and captures
coherent observer frames. No actor/module is patched after this run begins.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,shutil,sys,threading,time,traceback

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
SYSTEM=ROOT/'sistema'
PLAN=HERE/'PROTOCOLO_RESERVA_INTEGRADA_60_R02.json'
TAG='RESERVA_INTEGRADA_60_R02'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def stamp():return datetime.now(timezone.utc).isoformat()
def write(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
def append(p,v):
    with Path(p).open('a',encoding='utf8',newline='\n')as f:f.write(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n')

def worker():
    plan=read(PLAN)
    out=SYSTEM/'estado/observatorios'/('APD05_'+TAG);out.mkdir(parents=True,exist_ok=False)
    sources=[Path(__file__),PLAN,SYSTEM/'app/servicio_persistente.py',SYSTEM/'app/cola_local.py',
        SYSTEM/'app/mundo_genesis_apd05.py',SYSTEM/'app/protocolo_apd05.py',
        SYSTEM/'capacidades/percepcion_vigencia_apd05.py',SYSTEM/'capacidades/percepcion_cruda_fi01.py',
        SYSTEM/'capacidades/lexico_compartido_apd04.py',SYSTEM/'capacidades/ecosistema_apd04.py',
        ROOT/'aplicacion/GENESIS/propietario_genesis.py',ROOT/'aplicacion/GENESIS/visor_pasivo.py',
        ROOT/'aplicacion/GENESIS/genesis.py',ROOT/'aplicacion/GENESIS/app.js']
    # Capture all bytes before Native access guard. No later read of LAB/GUI.
    frozen=[]
    for i,source in enumerate(sources):
        dest=out/'FUENTES_EJECUTADAS'/(str(i).zfill(2)+'_'+source.name);dest.parent.mkdir(exist_ok=True)
        shutil.copy2(source,dest);frozen.append({'original':str(source),'copy':str(dest.relative_to(out)),'sha256':sha(source),'bytes':source.stat().st_size})
    write(out/'FUENTES_CONGELADAS.json',frozen)
    for key in('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
    sys.path[:0]=[str(SYSTEM),str(SYSTEM/'app'),str(ROOT/'aplicacion/GENESIS')]
    from app import process_control as pc
    pc.protect_current(output=out/'RECURSOS_NATIVE.json',memory_limit=plan['native_owner_memory_bytes'])
    from app.lives import Store
    from app.cola_local import QueueDB
    from app.mundo_genesis_apd05 import GenesisNativeWorld
    from propietario_genesis import ViewerService
    from app.servicio_persistente import now
    store=Store(SYSTEM);before=store.record(plan['life'])
    if before['snapshot_sha256']!=plan['opening_snapshot_sha256'] or before['physical']['tick']!=plan['opening_tick']:
        raise ValueError('MAIN changed since frozen opening. No substitute snapshot or favorable rewind.')
    write(out/'ESTADO_PREVIO.json',before)
    world=GenesisNativeWorld(SYSTEM,plan['life'],'mente_unificada').open()
    queue=QueueDB(world.folder/'cola.sqlite3')
    pending=queue.outstanding()
    actual=[{'id':r['id'],'payload_sha':r['payload_sha']}for r in pending]
    if actual!=plan['inherited_pending'] or any(r['status']!='queued'for r in pending):
        world.close();raise ValueError('Not the exact three preserved R01 queued requests. No discard, retry, substitute or new curriculum admitted.')
    queue.meta('genesis_view_config',{'enabled':True,'interval_seconds':plan['viewer_interval_seconds'],'max_points':plan['viewer_max_points'],'universe':'raw_nonzero'})
    class ReservedViewerService(ViewerService):
        def run(self):
            # Existing PersistentService.run operation/idle semantics, unchanged.
            # The sole addition seals a full pair BEFORE releasing this writer.
            self.restore_transport();self.publish()
            try:
                while not self.stop:
                    t=time.monotonic()
                    if t-self.started>=self.max_seconds:self.stop=True;break
                    row=self.queue.next(paused=self.paused or self.uncertain)
                    if row:self.perform(row);continue
                    if not self.paused and not self.uncertain and t>=self.next_idle:
                        self.world.advance(self.idle_ticks);self.idle_total+=self.idle_ticks
                        self.next_idle=time.monotonic()+self.idle_seconds
                    if time.monotonic()-self.last_save>=self.save_seconds:
                        self.checkpoint({'kind':'PERSISTENT_PERIODIC_IDLE_SAVE','idle_ticks':self.idle_total})
                    if time.monotonic()-self.last_publish>=.5:self.publish()
                    time.sleep(min(.05,self.idle_seconds))
            finally:
                self.stop=True
                try:
                    self.checkpoint({'kind':'PERSISTENT_GRACEFUL_CLOSE','idle_ticks':self.idle_total,'campaign':'APD05_'+TAG});self.publish()
                    ending={'utc':stamp(),'status':self.status(),'physical':self.world.fingerprint(),
                        'record':self.world.rec,'outstanding':self.queue.outstanding(),'observer':self.queue.get_meta('genesis_observer',{}),
                        'actual_wall_before_full_export_seconds':time.monotonic()-self.started}
                    ending['pair']=self.world.export_pair('APD05_'+TAG+'_COMPLETO_FINAL',self.queue)
                    write(out/'CIERRE_REAL.json',ending)
                finally:self.world.close()
    service=ReservedViewerService(world,queue,idle_ticks=plan['native_idle_ticks'],idle_seconds=plan['host_idle_seconds'],
        save_seconds=plan['periodic_checkpoint_seconds'],max_seconds=plan['wall_window_seconds'],start_paused=False,viewer=True)
    sent=[{'id':r['id'],'label':'inherited_R01_pending_consumed_once','payload':json.loads(r['payload']),
           'original_arrived_utc':r['arrived_utc'],'original_payload_sha':r['payload_sha'],
           'not_put_in_R02':True}for r in pending]
    resume_id='apd05_reserva60_r02_explicit_initial_reanudar'
    resume_payload={'operacion':'reanudar'}
    resume_admission=queue.put(resume_id,resume_payload)
    if resume_admission.get('admission')!='queued':world.close();raise ValueError('Explicit resume was not a unique new control')
    sent.append({'id':resume_id,'label':'explicit_operator_resume_not_native_initiative','payload':resume_payload,'admission':resume_admission})
    write(out/'PENDIENTES_HEREDADOS_Y_RESUME.json',{'inherited':pending,'resume':sent[-1],'no_reenqueue_of_R01':True})
    producer_done=threading.Event()
    def producer():
        try:
            for i,event in enumerate(plan['events']):
                while time.monotonic()-service.started<event['at'] and not service.stop:
                    time.sleep(min(.2,max(.001,event['at']-(time.monotonic()-service.started))))
                if service.stop:break
                payloads=([{'operacion':'avanzar','ticks':event['advance']}] if 'advance'in event else
                    [{'operacion':'sesion','situaciones':[row],'actuador':'closed','retorno':event.get('retorno','omit')} for row in event['rows']])
                for j,payload in enumerate(payloads):
                    identifier='apd05_reserva60_r02_'+str(i).zfill(2)+'_'+str(j)
                    item={'id':identifier,'label':event['label'],'scheduled_offset_seconds':event['at'],
                        'actual_arrival_offset_seconds':time.monotonic()-service.started,'utc':stamp(),'payload':payload}
                    try:item['admission']=queue.put(identifier,payload)
                    except Exception as exc:item['admission_error']={'type':type(exc).__name__,'detail':str(exc),'not_retried':True}
                    sent.append(item);append(out/'ADMISIONES_PROGRAMADAS.jsonl',item)
        except BaseException as exc:write(out/'ERROR_PRODUCTOR.json',{'error':repr(exc),'traceback':traceback.format_exc()})
        finally:producer_done.set()
    thread=threading.Thread(target=producer,name='fixed_literal_curriculum_not_actor',daemon=True);thread.start()
    write(out/'ARRANQUE_RESERVA.json',{'utc':stamp(),'life':world.life,'world_id':world.rec['world_id'],'tick':world.tick,
        'wall_window_seconds':plan['wall_window_seconds'],'native_runtime_loads':1,'plan_sha256':frozen[1]['sha256'],
        'observer_interval':plan['viewer_interval_seconds'],'schedule_not_an_acquired_policy':True})
    try:service.run()
    except BaseException as exc:
        write(out/'ERROR_OWNER.json',{'error':repr(exc),'traceback':traceback.format_exc(),'no_restart_or_restore':True});raise
    finally:
        thread.join(timeout=2)
        for item in sent:
            receipt=queue.get(item['id'])
            append(out/'EVENTOS.jsonl',{**item,'transport':receipt})
        write(out/'FIN_PRODUCTOR.json',{'done':producer_done.is_set(),'events_prescribed':len(plan['events']),
            'transport_requests_attempted':len(sent),'no_reenqueue_or_reteaching_after_failure':True,'utc':stamp()})

def supervise():
    p=read(PLAN);out=ROOT/'evidencia/campanas/APD05_GENESIS_SIN_LLM'/TAG;out.mkdir(parents=True,exist_ok=False)
    shutil.copy2(__file__,out/Path(__file__).name);shutil.copy2(PLAN,out/PLAN.name)
    sys.path.insert(0,str(SYSTEM));from app import process_control as pc
    begin=time.monotonic();timed=None
    with(out/'STDOUT.txt').open('x',encoding='utf8')as stdout,(out/'STDERR.txt').open('x',encoding='utf8')as stderr:
        proc,job,name=pc.spawn_owned([sys.executable,'-I','-B','-W','error',str(Path(__file__)),'--worker','--root-go','APD05_60_MINUTE_NATIVE_RESERVE_R02_APPROVED'],cwd=ROOT,stdout=stdout,stderr=stderr,memory_limit=p['outer_tree_memory_bytes'])
        try:
            while proc.poll()is None:
                elapsed=time.monotonic()-begin
                if elapsed>p['outer_guard_seconds']:timed='outer4500'
                # Read-only transport timestamps; never reenqueue a request.
                qpath=SYSTEM/'estado/servicios_persistentes/APD05_MAIN/cola.sqlite3'
                if qpath.is_file():
                    import sqlite3
                    try:
                        con=sqlite3.connect('file:'+qpath.as_posix()+'?mode=ro',uri=True,timeout=2)
                        processing=con.execute("SELECT id,started_utc FROM requests WHERE status='processing' AND id LIKE 'apd05_reserva60_%'").fetchall();con.close()
                        for identifier,started in processing:
                            if started and (datetime.now(timezone.utc)-datetime.fromisoformat(started)).total_seconds()>p['per_material_guard_seconds']:timed='material900:'+identifier
                    except sqlite3.Error:pass
                append(out/'RECURSOS_ARBOLES.jsonl',{'utc':stamp(),'elapsed_seconds':elapsed,**pc.job_resources(job)})
                if timed:pc.terminate_job(job,124);proc.wait(30);break
                time.sleep(5)
            write(out/'SUPERVISION.json',{'exit_code':proc.returncode,'timeout':timed,'wall_seconds':time.monotonic()-begin,
                'resources':pc.job_resources(job),'owned_job':name,'energy':'NO_MEDIDA','nested_scopes_not_added':True})
        finally:pc.close_job(job)
    source=SYSTEM/'estado/observatorios'/('APD05_'+TAG)
    if source.exists():shutil.copytree(source,out/'PRIMARIOS')
    print(json.dumps(read(out/'SUPERVISION.json'),ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--worker',action='store_true');parser.add_argument('--root-go',required=True);args=parser.parse_args()
    if args.root_go!='APD05_60_MINUTE_NATIVE_RESERVE_R02_APPROVED':raise ValueError('Root prospective GO is required')
    worker() if args.worker else supervise()
