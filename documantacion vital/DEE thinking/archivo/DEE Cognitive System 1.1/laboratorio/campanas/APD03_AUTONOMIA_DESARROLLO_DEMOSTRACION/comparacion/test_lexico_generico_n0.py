"""Static/preflight fixture checks; fake observations, zero Native imports."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest


def lexical():
    path=Path(__file__).with_name('lexico_generico_apd03_r01.py')
    spec=importlib.util.spec_from_file_location('lexical_design_fixture',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


class LexicalPreflightTests(unittest.TestCase):
    def screen(self,raw_by_site):
        module=lexical()
        def observe(actor,site):
            return {'site':list(site),'raw':raw_by_site.get(tuple(site),0),
                'state':0,'semantic':4 if raw_by_site.get(tuple(site),0) else 0,
                'clock':548407,'direction':[0,0,0],'s_reg':0}
        fake_ma=SimpleNamespace(view=observe);fake_prior=SimpleNamespace(get=lambda actor:None)
        module._libraries=lambda:(None,None,None,fake_ma,fake_prior,None)
        return module.preflight(SimpleNamespace(tick=548407))

    def test_complete_current_source_preflight(self):
        row=self.screen({})
        self.assertTrue(row['admissible'])
        self.assertEqual(len(row['rows']),64)
        self.assertEqual(sum(item['requires_RAW_zero']for item in row['rows']),34)

    def test_state0_nonzero_RAW_source_is_not_free(self):
        module=lexical();source=next(p['site']for p in module.geometry()['new_ports']if p['role']=='select')
        raw=4611686018427387904
        row=self.screen({tuple(source):raw})
        self.assertFalse(row['admissible'])
        self.assertEqual(row['required_RAW_zero_conflicts'][0]['observation']['raw'],raw)

    def test_intentional_shared_H_and_old_readers_are_observed_not_cleared(self):
        module=lexical();old=next(r['site']for r in module.geometry()['common_reader']if r['form']=='suma')
        row=self.screen({module.H:17,tuple(old):23})
        self.assertTrue(row['admissible'])
        self.assertEqual(sum(r['observation']['raw']==17 for r in row['rows']),2)
        self.assertTrue(all(r['intentional_exception']for r in row['rows']if r['observation']['raw']))

    def test_preparation_and_injection_have_no_design_overlap(self):
        design=lexical().geometry()
        self.assertEqual(design['new_preparation_overlap_injection_sources'],[])
        self.assertEqual(design['new_preparation_overlap_legacy_readers'],[])
        self.assertEqual(design['new_preparation_duplicate_count'],0)


if __name__=='__main__':unittest.main()
