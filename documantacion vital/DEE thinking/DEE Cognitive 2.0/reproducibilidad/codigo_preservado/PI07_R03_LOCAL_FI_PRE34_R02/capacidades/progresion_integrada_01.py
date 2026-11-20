"""PI01 R04: selection by a DEE trace, legacy access, real local resource effect.

The opportunity sequence and codecs are prepared. Neither the controller nor
the access functions receive the environmental lock, utility or optimal route.
Only the actual action's consequence is returned to its own physical trace.
"""
from pathlib import Path
import hashlib,json
from capacidades import pi01_traza_legal_base as trace
from app.native_tools import physical
from dee_thinking.persistence import encode_metadata,decode_metadata

VERSION='PI01.integrated_access_and_resources.R04'
KEY='DEE.Cognitive.System.1.1.PI01.resource_task.R04'
ORIGIN=(0,5,20)
FOLDER='PI01_RESOURCE_BANK_R04'
N=67;FEEDBACK_PERIODS=4;POST_FEEDBACK=40
DEV=[(9,7,1,17,0),(12,5,1,23,0),(2,9,-1,31,1),(11,3,-1,29,0),(14,4,-1,37,1)]
EVAL_PAIRS=[(8,3),(13,5),(17,4),(16,9),(3,12),(15,2),(10,2),(19,11),(7,1),(20,13),(12,4),(18,7),(4,11),(9,2),(14,5),(16,4),(11,6),(20,8)]
CONTEXT=[11,17,23,29,101,103];GAPS=[0,1,0,2,1,0]

def task(a):
 e=dict(a.world.runtime.snapshot_metadata_entries)
 if KEY not in e:raise ValueError('Explicit PI01 environment admission required; no reconstruction on reopen')
 m=decode_metadata(e[KEY])
 if m['version']!=VERSION:raise ValueError('PI01 environment/version mismatch')
 return m
def save_task(a,m):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m))
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(b):return hashlib.sha256(b).hexdigest()
def fixtures(series):
 if series=='desarrollo':items=DEV
 else:items=[(l,r,-1 if i<6 or i>=12 else 1,CONTEXT[i%6],GAPS[i%6])for i,(l,r)in enumerate(EVAL_PAIRS)]
 return [{'public':{'left':l,'right':r,'context_load':c,'gap_periods':g},'private_environment':{'lock_polarity':s}}for l,r,s,c,g in items]

def environment_start(a,row,directory):
 if KEY in dict(a.world.runtime.snapshot_metadata_entries):raise ValueError('Environment already admitted; never reset learned history or resource progress')
 trace.get(a)
 home=Path(directory)/FOLDER
 if home.exists():raise ValueError('Existing unpaired resource folder; preserve and inspect, never recreate')
 (home/'reservoir').mkdir(parents=True);(home/'collected').mkdir()
 fs=fixtures(row['serie']);records=[]
 for i in range(len(fs)):
  payload=hashlib.sha256(('PI01 reservoir '+str(i)).encode('ascii')).digest()*2;p=home/'reservoir'/('%04d.bin'%i);p.write_bytes(payload);records.append({'episode':i,'file':'reservoir/'+p.name,'bytes':len(payload),'sha256':digest(payload)})
 m={'version':VERSION,'series':row['serie'],'arm':row['brazo'],'episode':0,'resources':0,'fixtures':fs,'repeat_fixture_cycle':True,'max_episodes':64,'resource_folder_relative':FOLDER,'reservoir':records,'committed_resources':[],'in_progress':None,'uncertain':False,'scope':'External environment/protocol state. These private conditions and artifacts do NOT enter the native controller or its access decoder.'}
 save_task(a,m)
 return {'version':VERSION,'admitted_external_environment':True,'physical_ticks':0,'resource_files':len(records),'bytes_per_resource':64,'arm':row['brazo'],'series':row['serie'],'private_conditions_not_transduced':True}

