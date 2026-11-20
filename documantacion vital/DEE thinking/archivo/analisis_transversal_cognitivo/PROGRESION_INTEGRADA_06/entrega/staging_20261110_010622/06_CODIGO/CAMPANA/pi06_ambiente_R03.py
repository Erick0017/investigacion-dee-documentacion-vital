"""Fixed exogenous cloud/control and host-bounded evolution, no actor policy.

All previous operations delegate literally to R02. The environment fixture is
never resampled, filtered, relocated, cleared or converted into a Native plan.
RAW support limits are external host safety, never learned self-regulation.
"""
from pathlib import Path
import hashlib,json,uuid
from capacidades import pi06_interrupcion_R02 as previous
VERSION='DEE.PI06.fixed_exogenous_environment.R03'
ENV='eci01-pi06-ambiente';EVOLVE='eci01-pi06-ambiente-evolucion';MODES={*previous.MODES,ENV,EVOLVE}
PROTOCOL=Path(__file__).with_name('PROTOCOLO_PI06_AMBIENTE_R03_R06.json')
FIXTURE=Path(__file__).with_name('FIXTURE_PI06_AMBIENTE_R03_R02.json')
PROTOCOL_SHA='d70b1c2120569875113baab1c48da466457300c766761eb4f74ce65f5181b7d7'
FIXTURE_SHA='484b8efe0f0fbd53a815a4d33f17e0340e965370db44934aa99f35e4acbc1c7c'
SOURCE={'N':67,'tick':826449,'RAW_sha256':'acb6354a6c3acd711a0cd0047dc493fe12bdd6582ce5f29a8625d89f615acffc','clocks_sha256':'fc27f3df436cf69c8ab3fc4adff873b8859eaaa08b674c76c8a2874c29166dfd'}
def _sha(b):return hashlib.sha256(b).hexdigest()
def protocol():
 data=PROTOCOL.read_bytes();fdata=FIXTURE.read_bytes()
 if _sha(data)!=PROTOCOL_SHA or _sha(fdata)!=FIXTURE_SHA:raise ValueError('Frozen prospective cloud fixture/protocol changed')
 p=json.loads(data);f=json.loads(fdata)
 if p['status']!='SEALED_BEFORE_NATIVE'or p['N']!=67 or p['source_tick']!=826449 or p['fixture']['birth_count']!=61 or f['birth_count']!=61:raise ValueError('Exact declared61-source N67 fixture')
 if f['seed']!=61001 or f['Bernoulli_probability']!=0.4 or f['box_center']!=[35,35,35]or f['box_side']!=5 or not 0<len(f['births'])<=64:raise ValueError('No new seed/search/density or anatomy')
 sites=set();names=set()
 for i,b in enumerate(f['births']):
  if b['sequence']!=i or b['channel']in names or tuple(b['site'])in sites:raise ValueError('Fixed individual source order/identity differs')
  if any(type(x)is not int or not 33<=x<=37 for x in b['site'])or len(b['site'])!=3:raise ValueError('Bounded fixed5-cube only')
  if len(b['direction'])!=3 or not any(b['direction'])or any(type(x)is not int or x not in(-1,0,1)for x in b['direction']):raise ValueError('Fixed nonzero Moore26 direction')
  if b['state']!=1 or b['semantic']!=1 or b['payload']!=7 or b['delay_from_start']!=2:raise ValueError('Only legal SEM1/state1/c7 births; no SEM4 or clock/field edit')
  sites.add(tuple(b['site']));names.add(b['channel'])
 return p,f
def validate_literal(row):
 if isinstance(row,dict)and row.get('modo')==ENV:
  if set(row)!={'modo','condicion','captura'}or row['condicion']not in('nube','control')or row['captura']not in('global','normal'):raise ValueError('Fixed cloud/control and capture only')
  return row
 if isinstance(row,dict)and row.get('modo')==EVOLVE:
  if set(row)!={'modo','ticks','captura'}or type(row['ticks'])is not int or not 1<=row['ticks']<=2000 or row['captura']not in('global','normal'):raise ValueError('Only separate bounded1..2000-tick guarded evolution')
  return row
 return previous.validate_literal(row)
def _identity(a):
 identity=previous.old._diagnostic(a)
 if not identity['life_id'].split('PI06_',1)[-1].startswith('R03_'):raise ValueError('Separate explicitly named R03 diagnostic clone required')
 return identity
def validate(a,row):
 if not isinstance(row,dict)or row.get('modo')not in(ENV,EVOLVE):return previous.validate(a,row)
 validate_literal(row);_identity(a);_,f=protocol()
 if row['modo']==ENV:
  from app.native_tools import physical
  before=physical(a.world)
  if any(before[k]!=v for k,v in SOURCE.items()):raise ValueError('Only exact closed post-interference826449 prefix; no reset/retiming')
  if any(x.name in{b['channel']for b in f['births']}for x in a.world.interfaces):raise ValueError('One-time common environment interfaces already exist; never replace or resend')
 return True
