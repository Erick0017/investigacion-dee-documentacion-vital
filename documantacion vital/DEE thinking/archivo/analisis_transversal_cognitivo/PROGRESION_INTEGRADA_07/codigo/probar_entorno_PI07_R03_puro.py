"""Pure guard/actor/recorder checks; no DEE, S7 or product mutation."""
from pathlib import Path
from types import ModuleType,SimpleNamespace
import ast,hashlib,importlib.util,json,sys
H=Path(__file__).resolve().parent;P=H.parent;OUT=P/'control/PRUEBAS_ENTORNO_R03_FAKE';OUT.mkdir(exist_ok=False)
cap=ModuleType('capacidades');cap.__path__=[str(H)];sys.modules['capacidades']=cap
spec=importlib.util.spec_from_file_location('PI07_R03_pure',H/'pi07_regulacion_R03.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
tests=[]
def check(name,value):
 if not value:raise AssertionError(name)
 tests.append({'name':name,'passed':True})
p,ph=m.protocol(True);check('exact_immutable_protocol',ph==m.PROTOCOL_SHA)
check('original_read_motor_and_TC_helper',m._read is m.body._read and m._motor is m.body._motor and m._helper is m.body._helper)
check('no_new_bank_anatomy',m.ORIGIN==m.body.ORIGIN and len(p['schedule'])==18 and p['initial_reference_payloads']=={'A':0,'B':2})
check('new_distinct_progress_only',len({m.KEY,m.body.KEY,m.previous.KEY})==3)
check('perpendicular_fixed_geometry',m.ACTUATOR==(53,48,56)and m.MESSAGE_READER==(54,48,56)and m.SINK==(56,48,56))
calls=[];orig=m._submit;m._submit=lambda a,name,payload,tick,requests,**kw:calls.append((name,payload,tick,kw))or{'id':7}
for motor in(None,-1,0):check('no_pulse_'+str(motor),m._emit(None,motor,100,[],False)is None)
check('actuator_cut',m._emit(None,1,100,[],True)is None)
check('single_fixed_native_output_pulse',m._emit(None,1,100,[],False)=={'id':7}and calls==[(m.PULSE_CHANNEL,0,100,{'site':(53,48,56),'direction':(-1,0,0)})]);m._submit=orig
m.validate_literal({'modo':m.PREPARE,'prefijo_sha256':'e'*64});m.validate_literal({'modo':m.START,'clase':'viability','brazo':'real','registro_global':True})
auth={'schema':'DEE.PI07.R03.closed_calibration.authorization.v1','protocol_sha256':ph,'evaluation_authorized':True,'calibration_proofs':[{'forced_action':v,'path':'control/'+v+'.json','sha256':str(i)*64,'closed':True,'viability_passed':True}for i,v in enumerate(('pulso','nada'),1)]}
text=json.dumps(auth,sort_keys=True);h=m._sha(text.encode());m.validate_literal({'modo':m.START,'clase':'evaluation','brazo':'real','registro_global':True,'autorizacion':text,'autorizacion_sha256':h});check('external_closed_auth_schema',True)
for i,row in enumerate(({'modo':m.EPISODE,'condicion':'threat'},{'modo':m.EPISODE,'forzar':'pulso'},{'modo':m.START,'clase':'evaluation','brazo':'real','registro_global':True},{'modo':m.CALIBRATE,'forzar':'nada','target':1},{'modo':m.PREPARE,'prefijo_sha256':'not-a-manifest'},{'modo':m.START,'clase':'viability','brazo':'none','registro_global':True})):
 try:m.validate_literal(row)
 except ValueError:check('reject_unsafe_literal_'+str(i),True)
 else:raise AssertionError('Unsafe literal accepted')
bad={**auth,'evaluation_authorized':False};textbad=json.dumps(bad)
try:m._authorization(textbad,m._sha(textbad.encode()))
except ValueError:check('failed_calibration_not_authorized',True)
else:raise AssertionError('Failed calibration accepted')
# Use actual validated codec constructor, without capture/arrays or Native.
fakecap=OUT/'FAKE_SOURCE/capacidades';fakecap.mkdir(parents=True);(fakecap/'observador_global_PI05_R01.py').write_bytes((H/'observador_global_PI05_R01.py').read_bytes())
oldfile=m.__file__;m.__file__=str(fakecap/'pi07_regulacion_R03.py');a=SimpleNamespace(tick=900,world=SimpleNamespace())
for role,ordinal,enabled,wanted in(('viability',0,True,True),('viability',1,True,False),('evaluation',1,True,True),('evaluation',0,True,False),('evaluation',14,False,False)):
 used,safe,rec=m._instrumented(a,{'ordinal':ordinal,'role':role,'instrumentation':{'global_enabled':enabled}},p,1000,{'life_id':'FAKE_NO_NATIVE'})
 check('fixed_recording_plan_'+role+str(ordinal)+str(enabled),(rec is not None)==wanted)
 if rec is not None:
  check('31frames3anchors_'+role+str(ordinal),len(rec.ticks)==31 and rec.anchors=={997,1144,1412})
  check('constructor_no_frames_'+role+str(ordinal),rec.close()['captured_frames']==0)
m.__file__=oldfile
check('legacy_metadata_not_assigned_by_episode',all(s not in ast.get_source_segment((H/'pi07_regulacion_R03.py').read_text('utf8'),node)for node in ast.walk(ast.parse((H/'pi07_regulacion_R03.py').read_text('utf8')))if isinstance(node,ast.FunctionDef)and node.name=='episode'for s in('set_snapshot_metadata(body.KEY','set_snapshot_metadata(previous.KEY')))
check('no_DEE_or_app_import',not any(n=='app'or n.startswith(('app.','dee_thinking'))for n in sys.modules))
out=P/'control/PI07_R03_PRUEBAS_PURAS_PRE_NATIVE.json'
with out.open('x',encoding='utf8')as f:json.dump({'schema':'DEE.PI07.R03.pure_guards_recording_tests.v1','tests':tests,'passed':len(tests),'module_sha256':m._sha((H/'pi07_regulacion_R03.py').read_bytes()),'protocol_sha256':ph,'Native_executed':False,'S7_or_product_modified':False,'scope':'Pure fixed transducer, guard/schema and exact recorder constructor tests only. No Native viability, learning, passivity, conservation or adoption.'},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'proof':str(out),'sha256':m._sha(out.read_bytes()),'passed':len(tests),'Native_executed':False}))
