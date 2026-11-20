"""Exact PI10 continuation identity; all acquired ancestor metadata read-only.

Administrative Python namespaces only. No Native input/state/clock/metadata
write, hidden policy, answer or reinitialization occurs in this module.
"""
from pathlib import Path
import copy,hashlib,importlib.util,json,re

VERSION='DEE.PI10.exact_inherited_readonly_transport.R01'
SYSTEM='DEE.Cognitive.System.1.1.life.v1'
SCOPE=Path(__file__).with_name('PI10_TRANSPORTE_ANCESTRAL_R01.json')
PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_'
OLD_D='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'
PARENT_SOURCE=Path(__file__).with_name('pi09_transporte_heredado_R02.py')
PARENT_SHA='e7ba613480fc24db22a72a4bf2a09439277a9ad3988ee94b1ea5f4ae6d71c712'
D_SOURCE=Path(__file__).with_name('pi09_entorno_persistente_D_R02.py')
D_SHA='c9938b50fbdf68d94954eaf341abae025faa307e4c8d24d23862c7b78bf085f8'
_BASE=None;_D=None;_INSTALLED=False
STATES={'eci01-pi09-d-estado','eci01-pi09-estado','eci01-pi09-fi-lote-estado','eci01-pi04-c2c-estado','eci01-pi07-fi-acceso-estado','eci01-pi07-estado','eci01-pi07-r02-estado','eci01-pi07-r03-estado','eci01-pi08-b-estado','eci01-pi08-c-estado'}

def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def root():return Path(__file__).resolve().parents[1]
def raw_identity(a):return json.loads(dict(a.world.runtime.snapshot_metadata_entries)[SYSTEM])
def config():
 c=read(SCOPE)
 need(c.get('schema')=='DEE.PI10.exact_inherited_transport_scope.R01'and re.fullmatch(re.escape(PREFIX)+r'[A-Z0-9_]{1,25}',str(c.get('life_id','')))and c.get('profile')=='fisica_directa'and c.get('N')==67,'Exact PI10 scope required')
 need(c.get('source_main_life_id')==OLD_D and c.get('source_main_tick',0)>=922371 and isinstance(c.get('source_main_snapshot_sha256'),str)and len(c['source_main_snapshot_sha256'])==64,'Actual current D parent is mandatory')
 need(c.get('source_C_tick')==884835 and c.get('source_C_snapshot_sha256')=='ef52add3d7a6a5b9e310efb815bf8ae7dd47cb968104e7b1fa5c8a2b9f726d22','Literal C ancestry required, not a reconstruction')
 for name,digest in c['literal_sources_sha256'].items():need(Path(name).name==name and sha(Path(__file__).with_name(name))==digest,'Changed inherited scientific code '+name)
 return c
def applies(a):
 return SCOPE.is_file()and raw_identity(a).get('life_id')==read(SCOPE).get('life_id')
def identity(a):
 c=config();i=raw_identity(a);need(i.get('life_id')==c['life_id']and i.get('profile')=='fisica_directa'and int(a.world.runtime.dimension)==67,'Only the exact PI10 N67 descendant')
 entries=dict(a.world.runtime.snapshot_metadata_entries)
 for key,digest in c['inherited_metadata_sha256'].items():need(key in entries and hashlib.sha256(entries[key].encode('utf8')).hexdigest()==digest,'Acquired ancestor metadata changed: '+key)
 active=root()/'estado/ACTIVO.json'
 if active.exists():
  p=read(root()/'contratos/PI10_USO_OPERATIVO_R01.json');selected=read(active).get('life_id')
  need(c.get('role')=='real'and p.get('life_id')==i['life_id']and p.get('profile')=='fisica_directa'and p.get('all_adoption_gates_met')is True,'A control or unvalidated continuation cannot load operationally')
  need((selected==i['life_id']and p.get('status')=='COMMITTED'and isinstance(p.get('adoption_decision_sha256'),str))or(selected==OLD_D and p.get('status')=='PREPARED_DIAGNOSTIC'),'Exact PREPARED or COMMITTED lifecycle required')
 return i
def base():
 global _BASE
 if _BASE is None:
  need(sha(PARENT_SOURCE)==PARENT_SHA,'Literal PI09 inherited transport changed')
  s=importlib.util.spec_from_file_location('capacidades._PI10_ancestral_C_B_readonly',PARENT_SOURCE);b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
  b.SCOPE=SCOPE;b.config=config;b.current=identity;_BASE=b
 return _BASE
