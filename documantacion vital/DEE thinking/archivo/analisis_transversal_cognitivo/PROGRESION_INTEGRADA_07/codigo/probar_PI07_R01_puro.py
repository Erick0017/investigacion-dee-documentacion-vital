"""Pure transport/guard tests, NOT Native physics, learning or viability."""
from pathlib import Path
from types import SimpleNamespace
import ast,hashlib,importlib.util,json,sys
P=Path(__file__).resolve().parents[1];H=P/'codigo';tests=[]
def test(name,ok):
 if not ok:raise AssertionError(name)
 tests.append({'name':name,'passed':True})
p=H/'pi07_regulacion_R01.py';spec=importlib.util.spec_from_file_location('PI07_pure',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
proto,ph=m.protocol(material=True);test('actual_protocol1db5_parsed',ph=='1db513e8f38607ed9e41929fc49afada1be584875d6744e718ccdd9b628cb949'and len(proto['schedule'])==28)
test('final_origin_RAW_clear_candidate',m.ORIGIN==(8,40,50))
frame=m.frame_rows();by={tuple(v['site']):v for v in frame}
test('33_deduplicated_legal_P0_births',len(frame)==len(by)==33)
test('unlearned_references0_2',by[m.at((-1,-1,0))]['payload']==0 and by[m.at((1,-1,0))]['payload']==2)
test('six_fixed_output_stops',all(by[m.at((3*x,3,3*z))]['state']==0 and by[m.at((3*x,3,3*z))]['semantic']==4 for x in(-1,0,1)for z in(0,-1)))
test('old_Q_and_guards_not_installed_or_touched',not {(19,54,5),(18,53,5),(20,53,5),(19,53,20),(19,57,5)}&set(by))
for row in({'modo':m.PREPARE},{'modo':m.STATE},{'modo':m.EPISODE},{'modo':m.EPISODE,'actuator_ablation':True},{'modo':m.CALIBRATE,'forzar':'pulso'},{'modo':m.CALIBRATE,'forzar':'nada'},{'modo':m.WAIT,'ticks':2000}):m.validate_literal(row)
test('announced_literal_API_valid',True)
for i,row in enumerate(({'modo':m.EPISODE,'accion':'pulso'},{'modo':m.EPISODE,'condicion':'threat'},{'modo':m.EPISODE,'actuator_ablation':1},{'modo':m.WAIT,'ticks':2001},{'modo':m.CALIBRATE,'forzar':'correcta'})):
 try:m.validate_literal(row)
 except ValueError:test('reject_hidden_or_unbounded_argument_'+str(i),True)
 else:raise AssertionError('Bad literal accepted')
test('zero_no_pulse_is_declared_motor_minus',m._motor(0)==-1 and m._motor(-1)==-1 and m._motor(1)==1)
test('NULL_not_zero_or_action',m._motor(None)is None and m._motor(False)is None)
class World:
 def __init__(self):self.calls=[]
 def submit(self,name,payload,tick):self.calls.append((name,payload,tick));return SimpleNamespace(id=len(self.calls))
a=SimpleNamespace(tick=100,world=World());requests=[]
for motor in(None,-1):test('no_pulse_for_'+str(motor),m._emit(a,motor,101,requests,False)is None)
test('ablation_after_choice_omits_actual_input',m._emit(a,1,101,requests,True)is None and not a.world.calls)
r=m._emit(a,1,101,requests,False);test('one_fixed_legal_pulse',r['channel']=='PI07.actuator.fixed_minusZ.R01'and r['site']==[52,48,51]and r['direction']==[0,0,-1]and r['payload']==0 and r['requested_tick']==101 and len(a.world.calls)==1)
emit=next(n for n in ast.parse(p.read_bytes()).body if isinstance(n,ast.FunctionDef)and n.name=='_emit')
test('actuator_API_has_no_context_or_target',[v.arg for v in emit.args.args]==['a','motor','seed','requests','ablation'])
test('actuator_body_never_reads_sensor_environment_or_bank',not {'spec','cue','sensor','target','expected','bank','origin'}&{v.id for v in ast.walk(emit)if isinstance(v,ast.Name)})
realobserve=m._observe
for choice in(-1,0,1):
 m._observe=lambda a,site,c=choice:{'state':1,'semantic':1,'direction':[c,1,0]};r=m._read(SimpleNamespace(tick=104),100);test('fixed_reader_'+str(choice),r['choice']==choice)
m._observe=lambda a,site:{'state':0,'semantic':1,'direction':[0,1,0]};test('inactive_reader_is_NULL',m._read(SimpleNamespace(tick=104),100)['choice']is None);m._observe=realobserve
for now in(824914,825000,825305,826000):
 cal=m._helper().schedule_trial(now+16,now+16,6);q=cal['query_tick']
 test('finite_future_calendar_'+str(now),q-2>now and cal['seed_tick']==q+7 and cal['outcome_injection_tick']==q+408 and cal['contact_tick']+2-now<=1300 and q%782==763 and(q+192)%391==173)
requests=[{'id':i,'receipt':{'id':i,'requested_tick':101,'status':s}}for i,s in enumerate(('applied','rejected_conflict','rejected_conflict','rejected_occupied'),1)]
summary=m._summary(requests,100,110);test('resolved_conflict_and_occupied_are_known_outcomes',summary['unique_requested']==4 and summary['rejected']==3 and summary['all_terminal'])
requests.append({'id':5,'receipt':{'id':5,'requested_tick':101,'status':'queued'}});test('queued_is_not_terminal',not m._summary(requests,100,110)['all_terminal'])
oldidentity=m._identity;oldget=m._get;m._identity=lambda a:{'life_id':'ECI02_PI03_REPRO_PI04_PI05_PI07_VIAB_01'};m._get=lambda a:{'ready':True,'protocol_sha256':ph,'pending':None,'uncertain':False,'ordinal':0}
try:m.validate(SimpleNamespace(),{'modo':m.EPISODE})
except ValueError:test('viability_does_not_authorize_evaluation',True)
else:raise AssertionError('Unsealed evaluation accepted')
m.validate(SimpleNamespace(),{'modo':m.CALIBRATE,'forzar':'pulso'});test('explicit_forced_VIAB_allowed',True)
m._identity=lambda a:{'life_id':'ECI02_PI03_REPRO_PI04_PI05_PI07_DEV_01'}
try:m.validate(SimpleNamespace(),{'modo':m.CALIBRATE,'forzar':'pulso'})
except ValueError:test('forced_action_not_allowed_in_candidate',True)
else:raise AssertionError('Hidden operator action allowed')
m._identity=oldidentity;m._get=oldget
class Underlying:
 def __init__(self):self.tick=0;self.steps=[];self.world=SimpleNamespace(runtime=SimpleNamespace(raw_copy=lambda:[1]*10))
 def run_until(self,t):self.steps.append(t-self.tick);self.tick=t
u=Underlying();s=m.SafeAdapter(u);s.run_until(100);test('only_official_adapter_steps_at_most32',max(u.steps)<=32 and u.tick==100)
u=Underlying();u.world.runtime.raw_copy=lambda:[1]*3001;s=m.SafeAdapter(u)
try:s.run_until(100)
except m.HostSafetyStop:test('host_safety_preserves_at_first_observed_crossing',u.tick==32)
else:raise AssertionError('Host safety did not stop')
test('no_Native_or_app_import',not any(v=='app'or v.startswith(('app.','dee_thinking'))for v in sys.modules))
out=P/'control/PI07_R01_PRUEBAS_PURAS.json'
with out.open('x',encoding='utf8')as f:json.dump({'schema':'DEE.PI07.pure_control_transport_tests.R01','tests':tests,'passed':len(tests),'module_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'protocol_sha256':ph,
 'Native_executed':False,'source_system_or_product_modified':False,'scope':'Pure geometry/calendar/transport/guards only. No Native admission/collision/polarity/FI usefulness, observer passivity, physical viability, acquisition or conservation was tested.'},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'proof':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'passed':len(tests),'Native_executed':False}))
