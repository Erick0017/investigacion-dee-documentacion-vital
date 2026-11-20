"""Bounded pure fixtures: import, ABI, literal parent and no route substitution."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
class Test(unittest.TestCase):
    def test_pure_import_and_contract(self):
        before=set(sys.modules)
        m=load('_r07_fixture_world',ROOT/'control/world_comprimido_v3.py')
        added=set(sys.modules)-before
        self.assertFalse(any(x.startswith(('dee_thinking','dee_v27','rbx07_native'))for x in added))
        self.assertEqual(m.BASE.FINISH,1794863220)
        self.assertTrue(all(hasattr(m.CompressedWorld,k)for k in('initialize','call','checkpoint','close')))
        self.assertIn('expected_place',m.CompressedWorld.__init__.__code__.co_varnames)
    def test_source_parent_and_namespace(self):
        p=ROOT/'control/world_comprimido_v3.py';s=p.read_text('utf8');ast.parse(s)
        self.assertIn("expected={k:state[k]",s)
        self.assertIn('WorldAPI_R07',s)
        self.assertIn("'R07_TECHNICAL_IDENTITY'",s)
        self.assertIn("JSONEncode(r06Value)",s)
        c=(ROOT/'control/transporte_comprimido_v3.py').read_text('utf8')
        self.assertIn('WorldAPI_R07',c);self.assertNotIn('WorldAPI_R06',c)
    def test_actual_actions_only(self):
        s=(ROOT/'control/run_integrated_v3.py').read_text('utf8');tree=ast.parse(s)
        self.assertIn("'name':first['action']",s);self.assertIn("'name':route['action']",s)
        self.assertIn("'host_order_prepared':False",s)
        self.assertIn('29<=a.stop_cycle<=52',s)
        self.assertIn("cycle-28",s)
        execute=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='execute')
        self.assertTrue(any(isinstance(x,ast.Try)and x.finalbody for x in execute.body))
    def test_no_tool_creation_at_import(self):
        for name in('run_integrated_v3.py','world_comprimido_v3.py','mcp_persistente_v3.py','transporte_comprimido_v3.py'):
            t=ast.parse((ROOT/'control'/name).read_text('utf8'))
            for node in t.body:
                if isinstance(node,ast.Expr)and isinstance(node.value,ast.Call):
                    self.fail('Top-level executable call '+name)
if __name__=='__main__':unittest.main()
