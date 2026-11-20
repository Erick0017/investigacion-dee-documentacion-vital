"""Synthetic closed receipt delivery; no socket, Native, SQLite or real case."""
from pathlib import Path
import hashlib
import io
import json
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
import servir_recibo_cerrado_RO_R04 as ro

def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,sort_keys=True)+'\n',encoding='utf8')

class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.i='SDK_DEMO_0123456789ABCDEF';self.life='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_'+self.i
        self.sid='SDK_SESSION_test';self.op='ext_close_original';self.home=self.root/'estado_demo/instancias'/self.i
        cfg={'lifeId':self.life,'runtimeVersion':'0.1.1','validationRevision':'R06','sessionId':self.sid}
        write(self.home/'INSTANCE.json',cfg)
        card={'life_id':self.life,'physical':{'N':67,'tick':995895},'snapshot_sha256':'a'*64}
        self.card=self.home/'sistema/estado/vidas'/self.life/'VIDA.json';write(self.card,card)
        native={'writerClosed':True,'pending':0,'lifeId':self.life,'dimension':67,'nativeTick':995895,
                'cardSha256':ro.sha(self.card),'snapshotSha256':'a'*64,'databaseSha256':'b'*64}
        self.state=self.home/'CAPABILITIES_STATE_R06_R03.json'
        write(self.state,{'status':'CLOSED','lastError':None,'instanceId':self.i,'sessionId':self.sid,
                         'nativeTick':995895,'capabilitySequence':10,'closedNativeDescriptor':native})
        self.row=self.home/'capability_operations'/(self.op+'.json')
        write(self.row,{'operationId':self.op,'kind':'CLOSE','status':'COMPLETED','nativeAdmissionStarted':False,
                        'body':{'instanceId':self.i,'sessionId':self.sid,'operationId':self.op},
                        'value':dict(native,sessionId=self.sid,capabilitySequence=10)})
        self.ledger=self.root/'estado_demo/LEDGER_SDK_R06.json'
        write(self.ledger,{'intents':{},'worlds':{self.life:{'reserved':0,'consumed':4708,'cycles':2,'capability_events':10}}})
        write(self.home/'ENSAYOS.jsonl',{'kind':'OWNER_CLOSED','exit_code':0,'final_status':{'running':False}})
        write(self.root/'configuracion/CONEXION_PRIVADA.json',{'token':'SYNTHETIC_PRIVATE_TOKEN_01234567890123456789'})
        self.kw={'state_sha256':ro.sha(self.state),'receipt_sha256':ro.sha(self.row),'ledger_sha256':ro.sha(self.ledger)}
    def tearDown(self):self.temp.cleanup()
    def receipt(self):return ro.Receipt(self.root,self.i,self.op,**self.kw)
    def test_original_literal_only_and_no_files_changed(self):
        before={p.relative_to(self.root).as_posix():p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        r=self.receipt();value=r.check()
        self.assertEqual(value['operationId'],self.op);self.assertEqual(value['value'],ro.read(self.row)['value'])
        after={p.relative_to(self.root).as_posix():p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before,after)
    def test_hash_open_owner_and_pending_intent_are_rejected(self):
        r=self.receipt();lock=self.home/'SDK_SERVICE.lock';lock.write_text('owned')
        with self.assertRaisesRegex(ValueError,'OWNER'):r.check()
        lock.unlink();ledger=ro.read(self.ledger);ledger['intents']={self.life:{'id':'pending'}};write(self.ledger,ledger)
        with self.assertRaisesRegex(ValueError,'LEDGER'):r.check()
        ledger['intents']={};write(self.ledger,ledger)
        self.row.write_bytes(self.row.read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError,'SHA'):r.check()
    def test_other_closed_ledger_world_change_is_not_hash_locked(self):
        r=self.receipt();ledger=ro.read(self.ledger);ledger['worlds']['OTHER']={'reserved':0,'consumed':1};write(self.ledger,ledger)
        self.assertEqual(r.check()['status'],'COMPLETED')
        ledger['worlds'][self.life]['consumed']+=1;write(self.ledger,ledger)
        with self.assertRaisesRegex(ValueError,'LEDGER'):r.check()
    def test_fake_http_get_original_delivers_then_exits_no_post(self):
        r=self.receipt();codes=[];requests=[];closed=[]
        class FakeServer:
            def __init__(self,address,handler):self.handler=handler
            def handle_request(self):
                h=object.__new__(self.handler);h.headers={'Authorization':'Bearer '+r.token}
                h.path='/v1/capability-operations/'+r.operation+'?instanceId='+r.instance
                h.wfile=io.BytesIO();h.send_response=lambda code:codes.append(code)
                h.send_header=lambda *args:None;h.end_headers=lambda:None
                h.do_GET();requests.append(json.loads(h.wfile.getvalue()))
            def server_close(self):closed.append(True)
        result=ro.serve(r,server_factory=FakeServer,clock=lambda:0)
        self.assertEqual(codes,[200]);self.assertEqual(len(requests),1)
        self.assertEqual(requests[0]['result'],r.check());self.assertEqual(closed,[True])
        self.assertFalse(result['NativeExecuted']);self.assertEqual(result['status'],'ORIGINAL_CLOSE_RECEIPT_DELIVERED')
    def test_fake_http_expires_bounded_without_replaying(self):
        r=self.receipt();calls=[];ticks=iter((0,0,30,60))
        class FakeServer:
            def __init__(self,*_):pass
            def handle_request(self):calls.append('RO_WAIT')
            def server_close(self):calls.append('CLOSED')
        result=ro.serve(r,server_factory=FakeServer,clock=lambda:next(ticks))
        self.assertEqual(calls,['RO_WAIT','RO_WAIT','CLOSED'])
        self.assertEqual(result['status'],'RO_DELIVERY_WINDOW_EXPIRED')

if __name__=='__main__':unittest.main()
