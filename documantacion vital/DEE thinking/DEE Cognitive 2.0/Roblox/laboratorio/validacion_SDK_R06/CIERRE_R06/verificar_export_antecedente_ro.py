#!/usr/bin/env python3
"""Recálculo portable del export R05; no Native, SQLite, HTTP ni acceso a originales."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


def read(path):
    return json.loads(path.read_text("utf-8"))


def main():
    sys.dont_write_bytecode = True
    root = Path(__file__).resolve().parents[1]
    manifest = read(root / "MANIFIESTO_SHA256.json")
    for member in manifest["members"]:
        path = root / member["path"]
        assert not path.is_symlink() and path.resolve().is_relative_to(root)
        raw = path.read_bytes()
        assert len(raw) == member["bytes"] and hashlib.sha256(raw).hexdigest() == member["sha256"]
    receipts = [read(root / "RECIBOS_NATIVE" / (kind + ".json")) for kind in ("decision", "query_sensor", "feedback")]
    ids = [x["queue"]["id"] for x in receipts]
    assert len(set(ids)) == 3
    assert all(x["queue"]["status"] == "completed" for x in receipts)
    assert all(x["payloadByteHashMatches"] for x in receipts)
    assert receipts[0]["execution"]["before_tick"] == 991187
    assert [x["nativeOutput"]["nativeTicks"] for x in receipts] == [356, 22, 1186]
    assert [x["nativeOutput"]["nativeTick"] for x in receipts] == [991543, 991565, 992751]
    assert [x["nativeOutput"]["action"] for x in receipts[:2]] == ["ASK_STATION", "EXIT_1"]
    assert all(x["nativeOutput"]["null"] is False for x in receipts)
    assert receipts[2]["nativeOutput"]["accepted"] is True
    assert all(receipts[i]["execution"]["after_tick"] == receipts[i + 1]["execution"]["before_tick"] for i in range(2))
    cumulative = [x["nativeOutput"]["evidence"]["Native_inputs"]["applied"] for x in receipts]
    assert cumulative == [6, 11, 13]
    closure = read(root / "CIERRE_NATIVE_R05.json")["closure"]
    assert closure["ownerClosed"] is True and closure["Q1Q2replayed"] is False
    assert closure["originalOperationId"] == ids[-1] and closure["originalHttpRowPreserved"] is True
    assert closure["nativeAfter"]["pending"] == 0 and closure["nativeAfter"]["nativeTick"] == 992751
    module_path = Path(__file__).with_name("recalcular_validacion_sdk_R02.py")
    spec = importlib.util.spec_from_file_location("sdk_export_collector", module_path)
    collector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(collector)
    normal = collector.collect(root / "PROTOCOLO_NORMAL")
    assert normal["K2"]["status"] == "DOCUMENTED_NATIVE_RESPONSE_AND_EXECUTION_ACK"
    assert len(normal["K2"]["qualifyingOperationIds"]) == 2
    assert normal["K3"]["status"] == "PENDING_COMMITTED_EFFECT_AND_RETURN"
    assert normal["K4"]["status"] == "PENDING_DIRECT_REOPEN_AND_POST_USE_EVIDENCE"
    print(json.dumps({"schema": "DEE.SDK.PortableBriefRecalculation.v1", "membersVerified": len(manifest["members"]), "nativeReceipts": 3, "nativeTicksHistorical": 1564, "distinctAppliedInputCounter": cumulative[-1], "cumulativeCountersNotSummed": cumulative, "normalK2Responses": 2, "normalHttpK3": "PENDING", "assistedR05Native": "CLOSED", "K4": "NOT_VALIDATED", "NativeExecutedNow": False, "sqliteOpened": False, "httpRequested": False}))


if __name__ == "__main__":
    main()
