"""Explicit PI07 environment30→34, not a Native answer or acquired memory.
No DEE import/execution at import. Original30protocol/body preserved. A private
instance of that exact body reads the declared effective34protocol after an
explicit metadata/resource transaction. No RAW/clocks/interface changes.
"""
from pathlib import Path
import copy,hashlib,importlib.util,json,os
VERSION='DEE.PI07.C2C.explicit_environment34.R01'
KEY='DEE.Cognitive.PI07.C2C.explicit_environment34.R01'
PREVIOUS_KEY='DEE.Cognitive.PI05.C2C.explicit_environment30.R01'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_CAND_01'
EXTEND='eci01-pi07-c2c-ampliar';STATE='eci01-pi07-c2c-extension-estado';MODES={EXTEND,STATE}
MANIFEST=Path(__file__).with_name('PROTOCOLO_PI07_C2C_EXTENSION_R01.json')
_EFFECTIVE=None

def _sha(b):return hashlib.sha256(b).hexdigest()
def _safe(v):return json.loads(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False))
def _hash(v):return _sha(json.dumps(_safe(v),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def _entries(a):return dict(a.world.runtime.snapshot_metadata_entries)
def _state(a):return json.loads(_entries(a)[KEY])
def _put(a,m):
 from dee_thinking.persistence import encode_metadata
 a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(_safe(m)))
def _base():
 from capacidades import pi04_coordinacion_central_C2C as base
 from capacidades import pi05_c2c_ofertas_R01 as previous
 return previous._effective(base)

def code_files():
 from capacidades import pi05_c2c_ofertas_R01 as previous
 return tuple(dict.fromkeys([Path(__file__),MANIFEST,Path(__file__).with_name('PROTOCOLO_PI07_C2C_34_R01.json'),*previous.code_files()]))

def _protocol():
 b=MANIFEST.read_bytes();p=json.loads(b)
 if p['schema']!='DEE.PI07.C2C.explicit_environment34.protocol.v1'or p['status']!='SEALED_BEFORE_NEW_RESERVES':raise ValueError('Exact explicit environment extension must be sealed')
 for n,h in p['files_sha256'].items():
  if Path(n).name!=n or _sha(Path(__file__).with_name(n).read_bytes())!=h:raise ValueError('Changed extension dependency: '+n)
 old=json.loads(Path(__file__).with_name(p['original_protocol_file']).read_bytes());new=json.loads(Path(__file__).with_name(p['effective_protocol_file']).read_bytes())
 if len(old['schedule'])!=30 or len(new['schedule'])!=34 or new['schedule'][:30]!=old['schedule']or new['schedule'][30:]!=p['additional_public_offers']:raise ValueError('Original30schedule must stay literal; exactly4newpublicoffers only')
 for k in old:
  if k not in('schedule','attribution')and old[k]!=new[k]:raise ValueError('Only future schedule/attribution may change: '+k)
 return p,_sha(b)

def _effective(base=None):
 global _EFFECTIVE
 base=_base()if base is None else base;p,_=_protocol()
 if _EFFECTIVE is None:
  source=Path(base.__file__);spec=importlib.util.spec_from_file_location('PI07_C2C34_same_scientific_body',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  # Configuration only. Every function body was loaded from the exact old file.
  m.PROTOCOL=Path(__file__).with_name(p['effective_protocol_file']);_EFFECTIVE=m
 return _EFFECTIVE

def effective_component(a,base,for_dependencies=False):
 if KEY not in _entries(a):
  from capacidades import pi05_c2c_ofertas_R01 as previous
  return previous.effective_component(a,base,for_dependencies=for_dependencies)
 m=_state(a);p,_=_protocol();current=base._get(a)['protocol_sha256']
 if m.get('uncertain')or m.get('pending'):
  if not for_dependencies:raise ValueError('Uncertain explicit supply future preserved; no automatic repeat')
  if current==p['original_protocol_sha256']:
   from capacidades import pi05_c2c_ofertas_R01 as previous
   return previous._effective(base)
  if current==p['effective_protocol_sha256']:return _effective(base)
  raise ValueError('Unknown current protocol in preserved extension transaction')
 if not m.get('ready')or current!=p['effective_protocol_sha256']:raise ValueError('Incomplete explicit extension/current protocol mismatch')
 return _effective(base)

def _home(directory):return Path(directory)/'PI07_C2C_OFERTAS_R01'
def _event(a,m,directory,event):
 home=_home(directory);line=(json.dumps(_safe(event),ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()
 with(home/'eventos.jsonl').open('ab')as f:f.write(line);f.flush();os.fsync(f.fileno())
 m['log_count']+=1;m['log_chain_sha256']=_sha(bytes.fromhex(m['log_chain_sha256'])+line);_put(a,m)
def _verify_journal(m,directory):
 path=_home(directory)/'eventos.jsonl';count=0;chain='00'*32
 with path.open('rb')as f:
  for line in f:json.loads(line);count+=1;chain=_sha(bytes.fromhex(chain)+line)
 if count!=m['log_count']or chain!=m['log_chain_sha256']:raise ValueError('Explicit supply journal/snapshot mismatch')
 return {'path':str(path),'bytes':path.stat().st_size,'sha256':_sha(path.read_bytes()),'count':count}
def _no_links(path):
 for p in(Path(path),*Path(path).parents):
  if p.is_symlink()or(p.exists()and getattr(p.lstat(),'st_file_attributes',0)&0x400):raise ValueError('No linked/reparse extension target')

def validate_literal(row):
 if not isinstance(row,dict)or set(row)!={'modo'}or row['modo']not in MODES:raise ValueError('Only fixed extension/state; no answer,route,quantity or path argument')
 return row

def validate(a,row):
 validate_literal(row);base=_base();p,_=_protocol();identity=base._hardware()._identity(a,base._hardware().protocol()[0])
 if identity['life_id']!=LIFE or int(a.world.runtime.dimension)!=67 or base._selected_life_id()==LIFE:raise ValueError('PI05 inherited diagnostic N67 only; never original/main')
 if row['modo']==EXTEND:
  if KEY in _entries(a):raise ValueError('Existing34extension preserved; never reset/readmit/refill automatically')
  if PREVIOUS_KEY not in _entries(a):raise ValueError('Actual inherited26to30history required')
  previous=json.loads(_entries(a)[PREVIOUS_KEY])
  if not previous.get('ready')or previous.get('pending')or previous.get('uncertain'):raise ValueError('Original30environment must remain coherently closed')
  m=base._get(a)
  if m['arm']!='real'or m['ordinal']!=30 or len(m['rows'])!=30 or not m['ready']or any(m.get(k)for k in('pending','uncertain','halted_reason')):raise ValueError('Exact closed real30history before fresh reserves required')
  if m['protocol_sha256']!=p['original_protocol_sha256']:raise ValueError('Original30protocol current-cut proof required')
 return True

def prepare(a,directory):
 validate(a,{'modo':EXTEND});base=_base();p,ph=_protocol();identity=base._identity(a,directory,operation=base.STATE)[2]
 if Path(directory).name!=identity['life_id']:raise ValueError('Exact owned directory only')
 if any(str(r.status).rsplit('.',1)[-1].lower()=='scheduled'for r in a.world.runtime.receipts):raise ValueError('Native scheduled inputs remain; first admit/settle guard through original legal advance')
 base.operational_dependencies(a,directory);device=base._device(directory);old=copy.deepcopy(device.m);m=base._get(a);oldm=copy.deepcopy(m)
 if len(old['resources'])!=30 or old['ordinal']!=30 or any(old.get(k)for k in('pending','feedback_pending','uncertain')):raise ValueError('Exact30resources/closed30device required')
 if device.home.joinpath('ESTADO_DISPOSITIVO.json.pending').exists():raise ValueError('Uncertain device write remains')
 if _home(directory).exists():raise ValueError('Explicit supply directory exists; no retry or overwrite')
 _no_links(device.home);new=[]
 for i in range(30,34):
  content=hashlib.sha256(('PI07.C2.additional.resource.'+str(i)).encode('ascii')).digest()*2;name='%04d.resource'%i
  for folder in('reservoir','inflight_minus','inflight_plus','inflight_silence','consumed','rejected'):
   if(device.home/folder/name).exists():raise ValueError('Existing added resource name; no duplicate supply')
  new.append((name,content,{'name':name,'bytes':64,'sha256':_sha(content)}))
 previous_literal=_entries(a)[PREVIOUS_KEY];before=base._physical(a);root=_home(directory);root.mkdir();ext={'version':VERSION,'ready':False,'pending':{'phase':'explicit_supply_preparation'},'uncertain':True,'initial_ordinal':30,'original_resources':30,'effective_resources':34,'original_protocol_sha256':p['original_protocol_sha256'],'effective_protocol_sha256':p['effective_protocol_sha256'],'manifest_sha256':ph,'old_rows_sha256':_hash(m['rows']),'old_products_sha256':_hash(old['products']),'old_resources_sha256':_hash(old['resources']),'new_resource_files':[r for _,_,r in new],'log_count':0,'log_chain_sha256':'00'*32,'supply_is_external_not_acquisition':True}
 _put(a,ext)
 try:
  _event(a,ext,directory,{'kind':'EXPLICIT_ENVIRONMENT_EXTENSION_INTENT','before':before,'from':30,'to':34,'ordinal_unchanged':30,'new_public_offers':p['additional_public_offers']})
  for name,content,_ in new:
   with(device.home/'reservoir'/name).open('xb')as f:f.write(content);f.flush();os.fsync(f.fileno())
  device.m['resources']=old['resources']+[r for _,_,r in new]
  device.m['explicit_supply_history']=old.get('explicit_supply_history',[])+[{'Native_tick':int(a.tick),'resources_before':30,'resources_after':34,'ordinal_preserved':30,'public_extension_manifest_sha256':ph}]
  device.save()
  m['protocol_history']=m.get('protocol_history',[])+[{'effective_at_Native_tick':int(a.tick),'effective_from_ordinal':30,'previous_protocol_sha256':p['original_protocol_sha256'],'current_protocol_sha256':p['effective_protocol_sha256'],'original30schedule_preserved':True,'external_public_supply_not_learned_content':True}]
  m['protocol_sha256']=p['effective_protocol_sha256'];base._save(a,m)
  base._record(a,m,directory,{'kind':'PI07_EXPLICIT_ENVIRONMENT30_TO34','Native_tick':int(a.tick),'old_protocol_sha256':p['original_protocol_sha256'],'current_protocol_sha256':p['effective_protocol_sha256'],'ordinal_preserved':30,'new_resource_files':[r for _,_,r in new]})
  if _entries(a)[PREVIOUS_KEY]!=previous_literal or m['rows']!=oldm['rows']or device.m['products']!=old['products']or device.m['rejections']!=old['rejections']or device.m['ordinal']!=30 or base._physical(a)!=before:raise RuntimeError('Supply changed prior history,progress or Native physical state')
  ext.update(ready=True,pending=None,uncertain=False,current_ordinal_at_extension=30)
  _event(a,ext,directory,{'kind':'EXPLICIT_ENVIRONMENT_EXTENSION_COMMITTED','physical':base._physical(a),'new_resources':4,'Native_ticks':0,'old_rows_unchanged':True,'old_products_unchanged':True,'old30resource_references_unchanged':True})
  _effective(base).operational_dependencies(a,directory)
 except Exception as exc:
  ext.update(ready=False,uncertain=True,pending={'phase':'failed_extension_preserved'},error=type(exc).__name__+': '+str(exc))
  _put(a,ext)
  try:_event(a,ext,directory,{'kind':'EXPLICIT_EXTENSION_FAILURE_PRESERVED','error':ext['error']})
  except Exception:pass
  raise
 return {'version':VERSION,'ready':True,'new_native_ticks':0,'requests':[],'old_environment30_metadata_literal_unchanged':_entries(a)[PREVIOUS_KEY]==previous_literal,'resources_before':30,'resources_after':34,'ordinal_before':30,'ordinal_after':30,'Native_physical_before':before,'Native_physical_after':base._physical(a),'new_resources':[r for _,_,r in new],'old_protocol_file_unchanged':True,'original_rows_products_rejections_preserved':True,'future_role':'30/31declared material uses;32/33remainavailable;newexternaloffersnotlearning'}

def operational_dependencies(a,directory):
 if KEY not in _entries(a):return {'version':VERSION,'present':False,'new_native_ticks':0}
 m=_state(a);journal=_verify_journal(m,directory)
 return {'version':VERSION,'present':True,'ready':m['ready'],'pending':m['pending'],'uncertain':m['uncertain'],'original_protocol_sha256':m['original_protocol_sha256'],'effective_protocol_sha256':m['effective_protocol_sha256'],'journal':journal,'new_native_ticks':0,'scope':'Explicit external supplies/current protocol provenance, never participant answer memory'}
def uncertain(a):return KEY in _entries(a)and bool(_state(a).get('uncertain'))
def dispatch(a,row,*,actuator='closed',directory=None):
 validate(a,row)
 if row['modo']==STATE:return {'version':VERSION,'present':KEY in _entries(a),'state':_state(a)if KEY in _entries(a)else None,'new_native_ticks':0}
 if actuator!='closed'or directory is None:raise ValueError('Exact owned existing worker directory/closed action bridge required')
 return prepare(a,directory)
