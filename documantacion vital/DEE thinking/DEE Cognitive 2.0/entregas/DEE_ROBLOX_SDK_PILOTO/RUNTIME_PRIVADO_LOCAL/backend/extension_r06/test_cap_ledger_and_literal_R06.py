"""Pure temporary-ledger, literal and copied-mechanism checks for CAPEVENT R06.

Run with a stdlib interpreter: python -I -S -B <absolute path to this file>.
No Native, DEE, SQLite, owner or operational-state module may be imported.
"""
from pathlib import Path
from contextlib import contextmanager
from copy import deepcopy
from types import ModuleType
from unittest import mock
import ast
import builtins
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
RUNTIME = HERE.parents[1]
PREFIX = "ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_"
INSTANCE = "SDK_DEMO_0123456789ABCDEF"
LIFE = PREFIX + INSTANCE
OTHER_LIFE = PREFIX + "SDK_DEMO_FEDCBA9876543210"
MODE = "eci01-pi10-sdk-capability-r06"
FORBIDDEN = ("dee_thinking", "capacidades", "sqlite3")


@contextmanager
def no_native_imports():
    original = builtins.__import__
    seen = []

    def guarded(name, globals=None, locals=None, fromlist=(), level=0):
        seen.append(name)
        if any(name == item or name.startswith(item + ".") for item in FORBIDDEN):
            raise AssertionError("Operational import forbidden in pure fixture: " + name)
        return original(name, globals, locals, fromlist, level)

    with mock.patch("builtins.__import__", side_effect=guarded):
        yield seen


