"""Synthetic identity fixtures and AST preservation; never loads Native libraries."""
from pathlib import Path
import ast
import copy
import importlib.util
import json
import stat
import sys
import tempfile
import types
import unittest
from unittest import mock

sys.dont_write_bytecode = True
SOURCE = Path(__file__).with_name('sdk_native_functions_R06.py')
ORIGINAL = Path(__file__).resolve().parents[2] / 'dependencias/sdk_bundle/rbx07_funciones_v3.py'
SPEC = importlib.util.spec_from_file_location('_cap_helpers_r06_fixture', SOURCE)
helper = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = helper
SPEC.loader.exec_module(helper)
INSTANCE = 'SDK_DEMO_0123456789ABCDEF'
LIFE = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_' + INSTANCE
OTHER = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_SDK_DEMO_FEDCBA9876543210'
SESSION = 'SDK_SESSION_0123456789abcdef0123456789abcdef'
ACTOR_KEY = 'DEE.Cognitive.Roblox.SDK.native.0.1.0'


def write_json(path, value):
    path.write_text(json.dumps(value, sort_keys=True), encoding='utf8')


class HelpersFixtures(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='cap_helpers_r06_')
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name) / INSTANCE
        self.system = self.home / 'sistema'
        self.capabilities = self.system / 'capacidades'
        self.capabilities.mkdir(parents=True)
        (self.system / 'estado').mkdir()
        self.scope = self.capabilities / 'SDK_CAPABILITIES_SCOPE_R06.json'
        self.instance = self.home / 'INSTANCE.json'
        self.source_file = self.capabilities / SOURCE.name
        self.source_file.write_text('# synthetic installed code locator only\n', encoding='utf8')
        for name, value in (('SYSTEM_ROOT', self.system), ('SCOPE', self.scope),
                            ('__file__', str(self.source_file))):
            patcher = mock.patch.object(helper, name, value)
            patcher.start(); self.addCleanup(patcher.stop)
        self.reset()

    def reset(self):
        self.scope_data = {'schema': 'DEE.Roblox.SDK.capabilities.scope.R06',
                           'lifeId': LIFE, 'allowedLifeIds': [LIFE],
                           'instanceId': INSTANCE, 'sessionId': SESSION}
        self.cfg = {'runtimeVersion': '0.1.1', 'validationRevision': 'R06',
                    'lifeId': LIFE, 'instanceId': INSTANCE, 'sessionId': SESSION,
                    'localSequence': 4, 'completedCycles': 2}
        self.system_identity = {'life_id': LIFE, 'profile': 'fisica_directa',
                                'retained': {'ancestral': True}}
        self.actor = {'version': 'DEE.Roblox.SDK.native.0.1.0', 'phase': 'IDLE',
                      'pending': None, 'uncertain': False, 'session_id': SESSION,
                      'cycles': 2, 'last_sequence': 60}
        self.dimension = 67
        self.save()

    def save(self):
        write_json(self.scope, self.scope_data)
        write_json(self.instance, self.cfg)
        self.entries = {helper.SYSTEM_KEY: json.dumps(self.system_identity),
                        ACTOR_KEY: json.dumps(self.actor), 'retained_other': 'literal'}
        runtime = types.SimpleNamespace(dimension=self.dimension,
                                        snapshot_metadata_entries=list(self.entries.items()))
        self.adapter = types.SimpleNamespace(world=types.SimpleNamespace(runtime=runtime))

    def identify(self, expected=LIFE):
        self.save()
        with mock.patch.object(helper, '_libraries', side_effect=AssertionError('Native libraries forbidden')):
            return helper.identity(self.adapter, expected)

    def test_all_other_functions_and_classes_have_exact_original_ast(self):
        def definitions(path):
            tree = ast.parse(path.read_bytes())
            return {node.name: ast.dump(node, include_attributes=False)
                    for node in tree.body
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                    and node.name != 'identity'}
        self.assertEqual(definitions(SOURCE), definitions(ORIGINAL))
        self.assertEqual(helper.VERSION, 'capHelpers.R06')

    def test_original_constants_except_version_are_unchanged(self):
        def assignments(path):
            result = {}
            for node in ast.parse(path.read_bytes()).body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            result[target.id] = ast.dump(node.value, include_attributes=False)
            return result
        original = assignments(ORIGINAL); changed = assignments(SOURCE)
        for name, value in original.items():
            if name != 'VERSION':
                with self.subTest(name=name):
                    self.assertEqual(changed[name], value)

    def test_happy_identity_is_read_only_and_accepts_two_or_more_completed_cycles(self):
        for cycles in (2, 3):
            self.reset(); self.actor['cycles'] = cycles
            self.cfg.update(completedCycles=cycles, localSequence=2 * cycles)
            self.actor['last_sequence'] = 56 + 2 * cycles
            self.save()
            files_before = (self.scope.read_bytes(), self.instance.read_bytes(), self.source_file.read_bytes())
            entries_before = copy.deepcopy(self.adapter.world.runtime.snapshot_metadata_entries)
            with self.subTest(cycles=cycles):
                with mock.patch.object(helper, '_libraries', side_effect=AssertionError('No material imports')):
                    result = helper.identity(self.adapter, LIFE)
                self.assertEqual(result, self.system_identity)
                self.assertEqual(self.adapter.world.runtime.snapshot_metadata_entries, entries_before)
                self.assertEqual((self.scope.read_bytes(), self.instance.read_bytes(),
                                  self.source_file.read_bytes()), files_before)

    def test_schema_single_allowlist_and_expected_life_are_exact(self):
        for change in ('schema', 'empty', 'extra', 'other', 'not_list', 'principal', 'expected_type'):
            self.reset(); expected = LIFE
            if change == 'schema': self.scope_data['schema'] = 'old'
            elif change == 'empty': self.scope_data['allowedLifeIds'] = []
            elif change == 'extra': self.scope_data['allowedLifeIds'] = [LIFE, OTHER]
            elif change == 'other': self.scope_data['allowedLifeIds'] = [OTHER]
            elif change == 'not_list': self.scope_data['allowedLifeIds'] = LIFE
            elif change == 'principal':
                expected = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'
                self.scope_data.update(lifeId=expected, allowedLifeIds=[expected])
            else:
                class StringSubclass(str):
                    pass
                expected = StringSubclass(LIFE)
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.identify(expected)

    def test_scope_instance_relation_and_session_format_are_exact(self):
        for change in ('instance', 'lowercase_instance', 'empty_session', 'long_session', 'path_session'):
            self.reset()
            if change == 'instance': self.scope_data['instanceId'] = 'SDK_DEMO_FEDCBA9876543210'
            elif change == 'lowercase_instance': self.scope_data['instanceId'] = INSTANCE.lower()
            elif change == 'empty_session': self.scope_data['sessionId'] = ''
            elif change == 'long_session': self.scope_data['sessionId'] = 'x' * 97
            else: self.scope_data['sessionId'] = '../session'
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.identify()

    def test_home_instance_identity_runtime_revision_and_session_must_match(self):
        for key, value in (('runtimeVersion', '0.1.0'), ('validationRevision', 'R05'),
                           ('lifeId', OTHER), ('instanceId', 'SDK_DEMO_FEDCBA9876543210'),
                           ('sessionId', 'SDK_SESSION_' + 'f' * 32)):
            self.reset(); self.cfg[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'Private INSTANCE'):
                self.identify()
        # A scope-supplied locator cannot redirect the fixed HOME/INSTANCE read.
        self.reset()
        fallback = self.home.parent / 'other_home'; fallback.mkdir()
        write_json(fallback / 'INSTANCE.json', self.cfg)
        self.scope_data['home'] = str(fallback)
        self.cfg['runtimeVersion'] = '0.1.0'
        with self.assertRaisesRegex(ValueError, 'Private INSTANCE'):
            self.identify()

    def test_dimension_system_profile_and_life_are_exact(self):
        for change in ('dimension', 'float_dimension', 'system_life', 'profile'):
            self.reset()
            if change == 'dimension': self.dimension = 66
            elif change == 'float_dimension': self.dimension = 67.0
            elif change == 'system_life': self.system_identity['life_id'] = OTHER
            else: self.system_identity['profile'] = 'other'
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.identify()

    def test_actor_version_idle_pending_uncertain_cycles_and_same_session_required(self):
        cases = [('version', 'other'), ('phase', 'AWAIT_WORLD_CONSEQUENCE'),
                 ('pending', {}), ('pending', {'id': 'pending'}), ('uncertain', True),
                 ('uncertain', 0), ('cycles', 0), ('cycles', 1), ('cycles', 2.0),
                 ('cycles', '2'), ('session_id', 'SDK_SESSION_' + 'f' * 32)]
        for key, value in cases:
            self.reset(); self.actor[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                self.identify()
        self.reset(); self.actor.pop('pending')
        with self.assertRaises(ValueError): self.identify()
        for missing in (helper.SYSTEM_KEY, ACTOR_KEY):
            self.reset(); self.adapter.world.runtime.snapshot_metadata_entries = [
                (key, value) for key, value in self.entries.items() if key != missing]
            with self.subTest(missing=missing), self.assertRaises(ValueError):
                helper.identity(self.adapter, LIFE)

    def test_any_activo_path_is_rejected_even_empty_or_directory(self):
        active = self.system / 'estado/ACTIVO.json'
        for contents in ('', json.dumps({'life_id': LIFE}), json.dumps({'life_id': OTHER})):
            active.write_text(contents, encoding='utf8')
            with self.subTest(contents=contents), self.assertRaisesRegex(ValueError, 'any ACTIVO'):
                self.identify()
            active.unlink()
        active.mkdir()
        with self.assertRaisesRegex(ValueError, 'any ACTIVO'): self.identify()

    def test_scope_must_have_exact_basename_and_system_capabilities_parent(self):
        for system, scope in ((self.system, self.capabilities / 'wrong.json'),
                              (self.system, self.home / 'SDK_CAPABILITIES_SCOPE_R06.json'),
                              (self.home / 'wrong_system', self.home / 'wrong_system/capacidades/SDK_CAPABILITIES_SCOPE_R06.json')):
            with self.subTest(system=system, scope=scope):
                with mock.patch.object(helper, 'SYSTEM_ROOT', system), mock.patch.object(helper, 'SCOPE', scope):
                    with self.assertRaisesRegex(ValueError, 'private system capabilities'):
                        self.identify()

    def test_windows_reparse_scope_is_rejected_without_creating_real_links(self):
        original = Path.lstat
        def synthetic_lstat(path, *args, **kwargs):
            if path == self.scope:
                return types.SimpleNamespace(st_mode=stat.S_IFREG, st_file_attributes=1024)
            return original(path, *args, **kwargs)
        with mock.patch.object(Path, 'lstat', synthetic_lstat):
            with self.assertRaisesRegex(ValueError, 'No linked capability identity paths'):
                self.identify()


if __name__ == '__main__':
    unittest.main()
