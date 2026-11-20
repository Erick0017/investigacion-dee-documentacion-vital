"""Technical fixtures from frozen DEV; never final three-arm results/Native."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("_C02_comparison_test", ROOT / "analisis/RECALCULO_COMPARATIVA_C02.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
DEV = ROOT / "evidencia/DEV_REAPERTURA_R04/WORLD_FINAL.json"
BEFORE = ROOT / "evidencia/DEV_REAPERTURA_R04/WORLD_RESTORED_BEFORE_NATIVE.json"


class ComparisonTests(unittest.TestCase):
    def test_real_frozen_DEV_fixture_counts_and_common_missing_arms(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "pruebas") as temp:
            report = m.recalculate({"LIVE_NATIVE": ([BEFORE, DEV], [])}, Path(temp) / "out", technical=True)
            total = next(r for r in report["summary_rows"] if r["arm"] == "LIVE_NATIVE" and r["scope"] == "ALL_ACTUALLY_OBSERVED")
            self.assertEqual(report["arms"]["LIVE_NATIVE"]["completed_opportunities"], 4)
            self.assertEqual(total["actual_unique_actions"], 8)
            self.assertEqual(total["numeric_formed"], 2)
            self.assertEqual(total["arithmetic_correct"], 2)
            self.assertEqual(total["resources_collected"], 1)
            self.assertEqual(total["resources_delivered"], 0)
            self.assertEqual(total["codes_accepted"], 1)
            self.assertEqual(total["Native_tick_delta_observed"], 6256)
            self.assertEqual(report["common_completed_observed_prefix"], 0)
            self.assertTrue(report["technical_fixture_only_not_final_benchmark"])
            self.assertEqual(report["issues"], [])
    def test_full_checkpoint_prefixes_deduplicate(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "pruebas") as temp:
            report = m.recalculate({"LIVE_NATIVE": ([BEFORE, DEV, DEV], [])}, Path(temp) / "out", technical=True)
            self.assertEqual(report["arms"]["LIVE_NATIVE"]["unique_world_events"], 52)
            self.assertGreater(report["arms"]["LIVE_NATIVE"]["world_event_aliases_deduplicated"], 0)
            self.assertEqual(len(report["opportunity_rows"]), 4)
    def test_missing_full_S_endpoint_is_unknown(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "pruebas") as temp:
            report = m.recalculate({"LIVE_NATIVE": ([DEV], [])}, Path(temp) / "out", technical=True)
            period = next(r for r in report["summary_rows"] if r["arm"] == "LIVE_NATIVE" and r["scope"] == "PERIOD_1_6")
            self.assertIsNone(period["S_before_actual_checkpoint"])
            self.assertIsNone(period["S_after_actual_checkpoint"])
    def test_optional_frozen_DEV_native_receipts_are_not_inferred(self):
        native = ROOT / "native/DEV/sistema/estado/servicios_locales/ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_DEV/RBX02_NATIVE_C02"
        with tempfile.TemporaryDirectory(dir=ROOT / "pruebas") as temp:
            report = m.recalculate({"LIVE_NATIVE": ([DEV], [])}, Path(temp) / "out", technical=True,
                                   native_function_paths=[native / "functions"], native_event_paths=[str(native / "events.jsonl")])
            self.assertEqual(report["Native_material_coverage"]["unique_requested_observed"], 424)
            self.assertEqual(sum(r["Native_inputs_requested"] for r in report["opportunity_rows"]), 424)
            self.assertEqual(report["Native_material_coverage"]["unassigned_receipts_preserved"], [])
            self.assertEqual(report["issues"], [])
    def test_final_fingerprint_rejects_DEV_fixture(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "pruebas") as temp:
            with self.assertRaisesRegex(ValueError, "fingerprint"):
                m.recalculate({"LIVE_NATIVE": ([DEV], [])}, Path(temp) / "out", technical=False)
    def test_null_zero_lesson_and_actual_opcode_are_separate(self):
        value = json.loads(DEV.read_bytes())
        events = [copy.deepcopy(r) for r in value["events"] if r["kind"] == "FUNCTION_APPLIED"]
        for index, event in enumerate(events):
            event["source_sha256"] = "FIXTURE_" + str(index)
        # Original LESSON formedFalse is not a failure; no injected experience.
        actual = events[1]; actual["data"]["request"].update(left=2, right=2)
        actual["data"]["output"].update(operation="diferencia", numeric_result=0, formed=True)
        events[2]["data"]["output"]["numeric_result"] = None
        row = m.opportunity("LIVE_NATIVE", 1, events, {}, False, [])
        self.assertEqual(row["partial_lesson_admissions"], 0)
        self.assertEqual(row["numeric_valid_zero"], 1)
        self.assertEqual(row["numeric_NULL_or_absent"], 1)
        self.assertEqual(row["arithmetic_correct"], 1)
        self.assertEqual(row["arithmetic_not_evaluable"], 1)
    def test_voluntary_wait_requires_policy_evidence(self):
        event = {"kind": "ACTION_EXECUTED", "data": {"action": {"name": "SAFE_WAIT", "actionId": "TEST", "null": False}, "result": {}},
                 "seq": 1, "sessionId": "FIXTURE", "source_sha256": "TEST"}
        unknown = m.opportunity("CONVENTIONAL_AI", 1, [event], {}, False, [])
        voluntary = m.opportunity("CONVENTIONAL_AI", 1, [event], {"TEST": {"result": {"evidence": {"voluntary_wait": True}}}}, False, [])
        event["data"]["action"]["null"] = True
        null = m.opportunity("CONVENTIONAL_AI", 1, [event], {}, False, [])
        self.assertEqual(unknown["SAFE_WAIT_intention_unknown"], 1)
        self.assertEqual(voluntary["SAFE_WAIT_explicit_voluntary_policy"], 1)
        self.assertEqual(null["SAFE_WAIT_from_NULL_or_invalid"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
