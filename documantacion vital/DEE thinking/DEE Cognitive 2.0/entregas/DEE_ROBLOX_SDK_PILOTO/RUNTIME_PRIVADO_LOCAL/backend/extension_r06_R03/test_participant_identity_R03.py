"""Pure R03 participant identities: declared content only, no INSTANCE file."""
from pathlib import Path
from contextlib import contextmanager
from types import ModuleType, SimpleNamespace
from unittest import mock
import ast
import builtins
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
NAMES = ("sdk_capabilities_R06.py", "sdk_native_functions_R06.py")
INSTANCE = "SDK_DEMO_0123456789ABCDEF"
LIFE = "ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_" + INSTANCE
SID = "SDK_SESSION_0123456789abcdef0123456789abcdef"
SYSTEM_KEY = "DEE.Cognitive.System.1.1.life.v1"
ACTOR_KEY = "DEE.Cognitive.Roblox.SDK.native.0.1.0"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextmanager
def GuardReadContent(allowed):
    """Permit only these exact files; never widen to their parent directories."""
    allowed = {Path(path).resolve() for path in allowed}
    real_builtin, real_io = builtins.open, io.open
    observed = []

    def check(file, mode):
        if "r" in mode or not any(flag in mode for flag in "wax"):
            path = Path(file).resolve()
            observed.append(path)
            if path not in allowed:
                raise PermissionError("Read content outside declared participant files: " + str(path))

    def builtin_open(file, mode="r", *args, **kwargs):
        check(file, mode)
        return real_builtin(file, mode, *args, **kwargs)

    def io_open(file, mode="r", *args, **kwargs):
        check(file, mode)
        return real_io(file, mode, *args, **kwargs)

    with mock.patch("builtins.open", side_effect=builtin_open), mock.patch("io.open", side_effect=io_open):
        yield observed


