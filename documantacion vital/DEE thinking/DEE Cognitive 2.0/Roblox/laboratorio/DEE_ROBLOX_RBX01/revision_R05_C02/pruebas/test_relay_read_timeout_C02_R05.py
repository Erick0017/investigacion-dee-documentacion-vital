"""Timeout classification only; no MCP child, HTTP, model, Native or GUI."""
import ast
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/'control/studio_mailbox_relay_C02_R05.py'
spec=importlib.util.spec_from_file_location('_C02_R05_read_timeout_fixture',FILE)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class ReadTimeoutTests(unittest.TestCase):
    def invoke(self,name,args):
        obj=m.MCPClient.__new__(m.MCPClient);calls=[]
        def call(method,params=None,**kwargs):
            calls.append((method,params,kwargs));return {'content':[{'type':'text','text':'{"fixture":true}'}]}
        obj.call=call;obj.tool(name,args);return calls
    def test_inventory_wait120_one_read_only_call(self):
        calls=self.invoke('list_roblox_studios',{});self.assertEqual(len(calls),1);self.assertEqual(calls[0][2]['timeout'],120)
    def test_exact_pull_and_identity_guards_wait120(self):
        for code in(m.PULL_CODE,m.ACCOUNT_CODE,m.PREPARED_SERVER_CODE):
            self.assertEqual(self.invoke('execute_luau',{'code':code})[0][2]['timeout'],120)
    def test_mailbox_CAS_stays20_one_call(self):
        calls=self.invoke('execute_luau',{'code':m.push_code('RAW_FIXTURE','REPLY_FIXTURE')})
        self.assertEqual(len(calls),1);self.assertEqual(calls[0][2]['timeout'],20)
    def test_unrecognized_luau_is_not_reclassified_read_only(self):
        self.assertEqual(self.invoke('execute_luau',{'code':'return {not_a_whitelisted_read=true}'})[0][2]['timeout'],20)
    def test_initialize_and_tools_list_are_bounded120(self):
        tree=ast.parse(FILE.read_text('utf8'))
        client=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='MCPClient')
        init=next(n for n in client.body if isinstance(n,ast.FunctionDef)and n.name=='initialize')
        calls=[n for n in ast.walk(init)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='call'and n.args and isinstance(n.args[0],ast.Constant)and n.args[0].value in('initialize','tools/list')]
        self.assertEqual(len(calls),2)
        self.assertTrue(all(any(k.arg=='timeout'and isinstance(k.value,ast.Constant)and k.value.value==120 for k in n.keywords)for n in calls))
    def test_old_R04_and_no_attach_active_or_policy_change(self):
        old=(ROOT/'control/studio_mailbox_relay_C02_R04.py').read_text('utf8')
        self.assertIn('timeout=10',old)
        new=FILE.read_text('utf8');self.assertNotIn('--attach-active',new)
        self.assertIn('do not replay the mutation',new)
        self.assertIn('REQUEST_TIMEOUT_SECONDS = 120',new)


if __name__=='__main__':unittest.main(verbosity=2)
