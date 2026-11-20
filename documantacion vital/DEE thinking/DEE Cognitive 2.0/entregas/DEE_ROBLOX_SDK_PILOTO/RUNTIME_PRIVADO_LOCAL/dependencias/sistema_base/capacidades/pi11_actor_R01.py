"""PI11 persistent habitat and Native-gated renewal of an environmental permit.

Import is pure. No owner, world or engine is created. The existing Q1/Q2
geometry, clocks and banks are inherited, never installed/reset here. A Q2
output now determines whether an actual FI operation is performed or its
previous environmental certificate is reused. The correspondence is design,
not a discovered plan. Environment registers/certificates are NOT Native memory.
"""
from pathlib import Path
import hashlib,json,os

VERSION='DEE.PI11.persistent_habitat.native_continuation.R01'
KEY='DEE.Cognitive.PI11.persistent_habitat.native_continuation.R01'
FOLDER='PI11_HABITAT_ADAPTATIVO_R01'
PREPARE='eci01-pi11-preparar';EPISODE='eci01-pi11-episodio';STATE='eci01-pi11-estado'
MODES={PREPARE,EPISODE,STATE}
PROTOCOL=Path(__file__).with_name('PROTOCOLO_PI11_R01.json')
SCOPE=Path(__file__).with_name('PI11_EXPERIMENTO_R01.json')

def need(ok,message):
 if not ok:raise ValueError(message)
