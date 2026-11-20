"""Full Fake control flow, no Native physics/owner/source deployment."""
from pathlib import Path
from types import ModuleType,SimpleNamespace
import hashlib,importlib.util,json,sys
H=Path(__file__).resolve().parent;P=H.parent;OUT=P/'control/ACCESO_FI_FAKE_R01';OUT.mkdir(exist_ok=False)
# Exact dependency copied for hash validation, never executed as a Native call.
dep=H/'pi05_transito_causal_R01.py'
if not dep.exists():dep.write_bytes((P/'estados/candidato/sistema/capacidades'/dep.name).read_bytes())
cap=ModuleType('capacidades');cap.__path__=[str(H)];sys.modules['capacidades']=cap
s=importlib.util.spec_from_file_location('access_FI_pure',H/'pi07_acceso_FI_regulado_R01.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
tests=[]
def check(name,v):
 if not v:raise AssertionError(name)
 tests.append({'name':name,'passed':True})
p,ph=m.protocol(True);check('actual_frozen_protocol',p['max_queries']==8 and p['read_relative_FI_query']==4)
for row in({'modo':m.QUERY,'izquierda':14,'derecha':3},{'modo':m.QUERY,'izquierda':2,'derecha':12,'actuator_ablation':True},{'modo':m.QUERY,'izquierda':6,'derecha':6}):m.validate_literal(row)
for i,row in enumerate(({'modo':m.QUERY,'izquierda':21,'derecha':0},{'modo':m.QUERY,'izquierda':0,'derecha':0,'expected':0},{'modo':m.QUERY,'izquierda':3,'derecha':4,'sensor_ablation':1})):
 try:m.validate_literal(row)
 except ValueError:check('reject_override_or_domain_'+str(i),True)
 else:raise AssertionError('Unsafe access accepted')
decode=json.loads;encode=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'));native=lambda:(None,None,lambda x:x,decode,encode)
m.body._native=native;m.regulation._native=native;m.regulation.previous._native=native
life='ECI02_PI03_REPRO_PI04_PI05_PI07_FAKE_ACCESS';root=OUT/life;root.mkdir()
oldreg={'version':m.regulation.VERSION,'ready':True,'admitted':True,'ordinal':12,'pending':None,'uncertain':False}
class Runtime:
 def __init__(self):self.metadata={m.regulation.KEY:encode(oldreg)};self.receipts={};self.channels=[]
 @property
 def snapshot_metadata_entries(self):return list(self.metadata.items())
 def set_snapshot_metadata(self,k,v):self.metadata[k]=v
 def receipt(self,rid):return self.receipts[rid]
rt=Runtime();a=SimpleNamespace(tick=100,world=SimpleNamespace(runtime=rt));original=dict(rt.metadata)
def submit(name,payload,tick):
 rid=len(rt.receipts)+1;rt.receipts[rid]={'id':rid,'status':'applied','requested_tick':tick};rt.channels.append(name);return SimpleNamespace(id=rid)
a.world.submit=submit;m.regulation._identity=lambda a:{'life_id':life};m.regulation._selected=lambda a:False
physical=lambda a:{'N':67,'tick':a.tick,'RAW_sha256':'FAKE_NO_PHYSICS','clocks_sha256':'FAKE_NO_PHYSICS'};m.body._physical=physical
class Safe:
 def __init__(self,a):self.a=a
 def run_until(self,tick):self.a.tick=tick
m.body.SafeAdapter=Safe
m.body._observe=lambda a,site:{'raw':0,'state':0,'clock':a.tick,'semantic':0,'direction':[0,0,0],'s_reg':0}
returned=[]
def request(world,name,payload,tick):
 r=world.submit(name,payload,tick);return{'id':r.id,'channel':name,'payload':payload,'requested_tick':tick}
def schedule(now,clock,laps):
 q=now+4;return{'query_tick':q,'seed_tick':q+7,'outcome_injection_tick':q+408,'collision_tick':q+409,'contact_tick':q+410}
helper=SimpleNamespace(schedule_trial=schedule,submit_query=lambda w,q,prefix:[request(w,prefix+'.query'+str(i),0,q+i)for i in range(3)],submit_motor_copy=lambda w,motor,tick,prefix:request(w,prefix+'.motor',motor,tick),at=lambda origin,offset:tuple((origin[i]+offset[i])%67 for i in range(3)))
def generic(w,failed,tick,prefix):returned.append(failed);return request(w,prefix+'.generic',int(failed),tick)
helper.submit_generic_outcome=generic;m.body._helper=lambda:helper
m.body._read=lambda a,q:{'choice':0,'tick':a.tick,'fixed_Fake':True}
FI_values=iter((1,-1,0,None));fake=ModuleType('capacidades.pi05_transito_causal_R01');fake.FIPLUS='eci01-pi05-fiplus'
def fiplus(used,row,directory):
 q=int(a.tick)+56;value=next(FI_values);req=[request(a.world,'FAKE_FI'+str(i),0,int(a.tick)+2+i%10)for i in range(176)];used.run_until(q+142)
 return{'early_physical_choice':value,'old_q6_choice':value,'requests':req,'calendar':{'query_tick':q},'FAKE_ONLY':True}
fake._fiplus=fiplus;sys.modules['capacidades.pi05_transito_causal_R01']=fake;setattr(cap,'pi05_transito_causal_R01',fake)
init=m.initialize(a,root);check('zero_native_admission',init['new_native_ticks']==0 and a.tick==100)
for i,(left,right,actual)in enumerate(((14,3,1),(2,11,-1),(6,6,0),(6,6,None))):
 result=m.query(a,{'modo':m.QUERY,'izquierda':left,'derecha':right},root)
 check('preserve_actual_early_'+str(i),result['early_physical_choice']is actual if actual is None else type(result['early_physical_choice'])is int and result['early_physical_choice']==actual)
 check('old_R03_literal_unchanged_'+str(i),rt.metadata[m.regulation.KEY]==original[m.regulation.KEY])
 check('no_message_or_cue_'+str(i),not any(name.startswith('PI07.environment.')for name in rt.channels))
check('signed_and_zero_judgment_only_after_function',returned==[False,False,False,True])
check('material_zero_not_NULL',m._get(a)['rows'][2]['early_physical_choice']==0 and m._get(a)['rows'][3]['early_physical_choice']is None)
state=m._get(a);state['ordinal']=8;m._save(a,state)
try:m.validate(a,{'modo':m.QUERY,'izquierda':1,'derecha':0})
except ValueError:check('finite_eight_query_budget',True)
else:raise AssertionError('Unlimited query budget')
check('no_DEE_or_app_import',not any(n=='app'or n.startswith(('app.','dee_thinking'))for n in sys.modules))
out=P/'control/ACCESO_FI_PI07_PRUEBAS_PURAS_R01.json'
with out.open('x',encoding='utf8')as f:json.dump({'schema':'DEE.PI07.regulated_FI_access.fake_flow.v1','passed':len(tests),'tests':tests,'module_sha256':hashlib.sha256((H/'pi07_acceso_FI_regulado_R01.py').read_bytes()).hexdigest(),'protocol_sha256':ph,'Native_executed':False,'S7_or_product_modified':False,'scope':'Fake entire flow only: exact module/hash protocol, signed/zero/NULL handling, immutable oldprogress and no synthetic cue/message. No physical efficacy, acquired protection, access recovery or original API retention claimed.'},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'proof':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'passed':len(tests),'Native_executed':False}))
