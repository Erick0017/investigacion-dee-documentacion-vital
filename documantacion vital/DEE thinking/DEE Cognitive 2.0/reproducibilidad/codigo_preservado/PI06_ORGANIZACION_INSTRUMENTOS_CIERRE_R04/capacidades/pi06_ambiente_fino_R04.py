"""Fine-boundary confirmation of the unchanged R03 material pulse.

Every older mode delegates literally to the frozen R03 instrument. The host
checks RAW support at each boundary and stops; this is no learned regulator.
"""
from pathlib import Path
import hashlib,json,uuid
from capacidades import pi06_ambiente_R03 as previous
VERSION='DEE.PI06.fixed_exogenous_environment.fine_confirmation.R04'
FINE='eci01-pi06-ambiente-fino';CONTROL='eci01-pi06-control67'
MODES={*previous.MODES,FINE,CONTROL}
PROTOCOL=Path(__file__).with_name('PROTOCOLO_PI06_CONFIRMACION_R04.json')
PROTOCOL_SHA='30bc006be8f73859654fe47231f5ce19b5ac6128ea4e9bd40832fd30346baba8'
FINE_LIFE='ECI02_PI03_REPRO_PI04_PI05_PI06_R03_FINE_01'
CONTROL_LIFE='ECI02_PI03_REPRO_PI04_PI05_PI06_DISC_01'
SOURCE=previous.SOURCE
def protocol():
 data=PROTOCOL.read_bytes()
 if hashlib.sha256(data).hexdigest()!=PROTOCOL_SHA:raise ValueError('Exact prospective fine-confirmation protocol required')
 p=json.loads(data);_,fixture=previous.protocol()
 if p['status']!='SEALED_BEFORE_R04_NATIVE' or p['source_physical']!=SOURCE:raise ValueError('Unchanged exact post-interference826449 source required')
 instrument=p['matched_instrument']
 if instrument['support_check_cadence_ticks']!=1 or instrument['RAW_nonzero_stop_above']!=3000 or instrument['capture_offsets']!=list(range(68)) or instrument['anchor_offsets']!=[0,67]:raise ValueError('Fixed every-tick safety and complete0..67 capture')
 if p['fine_arm']['life_id']!=FINE_LIFE or p['control_arm']['life_id']!=CONTROL_LIFE or p['fixture_literal_unchanged']['sha256']!=previous.FIXTURE_SHA:raise ValueError('No new source, body, seed or dose')
 return p,fixture
def validate_literal(row):
 if isinstance(row,dict)and row.get('modo')in(FINE,CONTROL):
  if set(row)!={'modo','captura'}or row['captura']not in('global','normal'):raise ValueError('Only the fixed67-tick confirmation and capture mode')
  return row
 return previous.validate_literal(row)
def _identity(a,mode):
 identity=previous.previous.old._diagnostic(a)
 if identity['life_id']!=(FINE_LIFE if mode==FINE else CONTROL_LIFE):raise ValueError('Fine only in the last explicit clone; control only in the exact existing DISC life')
 return identity
def validate(a,row):
 if not isinstance(row,dict)or row.get('modo')not in(FINE,CONTROL):return previous.validate(a,row)
 validate_literal(row);_identity(a,row['modo']);_,fixture=protocol()
 from app.native_tools import physical
 before=physical(a.world)
 if any(before[k]!=v for k,v in SOURCE.items()):raise ValueError('Exact current closed826449 physical prefix only; no retiming/reset')
 names={birth['channel']for birth in fixture['births']}
 if any(i.name in names for i in a.world.interfaces):raise ValueError('One-time common interfaces already exist; do not replace or resend')
 return True
