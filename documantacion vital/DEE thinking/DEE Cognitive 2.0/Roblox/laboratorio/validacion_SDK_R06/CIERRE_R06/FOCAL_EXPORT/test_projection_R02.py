"""Two new pure fixtures for the frozen NativeAdapter HTTP projection."""
from pathlib import Path
from copy import deepcopy
from unittest import mock
import hashlib
import importlib.util
import json
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
VERSION = "DEE.Roblox.SDK.focal.native.0.1.0"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeOwner:
    life = "FAKE_LIFE_ONLY"
    def __init__(self, raw):
        self.raw = deepcopy(raw)
        self.calls = []
    def material(self, identifier, literal, **kwargs):
        self.calls.append((identifier, deepcopy(literal), deepcopy(kwargs)))
        return {"rows": [deepcopy(self.raw)]}


class ProjectionR02Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = load("_focal_export_R01_factory", HERE / "test_focal_export_R06.py")
        with cls.base.no_operational_imports():
            cls.tool = load("_focal_export_R02_projection", HERE / "exportar_recalcular_focal_R06_R02.py")
            cls.adapter = load("_frozen_focal_native_adapter",
                               HERE.parents[2] / "RUNTIME_PRIVADO_LOCAL/backend/focal_r06/native_adapter.py")

    def raw_dataset(self):
        dataset = self.base.FakeDataset(paid=True)
        # R01's abstract factory omitted version. Establish the real RAW schema
        # before deriving any public values; old factory/source files stay intact.
        pending = None
        for row in dataset.journal:
            if row["kind"] == "PHASE_INTENT":
                pending = row
            elif row["kind"] == "PHASE_COMPLETED":
                row["result"]["version"] = VERSION
                identifier = pending["context"]["operation_id"]
                dataset.members["PRIMARIOS/HTTP/" + identifier + ".json"]["value"] = deepcopy(row["result"])
        return dataset

    def project_http_only(self, dataset):
        raw_before = deepcopy(dataset.journal)
        pending = None
        for row in dataset.journal:
            if row["kind"] == "PHASE_INTENT":
                pending = row
            elif row["kind"] == "PHASE_COMPLETED":
                identifier = pending["context"]["operation_id"]
                operation = dataset.members["PRIMARIOS/HTTP/" + identifier + ".json"]
                other_fields = deepcopy({k: v for k, v in operation.items() if k != "value"})
                owner = FakeOwner(row["result"])
                actual = self.adapter.NativeAdapter(owner).execute(
                    operation["kind"], operation["nativePayload"], operation["nativeContext"])
                expected = self.tool.project_native_result(row["result"], identifier)
                self.assertEqual(actual, expected)
                self.assertEqual(owner.calls, [(identifier, {
                    "modo": pending["mode"], "payload": operation["nativePayload"],
                    "context": operation["nativeContext"]},
                    {"feedback": "omit", "actuator": "closed"})])
                self.assertEqual({k: v for k, v in actual.items() if k != "evidence"},
                                 {k: v for k, v in row["result"].items() if k != "evidence"})
                operation["value"] = actual
                self.assertEqual(other_fields, {k: v for k, v in operation.items() if k != "value"})
        self.assertEqual(dataset.journal, raw_before)
        return dataset

    def facts(self, dataset):
        with self.base.no_operational_imports():
            return self.tool.facts(deepcopy(dataset.index), dataset.local)

    def test_projection_matches_real_stdlib_adapter_and_rejects_literal_tampering(self):
        dataset = self.project_http_only(self.raw_dataset())
        self.assertEqual(self.facts(dataset)["newNativeTicks"], 20)
        q1 = dataset.members["PRIMARIOS/HTTP/Q1.json"]["value"]
        self.assertEqual(set(q1["evidence"]), {
            "native_request_id", "native_phase_sha256", "full_evidence"})
        self.assertEqual(q1["evidence"]["native_request_id"], "Q1")
        self.assertEqual(q1["evidence"]["full_evidence"],
                         "Official Native queue result and DEE_SDK_NATIVE_0_1_0/events.jsonl")
        for alteration in ("action", "tick", "raw_receipt", "hash"):
            value = self.project_http_only(self.raw_dataset())
            operation = value.members["PRIMARIOS/HTTP/Q1.json"]
            if alteration == "action":
                operation["value"]["action"] = "SKIP_STATION"
            elif alteration == "tick":
                operation["value"]["nativeTick"] += 1
            elif alteration == "hash":
                operation["value"]["evidence"]["native_phase_sha256"] = "0" * 64
            else:
                feedback = next(row["result"] for row in value.journal
                                if row.get("kind") == "PHASE_COMPLETED"
                                and row.get("mode") == "eci01-rbx01-feedback")
                feedback["evidence"]["requests"][0]["receipt"]["status"] = "rejected_synthetic_tamper"
            with self.subTest(alteration=alteration), self.assertRaisesRegex(
                    ValueError, "DURABLE_HTTP_NATIVE_RESULT_MISMATCH"):
                self.facts(value)
        raw = deepcopy(next(row["result"] for row in dataset.journal
                            if row.get("kind") == "PHASE_COMPLETED"))
        raw["version"] = "WRONG_NATIVE_VERSION"
        with self.assertRaises(ValueError):
            self.tool.project_native_result(raw, "Q1")
        owner = FakeOwner(raw)
        operation = dataset.members["PRIMARIOS/HTTP/Q1.json"]
        with self.assertRaises(self.adapter.NativeUnavailable):
            self.adapter.NativeAdapter(owner).execute(
                operation["kind"], operation["nativePayload"], operation["nativeContext"])

    def test_projected_http_export_and_portable_recalculation_without_original_sources(self):
        dataset = self.project_http_only(self.raw_dataset())
        with tempfile.TemporaryDirectory(prefix="focal_projection_r02_pure_") as temporary:
            base = Path(temporary)
            runtime, home, protocol = dataset.filesystem(base)
            output = base / "PACKAGE"
            before = {p.relative_to(runtime).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in runtime.rglob("*") if p.is_file()}
            with self.base.no_operational_imports():
                exported = self.tool.export(runtime, self.base.INSTANCE, "OSCILANTE", protocol, output)
            self.assertEqual(exported["status"], "EXPORTED_CLOSED")
            self.assertEqual(before, {p.relative_to(runtime).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in runtime.rglob("*") if p.is_file()})
            expected = json.loads((output / "HECHOS_RECALCULADOS.json").read_text())
            self.assertEqual(expected["NativeInputs"], {"requested": 4, "applied": 4, "rejected": 0})
            self.assertEqual(expected["stock"], {"initial": 164, "final": 163})
            # Projection never replaces the RAW journal primary or its receipts.
            copied_journal = [json.loads(line) for line in
                              (output / "PRIMARIOS/NATIVE/events.jsonl").read_text().splitlines()]
            self.assertEqual(copied_journal, dataset.journal)
            copied_http = json.loads((output / "PRIMARIOS/HTTP/Q1.json").read_text())
            self.assertEqual(copied_http["value"], dataset.members["PRIMARIOS/HTTP/Q1.json"]["value"])
            runtime.rename(base / "RUNTIME_SOURCE_INACCESSIBLE")
            protocol.rename(base / "PROTOCOL_SOURCE_INACCESSIBLE.json")
            with self.base.no_operational_imports():
                portable = load("_portable_focal_projection_R02", output / "RECALCULAR_FOCAL_R06_R02.py")
            original = portable.raw
            def extraction_only(path):
                self.assertTrue(Path(path).resolve().is_relative_to(output.resolve()))
                return original(path)
            with mock.patch.object(portable, "raw", side_effect=extraction_only), self.base.no_operational_imports():
                recalculated = portable.recalculate(output, output / "RECALCULO_NUEVO")
            self.assertEqual(recalculated, expected)
            self.assertEqual(recalculated["cycles"][0]["nativeRawPrice"], 0)
            self.assertFalse(recalculated["NativeExecuted"])
            self.assertFalse(recalculated["SQLiteOpened"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

