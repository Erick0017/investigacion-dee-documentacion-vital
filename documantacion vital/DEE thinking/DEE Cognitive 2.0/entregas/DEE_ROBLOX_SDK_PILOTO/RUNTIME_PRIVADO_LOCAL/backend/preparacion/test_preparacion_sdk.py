"""Stdlib fixtures only: synthetic temp runtimes, never Native/import_pair.

The two private modules are loaded inertly. Every exercised filesystem path is
inside TemporaryDirectory; material import0 is always rejected before loading.
"""
from pathlib import Path
import builtins
import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
import time
import unittest
from unittest import mock

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def load_stdlib_module(filename, name):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


preparation = load_stdlib_module('preparar_instancia_par28_sdk.py', '_sdk_preparation_fixture')
importer = load_stdlib_module('importar_instancia_sdk.py', '_sdk_importer_fixture')
INSTANCE = 'SDK_DEMO_0123456789ABCDEF'
LIFE = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_' + INSTANCE
SESSION = 'SDK_SESSION_0123456789abcdef0123456789abcdef'
PUBLIC_STATE = {'permissionStock': 164, 'inventoryKey': True, 'inventoryResource': False,
                'numberAPresent': True, 'codeBPresent': False, 'numberAVersion': 5,
                'codeBCurrent': False}
FIXTURE_CODE = ('app/lives.py', 'app/native_tools.py', 'app/importacion_emparejada.py',
                'capacidades/rbx07_native_v3.py', 'capacidades/rbx07_identity_v3.py',
                'capacidades/rbx07_funciones_v3.py')


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, sort_keys=True, indent=2) + '\n').encode('utf8'))


def row(path, relative):
    payload = path.read_bytes()
    return {'file': relative, 'bytes': len(payload), 'sha256': sha_bytes(payload)}


def tree_signature(root):
    """Only small synthetic fixture files; never used on a real runtime."""
    return {p.relative_to(root).as_posix(): sha_bytes(p.read_bytes())
            for p in root.rglob('*') if p.is_file()}


