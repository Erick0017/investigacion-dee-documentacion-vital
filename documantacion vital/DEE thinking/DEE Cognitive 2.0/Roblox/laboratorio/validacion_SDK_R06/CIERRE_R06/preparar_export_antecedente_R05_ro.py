#!/usr/bin/env python3
"""Transferencia documental acotada R05: lectura stdlib, sin Native/SQLite/HTTP."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil


OPS = [
    ("decision", "sdk_decision_b5a351f6-f355-44b0-a56a-899c5cf21032"),
    ("query_sensor", "sdk_query_sensor_d45f69a9-fd70-4e2b-af3b-7a110ab3af16"),
    ("feedback", "sdk_feedback_2157e2ba-9ddf-4695-b061-12ab705e7085"),
]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as out:
        json.dump(value, out, ensure_ascii=False, indent=2, allow_nan=False)
        out.write("\n")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--instance-home", required=True, type=Path)
    p.add_argument("--export-root", required=True, type=Path)
    p.add_argument("--collector", required=True, type=Path)
    p.add_argument("--verifier", required=True, type=Path)
    a = p.parse_args()
    home = a.instance_home.resolve(strict=True)
    root = a.export_root / "ANTECEDENTE_R05"
    root.mkdir(parents=True, exist_ok=False)
    sources, redactions = [], []

    def source(relative):
        path = home / relative
        if path.is_symlink() or not path.resolve(strict=True).is_relative_to(home):
            raise ValueError("Unsafe source")
        raw = path.read_bytes()
        if len(raw) > 2_000_000:
            raise ValueError("Source byte cap")
        entry = {"scope": "PRESERVED_CLOSED_PRIVATE_INSTANCE", "relative": relative, "bytes": len(raw), "sha256": sha(raw)}
        sources.append(entry)
        return json.loads(raw.decode("utf-8-sig")), entry, raw

    def clean(value, locator):
        if isinstance(value, dict):
            result = {}
            for key, item in value.items():
                if re.search(r"token|password|authorization|secret|credential", key, re.I):
                    redactions.append({"locator": locator + "/" + key, "kind": "private_key_name"})
                    result[key] = "[OMITTED_PRIVATE_VALUE]"
                else:
                    result[key] = clean(item, locator + "/" + key)
            return result
        if isinstance(value, list):
            return [clean(item, locator + "/" + str(index)) for index, item in enumerate(value)]
        if isinstance(value, str) and re.search(r"(?<![A-Za-z])[A-Za-z]:[\\/]|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", value):
            redactions.append({"locator": locator, "kind": "absolute_path_or_email"})
            return "[OMITTED_ABSOLUTE_OR_PERSONAL_LOCATOR]"
        return value

    cfg, cfg_source, _ = source("INSTANCE.json")
    config_keys = ("instanceId", "sessionId", "lifeId", "nativeTick", "sequenceOffset", "localSequence", "completedCycles", "nextPhase")
    write(root / "PROTOCOLO_NORMAL" / "INSTANCE.json", {**{key: cfg[key] for key in config_keys}, "_export": {"derived": True, "source": cfg_source, "scope": "HTTP cursor preserved; technical Native R05 may be later"}})
    ack, ack_source, ack_raw = source("ACTION_ACKS.json")
    cleaned_ack = clean(ack, "ACTION_ACKS")
    write(root / "PROTOCOLO_NORMAL" / "ACTION_ACKS.json", cleaned_ack)
    native_receipts = []
    for kind, op in OPS:
        row, provenance, _ = source("ensayos/" + op + ".json")
        payload, execution = json.loads(row["payload"]), json.loads(row["result"])
        outputs = execution["result"]["rows"]
        if len(outputs) != 1:
            raise ValueError("Unexpected Native row count")
        selected_execution = {key: execution[key] for key in ("id", "operation", "before_tick", "after_tick", "host_elapsed_seconds", "started_utc", "finished_execution_utc", "owner_idle_ticks_after", "owner_material_calls_after") if key in execution}
        snapshot = execution.get("committed_snapshot", {})
        item = {"schema": "DEE.SDK.DerivedNativeReceipt.v1", "derived": True, "kind": kind, "source": provenance, "queue": {key: row[key] for key in ("seq", "id", "status", "is_control", "arrived_utc", "started_utc", "finished_utc", "payload_sha")}, "payload": clean(payload, kind + "/payload"), "payloadByteHashMatches": row["payload_sha"] == sha(row["payload"].encode("utf-8")), "execution": selected_execution, "nativeOutput": clean(outputs[0], kind + "/nativeOutput"), "snapshotIdentityOnly": {key: snapshot[key] for key in ("life_id", "snapshot_sha256") if key in snapshot}, "omittedFromOriginal": ["committed_snapshot physical/snapshot/operational_dependencies", "full private life/state serialization"], "scope": "Native queue receipt extract with full phase output and source hash; not the literal full queue JSON or an executable state backup"}
        write(root / "RECIBOS_NATIVE" / (kind + ".json"), item)
        native_receipts.append({"kind": kind, "operationId": op, "before": execution["before_tick"], "after": execution["after_tick"], "ticks": outputs[0]["nativeTicks"], "action": outputs[0].get("action"), "null": outputs[0].get("null"), "accepted": outputs[0].get("accepted"), "appliedCumulative": outputs[0].get("evidence", {}).get("Native_inputs", {}).get("applied")})
        http, http_source, _ = source("http_operations/" + op + ".json")
        http_keys = ("schema", "operationId", "kind", "requestSha256", "status", "body", "nativePayload", "nativeContext", "localSequence", "admittedUtcEpoch", "startedUtcEpoch", "completedUtcEpoch", "failedUtcEpoch", "value")
        http_public = {key: http[key] for key in http_keys if key in http}
        if "error" in http:
            http_public["error"] = {"code": http["error"].get("code"), "messageOmitted": True}
        http_public["_export"] = {"derived": True, "source": http_source, "scope": "Preserved normal HTTP status; no technical R05 completion inserted"}
        write(root / "PROTOCOLO_NORMAL" / "http_operations" / (op + ".json"), clean(http_public, kind + "/http"))
    closure, closure_source, closure_raw = source("RECONCILIACION_FB_R05_B/RESULTADO.json")
    cleaned_closure = clean(closure, "R05/closure")
    write(root / "CIERRE_NATIVE_R05.json", {"schema": "DEE.SDK.ExportedR05Closure.v1", "derived": True, "source": closure_source, "closure": cleaned_closure})
    parent, parent_source, _ = source("VIDA_PADRE_PAR28.json")
    write(root / "GENEALOGIA.json", {"schema": "DEE.SDK.DerivedLineage.v1", "derived": True, "parentSource": parent_source, "parent": {key: parent[key] for key in ("life_id", "profile", "snapshot_sha256") if key in parent}, "parentTick": native_receipts[0]["before"], "diagnostic": {"instanceId": cfg["instanceId"], "sessionId": cfg["sessionId"], "lifeId": cfg["lifeId"], "N": closure["nativeAfter"]["dimension"], "finalNativeTick": closure["nativeAfter"]["nativeTick"], "httpCursorTickPreserved": cfg["nativeTick"]}, "scope": "Diagnostic continuation, not principal selection; parent/child physical states and kernel are excluded"})
    for src, name in ((a.collector, "recalcular_validacion_sdk_R02.py"), (a.verifier, "verificar_export_ro.py")):
        target = root / "CODIGO" / name
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(src, target)
    write(root / "INDICE_R05.json", {"schema": "DEE.SDK.R05BriefExport.v1", "status": "CLOSED_HISTORICAL_ANTECEDENT_NOT_NEW_CIERRE_R06", "nativeReceipts": native_receipts, "tickDelta": native_receipts[-1]["after"] - native_receipts[0]["before"], "nativeOperations": len(native_receipts), "appliedCountersAreCumulative": True, "appliedDistinctFinal": native_receipts[-1]["appliedCumulative"], "doNotSumCumulativeCounters": [x["appliedCumulative"] for x in native_receipts], "sourceFiles": sources, "redactions": redactions, "privateRuntimeKernelLivesIncluded": False, "credentialsIncluded": False, "newNativeExecuted": False, "normalHttpK3": "PENDING_UNCERTAIN_HTTP", "assistedNativeR05": "COMPLETED_CLOSED_NO_Q1_Q2_REPLAY", "K4": "NOT_VALIDATED_NO_SDK_PAIR"})
    readme = """# Antecedente R05 cerrado — export breve\n\nTres recibos Native derivados, ACK y estados HTTP conservados, cierre R05 y genealogía. No son una ejecución nueva de CIERRE_R06.\n\nNative: Q1 ASK_STATION +356; Q2 EXIT_1 +22; retorno del mismo ID +1186. Total 1564 ticks. Los contadores de entradas 6→11→13 son acumulativos: 13 entradas, no 30. No equivalen a conceptos ni réplicas. El feedback HTTP original sigue UNCERTAIN; R05 completó Native mediante conciliación técnica, sin repetir Q1/Q2. No se mezcla ese cierre con un éxito del flujo SDK automático.\n\nLos recibos son EXTRACTOS DERIVADOS con hashes y localizadores de los originales privados; se omiten snapshots completos, dependencias y vidas privadas. Los observables puntuales de Native se conservan como evidencia, no como respaldo operativo. No hay kernel, motor ni credenciales.\n\nEjecute desde esta carpeta: `python -I -B CODIGO/verificar_export_ro.py`. Sólo recálculo de archivos, sin Native/SQLite/HTTP.\n\nAcceso externo elegido: demostración local acompañada por el propietario. El investigador puede revisar el kit público; usar Native exige el equipo y backend privado autorizado del propietario. No se ofrece endpoint público ni uso externo autónomo. Una eventual distribución de runtime binario autorizado queda pendiente de decisión y no forma parte de esta entrega.\n"""
    (root / "LEER_PRIMERO.md").write_text(readme, encoding="utf-8")
    members = [{"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path.read_bytes())} for path in sorted(root.rglob("*")) if path.is_file()]
    write(root / "MANIFIESTO_SHA256.json", {"schema": "DEE.SDK.BriefExportManifest.v1", "members": members, "selfExcluded": True})
    for entry in sources:
        if sha((home / entry["relative"]).read_bytes()) != entry["sha256"]:
            raise ValueError("Selected source changed")
    print(json.dumps({"rootName": root.name, "members": len(members) + 1, "sourceFilesUnchanged": True, "newNativeExecuted": False}))


if __name__ == "__main__":
    main()
