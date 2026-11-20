"""Pruebas de transporte EO02 en stdlib, cero motor y cero ticks."""
from pathlib import Path
import importlib.util
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location('eo02_launcher_test', Path(__file__).with_name('arrancar.py'))
L = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(L)


class EvolucionLauncherTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='dee_eo02_launcher_')
        L.ROOT = Path(self.tmp.name).resolve(); self.calls = []
        L.call = lambda argv: self.calls.append(('call', argv)) or 0
        L.open_copy = lambda alias, life: self.calls.append(('import', alias, life))

    def tearDown(self): self.tmp.cleanup()

    def existing(self):
        path = L.ROOT / 'trabajo_personal/estado/vidas/MI_EO02/VIDA.json'
        path.parent.mkdir(parents=True); path.write_bytes(b'preserve personal learning')
        return path

    def test_four_components_pass_unchanged_not_host_aggregated(self):
        raw = '[[2,14,1,3],[8,21,0,2]]'
        L.service_evolucion(['MI_EO02', '--observaciones', raw])
        self.assertEqual(self.calls, [('import', 'EVOLUCION_OPERATIVA', 'MI_EO02'),
            ('call', ['evolucion-servicio', '--vida', 'MI_EO02', '--observaciones', raw, '--dominio', 'puertas'])])

    def test_worker_task_is_an_explicit_operator_choice_and_same_life(self):
        record = self.existing(); raw = '[[3,16,2,4]]'
        L.service_evolucion(['MI_EO02', '--continuar', '--observaciones', raw, '--dominio', 'trabajadores'])
        self.assertEqual(self.calls, [('call', ['evolucion-servicio', '--vida', 'MI_EO02', '--observaciones', raw, '--dominio', 'trabajadores'])])
        self.assertEqual(record.read_bytes(), b'preserve personal learning')

    def test_missing_or_existing_identity_never_silently_recreated(self):
        with self.assertRaises(ValueError): L.service_evolucion(['MI_EO02', '--continuar', '--observaciones', '[[1,2]]'])
        self.existing()
        with self.assertRaises(ValueError): L.service_evolucion(['MI_EO02', '--observaciones', '[[1,2]]'])
        self.assertEqual(self.calls, [])

    def test_transaction_controls_are_only_forwarded(self):
        self.existing()
        L.service_evolucion(['MI_EO02', '--continuar', '--observaciones', '[[1,2]]', '--dominio', 'transaccion',
                             '--referencia-entorno', '15', '--reiniciar-entorno', '--retorno', 'omit', '--actuador', 'nulled',
                             '--fase-visible', '--fase-cero', '--detalle'])
        self.assertEqual(self.calls, [('call', ['evolucion-servicio', '--vida', 'MI_EO02', '--observaciones', '[[1,2]]',
            '--dominio', 'transaccion', '--referencia-entorno', '15', '--reiniciar-entorno', '--retorno', 'omit', '--actuador', 'nulled',
            '--fase-visible', '--fase-cero', '--detalle'])])

    def test_R10_is_explicit_another_T0_alias_and_eight_inputs_stay_separate(self):
        raw = '[[2,7,1,3,4,2,3,2]]'
        L.service_evolucion(['MI_EO02', '--sensorial', '--observaciones', raw, '--dominio', 'trabajadores'])
        self.assertEqual(self.calls, [('import', 'SENSORIAL_R10', 'MI_EO02'),
            ('call', ['evolucion-sensorial', '--vida', 'MI_EO02', '--observaciones', raw, '--dominio', 'trabajadores'])])

    def test_R10_never_silently_enters_the_R9_transaction_profile(self):
        with self.assertRaises(ValueError):
            L.service_evolucion(['MI_EO02', '--sensorial', '--observaciones', '[[1,2]]', '--dominio', 'transaccion'])
        self.assertEqual(self.calls, [])


if __name__ == '__main__': unittest.main(verbosity=2)
