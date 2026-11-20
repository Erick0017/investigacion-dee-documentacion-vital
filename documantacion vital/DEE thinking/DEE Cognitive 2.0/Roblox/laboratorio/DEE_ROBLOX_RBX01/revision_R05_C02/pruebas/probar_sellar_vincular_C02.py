"""Synthetic whole-root sealing with a binder double, no Native/MCP/network."""
from pathlib import Path
import argparse,copy,datetime,hashlib,importlib.util,json,sqlite3,sys,types
ROOT=Path(__file__).resolve().parents[1]
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
work=ROOT/'pruebas'/('SELLADO_FIXTURE_'+stamp);work.mkdir()
def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
m=load(ROOT/'control/sellar_vincular_C02.py','_seal_fixture');p=load(ROOT/'control/persistencia_C02.py','_seal_codec_fixture')
m.ROOT=work
def write(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value)+'\n',encoding='utf8')
life='ECI02_RBX01_C02_FIXTURE';native=work/'native';system=native/'sistema';snapshot=system/'estado/checkpoints/fixture.deetsnap.gz'
snapshot.parent.mkdir(parents=True);snapshot.write_bytes(b'SYNTHETIC_OPAQUE_NOT_DEE_SNAPSHOT')
card={'life_id':life,'world_id':life,'snapshot':'estado/checkpoints/fixture.deetsnap.gz','snapshot_sha256':m.sha(snapshot),'physical':{'N':67,'tick':42}}
write(system/'estado/vidas'/life/'VIDA.json',card)
(system/'estado/vidas'/life/'HISTORIA.jsonl').write_text(json.dumps({'snapshot_sha256':card['snapshot_sha256']})+'\n',encoding='utf8')
qpath=system/'estado/servicios_persistentes'/life/'cola.sqlite3';qpath.parent.mkdir(parents=True)
q=sqlite3.connect(qpath);q.executescript('CREATE TABLE requests(id,payload,payload_sha,status);CREATE TABLE meta(key,value);')
q.execute("INSERT INTO requests VALUES('old','{}',?,'completed')",(hashlib.sha256(b'{}').hexdigest(),));q.execute("INSERT INTO meta VALUES('owner',?)",(json.dumps({'life_id':life,'tick':42,'running':False,'uncertain_external_result':False}),));q.commit();q.close()
(system/'estado/servicios_locales'/life/'empty/device').mkdir(parents=True)
db=work/'configuracion_privada/bridge_fixture.sqlite3';db.parent.mkdir()
b=sqlite3.connect(db)
b.executescript('CREATE TABLE session(id,server_id,status,phase,ticks,last_action_id);CREATE TABLE boundary(session_id,completed_cycles,next_opportunity,last_action_id,feedback_operation_id);CREATE TABLE operation(id,status);CREATE TABLE request(id);CREATE TABLE observation(id);CREATE TABLE action(id,acknowledged,execution_status);CREATE TABLE tool_call(id,acknowledged);CREATE TABLE checkpoint_binding(checkpoint_id,checkpoint_sha256,pair_manifest_sha256,database_before_binding_sha256,bound_at);')
b.execute("INSERT INTO session VALUES('session_fixture','server_fixture','SUSPENDED_BOUNDARY','READY_QUERY',12,'action_fixture')")
b.execute("INSERT INTO boundary VALUES('session_fixture',1,2,'action_fixture','feedback_fixture')")
b.execute("INSERT INTO operation VALUES('feedback_fixture','COMPLETED')");b.execute("INSERT INTO action VALUES('action_fixture',1,'EXECUTED')");b.execute("INSERT INTO tool_call VALUES('tool_fixture',1)");b.commit();b.close()
world={'schema':p.WORLD_SCHEMA,'checkpoint_id':'checkpoint_fixture','world_id':'RBX01_R05_C02_DEV4','scenario_sha256':'a'*64,'native_life_id':life,'native_tick':42,
       'boundary':{'phase':'BOUNDARY','native_phase':'IDLE','completed_opportunities':1,'next_opportunity':2,'uncertain':False,
                   'last_action_id':'action_fixture','acknowledged_action_id':'action_fixture','last_feedback_operation_id':'feedback_fixture'},
       'S':{'nativeTick':42,'completedCycles':1,'cycle':1,'worldTime':12,'zero':0,'none':None},
       'body_pose':[0,0,0,1,0,0,0,1,0,0,0,1],'executed_actions':{'action_fixture':'EXECUTED'},'events':[],
       'physical':{'parts':[]},'rng':{'algorithm':'PREDECLARED_EVENT_TABLE_V1'},'controller':{'next_opportunity':2},
       'bridge':{'session_id':'session_fixture','server_id':'server_fixture','phase':'READY_QUERY','pending_count':0,'uncertain_count':0,'native_ticks_in_session':12}}
