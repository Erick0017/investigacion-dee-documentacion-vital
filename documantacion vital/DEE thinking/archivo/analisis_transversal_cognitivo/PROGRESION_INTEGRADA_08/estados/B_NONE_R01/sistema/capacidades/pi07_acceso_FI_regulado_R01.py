"""Explicit new functional FI access, never a silent legacy-reader change.

The inherited Native TC actor selects a fixed perpendicular pulse from its
actual physical sensor. There is NO prepared cue or useful-message episode.
Public independent operands enter the unchanged FI128 frame. Its original
earlyq4 decoder supplies the result including material0; NULL stays invalid.
"""
from pathlib import Path
import hashlib,json,os
from capacidades import pi07_regulacion_R03 as regulation
body=regulation.body
VERSION='DEE.PI07.fixed_regulated_FI_access.R01_PREPARED'
KEY='DEE.Cognitive.PI07.regulated_FI_access.R01';FOLDER='PI07_ACCESO_FI_REGULADO_R01'
START='eci01-pi07-fi-acceso-admitir';QUERY='eci01-pi07-fi-regulada';STATE='eci01-pi07-fi-acceso-estado';NEW_MODES={START,QUERY,STATE};MODES={*regulation.MODES,*NEW_MODES}
PROTOCOL=Path(__file__).with_name('PROTOCOLO_PI07_ACCESO_FI_R01.json')
REGULATION_SHA='40648fd81c5b1f278ee9c18d0d464c5a4b5e9fd808054afe6ff072a10fda0ac5'
def sha(b):return hashlib.sha256(b).hexdigest()
def protocol(material=False):
 data=PROTOCOL.read_bytes();p=json.loads(data)
 if p.get('schema')!='DEE.PI07.regulated_FI_access.protocol.R01'or p.get('status')!='SEALED_BEFORE_NEW_FI_TESTS'or p.get('N')!=67:raise ValueError('Prospectively sealed new access protocol required')
 if p.get('query_lead')!=16 or p.get('delay_laps')!=6 or p.get('FI_start_relative_query')!=136 or p.get('read_relative_FI_query')!=4 or p.get('max_native_ticks')!=1300 or p.get('max_queries')!=8:raise ValueError('Exact fixed TC/FI calendar, eight-use budget and unchanged early reader required')
 if sha(Path(regulation.__file__).read_bytes())!=REGULATION_SHA or sha(regulation.PROTOCOL.read_bytes())!=regulation.PROTOCOL_SHA:raise ValueError('Original R03 source/protocol must stay literal')
 for name,h in p.get('dependencies_sha256',{}).items():
  if Path(name).name!=name or sha(Path(__file__).with_name(name).read_bytes())!=h:raise ValueError('Frozen dependency changed: '+name)
 return p,sha(data)
def validate_literal(row):
 if not isinstance(row,dict):raise ValueError('One fixed access request required')
 if row.get('modo')not in NEW_MODES:return regulation.validate_literal(row)
 if row.get('modo')in(START,STATE)and set(row)=={'modo'}:return
 if row.get('modo')==QUERY:
  if not{'modo','izquierda','derecha'}<=set(row)or set(row)-{'modo','izquierda','derecha','sensor_ablation','actuator_ablation'}:raise ValueError('No cue, target, expected response, site, reader or corrective pulse argument')
  if any(type(row[k])is not int or not 0<=row[k]<=20 for k in('izquierda','derecha'))or any(type(row[k])is not bool for k in('sensor_ablation','actuator_ablation')if k in row):raise ValueError('Public independent operands0..20 and explicit diagnostic cuts only')
  return
 raise ValueError('Unknown explicit regulated-FI operation')
def _entries(a):return dict(a.world.runtime.snapshot_metadata_entries)
def _get(a):
 _,_,_,decode,_=body._native()
 if KEY not in _entries(a):raise ValueError('Explicit0Native access admission required')
 m=decode(_entries(a)[KEY])
 if m['version']!=VERSION:raise ValueError('Exact new access revision only')
 return m
