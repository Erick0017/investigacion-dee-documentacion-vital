"""AST whitelist of the recovery wrapper; never loads a state or Native."""
from pathlib import Path
import ast
import unittest

class Whitelist(unittest.TestCase):
    def test_only_one_native_call_and_only_feedback(self):
        p=Path(__file__).with_name('RECUPERAR_SOLO_FEEDBACK_R05.py');tree=ast.parse(p.read_text('utf8'))
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='execute' and isinstance(n.func.value,ast.Name) and n.func.value.id=='adapter']
        self.assertEqual(len(calls),1);self.assertEqual(calls[0].args[0].value,'feedback')
        for n in ast.walk(tree):
            if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute):
                self.assertNotIn(n.func.attr,('advance','run_until','submit_query','submit_scalar','set_snapshot_metadata'))
    def test_original_id_payload_guards_and_ram_limits_are_present(self):
        s=Path(__file__).with_name('RECUPERAR_SOLO_FEEDBACK_R05.py').read_text('utf8')
        for required in ('EXACT_ORIGINAL_NATIVE_CONTEXT','ORIGINAL_PAYLOAD_UNCHANGED_NOT_REPAIRED',
                         'ORIGINAL_FEEDBACK_ALREADY_QUEUED_NO_REPLAY','ORIGINAL_EPISODE_RESERVATION_AND_NO_INTENT',
                         '3758096384','1073741824','cutoff_epoch=window[',"continuous=True"):
            self.assertIn(required,s)

if __name__=='__main__':unittest.main(verbosity=2)
