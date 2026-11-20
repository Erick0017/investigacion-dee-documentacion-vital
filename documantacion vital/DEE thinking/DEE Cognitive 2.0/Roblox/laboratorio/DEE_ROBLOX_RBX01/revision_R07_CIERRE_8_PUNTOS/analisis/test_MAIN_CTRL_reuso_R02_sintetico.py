"""Synthetic reuse test; proves MAIN phase sources are not opened/calculated."""
from pathlib import Path
import hashlib
import json
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_recalculo_cierre8_R07_offline import fixture
from RECALCULO_CIERRE8_R07_R02 import Sources,run
import RECALCULO_MAIN_CTRL_R07_R02 as wrapper

class ReuseFixture(unittest.TestCase):
    def test_only_control_is_calculated_and_MAIN_facts_are_byte_preserved(self):
        with tempfile.TemporaryDirectory()as temp:
            root=Path(temp);main_spec=fixture(root/'main',count=6,loop=True)
            main=run(main_spec,Sources(root));main_file=root/'MAIN_FACTS.json'
            raw=json.dumps(main).encode();main_file.write_bytes(raw)
            # A historical phase file is now unavailable: reuse must not open it.
            (root/'main/events.jsonl').rename(root/'main/NOT_AN_INPUT_NOW.jsonl')
            control_spec=fixture(root/'ctrl',count=6,loop=True)
            control=control_spec['arms'][0];control.update(name='SYNTHETIC_CTRL',sensor_arm='constant_tag2')
            physical={'N':67,'tick':1000571,'RAW_sha256':'0'*64,'clocks_sha256':'1'*64}
            main_proof=root/'MAIN_PROOF.json';main_proof.write_text(json.dumps({'boundary':{'native_physical':physical}}))
            ctrl_proof=root/'CTRL_PROOF.json';ctrl_proof.write_text(json.dumps({'physical_fingerprint_recorded_by_official_owner':physical}))
            spec={'schema':'DEE.R07.MAIN_CTRL.reuse.inputs.v1','reused_main_facts':str(main_file),
                'reused_main_facts_sha256':hashlib.sha256(raw).hexdigest(),'parent_world':main_spec['parent_world'],
                'main_closed_physical_proof':str(main_proof),'control_closed_physical_proof':str(ctrl_proof),'controls':[control]}
            inputs=root/'INPUTS.json';inputs.write_text(json.dumps(spec));called=[];actual=wrapper.analyze_arm
            def tracked(source,arm,parent):called.append(arm['name']);return actual(source,arm,parent)
            with patch.object(wrapper,'analyze_arm',tracked):facts,paired=wrapper.execute(inputs,root,None,root/'OUTPUT')
            self.assertEqual(called,['SYNTHETIC_CTRL']);self.assertEqual(main_file.read_bytes(),raw)
            self.assertEqual(facts['issues_total'],0);self.assertTrue(facts['physical_comparison']['equal_N_T_RAW_clocks'])
            self.assertEqual(paired['pairs'][0]['matched_completed'],6)
            self.assertFalse(facts['reused_main']['MAIN_scientific_recalculation_performed_now'])

if __name__=='__main__':unittest.main(verbosity=2)
