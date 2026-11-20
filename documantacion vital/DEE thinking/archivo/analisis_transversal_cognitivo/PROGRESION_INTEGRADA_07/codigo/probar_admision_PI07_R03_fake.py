"""Fake metadata/interface transaction tests, never Native physics."""
from pathlib import Path
from types import ModuleType,SimpleNamespace
import hashlib,importlib.util,json,sys
H=Path(__file__).resolve().parent;P=H.parent;OUT=P/'control/ADMISION_R03_FAKE';OUT.mkdir(exist_ok=False)
pkg=ModuleType('capacidades');pkg.__path__=[str(H)];sys.modules['capacidades']=pkg
spec=importlib.util.spec_from_file_location('R03_admission_FAKE',H/'pi07_regulacion_R03.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
tests=[]
def check(n,v):
 if not v:raise AssertionError(n)
 tests.append({'name':n,'passed':True})
encode=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'));decode=json.loads
native=lambda:(None,None,lambda x:x,decode,encode)
m._native=native;m.body._native=native;m.previous._native=native
life='ECI02_PI03_REPRO_PI04_PI05_PI07_FAKE_R03';home=OUT/life;home.mkdir()
class Runtime:
 dimension=67
 def __init__(self):
  self.metadata={m.body.SYSTEM_KEY:encode({'life_id':life,'profile':'fisica_directa'}),m.body.KEY:encode({'version':m.body.VERSION,'ready':True,'ordinal':0,'pending':None,'uncertain':False,'rows':[]}),m.previous.KEY:encode({'version':m.previous.VERSION,'ready':True,'ordinal':28,'pending':None,'uncertain':False,'body_P0':{'preparation_life_id':'P0_LITERAL'}})};self.channel_names=[];self.receipts={}
 @property
 def snapshot_metadata_entries(self):return list(self.metadata.items())
 def set_snapshot_metadata(self,k,v):self.metadata[k]=v
 def receipt(self,i):return self.receipts[i]
rt=Runtime();a=SimpleNamespace(tick=846517,world=SimpleNamespace(runtime=rt));old=dict(rt.metadata)
def declare(w,name,*args):
 if name in rt.channel_names:raise ValueError('used namespace')
 rt.channel_names.append(name)
def submit(name,payload,tick):
 i=len(rt.receipts)+1;rt.receipts[i]={'id':i,'status':'applied','requested_tick':tick};return SimpleNamespace(id=i)
a.world.submit=submit;m.body._declare=declare
m._observe=lambda a,site:{'raw':0,'clock':a.tick,'state':0,'s_reg':0,'semantic':0,'direction':[0,0,0]}
class Safe:
 def __init__(self,a):self.a=a;self.safety=[]
 def run_until(self,tick):self.a.tick=tick
m.body.SafeAdapter=Safe;m._physical=lambda a:{'N':67,'tick':a.tick,'RAW_sha256':'FAKE_NO_PHYSICS','clocks_sha256':'FAKE_NO_PHYSICS'}
result=m.prepare(a,{'modo':m.PREPARE,'prefijo_sha256':'e'*64},home)
check('one_fixed_legal_sink_request',result['Native_inputs']['unique_requested']==1 and result['Native_inputs']['applied']==1)
check('declared_three_new_interfaces',set(rt.channel_names)=={m.SINK_CHANNEL,m.MESSAGE_CHANNEL,m.PULSE_CHANNEL})
check('finite_preparation_three_fake_ticks',result['new_native_ticks']==3 and a.tick==846520)
check('historical_literals_preserved',all(rt.metadata[k]==v for k,v in old.items()))
prepared=m._get(a);check('ready_unadmitted_no_bank_reset',prepared['ready']and not prepared['admitted']and prepared['ordinal']==0)
result=m.initialize(a,{'modo':m.START,'clase':'viability','brazo':'real','registro_global':True},home)
check('zero_tick_external_admission',result['new_native_ticks']==0 and result['requests']==[] and a.tick==846520)
check('both_old_metadata_literals_after_admission',all(rt.metadata[k]==v for k,v in old.items()))
m.validate(a,{'modo':m.CALIBRATE,'forzar':'pulso'});check('calibration_first_force_allowed',True)
state=m._get(a);state['forced_action']='pulso';m._save(a,state)
try:m.validate(a,{'modo':m.CALIBRATE,'forzar':'nada'})
except ValueError:check('reject_switching_force_between_cases',True)
else:raise AssertionError('force switch accepted')
try:m.initialize(a,{'modo':m.START,'clase':'viability','brazo':'real','registro_global':True},home)
except ValueError:check('reject_reset_or_readmission',True)
else:raise AssertionError('reset accepted')
try:m.validate(a,{'modo':m.EPISODE})
except ValueError:check('calibration_not_evaluation',True)
else:raise AssertionError('evaluation without external gate accepted')
check('no_DEE_or_app_import',not any(n=='app'or n.startswith(('app.','dee_thinking'))for n in sys.modules))
output=P/'control/PI07_R03_ADMISION_FAKE_PRE_NATIVE.json'
with output.open('x',encoding='utf8')as f:json.dump({'schema':'DEE.PI07.R03.fake_admission_transactions.v1','tests':tests,'passed':len(tests),'module_sha256':hashlib.sha256((H/'pi07_regulacion_R03.py').read_bytes()).hexdigest(),'Native_executed':False,'S7_or_product_modified':False,'scope':'Fake metadata, declarations, request and clock stand-ins only. Not Native birth/admission, viability, learning or observation passivity.'},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'proof':str(output),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'passed':len(tests),'Native_executed':False}))
