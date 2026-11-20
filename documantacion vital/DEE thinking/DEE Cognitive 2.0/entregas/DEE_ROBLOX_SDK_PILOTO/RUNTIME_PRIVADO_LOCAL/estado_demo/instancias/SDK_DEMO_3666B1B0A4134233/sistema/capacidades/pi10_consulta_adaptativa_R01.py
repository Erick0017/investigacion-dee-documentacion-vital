"""PI10 two-trace adaptive question apparatus on an existing complete N67 life.

No engine/world/owner is opened on import. Architecture, calendars and host
resource law are P0. Only explicitly supplied Native-owner operations mutate
the physical continuation. No bank/clock/RAW setters or answer policy exist.
"""
from pathlib import Path
import copy,hashlib,itertools,json,os

VERSION='DEE.PI10.adaptive_query.two_native_traces.R01'
KEY='DEE.Cognitive.PI10.adaptive_query.two_native_traces.R01'
FOLDER='PI10_CONSULTA_ADAPTATIVA_R01'
PREPARE='eci01-pi10-preparar';ADMIT='eci01-pi10-admitir'
EPISODE='eci01-pi10-episodio';CALIBRATE='eci01-pi10-calibrar';STATE='eci01-pi10-estado'
MODES={PREPARE,ADMIT,EPISODE,CALIBRATE,STATE}
PROTOCOL=Path(__file__).with_name('PROTOCOLO_PI10_R01.json')
SCOPE=Path(__file__).with_name('PI10_EXPERIMENTO_R01.json')
PREVIEW=(30,40,30);PREVIEW_Z=(30,40,29);PREVIEW_X=(29,40,30)
QUESTION=(33,40,30);QUESTION_READER=(34,40,30)
DEVICE_CHECK_SITES=(PREVIEW,PREVIEW_Z,PREVIEW_X,QUESTION,QUESTION_READER,(32,40,30),(30,40,32),(35,40,30))
HISTORICAL_DEVICE_SINK=(36,40,30)
HISTORICAL_DEVICE_SINK_RAW=4<<60
Z_CHANNEL='PI10.device.actual_plusZ.R01';X_CHANNEL='PI10.device.actual_plusX.R01'
QUESTION_CHANNEL='PI10.device.material_question.R01'
PARENT_KEYS=('DEE.Cognitive.PI07.regulation.R01','DEE.Cognitive.PI07.regulation.environment.R02',
 'DEE.Cognitive.PI07.regulation.environment.R03','DEE.Cognitive.PI08.successive_contextual_regulation.B.R01',
 'DEE.Cognitive.PI08.conditional_sensor_register_access.C.R02','DEE.Cognitive.PI09.selective_registered_consultation.R02',
 'DEE.Cognitive.PI09.persistent_environment.D.R02','DEE.Cognitive.PI09.explicit_FI_eight_offer_lot.R01',
 'DEE.Cognitive.PI07.regulated_FI_access.R01','DEE.Cognitive.PI04.C2C.coordination.R01')

