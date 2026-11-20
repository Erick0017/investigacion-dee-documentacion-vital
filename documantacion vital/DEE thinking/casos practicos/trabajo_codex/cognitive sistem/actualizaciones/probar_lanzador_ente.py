"""Pruebas stdlib del acceso EO01: sin motor, mundo, instalación ni ticks."""
from pathlib import Path
import importlib.util
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location('lanzador_ente_probado', Path(__file__).with_name('arrancar.py'))
L = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(L)


class EnteLauncherTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='dee_eo01_launcher_')
        L.ROOT = Path(self.tmp.name).resolve()
        self.calls = []
        L.call = lambda argv: self.calls.append(('call', argv)) or 0
        L.open_copy = lambda alias, life: self.calls.append(('import', alias, life))

    def tearDown(self): self.tmp.cleanup()

    def existing(self):
        file = L.ROOT / 'trabajo_personal/estado/vidas/MI_ENTE/VIDA.json'
        file.parent.mkdir(parents=True); file.write_bytes(b'personal state, no reset')
        return file

    def test_new_imports_only_selected_ente_and_does_not_send_a_calibration_or_target(self):
        L.service_ente(['MI_ENTE', '--mediciones=2:11,6:15'])
        self.assertEqual(self.calls, [('import', 'ENTE_OPERATIVO', 'MI_ENTE'),
            ('call', ['ente-servicio', '--vida', 'MI_ENTE', '--mediciones=2:11,6:15'])])

    def test_continuation_uses_existing_identity_and_no_reimport(self):
        record = self.existing()
        L.service_ente(['MI_ENTE', '--continuar', '--mediciones=3:12'])
        self.assertEqual(self.calls, [('call', ['ente-servicio', '--vida', 'MI_ENTE', '--mediciones=3:12'])])
        self.assertEqual(record.read_bytes(), b'personal state, no reset')

    def test_existing_without_continue_remains_untouched(self):
        record = self.existing()
        with self.assertRaises(ValueError): L.service_ente(['MI_ENTE', '--mediciones=3:12'])
        self.assertEqual(self.calls, [])
        self.assertEqual(record.read_bytes(), b'personal state, no reset')

    def test_missing_continue_does_not_reconstruct(self):
        with self.assertRaises(ValueError): L.service_ente(['MI_ENTE', '--continuar', '--mediciones=3:12'])
        self.assertEqual(self.calls, [])

    def test_explicit_controls_and_sensor_changes_are_only_forwarded(self):
        self.existing()
        L.service_ente(['MI_ENTE', '--continuar', '--mediciones=4:14', '--referencia-entorno', '9', '--reiniciar-entorno',
                        '--retorno', 'omit', '--actuador', 'nulled', '--fase', '2', '--detalle'])
        self.assertEqual(self.calls, [('call', ['ente-servicio', '--vida', 'MI_ENTE', '--mediciones=4:14',
            '--referencia-entorno', '9', '--reiniciar-entorno', '--retorno', 'omit', '--actuador', 'nulled', '--fase', '2', '--detalle'])])

    def test_private_B_and_social_valve_controls_are_forwarded_without_a_policy(self):
        self.existing()
        L.service_ente(['MI_ENTE', '--continuar', '--mediciones=4:14', '--privada-B', '52', '--valvula-social',
                        '--actuador-B', 'nulled', '--corte-mensaje', 'minus_bus'])
        self.assertEqual(self.calls, [('call', ['ente-servicio', '--vida', 'MI_ENTE', '--mediciones=4:14',
            '--privada-B', '52', '--valvula-social', '--actuador-B', 'nulled', '--corte-mensaje', 'minus_bus'])])


if __name__ == '__main__': unittest.main(verbosity=2)
