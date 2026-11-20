"""Real synthetic Deflate ZIP verification; declared maxima are large, payloads tiny."""
import hashlib, importlib.util, json, tempfile, unittest, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def module(name,filename):
 s=importlib.util.spec_from_file_location(name,ROOT/'control'/filename);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
p=module('packager_R04','expediente_compacto_v3_R04.py');old=module('packager_R03','expediente_compacto_v3_R03.py')
class VerifyDelta(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'pruebas');self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
 def make(self,names=None,role_bad=False,bad_hash=False,traversal=False):
  names=names or [f'legacy/{i}.json'for i in range(4)]+sorted(p.EXTRA_CLOSED_WORLD_EXCEPTIONS)
  if traversal:names=list(names)+['../outside.json']
  rows=[];values={}
  for name in names:
   raw=b'{"synthetic":true}';values[name]=raw
   row={'archive':name,'source':str(self.root/name),'role':'native_primary','bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'max_bytes':8_000_000}
   if role_bad and name in p.EXTRA_CLOSED_WORLD_EXCEPTIONS:row['role']='analysis'
   rows.append(row)
  if bad_hash:rows[0]['sha256']='0'*64
  protected=json.dumps({'all_eleven_unchanged':True,'files':[{'synthetic':i}for i in range(11)]}).encode()
  values[p.PROTECTION]=protected;rows.append({'archive':p.PROTECTION,'source':None,'role':'verification','bytes':len(protected),'sha256':hashlib.sha256(protected).hexdigest()})
  values[p.MANIFEST]=json.dumps({'schema':'DEE.INTEGRAL.V3.content_manifest.R01','files':rows}).encode()
  target=self.root/'synthetic.zip'
  with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED)as z:
   for name,raw in values.items():z.writestr(name,raw)
  return target
 def test_real_six_declared_primaries_verify_and_extract(self):
  target=self.make()
  with self.assertRaisesRegex(ValueError,'MANIFEST_LARGE_PRIMARY_EXCEPTION'):old.verify(target)
  result=p.verify(target,self.root/'clean');self.assertTrue(result['all_member_CRC_SHA_UTF8_checks']);self.assertEqual(result['members'],8)
  self.assertEqual(len(list((self.root/'clean').rglob('*.json'))),8)
 def test_seventh_unlisted_primary_rejected(self):
  names=[f'legacy/{i}.json'for i in range(5)]+sorted(p.EXTRA_CLOSED_WORLD_EXCEPTIONS)
  with self.assertRaisesRegex(ValueError,'MANIFEST_LARGE_PRIMARY_EXCEPTION'):p.verify(self.make(names))
 def test_six_arbitrary_large_primaries_not_allowed(self):
  names=[f'legacy/{i}.json'for i in range(5)]+[sorted(p.EXTRA_CLOSED_WORLD_EXCEPTIONS)[0]]
  with self.assertRaisesRegex(ValueError,'MANIFEST_LARGE_PRIMARY_EXCEPTION'):p.verify(self.make(names))
 def test_named_exception_still_needs_native_role(self):
  with self.assertRaisesRegex(ValueError,'MANIFEST_LARGE_PRIMARY_EXCEPTION'):p.verify(self.make(role_bad=True))
 def test_real_member_hash_mismatch_rejected(self):
  with self.assertRaisesRegex(ValueError,'MEMBER_HASH_MISMATCH'):p.verify(self.make(bad_hash=True))
 def test_zip_traversal_rejected(self):
  with self.assertRaises(ValueError):p.verify(self.make(traversal=True))
if __name__=='__main__':unittest.main(verbosity=2)
