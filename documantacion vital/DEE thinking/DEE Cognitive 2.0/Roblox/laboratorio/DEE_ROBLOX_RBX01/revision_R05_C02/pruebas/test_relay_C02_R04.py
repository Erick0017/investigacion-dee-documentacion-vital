"""Native/comparator resume cut guards only; no DB, MCP, HTTP or engine."""
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('_C02_R04_resume_test',ROOT/'control/studio_mailbox_relay_C02_R04.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
NATIVE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_MAIN_R02'
def world(life,tick,bridge_ticks=0):
    return {'native_life_id':life,'native_tick':tick,'S':{'nativeTick':tick,'lifeId':life},
            'bridge':{'native_ticks_in_session':bridge_ticks}}

class CutGuardTests(unittest.TestCase):
    def test_positive_real_native_cut_is_accepted(self):
        self.assertEqual(m.validate_resume_cut(world(NATIVE,956779,9384),'LIVE_NATIVE',9384),'LIVE_NATIVE')
    def test_zero_native_or_wrong_life_is_rejected(self):
        for value in(world(NATIVE,0),world('COMPARATOR_PROGRAMMED_RUN1',100)):
            with self.assertRaises(ValueError):m.validate_resume_cut(value,'LIVE_NATIVE',0)
    def test_both_comparator_zero_cuts_are_accepted(self):
        for participant in('PROGRAMMED','CONVENTIONAL_AI'):
            self.assertEqual(m.validate_resume_cut(world('COMPARATOR_'+participant+'_RUN1',0),participant,0),participant)
    def test_comparator_cannot_claim_native_tick_or_identity(self):
        for value in(world('COMPARATOR_PROGRAMMED_RUN1',1),world(NATIVE,0),world('COMPARATOR_CONVENTIONAL_AI_RUN1',0)):
            with self.assertRaises(ValueError):m.validate_resume_cut(value,'PROGRAMMED',0)
    def test_comparator_transport_tick_nonzero_rejected(self):
        with self.assertRaises(ValueError):m.validate_resume_cut(world('COMPARATOR_PROGRAMMED_RUN1',0,1),'PROGRAMMED',0)
        with self.assertRaises(ValueError):m.validate_resume_cut(world('COMPARATOR_PROGRAMMED_RUN1',0),'PROGRAMMED',1)
    def test_S_wire_identity_mismatch_rejected(self):
        value=world('COMPARATOR_PROGRAMMED_RUN1',0);value['S']['lifeId']='OTHER'
        with self.assertRaises(ValueError):m.validate_resume_cut(value,'PROGRAMMED',0)
    def test_explicit_resume_permission_rule_unchanged(self):
        self.assertFalse(m.explicit_resume_requested({'resumeAllowed':True},None))
        self.assertTrue(m.explicit_resume_requested({'resumeAllowed':True},Path('WORLD.json')))
    def test_resume_file_still_checks_session_mode_cursor_binding(self):
        source=(ROOT/'control/studio_mailbox_relay_C02_R04.py').read_text('utf8')
        self.assertIn("session['mode']==EXPECTED_PARTICIPANT",source)
        self.assertIn("binding['checkpoint_id']==world['checkpoint_id']",source)
        self.assertIn("pending==actions==tools==0",source)
        self.assertIn("session['phase']=='READY_QUERY'",source)

if __name__=='__main__':unittest.main(verbosity=2)
