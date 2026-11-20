"""Static AST fixtures: never imports or executes the migrator."""
import ast
from pathlib import Path
import unittest
class StaticLeaseREV2(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tree=ast.parse(Path(__file__).with_name("renovar_PILOT_unused_R07_REV2.py").read_bytes())
  cls.apply=next(n for n in cls.tree.body if isinstance(n,ast.FunctionDef) and n.name=="apply")
 def test_result_before_unique_marker_unlink(self):
  calls=[n for n in ast.walk(self.apply) if isinstance(n,ast.Call)]
  unlinks=[n for n in calls if isinstance(n.func,ast.Attribute) and n.func.attr=="unlink" and isinstance(n.func.value,ast.Name) and n.func.value.id=="marker"]
  results=[n for n in calls if isinstance(n.func,ast.Name) and n.func.id=="create" and n.args and isinstance(n.args[0],ast.BinOp) and isinstance(n.args[0].right,ast.Constant) and n.args[0].right.value=="RESULTADO.json"]
  self.assertEqual(len(unlinks),1);self.assertEqual(len(results),1);self.assertLess(results[0].lineno,unlinks[0].lineno)
 def test_final_proof_uses_tx_before_result(self):
  final=[n for n in ast.walk(self.apply) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="final_proof" for t in n.targets)]
  self.assertEqual(len(final),1);call=final[0].value
  self.assertIsInstance(call,ast.Call);self.assertIsInstance(call.func,ast.Name);self.assertEqual(call.func.id,"proof")
  self.assertEqual(len(call.args),1);self.assertIsInstance(call.args[0],ast.Name);self.assertEqual(call.args[0].id,"tx")
  result=next(n for n in ast.walk(self.apply) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="result" for t in n.targets))
  self.assertLess(final[0].lineno,result.lineno)
  physical=next(v for k,v in zip(result.value.keys,result.value.values) if isinstance(k,ast.Constant) and k.value=="physical_after")
  self.assertIsInstance(physical,ast.Subscript);self.assertIsInstance(physical.value,ast.Name);self.assertEqual(physical.value.id,"final_proof")
if __name__=="__main__":unittest.main()
