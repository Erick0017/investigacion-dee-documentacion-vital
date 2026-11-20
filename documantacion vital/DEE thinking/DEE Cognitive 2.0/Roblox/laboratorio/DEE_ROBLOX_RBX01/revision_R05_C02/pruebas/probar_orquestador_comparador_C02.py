"""Synthetic stdlib only. No model/Roblox/Native/orchestrator.run call."""
from pathlib import Path
import copy,datetime,hashlib,importlib.util,json,sys,types
ROOT=Path(__file__).resolve().parents[1]
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
folder=ROOT/'pruebas'/('COMPARATOR_ORQ_FIXTURE_'+stamp);folder.mkdir()
source=ROOT/'control/orquestar_comparador_C02.py';spec=importlib.util.spec_from_file_location('_comparator_orq_test',source)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
tests=[]
def test(name,fn):fn();tests.append(name)
def fails(fn):
    try:fn()
    except(RuntimeError,ValueError):return
    raise AssertionError('Expected guard rejection')
def world():
    return {'schema':'DEE.RBX01.C02.world_checkpoint.v1','checkpoint_id':'checkpoint_test','world_id':m.WORLD_ID,
        'scenario_sha256':'a'*64,'native_life_id':'COMPARATOR_PROGRAMMED_test','native_tick':0,
        'S':{'nativeTick':0,'lifeId':'COMPARATOR_PROGRAMMED_test','completedCycles':16,'cycle':16,'zero':0,'none':None,'mode':'WAIT'},
        'boundary':{'phase':'BOUNDARY','native_phase':'IDLE','uncertain':False,'completed_opportunities':16,'next_opportunity':17,
                    'last_action_id':'action_test','acknowledged_action_id':'action_test','last_feedback_operation_id':'feedback_test'},
        'bridge':{'session_id':'session_test','server_id':'server_test','pending_count':0,'uncertain_count':0,'phase':'READY_QUERY'},
        'executed_actions':{'action_test':'EXECUTED'},'events':[],'pose_trace':[],
        'physical':{'parts':[{'path':'Body','cframe':[0.0]*12}]},'body_pose':[0.0]*12,
        'rng':{'algorithm':'PREDECLARED_EVENT_TABLE_V1'},'observer':{'segment':1},'close_requested':True}
test('Own comparator identity uses zero Native ticks',lambda:m.verify_world(world(),'PROGRAMMED','test'))
def reject_native():
    w=world();w['native_life_id']='ECI02_RBX01_NATIVE';fails(lambda:m.verify_world(w,'PROGRAMMED','test'))
test('Native identity cannot be passed off as comparator history',reject_native)
def exact():
    a=world();b=copy.deepcopy(a);b['observer']['segment']=2;b['close_requested']=False;b['S']['mode']='PROGRAMMED'
    assert m.compare_world(a,b,'PROGRAMMED','test')['equal']
    b['S']['zero']=None;fails(lambda:m.compare_world(a,b,'PROGRAMMED','test'))
test('Roundtrip allows declared observer changes but preserves zero versus NULL',exact)
def geometry():
    a=world();b=copy.deepcopy(a);b['body_pose'][0]=1e-6;assert m.compare_world(a,b,'PROGRAMMED','test')['equal']
    b['body_pose'][0]=.01;fails(lambda:m.compare_world(a,b,'PROGRAMMED','test'))
test('Geometry tolerance is fixed before runtime',geometry)
def closure():
    row={'schema':'DEE.RBX01.C02.comparator_closure.v1','status':'CLOSED','participant':'PROGRAMMED','run_id':'test',
         'writerDrained':True,'policyWriterClosed':True,'nativeOwnerOpened':False,'nativeTicks':0,'coherence_error':None,'coherence':{'coherent':True}}
    path=folder/'close.log';path.write_text(json.dumps(row),encoding='utf8');assert m.comparator_closure(path,0,'PROGRAMMED','test')
    assert m.comparator_closure(path,1,'PROGRAMMED','test')is None
    row['nativeOwnerOpened']=True;path.write_text(json.dumps(row),encoding='utf8');assert m.comparator_closure(path,0,'PROGRAMMED','test')is None
test('Comparator closure requires own clean writer and no Native owner',closure)
def sealing():
    directory=folder/'policy';directory.mkdir();output=folder/'output';output.mkdir()
    policy=directory/'POLICY_STATE_C02.json';policy.write_text('{"pending":null}\n',encoding='utf8')
    identity=directory/'RUNNER_IDENTITY_C02.json';identity.write_text('{}\n',encoding='utf8')
    db=folder/'closed_fixture.sqlite3';db.write_bytes(b'SYNTHETIC_OPAQUE_DATABASE_NOT_LIVE')
    wpath=folder/'world.json';wpath.write_text(json.dumps(world()),encoding='utf8')
    calls=[]
    def bind(path,cid,anchor):
        calls.append((str(path),cid,anchor));return {'checkpoint_id':cid,'checkpoint_sha256':anchor,'fixture_only':True}
    state={'session':{'id':'session_test','server_id':'server_test'},'binding':None}
    runner=types.SimpleNamespace(db_read=lambda p:state,compare_states=lambda d,p:{'status':'SUSPENDED_BOUNDARY'},
        source_pins=lambda:{'synthetic':'b'*64},load=lambda *args:types.SimpleNamespace(bind_checkpoint=bind))
    closure={'participant':'PROGRAMMED','run_id':'test','policy_checkpoint':{'sha256':m.sha(policy)}}
    result=m.seal_comparator(directory,{'databaseFile':db},wpath,closure,output,runner)
    pack=Path(result['directory']);manifest=json.loads((pack/'PAIR_COMPARATOR_C02.json').read_text('utf8'))
    assert len(calls)==1 and result['Native_backup']is False and manifest['new_Native_ticks']==0
    assert result['bound_checkpoint_sha256']==m.sha(pack/'ANCHOR_COMPARATOR_C02.json')
    assert result['bound_checkpoint_sha256']!=m.sha(pack/'PAIR_COMPARATOR_C02.json')
    for name,row in manifest['members'].items():assert m.sha(pack/name)==row['sha256']
test('Closed own-policy pair has noncircular anchor, exact members and no Native claim',sealing)
report={'scope':'SYNTHETIC_COMPARATOR_HELPERS_ONLY','tests':len(tests),'checks':tests,
        'Native_imports':0,'Native_ticks':0,'model_calls':0,'MCP_calls':0,'Studio_calls':0,
        'source_sha256':m.sha(source),'fixture':str(folder)}
out=ROOT/'pruebas'/('ORQUESTADOR_COMPARADOR_SINTETICO_'+stamp+'.json');out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'report':str(out),**report},ensure_ascii=False))
