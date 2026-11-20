"""Static/preflight tests only; no capsule execution, state import or Native."""
import ast
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT.parents[2]
CAPSULE = PRODUCT / 'reproducibilidad/codigo_preservado/PI11_HABITAT16_FAMILIA_R02'


class PreparationTests(unittest.TestCase):
    def setUp(self):
        path = ROOT / 'native/preparar_descendiente_C02.py'
        spec = importlib.util.spec_from_file_location('C02_preparation_double', path)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def test_import_is_stdlib_no_native(self):
        self.assertNotIn('dee_thinking', sys.modules)
        self.assertEqual(self.module.SOURCE_SNAPSHOT,
                         'fd7372b7f2adc9040866fab8adfaca0d79e0bd18e997c0abc0651fe4fa3c23dc')

    def test_exact_frozen_owner_patch_parses_and_has_new_direct_imports(self):
        path = CAPSULE / 'app/mundo_genesis_apd05.py'
        original = path.read_text('utf-8-sig')
        adapted = self.module.owner_extension(original)
        ast.parse(adapted)
        self.assertIn('rbx02_identity_C02 as pi11_identity', adapted)
        self.assertIn('from capacidades import rbx02_native_C02 as rbx', adapted)
        self.assertNotIn('rbx01_native_R01', adapted)
        self.assertIn("self.before_mutation('RBX01_EXPLICIT_ASYNC_NATIVE_PHASE')", adapted)
        self.assertEqual(path.read_text('utf-8-sig'), original)

    def test_function_dependencies_all_in_frozen_capsule(self):
        manifest = self.module.read(CAPSULE / 'SISTEMA_CODIGO.json')
        names = {row['file'] for row in manifest['files']}
        self.assertTrue(all('capacidades/' + name in names for name in self.module.FUNCTION_FILES))

    def test_unsafe_manifest_paths_rejected(self):
        for name in ('../bad', '/absolute', 'C:/x', 'a\\b'):
            with self.assertRaises(ValueError):
                self.module.member(CAPSULE, name)


if __name__ == '__main__':
    unittest.main(verbosity=2)
