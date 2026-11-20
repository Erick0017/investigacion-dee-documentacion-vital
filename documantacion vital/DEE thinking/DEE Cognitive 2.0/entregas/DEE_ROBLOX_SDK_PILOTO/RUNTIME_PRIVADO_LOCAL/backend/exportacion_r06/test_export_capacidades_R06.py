"""Pure closed-export and portable-recalculation fixtures; no operational state."""
from pathlib import Path
from contextlib import contextmanager
from copy import deepcopy
from unittest import mock
import builtins
import hashlib
import importlib.util
import json
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
INSTANCE = "SDK_DEMO_0123456789ABCDEF"
LIFE = "ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_" + INSTANCE
SID = "SDK_SESSION_0123456789abcdef0123456789abcdef"
START = 991187
SECRET = "PRIVATE_FIXTURE_TOKEN_DO_NOT_EXPORT_0123456789"
FORBIDDEN = ("dee_thinking", "capacidades", "sqlite3")


@contextmanager
def no_operational_imports():
    original = builtins.__import__

    def guarded(name, globals=None, locals=None, fromlist=(), level=0):
        if any(name == x or name.startswith(x + ".") for x in FORBIDDEN):
            raise AssertionError("Operational import forbidden: " + name)
        return original(name, globals, locals, fromlist, level)

    with mock.patch("builtins.__import__", side_effect=guarded):
        yield


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    with no_operational_imports():
        spec.loader.exec_module(module)
    return module


def data(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data(value))


