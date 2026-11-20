"""Transport/owner tests only. Fake worlds are not DEE experiments."""
import json,sys,tempfile,threading,time,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cola_local import QueueDB,canonical
from servicio_persistente import PersistentService


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


if __name__=='__main__':unittest.main(verbosity=2)