def sha(data):return hashlib.sha256(data).hexdigest()
def read(path):return json.loads(Path(path).read_text('utf-8-sig'))
def safe(v):return json.loads(json.dumps(v,ensure_ascii=False,allow_nan=False))
def encoded(v):
 text=json.dumps(safe(v),ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
 need(len(text.encode('utf8'))<=65536,'PI11 metadata exceeds64KB before journal/write')
 return text
def inherited():
 from capacidades import pi10_consulta_adaptativa_R02 as old
 return old
def identity(a):return inherited().identity(a)
def env():
 from capacidades import pi11_habitat_persistente_R01 as e
 return e
def home(directory,life):
 base=Path(directory).resolve(strict=True)
 need(base.is_dir()and base.name==life,'Exact current-life artifact directory required')
 for p in(base,*base.parents):need(not p.is_symlink()and not(getattr(p.lstat(),'st_file_attributes',0)&1024),'No linked artifact paths')
 return base/FOLDER
def protocol(a=None,material=False):
 data=PROTOCOL.read_bytes();p=json.loads(data);c=read(SCOPE)
 need(p.get('schema')=='DEE.PI11.persistent_habitat.protocol.R01'and p.get('N')==67,'Exact N67 PI11 protocol')
 need(c.get('schema')=='DEE.PI11.fixed_experiment_scope.R01'and c.get('protocol_sha256')==sha(data),'Exact PI11 scope/protocol binding')
 need(c.get('return_arm')in('real','nonfailure','yoked')and c.get('continuation')in('native','fixed'),'Explicit fixed arm, not a per-case policy')
 need(p.get('query_origin')==[24,12,12]and p.get('old_origin')==[8,40,50]and p.get('query_prefix')=='PI10.Q1.TC.R01','Inherited selector geometry only')
 need(p.get('max_ticks_per_episode')==2016 and 1<=p.get('max_opportunities',0)<=24 and p.get('habitat',{}).get('stock')==24,'Finite PI11 supply and horizon; PI10 stock untouched')
 need(len(p.get('events',[]))>=6 and p['events'][0]['at_offset']==0 and all(p['events'][i]['at_offset']<p['events'][i+1]['at_offset']for i in range(len(p['events'])-1)),'Prospective irregular tick-based environment')
 if c['return_arm']=='yoked':need(len(c.get('yoked_values',[]))==24 and all(type(x)is bool for x in c['yoked_values']),'Sealed independent feedback sequence')
 if a is not None:need(c.get('life_id')==identity(a)['life_id'],'Current PI11 life/scope mismatch')
 if material:
  need(p.get('status')in('SEALED_FOR_DEVELOPMENT','SEALED_FOR_EVALUATION'),'Seal before effects')
  for name,digest in p.get('sources_sha256',{}).items():need(Path(name).name==name and sha(Path(__file__).with_name(name).read_bytes())==digest,'Pinned PI11 source changed: '+name)
 return p,sha(data),c
def ancestors(a):
 e=dict(a.world.runtime.snapshot_metadata_entries);old=inherited()
 return {k:e[k]for k in (*old.PARENT_KEYS,old.KEY)if k in e}
def get(a):
 e=dict(a.world.runtime.snapshot_metadata_entries);need(KEY in e,'PI11 supply has not been explicitly admitted')
 m=json.loads(e[KEY]);need(m.get('version')==VERSION and m.get('ready')is True,'Exact reached PI11 preparation')
 return m
def record(a,m,directory,event):
 folder=home(directory,identity(a)['life_id']);folder.mkdir(exist_ok=True)
 line=(json.dumps(safe({'index':m['log_count'],'tick':int(a.tick),**event}),sort_keys=True,ensure_ascii=False,separators=(',',':'))+'\n').encode('utf8')
 proposed={**m,'log_count':m['log_count']+1,'log_chain_sha256':sha(bytes.fromhex(m['log_chain_sha256'])+line)}
 capsule=encoded(proposed)
 with(folder/'eventos.jsonl').open('ab')as f:f.write(line);f.flush();os.fsync(f.fileno())
 m.update(proposed);a.world.runtime.set_snapshot_metadata(KEY,capsule)
def validate_literal(row):need(isinstance(row,dict)and set(row)=={'modo'}and row.get('modo')in MODES,'PI11 mode only, no action/answer/wait override')
def validate(a,row):
 validate_literal(row);identity(a)
 if row['modo']==STATE:return
 p,ph,c=protocol(a,True);entries=dict(a.world.runtime.snapshot_metadata_entries)
 if row['modo']==PREPARE:
  need(KEY not in entries,'Never reset PI11 history or supply')
  old=json.loads(entries[inherited().KEY]);need(old.get('ready')and old.get('admitted')and old['ordinal']==14 and not old.get('pending')and not old.get('uncertain'),'Closed actual PI10 fourteen-offer history required')
  need(int(a.tick)==947395,'Preparation only from the confirmed current complete PI10 cut')
  return
 m=get(a);need(not m.get('pending')and not m.get('uncertain'),'Preserve/reconcile pending PI11 future')
 need(m['protocol_sha256']==ph and m['ordinal']==len(m['rows'])and m['ordinal']<p['max_opportunities'],'Frozen finite PI11 protocol/horizon exhausted or inconsistent')
def prepare(a,directory):
 validate(a,{'modo':PREPARE});p,ph,c=protocol(a,True);old=ancestors(a);before=inherited().physical(a);folder=home(directory,identity(a)['life_id'])
 need(not folder.exists(),'Existing/partial habitat cannot be reset')
 folder.mkdir();environment=env().init(folder,p,int(a.tick))
 m={'version':VERSION,'ready':True,'preparation_life_id':identity(a)['life_id'],'protocol_sha256':ph,'environment_start_tick':int(a.tick),'ordinal':0,'rows':[],'pending':None,'uncertain':False,'log_count':0,'log_chain_sha256':'00'*32,'preparation':'New finite external supply and fixed continuation transduction only; zero Native evolution; no anatomy/bank/clock reset'}
 record(a,m,directory,{'kind':'PERSISTENT_HABITAT_PREPARED','environment':environment,'external_control':c,'not_learning':True})
 need(before==inherited().physical(a)and old==ancestors(a),'Zero-tick environment admission changed Native/ancestor state')
 return {'version':VERSION,'ready':True,'before_tick':int(a.tick),'after_tick':int(a.tick),'new_native_ticks':0,'environment':environment,'PI10_history_and_stock_literal':True,'not_learning':True}

class CoupledTime:
 """Advance through owner/agenda while habitat follows every <=16tick block.

 Environment.advance integrates all intervening events/replenishments exactly.
 No adaptive wait, skipped Native agenda or event-aligned choice is performed.
 """
 def __init__(self,a,folder):
  from capacidades.pi07_regulacion_R01 import SafeAdapter
  self.a=a;self.safe=SafeAdapter(a);self.folder=folder;self.samples=[]
 def __getattr__(self,name):return getattr(self.a,name)
 def run_until(self,end):
  need(int(end)>=int(self.a.tick),'No rewind')
  while int(self.a.tick)<int(end):
   self.safe.run_until(min(int(end),int(self.a.tick)+16));value=env().advance(self.folder,int(self.a.tick))
   if not self.samples or int(self.a.tick)-self.samples[-1]['tick']>=256:self.samples.append({'tick':int(self.a.tick),'environment':value})

def episode(a,directory):
 validate(a,{'modo':EPISODE});p,ph,c=protocol(a,True);m=get(a);b=inherited();h,g,d,exact,receipt=b.native();old=ancestors(a);start=int(a.tick);i=identity(a);ordinal=m['ordinal'];folder=home(directory,i['life_id']);used=CoupledTime(a,folder)
 refs1=g.bank_observations(a,d,exact,tuple(p['query_origin']));refs2=g.bank_observations(a,d,exact,g.OLD_ORIGIN)
 need(refs1['reference_clocks'][0]%782==refs1['reference_clocks'][1]%782 and refs2['reference_clocks'][0]%782==refs2['reference_clocks'][1]%782,'Inherited reference phase mismatch; no repair')
 cal=g.two_selector_calendar(start,refs1['reference_clocks'][0],refs2['reference_clocks'][0]);one=cal['first'];two=cal['second'];q1=one['query_tick'];q2=two['query_tick'];requests=[];frames=[]
 m.update(pending={'ordinal':ordinal,'phase':'PERSISTENT_INTERACTION','q1':q1,'q2':q2},uncertain=True)
 record(a,m,directory,{'kind':'OPPORTUNITY_INTENT','ordinal':ordinal,'calendar':cal,'environment_before':env().status(folder),'external_control':c})
 try:
  used.run_until(q1-3);spec=env().environment_at(folder,int(a.tick))
  if spec['cue']!='none':b.submit(a,b.Z_CHANNEL if spec['cue']=='z'else b.X_CHANNEL,0,q1-2,requests)
  used.run_until(q1-1);sample=b.observe(a,b.PREVIEW);decoded=b.decode_sample(sample)
  need(decoded['valid'],'NULL actual preview preserved; no expected-bit replacement')
  offer=env().prepare_offer(folder,ordinal,sample,q1)
  datum=int(sample['state']);need(0<=datum<=3,'Actual state outside fixed two-bit codec')
  requests.extend(h.submit_query(a.world,q1,prefix=p['query_prefix']));b.submit(a,p['query_prefix']+'.datum',datum,q1+3,requests)
  used.run_until(q1+4);reader1=g.read_central(a,d,exact,tuple(p['query_origin']),q1);motor1=g.actual_motor(reader1['choice'])
  if motor1 is not None:requests.append(h.submit_motor_copy(a.world,motor1,one['seed_tick'],prefix=p['query_prefix']))
  access_available=env().can_access(folder,int(a.tick))
  question=b.submit(a,b.QUESTION_CHANNEL,0,one['seed_tick'],requests)if motor1==1 and access_available['allowed'] else None
  used.run_until(q1+8);question_observation=b.observe(a,b.QUESTION_READER);initial_receipts=b.receipts(a,requests);need(b.summary(initial_receipts)['all_terminal'],'Uncertain first-stage receipts')
  if question is not None:question=next(r for r in initial_receipts if r['id']==question['id'])
  applied=question is not None and question['receipt']['status']=='applied';signature=int(question_observation['state'])>0 and int(question_observation['semantic'])==1 and list(question_observation['direction'])==[1,0,0]
  released=bool(applied and signature)
  access=env().request_access(folder,ordinal,motor1,released,int(a.tick));released=bool(released and access['allowed'])
  bit=decoded['bit']if released else 0
  register={'sample_site':list(b.PREVIEW),'sample_tick':q1-1,'release_tick':q1+8,'age_ticks':9,'actual_observation':sample,'released':released,'released_bit':bit,'external_technical_register_not_Native_memory':True,'access':access,'material_question':question,'question_observation':question_observation}
  frames.append({'phase':'q1_eligibility','frame':g.trace_stencil(a,d,exact,tuple(p['query_origin']))})
  requests.extend(h.submit_query(a.world,q2,prefix=g.OLD_PREFIX));b.submit(a,g.OLD_PREFIX+'.datum',2*bit,q2+3,requests)
  used.run_until(q2+4);reader2=g.read_central(a,d,exact,g.OLD_ORIGIN,q2);motor2=g.actual_motor(reader2['choice']);used.run_until(q2+6);copied=None
  if motor2 is not None:copied=h.submit_motor_copy(a.world,motor2,two['seed_tick'],prefix=g.OLD_PREFIX);requests.append(copied)
  used.run_until(q2+8);copy_receipt=receipt(a.world.runtime.receipt(copied['id']))if copied else None;valid=motor2 is not None and copy_receipt is not None and copy_receipt['status']=='applied';route=(1 if motor2==1 else 0)if valid else None
  # Fixed public transduction, never consults target/regime/outcome/history.
  refresh=bool(valid and (c['continuation']=='fixed'or motor2==1))
  fi=None;used.run_until(q2+136)
  if refresh:
   from capacidades import pi05_transito_causal_R01 as baseline
   fi=baseline._fiplus(used,{'modo':baseline.FIPLUS,'izquierda':p['FI_operands'][0],'derecha':p['FI_operands'][1],'captura':'normal'},directory);requests.extend(fi['requests'])
  need(int(a.tick)<two['outcome_injection_tick'],'FI continuation exceeded fixed eligibility margin')
  consequence=env().execute(folder,ordinal,route,motor1 is not None,valid,None if fi is None else fi['old_q6_choice'],refresh,int(a.tick))
  actual=bool(consequence['actual_failed']);returned=actual if c['return_arm']=='real'else False if c['return_arm']=='nonfailure'else c['yoked_values'][ordinal]
  used.run_until(two['outcome_injection_tick']-1);requests.append(h.submit_generic_outcome(a.world,False,two['outcome_injection_tick'],prefix=g.OLD_PREFIX));used.run_until(two['settled_after_tick'])
  used.run_until(one['outcome_injection_tick']-1);frames.append({'phase':'before_q1_return','frame':g.trace_stencil(a,d,exact,tuple(p['query_origin']))})
  generic=h.submit_generic_outcome(a.world,returned,one['outcome_injection_tick'],prefix=p['query_prefix']);requests.append(generic)
  for tick in(one['outcome_injection_tick'],one['collision_tick'],one['contact_tick'],one['settled_after_tick']):
   used.run_until(tick);frames.append({'phase':'q1_return','tick':int(a.tick),'frame':g.trace_stencil(a,d,exact,tuple(p['query_origin'])),'references':g.bank_observations(a,d,exact,tuple(p['query_origin']))})
  complete=b.receipts(a,requests);counts=b.summary(complete);need(counts['all_terminal'],'Uncertain final Native receipt; no resend')
  need(ancestors(a)==old,'Inherited progress metadata changed; do not reset/normalize')
  need(0<=int(a.tick)-start<=2016,'Whole opportunity exceeded frozen bound')
  after={'q1':g.bank_observations(a,d,exact,tuple(p['query_origin'])),'q2':g.bank_observations(a,d,exact,g.OLD_ORIGIN)}
  result={'version':VERSION,'life_id':i['life_id'],'ordinal':ordinal,'before_tick':start,'after_tick':int(a.tick),'new_native_ticks':int(a.tick)-start,'calendar':cal,'environment_spec_at_input':spec,'offer':offer,'first_stage':{'reader':reader1,'motor':motor1,'register':register},'second_stage':{'reader':reader2,'motor':motor2,'command_valid':valid,'copy_receipt':copy_receipt,'route':route,'refresh_FI':refresh,'continuation_mode':c['continuation'],'FI':fi},'resource':consequence,'actual_failed':actual,'returned_failed':returned,'return_arm':c['return_arm'],'Q1_references_before':refs1,'Q2_references_before':refs2,'references_after':after,'requests':complete,'Native_inputs':counts,'trace_observations':frames,'environment_after':env().status(folder),'coupled_clock_samples':used.samples,'old_metadata_literal_unchanged':True,'physical_anchor':b.physical(a),'attribution':'Native output gates FI renewal/reuse; transduction/curriculum/physics clock are prepared. Cached RAW and certificate are external environmental resources, not Native memory. Q1 updates via fixed generic consequence and existing physical eligibility; Q2 gets fixed nonpunitive disposal.'}
  witness=folder/('episodio_%04d.json'%ordinal);data=(json.dumps(safe(result),ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf8')
  with witness.open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
  m['ordinal']+=1;m['rows'].append({'ordinal':ordinal,'before_tick':start,'after_tick':int(a.tick),'q1':reader1['choice'],'q2':reader2['choice'],'refresh_FI':refresh,'actual_failed':actual,'returned_failed':returned,'attributed_useful':consequence['attributed_useful'],'q1_delta':after['q1']['A_minus_B'],'witness':{'file':witness.name,'bytes':len(data),'sha256':sha(data)}});m.update(pending=None,uncertain=False)
  record(a,m,directory,{'kind':'OPPORTUNITY_COMPLETED','ordinal':ordinal,'witness':m['rows'][-1]['witness'],'Native_inputs':counts,'environment':env().status(folder)})
  return result
 except BaseException as exc:
  m.update(pending={'ordinal':ordinal,'tick':int(a.tick),'phase':'PRESERVED_INCOMPLETE','reason':type(exc).__name__},uncertain=True);a.world.runtime.set_snapshot_metadata(KEY,encoded(m));raise
def state(a):
 identity(a);entries=dict(a.world.runtime.snapshot_metadata_entries)
 return {'version':VERSION,'present':KEY in entries,'progress':json.loads(entries[KEY])if KEY in entries else None,'physical':inherited().physical(a),'new_native_ticks':0}
def dispatch(a,row,*,actuator='closed',directory=None):
 validate(a,row)
 if row['modo']==STATE:return state(a)
 need(actuator=='closed'and directory is not None,'Explicit closed local actuator')
 return prepare(a,directory)if row['modo']==PREPARE else episode(a,directory)
def uncertain(a):return KEY in dict(a.world.runtime.snapshot_metadata_entries)and get(a).get('uncertain',False)
def operational_dependencies(a,directory):
 v=state(a)
 if not v['present']:return v
 m=v['progress'];need(m['ordinal']==len(m['rows'])and not m.get('pending')and not m.get('uncertain'),'PI11 incomplete state must remain preserved')
 folder=home(directory,identity(a)['life_id']);need((folder/'eventos.jsonl').is_file(),'PI11 journal missing')
 for row in m['rows']:
  ref=row['witness'];f=folder/ref['file'];need(f.is_file()and f.stat().st_size==ref['bytes']and sha(f.read_bytes())==ref['sha256'],'PI11 immutable witness missing/changed')
 return {'version':VERSION,'ordinal':m['ordinal'],'environment':env().status(folder),'new_native_ticks':0,'PI10_ancestry_readonly':True}
def code_files():return tuple(Path(__file__).with_name(n)for n in('pi11_actor_R01.py','pi11_habitat_persistente_R01.py','PROTOCOLO_PI11_R01.json','PI11_EXPERIMENTO_R01.json'))
