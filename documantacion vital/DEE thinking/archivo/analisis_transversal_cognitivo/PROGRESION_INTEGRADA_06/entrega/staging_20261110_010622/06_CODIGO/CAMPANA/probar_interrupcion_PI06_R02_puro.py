"""R02 interface/scheduler/guard tests with fake objects only, no Native physics."""
from pathlib import Path
import copy,hashlib,importlib.util,json,sys,types
P=Path(__file__).resolve().parents[1];H=P/'codigo';tests=[];oldcalls=[]
def test(name,value):
 if not value:raise AssertionError(name)
 tests.append({'name':name,'passed':True})
def must_fail(name,fn):
 try:fn()
 except ValueError:test(name,True)
 else:raise AssertionError(name)
old=types.ModuleType('capacidades.pi06_organizacion_R01');old.MODES={'eci01-pi06-fiplus','eci01-pi06-evolucion'}
old.validate_literal=lambda row:oldcalls.append(('literal',row));old.validate=lambda a,row:oldcalls.append(('validate',a,row))
old.dispatch=lambda a,row,**kw:('OLD_EXACT_RESULT',a,row,kw);old.operational_dependencies=lambda a,d:{'present':False};old.uncertain=lambda a:False;old.code_files=lambda:[H/'pi06_organizacion_R01.py']
def diagnostic(a):
 if not a.life.startswith('ECI02_PI03_REPRO_PI04_PI05_PI06_'):raise ValueError('Fake diagnostic identity refuses actual principal')
 return {'life_id':a.life}
old._diagnostic=diagnostic
cap=types.ModuleType('capacidades');cap.pi06_organizacion_R01=old
sys.modules['capacidades']=cap;sys.modules[old.__name__]=old
class Plain:pass
class Coord:
 def __init__(self,*v):self.x,self.y,self.z=v
class Dir:
 def __init__(self,*v):self.dx,self.dy,self.dz=v
native=types.ModuleType('dee_thinking._native');native.ChannelSpec=Plain;native.InterfaceSpec=Plain;native.Coordinate=Coord;native.Direction=Dir
dee=types.ModuleType('dee_thinking');dee._native=native;con=types.ModuleType('dee_thinking.consolidated');con.exact_receipt=lambda r:copy.deepcopy(r)
sys.modules['dee_thinking']=dee;sys.modules[native.__name__]=native;sys.modules[con.__name__]=con
app=types.ModuleType('app');tools=types.ModuleType('app.native_tools')
def physical(world):return {**world.adapter.source,'tick':world.adapter.tick}
def observe(world,site):return {'raw':world.adapter.raw.get(tuple(site),0),'clock':world.adapter.tick,'site':list(site)}
tools.physical=physical;tools.observe=observe;app.native_tools=tools;sys.modules['app']=app;sys.modules[tools.__name__]=tools
class Recorder:
 def __init__(self,target,**kw):self.kw=kw;self.frames=[]
 def capture(self,a):self.frames.append(a.tick)
 def close(self):return {'FAKE_ONLY':True,'captured_frames':len(self.frames),'ticks':self.frames}
class CaptureAdapter:
 def __init__(self,a,*,ticks,recorder):self.a=a;self.ticks=ticks;self.recorder=recorder
 def run_until(self,target):
  for t in self.ticks:
   if self.a.tick<t<=target:self.a.run_until(t)
   if self.a.tick==t:self.recorder.capture(self.a)
