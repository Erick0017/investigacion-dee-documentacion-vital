#!/usr/bin/env python3
"""Recálculo pasivo de JSON atómicos del SDK. Nunca importa DEE, HTTP ni SQLite.

La entrada es una instancia explícita. No consulta al propietario ni modifica la
instancia. Un SDK_PAIR acredita un guardado, no por sí solo una reapertura.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import re
import sys

SCHEMA = "DEE.SDK.PassiveValidation.v1"
NATIVE_KINDS = frozenset({"decision", "query_sensor", "feedback"})
ACTION_KINDS = frozenset({"decision", "query_sensor"})
ALLOWED_ACTIONS = frozenset({"ASK_STATION", "SKIP_STATION", "EXIT_0", "EXIT_1", "SAFE_WAIT"})
MAX_FILE_BYTES = 8_000_000
MAX_TOTAL_BYTES = 64_000_000
MAX_OPERATIONS = 512


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def integer(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def obj(value):
    return value if isinstance(value, dict) else {}


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def reparse(path):
    return path.is_symlink() or bool(getattr(path.lstat(), "st_file_attributes", 0) & 0x400)


def safe_text(value, length=180):
    """Sólo identificadores/códigos acotados; nunca mensajes arbitrarios de error."""
    return value[:length] if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_./ -]{1,180}", value) else None


def project(value, keys):
    return {key: value[key] for key in keys if key in value}


def pose(value):
    if isinstance(value, list) and len(value) in (3, 12) and all(number(x) for x in value):
        return value
    return None


def effect(result):
    result = obj(result)
    before, after = pose(result.get("before")), pose(result.get("after"))
    moved = bool(before and after and any(abs(before[i] - after[i]) > 1e-8 for i in range(3)))
    device_before, device_after = result.get("deviceBefore"), result.get("deviceAfter")
    device_changed = (number(device_before) and number(device_after) and device_before != device_after)
    return {
        "before": before, "after": after, "positionChanged": moved,
        "deviceBefore": device_before if number(device_before) else None,
        "deviceAfter": device_after if number(device_after) else None,
        "deviceChanged": device_changed,
        "deviceActuation": project(obj(result.get("deviceActuation")), ("port", "value", "actualCanCollide", "semantic_choice_in_motor", "prepared_fixed_actuator")),
        "resourceCollected": result.get("resourceCollected") is True,
        "resourceDelivered": result.get("resourceDelivered") is True,
        "collision": result.get("collision") is True,
        "invalidAction": result.get("invalidAction") is True,
        "outcome": safe_text(result.get("outcome")),
        "permissionSpent": result.get("permissionSpent") if number(result.get("permissionSpent")) else None,
        "durationMs": result.get("durationMs") if number(result.get("durationMs")) else None,
        "motor": project(obj(result.get("motor")), ("status", "waypoints", "durationMs", "elapsedSeconds", "recomputes")),
        "observableEffectRecorded": moved or device_changed or result.get("resourceCollected") is True or result.get("resourceDelivered") is True,
    }


def selected_files(home):
    fixed = ["INSTANCE.json", "ACTION_ACKS.json", "BACKEND_CLOSED.json", "SDK_PAIR.json"]
    selected = [home / name for name in fixed if (home / name).is_file()]
    selected += sorted(home.glob("SDK_PAIR_*.json"))
    store = home / "http_operations"
    if store.exists():
        if reparse(store) or not store.is_dir():
            raise ValueError("Operation store must be a real directory")
        operations = sorted(store.glob("*.json"))
        if len(operations) > MAX_OPERATIONS:
            raise ValueError("Finite operation file cap exceeded")
        selected += operations
    if home / "INSTANCE.json" not in selected:
        raise ValueError("Explicit instance lacks INSTANCE.json")
    return sorted(set(selected))


def collect(home):
    supplied = Path(home).absolute()
    if any(reparse(p) for p in (supplied, *supplied.parents)):
        raise ValueError("Symbolic/reparse traversal is not admitted")
    home = supplied.resolve(strict=True)
    if not home.is_dir():
        raise ValueError("--instance-home must name a directory")
    files = selected_files(home)
    documents, sources, errors = {}, [], []
    total = 0
    for path in files:
        if reparse(path) or not path.resolve(strict=True).is_relative_to(home):
            raise ValueError("Source escaped explicit instance")
        if path.stat().st_size > MAX_FILE_BYTES:
            raise ValueError("Finite JSON file cap exceeded before read")
        raw = path.read_bytes()
        total += len(raw)
        if len(raw) > MAX_FILE_BYTES or total > MAX_TOTAL_BYTES:
            raise ValueError("Finite JSON byte cap exceeded")
        relative = path.relative_to(home).as_posix()
        sources.append({"path": relative, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
        try:
            value = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=no_duplicate_keys, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Nonfinite JSON")))
            if not isinstance(value, dict):
                raise ValueError("Expected JSON object")
            documents[relative] = value
        except (ValueError, UnicodeError):
            errors.append({"code": "INVALID_JSON_OBJECT", "path": relative})
    cfg = documents.get("INSTANCE.json", {})
    identity = project(cfg, ("instanceId", "sessionId", "lifeId", "nativeTick", "sequenceOffset", "localSequence", "completedCycles", "nextPhase"))
    sid, instance_id, life = cfg.get("sessionId"), cfg.get("instanceId"), cfg.get("lifeId")
    if not all(isinstance(x, str) and x for x in (sid, instance_id, life)):
        errors.append({"code": "INSTANCE_IDENTITY_MISSING"})

    pairs, receipts = [], {}
    for relative, pair in documents.items():
        if not (relative == "SDK_PAIR.json" or (relative.startswith("SDK_PAIR_") and "/" not in relative)):
            continue
        snapshot, proof = obj(pair.get("snapshot")), obj(pair.get("backendProof"))
        state, native = obj(snapshot.get("state")), obj(pair.get("native"))
        proof_copy = dict(proof)
        proof_hash = proof_copy.pop("proofSha256", None)
        checks = {
            "snapshotDigest": pair.get("snapshotSha256") == digest(snapshot),
            "closedProofDigest": isinstance(proof_hash, str) and proof_hash == digest(proof_copy),
            "instanceIdentity": pair.get("instanceId") == instance_id and pair.get("sessionId") == sid,
            "lifeAndSession": state.get("lifeId") == life and state.get("sessionId") == sid and proof.get("lifeId") == life and proof.get("sessionId") == sid,
            "nativeTick": integer(state.get("nativeTick")) and state.get("nativeTick") == proof.get("nativeTick") == native.get("nativeTick"),
            "cursor": integer(pair.get("localSequence")) and pair.get("localSequence") == state.get("sequence") == proof.get("localSequence"),
            "closedBoundary": state.get("phase") == "BOUNDARY" and state.get("pendingActionId") is None and proof.get("backendWriterClosed") is True and proof.get("bridgeQuiescent") is True,
        }
        valid = all(checks.values())
        pairs.append({"path": relative, "checkpointId": safe_text(pair.get("checkpointId")), "snapshotSha256": pair.get("snapshotSha256"), "nativeTick": state.get("nativeTick"), "localSequence": pair.get("localSequence"), "completedOpportunities": state.get("completedOpportunities"), "checks": checks, "validRecordedPair": valid})
        if valid:
            for action_id, receipt in obj(snapshot.get("actions")).items():
                receipts.setdefault(action_id, []).append((relative, obj(receipt)))

    operations, by_id = [], {}
    for relative, row in documents.items():
        if not relative.startswith("http_operations/"):
            continue
        op = row.get("operationId")
        if not isinstance(op, str) or not op:
            errors.append({"code": "MISSING_OPERATION_ID", "path": relative})
            continue
        if op in by_id:
            errors.append({"code": "DUPLICATE_OPERATION_ID", "path": relative, "operationId": op})
            continue
        by_id[op] = row
        body, context, value = obj(row.get("body")), obj(row.get("nativeContext")), obj(row.get("value"))
        kind = row.get("kind")
        native_context_valid = (context.get("mode") == "LIVE_NATIVE" and context.get("operation_id") == op and context.get("session_id") == sid)
        identity_valid = body.get("instanceId") == instance_id and body.get("sessionId") == sid
        tick_value = value.get("nativeTick") if kind != "close" else obj(value.get("backendProof")).get("nativeTick")
        item = {"path": relative, "operationId": op, "kind": safe_text(kind), "status": safe_text(row.get("status")), "instanceAndSessionMatch": identity_valid, "nativeContextValid": native_context_valid, "localSequence": row.get("localSequence"), "nativeSequence": context.get("sequence"), "observationId": safe_text(context.get("observation_id")), "nativeTick": tick_value if integer(tick_value) else None, "action": value.get("action") if value.get("action") in ALLOWED_ACTIONS else None, "null": value.get("null") if isinstance(value.get("null"), bool) else None, "accepted": value.get("accepted") is True, "errorCode": safe_text(obj(row.get("error")).get("code"))}
        item["completedRecordedNative"] = kind in NATIVE_KINDS and row.get("status") == "COMPLETED" and identity_valid and native_context_valid and item["nativeTick"] is not None
        operations.append(item)

    acknowledgments = obj(documents.get("ACTION_ACKS.json"))
    actions = []
    committed_chains = []
    for op, row in by_id.items():
        if row.get("kind") not in ACTION_KINDS:
            continue
        summary = next(x for x in operations if x["operationId"] == op)
        envelope = obj(acknowledgments.get(op))
        ack, value, context = obj(envelope.get("ack")), obj(row.get("value")), obj(row.get("nativeContext"))
        checks = {
            "completedNativeAction": summary["completedRecordedNative"] and summary["action"] is not None,
            "ackEnvelopeIdentity": envelope.get("instanceId") == instance_id and envelope.get("sessionId") == sid and envelope.get("actionId") == op,
            "ackIdentityAndCursor": ack.get("protocol") == "DEE.RBX.Connector.R01" and ack.get("sessionId") == sid and ack.get("actionId") == op and ack.get("operationId") == op and ack.get("observationId") == context.get("observation_id") == envelope.get("observationId") and ack.get("seq") == row.get("localSequence") == envelope.get("localSequence"),
            "executedNontechnicalAck": ack.get("executionStatus") == "EXECUTED" and ack.get("technicalControl") is False and isinstance(ack.get("result"), dict),
        }
        matches = []
        for relative, receipt in receipts.get(op, []):
            raw_request = receipt.get("rawRequest")
            try:
                message = json.loads(raw_request) if isinstance(raw_request, str) else {}
            except ValueError:
                message = {}
            exact = receipt.get("status") == "COMMITTED" and receipt.get("operationId") == op and receipt.get("technical") is False and receipt.get("ack") == ack and obj(message).get("sourceKind") == "DEE_NATIVE" and obj(message).get("operationId") == op and obj(obj(message).get("action")).get("name") == value.get("action")
            if exact:
                matches.append(relative)
        feedback = []
        for fb_op, fb_row in by_id.items():
            payload = obj(obj(fb_row.get("body")).get("payload"))
            fb_value, fb_context = obj(fb_row.get("value")), obj(fb_row.get("nativeContext"))
            feedback_body = obj(fb_row.get("body"))
            result = obj(ack.get("result"))
            effect_matches = all(key in payload and key in result and payload[key] == result[key] for key in ("outcome", "collision", "resourceCollected", "resourceDelivered", "materialConsequence", "durationMs", "worldTimeMs"))
            if fb_row.get("kind") == "feedback" and fb_row.get("status") == "COMPLETED" and feedback_body.get("instanceId") == instance_id and feedback_body.get("sessionId") == sid and payload.get("actionId") == op and payload.get("observationId") == ack.get("observationId") and payload.get("seq") == ack.get("seq") == fb_row.get("localSequence") and fb_value.get("accepted") is True and integer(fb_value.get("nativeTick")) and fb_context.get("mode") == "LIVE_NATIVE" and fb_context.get("session_id") == sid and fb_context.get("operation_id") == fb_op and effect_matches:
                feedback.append(fb_op)
        checks["committedReceiptInValidPair"] = bool(matches)
        checks["acceptedCorrelatedFeedback"] = len(feedback) == 1
        physical = effect(ack.get("result"))
        item = {"operationId": op, "action": summary["action"], "null": summary["null"], "checks": checks, "feedbackOperationIds": feedback, "committedPairPaths": matches, "effect": physical, "durableActionReceipts": 1 if receipts.get(op) else 0, "exactlyOnceScope": "One logical action ID/receipt under the connector idempotency contract; not independent measurement of every physical application"}
        actions.append(item)
        if all(checks.values()):
            committed_chains.append(item)

    stable = []
    for source in sources:
        path = home / source["path"]
        try:
            same = hashlib.sha256(path.read_bytes()).hexdigest() == source["sha256"]
        except OSError:
            same = False
        if not same:
            stable.append(source["path"])
    if [p.relative_to(home).as_posix() for p in selected_files(home)] != [s["path"] for s in sources]:
        stable.append("SELECTED_FILE_SET")
    if stable:
        errors.append({"code": "CONCURRENT_SOURCE_CHANGE", "paths": stable})
    can_conclude = not errors
    k2_ids = [x["operationId"] for x in committed_chains] if can_conclude else []
    k3_ids = [x["operationId"] for x in committed_chains if x["effect"]["observableEffectRecorded"]] if can_conclude else []
    historical_pair_progress = sorted((x for x in pairs if x["validRecordedPair"]), key=lambda x: x["localSequence"])
    return {
        "schema": SCHEMA, "inspectionUtc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "mode": "PASSIVE_JSON_RECALCULATION_NOT_NATIVE_REPRODUCTION", "identity": identity,
        "nativeExecutedByCollector": False, "sqliteOpened": False, "httpRequested": False, "instanceModified": False,
        "selectedSourceCount": len(sources), "selectedBytes": total, "sources": sources,
        "sourceStability": "NO_SELECTED_CONTENT_CHANGE_DETECTED" if not stable else "CHANGED_DURING_READ",
        "operationCounts": {"uniqueNativeMaterialOperationIds": sum(x["kind"] in NATIVE_KINDS for x in operations), "completedRecordedNative": sum(x["completedRecordedNative"] for x in operations), "closeOperationIds": sum(x["kind"] == "close" for x in operations), "otherStoredOperationIds": sum(x["kind"] not in NATIVE_KINDS | {"close"} for x in operations), "ackEnvelopeIds": len(acknowledgments)},
        "operations": operations, "actions": actions, "pairs": pairs, "issues": errors,
        "K2": {"status": "DOCUMENTED_LOCAL_CHAIN" if k2_ids else "PENDING_COMMITTED_CHAIN_EVIDENCE", "qualifyingOperationIds": k2_ids, "scope": "Atomic service records identify completed Native output, exact execution ACK, accepted feedback and committed receipt in a valid closed pair; independent engine provenance remains in original private primaries"},
        "K3": {"status": "DOCUMENTED_LOCAL_EFFECT_AND_RETURN" if k3_ids else "PENDING_COMMITTED_EFFECT_AND_RETURN", "qualifyingOperationIds": k3_ids, "scope": "Recorded positions/device/resource effect and correlated feedback; no inference of learning from movement"},
        "K4": {"status": "PENDING_DIRECT_REOPEN_AND_POST_USE_EVIDENCE", "savedPairRecorded": bool(historical_pair_progress), "validPairCount": len(historical_pair_progress), "serializedCursorProgress": len(historical_pair_progress) >= 2 and historical_pair_progress[-1]["localSequence"] > historical_pair_progress[0]["localSequence"], "reason": "SDK_PAIR proves serialized coupled save only. Two saved pairs do not alone prove an actual restore comparison and subsequent use. No new proof schema is invented by this collector."},
        "countingRules": ["REST GET polling is not a Native event and is not counted.", "ACK HTTP registrations are not additional Native events.", "Close is reported separately from decision/query_sensor/feedback.", "Repeated receipts in SDK_PAIR archives are aliases of the same operation ID.", "Zero material value and null remain distinct; null is never repaired into an action.", "Historical footage is not a new SDK episode and is not read or counted."],
        "limits": ["Reads only selected atomic JSON files in the explicit instance; no private connection/configuration, tokens, logs, databases, engine or owner.", "A stable selected-file read is not a coherent live-world snapshot guarantee; concurrent changes invalidate automatic conclusions.", "This is documentary recalculation, not Native execution, external evaluation, learned autonomy or certification of every physical application.", "K1 and K5 are outside this collector. K4 requires direct additional evidence and stays pending here."],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance-home", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path, help="New report outside instance; existing file refused")
    args = parser.parse_args()
    home = args.instance_home.resolve(strict=True)
    target = args.output.absolute()
    parent = target.parent.resolve(strict=True)
    if parent.is_relative_to(home) or target.exists() or target.is_symlink():
        parser.error("Output must be a new file outside the read-only instance")
    report = collect(args.instance_home)
    with target.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"schema": SCHEMA, "outputName": target.name, "K2": report["K2"]["status"], "K3": report["K3"]["status"], "K4": report["K4"]["status"], "issues": len(report["issues"]), "nativeExecuted": False}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError):
        print("SDK_PASSIVE_COLLECTOR_FAILED_PRESERVED: invalid input, limits or file condition; no Native or source writes", file=sys.stderr)
        raise SystemExit(2)
