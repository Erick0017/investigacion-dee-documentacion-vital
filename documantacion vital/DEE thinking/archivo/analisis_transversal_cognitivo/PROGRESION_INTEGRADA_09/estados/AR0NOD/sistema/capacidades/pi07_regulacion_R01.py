"""PI07: prepared new Native TC selector, physical sensor and fixed actuator.

Import is stdlib-only. No main, engine or world is opened here. All Native
mutations need the existing single owner and a sealed, explicit PI07 clone.
The environment prepares opportunities; only a fixed Native record selects the
pulse. Diagnostic forced actions are labelled and never acquisition evidence.
"""
from pathlib import Path
import hashlib,importlib.util,json,os
VERSION='DEE.PI07.physical_state_selective_regulation.R01'
KEY='DEE.Cognitive.PI07.regulation.R01';SYSTEM_KEY='DEE.Cognitive.System.1.1.life.v1'
FOLDER='PI07_REGULACION_R01';PREFIX='PI07.TC.R01';ORIGIN=(8,40,50);N=67
PROTOCOL=Path(__file__).with_name('PROTOCOLO_PI07_R01.json')
PREPARE='eci01-pi07-preparar';EPISODE='eci01-pi07-episodio';CALIBRATE='eci01-pi07-calibrar'
STATE='eci01-pi07-estado';WAIT='eci01-pi07-esperar';MODES={PREPARE,EPISODE,CALIBRATE,STATE,WAIT}
SENSOR=(52,48,47);ACTUATOR=(52,48,51);MESSAGE_READER=(53,48,51)
SINKS=((55,48,47),(55,48,51));CUES={'threat':((52,48,46),(0,0,1)),'falsecue':((51,48,47),(1,0,0))}
_HELPER=None
def _sha(b):return hashlib.sha256(b).hexdigest()
def _safe(x):return json.loads(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False))
def _helper():
 global _HELPER
 if _HELPER is None:
  p=Path(__file__).with_name('pi03_credito_generico_R01_BORRADOR.py');s=importlib.util.spec_from_file_location('PI07_preserved_TC_helper',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);_HELPER=m
 return _HELPER
def at(offset):return _helper().at(ORIGIN,offset)
def frame_rows():
 rows={tuple(r['site']):dict(r)for r in _helper().frame_rows(ORIGIN)}
 rows[at((1,-1,0))]['payload']=2 # Explicit unlearned P0 reference B, never a learned bank copy.
 for x in(-1,0,1):
  for z in(0,-1):
   site=at((3*x,3,3*z));row={'site':site,'state':0,'payload':0,'semantic':4,'direction':(0,0,0)}
   if site in rows and any(rows[site][k]!=row[k]for k in('state','payload','semantic')):raise ValueError('P0 stop geometry conflict')
   rows[site]=row
 for site in SINKS:rows[site]={'site':site,'state':0,'payload':0,'semantic':4,'direction':(0,0,0)}
 return [rows[p]for p in sorted(rows)]
def ports():
 result=[dict(r)for r in _helper().port_rows(ORIGIN,prefix=PREFIX)]
 result +=[{'name':PREFIX+'.datum','site':at((-1,0,1)),'direction':(0,0,0),'state':1,'semantic':1},
  {'name':'PI07.actuator.fixed_minusZ.R01','site':ACTUATOR,'direction':(0,0,-1),'state':1,'semantic':1},
  {'name':'PI07.environment.useful_plusX.R01','site':ACTUATOR,'direction':(1,0,0),'state':1,'semantic':1}]
 for cue,(site,direction)in CUES.items():result.append({'name':'PI07.environment.'+cue+'.R01','site':site,'direction':direction,'state':1,'semantic':1})
 return result
