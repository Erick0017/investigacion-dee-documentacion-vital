"""Pure R03 state selection and literal provenance; no operational data."""
from pathlib import Path
from copy import deepcopy
import hashlib
import importlib.util
import json
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
OLD = "CAPABILITIES_STATE_R06.json"
CURRENT = "CAPABILITIES_STATE_R06_R03.json"
REPAIR = "CAPABILITIES_REPAIR_ACCESS_R03/RESULTADO.json"
INSTANCE = "SDK_DEMO_0123456789ABCDEF"
SID = "SDK_SESSION_0123456789abcdef0123456789abcdef"
ERROR = {"code": "OWNER_START_OR_CLOSE_FAILED", "message": "SYNTHETIC_INSTANCE_READ_DENIED"}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf8")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class R03StateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load("_pure_export_R03_state", HERE / "exportar_capacidades_cerradas_R03.py")
        cls.base = load("_pure_export_R06_fixture",
                        HERE.parent / "exportacion_r06/test_export_capacidades_R06.py")

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="sdk_state_r03_pure_")
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name) / INSTANCE
        self.home.mkdir()
        self.old = {
            "status": "FAILED_PRESERVED", "instanceId": INSTANCE, "sessionId": SID,
            "nativeTick": 991207, "capabilitySequence": 0, "lastError": deepcopy(ERROR),
        }
        self.current = {
            "status": "CLOSED", "instanceId": INSTANCE, "sessionId": SID,
            "nativeTick": 991217, "capabilitySequence": 1, "lastError": None,
        }

    def pair(self, old=None, current=None):
        old = deepcopy(self.old if old is None else old)
        current = deepcopy(self.current if current is None else current)
        write(self.home / OLD, old)
        current.setdefault("previousFailedBoot", {
            "file": OLD, "sha256": digest(self.home / OLD), "errorPreserved": old["lastError"],
        })
        write(self.home / CURRENT, current)
        return old, current

    def select(self):
        with self.base.no_operational_imports():
            return self.module.select_capability_state(self.home)

    def test_r03_selected_exclusively_with_exact_historical_role(self):
        old, current = self.pair()
        before = {(self.home / name): (self.home / name).read_bytes() for name in (OLD, CURRENT)}
        path, state, history = self.select()
        self.assertEqual((path, state), (self.home / CURRENT, current))
        self.assertEqual(history, [{
            "path": self.home / OLD,
            "archive": "PRIMARIOS/ESTADO_HOST/HISTORICO_CAPABILITIES_STATE_R06.json",
            "role": "historical_failed_boot",
        }])
        for source, literal in before.items():
            self.assertEqual(source.read_bytes(), literal)
        self.assertEqual(old["lastError"], state["previousFailedBoot"]["errorPreserved"])

    def test_present_invalid_r03_never_falls_back_to_valid_r02(self):
        old = dict(self.old, status="CLOSED", capabilitySequence=0, lastError=None)
        write(self.home / OLD, old)
        for patch in ({"status": "FAILED_PRESERVED"}, {"status": "RUNNING"},
                      {"lastError": {"code": "FAILED"}}):
            current = dict(self.current, **patch)
            write(self.home / CURRENT, current)
            with self.subTest(patch=patch), self.assertRaisesRegex(
                    ValueError, "R03_CAPABILITIES_NOT_CLOSED_NO_FALLBACK"):
                self.select()
        (self.home / CURRENT).write_text("{invalid-json", encoding="utf8")
        with self.assertRaises(ValueError):
            self.select()

    def test_previous_failure_file_sha_and_error_must_match_exactly(self):
        _, valid = self.pair()
        for patch in ({"file": "OTHER.json"}, {"sha256": "0" * 64},
                      {"errorPreserved": {"code": "DIFFERENT"}}, {"errorPreserved": None}):
            current = deepcopy(valid)
            current["previousFailedBoot"].update(patch)
            write(self.home / CURRENT, current)
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                self.select()

    def test_historical_failure_requires_zero_events_same_identity_and_prior_tick(self):
        for patch in (
            {"status": "CLOSED"}, {"capabilitySequence": 1}, {"lastError": None},
            {"instanceId": "SDK_DEMO_FEDCBA9876543210"}, {"sessionId": "OTHER_SESSION"},
            {"nativeTick": 991218},
        ):
            old = dict(self.old, **patch)
            self.pair(old=old)
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                self.select()

    def test_optional_repair_receipt_has_exact_role_and_zero_tick_guards(self):
        self.pair()
        receipt = {
            "status": "REPAIRED_ZERO_EVENT_FS_ONLY", "newNativeTicks": 0,
            "nativeBefore": {"nativeTick": 991207, "sha256": "a" * 64},
            "nativeAfter": {"nativeTick": 991207, "sha256": "a" * 64},
            "ledgerUnchanged": True, "oldFailurePreserved": True, "accessGuardUnchanged": True,
        }
        write(self.home / REPAIR, receipt)
        _, _, history = self.select()
        self.assertEqual(history[1], {
            "path": self.home / REPAIR,
            "archive": "PRIMARIOS/ESTADO_HOST/REPARACION_R03_RESULTADO.json",
            "role": "technical_repair_receipt",
        })
        for patch in (
            {"status": "OTHER"}, {"newNativeTicks": 1}, {"nativeAfter": {"nativeTick": 991208}},
            {"ledgerUnchanged": False}, {"oldFailurePreserved": False}, {"accessGuardUnchanged": False},
        ):
            write(self.home / REPAIR, dict(receipt, **patch))
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                self.select()

    def test_no_r03_preserves_legacy_selection_and_no_state_case(self):
        legacy = dict(self.old, status="CLOSED", capabilitySequence=1, lastError=None)
        write(self.home / OLD, legacy)
        self.assertEqual(self.select(), (self.home / OLD, legacy, []))
        (self.home / OLD).unlink()
        self.assertEqual(self.select(), (self.home / OLD, None, []))

    def test_reused_fixture_exports_r02_and_r03_literals_and_recalculates(self):
        for version in ("R02", "R03"):
            with self.subTest(version=version):
                # Compose the existing fixture; do not run/inherit its eight tests.
                fixture = self.base.ClosedCapabilityExportTests(
                    "test_capabilities_export_portable_recalculation_without_original_sources")
                fixture.setUp()
                self.addCleanup(fixture.doCleanups)
                fixture.exporter = self.module
                fixture.fixture()
                old_path = fixture.home / OLD
                legacy_current = json.loads(old_path.read_text())
                legacy_current.update(instanceId=INSTANCE, sessionId=SID, lastError=None)
                write(old_path, legacy_current)
                if version == "R03":
                    current = json.loads(old_path.read_text())
                    current.update(instanceId=INSTANCE, sessionId=SID, lastError=None)
                    old = deepcopy(self.old)
                    write(old_path, old)
                    current["previousFailedBoot"] = {
                        "file": OLD, "sha256": digest(old_path), "errorPreserved": old["lastError"],
                    }
                    write(fixture.home / CURRENT, current)
                    proof = {"nativeTick": 991207, "sha256": "b" * 64}
                    write(fixture.home / REPAIR, {
                        "status": "REPAIRED_ZERO_EVENT_FS_ONLY", "newNativeTicks": 0,
                        "nativeBefore": proof, "nativeAfter": proof,
                        "ledgerUnchanged": True, "oldFailurePreserved": True, "accessGuardUnchanged": True,
                    })
                before = fixture.source_hashes()
                result = fixture.export()
                self.assertEqual(fixture.source_hashes(), before)
                self.assertEqual(result["status"], "EXPORTED_CLOSED")
                self.assertEqual(result["facts"]["newNativeTicks"], 30)
                index = json.loads((fixture.output / "INDICE_CERRADO.json").read_text())
                provenance = index["capturedHostStates"]
                expected_name = CURRENT if version == "R03" else OLD
                current_row = provenance["current"]
                self.assertEqual(current_row["role"], "current_closed_host_state")
                self.assertEqual(current_row["archive"], "PRIMARIOS/ESTADO_HOST/" + expected_name)
                self.assertEqual((fixture.output / current_row["archive"]).read_bytes(),
                                 (fixture.home / expected_name).read_bytes())
                if version == "R03":
                    roles = {row["role"]: row for row in provenance["historical"]}
                    self.assertEqual(set(roles), {"historical_failed_boot", "technical_repair_receipt"})
                    for role, relative in (("historical_failed_boot", OLD),
                                           ("technical_repair_receipt", REPAIR)):
                        row = roles[role]
                        self.assertEqual((fixture.output / row["archive"]).read_bytes(),
                                         (fixture.home / relative).read_bytes())
                        self.assertEqual(row["sha256"], digest(fixture.home / relative))
                    # All operational source paths become inaccessible before recalc.
                    fixture.runtime.rename(fixture.base / "SOURCES_INACCESSIBLE")
                    with self.base.no_operational_imports():
                        report = self.module.recalculate(fixture.output, fixture.output / "RECALCULO_R03")
                    self.assertEqual(report, result["facts"])
                else:
                    self.assertEqual(provenance["historical"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)

