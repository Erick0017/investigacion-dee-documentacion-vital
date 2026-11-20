"""Closed-boundary DEE/Roblox checkpoint package. Stdlib, never imports Native.

This binds an existing official complete-service export to a full world JSON
checkpoint and a closed bridge database. It neither advances a world nor fixes
an uncertain action. Native reopening and Luau apply must be tested separately.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import shutil
import sqlite3
import stat

SCHEMA = "DEE.RBX01.C02.joint_checkpoint.v1"
WORLD_SCHEMA = "DEE.RBX01.C02.world_checkpoint.v1"
ROOT = Path(__file__).resolve().parents[1]
MAX_MEMBERS = 30000
MAX_BYTES = 4 * 1024**3
PROTECTED = "ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def sha(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def read(path):
    return json.loads(Path(path).read_text("utf-8-sig"))


def relative(name):
    need(isinstance(name, str) and name and "\\" not in name and ":" not in name,
         "Portable relative member required")
    p = PurePosixPath(name)
    need(not p.is_absolute() and all(t not in ("", ".", "..") for t in p.parts),
         "Unsafe checkpoint member")
    return p


def safe(path, root=ROOT, *, exists=True):
    path, root = Path(path).absolute(), Path(root).resolve(strict=True)
    for item in (path, *path.parents):
        try:
            info = item.lstat()
        except FileNotFoundError:
            continue
        need(not stat.S_ISLNK(info.st_mode) and not
             (getattr(info, "st_file_attributes", 0) & 1024),
             "Linked/reparse checkpoint path refused")
    result = path.resolve(strict=exists)
    need(result.is_relative_to(root), "Checkpoint path outside campaign")
    return result


def finite_json(value, depth=0):
    need(depth <= 40, "World state nesting limit")
    if value is None or isinstance(value, (str, bool)):
        return
    if type(value) in (int, float):
        need(math.isfinite(value), "Non-finite world number")
        return
    if isinstance(value, list):
        need(len(value) <= 100000, "World array limit")
        for item in value:
            finite_json(item, depth + 1)
        return
    need(isinstance(value, dict), "World checkpoint must be JSON data")
    need(len(value) <= 100000 and all(isinstance(k, str) for k in value),
         "World object keys/limit")
    for item in value.values():
        finite_json(item, depth + 1)


def validate_world(value):
    finite_json(value)
    need(value.get("schema") == WORLD_SCHEMA, "Full C02 world checkpoint required")
    need(isinstance(value.get("checkpoint_id"), str) and value["checkpoint_id"],
         "Explicit checkpoint id required")
    need(isinstance(value.get("world_id"), str) and value["world_id"], "World id required")
    need(isinstance(value.get("scenario_sha256"), str) and
         len(value["scenario_sha256"]) == 64 and
         all(c in "0123456789abcdef" for c in value["scenario_sha256"]),
         "Frozen scenario fingerprint required")
    life = value.get("native_life_id")
    need(isinstance(life, str) and "_RBX01_" in life and life != PROTECTED,
         "Only explicit RBX descendants may be paired")
    tick = value.get("native_tick")
    need(type(tick) is int and tick >= 0, "Exact Native tick required")
    boundary = value.get("boundary", {})
    need(boundary.get("phase") == "BOUNDARY" and
         boundary.get("native_phase") == "IDLE", "Only a fully settled opportunity boundary")
    complete = boundary.get("completed_opportunities")
    next_opportunity = boundary.get("next_opportunity")
    need(type(complete) is int and complete >= 0 and
         type(next_opportunity) is int and next_opportunity == complete + 1,
         "Opportunity cursor must continue, not restart")
    need(boundary.get("pending_action") is None and
         boundary.get("pending_operation") is None and
         boundary.get("uncertain") is False,
         "Pending/uncertain actions cannot be checkpointed as settled")
    if complete:
        action = boundary.get("last_action_id")
        need(isinstance(action, str) and action and
             boundary.get("acknowledged_action_id") == action,
             "Last action must have the exact execution ACK")
        need(isinstance(boundary.get("last_feedback_operation_id"), str) and
             boundary["last_feedback_operation_id"], "Last feedback receipt required")
    state = value.get("S")
    need(isinstance(state, dict) and state.get("nativeTick") == tick,
         "World S must carry the matching Native tick")
    need(state.get("completedCycles") == complete and state.get("cycle") == complete,
         "World cycle counters disagree with boundary")
    need(type(state.get("worldTime")) in (int, float) and state["worldTime"] >= 0,
         "World logical clock required")
    pose = value.get("body_pose")
    need(isinstance(pose, list) and len(pose) == 12 and
         all(type(v) in (int, float) and math.isfinite(v) for v in pose),
         "Full body CFrame required")
    need(isinstance(value.get("executed_actions"), dict), "Action deduplication state required")
    need(all(v in ("EXECUTED", "ACKNOWLEDGED") for v in value["executed_actions"].values()),
         "An executing/failed action requires reconciliation, not restore")
    if complete:
        need(value["executed_actions"].get(boundary["last_action_id"]) in
             ("EXECUTED", "ACKNOWLEDGED"), "Last action not preserved in dedup state")
    need(isinstance(value.get("events"), list), "Complete event prefix required")
    need(isinstance(value.get("physical"), dict) and
         isinstance(value["physical"].get("parts"), list), "Physical part state required")
    part_names = [p.get("path") for p in value["physical"]["parts"]]
    need(len(part_names) == len(set(part_names)) and all(isinstance(x, str) and x for x in part_names),
         "Duplicate or missing physical paths")
    need(isinstance(value.get("rng"), dict) and value["rng"].get("algorithm") in
         ("NONE", "C02_LCG32_V1", "PREDECLARED_EVENT_TABLE_V1"),
         "Explicit restorable RNG or immutable exogenous event table required")
    need(isinstance(value.get("controller"), dict) and
         isinstance(value.get("bridge"), dict), "Controller/bridge progress required")
    bridge = value["bridge"]
    need(isinstance(bridge.get("session_id"), str) and bridge["session_id"] and
         isinstance(bridge.get("server_id"), str) and bridge["server_id"],
         "Preserved logical session/server identities required")
    need(bridge.get("pending_count") == 0 and bridge.get("uncertain_count") == 0,
         "Bridge must be quiescent")
    need(bridge.get("phase") in ("READY", "READY_QUERY", "BOUNDARY", "STOPPED"),
         "Bridge not at an admitted boundary")
    return {"life": life, "tick": tick, "completed": complete,
            "next_opportunity": next_opportunity,
            "world_time": state["worldTime"], "checkpoint_id": value["checkpoint_id"]}


def compare_world_semantics(before, after, *, geometry_tolerance=1e-5):
    """Compare a save/apply/capture roundtrip without confusing transport UI.

    Geometry tolerance is declared before the material test. Gameplay scalar
    values, zero/absence, inventory, IDs, cursor, RNG and event prefix are exact.
    Only S.mode/reason/latency and close_requested are technical/UI exceptions.
    """
    validate_world(before); validate_world(after)
    need(type(geometry_tolerance) in (int, float) and 0 <= geometry_tolerance <= 1e-4,
         "Finite predeclared geometry tolerance required")
    ignored = {"S.mode", "S.reason", "S.latency", "close_requested", "observer.segment"}
    tolerant_keys = {"body_pose", "cframe", "size", "color", "transparency",
                     "linearVelocity", "angularVelocity", "pivotOffset", "customPhysicalProperties"}
    packed_geometry = {"Vector3", "Color3", "CFrame", "UDim", "UDim2", "NumberRange"}
    differences = []
    def visit(a, b, path="", tolerant=False):
        if path in ignored:
            return
        if type(a) in (int, float) and type(b) in (int, float):
            equal = abs(a-b) <= geometry_tolerance if tolerant else a == b
            if not equal: differences.append({"path":path,"before":a,"after":b})
            return
        if isinstance(a, dict) and isinstance(b, dict):
            keys = set(a) | set(b)
            for key in sorted(keys):
                child = key if not path else path+"."+key
                if child in ignored:continue
                if key not in a or key not in b:
                    differences.append({"path":child,"kind":"missing_key"});continue
                typed = key == "v" and a.get("_type") in packed_geometry and a.get("_type") == b.get("_type")
                visit(a[key], b[key], child, tolerant or key in tolerant_keys or typed)
            return
        if isinstance(a, list) and isinstance(b, list):
            if len(a) != len(b):
                differences.append({"path":path,"kind":"array_length"});return
            for index,(left,right) in enumerate(zip(a,b)):visit(left,right,path+"["+str(index)+"]",tolerant)
            return
        if type(a) is not type(b) or a != b:
            differences.append({"path":path,"before":a,"after":b})
    visit(before, after)
    return {"scope":"World JSON roundtrip only; Native physical hashes must be verified separately.",
            "equal_with_declared_geometry_tolerance":not differences,
            "geometry_absolute_tolerance":geometry_tolerance,
            "ignored_technical_UI_paths":sorted(ignored),"differences":differences,
            "Native_imports":0,"MCP_calls":0,"new_native_ticks":0}


def check_close(proof, life):
    detail = proof.get("closure_proof", proof)
    need(detail.get("lifeId", detail.get("life_id")) == life,
         "Closed-owner proof belongs to another life")
    need(detail.get("ownerClosed", proof.get("owner_closed")) is True and
         detail.get("writerDrained", proof.get("writer_drained")) is True,
         "Owner and material writer must both have closed")
    need(proof.get("owner_returncode", 0) == 0 and
         proof.get("reconciliation_required", False) is False,
         "Nonzero/uncertain owner close cannot form a settled checkpoint")
    child = proof.get("owned_child_close_evidence")
    if child is not None:
        status = child.get("final_status", {})
        need(child.get("exit_code") == 0 and status.get("running") is False and
             status.get("uncertain_external_result") is False,
             "Child-owner proof is not cleanly closed and certain")


def check_sqlite(path, *, bridge=False, known_export_id=None):
    path = Path(path)
    for suffix in ("-wal", "-shm"):
        extra = Path(str(path) + suffix)
        need(not extra.exists() or extra.stat().st_size == 0,
             "SQLite sidecar present: close/checkpoint through its owner first")
    con = sqlite3.connect(path.resolve().as_uri() + "?mode=ro&immutable=1", uri=True)
    con.row_factory = sqlite3.Row
    try:
        need(con.execute("PRAGMA integrity_check").fetchone()[0] == "ok", "SQLite integrity failure")
        tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if bridge:
            need({"session", "operation"} <= tables, "Bridge database schema missing")
            statuses = {r[0] for r in con.execute("SELECT DISTINCT status FROM operation")}
            need(statuses <= {"QUEUED", "RUNNING", "UNCERTAIN", "COMPLETED", "FAILED_PRESERVED", "REJECTED_INVALID"},
                 "Unrecognized bridge operation status")
            pending = list(con.execute("SELECT * FROM operation WHERE status IN ('QUEUED','RUNNING','UNCERTAIN')"))
            need(not pending, "Bridge has a pending or uncertain operation")
            sessions = list(con.execute("SELECT * FROM session"))
            need(len(sessions) == 1, "Exactly one closed bridge session required")
            session = dict(sessions[0])
            need(session.get("status") in ("STOPPED", "SUSPENDED_BOUNDARY"),
                 "Bridge session has not been explicitly suspended/closed")
            need(session.get("phase") in ("READY", "READY_QUERY", "BOUNDARY", "STOPPED"),
                 "Closed bridge is not at a completed opportunity boundary")
            return {"session": session, "pending": 0}
        need("requests" in tables, "Native paired transport journal missing")
        unresolved = []
        for row in con.execute("SELECT id,payload,payload_sha,status FROM requests"):
            payload = json.loads(row["payload"])
            need(row["status"] in {"queued", "processing", "completed", "uncertain", "failed_preserved", "rejected_invalid"},
                 "Unrecognized Native transport status")
            need(hashlib.sha256(canonical(payload).encode()).hexdigest() == row["payload_sha"],
                 "Native queue payload digest mismatch")
            if row["status"] in ("processing", "uncertain", "queued"):
                permitted = (row["status"] == "processing" and row["id"] == known_export_id and
                             payload.get("operacion") == "exportar")
                need(permitted, "Native journal has an unresolved operation other than known export")
                unresolved.append(row["id"])
        return {"known_export_processing_ids": unresolved,
                "meaning": "Exact committed export receipt is reconciled by the existing owner, never replayed."}
    finally:
        con.close()


def verify_native_export(directory, *, known_export_id=None):
    directory = safe(directory)
    manifest = read(directory / "EXPORTACION_SERVICIO.json")
    need(manifest.get("schema") == "DEE.persistent_service.paired_export.v1" and
         manifest.get("queue_journal_required") is True, "Official complete-service export required")
    members = manifest.get("members")
    need(isinstance(members, list) and 2 <= len(members) <= MAX_MEMBERS, "Bounded complete member manifest required")
    seen, total = set(), 0
    for row in members:
        name = relative(row["file"]).as_posix()
        need(name not in seen, "Duplicate native-export member")
        seen.add(name)
        file = safe(directory / name)
        need(file.is_file() and file.stat().st_size == row["bytes"] and
             sha(file) == row["sha256"], "Native-export member changed: " + name)
        total += row["bytes"]
    need(total <= MAX_BYTES and {"VIDA.deetsnap.gz", "cola.sqlite3"} <= seen,
         "Complete snapshot plus queue required within finite storage budget")
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*")
              if p.is_file() and p != directory / "EXPORTACION_SERVICIO.json"}
    need(actual == seen, "Native export has missing or extra unindexed files")
    need(sha(directory / "VIDA.deetsnap.gz") == manifest.get("snapshot_sha256"),
         "Native snapshot identity mismatch")
    queue = check_sqlite(directory / "cola.sqlite3", known_export_id=known_export_id)
    if queue["known_export_processing_ids"]:
        outbox = directory / "resultados" / (known_export_id + ".json")
        result = read(outbox)
        need(result.get("id") == known_export_id and result.get("operation") == "exportar" and
             result.get("after_tick") == manifest["physical"]["tick"],
             "Known export has no exact committed outbox receipt")
    return manifest, {"members": len(members), "bytes": total,
                      "manifest_sha256": sha(directory / "EXPORTACION_SERVICIO.json"), **queue}


def write_json(path, value):
    with Path(path).open("x", encoding="utf8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n"); handle.flush(); os.fsync(handle.fileno())


def create_pair(native_export, world_file, bridge_database, close_proof, destination,
                *, known_export_id=None):
    native_export = safe(native_export)
    world_file, bridge_database, close_proof = map(safe, (world_file, bridge_database, close_proof))
    destination = safe(destination, exists=False)
    need(not destination.exists(), "New checkpoint destination only; never overwrite a pair")
    world = read(world_file); boundary = validate_world(world)
    native, native_check = verify_native_export(native_export, known_export_id=known_export_id)
    need(native["life_id"] == boundary["life"] and native["physical"]["tick"] == boundary["tick"],
         "Native/world checkpoint identities or ticks differ")
    check_close(read(close_proof), boundary["life"])
    bridge_check = check_sqlite(bridge_database, bridge=True)
    session = bridge_check["session"]
    need(session.get("id") == world["bridge"].get("session_id"), "Bridge session differs from world")
    if "native_ticks_in_session" in world["bridge"]:
        need(session.get("ticks") == world["bridge"]["native_ticks_in_session"],
             "Bridge Native accounting differs from world checkpoint")
    if "last_action_id" in session:
        need(session["last_action_id"] == world["boundary"].get("last_action_id"),
             "Bridge last action differs from world boundary")
    # Validate every source before first destination write. Copies are taken
    # only after owner closure; this is not a live SQLite filesystem copy.
    destination.mkdir(parents=True)
    try:
        shutil.copytree(native_export, destination / "native_export", copy_function=shutil.copyfile)
        shutil.copyfile(world_file, destination / "WORLD_CHECKPOINT.json")
        shutil.copyfile(bridge_database, destination / "BRIDGE.sqlite3")
        shutil.copyfile(close_proof, destination / "OWNER_CLOSED.json")
        files = []
        for path in sorted(destination.rglob("*")):
            if path.is_file():
                files.append({"file": path.relative_to(destination).as_posix(),
                              "bytes": path.stat().st_size, "sha256": sha(path)})
        receipt = {"schema": SCHEMA, "checkpoint_id": boundary["checkpoint_id"],
                   "life_id": boundary["life"], "native_tick": boundary["tick"],
                   "world_id": world["world_id"], "scenario_sha256": world["scenario_sha256"],
                   "completed_opportunities": boundary["completed"],
                   "next_opportunity": boundary["next_opportunity"],
                   "known_export_id": known_export_id, "native_export_verification": native_check,
                   "members": files, "Native_imported": False, "new_native_ticks": 0,
                   "restoration_status": "PACKAGED_NOT_MATERIAL_REOPEN_TESTED",
                   "boundary": "Owner closed; bridge settled; exact world/action cursor; no uncertain replay."}
        write_json(destination / "PAREJA_C02.json", receipt)
        return verify_pair(destination)
    except BaseException as error:
        write_json(destination / "INCOMPLETE_PAIR_PRESERVED.json",
                   {"error_type": type(error).__name__, "detail": str(error),
                    "no_automatic_retry": True, "original_sources_untouched": True})
        raise


def verify_pair(directory):
    directory = safe(directory)
    need(not (directory / "INCOMPLETE_PAIR_PRESERVED.json").exists(), "Incomplete pair must be diagnosed")
    record = read(directory / "PAREJA_C02.json")
    need(record.get("schema") == SCHEMA, "C02 joint package schema required")
    if record.get("storage_mode") == "CLOSED_NATIVE_ROOT":
        return verify_closed_system_pair(directory, record)
    expected = set()
    for row in record["members"]:
        name = relative(row["file"]).as_posix(); need(name not in expected, "Duplicate pair member")
        expected.add(name); path = safe(directory / name)
        need(path.is_file() and path.stat().st_size == row["bytes"] and sha(path) == row["sha256"],
             "Joint checkpoint member changed: " + name)
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*")
              if p.is_file() and p != directory / "PAREJA_C02.json"}
    need(actual == expected, "Joint package members differ from manifest")
    boundary = validate_world(read(directory / "WORLD_CHECKPOINT.json"))
    native, ncheck = verify_native_export(directory / "native_export", known_export_id=record.get("known_export_id"))
    need(boundary["life"] == record["life_id"] == native["life_id"] and
         boundary["tick"] == record["native_tick"] == native["physical"]["tick"],
         "Joint checkpoint identity/tick mismatch")
    check_close(read(directory / "OWNER_CLOSED.json"), boundary["life"])
    bridge = check_sqlite(directory / "BRIDGE.sqlite3", bridge=True)
    need(bridge["session"]["id"] == read(directory / "WORLD_CHECKPOINT.json")["bridge"]["session_id"],
         "Bridge session mismatch")
    return {"status": "VERIFIED_FILES_NOT_MATERIAL_RESTORATION", "life_id": boundary["life"],
            "native_tick": boundary["tick"], "next_opportunity": boundary["next_opportunity"],
            "members": len(expected), "native_export": ncheck,
            "manifest_sha256": sha(directory / "PAREJA_C02.json"),
            "Native_imports": 0, "MCP_calls": 0, "new_native_ticks": 0}


def prepare_restore(directory, destination):
    """Stage exact bytes in a NEW diagnostic destination; never open Native.

    Root must perform official paired import, explicitly resume the matching
    closed bridge session, and call EstadoPareja_C02.apply in a fresh matching
    scene. This function's success does not claim that material test occurred.
    """
    proof = verify_pair(directory)
    directory, destination = safe(directory), safe(destination, exists=False)
    need(not destination.exists(), "Restore staging requires an unused destination")
    shutil.copytree(directory, destination, copy_function=shutil.copyfile)
    restored = verify_pair(destination)
    need(restored == proof, "Byte-preserving restore staging changed joint state")
    return {**restored, "status": "STAGED_NOT_OPENED", "destination": str(destination),
            "next_required": ["official complete Native import/reopen with same physical state",
                              "bridge session explicit resume against checkpoint identity",
                              "Luau apply in matching scenario; compare state fingerprint before new action"]}


def closed_native_root(native_root, life):
    """Read an already closed isolated root, no Store/Native module import."""
    native_root=safe(native_root);system=native_root/"sistema"
    need(system.is_dir() and not(system/"estado/ACTIVO.json").exists(),
         "Only an unselected isolated Native root may be checkpointed")
    need("_RBX01_" in life and life!=PROTECTED,"Protected Native root refused")
    card_file=system/"estado/vidas"/life/"VIDA.json";card=read(card_file)
    need(card["life_id"]==life and card["world_id"]==life,"Native identity mismatch")
    need(not(card_file.parent/"FUTURO_INTERRUMPIDO.json").exists() and
         not(system/"estado/locks"/(life+".lock")).exists(),
         "Interrupted future or owned writer lock preserved; cannot copy as closed")
    snapshot=safe(system/relative(card["snapshot"]))
    need(sha(snapshot)==card["snapshot_sha256"],"Current Native snapshot differs from record")
    journal=card_file.parent/"HISTORIA.jsonl"
    if journal.exists():
        lines=journal.read_text("utf8").splitlines()
        need(lines and json.loads(lines[-1])["snapshot_sha256"]==card["snapshot_sha256"],
             "Latest Native history and life pointer disagree")
    queue=system/"estado/servicios_persistentes"/life/"cola.sqlite3"
    check_sqlite(queue)
    con=sqlite3.connect(queue.resolve().as_uri()+"?mode=ro&immutable=1",uri=True)
    try:
        row=con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()
        need(row is not None,"Native closed owner cache missing")
        owner=json.loads(row[0])
        need(owner.get("running")is False and owner.get("uncertain_external_result",False)is False and
             owner.get("life_id")==life and owner.get("tick")==card["physical"]["tick"],
             "Native owner cache is not the matching closed cut")
    finally:con.close()
    return card


def create_closed_system_pair(native_root, world_file, bridge_database, close_proof, destination):
    """Full closed destination copy; shared official installed motor stays outside.

    This alternative avoids creating an export operation. It preserves the whole
    existing isolated destination and its empty directories, not a raw-only cut.
    The resulting backup is not an automatic relocated Native importer.
    """
    native_root=safe(native_root)
    world_file,bridge_database,close_proof=map(safe,(world_file,bridge_database,close_proof))
    destination=safe(destination,exists=False)
    need(not destination.exists() and not destination.is_relative_to(native_root),
         "New checkpoint destination must be outside the copied Native root")
    world=read(world_file);boundary=validate_world(world)
    card=closed_native_root(native_root,boundary["life"])
    need(card["physical"]["tick"]==boundary["tick"],"Native/world closed ticks differ")
    check_close(read(close_proof),boundary["life"])
    bridge=check_sqlite(bridge_database,bridge=True)
    need(bridge["session"].get("id")==world["bridge"]["session_id"] and
         bridge["session"].get("last_action_id")==world["boundary"].get("last_action_id"),
         "Closed bridge differs from world action boundary")
    source_files=[];source_dirs=[];total=0
    for entry in sorted(native_root.rglob("*")):
        safe(entry)
        relative_name=entry.relative_to(native_root).as_posix()
        if entry.is_dir():source_dirs.append(relative_name)
        elif entry.is_file():
            row={"file":relative_name,"bytes":entry.stat().st_size,"sha256":sha(entry)}
            source_files.append(row);total+=row["bytes"]
        else:raise ValueError("Nonregular native checkpoint member")
    need(len(source_files)<=MAX_MEMBERS and total<=MAX_BYTES,"Finite closed Native copy bound exceeded")
    destination.mkdir(parents=True)
    try:
        shutil.copytree(native_root,destination/"native_root",copy_function=shutil.copyfile)
        shutil.copyfile(world_file,destination/"WORLD_CHECKPOINT.json")
        shutil.copyfile(bridge_database,destination/"BRIDGE.sqlite3")
        shutil.copyfile(close_proof,destination/"OWNER_CLOSED.json")
        files=[]
        for row in source_files:
            copied=destination/"native_root"/row["file"]
            need(copied.stat().st_size==row["bytes"] and sha(copied)==row["sha256"],
                 "Native source changed during closed copy")
        for entry in sorted(destination.rglob("*")):
            if entry.is_file():files.append({"file":entry.relative_to(destination).as_posix(),
                                            "bytes":entry.stat().st_size,"sha256":sha(entry)})
        record={"schema":SCHEMA,"storage_mode":"CLOSED_NATIVE_ROOT",
            "checkpoint_id":boundary["checkpoint_id"],"life_id":boundary["life"],"native_tick":boundary["tick"],
            "world_id":world["world_id"],"scenario_sha256":world["scenario_sha256"],
            "completed_opportunities":boundary["completed"],"next_opportunity":boundary["next_opportunity"],
            "native_source_root_locator":str(native_root),"native_snapshot_sha256":card["snapshot_sha256"],
            "native_physical":card["physical"],"native_directories":source_dirs,"members":files,
            "Native_imported":False,"new_native_ticks":0,
            "restoration_status":"BACKUP_VERIFIED_NOT_MATERIAL_REOPEN_TESTED",
            "shared_dependencies":"Official installed motor and source scopes remain shared, read-only, separately pinned. Absolute source locators are not automatically remapped.",
            "budget_rule":"Global cumulative Native budget is not rewound by restoring an environmental checkpoint."}
        write_json(destination/"PAREJA_C02.json",record)
        return verify_pair(destination)
    except BaseException as error:
        write_json(destination/"INCOMPLETE_PAIR_PRESERVED.json",{"error_type":type(error).__name__,
            "detail":str(error),"original_sources_untouched":True,"no_automatic_retry":True})
        raise


def verify_closed_system_pair(directory,record):
    expected=set()
    for row in record["members"]:
        name=relative(row["file"]).as_posix();need(name not in expected,"Duplicate closed pair member")
        expected.add(name);entry=safe(directory/name)
        need(entry.is_file() and entry.stat().st_size==row["bytes"] and sha(entry)==row["sha256"],
             "Closed pair member changed: "+name)
    actual={x.relative_to(directory).as_posix()for x in directory.rglob("*")
            if x.is_file()and x!=directory/"PAREJA_C02.json"}
    need(actual==expected,"Closed pair file-set differs")
    dirs={x.relative_to(directory/"native_root").as_posix()for x in(directory/"native_root").rglob("*")if x.is_dir()}
    need(dirs==set(record["native_directories"]),"Closed Native empty-directory structure differs")
    world=read(directory/"WORLD_CHECKPOINT.json");boundary=validate_world(world)
    card=closed_native_root(directory/"native_root",boundary["life"])
    need(boundary["tick"]==record["native_tick"]==card["physical"]["tick"] and
         card["snapshot_sha256"]==record["native_snapshot_sha256"],"Closed paired Native cut differs")
    check_close(read(directory/"OWNER_CLOSED.json"),boundary["life"])
    bridge=check_sqlite(directory/"BRIDGE.sqlite3",bridge=True)
    need(bridge["session"]["id"]==world["bridge"]["session_id"],"Closed bridge session differs")
    return {"status":"VERIFIED_FILES_NOT_MATERIAL_RESTORATION","storage_mode":"CLOSED_NATIVE_ROOT",
            "life_id":boundary["life"],"native_tick":boundary["tick"],"next_opportunity":boundary["next_opportunity"],
            "members":len(expected),"native_snapshot_sha256":card["snapshot_sha256"],
            "manifest_sha256":sha(directory/"PAREJA_C02.json"),"Native_imports":0,"MCP_calls":0,"new_native_ticks":0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    s = sub.add_parser("seal")
    for name in ("native-export", "world-file", "bridge-database", "close-proof", "destination"):
        s.add_argument("--" + name, type=Path, required=True)
    s.add_argument("--known-export-id")
    n = sub.add_parser("seal-system")
    for name in ("native-root", "world-file", "bridge-database", "close-proof", "destination"):
        n.add_argument("--" + name, type=Path, required=True)
    v = sub.add_parser("verify"); v.add_argument("--pair", type=Path, required=True)
    r = sub.add_parser("stage-restore"); r.add_argument("--pair", type=Path, required=True)
    r.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    if args.mode == "seal":
        answer = create_pair(args.native_export, args.world_file, args.bridge_database,
                             args.close_proof, args.destination, known_export_id=args.known_export_id)
    elif args.mode == "seal-system":
        answer = create_closed_system_pair(args.native_root,args.world_file,args.bridge_database,args.close_proof,args.destination)
    elif args.mode == "verify":
        answer = verify_pair(args.pair)
    else:
        answer = prepare_restore(args.pair, args.destination)
    print(json.dumps(answer, ensure_ascii=False))


if __name__ == "__main__":
    main()
