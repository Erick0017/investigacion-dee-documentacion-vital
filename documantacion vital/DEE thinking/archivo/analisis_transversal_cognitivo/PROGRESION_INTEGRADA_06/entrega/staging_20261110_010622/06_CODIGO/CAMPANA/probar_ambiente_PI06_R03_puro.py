"""R03 exact fixture/interfaces with fake Native admission and host safety.

Only fake objects implement the already-read occupied-birth contract. No real
Native physics, relaxation, functionality, learning or passivity is tested.
"""
from pathlib import Path
import copy,hashlib,importlib.util,json,sys,types
P=Path(__file__).resolve().parents[1];H=P/'codigo';tests=[]
def test(n,v):
 if not v:raise AssertionError(n)
 tests.append({'name':n,'passed':True})
previous=types.ModuleType('capacidades.pi06_interrupcion_R02');previous.MODES={'eci01-pi06-fiplus','eci01-pi06-evolucion','eci01-pi06-interrupcion'}
previous.validate_literal=lambda row:('OLD_LITERAL',row);previous.validate=lambda a,row:('OLD_VALIDATE',a,row);previous.dispatch=lambda a,row,**kw:('OLD_DISPATCH',a,row,kw)
previous.operational_dependencies=lambda a,d:{'present':False};previous.uncertain=lambda a:False;previous.code_files=lambda:[]
def diagnostic(a):
 if not a.life.startswith('ECI02_PI03_REPRO_PI04_PI05_PI06_'):raise ValueError('Explicit fake diagnostic only')
 return {'life_id':a.life}
previous.old=types.SimpleNamespace(_diagnostic=diagnostic)
cap=types.ModuleType('capacidades');cap.pi06_interrupcion_R02=previous;sys.modules['capacidades']=cap;sys.modules[previous.__name__]=previous
class Plain:pass
class Coord:
 def __init__(self,*v):self.x,self.y,self.z=v
class Direction:
 def __init__(self,*v):self.dx,self.dy,self.dz=v
native=types.ModuleType('dee_thinking._native');native.ChannelSpec=Plain;native.InterfaceSpec=Plain;native.Coordinate=Coord;native.Direction=Direction
dee=types.ModuleType('dee_thinking');dee._native=native;con=types.ModuleType('dee_thinking.consolidated');con.exact_receipt=lambda v:copy.deepcopy(v)
sys.modules['dee_thinking']=dee;sys.modules[native.__name__]=native;sys.modules[con.__name__]=con
app=types.ModuleType('app');tools=types.ModuleType('app.native_tools');tools.physical=lambda world:{**world.a.source,'tick':world.a.tick};tools.observe=lambda world,site:{'raw':str(world.a.raw.get(tuple(site),0)),'clock':str(world.a.tick),'site':list(site)}
app.native_tools=tools;sys.modules['app']=app;sys.modules[tools.__name__]=tools
class Recorder:
 def __init__(self,target,**kw):self.frames=[]
 def capture(self,a):
  if a.tick not in self.frames:self.frames.append(a.tick)
 def close(self):return {'FAKE_ONLY':True,'captured_frames':len(self.frames),'ticks':self.frames}
class CaptureAdapter:
 def __init__(self,a,*,ticks,recorder):self.a=a;self.ticks=ticks;self.recorder=recorder
 def run_until(self,target):
  for t in self.ticks:
   if self.a.tick<t<=target:self.a.run_until(t)
   if self.a.tick==t:self.recorder.capture(self.a)
  if self.a.tick<target:self.a.run_until(target)