def _guarded_advance(a,count,capture_mode,identity,operation):
 from capacidades import pi05_transito_causal_R01 as baseline
 from app.native_tools import physical
 start=int(a.tick);end=start+count
 planned=sorted(set(range(start,start+min(count,10)+1))|set(range(start+67,end+1,67))|{end})
 safety=sorted(set(range(start,end+1,67))|{end});recorder=None;used=a
 if capture_mode=='global':
  capture=baseline._capture_module();system=Path(__file__).resolve().parents[1]
  target=system/'estado/observacion_pasiva'/identity['life_id']/('PI06_R03_'+uuid.uuid4().hex)
  recorder=capture.GlobalRecorder(target,N=67,ticks=planned,anchor_ticks={start,end},provenance={'life_id':identity['life_id'],
    'operation':operation,'module_version':VERSION,'fixture_sha256':FIXTURE_SHA,'host_safety_not_cognitive_regulation':True},max_frames=42,max_compressed_bytes=67108864)
  used=capture.CapturingAdapter(a,ticks=planned,recorder=recorder)
 observations=[];stopped=False
 for tick in safety:
  used.run_until(tick)
  raw=a.world.runtime.raw_copy();support=sum(int(v)!=0 for v in raw)
  observations.append({'tick':int(a.tick),'RAW_nonzero_support':support})
  if support>3000:stopped=True;break
 recording=None if recorder is None else recorder.close()
 return {'before_tick':start,'after_tick':int(a.tick),'new_native_ticks':int(a.tick)-start,'requested_horizon_ticks':count,
  'physical_after':physical(a.world),'host_safety_observations':observations,'host_safety_stop':stopped,
  'host_safety_reason':'RAW_nonzero_support_exceeded3000'if stopped else None,'host_safety_is_not_autoregulation':True,
  'no_between_sample_support_bound_claim':True,'external_global_capture':recording}
def dispatch(a,row,*,actuator='closed',directory=None):
 if not isinstance(row,dict)or row.get('modo')not in(ENV,EVOLVE):return previous.dispatch(a,row,actuator=actuator,directory=directory)
 validate(a,row);identity=_identity(a);p,f=protocol()
 if actuator!='closed'or directory is None or Path(directory).resolve().name!=identity['life_id']:raise ValueError('Existing exact owned diagnostic home and legal closed interface only')
 if row['modo']==EVOLVE:
  result=_guarded_advance(a,row['ticks'],row['captura'],identity,'bounded_unforced_evolution_without_new_birth')
  return {**result,'version':VERSION,'life_id':identity['life_id'],'new_inputs_scheduled':0,'requests':[],
   'scope':'Existing legal evolution with finite host safety. No supplied packet/correction, and no learned regulation implied.'}
 from app.native_tools import physical,observe
 from dee_thinking import _native as d
 from dee_thinking.consolidated import exact_receipt
 before=physical(a.world);requests=[];raw_before=[]
 # Both arms declare the exact same61 interfaces, in the same fixed order.
 # Only the cloud submits; control has no supplied pulse, not another anatomy.
 for birth in f['births']:
   observation=observe(a.world,birth['site']);raw_before.append({'sequence':birth['sequence'],'site':birth['site'],'observation':observation})
   # Even known occupied SEM4 sites are individually submitted unchanged.
   # Official Native admission, not this host, rejects a RAW-nonzero birth.
   c=d.ChannelSpec();c.name=birth['channel'];c.injection_site=d.Coordinate(*birth['site']);c.direction=d.Direction(*birth['direction'])
   c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=False
   i=d.InterfaceSpec();i.name=birth['channel'];i.channel=c;a.world.declare_interface(i)
   if row['condicion']=='nube':
    tick=int(a.tick)+2;r=a.world.submit(birth['channel'],7,tick)
    requests.append({'id':int(r.id),'port':birth['channel'],'site':birth['site'],'direction':birth['direction'],'tick':tick,'payload':7,'declared_state':1,'declared_semantic':1})
 if physical(a.world)!=before:raise RuntimeError('Scheduling alone changed physical buffers/age; preserve future')
 result=_guarded_advance(a,268,row['captura'],identity,'one_fixed_cloud_or_no_supply_then268')
 for request in requests:request['receipt']=exact_receipt(a.world.runtime.receipt(request['id']))
 ids={r['id']for r in requests}
 if len(ids)!=len(requests):raise RuntimeError('Repeated Native input ID; preserve result')
 counts={}
 for request in requests:
  status=request['receipt']['status'];counts[status]=counts.get(status,0)+1
 unexpected=[s for s in counts if s not in('applied','rejected_occupied')]
 return {**result,'version':VERSION,'life_id':identity['life_id'],'condition':row['condicion'],'fixture_sha256':FIXTURE_SHA,
  'protocol_sha256':PROTOCOL_SHA,'physical_before':before,'source_observations_before':raw_before,'requests':requests,'common_interfaces_declared':len(f['births']),
  'birth_inputs':{'unique_requested':len(ids),'status_counts':counts,'applied':counts.get('applied',0),'rejected_occupied':counts.get('rejected_occupied',0),
   'terminal_all_known':not unexpected,'unexpected_or_unresolved_statuses':unexpected,'all_fixed_sources_submitted':len(requests)==(61 if row['condicion']=='nube' else 0)},
  'admission_stop':bool(unexpected),'new_inputs_scheduled':len(requests),
  'scope':'Prepared exogenous material supply, not a Native discovered body or plan. Every fixed source submitted individually; no filtering/resampling/overwriting. Occupied rejections are retained and do not imply uncertain transport. Host safety may stop the remaining fixed follow-up.'}
def operational_dependencies(a,directory):return {**previous.operational_dependencies(a,directory),'R03_environment_instrument':VERSION,'R03_cognitive_key_installed':False}
def uncertain(a):return previous.uncertain(a)
def code_files():return list(dict.fromkeys([Path(__file__),PROTOCOL,FIXTURE,*previous.code_files()]))
