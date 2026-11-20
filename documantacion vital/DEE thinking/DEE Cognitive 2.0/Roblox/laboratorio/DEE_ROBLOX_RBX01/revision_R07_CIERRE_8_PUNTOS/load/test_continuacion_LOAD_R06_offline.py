"""No Native execution: stock and AST first-phase continuation fixtures."""
import ast,importlib.util
from pathlib import Path
import unittest
FILE=Path(__file__).with_name('continuar_carga_v3_R06.py');s=importlib.util.spec_from_file_location('continued_load_pure',FILE);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class ContinuationTests(unittest.TestCase):
    def test_ASK_spends_exactly_one(self):self.assertEqual(m.consumed_stock(164,{'name':'ASK_STATION','null':False}),(163,1))
    def test_SKIP_does_not_spend(self):self.assertEqual(m.consumed_stock(164,{'name':'SKIP_STATION','null':False}),(164,0))
    def test_NULL_does_not_invent_query(self):self.assertEqual(m.consumed_stock(164,{'name':'SAFE_WAIT','null':True}),(164,0))
    def test_underflow_rejected(self):
        with self.assertRaises(ValueError):m.consumed_stock(0,{'name':'ASK_STATION','null':False})
    def test_first_episode_branch_never_calls_decision(self):
        tree=ast.parse(FILE.read_text('utf8'));branch=next(n for n in ast.walk(tree)if isinstance(n,ast.If)and ast.unparse(n.test)=='index == 0'and any(isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='q1'for t in x.targets)for x in n.body))
        calls=[n for statement in branch.body for n in ast.walk(statement)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='phase']
        self.assertEqual([ast.literal_eval(n.args[1])for n in calls],['query_sensor'])
    def test_no_clone_or_reset(self):
        tree=ast.parse(FILE.read_text('utf8'))
        for n in ast.walk(tree):
            if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute):self.assertNotIn(n.func.attr,('initialize','run_until','advance','restore_snapshot'))
if __name__=='__main__':unittest.main()
