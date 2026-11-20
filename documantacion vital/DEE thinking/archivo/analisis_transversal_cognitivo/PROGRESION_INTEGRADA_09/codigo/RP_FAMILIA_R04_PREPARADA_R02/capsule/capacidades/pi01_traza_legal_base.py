"""PI01 R01: legal-interface returning trace; no direct RAW/clock edits.

Development-only calibration. Origin and reader are fixed before execution.
The historical CORE09 scaffold/deletion is intentionally absent.
"""
import json
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata
from dee_thinking.consolidated import exact_receipt,exact_observation
from app.native_tools import physical

VERSION='PI01.legal_returning_access.R03'
KEY='DEE.Cognitive.System.1.1.PROGRESION_INTEGRADA_01.R01'
N=67;D=(41,43,47)
A=(1,0,0);B=(0,1,0);SENSOR=(-1,0,1);NORMALIZER=(1,0,-1)
ACTION={0:(0,0,1),1:(-1,1,1)}
PENALTY={0:(-1,1,0),1:(1,-1,0)}

def add(p,v,k=1):return tuple((p[i]+k*v[i])%N for i in range(3))
def obs(a,p):return exact_observation(a.world.runtime.observe(d.Coordinate(*p)))
def get(a):
 e=dict(a.world.runtime.snapshot_metadata_entries)
 if KEY not in e:raise ValueError('PI01 component not prepared; no implicit anatomy')
 return decode_metadata(e[KEY])
def save(a,m):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m))
def rr(a,r):return exact_receipt(a.world.runtime.receipt(int(r.id)))
def declare(a,name,site,direction,state):
 c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*site);c.direction=d.Direction(*direction);c.state=state;c.semantic=1;c.allow_experience=True;c.allow_probe=False
 i=d.InterfaceSpec();i.name=name;i.channel=c;a.world.declare_interface(i)
def roi(a,radius=3):
 D=tuple(get(a)['origin'])
 return [obs(a,add(D,(x,y,z)))for x in range(-radius,radius+1)for y in range(-radius,radius+1)for z in range(-radius,radius+1)]
def submit_arrival(a,channel,load,arrival):
 if int(arrival)-1<=a.tick:raise ValueError('Prepared arrival would be in past; no calendar repair')
 return a.world.submit(channel,int(load),int(arrival)-1)
def state(a):
 return {'version':VERSION,'physical':physical(a.world),'component':get(a),'center':obs(a,tuple(get(a)['origin'])),'scope':'Investigator view; not a memory/target available to selector.'}

def prepare(a,origin=D):
 D=tuple(origin)
 if int(a.world.runtime.dimension)!=N:raise ValueError('N67 only')
 if KEY in dict(a.world.runtime.snapshot_metadata_entries):raise ValueError('Already prepared; do not reinstall a lived component')
 names=[('seed',D,A,1001),('sensor',add(D,SENSOR,-1),SENSOR,200001),('normalizer',add(D,NORMALIZER,-1),NORMALIZER,400001),('penalty0',add(D,PENALTY[0],-1),PENALTY[0],600001),('penalty1',add(D,PENALTY[1],-1),PENALTY[1],600002)]
 pre=[obs(a,site)for _,site,_,_ in names]
 if any(int(x['raw'])!=0 for x in pre):raise ValueError('Nonzero RAW at prepared interface, no overwrite or cleanup')
 rays=[]
 for v in [A,B,ACTION[0],ACTION[1],NORMALIZER]:
  for k in range(N):
   o=obs(a,add(D,v,k))
   if int(o['raw'])!=0:rays.append(o)
 if rays:raise ValueError('Prepared return path intersects existing causal RAW; no cleanup')
 prefix='PI01.R03.'
 for name,p,v,st in names:declare(a,prefix+name,p,v,st)
 at=int(a.tick)+2;r=a.world.submit(prefix+'seed',7,at)
 a.run_until(at+1)
 receipt=rr(a,r)
 m={'version':VERSION,'origin':list(D),'seed_requested_tick':at,'seed_effective_tick':receipt.get('effective_tick'),'seed_receipt':receipt,'prepared_at':int(a.tick),'prefix':prefix,'episodes':0,'calibration':[],'in_progress':None,'uncertain':False,'external_design':'Initial A direction and generic ports are prepared, not learned knowledge. CORE09 scaffold/deletion absent; local clocks never edited.'}
 save(a,m)
 if receipt['status']!='applied':raise ValueError('Initial policy seed rejected; preserve reached future')
 return {'pre_interfaces':pre,'admission':receipt,'center_after_admission':obs(a,D),'state':state(a),'new_preparation_T0':False,'direct_raw_writes':0,'direct_clock_writes':0}

