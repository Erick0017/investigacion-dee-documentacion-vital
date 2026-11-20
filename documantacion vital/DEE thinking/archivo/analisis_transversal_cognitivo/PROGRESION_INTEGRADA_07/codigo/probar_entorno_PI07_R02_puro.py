"""Pure R02 administration/transport/recorder-constructor checks; no DEE."""
from pathlib import Path
from types import SimpleNamespace,ModuleType
import ast,copy,hashlib,importlib.util,json,sys
P=Path(__file__).resolve().parents[1];H=P/'codigo';OUT=P/'control/PRUEBAS_ENTORNO_R02_FAKE';OUT.mkdir(exist_ok=False);tests=[]
cap=ModuleType('capacidades');cap.__path__=[str(H)];sys.modules['capacidades']=cap
file=H/'pi07_regulacion_R02.py';sp=importlib.util.spec_from_file_location('PI07_R02_pure',file);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def test(name,ok):
 if not ok:raise AssertionError(name)
 tests.append({'name':name,'passed':True})
p,ph=m.protocol(material=True);test('actual_frozen_evaluation_protocol',ph=='44ff1cc6a9f0634edcf56273b5956e39665c0dbb89f21e5bf36c1650b730b544')
test('same_native_actor_functions',m._read is m.body._read and m._emit is m.body._emit and m._motor is m.body._motor and m._helper is m.body._helper)
test('new_KEY_distinct_from_R1',m.KEY!=m.body.KEY and m.FOLDER!=m.body.FOLDER)
source=[True,False,False,True,False,True,True,False,True,False,False,True]
plan={'schema':'DEE.PI07.yoked_return.roll5.v1','roll':5,'roll_direction':'source_plus_5','source_failed':source,'values':[source[(i+5)%12]for i in range(12)],'source_evidence_sha256':'f'*64}
text=json.dumps(plan,sort_keys=True,separators=(',',':'));h=m._sha(text.encode('utf8'));test('exact_source_plus5_yoke',m._plan(text,h)['values']==[source[i]for i in(5,6,7,8,9,10,11,0,1,2,3,4)])
wrong=copy.deepcopy(plan);wrong['values']=[source[(i-5)%12]for i in range(12)];bad=json.dumps(wrong)
try:m._plan(bad,m._sha(bad.encode('utf8')))
except ValueError:test('reject_opposite_rotation',True)
else:raise AssertionError('Opposite rotation accepted')
try:m._plan(text,'0'*64)
except ValueError:test('reject_unbound_plan_hash',True)
else:raise AssertionError('Changed plan accepted')
for arm in('real','none'):
 m.validate_literal({'modo':m.START,'brazo':arm,'registro_global':False})
m.validate_literal({'modo':m.START,'brazo':'yoked','registro_global':False,'plan':text,'plan_sha256':h})
m.validate_literal({'modo':m.EPISODE,'sensor_ablation':True,'actuator_ablation':False});test('new_explicit_API_valid',True)
for i,row in enumerate(({'modo':m.START,'brazo':'real','registro_global':1},{'modo':m.EPISODE,'sensor_ablation':1},{'modo':m.EPISODE,'target':'protect'},{'modo':m.CONTROL,'brazo':'real','registro_global':False})):
 try:m.validate_literal(row)
 except ValueError:test('reject_hidden_or_nonbool_control_'+str(i),True)
 else:raise AssertionError('Unsafe literal accepted')
for i in range(12):test('yoke_return_'+str(i),m._return({'ordinal':i,'control':{'arm':'yoked','from_ordinal':0,'yoked_values':plan['values']}},False)==plan['values'][i])
test('none_is_fixed_nonfailure',m._return({'control':{'arm':'none'}},True)is False)
test('real_uses_actual_consequence',m._return({'control':{'arm':'real'}},True)is True)
# Actual d60 constructor, no simulated physics and no arrays captured.
fakecap=OUT/'FAKE_SOURCE/capacidades';fakecap.mkdir(parents=True);(fakecap/'observador_global_PI05_R01.py').write_bytes((H/'observador_global_PI05_R01.py').read_bytes())
oldfile=m.__file__;m.__file__=str(fakecap/'pi07_regulacion_R02.py');underlying=SimpleNamespace(tick=900,world=SimpleNamespace())
used,safe,rec=m._instrumented(underlying,{'ordinal':0,'instrumentation':{'global_enabled':True},'control':{'max_ordinal':28}},p,1000,{'life_id':'FAKE_ONLY_NO_NATIVE'})
test('actual_global_constructor31frames',len(rec.ticks)==31 and rec.config['N']==67)
test('seven_anchors_including_first_frame',len(rec.anchors)==7 and rec.ticks[0]==997 and rec.ticks[0]in rec.anchors)
test('all_fixed_sensor_Q_message_contact_parent_return_windows',all(centre+d in rec.ticks for centre in(999,1004,1008,1072,1144,1408,1410)for d in(-2,-1,0,1,2)))
test('capture_does_not_change_scalar_sensor_or_actor',used.base is safe and m._read is m.body._read and m._emit is m.body._emit)
closed=rec.close();test('constructor_test_has_no_frames_or_physics',closed['captured_frames']==0)
for ordinal in(2,12):
 used,safe,rec=m._instrumented(underlying,{'ordinal':ordinal,'instrumentation':{'global_enabled':True},'control':{'max_ordinal':28}},p,1000,{'life_id':'FAKE_ONLY_NO_NATIVE'})
 test('not_every_episode_globally_recorded_'+str(ordinal),rec is None)