def _advance(a,capture_mode,identity,operation):
 from capacidades import pi05_transito_causal_R01 as baseline
 from app.native_tools import physical
 start=int(a.tick);end=start+67;planned=list(range(start,end+1));recorder=None;used=a
 if capture_mode=='global':
  capture=baseline._capture_module();system=Path(__file__).resolve().parents[1]
  target=system/'estado/observacion_pasiva'/identity['life_id']/('PI06_R04_'+uuid.uuid4().hex)
  recorder=capture.GlobalRecorder(target,N=67,ticks=planned,anchor_ticks={start,end},provenance={
   'life_id':identity['life_id'],'operation':operation,'module_version':VERSION,
   'protocol_sha256':PROTOCOL_SHA,'fixture_sha256':previous.FIXTURE_SHA,
   'host_safety_cadence_ticks':1,'host_safety_not_cognitive_regulation':True},max_frames=68,max_compressed_bytes=67108864)
  used=capture.CapturingAdapter(a,ticks=planned,recorder=recorder)
 observations=[];stopped=False
 for tick in planned:
  used.run_until(tick)
  support=sum(int(v)!=0 for v in a.world.runtime.raw_copy())
  observations.append({'tick':int(a.tick),'RAW_nonzero_support':support})
  if support>3000:stopped=True;break
 recording=None if recorder is None else recorder.close()
 return {'before_tick':start,'after_tick':int(a.tick),'new_native_ticks':int(a.tick)-start,'requested_horizon_ticks':67,
  'physical_after':physical(a.world),'host_safety_observations':observations,'host_safety_cadence_ticks':1,
  'host_safety_stop':stopped,'host_safety_reason':'RAW_nonzero_support_exceeded3000'if stopped else None,
  'host_safety_is_not_autoregulation':True,'no_between_boundary_support_bound_claim':True,
  'planned_capture_ticks':planned if capture_mode=='global'else[],
  'missing_planned_capture_ticks':list(range(int(a.tick)+1,end+1))if capture_mode=='global'else[],
  'external_global_capture':recording}
def dispatch(a,row,*,actuator='closed',directory=None):
 if not isinstance(row,dict)or row.get('modo')not in(FINE,CONTROL):return previous.dispatch(a,row,actuator=actuator,directory=directory)
 validate(a,row);identity=_identity(a,row['modo']);_,fixture=protocol()
 if actuator!='closed'or directory is None or Path(directory).resolve().name!=identity['life_id']:raise ValueError('Existing exact diagnostic home and legal closed interface only')
 from app.native_tools import physical,observe
 from dee_thinking import _native as d
 from dee_thinking.consolidated import exact_receipt
 before=physical(a.world);requests=[];raw_before=[]
 for birth in fixture['births']:
  observation=observe(a.world,birth['site']);raw_before.append({'sequence':birth['sequence'],'site':birth['site'],'observation':observation})
  channel=d.ChannelSpec();channel.name=birth['channel'];channel.injection_site=d.Coordinate(*birth['site']);channel.direction=d.Direction(*birth['direction'])
  channel.state=1;channel.semantic=1;channel.allow_experience=True;channel.allow_probe=False
  interface=d.InterfaceSpec();interface.name=birth['channel'];interface.channel=channel;a.world.declare_interface(interface)
  if row['modo']==FINE:
   tick=int(a.tick)+2;request=a.world.submit(birth['channel'],7,tick)
   requests.append({'id':int(request.id),'port':birth['channel'],'site':birth['site'],'direction':birth['direction'],
    'tick':tick,'payload':7,'declared_state':1,'declared_semantic':1})
 if physical(a.world)!=before:raise RuntimeError('Scheduling changed physical buffers or age; preserve future')
 result=_advance(a,row['captura'],identity,'same61_source_pulse_fine_safety'if row['modo']==FINE else'no_supply_same61_interfaces_fine_safety')
 for request in requests:request['receipt']=exact_receipt(a.world.runtime.receipt(request['id']))
 ids={r['id']for r in requests}
 if len(ids)!=len(requests):raise RuntimeError('Repeated Native input ID; preserve result')
 counts={}
 for request in requests:
  status=request['receipt']['status'];counts[status]=counts.get(status,0)+1
 unexpected=[s for s in counts if s not in('applied','rejected_occupied')]
 return {**result,'version':VERSION,'life_id':identity['life_id'],'condition':'nube'if row['modo']==FINE else'control',
  'fixture_sha256':previous.FIXTURE_SHA,'protocol_sha256':PROTOCOL_SHA,'physical_before':before,
  'source_observations_before':raw_before,'requests':requests,'common_interfaces_declared':61,
  'birth_inputs':{'unique_requested':len(ids),'status_counts':counts,'applied':counts.get('applied',0),'rejected_occupied':counts.get('rejected_occupied',0),
   'terminal_all_known':not unexpected,'unexpected_or_unresolved_statuses':unexpected,'all_fixed_sources_submitted':len(requests)==(61 if row['modo']==FINE else 0)},
  'admission_stop':bool(unexpected),'new_inputs_scheduled':len(requests),
  'scope':'Same fixed exogenous61-source pulse or no-supply control; every-tick external host safety. No learned protection, resampling, overwrite, repair or functional success implied.'}
def operational_dependencies(a,directory):return {**previous.operational_dependencies(a,directory),'R04_fine_confirmation_instrument':VERSION,'R04_cognitive_key_installed':False}
def uncertain(a):return previous.uncertain(a)
def code_files():return list(dict.fromkeys([Path(__file__),PROTOCOL,*previous.code_files()]))
