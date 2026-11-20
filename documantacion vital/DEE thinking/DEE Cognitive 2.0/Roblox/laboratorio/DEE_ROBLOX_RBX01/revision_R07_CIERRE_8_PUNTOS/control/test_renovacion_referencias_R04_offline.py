"""Lease-only static fixtures; no service, HTTP, SDK, model or Native."""
from pathlib import Path
import ast,hashlib,json,unittest
ROOT=Path(__file__).resolve().parent.parent
C=ROOT/'comparadores';P=ROOT/'prototipo/NATIVE_LIMPIO_R07'
def text(p):return p.read_text('utf-8')
def named_nodes(s,klass):return{n.name:ast.dump(n,include_attributes=False)for n in ast.parse(s).body if isinstance(n,klass)}
def constant(s,key):
 for n in ast.parse(s).body:
  if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id==key for t in n.targets):return ast.literal_eval(n.value)
 raise AssertionError(key)
class LeaseChecks(unittest.TestCase):
 def test_01_old_sources_unchanged(self):
  witness=json.loads((ROOT/'control/REFERENCIAS_PILOTO_LEASE_R04.json').read_text('utf-8'))
  for p,h in witness['originals'].items():self.assertEqual(hashlib.sha256(Path(p).read_bytes()).hexdigest(),h)
 def test_02_client_grammar_and_model_policy_identical(self):
  old=text(C/'cliente_modelo_v3.py');new=text(C/'cliente_modelo_v3_R04.py')
  self.assertEqual(named_nodes(old,ast.FunctionDef),named_nodes(new,ast.FunctionDef))
  self.assertEqual(named_nodes(old,ast.ClassDef),named_nodes(new,ast.ClassDef))
  self.assertEqual(constant(new,'STOP_NEW_CALLS'),1794870000)
  self.assertIn("ROOT/'CUOTA_LLM_V3.json'",new);self.assertNotIn('CUOTA_LLM_V3_R04.json',new)
 def test_03_reference_deciders_and_public_rules_identical(self):
  old=text(C/'backends_v3.py');new=text(C/'backends_v3_R04.py')
  self.assertEqual(constant(old,'PUBLIC_RULES'),constant(new,'PUBLIC_RULES'))
  a=named_nodes(old,ast.ClassDef);b=named_nodes(new,ast.ClassDef)
  for n in('ProgrammedBackend','ConventionalAIBackend','PersistedLocalPolicy'):self.assertEqual(a[n],b[n])
  self.assertIn('from cliente_modelo_v3_R04 import',new)
 def test_04_server_new_lifecycle_without_model_or_memory_change(self):
  old=text(C/'servidor_modelo_v3.py');new=text(C/'servidor_modelo_v3_R04.py')
  self.assertEqual(constant(new,'HARD_FINISH'),1794874020)
  self.assertEqual(constant(new,'STOP_NEW_CALLS'),1794870000)
  self.assertEqual(ast.dump(ast.parse(old).body[0],include_attributes=False).split('\n')[0],ast.dump(ast.parse(new).body[0],include_attributes=False).split('\n')[0])
  self.assertIn('SERVIDOR_MODELO_V3_R04.jsonl',new);self.assertIn('ollama_V3_R04.stop',new)
  self.assertIn('MEMORY_LIMIT=6*1024**3',new)
  self.assertIn('a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72',new)
 def test_05_runner_horizon_and_new_transport(self):
  s=text(ROOT/'control/runner_comparador_v3_R04.py');compile(s,'runner','exec')
  self.assertIn('from world_comprimido_v3_R04 import CompressedWorld',s)
  self.assertIn('29<=a.stop_cycle<=46',s);self.assertEqual(constant(s,'CUTOFF'),1794870000)
  self.assertEqual(constant(s,'HARD_CLOSE'),1794874020)
 def test_06_pilot_stays_fresh_and_raw_string_once(self):
  s=text(P/'ejecutar_piloto_R07_preparado_R03.py');compile(s,'pilot','exec')
  self.assertEqual(constant(s,'CUTOFF'),1794874020);self.assertEqual(constant(s,'LAST_NEW'),1794870000)
  self.assertIn("ROOT/'native/owner_support_v3_R04.py'",s)
  self.assertIn("default='PILOTO_R07.rbxlx'",s)
  self.assertIn("card['physical']['tick']==991187",s)
  self.assertIn("not journal.exists()or journal.stat().st_size==0",s)
  self.assertIn("a:deliverAction('+literal(wire)+')",s)
  self.assertNotIn('a:deliverAction(H:JSONDecode',s)
if __name__=='__main__':unittest.main(verbosity=2)
