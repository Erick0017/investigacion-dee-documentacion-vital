"""Exact PI10 public permission, no engine/world import on load.

Scientific actor stays literal. Selected use is EP/STATE only; inherited
balance uses the actual remaining FI8 in its private identity namespace, never
its admission/reset or the internal PI10/C2C FI. Exact closed REAL diagnostics
may exercise the same inherited public access before an adoption decision.
"""
from pathlib import Path
import copy,hashlib,json
VERSION='DEE.PI10.exact_public_permission.R02';SCHEMA='DEE.PI10.exact_operational_permission.v2'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01';PARENT='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'
SYSTEM='DEE.Cognitive.System.1.1.life.v1';KEY='DEE.Cognitive.PI10.adaptive_query.two_native_traces.R02';C2CKEY='DEE.Cognitive.PI04.C2C.coordination.R01';CONTRACT='PI10_USO_OPERATIVO_R01.json'
EP='eci01-pi10-episodio';STATE='eci01-pi10-estado';FI8_QUERY='eci01-pi09-fi-lote-consultar';C2C_PROTOCOL='0cf6bf8508e071a1c8cf1448023a096bc43336d66b8a1deb98f488b29b4205fd';P0_SHA='214062c2d706e1354e5bb22fa5c66b72f32c0e61a249913b71a5f4fa7d4cf7da';_INSTALLED=False
def need(ok,msg):
 if not ok:raise ValueError(msg)
def root():return Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def entries(a):return dict(a.world.runtime.snapshot_metadata_entries)
def identity(a):return json.loads(entries(a)[SYSTEM])
def selected_id():
 f=root()/'estado/ACTIVO.json';return read(f).get('life_id')if f.is_file()else None