def _save(a,m):a.world.runtime.set_snapshot_metadata(KEY,body._encoded(m))
def _home(directory,a):return body._home(directory,regulation._identity(a)['life_id']).with_name(FOLDER)
def _record(a,m,directory,event):
 home=_home(directory,a);home.mkdir(exist_ok=True);line=(json.dumps(body._safe({'index':m['log_count'],'tick':int(a.tick),**event}),sort_keys=True,ensure_ascii=False,separators=(',',':'))+'\n').encode('utf8')
 proposed={**m,'log_count':m['log_count']+1,'log_chain_sha256':sha(bytes.fromhex(m['log_chain_sha256'])+line)};encoded=body._encoded(proposed)
 with(home/'eventos.jsonl').open('ab')as f:f.write(line);f.flush();os.fsync(f.fileno())
 m.update(proposed);a.world.runtime.set_snapshot_metadata(KEY,encoded)
def validate(a,row):
 validate_literal(row)
 if row['modo']not in NEW_MODES:return regulation.validate(a,row)
 regulation._identity(a)
 if row['modo']==STATE:return
 p,ph=protocol(True);old=regulation._get(a)
 if not old.get('ready')or not old.get('admitted')or old.get('pending')or old.get('uncertain'):raise ValueError('Actual closed formed R03 organization required; no repair or reset')
 if row['modo']==START:
  if KEY in _entries(a):raise ValueError('Existing access progress preserved; no readmission')
  return
 m=_get(a)
 if m['protocol_sha256']!=ph or not m.get('ready')or m.get('pending')or m.get('uncertain'):raise ValueError('Closed exact access progress required')
 if m['ordinal']>=p['max_queries']:raise ValueError('Finite declared eight-query access budget exhausted; no reset/refill')
 if regulation._selected(a)and any(row.get(k)for k in('sensor_ablation','actuator_ablation')):raise ValueError('No diagnostic lesion on selected principal')
def initialize(a,directory):
 validate(a,{'modo':START});p,ph=protocol(True);before=body._physical(a);literal=_entries(a)[regulation.KEY]
 if _home(directory,a).exists():raise ValueError('Existing journal preserved')
 m={'version':VERSION,'protocol_sha256':ph,'ready':True,'ordinal':0,'rows':[],'pending':None,'uncertain':False,'log_count':0,'log_chain_sha256':'00'*32,'R03_metadata_literal_sha256':sha(literal.encode('utf8'))}
 _save(a,m);_record(a,m,directory,{'kind':'EXPLICIT_FIXED_FUNCTIONAL_ACCESS_ADMITTED_ZERO_NATIVE','historical_legacy_API_unchanged':True,'not_new_anatomy_or_learning':True})
 if body._physical(a)!=before or _entries(a)[regulation.KEY]!=literal:raise RuntimeError('Administrative admission altered Native/R03 history')
 return{'version':VERSION,'admitted':True,'new_native_ticks':0,'requests':[],'physical_unchanged':True,'old_R03_metadata_literal_unchanged':True}
