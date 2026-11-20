"""Pure fixtures: no DEE import, owner, MCP, database or material call."""
import ast
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'control/continuar34_oldscope_R01.py'
spec=importlib.util.spec_from_file_location('continuation34_fixture',SOURCE)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ContinuationTests(unittest.TestCase):
    def receipt(self,folder,mutate=False):
        state={'phase':'Q2','S':{'sessionId':module.SESSION,'lifeId':module.LIFE,'nativeTick':999363}}
        value={'before':state,'after':state,'result':{'observation':{'phase':'ROUTE_CHOICE','seq':68,'previousActionId':module.Q1_ID}},'reconciliation':'EXACT_ALREADY_APPLIED_Q1_CACHED_RESULT'}
        if mutate:value['after']={**state,'unexpected':True}
        proof={'no_Native_request_submitted':True,'no_BEGIN_no_Q1_material_replay':True,'raw_tool_responses':{'R07_RECONCILE34_Q1_CACHED_RECEIPT':{'isError':False,'content':[{'type':'text','text':json.dumps(value)}]}}}
        (folder/'RECONCILIACION34_ROOT_R01.json').write_text(json.dumps(proof),encoding='utf8')
    def test_receipt_returns_original_packet(self):
        with tempfile.TemporaryDirectory()as temp:
            folder=Path(temp);self.receipt(folder)
            _,value=module.reconciled_receipt(folder)
            self.assertEqual(value['result']['observation']['seq'],68)
    def test_receipt_with_world_change_rejected(self):
        with tempfile.TemporaryDirectory()as temp:
            folder=Path(temp);self.receipt(folder,True)
            with self.assertRaisesRegex(ValueError,'ZERO_WORLD_CHANGE'):module.reconciled_receipt(folder)
    def test_no_decision_begin_or_initialize_call(self):
        tree=ast.parse(SOURCE.read_text('utf8'))
        kinds=[]
        for node in ast.walk(tree):
            if not isinstance(node,ast.Call):continue
            if isinstance(node.func,ast.Name)and node.func.id=='native':
                kinds.append(ast.literal_eval(node.args[1]))
            if isinstance(node.func,ast.Attribute):
                self.assertNotIn(node.func.attr,('initialize','run_until','advance'))
                if node.func.attr=='call':
                    self.assertNotEqual(ast.literal_eval(node.args[1]),'begin')
        self.assertEqual(set(kinds),{'query_sensor','function','feedback'})

if __name__=='__main__':unittest.main()
