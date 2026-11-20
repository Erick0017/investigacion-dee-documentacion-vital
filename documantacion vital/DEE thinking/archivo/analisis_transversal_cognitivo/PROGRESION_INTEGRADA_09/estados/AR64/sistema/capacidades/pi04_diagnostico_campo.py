"""NEW PI04 diagnostic, not historical reproduction or a learned repair.

Import/validation of literal arguments are stdlib only. Root alone may execute
the one material operation on complete, named C2TRACE diagnostic clones.
No efference, outcome, arithmetic, actuator or old-C2 resume is called.
"""
from pathlib import Path
from array import array
import hashlib,importlib.util,json,os

VERSION='PI04.DG.field_equality.NEW_DIAGNOSTIC.R01'
MODE='eci01-pi04-dg-campo';MODES={MODE}
KEY='DEE.Cognitive.PI04.DG.field_equality.R01'
OLD_C2_KEY='DEE.Cognitive.PI04.C2.coordination.R01'
LIFE_KEY='DEE.Cognitive.System.1.1.life.v1'
LIFE_PREFIX='ECI02_PI03_REPRO_PI04_C2TRACE_'
FOLDER='PI04_DIAGNOSTICO_CAMPO_R01'
BASE_PREFIX='PI03.TC.R01'
OLD_DATUM='PI04.C2.CURRENT.R01.datum'
MINUS_DATUM='PI04.DG.CAMPO.R01.datum.minusZ'
SOURCE_T=798033;N=67;Q=(19,54,5);DATUM=4
_MODULES={}

def _sha(b):return hashlib.sha256(b).hexdigest()
def _safe(value):return json.loads(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False))
def at(offset):return tuple((Q[k]+offset[k])%N for k in range(3))
def roi_points():return [at((x,y,z))for x in range(-3,4)for y in range(-3,5)for z in range(-4,4)]
def _module(name):
 if name not in _MODULES:
  p=Path(__file__).with_name(name+'.py');spec=importlib.util.spec_from_file_location('PI04_DG_'+name,p)
  m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);_MODULES[name]=m
 return _MODULES[name]
def _helper():return _module('pi03_credito_generico_R01_BORRADOR')
def _sensor():return _module('pi04_selector_contextual_C2_R01')
def _native():
 from dee_thinking import _native as d
 from dee_thinking.consolidated import exact_observation,exact_receipt
 from dee_thinking.persistence import decode_metadata,encode_metadata
 return d,exact_observation,exact_receipt,decode_metadata,encode_metadata
def _entries(a):return dict(a.world.runtime.snapshot_metadata_entries)
def _get(a):
 entries=_entries(a)
 if KEY not in entries:raise ValueError('No DG state')
 m=_native()[3](entries[KEY])
 if m['version']!=VERSION:raise ValueError('DG revision mismatch')
 return m
def _encoded(m):
 safe=_safe(m)
 if len(json.dumps(safe,ensure_ascii=False,separators=(',',':')).encode('utf-8'))>32768:raise ValueError('DG metadata32KB limit; frames belong only in external journal')
 return _native()[4](safe)
def _save(a,m):a.world.runtime.set_snapshot_metadata(KEY,_encoded(m))
def _obs(a,site):
 d,exact,_,_,_=_native();o=exact(a.world.runtime.observe(d.Coordinate(*site)))
 return {'site':list(site),**o,'raw':str(o['raw']),'clock':str(o['clock'])}
def _physical(a):
 rt=a.world.runtime
 return {'N':int(rt.dimension),'tick':int(rt.current_tick),'RAW_sha256':_sha(array('Q',rt.raw_copy()).tobytes()),'clocks_sha256':_sha(array('Q',rt.clock_copy()).tobytes())}
def _banks(a):return {'A':_obs(a,at((-1,-1,0))),'B':_obs(a,at((1,-1,0)))}
def _sources():
 return {name:_sha(Path(__file__).with_name(name).read_bytes())for name in('pi04_diagnostico_campo.py','pi03_credito_generico_R01_BORRADOR.py','pi04_selector_contextual_C2_R01.py')}
def validate_literal(row):
 if not isinstance(row,dict)or set(row)!={'modo','condicion','registro'}or row['modo']!=MODE:raise ValueError('Only fixed DG campo operation/condition/recording; no answer, datum, geometry or reader overrides')
 if row['condicion']not in('single','symmetric')or row['registro']not in('full','compact'):raise ValueError('Declared single/symmetric and full/compact only')
