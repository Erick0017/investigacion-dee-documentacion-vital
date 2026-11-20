"""Pruebas stdlib del paso directo al gestor, sin importar DEE ni emitir ticks."""
from pathlib import Path
import importlib.util
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location('lanzador_probado', Path(__file__).with_name('arrancar.py'))
L = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(L)


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='dee_cf01_launcher_')
        L.ROOT = Path(self.tmp.name).resolve()
        self.calls = []
        L.call = lambda argv: self.calls.append(('call', argv)) or 0
        L.open_copy = lambda alias, life: self.calls.append(('import', alias, life))

    def tearDown(self): self.tmp.cleanup()

    def existing(self):
        file = L.ROOT / 'trabajo_personal/estado/vidas/MI_PRUEBA/VIDA.json'
        file.parent.mkdir(parents=True); file.write_bytes(b'original personal bytes')
        return file

    def test_new_life_imports_one_closed_alias_and_forwards_measurements_unchanged(self):
        L.service_cf01(['MI_PRUEBA', '--mediciones=20:28,7:13,9:18'])
        self.assertEqual(self.calls, [('import', 'CF01_OPERATIVO', 'MI_PRUEBA'),
            ('call', ['cf01-servicio', '--vida', 'MI_PRUEBA', '--mediciones=20:28,7:13,9:18'])])

    def test_continue_never_reimports_or_rewinds(self):
        record = self.existing()
        L.service_cf01(['MI_PRUEBA', '--continuar', '--mediciones=18:25,6:14'])
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.calls[0][0], 'call')
        self.assertEqual(record.read_bytes(), b'original personal bytes')

    def test_existing_without_explicit_continue_is_preserved(self):
        record = self.existing()
        with self.assertRaises(ValueError): L.service_cf01(['MI_PRUEBA', '--mediciones=1:2'])
        self.assertEqual(self.calls, [])
        self.assertEqual(record.read_bytes(), b'original personal bytes')

    def test_missing_continue_has_no_fallback(self):
        with self.assertRaises(ValueError): L.service_cf01(['MI_PRUEBA', '--continuar', '--mediciones=1:2'])
        self.assertEqual(self.calls, [])

    def test_explicit_environment_reset_and_return_control_are_not_native_memory_updates(self):
        self.existing()
        L.service_cf01(['MI_PRUEBA', '--continuar', '--mediciones=1:2', '--referencia-entorno', '8', '--reiniciar-entorno', '--retorno', 'omit_return'])
        self.assertEqual(self.calls, [('call', ['cf01-servicio', '--vida', 'MI_PRUEBA', '--mediciones=1:2', '--referencia-entorno', '8', '--reiniciar-entorno', '--retorno', 'omit_return'])])


if __name__ == '__main__': unittest.main(verbosity=2)
