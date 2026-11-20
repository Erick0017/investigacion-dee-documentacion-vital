"""Synthetic contract tests only. Never imports DEE, opens a real state or network."""
from pathlib import Path
import ast
import copy
import datetime as dt
import tempfile
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sdk_common import atomic, budget, native_payload, safe, LIFE_PREFIX, INSTANCE

def observation():
    return {'observationId': 'obs_1', 'seq': 1, 'phase': 'QUERY_CHOICE',
            'worldTimeMs': 0, 'sampleTimeMs': 0, 'previousActionId': None,
            'sensors': {'permissionStock': 164, 'stationSignal': -1},
            'protocol': 'DEE.RBX.Connector.R01', 'namespace': 'test',
            'sessionId': 'session_1', 'opportunity': 1}

class Contracts(unittest.TestCase):
    def test_connector_projection_offset_and_original_unchanged(self):
        original = {'observation': observation()}; before = copy.deepcopy(original)
        payload, sequence, oid = native_payload('decision', original, 56)
        self.assertEqual(payload['observation']['seq'], 57)
        self.assertEqual(set(payload['observation']), {'observationId','seq','phase','worldTimeMs','sampleTimeMs','previousActionId','sensors'})
        self.assertEqual(payload['observation']['sensors'], original['observation']['sensors'])
        self.assertEqual(original, before); self.assertEqual((sequence, oid), (1, 'obs_1'))

    def test_q2_permission_cost_not_added_to_native_abi(self):
        with self.assertRaises(ValueError):
            native_payload('query_sensor', {'observation': observation(), 'permissionSpent': 1}, 56)

    def test_first_lua_nil_previous_action_is_explicit_none(self):
        value = observation(); del value['previousActionId']
        actual, _, _ = native_payload('decision', {'observation': value}, 56)
        self.assertIsNone(actual['observation']['previousActionId'])
        self.assertNotIn('previousActionId', value)

    def test_feedback_projects_both_sequence_fields_only_once(self):
        value = {'seq': 2, 'observationId': 'obs_2', 'lastObservation': {**observation(), 'seq': 2}}
        actual, local, _ = native_payload('feedback', value, 56)
        self.assertEqual((actual['seq'], actual['lastObservation']['seq'], local), (58, 58, 2))
        self.assertEqual(value['seq'], 2)

    def test_no_function_or_policy_fallback(self):
        with self.assertRaises(ValueError): native_payload('function', {'tool': {}}, 56)
        with self.assertRaises(ValueError): native_payload('bad', {}, 56)

    def test_safe_path_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with self.assertRaises(ValueError): safe(root, '../outside')
            with self.assertRaises(ValueError): safe(root, 'C:/outside')
            out = safe(root, 'proof.json'); atomic(out, {'x': 1}, new=True)
            with self.assertRaises(FileExistsError): atomic(out, {'x': 2}, new=True)

    def test_finite_window_exact_utc(self):
        window = budget(now=0)
        self.assertEqual(dt.datetime.fromtimestamp(window['startUtcEpoch'], dt.timezone.utc).isoformat(), '2026-11-17T23:03:43+00:00')
        self.assertEqual(dt.datetime.fromtimestamp(window['hardFinishUtcEpoch'], dt.timezone.utc).isoformat(), '2026-11-18T05:03:43+00:00')
        with self.assertRaises(RuntimeError): budget(now=window['hardFinishUtcEpoch'])

    def test_private_namespace_preserves_ancestral_limit(self):
        iid = 'SDK_DEMO_0123456789ABCDEF'
        self.assertIsNotNone(INSTANCE.fullmatch(iid)); self.assertEqual(len(iid), 25)
        self.assertNotIn('REAL2_01', LIFE_PREFIX + iid)
        self.assertIsNone(INSTANCE.fullmatch('ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'))

    def test_all_private_sources_parse_without_execution(self):
        for p in Path(__file__).parent.glob('*.py'):
            ast.parse(p.read_text('utf-8-sig'), filename=str(p))

if __name__ == '__main__': unittest.main(verbosity=2)
