"""Transport/owner tests only. Fake worlds are not DEE experiments."""
import json,sys,tempfile,threading,time,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cola_local import QueueDB,canonical
from servicio_persistente import PersistentService,NativeWorld


class FakeWorld:
    def __init__(self,folder):
        self.folder=Path(folder);self.life='FAKE_TRANSPORT_ONLY';self.tick=0
        self.rec={'physical':{'tick':0},'snapshot_sha256':'start'};self.loaded_protocol=None;self.executions=0;self.closed=False
    def fingerprint(self):return {'N':1,'tick':self.tick,'RAW_sha256':'test','clocks_sha256':str(self.tick)}
    def advance(self,n):self.tick+=n
    def execute(self,payload):
        self.executions+=1;self.tick+=5
        if payload.get('situaciones',[{}])[0].get('modo')=='trabajo':raise RuntimeError('Synthetic interrupted worker, not native physics')
        return {'test_echo_only':payload,'not_a_native_answer':True}
    def checkpoint(self,protocol,pending,operation):
        self.rec={'physical':{'tick':self.tick},'snapshot_sha256':'test-'+str(self.tick)}
        self.loaded_protocol=protocol;return {'physical':self.fingerprint(),'snapshot_sha256':self.rec['snapshot_sha256']}
    def close(self):self.closed=True


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='dee-local-transport-');self.root=Path(self.temp.name)
        self.q=QueueDB(self.root/'q.sqlite3',capacity=2)
    def tearDown(self):self.temp.cleanup()
    def request(self):return {'operacion':'sesion','situaciones':[{'contexto':'gamma'}]}
    def wait(self,identifier):
        for _ in range(200):
            row=self.q.get(identifier)
            if row and row['status']in('completed','uncertain','failed_preserved'):return row
            time.sleep(.005)
        self.fail('Transport did not complete')
    def test_capacity_is_technical_and_no_native_fallback(self):
        self.assertEqual(self.q.put('a',self.request())['admission'],'queued')
        self.q.put('b',self.request());self.assertEqual(self.q.put('c',self.request())['admission'],'rejected_queue_capacity')
    def test_idempotent_id_and_conflict(self):
        self.q.put('a',self.request());self.q.next();self.q.finish('a','completed',{'value':3})
        self.assertEqual(self.q.put('a',self.request())['request']['status'],'completed')
        with self.assertRaises(ValueError):self.q.put('a',{'operacion':'guardar'})
        self.assertEqual(self.q.counters(),{'completed':1})
    def test_explicit_close_gates_new_arrivals_without_erasing_ids(self):
        self.q.put('a',self.request())
        with self.assertRaises(ValueError):self.q.close_admission_if_idle()
        self.q.next();self.q.finish('a','completed',{'past':True});self.q.close_admission_if_idle()
        self.assertEqual(self.q.put('b',self.request())['admission'],'rejected_protocol_closed')
        self.assertEqual(self.q.put('a',self.request())['admission'],'existing_same_transport_request')
    def test_explicit_new_epoch_allows_later_legitimate_world_continuation(self):
        world=FakeWorld(self.root);world.tick=9;world.loaded_protocol={'native_tick_at_checkpoint':4,'closed_epoch':True,'epoch':2,'paused':True,'material_calls':12}
        self.q.close_admission_if_idle();server=PersistentService(world,self.q);server.restore_transport()
        self.assertEqual(server.epoch,3);self.assertFalse(server.paused);self.assertEqual(server.material_calls,12)
        self.assertEqual(world.executions,0);self.assertEqual(self.q.put('a',self.request())['admission'],'queued')
    def test_FIFO_and_explicit_control_precedence(self):
        self.q.put('first',self.request());self.q.put('second',self.request());self.q.put('pause',{'operacion':'pausar'})
        self.assertEqual(self.q.next()['id'],'pause');self.assertEqual(self.q.next()['id'],'first');self.assertEqual(self.q.next()['id'],'second')
    def test_two_concurrent_clients_capacity_never_exceeded(self):
        results=[]
        threads=[threading.Thread(target=lambda i=i:results.append(self.q.put('r'+str(i),self.request())))for i in range(8)]
        [t.start()for t in threads];[t.join()for t in threads]
        self.assertEqual(sum(q['admission']=='queued'for q in results),2)
    def test_validation_no_hidden_file_shell_or_target(self):
        for payload in ({'operacion':'sesion','situaciones':[{'contexto':'gamma','target':1}]},
                        {'operacion':'avanzar','ticks':True},{'operacion':'avanzar','ticks':1000000},
                        {'operacion':'guardar','shell':'x'}):
            with self.assertRaises(ValueError):self.q.put('bad',payload)
    def test_unified_datum_and_two_stage_chain_schema_has_no_completion_target(self):
        self.assertEqual(self.q.put('datum',{'operacion':'sesion','situaciones':[{'modo':'dato','valor':512}]})['admission'],'queued')
        self.assertEqual(self.q.put('chain',{'operacion':'sesion','situaciones':[{'modo':'cadena-iniciar','contexto':'gamma','valores':[3,11]},{'modo':'cadena-finalizar'}]})['admission'],'queued')
        for row in({'modo':'dato','valor':513},{'modo':'dato','valor':True},{'modo':'cadena-finalizar','contexto':'gamma'},{'modo':'cadena-iniciar','contexto':'gamma'}):
            with self.assertRaises(ValueError):self.q.put('invalid',{'operacion':'sesion','situaciones':[row]})
    def test_native_external_uncertainty_blocks_resume_without_actor_call(self):
        world=FakeWorld(self.root);world.external_uncertainty=lambda:True;server=PersistentService(world,self.q);server.restore_transport()
        self.assertTrue(server.paused);self.assertTrue(server.uncertain);self.assertEqual(world.executions,0)
    def test_raw_components_are_literal_bounded_and_never_aggregated(self):
        components=[0]*128;components[0]=19;components[2]=2
        request={'operacion':'sesion','situaciones':[{'modo':'crudos','componentes':components}]}
        self.q.put('raw',request);self.assertEqual(json.loads(self.q.get('raw')['payload']),request)
        for values in([0]*127,[0]*129,[True]+[0]*127,[33]+[0]*127):
            with self.assertRaises(ValueError):self.q.put('invalid_raw',{'operacion':'sesion','situaciones':[{'modo':'crudos','componentes':values}]})
        with self.assertRaises(ValueError):self.q.put('aggregate',{'operacion':'sesion','situaciones':[{'modo':'crudos','componentes':components,'valor':21}]})
    def test_transport_ids_are_portable_filenames(self):
        for name in('..','.','NUL','CON.json','a.','COM1'):
            with self.assertRaises(ValueError):self.q.put(name,self.request())
    def test_owner_rejects_unadmitted_interface_without_native_execution(self):
        world=FakeWorld(self.root)
        def reject(payload):raise ValueError('Unknown prepared interface')
        world.validate=reject;server=PersistentService(world,self.q)
        self.q.put('unknown',{'operacion':'sesion','situaciones':[{'contexto':'unknown'}]});server.perform(self.q.next())
        self.assertEqual(self.q.get('unknown')['status'],'rejected_invalid');self.assertEqual(world.tick,0)
        self.assertEqual(world.executions,0);self.assertFalse(server.paused)
    def test_declared_backend_does_not_select_memory_bank_from_answer(self):
        from types import SimpleNamespace
        memory=SimpleNamespace(BASE_TOKENS=['gamma'],get=lambda a:{'enabled_contexts':['gamma']})
        world=NativeWorld(self.root,'FAKE_BACKEND_TEST','mente_unificada');world.a=None;world.capability=SimpleNamespace(ma=memory)
        world.validate({'operacion':'sesion','situaciones':[{'modo':'usar'}]})
        world.validate({'operacion':'sesion','situaciones':[{'modo':'memoria','contexto':'gamma'}]})
        with self.assertRaises(ValueError):world.validate({'operacion':'sesion','situaciones':[{'modo':'usar','contexto':'gamma'}]})
        with self.assertRaises(ValueError):world.validate({'operacion':'sesion','situaciones':[{'modo':'memoria','contexto':'unknown'}]})
    def test_chain_preflight_uses_protocol_presence_not_expected_content(self):
        from types import SimpleNamespace
        memory=SimpleNamespace(BASE_TOKENS=['gamma'],get=lambda a:{'enabled_contexts':['gamma']})
        state={};world=NativeWorld(self.root,'FAKE_CHAIN_PREFLIGHT','mente_unificada');world.a=None
        world.capability=SimpleNamespace(ma=memory,get=lambda a:state)
        start={'operacion':'sesion','situaciones':[{'modo':'cadena-iniciar','contexto':'gamma','valores':[3,11]}]}
        finish={'operacion':'sesion','situaciones':[{'modo':'cadena-finalizar'}]}
        world.validate(start)
        with self.assertRaisesRegex(ValueError,'No actual prepared'):world.validate(finish)
        state.update(external_pending={'opaque_content_not_inspected':-1},cascade_pending={'public_values':[3,11]})
        world.validate(finish)
        with self.assertRaisesRegex(ValueError,'already pending'):world.validate(start)
        state['external_uncertain']={'unknown_outcome':True}
        with self.assertRaisesRegex(ValueError,'uncertain'):world.validate(finish)
        self.assertEqual(state['external_pending'],{'opaque_content_not_inspected':-1})
    def test_service_chain_stages_are_explicit_requests_not_internal_planning(self):
        from types import SimpleNamespace
        memory=SimpleNamespace(BASE_TOKENS=['gamma'],get=lambda a:{'enabled_contexts':['gamma']})
        world=NativeWorld(self.root,'FAKE_CHAIN_PREFLIGHT','mente_unificada');world.a=None;world.capability=SimpleNamespace(ma=memory,get=lambda a:{})
        with self.assertRaisesRegex(ValueError,'two explicit separate'):
            world.validate({'operacion':'sesion','situaciones':[{'modo':'cadena-iniciar','contexto':'gamma','valores':[3,11]},{'modo':'cadena-finalizar'}]})
    def test_sqlite_backup_preserves_queue_without_reexecution(self):
        self.q.put('a',self.request());target=self.root/'backup.sqlite3';self.q.backup(target)
        other=QueueDB(target);self.assertEqual(other.get('a')['payload_sha'],self.q.get('a')['payload_sha'])
    def test_pause_preserves_tick_resume_executes_once(self):
        world=FakeWorld(self.root);server=PersistentService(world,self.q,idle_seconds=.01,save_seconds=.2,max_seconds=2)
        thread=threading.Thread(target=server.run);thread.start()
        try:
            time.sleep(.06);self.q.put('pause',{'operacion':'pausar'});self.wait('pause');at=world.tick
            time.sleep(.06);self.assertEqual(world.tick,at)
            self.q.put('use',self.request());time.sleep(.04);self.assertEqual(world.executions,0)
            self.q.put('resume',{'operacion':'reanudar'});self.wait('use')
            self.q.put('use',self.request());self.assertEqual(world.executions,1)
            self.q.put('stop',{'operacion':'detener'});self.wait('stop')
        finally:server.stop=True;thread.join(3)
        self.assertTrue(world.closed);self.assertGreater(server.idle_total,0)
    def test_uncertain_worker_no_retry_or_native_rewind(self):
        world=FakeWorld(self.root);server=PersistentService(world,self.q)
        req={'operacion':'sesion','situaciones':[{'contexto':'gamma','modo':'trabajo'}]}
        self.q.put('work',req);server.perform(self.q.next())
        self.assertEqual(world.tick,5);self.assertTrue(server.uncertain);self.assertTrue(server.paused)
        self.assertEqual(self.q.get('work')['status'],'uncertain')
        self.q.put('work',req);self.assertEqual(world.executions,1)
    def test_nested_assisted_memory_job_is_uncertain_on_exception(self):
        world=FakeWorld(self.root)
        def interrupted(payload):raise RuntimeError('Synthetic nested worker interruption')
        world.execute=interrupted;server=PersistentService(world,self.q)
        self.q.put('nested',{'operacion':'sesion','situaciones':[{'modo':'memoria','contexto':'gamma','operacion_memoria':'trabajo'}]})
        server.perform(self.q.next());self.assertEqual(self.q.get('nested')['status'],'uncertain');self.assertTrue(server.paused)
    def test_uncommitted_processing_is_not_retried_at_restart(self):
        self.q.put('old',self.request());self.q.next();world=FakeWorld(self.root);server=PersistentService(world,self.q)
        server.restore_transport();self.assertEqual(self.q.get('old')['status'],'uncertain')
        self.assertEqual(world.executions,0);self.assertTrue(server.paused)
    def test_exact_staged_committed_result_reconciles_without_execution(self):
        import hashlib
        self.q.put('old',self.request());row=self.q.next();world=FakeWorld(self.root)
        p=self.root/'resultados/old.json';p.parent.mkdir();p.write_text('{"past_result":2}\n',encoding='utf8')
        world.loaded_protocol={'last_completed_receipt':{'id':'old','payload_sha256':row['payload_sha'],
            'result_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}}
        server=PersistentService(world,self.q);server.restore_transport()
        self.assertEqual(self.q.get('old')['status'],'completed');self.assertEqual(world.executions,0)
    def test_service_protocol_refuses_uncoordinated_native_continuation(self):
        world=FakeWorld(self.root);world.tick=5;world.loaded_protocol={'native_tick_at_checkpoint':4}
        with self.assertRaisesRegex(ValueError,'OUT_OF_SYNC'):PersistentService(world,self.q).restore_transport()
    def test_paired_manifest_validates_every_byte_without_native_import(self):
        import hashlib
        from importacion_emparejada import verify_export
        root=self.root/'export';root.mkdir();(root/'VIDA.deetsnap.gz').write_bytes(b'Not physics; validation test only')
        self.q.backup(root/'cola.sqlite3')
        members=[{'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in root.iterdir()]
        m={'schema':'DEE.persistent_service.paired_export.v1','backend':'ma02','queue_journal_required':True,'members':members,
            'native_snapshot':'VIDA.deetsnap.gz','snapshot_sha256':hashlib.sha256((root/'VIDA.deetsnap.gz').read_bytes()).hexdigest()}
        index=root/'EXPORTACION_SERVICIO.json';index.write_text(json.dumps(m),encoding='utf8')
        self.assertEqual(verify_export(root)[2]['members_verified'],2)
        (root/'VIDA.deetsnap.gz').write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError,'mismatch'):verify_export(root)


if __name__=='__main__':unittest.main(verbosity=2)
