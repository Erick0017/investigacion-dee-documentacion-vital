"""R02 static prep/import contracts; no Native, copy preparation or owner."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
PRODUCT=ROOT.parents[2]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m);return m

class R02PreparationTests(unittest.TestCase):
    def test_original_five_frozen_sources_still_match(self):
        original=json.loads((ROOT/'protocolo/CODE_SCOPE_C02.json').read_text('utf8'))
        self.assertEqual(len(original['source_files_sha256']),5)
        for name,expected in original['source_files_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),expected,name)
    def test_new_preparation_uses_parent_and_separate_bundle_scope(self):
        module=load('C02_R02_prepare_static',ROOT/'native/preparar_descendiente_C02_R02.py')
        self.assertEqual(module.SOURCE_SNAPSHOT,'fd7372b7f2adc9040866fab8adfaca0d79e0bd18e997c0abc0651fe4fa3c23dc')
        text=(ROOT/'native/preparar_descendiente_C02_R02.py').read_text('utf8')
        self.assertIn('CODE_SCOPE_C02_R02.json',text)
        self.assertIn('RBX02_NATIVE_SCOPE_C02_R02.json',text)
        self.assertIn("source = here / 'r02_bundle' / name",text)
        self.assertIn('RBX01_C02_MAIN_R02',text)
        self.assertIn("'last_new_cycle_utc_epoch': 1794736800",text)
        capsule=PRODUCT/'reproducibilidad/codigo_preservado/PI11_HABITAT16_FAMILIA_R02'
        adapted=module.owner_extension((capsule/'app/mundo_genesis_apd05.py').read_text('utf8'))
        ast.parse(adapted)
        self.assertIn('from capacidades import rbx02_native_C02 as rbx',adapted)
    def test_new_import_default_is_stdlib_and_preserves_official_import(self):
        path=ROOT/'native/rbx02_import0_C02_R02.py';text=path.read_text('utf8');ast.parse(text)
        module=load('C02_R02_import_static',path)
        self.assertEqual(module.LIMIT,512*1024*1024)
        self.assertIn('reproducibilidad/importar_diagnostico.py',text)
        self.assertIn('rbx02_owner_support_C02_R02.py',text)
        self.assertIn('new_native_ticks',text)

if __name__=='__main__':unittest.main(verbosity=2)
