"""Pure synthetic cache tests; never reads the actual package plan."""
import importlib.util, unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('privacy_incremental',ROOT/'analisis/revisar_privacidad_incremental_R08.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
class CacheTests(unittest.TestCase):
    def test_same_source_sha_not_rescanned(self):
        raw=b'{}';cache={'coverage':[{'source':'synthetic.json','bytes':2,'sha256':p.digest(raw)}]}
        with patch.object(p,'scan_text',side_effect=AssertionError('must not rescan')):r,f,l=p.review_member(raw,'synthetic.json','newalias.json',cache)
        self.assertEqual(r['review'],'REUSED_EXACT_CACHED_SHA');self.assertEqual(f,[])
    def test_changed_bytes_are_reviewed(self):
        cache={'coverage':[{'source':'synthetic.json','bytes':2,'sha256':p.digest(b'{}')}]}
        r,f,l=p.review_member(b'{"note":"person@example.invalid"}','synthetic.json','test.json',cache)
        self.assertEqual(r['review'],'NEW_OR_CHANGED_BYTES_REVIEWED');self.assertEqual(f[0]['kind'],'EMAIL_LIKE_PERSONAL_DATA');self.assertNotIn('value',f[0])
    def test_binary_limit_retained_from_cache(self):
        raw=b'\xff';cache={'coverage':[{'source':'synthetic.png','bytes':1,'sha256':p.digest(raw)}], 'skipped_or_limited':[{'source':'synthetic.png','reason':'No visual review'}]}
        r,f,l=p.review_member(raw,'synthetic.png','image.png',cache);self.assertEqual(l[0]['reason'],'No visual review')
if __name__=='__main__':unittest.main(verbosity=2)