def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(data):return hashlib.sha256(data).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def safe(value):return json.loads(json.dumps(value,ensure_ascii=False,allow_nan=False))
def encoded(value):
 data=json.dumps(safe(value),ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
 need(len(data.encode('utf8'))<=65536,'PI10 own metadata exceeds64KB; no Native or journal append')
 return data
def native():
 from capacidades import pi03_credito_generico_R01_BORRADOR as h
 d,observe,receipt=h._native()
 from capacidades import pi10_dos_trazas_legales_R01 as geometry
 return h,geometry,d,observe,receipt
def identity(a):
 from capacidades import pi10_transporte_ancestral_R01 as transport
 transport.install(a);return transport.identity(a)
def config(a=None):
 c=read(SCOPE);need(c.get('schema')=='DEE.PI10.fixed_experiment_scope.R01','Exact fixed PI10 experiment scope')
 need(c.get('role')in('p0','calibration','evaluation')and c.get('arm')in('real','nonfailure','yoked')and c.get('trace_control')in('none','cut','sham'),'Fixed external role/return/trace control')
 need(c.get('force_query')is None or(type(c.get('force_query'))is bool and c['role']=='calibration'),'Only separately identified forced calibration')
 if a is not None:need(identity(a)['life_id']==c.get('life_id'),'Scope/current life mismatch')
 return c
def protocol(a=None,material=False):
 b=PROTOCOL.read_bytes();p=json.loads(b);c=config(a)
 need(p.get('schema')=='DEE.PI10.adaptive_query.protocol.R01'and p.get('N')==67,'Fixed existing N67 PI10 protocol')
 need(p.get('query_origin')==[24,12,12]and p.get('old_origin')==[8,40,50]and p.get('query_prefix')=='PI10.Q1.TC.R01'and p.get('old_prefix')=='PI07.TC.R01','Frozen two TC locations/prefixes')
 need(p.get('q1_delay_laps')==18 and p.get('q2_delay_laps')==6 and p.get('max_ticks_per_episode')==2016,'Frozen calendar/bound2016')
 need(p.get('evaluation_horizon')==18 and p.get('total_offers')==24 and len(p.get('schedule',[]))==24,'Explicit finite eighteen plus six supply')
 need(p.get('fi_required')is True and p.get('initial_old_q2_delta')==-1,'Real Native FI and inherited fixed q2 offset contract')
 need(c.get('protocol_sha256')==sha(b),'Scope must bind exact current protocol')
 for row in p['schedule']+p.get('calibration_schedule',[]):
  need(row.get('cue')in('threat','falsecue','none')and row.get('regime')in('need','bypass','need_return'),'Prepared environment law only')
  need(type(row.get('left'))is int and type(row.get('right'))is int and 0<=row['right']<row['left']<=20,'Finite positive independent FI work')
 if material:
  need(p.get('status')in('SEALED_FOR_CALIBRATION','SEALED_FOR_EVALUATION'),'Root must seal before Native')
  for name,digest in p.get('sources_sha256',{}).items():need(Path(name).name==name and sha(Path(__file__).with_name(name).read_bytes())==digest,'Pinned source changed: '+name)
 return p,sha(b),c
def old_literals(a):
 entries=dict(a.world.runtime.snapshot_metadata_entries)
 return {k:entries[k]for k in PARENT_KEYS if k in entries}
def physical(a):
 from app.native_tools import physical as get
 return get(a.world)
def _get(a):
 e=dict(a.world.runtime.snapshot_metadata_entries);need(KEY in e,'PI10 legal P0 has not been prepared')
 m=json.loads(e[KEY]);need(m.get('version')==VERSION and m.get('ready')is True,'Exact reached PI10 preparation required')
 return m
def _save(a,m):a.world.runtime.set_snapshot_metadata(KEY,encoded(m))
def home(directory,life):
 base=Path(directory).resolve(strict=True);need(base.is_dir()and base.name==life,'Existing exact owned current-life artifact home')
 for p in(base,*base.parents):need(not p.is_symlink()and not(getattr(p.lstat(),'st_file_attributes',0)&1024),'No linked artifact home')
 return base/FOLDER
def record(a,m,directory,event):
 folder=home(directory,identity(a)['life_id']);folder.mkdir(exist_ok=True)
 data=(json.dumps(safe({'index':m['log_count'],'tick':int(a.tick),'current_life_id':identity(a)['life_id'],**event}),ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf8')
 proposed={**m,'log_count':m['log_count']+1,'log_chain_sha256':sha(bytes.fromhex(m['log_chain_sha256'])+data)}
 capsule=encoded(proposed)
 with(folder/'eventos.jsonl').open('ab')as f:f.write(data);f.flush();os.fsync(f.fileno())
 m.update(proposed);a.world.runtime.set_snapshot_metadata(KEY,capsule)
def observe(a,site):
 _,_,d,exact,_=native();return exact(a.world.runtime.observe(d.Coordinate(*site)))
def submit(a,name,payload,tick,requests):
 r=a.world.submit(name,int(payload),int(tick));v={'id':int(r.id),'channel':name,'payload':int(payload),'requested_tick':int(tick)};requests.append(v);return v
def receipts(a,requests):
 exact=native()[4];return [{**r,'receipt':exact(a.world.runtime.receipt(r['id']))}for r in requests]
def summary(rows):
 unique={}
 for row in rows:
  r=row['receipt'];need(r['id']==row['id'],'Receipt identity mismatch')
  need(row['id']not in unique or unique[row['id']]==r,'Incompatible alias receipt');unique[row['id']]=r
 statuses={}
 for r in unique.values():statuses[r['status']]=statuses.get(r['status'],0)+1
 pending=sum(v for k,v in statuses.items()if k!='applied'and not k.startswith('rejected'))
 return {'unique_requested':len(unique),'applied':statuses.get('applied',0),'rejected':sum(v for k,v in statuses.items()if k.startswith('rejected')),'pending_or_other':pending,'all_terminal':pending==0,'status_counts':statuses,'aliases_deduplicated':len(rows)-len(unique)}
def validate_literal(row):need(isinstance(row,dict)and set(row)=={'modo'}and row.get('modo')in MODES,'Fixed PI10 mode only; no action/answer/bank override')
def validate(a,row):
 validate_literal(row);identity(a)
 if row['modo']==STATE:return
 p,ph,c=protocol(a,True);entries=dict(a.world.runtime.snapshot_metadata_entries)
 if row['modo']==PREPARE:
  need(KEY not in entries,'Do not reinstall PI10 or reset acquired banks')
  expected=c.get('source_physical',{});actual=physical(a)
  need(set(expected)=={'N','tick','RAW_sha256','clocks_sha256'}and all(actual[k]==v for k,v in expected.items()),'Exact full coherent source physical identity before preparation')
  return
 m=_get(a);need(not m.get('pending')and not m.get('uncertain'),'Preserve and reconcile a pending/uncertain future')
 if row['modo']==ADMIT:
  need(not m.get('admitted')and m['ordinal']==0 and not m['rows'],'External finite lot cannot reset an admitted history')
  need(c['role']in('calibration','evaluation'),'Explicit experimental role required')
  need(c.get('calibration_authorized')is True if c['role']=='calibration'else c.get('evaluation_authorized')is True,'Root calibration/evaluation authorization required')
  return
 need(m.get('admitted')is True and m['protocol_sha256']==ph,'One admitted lot under this frozen protocol')
 limit=len(p['calibration_schedule'])if c['role']=='calibration'else 24 if c['arm']=='real'and c['trace_control']=='none'else 18
 need(m['ordinal']<limit,'Current finite stock exhausted; no reset/extension')
 need((row['modo']==CALIBRATE)==(c['role']=='calibration'),'Forced calibration is never attributed to candidate learning')
def device_preflight(a):
 """Preserved C hardware, no sink installation/cleanup or route reconstruction.

 The sole nonzero halo exception is the exact historical SEM4 at36. The
 clearance points32/35 are not new anatomy. Root declared this exception
 before Native from frozen-source preflight bfc8859c32333af6d8dec155e65c6879a5c3b84a418bd8124653d5c5b3e9577f.
 """
 halo={tuple((s[k]+d[k])%67 for k in range(3))for s in DEVICE_CHECK_SITES for d in itertools.product((-1,0,1),repeat=3)}
 observations=[{'site':list(site),**observe(a,site)}for site in sorted(halo)]
 historical=[r for r in observations if tuple(r['site'])==HISTORICAL_DEVICE_SINK]
 conflicts=[r for r in observations if int(r['raw'])!=0 and not(tuple(r['site'])==HISTORICAL_DEVICE_SINK and int(r['raw'])==HISTORICAL_DEVICE_SINK_RAW)]
 sites=[{'site':list(site),**observe(a,site)}for site in DEVICE_CHECK_SITES]
 return {'version':'PI10.preserved_C_device_whole_RAW_halo1.R01','tick':int(a.tick),'sites_checked':len(observations),'site_observations':sites,'all_eight_RAW0':all(int(r['raw'])==0 for r in sites),
   'immutable_historical_sink':historical,'exact_historical_sink_present':len(historical)==1 and int(historical[0]['raw'])==HISTORICAL_DEVICE_SINK_RAW,
   'conflicts':conflicts,'eligible':not conflicts and all(int(r['raw'])==0 for r in sites)and len(historical)==1 and int(historical[0]['raw'])==HISTORICAL_DEVICE_SINK_RAW,
   'observations_sha256':sha(json.dumps(safe(observations),sort_keys=True,separators=(',',':')).encode('utf8')),
   'scope':'Current RAW clearance with sole exact immutable C SEM4 exception; no new device anatomy or guarantee of future isolation/absorption.'}
def prepare(a,directory):
 validate(a,{'modo':PREPARE});p,ph,c=protocol(a,True);h,g,d,exact,_=native();i=identity(a);old=old_literals(a);start=int(a.tick)
 # Complete TC and inherited-device clearance before any Native preparation.
 tc_check=g.passive_preflight(h,tuple(p['query_origin']),lambda site:observe(a,site));device_check=device_preflight(a)
 need(tc_check['eligible']and device_check['eligible'],'Whole TC/preserved-device preflight refused; no cleanup, resampling, or partial TC installation')
 need(not {Z_CHANNEL,X_CHANNEL,QUESTION_CHANNEL}.intersection(set(a.world.runtime.channel_names)),'Fresh fixed aliases required; historical device is preserved')
 m={'version':VERSION,'preparation_life_id':i['life_id'],'geometry':{'origin':p['query_origin'],'prefix':p['query_prefix'],'initial_A':0,'initial_B':0},'preparation_protocol_sha256':ph,'protocol_sha256':None,'ready':False,'admitted':False,'ordinal':0,'rows':[],'pending':{'phase':'LEGAL_P0_INSTALLATION'},'uncertain':True,'log_count':0,'log_chain_sha256':'00'*32,'barrier_attempted':False,'barrier_installed':False}
 record(a,m,directory,{'kind':'LEGAL_ADDITIVE_UNLEARNED_Q1_PREPARATION_INTENT','external_scope':c,'whole_TC_preflight':tc_check,'preserved_C_device_preflight':device_check,'old_metadata_hashes':{k:sha(v.encode('utf8'))for k,v in old.items()}})
 from capacidades.pi07_regulacion_R01 import SafeAdapter
 try:
  prepared=g.install_first_tc(SafeAdapter(a),h,tuple(p['query_origin']),p['query_prefix'],i['life_id'])
  if prepared['ready']:
   for name,site,dr in((Z_CHANNEL,PREVIEW_Z,(0,0,1)),(X_CHANNEL,PREVIEW_X,(1,0,0)),(QUESTION_CHANNEL,QUESTION,(1,0,0))):h._channel(a.world,name,site,dr)
  need(old_literals(a)==old,'Inherited progress changed during P0 setup')
  m.update(ready=prepared['ready'],pending=None if prepared['ready']else{'phase':'PRESERVED_PARTIAL_NATIVE_ADMISSION'},uncertain=not prepared['ready'])
  record(a,m,directory,{'kind':'LEGAL_P0_REACHED','preparation':prepared,'preserved_C_device_preflight':device_check})
  return {'version':VERSION,'before_tick':start,'after_tick':int(a.tick),'new_native_ticks':int(a.tick)-start,'ready':m['ready'],'requests':prepared['requests'],'Native_inputs':summary(prepared['requests']),'preparation':prepared,'preserved_C_device_preflight':device_check,'old_metadata_literal_unchanged':old_literals(a)==old,'not_learning':True}
 except BaseException as e:m.update(pending={'phase':'PRESERVED_P0_FAILURE','reason':type(e).__name__},uncertain=True);_save(a,m);raise
def admit(a,directory):
 validate(a,{'modo':ADMIT});p,ph,c=protocol(a,True);m=_get(a);before=physical(a);old=old_literals(a)
 m.update(admitted=True,admission_life_id=identity(a)['life_id'],protocol_sha256=ph,admission_control={k:c[k]for k in('role','arm','trace_control','force_query')},environment_supply={'PI10_new_total':24,'evaluation':18,'future':6,'ancestor_D_FI8_C2C_not_reset':True})
 record(a,m,directory,{'kind':'FINITE_ENVIRONMENT_LOT_ADMITTED_ZERO_NATIVE','control':c,'old_metadata_literal_unchanged':old_literals(a)==old})
 need(physical(a)==before and old_literals(a)==old,'Zero-Native admission changed physical/ancestral state')
 return {'version':VERSION,'before_tick':int(a.tick),'after_tick':int(a.tick),'new_native_ticks':0,'admitted':True,'new_PI10_offers':24,'old_metadata_literal_unchanged':True,'environment_preparation_not_learning':True}
def decode_sample(sample):
 if int(sample['raw'])==0:return {'valid':True,'bit':0,'kind':'measured_exact_RAW0_absence'}
 if int(sample['state'])>0 and int(sample['semantic'])==1:
  direction=list(sample['direction'])
  if direction==[0,0,1]:return {'valid':True,'bit':1,'kind':'actual_active_SEM1_plusZ'}
  if direction==[1,0,0]:return {'valid':True,'bit':0,'kind':'actual_active_SEM1_plusX'}
 return {'valid':False,'bit':None,'kind':'NULL_unrecognized_RAW'}
def returned_failed(c,ordinal,actual):
 if c['arm']=='real':return bool(actual)
 if c['arm']=='nonfailure':return False
 values=c.get('yoked_values');need(isinstance(values,list)and ordinal<len(values)and all(type(v)is bool for v in values),'Prospectively sealed yoked values required')
 return values[ordinal]
def episode(a,directory,calibration=False):
 validate(a,{'modo':CALIBRATE if calibration else EPISODE});p,ph,c=protocol(a,True);m=_get(a);h,g,d,exact,exact_receipt=native();i=identity(a);old=old_literals(a);start=int(a.tick);ordinal=m['ordinal']
 spec=copy.deepcopy((p['calibration_schedule']if calibration else p['schedule'])[ordinal]);origin=tuple(p['query_origin']);prefix=p['query_prefix']
 from capacidades.pi07_regulacion_R01 import SafeAdapter
 used=SafeAdapter(a);refs1=g.bank_observations(a,d,exact,origin);refs2=g.bank_observations(a,d,exact,g.OLD_ORIGIN)
 need(refs1['reference_clocks'][0]%782==refs1['reference_clocks'][1]%782 and refs2['reference_clocks'][0]%782==refs2['reference_clocks'][1]%782,'Reference pair phase mismatch; no repair')
 calendar=g.two_selector_calendar(start,refs1['reference_clocks'][0],refs2['reference_clocks'][0]);one=calendar['first'];two=calendar['second'];q1=one['query_tick'];q2=two['query_tick'];requests=[];traces=[]
 m.update(pending={'phase':'OPPORTUNITY_STARTED','ordinal':ordinal,'q1':q1,'q2':q2},uncertain=True)
 record(a,m,directory,{'kind':'TWO_NATIVE_SELECTORS_OPPORTUNITY_INTENT','ordinal':ordinal,'calendar':calendar,'environment_spec':spec,'external_control':c,'Native_input_scope':'Only actual previewSTATE and gated bit0/2, no regime/target/optimal action'})
 try:
  if spec['cue']!='none':submit(a,Z_CHANNEL if spec['cue']=='threat'else X_CHANNEL,0,q1-2,requests)
  used.run_until(q1-1);sample=observe(a,PREVIEW);decoded=decode_sample(sample);need(decoded['valid'],'No expected-bit fallback for NULL current preview')
  from capacidades import pi10_entorno_dos_puertas_R01 as env
  folder=home(directory,i['life_id']);offer=env.prepare_offer(folder,ordinal,sample,spec['regime'],actual_tick=int(a.tick),query_tick=q1)
  datum=int(sample['state']);need(0<=datum<=3,'Actual state outside declared two-bit codec')
  requests.extend(h.submit_query(a.world,q1,prefix=prefix));submit(a,prefix+'.datum',datum,q1+3,requests)
  used.run_until(q1+4);reader1=g.read_central(a,d,exact,origin,q1);native_motor1=g.actual_motor(reader1['choice']);motor1=(1 if c['force_query']else-1)if calibration and type(c.get('force_query'))is bool else native_motor1
  if motor1 is not None:requests.append(h.submit_motor_copy(a.world,motor1,one['seed_tick'],prefix=prefix))
  question=submit(a,QUESTION_CHANNEL,0,one['seed_tick'],requests)if motor1==1 else None
  used.run_until(q1+8);question_observation=observe(a,QUESTION_READER);first_receipts=receipts(a,requests);first_summary=summary(first_receipts);need(first_summary['all_terminal'],'Uncertain first stage; do not resend')
  if question is not None:question=next(r for r in first_receipts if r['id']==question['id'])
  applied=question is not None and question['receipt']['status']=='applied';signature=int(question_observation['state'])>0 and int(question_observation['semantic'])==1 and list(question_observation['direction'])==[1,0,0]
  released=bool(applied and signature);access_valid=not applied or signature
  bit=decoded['bit']if released else 0
  register={'sample_site':list(PREVIEW),'sample_tick':q1-1,'actual_preview_observation':sample,'first_submitted_STATE':datum,'question_scheduled':question is not None,'question_applied':bool(applied),'question_signature':signature,'question_applied_and_signature':released,'access_valid':access_valid,'released_bit':bit,'release_tick':q1+8,'technical_register_not_Native_memory':True,'release_kind':decoded['kind']if released else'declared_NoQuery_or_rejected_material0_not_observation'}
  traces.append({'phase':'q1_after_efference_before_barriers','q1':g.trace_stencil(a,d,exact,origin)})
  barrier_requests=[]
  if c['trace_control']!='none'and not m['barrier_attempted']:
   m['barrier_attempted']=True;m['barrier_attempt_ordinal']=ordinal
   barrier_requests=g.barrier_requests(a.world,prefix,one['seed_tick'],c['trace_control']);requests.extend(barrier_requests)
  used.run_until(q1+13);traces.append({'phase':'q1_after_barrier_arrival','q1':g.trace_stencil(a,d,exact,origin)})
  if barrier_requests:
   br=receipts(a,barrier_requests);m['barrier_installed']=all(r['receipt']['status']=='applied'for r in br);m['barrier_receipts']=br
  # q2 Native receives a fixed scaling of the real gated bit, never a target.
  requests.extend(h.submit_query(a.world,q2,prefix=g.OLD_PREFIX));submit(a,g.OLD_PREFIX+'.datum',2*int(bit),q2+3,requests)
  used.run_until(q2+4);reader2=g.read_central(a,d,exact,g.OLD_ORIGIN,q2);motor2=g.actual_motor(reader2['choice']);used.run_until(q2+6)
  copied2=None
  if motor2 is not None:copied2=h.submit_motor_copy(a.world,motor2,two['seed_tick'],prefix=g.OLD_PREFIX);requests.append(copied2)
  used.run_until(q2+8)
  copy_receipt=exact_receipt(a.world.runtime.receipt(copied2['id']))if copied2 is not None else None
  command_valid=motor2 is not None and copy_receipt is not None and copy_receipt['status']=='applied'
  route=(1 if motor2==1 else 0)if command_valid else None
  # The real inherited FI hardware is used under the new finite PI10 lot.
  used.run_until(q2+136)
  from capacidades import pi05_transito_causal_R01 as baseline
  fi=baseline._fiplus(used,{'modo':baseline.FIPLUS,'izquierda':spec['left'],'derecha':spec['right'],'captura':'normal'},directory);requests.extend(fi['requests'])
  need(int(a.tick)<two['outcome_injection_tick'],'Native work missed fixed disposal deadline; no past input')
  consequence=env.act_on_observed_motor(folder,ordinal,route,native_choice=reader2['choice'],reader_observation=reader2['observation'],command_valid=command_valid,q1_valid=native_motor1 is not None and access_valid,fi_choice=fi['old_q6_choice'],fi_required=True,actual_tick=int(a.tick),command_receipt=copy_receipt)
  actual=bool(consequence['actual_failed']);returned=returned_failed(c,ordinal,actual)
  used.run_until(two['outcome_injection_tick']-1);disposal=h.submit_generic_outcome(a.world,False,two['outcome_injection_tick'],prefix=g.OLD_PREFIX);requests.append(disposal)
  used.run_until(two['settled_after_tick']);refs2_after_disposal=g.bank_observations(a,d,exact,g.OLD_ORIGIN)
  used.run_until(one['outcome_injection_tick']-1);traces.append({'phase':'before_q1_generic_return','q1':g.trace_stencil(a,d,exact,origin)})
  first_return=h.submit_generic_outcome(a.world,returned,one['outcome_injection_tick'],prefix=prefix);requests.append(first_return)
  for tick in(one['outcome_injection_tick'],one['collision_tick'],one['contact_tick'],one['settled_after_tick']):
   used.run_until(tick);traces.append({'phase':'q1_return_frame','tick':int(a.tick),'q1':g.trace_stencil(a,d,exact,origin),'q1_references':g.bank_observations(a,d,exact,origin)})
  completed=receipts(a,requests);counts=summary(completed);need(counts['all_terminal'],'Unknown final Native receipts; preserve pending future')
  need(old_literals(a)==old,'Inherited progress changed; do not reinterpret/reset ancestors')
  end=int(a.tick);need(0<=end-start<=p['max_ticks_per_episode'],'Fixed whole episode bound exceeded')
  refs_after={'q1':g.bank_observations(a,d,exact,origin),'q2':g.bank_observations(a,d,exact,g.OLD_ORIGIN)}
  result={'version':VERSION,'life_id':i['life_id'],'ordinal':ordinal,'before_tick':start,'after_tick':end,'new_native_ticks':end-start,'calendar':calendar,'environment_spec':spec,
   'first_stage':{'query_tick':q1,'reader':reader1,'native_motor':native_motor1,'actual_query_motor':motor1,'operator_forced_query':c['force_query']if calibration else None,'sample_register':register,'question_request':question,'question_observation':question_observation,'Native_selection_valid':native_motor1 is not None,'Native_inputs':first_summary},
   'second_stage':{'query_tick':q2,'reader':reader2,'native_motor':motor2,'actual_motor':motor2,'actual_route':route,'command_valid':command_valid,'copy_request':copied2,'copy_receipt':copy_receipt,'FI':fi,'resource':consequence,'fixed_nonfailure_disposal':disposal},
   'resource':consequence,'offer':offer,'actual_failed':actual,'returned_failed':returned,'feedback_arm':c['arm'],'trace_control':c['trace_control'],'barrier_installed':m['barrier_installed'],'barrier_attempt_ordinal':m.get('barrier_attempt_ordinal'),'Q1_generic_return':first_return,
   'Q1_references_before':refs1,'Q2_references_before':refs2,'Q2_references_after_disposal':refs2_after_disposal,'references_after':refs_after,'Q2_reference_difference_stable':refs2['A_minus_B']==refs_after['q2']['A_minus_B'],
   'trace_observations':traces,'requests':completed,'Native_inputs':counts,'inherited_metadata_literal_unchanged':True,'operator_calibration':calibration,
   'attribution':'New support, timing, resource law and two-stage sequence are prepared. Native chooses; only Q1 receives actual task consequence at its fixed hub. Isolated useful learning requires controls and actual Q2/FI stability, not this declaration.'}
  witness=folder/('episodio_%04d.json'%ordinal);need(not witness.exists(),'Existing reached episode preserved; no retry')
  data=(json.dumps(safe(result),ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf8')
  with witness.open('xb')as out:out.write(data);out.flush();os.fsync(out.fileno())
  m['ordinal']+=1;m['rows'].append({'ordinal':ordinal,'after_tick':end,'q1_choice':reader1['choice'],'actual_query':released,'q2_choice':reader2['choice'],'actual_failed':actual,'returned_failed':returned,'resource_delivered':consequence['attributed_useful'],'Q1_A_minus_B':refs_after['q1']['A_minus_B'],'Q2_A_minus_B':refs_after['q2']['A_minus_B'],'witness':{'file':witness.name,'bytes':len(data),'sha256':sha(data)}})
  m.update(pending=None,uncertain=False)
  record(a,m,directory,{'kind':'TWO_STAGE_NATIVE_OPPORTUNITY_COMPLETED','ordinal':ordinal,'witness':m['rows'][-1]['witness'],'Native_inputs':counts,'actual_failed':actual,'returned_failed':returned})
  return result
 except BaseException as e:
  m.update(uncertain=True,pending={'phase':'PRESERVED_INCOMPLETE_OPPORTUNITY','ordinal':ordinal,'tick':int(a.tick),'reason':type(e).__name__})
  _save(a,m);raise
def state(a):
 identity(a);entries=dict(a.world.runtime.snapshot_metadata_entries)
 return {'version':VERSION,'present':KEY in entries,'progress':json.loads(entries[KEY])if KEY in entries else None,'physical':physical(a),'new_native_ticks':0,'scope':'No Native query, preview, step or material admission.'}
def dispatch(a,row,*,actuator='closed',directory=None):
 validate(a,row)
 if row['modo']==STATE:return state(a)
 need(actuator=='closed'and directory is not None,'Explicit owned fixed safe actuator required')
 if row['modo']==PREPARE:return prepare(a,directory)
 if row['modo']==ADMIT:return admit(a,directory)
 return episode(a,directory,row['modo']==CALIBRATE)
def uncertain(a):return KEY in dict(a.world.runtime.snapshot_metadata_entries)and json.loads(dict(a.world.runtime.snapshot_metadata_entries)[KEY]).get('uncertain',False)
def operational_dependencies(a,directory):
 v=state(a)
 if not v['present']:return v
 m=v['progress'];need(m['ordinal']==len(m['rows']),'PI10 progress/witness count differs')
 folder=home(directory,identity(a)['life_id']);need((folder/'eventos.jsonl').is_file(),'PI10 journal missing')
 for row in m['rows']:
  ref=row['witness'];p=folder/ref['file'];need(p.is_file()and p.stat().st_size==ref['bytes']and sha(p.read_bytes())==ref['sha256'],'Immutable PI10 episode witness missing/changed')
 return {'version':VERSION,'present':True,'ordinal':m['ordinal'],'remaining':24-m['ordinal'],'pending':m['pending'],'uncertain':m['uncertain'],'journal_sha256':sha((folder/'eventos.jsonl').read_bytes()),'new_native_ticks':0,'finite_lot24_no_ancestral_counter_reset':True}
def code_files():
 return tuple([Path(__file__),PROTOCOL,SCOPE,*(Path(__file__).with_name(n)for n in('pi10_dos_trazas_legales_R01.py','pi10_entorno_dos_puertas_R01.py','pi10_transporte_ancestral_R01.py','pi03_credito_generico_R01_BORRADOR.py','pi07_regulacion_R01.py','pi05_transito_causal_R01.py'))])
