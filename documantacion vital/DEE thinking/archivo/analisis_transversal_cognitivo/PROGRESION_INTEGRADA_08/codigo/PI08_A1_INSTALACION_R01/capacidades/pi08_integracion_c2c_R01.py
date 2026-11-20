"""PI08 A1: prepared/recoverable external30->32 integration, zero Native input.

The frozen C2C body, scientific protocols26/30, old device and all learned rows
remain literal. A small complete device32 is staged separately. An explicit
metadata transaction selects that device/protocol; no Native decoder or policy
is changed. A failed/unresolved transaction is never automatically repeated.
"""
from pathlib import Path
import copy,hashlib,importlib.util,json,os,shutil

VERSION='DEE.PI08.C2C.prepared_environment32.R01'
KEY='DEE.Cognitive.PI08.C2C.prepared_environment32.R01'
PREPARE='eci01-pi08-c2c-preparar';COMMIT='eci01-pi08-c2c-confirmar'
RECONCILE='eci01-pi08-c2c-reconciliar';STATE='eci01-pi08-c2c-estado'
INTERRUPT='eci01-pi08-c2c-prueba-precommit'
MODES={PREPARE,COMMIT,RECONCILE,STATE,INTERRUPT}
FOLDER='PI08_C2C_INTEGRACION_R01'
MANIFEST=Path(__file__).with_name('PROTOCOLO_PI08_C2C_INTEGRACION_R01.json')
_COMPONENTS={}

