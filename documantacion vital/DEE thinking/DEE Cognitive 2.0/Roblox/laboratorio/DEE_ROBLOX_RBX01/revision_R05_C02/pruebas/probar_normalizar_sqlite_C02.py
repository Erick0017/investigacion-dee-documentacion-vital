"""Synthetic C02 SQLite maintenance, real SQLite/lease; no Native or live DB."""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,sqlite3,sys,types
ROOT=Path(__file__).resolve().parents[1]
def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
m=load(ROOT/'control/normalizar_sqlite_cerrado_C02.py','_maintenance_fixture')
b=load(ROOT/'puente/rbx02_bridge_C02.py','_maintenance_lease_fixture')
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');work=ROOT/'pruebas'/('MANTENIMIENTO_SQLITE_FIXTURE_'+stamp);work.mkdir();m.ROOT=work
native=work/'native';native.mkdir();(native/'CONTEXTO_EJECUCION.json').write_text('{"life":"ECI02_RBX01_FIXTURE"}',encoding='utf8')
proof=work/'closed.json';proof.write_text('{"technical_fixture":true}',encoding='utf8');snapshot=native/'opaque.bin';snapshot.write_bytes(b'NOT_NATIVE')
card={'physical':{'tick':42},'snapshot_sha256':m.sha(snapshot)}
def check(path,bridge):
    db=sqlite3.connect(path.as_uri()+'?mode=ro&immutable=1',uri=True)
    try:assert db.execute('PRAGMA quick_check').fetchone()[0]=='ok'
    finally:db.close()
p=types.SimpleNamespace(safe=lambda path,exists=True:Path(path).resolve(),closed_native_root=lambda *args:card,
                        check_close=lambda *args:None,check_sqlite=check)
db=work/'configuracion_privada/fixture.sqlite3';db.parent.mkdir();con=sqlite3.connect(db)
con.execute('PRAGMA journal_mode=WAL')
con.executescript('CREATE TABLE bridge_meta(key,value);CREATE TABLE session(id,status,phase,last_action_id);CREATE TABLE operation(status);CREATE TABLE boundary(session_id,last_action_id);CREATE TABLE action(acknowledged,execution_status);CREATE TABLE tool_call(acknowledged);')
con.execute("INSERT INTO bridge_meta VALUES('schema','DEE.RBX01.bridge_database.C02.R01')")
con.execute("INSERT INTO session VALUES('session_fixture','SUSPENDED_BOUNDARY','READY_QUERY','action_fixture')")
con.execute("INSERT INTO operation VALUES('COMPLETED')");con.execute("INSERT INTO boundary VALUES('session_fixture','action_fixture')")
con.execute("INSERT INTO action VALUES(1,'EXECUTED')");con.execute('INSERT INTO tool_call VALUES(1)');con.commit();con.close()
args=argparse.Namespace(root_run=True,native_root=native,close_proof=proof,bridge_database=db,output=work/'maintenance')
result=m.maintain(args,persistence=p,bridge=b);checks=[]
assert result['status']=='CLOSED_BRIDGE_CHECKPOINTED_ROWS_IDENTICAL';checks.append('SQLite checkpoint closes clean suspended synthetic bridge')
assert result['before_semantics']==result['after_semantics'];checks.append('All scientific table rows unchanged')
backup=Path(result['coherent_backup']['file']);assert backup.exists()and backup.stat().st_size>0;checks.append('Coherent SQLite backup preserved before maintenance')
assert result['files_deleted_by_script']==0 and result['Native_ticks']==0;checks.append('No manual deletion or Native execution')
assert m.sha(snapshot)==card['snapshot_sha256'];checks.append('Synthetic Native component untouched')
report={'scope':'SYNTHETIC_SQLITE_AND_ACTUAL_PROCESSLEASE_ONLY','tests':len(checks),'checks':checks,
        'fixture':str(work),'Native_imports':0,'Native_ticks':0,'MCP_calls':0,'live_databases':0,
        'source_sha256':m.sha(ROOT/'control/normalizar_sqlite_cerrado_C02.py')}
out=ROOT/'pruebas'/('MANTENIMIENTO_SQLITE_SINTETICO_'+stamp+'.json');out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'report':str(out),**report},ensure_ascii=False))
