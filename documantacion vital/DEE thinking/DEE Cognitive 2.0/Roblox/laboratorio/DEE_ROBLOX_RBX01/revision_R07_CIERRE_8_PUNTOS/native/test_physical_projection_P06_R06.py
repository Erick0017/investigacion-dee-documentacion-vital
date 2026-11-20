"""Pure closed-record schema fixtures; importing the benchmark opens no world."""
import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('p06_r06_projection',Path(__file__).with_name('benchmark_dependencias_P06_R06.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class ProjectionTests(unittest.TestCase):
    def card(self):return dict(N=67,tick=991187,RAW_sha256='a'*64,clocks_sha256='b'*64,sites=300763,occupied=148,max_s_reg=4530,basic_buffers_bytes=9624416)
    def test_exact_four_fields_equal_eight_field_projection(self):
        card=self.card();observed={k:card[k]for k in module.PHYSICAL_CORE}
        self.assertEqual(module.physical_projection(card,recorded=True),module.physical_projection(observed,recorded=False))
    def test_unknown_card_field_rejected(self):
        card=self.card();card['unknown']=1
        with self.assertRaisesRegex(ValueError,'schema'):module.physical_projection(card,recorded=True)
    def test_observed_extra_field_rejected(self):
        with self.assertRaisesRegex(ValueError,'schema'):module.physical_projection(self.card(),recorded=False)
    def test_boolean_tick_rejected(self):
        card=self.card();card['tick']=True
        with self.assertRaisesRegex(ValueError,'Typed fixed'):module.physical_projection(card,recorded=True)
    def test_corrupt_digest_rejected(self):
        card=self.card();card['RAW_sha256']='g'*64
        with self.assertRaisesRegex(ValueError,'SHA256'):module.physical_projection(card,recorded=True)
    def test_real_shared_hash_mismatch_not_normalized(self):
        card=self.card();observed={k:card[k]for k in module.PHYSICAL_CORE};observed['RAW_sha256']='c'*64
        self.assertNotEqual(module.physical_projection(card,recorded=True),module.physical_projection(observed,recorded=False))
if __name__=='__main__':unittest.main()
