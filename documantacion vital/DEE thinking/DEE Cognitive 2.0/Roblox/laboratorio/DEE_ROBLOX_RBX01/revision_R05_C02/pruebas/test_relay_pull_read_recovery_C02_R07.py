"""Offline fixtures only; no process, SDK, HTTP, model or Native execution."""
import hashlib
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

SOURCE=Path(__file__).resolve().parents[1]/'control/studio_mailbox_relay_C02_R07.py'
spec=importlib.util.spec_from_file_location('relay_r07_fixture',SOURCE)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
SID='STUDIO_FIXTURE_123'
TARGET={'id':SID,'file':m.EXPECTED_PLACE,'mode':'Play','state':'Available DataModels: Edit, Server'}

def error(text=None,code=None,studio=SID,datamodel='Server',tool='execute_luau'):
    return m.MCPError('fixture',sdk_result={'isError':True,'content':[{'type':'text','text':text or m.EXACT_PULL_TARGET_ERROR}]},
        context=m.tool_error_context(tool,{'studio_id':studio,'datamodel_type':datamodel,'code':code or m.PULL_CODE}))
class Evidence:
    def __init__(self):self.rows=[]
    def write(self,kind,**fields):self.rows.append((kind,fields))
class Relay:
    def __init__(self):self.views=[];self.failure=None
    def step(self,guarded_view=None):
        if self.failure:raise self.failure
        self.views.append(guarded_view)
class MCP:
    def __init__(self,results):self.results=list(results);self.calls=[]
    def tool(self,name,args,**kwargs):self.calls.append(('inventory',kwargs));return {'studios':[dict(TARGET)]}
    def execute(self,studio,dm,code,**kwargs):
        self.calls.append(('execute',code,kwargs));value=self.results.pop(0)
        if isinstance(value,Exception):raise value
        return value
class Fixtures(unittest.TestCase):
    def gate(self,clock=None):return m.StudioRuntimeGate(SID,Evidence(),clock=clock or (lambda:100.0))
    def test_exact_sdk_error_only(self):
        self.assertTrue(m.exact_pull_target_unreachable(error(),SID))
        for value in (error(text=m.EXACT_PULL_TARGET_ERROR+' extra'),error(code=m.push_code('{}','{}')),
                      error(studio='ANOTHER_STUDIO'),error(datamodel='Edit'),error(tool='list_roblox_studios'),
                      RuntimeError(m.EXACT_PULL_TARGET_ERROR),error(text='Target is not reachable'),
                      m.MCPError(m.EXACT_PULL_TARGET_ERROR)):
            self.assertFalse(m.exact_pull_target_unreachable(value,SID))
    def test_exact_load_variant_only_and_r06_preserved(self):
        self.assertTrue(m.exact_pull_target_unreachable(error(text=m.EXACT_PULL_TARGET_LOAD_ERROR),SID))
        self.assertFalse(m.exact_pull_target_unreachable(error(text=m.EXACT_PULL_TARGET_LOAD_ERROR.replace('loadCode,','runCode,')),SID))
        self.assertFalse(m.exact_pull_target_unreachable(error(text=m.EXACT_PULL_TARGET_LOAD_ERROR,code=m.push_code('{}','{}')),SID))
        prior=SOURCE.with_name('studio_mailbox_relay_C02_R06.py')
        self.assertEqual(hashlib.sha256(prior.read_bytes()).hexdigest(),'af62c2fe8c73dcde01de15d36f53deada17679e5247b4096b85dfe8e901ca9df')
    def test_failed_pull_has_zero_forward_then_successful_exact_read(self):
        clock=[100.0];gate=self.gate(lambda:clock[0]);relay=Relay();sdk=MCP([error(),{'ready':True}])
        category,_=m.runtime_inventory_step(sdk,SID,relay,gate)
        self.assertEqual(category,'EXACT_PULL_READ_RETRY_WAIT');self.assertEqual(relay.views,[])
        self.assertEqual(gate.pull_read_recovery_started,100.0)
        clock[0]=101.0
        m.runtime_inventory_step(sdk,SID,relay,gate)
        self.assertEqual(relay.views,[{'ready':True}]);self.assertIsNone(gate.pull_read_recovery_started)
        self.assertEqual(sdk.calls[2],('inventory',{'read_deadline':700.0}))
        self.assertEqual(sdk.calls[3][2],{'read_deadline':700.0})
        self.assertEqual([r[0]for r in gate.evidence.rows].count('EXACT_PULL_TARGET_READ_RETRY_WAIT'),1)
    def test_mutation_error_outside_read_handler_is_never_retried(self):
        relay=Relay();relay.failure=error();sdk=MCP([{'ready':True}]);gate=self.gate()
        with self.assertRaises(m.MCPError):m.runtime_inventory_step(sdk,SID,relay,gate)
        self.assertIsNone(gate.pull_read_recovery_started);self.assertEqual(len(sdk.calls),2)
    def test_deadline_stops_before_new_read(self):
        clock=[100.0];gate=self.gate(lambda:clock[0]);sdk=MCP([error()]);relay=Relay()
        m.runtime_inventory_step(sdk,SID,relay,gate);clock[0]=700.0
        before=len(sdk.calls)
        with self.assertRaises(TimeoutError):m.runtime_inventory_step(sdk,SID,relay,gate)
        self.assertEqual(len(sdk.calls),before);self.assertEqual(relay.views,[])
    def test_identity_change_stops_before_pull(self):
        sdk=MCP([error()]);sdk.tool=lambda *a,**k:{'studios':[dict(TARGET,file='OTHER.rbxlx')]}
        with self.assertRaises(m.MCPError):m.runtime_inventory_step(sdk,SID,Relay(),self.gate())
        self.assertEqual(sdk.calls,[])
    def test_unclassified_error_stops(self):
        sdk=MCP([error(text='Permission denied')]);gate=self.gate()
        with self.assertRaises(m.MCPError):m.runtime_inventory_step(sdk,SID,Relay(),gate)
        self.assertIsNone(gate.pull_read_recovery_started)
    def test_read_timeout_caps_and_push_unchanged(self):
        sdk=m.MCPClient.__new__(m.MCPClient);calls=[]
        def call(*a,**k):calls.append(k);return {'content':[{'type':'text','text':'{"ok":true}'}]}
        sdk.call=call
        with patch.object(m.time,'monotonic',return_value=100.0):
            sdk.execute(SID,'Server',m.PULL_CODE,read_deadline=102.0)
            sdk.execute(SID,'Server',m.push_code('{}','{}'))
            with self.assertRaises(ValueError):sdk.execute(SID,'Server',m.push_code('{}','{}'),read_deadline=200)
        self.assertEqual([c['timeout'] for c in calls],[2.0,20])
    def test_no_attach_active_and_old_sources_preserved(self):
        s=SOURCE.read_text('utf-8');self.assertNotIn('--attach-active',s)
        old=SOURCE.with_name('studio_mailbox_relay_C02_R05.py')
        self.assertEqual(hashlib.sha256(old.read_bytes()).hexdigest(),'1343528ebf9822c9f8709f8357eed7ab29c52ca374d423f5ffdae5c274a05322')
        self.assertNotIn('except MCPError',s[s.index('class Relay:'):s.index('def confirmed_play_server')])
if __name__=='__main__':unittest.main()