def applies(a):return identity(a).get('life_id')==LIFE
def acquired(a):
 oldkey='DEE.Cognitive.PI10.adaptive_query.two_native_traces.R01';oldliteral=entries(a)[oldkey];old=json.loads(oldliteral)
 need(old.get('ready')and not old.get('admitted')and old['ordinal']==0 and not old['rows']and not old.get('pending')and not old.get('uncertain'),'R01 neutral preparation remains literal, never four acquired adverse episodes')
 m=json.loads(entries(a)[KEY]);need(m.get('preparation_life_id')=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_P02_01'and m.get('source_R01_P0_metadata_sha256')==hashlib.sha256(oldliteral.encode('utf8')).hexdigest(),'Actual R02 neutral-P02 genealogy and R01-P0 history required');need(m.get('ready')and m.get('admitted')and m['ordinal']==len(m['rows'])and 12<=m['ordinal']<=18 and not m.get('pending')and not m.get('uncertain')and m.get('admission_control')=={'role':'evaluation','arm':'real','trace_control':'none','force_query':None},'Actual closed unforced Real12+ acquired history, no reset or control');return m
def profile(a):
 if not applies(a):return None
 f=root()/'contratos'/CONTRACT
 if not f.is_file():return None
 p=read(f);need(p.get('schema')==SCHEMA and p.get('life_id')==LIFE and p.get('profile')=='fisica_directa'and p.get('N')==67 and p.get('status')in('PREPARED_DIAGNOSTIC','COMMITTED')and p.get('all_adoption_gates_met')is True,'Exact validated PI10 operational contract')
 need(p.get('source_P02_manifest_sha256')==__import__('capacidades.pi10_transporte_ancestral_R01',fromlist=['config']).config()['source_main_manifest_sha256'] and p.get('protocol_sha256')==sha(Path(__file__).with_name('PROTOCOLO_PI10_R02.json'))and p.get('allowed_modes')==[EP,STATE],'Exact source and EP/STATE domain')
 need(p.get('public_FI_backend')=='inherited_FI8_same_frozen_body'and p.get('public_FI_domain')==[0,20]and p.get('internal_FI_redirected')is False and p.get('historical_material_disabled')is True and p.get('C2C_protocol_sha256')==C2C_PROTOCOL and p.get('public_arithmetic_policy')=='legacy_partial','No new supply, internal FI reroute or broadened arithmetic domain')
 for name,digest in p['frozen_files_sha256'].items():need(Path(name).name==name and sha(Path(__file__).with_name(name))==digest,'Frozen PI10 source changed: '+name)
 acquired(a)
 if selected_id()==LIFE:need(p['status']=='COMMITTED'and isinstance(p.get('adoption_decision_sha256'),str)and len(p['adoption_decision_sha256'])==64,'Actual committed adoption decision required')
 else:need(selected_id()==PARENT and p['status']=='PREPARED_DIAGNOSTIC','Only exact precommit load while protected D remains selected')
 return p
def diagnostic_real(a):
 if not applies(a)or(root()/'estado/ACTIVO.json').exists():return False
 m=json.loads(entries(a).get(KEY,'null'))
 if m is None or m.get('ordinal',0)<12:return False
 from capacidades import pi10_transporte_ancestral_R01 as transport
 transport.identity(a);need(transport.config()['role']=='real','Only original REAL diagnostic can exercise public retention, never controls/replay');acquired(a);return True
def public_allowed(a):return (selected_id()==LIFE and profile(a)is not None)or diagnostic_real(a)
def routes_public(a,row):return applies(a)and isinstance(row,dict)and row.get('modo')=='eci01-balance'and public_allowed(a)
def validate_public(a,row):
 need(routes_public(a,row),'Outside exact PI10 public/diagnostic retention domain')
 from capacidades import acceso_integrado_eci01 as public,pi09_FI8_D_alias_R01 as access
 public.validate(a,row);return access.private().validate(a,{'modo':FI8_QUERY,'izquierda':row['izquierda'],'derecha':row['derecha']})
def execute_public(a,row,*,actuator='closed',directory=None):
 validate_public(a,row)
 from capacidades import pi09_FI8_D_alias_R01 as access
 old=entries(a).get('DEE.Cognitive.PI07.regulated_FI_access.R01');value=access.private().dispatch(a,{'modo':FI8_QUERY,'izquierda':row['izquierda'],'derecha':row['derecha']},actuator=actuator,directory=directory);need(entries(a).get('DEE.Cognitive.PI07.regulated_FI_access.R01')==old,'Old FI quota changed; never double-consume')
 return {**value,'public_outer_request':dict(row),'PI10_public_permission':VERSION,'internal_FI_redirected':False,'new_FI_supply_added':0,'diagnostic_assistance':selected_id()!=LIFE}
def validate_external(a,row,*,payload):
 if not applies(a):return
 current=selected_id()
 if current==PARENT:
  need(profile(a)is not None,'Exact prepared moved PI10 contract')
  if payload.get('operacion')in('reanudar','pausar','guardar','detener'):need(row is None and set(payload)=={'operacion'},'Exact administrative control only');return
  from capacidades import pi10_transporte_ancestral_R01 as transport
  need(isinstance(row,dict)and row=={'modo':row.get('modo')}and row['modo']in transport.STATES|{STATE}and payload.get('operacion')=='sesion'and payload.get('retorno','real')=='omit'and payload.get('actuador','closed')=='closed','Prepared load permits only STATE/control, no material before commit');return
 if current!=LIFE:return
 need(profile(a)is not None,'Selected PI10 requires committed profile')
 if not isinstance(row,dict):return
 mode=str(row.get('modo',''))
 if mode.startswith('eci01-pi10-'):need(mode in(EP,STATE),'Selected PI10 cannot PREPARE/ADMIT/CALIBRATE/force/reset')
 if mode.startswith(('eci01-pi07-','eci01-pi08-','eci01-pi09-')):
  from capacidades import pi10_transporte_ancestral_R01 as transport
  need(mode in transport.STATES,'Historical material calendars remain closed')
 if mode in('eci01-pi05-c2c-ampliar','eci01-pi05-c2c-extension-estado'):need(False,'No C2C resupply/reset as selected learning')
def configure_C2C(component,a):
 if not applies(a):return component
 if selected_id()in(PARENT,LIFE):need(profile(a)is not None,'PI10 C2C configuration requires actual prepared/committed profile')
 elif not diagnostic_real(a):return component
 need(component.protocol()[1]==C2C_PROTOCOL,'Literal existing C2C32 protocol only');component.OPERATIONAL_LIFE_ID=LIFE;return component
def propose_C2C_identity(metadata):
 need(metadata.get('life_id')in(PARENT,LIFE)and not any(metadata.get(k)for k in('pending','uncertain','halted_reason'))and metadata.get('protocol_sha256')==C2C_PROTOCOL and metadata.get('arm')=='real'and metadata.get('ready')and metadata.get('admitted')and metadata['ordinal']==len(metadata['rows'])<=32,'Only the closed real current C2C history, no counter/protocol reset');new=copy.deepcopy(metadata);old=new['life_id'];new['life_id']=LIFE
 return new,{'metadata_old_life_id':old,'metadata_new_life_id':LIFE,'changed_paths':[]if old==LIFE else['/life_id'],'new_ticks':0,'not_learning':True}
def install(a):
 global _INSTALLED
 if _INSTALLED or not applies(a):return
 from capacidades import pi09_permiso_operativo_D_R01 as old,pi04_dispatcher as dispatcher
 # PI04 uses its own importlib namespace. Bind that actual consumer as well
 # as the ordinary module; no scientific function body or Native field edits.
 for module in(old,dispatcher._load('pi09_permiso_operativo_D_R01')):
  previous=module.configure_C2C
  module.configure_C2C=lambda component,a,_old=previous:configure_C2C(component,a)if applies(a)else _old(component,a)
 _INSTALLED=True
def code_files():
 files=[Path(__file__)];f=root()/'contratos'/CONTRACT
 if f.exists():files.append(f)
 return tuple(files)
