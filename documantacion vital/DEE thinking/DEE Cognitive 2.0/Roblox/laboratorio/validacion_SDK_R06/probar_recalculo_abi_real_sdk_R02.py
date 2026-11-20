#!/usr/bin/env python3
"""Fixture anónimo del DTO HTTP cerrado real; cero Native, SQLite o HTTP."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re


def read(path):
    return json.loads(path.read_text("utf-8-sig"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as out:
        json.dump(value, out, ensure_ascii=False, indent=2)
        out.write("\n")


def shape(value):
    if isinstance(value, dict):
        return {key: shape(item) for key, item in value.items()}
    if isinstance(value, list):
        return [shape(item) for item in value]
    return type(value).__name__


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--instance-home", required=True, type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
    a = p.parse_args()
    home = a.instance_home.resolve(strict=True)
    a.output_dir.mkdir(exist_ok=False)
    src = Path(__file__).with_name("recalcular_validacion_sdk_R02.py")
    compile(src.read_text("utf-8"), str(src), "exec")
    spec = importlib.util.spec_from_file_location("sdk_passive_r02_fixture", src)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cfg = read(home / "INSTANCE.json")
    source_rows = [read(path) for path in sorted((home / "http_operations").glob("*.json"))]
    acks = read(home / "ACTION_ACKS.json")
    replacement = {cfg["instanceId"]: "SDK_DEMO_00000000000000A2", cfg["sessionId"]: "SDK_SESSION_FIXTURE_R02", cfg["lifeId"]: "SDK_FIXTURE_DIAGNOSTIC_N67"}
    for index, row in enumerate(source_rows):
        replacement[row["operationId"]] = f"fixture_op_{index}"
        context = row.get("nativeContext", {})
        if isinstance(context.get("observation_id"), str):
            replacement.setdefault(context["observation_id"], f"fixture_obs_{index}")
    allowed = {"DEE.RBX.Connector.R01", "LIVE_NATIVE", "COMPLETED", "CANCELLED_PRE_NATIVE", "UNCERTAIN", "EXECUTED", "ACKNOWLEDGED", "COMMITTED", "decision", "query_sensor", "feedback", "close", "ASK_STATION", "SKIP_STATION", "EXIT_0", "EXIT_1", "SAFE_WAIT", "PANEL_OBSERVED", "MOVED", "WAITED", "ARRIVED", "BOUNDARY", "PRESERVED_NO_REPLAY", "WINDOWS_ATOMIC_RENAME_PRE_SUBMIT"}

    def anonymous(value):
        if isinstance(value, dict):
            return {replacement.get(key, key): ("" if re.search("token|password|authorization|secret", key, re.I) else anonymous(item)) for key, item in value.items()}
        if isinstance(value, list):
            return [anonymous(item) for item in value]
        if isinstance(value, str):
            return replacement.get(value, value if value in allowed else "ANONYMIZED_STRING")
        return value

    base = {"INSTANCE.json": anonymous({key: cfg[key] for key in ("instanceId", "sessionId", "lifeId", "nativeTick", "sequenceOffset", "localSequence", "completedCycles", "nextPhase")}), "ACTION_ACKS.json": anonymous(acks)}
    dto_shapes = []
    for row in source_rows:
        sanitized = anonymous(row)
        assert shape(row) == shape(sanitized), "DTO field/type shape changed"
        base["http_operations/" + sanitized["operationId"] + ".json"] = sanitized
        dto_shapes.append({"kind": row["kind"], "status": row["status"], "valueShape": shape(row.get("value", {})), "formedPresent": "formed" in row.get("value", {}), "acceptedPresent": "accepted" in row.get("value", {})})

    expected2 = "DOCUMENTED_NATIVE_RESPONSE_AND_EXECUTION_ACK"
    pending2 = "PENDING_NATIVE_RESPONSE_AND_EXECUTION_ACK"
    expected3 = "PENDING_COMMITTED_EFFECT_AND_RETURN"
    tests = []

    def run(name, mutation, status, response_count):
        docs = copy.deepcopy(base)
        mutation(docs)
        directory = a.output_dir / name
        directory.mkdir()
        for relative, value in docs.items():
            write(directory / relative, value)
        before = {str(x.relative_to(directory)): hashlib.sha256(x.read_bytes()).hexdigest() for x in directory.rglob("*.json")}
        report = module.collect(directory)
        assert report["K2"]["status"] == status
        assert len(report["K2"]["qualifyingOperationIds"]) == response_count
        assert report["K3"]["status"] == expected3
        assert report["K4"]["status"] == "PENDING_DIRECT_REOPEN_AND_POST_USE_EVIDENCE"
        assert not report["issues"], report["issues"]
        after = {str(x.relative_to(directory)): hashlib.sha256(x.read_bytes()).hexdigest() for x in directory.rglob("*.json")}
        assert before == after
        write(a.output_dir / (name + "_REPORT.json"), report)
        tests.append({"name": name, "passed": True, "K2": status, "K2Responses": response_count, "K3": expected3, "K4Pending": True, "sourcesUnchanged": True})
        return report

    real = run("01_exact_real_dto_anonymized", lambda d: None, expected2, 2)
    assert real["operationCounts"]["uniqueStoredNativeKindOperationIds"] == 4
    assert real["operationCounts"]["completedRecordedNative"] == 2
    assert real["operationCounts"]["cancelledBeforeNative"] == 1
    assert real["operationCounts"]["uncertainNotCountedAsCompleted"] == 1
    run("02_no_ack_pending", lambda d: d.update({"ACTION_ACKS.json": {}}), pending2, 0)
    run("03_wrong_ack_sessions_pending", lambda d: [value["ack"].update(sessionId="OTHER_SESSION") for value in d["ACTION_ACKS.json"].values()], pending2, 0)

    def all_incomplete(d):
        for path, row in d.items():
            if path.startswith("http_operations/") and row.get("status") == "COMPLETED":
                row["status"] = "UNCERTAIN"
    run("04_incomplete_outputs_pending", all_incomplete, pending2, 0)
    run("05_missing_one_ack_keeps_one_response", lambda d: d["ACTION_ACKS.json"].pop(next(iter(d["ACTION_ACKS.json"]))), expected2, 1)

    def wrong_source(d):
        for path, row in d.items():
            if path.startswith("http_operations/"):
                row.get("nativeContext", {})["mode"] = "NOT_NATIVE"
    run("06_non_native_context_pending", wrong_source, pending2, 0)
    result = {"schema": "DEE.SDK.ExactRealDtoFixtureCheck.v1", "passed": len(tests), "tests": tests, "actualDtoFieldAndTypeShapes": dto_shapes, "actualInstanceReadOnly": True, "sourceInstanceIdentityPublished": False, "privateStringValuesAnonymized": True, "nativeExecuted": False, "sqliteOpened": False, "httpRequested": False, "collectorSha256": hashlib.sha256(src.read_bytes()).hexdigest(), "interpretation": "K2 is independent from feedback/COMMITTED/SDK_PAIR. Normal K3 stays pending for original HTTP UNCERTAIN. Separate Native R05 closure is not merged into this HTTP fixture."}
    write(a.output_dir / "VERIFICACION_ABI_REAL_R02.json", result)
    print(json.dumps({"passed": len(tests), "nativeExecuted": False, "K2": expected2, "K3Normal": expected3, "privateValuesAnonymized": True}))


if __name__ == "__main__":
    main()
