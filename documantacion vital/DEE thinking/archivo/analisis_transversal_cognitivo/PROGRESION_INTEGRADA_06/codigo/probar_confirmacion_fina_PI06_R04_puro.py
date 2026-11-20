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
  if self.a.force_safety and self.a.tick>=self.a.safety_at:return [1]*3001
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

# R03 is imported against Fake dependencies. R04 receives exactly that frozen
# module, not a Native runtime. Its older operations still reach the same stub.
old=m;cap.pi06_ambiente_R03=old;sys.modules['capacidades.pi06_ambiente_R03']=old
spec=importlib.util.spec_from_file_location('PI06_R04_fake',H/'pi06_ambiente_fino_R04.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
proto,fixture=m.protocol()
arms={}
for mode,life in((m.FINE,m.FINE_LIFE),(m.CONTROL,m.CONTROL_LIFE)):
 a=Adapter();a.life=life;a.safety_at=826452;before=copy.deepcopy(a.raw)
 literal={'modo':mode,'captura':'global'};m.validate(a,literal)
 test('validation_read_only_'+mode,a.requests==[]and a.world.interfaces==[])
 result=m.dispatch(a,literal,directory=Path('FAKE_ONLY')/life);arms[mode]=(a,result)
 test('same61_interfaces_'+mode,len(a.world.interfaces)==61)
 test('SEM1_state1_only_'+mode,all(i.channel.state==1 and i.channel.semantic==1 for i in a.world.interfaces))
 test('all_inherited_SEM4_preserved_'+mode,all(a.raw[site]==raw for site,raw in before.items()))
 test('finite67_'+mode,a.tick==826516 and result['new_native_ticks']==67 and not result['host_safety_stop'])
 test('check_every_boundary_'+mode,[r['tick']for r in result['host_safety_observations']]==list(range(826449,826517)))
 test('capture_all68_boundaries_'+mode,result['external_global_capture']['ticks']==list(range(826449,826517))and result['missing_planned_capture_ticks']==[])
 test('admissions_resolved_'+mode,result['birth_inputs']['terminal_all_known']and not result['admission_stop'])
 test('repeated_interfaces_rejected_'+mode,any(i.name==fixture['births'][0]['channel']for i in a.world.interfaces))
 try:m.validate(a,literal)
 except ValueError:pass
 else:raise AssertionError('Second declaration accepted')
a,result=arms[m.FINE]
test('fine61_individual58applied3occupied_FAKE_contract',len(a.requests)==61 and result['birth_inputs']['applied']==58 and result['birth_inputs']['rejected_occupied']==3)
test('same_fixed_payload_time_seed',all(r['payload']==7 and r['tick']==826451 for r in a.requests)and proto['fixture_literal_unchanged']['seed']==61001)
def iv(a):return[(i.name,vars(i.channel.injection_site),vars(i.channel.direction),i.channel.state,i.channel.semantic)for i in a.world.interfaces]
test('control_zero_births_same_anatomy',arms[m.CONTROL][0].requests==[]and iv(arms[m.FINE][0])==iv(arms[m.CONTROL][0]))
a=Adapter();a.life=m.FINE_LIFE;a.force_safety=True;a.safety_at=826452
result=m.dispatch(a,{'modo':m.FINE,'captura':'global'},directory=Path('FAKE_ONLY')/a.life)
test('first_crossing_stops_at3_not67',a.tick==826452 and result['new_native_ticks']==3 and result['host_safety_stop'])
test('no_advance_after_host_stop',result['external_global_capture']['ticks']==list(range(826449,826453))and result['missing_planned_capture_ticks']==list(range(826453,826517)))
test('same61_dose_despite_early_stop',result['birth_inputs']['unique_requested']==61 and result['birth_inputs']['applied']==58 and result['birth_inputs']['rejected_occupied']==3)
for mode,life in((m.FINE,m.CONTROL_LIFE),(m.CONTROL,m.FINE_LIFE),(m.CONTROL,'ECI02_PI03_REPRO_PI04_PI05_PI06_R03_OTHER')):
 a=Adapter();a.life=life
 try:m.validate(a,{'modo':mode,'captura':'normal'})
 except ValueError:test('reject_wrong_id_'+mode+'_'+life,True)
 else:raise AssertionError('Wrong fixed life allowed')
a=Adapter();a.life=m.FINE_LIFE;a.tick+=1
try:m.validate(a,{'modo':m.FINE,'captura':'normal'})
except ValueError:test('reject_changed_source_tick',True)
else:raise AssertionError('Wrong age allowed')
for row in({'modo':m.FINE,'captura':'global','target':1},{'modo':m.CONTROL,'captura':'fragmentar'}):
 try:m.validate_literal(row)
 except ValueError:test('reject_hidden_target_or_capture_'+str(len(tests)),True)
 else:raise AssertionError('Invalid literal allowed')
row={'modo':'eci01-pi06-evolucion','ticks':6,'captura':'normal'}
test('all_old_operations_exact_delegation',m.dispatch(a,row,directory=Path('x'))==('OLD_DISPATCH',a,row,{'actuator':'closed','directory':Path('x')}))
rs=importlib.util.spec_from_file_location('PI06_R04_runner_fake',H/'ejecutar_fases_PI06_R04.py');runner=importlib.util.module_from_spec(rs);rs.loader.exec_module(runner)
for filename,expected in runner.R04_PLANS.items():
 path=P/'control'/filename;data=path.read_bytes();plan=json.loads(data)
 test('exact_plan_'+filename,runner.r04_plan_enabled(expected[1],path,data,plan['steps'],826449))
 test('reject_plan_hash_change_'+filename,not runner.r04_plan_enabled(expected[1],path,data+b' ',plan['steps'],826449))
 test('reject_cross_arm_life_'+filename,not runner.r04_plan_enabled('ECI02_PI03_REPRO_PI04_PI05_PI06_OTHER',path,data,plan['steps'],826449))
frozen={'pi06_ambiente_R03.py':'9d06316836e24f915da74116d9b70f3eafa51bd0062934d974ee2a08ca8e99c6','ejecutar_fases_PI06_R03.py':'13c6da19e2a65e58e42709f260392b86798e6665681805881cce4d89eb5caed2','pi06_interrupcion_R02.py':'80643a9d81ee92225350d3bc81a94d7e65c685e4c1b1f27b932cd9956454ef72'}
for name,h in frozen.items():test('old_source_unchanged_'+name,hashlib.sha256((H/name).read_bytes()).hexdigest()==h)
out=P/'control/CONFIRMACION_FINA_PI06_R04_PRUEBAS_PURAS.json'
with out.open('x',encoding='utf8')as f:json.dump({'schema':'DEE.PI06.R04.fake_fine_safety_tests.v1','tests':tests,'passed':len(tests),'Native_executed':False,'new_code':{name:hashlib.sha256((H/name).read_bytes()).hexdigest()for name in('pi06_ambiente_fino_R04.py','ejecutar_fases_PI06_R04.py')},'scope':'Fake admission, exact source/identity/plan guards, every-boundary capture/safety and unchanged delegation only. No Native cloud dynamics, Native observer passivity, functionality or learned regulation tested.'},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'proof':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'passed':len(tests),'Native_executed':False}))