fakecapture=types.SimpleNamespace(GlobalRecorder=Recorder,CapturingAdapter=CaptureAdapter)
baseline=types.ModuleType('capacidades.pi05_transito_causal_R01');baseline._capture_module=lambda:fakecapture;cap.pi05_transito_causal_R01=baseline;sys.modules[baseline.__name__]=baseline
spec=importlib.util.spec_from_file_location('PI06_R02_pure',H/'pi06_interrupcion_R02.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
proto,ph=m.protocol();test('actual_protocol_and_R01_hashes_verified',len(ph)==64 and proto['advance_ticks']==3)
class Runtime:
 def __init__(self,a):self.a=a
 def receipt(self,rid):return {'id':rid,'status':'applied'if self.a.tick>=self.a.pending['tick']else'queued','requested_tick':self.a.pending['tick']}
class World:
 def __init__(self,a):self.adapter=a;self.interfaces=[];self.runtime=Runtime(a)
 def declare_interface(self,i):self.interfaces.append(i);self.adapter.declarations.append(i)
 def submit(self,name,payload,tick):self.adapter.pending={'name':name,'payload':payload,'tick':tick};return types.SimpleNamespace(id=1)
class Adapter:
 def __init__(self):
  self.life='ECI02_PI03_REPRO_PI04_PI05_PI06_FAKE';self.tick=826449;self.source=proto['source'];self.raw={tuple(m.CARRIER):1224979098644774913};self.declarations=[];self.pending=None;self.advances=[];self.world=World(self)
 def run_until(self,t):self.advances.append((self.tick,t));self.tick=t
for condition in('contraflujo','sham'):
 for capture in('normal','global'):
  a=Adapter();row={'modo':m.INTERRUPT,'condicion':condition,'captura':capture};m.validate(a,row)
  test('validation_schedules_no_input_'+condition+capture,a.tick==826449 and a.pending is None and a.declarations==[])
  out=m.dispatch(a,row,directory=Path('FAKE_ONLY')/a.life);c=a.declarations[0].channel
  test('exact_legal_packet_'+condition+capture,len(a.declarations)==1 and a.pending['payload']==0 and a.pending['tick']==826451 and c.state==1 and c.semantic==1 and(c.direction.dx,c.direction.dy,c.direction.dz)==(0,0,-1))
  test('fixed_source_'+condition+capture,[c.injection_site.x,c.injection_site.y,c.injection_site.z]==m.SITES[condition])
  test('three_legal_ticks_one_receipt_'+condition+capture,a.tick==826452 and out['new_native_ticks']==3 and out['Native_inputs']=={'unique_requested':1,'applied':1,'rejected_or_other':0})
  test('host_never_assigns_fake_RAW_clock_'+condition+capture,a.raw=={tuple(m.CARRIER):1224979098644774913})
  if capture=='global':test('four_prospective_global_boundaries_'+condition,out['external_global_capture']['ticks']==[826449,826450,826451,826452])
must_fail('reject_source_RAW_nonzero',lambda:(lambda a:(a.raw.update({tuple(m.SITES['contraflujo']):4<<60}),m.validate(a,{'modo':m.INTERRUPT,'condicion':'contraflujo','captura':'normal'})))(Adapter()))
must_fail('reject_carrier_missing',lambda:(lambda a:(a.raw.clear(),m.validate(a,{'modo':m.INTERRUPT,'condicion':'sham','captura':'normal'})))(Adapter()))
must_fail('reject_wrong_age',lambda:(lambda a:(setattr(a,'tick',826450),m.validate(a,{'modo':m.INTERRUPT,'condicion':'sham','captura':'normal'})))(Adapter()))
must_fail('reject_expected_answer_argument',lambda:m.validate_literal({'modo':m.INTERRUPT,'condicion':'sham','captura':'normal','expected':1}))
must_fail('reject_new_condition',lambda:m.validate_literal({'modo':m.INTERRUPT,'condicion':'repair','captura':'normal'}))
a=Adapter();row={'modo':'eci01-pi06-evolucion','ticks':6,'captura':'normal'}
test('old_dispatch_exact_delegation',m.dispatch(a,row,directory=Path('unchanged'))==('OLD_EXACT_RESULT',a,row,{'actuator':'closed','directory':Path('unchanged')}))
test('old_dependency_and_uncertainty_delegation',m.operational_dependencies(a,Path('x'))['present']is False and m.uncertain(a)is False)
out=P/'control/INTERRUPCION_PI06_R02_PRUEBAS_PURAS.json';proof={'schema':'DEE.PI06.counterflow.fake_tests.R02','tests':tests,'passed':len(tests),'module_sha256':hashlib.sha256((H/'pi06_interrupcion_R02.py').read_bytes()).hexdigest(),'Native_executed':False,
 'actual_physics_tested':False,'scope':'Fake interface requests/scheduler/observer only. No annihilation, restored response, sham innocuity or causal success is asserted.'}
with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'proof':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'passed':len(tests),'Native_executed':False}))
