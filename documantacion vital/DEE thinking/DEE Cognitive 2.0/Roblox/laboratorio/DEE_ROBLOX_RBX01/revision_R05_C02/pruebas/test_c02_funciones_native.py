"""Synthetic orchestration tests only; never imports DEE or opens a world."""
from pathlib import Path
import importlib.util
import json
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'capacidades/c02_funciones_native.py'
spec = importlib.util.spec_from_file_location('_C02_function_fixture', SOURCE)
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)
LIFE = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_FIXTURE'


class Adapter:
    def __init__(self):
        self.tick = 0
        self.calls = []
        self.signs = []
        self.numbers = []
        self.world = type('World', (), {})()
        self.world.runtime = type('Runtime', (), {})()
        self.world.runtime.dimension = 67
        self.world.runtime.snapshot_metadata_entries = [(api.SYSTEM_KEY, json.dumps({'life_id': LIFE, 'profile': 'fisica_directa'}))]


class Teacher:
    @staticmethod
    def get(a): return {}

    @staticmethod
    def teach(a, form, sign, *, mode, revision):
        a.calls.append(('teach', form, sign, mode, revision))
        a.tick = api.next_lexical_tick(a.tick) + (11 if mode == 'desync' else 0) + 3
        return {'technical_fixture': True, 'requests': []}


class Reader:
    @staticmethod
    def get(a): return {}

    @staticmethod
    def query(a, form, *, detailed):
        a.calls.append(('query', form, detailed))
        a.tick = api.next_lexical_tick(a.tick) + 7
        return {'technical_fixture': True, 'reader': {'formed_native_command': a.signs.pop(0)}, 'requests': []}


class Arithmetic:
    @staticmethod
    def execute_public(a, literal, *, actuator):
        a.calls.append(('numeric', dict(literal), actuator))
        f = api.forecast_numeric(a.tick)
        a.tick = f['end_tick']
        return {'technical_fixture': True, 'numeric_result': a.numbers.pop(0),
                'native_operation': {'native_trial': {'query_tick': f['query_tick']}}}


class Unified:
    @staticmethod
    def get(a): return {'phase_protection': {'version': 'MUFI01.sensor_calendar.R3P0', 'enabled': True}}


class Cases(unittest.TestCase):
    def setUp(self):
        self.previous = api._libraries
        api._libraries = lambda: (Teacher, Reader, Arithmetic, Unified)
        self.a = Adapter()

    def tearDown(self): api._libraries = self.previous

    def test_clock_forecasts_known_edges(self):
        self.assertEqual(api.forecast_numeric(0)['query_tick'], 56)
        self.assertEqual(api.forecast_numeric(0)['end_tick'], 198)
        self.assertEqual(api.forecast_numeric(30)['guard_paid_ticks'], 1)
        self.assertEqual(api.forecast_numeric(335)['query_tick'], 393)
        self.assertEqual(api.forecast_solve(0)['end_tick_upper'], 272)

    def test_rejects_principal_without_material_call(self):
        with self.assertRaises(ValueError): api.recall(self.a, 'luma', expected_life_id='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01')
        self.assertEqual(self.a.calls, [])

    def test_null_memory_does_not_invoke_numeric(self):
        self.a.signs = [None]
        result = api.solve(self.a, 'nara', 4, 5, expected_life_id=LIFE)
        self.assertIsNone(result['numeric_result'])
        self.assertEqual(result['status'], 'NO_LEXICAL_EMISSION')
        self.assertEqual(len(self.a.calls), 1)

    def test_native_sign_selects_operation(self):
        self.a.signs = [-1]
        self.a.numbers = [7]
        result = api.solve(self.a, 'nara', 9, 2, expected_life_id=LIFE)
        self.assertEqual(result['operation'], 'diferencia')
        self.assertEqual(result['numeric_result'], 7)
        self.assertEqual(self.a.calls[-1][1]['operacion'], 'diferencia')

    def test_actual_unexpected_intermediate_is_transported(self):
        self.a.signs = [1, -1]
        # Deliberately differs from4+5: wrapper must carry12, not calculate9.
        self.a.numbers = [12, 7]
        result = api.compose(self.a, ['luma', 'nara'], [4, 5, 2], expected_life_id=LIFE)
        self.assertEqual(result['transported_actual_intermediate'], 12)
        self.assertEqual([c[1]['izquierda'] for c in self.a.calls if c[0] == 'numeric'], [4, 12])

    def test_out_of_domain_intermediate_is_not_repaired(self):
        self.a.signs = [1]
        self.a.numbers = [64]
        result = api.compose(self.a, ['luma', 'nara'], [4, 5, 2], expected_life_id=LIFE)
        self.assertIsNone(result['second'])
        self.assertIsNone(result['numeric_result'])

    def test_deadline_rejects_before_query(self):
        with self.assertRaises(ValueError): api.solve(self.a, 'luma', 4, 5, expected_life_id=LIFE, deadline_tick=200)
        self.assertEqual(self.a.calls, [])
        self.assertEqual(self.a.tick, 0)

    def test_teacher_modes_are_explicit(self):
        result = api.lesson(self.a, 'nara', 1, expected_life_id=LIFE, teacher_mode='desync', revision=True)
        self.assertEqual(self.a.calls, [('teach', 'nara', 1, 'desync', True)])
        self.assertEqual(result['after_tick'], 81)


if __name__ == '__main__': unittest.main(verbosity=2)
