"""Synthetic, stdlib-only persistence guards. No DEE, Studio, MCP or live DB."""
from pathlib import Path
import copy
import datetime
import hashlib
import importlib.util
import json
import sqlite3
import time

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("C02_persistence_under_test",ROOT/"control/persistencia_C02.py")
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
stamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
WORK=ROOT/"pruebas"/("fixture_persistencia_"+stamp)
LIFE="ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_FIXTURE"


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf8")


def fixture(name,*,pending_export=False):
    base=WORK/name;base.mkdir(parents=True)
    native=base/"native_export";native.mkdir()
    (native/"VIDA.deetsnap.gz").write_bytes(b"TECHNICAL_FIXTURE_ONLY_NO_NATIVE_STATE")
    resource=native/"artefactos_trabajador"/"resource.bin"
    resource.parent.mkdir();resource.write_bytes(b"fixed-resource-contents")
    q=sqlite3.connect(native/"cola.sqlite3")
    q.execute("CREATE TABLE requests(id TEXT PRIMARY KEY,payload TEXT,payload_sha TEXT,status TEXT)")
    identifier="export_fixture" if pending_export else "material_fixture"
    payload={"operacion":"exportar" if pending_export else "sesion","situaciones":[]}
    data=p.canonical(payload)
    q.execute("INSERT INTO requests VALUES(?,?,?,?)",(identifier,data,hashlib.sha256(data.encode()).hexdigest(),
                                                       "processing" if pending_export else "completed"))
    q.commit();q.close()
    if pending_export:
        write(native/"resultados"/(identifier+".json"),
              {"id":identifier,"operation":"exportar","after_tick":947395,"result":{"paired_export_requested":True}})
    rows=[{"file":x.relative_to(native).as_posix(),"bytes":x.stat().st_size,"sha256":p.sha(x)}
          for x in sorted(native.rglob("*"))if x.is_file()]
    write(native/"EXPORTACION_SERVICIO.json",{"schema":"DEE.persistent_service.paired_export.v1",
         "technical_fixture":True,"life_id":LIFE,"backend":"mente_unificada","profile":"fisica_directa",
         "queue_journal_required":True,"native_snapshot":"VIDA.deetsnap.gz",
         "snapshot_sha256":p.sha(native/"VIDA.deetsnap.gz"),"physical":{"N":67,"tick":947395},"members":rows})
    bridge=base/"bridge.sqlite3";b=sqlite3.connect(bridge)
    b.execute("CREATE TABLE session(id TEXT,status TEXT,phase TEXT,ticks INTEGER,last_action_id TEXT)")
    b.execute("INSERT INTO session VALUES('session_fixture','STOPPED','READY_QUERY',1564,'action_fixture')")
    b.execute("CREATE TABLE operation(id TEXT,status TEXT)")
    b.execute("INSERT INTO operation VALUES('feedback_fixture','COMPLETED')");b.commit();b.close()
    world={"schema":p.WORLD_SCHEMA,"technical_fixture":True,"checkpoint_id":"joint_fixture_"+name,
      "world_id":"RBX01_C02_FIXTURE","scenario_sha256":"a"*64,"native_life_id":LIFE,"native_tick":947395,
      "boundary":{"phase":"BOUNDARY","native_phase":"IDLE","completed_opportunities":1,"next_opportunity":2,
        "pending_action":None,"pending_operation":None,"uncertain":False,"last_action_id":"action_fixture",
        "acknowledged_action_id":"action_fixture","last_feedback_operation_id":"feedback_fixture"},
      "S":{"nativeTick":947395,"completedCycles":1,"cycle":1,"worldTime":10.0,"permissionStock":47,
        "inventoryKey":True,"inventoryResource":False,"zero_output":{"present":True,"value":0},
        "absent_output":{"present":False,"value":None}},
      "body_pose":[0,0,0,1,0,0,0,1,0,0,0,1],"executed_actions":{"action_fixture":"EXECUTED"},
      "events":[{"kind":"ACTION_EXECUTED","actionId":"action_fixture"}],
      "physical":{"parts":[{"path":"Gates/Gate_0_0","className":"Part","cframe":[0,0,0,1,0,0,0,1,0,0,0,1]}]},
      "rng":{"algorithm":"C02_LCG32_V1","state":404271,"counter":0},
      "controller":{"phase":"BOUNDARY","next_opportunity":2},
      "bridge":{"session_id":"session_fixture","server_id":"server_fixture","phase":"READY_QUERY","pending_count":0,
                "uncertain_count":0,"native_ticks_in_session":1564}}
    write(base/"world.json",world)
    write(base/"closed.json",{"closure_proof":{"status":"CLOSED","lifeId":LIFE,"ownerClosed":True,"writerDrained":True},
                              "owner_returncode":0,"technical_fixture":True})
    return base,world