def query(a,row,directory):
 validate(a,row);p,ph=protocol(True);m=_get(a);start=int(a.tick);old_R03=_entries(a)[regulation.KEY];identity=regulation._identity(a)
 refs=[body._observe(a,body.at(v))for v in((-1,-1,0),(1,-1,0))]
 if int(refs[0]['clock'])%782!=int(refs[1]['clock'])%782:raise ValueError('Reference phase mismatch; no clock repair')
 calendar=body._helper().schedule_trial(start+16,int(refs[0]['clock'])+16,6);q=calendar['query_tick'];seed=calendar['seed_tick'];end=calendar['contact_tick']+2
 if seed!=q+7 or end-start>p['max_native_ticks']or calendar['outcome_injection_tick']!=q+408:raise ValueError('Fixed calendar cannot fit, no adaptive response-based timing')
 requests=[];safe=body.SafeAdapter(a);m.update(pending={'phase':'fixed_access_intent','query_tick':q},uncertain=True);_save(a,m)
 _record(a,m,directory,{'kind':'REGULATED_FI_ACCESS_INTENT','calendar':calendar,'public_operands':{'left':row['izquierda'],'right':row['derecha']},'environment_cue_inputs':0,'synthetic_message_inputs':0})
 try:
  safe.run_until(q-1);sensor=body._observe(a,regulation.SENSOR);datum=int(sensor['state']);sent=0 if row.get('sensor_ablation',False)else datum
  if not 0<=datum<=3:raise RuntimeError('Actual state outside identity codec')
  requests.extend(body._helper().submit_query(a.world,q,prefix=body.PREFIX));body._submit(a,body.PREFIX+'.datum',sent,q+3,requests,site=body.at((-1,0,1)),direction=(0,0,0))
  safe.run_until(q+4);reader=body._read(a,q);safe.run_until(q+6);motor=body._motor(reader['choice'])
  if motor is not None:requests.append(body._helper().submit_motor_copy(a.world,motor,seed,prefix=body.PREFIX))
  pulse=regulation._emit(a,motor,seed,requests,row.get('actuator_ablation',False))
  safe.run_until(q+136)
  from capacidades import pi05_transito_causal_R01 as old
  FI=old._fiplus(safe,{'modo':old.FIPLUS,'izquierda':row['izquierda'],'derecha':row['derecha'],'captura':'normal'},directory);requests.extend(FI['requests']);actual=FI['early_physical_choice']
  # The external functional checker runs AFTER the actual old FI result.
  # It never selects a pulse or supplies a response/credit-recipient target.
  expected=(row['izquierda']>row['derecha'])-(row['izquierda']<row['derecha']);failed=type(actual)is not int or actual!=expected
  if int(a.tick)>=calendar['outcome_injection_tick']:raise RuntimeError('Outcome deadline missed; no past event or rewind')
  safe.run_until(calendar['outcome_injection_tick']-1);requests.append(body._helper().submit_generic_outcome(a.world,failed,calendar['outcome_injection_tick'],prefix=body.PREFIX))
  frames=[]
  for tick in(calendar['outcome_injection_tick'],calendar['collision_tick'],calendar['contact_tick'],end):
   safe.run_until(tick);frames.append({'tick':int(a.tick),'A':body._observe(a,body.at((-1,-1,0))),'B':body._observe(a,body.at((1,-1,0)))})
  requests=body._receipts(a,requests);dose=body._summary(requests,start,int(a.tick));pulse=None if pulse is None else next(r for r in requests if r['id']==pulse['id'])
  result={'version':VERSION,'life_id':identity['life_id'],'ordinal':m['ordinal'],'before_tick':start,'after_tick':int(a.tick),'new_native_ticks':int(a.tick)-start,'calendar':calendar,'public_operands':{'left':row['izquierda'],'right':row['derecha']},'sensor':{'site':list(regulation.SENSOR),'tick':q-1,'observation':sensor,'actual_state_datum':datum,'submitted_state_datum':sent},'reader':reader,'native_motor':motor,'pulse_scheduled':pulse is not None,'pulse_applied':bool(pulse and pulse['receipt']['status']=='applied'),'actuator_request':pulse,'sensor_ablation':row.get('sensor_ablation',False),'actuator_ablation':row.get('actuator_ablation',False),'FI':FI,'early_physical_choice':actual,'old_q6_choice':FI['old_q6_choice'],'NULL_is_not_zero':True,'generic_return_failed':failed,'evaluator_after_function_expected_direction':expected,'requests':requests,'Native_inputs':dose,'return_frames':frames,'physical_after':body._physical(a),'old_R03_metadata_literal_unchanged':_entries(a)[regulation.KEY]==old_R03,'scope':'New prepared temporal access using the inherited acquired selector and fixed tool. Same physical FI frame/early decoder; no claim that the old198tick API was intact or that access timing was learned.'}
  if _entries(a)[regulation.KEY]!=old_R03:raise RuntimeError('R03 environment history changed')
  m['ordinal']+=1;m['rows'].append({'ordinal':result['ordinal'],'after_tick':int(a.tick),'early_physical_choice':actual,'Native_selector_choice':reader['choice'],'pulse_applied':result['pulse_applied'],'generic_return_failed':failed});m.update(pending=None if dose['all_terminal']else{'phase':'unknown_receipt'},uncertain=not dose['all_terminal']);_record(a,m,directory,{'kind':'REGULATED_FI_ACCESS_COMPLETED','result':result});return result
 except BaseException as error:
  m.update(uncertain=True,pending={'phase':'preserved_incomplete_functional_access','tick':int(a.tick),'error':type(error).__name__});_save(a,m);raise