class PreparationFixtures(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='sdk_preparation_fixture_')
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.runtime = self.base / 'runtime'
        self.runtime.mkdir()
        old_path = list(sys.path)
        self.addCleanup(lambda: sys.path.__setitem__(slice(None), old_path))
        self.world = {'native_tick': 991187,
                      'S': {'completedCycles': 28, 'seq': 56, 'permissionStock': 164,
                            'inventoryKey': True, 'inventoryResource': False,
                            'numberAPresent': True, 'codeBPresent': False, 'numberAVersion': 5,
                            'fixtureRetained': ['whole', 'world']},
                      'fixtureWorldMetadata': {'preserve': True}}
        card = {'life_id': preparation.SOURCE, 'snapshot_sha256': preparation.SNAPSHOT,
                'physical': {'N': 67, 'tick': 991187}, 'fixtureRetained': True}
        world_path = self.runtime / 'anclas/WORLD_PAR28.json'
        card_path = self.runtime / 'anclas/VIDA_PAR28.json'
        write_json(world_path, self.world)
        write_json(card_path, card)
        self.world_sha = sha_bytes(world_path.read_bytes())
        prefix = {'schema': 'DEE.persistent_service.paired_export.v1',
                  'life_id': preparation.SOURCE, 'backend': 'mente_unificada',
                  'profile': 'fisica_directa', 'queue_journal_required': True,
                  'new_Native_ticks': 0, 'snapshot_sha256': preparation.SNAPSHOT,
                  'physical': {'N': 67, 'tick': 991187},
                  'source_PAR28_manifest_sha256': preparation.PAIR_SHA,
                  'members': [{'file': 'VIDA.deetsnap.gz', 'bytes': 2316929,
                               'sha256': preparation.SNAPSHOT},
                              {'file': 'cola.sqlite3', 'bytes': 195915776,
                               'sha256': '0' * 64}],
                  'empty_directories_preserved': ['artefactos_trabajador/empty_fixture',
                                                  'resultados/empty_fixture']}
        prefix_index = self.runtime / preparation.PREFIX / 'EXPORTACION_SERVICIO.json'
        write_json(prefix_index, prefix)
        self.export_sha = sha_bytes(prefix_index.read_bytes())
        # No snapshot or SQLite payload exists in this synthetic prefix.
        self.addCleanup(mock.patch.stopall)
        mock.patch.object(preparation, 'WORLD_SHA', self.world_sha).start()
        mock.patch.object(preparation, 'EXPORT_SHA', self.export_sha).start()
        template_root = self.runtime / preparation.TEMPLATE
        members = []
        for name in FIXTURE_CODE:
            target = template_root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(('# inert fixture: ' + name + '\n').encode('utf8'))
            members.append(row(target, name))
        transport_name = 'capacidades/PI10_TRANSPORTE_ANCESTRAL_R01.json'
        transport = template_root / transport_name
        write_json(transport, {'life_id': preparation.SOURCE, 'role': 'ancestor',
                               'fixtureRetained': {'permission': 164}})
        members.append(row(transport, transport_name))
        registry_name = 'capacidades/PI10_PLUGINS_R01.json'
        registry = template_root / registry_name
        write_json(registry, {'files_sha256': {transport.name: sha_bytes(transport.read_bytes())},
                              'fixtureRetained': True})
        members.append(row(registry, registry_name))
        tools = []
        for filename in ('importar_diagnostico.py', 'observador_pasivo.py'):
            relative = 'backend/fixture_tools/' + filename
            target = self.runtime / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b'# inert official-tool fixture; never imported\n')
            tools.append({'file': relative, 'sha256': sha_bytes(target.read_bytes())})
        (self.runtime / 'dependencias/producto').mkdir(parents=True)
        template = {'schema': preparation.SCHEMA, 'members': members,
                    'empty_directories': ['app/empty_fixture'], 'tool_sources': tools,
                    'import_paths': ['dependencias/producto', 'backend/fixture_tools'],
                    'anchors': {'sourceWorld': {'file': 'anclas/WORLD_PAR28.json',
                                                'sha256': self.world_sha},
                                'sourceRecord': {'file': 'anclas/VIDA_PAR28.json',
                                                 'sha256': sha_bytes(card_path.read_bytes())}}}
        write_json(self.runtime / preparation.TEMPLATE_INDEX, template)
        now = int(time.time())
        limits = {'schema': preparation.SCHEMA, 'startUtcEpoch': now - 600,
                  'lastNewUtcEpoch': now + 7200, 'hardFinishUtcEpoch': now + 10800,
                  'maxNativeTicks': 40000, 'maxSdkCycles': 3,
                  'ownerMemoryBytes': 536870912, 'threads': 1, 'maxRawSupport': 10000,
                  'minimumHostFreeBytes': 3758096384, 'sealed': True}
        write_json(self.runtime / preparation.WINDOW, limits)
        configure = self.runtime / 'backend/configure_instance.py'
        configure.write_text('from pathlib import Path\nimport json\n'
                             'def create_scopes(home, cfg):\n'
                             ' p = Path(home) / "sistema/app/HOST_FIXTURE.json"\n'
                             ' p.write_text(json.dumps({"life": cfg["lifeId"]}), encoding="utf8")\n'
                             ' return {"fixtureOnly": True}\n', encoding='utf8')

    def planned(self):
        return preparation.plan(self.runtime, INSTANCE, SESSION)

    def prepared(self):
        planned = self.planned()
        result = preparation.prepare(planned, self.runtime, execute_root_only=True)
        self.assertEqual(result['status'], 'PREPARED_NOT_IMPORTED')
        return self.runtime / planned['home']

    def test_relative_paths_reject_traversal_and_windows_escape(self):
        for value in ('', '/', '/absolute', '../escape', 'a/..', 'a/./b', 'a//b',
                      'a/', 'C:/escape', 'a:b', 'a\\b'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                preparation.relative(value)
        self.assertEqual(preparation.relative('app/ordinary.py').as_posix(), 'app/ordinary.py')

    def test_sdk_namespace_rejects_research_identity_and_malformed_ids(self):
        for value in (preparation.SOURCE, '../SDK_DEMO_0123456789ABCDEF',
                      'SDK_DEMO_abcdef0123456789', 'SDK_DEMO_0123456789ABCDE',
                      'SDK_DEMO_0123456789ABCDEF0'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                preparation.plan(self.runtime, value, SESSION)
        for value in ('R07_SESSION', 'SDK_SESSION_' + 'a' * 31, 'SDK_SESSION_' + 'G' * 32):
            with self.subTest(session=value), self.assertRaises(ValueError):
                preparation.plan(self.runtime, INSTANCE, value)

    def test_plan_is_read_only_and_projects_exact_inherited_public_state(self):
        before = tree_signature(self.runtime)
        planned = self.planned()
        self.assertEqual(tree_signature(self.runtime), before)
        self.assertFalse((self.runtime / planned['home']).exists())
        self.assertEqual(planned['instance']['initialPublicState'], PUBLIC_STATE)
        self.assertEqual(planned['instance']['lifeId'], LIFE)
        self.assertNotEqual(planned['instance']['lifeId'], planned['instance']['instanceId'])
        self.assertEqual(planned['instance']['sequenceOffset'], 56)
        self.assertEqual(planned['instance']['nextPhase'], 'decision')
        self.assertEqual(planned['instance']['localSequence'], 0)
        self.assertEqual(planned['instance']['completedCycles'], 0)
        self.assertEqual(planned['instance']['nativeTick'], 991187)
        self.assertNotIn('seq', planned['instance']['initialPublicState'])
        self.assertNotIn('codeBCurrent', self.world['S'])
        self.assertEqual(planned['prefixMembers'], 2)
        self.assertTrue(planned['payloadVerificationDeferredToOfficialImportPair'])
        self.assertFalse(planned['Native_imported'])
        planned['instance']['initialPublicState']['permissionStock'] = 0
        self.assertEqual(preparation.read(self.runtime / 'anclas/WORLD_PAR28.json'), self.world)

    def test_projection_rejects_present_b_without_inventing_freshness(self):
        changed = json.loads(json.dumps(self.world))
        changed['S']['codeBPresent'] = True
        source = self.runtime / 'anclas/WORLD_PAR28.json'
        write_json(source, changed)
        changed_sha = sha_bytes(source.read_bytes())
        template_path = self.runtime / preparation.TEMPLATE_INDEX
        template = preparation.read(template_path)
        template['anchors']['sourceWorld']['sha256'] = changed_sha
        write_json(template_path, template)
        with mock.patch.object(preparation, 'WORLD_SHA', changed_sha):
            with self.assertRaisesRegex(ValueError, 'NO_PRESENT_B_WITHOUT_DECLARED_LINEAGE'):
                self.planned()

    def test_existing_empty_or_nonempty_instance_cannot_be_reused(self):
        home = self.runtime / 'estado_demo/instancias' / INSTANCE
        home.mkdir(parents=True)
        with self.assertRaises(ValueError):
            self.planned()
        (home / 'existing.txt').write_text('preserved', encoding='utf8')
        with self.assertRaises(ValueError):
            self.planned()
        self.assertEqual((home / 'existing.txt').read_text('utf8'), 'preserved')

    def test_prepare_requires_root_flag_before_mutating(self):
        planned = self.planned()
        before = tree_signature(self.runtime)
        with self.assertRaises(ValueError):
            preparation.prepare(planned, self.runtime)
        self.assertEqual(tree_signature(self.runtime), before)
        self.assertFalse((self.runtime / planned['home']).exists())

    def test_past_campaign_does_not_expire_fs_only_preparation(self):
        window_path = self.runtime / preparation.WINDOW
        limits = preparation.read(window_path)
        limits.update(startUtcEpoch=1600000000, lastNewUtcEpoch=1600003600,
                      hardFinishUtcEpoch=1600007200)
        write_json(window_path, limits)
        planned = self.planned()
        result = preparation.prepare(planned, self.runtime, execute_root_only=True)
        self.assertEqual(result['status'], 'PREPARED_NOT_IMPORTED')
        home = self.runtime / planned['home']
        self.assertTrue((home / 'PREPARACION_PAR28_SDK.json').is_file())
        self.assertFalse((home / 'IMPORTACION_DIAGNOSTICA.json').exists())
        self.assertFalse((home / 'sistema/estado/ACTIVO.json').exists())
        self.assertFalse((home / 'sistema/estado/vidas').exists())

    def test_checked_copy_streams_binary_and_rejects_existing_target(self):
        source = self.base / 'copy_source'; source.mkdir()
        target = self.base / 'copy_target'; target.mkdir()
        payload = bytes(range(256)) * 9000
        (source / 'payload.bin').write_bytes(payload)
        expected = {'bytes': len(payload), 'sha256': sha_bytes(payload)}
        preparation.copy_checked('payload.bin', 'nested/copied.bin', expected,
                                 preparation.Guard(source), preparation.Guard(target))
        self.assertEqual((target / 'nested/copied.bin').read_bytes(), payload)
        self.assertEqual(preparation.hash_file(target / 'nested/copied.bin'), expected['sha256'])
        with self.assertRaises(ValueError):
            preparation.copy_checked('payload.bin', 'nested/copied.bin', expected,
                                     preparation.Guard(source), preparation.Guard(target))
        self.assertEqual((target / 'nested/copied.bin').read_bytes(), payload)

    def test_copy_hash_failure_preserves_partial_and_blocks_reuse(self):
        planned = self.planned()
        source = self.runtime / preparation.TEMPLATE / 'app/lives.py'
        original = source.read_bytes()
        source.write_bytes(b'!' + original[1:])
        with self.assertRaisesRegex(ValueError, 'SOURCE_COPY_HASH_MISMATCH'):
            preparation.prepare(planned, self.runtime, execute_root_only=True)
        home = self.runtime / planned['home']
        self.assertTrue((home / 'PREPARACION_EN_CURSO.json').is_file())
        failure = preparation.read(home / 'PREPARACION_INCOMPLETA.json')
        self.assertTrue(failure['partial_preserved'])
        self.assertFalse(failure['automatic_retry'])
        self.assertFalse(failure['Native_imported'])
        self.assertTrue((home / 'sistema/app/lives.py').exists())
        self.assertFalse((home / 'PREPARACION_PAR28_SDK.json').exists())
        with self.assertRaises(ValueError):
            self.planned()

    def test_preparation_only_copies_code_and_anchors_and_binds_new_identity(self):
        prefix_before = tree_signature(self.runtime / preparation.PREFIX)
        home = self.prepared()
        self.assertEqual(tree_signature(self.runtime / preparation.PREFIX), prefix_before)
        self.assertFalse((home / 'PREPARACION_EN_CURSO.json').exists())
        self.assertFalse((home / 'IMPORTACION_DIAGNOSTICA.json').exists())
        self.assertFalse((home / 'sistema/estado/ACTIVO.json').exists())
        self.assertFalse((home / 'sistema/estado/vidas').exists())
        cfg = preparation.read(home / 'INSTANCE.json')
        self.assertEqual(cfg['lifeId'], LIFE)
        self.assertEqual(cfg['sessionId'], SESSION)
        self.assertEqual(cfg['initialPublicState'], PUBLIC_STATE)
        self.assertEqual(preparation.read(home / 'WORLD_PADRE_PAR28.json'), self.world)
        transport = home / 'sistema/capacidades/PI10_TRANSPORTE_ANCESTRAL_R01.json'
        value = preparation.read(transport)
        self.assertEqual(value['life_id'], LIFE)
        self.assertEqual(value['fixtureRetained'], {'permission': 164})
        registry = preparation.read(home / 'sistema/capacidades/PI10_PLUGINS_R01.json')
        self.assertEqual(registry['files_sha256'][transport.name], preparation.hash_file(transport))

    def test_context_relocates_in_memory_without_rewriting_portable_file(self):
        home = self.prepared()
        context_bytes = (home / 'CONTEXTO_EJECUCION.json').read_bytes()
        relocated = self.base / 'relocated_runtime'
        shutil.copytree(self.runtime, relocated)
        new_home = relocated / home.relative_to(self.runtime)
        resolved = preparation.resolve_context(new_home, relocated)
        self.assertEqual(resolved['life'], LIFE)
        for key in ('product', 'system', 'prefix', 'source_world', 'source_record',
                    'source_code_directory', 'template_manifest'):
            self.assertTrue(Path(resolved[key]).is_relative_to(relocated), key)
        self.assertEqual(Path(resolved['system']), new_home / 'sistema')
        self.assertEqual(resolved['import_paths'][:2], [str(new_home / 'sistema'),
                                                       str(new_home / 'sistema/app')])
        self.assertEqual((new_home / 'CONTEXTO_EJECUCION.json').read_bytes(), context_bytes)
        self.assertEqual((home / 'CONTEXTO_EJECUCION.json').read_bytes(), context_bytes)

    def test_context_cannot_redirect_operational_system(self):
        home = self.prepared()
        context = preparation.read(home / 'CONTEXTO_EJECUCION.json')
        (self.runtime / 'dependencias/redirected_system').mkdir()
        context['system'] = 'dependencias/redirected_system'
        write_json(home / 'CONTEXTO_EJECUCION.json', context)
        with self.assertRaises(ValueError):
            preparation.resolve_context(home, self.runtime)

    def test_importer_rejects_missing_root_flag_before_loading_or_importing(self):
        def no_imports(*args, **kwargs):
            raise AssertionError('An import occurred before the Root-only rejection')
        with mock.patch.object(importer, 'load', side_effect=AssertionError('loader must not run')) as loader:
            with mock.patch.object(builtins, '__import__', side_effect=no_imports):
                with self.assertRaisesRegex(ValueError, 'EXPLICIT_ROOT_ONLY_MATERIAL_IMPORT0'):
                    importer.import0(self.base / 'does_not_exist', self.base / 'not_a_runtime')
            loader.assert_not_called()
        self.assertFalse((self.base / 'does_not_exist').exists())


if __name__ == '__main__':
    unittest.main()
