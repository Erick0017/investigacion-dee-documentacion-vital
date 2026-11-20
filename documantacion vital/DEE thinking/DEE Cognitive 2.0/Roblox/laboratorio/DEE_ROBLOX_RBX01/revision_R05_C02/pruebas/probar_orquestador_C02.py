"""Stdlib synthetic helper tests only; never calls run/Native/MCP/Studio."""
from pathlib import Path
import datetime, hashlib, importlib.util, json, sqlite3, sys

ROOT=Path(__file__).resolve().parents[1]
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
folder=ROOT/'pruebas'/('ORQUESTADOR_FIXTURE_'+stamp);folder.mkdir()
source=ROOT/'control/orquestar_C02.py'
spec=importlib.util.spec_from_file_location('_C02_orq_fixture',source)
mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
checks=[]
def test(name,fn):
    fn();checks.append(name)
def fails(fn):
    try:fn()
    except(RuntimeError,ValueError):return
    raise AssertionError('Expected preservation guard failure')

def fingerprints():
    physical={'N':67,'tick':100,'RAW_sha256':'a'*64,'clocks_sha256':'b'*64}
    x={'physical':physical,'idle_ticks':0,'C02_host_event_driven':True}
    assert mod.no_idle_equal(x,x,physical)
    bad={**x,'idle_ticks':1};assert not mod.no_idle_equal(x,bad,physical)
    bad={**x,'physical':{**physical,'tick':101}};assert not mod.no_idle_equal(x,bad,physical)
test('No-idle fingerprint includes RAW clocks tick and idle count',fingerprints)
test('Unknown MCP outcome is not accepted',lambda:fails(lambda:mod.decode_tool({'status':'TIMEOUT'})))
test('Wrong subtree is refused',lambda:fails(lambda:mod.safe(ROOT.parent/'not_C02')))
def decoding():
    value={'verified':True,'zero':0,'missing':None}
    assert mod.decode_tool({'status':'REPLIED','reply':{'result':{'content':[{'type':'text','text':json.dumps(value)}]}}})==value
test('MCP data decoding preserves zero versus NULL',decoding)
def closed():
    p=folder/'synthetic_owner.log';p.write_text(json.dumps({'status':'CLOSED','lifeId':'fixture','ownerClosed':True,'writerDrained':True}),encoding='utf8')
    assert mod.closure_proof(p,0,'fixture')is not None
    assert mod.closure_proof(p,1,'fixture')is None
    assert mod.closure_proof(p,0,'other')is None
test('Closure requires exact life and successful process return',closed)
def dbread():
    p=folder/'synthetic.sqlite3';db=sqlite3.connect(p)
    db.executescript('CREATE TABLE session(id,server_id,status,phase);CREATE TABLE operation(id,kind,status);CREATE TABLE boundary(completed_cycles,next_opportunity);CREATE TABLE checkpoint_binding(checkpoint_id,checkpoint_sha256);CREATE TABLE action(acknowledged);CREATE TABLE tool_call(acknowledged);')
    db.execute("INSERT INTO session VALUES('session_fixture','server_fixture','SUSPENDED_BOUNDARY','READY_QUERY')")
    db.execute("INSERT INTO operation VALUES('feedback_fixture','feedback','COMPLETED')")
    db.execute('INSERT INTO boundary VALUES(2,3)');db.execute("INSERT INTO checkpoint_binding VALUES('checkpoint_fixture',?)",('a'*64,))
    db.execute('INSERT INTO action VALUES(1)');db.execute('INSERT INTO tool_call VALUES(1)');db.commit();db.close()
    before=hashlib.sha256(p.read_bytes()).hexdigest();result=mod.bridge_read(p)
    assert result['feedback_operations_completed']==1 and result['pending']==result['uncertain']==result['unacknowledged_actions']==result['unacknowledged_tools']==0
    assert result['boundary']['next_opportunity']==3 and result['checkpoint_binding']['checkpoint_id']=='checkpoint_fixture'
    assert hashlib.sha256(p.read_bytes()).hexdigest()==before
test('Readonly coherent bridge boundary reports cursor binding ACK and zero pending',dbread)
def guard():
    code=mod.prepared_guard(4,2)
    assert 'c.MaxCycles==4' in code and 'c.SuspendAfter==2' in code and 'PermissionStock==200' in code
    assert 'MaxCycles==16'not in code and 'ReserveStartsAtCycle==13'not in code and 'LayoutSeed'not in code
test('DEV guard uses explicit4/2 with new200stock and no stale C01 seeds',guard)
def literal():
    s='x]] ]=] á\n"'
    value=mod.long_string(s);assert s in value and value.endswith(':sub(2)')
test('Lua transport quotes remain literal UTF8 payload',literal)
report={'scope':'SYNTHETIC_STDLIB_HELPERS_ONLY','tests':len(checks),'checks':checks,
        'Native_imports':0,'Native_ticks':0,'MCP_calls':0,'Studio_calls':0,
        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'fixture':str(folder)}
out=ROOT/'pruebas'/('ORQUESTADOR_SINTETICO_'+stamp+'.json')
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'report':str(out),**report},ensure_ascii=False))
