"""Four synthetic focal export/recalculation fixtures; never open a real instance."""
from pathlib import Path
from copy import deepcopy
from contextlib import contextmanager
from unittest import mock
import builtins
import hashlib
import importlib.util
import json
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
START = 991187
INSTANCE = "SDK_DEMO_0123456789ABCDEF"
LIFE = "ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_" + INSTANCE
SID = "SDK_SESSION_0123456789abcdef0123456789abcdef"


@contextmanager
def no_operational_imports():
    original = builtins.__import__
    def guarded(name, globals=None, locals=None, fromlist=(), level=0):
        if any(name == item or name.startswith(item + ".")
               for item in ("dee_thinking", "capacidades", "sqlite3")):
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


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def write(path, value, jsonl=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(canonical(x) + "\n" for x in value) if jsonl else canonical(value) + "\n"
    path.write_text(text, encoding="utf8")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class FakeDataset:
    """One literal cycle: Q1=5, Q2=2, feedback=13 ticks; no fabricated bindings."""
    def __init__(self, paid=True, null_route=False, duplicate_receipt=False):
        self.cfg = {
            "instanceId": INSTANCE, "lifeId": LIFE, "sessionId": SID,
            "profile": "FOCAL", "validationRevision": "FOCAL_R06", "focalCondition": "OSCILANTE",
            "maxCycles": 6, "maxLocalSequence": 12, "sequenceOffset": 56,
            "completedCycles": 1, "localSequence": 2, "nativeTick": START + 20,
            "initialPublicState": {"permissionStock": 164},
        }
        def receipt(identifier, channel, at):
            return {"id": identifier, "channel": channel, "payload": 0, "requested_tick": at,
                    "receipt": {"id": identifier, "status": "applied", "effective_tick": at}}
        q1r = receipt(701, "QUESTION" if paid else "Q1_QUERY", START + 1)
        q2r = receipt(702, "PAID_DATUM" if paid else "Q2_QUERY", START + 6)
        returns = [receipt(703, "Q2_RETURN", START + 8), receipt(704, "Q1_RETURN", START + 9)]
        self.receipts = [q1r, q2r, *returns]
        final_receipts = deepcopy(self.receipts)
        if duplicate_receipt:
            final_receipts.append(deepcopy(q1r))
        q1result = {
            "permissionSpent": int(paid), "querySpent": int(paid), "tollSpent": 0,
            "outcome": "PANEL_OBSERVED" if paid else "QUERY_OMITTED",
            "collision": False, "invalidAction": False, "materialConsequence": False,
            "resourceCollected": False, "resourceDelivered": False,
            "worldTimeMs": 100, "durationMs": 100,
        }
        q2result = {
            "permissionSpent": 0, "querySpent": 0, "tollSpent": 0,
            "outcome": "WAITED" if null_route else "MOVED",
            "collision": False, "invalidAction": False, "materialConsequence": False,
            "resourceCollected": False, "resourceDelivered": False,
            "worldTimeMs": 200, "durationMs": 100,
        }
        if not null_route:
            q2result.update(selectedPort=0, originStation=0, selectedTarget=1,
                            passage={"freePassUsed": True, "rechargeAt": 4})
        observation1 = {"observationId": "OBS_1", "seq": 57, "phase": "QUERY_CHOICE",
                        "worldTimeMs": 0, "sampleTimeMs": 0, "previousActionId": None,
                        "sensors": {"station": 0, "permissionStock": 164, "stationSignal": -1}}
        observation2 = {"observationId": "OBS_2", "seq": 58, "phase": "ROUTE_CHOICE",
                        "worldTimeMs": 100, "sampleTimeMs": 100, "previousActionId": "Q1",
                        "sensors": {"station": 0, "permissionStock": 164-int(paid),
                                    "stationSignal": 0 if paid else -1}}
        feedback = {
            "actionId": "Q2", "seq": 58, "observationId": "OBS_2",
            "permissionSpent": int(paid), "outcome": q2result["outcome"],
            "collision": False, "resourceCollected": False, "resourceDelivered": False,
            "materialConsequence": False, "worldTimeMs": 200, "durationMs": 100,
            "lastObservation": observation2,
        }
        q1value = {
            "nativeTick": START+5, "nativeTicks": 5,
            "action": "ASK_STATION" if paid else "SKIP_STATION", "null": False,
            "evidence": {
                "question_receipt": deepcopy(q1r) if paid else None,
                "question_observation": {"state": 1 if paid else 0, "semantic": 1,
                                         "direction": [1, 0, 0] if paid else [0, 0, 0]},
                "Native_inputs": {"requested": 1, "applied": 1},
            },
        }
        q2value = {
            "nativeTick": START+7, "nativeTicks": 2,
            "action": "SAFE_WAIT" if null_route else "EXIT_0", "null": null_route,
            "evidence": {
                "reader": {"choice": None if null_route else 1},
                "datum_request": {"id": 702} if paid else None, "datum_omitted": not paid,
                "raw_price": 0 if paid else -1, "actual_tag": 0,
                "submitted_tag": 0 if paid else None,
                "Native_inputs": {"requested": 2, "applied": 2},
            },
        }
        fbvalue = {
            "nativeTick": START+20, "nativeTicks": 13, "accepted": True, "action": None,
            "evidence": {"requests": final_receipts, "actual_consequence": deepcopy(feedback),
                         "Native_inputs": {"requested": 4, "applied": 4},
                         "actual_physical_failed": False, "applied_generic_failed": False,
                         "generic_return_pulses": 2},
        }
        self.members = {}
        self.journal = []
        self.operations = []
        before = START
        phases = (
            ("Q1", "decision", "eci01-rbx01-decision", {"observation": observation1}, q1value, 1, 57),
            ("Q2", "query_sensor", "eci01-rbx01-query-sensor", {"observation": observation2}, q2value, 2, 58),
            ("FB", "feedback", "eci01-rbx01-feedback", feedback, fbvalue, 2, 58),
        )
        for identifier, kind, mode, payload, value, local, native in phases:
            context = {"session_id": SID, "sequence": native, "observation_id": "OBS_1" if local == 1 else "OBS_2",
                       "operation_id": identifier, "mode": "LIVE_NATIVE"}
            self.journal.append({"kind": "PHASE_INTENT", "mode": mode, "tick": before,
                                 "payload": deepcopy(payload), "context": deepcopy(context)})
            self.journal.append({"kind": "PHASE_COMPLETED", "mode": mode, "tick": value["nativeTick"],
                                 "result": deepcopy(value)})
            before = value["nativeTick"]
            archive = "PRIMARIOS/HTTP/" + identifier + ".json"
            self.operations.append(archive)
            self.members[archive] = {
                "operationId": identifier, "kind": kind, "status": "COMPLETED",
                "nativePayload": deepcopy(payload), "nativeContext": deepcopy(context),
                "localSequence": local, "value": deepcopy(value),
            }
        acks, action_records = {}, {}
        for identifier, seq, result in (("Q1", 1, q1result), ("Q2", 2, q2result)):
            ack = {"actionId": identifier, "operationId": identifier, "seq": seq,
                   "executionStatus": "EXECUTED", "technicalControl": False,
                   "result": deepcopy(result)}
            acks[identifier] = {"actionId": identifier, "ack": deepcopy(ack)}
            action_records[identifier] = {"status": "ACKNOWLEDGED" if identifier == "Q1" else "COMMITTED",
                                          "ack": deepcopy(ack)}
        events = [
            {"kind": "ACTION_EXECUTED", "data": {"actionId": "Q1", "name": q1value["action"],
                                                "result": deepcopy(q1result)}},
            {"kind": "ACTION_EXECUTED", "data": {"actionId": "Q2", "name": q2value["action"],
                                                "result": deepcopy(q2result)}},
        ]
        if paid:
            events.insert(0, {"kind": "PAID_LOCAL_PANEL", "data": {
                "actionId": "Q1", "station": 0, "epoch": 1,
                "sample": {"signal": 0, "price0": 0, "price1": 2, "epoch": 1},
            }})
        ports = [{"station": s, "port": port, "available": True} for s in range(6) for port in range(2)]
        world_state = {
            "stock": 164-int(paid), "queries": int(paid), "skips": int(not paid),
            "moves": int(not null_route), "waits": int(null_route),
            "tollSpent": 0, "freePassesUsed": int(not null_route),
            "environmentEvents": events,
        }
        snapshot = {
            "schema": "DEE.RBX.AgentWorldCheckpoint.R01", "namespace": "FAKE/FOCAL/AGENT",
            "scenarioFingerprint": "a"*64,
            "state": {"phase": "BOUNDARY", "lifeId": LIFE, "sessionId": SID, "nativeTick": START+20,
                      "sequence": 2, "completedOpportunities": 1},
            "actions": action_records, "tools": {}, "body": {"schema": "DEE.Focal.Body.R02", "pose": []},
            "world": {"schema": "DEE.Focal.World.R02", "state": world_state,
                      "availability": {"schema": "DEE.Focal.LocalAvailability.R02",
                                       "arm": "CONSUME_RECHARGE", "epoch": 1, "ports": ports, "actions": {}}},
        }
        self.pair = {"snapshot": snapshot, "snapshotSha256": hashlib.sha256(canonical(snapshot).encode()).hexdigest()}
        self.members["PRIMARIOS/SDK_PAIR.json"] = self.pair
        self.members["PRIMARIOS/ACTION_ACKS.json"] = acks
        self.members["PRIMARIOS/NATIVE/events.jsonl"] = self.journal
        self.world = {"cycles": 1, "consumed": 20, "reserved": 0}
        self.index = {"configuration": self.cfg, "operations": self.operations,
                      "closure": {"nativeTick": START+20, "ledgerWorld": self.world}}

    def local(self, name, jsonl=False):
        return deepcopy(self.members[name])

    def filesystem(self, base):
        runtime = Path(base) / "RUNTIME_PRIVADO_LOCAL"
        home = runtime / "estado_demo/instancias" / INSTANCE
        write(home/"INSTANCE.json", self.cfg)
        card = {"life_id": LIFE, "snapshot_sha256": "b"*64,
                "physical": {"N": 67, "tick": START+20, "RAW_sha256": "c"*64, "clocks_sha256": "d"*64}}
        cardfile = home/"sistema/estado/vidas"/LIFE/"VIDA.json"
        write(cardfile, card)
        native = {"lifeId": LIFE, "dimension": 67, "nativeTick": START+20, "writerClosed": True,
                  "pending": 0, "snapshotSha256": "b"*64, "databaseSha256": "e"*64,
                  "cardSha256": sha(cardfile)}
        proof = dict(native, backendWriterClosed=True, bridgeQuiescent=True)
        pair = deepcopy(self.pair)
        pair.update(native=native, backendProof=proof, instanceId=INSTANCE, sessionId=SID, localSequence=2)
        write(home/"SDK_PAIR.json", pair)
        write(home/"BACKEND_CLOSED.json", proof)
        write(home/"ACTION_ACKS.json", self.members["PRIMARIOS/ACTION_ACKS.json"])
        write(home/"ENSAYOS.jsonl", [{"kind": "OWNER_CLOSED", "exit_code": 0,
              "final_status": {"running": False, "tick": START+20}}], True)
        worker = home/"sistema/estado/servicios_locales"/LIFE
        write(worker/"DEE_SDK_FOCAL_NATIVE_0_1_0/events.jsonl", self.journal, True)
        for archive in self.operations:
            write(home/"http_operations"/Path(archive).name, self.members[archive])
        write(runtime/"estado_demo/LEDGER_SDK_R06.json", {"intents": {}, "worlds": {LIFE: self.world}})
        write(runtime/"configuracion/CONEXION_PRIVADA.json", {"token": "SYNTHETIC_PRIVATE_TOKEN_NOT_FOR_EXPORT_123456"})
        write(runtime/"configuracion/VENTANA_FOCAL_R06.json", {"schema": "FAKE_WINDOW", "hardFinishUtcEpoch": 3000})
        write(runtime/"backend/focal_r06/FUENTES_FOCAL_R06.json", {"schema": "FAKE_SOURCE_PINS", "files": []})
        protocol = Path(base)/"PROTOCOL.json"
        write(protocol, {"schema": "FAKE_PROSPECTIVE_PROTOCOL", "status": "FIXED_BEFORE_SYNTHETIC_TEST"})
        return runtime, home, protocol


class FocalExportR06Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tool = load(HERE/"exportar_recalcular_focal_R06.py", "_pure_focal_export_R06")

    def facts(self, dataset):
        with no_operational_imports():
            return self.tool.facts(deepcopy(dataset.index), dataset.local)

    def test_paid_ask_price_zero_applied_cost_stock_and_phase_chain(self):
        value = self.facts(FakeDataset(paid=True))
        self.assertEqual(value["actualCompletedCycles"], 1)
        self.assertEqual([p["kind"] for p in value["cycles"][0]["phases"]],
                         ["decision", "query_sensor", "feedback"])
        self.assertEqual(value["cycles"][0]["nativeRawPrice"], 0)
        self.assertEqual((value["paidASKApplied"], value["NativeQ2DatumApplied"]), (1, 1))
        self.assertEqual(value["costs"], {"permissionSpent": 1, "querySpent": 1, "tollSpent": 0})
        self.assertEqual(value["stock"], {"initial": 164, "final": 163})
        self.assertEqual(value["newNativeTicks"], 20)
        for phase in value["cycles"][0]["phases"]:
            self.assertEqual(phase["nativeSequence"], 56+phase["localSequence"])

    def test_skip_without_panel_and_omitted_datum_is_not_paid_exposure(self):
        value = self.facts(FakeDataset(paid=False))
        self.assertEqual((value["paidASKApplied"], value["nativeQuestionReleased"],
                          value["NativeQ2DatumApplied"], value["datumOmitted"]), (0, 0, 0, 1))
        self.assertIsNone(value["cycles"][0]["paidPanel"])
        self.assertEqual(value["cycles"][0]["nativeRawPrice"], -1)
        self.assertEqual(value["stock"], {"initial": 164, "final": 164})
        self.assertEqual(value["costs"]["permissionSpent"], 0)

    def test_cumulative_receipt_union_does_not_sum_phases_and_retains_null(self):
        value = self.facts(FakeDataset(paid=True, null_route=True, duplicate_receipt=True))
        self.assertEqual(value["NativeInputs"], {"requested": 4, "applied": 4, "rejected": 0})
        self.assertEqual(value["cycles"][0]["NativeInputs"], value["NativeInputs"])
        route = value["cycles"][0]["actions"][1]
        self.assertTrue(route["nativeNull"])
        self.assertIsNone(route["nativeEvidence"]["reader"]["choice"])
        self.assertEqual(route["nativeAction"], "SAFE_WAIT")
        self.assertFalse(value["NativeExecuted"])
        self.assertFalse(value["SQLiteOpened"])

    def test_native_question_release_requires_full_observation_signature(self):
        for patch, expected in (({}, True), ({"state": 0}, False),
                                ({"semantic": 0}, False), ({"direction": [0, 1, 0]}, False)):
            with self.subTest(observation_patch=patch):
                dataset = FakeDataset(paid=True)
                admitted = dataset.members["PRIMARIOS/HTTP/Q1.json"]["value"]
                completed = next(row["result"] for row in dataset.journal
                                 if row.get("kind") == "PHASE_COMPLETED"
                                 and row.get("mode") == "eci01-rbx01-decision")
                for value in (admitted, completed):
                    value["evidence"]["question_observation"].update(deepcopy(patch))
                    self.assertEqual(value["evidence"]["question_receipt"]["receipt"]["status"], "applied")
                result = self.facts(dataset)
                self.assertIs(result["cycles"][0]["nativeQuestionReleased"], expected)
                self.assertEqual(result["nativeQuestionReleased"], int(expected))

    def test_closed_export_rejects_lock_and_recalculates_without_source_runtime(self):
        dataset = FakeDataset(paid=True)
        with tempfile.TemporaryDirectory(prefix="focal_export_e2e_pure_") as temporary:
            base = Path(temporary)
            runtime, home, protocol = dataset.filesystem(base)
            output = base/"PACKAGE"
            lock = home/"SDK_SERVICE.lock"
            lock.write_bytes(b"SYNTHETIC_LOCK")
            with no_operational_imports(), self.assertRaises(ValueError):
                self.tool.export(runtime, INSTANCE, "OSCILANTE", protocol, output)
            self.assertFalse(output.exists())
            lock.unlink()
            pins = {p.relative_to(runtime).as_posix(): sha(p) for p in runtime.rglob("*") if p.is_file()}
            with no_operational_imports():
                result = self.tool.export(runtime, INSTANCE, "OSCILANTE", protocol, output)
            self.assertEqual(result["status"], "EXPORTED_CLOSED")
            self.assertEqual(pins, {p.relative_to(runtime).as_posix(): sha(p) for p in runtime.rglob("*") if p.is_file()})
            expected = json.loads((output/"HECHOS_RECALCULADOS.json").read_text())
            self.assertNotIn("bindings", json.loads((home/"SDK_PAIR.json").read_text())["snapshot"])
            runtime.rename(base/"SOURCES_INACCESSIBLE")
            protocol.rename(base/"PROTOCOL_INACCESSIBLE.json")
            portable = load(output/"RECALCULAR_FOCAL_R06.py", "_portable_focal_export_R06")
            original = portable.raw
            def local_only(path):
                self.assertTrue(Path(path).resolve().is_relative_to(output.resolve()))
                return original(path)
            with mock.patch.object(portable, "raw", side_effect=local_only), no_operational_imports():
                recalculated = portable.recalculate(output, output/"RECALCULO_NUEVO")
            self.assertEqual(recalculated, expected)
            self.assertEqual(recalculated["NativeInputs"]["applied"], 4)
            self.assertEqual(recalculated["stock"]["final"], 163)


if __name__ == "__main__":
    unittest.main(verbosity=2)

