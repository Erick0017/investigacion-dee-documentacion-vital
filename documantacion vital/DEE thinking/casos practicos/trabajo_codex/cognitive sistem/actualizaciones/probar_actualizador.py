"""Pruebas de archivos del actualizador. No importa DEE ni produce ticks."""
from pathlib import Path
import importlib.util
import json
import tempfile
import unittest
import zipfile


SPEC = importlib.util.spec_from_file_location('actualizador_probado', Path(__file__).with_name('actualizar.py'))
U = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(U)


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='dee_cf01_update_')
        self.base = Path(self.temporary.name).resolve()
        U.ROOT = self.base / 'cognitive sistem'
        U.ROOT.mkdir()
        U.OWNER = U.ROOT / 'actualizaciones/ARCHIVOS_GESTIONADOS.json'
        U.OWNER.parent.mkdir(parents=True)
        self.members = {}

    def tearDown(self):
        self.temporary.cleanup()

    def put(self, name, data, managed=True):
        path = U.ROOT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        if managed:
            self.members[name] = {'sha256': U.sha_bytes(data), 'bytes': len(data)}
        return path

    def owner(self, release='unit_test'):
        manifest = {'release': release, 'members': self.members.copy()}
        U.OWNER.write_bytes(U.encoded(manifest))
        self.put('actualizaciones/CAMBIOS.jsonl', b'{}\n', False)
        return manifest

    def test_zip_excludes_deliveries_and_can_be_repeated(self):
        self.put('LEER_PRIMERO.md', b'root')
        self.put('entregas/LEER_PRIMERO.md', b'never nested')
        self.put('trabajo_personal/LEER_PRIMERO.md', b'personal instructions')
        manifest = self.owner()
        first = U.seal_zip(manifest)
        second = U.seal_zip(manifest)
        third = U.seal_zip(manifest)
        with zipfile.ZipFile(U.ROOT / 'entregas' / third['zip']) as archive:
            self.assertFalse(any('/entregas/' in name for name in archive.namelist()))
            self.assertEqual(third['members'], len(archive.namelist()))
            self.assertEqual(None, archive.testzip())
        self.assertEqual(first['bytes'], second['bytes'])
        self.assertGreaterEqual(len(list((U.ROOT / 'entregas').glob('*.anterior.*.zip'))), 2)

    def test_rejects_changed_member_before_replacing_zip(self):
        path = self.put('LEER_PRIMERO.md', b'original')
        manifest = self.owner()
        proof = U.seal_zip(manifest)
        path.write_bytes(b'modified after closing')
        with self.assertRaises(ValueError): U.seal_zip(manifest)
        self.assertEqual(U.sha(U.ROOT / 'entregas' / proof['zip']), proof['sha256'])

    def test_build_prepares_then_commits_without_losing_new_selection(self):
        current = self.put('sistema/code.py', b'old')
        self.put('actualizaciones/SELECCION.json', b'{"old":true}\n')
        self.owner()
        source = self.base / 'source'; source.mkdir()
        build = U.Build(source)
        build.release = 'unit_build'; build.selection = {'campaign': 'CF01_TEST'}; build.seal_sha = 'a' * 64
        build.add('sistema/code.py', b'new')
        build.json('actualizaciones/SELECCION.json', {'new': True})
        self.assertEqual(current.read_bytes(), b'old')
        report = build.finish()
        self.assertEqual(current.read_bytes(), b'new')
        self.assertEqual(U.read(U.ROOT / 'actualizaciones/SELECCION.json'), {'new': True})
        self.assertEqual(report['members']['actualizaciones/SELECCION.json']['sha256'], U.sha(U.ROOT / 'actualizaciones/SELECCION.json'))
        self.assertEqual((U.ROOT / 'actualizaciones/respaldos/unit_build/sistema/code.py').read_bytes(), b'old')

    def test_conflict_leaves_operational_files_unchanged_and_saves_incoming(self):
        a = self.put('sistema/a.py', b'a old')
        b = self.put('sistema/b.py', b'b old')
        self.owner()
        b.write_bytes(b'personal version')
        source = self.base / 'source'; source.mkdir()
        build = U.Build(source); build.release = 'conflict'
        build.add('sistema/a.py', b'a new')
        with self.assertRaises(RuntimeError): build.add('sistema/b.py', b'b incoming')
        self.assertEqual(a.read_bytes(), b'a old')
        self.assertEqual(b.read_bytes(), b'personal version')
        receipts = list((U.ROOT / 'actualizaciones/conflictos').glob('*/CONFLICTO.json'))
        self.assertEqual(len(receipts), 1)
        row = U.read(receipts[0])
        self.assertEqual((U.ROOT / row['incoming_saved']).read_bytes(), b'b incoming')

    def update_archive(self, release, payloads):
        target = self.base / (release['release'] + '.zip')
        with zipfile.ZipFile(target, 'w') as archive:
            prefix = 'cognitive sistem/'
            archive.writestr(prefix + 'actualizaciones/ARCHIVOS_GESTIONADOS.json', U.encoded(release))
            for name, value in payloads.items(): archive.writestr(prefix + name, value)
        return target

    def test_receiver_keeps_personal_state_and_retires_only_intact_owned_file(self):
        self.put('sistema/code.py', b'old')
        self.put('sistema/retired.py', b'intact old')
        self.put('sistema/edited_old.py', b'old owned')
        edited = U.ROOT / 'sistema/edited_old.py'; edited.write_bytes(b'personal edit')
        personal = self.put('trabajo_personal/estado/ACTIVO.json', b'never change', False)
        self.owner()
        release = {'release': 'new', 'members': {'sistema/code.py': {'sha256': U.sha_bytes(b'new'), 'bytes': 3}},
                   'retired_members': ['sistema/retired.py', 'sistema/edited_old.py']}
        result = U.apply_update(self.update_archive(release, {'sistema/code.py': b'new'}))
        self.assertTrue(result['personal_work_untouched'])
        self.assertEqual(personal.read_bytes(), b'never change')
        self.assertEqual(edited.read_bytes(), b'personal edit')
        self.assertFalse((U.ROOT / 'sistema/retired.py').exists())
        self.assertEqual((U.ROOT / 'actualizaciones/respaldos/receptor_new/sistema/retired.py').read_bytes(), b'intact old')

    def test_receiver_preflights_conflict_before_any_operational_write(self):
        first = self.put('sistema/first.py', b'first old')
        second = self.put('sistema/second.py', b'second old')
        self.owner(); second.write_bytes(b'personal')
        payloads = {'sistema/first.py': b'first new', 'sistema/second.py': b'second new'}
        release = {'release': 'conflicted', 'members': {name: {'sha256': U.sha_bytes(value), 'bytes': len(value)} for name, value in payloads.items()}}
        with self.assertRaises(RuntimeError): U.apply_update(self.update_archive(release, payloads))
        self.assertEqual(first.read_bytes(), b'first old')
        self.assertEqual(second.read_bytes(), b'personal')

    def test_receiver_rejects_path_traversal_in_manifest(self):
        self.owner()
        release = {'release': 'unsafe', 'members': {'../escape.py': {'sha256': 'a' * 64, 'bytes': 0}}}
        with self.assertRaises(ValueError): U.apply_update(self.update_archive(release, {}))
        self.assertFalse((self.base / 'escape.py').exists())

    def test_windows_ambiguous_names_are_rejected(self):
        for name in ('', '.', 'sistema/.. /escape.py', 'sistema/code.py.', 'sistema/CON.txt'):
            with self.subTest(name=name):
                with self.assertRaises(ValueError): U.safe_name(name)

    def test_legacy_local_worker_outputs_are_redirected_to_personal_state_only(self):
        source = b"directory=s.root/'estado/servicios_locales'/args.vida"
        self.assertEqual(U.transformed('sistema/gestionar.py', source), b"directory=s.state/'servicios_locales'/args.vida")
        fixed = b"directory=s.state/'servicios_locales'/args.vida"
        self.assertEqual(U.transformed('sistema/gestionar.py', fixed), fixed)

    def test_research_omits_old_cut_without_removing_final_v2_or_failures(self):
        config = {'exclude_prefixes': ['recalculo/CORTE_01', 'recalculo/FINAL'],
                  'exclude_files': ['recalculo/INDEPENDENCIA_RECALCULO_FINAL.json']}
        self.assertFalse(U.research_member('recalculo/FINAL/duplicate.json', config))
        self.assertFalse(U.research_member('recalculo/CORTE_01/duplicate.json', config))
        self.assertFalse(U.research_member('recalculo/INDEPENDENCIA_RECALCULO_FINAL.json', config))
        self.assertTrue(U.research_member('recalculo/FINAL_V2/results.json', config))
        self.assertTrue(U.research_member('42_ERROR.json.gz', config))
        self.assertTrue(U.research_member('44_PREFLIGHT.json.gz', config))
        self.assertTrue(U.research_member('PROTOCOLO.json', {'root_files_only': True, 'include_patterns': ['*.json']}))
        self.assertFalse(U.research_member('nested/PROTOCOLO.json', {'root_files_only': True, 'include_patterns': ['*.json']}))


if __name__ == '__main__': unittest.main(verbosity=2)
