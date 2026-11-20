"""PI07 R02 environment/control progress around the unchanged R01 Native body.

R01 source, protocol, KEY, preparation journal and A0/B2 anatomy are preserved.
Only explicit INICIAR/configuration creates new administrative progress. The
actor reads neither return-control plans nor observation flags. Import is pure
stdlib and never opens or advances a Native world.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,uuid
from capacidades import pi07_regulacion_R01 as body
VERSION='DEE.PI07.acquired_regulation.environment.R02'
KEY='DEE.Cognitive.PI07.regulation.environment.R02';FOLDER='PI07_REGULACION_ENV_R02'
PROTOCOL=Path(__file__).with_name('PROTOCOLO_PI07_R02.json')
START='eci01-pi07-iniciar';CONTROL='eci01-pi07-configurar-control'
EPISODE=body.EPISODE;STATE=body.STATE;MODES={*body.MODES,START,CONTROL}
R1_SOURCE_SHA='8e6ccfc2d9463c46d2312cc81108ba7e481c5cb31026f05c6d349409f8a09499'
R1_PROTOCOL_SHA='1db513e8f38607ed9e41929fc49afada1be584875d6744e718ccdd9b628cb949'
CODEC_SHA='d60d58301fd29ae0aabf577adc2d6f82392ed42f1d691890d095873cdf80f8d6'
ORIGIN=body.ORIGIN;PREFIX=body.PREFIX;SENSOR=body.SENSOR;ACTUATOR=body.ACTUATOR;MESSAGE_READER=body.MESSAGE_READER;CUES=body.CUES
_native=body._native;_helper=body._helper;_identity=body._identity;_observe=body._observe;_physical=body._physical
_read=body._read;_motor=body._motor;_emit=body._emit;_submit=body._submit;_receipts=body._receipts;_summary=body._summary;_safe=body._safe;at=body.at
def _sha(b):return hashlib.sha256(b).hexdigest()
def protocol(material=False):
 data=PROTOCOL.read_bytes();p=json.loads(data)
 if p.get('schema')!='DEE.PI07.regulation.protocol.R02'or p.get('status')not in('DRAFT','SEALED_FOR_EVALUATION'):raise ValueError('Exact R02 environmental protocol required')
 if material and(p['status']!='SEALED_FOR_EVALUATION'or p.get('evaluation_authorized_by_this_version')is not True):raise ValueError('Root must close viability and seal evaluation first')
 if p.get('N')!=67 or p.get('origin')!=[8,40,50]or p.get('initial_reference_payloads')!={'A':0,'B':2}or p.get('delay_laps')!=6 or p.get('max_ticks_per_episode')!=1300:raise ValueError('Unchanged R01 physical circuit/calendar only')
 if _sha(Path(body.__file__).read_bytes())!=R1_SOURCE_SHA or _sha(body.PROTOCOL.read_bytes())!=R1_PROTOCOL_SHA:raise ValueError('R01 source/protocol history changed; never reinterpret it')
 if p.get('calendar',{}).get('planning_lead_ticks')!=16:raise ValueError('Unchanged fixed source planning lead')
 schedule=p.get('schedule')
 if not isinstance(schedule,list)or len(schedule)!=28:raise ValueError('One frozen cumulative28-opportunity trajectory')
 for row in schedule:
  if set(row)!={'stage','cue','message_payload','left','right'}or row['cue']not in('none','threat','falsecue')or row['message_payload']not in(None,5,8,11):raise ValueError('Frozen physical environment inputs only; no actor target/action')
  if any(type(row[k])is not int for k in('left','right'))or not 0<=row['right']<row['left']<=20:raise ValueError('Fixed public positive comparison domain')
 for name,h in p.get('dependencies_sha256',{}).items():
  if Path(name).name!=name or len(h)!=64 or _sha(Path(__file__).with_name(name).read_bytes())!=h:raise ValueError('Frozen local dependency differs: '+name)
 return p,_sha(data)
def _plan(text,expected):
 if not isinstance(text,str)or len(text.encode('utf8'))>8192 or _sha(text.encode('utf8'))!=expected:raise ValueError('Exact pre-admitted external plan text/hash required')
 plan=json.loads(text);required={'schema','roll','roll_direction','source_failed','values','source_evidence_sha256'}
 if set(plan)!=required or plan['schema']!='DEE.PI07.yoked_return.roll5.v1'or plan['roll']!=5 or plan['roll_direction']!='source_plus_5':raise ValueError('Only the predeclared +5-source twelve-return control')
 if any(not isinstance(plan[k],list)or len(plan[k])!=12 or any(type(v)is not bool for v in plan[k])for k in('source_failed','values')):raise ValueError('Twelve real booleans, not a policy or answer table')
 if plan['values']!=[plan['source_failed'][(i+5)%12]for i in range(12)]:raise ValueError('Yoke is not the predeclared source+5 rotation')
 if not isinstance(plan['source_evidence_sha256'],str)or len(plan['source_evidence_sha256'])!=64:raise ValueError('The actual source evidence must be hash-bound before control')
 return plan
def validate_literal(row):
 if not isinstance(row,dict):raise ValueError('One explicit R02 operation required')
 if row.get('modo')==START:
  arm=row.get('brazo');expected={'modo','brazo','registro_global'}|({'plan','plan_sha256'}if arm=='yoked'else set())
  if arm not in('real','none','yoked')or set(row)!=expected or type(row.get('registro_global'))is not bool:raise ValueError('Explicit per-life control and observation flag only')
  if arm=='yoked':_plan(row['plan'],row['plan_sha256'])
  return
 if row.get('modo')==CONTROL:
  if set(row)!={'modo','brazo','registro_global'}or row['brazo']!='none'or type(row['registro_global'])is not bool:raise ValueError('Only a declared post12 nonfailure control, no bank/action reset')
  return
 if row.get('modo')==EPISODE:
  if set(row)-{'modo','actuator_ablation','sensor_ablation'}or any(type(row[k])is not bool for k in row if k!='modo'):raise ValueError('Only explicit after-formation actuator or datum-zero link ablation')
  return
 body.validate_literal(row)
def _get(a):
 _,_,_,decode,_=_native();entries=dict(a.world.runtime.snapshot_metadata_entries)
 if KEY not in entries:raise ValueError('Explicit R02 administrative admission required; no implicit conversion of R01')
 m=decode(entries[KEY])
 if m['version']!=VERSION:raise ValueError('Exact R02 environment revision required')
 return m
def _save(a,m):a.world.runtime.set_snapshot_metadata(KEY,body._encoded(m))
def _home(directory,life):return body._home(directory,life).with_name(FOLDER)
def _record(a,m,directory,event):
 home=_home(directory,_identity(a)['life_id']);home.mkdir(exist_ok=True)
 data=(json.dumps(_safe({'index':m['log_count'],'tick':int(a.tick),**event}),ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf8')
 proposed={**m,'log_count':m['log_count']+1,'log_chain_sha256':_sha(bytes.fromhex(m['log_chain_sha256'])+data)};capsule=body._encoded(proposed)
 with(home/'eventos.jsonl').open('ab')as out:out.write(data);out.flush();os.fsync(out.fileno())
 m.update(proposed);a.world.runtime.set_snapshot_metadata(KEY,capsule)
def validate(a,row):
 validate_literal(row)
 if row['modo']not in(START,CONTROL,EPISODE,STATE):return body.validate(a,row)
 identity=_identity(a)
 if row['modo']==STATE:return
 p,ph=protocol(material=True)
 if row['modo']==START:
  if KEY in dict(a.world.runtime.snapshot_metadata_entries):raise ValueError('Environment already admitted; no reset/re-admission')
  old=body._get(a)
  if not old.get('ready')or old['ordinal']!=0 or old['protocol_sha256']!=R1_PROTOCOL_SHA or old.get('pending')or old.get('uncertain')or old.get('rows')or int(a.tick)!=824914:raise ValueError('Only the actual closed unlearned P0 cutT824914; no restore or bank copying')
  return
 m=_get(a)
 if not m.get('ready')or m['protocol_sha256']!=ph or m.get('pending')or m.get('uncertain'):raise ValueError('Closed matching R02 progress required')
 if row['modo']==CONTROL:
  if m['ordinal']!=12 or 'REVERSE'not in identity['life_id']or m.get('post12_control'):raise ValueError('One explicit diagnostic post12 reversal-return control only')
  return
 if m['ordinal']>=m['control']['max_ordinal']:raise ValueError('This finite per-life control/environment is exhausted')
def initialize(a,row,directory):
 validate(a,row);identity=_identity(a);p,ph=protocol(material=True);before=_physical(a);old=body._get(a);old_literal=dict(a.world.runtime.snapshot_metadata_entries)[body.KEY]
 plan=_plan(row['plan'],row['plan_sha256'])if row['brazo']=='yoked'else None
 control={'arm':row['brazo'],'from_ordinal':0,'max_ordinal':28 if row['brazo']=='real'else 12,'plan_sha256':row.get('plan_sha256'),
  'yoked_values':plan['values']if plan else None,'source_evidence_sha256':plan['source_evidence_sha256']if plan else None,'source_rotation':'source_plus_5'if plan else None}
 m={'version':VERSION,'life_id':identity['life_id'],'protocol_sha256':ph,'admitted_tick':int(a.tick),'ready':True,'ordinal':0,'pending':None,'uncertain':False,'rows':[],
  'control':control,'instrumentation':{'global_enabled':row['registro_global']},'body_P0':{'KEY':body.KEY,'version':old['version'],'protocol_sha256':old['protocol_sha256'],'preparation_life_id':old['life_id'],'prepared_tick':old['prepared_tick']},
  'log_count':0,'log_chain_sha256':'00'*32}
 if _home(directory,identity['life_id']).exists():raise ValueError('New R02 journal home already exists; no overwrite')
 _save(a,m);_record(a,m,directory,{'kind':'R02_ENVIRONMENT_ADMITTED_ZERO_NATIVE','control':control,'original_plan_text':row.get('plan'),'instrumentation':m['instrumentation'],'R01_P0_unchanged':True,'protocol_sha256':ph})
 after=_physical(a)
 if before!=after or dict(a.world.runtime.snapshot_metadata_entries)[body.KEY]!=old_literal:raise RuntimeError('Administrative admission altered R01/physical state')
 return{'version':VERSION,'life_id':identity['life_id'],'before_tick':int(a.tick),'after_tick':int(a.tick),'new_native_ticks':0,'requests':[],'admitted':True,'control':control,'physical_before':before,'physical_after':after,'R01_body_metadata_literal_unchanged':True,'scope':'External control/protocol progress only; no new body, learned bank or experience installed.'}
def configure_control(a,row,directory):
 validate(a,row);m=_get(a);before=_physical(a);oldbody=dict(a.world.runtime.snapshot_metadata_entries)[body.KEY]
 m['post12_control']={'previous_control':m['control'],'configured_tick':int(a.tick),'source_ordinal':12};m['control']={'arm':'none','from_ordinal':12,'max_ordinal':20,'plan_sha256':None,'yoked_values':None,'source_evidence_sha256':None,'source_rotation':None};m['instrumentation']={'global_enabled':row['registro_global']}
 _record(a,m,directory,{'kind':'EXPLICIT_POST12_NONFAILURE_RETURN_CONTROL','old_control':m['post12_control'],'control':m['control'],'not_a_Native_action':True})
 if before!=_physical(a)or dict(a.world.runtime.snapshot_metadata_entries)[body.KEY]!=oldbody:raise RuntimeError('External control declaration changed physical/R01 state')
 return{'version':VERSION,'new_native_ticks':0,'before_tick':int(a.tick),'after_tick':int(a.tick),'requests':[],'control':m['control'],'ordinal_preserved':m['ordinal'],'no_bank_or_counter_reset':True}
def _return(m,actual_failed):
 control=m['control'];arm=control['arm']
 if arm=='real':return actual_failed
 if arm=='none':return False
 return control['yoked_values'][m['ordinal']-control['from_ordinal']]
def _instrumented(a,m,p,q,identity):
 safe=body.SafeAdapter(a);indices=p.get('instrumentation',{}).get('episode_indices',[0,1,3,7,11,27]);recorder=None;used=safe
 if m['instrumentation']['global_enabled']and(m['ordinal']in indices or m['ordinal']==m['control']['max_ordinal']-1):
  path=Path(__file__).with_name('observador_global_PI05_R01.py')
  if _sha(path.read_bytes())!=CODEC_SHA:raise ValueError('Exact previously validated global recorder required')
  spec=importlib.util.spec_from_file_location('PI07_global_recorder_exact_d60',path);capture=importlib.util.module_from_spec(spec);spec.loader.exec_module(capture)
  centres=(q-1,q+4,q+8,q+72,q+144,q+408,q+410)
  ticks=sorted({centre+d for centre in centres for d in(-2,-1,0,1,2)})
  target=Path(__file__).resolve().parents[1]/'estado/observacion_pasiva'/identity['life_id']/('PI07_R02_'+uuid.uuid4().hex)
  recorder=capture.GlobalRecorder(target,N=67,ticks=ticks,anchor_ticks={q-3,q+4,q+8,q+72,q+144,q+408,q+412},
   provenance={'life_id':identity['life_id'],'ordinal':m['ordinal'],'version':VERSION,'sensor_not_observer_ablation':True,'actor_receives_recording':False},max_frames=31,max_compressed_bytes=67108864)
  used=capture.CapturingAdapter(safe,ticks=ticks,recorder=recorder)
 return used,safe,recorder

def episode(a,row,directory):
 validate(a,row);p,ph=protocol(material=True);identity=_identity(a);m=_get(a);start=int(a.tick);spec=p['schedule'][m['ordinal']]
 refs=[_observe(a,at(v))for v in((-1,-1,0),(1,-1,0))]
 if int(refs[0]['clock'])%782!=int(refs[1]['clock'])%782:raise ValueError('Reference phases diverged; no repair')
 cal=_helper().schedule_trial(start+16,int(refs[0]['clock'])+16,6);q=cal['query_tick'];seed=cal['seed_tick'];S=q-1;end=cal['contact_tick']+2
 if seed!=q+7 or cal['outcome_injection_tick']!=q+408 or end-start>p['max_ticks_per_episode']or q-2<=start:raise ValueError('Frozen six-lap calendar/source lead cannot fit; no adaptive retiming')
 forced=None;ablation=row.get('actuator_ablation',False);sensor_ablation=row.get('sensor_ablation',False)
 used,safety,recorder=_instrumented(a,m,p,q,identity);body_literal_before=dict(a.world.runtime.snapshot_metadata_entries)[body.KEY]
 m['pending']={'phase':'episode_started','ordinal':m['ordinal'],'query_tick':q};m['uncertain']=True;_save(a,m)
 _record(a,m,directory,{'kind':'OPPORTUNITY_INTENT','ordinal':m['ordinal'],'calendar':cal,'environment_spec':spec,'forced_operator_action':forced,'actuator_ablation':ablation,'attribution':'Environment inputs are prepared. Actor sees only the fixed physical state datum; diagnostic force is not learned selection.'})
 requests=[];message_artifact=None
 try:
  if spec['cue']!='none':
   site,direction=CUES[spec['cue']];_submit(a,'PI07.environment.'+spec['cue']+'.R01',0,q-2,requests,site=site,direction=direction)
  used.run_until(S);sensor=_observe(a,SENSOR);datum=int(sensor['state'])
  if not 0<=datum<=3:raise RuntimeError('Native2bit state outside declared identity codec')
  sent_datum=0 if sensor_ablation else datum
  requests.extend(_helper().submit_query(a.world,q,prefix=PREFIX));_submit(a,PREFIX+'.datum',sent_datum,q+3,requests,site=at((-1,0,1)),direction=(0,0,0))
  used.run_until(q+4);reader=_read(a,q);used.run_until(q+6);native_motor=_motor(reader['choice']);motor=native_motor
  if motor is not None:requests.append(_helper().submit_motor_copy(a.world,motor,seed,prefix=PREFIX))
  # A fixed environment pulse may compete with the selected actuator at one
  # Native inlet. Runtime, not this host, resolves the same-boundary conflict.
  message_request=None
  if spec['message_payload']is not None:message_request=_submit(a,'PI07.environment.useful_plusX.R01',spec['message_payload'],seed,requests,site=ACTUATOR,direction=(1,0,0))
  action=_emit(a,motor,seed,requests,ablation)
  _record(a,m,directory,{'kind':'NATIVE_SELECTION_AND_FIXED_ACTUATOR','sensor':{'site':list(SENSOR),'tick':S,'observation':sensor,'actual_state_datum':datum,'submitted_state_datum':sent_datum,'link_ablation_to_material_zero':sensor_ablation},'reader':reader,'native_motor':native_motor,'actual_motor':motor,'operator_forced':forced is not None,'copy_at_seed':motor is not None,'actuator_request':action})
  used.run_until(seed+1);message_observation=_observe(a,MESSAGE_READER);mv=list(message_observation['direction']);message_valid=int(message_observation['state'])>0 and int(message_observation['semantic'])==1 and mv==[1,0,0]
  actual_message=int(message_observation['s_reg'])if message_valid else None
  message_receipt=None
  if message_request is not None:
   _,_,exact,_,_=_native();message_receipt=exact(a.world.runtime.receipt(message_request['id']))
  delivered=bool(message_receipt and message_receipt['status']=='applied'and message_valid and spec['message_payload']is not None and actual_message==spec['message_payload'])
  if message_valid:
   home=_home(directory,identity['life_id']);name='mensaje_%04d.bin'%m['ordinal'];file=home/name;content=actual_message.to_bytes(8,'little')*8
   with file.open('xb')as out:out.write(content);out.flush();os.fsync(out.fileno())
   message_artifact={'file':name,'bytes':64,'sha256':_sha(content),'actual_Native_payload':actual_message,'scope':'Actual measured Native value, no expected-value substitution; simulated information resource, not physical food or energy.'}
  used.run_until(q+136)
  from capacidades import pi05_transito_causal_R01 as baseline
  planned_FI=baseline._calendar(used)
  result_FI=baseline._fiplus(used,{'modo':baseline.FIPLUS,'izquierda':spec['left'],'derecha':spec['right'],'captura':'normal'},directory)
  requests.extend(result_FI['requests'])
  if int(a.tick)>=cal['outcome_injection_tick']:raise RuntimeError('Actual function missed generic-return deadline; no past return or reset')
  actual_failed=(result_FI['old_q6_choice']!=1)or(spec['message_payload']is not None and not delivered)
  arm=m['control']['arm'];returned=_return(m,actual_failed)
  used.run_until(cal['outcome_injection_tick']-1)
  outcome=_helper().submit_generic_outcome(a.world,returned,cal['outcome_injection_tick'],prefix=PREFIX);requests.append(outcome)
  _record(a,m,directory,{'kind':'ACTUAL_FUNCTION_AND_GENERIC_RETURN','FI':result_FI,'message':{'required_payload':spec['message_payload'],'observation_tick':seed+1,'observation':message_observation,'actual_payload':actual_message,'own_native_receipt':message_receipt,'delivered_exact':delivered,'artifact':message_artifact},'actual_failed':actual_failed,'returned_failed':returned,'feedback_arm':arm,'outcome':outcome,'no_action_or_bank_argument_to_return':True})
  return_frames=[]
  for tick in(cal['outcome_injection_tick'],cal['collision_tick'],cal['contact_tick'],end):
   used.run_until(tick);return_frames.append({'tick':int(a.tick),'hub':_observe(a,at((0,-1,-2))),'A':_observe(a,at((-1,-1,0))),'B':_observe(a,at((1,-1,0)))})
  requests=_receipts(a,requests);summary=_summary(requests,start,int(a.tick));terminal=summary['all_terminal']
  if action is not None:action=next(r for r in requests if r['id']==action['id'])
  if message_request is not None:message_request=next(r for r in requests if r['id']==message_request['id'])
  pulse_applied=bool(action is not None and action['receipt']['status']=='applied')
  result={'version':VERSION,'life_id':identity['life_id'],'preparation_life_id':m['body_P0']['preparation_life_id'],'ordinal':m['ordinal'],'before_tick':start,'after_tick':int(a.tick),'new_native_ticks':int(a.tick)-start,'calendar':cal,'environment_spec':spec,
   'sensor':{'site':list(SENSOR),'tick':S,'observation':sensor,'actual_state_datum':datum,'submitted_state_datum':sent_datum,'link_ablation_to_material_zero':sensor_ablation},'reader':reader,'native_motor':native_motor,'actual_motor':motor,'operator_forced_action':forced,
   'Native_selection_valid':native_motor is not None,'actuator_ablation':ablation,'sensor_ablation':sensor_ablation,'actuator_request':action,'pulse_scheduled':action is not None,'pulse_applied':pulse_applied,'pulse_emitted':pulse_applied,
   'message':{'request':message_request,'own_native_receipt':message_receipt,'read_tick':seed+1,'site':list(MESSAGE_READER),'observation':message_observation,'actual_payload':actual_message,'required_payload':spec['message_payload'],'delivered_exact':delivered,'artifact':message_artifact},
   'FI':result_FI,'FI_planned_calendar':planned_FI,'FI_query_expected':q+192,'FI_query_matches_predicted_phase':result_FI['calendar']['query_tick']==q+192,
   'actual_failed':actual_failed,'returned_failed':returned,'feedback_arm':arm,'requests':requests,'Native_inputs':summary,'reference_before':refs,'return_frames':return_frames,
   'physical_after':_physical(a),'external_global_capture':None if recorder is None else recorder.close(),'R01_body_metadata_literal_unchanged':dict(a.world.runtime.snapshot_metadata_entries)[body.KEY]==body_literal_before,
   'host_safety':{'check_max_step_ticks':32,'observations':safety.safety,'is_external_not_learned_regulation':True},
   'scope':'New prepared Native selection plus identity sensor and fixed transducer. Host offers opportunities/environment and evaluates actual function; forced controls are not Native learned decisions. Useful learning requires causal controls and conservation.'}
  if dict(a.world.runtime.snapshot_metadata_entries)[body.KEY]!=body_literal_before:raise RuntimeError('R01 preparation metadata was modified')
  m['ordinal']+=1;m['rows'].append({'ordinal':result['ordinal'],'after_tick':int(a.tick),'native_choice':reader['choice'],'actual_failed':actual_failed,'pulse_scheduled':action is not None,'pulse_applied':pulse_applied,'message_delivered':delivered,'message_artifact':message_artifact,'FI_choice':result_FI['old_q6_choice'],'forced':False})
  m['pending']=None if terminal else{'phase':'unknown_terminal_receipts'};m['uncertain']=not terminal
  _record(a,m,directory,{'kind':'EPISODE_COMPLETED','result':result})
  return result
 except BaseException as error:
  if recorder is not None:
   try:recorder.close()
   except Exception:pass # A previously finalized capture is preserved, never overwritten.
  m['uncertain']=True;m['pending']={'phase':'preserved_incomplete_episode','ordinal':m['ordinal'],'tick':int(a.tick),'reason':type(error).__name__}
  _save(a,m)
  raise

def state(a):
 result=body.state(a);result['version']=VERSION;entries=dict(a.world.runtime.snapshot_metadata_entries)
 result.update(R01_body_P0=result.pop('progress'),R02_environment_admitted=KEY in entries,progress=_get(a)if KEY in entries else None,new_native_ticks=0)
 return result
def dispatch(a,row,*,actuator='closed',directory=None):
 validate(a,row)
 if row['modo']==STATE:return state(a)
 if row['modo']not in(START,CONTROL,EPISODE):return body.dispatch(a,row,actuator=actuator,directory=directory)
 if directory is None or actuator!='closed':raise ValueError('Existing exact diagnostic owner/home and closed legal interface required')
 _home(directory,_identity(a)['life_id'])
 if row['modo']==START:return initialize(a,row,directory)
 if row['modo']==CONTROL:return configure_control(a,row,directory)
 return episode(a,row,directory)
def uncertain(a):
 return body.uncertain(a)or(KEY in dict(a.world.runtime.snapshot_metadata_entries)and bool(_get(a).get('uncertain')))
def operational_dependencies(a,directory):
 prior=body.operational_dependencies(a,directory)
 if KEY not in dict(a.world.runtime.snapshot_metadata_entries):return{'version':VERSION,'R01_body':prior,'R02_environment_admitted':False,'new_native_ticks':0}
 m=_get(a);p,ph=protocol();identity=_identity(a)
 if m['protocol_sha256']!=ph:raise ValueError('R02 environmental protocol changed; preserve the exact version')
 home=_home(directory,identity['life_id']);journal=home/'eventos.jsonl';chain='00'*32;count=0
 with journal.open('rb')as rows:
  for line in rows:json.loads(line);chain=_sha(bytes.fromhex(chain)+line);count+=1
 if count!=m['log_count']or chain!=m['log_chain_sha256']or len(m['rows'])!=m['ordinal']:raise ValueError('R02 journal/progress mismatch; no reset')
 artifacts=[]
 for row in m['rows']:
  artifact=row.get('message_artifact')
  if artifact is None:continue
  expected='mensaje_%04d.bin'%row['ordinal']
  if artifact['file']!=expected:raise ValueError('Unexpected external artifact path')
  file=home/expected
  if not file.is_file()or file.stat().st_size!=artifact['bytes']or _sha(file.read_bytes())!=artifact['sha256']:raise ValueError('Actual Native message artifact differs/missing')
  artifacts.append(artifact)
 return{'version':VERSION,'R01_body':prior,'R02_environment_admitted':True,'protocol_sha256':ph,'ordinal':m['ordinal'],'control':m['control'],'remaining':m['control']['max_ordinal']-m['ordinal'],
  'pending':m['pending'],'uncertain':m['uncertain'],'journal':str(journal),'journal_sha256':_sha(journal.read_bytes()),'artifacts_verified':artifacts,'new_native_ticks':0,
  'scope':'R01 P0 body/journal plus R02 external progress/actual artifacts, complete Native state and original PersistentService/SQLite/outbox. No memory or physical-state transplant.'}
def code_files():return list(dict.fromkeys([Path(__file__),PROTOCOL,Path(__file__).with_name('observador_global_PI05_R01.py'),*body.code_files()]))