def dispatch(a,row,*,actuator='closed',directory=None):
 validate(a,row)
 if row['modo']not in NEW_MODES:return regulation.dispatch(a,row,actuator=actuator,directory=directory)
 if row['modo']==STATE:return{'version':VERSION,'admitted':KEY in _entries(a),'progress':_get(a)if KEY in _entries(a)else None,'new_native_ticks':0}
 if directory is None or actuator!='closed':raise ValueError('Existing owned directory and closed action bridge required')
 if row['modo']==START:return initialize(a,directory)
 return query(a,row,directory)
def operational_dependencies(a,directory):
 prior=regulation.operational_dependencies(a,directory)
 if KEY not in _entries(a):return{'version':VERSION,'present':False,'R03':prior,'new_native_ticks':0}
 m=_get(a);p,ph=protocol();journal=_home(directory,a)/'eventos.jsonl';chain='00'*32;count=0
 for line in journal.read_bytes().splitlines(keepends=True):json.loads(line);chain=sha(bytes.fromhex(chain)+line);count+=1
 if m['protocol_sha256']!=ph or count!=m['log_count']or chain!=m['log_chain_sha256']or len(m['rows'])!=m['ordinal']:raise ValueError('Exact access history integrity required')
 return{'version':VERSION,'present':True,'ordinal':m['ordinal'],'pending':m['pending'],'uncertain':m['uncertain'],'journal_sha256':sha(journal.read_bytes()),'R03':prior,'new_native_ticks':0}
def uncertain(a):return regulation.uncertain(a)or(KEY in _entries(a)and bool(_get(a).get('uncertain')))
def code_files():return list(dict.fromkeys([Path(__file__),PROTOCOL,*regulation.code_files()]))
def routes_selected_legacy(a,row):
 # Fixed routing permission ONLY: never operands, target, future or old output.
 if not isinstance(row,dict)or row.get('modo')!='eci01-balance':return False
 entries=_entries(a)
 if regulation.body.SYSTEM_KEY not in entries:return False
 identity=json.loads(entries[regulation.body.SYSTEM_KEY])
 if identity.get('life_id')!='ECI02_PI03_REPRO_PI04_PI05_PI07_CAND_01':return False
 if not regulation._selected(a):return False
 root=Path(__file__).resolve().parents[1];contract=root/'contratos/PI07_REGULACION_USO_PRINCIPAL_01.json'
 if not contract.is_file():return False
 c=json.loads(contract.read_text('utf-8-sig'));p,ph=protocol();config=c.get('FI_access',{})
 if config.get('enabled')is not True:return False
 if c.get('status')!='COMMITTED'or c.get('life_id')!=identity['life_id']or config.get('protocol_sha256')!=ph or config.get('all_outer_FI_requests')is not True:raise ValueError('Exact committed all-outer-FI access permission required')
 return True
