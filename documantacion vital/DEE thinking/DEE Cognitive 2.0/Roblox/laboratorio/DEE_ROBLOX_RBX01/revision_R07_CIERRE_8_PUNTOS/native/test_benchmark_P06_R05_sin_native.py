"""Static and synthetic-SQL safeguards only. Never opens a DEE world."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sqlite3,sys,tempfile,unittest
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
SCRIPT=HERE/'benchmark_dependencias_P06_R05.py'
spec=importlib.util.spec_from_file_location('_p06_offline_fixture',SCRIPT)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
def read(p):return p.read_text('utf-8')
def nodes(s,t):return{n.name:ast.dump(n,include_attributes=False)for n in ast.parse(s).body if isinstance(n,t)}
class PreparedChecks(unittest.TestCase):
 def test_01_pure_import_and_final_deadline(self):
  self.assertEqual(m.HARD_FINISH,1794884820);self.assertEqual(m.LIMIT,536870912)
  tree=ast.parse(read(SCRIPT))
  imports=[n.module for n in tree.body if isinstance(n,ast.ImportFrom)]
  self.assertNotIn('app.mundo_genesis_apd05',imports);self.assertNotIn('dee_thinking',imports)
 def test_02_actual_job_guard_and_official_python(self):
  s=read(SCRIPT)
  self.assertIn('pc.protect_current(memory_limit=LIMIT)',s)
  self.assertIn("resources.get('job_memory_limit')==LIMIT",s)
  self.assertIn("PRODUCT/'motor/python313/python.exe'",s)
  self.assertIn('spawn_owned(argv,cwd=ROOT,stdout=so,stderr=se,memory_limit=LIMIT)',s)
 def test_03_no_actor_queue_service_or_save_call(self):
  tree=ast.parse(read(SCRIPT))
  calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)]
  self.assertFalse(any(isinstance(n.func,ast.Name)and n.func.id in('QueueDB','PersistentService')for n in calls))
  self.assertFalse(any(isinstance(n.func,ast.Attribute)and n.func.attr in('execute','advance','control','run_until')
    and isinstance(n.func.value,ast.Name)and n.func.value.id in('world','adapter','owner','service','a')for n in calls))
  self.assertIn("'?mode=ro&immutable=1'",read(SCRIPT))
  self.assertIn('world.a.run_until=forbid',read(SCRIPT))
 def test_04_full_payload_and_physical_not_subset(self):
  s=read(SCRIPT)
  self.assertIn('payload=world.operational_dependencies()',s)
  self.assertIn("len({p['payload_sha256']for p in passes})==1",s)
  self.assertIn('world.fingerprint()',s);self.assertIn('metadata_hash(world.a)',s)
  self.assertIn("'operational_files_identical':unchanged",s)
  self.assertIn("'no_operational_add_delete':set(before_files)==set(after_files)",s)
  self.assertIn("'Native_ticks':final_physical['tick']-basis['expected_tick']",s)
 def test_05_separate_prospective_protocol_unchanged_criterion(self):
  p=json.loads(read(ROOT/'protocolo/PROTOCOLO_P06_DEPENDENCIAS_R05.json'))
  self.assertEqual(p['pass_order'],['BASE_1','PROTO','BASE_2'])
  self.assertEqual(p['criterion']['minimum_fraction_reduction'],.20)
  self.assertEqual(p['Native_ticks_allowed'],0);self.assertFalse(p['queue_writer_allowed'])
  self.assertEqual(p['campaign_hard_close_utc'],'2026-11-17T03:07:00Z')
 def test_06_closed_transport_rejects_pending_without_mutation(self):
  with tempfile.TemporaryDirectory()as tmp:
   d=Path(tmp);life='SYNTHETIC';(d/'CONTEXTO_EJECUCION.json').write_text(json.dumps({'life':life}))
   folder=d/'sistema/estado/servicios_persistentes'/life;folder.mkdir(parents=True);db=folder/'cola.sqlite3'
   con=sqlite3.connect(db);con.execute('CREATE TABLE meta(key TEXT,value TEXT)');con.execute('CREATE TABLE requests(status TEXT)')
   con.execute('INSERT INTO meta VALUES(?,?)',('owner',json.dumps({'running':False})))
   con.execute('INSERT INTO requests VALUES(?)',('queued',));con.commit();con.close()
   before=hashlib.sha256(db.read_bytes()).hexdigest()
   with self.assertRaisesRegex(ValueError,'pending/uncertain'):m.closed_transport(d)
   self.assertEqual(hashlib.sha256(db.read_bytes()).hexdigest(),before)
 def test_07_whole_operational_tree_comparison_detects_changes(self):
  with tempfile.TemporaryDirectory()as tmp:
   p=Path(tmp);(p/'a').write_text('one');before=m.tree_hashes(p)
   (p/'a').write_text('two');(p/'b').write_text('added');after=m.tree_hashes(p)
   self.assertNotEqual(before,after);self.assertNotEqual(set(before),set(after))
 def test_08_final_reference_lease_does_not_change_policy_or_quota(self):
  c=ROOT/'comparadores';old=read(c/'cliente_modelo_v3_R04.py');new=read(c/'cliente_modelo_v3_R05.py')
  self.assertEqual(nodes(old,ast.ClassDef),nodes(new,ast.ClassDef));self.assertEqual(nodes(old,ast.FunctionDef),nodes(new,ast.FunctionDef))
  self.assertIn('STOP_NEW_CALLS=1794880800',new);self.assertIn("ROOT/'CUOTA_LLM_V3.json'",new)
  old=nodes(read(c/'backends_v3_R04.py'),ast.ClassDef);new=nodes(read(c/'backends_v3_R05.py'),ast.ClassDef)
  for name in('ProgrammedBackend','ConventionalAIBackend','PersistedLocalPolicy'):self.assertEqual(old[name],new[name])
 def test_09_final_pilot_owner_and_short_filename(self):
  s=read(ROOT/'prototipo/NATIVE_LIMPIO_R07/ejecutar_piloto_R07_preparado_R05.py')
  self.assertIn('CUTOFF=1794884820;LAST_NEW=1794880800',s)
  self.assertIn("ROOT/'native/owner_support_v3_R05.py'",s)
  self.assertIn("default='PILOTO_R07.rbxlx'",s)
  self.assertIn("not journal.exists()or journal.stat().st_size==0",s)
if __name__=='__main__':unittest.main(verbosity=2)