def complete_preparation(a):
 m=get(a);identifier=int(m['seed_receipt']['id']);before=physical(a.world);old=exact_receipt(a.world.runtime.receipt(identifier))
 if old['status']!='scheduled':raise ValueError('Only the recorded still-scheduled seed may be completed, never resubmit')
 a.run_until(max(int(a.tick),int(m['seed_requested_tick']))+1)
 new=exact_receipt(a.world.runtime.receipt(identifier));m['seed_receipt']=new;m['seed_effective_tick']=new.get('effective_tick');m['preparation_completed_boundary']=int(a.tick);m['instrument_correction']='R01 checked before input boundary was processed; no seed rejection or reexecution occurred.';save(a,m)
 if new['status']!='applied':raise ValueError('Seed has a terminal non-applied status; preserve future')
 return {'before':before,'after':physical(a.world),'previous_receipt':old,'current_receipt':new,'origin':obs(a,D),'next':obs(a,add(D,A)),'same_material_receipt_no_resubmit':True,'state':state(a)}

def calibrate(a,count):
 m=get(a);D=tuple(m['origin'])
 if m['uncertain']or m['in_progress']:raise ValueError('Inspect preserved incomplete future')
 if m['calibration']:raise ValueError('Calibration may run only once per component; use another declared branch/version')
 seed=int(m['seed_effective_tick']);rows=[]
 # Observe one original circuit without adding a sensor. No target label.
 first=seed+N
 if a.tick>=first-2:raise ValueError('Calibration window passed')
 a.run_until(first-2);base=[]
 for t in range(first-2,first+3):a.run_until(t);base.append({'tick':int(a.tick),'center':obs(a,D),'roi':roi(a,3)})
 for e in range(count):
  decision=seed+(3+2*e)*N;feedback=decision+N
  m['in_progress']={'kind':'calibration','episode':e,'decision':decision,'feedback':feedback};save(a,m)
  sensor=submit_arrival(a,m['prefix']+'sensor',17+2*e,decision)
  frames=[]
  for t in range(decision-2,decision+3):
   a.run_until(t);frames.append({'tick':int(a.tick),'center':obs(a,D),'roi':roi(a,3)})
  decision_observation=next(x['center']for x in frames if x['tick']==decision)
  direction=tuple(decision_observation['direction']);route=next((k for k,v in ACTION.items()if direction==v),None) if decision_observation['state']>0 and decision_observation['semantic']==1 else None
  negative=None
  if e==1 and route is not None:negative=submit_arrival(a,m['prefix']+'penalty'+str(route),5,feedback)
  normal=submit_arrival(a,m['prefix']+'normalizer',3,feedback)
  for t in range(feedback-2,feedback+3):
   a.run_until(t);frames.append({'tick':int(a.tick),'center':obs(a,D),'roi':roi(a,3)})
  rows.append({'episode':e,'decision':decision,'feedback':feedback,'sensor_receipt':rr(a,sensor),'normalizer_receipt':rr(a,normal),'calibration_negative_receipt':None if negative is None else rr(a,negative),'fixed_read_route':route,'decision_observation':decision_observation,'frames':frames})
 passive_before=physical(a.world);entries_before=dict(a.world.runtime.snapshot_metadata_entries);tick_before=int(a.tick);roi(a,3)
 passive_unchanged=physical(a.world)==passive_before and dict(a.world.runtime.snapshot_metadata_entries)==entries_before and int(a.tick)==tick_before
 if not passive_unchanged:raise RuntimeError('Observer changed physical state or metadata')
 m['calibration']={'completed':True,'episodes':count,'last_tick':int(a.tick)};m['in_progress']=None;save(a,m)
 return {'version':VERSION,'scope':'Development calibration, no useful-action/learning score. Fixed one-circuit clock interpretation; no direct clock or RAW modification.','passive_observer_unchanged':passive_unchanged,'rows':[{'kind':'baseline_return','frames':base}]+rows,'state':state(a)}

def validate_literal(row):
 if not isinstance(row,dict):raise ValueError('PI01 exact literal required')
 mode=row.get('modo')
 if mode in('eci01-pi01-preparar','eci01-pi01-estado','eci01-pi01-completar-preparacion'):
  if set(row)!={'modo'}:raise ValueError('No target or extra metadata accepted')
 elif mode=='eci01-pi01-calibrar':
  if set(row)!={'modo','circuitos'}or type(row['circuitos'])is not int or not 1<=row['circuitos']<=3:raise ValueError('One to three calibration circuits')
 else:raise ValueError('Unknown PI01 R01 literal')
def validate(a,row):
 validate_literal(row)
 if row['modo']!='eci01-pi01-preparar':get(a)
def dispatch(a,row,*,actuator='closed',directory=None):
 validate(a,row)
 if row['modo']=='eci01-pi01-preparar':return prepare(a)
 if row['modo']=='eci01-pi01-estado':return state(a)
 if row['modo']=='eci01-pi01-completar-preparacion':return complete_preparation(a)
 return calibrate(a,row['circuitos'])