baseline=types.ModuleType('capacidades.pi05_transito_causal_R01');baseline._capture_module=lambda:types.SimpleNamespace(GlobalRecorder=Recorder,CapturingAdapter=CaptureAdapter)
cap.pi05_transito_causal_R01=baseline;sys.modules[baseline.__name__]=baseline
spec=importlib.util.spec_from_file_location('PI06_R03_fake',H/'pi06_ambiente_R03.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);proto,fixture=m.protocol()
test('exact_fixture0_4_seed61001_61_sources',len(fixture['births'])==61 and fixture['seed']==61001 and fixture['Bernoulli_probability']==0.4)
class Runtime:
 def __init__(self,a):self.a=a
 def receipt(self,rid):return self.a.receipts[rid]
 def raw_copy(self):
  if self.a.force_safety and self.a.tick>=826516:return [1]*3001
  return list(self.a.raw.values())
class World:
 def __init__(self,a):self.a=a;self.runtime=Runtime(a);self.interfaces=[]
 def declare_interface(self,i):self.interfaces.append(i)
 def submit(self,name,payload,tick):
  rid=len(self.a.requests)+1;spec=next(x.channel for x in self.interfaces if x.name==name);site=(spec.injection_site.x,spec.injection_site.y,spec.injection_site.z)
  self.a.requests.append({'id':rid,'name':name,'payload':payload,'tick':tick,'site':site});self.a.receipts[rid]={'id':rid,'status':'queued','requested_tick':tick};return types.SimpleNamespace(id=rid)
class Adapter:
 def __init__(self):
  self.life='ECI02_PI03_REPRO_PI04_PI05_PI06_R03_FAKE';self.source=m.SOURCE;self.tick=826449;self.raw={tuple(b['site']):int(b['snapshot_RAW_before'])for b in fixture['births']if int(b['snapshot_RAW_before'])!=0};self.receipts={};self.requests=[];self.force_safety=False;self.world=World(self)
 def run_until(self,t):
  for request in self.requests:
   if request['tick']<=t and self.receipts[request['id']]['status']=='queued':
    occupied=self.raw.get(request['site'],0)!=0;self.receipts[request['id']]['status']='rejected_occupied'if occupied else'applied'
    if not occupied:self.raw[request['site']]=1 # fake Native birth, not host/module write
  self.tick=t
arms={}
for condition in('nube','control'):
 a=Adapter();before=copy.deepcopy(a.raw);row={'modo':m.ENV,'condicion':condition,'captura':'global'};m.validate(a,row)
 test('validation_has_no_birth_or_anatomy_'+condition,a.requests==[]and a.world.interfaces==[])
 result=m.dispatch(a,row,directory=Path('FAKE_ONLY')/a.life);arms[condition]=(a,result)
 test('same61_declared_'+condition,len(a.world.interfaces)==61 and result['common_interfaces_declared']==61)
 test('all_SEM1_state1_no_SEM4_birth_'+condition,all(i.channel.state==1 and i.channel.semantic==1 for i in a.world.interfaces))
 test('finite268_no_repair_'+condition,a.tick==826717 and not result['host_safety_stop'])
 test('inherited_SEM4_raw_preserved_'+condition,all(a.raw[site]==raw for site,raw in before.items()))
 test('known_terminal_admission_'+condition,result['birth_inputs']['terminal_all_known']and not result['admission_stop'])
test('61_individual_58applied_3occupied_FAKE_contract',len(arms['nube'][0].requests)==61 and arms['nube'][1]['birth_inputs']['applied']==58 and arms['nube'][1]['birth_inputs']['rejected_occupied']==3)
def interface_values(a):return[(i.name,vars(i.channel.injection_site),vars(i.channel.direction),i.channel.state,i.channel.semantic,i.channel.allow_experience,i.channel.allow_probe)for i in a.world.interfaces]
test('control_zero_submits_but_same_interfaces',arms['control'][0].requests==[] and interface_values(arms['nube'][0])==interface_values(arms['control'][0]))
a=Adapter();a.force_safety=True;result=m.dispatch(a,{'modo':m.ENV,'condicion':'nube','captura':'normal'},directory=Path('FAKE_ONLY')/a.life)
test('host_safety_stops_at67_not268',result['host_safety_stop']and result['new_native_ticks']==67 and result['host_safety_is_not_autoregulation'])
a=Adapter();a.tick=826915;result=m.dispatch(a,{'modo':m.EVOLVE,'ticks':271,'captura':'global'},directory=Path('FAKE_ONLY')/a.life)
test('new271_evolution_has_no_birth',result['new_native_ticks']==271 and result['new_inputs_scheduled']==0 and a.requests==[])
for count in(1,274,2000):
 a=Adapter();a.tick=826915;result=m.dispatch(a,{'modo':m.EVOLVE,'ticks':count,'captura':'global'},directory=Path('FAKE_ONLY')/a.life)
 test('bounded_legal_evolution_'+str(count),result['new_native_ticks']==count and a.requests==[] and result['external_global_capture']['captured_frames']<=42)
try:m.validate_literal({'modo':m.EVOLVE,'ticks':2001,'captura':'global'})
except ValueError:test('reject_evolution2001',True)
else:raise AssertionError('Unbounded evolution accepted')
oldrow={'modo':'eci01-pi06-evolucion','ticks':6,'captura':'normal'};test('old_R02_operations_exact_delegation',m.dispatch(a,oldrow,directory=Path('x'))==('OLD_DISPATCH',a,oldrow,{'actuator':'closed','directory':Path('x')}))
rs=importlib.util.spec_from_file_location('PI06_R03_runner_pure',H/'ejecutar_fases_PI06_R03.py');runner=importlib.util.module_from_spec(rs);rs.loader.exec_module(runner)
outcome={'before_tick':10,'after_tick':208};literal={'modo':'eci01-pi06-fiplus','condicion':'intacto'}
requests=[{'id':i,'receipt':{'id':i,'requested_tick':10+i,'status':'applied'if i<174 else'rejected_occupied'}}for i in range(1,177)]
row={'Native_inputs':{'unique_requested':176,'applied':173,'rejected_or_other':3},'requests':requests}
test('R03_FI_terminal_occupied_is_reportable',runner.r03_fi_terminal_admission(row,outcome,literal,True))
test('nonR03_remains_strict',not runner.r03_fi_terminal_admission(row,outcome,literal,False))
requests[-1]['receipt']['status']='queued';test('pending_FI_never_accepted',not runner.r03_fi_terminal_admission(row,outcome,literal,True))
requests[-1]['receipt']['status']='rejected_invalid';test('other_FI_rejection_never_accepted',not runner.r03_fi_terminal_admission(row,outcome,literal,True))
for filename in runner.R03_PLANS:
 path=P/'control'/filename;data=path.read_bytes();plan=json.loads(data)
 test('final_R05_plan_'+filename,runner.r03_plan_enabled('ECI02_PI03_REPRO_PI04_PI05_PI06_R03_FAKE',path,data,plan['steps'],826449))
 test('reject_nonR03_life_'+filename,not runner.r03_plan_enabled('ECI02_PI03_REPRO_PI04_PI05_PI06_OLD',path,data,plan['steps'],826449))
 test('reject_modified_plan_'+filename,not runner.r03_plan_enabled('ECI02_PI03_REPRO_PI04_PI05_PI06_R03_FAKE',path,data+b' ',plan['steps'],826449))
out=P/'control/AMBIENTE_PI06_R03_PRUEBAS_PURAS_R06_FINAL.json'
with out.open('x',encoding='utf8')as f:json.dump({'schema':'DEE.PI06.R03.fake_interface_safety_tests.v1','tests':tests,'passed':len(tests),'Native_executed':False,'module_sha256':hashlib.sha256((H/'pi06_ambiente_R03.py').read_bytes()).hexdigest(),
 'runner_file':'ejecutar_fases_PI06_R03.py','runner_sha256':hashlib.sha256((H/'ejecutar_fases_PI06_R03.py').read_bytes()).hexdigest(),
 'scope':'Fake individual-birth occupied contract and host controls only; does not verify Native cloud dynamics, useful function, observer passivity, regulation or actual58/3 admission.'},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'proof':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'passed':len(tests),'Native_executed':False}))
