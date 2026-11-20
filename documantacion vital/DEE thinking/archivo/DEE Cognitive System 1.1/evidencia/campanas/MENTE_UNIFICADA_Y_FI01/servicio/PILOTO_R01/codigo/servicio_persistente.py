"""Single-owner local DEE service; prepared transport, not a cognitive selector.

Candidate implementation over the existing Store and MA02 capability. No daemon,
public port, shell command execution or automatic process restart is installed.
"""
import argparse,hashlib,json,os,sys,time,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cola_local import QueueDB,canonical,digest,now

KEY='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'


class NativeWorld:
    def __init__(self,system,life):
        self.system=Path(system).resolve();self.life=life;self.writer=None;self.rec=None;self.a=None;self.dirty=False
    def open(self):
        self.code_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in(Path(__file__),Path(__file__).with_name('cola_local.py'))}
        sys.path.insert(0,str(self.system))
        from app.lives import Store
        from app.native_tools import physical,atomic_json
        from dee_thinking.persistence import encode_metadata,decode_metadata
        from capacidades import mente_acumulativa_r02 as capability
        self.store=Store(self.system);record=self.store.record(self.life)
        self.writer=self.store.writer(record['world_id']);self.writer.__enter__()
        try:self.rec,self.a=self.store.load(self.life)
        except BaseException:self.writer.__exit__(*sys.exc_info());self.writer=None;raise
        self.physical=physical;self.atomic_json=atomic_json;self.encode=encode_metadata;self.decode=decode_metadata;self.capability=capability
        capability.get(self.a)  # Strict declared contract; no empty/T0 fallback.
        self.marker=self.store.life_dir(self.life)/'FUTURO_INTERRUMPIDO.json'
        self.folder=self.store.state/'servicios_persistentes'/self.rec['world_id'];self.folder.mkdir(parents=True,exist_ok=True)
        self.work_directory=self.store.state/'servicios_locales'/self.life
        from app.access_guard import install
        worker=[sys.executable,'-I','-B','-X','utf8',str(self.system/'capacidades/eo02_trabajador_local.py')]
        self.guard=install(self.system,external_command=worker)
        entries=dict(self.a.world.runtime.snapshot_metadata_entries)
        self.loaded_protocol=self.decode(entries[KEY])if KEY in entries else None
        return self
    @property
    def tick(self):return int(self.a.tick)
    def fingerprint(self):return self.physical(self.a.world)
    def before_mutation(self,kind,target=None):
        if not self.dirty:
            self.atomic_json(self.marker,{'schema':'DCS1.1.interrupted_persistent_future.v1','life_id':self.life,
                'last_committed_snapshot_sha256':self.rec['snapshot_sha256'],'last_committed_tick':self.rec['physical']['tick'],
                'uncommitted_native_future_possible':True,'operation':kind,'planned_target':target,'registered_utc':now(),
                'no_silent_checkpoint_rewind':'If this owner dies, normal Store.load is deliberately blocked. Diagnose or explicitly branch from a named full past.'})
            self.dirty=True
    def advance(self,ticks,kind='idle_continuous'):
        self.before_mutation(kind,self.tick+ticks)
        self.a.run_until(self.tick+ticks)  # Official OrganizationalWorld owner, not Runtime.run.
    def execute(self,payload):
        self.before_mutation('material_request')
        if payload['operacion']=='avanzar':
            self.advance(payload['ticks'],'explicit_advance');return {'real_ticks_advanced':payload['ticks'],'physical':self.fingerprint()}
        return self.capability.session(self.a,situations=payload['situaciones'],directory=self.work_directory,
            actuator=payload.get('actuador','closed'),feedback=payload.get('retorno','real'),detailed=False)
    def checkpoint(self,protocol,pending,operation):
        # Slots are reused; no unbounded native metadata ledger or hidden answers.
        self.a.world.runtime.set_snapshot_metadata(KEY,self.encode(protocol))
        for slot in range(16):
            value={'empty':True}if slot>=len(pending)else {'id':pending[slot]['id'],
                'payload':json.loads(pending[slot]['payload']),'payload_sha256':pending[slot]['payload_sha'],
                'transport_status':pending[slot]['status'],'arrival_utc':pending[slot]['arrived_utc']}
            self.a.world.runtime.set_snapshot_metadata(KEY+'.queue.'+str(slot),self.encode(value))
        self.rec=self.store.commit(self.rec,self.a,operation)
        if self.marker.exists():self.marker.unlink()
        self.dirty=False
        return {'life_id':self.life,'snapshot':self.rec['snapshot'],'snapshot_sha256':self.rec['snapshot_sha256'],'physical':self.rec['physical']}
    def close(self):
        if self.writer:self.writer.__exit__(None,None,None);self.writer=None


