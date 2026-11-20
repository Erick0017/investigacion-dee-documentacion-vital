"""Only synthetic six/eight histories; no actual World/model execution."""
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_recalculo_cierre8_R07_offline import fixture
from RECALCULO_CIERRE8_R07_R02 import Sources,run
from RECALCULO_MAIN_CTRL_R07 import paired_view

class PairedFixtures(unittest.TestCase):
    def test_six_vs_eight_does_not_score_two_missing_control_episodes(self):
        with tempfile.TemporaryDirectory()as temp:
            root=Path(temp);spec=fixture(root/'main',count=8,loop=True)
            control=fixture(root/'control',count=6,loop=True)['arms'][0]
            control.update(name='SYNTHETIC_CTRL',sensor_arm='constant_tag2')
            spec['arms'].append(control)
            facts=run(spec,Sources(root));view=paired_view(facts)
            self.assertEqual(facts['issues_total'],0)
            pair=view['pairs'][0]
            self.assertEqual((pair['main_completed'],pair['control_completed'],pair['matched_completed']),(8,6,6))
            self.assertEqual([r['completed_opportunities']for r in view['table']],[8,6,6,6])
            self.assertEqual(pair['matched_global_cycles'],list(range(29,35)))
            self.assertFalse(pair['main_first6_P02']['sustained_exit_criterion_met'])
    def test_without_control_is_not_a_certified_paired_comparison(self):
        with tempfile.TemporaryDirectory()as temp:
            root=Path(temp);facts=run(fixture(root/'main'),Sources(root))
            with self.assertRaisesRegex(ValueError,'closed MAIN'):paired_view(facts)

if __name__=='__main__':unittest.main(verbosity=2)