def protocol(material=False):
 data=PROTOCOL.read_bytes();p=json.loads(data)
 required={'schema','status','N','origin','initial_reference_payloads','delay_laps','max_ticks_per_episode','schedule','dependencies_sha256'}
 if not required<=set(p)or p['schema']!='DEE.PI07.regulation.protocol.R01':raise ValueError('Exact declared PI07 protocol required')
 if p['status']not in('DRAFT','SEALED_FOR_VIABILITY','SEALED_FOR_EVALUATION')or(material and p['status']=='DRAFT'):raise ValueError('Root must seal PI07 before Native')
 if p['N']!=67 or p['origin']!=list(ORIGIN)or p['initial_reference_payloads']!={'A':0,'B':2}or p['delay_laps']!=6:raise ValueError('Only fixed new N67 TC anatomy, P0 references0/2 and six laps')
 if type(p['max_ticks_per_episode'])is not int or not 1200<=p['max_ticks_per_episode']<=2000:raise ValueError('Finite1200..2000 episode horizon required')
 if not isinstance(p['schedule'],list)or not 1<=len(p['schedule'])<=64:raise ValueError('A finite1..64-opportunity schedule only')
 for row in p['schedule']:
  if set(row)-{'stage','cue','message_payload','left','right','return_failed'}or row.get('cue')not in('none','threat','falsecue'):raise ValueError('Only frozen environment inputs, not an actor action/answer')
  if row.get('stage')not in('viability','acquisition','reserve_A','changed_contingency','reserve_B','restore_contingency','post_reopen'):raise ValueError('Explicit canonical stage required')
  if row.get('message_payload')not in(None,5,8,11):raise ValueError('Only frozen useful-message payloads5/8/11 or absent')
  if any(type(row.get(k))is not int for k in('left','right'))or not 0<=row['right']<row['left']<=20:raise ValueError('Fixed positive independent comparison domain0..20')
  if 'return_failed'in row and type(row['return_failed'])is not bool:raise ValueError('An external declared return control is bool, never action/bank')
 arm=p.get('feedback',{}).get('arm',p.get('feedback_arm','real'))
 if arm not in('real','none','yoked'):raise ValueError('Only real/none or explicitly fixed yoked return')
 if arm=='yoked'and any('return_failed'not in row for row in p['schedule']):raise ValueError('A yoked schedule must be fixed before execution')
 if p.get('calendar',{}).get('planning_lead_ticks')!=16:raise ValueError('Fixed sixteen-tick source planning lead required')
 for name,h in p['dependencies_sha256'].items():
  if Path(name).name!=name or len(h)!=64 or _sha(Path(__file__).with_name(name).read_bytes())!=h:raise ValueError('Exact local dependency differs: '+name)
 return p,_sha(data)
def validate_literal(row):
 if not isinstance(row,dict):raise ValueError('One explicit PI07 literal required')
 mode=row.get('modo')
 if mode in(PREPARE,STATE)and set(row)=={'modo'}:return
 if mode==EPISODE and set(row)in({'modo'},{'modo','actuator_ablation'})and('actuator_ablation'not in row or type(row['actuator_ablation'])is bool):return
 if mode==CALIBRATE and set(row)=={'modo','forzar'}and row['forzar']in('pulso','nada'):return
 if mode==WAIT and set(row)=={'modo','ticks'}and type(row['ticks'])is int and 1<=row['ticks']<=2000:return
 raise ValueError('Unknown PI07 literal/fields; no condition, target, action, path, site or reader override')
def _native():
 from dee_thinking import _native as d
 from dee_thinking.consolidated import exact_observation,exact_receipt
 from dee_thinking.persistence import decode_metadata,encode_metadata
 return d,exact_observation,exact_receipt,decode_metadata,encode_metadata
def _identity(a):
 _,_,_,decode,_=_native();entries=dict(a.world.runtime.snapshot_metadata_entries)
 if SYSTEM_KEY not in entries or int(a.world.runtime.dimension)!=67:raise ValueError('Complete inherited N67 life required')
 identity=decode(entries[SYSTEM_KEY]);life=identity['life_id']
 if not life.startswith('ECI02_PI03_REPRO_')or'PI04_'not in life or'PI05_'not in life or'PI07_'not in life or identity.get('profile')!='fisica_directa':raise ValueError('Explicit inherited PI07 diagnostic life only')
 active=Path(__file__).resolve().parents[1]/'estado/ACTIVO.json'
 if active.exists()and json.loads(active.read_text('utf-8-sig')).get('life_id')==life:raise ValueError('Selected principal is never a PI07 diagnostic target')
 return identity