def load_source(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf8")


class CapabilityLedgerAndLiteralTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fake_common = ModuleType("sdk_common")
        fake_common.atomic = write_json
        old_path = list(sys.path)
        try:
            with mock.patch.dict(sys.modules, {"sdk_common": fake_common}), no_native_imports() as seen:
                cls.cap = load_source("_pure_caps_ledger_R06", HERE / "ledger_caps_R06.py")
                cls.plugin = load_source("_pure_caps_literal_R06", HERE / "sdk_capabilities_R06.py")
            cls.imports_seen = tuple(seen)
        finally:
            sys.path[:] = old_path

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="sdk_cap_ledger_pure_")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "RUNTIME_PRIVADO_LOCAL"
        self.ledger_path = self.root / "estado_demo/LEDGER_SDK_R06.json"
        self.scope_path = (self.root / "estado_demo/instancias" / INSTANCE /
                           "sistema/capacidades/SDK_CAPABILITIES_SCOPE_R06.json")
        self.scope = {
            "schema": "DEE.Roblox.SDK.capabilities.scope.R06",
            "lifeId": LIFE, "allowedLifeIds": [LIFE], "sealed": True,
            "maxEvents": 1, "lastNewUtcEpoch": 2000,
        }
        self.value = {
            "schema": self.cap._base.SCHEMA,
            "limit": 40000, "max_worlds": 6, "sdk_global_cycles": 3,
            "consumed": 3128, "validation_consumed": 3128,
            "worlds": {LIFE: {
                "consumed": 3128, "validation_consumed": 3128,
                "cycles": 2, "validation_cycles": 2, "reserved": 0,
                "role": "pilot", "max_cycles": 3,
            }},
            "intents": {}, "leases": {}, "lease_history": [],
            "source_tick_per_new_life": 991187, "physical_history_not_reset": True,
        }
        write_json(self.root / "configuracion/VENTANA_R06.json",
                   {"lastNewUtcEpoch": 2000, "hardFinishUtcEpoch": 3000})
        write_json(self.scope_path, self.scope)
        write_json(self.ledger_path, self.value)
        self.roots = mock.patch.multiple(self.cap, ROOT=self.root)
        self.roots.start()
        self.addCleanup(self.roots.stop)
        self.base_root = mock.patch.object(self.cap._base, "ROOT", self.root)
        self.base_root.start()
        self.addCleanup(self.base_root.stop)
        self.clock = mock.patch.object(self.cap.time, "time", return_value=1000.0)
        self.clock.start()
        self.addCleanup(self.clock.stop)
        self.ledger = self.cap.TickLedger(self.ledger_path, LIFE, 3, role="pilot")

    def snapshot(self):
        data = self.ledger_path.read_bytes()
        return data, hashlib.sha256(data).hexdigest()

    def assert_rejected_without_ledger_change(self, action):
        before = self.snapshot()
        with self.assertRaises((RuntimeError, ValueError)):
            action()
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(self.ledger_path.with_name(self.ledger_path.name + ".LOCK").exists())

    def test_capability_200_ticks_preserves_two_completed_core_cycles(self):
        self.ledger.begin(LIFE, "CAP_TEST_01", MODE)
        admitted = self.ledger.read()
        self.assertEqual(admitted["worlds"][LIFE]["reserved"], 4096)
        self.assertEqual(admitted["consumed"], 3128)
        self.assertEqual(admitted["worlds"][LIFE]["cycles"], 2)
        self.assertTrue(admitted["intents"][LIFE]["capability_event"])
        self.assertTrue(admitted["intents"][LIFE]["not_new_sdk_cycle"])
        self.ledger.finish(LIFE, "CAP_TEST_01", 991187, 991387, MODE)
        closed = self.ledger.read()
        world = closed["worlds"][LIFE]
        self.assertEqual((closed["consumed"], closed["validation_consumed"]), (3328, 3328))
        self.assertEqual((world["consumed"], world["validation_consumed"]), (3328, 3328))
        self.assertEqual((world["cycles"], world["validation_cycles"]), (2, 2))
        self.assertEqual((world["reserved"], world["capability_events"]), (0, 1))
        self.assertEqual(closed["intents"], {})
        self.assertEqual(world["last_completed"]["actual_ticks"], 200)
        self.assertEqual(closed["last_completed"], world["last_completed"])

    def test_global_40000_budget_includes_other_life_consumption_and_reservations(self):
        for consumed, reserved in ((32800, 0), (32000, 1024)):
            with self.subTest(other_consumed=consumed, other_reserved=reserved):
                value = deepcopy(self.value)
                value["worlds"][OTHER_LIFE] = {
                    "consumed": consumed, "validation_consumed": consumed,
                    "cycles": 0, "validation_cycles": 0, "reserved": reserved,
                    "role": "control", "max_cycles": 6,
                }
                value["consumed"] += consumed
                value["validation_consumed"] += consumed
                write_json(self.ledger_path, value)
                self.assert_rejected_without_ledger_change(
                    lambda: self.ledger.begin(LIFE, "CAP_OVER_GLOBAL", MODE))

    def test_prior_intent_is_preserved(self):
        value = deepcopy(self.value)
        value["intents"][OTHER_LIFE] = {
            "life": OTHER_LIFE, "id": "PRIOR", "mode": MODE, "utc_epoch": 900,
        }
        write_json(self.ledger_path, value)
        self.assert_rejected_without_ledger_change(
            lambda: self.ledger.begin(LIFE, "CAP_WITH_PRIOR", MODE))

    def test_max_events_existing_reservation_and_incomplete_core_are_preserved(self):
        for patch in ({"capability_events": 1}, {"reserved": 1}, {"cycles": 1}):
            with self.subTest(world_patch=patch):
                value = deepcopy(self.value)
                value["worlds"][LIFE].update(patch)
                write_json(self.ledger_path, value)
                self.assert_rejected_without_ledger_change(
                    lambda: self.ledger.begin(LIFE, "CAP_BLOCKED", MODE))

    def test_failed_settlement_keeps_exact_original_intent(self):
        self.ledger.begin(LIFE, "CAP_SETTLE", MODE)
        for identifier, after in (("WRONG_ID", 991387), ("CAP_SETTLE", 995284),
                                  ("CAP_SETTLE", 991186)):
            with self.subTest(identifier=identifier, after=after):
                self.assert_rejected_without_ledger_change(
                    lambda: self.ledger.finish(LIFE, identifier, 991187, after, MODE))

    def test_six_advertised_literal_contracts_need_no_native_imports(self):
        requests = (
            {"kind": "RECALL", "form": "luma"},
            {"kind": "LESSON", "form": "nara", "observedSign": -1,
             "revision": True, "teacherMode": "paired"},
            {"kind": "NUMERIC", "operation": "suma", "left": 0, "right": 32},
            {"kind": "SOLVE", "form": "luma", "left": 32, "right": 0},
            {"kind": "COMPOSE", "forms": ["luma", "nara"], "data": [0, 32, 1]},
            {"kind": "COMPARE", "left": 20, "right": 0},
        )
        with no_native_imports():
            for request in requests:
                with self.subTest(kind=request["kind"]):
                    before = deepcopy(request)
                    self.assertIs(self.plugin.validate_request(request), request)
                    self.assertEqual(request, before)

    def test_literal_rejects_expected_target_extra_domains_null_and_bool(self):
        requests = [
            {"kind": "RECALL", "form": "luma", "expected": 1},
            {"kind": "NUMERIC", "operation": "suma", "left": 1, "right": 2, "target": 3},
            {"kind": "SOLVE", "form": "luma", "left": 1, "right": 2, "extra": False},
            {"kind": "NUMERIC", "operation": "suma", "left": 33, "right": 0},
            {"kind": "SOLVE", "form": "luma", "left": -1, "right": 0},
            {"kind": "COMPARE", "left": 21, "right": 0},
            {"kind": "COMPARE", "left": 0, "right": 21},
            {"kind": "NUMERIC", "operation": "suma", "left": None, "right": 0},
            {"kind": "NUMERIC", "operation": "suma", "left": True, "right": 0},
            {"kind": "SOLVE", "form": "luma", "left": 1, "right": False},
            {"kind": "COMPARE", "left": None, "right": 0},
            {"kind": "COMPARE", "left": False, "right": 0},
            {"kind": "COMPOSE", "forms": ["luma", "nara"], "data": [1, None, 2]},
            {"kind": "COMPOSE", "forms": ["luma", "nara"], "data": [1, True, 2]},
            {"kind": "COMPOSE", "forms": ["luma", "nara"], "data": [1, 33, 2]},
            {"kind": "LESSON", "form": "luma", "observedSign": True,
             "revision": True, "teacherMode": "paired"},
        ]
        with no_native_imports():
            for request in requests:
                with self.subTest(request=request):
                    before = deepcopy(request)
                    with self.assertRaises(ValueError):
                        self.plugin.validate_request(request)
                    self.assertEqual(request, before)

    def test_copied_safety_and_receipt_mechanisms_are_ast_identical(self):
        source = ast.parse((RUNTIME / "dependencias/sdk_bundle/rbx07_native_v3.py").read_text("utf-8-sig"))
        copied = ast.parse((HERE / "sdk_capabilities_R06.py").read_text("utf-8-sig"))
        for name in ("BoundedTime", "TimedAdapter", "normalized_requests"):
            with self.subTest(mechanism=name):
                old = [node for node in source.body if isinstance(node, (ast.ClassDef, ast.FunctionDef))
                       and node.name == name]
                new = [node for node in copied.body if isinstance(node, (ast.ClassDef, ast.FunctionDef))
                       and node.name == name]
                self.assertEqual((len(old), len(new)), (1, 1))
                self.assertEqual(ast.dump(new[0], include_attributes=False),
                                 ast.dump(old[0], include_attributes=False))

    def test_source_modules_loaded_without_operational_imports(self):
        for name in self.imports_seen:
            self.assertFalse(any(name == item or name.startswith(item + ".") for item in FORBIDDEN), name)


if __name__ == "__main__":
    unittest.main(verbosity=2)

