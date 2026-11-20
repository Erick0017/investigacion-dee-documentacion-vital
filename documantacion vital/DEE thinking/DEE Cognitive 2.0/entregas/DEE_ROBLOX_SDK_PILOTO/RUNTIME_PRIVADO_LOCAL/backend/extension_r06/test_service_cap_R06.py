"""Fake-owner/temporary-JSON tests only; never opens Native or HTTP."""
from pathlib import Path
import queue
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import servicio_capabilities_http_R06 as api

class FakeOwner:
    def __init__(self,error=None):self.calls=[];self.closed=False;self.error=error
    def __enter__(self):return self
    def __exit__(self,*_):self.closed=True
    def material(self,op,literal,**kwargs):
        self.calls.append((op,literal,kwargs))
        if self.error:raise self.error
        return {'rows':[{'version':api.VERSION,'nativeTick':123020,'nativeTicks':20,
            'nativeValue':{'numeric_result':700,'status':'FORMED'},'assisted':True}]}

class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();home=Path(self.tmp.name)
        s=api.Service.__new__(api.Service);self.s=s;s.home=home;s.cfg={};s.instance='SDK_DEMO_0123456789ABCDEF';s.sid='sid';s.life='life'
        s.scope={'lastNewUtcEpoch':time.time()+60,'native_cutoff_utc_epoch':time.time()+120,'maxEvents':12}
        s.statefile=home/'CAPABILITIES_STATE_R06.json';s.saved={'preCapDescriptor':{'nativeTick':123000}}
        s.folder=home/'capability_operations';s.folder.mkdir();s.lock=threading.RLock();s.work=queue.Queue()
        s.native_tick=123000;s.sequence=0;s.owner=None;s.status='STARTING';s.resource=None;s.last_error=None;s.stop=False
        s.memory=lambda:4*1024**3;s.token='fake-only';s.fd=None;s.lockfile=home/'unused.lock'
        self.proof={'nativeTick':123020,'snapshotSha256':'a'*64,'databaseSha256':'b'*64,'cardSha256':'c'*64,'pending':0,'writerClosed':True}
    def tearDown(self):
        if getattr(self.s,'thread',None) is not None and self.s.thread.is_alive():
            self.s.scope['native_cutoff_utc_epoch']=time.time()-.01;self.s.thread.join(3)
        self.tmp.cleanup()
    def start(self,owner):
        self.s.factory=lambda:owner
        self.patch=patch.object(api,'closed_native',return_value=self.proof);self.patch.start();self.addCleanup(self.patch.stop)
        self.s.thread=threading.Thread(target=self.s.worker);self.s.thread.start();self.until(lambda:self.s.status=='READY')
    def until(self,fn):
        end=time.monotonic()+3
        while not fn() and time.monotonic()<end:time.sleep(.005)
        self.assertTrue(fn())
    def body(self):return {'instanceId':self.s.instance,'sessionId':'sid','operationId':'cap_original','request':{'kind':'NUMERIC','operation':'suma','left':4,'right':5}}
    def close(self):
        op={'instanceId':self.s.instance,'sessionId':'sid','operationId':'close_original'}
        self.s.submit(op,close=True);self.s.thread.join(3);self.assertFalse(self.s.thread.is_alive())
    def test_native_output_700_is_not_repaired_and_duplicate_does_not_reexecute(self):
        owner=FakeOwner();self.start(owner);body=self.body();self.s.submit(body)
        self.until(lambda:self.s.operation('cap_original')['status']=='COMPLETED')
        self.assertEqual(self.s.operation('cap_original')['value']['nativeValue']['numeric_result'],700)
        self.s.submit(body);self.assertEqual(len(owner.calls),1);self.assertEqual(self.s.sequence,1)
        self.close();self.assertTrue(owner.closed)
    def test_unknown_after_material_preserves_exact_id_without_retry(self):
        owner=FakeOwner(RuntimeError('unknown Native return'));self.start(owner);body=self.body();self.s.submit(body)
        self.s.thread.join(3);row=self.s.operation('cap_original')
        self.assertEqual(row['status'],'UNCERTAIN');self.assertTrue(row['nativeAdmissionStarted'])
        self.s.submit(body);self.assertEqual(len(owner.calls),1)
    def test_resource_wait_has_no_material_before_guard(self):
        owner=FakeOwner();enough=threading.Event()
        self.s.memory=lambda:4*1024**3 if self.s.owner is None or enough.is_set() else 1024**3-1
        self.start(owner);self.s.submit(self.body());self.until(lambda:self.s.status=='PENDING_RESOURCE')
        self.assertEqual(owner.calls,[]);self.assertEqual(self.s.sequence,0)
        enough.set();self.until(lambda:self.s.operation('cap_original')['status']=='COMPLETED')
        self.assertEqual(len(owner.calls),1);self.close()
    def test_expected_answer_field_rejected_before_durable_admission(self):
        self.s.status='READY';body=self.body();body['request']['expected']=9
        with self.assertRaises(ValueError):self.s.submit(body)
        self.assertEqual(list(self.s.folder.iterdir()),[])
    def test_known_failed_boot_close_is_zero_material_and_keeps_error(self):
        self.s.status='FAILED_PRESERVED';self.s.owner=None;self.s.thread=None
        self.s.last_error={'code':'BOOT_RESOURCE_EXPIRED'}
        d=self.s.home/'estado_demo';d.mkdir();api.atomic(d/'LEDGER_SDK_R06.json',{'intents':{}})
        proof={**self.proof,'nativeTick':123000}
        with patch.object(api,'RUNTIME',self.s.home),patch.object(api,'closed_native',return_value=proof):
            v=self.s.submit({'instanceId':self.s.instance,'sessionId':'sid','operationId':'close_failed'},close=True)
        self.assertEqual(v['status'],'COMPLETED');self.assertEqual(v['value']['newNativeTicks'],0)
        self.assertEqual(v['value']['errorPreserved'],self.s.last_error);self.assertTrue(self.s.stop)
    def test_failed_boot_close_never_discards_uncertain_operation(self):
        self.s.status='FAILED_PRESERVED';self.s.owner=None;self.s.thread=None
        api.atomic(self.s.folder/'unknown.json',{'status':'UNCERTAIN'})
        with self.assertRaises(api.Conflict):
            self.s.submit({'instanceId':self.s.instance,'sessionId':'sid','operationId':'close_failed'},close=True)

if __name__=='__main__':unittest.main()