class PersistentService:
    def __init__(self,world,queue,*,idle_ticks=1,idle_seconds=.1,save_seconds=15,max_seconds=None):
        if type(idle_ticks)is not int or not 1<=idle_ticks<=67:raise ValueError('Idle quantum1..67 exact ticks.')
        if not .01<=idle_seconds<=60 or not .2<=save_seconds<=3600:raise ValueError('Explicit bounded host cadence/checkpoint interval required.')
        self.world=world;self.queue=queue;self.idle_ticks=idle_ticks;self.idle_seconds=idle_seconds
        self.save_seconds=save_seconds;self.max_seconds=max_seconds
        self.paused=False;self.stop=False;self.uncertain=False;self.idle_total=0;self.material_calls=0;self.checkpoints=0
        self.started=time.monotonic();self.last_save=self.started;self.next_idle=self.started+idle_seconds;self.last_publish=0
        self.current=None;self.owner_pid=os.getpid();self.last_receipt=None
    def protocol(self,receipt=None):
        return {'schema':'DEE.persistent_service.owner.v1','life_id':self.world.life,'pid_at_checkpoint':self.owner_pid,
            'source_sha256':getattr(self.world,'code_sha256',{}),
            'paused':self.paused,'uncertain_external_result':self.uncertain,'idle_ticks_per_quantum':self.idle_ticks,
            'idle_interval_microseconds':round(self.idle_seconds*1000000),'idle_total':self.idle_total,'material_calls':self.material_calls,
            'last_completed_receipt':receipt if receipt is not None else self.last_receipt,
            'queue_journal_required_for_transport_deduplication':True,
            'queue_not_cognitive_memory':'Current literal inputs are protocol state; IDs/journal/targets never choose a native answer.',
            'technical_control_precedence':'Pause/resume/save/stop preempt waiting material FIFO only at safe operation boundaries.',
            'wall_cadence_not_native_policy':'No catch-up bursts. Busy operations evolve through their official protocol; idle quanta evolve continuously.'}
    def status(self):
        return {'schema':'DEE.local.persistent.status.v1','life_id':self.world.life,'pid':self.owner_pid,
            'running':not self.stop,'paused':self.paused,'uncertain_external_result':self.uncertain,
            'tick':self.world.tick,'last_saved_tick':self.world.rec['physical']['tick'],
            'idle_ticks':self.idle_total,'material_calls':self.material_calls,'checkpoints':self.checkpoints,
            'queue':self.queue.counters(),'physical':self.world.fingerprint(),
            'host_elapsed_seconds':time.monotonic()-self.started,'wall_utc':now(),
            'single_native_adapter':True,'runtime_loads_in_this_process':1,'network_listener':False,
            'scope':'Passive external observation and transport status, not an extra native question.'}
    def publish(self):
        value=self.status();self.queue.meta('owner',value);self.last_publish=time.monotonic();return value
    def checkpoint(self,operation,receipt=None):
        pending=[r for r in self.queue.outstanding()if self.current is None or r['id']!=self.current['id']]
        if len(pending)>16:raise ValueError('Native queue snapshot slots exceeded; no silent loss.')
        result=self.world.checkpoint(self.protocol(receipt),pending,operation)
        self.last_save=time.monotonic();self.checkpoints+=1
        self.queue.meta('latest_checkpoint',result)
        return result
    def restore_transport(self):
        protocol=self.world.loaded_protocol
        unresolved=[r for r in self.queue.outstanding()if r['status']in('processing','uncertain')]
        receipt=(protocol or{}).get('last_completed_receipt')
        for row in unresolved:
            if receipt and row['id']==receipt['id']and row['payload_sha']==receipt['payload_sha256']:
                path=self.world.folder/'resultados'/(row['id']+'.json')
                if path.is_file()and hashlib.sha256(path.read_bytes()).hexdigest()==receipt['result_sha256']:
                    self.queue.finish(row['id'],'completed',json.loads(path.read_bytes()));continue
            self.queue.finish(row['id'],'uncertain',error={'reason':'Prior owner did not leave a matching committed result; do not repeat action.'})
            self.uncertain=True;self.paused=True
        if protocol:
            self.idle_total=protocol.get('idle_total',0);self.material_calls=protocol.get('material_calls',0)
            self.paused=self.paused or protocol.get('paused',False)
            self.uncertain=self.uncertain or protocol.get('uncertain_external_result',False)
    def perform(self,row):
        self.current=row;payload=json.loads(row['payload']);op=payload['operacion'];started=self.world.tick;execution_utc=now()
        try:
            if op=='pausar':self.paused=True;value={'technical_pause':True,'native_ticks_do_not_advance_while_paused':True}
            elif op=='reanudar':
                if self.uncertain:raise ValueError('Unresolved external outcome blocks automatic resume/retry; inspect preserved receipts.')
                self.paused=False;self.next_idle=time.monotonic()+self.idle_seconds;value={'technical_resume':True}
            elif op=='detener':self.stop=True;value={'graceful_stop':True,'no_autostart_or_restart':True}
            elif op=='guardar':value={'explicit_checkpoint':True}
            else:value=self.world.execute(payload);self.material_calls+=1
            result={'id':row['id'],'operation':op,'arrival_utc':row['arrived_utc'],'started_utc':execution_utc,'finished_execution_utc':now(),
                'before_tick':started,'after_tick':self.world.tick,'result':value,
                'host_elapsed_seconds':time.monotonic()-self.started,'scope':'Native result unchanged; request ID is transport only.'}
            out=self.world.folder/'resultados'/(row['id']+'.json');out.parent.mkdir(parents=True,exist_ok=True)
            data=(canonical(result)+'\n').encode('utf-8');out.write_bytes(data)
            receipt={'id':row['id'],'payload_sha256':row['payload_sha'],'result_sha256':hashlib.sha256(data).hexdigest()}
            saved=self.checkpoint({'kind':'PERSISTENT_'+op.upper(),'before_tick':started,'after_tick':self.world.tick,
                'transport_id':row['id'],'result':value},receipt)
            result['committed_snapshot']=saved
            self.last_receipt=receipt;self.queue.finish(row['id'],'completed',result)
        except Exception as error:
            work=any(q.get('modo')=='trabajo'or(q.get('modo')=='componer'and q.get('dominio'))for q in payload.get('situaciones',[]))
            self.uncertain=self.uncertain or work;self.paused=True
            info={'type':type(error).__name__,'detail':str(error),'native_tick_after_attempt':self.world.tick,
                'external_execution_may_be_uncertain':work,'no_retry_or_rollback':True}
            try:
                saved=self.checkpoint({'kind':'FAILED_PERSISTENT_'+op.upper(),'transport_id':row['id'],'error':info})
                info['failed_native_future_preserved']=saved
            except Exception as save_error:info['checkpoint_error']=str(save_error)
            self.queue.finish(row['id'],'uncertain'if work else'failed_preserved',error=info)
        finally:self.current=None;self.publish()
    def run(self):
        self.restore_transport();self.publish()
        try:
            while not self.stop:
                t=time.monotonic()
                if self.max_seconds is not None and t-self.started>=self.max_seconds:
                    self.stop=True;break
                row=self.queue.next(paused=self.paused or self.uncertain)
                if row:self.perform(row);continue
                if not self.paused and not self.uncertain and t>=self.next_idle:
                    self.world.advance(self.idle_ticks);self.idle_total+=self.idle_ticks
                    self.next_idle=time.monotonic()+self.idle_seconds
                if time.monotonic()-self.last_save>=self.save_seconds:
                    self.checkpoint({'kind':'PERSISTENT_PERIODIC_IDLE_SAVE','idle_ticks':self.idle_total})
                if time.monotonic()-self.last_publish>=.5:self.publish()
                time.sleep(min(.05,self.idle_seconds))
        except KeyboardInterrupt:self.stop=True
        finally:
            self.stop=True
            try:self.checkpoint({'kind':'PERSISTENT_GRACEFUL_CLOSE','idle_ticks':self.idle_total});self.publish()
            finally:self.world.close()
        return self.status()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--vida',required=True)
    p.add_argument('--ticks-ocio',type=int,default=1);p.add_argument('--intervalo',type=float,default=.1)
    p.add_argument('--guardar-cada',type=float,default=15);p.add_argument('--max-segundos',type=float)
    a=p.parse_args();world=NativeWorld(a.sistema,a.vida).open()
    queue=QueueDB(world.folder/'cola.sqlite3')
    service=PersistentService(world,queue,idle_ticks=a.ticks_ocio,idle_seconds=a.intervalo,
        save_seconds=a.guardar_cada,max_seconds=a.max_segundos)
    print(json.dumps(service.run(),ensure_ascii=False),flush=True)


if __name__=='__main__':main()