def seal(base,target="pair",known_export_id=None):
    return p.create_pair(base/"native_export",base/"world.json",base/"bridge.sqlite3",base/"closed.json",base/target,
                         known_export_id=known_export_id)


def reject(call):
    try:call()
    except (ValueError,FileExistsError):return
    raise AssertionError("Invalid checkpoint was accepted")


def roundtrip():
    base,world=fixture("roundtrip")
    before={str(x):p.sha(x)for x in base.rglob("*")if x.is_file()}
    a=seal(base)
    assert a["status"]=="VERIFIED_FILES_NOT_MATERIAL_RESTORATION" and a["next_opportunity"]==2
    staged=p.prepare_restore(base/"pair",base/"restore")
    assert staged["status"]=="STAGED_NOT_OPENED" and p.read(base/"restore/WORLD_CHECKPOINT.json")==world
    assert p.sha(base/"native_export/VIDA.deetsnap.gz")==p.sha(base/"restore/native_export/VIDA.deetsnap.gz")
    assert all(p.sha(Path(k))==v for k,v in before.items())
    assert p.read(base/"restore/WORLD_CHECKPOINT.json")["S"]["zero_output"]["value"]==0
    assert p.read(base/"restore/WORLD_CHECKPOINT.json")["S"]["absent_output"]["value"]is None
    reject(lambda:p.prepare_restore(base/"pair",base/"restore"))


def pending():
    base,w=fixture("pending")
    w["boundary"]["pending_action"]="action_unknown";write(base/"world.json",w)
    reject(lambda:seal(base));assert not(base/"pair").exists()


def wrong_tick():
    base,w=fixture("tick")
    w["native_tick"]+=1;w["S"]["nativeTick"]+=1;write(base/"world.json",w)
    reject(lambda:seal(base));assert not(base/"pair").exists()


def missing_ack():
    base,w=fixture("ack")
    w["boundary"]["acknowledged_action_id"]="other";write(base/"world.json",w)
    reject(lambda:seal(base));assert not(base/"pair").exists()


def active_action():
    base,w=fixture("executing")
    w["executed_actions"]["action_fixture"]="EXECUTING";write(base/"world.json",w)
    reject(lambda:seal(base));assert not(base/"pair").exists()


def queue_uncertain():
    base,w=fixture("queue")
    q=sqlite3.connect(base/"native_export/cola.sqlite3");q.execute("UPDATE requests SET status='uncertain'");q.commit();q.close()
    manifest=p.read(base/"native_export/EXPORTACION_SERVICIO.json")
    for row in manifest["members"]:
        file=base/"native_export"/row["file"];row.update(bytes=file.stat().st_size,sha256=p.sha(file))
    write(base/"native_export/EXPORTACION_SERVICIO.json",manifest)
    reject(lambda:seal(base));assert not(base/"pair").exists()


def export_receipt_reconciliation():
    base,w=fixture("export_pending",pending_export=True)
    reject(lambda:seal(base,"wrong"));assert not(base/"wrong").exists()
    answer=seal(base,known_export_id="export_fixture")
    assert answer["native_export"]["known_export_processing_ids"]==["export_fixture"]
    assert p.read(base/"pair/native_export/resultados/export_fixture.json")["after_tick"]==947395


def corrupt_member():
    base,w=fixture("corrupt")
    (base/"native_export/artefactos_trabajador/resource.bin").write_bytes(b"changed")
    reject(lambda:seal(base));assert not(base/"pair").exists()


def sqlite_wal():
    base,w=fixture("wal")
    Path(str(base/"bridge.sqlite3")+"-wal").write_bytes(b"not-a-closed-database")
    reject(lambda:seal(base));assert not(base/"pair").exists()


def rng_continuation():
    def step(state):return (1664525*state+1013904223)%4294967296
    value=404271
    prefix=[]
    for _ in range(4):value=step(value);prefix.append(value)
    saved={"algorithm":"C02_LCG32_V1","state":value,"counter":4}
    continued=[]
    for _ in range(3):value=step(value);continued.append(value)
    restored=json.loads(json.dumps(saved));other=[]
    for _ in range(3):restored["state"]=step(restored["state"]);restored["counter"]+=1;other.append(restored["state"])
    assert continued==other and restored["counter"]==7


def declared_roundtrip_tolerance():
    base,before=fixture("roundtrip_tolerance")
    after=copy.deepcopy(before);after["S"]["mode"]="RESTORED"
    after["physical"]["parts"][0]["cframe"][0]+=1e-6
    assert p.compare_world_semantics(before,after)["equal_with_declared_geometry_tolerance"]
    after["S"]["permissionStock"]-=1
    assert not p.compare_world_semantics(before,after)["equal_with_declared_geometry_tolerance"]
    after=copy.deepcopy(before);after["S"]["zero_output"]["value"]=None
    assert not p.compare_world_semantics(before,after)["equal_with_declared_geometry_tolerance"]