class ParticipantIdentityR03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_pins = {name: sha(HERE / name) for name in NAMES}

    @classmethod
    def tearDownClass(cls):
        for name, expected in cls.source_pins.items():
            if sha(HERE / name) != expected:
                raise AssertionError("Participant source changed during pure fixture: " + name)

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="sdk_r03_identity_pure_")
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name) / INSTANCE
        self.system = self.home / "sistema"
        self.capabilities = self.system / "capacidades"
        self.capabilities.mkdir(parents=True)
        for name in NAMES:
            (self.capabilities / name).write_bytes((HERE / name).read_bytes())
        self.scope_path = self.capabilities / "SDK_CAPABILITIES_SCOPE_R06.json"
        self.scope = {
            "schema": "DEE.Roblox.SDK.capabilities.scope.R06", "sealed": True,
            "lifeId": LIFE, "allowedLifeIds": [LIFE], "instanceId": INSTANCE, "sessionId": SID,
            "max_ticks_per_cycle": 4096, "max_total_ticks": 40000,
            "max_raw_support": 10000, "monitor_tick_block": 16,
            "ownerMemoryBytes": 536870912, "threads": 1, "maxEvents": 3,
            "startUtcEpoch": 1000, "lastNewUtcEpoch": 2000, "native_cutoff_utc_epoch": 3000,
            "participantIdentityRevision": "R03_SCOPE_NATIVE_ONLY",
            "hostProfile": {"runtimeVersion": "0.1.1", "validationRevision": "R06"},
            "sourceHashes": {name: sha(self.capabilities / name) for name in NAMES},
        }
        self.write_scope()
        self.actual = {"life_id": LIFE, "profile": "fisica_directa"}
        self.actor = {"version": "DEE.Roblox.SDK.native.0.1.0", "phase": "IDLE",
                      "pending": None, "uncertain": False, "cycles": 2, "session_id": SID}
        runtime = SimpleNamespace(dimension=67, snapshot_metadata_entries={})
        self.adapter = SimpleNamespace(world=SimpleNamespace(runtime=runtime))
        self.sync_metadata()
        package = ModuleType("capacidades")
        package.__path__ = []
        core = ModuleType("capacidades.rbx07_native_v3")
        core.identity = lambda adapter: json.loads(dict(adapter.world.runtime.snapshot_metadata_entries)[SYSTEM_KEY])
        core.get = lambda adapter: json.loads(dict(adapter.world.runtime.snapshot_metadata_entries)[ACTOR_KEY])
        package.rbx07_native_v3 = core
        self.fake_modules = mock.patch.dict(sys.modules, {
            "capacidades": package, "capacidades.rbx07_native_v3": core,
        })
        self.fake_modules.start()
        self.addCleanup(self.fake_modules.stop)
        original_import = builtins.__import__

        def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "dee_thinking" or name.startswith("dee_thinking.") or name == "sqlite3":
                raise AssertionError("DEE/SQLite import forbidden in pure fixture")
            if name.startswith("capacidades.") and name != "capacidades.rbx07_native_v3":
                raise AssertionError("Only the explicit fake core module is available")
            return original_import(name, globals, locals, fromlist, level)

        self.import_guard = mock.patch("builtins.__import__", side_effect=guarded_import)
        self.import_guard.start()
        self.addCleanup(self.import_guard.stop)
        self.plugin = load("_pure_plugin_R03", self.capabilities / NAMES[0])
        self.helper = load("_pure_helper_R03", self.capabilities / NAMES[1])
        self.allowed = [self.scope_path, *(self.capabilities / name for name in NAMES)]

    def write_scope(self):
        self.scope_path.write_text(json.dumps(self.scope, sort_keys=True), encoding="utf8")

    def sync_metadata(self):
        self.adapter.world.runtime.snapshot_metadata_entries = {
            SYSTEM_KEY: json.dumps(self.actual), ACTOR_KEY: json.dumps(self.actor),
        }

    def assert_both_reject(self):
        with GuardReadContent(self.allowed):
            for participant in (self.plugin, self.helper):
                with self.subTest(participant=participant.__name__):
                    with self.assertRaises(ValueError):
                        participant.identity(self.adapter, LIFE)

    def test_both_identities_pass_without_instance_and_read_only_declared_files(self):
        self.assertFalse((self.home / "INSTANCE.json").exists())
        with GuardReadContent(self.allowed) as observed:
            self.assertEqual(self.plugin.identity(self.adapter, LIFE), self.actual)
            self.assertEqual(self.helper.identity(self.adapter, LIFE), self.actual)
        self.assertTrue(observed)
        self.assertTrue(set(observed).issubset({p.resolve() for p in self.allowed}))
        self.assertNotIn((self.home / "INSTANCE.json").resolve(), observed)
        self.assertFalse((self.home / "INSTANCE.json").exists())

    def test_wrong_native_life_is_rejected(self):
        self.actual["life_id"] = "ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01"
        self.sync_metadata()
        self.assert_both_reject()

    def test_wrong_native_session_is_rejected(self):
        self.actor["session_id"] = "SDK_SESSION_OTHER"
        self.sync_metadata()
        self.assert_both_reject()

    def test_any_activo_file_is_rejected(self):
        active = self.system / "estado/ACTIVO.json"
        active.parent.mkdir(parents=True)
        active.write_text("{}")
        self.assert_both_reject()

    def test_wrong_scope_host_profile_or_identity_revision_is_rejected(self):
        for key, value in (
            ("hostProfile", {"runtimeVersion": "0.1.0", "validationRevision": "R06"}),
            ("hostProfile", {"runtimeVersion": "0.1.1", "validationRevision": "R05"}),
            ("participantIdentityRevision", "R02"),
        ):
            original = self.scope[key]
            self.scope[key] = value
            self.write_scope()
            with self.subTest(key=key, value=value):
                self.assert_both_reject()
            self.scope[key] = original
            self.write_scope()

    def test_content_guard_stays_exact_and_source_sha256_pins_are_enforced(self):
        for forbidden in (self.home / "INSTANCE.json", self.home / "PARENT.json"):
            with self.subTest(forbidden=forbidden.name), GuardReadContent(self.allowed):
                with self.assertRaises(PermissionError):
                    forbidden.read_text()
        source = self.capabilities / NAMES[1]
        source.write_bytes(source.read_bytes() + b"\n# synthetic tamper\n")
        with GuardReadContent(self.allowed), self.assertRaises(ValueError):
            self.plugin.identity(self.adapter, LIFE)

    def test_helper_mechanisms_ast_and_version_are_unchanged_from_r02(self):
        old_path = HERE.parent / "extension_r06" / NAMES[1]
        old = ast.parse(old_path.read_text("utf-8-sig"))
        new = ast.parse((HERE / NAMES[1]).read_text("utf-8-sig"))
        kinds = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        old_nodes = {node.name: node for node in old.body if isinstance(node, kinds) and node.name != "identity"}
        new_nodes = {node.name: node for node in new.body if isinstance(node, kinds) and node.name != "identity"}
        self.assertEqual(set(new_nodes), set(old_nodes))
        for name in old_nodes:
            with self.subTest(mechanism=name):
                self.assertEqual(ast.dump(new_nodes[name], include_attributes=False),
                                 ast.dump(old_nodes[name], include_attributes=False))
        def version(tree):
            return [ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == "VERSION" for target in node.targets)]
        self.assertEqual(version(new), version(old))
        self.assertEqual(version(new), ["capHelpers.R06"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

