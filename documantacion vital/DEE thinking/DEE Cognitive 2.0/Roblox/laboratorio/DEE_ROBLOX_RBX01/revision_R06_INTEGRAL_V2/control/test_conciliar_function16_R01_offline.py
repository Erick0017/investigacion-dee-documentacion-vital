"""Accounting-only fixtures. No Native, SQLite write, process or live ledger use."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

SOURCE = Path(__file__).with_name('conciliar_no_admitido_function16_R01.py')
spec = importlib.util.spec_from_file_location('r06_known_not_admitted', SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class AccountingOnly(unittest.TestCase):
    def setUp(self):
        self.intent = {'life': m.LIFE, 'id': m.TARGET, 'mode': 'eci01-rbx01-function', 'utc_epoch': 1.0}
        self.value = {'schema': 'fixture_only', 'consumed': 17582,
                      'worlds': {m.LIFE: {'consumed': 17582, 'reserved': 3718, 'cycles': 11, 'max_cycles': 24}},
                      'intents': {m.LIFE: copy.deepcopy(self.intent)},
                      'last_completed': {'id': m.LAST_Q2, 'after_tick': m.TICK}}
        self.proof = {'ledger_intent': copy.deepcopy(self.intent), 'critical_sha256': {'fixture': 'a' * 64}}

    def transform(self, value=None):
        return m.transform_ledger(self.value if value is None else value, self.proof, Path('fixture_proof.json'), 'b' * 64)

    def test_only_exact_intent_removed(self):
        after = self.transform()
        self.assertEqual(after['intents'], {})
        self.assertIn(m.LIFE, self.value['intents'])

    def test_counters_and_last_completed_unchanged(self):
        after = self.transform()
        for k in ('consumed', 'worlds', 'last_completed', 'schema'):
            self.assertEqual(after[k], self.value[k])

    def test_archive_retains_intent_and_evidence(self):
        after = self.transform(); row = after['rejected_before_queue'][0]
        for k, v in self.intent.items():
            self.assertEqual(row[k], v)
        self.assertEqual(row['proof_sha256'], 'b' * 64)
        self.assertFalse(row['automatic_resend'])
        self.assertEqual(row['new_native_ticks'], 0)

    def test_existing_archive_preserved(self):
        self.value['rejected_before_queue'] = [{'id': 'old_evidence'}]
        after = self.transform()
        self.assertEqual(after['rejected_before_queue'][0], {'id': 'old_evidence'})
        self.assertEqual(len(after['rejected_before_queue']), 2)

    def test_changed_id_rejected(self):
        self.value['intents'][m.LIFE]['id'] = 'another'
        with self.assertRaises(RuntimeError):
            self.transform()

    def test_missing_intent_rejected(self):
        self.value['intents'].clear()
        with self.assertRaises(RuntimeError):
            self.transform()

    def test_nonlist_archive_rejected(self):
        self.value['rejected_before_queue'] = {}
        with self.assertRaises(RuntimeError):
            self.transform()

if __name__ == '__main__':
    unittest.main()