def _get(a):
 _,_,_,decode,_=_native();entries=dict(a.world.runtime.snapshot_metadata_entries)
 if KEY not in entries:raise ValueError('Explicit PI07 preparation required')
 m=decode(entries[KEY])
 if m['version']!=VERSION:raise ValueError('Do not reinterpret another PI07 revision')
 return m
def _encoded(m):
 _,_,_,_,encode=_native();safe=_safe(m)
 if len(json.dumps(safe,ensure_ascii=False,separators=(',',':')).encode('utf8'))>65536:raise ValueError('Progress exceeds64KB; full evidence belongs externally')
 return encode(safe)
def _save(a,m):a.world.runtime.set_snapshot_metadata(KEY,_encoded(m))
def _home(directory,life):
 path=Path(directory).resolve(strict=True)
 if path.name!=life:raise ValueError('Existing exact owned diagnostic home required')
 for p in(path,*path.parents):
  if p.exists()and(p.is_symlink()or getattr(p.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked scientific workspace')
 return path/FOLDER
def _record(a,m,directory,event):
 home=_home(directory,_identity(a)['life_id']);home.mkdir(exist_ok=True)
 data=(json.dumps(_safe({'index':m['log_count'],'tick':int(a.tick),**event}),ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf8')
 proposed={**m,'log_count':m['log_count']+1,'log_chain_sha256':_sha(bytes.fromhex(m['log_chain_sha256'])+data)}
 capsule=_encoded(proposed) # Validate BEFORE journal append, not after a quota failure.
 with(home/'eventos.jsonl').open('ab')as out:out.write(data);out.flush();os.fsync(out.fileno())
 m.update(proposed);a.world.runtime.set_snapshot_metadata(KEY,capsule)
def _observe(a,site):
 d,exact,_,_,_=_native();return exact(a.world.runtime.observe(d.Coordinate(*site)))
def _physical(a):
 from app.native_tools import physical
 return physical(a.world)
class HostSafetyStop(RuntimeError):pass
class SafeAdapter:
 def __init__(self,a):self.a=a;self.safety=[]
 def __getattr__(self,name):return getattr(self.a,name)
 def run_until(self,end):
  end=int(end)
  if end<int(self.a.tick):raise ValueError('No rewind')
  while int(self.a.tick)<end:
   self.a.run_until(min(end,int(self.a.tick)+32))
   support=sum(int(v)!=0 for v in self.a.world.runtime.raw_copy());self.safety.append({'tick':int(self.a.tick),'RAW_nonzero_support':support})
   if support>3000:raise HostSafetyStop('External host RAWsupport>3000; no more advance/corrective input')
def _declare(world,name,site,direction,state=1,semantic=1):
 d,_,_,_,_=_native()
 if name in set(world.runtime.channel_names):raise ValueError('New channel namespace already exists; no replacement')
 c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*site);c.direction=d.Direction(*direction);c.state=state;c.semantic=semantic;c.allow_experience=True;c.allow_probe=False
 interface=d.InterfaceSpec();interface.name=name;interface.channel=c;world.declare_interface(interface)
def _submit(a,name,payload,tick,requests,*,site=None,direction=None):
 if tick<=int(a.tick):raise ValueError('Future Native admission boundary required')
 r=a.world.submit(name,int(payload),int(tick));v={'id':int(r.id),'channel':name,'payload':int(payload),'requested_tick':int(tick)}
 if site is not None:v.update(site=list(site),direction=list(direction))
 requests.append(v);return v
def _receipts(a,requests):
 _,_,exact,_,_=_native()
 return[{**r,'receipt':exact(a.world.runtime.receipt(r['id']))}for r in requests]
def _summary(requests,start,end):
 unique={};aliases=0
 for r in requests:
  receipt=r['receipt'];rid=r['id']
  if type(rid)is not int or rid!=receipt['id']or not start<=receipt['requested_tick']<=end:raise ValueError('Only direct current-operation receipts/IDs')
  if rid in unique:
   if unique[rid]!=receipt:raise ValueError('Conflicting Native receipt alias')
   aliases+=1
  unique[rid]=receipt
 counts={}
 for r in unique.values():counts[r['status']]=counts.get(r['status'],0)+1
 other=[v for v in counts if v!='applied'and not v.startswith('rejected')]
 return{'unique_requested':len(unique),'applied':counts.get('applied',0),'rejected':sum(v for k,v in counts.items()if k.startswith('rejected')),'pending_or_other':sum(counts[k]for k in other),'status_counts':counts,'all_terminal':not other,'aliases_deduplicated':aliases}
def preflight(a):
 identity=_identity(a);rows=frame_rows();births={tuple(r['site'])for r in rows};points=set(_helper().geometry_footprint(ORIGIN,halo=1))
 points.update(tuple(r['site'])for r in ports());points.update((SENSOR,MESSAGE_READER,*SINKS))
 observations=[{'site':list(site),'observation':_observe(a,site)}for site in sorted(points)]
 conflicts=[]
 for row in observations:
  site=tuple(row['site']);raw=int(row['observation']['raw'])
  if raw==0:continue
  conflicts.append(row)
 names={PREFIX+'.prepare.'+str(i)for i in range(len(rows))}|{r['name']for r in ports()}
 reused=sorted(names.intersection(set(a.world.runtime.channel_names)))
 refs=[_observe(a,at(v))for v in((-1,-1,0),(1,-1,0))]
 return{'life_id':identity['life_id'],'checked_sites':len(points),'conflicts':conflicts,'reused_channels':reused,'reference_clocks':[str(v['clock'])for v in refs],
  'eligible':not conflicts and not reused and int(refs[0]['clock'])%782==int(refs[1]['clock'])%782,
  'scope':'Strict whole-footprint RAW0 preflight; inherited support is never removed, overwritten or silently tolerated. No guarantee of future isolation.'}
def _viability_case(identity,row,p):
 # External forced diagnostic preparation ONLY. Normal EPISODE never uses
 # this function, a case label or the life ID to choose an environment/action.
 tail=identity['life_id'].split('PI07_',1)[-1]
 matches=[case for case in p.get('viability',{}).get('cases',[])if case.get('id')==tail]
 if len(matches)!=1 or matches[0].get('forced_action')!=row.get('forzar'):raise ValueError('Exact predeclared VIAB life suffix and matching forced action required')
 case=matches[0]
 return {'stage':'viability',**{key:case[key]for key in('cue','message_payload','left','right')}}
def validate(a,row):
 validate_literal(row);identity=_identity(a)
 if row['modo']==STATE:return
 p,ph=protocol(material=True)
 if row['modo']==PREPARE:
  if KEY in dict(a.world.runtime.snapshot_metadata_entries):raise ValueError('Already prepared; never reinstall')
  return
 if row['modo']==WAIT:return
 m=_get(a)
 if not m.get('ready')or m['protocol_sha256']!=ph or m.get('pending')or m.get('uncertain'):raise ValueError('Not ready or an uncertain/pending future must be preserved')
 if m['ordinal']>=len(p['schedule']):raise ValueError('Explicit finite environment exhausted; no counter reset')
 if row['modo']==CALIBRATE:
  if m['ordinal']!=0:raise ValueError('A forced VIAB case is one-shot; preserve and do not retry')
  _viability_case(identity,row,p)
 if row['modo']==EPISODE and(p['status']!='SEALED_FOR_EVALUATION'or p.get('evaluation_authorized_by_this_version')is not True):raise ValueError('Viability protocol does not authorize acquisition/evaluation; only explicit forced diagnostic calibration')
def prepare(a,directory):
 validate(a,{'modo':PREPARE});p,ph=protocol(material=True);identity=_identity(a);check=preflight(a)
 if not check['eligible']:raise ValueError('Unsafe PI07 P0 geometry; preserve without clearing: '+repr(check))
 home=_home(directory,identity['life_id'])
 if home.exists():raise ValueError('Existing preparation folder is preserved')
 start=int(a.tick);m={'version':VERSION,'life_id':identity['life_id'],'protocol_sha256':ph,'prepared_tick':start,'ready':False,'ordinal':0,'pending':{'phase':'P0_preparation'},'uncertain':True,'rows':[],'log_count':0,'log_chain_sha256':'00'*32}
 _save(a,m);_record(a,m,directory,{'kind':'P0_PREPARATION_INTENT','preflight':check,'initial_reference_payloads':{'A':0,'B':2},'old_selector_never_modified':True})
 requests=[];arrival=start+2;used=SafeAdapter(a)
 for i,r in enumerate(frame_rows()):
  name=PREFIX+'.prepare.'+str(i);_declare(a.world,name,r['site'],r['direction'],r['state'],r['semantic']);_submit(a,name,r['payload'],arrival,requests,site=r['site'],direction=r['direction'])
 used.run_until(arrival+1);requests=_receipts(a,requests);summary=_summary(requests,start,int(a.tick));ready=summary['applied']==summary['unique_requested']
 if ready:
  for r in ports():_declare(a.world,r['name'],r['site'],r['direction'],r['state'],r['semantic'])
 m.update(ready=ready,pending=None if summary['all_terminal']else{'phase':'unknown_P0_admission'},uncertain=not summary['all_terminal'])
 _record(a,m,directory,{'kind':'P0_PREPARATION_COMPLETED','requests':requests,'Native_inputs':summary,'ready':ready,'safety':used.safety})
 return{'version':VERSION,'before_tick':start,'after_tick':int(a.tick),'new_native_ticks':int(a.tick)-start,'ready':ready,'requests':requests,'Native_inputs':summary,'preflight':check,'new_selector_origin':list(ORIGIN),'old_Q_untouched':True,'scope':'Legal unlearned P0 anatomy/reference bias/stops/sinks only, not acquired regulation.'}
def _read(a,q):
 if int(a.tick)!=q+4:raise ValueError('Only fixed centralq+4 reading')
 observation=_observe(a,ORIGIN);v=list(observation['direction']);valid=int(observation['state'])>0 and int(observation['semantic'])==1 and len(v)==3 and v[0]in(-1,0,1)and v[1]==1 and v[2]in(-1,0)
 return{'tick':int(a.tick),'site':list(ORIGIN),'observation':observation,'choice':v[0]if valid else None,'zero_is_not_NULL':True,'fixed_signature':'activeSEM1 direction[dx,+1,z], dx-1/0/+1,z-1/0'}
def _motor(choice):return(-1 if choice==0 else choice)if type(choice)is int and choice in(-1,0,1)else None
def _emit(a,motor,seed,requests,ablation):
 # This function has NO environment, sensor, target, expected answer or bank.
 if motor==1 and not ablation:return _submit(a,'PI07.actuator.fixed_minusZ.R01',0,seed,requests,site=ACTUATOR,direction=(0,0,-1))
 return None
def episode(a,row,directory):
 validate(a,row);p,ph=protocol(material=True);identity=_identity(a);m=_get(a);start=int(a.tick);spec=_viability_case(identity,row,p)if row['modo']==CALIBRATE else p['schedule'][m['ordinal']];used=SafeAdapter(a)
 refs=[_observe(a,at(v))for v in((-1,-1,0),(1,-1,0))]
 if int(refs[0]['clock'])%782!=int(refs[1]['clock'])%782:raise ValueError('Reference phases diverged; no repair')
 cal=_helper().schedule_trial(start+16,int(refs[0]['clock'])+16,6);q=cal['query_tick'];seed=cal['seed_tick'];S=q-1;end=cal['contact_tick']+2
 if seed!=q+7 or cal['outcome_injection_tick']!=q+408 or end-start>p['max_ticks_per_episode']or q-2<=start:raise ValueError('Frozen six-lap calendar/source lead cannot fit; no adaptive retiming')
 forced=row.get('forzar')if row['modo']==CALIBRATE else None;ablation=row.get('actuator_ablation',False)
 m['pending']={'phase':'episode_started','ordinal':m['ordinal'],'query_tick':q};m['uncertain']=True;_save(a,m)
 _record(a,m,directory,{'kind':'OPPORTUNITY_INTENT','ordinal':m['ordinal'],'calendar':cal,'environment_spec':spec,'forced_operator_action':forced,'actuator_ablation':ablation,'attribution':'Environment inputs are prepared. Actor sees only the fixed physical state datum; diagnostic force is not learned selection.'})
 requests=[];message_artifact=None
 try:
  if spec['cue']!='none':
   site,direction=CUES[spec['cue']];_submit(a,'PI07.environment.'+spec['cue']+'.R01',0,q-2,requests,site=site,direction=direction)
  used.run_until(S);sensor=_observe(a,SENSOR);datum=int(sensor['state'])
  if not 0<=datum<=3:raise RuntimeError('Native2bit state outside declared identity codec')
  requests.extend(_helper().submit_query(a.world,q,prefix=PREFIX));_submit(a,PREFIX+'.datum',datum,q+3,requests,site=at((-1,0,1)),direction=(0,0,0))
  used.run_until(q+4);reader=_read(a,q);used.run_until(q+6);native_motor=_motor(reader['choice']);motor=(1 if forced=='pulso'else -1)if forced else native_motor
  if motor is not None:requests.append(_helper().submit_motor_copy(a.world,motor,seed,prefix=PREFIX))
  # A fixed environment pulse may compete with the selected actuator at one
  # Native inlet. Runtime, not this host, resolves the same-boundary conflict.
  message_request=None
  if spec['message_payload']is not None:message_request=_submit(a,'PI07.environment.useful_plusX.R01',spec['message_payload'],seed,requests,site=ACTUATOR,direction=(1,0,0))
  action=_emit(a,motor,seed,requests,ablation)
  _record(a,m,directory,{'kind':'NATIVE_SELECTION_AND_FIXED_ACTUATOR','sensor':{'site':list(SENSOR),'tick':S,'observation':sensor,'identity_state_datum':datum},'reader':reader,'native_motor':native_motor,'actual_motor':motor,'operator_forced':forced is not None,'copy_at_seed':motor is not None,'actuator_request':action})
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
  arm=p.get('feedback',{}).get('arm',p.get('feedback_arm','real'));returned=False if arm=='none'else spec['return_failed']if arm=='yoked'else actual_failed
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
  result={'version':VERSION,'life_id':identity['life_id'],'preparation_life_id':m['life_id'],'ordinal':m['ordinal'],'before_tick':start,'after_tick':int(a.tick),'new_native_ticks':int(a.tick)-start,'calendar':cal,'environment_spec':spec,
   'sensor':{'site':list(SENSOR),'tick':S,'observation':sensor,'identity_state_datum':datum},'reader':reader,'native_motor':native_motor,'actual_motor':motor,'operator_forced_action':forced,
   'Native_selection_valid':native_motor is not None,'actuator_ablation':ablation,'actuator_request':action,'pulse_scheduled':action is not None,'pulse_applied':pulse_applied,'pulse_emitted':pulse_applied,
   'message':{'request':message_request,'own_native_receipt':message_receipt,'read_tick':seed+1,'site':list(MESSAGE_READER),'observation':message_observation,'actual_payload':actual_message,'required_payload':spec['message_payload'],'delivered_exact':delivered,'artifact':message_artifact},
   'FI':result_FI,'FI_planned_calendar':planned_FI,'FI_query_expected':q+192,'FI_query_matches_predicted_phase':result_FI['calendar']['query_tick']==q+192,
   'actual_failed':actual_failed,'returned_failed':returned,'feedback_arm':arm,'requests':requests,'Native_inputs':summary,'reference_before':refs,'return_frames':return_frames,
   'physical_after':_physical(a),'host_safety':{'check_max_step_ticks':32,'observations':used.safety,'is_external_not_learned_regulation':True},
   'scope':'New prepared Native selection plus identity sensor and fixed transducer. Host offers opportunities/environment and evaluates actual function; forced controls are not Native learned decisions. Useful learning requires causal controls and conservation.'}
  m['ordinal']+=1;m['rows'].append({'ordinal':result['ordinal'],'after_tick':int(a.tick),'native_choice':reader['choice'],'actual_failed':actual_failed,'pulse_scheduled':action is not None,'pulse_applied':pulse_applied,'message_delivered':delivered,'FI_choice':result_FI['old_q6_choice'],'forced':forced is not None})
  m['pending']=None if terminal else{'phase':'unknown_terminal_receipts'};m['uncertain']=not terminal
  _record(a,m,directory,{'kind':'EPISODE_COMPLETED','result':result})
  return result
 except BaseException as error:
  m['uncertain']=True;m['pending']={'phase':'preserved_incomplete_episode','ordinal':m['ordinal'],'tick':int(a.tick),'reason':type(error).__name__}
  _save(a,m)
  raise
def state(a):
 entries=dict(a.world.runtime.snapshot_metadata_entries)
 return{'version':VERSION,'prepared':KEY in entries,'progress':_get(a)if KEY in entries else None,'physical':_physical(a),'new_native_ticks':0,'scope':'Read-only progress/physical hashes, no material query or automatic preparation.'}
def dispatch(a,row,*,actuator='closed',directory=None):
 validate(a,row)
 if row['modo']==STATE:return state(a)
 if directory is None or actuator!='closed':raise ValueError('Existing owned diagnostic home and closed legal interface required')
 _home(directory,_identity(a)['life_id'])
 if row['modo']==PREPARE:return prepare(a,directory)
 if row['modo']==WAIT:
  start=int(a.tick);used=SafeAdapter(a);used.run_until(start+row['ticks']);return{'version':VERSION,'before_tick':start,'after_tick':int(a.tick),'new_native_ticks':row['ticks'],'new_inputs_scheduled':0,'requests':[],'host_safety':used.safety,'not_autoregulation':True}
 return episode(a,row,directory)
def uncertain(a):return KEY in dict(a.world.runtime.snapshot_metadata_entries)and bool(_get(a).get('uncertain'))
def operational_dependencies(a,directory):
 if KEY not in dict(a.world.runtime.snapshot_metadata_entries):return{'version':VERSION,'prepared':False,'new_native_ticks':0}
 m=_get(a);p,ph=protocol();identity=_identity(a)
 if ph!=m['protocol_sha256']:raise ValueError('Installed protocol changed; preserve historical source/version')
 home=_home(directory,identity['life_id']);journal=home/'eventos.jsonl';chain='00'*32;count=0
 with journal.open('rb')as rows:
  for line in rows:json.loads(line);chain=_sha(bytes.fromhex(chain)+line);count+=1
 if count!=m['log_count']or chain!=m['log_chain_sha256']:raise ValueError('Progress/journal mismatch; no reset or implicit replay')
 for row in m['rows']:
  file=home/('mensaje_%04d.bin'%row['ordinal'])
  if row['message_delivered']and not file.is_file():raise ValueError('A delivered real message artifact is missing')
 return{'version':VERSION,'prepared':m['ready'],'protocol_sha256':ph,'ordinal':m['ordinal'],'remaining':len(p['schedule'])-m['ordinal'],'pending':m['pending'],'uncertain':m['uncertain'],'journal':str(journal),'journal_sha256':_sha(journal.read_bytes()),'new_native_ticks':0,'complete_state_required':'Whole Native snapshot, interfaces/agenda, existing SQLite/outbox/receipts and this local journal/artifacts. No partial RAW/clocks restoration.'}
def code_files():return[Path(__file__),PROTOCOL,Path(__file__).with_name('pi03_credito_generico_R01_BORRADOR.py')]
