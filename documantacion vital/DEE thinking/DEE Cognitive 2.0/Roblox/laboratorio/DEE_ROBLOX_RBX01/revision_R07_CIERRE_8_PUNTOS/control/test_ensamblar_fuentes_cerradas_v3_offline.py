"""Synthetic FS fixtures for the closed-source selector. Zero Native/DB/MCP."""
from pathlib import Path
import contextlib,hashlib,importlib.util,io,json,tempfile,unittest
SCRIPT=Path(__file__).with_name('ensamblar_fuentes_cerradas_v3.py')
spec=importlib.util.spec_from_file_location('_selector_v3_fs',SCRIPT)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def raw(v):return(json.dumps(v,sort_keys=True)+'\n').encode()
class Fixtures(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)/'revision_R07_CIERRE_8_PUNTOS'
  (self.root/'control').mkdir(parents=True);(self.root/'evidencia').mkdir()
  self.b=raw({'owner_closed':True,'final_tick':123,'status':'CLOSED'})
  (self.root/'evidencia/RESULTADO.json').write_bytes(self.b)
  self.row={'source':'evidencia/RESULTADO.json','archive':'evidencia/RESULTADO.json','role':'native_primary','bytes':len(self.b),'sha256':m.digest(self.b)}
  self.group={'family':'CTRL','label':'SYNTHETIC_NOT_NATIVE','status':'CLOSED','basis':{**self.row,'proof_kind':'OWNER_CLOSED','assertions':[{'pointer':'/owner_closed','equals':True}]},'files':[dict(self.row)]}
  self.registry={'schema':'DEE.R07.ClosedSourceRegistry.R01','groups':[self.group]}
  self.plan={'finalized':False,'files':[]}
 def tearDown(self):self.tmp.cleanup()
 def run_case(self):
  return m.assemble(self.plan,self.registry,m.Sources(self.root))
 def test_01_closed_sources_remain_tentative(self):
  out=self.run_case();self.assertFalse(out['finalized']);self.assertEqual(len(out['files']),1)
  self.assertEqual(out['closed_source_assembly']['Native_calls'],0)
 def test_02_pending_is_not_read_or_counted(self):
  self.registry['groups']=[{'family':'LOAD','label':'PENDING_NOT_MATERIAL','status':'PENDING','reason':'Missing closure'}]
  self.assertEqual(self.run_case()['files'],[])
 def test_03_bad_hash_rejected(self):
  self.group['basis']['sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'SOURCE_DIFFERS'):self.run_case()
 def test_04_open_owner_rejected(self):
  b=raw({'owner_closed':False});(self.root/'evidencia/RESULTADO.json').write_bytes(b)
  for r in(self.row,self.group['basis'],self.group['files'][0]):r.update(bytes=len(b),sha256=m.digest(b))
  with self.assertRaisesRegex(ValueError,'CLOSURE_ASSERTION'):self.run_case()
 def test_05_archive_collision_rejected(self):
  (self.root/'evidencia/OTHER.json').write_bytes(self.b)
  self.plan['files']=[{**self.row,'source':'evidencia/OTHER.json'}]
  with self.assertRaisesRegex(ValueError,'ARCHIVE_COLLISION'):self.run_case()
 def test_06_scope_escape_rejected(self):
  p=self.root.parent/'OTHER.json';p.write_bytes(self.b)
  self.group['basis']['source']=str(p);self.group['files'][0]['source']=str(p)
  with self.assertRaisesRegex(ValueError,'SOURCE_OUTSIDE'):self.run_case()
 def test_07_finalized_plan_rejected(self):
  self.plan['finalized']=True
  with self.assertRaisesRegex(ValueError,'TENTATIVE'):self.run_case()
 def test_08_explicit_portable_map_without_original(self):
  pack=self.root/'extracted';(pack/'CONTROL').mkdir(parents=True);(pack/'evidencia').mkdir()
  (pack/'evidencia/RESULTADO.json').write_bytes(self.b)
  (pack/'CONTROL/MANIFIESTO_SHA256.json').write_bytes(raw({'files':[self.row]}))
  (self.root/'evidencia/RESULTADO.json').unlink()
  out=m.assemble(self.plan,self.registry,m.Sources(self.root,pack))
  self.assertTrue(out['closed_source_assembly']['portable_verification'])
 def test_09_semantic_assertion_type_not_bool_as_int(self):
  self.group['basis']['assertions']=[{'pointer':'/final_tick','equals':True}]
  with self.assertRaisesRegex(ValueError,'CLOSURE_ASSERTION'):self.run_case()
 def test_10_no_overwrite_output(self):
  plan=self.root/'control/plan.json';reg=self.root/'control/registry.json';out=self.root/'control/out.json'
  plan.write_bytes(raw(self.plan));reg.write_bytes(raw(self.registry));out.write_text('PRESERVE')
  with self.assertRaisesRegex(ValueError,'FRESH_JSON'):
   with contextlib.redirect_stdout(io.StringIO()):m.main(['--workspace-root',str(self.root),'--plan',str(plan),'--registry',str(reg),'--output',str(out)])
  self.assertEqual(out.read_text(),'PRESERVE')
 def test_11_manifest_source_alias_is_exact_absolute(self):
  self.plan['files']=[dict(self.row)]
  out=self.run_case()
  self.assertEqual(out['files'][0]['source'],str((self.root/'evidencia/RESULTADO.json').resolve()))
  self.assertEqual(out['files'][0]['archive'],'evidencia/RESULTADO.json')
if __name__=='__main__':unittest.main(verbosity=2)