def unknown_bridge_status():
    base,w=fixture("unknown_status")
    q=sqlite3.connect(base/"bridge.sqlite3");q.execute("UPDATE operation SET status='IN_PROGRESS_UNKNOWN'");q.commit();q.close()
    reject(lambda:seal(base));assert not(base/"pair").exists()


def uncertain_owner_close():
    base,w=fixture("uncertain_owner")
    proof=p.read(base/"closed.json")
    proof["owned_child_close_evidence"]={"exit_code":0,"final_status":{"running":False,"uncertain_external_result":True}}
    write(base/"closed.json",proof)
    reject(lambda:seal(base));assert not(base/"pair").exists()


def full_closed_native_root():
    base,w=fixture("closed_root")
    native=base/"source_root";system=native/"sistema"
    checkpoint=system/"estado/checkpoints/fixture.deetsnap.gz"
    checkpoint.parent.mkdir(parents=True);checkpoint.write_bytes(b"SYNTHETIC_CLOSED_NOT_A_DEE_SNAPSHOT")
    life=system/"estado/vidas"/LIFE;life.mkdir(parents=True)
    card={"life_id":LIFE,"world_id":LIFE,"snapshot":"estado/checkpoints/fixture.deetsnap.gz",
          "snapshot_sha256":p.sha(checkpoint),"physical":{"N":67,"tick":947395}}
    write(life/"VIDA.json",card)
    (life/"HISTORIA.jsonl").write_text(json.dumps({"snapshot_sha256":card["snapshot_sha256"]})+"\n",encoding="utf8")
    qdir=system/"estado/servicios_persistentes"/LIFE;qdir.mkdir(parents=True)
    import shutil
    shutil.copyfile(base/"native_export/cola.sqlite3",qdir/"cola.sqlite3")
    q=sqlite3.connect(qdir/"cola.sqlite3");q.execute("CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT)")
    q.execute("INSERT INTO meta VALUES('owner',?)",(json.dumps({"life_id":LIFE,"tick":947395,"running":False,"uncertain_external_result":False}),));q.commit();q.close()
    empty=system/"estado/servicios_locales"/LIFE/"device/reservoir";empty.mkdir(parents=True)
    write(native/"CONTEXTO_EJECUCION.json",{"system":str(system),"life":LIFE,"technical_fixture":True})
    answer=p.create_closed_system_pair(native,base/"world.json",base/"bridge.sqlite3",base/"closed.json",base/"fullpair")
    assert answer["storage_mode"]=="CLOSED_NATIVE_ROOT"
    assert (base/"fullpair/native_root"/empty.relative_to(native)).is_dir()
    restored=p.prepare_restore(base/"fullpair",base/"fullrestore")
    assert restored["status"]=="STAGED_NOT_OPENED"
    assert p.sha(base/"fullrestore/native_root"/checkpoint.relative_to(native))==card["snapshot_sha256"]
    (base/"fullrestore/native_root"/empty.relative_to(native)).rmdir()
    reject(lambda:p.verify_pair(base/"fullrestore"))


def main():
    WORK.mkdir(parents=True)
    results=[];start=time.monotonic()
    for test in(roundtrip,pending,wrong_tick,missing_ack,active_action,queue_uncertain,
                export_receipt_reconciliation,corrupt_member,sqlite_wal,rng_continuation,
                declared_roundtrip_tolerance,unknown_bridge_status,uncertain_owner_close,full_closed_native_root):
        test();results.append({"name":test.__name__,"result":"PASSED_SYNTHETIC_GUARD"})
    report={"schema":"DEE.RBX01.C02.persistence_synthetic_tests.v1","technical_fixture":True,
        "Native_imports":0,"Native_ticks":0,"Studio_MCP_calls":0,"live_databases_opened":0,
        "scope":"Synthetic opaque bytes, fake transport databases and world JSON only; not a material reopen test.",
        "module_sha256":p.sha(ROOT/"control/persistencia_C02.py"),
        "Luau_source_sha256_not_executed":p.sha(ROOT/"mundo/EstadoPareja_C02.luau"),
        "test_source_sha256":p.sha(Path(__file__)),"work":str(WORK),"elapsed_seconds":time.monotonic()-start,
        "results":results}
    output=ROOT/"pruebas"/("PERSISTENCIA_SINTETICA_"+stamp+".json")
    write(output,report)
    print(json.dumps({"synthetic_guards":len(results),"elapsed_seconds":report["elapsed_seconds"],"report":str(output),
                      "Native_executed":False}))


if __name__=="__main__":main()