def component_B(a,original):identity(a);return base().component_B(a,original)
def component_C(a,original):identity(a);return base().component_C(a,original)
def private_D(a=None):
 global _D
 if a is not None:identity(a)
 if _D is None:
  need(sha(D_SOURCE)==D_SHA,'Literal D actor changed')
  s=importlib.util.spec_from_file_location('capacidades._PI10_D_acquired_readonly',D_SOURCE);d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
  def current(a):
   i=identity(a);d._bridge()._C().LIFE=i['life_id'];return i
  d._identity=current;_D=d
 return _D
def install(a):
 global _INSTALLED
 if not applies(a)or _INSTALLED:return
 identity(a)
 from capacidades import pi07_regulacion_R03 as r03,pi09_transporte_D_R02 as t,pi09_transporte_heredado_R02 as old
 prior=r03._identity;r03._identity=lambda a:identity(a)if applies(a)else prior(a)
 for name,ours in(('component_B',component_B),('component_C',component_C)):
  for module in(t,old):
   prior_fn=getattr(module,name)
   def call(a,original,_old=prior_fn,_new=ours):return _new(a,original)if applies(a)else _old(a,original)
   setattr(module,name,call)
 prior_applies=t.applies;prior_current=t.current
 t.applies=lambda a:applies(a)or prior_applies(a)
 t.current=lambda a:identity(a)if applies(a)else prior_current(a)
 # The old dispatcher is contextually STATE/deps-only for PI10. The actor
 # never reopens old D/R02 calendars or consumes their remaining stock.
 from capacidades import pi09_dispatcher_D_R02 as dispatcher
 old_validate=dispatcher.validate;old_dispatch=dispatcher.dispatch;old_deps=dispatcher.operational_dependencies;old_uncertain=dispatcher.uncertain
 def validate(a,row):
  if not applies(a):return old_validate(a,row)
  need(row.get('modo')in STATES,'PI09 ancestors are STATE-only in PI10')
  if row['modo']=='eci01-pi09-d-estado':return private_D(a).validate(a,row)
  identity(a);return old_validate(a,row)
 def dispatch(a,row,*,actuator='closed',directory=None):
  if not applies(a):return old_dispatch(a,row,actuator=actuator,directory=directory)
  validate(a,row)
  if row['modo']=='eci01-pi09-d-estado':return private_D(a).state(a)
  return old_dispatch(a,row,actuator=actuator,directory=directory)
 def deps(a,directory):
  if not applies(a):return old_deps(a,directory)
  identity(a)
  from capacidades import pi09_antecedente_R02_readonly_D_R01 as r02,pi09_FI8_D_alias_R01 as fi8
  return {'D_ancestral_readonly':private_D(a).operational_dependencies(a,directory),'R02_ancestral_readonly':r02.operational_dependencies(a,directory),'FI8_ancestral_readonly':fi8.operational_dependencies(a,directory),'new_ticks':0}
 dispatcher.validate=validate;dispatcher.dispatch=dispatch;dispatcher.operational_dependencies=deps
 dispatcher.uncertain=lambda a:private_D(a).uncertain(a)if applies(a)else old_uncertain(a)
 _INSTALLED=True
def validate_external(a,row,*,payload):
 if not applies(a):return
 identity(a);active=root()/'estado/ACTIVO.json'
 if active.exists()and read(active).get('life_id')!=raw_identity(a)['life_id']:
  if payload.get('operacion')in('reanudar','pausar','guardar','detener'):need(set(payload)=={'operacion'},'Exact transport control only');return
  allowed=STATES|{'eci01-pi10-estado'}
  need(payload.get('operacion')=='sesion'and payload.get('retorno','real')=='omit'and payload.get('actuador','closed')=='closed'and row=={'modo':row.get('modo')}and row.get('modo')in allowed,'Only STATE/control in a moved unselected PREPARED world');return
 if isinstance(row,dict):
  mode=row.get('modo','')
  if mode.startswith(('eci01-pi07-','eci01-pi08-','eci01-pi09-')):need(mode in STATES,'No ancestral reset/supply/material calendar in PI10')
def code_files():return tuple([Path(__file__),SCOPE,PARENT_SOURCE,D_SOURCE])
