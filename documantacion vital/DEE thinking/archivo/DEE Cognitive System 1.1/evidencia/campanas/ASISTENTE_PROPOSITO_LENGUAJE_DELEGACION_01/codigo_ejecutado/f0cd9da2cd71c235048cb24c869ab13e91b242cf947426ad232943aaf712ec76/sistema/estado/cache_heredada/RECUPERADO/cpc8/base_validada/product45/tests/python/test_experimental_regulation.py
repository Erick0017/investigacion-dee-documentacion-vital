"""Finite experimental recipe contracts, not a new semantic classification."""
import tempfile
from pathlib import Path
import unittest
from dee_thinking.experimental_regulation import CPC5RegulationSession

def physical(s):return s.tick,s.world.runtime.raw_copy(),s.world.runtime.clock_copy()
class ExperimentalRegulationTests(unittest.TestCase):
    def test_exact_inputs_and_finite_domain(self):
        for options in ({'mode':'attention'},{'a_history':True},{'c_history':0},{'translation':(1,2.0,3)}):
            with self.assertRaises(ValueError):CPC5RegulationSession.create(**options)
        s=CPC5RegulationSession.create();before=physical(s)
        for _ in range(3):s.observe()
        self.assertEqual(before,physical(s))
        for tick in (True,-1,438):
            with self.assertRaises(ValueError):s.run_until(tick)
        pulse=[x for x in s.journal if x['channel'].startswith('native_regulator.')]
        self.assertEqual(len(pulse),2);self.assertTrue(all(x['load']==0 for x in pulse))
    def test_acquired_pulse_persistence_and_fork(self):
        s=CPC5RegulationSession.create();s.run_until(3);o=s.observe()['samples']['nominal_regulator_segment']
        self.assertTrue(o['active']);self.assertEqual(o['s_reg'],0);self.assertEqual(o['direction'],[0,0,1])
        before=physical(s)
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary)/'finite.deetsnap.gz';s.save_snapshot(path);loaded=CPC5RegulationSession.load_snapshot(path)
            self.assertEqual(physical(loaded),physical(s));self.assertEqual(loaded.journal,s.journal)
            child=s.fork();child.run_until(13);self.assertEqual(physical(s),before)
            with self.assertRaises(FileExistsError):s.save_snapshot(path)
if __name__=='__main__':unittest.main()
