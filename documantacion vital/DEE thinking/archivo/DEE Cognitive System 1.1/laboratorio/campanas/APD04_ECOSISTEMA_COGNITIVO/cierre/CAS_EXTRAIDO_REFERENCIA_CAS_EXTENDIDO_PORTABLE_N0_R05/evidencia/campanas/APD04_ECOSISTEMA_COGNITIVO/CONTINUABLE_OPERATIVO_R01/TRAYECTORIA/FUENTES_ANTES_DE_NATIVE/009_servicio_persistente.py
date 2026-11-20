"""Single-owner local DEE service; prepared transport, not a cognitive selector.

Candidate implementation over the existing Store and MA02 capability. No daemon,
public port, shell command execution or automatic process restart is installed.
"""
import argparse,hashlib,json,os,shutil,sys,time,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cola_local import QueueDB,canonical,digest,now

KEY='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'


class NativeWorld:
    def __init__(self,system,life,backend='ma02'):
        if backend not in('ma02','mente_unificada'):raise ValueError('Explicit admitted backend required; no response-based routing.')
        self.system=Path(system).resolve();self.life=life;self.backend=backend;self.writer=None;self.rec=None;self.a=None;self.dirty=False
    def open(self):
        if self.life in('E1_SOCIAL_11','MA02_MAIN_5','MA_MAIN_R9','MA_U0_ACUMULATIVO_AUX','EO02_MAIN'):
            raise ValueError('Protected documented original: create an explicit full fork before starting persistent evolution.')
        self.code_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in(Path(__file__),Path(__file__).with_name('cola_local.py'))}
        sys.path.insert(0,str(self.system))
        from app.lives import Store
        from app.native_tools import physical,atomic_json
        from dee_thinking.persistence import encode_metadata,decode_metadata
        if self.backend=='ma02':from capacidades import mente_acumulativa_r02 as capability
        else:from capacidades import mente_unificada_01 as capability
        self.store=Store(self.system);record=self.store.record(self.life)
        self.writer=self.store.writer(record['world_id']);self.writer.__enter__()
        self.physical=physical;self.atomic_json=atomic_json;self.encode=encode_metadata;self.decode=decode_metadata;self.capability=capability
        try:return self._open_locked()
        except BaseException:self.close();raise
    def _open_locked(self):
        self.rec,self.a=self.store.load(self.life)
        self.capability.get(self.a)  # Strict declared contract; no empty/T0 fallback.
        self.code_sha256['native_capability_source']=hashlib.sha256(Path(self.capability.__file__).read_bytes()).hexdigest()
        self.marker=self.store.life_dir(self.life)/'FUTURO_INTERRUMPIDO.json'
        self.folder=self.store.state/'servicios_persistentes'/self.rec['world_id'];self.folder.mkdir(parents=True,exist_ok=True)
        self.work_directory=self.store.state/'servicios_locales'/self.life
        from app.access_guard import install
        worker=[sys.executable,'-I','-B','-X','utf8',str(self.system/'capacidades/eo02_trabajador_local.py')]
        self.guard=install(self.system,external_command=worker)
        entries=dict(self.a.world.runtime.snapshot_metadata_entries)
        self.loaded_protocol=self.decode(entries[KEY])if KEY in entries else None
        if self.loaded_protocol and self.loaded_protocol.get('backend','ma02')!=self.backend:
            raise ValueError('Declared backend differs from this service history. No silent strategy/profile substitution.')
        if self.loaded_protocol and self.loaded_protocol.get('queue_journal_required_for_transport_deduplication')and not(self.folder/'cola.sqlite3').is_file():
            self.close();raise ValueError('MISSING_OPERATIONAL_QUEUE_JOURNAL: a full native snapshot alone is not the complete persistent service. Import the paired export; no empty queue is substituted.')
        return self
    @property
    def tick(self):return int(self.a.tick)
    def fingerprint(self):return self.physical(self.a.world)
    def validate(self,payload):
        if payload['operacion']!='sesion':return
        memory=self.capability if self.backend=='ma02'else self.capability.ma
        enabled=memory.get(self.a).get('enabled_contexts',list(memory.BASE_TOKENS))
        if self.backend=='mente_unificada':
            apd04_rows=[row for row in payload['situaciones']if isinstance(row.get('modo'),str)and row['modo'].startswith('apd04')]
            if apd04_rows and len(payload['situaciones'])!=1:raise ValueError('APD04 uses explicit separate environmental, teaching and use requests')
            apd03_rows=[row for row in payload['situaciones']if isinstance(row.get('modo'),str)and row['modo'].startswith('apd03')]
            if apd03_rows and len(payload['situaciones'])!=1:raise ValueError('APD03 preparation, teaching, material panels and goal opportunities are explicit separate requests')
            if apd03_rows and payload.get('actuador','closed')!='closed':raise ValueError('APD03 has no admitted null-actuator protocol; no material input submitted')
            preparation=[row for row in payload['situaciones']if row.get('modo')in('apd-docencia','apd-ambiente','apd-ruta-docencia','apd02-admitir','apd02-ruta-admitir','apd02-ruta04-admitir','apd02-docencia','apd02-ambiente','apd02-meta','apd02-meta-iniciar','apd02-meta-paso')]
            if preparation and len(payload['situaciones'])!=1:raise ValueError('APD teaching/environment configuration are explicit separate requests, never hidden fields or mixed evaluation rows.')
            stages=[row for row in payload['situaciones']if row.get('modo')in('cadena-iniciar','cadena-finalizar')]
            if stages:
                if len(payload['situaciones'])!=1:raise ValueError('The service exposes chain stages as two explicit separate requests, not an implicit planner.')
                state=self.capability.get(self.a)
                if state.get('external_uncertain'):raise ValueError('A preserved uncertain external outcome requires examination; no new chain or retry.')
                pending=bool(state.get('external_pending'));cascade=bool(state.get('cascade_pending'))
                if stages[0]['modo']=='cadena-iniciar'and(pending or cascade):raise ValueError('An actual transaction is already pending; no material input or replacement submitted.')
                if stages[0]['modo']=='cadena-finalizar'and not(pending and cascade):raise ValueError('No actual prepared chain exists; this preflight rejection causes no native input or external action.')
        for row in payload['situaciones']:
            mode=row.get('modo','usar')
            if self.backend=='mente_unificada':
                if isinstance(mode,str)and mode.startswith('apd04'):
                    from capacidades import ecosistema_apd04 as apd04
                    apd04.validate(self.a,row)
                    continue
                if isinstance(mode,str)and mode.startswith('apd03'):
                    from capacidades import asistente_apd03 as apd03
                    apd03.validate(self.a,row)
                    continue
                if isinstance(mode,str)and mode.startswith('apd02'):
                    from capacidades import asistente_apd02 as apd02
                    apd02.validate(self.a,row)
                    continue
                if mode not in('usar','trabajo','experiencia','memoria','dato','crudos','cadena-iniciar','cadena-finalizar','apd','apd-docencia','apd-ambiente','apd-conteo','apd-componer','apd-ruta-docencia'):raise ValueError('Operation outside declared unified backend.')
                if mode in('apd','apd-docencia','apd-ambiente','apd-conteo','apd-componer','apd-ruta-docencia'):
                    # Passive preparation/domain check only. The literal word
                    # and operands are forwarded unchanged by session; no host
                    # operation, useful route or correct result is selected.
                    from capacidades import asistente_proposito_01 as apd
                    apd.state(self.a)
                    if mode in('apd','apd-docencia','apd-componer','apd-ambiente','apd-ruta-docencia'):
                        validator=getattr(apd,'validate_literal',None)
                        if not callable(validator):raise ValueError('Declared APD literal-admission preflight is absent; no material request or tool action submitted.')
                        validator(self.a,row)
                    if mode=='apd-conteo':
                        from capacidades import percepcion_cruda_fi01 as pc
                        if pc.get(self.a).get('level')!=128:raise ValueError('Count requires the already admitted128-component frontend; no automatic preparation or level switch.')
                    continue
                if mode=='crudos':
                    from capacidades import percepcion_cruda_fi01 as pc
                    if pc.get(self.a).get('level')!=128:raise ValueError('This service admits only the explicit prepared128-component profile; no new sensor installation or level substitution.')
                if mode=='cadena-iniciar':
                    if row.get('contexto')not in enabled:raise ValueError('Chain initiation context not physically admitted by this life.')
                    continue
                if mode!='memoria':
                    if 'contexto'in row:raise ValueError('Native selector receives no host-selected memory context; use explicit memoria mode for assisted context access.')
                    continue
                mode=row.get('operacion_memoria','usar')
            elif mode in('experiencia','memoria','dato','crudos','cadena-iniciar','cadena-finalizar'):raise ValueError('This operation is outside declared MA02 backend.')
            if mode!='componer'and row.get('contexto')not in enabled:
                raise ValueError('Interface not physically admitted by this life: '+str(row.get('contexto')))
    def before_mutation(self,kind,target=None):
        if not self.dirty:
            self.atomic_json(self.marker,{'schema':'DCS1.1.interrupted_persistent_future.v1','life_id':self.life,
                'last_committed_snapshot_sha256':self.rec['snapshot_sha256'],'last_committed_tick':self.rec['physical']['tick'],
                'uncommitted_native_future_possible':True,'operation':kind,'planned_target':target,'registered_utc':now(),
                'no_silent_checkpoint_rewind':'If this owner dies, normal Store.load is deliberately blocked. Diagnose or explicitly branch from a named full past.'})
            self.dirty=True
    def external_uncertainty(self):
        # Protocol state only. A legitimate pending artifact is NOT an error.
        hook=getattr(self.capability,'external_uncertainty',None)
        if hook is not None:
            value=hook(self.a)
            if type(value)is not bool:raise ValueError('Declared uncertainty hook must return an explicit boolean')
            return value
        own=self.capability.get(self.a)
        return bool(own.get('external_uncertain'))
    def operational_dependencies(self):
        # Passive receipt only: no value from this witness selects an action.
        own=self.capability.get(self.a)
        fields={key:own.get(key)for key in('external_pending','cascade_pending','external_uncertain')}
        hook=getattr(self.capability,'additional_operational_state',None)
        if hook is not None:
            extra=hook(self.a)
            if not isinstance(extra,dict):raise ValueError('Additional operational state must be a serializable declared dictionary')
            if extra:fields['additional_external_state']=extra
        return {'external_pending_present':bool(fields['external_pending']),
            'cascade_pending_present':bool(fields['cascade_pending']),
            'external_uncertain_present':bool(fields['external_uncertain']),
            'exact_serialized_external_protocol_sha256':hashlib.sha256(canonical(fields).encode('utf8')).hexdigest(),
            'scope':'Passive exact serialized pending-artifact/progress witness, not a memory reader or actor input.'}
    def advance(self,ticks,kind='idle_continuous'):
        self.before_mutation(kind,self.tick+ticks)
        self.a.run_until(self.tick+ticks)  # Official OrganizationalWorld owner, not Runtime.run.
    def execute(self,payload):
        self.before_mutation('material_request')
        if payload['operacion']=='avanzar':
            self.advance(payload['ticks'],'explicit_advance');return {'real_ticks_advanced':payload['ticks'],'physical':self.fingerprint()}
        before_calls=len(self.guard['allowed_exact_external_calls'])
        value=self.capability.session(self.a,situations=payload['situaciones'],directory=self.work_directory,
            actuator=payload.get('actuador','closed'),feedback=payload.get('retorno','real'),detailed=False)
        value['INSTRUMENTO_FENCE']={'denied':self.guard['denied_operations'],
            'exact_environment_processes':self.guard['allowed_exact_external_calls'][before_calls:],
            'no_lab_evidence_or_history_reads_allowed':False,'legacy_combined_flag_deprecated_no_universal_history_guarantee':True,'no_undeclared_external_lab_or_evidence_reads_allowed':True,'operational_history_reads_universally_blocked':False,'scope':self.guard['scope']}
        return value
    def checkpoint(self,protocol,pending,operation):
        # Slots are reused; no unbounded native metadata ledger or hidden answers.
        self.rec={**self.rec,'persistent_service':{'schema':'DEE.persistent_service.record_index.v1','backend':self.backend,
            'sidecar_directory':self.folder.relative_to(self.store.state).as_posix(),
            'worker_directory':self.work_directory.relative_to(self.store.state).as_posix(),
            'snapshot_alone_is_not_complete_transport':True,
            'scope':'Technical state locator, no learned contents or answers. Native metadata and the paired journal remain authoritative.'}}
        self.a.world.runtime.set_snapshot_metadata(KEY,self.encode(protocol))
        for slot in range(16):
            value={'empty':True}if slot>=len(pending)else {'id':pending[slot]['id'],
                'payload':json.loads(pending[slot]['payload']),'payload_sha256':pending[slot]['payload_sha'],
                'transport_status':pending[slot]['status'],'arrival_utc':pending[slot]['arrived_utc']}
            self.a.world.runtime.set_snapshot_metadata(KEY+'.queue.'+str(slot),self.encode(value))
        self.rec=self.store.commit(self.rec,self.a,operation)
        if self.marker.exists():self.marker.unlink()
        self.dirty=False
        return {'life_id':self.life,'snapshot':self.rec['snapshot'],'snapshot_sha256':self.rec['snapshot_sha256'],'physical':self.rec['physical'],
            'operational_dependencies':self.operational_dependencies()}
    def export_pair(self,identifier,queue):
        target=self.folder/'exportaciones'/identifier
        target.mkdir(parents=True,exist_ok=False)
        native=self.store.snapshot(self.rec);shutil.copyfile(native,target/'VIDA.deetsnap.gz')
        queue.backup(target/'cola.sqlite3')
        files=[]
        def copy_tree(source,relative):
            if not source.is_dir():return
            for p in sorted(source.rglob('*')):
                if not p.is_file():continue
                if not p.resolve().is_relative_to(source.resolve()):raise ValueError('External link outside declared service artifacts.')
                dest=target/relative/p.relative_to(source);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
        copy_tree(self.folder/'resultados',Path('resultados'))
        copy_tree(self.work_directory,Path('artefactos_trabajador'))
        for p in sorted(target.rglob('*')):
            if p.is_file():files.append({'file':p.relative_to(target).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        manifest={'schema':'DEE.persistent_service.paired_export.v1','life_id':self.life,'profile':self.rec['profile'],
            'backend':self.backend,'native_snapshot':'VIDA.deetsnap.gz','snapshot_sha256':self.rec['snapshot_sha256'],
            'physical':self.rec['physical'],'members':files,'queue_journal_required':True,
            'source_record':{'life_id':self.life,'world_id':self.rec['world_id'],'parent':self.rec.get('parent')},
            'no_engine_or_WHL':True,'not_a_new_cognitive_acquisition':True,
            'scope':'One complete native world plus local transport journal/outbox and bounded worker artifacts. Export row may be processing in the SQLite backup; the committed native receipt and exact staged result permit reconciliation without re-execution.'}
        self.atomic_json(target/'EXPORTACION_SERVICIO.json',manifest)
        return {'directory':str(target),'manifest_sha256':hashlib.sha256((target/'EXPORTACION_SERVICIO.json').read_bytes()).hexdigest(),
            'members':len(files),'bytes':sum(x['bytes']for x in files),'snapshot_sha256':self.rec['snapshot_sha256']}
    def close(self):
        if self.writer:self.writer.__exit__(None,None,None);self.writer=None


class PersistentService:
    def __init__(self,world,queue,*,idle_ticks=1,idle_seconds=.1,save_seconds=15,max_seconds=None,start_paused=False):
        if type(idle_ticks)is not int or not 1<=idle_ticks<=67:raise ValueError('Idle quantum1..67 exact ticks.')
        if not .01<=idle_seconds<=60 or not .2<=save_seconds<=3600:raise ValueError('Explicit bounded host cadence/checkpoint interval required.')
        self.world=world;self.queue=queue;self.idle_ticks=idle_ticks;self.idle_seconds=idle_seconds
        self.save_seconds=save_seconds;self.max_seconds=max_seconds
        self.paused=bool(start_paused);self.stop=False;self.uncertain=False;self.idle_total=0;self.material_calls=0;self.checkpoints=0
        self.started=time.monotonic();self.last_save=self.started;self.next_idle=self.started+idle_seconds;self.last_publish=0
        self.current=None;self.owner_pid=os.getpid();self.last_receipt=None;self.epoch=1
    def protocol(self,receipt=None):
        return {'schema':'DEE.persistent_service.owner.v1','life_id':self.world.life,'pid_at_checkpoint':self.owner_pid,
            'source_sha256':getattr(self.world,'code_sha256',{}),'native_tick_at_checkpoint':self.world.tick,'backend':getattr(self.world,'backend','FAKE_TEST_ONLY'),'epoch':self.epoch,'closed_epoch':False,
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
            'backend':getattr(self.world,'backend','FAKE_TEST_ONLY'),'epoch':self.epoch,'source_sha256':getattr(self.world,'code_sha256',{}),
            'scope':'Passive external observation cached at wall_utc, not an instantaneous native clock or an extra question. Check cache age.'}
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
        closed=bool((protocol or{}).get('closed_epoch'))
        if protocol and not closed and 'native_tick_at_checkpoint'in protocol and protocol['native_tick_at_checkpoint']!=self.world.tick:
            raise ValueError('SERVICE_PROTOCOL_OUT_OF_SYNC: a non-service continuation changed the world without its paired transport; no rewind or empty-queue substitution.')
        unresolved=[r for r in self.queue.outstanding()if r['status']in('processing','uncertain')]
        if closed and self.queue.outstanding():raise ValueError('Closed epoch unexpectedly contains pending or uncertain requests; do not discard or repeat them.')
        receipt=(protocol or{}).get('last_completed_receipt')
        for row in unresolved:
            if receipt and row['id']==receipt['id']and row['payload_sha']==receipt['payload_sha256']:
                path=self.world.folder/'resultados'/(row['id']+'.json')
                if path.is_file()and hashlib.sha256(path.read_bytes()).hexdigest()==receipt['result_sha256']:
                    self.queue.finish(row['id'],'completed',json.loads(path.read_bytes()));continue
            self.queue.finish(row['id'],'uncertain',error={'reason':'Prior owner did not leave a matching committed result; do not repeat action.'})
            self.uncertain=True;self.paused=True
        if protocol:
            self.epoch=int(protocol.get('epoch',1))+(1 if closed else 0)
            self.idle_total=protocol.get('idle_total',0);self.material_calls=protocol.get('material_calls',0)
            self.paused=self.paused or(protocol.get('paused',False)and not closed)
            self.uncertain=self.uncertain or protocol.get('uncertain_external_result',False)
        native_uncertainty=getattr(self.world,'external_uncertainty',None)
        if native_uncertainty and native_uncertainty():self.uncertain=True;self.paused=True
        self.queue.meta('protocol_admission_closed',False)  # Only this explicit owner start reopens transport admission.
    def perform(self,row):
        self.current=row;payload=json.loads(row['payload']);op=payload['operacion'];started=self.world.tick;execution_utc=now()
        try:
            try:
                validator=getattr(self.world,'validate',None)
                if validator:validator(payload)
            except ValueError as invalid:
                self.queue.finish(row['id'],'rejected_invalid',error={'type':'interface_contract','detail':str(invalid),
                    'native_tick_unchanged':self.world.tick==started,'no_material_input_submitted':True})
                return
            if op=='pausar':self.paused=True;value={'technical_pause':True,'native_ticks_do_not_advance_while_paused':True}
            elif op=='reanudar':
                if self.uncertain:raise ValueError('Unresolved external outcome blocks automatic resume/retry; inspect preserved receipts.')
                self.paused=False;self.next_idle=time.monotonic()+self.idle_seconds;value={'technical_resume':True}
            elif op=='detener':self.stop=True;value={'graceful_stop':True,'no_autostart_or_restart':True}
            elif op=='guardar':value={'explicit_checkpoint':True}
            elif op=='exportar':value={'paired_export_requested':True,'relative_export_directory':'exportaciones/'+row['id']}
            else:value=self.world.execute(payload);self.material_calls+=1
            result={'id':row['id'],'operation':op,'arrival_utc':row['arrived_utc'],'started_utc':execution_utc,'finished_execution_utc':now(),
                'before_tick':started,'after_tick':self.world.tick,'result':value,
                'owner_material_calls_after':self.material_calls,'owner_idle_ticks_after':self.idle_total,'owner_epoch':self.epoch,
                'host_elapsed_seconds':time.monotonic()-self.started,'scope':'Native result unchanged; request ID is transport only.'}
            out=self.world.folder/'resultados'/(row['id']+'.json');out.parent.mkdir(parents=True,exist_ok=True)
            data=(canonical(result)+'\n').encode('utf-8');out.write_bytes(data)
            receipt={'id':row['id'],'payload_sha256':row['payload_sha'],'result_sha256':hashlib.sha256(data).hexdigest()}
            saved=self.checkpoint({'kind':'PERSISTENT_'+op.upper(),'before_tick':started,'after_tick':self.world.tick,
                'transport_id':row['id'],'result_file':'resultados/'+row['id']+'.json','result_sha256':receipt['result_sha256'],
                'exact_result_preserved_in_outbox_and_transport_journal':True},receipt)
            result['committed_snapshot']=saved
            if op=='exportar':result['paired_export']=self.world.export_pair(row['id'],self.queue)
            self.last_receipt=receipt;self.queue.finish(row['id'],'completed',result)
        except BaseException as error:
            work=any(q.get('modo')in('trabajo','cadena-iniciar','cadena-finalizar','apd','apd-componer','apd02','apd02-componer','apd02-meta','apd02-meta-iniciar','apd02-meta-paso','apd03-tarea-iniciar','apd03-paso')or(q.get('modo')=='componer'and q.get('dominio'))or(q.get('modo')=='memoria'and(q.get('operacion_memoria')=='trabajo'or q.get('operacion_memoria')=='componer'and q.get('dominio')))for q in payload.get('situaciones',[]))
            self.uncertain=self.uncertain or work;self.paused=True
            info={'type':type(error).__name__,'detail':str(error),'native_tick_after_attempt':self.world.tick,
                'external_execution_may_be_uncertain':work,'no_retry_or_rollback':True}
            try:
                saved=self.checkpoint({'kind':'FAILED_PERSISTENT_'+op.upper(),'transport_id':row['id'],'error':info})
                info['failed_native_future_preserved']=saved
            except Exception as save_error:info['checkpoint_error']=str(save_error)
            self.queue.finish(row['id'],'uncertain'if work else'failed_preserved',error=info)
            if isinstance(error,(KeyboardInterrupt,SystemExit)):self.stop=True
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
    p.add_argument('--backend',choices=('ma02','mente_unificada'),default='ma02')
    p.add_argument('--pausado',action='store_true')
    p.add_argument('--ticks-ocio',type=int,default=1);p.add_argument('--intervalo',type=float,default=.1)
    p.add_argument('--guardar-cada',type=float,default=15);p.add_argument('--max-segundos',type=float)
    a=p.parse_args()
    print(json.dumps(serve(a.sistema,a.vida,backend=a.backend,idle_ticks=a.ticks_ocio,idle_seconds=a.intervalo,
        save_seconds=a.guardar_cada,max_seconds=a.max_segundos,start_paused=a.pausado),ensure_ascii=False),flush=True)


def serve(system,life,backend='ma02',**cadence):
    world=NativeWorld(system,life,backend).open()
    try:
        queue=QueueDB(world.folder/'cola.sqlite3')
        return PersistentService(world,queue,**cadence).run()
    finally:world.close()


if __name__=='__main__':main()