wp=work/'world.json';write(wp,world);proof=work/'closed.json';write(proof,{'lifeId':life,'ownerClosed':True,'writerDrained':True,'owner_returncode':0})
cfg=db.parent/'config.json';write(cfg,{'apiVersion':'RBX01.C02.v1','bind':'127.0.0.1','port':8895,'allowControl':False,'requestsPerMinute':60,'worldId':world['world_id'],'databaseFile':db.name,'tokenFile':'SYNTHETIC_TOKEN_NOT_OPENED','resumeAllowed':False})
calls=[]
def bind(path,checkpoint_id,anchor,*,pair_manifest_sha256=None):
    before=m.sha(path);db=sqlite3.connect(path);db.execute('INSERT INTO checkpoint_binding VALUES(?,?,?,?,?)',(checkpoint_id,anchor,pair_manifest_sha256,before,1));db.commit();db.close()
    result={'database_before_sha256':before,'database_after_sha256':m.sha(path),'checkpoint_id':checkpoint_id,'checkpoint_sha256':anchor,'pair_manifest_sha256':pair_manifest_sha256,'fixture_double_only':True};calls.append(result);return result
ledger=work/'ledger.json';write(ledger,{'schema':'DEE.RBX01.C02.prospective_native_budget.R01','limit':200000,'max_worlds':6,'intent':None,'consumed':12,'worlds':{life:{'cycles':1,'reserved':0,'consumed':12}}})
args=argparse.Namespace(root_run=True,native_root=native,world_file=wp,bridge_database=db,close_proof=proof,config=cfg,output=work/'sealed',resume_config=db.parent/'resume.json',ledger=ledger)
original_config=m.sha(cfg);native_before=m.native_manifest(native,p)
result=m.seal(args,persistence=p,bridge=types.SimpleNamespace(bind_checkpoint=bind));tests=[]
assert result['status']=='SEALED_BOUND_VERIFIED_NOT_REOPENED';tests.append('Whole-root pair sealed and verified with binder double')
assert m.native_manifest(native,p)==native_before and m.sha(cfg)==original_config;tests.append('Native files and original config preserved')
assert len(calls)==1 and calls[0]['checkpoint_sha256']!=result['pair']['manifest_sha256'];tests.append('External anchor is not final pair/self hash')
resume=json.loads(args.resume_config.read_text('utf8'));assert resume['resumeAllowed']is True and resume['databaseFile']==db.name and resume['tokenFile']=='SYNTHETIC_TOKEN_NOT_OPENED';tests.append('New resume config uses same database/token, original retained')
assert set(result['resume_arguments'])=={'world_checkpoint','world_checkpoint_sha256','bound_checkpoint_sha256'};tests.append('Three exact resume arguments emitted')
assert m.verify(args.output,p)['anchor_sha256']==result['anchor_sha256'];tests.append('Readonly verification repeats without rebinding')
try:m.seal(args,persistence=p,bridge=types.SimpleNamespace(bind_checkpoint=bind))
except ValueError:tests.append('Existing output/config refused without rebind')
else:raise AssertionError('Overwrite accepted')
report={'scope':'SYNTHETIC_OPAQUE_NATIVE_ROOT_AND_BINDER_DOUBLE_ONLY','tests':len(tests),'checks':tests,'fixture':str(work),
        'Native_imports':0,'Native_ticks':0,'MCP_calls':0,'real_bridge_bindings':0,'source_sha256':m.sha(ROOT/'control/sellar_vincular_C02.py')}
out=ROOT/'pruebas'/('SELLADO_VINCULO_SINTETICO_'+stamp+'.json');write(out,report)
print(json.dumps({'report':str(out),**report},ensure_ascii=False))