def native_route(a,public):
 """Receives only a generic opportunity, scalar nuisance and fixed P0 cadence."""
 m=trace.get(a);origin=tuple(m['origin']);seed=int(m['seed_effective_tick'])
 q=seed+((int(a.tick)+3-seed+N-1)//N)*N+public['gap_periods']*N
 sensor=trace.submit_arrival(a,m['prefix']+'sensor',public['context_load'],q)
 frames=[];selected=None
 for t in range(q-2,q+3):
  a.run_until(t);o=trace.obs(a,origin);frames.append({'tick':int(a.tick),'center':o,'context_radius3':trace.roi(a,3)})
  if t==q:
   direction=tuple(o['direction'])
   selected=next((k for k,v in trace.ACTION.items()if direction==v),None)if o['state']>0 and o['semantic']==1 else None
 receipt=trace.rr(a,sensor)
 return {'query_tick':q,'frozen_read_tick':q,'route':selected,'sensor_receipt':receipt,'frames':frames,'no_environment_target_in_this_function':True}

def use_selected_access(a,route,public,directory):
 """Fixed transduction: physical0 requests MA; physical1 requests FI.

No environment condition, reward, expected response or alternate answer is
passed. The unselected access is NOT called to look for a favorable result.
"""
 if route==0:
  from capacidades import mente_unificada_01 as mu
  result=mu.session(a,situations=[{'modo':'memoria','contexto':'alfa','operacion_memoria':'usar'}],directory=Path(directory)/'PI01_MA',actuator='closed',feedback='omit',detailed=False)
  row=result['rows'][0];unit=row['result']['rows'][0]if row.get('kind')=='explicit_operator_memory_access'else row
  response=unit['reader']['formed_native_command']
  return {'access':'MA_alfa','physical_response':response,'native_result':result,'operator_context_prepared':'alfa','unselected_access_called':False}
 if route==1:
  from capacidades import acceso_eci01 as access
  result=access.balance(a,public['left'],public['right'])
  return {'access':'FI128_early_q4','physical_response':result['early_physical_choice'],'native_result':result,'unselected_access_called':False}
 return {'access':None,'physical_response':None,'native_result':None,'unselected_access_called':False,'reason':'No unique valid native route; no fallback'}

def apply_environment(m,fixture,formed_response,actuator,directory):
 """An external lock releases actual bytes only after its actuator command.

This is an environment law/evaluator, not the participant or policy updater.
It returns success/failure, never the desired access or next policy.
"""
 ep=m['episode'];home=Path(directory)/m['resource_folder_relative'];src=home/'reservoir'/('%04d.bin'%ep)
 if not src.exists():
  payload=hashlib.sha256(('PI01 reservoir '+str(ep)).encode('ascii')).digest()*2
  with src.open('xb')as f:f.write(payload)
  m['reservoir'].append({'episode':ep,'file':'reservoir/'+src.name,'bytes':len(payload),'sha256':digest(payload)})
 payload=src.read_bytes();command=formed_response if actuator=='closed'and m['arm']!='nulled'else None
 if command is not None and(type(command)is not int or command not in(-1,0,1)):raise ValueError('Invalid physical actuator class; do not fill answer')
 accepted=command is not None and command==fixture['private_environment']['lock_polarity']
 before=m['resources'];record=None
 if accepted:
  dst=home/'collected'/('%04d.bin'%ep)
  with dst.open('xb')as f:f.write(payload)
  copied=dst.read_bytes()
  if copied!=payload:raise RuntimeError('Actual resource bytes do not match reservoir')
  m['resources']+=1;record={'episode':ep,'file':'collected/'+dst.name,'bytes':len(copied),'sha256':digest(copied)};m['committed_resources'].append(record)
 return {'formed_native_response':formed_response,'applied_command':command,'actuator_control':m['arm'],'accepted':accepted,'resources_before':before,'resources_after':m['resources'],'actual_resource':record,'private_lock_used_only_after_action':fixture['private_environment']['lock_polarity'],'reason':'actual_resource_released'if accepted else('no_emission_or_action_nullified'if command is None else'physical_command_did_not_open_current_lock')}

def feedback(a,route,negative,q,arm):
 """Prepared actual-action echo + generic negative valence. No optimal route."""
 m=trace.get(a);at=q+FEEDBACK_PERIODS*N
 if int(a.tick)>=at-2:raise RuntimeError('Access overran fixed feedback deadline; preserve future, no adaptive rescue')
 normal=trace.submit_arrival(a,m['prefix']+'normalizer',3,at);penalty=None;offset=None
 if negative and route is not None and arm not in('omit',):
  offset=0
  penalty=trace.submit_arrival(a,m['prefix']+'penalty'+str(route),5,at)
 frames=[]
 for t in range(at-2,at+3):
  a.run_until(t);frames.append({'tick':int(a.tick),'center':trace.obs(a,tuple(m['origin'])),'context_radius3':trace.roi(a,3)})
 a.run_until(at+POST_FEEDBACK)
 return {'fixed_tick':at,'normalizer':trace.rr(a,normal),'negative_valence':None if penalty is None else trace.rr(a,penalty),'omitted':negative and arm=='omit','negative_condition':negative,'selected_actual_route_echo':route,'target_route_sent':False,'frames':frames,'end_tick':int(a.tick)}

def step(a,directory,*,actuator='closed'):
 m=task(a)
 if m['in_progress']or m['uncertain']:raise ValueError('PI01 incomplete future: no repeated action or checkpoint fallback')
 if m['episode']>=m['max_episodes']:raise ValueError('Outside declared64-opportunity protocol, not physical memory death')
 ep=m['episode'];fixture=m['fixtures'][ep%len(m['fixtures'])];public=dict(fixture['public']);before=physical(a.world,occupation=True)
 m['in_progress']={'episode':ep,'phase':'native_route','started_tick':int(a.tick)};save_task(a,m)
 try:
  decision=native_route(a,public)
  m['in_progress']['phase']='selected_access';save_task(a,m)
  access=use_selected_access(a,decision['route'],public,directory)
  effect=apply_environment(m,fixture,access['physical_response'],actuator,directory)
  m['in_progress']['phase']='consequence_committed_awaiting_native_return';save_task(a,m)
  returned=feedback(a,decision['route'],not effect['accepted'],decision['query_tick'],m['arm'])
  m['episode']+=1;m['in_progress']=None;save_task(a,m)
 except BaseException:
  m['uncertain']=True;save_task(a,m);raise
 return {'version':VERSION,'episode':ep,'public_observation':public,'before':before,'native_decision':decision,'selected_access':access,'external_effect':effect,'native_return':returned,'after':physical(a.world,occupation=True),'initiative':'Operator offers opportunity; DEE selects0/1; fixed host codec calls selected access. No autonomous opportunity timing or plan claimed.','preparation':'Environment, reader, route->method codec and consequence channels prepared; policy contents change only through native encounters.'}

def resources_valid(a,directory):
 if KEY not in dict(a.world.runtime.snapshot_metadata_entries):return {'PI01_not_admitted':True}
 m=task(a);home=Path(directory)/m['resource_folder_relative']
 for item in m['reservoir']+m['committed_resources']:
  p=home/item['file']
  if not p.is_file()or p.stat().st_size!=item['bytes']or digest(p.read_bytes())!=item['sha256']:raise ValueError('Missing or altered PI01 operational resource: '+item['file'])
 return {'episode':m['episode'],'resources':m['resources'],'native_component':trace.get(a)['version'],'environment_protocol_sha256':digest(canonical(m).encode('utf-8')),'operational_resource_files':len(m['reservoir'])+len(m['committed_resources']),'in_progress':m['in_progress'],'uncertain':m['uncertain'],'scope':'Administrative continuation witness, not a participant answer.'}
def uncertain(a):
 if KEY not in dict(a.world.runtime.snapshot_metadata_entries):return False
 m=task(a);return bool(m['uncertain']or m['in_progress'])
def validate_literal(row):
 mode=row.get('modo')if isinstance(row,dict)else None
 if mode in('eci01-pi01-preparar','eci01-pi01-estado','eci01-pi01-paso'):
  if set(row)!={'modo'}:raise ValueError('PI01 accepts no target, preferred action, alternative answer or extra field')
 elif mode=='eci01-pi01-ambiente':
  if set(row)!={'modo','serie','brazo'}or row['serie']not in('desarrollo','evaluacion')or row['brazo']not in('real','omit','nulled'):raise ValueError('Explicit frozen PI01 external setup series/arm only')
 else:raise ValueError('Unknown PI01 R04 mode')
def validate(a,row):
 validate_literal(row)
 if row['modo']!='eci01-pi01-preparar':trace.get(a)
 if row['modo']=='eci01-pi01-paso':
  m=task(a)
  if m['in_progress']or m['uncertain']:raise ValueError('Preserved uncertain PI01 state')
def dispatch(a,row,*,actuator='closed',directory=None):
 validate(a,row)
 if row['modo']=='eci01-pi01-preparar':return trace.prepare(a,origin=ORIGIN)
 if directory is None:raise ValueError('Existing owner work_directory required, no laboratory lookup')
 if row['modo']=='eci01-pi01-ambiente':return environment_start(a,row,directory)
 if row['modo']=='eci01-pi01-paso':return step(a,directory,actuator=actuator)
 return {'native_component':trace.state(a),'external_environment':resources_valid(a,directory),'scope':'Auditor/administrator view; no Native material inputs.'}
