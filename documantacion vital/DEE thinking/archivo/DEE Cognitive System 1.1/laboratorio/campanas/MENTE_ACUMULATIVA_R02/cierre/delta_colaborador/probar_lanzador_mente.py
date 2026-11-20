"""Pruebas del transporte literal MENTE; stdlib, sin motor ni ticks."""
from pathlib import Path
import importlib.util, json, tempfile, unittest

SPEC = importlib.util.spec_from_file_location('ma_launcher_test', Path(__file__).with_name('arrancar.py'))
L = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(L)


class MenteLauncherTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='dee_ma_launcher_')
        L.ROOT = Path(self.tmp.name).resolve(); self.calls = []
        L.call = lambda argv: self.calls.append(('call', argv)) or 0
        L.open_copy = lambda alias, life: self.calls.append(('import', alias, life))
        L.catalog = lambda: [{'alias':'MENTE_ACUMULATIVA','source_life':'MA_MAIN_R9',
                              'snapshot_sha256':'exact_source_snapshot','profile':'fisica_directa'}]

    def tearDown(self): self.tmp.cleanup()

    def existing(self):
        p = L.ROOT / 'trabajo_personal/estado/vidas/MI_MENTE/VIDA.json'
        p.parent.mkdir(parents=True)
        p.write_text(json.dumps({'life_id':'MI_MENTE','profile':'fisica_directa',
                                'parent':{'encoded_sha256':'exact_source_snapshot','source_name':'MA_MAIN_R9.T230379.deetsnap.gz'}}), encoding='utf8')
        return p

    def test_all_situations_pass_unmodified_not_target_selected(self):
        raw = '[{"contexto":"c2","valores":[7,23],"herramienta":"trabajadores"}]'
        L.service_mente(['MI_MENTE', '--situaciones', raw])
        self.assertEqual(self.calls, [('import', 'MENTE_ACUMULATIVA', 'MI_MENTE'),
            ('call', ['mente-sesion', '--vida', 'MI_MENTE', '--situaciones', raw])])

    def test_continuation_does_not_reimport_or_edit_personal_memory(self):
        record = self.existing(); original = record.read_bytes(); raw = '[{"contexto":"c1","valores":[1,15]}]'
        L.service_mente(['MI_MENTE', '--continuar', '--situaciones', raw])
        self.assertEqual(self.calls, [('call', ['mente-sesion', '--vida', 'MI_MENTE', '--situaciones', raw])])
        self.assertEqual(record.read_bytes(), original)

    def test_control_only_forwarded_explicitly(self):
        self.existing(); raw = '[{"contexto":"c4","valores":[2,20]}]'
        L.service_mente(['MI_MENTE', '--continuar', '--situaciones', raw, '--retorno', 'omit', '--actuador', 'nulled'])
        self.assertEqual(self.calls, [('call', ['mente-sesion', '--vida', 'MI_MENTE', '--situaciones', raw,
                                             '--retorno', 'omit', '--actuador', 'nulled'])])

    def test_identity_never_silently_recreated_or_rewound(self):
        with self.assertRaises(ValueError): L.service_mente(['MI_MENTE', '--continuar', '--situaciones', '[]'])
        self.existing()
        with self.assertRaises(ValueError): L.service_mente(['MI_MENTE', '--situaciones', '[]'])
        self.assertEqual(self.calls, [])

    def test_default_existing_active_is_observed_without_input_or_reimport(self):
        record = self.existing(); original = record.read_bytes()
        active = L.ROOT / 'trabajo_personal/estado/ACTIVO.json'
        active.write_text('{"life_id":"MI_MENTE"}', encoding='utf8')
        L.service_mente([])
        self.assertEqual(self.calls, [('call', ['mente-estado', '--vida', 'MI_MENTE'])])
        self.assertEqual(record.read_bytes(), original)

    def test_out_of_domain_active_is_preserved_not_replaced(self):
        record = self.existing()
        record.write_text('{"life_id":"MI_MENTE","profile":"u0_integrado_4_5","parent":null}', encoding='utf8')
        original = record.read_bytes()
        active = L.ROOT / 'trabajo_personal/estado/ACTIVO.json'; active.write_text('{"life_id":"MI_MENTE"}', encoding='utf8')
        with self.assertRaises(ValueError): L.service_mente([])
        self.assertEqual(self.calls, [])
        self.assertEqual(record.read_bytes(), original)

    def test_first_default_import_is_explicit_complete_state_not_T0(self):
        def imported(alias, life):
            self.calls.append(('import', alias, life))
            folder = L.ROOT / 'trabajo_personal/estado/vidas' / life; folder.mkdir(parents=True)
            (folder/'VIDA.json').write_text(json.dumps({'life_id':life,'profile':'fisica_directa',
                'parent':{'encoded_sha256':'exact_source_snapshot','source_name':'MA_MAIN_R9.T230379.deetsnap.gz'}}), encoding='utf8')
            (L.ROOT/'trabajo_personal/estado/ACTIVO.json').write_text(json.dumps({'life_id':life}), encoding='utf8')
        L.open_copy = imported
        L.service_mente([])
        self.assertEqual(self.calls[0][:2], ('import', 'MENTE_ACUMULATIVA'))
        self.assertTrue(self.calls[0][2].startswith('COLAB_MENTE_'))
        self.assertEqual(self.calls[1], ('call', ['mente-estado', '--vida', self.calls[0][2]]))


if __name__ == '__main__': unittest.main(verbosity=2)
