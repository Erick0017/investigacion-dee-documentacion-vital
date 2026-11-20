"""Synthetic SQLite/guard verification; no real DB/owner/model/MCP activity."""
from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,sqlite3
ROOT=Path(__file__).resolve().parents[1]
def load(path,name):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
p=ROOT/'control/normalizar_y_sellar_comparador_C02.py';m=load(p.relative_to(ROOT),'_closed_comparator_fixture')
proof=dict(schema='DEE.RBX01.C02.comparator_closure.v1',status='CLOSED',participant='PROGRAMMED',run_id='TEST',
 policyWriterClosed=True,writerDrained=True,nativeOwnerOpened=False,nativeTicks=0,coherence_error=None,
 coherence=dict(coherent=True),policy_checkpoint=dict(pending=None,sha256='a'*64))
m.verify_proof(proof,'PROGRAMMED','TEST','a'*64)
tests=[dict(name='closed_coherent_exact_policy_proof',passed=True)]
for key,value in[('writerDrained',False),('nativeTicks',1),('nativeOwnerOpened',True),('status','RUNNING')]:
 q=copy.deepcopy(proof);q[key]=value
 try:m.verify_proof(q,'PROGRAMMED','TEST','a'*64)
 except RuntimeError:tests.append(dict(name='reject_'+key,passed=True))
 else:raise AssertionError(key)
try:m.verify_proof(proof,'PROGRAMMED','TEST','b'*64)
except RuntimeError:tests.append(dict(name='reject_changed_policy_bytes',passed=True))
else:raise AssertionError('hash')
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
folder=ROOT/'pruebas'/('SQLITE_COMPARADOR_SINTETICO_'+stamp);folder.mkdir()
db=folder/'synthetic.sqlite3';con=sqlite3.connect(db,isolation_level=None)
con.execute('PRAGMA journal_mode=WAL')
schema=["CREATE TABLE bridge_meta(key TEXT,value TEXT)","CREATE TABLE session(id TEXT,mode TEXT,ticks INTEGER,status TEXT,phase TEXT,last_action_id TEXT)",
 "CREATE TABLE boundary(session_id TEXT,last_action_id TEXT)","CREATE TABLE operation(status TEXT)",
 "CREATE TABLE action(acknowledged INTEGER,execution_status TEXT)","CREATE TABLE tool_call(acknowledged INTEGER)","CREATE TABLE checkpoint_binding(checkpoint_id TEXT)"]
for statement in schema:con.execute(statement)
con.execute("INSERT INTO bridge_meta VALUES('schema','DEE.RBX01.bridge_database.C02.R01')")
con.execute("INSERT INTO session VALUES('S','PROGRAMMED',0,'SUSPENDED_BOUNDARY','READY_QUERY','A')")
con.execute("INSERT INTO boundary VALUES('S','A')");con.execute("INSERT INTO operation VALUES('COMPLETED')")
con.execute("INSERT INTO action VALUES(1,'EXECUTED')");con.execute("INSERT INTO tool_call VALUES(1)")
generic=load('control/normalizar_sqlite_cerrado_C02.py','_generic_sqlite_fixture')
before=generic.semantics(con);backup=folder/'backup.sqlite3';dst=sqlite3.connect(backup)
con.backup(dst);assert dst.execute('PRAGMA quick_check').fetchone()[0]=='ok';dst.close()
result=list(con.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchone());assert result[0]==0
assert generic.semantics(con)==before;con.close()
tests.append(dict(name='coherent_backup_SQLite_checkpoint_all_rows_equal',passed=True,checkpoint=result))
t=p.read_text('utf8');ast.parse(t)
assert t.index('before=m.semantics(con)')<t.index("PRAGMA wal_checkpoint(TRUNCATE)")<t.index('after=m.semantics(con)')<t.index('pair=v.seal_comparator')
assert "lease.close();lease=None"in t and "world_path==original/'WORLD_CHECKPOINT.json'"in t
assert 'unlink('not in t and 'remove('not in t
tests.append(dict(name='maintenance_before_binding_original_World_and_no_aux_deletion',passed=True))
report=dict(schema='DEE.RBX01.C02.closed_comparator_offline_fixtures.R01',tests=tests,all_passed=True,
 source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),Native_calls=0,MCP_calls=0,HTTP_calls=0,model_calls=0,
 actual_experiment_DB_opened=False,synthetic_files=str(folder))
out=ROOT/'pruebas'/('SELLADO_COMPARADOR_CERRADO_'+stamp+'.json');out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report,indent=2))
