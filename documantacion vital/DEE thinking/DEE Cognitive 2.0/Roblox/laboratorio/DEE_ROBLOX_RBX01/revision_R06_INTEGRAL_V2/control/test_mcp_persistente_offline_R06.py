"""Fake SDK stdlib fixtures: no Popen, Studio, network, model or Native."""
from pathlib import Path
from types import SimpleNamespace
import importlib.util,json,queue,sys,unittest,uuid
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_mcp_persistent_fixture',HERE/'mcp_persistente_R06.py')
lib=importlib.util.module_from_spec(spec);sys.modules[spec.name]=lib;spec.loader.exec_module(lib)
class Fake:
    instances=[]
    def __init__(self,seconds):
        self.identifier=0;self.incoming=queue.Queue();self.calls=[];self.fail_next=False
        self.process=SimpleNamespace(pid=74000+len(self.instances));self.instances.append(self);self.closed=False
    def call(self,method,params=None,notification=False,timeout=20):
        self.identifier+=1;self.calls.append((self.identifier,method,params))
        if notification:return None
        if method=='initialize':return {'serverInfo':{'name':'FAKE_SDK_ONLY'}}
        if method=='tools/list':return {'tools':[{'name':n,'inputSchema':{'required':[]}}for n in('list_roblox_studios','execute_luau')]}
        if params['name']=='list_roblox_studios':return {'content':[{'type':'text','text':json.dumps({'studios':[{'id':'S','file':'F.rbxlx'}]})}]}
        if self.fail_next:self.fail_next=False;raise TimeoutError('Synthetic unknown reply')
        return {'content':[{'type':'text','text':'{"fixture":true}'}]}
    def close(self):self.closed=True
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=HERE/('pruebas_mcp_persistente_'+uuid.uuid4().hex);cls.root.mkdir()
    def setUp(self):Fake.instances=[]
    def session(self,name):return lib.Session('S','F.rbxlx',self.root/name,seconds=600,_client_factory=Fake)
    def args(self):return dict(studio_id='S',datamodel_type='Server',code='return {fixture=true}')
    def test_two_calls_one_sdk_bootstrap(self):
        with self.session('two')as s:
            one=s.run('execute_luau',self.args(),self.root/'one.json',20,read_only=True)
            two=s.run('execute_luau',self.args(),self.root/'two.json',20,read_only=True)
            self.assertEqual(one['sdk_pid'],two['sdk_pid']);self.assertEqual(len(Fake.instances),1)
            self.assertEqual(sum(x[1]=='initialize'for x in s.client.calls),1)
            self.assertEqual(sum(x[1]=='tools/list'for x in s.client.calls),1)
            self.assertEqual(sum(x[1]=='tools/call'and x[2]['name']=='list_roblox_studios'for x in s.client.calls),1)
    def test_unknown_mutation_latched_no_retry_then_same_receipt(self):
        with self.session('mutation')as s:
            s.client.fail_next=True
            with self.assertRaises(TimeoutError):s.run('execute_luau',self.args(),self.root/'unknown.json',20)
            count=len(s.client.calls);rpc=s.pending['rpc_id'];logical=s.pending['logical_call_id']
            with self.assertRaises(RuntimeError):s.run('execute_luau',self.args(),self.root/'forbidden.json',20)
            with self.assertRaises(RuntimeError):s.reconnect_read_only()
            self.assertEqual(len(s.client.calls),count);self.assertEqual(len(Fake.instances),1)
            s.client.incoming.put({'id':rpc,'result':{'content':[{'type':'text','text':'{"late":true}'}]}})
            result=s.reconcile_pending(self.root/'late.json',1)
            self.assertEqual(result['reply']['id'],rpc);self.assertEqual(result['logical_call_id'],logical)
            self.assertTrue(result['reconciled_late_reply']);self.assertEqual(len(s.client.calls),count)
    def test_explicit_read_reconnect_preserves_logical_id(self):
        with self.session('read_reconnect')as s:
            s.client.fail_next=True
            with self.assertRaises(TimeoutError):s.run('execute_luau',self.args(),self.root/'read_timeout.json',20,read_only=True)
            previous=s.pending.copy();ticket=s.reconnect_read_only()
            self.assertEqual(len(Fake.instances),2)
            result=s.repeat_read_explicit(ticket,self.root/'explicit_read.json',20)
            self.assertEqual(result['logical_call_id'],previous['logical_call_id']);self.assertEqual(result['attempt'],2)
            self.assertGreater(result['reply']['id'],previous['rpc_id'])
    def test_no_native_imported(self):
        self.assertFalse(any(k=='dee_thinking'or k.startswith('dee_thinking.')for k in sys.modules))
if __name__=='__main__':unittest.main()
