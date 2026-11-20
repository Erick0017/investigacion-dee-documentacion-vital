"""C02 technical doubles only: imports stdlib actor, never DEE or a world."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def observation(phase='QUERY_CHOICE', seq=1):
    return {'observationId': 'OBS_01', 'seq': seq, 'phase': phase,
            'worldTimeMs': 100, 'sampleTimeMs': 100, 'previousActionId': None,
            'sensors': {'station': 0, 'stage': 0, 'contact': 1,
                        'inventoryKey': False, 'inventoryResource': False,
                        'queryAvailable': True, 'stationSignal': -1,
                        'permissionStock': 48, 'publicContactCode': 5,
                        'lastFailure': False}}


def context(seq=1):
    return {'session_id': 'S_01', 'sequence': seq, 'observation_id': 'OBS_01',
            'operation_id': 'OP_01', 'mode': 'LIVE_NATIVE'}


class Adapter:
    def __init__(self):
        self.tick = 108


class Timer:
    def __init__(self, a):
        self.a = a
        self.samples = []

    def run_until(self, tick):
        if tick < self.a.tick:
            raise ValueError('No fake rewind')
        self.a.tick = tick
        self.samples.append(tick)


class FakeTools:
    def __init__(self):
        self.calls = []
        self.serial = 0

    @staticmethod
    def next_lexical_tick(tick):
        return (tick // 67 + 1) * 67

    def request(self, tick, payload):
        self.serial += 1
        return {'id': self.serial, 'port': 'TEST.SOURCE', 'payload': payload,
                'tick': tick, 'receipt': {'id': self.serial, 'status': 'applied'}}

    def lesson(self, adapter, form, sign, **kw):
        self.calls.append((form, sign, kw))
        tick = self.next_lexical_tick(adapter.tick)
        end = tick + (11 if kw['teacher_mode'] == 'desync' else 0) + 3
        adapter.run_until(end)
        return {'requests': [self.request(tick, 5), self.request(end - 3, 11)]}

    def solve(self, adapter, form, left, right, **kw):
        self.calls.append((form, left, right, kw))
        adapter.run_until(adapter.tick + 25)
        return {'recall': {'native_sign': -1}, 'operation': 'diferencia',
                'numeric_result': 12, 'status': 'FORMED',
                'requests': [self.request(adapter.tick - 10, 0)]}


class FakeApparatus:
    def __init__(self, reject=False):
        self.reject = reject

    def receipts(self, a, rows):
        return [{**r, 'receipt': {'id': r['id'], 'status':
                                  'rejected_conflict' if self.reject else 'applied'}} for r in rows]

    @staticmethod
    def summary(rows):
        applied = sum(r['receipt']['status'] == 'applied' for r in rows)
        return {'unique_requested': len(rows), 'applied': applied,
                'rejected': len(rows) - applied}


class ActorTests(unittest.TestCase):
    def setUp(self):
        self.actor = load('C02_actor_technical', ROOT / 'native/rbx02_native_C02.py')

    def test_import_does_not_import_native(self):
        self.assertNotIn('dee_thinking', sys.modules)
        text = (ROOT / 'native/rbx02_native_C02.py').read_text('utf8')
        for forbidden in ('.set_raw(', '.set_clock(', 'runtime.run(', 'Runtime('):
            self.assertNotIn(forbidden, text)

    def test_q1_scalar_codec_exhaustive_invertible(self):
        seen = {}
        for zone in range(6):
            for key in (False, True):
                for resource in (False, True):
                    for failure in (False, True):
                        sensors = dict(publicContactCode=zone, inventoryKey=key,
                                       inventoryResource=resource, lastFailure=failure)
                        value = self.actor.contact_datum(sensors)
                        self.assertNotIn(value, seen)
                        seen[value] = sensors
        self.assertEqual(len(seen), 48)
        self.assertEqual((min(seen), max(seen)), (1, 62))

    def test_function_literal_has_no_target_or_teacher_mode(self):
        row = {'modo': self.actor.FUNCTION, 'context': context(),
               'payload': {'tool': {'kind': 'CALCULATE', 'slot': 'A',
                                    'form': 'luma', 'left': 4, 'right': 5}}}
        self.actor.validate_literal(row)
        row['payload']['tool']['expected'] = 9
        with self.assertRaises(ValueError):
            self.actor.validate_literal(row)
        with self.assertRaises(ValueError):
            self.actor.validate_tool({'kind': 'LESSON', 'items': [{'form': 'luma', 'observedSign': 0}]})

    def test_new_sensor_literal_and_no_packed_target(self):
        row = {'modo': self.actor.Q1, 'context': context(), 'payload': {'observation': observation()}}
        self.actor.validate_literal(row)
        row['payload']['observation']['sensors']['target'] = 1
        with self.assertRaises(ValueError):
            self.actor.validate_literal(row)

    def test_alias_normalization_preserves_real_zero(self):
        result = [{'requests': [{'id': 8, 'port': 'P', 'payload': 0, 'tick': 12}]},
                  {'requests': [{'id': 8, 'channel': 'P', 'value': 0, 'requested_tick': 12}]}]
        rows = self.actor.normalized_requests(result)
        self.assertEqual(rows, [{'id': 8, 'channel': 'P', 'payload': 0, 'requested_tick': 12}])
        result[1]['requests'][0]['value'] = 1
        with self.assertRaises(ValueError):
            self.actor.normalized_requests(result)
        with self.assertRaises(ValueError):
            self.actor.normalized_requests({'id': 1, 'port': 'P', 'tick': 1})

    def run_function(self, folder, tool, mode='paired', deadline=500, reject=False):
        a = Adapter(); timer = Timer(a); fake = FakeTools()
        self.actor.identity = lambda a: {'life_id': 'TECHNICAL_C02_ID'}
        self.actor.scope = lambda: {'teacher_mode': mode}
        self.actor.home = lambda directory, adapter: Path(directory)
        package = types.ModuleType('capacidades'); package.c02_funciones_native = fake
        progress = {'pending': {'calendar': {'second': {'query_tick': 100,
                                                      'outcome_injection_tick': deadline}}}}
        row = {'context': context(), 'payload': {'tool': tool}}
        with patch.dict(sys.modules, {'capacidades': package}):
            result = self.actor.function(a, row, folder, progress, timer, FakeApparatus(reject))
        return a, timer, fake, progress, result

    def test_actual_calculation_result_not_expected_is_returned_and_persisted(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'pruebas') as folder:
            tool = {'kind': 'CALCULATE', 'slot': 'A', 'form': 'luma', 'left': 4, 'right': 5}
            a, timer, fake, progress, result = self.run_function(folder, tool)
            self.assertEqual(result['toolResult']['numeric_result'], 12)
            self.assertEqual(result['toolResult']['operation'], 'diferencia')
            primary = Path(folder) / result['evidence']['primary']['path']
            data = json.loads(primary.read_text('utf8'))
            self.assertEqual(data['native_function']['numeric_result'], 12)
            self.assertNotIn('native_function', progress['pending'])
            self.assertEqual(timer.samples, [133])

    def test_lesson_revision_and_control_are_fixed_by_scope(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'pruebas') as folder:
            tool = {'kind': 'LESSON', 'items': [{'form': 'luma', 'observedSign': -1},
                                               {'form': 'nara', 'observedSign': 1}]}
            a, timer, fake, progress, result = self.run_function(folder, tool, mode='desync')
            self.assertEqual(len(fake.calls), 2)
            self.assertTrue(all(call[2]['revision'] and call[2]['teacher_mode'] == 'desync' for call in fake.calls))
            self.assertIsNone(result['toolResult']['memory_value'])
            self.assertEqual(result['toolResult']['reason'], 'EXPERIENCE_ADMITTED_NOT_YET_RECALLED')

    def test_deadline_rejects_all_lessons_before_first_input(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'pruebas') as folder:
            tool = {'kind': 'LESSON', 'items': [{'form': 'luma', 'observedSign': -1},
                                               {'form': 'nara', 'observedSign': 1}]}
            with self.assertRaises(ValueError):
                self.run_function(folder, tool, deadline=150)
            self.assertEqual(list(Path(folder).iterdir()), [])

    def test_rejection_preserves_primary_and_does_not_report_success(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'pruebas') as folder:
            tool = {'kind': 'CALCULATE', 'slot': 'A', 'form': 'luma', 'left': 4, 'right': 5}
            with self.assertRaises(ValueError):
                self.run_function(folder, tool, reject=True)
            data = json.loads((Path(folder) / 'functions/OP_01.json').read_text('utf8'))
            self.assertEqual(data['Native_inputs']['rejected'], 1)

    def test_missing_left_is_no_material_environment_precondition_not_zero(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'pruebas') as folder:
            tool = {'kind': 'CALCULATE', 'slot': 'B', 'form': 'nara', 'left': None, 'right': 5}
            self.actor.validate_tool(tool)
            a, timer, fake, progress, result = self.run_function(folder, tool)
            self.assertEqual(a.tick, 108)
            self.assertEqual(timer.samples, [])
            self.assertEqual(fake.calls, [])
            self.assertFalse(result['toolResult']['capability_execution_admitted'])
            self.assertEqual(result['toolResult']['reason'], 'MISSING_OPERAND')
            self.assertIsNone(result['toolResult']['numeric_result'])
            self.assertEqual(result['evidence']['Native_inputs']['unique_requested'], 0)

    def test_adapter_function_uses_same_id_and_exposes_real_tool(self):
        adapter = load('C02_adapter_technical', ROOT / 'native/rbx02_adapter_C02.py')
        calls = []
        class Owner:
            life = 'TECHNICAL_ONLY'
            def material(self, *args, **kwargs):
                calls.append((args, kwargs))
                return {'rows': [{'version': 'DEE.RBX01.async_native.C02.R01',
                                  'toolResult': {'numeric_result': 0}, 'nativeTick': 12,
                                  'nativeTicks': 2, 'evidence': {'test': True}}]}
        out = adapter.NativeAdapter(Owner()).execute('function', {'tool': {}}, context())
        self.assertEqual(calls[0][0][0], 'OP_01')
        self.assertEqual(calls[0][0][1]['modo'], 'eci01-rbx01-function')
        self.assertEqual(out['toolResult']['numeric_result'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