def _sha(data):return hashlib.sha256(data).hexdigest()
def _safe(value):return json.loads(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False))
def _bytes(value):return json.dumps(_safe(value),ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf8')
def _hash(value):return _sha(_bytes(value))
def _read(path):return json.loads(Path(path).read_text('utf-8-sig'))
def _entries(a):return dict(a.world.runtime.snapshot_metadata_entries)
def _encode(value):
 from dee_thinking.persistence import encode_metadata
 return encode_metadata(_safe(value))
def _decode(value):
 from dee_thinking.persistence import decode_metadata
 return decode_metadata(value)
def _put(a,value):a.world.runtime.set_snapshot_metadata(KEY,_encode(value))
def _state(a):return _decode(_entries(a)[KEY])
def _base():
 from capacidades import pi04_coordinacion_central_C2C as base
 from capacidades import pi05_c2c_ofertas_R01 as old
 return base,old,old._effective(base)
def _regular(path):
 path=Path(path)
 for node in(path,*path.parents):
  if node.exists()and(node.is_symlink()or getattr(node.lstat(),'st_file_attributes',0)&0x400):raise ValueError('No linked/reparse integration source or target')
 return path
def _atomic_new(path,value):
 path=_regular(path);data=_bytes(value)+b'\n'
 if path.exists():
  if path.read_bytes()!=data:raise ValueError('Different existing immutable transaction record')
  return
 temporary=path.with_name(path.name+'.WRITING')
 with temporary.open('xb')as out:out.write(data);out.flush();os.fsync(out.fileno())
 os.replace(temporary,path)
def _home(directory):return Path(directory)/FOLDER
def _prepared(directory):return _home(directory)/'PREPARADO.json'
def _device_home(directory):return _home(directory)/'dispositivo32'
def _copytree_manifest(root):
 root=_regular(root);files=[];dirs=[]
 for node in sorted(root.rglob('*')):
  _regular(node)
  if node.is_dir():dirs.append(node.relative_to(root).as_posix())
  elif node.is_file():
   if node.stat().st_size>262144:raise ValueError('Only the small bounded external device may be staged')
   files.append({'file':node.relative_to(root).as_posix(),'bytes':node.stat().st_size,'sha256':_sha(node.read_bytes())})
  else:raise ValueError('Only ordinary external device entries')
 if len(files)>512 or sum(v['bytes']for v in files)>2097152:raise ValueError('External device staging bound exceeded')
 return {'files':files,'directories':dirs}

def _configuration(proposal='32'):
 manifest=_read(MANIFEST)
 if manifest.get('schema')!='DEE.PI08.C2C.integration32.protocol.v1'or manifest.get('status')!='SEALED_BEFORE_WRITES':raise ValueError('Exact sealed integration manifest required')
 for name,digest in manifest['files_sha256'].items():
  if Path(name).name!=name or _sha(Path(__file__).with_name(name).read_bytes())!=digest:raise ValueError('Changed full-chain integration dependency: '+name)
 old=_read(Path(__file__).with_name(manifest['original_protocol_file']))
 if len(old['schedule'])!=30:raise ValueError('Literal effective30 prefix required')
 name=manifest['effective_protocol_file']if proposal=='32'else manifest['invalid34_control_file']
 spec=importlib.util.spec_from_file_location('PI08_A1_real_C2C_protocol_'+proposal,Path(__file__).with_name('pi04_coordinacion_central_C2C.py'))
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.PROTOCOL=Path(__file__).with_name(name)
 # Invoke the ACTUAL full consumer validator BEFORE any directory/metadata write.
 protocol,digest=module.protocol(material=True,evaluation=True)
 if proposal!='32':raise ValueError('The invalid34 control unexpectedly passed the old consumer')
 if len(protocol['schedule'])!=32 or protocol['schedule'][:30]!=old['schedule']or protocol['schedule'][30:]!=manifest['additional_public_offers']:raise ValueError('Exactly2 new offers; original30 remain literal')
 for key in old:
  if key not in('schedule','attribution')and old[key]!=protocol[key]:raise ValueError('Scientific protocol change outside explicit future offers: '+key)
 return manifest,protocol,digest

def code_files():
 manifest=_read(MANIFEST)
 return tuple(dict.fromkeys([Path(__file__),MANIFEST,*[Path(__file__).with_name(name)for name in manifest['files_sha256']]]))

def _component32(directory):
 key=str(Path(directory).resolve())
 if key not in _COMPONENTS:
  manifest,_,_=_configuration();source=Path(__file__).with_name('pi04_coordinacion_central_C2C.py');spec=importlib.util.spec_from_file_location('PI08_A1_same_C2C_body_'+_sha(key.encode())[:10],source);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  module.PROTOCOL=Path(__file__).with_name(manifest['effective_protocol_file'])
  # Explicit P0 environment-location migration only, not a Native function change.
  module._device=lambda owned_directory:module.Device(_device_home(owned_directory))
  _COMPONENTS[key]=module
 return _COMPONENTS[key]

def effective_component(a,base,for_dependencies=False,directory=None):
 from capacidades import pi05_c2c_ofertas_R01 as old
 if KEY not in _entries(a):return old.effective_component(a,base,for_dependencies=for_dependencies)
 state=_state(a);manifest,_,new_digest=_configuration();current=base._get(a)['protocol_sha256']
 if directory is None:
  identity=base._hardware()._identity(a,base._hardware().protocol()[0]);directory=Path(__file__).resolve().parents[1]/'estado/servicios_locales'/identity['life_id']
 if state.get('phase')!='COMMITTED'and not for_dependencies:raise ValueError('Preserved transaction requires explicit state/reconciliation; no automatic Native replay')
 if current==manifest['original_protocol_sha256']:return old._effective(base)
 if current==new_digest:return _component32(directory)
 raise ValueError('Unrecognized effective protocol in preserved integration future')

def _identity(a,directory=None):
 base,old,component=_base();identity=base._hardware()._identity(a,base._hardware().protocol()[0])
 life=identity['life_id']
 if not life.startswith('ECI02_PI03_REPRO_')or any(text not in life for text in('PI04_','PI05_','PI07_','PI08_'))or int(a.world.runtime.dimension)!=67:raise ValueError('Explicit inherited PI08 diagnostic N67 life required')
 if base._selected_life_id()==life:raise ValueError('No preparation/commit/reconciliation on the selected principal')
 if directory is not None and Path(directory).resolve().name!=life:raise ValueError('Exact owned existing-life directory only')
 return identity

def validate_literal(row):
 if not isinstance(row,dict)or row.get('modo')not in MODES:raise ValueError('Explicit integration instrument operation required')
 mode=row['modo']
 if mode==STATE and set(row)=={'modo'}:return
 if mode==PREPARE and(set(row)=={'modo'}or set(row)=={'modo','propuesta'}and row['propuesta']=='control34'):return
 if mode in(COMMIT,RECONCILE,INTERRUPT)and set(row)=={'modo','token'}and isinstance(row['token'],str)and len(row['token'])==64 and all(c in'0123456789abcdef'for c in row['token']):return
 raise ValueError('Only fixed proposal/token; no resource count, answer, action or path argument')
def validate(a,row):
 validate_literal(row);_identity(a)
 if row['modo']==PREPARE:_configuration('34'if row.get('propuesta')=='control34'else'32')
 elif row['modo']!=STATE:_configuration()

class _ReadOnlyRuntime:
 def __init__(self,runtime,entries):self._runtime=runtime;self._entries=entries
 @property
 def snapshot_metadata_entries(self):return tuple(self._entries.items())
 def __getattr__(self,name):
  value=getattr(self._runtime,name)
  if callable(value)and name not in('receipt','raw_copy','clock_copy'):raise ValueError('Projected preflight cannot invoke a mutating/undeclared Native method: '+name)
  return value
class _ReadOnlyWorld:
 def __init__(self,world,entries):self.runtime=_ReadOnlyRuntime(world.runtime,entries)
class _ReadOnlyAdapter:
 def __init__(self,a,entries):self.world=_ReadOnlyWorld(a.world,entries);self.tick=int(a.tick)

def _full_chain_preflight(a,directory,prepared,proposed):
 entries=_entries(a);base,old,_=_base();entries[base.KEY]=_encode(proposed)
 entries[KEY]=_encode({'version':VERSION,'phase':'COMMITTED','token':prepared['token'],'prepared_sha256':_sha(_prepared(directory).read_bytes()),'ready':True,'uncertain':False,'pending':None})
 projected=_ReadOnlyAdapter(a,entries);component=_component32(directory)
 component.protocol(material=True,evaluation=True);component._identity(projected,directory,operation=component.STATE)
 direct=component.operational_dependencies(projected,directory)
 from capacidades import pi04_dispatcher as dispatcher
 from capacidades import pi07_acceso_FI_regulado_R01 as access
 all_c2c=dispatcher.operational_dependencies(projected,directory);all_access=access.operational_dependencies(projected,directory)
 return {'scope':'Actual consumer protocol/identity/hardware/journal/device plus existing dispatcher and regulated-FI dependencies, with read-only projected administrative metadata. No Native input or advancement.','C2C':direct,'dispatcher_keys':sorted(all_c2c),'regulated_access_keys':sorted(all_access),'Native_mutators_available':False}

def _closed_before(a,directory):
 identity=_identity(a,directory);manifest,_,_= _configuration();base,old,component=_base()
 component._identity(a,directory,operation=component.STATE);component.protocol(material=True,evaluation=True);component.operational_dependencies(a,directory)
 if any(str(value.status).rsplit('.',1)[-1].lower()=='scheduled'for value in a.world.runtime.receipts):raise ValueError('A scheduled Native input remains; no pending cleanup')
 if 'DEE.Cognitive.PI07.C2C.explicit_environment34.R01'in _entries(a):raise ValueError('Never repair or import the PI07 failed34future through this extension')
 previous=_decode(_entries(a)[old.KEY]);current=component._get(a);device=component._device(directory)
 if not previous.get('ready')or previous.get('pending')or previous.get('uncertain'):raise ValueError('Original environment30 must remain actually ready')
 if current['protocol_sha256']!=manifest['original_protocol_sha256']or current['ordinal']!=30 or len(current['rows'])!=30 or current['arm']!='real'or not current.get('ready')or any(current.get(k)for k in('pending','uncertain','halted_reason')):raise ValueError('Actual closed real30 history required; never manufacture ordinal30')
 if len(device.m['resources'])!=30 or device.m['ordinal']!=30 or any(device.m.get(k)for k in('pending','feedback_pending','uncertain')):raise ValueError('Exact closed30 device/stock required')
 for folder in('reservoir','inflight_minus','inflight_plus','inflight_silence','consumed','rejected','products'):
  if not(device.home/folder).is_dir():raise ValueError('Complete fixed device directories required; preflight never repairs')
 return identity,component,current,device

def prepare(a,directory,proposal='32'):
 # Even the invalid34 control reaches its actual old validator before writes.
 manifest,protocol,new_digest=_configuration(proposal)
 if KEY in _entries(a):
  state=_state(a)
  if state.get('phase')=='COMMITTED':return {'already_committed':True,'token':state['token'],'new_native_ticks':0,'requests':[],'no_supply_repeated':True}
  raise ValueError('A preserved transaction exists; explicit state/reconcile only')
 identity,component,current,device=_closed_before(a,directory);home=_home(directory);source_tree=_copytree_manifest(device.home);source_literal=_entries(a)[component.KEY]
 seed={'version':VERSION,'life_id':identity['life_id'],'source_tick':int(a.tick),'source_physical':component._physical(a),'source_C2C_literal_sha256':_sha(source_literal.encode('utf8')),'source_device_tree':source_tree,'target_protocol_sha256':new_digest,'source_protocol_sha256':current['protocol_sha256']};token=_hash(seed)
 if _prepared(directory).is_file():
  prior=_read(_prepared(directory))
  if prior['token']!=token:raise ValueError('Another preparation preserved; no overwrite')
  _verify_prepared(directory,token,initial_device=True)
  _verified_preflight_record(directory,prior)
  return {'version':VERSION,'prepared':True,'already_prepared':True,'token':token,'new_native_ticks':0,'requests':[],'no_supply_repeated':True}
 if home.exists():raise ValueError('Incomplete administrative stage preserved; inspect it, no blind retry')
 if shutil.disk_usage(Path(directory)).free<8388608:raise ValueError('At least8MiB bounded staging/closure headroom required')
 # Scientific/resource state and selection have not been written above.
 home.mkdir();shutil.copytree(device.home,_device_home(directory));new_device=component.Device(_device_home(directory));new_resources=[]
 for index in(30,31):
  content=hashlib.sha256(('PI08.C2.additional.resource.'+str(index)).encode('ascii')).digest()*2;name='%04d.resource'%index;path=new_device.home/'reservoir'/name
  with path.open('xb')as f:f.write(content);f.flush();os.fsync(f.fileno())
  new_resources.append({'name':name,'bytes':64,'sha256':_sha(content)})
 new_device.m['resources']=new_device.m['resources']+new_resources
 new_device.m['explicit_supply_history']=new_device.m.get('explicit_supply_history',[])+[{'Native_tick':int(a.tick),'resources_before':30,'resources_after':32,'ordinal_preserved':30,'version':VERSION,'external_supply_not_learning':True}];new_device.save()
 proposed=copy.deepcopy(current);proposed['protocol_sha256']=new_digest;proposed['protocol_history']=proposed.get('protocol_history',[])+[{'effective_at_Native_tick':int(a.tick),'effective_from_ordinal':30,'previous_protocol_sha256':current['protocol_sha256'],'current_protocol_sha256':new_digest,'original30schedule_preserved':True,'external_public_supply_not_learned_content':True,'environment_location':FOLDER+'/dispositivo32'}]
 # Exercise the real encoder before any world-metadata write.
 component._checked_metadata(proposed,_encode)
 _atomic_new(home/'ANTES_C2C.json',current);_atomic_new(home/'PROPUESTA_C2C.json',proposed)
 prepared={**seed,'token':token,'new_resource_files':new_resources,'staged_device_tree':_copytree_manifest(new_device.home),'proposed_C2C_sha256':_hash(proposed),'immutable_files':{'ANTES_C2C.json':_sha((home/'ANTES_C2C.json').read_bytes()),'PROPUESTA_C2C.json':_sha((home/'PROPUESTA_C2C.json').read_bytes())},'scope':'External administrative PREPARE only; old device, C2C metadata, Native landscape/agenda and selector unchanged.'}
 _atomic_new(_prepared(directory),prepared)
 proof=_full_chain_preflight(a,directory,prepared,proposed);_atomic_new(home/'PREFLIGHT_REAL.json',{'token':token,'prepared_sha256':_sha(_prepared(directory).read_bytes()),'full_chain':proof})
 if component._physical(a)!=seed['source_physical']or _entries(a)[component.KEY]!=source_literal or _copytree_manifest(device.home)!=source_tree:raise RuntimeError('Source changed during preparation; preserve stage, do not commit')
 return {'version':VERSION,'prepared':True,'token':token,'new_native_ticks':0,'requests':[],'new_external_resources_staged':2,'old_resources':30,'target_resources':32,'original_device_unchanged':True,'C2C_metadata_unchanged':True,'full_consumer_preflight':proof}

def _verify_prepared(directory,token,initial_device=False):
 prepared=_read(_prepared(directory))
 if prepared['token']!=token:raise ValueError('Wrong transaction token; no mutation')
 home=_home(directory)
 for name,digest in prepared['immutable_files'].items():
  if Path(name).name!=name or _sha((home/name).read_bytes())!=digest:raise ValueError('Altered prepared metadata artifact')
 if initial_device and _copytree_manifest(_device_home(directory))!=prepared['staged_device_tree']:raise ValueError('Staged device changed before commit')
 return prepared,_read(home/'PROPUESTA_C2C.json')

def _verified_preflight_record(directory,prepared):
 proof=_read(_home(directory)/'PREFLIGHT_REAL.json')
 if proof.get('token')!=prepared['token']or proof.get('prepared_sha256')!=_sha(_prepared(directory).read_bytes()):raise ValueError('Actual prepared full-consumer preflight did not finish; do not commit/retry a partial preparation')
 return proof

def commit(a,directory,token,*,reconcile=False,interrupt_before=False):
 _identity(a,directory);manifest,_,new_digest=_configuration();prepared,proposed=_verify_prepared(directory,token,initial_device=KEY not in _entries(a));_verified_preflight_record(directory,prepared);base,old,component=_base();current=base._get(a)
 if KEY in _entries(a):
  state=_state(a)
  if state.get('token')!=token:raise ValueError('Another transaction identity exists')
  if state.get('phase')=='COMMITTED':
   effective_component(a,base,for_dependencies=True,directory=directory).operational_dependencies(a,directory)
   return {'already_committed':True,'token':token,'new_native_ticks':0,'requests':[],'no_resources_or_experiences_repeated':True}
  if not reconcile:raise ValueError('Explicit reconciliation required for the preserved interrupted commit')
 else:
  _closed_before(a,directory)
 if _copytree_manifest(component._device(directory).home)!=prepared['source_device_tree']:raise ValueError('Original30device changed after prepare')
 before=component._physical(a)
 if before!=prepared['source_physical']:raise ValueError('Native world advanced after prepare; do not retime the transaction')
 if current['protocol_sha256']==manifest['original_protocol_sha256']:
  if _sha(_entries(a)[base.KEY].encode('utf8'))!=prepared['source_C2C_literal_sha256']:raise ValueError('Source C2C history changed after prepare')
 elif current['protocol_sha256']==new_digest:
  if not reconcile or _hash(current)!=prepared['proposed_C2C_sha256']:raise ValueError('A different new32future exists; never reset it')
 else:raise ValueError('Unknown transaction state; preserve it')
 # Revalidate the actual full prospective consumer chain immediately before commit.
 _full_chain_preflight(a,directory,prepared,proposed)
 if interrupt_before:raise RuntimeError('PI08_DECLARED_PRECOMMIT_INTERRUPTION: preparation preserved; no life/device/Native write occurred')
 intent={'version':VERSION,'phase':'COMMITTING','token':token,'prepared_sha256':_sha(_prepared(directory).read_bytes()),'ready':False,'uncertain':True,'pending':{'phase':'explicit_metadata_commit'},'original_protocol_sha256':manifest['original_protocol_sha256'],'effective_protocol_sha256':new_digest,'source_tick':int(a.tick),'external_supply_not_acquisition':True}
 _encode(intent);_encode(proposed)
 _put(a,intent)
 # Both states have a complete device and a valid protocol. Dependency lookup
 # selects30or32 by actual protocol SHA during an explicitly uncertain commit.
 a.world.runtime.set_snapshot_metadata(base.KEY,_encode(proposed))
 # The immutable external completion record precedes the final ready flag.
 # If it cannot be written, the actual new32future remains COMMITTING and
 # checkpointable, requiring explicit reconciliation rather than a false ready.
 final={**intent,'phase':'COMMITTED','ready':True,'uncertain':False,'pending':None}
 _atomic_new(_home(directory)/'COMMIT_CONFIRMADO.json',{'token':token,'Native_tick':int(a.tick),'prepared_sha256':final['prepared_sha256'],'resources_before':30,'resources_after':32,'ordinal_preserved':30,'new_native_ticks':0})
 _put(a,final)
 dependencies=_component32(directory).operational_dependencies(a,directory)
 if component._physical(a)!=before:raise RuntimeError('Unexpected Native change during administrative commit')
 return {'version':VERSION,'committed':True,'token':token,'new_native_ticks':0,'requests':[],'resources_before':30,'resources_after':32,'ordinal_preserved':30,'old_device_preserved':True,'new_device_relative':FOLDER+'/dispositivo32','Native_physical_before':before,'Native_physical_after':component._physical(a),'dependencies':dependencies,'not_learning':True}

def operational_dependencies(a,directory):
 if KEY not in _entries(a):return {'version':VERSION,'present':False,'new_native_ticks':0}
 state=_state(a);prepared,proposed=_verify_prepared(directory,state['token'])
 if state['prepared_sha256']!=_sha(_prepared(directory).read_bytes()):raise ValueError('Changed prepared transaction identity')
 base,old,component=_base()
 if _copytree_manifest(component._device(directory).home)!=prepared['source_device_tree']:raise ValueError('Inactive original30device/history changed')
 return {'version':VERSION,'present':True,'phase':state['phase'],'ready':state['ready'],'pending':state['pending'],'uncertain':state['uncertain'],'token':state['token'],'prepared_sha256':state['prepared_sha256'],'effective_protocol_sha256':prepared['target_protocol_sha256'],'old30device_preserved':True,'new_native_ticks':0,'scope':'External environment migration/provenance, not an acquired Native capability.'}
def uncertain(a):return KEY in _entries(a)and _state(a).get('phase')!='COMMITTED'
def dispatch(a,row,*,actuator='closed',directory=None):
 validate(a,row)
 if row['modo']==STATE:return {'version':VERSION,'present':KEY in _entries(a),'state':_state(a)if KEY in _entries(a)else None,'new_native_ticks':0,'requests':[]}
 if directory is None or actuator!='closed':raise ValueError('Exact existing owned directory/closed bridge required')
 if row['modo']==PREPARE:return prepare(a,directory,'34'if row.get('propuesta')=='control34'else'32')
 return commit(a,directory,row['token'],reconcile=row['modo']==RECONCILE,interrupt_before=row['modo']==INTERRUPT)
