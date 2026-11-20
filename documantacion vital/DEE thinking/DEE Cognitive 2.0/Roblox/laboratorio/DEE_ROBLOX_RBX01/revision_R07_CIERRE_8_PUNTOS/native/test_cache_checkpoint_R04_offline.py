"""Pure filesystem prototype fixtures. No DEE, engine, queue or SDK imports."""
from pathlib import Path
import hashlib,importlib.util,json,os,sys,tempfile,time,unittest
HERE=Path(__file__).resolve().parent
P=HERE/'prototipos/cache_fuentes_C02_R04.py'
spec=importlib.util.spec_from_file_location('cache_checkpoint_R04_fixture',P)
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
BASE_STAT=Path.stat;BASE_RESOLVE=Path.resolve;BASE_LSTAT=Path.lstat
class SyntheticLease:
 def __init__(self,path):self.path=path
 def close(self):pass
def stamp(p):
 s=p.stat();return[s.st_dev,s.st_ino,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
def probe(paths,repeats=6):
 return[{'path':str(p.resolve(strict=True)),'is_file':p.is_file(),'stat':stamp(p),
         'lstat_size':p.lstat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
         'text':p.read_text('utf-8')}for _ in range(repeats)for p in paths]
class MetadataPassTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  self.system=self.root/'system';(self.system/'app').mkdir(parents=True);(self.system/'capacidades').mkdir()
  (self.system/'estado').mkdir()
  self.a=self.system/'app/example.py';self.a.write_text('VALUE=123\n','utf-8')
  self.b=self.system/'capacidades/protocol.json';self.b.write_text('{"scope":"synthetic"}\n','utf-8')
  self.mutable=self.system/'estado/current.json';self.mutable.write_text('{"current":0}\n','utf-8')
  self.cache=None
 def tearDown(self):
  if self.cache is not None:self.cache.close()
  self.assertIs(Path.stat,BASE_STAT);self.assertIs(Path.resolve,BASE_RESOLVE);self.assertIs(Path.lstat,BASE_LSTAT)
  self.tmp.cleanup()
 def open(self,real=False):
  self.cache=module.ImmutableSourceCache(self.system,lease_factory=module.WindowsReadLease if real else SyntheticLease).open()
  return self.cache
 def test_01_exact_filesystem_validator_payload(self):
  cache=self.open();before=probe([self.a,self.b])
  with cache.checkpoint_pass()as counts:after=probe([self.a,self.b])
  self.assertEqual(before,after)
  self.assertGreaterEqual(counts['stat_hits'],12);self.assertGreaterEqual(counts['resolve_hits'],10)
  self.assertEqual(counts['fresh_rechecks'],2)
 def test_02_mutable_state_is_always_fresh(self):
  cache=self.open()
  with cache.checkpoint_pass()as counts:
   first=self.mutable.stat().st_size;self.mutable.write_text('{"current":123456789}\n','utf-8')
   self.assertNotEqual(first,self.mutable.stat().st_size)
   self.assertIn('123456789',self.mutable.read_text('utf-8'))
  self.assertEqual(counts['stat_hits'],0);self.assertEqual(counts['fresh_rechecks'],0)
 def test_03_no_cross_checkpoint_stat_reuse(self):
  cache=self.open()
  for _ in range(2):
   with cache.checkpoint_pass()as counts:
    self.a.stat();self.a.stat()
   self.assertEqual(counts['stat_misses'],1);self.assertEqual(counts['stat_hits'],1)
 def test_04_exception_restores_methods_and_clears_pass(self):
  cache=self.open()
  with self.assertRaisesRegex(RuntimeError,'synthetic validator'):
   with cache.checkpoint_pass():self.a.stat();raise RuntimeError('synthetic validator')
  self.assertFalse(cache._checkpoint_pass_active_R04)
  self.assertIs(Path.stat,BASE_STAT);self.assertIs(Path.resolve,BASE_RESOLVE)
  with cache.checkpoint_pass():self.a.stat()
 def test_05_source_change_is_detected_by_final_fence(self):
  cache=self.open();original=self.a.read_bytes()
  try:
   with self.assertRaisesRegex(RuntimeError,'changed within checkpoint'):
    with cache.checkpoint_pass():self.a.stat();self.a.write_text('VALUE=9876543210\n','utf-8')
  finally:self.a.write_bytes(original) # synthetic fixture only, before closing its fake lease.
 def test_06_nested_or_unopened_pass_refused(self):
  empty=module.ImmutableSourceCache(self.system,lease_factory=SyntheticLease)
  with self.assertRaisesRegex(RuntimeError,'open deny-write'):
   with empty.checkpoint_pass():pass
  cache=self.open()
  with cache.checkpoint_pass():
   with self.assertRaisesRegex(RuntimeError,'nonnested'):
    with cache.checkpoint_pass():pass
 def test_07_lease_prevents_actual_source_write_on_windows(self):
  if os.name!='nt':self.skipTest('Windows lease proof requires Windows')
  cache=self.open(real=True)
  with cache.checkpoint_pass():
   with self.assertRaises(OSError):self.a.write_text('DENIED\n','utf-8')
  self.assertEqual(self.a.read_text('utf-8'),'VALUE=123\n')
 def test_08_no_operational_payload_cache_or_new_whitelist(self):
  cache=self.open()
  self.assertNotIn(module.key(self.mutable),cache.entries)
  with cache.checkpoint_pass():probe([self.a,self.b],2)
  witness=cache.witness();self.assertFalse(witness['operational_state_cached']);self.assertTrue(witness['validators_not_skipped'])
  self.assertEqual(set(cache.entries),{module.key(self.a),module.key(self.b)})
if __name__=='__main__':unittest.main(verbosity=2)