used,safe,rec=m._instrumented(underlying,{'ordinal':0,'instrumentation':{'global_enabled':False},'control':{'max_ordinal':12}},p,1000,{'life_id':'FAKE_ONLY_NO_NATIVE'});test('disabled_external_recorder_creates_none',rec is None)
m.__file__=oldfile
# Fake metadata transport: zero Native methods exist, so an advance would fail.
decode=lambda x:json.loads(x);encode=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'))
oldnative=m._native;oldbodynative=m.body._native;oldphysical=m._physical
fake_native=lambda:(None,None,None,decode,encode);m._native=fake_native;m.body._native=fake_native
class Runtime:
 dimension=67
 def __init__(self,life):
  self.metadata={m.body.SYSTEM_KEY:encode({'life_id':life,'profile':'fisica_directa'}),m.body.KEY:encode({'version':m.body.VERSION,'ready':True,'ordinal':0,'protocol_sha256':m.R1_PROTOCOL_SHA,'pending':None,'uncertain':False,'rows':[],'life_id':'OLD_PREPARATION_LIFE','prepared_tick':824911})}
 @property
 def snapshot_metadata_entries(self):return list(self.metadata.items())
 def set_snapshot_metadata(self,key,value):self.metadata[key]=value
for arm in('real','none','yoked'):
 life='ECI02_PI03_REPRO_PI04_PI05_PI07_FAKE_'+arm;home=OUT/life;home.mkdir();rt=Runtime(life);a=SimpleNamespace(tick=824914,world=SimpleNamespace(runtime=rt));m._physical=lambda a:{'N':67,'tick':a.tick,'RAW_sha256':'FAKE_SAME','clocks_sha256':'FAKE_SAME'}
 before=dict(rt.metadata);row={'modo':m.START,'brazo':arm,'registro_global':False}
 if arm=='yoked':row.update(plan=text,plan_sha256=h)
 result=m.initialize(a,row,home);env=m._get(a)
 test('zero_Native_admin_admission_'+arm,result['new_native_ticks']==0 and a.tick==824914 and result['requests']==[])
 test('R1_literal_and_SYSTEM_preserved_'+arm,all(rt.metadata[k]==v for k,v in before.items())and set(rt.metadata)==set(before)|{m.KEY})
 test('new_environment_journal_ready_'+arm,env['ordinal']==0 and env['log_count']==1 and env['ready']and not env['uncertain'])
 try:m.initialize(a,row,home)
 except ValueError:test('reject_reinitialization_'+arm,True)
 else:raise AssertionError('Environment reset accepted')
m._native=oldnative;m.body._native=oldbodynative;m._physical=oldphysical
test('R1_source_and_protocol_unchanged',m._sha(Path(m.body.__file__).read_bytes())==m.R1_SOURCE_SHA and m._sha(m.body.PROTOCOL.read_bytes())==m.R1_PROTOCOL_SHA)
test('no_DEE_or_app_import',not any(n=='app'or n.startswith(('app.','dee_thinking'))for n in sys.modules))
out=P/'control/PI07_R02_PRUEBAS_PURAS_PRE_NATIVE.json'
with out.open('x',encoding='utf8')as f:json.dump({'schema':'DEE.PI07.R02.pure_administration_recording_tests.v1','tests':tests,'passed':len(tests),'module_sha256':m._sha(file.read_bytes()),'protocol_sha256':ph,
 'Native_executed':False,'S7_or_product_modified':False,'scope':'Pure external admission/configuration, exact actor aliases, +5 control, actual recorder constructor with no captured arrays, and Fake metadata transport only. Not Native learning/passivity/conservation or experimental replication.'},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'proof':str(out),'sha256':m._sha(out.read_bytes()),'passed':len(tests),'Native_executed':False}))
