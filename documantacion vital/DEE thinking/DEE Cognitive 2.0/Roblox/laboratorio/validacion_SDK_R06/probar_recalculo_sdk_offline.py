#!/usr/bin/env python3
"""Fixtures sintéticos del collector; no importa código Native ni lee instancias reales."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", required=True, type=Path)
    args = p.parse_args()
    args.output_dir.mkdir(exist_ok=False)
    module_path = Path(__file__).with_name("recalcular_validacion_sdk.py")
    compile(module_path.read_text("utf-8"), str(module_path), "exec")
    spec = importlib.util.spec_from_file_location("sdk_passive_collector_fixture", module_path)
    collector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(collector)
    iid, sid, life = "SDK_DEMO_0000000000000001", "SDK_SYNTHETIC_SESSION", "SDK_SYNTHETIC_LIFE"
    cfg = {"instanceId": iid, "sessionId": sid, "lifeId": life, "nativeTick": 101, "sequenceOffset": 56, "localSequence": 2, "completedCycles": 1, "nextPhase": "decision"}
    values, acks, receipts, operations = {}, {}, {}, {}
    for index, action in ((1, "ASK_STATION"), (2, "EXIT_0")):
        op, oid = f"op{index}", f"obs{index}"
        result = {"before": [0, 3, 0], "after": [0, 3, 0] if index == 1 else [-12, 3, 48], "collision": False, "invalidAction": False, "resourceCollected": False, "resourceDelivered": False, "permissionSpent": 1 if index == 1 else 0, "outcome": "PANEL_OBSERVED" if index == 1 else "MOVED", "materialConsequence": False, "durationMs": 100 if index == 1 else 6000, "worldTimeMs": 100 if index == 1 else 6100, "deviceBefore": -1, "deviceAfter": -1 if index == 1 else 0}
        value = {"nativeTick": 89 + index, "action": action, "null": False}
        values[op] = value
        ack = {"protocol": "DEE.RBX.Connector.R01", "sessionId": sid, "actionId": op, "operationId": op, "observationId": oid, "seq": index, "executionStatus": "EXECUTED", "technicalControl": False, "result": result}
        acks[op] = {"instanceId": iid, "sessionId": sid, "operationId": "ack" + str(index), "actionId": op, "observationId": oid, "localSequence": index, "ack": ack}
        receipts[op] = {"status": "ACKNOWLEDGED" if index == 1 else "COMMITTED", "operationId": op, "technical": False, "ack": ack, "rawRequest": json.dumps({"sourceKind": "DEE_NATIVE", "operationId": op, "action": {"name": action}})}
        operations[op] = {"operationId": op, "kind": "decision" if index == 1 else "query_sensor", "status": "COMPLETED", "body": {"instanceId": iid, "sessionId": sid, "operationId": op}, "localSequence": index, "nativeContext": {"mode": "LIVE_NATIVE", "session_id": sid, "operation_id": op, "observation_id": oid, "sequence": 56 + index}, "value": value}
    payload = dict(acks["op2"]["ack"]["result"], actionId="op2", observationId="obs2", seq=2)
    operations["feedback"] = {"operationId": "feedback", "kind": "feedback", "status": "COMPLETED", "localSequence": 2, "body": {"instanceId": iid, "sessionId": sid, "operationId": "feedback", "payload": payload}, "nativeContext": {"mode": "LIVE_NATIVE", "session_id": sid, "operation_id": "feedback", "observation_id": "obs2", "sequence": 58}, "value": {"accepted": True, "nativeTick": 101}}
    proof = {"nativeTick": 101, "lifeId": life, "sessionId": sid, "localSequence": 2, "backendWriterClosed": True, "bridgeQuiescent": True}
    proof["proofSha256"] = collector.digest(proof)
    snapshot = {"schema": "DEE.RBX.AgentWorldCheckpoint.R01", "state": {"sessionId": sid, "lifeId": life, "nativeTick": 101, "sequence": 2, "completedOpportunities": 1, "phase": "BOUNDARY"}, "actions": receipts}
    pair = {"checkpointId": "cp1", "instanceId": iid, "sessionId": sid, "snapshot": snapshot, "snapshotSha256": collector.digest(snapshot), "backendProof": proof, "native": {"nativeTick": 101}, "localSequence": 2}
    operations["close"] = {"operationId": "close", "kind": "close", "status": "COMPLETED", "body": {"instanceId": iid, "sessionId": sid, "operationId": "close"}, "value": {"backendProof": proof}}
    base = {"INSTANCE.json": cfg, "ACTION_ACKS.json": acks, "BACKEND_CLOSED.json": proof, "SDK_PAIR.json": pair, **{"http_operations/" + op + ".json": row for op, row in operations.items()}}
    tests = []

    def run(name, mutate, expected2, expected3, expected_issues=0):
        documents = copy.deepcopy(base)
        mutate(documents)
        home = args.output_dir / name
        home.mkdir()
        for relative, value in documents.items():
            write(home / relative, value)
        before = {str(x.relative_to(home)): hashlib.sha256(x.read_bytes()).hexdigest() for x in home.rglob("*.json")}
        report = collector.collect(home)
        after = {str(x.relative_to(home)): hashlib.sha256(x.read_bytes()).hexdigest() for x in home.rglob("*.json")}
        assert before == after, name + " source mutation"
        assert report["K2"]["status"] == expected2, (name, "K2", report["K2"])
        assert report["K3"]["status"] == expected3, (name, "K3", report["K3"])
        assert report["K4"]["status"] == "PENDING_DIRECT_REOPEN_AND_POST_USE_EVIDENCE", name
        assert len(report["issues"]) == expected_issues, (name, report["issues"])
        write(args.output_dir / (name + "_REPORT.json"), report)
        tests.append({"name": name, "passed": True, "sourceUnchanged": True, "K2": expected2, "K3": expected3})

    pending2, pending3 = "PENDING_COMMITTED_CHAIN_EVIDENCE", "PENDING_COMMITTED_EFFECT_AND_RETURN"
    yes2, yes3 = "DOCUMENTED_LOCAL_CHAIN", "DOCUMENTED_LOCAL_EFFECT_AND_RETURN"
    run("01_full_synthetic_chain", lambda d: None, yes2, yes3)
    run("02_no_pair", lambda d: d.pop("SDK_PAIR.json"), pending2, pending3)
    run("03_no_feedback", lambda d: d.pop("http_operations/feedback.json"), pending2, pending3)
    run("04_wrong_ack_session", lambda d: d["ACTION_ACKS.json"]["op2"]["ack"].update(sessionId="OTHER_SESSION"), pending2, pending3)
    run("05_uncommitted_receipt", lambda d: (d["SDK_PAIR.json"]["snapshot"]["actions"]["op2"].update(status="ACKNOWLEDGED"), d["SDK_PAIR.json"].update(snapshotSha256=collector.digest(d["SDK_PAIR.json"]["snapshot"]))), pending2, pending3)
    run("06_bad_pair_digest", lambda d: d["SDK_PAIR.json"].update(snapshotSha256="0" * 64), pending2, pending3)
    run("07_duplicate_operation_id", lambda d: d.update({"http_operations/alias.json": copy.deepcopy(d["http_operations/op2.json"])}), pending2, pending3, 1)
    run("08_feedback_wrong_effect", lambda d: d["http_operations/feedback.json"]["body"]["payload"].update(resourceCollected=True), pending2, pending3)

    def no_effect(d):
        for result in (d["ACTION_ACKS.json"]["op2"]["ack"]["result"], d["SDK_PAIR.json"]["snapshot"]["actions"]["op2"]["ack"]["result"]):
            result.update(after=[0, 3, 0], deviceAfter=-1)
        d["SDK_PAIR.json"]["snapshotSha256"] = collector.digest(d["SDK_PAIR.json"]["snapshot"])
    run("09_no_observed_physical_effect", no_effect, yes2, pending3)

    def archived_pair(d):
        older = copy.deepcopy(d["SDK_PAIR.json"])
        older.update(checkpointId="cp0", localSequence=0)
        older["snapshot"]["state"].update(sequence=0, completedOpportunities=0, nativeTick=80)
        older["snapshot"]["actions"] = {}
        older["snapshotSha256"] = collector.digest(older["snapshot"])
        older["backendProof"].update(localSequence=0, nativeTick=80)
        older["backendProof"].pop("proofSha256")
        older["backendProof"]["proofSha256"] = collector.digest(older["backendProof"])
        older["native"]["nativeTick"] = 80
        d["SDK_PAIR_cp0.json"] = older
    run("10_two_pairs_not_reopen_proof", archived_pair, yes2, yes3)

    def rest_ack(d):
        d["http_operations/rest_ack.json"] = {"operationId": "rest_ack", "kind": "action_ack", "status": "ACKNOWLEDGED", "body": {"instanceId": iid, "sessionId": sid}}
    run("11_rest_ack_not_native", rest_ack, yes2, yes3)

    def no_operations(d):
        for key in list(d):
            if key != "INSTANCE.json":
                d.pop(key)
        d["INSTANCE.json"].update(nativeTick=991187, localSequence=0, completedCycles=0)
    run("12_ready_without_native_operations", no_operations, pending2, pending3)

    def material_null_wait(d):
        d["http_operations/op2.json"]["value"].update(action="SAFE_WAIT", null=True)
        receipt = d["SDK_PAIR.json"]["snapshot"]["actions"]["op2"]
        message = json.loads(receipt["rawRequest"])
        message["action"]["name"] = "SAFE_WAIT"
        receipt["rawRequest"] = json.dumps(message)
        result = d["ACTION_ACKS.json"]["op2"]["ack"]["result"]
        result.update(after=[0, 3, 0], deviceAfter=-1, outcome="WAITED", durationMs=100, worldTimeMs=200)
        d["http_operations/feedback.json"]["body"]["payload"].update(result)
        d["SDK_PAIR.json"]["snapshotSha256"] = collector.digest(d["SDK_PAIR.json"]["snapshot"])
    run("13_null_wait_not_zero_exit_or_effect", material_null_wait, yes2, pending3)
    report = {"schema": "DEE.SDK.PassiveCollectorOfflineFixtures.v1", "syntheticOnly": True, "nativeExecuted": False, "sqliteOpened": False, "httpRequested": False, "passed": len(tests), "tests": tests, "collectorSha256": hashlib.sha256(module_path.read_bytes()).hexdigest()}
    write(args.output_dir / "VERIFICACION_OFFLINE.json", report)
    print(json.dumps({"passed": len(tests), "syntheticOnly": True, "nativeExecuted": False}))


if __name__ == "__main__":
    main()