def write_lines(path, values):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"".join(data(value) for value in values))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class ClosedCapabilityExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exporter = load(HERE / "exportar_capacidades_cerradas_R06.py", "_pure_closed_export_R06")

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="sdk_closed_export_pure_")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.runtime = self.base / "RUNTIME_PRIVADO_LOCAL"
        self.home = self.runtime / "estado_demo/instancias" / INSTANCE
        self.output = self.base / "PACKAGE"
        self.worker = self.home / "sistema/estado/servicios_locales" / LIFE
        self.card = self.home / "sistema/estado/vidas" / LIFE / "VIDA.json"
        self.ledger = self.runtime / "estado_demo/LEDGER_SDK_R06.json"
        self.operation = self.home / "capability_operations/CAP_TEST_01.json"
        self.primary = self.worker / "DEE_SDK_ASSISTED_CAPABILITIES_R06/CAP_TEST_01.json"

    def fixture(self, capability=True):
        tick = START + (30 if capability else 20)
        write(self.home / "INSTANCE.json", {
            "instanceId": INSTANCE, "lifeId": LIFE, "sessionId": SID,
            "nativeTick": tick, "completedCycles": 1, "localSequence": 2, "sequenceOffset": 56,
        })
        card = {"life_id": LIFE, "physical": {"N": 67, "tick": tick,
                "RAW_sha256": "a" * 64, "clocks_sha256": "b" * 64},
                "snapshot_sha256": "c" * 64}
        write(self.card, card)
        descriptor = {"nativeTick": tick, "dimension": 67, "lifeId": LIFE,
                      "cardSha256": sha(self.card), "snapshotSha256": "c" * 64,
                      "databaseSha256": "d" * 64, "writerClosed": True, "pending": 0}
        old_card = deepcopy(card)
        old_card["physical"]["tick"] = START + 20
        pair_native = dict(descriptor, nativeTick=START + 20,
                           cardSha256=hashlib.sha256(data(old_card)).hexdigest())
        snapshot = {"state": {"completedOpportunities": 1, "sequence": 2,
                    "nativeTick": START + 20, "sessionId": SID, "lifeId": LIFE, "phase": "BOUNDARY"}}
        write(self.home / "SDK_PAIR.json", {
            "snapshotSha256": hashlib.sha256(data(snapshot)).hexdigest(),
            "native": pair_native, "backendProof": dict(pair_native, backendWriterClosed=True,
                bridgeQuiescent=True, sessionId=SID, localSequence=2), "snapshot": snapshot,
        })
        core = []
        before = START
        for identifier, mode, ticks in (
            ("CORE_Q1", "eci01-rbx01-decision", 5),
            ("CORE_Q2", "eci01-rbx01-query-sensor", 2),
            ("CORE_FB", "eci01-rbx01-feedback", 13),
        ):
            core.append({"kind": "PHASE_INTENT", "mode": mode, "tick": before,
                         "context": {"operation_id": identifier, "session_id": SID}})
            before += ticks
            core.append({"kind": "PHASE_COMPLETED", "mode": mode, "tick": before,
                         "result": {"nativeTick": before, "nativeTicks": ticks,
                                    "accepted": True, "action": None}})
        write_lines(self.worker / "DEE_SDK_NATIVE_0_1_0/events.jsonl", core)
        write_lines(self.home / "ENSAYOS.jsonl", [
            {"kind": "OWNER_STARTED", "runid": "FAKE_OWNER"},
            {"kind": "OWNER_CLOSED", "runid": "FAKE_OWNER", "exit_code": 0,
             "final_status": {"running": False, "tick": tick}},
        ])
        world = {"consumed": tick - START, "cycles": 1, "reserved": 0,
                 "capability_events": int(capability)}
        write(self.ledger, {"worlds": {LIFE: world}, "intents": {}})
        write(self.runtime / "configuracion/CONEXION_PRIVADA.json", {"token": SECRET})
        # Synthetic forbidden payloads prove selection excludes snapshots and DBs.
        write(self.home / "sistema/estado/snapshots/NEVER_EXPORT.snapshot", {"secret": SECRET})
        database = self.home / "sistema/estado/servicios_persistentes" / LIFE / "cola.sqlite3"
        database.parent.mkdir(parents=True, exist_ok=True)
        database.write_bytes(b"SYNTHETIC_DB_MUST_NOT_BE_OPENED_OR_COPIED")
        if capability:
            receipt = {"id": 701, "channel": "FAKE.CUE", "payload": 1,
                       "requested_tick": START + 21,
                       "receipt": {"id": 701, "status": "applied", "effective_tick": START + 21}}
            primary = {"lifeId": LIFE, "sessionId": SID,
                       "context": {"operation_id": "CAP_TEST_01", "capability_sequence": 1},
                       "before_tick": START + 20, "after_tick": tick,
                       "request": {"kind": "NUMERIC", "operation": "suma", "left": 2, "right": 3},
                       "nativeValue": {"numeric_result": None, "status": "NULL", "operation": "suma"},
                       "requests_normalized": [receipt, deepcopy(receipt)],
                       "Native_inputs": {"unique_requested": 1, "applied": 1,
                                         "rejected": 0, "pending_or_other": 0}}
            write(self.primary, primary)
            write(self.operation, {
                "operationId": "CAP_TEST_01", "kind": "CAPABILITY", "status": "COMPLETED",
                "capabilitySequence": 1,
                "value": {"nativeTick": tick, "nativeTicks": 10, "capabilitySequence": 1,
                          "primary": {"path": self.primary.relative_to(self.worker).as_posix(),
                                      "sha256": sha(self.primary), "bytes": self.primary.stat().st_size}},
            })
            write(self.home / "CAPABILITIES_STATE_R06.json", {
                "status": "CLOSED", "nativeTick": tick, "capabilitySequence": 1,
                "closedNativeDescriptor": descriptor,
            })

    def source_hashes(self):
        return {p.relative_to(self.runtime).as_posix(): sha(p)
                for p in self.runtime.rglob("*") if p.is_file()}

    def export(self, **kwargs):
        with no_operational_imports():
            return self.exporter.export(self.home, self.output, self.runtime, **kwargs)

    def reject(self):
        before = self.source_hashes()
        with self.assertRaises(ValueError):
            self.export()
        self.assertEqual(self.source_hashes(), before)
        self.assertFalse(self.output.exists())

    def test_capabilities_export_portable_recalculation_without_original_sources(self):
        self.fixture()
        before = self.source_hashes()
        result = self.export()
        self.assertEqual(result["status"], "EXPORTED_CLOSED")
        self.assertFalse(result["NativeExecuted"])
        self.assertEqual(self.source_hashes(), before)
        report = result["facts"]
        self.assertEqual((report["newNativeTicks"], report["finalNativeTick"]), (30, START + 30))
        self.assertEqual((report["coreCompletedCycles"], len(report["capabilityEvents"])), (1, 1))
        event = report["capabilityEvents"][0]
        self.assertIsNone(event["actualNativeContent"]["numeric_result"])
        self.assertEqual(event["actualNativeContent"]["status"], "NULL")
        self.assertEqual(event["Native_inputs"]["unique_requested"], 1)
        manifest = json.loads((self.output / "MANIFIESTO.json").read_text())
        self.assertFalse(manifest["NativeSnapshotsOrDBIncluded"])
        for member in manifest["files"]:
            file = self.output / member["archive"]
            self.assertEqual((file.stat().st_size, sha(file)), (member["bytes"], member["sha256"]))
            self.assertNotIn(SECRET.encode(), file.read_bytes())
            self.assertNotIn(".sqlite", member["archive"])
            self.assertNotIn(".snapshot", member["archive"])
        self.assertFalse((self.output / "SDK_PAIR.json").exists())
        hidden = self.base / "ORIGINAL_SOURCES_INACCESSIBLE"
        self.assertTrue(self.runtime.resolve().is_relative_to(self.base.resolve()))
        self.runtime.rename(hidden)
        portable = load(self.output / "RECALCULAR_CAPACIDADES_R06.py", "_portable_recalculation_fixture")
        original_raw = portable.raw

        def extraction_only(path):
            self.assertTrue(Path(path).resolve().is_relative_to(self.output.resolve()))
            return original_raw(path)

        with mock.patch.object(portable, "raw", side_effect=extraction_only), no_operational_imports():
            recalculated = portable.recalculate(self.output, self.output / "RECALCULO_NUEVO")
        self.assertEqual(recalculated, report)

    def test_core_only_closed_export_has_no_fabricated_capabilities(self):
        self.fixture(capability=False)
        result = self.export()
        self.assertEqual(result["facts"]["newNativeTicks"], 20)
        self.assertEqual(result["facts"]["capabilityEvents"], [])
        self.assertEqual(result["facts"]["coreCompletedCycles"], 1)
        index = json.loads((self.output / "INDICE_CERRADO.json").read_text())
        self.assertTrue(index["closure"]["WorldPairCurrentAfterCapabilities"])

    def test_locks_and_unclosed_owner_are_rejected(self):
        self.fixture()
        for name in ("SDK_SERVICE.lock", "SDK_CAPABILITIES_SERVICE.lock",
                     "sistema/estado/locks/" + LIFE + ".lock",
                     "sistema/estado/vidas/" + LIFE + "/FUTURO_INTERRUMPIDO.json"):
            with self.subTest(lock=name):
                path = self.home / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"fake-lock")
                self.reject()
                path.unlink()
        journal = self.home / "ENSAYOS.jsonl"
        original = journal.read_bytes()
        for closing in (
            {"kind": "OWNER_CLOSED", "exit_code": 1, "final_status": {"running": False}},
            {"kind": "OWNER_CLOSED", "exit_code": 0, "final_status": {"running": True}},
            {"kind": "OWNER_STARTED"},
        ):
            with self.subTest(closing=closing):
                write_lines(journal, [closing])
                self.reject()
        journal.write_bytes(original)

    def test_ledger_intent_and_reservation_are_rejected(self):
        self.fixture()
        original = json.loads(self.ledger.read_text())
        for change in ("intent", "reserved"):
            value = deepcopy(original)
            if change == "intent":
                value["intents"] = {LIFE: {"id": "UNFINISHED"}}
            else:
                value["worlds"][LIFE]["reserved"] = 4096
            write(self.ledger, value)
            with self.subTest(change=change):
                self.reject()

    def test_pending_uncertain_and_unknown_operations_are_rejected(self):
        self.fixture()
        original = json.loads(self.operation.read_text())
        for status in ("PENDING", "RUNNING", "UNCERTAIN", "UNKNOWN"):
            write(self.operation, dict(original, status=status))
            with self.subTest(status=status):
                self.reject()

    def test_primary_locator_hash_mismatch_is_rejected(self):
        self.fixture()
        self.primary.write_bytes(self.primary.read_bytes() + b"\n")
        self.reject()

    def test_secret_field_is_rejected_even_with_updated_locator(self):
        self.fixture()
        value = json.loads(self.primary.read_text())
        value["nativeValue"]["secret"] = "SYNTHETIC_SECRET"
        write(self.primary, value)
        operation = json.loads(self.operation.read_text())
        operation["value"]["primary"].update(sha256=sha(self.primary), bytes=self.primary.stat().st_size)
        write(self.operation, operation)
        self.reject()

    def test_existing_destination_and_closed_bypass_are_rejected(self):
        self.fixture()
        self.output.mkdir()
        sentinel = self.output / "PRESERVE.txt"
        sentinel.write_text("unchanged")
        before = self.source_hashes()
        with self.assertRaises(ValueError):
            self.export()
        self.assertEqual(sentinel.read_text(), "unchanged")
        self.assertEqual(list(self.output.iterdir()), [sentinel])
        self.assertEqual(self.source_hashes(), before)
        with self.assertRaises(ValueError):
            self.export(strict_closed=False)


if __name__ == "__main__":
    unittest.main(verbosity=2)