def _identity(a,directory=None):
 entries=_entries(a);d,_,_,decode,_=_native()
 if LIFE_KEY not in entries or OLD_C2_KEY not in entries:raise ValueError('Complete inherited identity and halted C2 history required')
 life=decode(entries[LIFE_KEY])['life_id']
 if not life.startswith(LIFE_PREFIX)or life==LIFE_PREFIX or int(a.world.runtime.dimension)!=N:raise ValueError('Named C2TRACE diagnostic N67 clones only; MAIN rejected')
 if directory is not None:
  home=Path(directory).resolve()
  if home.name!=life:raise ValueError('Exact owned diagnostic directory required')
  active=home.parents[1]/'ACTIVO.json'
  if active.is_file()and json.loads(active.read_text(encoding='utf-8-sig')).get('life_id')==life:raise ValueError('Selected principal rejected')
 old=decode(entries[OLD_C2_KEY])
 if old.get('pending')or old.get('uncertain'):raise ValueError('Old C2 must be coherently closed; never erase pending or uncertain work')
 if not old.get('halted_reason'):raise ValueError('This NEW diagnostic is specifically from the preserved halted C2 cut')
 if 'DEE.Cognitive.PI02.continuous_workbench.R04'in entries:
  prior=decode(entries['DEE.Cognitive.PI02.continuous_workbench.R04'])
  if prior.get('enabled')or prior.get('active_event'):raise ValueError('Inherited O/H must already be explicitly paused/closed')
 return life,_sha(entries[OLD_C2_KEY].encode('utf-8'))
def validate(a,row):
 validate_literal(row);_identity(a)
 if KEY in _entries(a):raise ValueError('One DG execution per clone; completed and failed futures preserved')
 if int(a.tick)!=SOURCE_T:raise ValueError('Only exact complete source T798033; no rephase, reset or substitute life')
 channels=set(a.world.runtime.channel_names)
 if not {OLD_DATUM,*[BASE_PREFIX+'.'+s for s in('query','support.plus','support.minus')]}<=channels:raise ValueError('Inherited query/support and +Z sensor interfaces must already exist')
 if MINUS_DATUM in channels:raise ValueError('New diagnostic interface namespace already used')
 for pos in(at((-1,0,1)),at((-1,0,-1))):
  if int(_obs(a,pos)['raw'])!=0:raise ValueError('Datum site not RAW-empty; preserve, never clear')
