"""One legal counterflow/sham diagnostic; every R01 operation delegates unchanged.

No learned repair, SEM4 support, reset, RAW/clock assignment or favourable
reader. The new mode schedules exactly one zero SEM1 packet then advances3.
The later intact FI query is a separate explicit preregistered operation.
"""
from pathlib import Path
import hashlib,json,uuid
from capacidades import pi06_organizacion_R01 as old
VERSION='DEE.PI06.legal_counterflow_diagnostic.R02'
INTERRUPT='eci01-pi06-interrupcion';MODES={*old.MODES,INTERRUPT}
PROTOCOL=Path(__file__).with_name('PROTOCOLO_PI06_INTERRUPCION_R02.json')
SITES={'contraflujo':[52,48,51],'sham':[60,48,51]};CARRIER=[52,48,47];CONTACT=[52,48,50]
def _sha(b):return hashlib.sha256(b).hexdigest()
def protocol():
 data=PROTOCOL.read_bytes();p=json.loads(data)
 if p.get('schema')!='DEE.PI06.counterflow.protocol.R02'or p.get('status')!='SEALED':raise ValueError('Frozen prospective counterflow protocol required')
 if p.get('source')!={'N':67,'tick':826449,'RAW_sha256':'acb6354a6c3acd711a0cd0047dc493fe12bdd6582ce5f29a8625d89f615acffc','clocks_sha256':'fc27f3df436cf69c8ab3fc4adff873b8859eaaa08b674c76c8a2874c29166dfd'}:raise ValueError('Only the exact observed closed R01 development future')
 if p.get('sites')!=SITES or p.get('carrier')!=CARRIER or p.get('contact')!=CONTACT:raise ValueError('Fixed declared geometry only')
 if p.get('birth')!={'state':1,'semantic':1,'s_reg':0,'direction':[0,0,-1],'delay_ticks':2}or p.get('advance_ticks')!=3:raise ValueError('One legal SEM1 zero packet and fixed3-tick advance')
 for name,h in p['dependencies_sha256'].items():
  if Path(name).name!=name or _sha(Path(__file__).with_name(name).read_bytes())!=h:raise ValueError('Exact R01 dependency changed: '+name)
 return p,_sha(data)
def validate_literal(row):
 if isinstance(row,dict)and row.get('modo')==INTERRUPT:
  if set(row)!={'modo','condicion','captura'}or row['condicion']not in SITES or row['captura']not in('global','normal'):raise ValueError('Fixed counterflow/sham and prospective capture only')
  return row
 return old.validate_literal(row)
def _preflight(a,row):
 validate_literal(row);identity=old._diagnostic(a);p,ph=protocol()
 from app.native_tools import physical,observe
 before=physical(a.world)
 if any(before[k]!=p['source'][k]for k in p['source']):raise ValueError('Exact source N/tick/RAW/clocks required, no reset/retiming')
 site=SITES[row['condicion']];observed={name:observe(a.world,coord)for name,coord in(('source',site),('carrier',CARRIER),('contact',CONTACT))}
 if int(observed['source']['raw'])!=0 or int(observed['contact']['raw'])!=0:raise ValueError('Counter/sham source and contact must be recorded RAW0; no clearing')
 if int(observed['carrier']['raw'])!=1224979098644774913:raise ValueError('The actual recorded SEM1 zero +Z carrier is absent/different')
 name='PI06.R02.'+row['condicion']+'.SEM1.zero.minusZ'
 if any(i.name==name for i in a.world.interfaces):raise ValueError('One-time diagnostic channel already exists; do not reapply')
 return identity,p,ph,before,observed,name
def validate(a,row):
 if row.get('modo')!=INTERRUPT:return old.validate(a,row)
 _preflight(a,row);return True
def dispatch(a,row,*,actuator='closed',directory=None):
 if row.get('modo')!=INTERRUPT:return old.dispatch(a,row,actuator=actuator,directory=directory)
 if actuator!='closed'or directory is None:raise ValueError('Existing owned clone directory and legal closed interface only')
 identity,p,ph,before,observed,name=_preflight(a,row)
 if Path(directory).resolve().name!=identity['life_id']:raise ValueError('Exact owned diagnostic life directory only')
 from dee_thinking import _native as d
 from dee_thinking.consolidated import exact_receipt
 from app.native_tools import physical,observe
 from capacidades import pi05_transito_causal_R01 as baseline
 c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*SITES[row['condicion']]);c.direction=d.Direction(0,0,-1)
 c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=False
 interface=d.InterfaceSpec();interface.name=name;interface.channel=c;a.world.declare_interface(interface)
 start=int(a.tick);tick=start+2;r=a.world.submit(name,0,tick)
 request={'id':int(r.id),'port':name,'site':SITES[row['condicion']],'direction':[0,0,-1],'tick':tick,'payload':0,'declared_state':1,'declared_semantic':1}
 scheduled=physical(a.world)
 if scheduled!=before:raise RuntimeError('Legal scheduling changed physical buffers; preserve actual future')
 recorder=None;used=a;planned=list(range(start,start+4))
 if row['captura']=='global':
  capture=baseline._capture_module();system=Path(__file__).resolve().parents[1]
  target=system/'estado/observacion_pasiva'/identity['life_id']/('PI06_R02_'+uuid.uuid4().hex)
  recorder=capture.GlobalRecorder(target,N=67,ticks=planned,anchor_ticks={start,start+3},
   provenance={'life_id':identity['life_id'],'protocol_sha256':ph,'module_version':VERSION,'condition':row['condicion'],
    'operation':'one_legal_zero_counterflow_then_evolution3','no_expected_response_or_actor_answer':True},max_frames=4,max_compressed_bytes=33554432)
  used=capture.CapturingAdapter(a,ticks=planned,recorder=recorder)
 used.run_until(start+3)
 request['receipt']=exact_receipt(a.world.runtime.receipt(request['id']))
 recording=None if recorder is None else recorder.close();after=physical(a.world)
 if int(a.tick)!=start+3:raise RuntimeError('Fixed3-tick horizon changed; preserve future')
 status=request['receipt']['status']
 return {'version':VERSION,'protocol_sha256':ph,'life_id':identity['life_id'],'condition':row['condicion'],
  'before_tick':start,'after_tick':int(a.tick),'new_native_ticks':3,'physical_before':before,'physical_after_scheduling':scheduled,'physical_after':after,
  'requests':[request],'Native_inputs':{'unique_requested':1,'applied':int(status=='applied'),'rejected_or_other':int(status!='applied')},
  'observations_before':observed,'observations_after':{name:observe(a.world,coord)for name,coord in(('source',SITES[row['condicion']]),('old_carrier_site',CARRIER),('prospective_contact',CONTACT))},
  'external_global_capture':recording,'planned_capture_ticks':planned if recorder is not None else[],
  'scope':'External causal diagnostic only: one material zero SEM1 packet, no SEM4 support or learned action. Contact and later FI usefulness remain observed outcomes, not assigned answers. Raw/clock fields were never written by the host.'}
def operational_dependencies(a,directory):
 result=old.operational_dependencies(a,directory)
 return {**result,'counterflow_instrument_version':VERSION,'counterflow_cognitive_key_installed':False}
def uncertain(a):return old.uncertain(a)
def code_files():return list(dict.fromkeys([Path(__file__),PROTOCOL,*old.code_files()]))