def _record(a,m,directory,event):
 home=Path(directory)/FOLDER;home.mkdir(parents=False,exist_ok=True)
 data=(json.dumps(_safe({'index':m['log_count'],'tick':int(a.tick),**event}),ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode('utf-8')
 following=dict(m,log_count=m['log_count']+1,log_chain_sha256=_sha(bytes.fromhex(m['log_chain_sha256'])+data))
 _encoded(following) # Validate before append: full frames never enter Native metadata.
 file=home/'eventos.jsonl';offset=file.stat().st_size if file.exists()else 0
 with file.open('ab')as f:f.write(data);f.flush();os.fsync(f.fileno())
 m.update(following);_save(a,m)
 return {'file':str(file),'index':m['log_count']-1,'byte_offset':offset,'bytes':len(data),'line_sha256':_sha(data)}
def _frame(a,mode,relative):
 frame={'relative_to_query':relative,'physical':_physical(a),'observations':[],'scope':'Global hashes in both modes; only full adds448 passive ROI observations. TickT is before events atT are applied on the next advance.'}
 if mode=='full':frame['observations']=[_obs(a,p)for p in roi_points()]
 return frame
def _declare_minus(a):
 d=_native()[0];c=d.ChannelSpec();c.name=MINUS_DATUM;c.injection_site=d.Coordinate(*at((-1,0,-1)));c.direction=d.Direction(0,0,0);c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=False
 interface=d.InterfaceSpec();interface.name=MINUS_DATUM;interface.channel=c;a.world.declare_interface(interface)
def _execute(a,row,directory):
 life,old_hash=_identity(a,directory);home=Path(directory)/FOLDER
 if home.exists():raise ValueError('Existing DG journal/directory preserved')
 before=_physical(a);banks=_banks(a)
 if int(banks['A']['s_reg'])-int(banks['B']['s_reg'])!=-4:raise ValueError('Exact diagnosed source deltaA-B=-4 required, not an arbitrary calibration')
 calendar=_helper().schedule_trial(int(a.tick),int(banks['A']['clock']),4);q=int(calendar['query_tick']);end=int(calendar['contact_tick'])+2
 if q-1<=int(a.tick)or end-int(a.tick)>1000:raise ValueError('Bounded inherited phase calendar required')
 m={'version':VERSION,'life_id':life,'condition':row['condicion'],'recording':row['registro'],'source_tick':int(a.tick),'source_physical':before,'old_C2_sha256':old_hash,'source_files':_sources(),'calendar':calendar,'pending':{'phase':'before_inputs'},'uncertain':True,'completed':False,'log_count':0,'log_chain_sha256':'00'*32}
 _save(a,m);_record(a,m,directory,{'kind':'DG_NEW_DIAGNOSTIC_INTENT','parameters':{'datum':4,'query_payload':0,'single_site':list(at((-1,0,1))),'symmetric_extra_site':list(at((-1,0,-1)))if row['condicion']=='symmetric'else None},'banks':banks,'before':before})
 if row['condicion']=='symmetric':_declare_minus(a)
 requests=[]
 for suffix in('query','support.plus','support.minus'):
  r=a.world.submit(BASE_PREFIX+'.'+suffix,0,q);requests.append({'id':int(r.id),'channel':BASE_PREFIX+'.'+suffix,'payload':0,'requested_tick':q})
 for channel in([OLD_DATUM,MINUS_DATUM]if row['condicion']=='symmetric'else[OLD_DATUM]):
  r=a.world.submit(channel,4,q+3);requests.append({'id':int(r.id),'channel':channel,'payload':4,'requested_tick':q+3})
 m['pending']={'phase':'inputs_scheduled','request_ids':[r['id']for r in requests]};_save(a,m)
 frames=[];reader=None
 for rel in range(-1,9):
  a.run_until(q+rel);frame=_frame(a,row['registro'],rel)
  if rel==6:reader=_sensor().read_fixed(a,q);frame['fixed_six_reader']=reader
  location=_record(a,m,directory,{'kind':'DG_PASSIVE_FRAME','frame':frame})
  frames.append({'relative_to_query':rel,'physical':frame['physical'],'ROI_observations':len(frame['observations']),'journal':location})
 a.run_until(end)
 exact_receipt=_native()[2]
 for r in requests:r['receipt']=exact_receipt(a.world.runtime.receipt(r['id']))
 applied=all(r['receipt']['status']=='applied'for r in requests)
 actual_old_hash=_sha(_entries(a)[OLD_C2_KEY].encode('utf-8'))
 if actual_old_hash!=old_hash:raise ValueError('Old halted C2 metadata changed; preserve diagnostic future')
 result={'version':VERSION,'kind':'NEW_DIAGNOSTIC_NOT_HISTORICAL_REPRODUCTION','life_id':life,'condition':row['condicion'],'recording':row['registro'],'source':before,'after':_physical(a),'before_tick':before['tick'],'after_tick':int(a.tick),'new_native_ticks':int(a.tick)-before['tick'],'calendar':calendar,'frames':frames,'ROI_offsets':{'x':[-3,3],'y':[-3,4],'z':[-4,3]},'reader':reader,'requests':requests,'all_inputs_applied':applied,'requested':len(requests),'applied':sum(r['receipt']['status']=='applied'for r in requests),'banks_before':banks,'banks_after':_banks(a),'old_C2_metadata_unchanged':True,'efference_count':0,'generic_return_count':0,'arithmetic_calls':0,'actuator_calls':0,'scope':'Prepared finite field diagnostic. Symmetric has an extra material input, not dose-matched control. NULL is observed data, not substituted action or a global failure.'}
 m['pending']=None if applied else {'phase':'rejected_input_preserved'};m['uncertain']=not applied;m['completed']=applied;m['last_tick']=int(a.tick)
 _record(a,m,directory,{'kind':'DG_COMPLETED','result':result})
 return result
def dispatch(a,row,*,actuator='closed',directory=None):
 validate(a,row)
 if directory is None or actuator!='closed':raise ValueError('Root-owned diagnostic directory and closed actuator wrapper only')
 try:return _execute(a,row,directory)
 except Exception as error:
  if KEY in _entries(a):
   m=_get(a);m['uncertain']=True;m['error']={'type':type(error).__name__,'message':str(error)}
   try:_save(a,m)
   except Exception:pass
  raise
def uncertain(a):return KEY in _entries(a)and bool(_get(a).get('uncertain'))
def operational_dependencies(a,directory):
 if KEY not in _entries(a):return {'version':VERSION,'present':False,'new_native_ticks':0}
 m=_get(a);chain='00'*32;count=0;file=Path(directory)/FOLDER/'eventos.jsonl'
 with file.open('rb')as f:
  for line in f:
   value=json.loads(line)
   if value['index']!=count:raise ValueError('DG journal order mismatch')
   chain=_sha(bytes.fromhex(chain)+line);count+=1
 if count!=m['log_count']or chain!=m['log_chain_sha256']:raise ValueError('DG snapshot/journal mismatch; never repair silently')
 if _sha(_entries(a)[OLD_C2_KEY].encode('utf-8'))!=m['old_C2_sha256']:raise ValueError('Preserved C2 metadata changed')
 if _sources()!=m['source_files']:raise ValueError('DG scientific source changed after execution')
 return {'version':VERSION,'present':True,'completed':m['completed'],'condition':m['condition'],'recording':m['recording'],'pending':m['pending'],'uncertain':m['uncertain'],'log_count':count,'log_chain_sha256':chain,'old_C2_metadata_unchanged':True,'new_native_ticks':0}
