"""Conditional exact Discovery operational permission, no Native on import.

Only external public FI is routed to the already declared FI8 alias. Internal
C2C/C/D FI calls, Native selectors and feedback stay literal. Both historical
R02 and old R03 material calendars remain read-only after selection. PREPARED
load permits transport controls and fixed STATE only; no material trial.
"""
from pathlib import Path
import copy,hashlib,json,re
VERSION='DEE.PI09.D.exact_public_permission.R01'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01';PREDECESSOR='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01';ANCESTRAL_C2C='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01'
SYSTEM='DEE.Cognitive.System.1.1.life.v1';KEY='DEE.Cognitive.PI09.persistent_environment.D.R02';OLDKEY='DEE.Cognitive.PI09.selective_registered_consultation.R02';CONTRACT='PI09_D_USO_OPERATIVO_R02.json'
D_EP='eci01-pi09-d-episodio';D_STATE='eci01-pi09-d-estado';FI8_QUERY='eci01-pi09-fi-lote-consultar';FI8_STATE='eci01-pi09-fi-lote-estado'
C2C_PROTOCOL='0cf6bf8508e071a1c8cf1448023a096bc43336d66b8a1deb98f488b29b4205fd'
PINS={'pi09_entorno_persistente_D_R02.py':'c9938b50fbdf68d94954eaf341abae025faa307e4c8d24d23862c7b78bf085f8','PROTOCOLO_PI09_D_R02.json':'7d99060711544aebaf8882b8246cd0e09ac36ca77374d32e7dd29080188ea897','pi09_consulta_selectiva_R02.py':'3b81573f4dc0d9401db2210f3b23694e1f1f4a4d820d7654bcbd1e1b42b2dfbf','PROTOCOLO_PI09_CONSULTA_R01.json':'cb6973e6f1bd747de8da73ecda37497579370330f828ea43d559a61c86e45ad5','pi07_regulacion_R03.py':'40648fd81c5b1f278ee9c18d0d464c5a4b5e9fd808054afe6ff072a10fda0ac5','pi07_acceso_FI_regulado_R01.py':'cefe1174debca3650fffeba22f1f1c2d03420211993734e319b9e47684c5db46','pi09_lote_FI8_R01.py':'ecbf6cf65bdfce0359ed840bd803e5775e494bc10d8b50716bfd4124cfd12d96'}
STATES={D_STATE,'eci01-pi09-estado',FI8_STATE,'eci01-pi04-c2c-estado','eci01-pi07-fi-acceso-estado','eci01-pi07-estado','eci01-pi07-r02-estado','eci01-pi07-r03-estado'}
_INSTALLED=False;_PRIOR_R03=None
def need(ok,msg):
 if not ok:raise ValueError(msg)
def root():return Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def identity(a):return json.loads(dict(a.world.runtime.snapshot_metadata_entries)[SYSTEM])
def selected_id():
 file=root()/'estado/ACTIVO.json';return read(file).get('life_id')if file.is_file()else None
def hash64(v):return isinstance(v,str)and re.fullmatch('[0-9a-f]{64}',v)is not None
def acquired(a):
 entries=dict(a.world.runtime.snapshot_metadata_entries);need(KEY in entries and OLDKEY in entries,'Se requieren D adquirido y su antecedente R02 literal')
 m=json.loads(entries[KEY]);old=json.loads(entries[OLDKEY]);control=m.get('control',{})
 need(m.get('version')=='DEE.PI09.persistent_environment.D.R02'and type(m.get('ordinal'))is int and 6<=m['ordinal']<=12 and len(m.get('rows',[]))==m['ordinal']and m.get('ready')and not m.get('pending')and not m.get('uncertain')and m.get('sample_register')is None,'Se requiere progreso D real cerrado; no reset ni stock inventado')
 need(control.get('arm')=='real'and control.get('query_policy')=='native'and control.get('information_policy')=='real','Ningún control, referencia o política de Python puede ser principal')
 need(old.get('ordinal')==12 and len(old.get('rows',[]))==12 and old.get('ready')and not old.get('pending')and not old.get('uncertain'),'El R02 adquirido es antecedente histórico; no se reabre su calendario')
 return m,old
def profile(a):
 i=identity(a)
 if i.get('life_id')!=LIFE:return None
 file=root()/'contratos'/CONTRACT
 if not file.is_file():return None
 for node in(file,*file.parents):need(not node.exists()or not(node.is_symlink()or getattr(node.lstat(),'st_file_attributes',0)&1024),'No se permiten enlaces en el perfil D exacto')
 p=read(file);need(p.get('schema')=='DEE.PI09.D.exact_operational_permission.v2'and p.get('life_id')==LIFE and p.get('profile')=='fisica_directa'and p.get('status')in('PREPARED_DIAGNOSTIC','COMMITTED'),'Perfil D exacto y separado requerido')
 need(i.get('profile')=='fisica_directa'and int(a.world.runtime.dimension)==67,'Sólo la identidad física N67 actual')
 need(p.get('protocol_sha256')==PINS['PROTOCOLO_PI09_D_R02.json']and p.get('allowed_modes')==[D_EP,D_STATE]and p.get('frozen_files_sha256')==PINS,'El cuerpo D, lectores y protocolos deben permanecer literales')
 for name,digest in PINS.items():need(sha(Path(__file__).with_name(name))==digest,'Cambió una fuente científica D: '+name)
 need(p.get('all_outer_FI_requests')is True and p.get('public_FI_domain')==[0,20]and p.get('public_FI_backend')=='explicit_FI8_same_frozen_body'and p.get('internal_C2C_FI_redirected')is False,'Sólo acceso FI externo fijo por FI8, sin redirigir FI interno')
 need(p.get('C2C_protocol_sha256')==C2C_PROTOCOL and p.get('historical_R02_material_disabled')is True and p.get('historical_PI07_material_disabled')is True and p.get('public_arithmetic_policy')=='legacy_partial','No se duplican calendarios ni se habilita una guardia P0 sin ganancia')
 if selected_id()==LIFE:need(p['status']=='COMMITTED'and p.get('all_adoption_gates_met')is True and hash64(p.get('adoption_decision_sha256')),'El seleccionado D exige COMMITTED y SHA de decisión real');acquired(a)
 return p
def validate_prepared_load(a,i=None):
 i=identity(a)if i is None else i;p=profile(a)
 need(i.get('life_id')==LIFE and selected_id()==PREDECESSOR and p is not None and p['status']=='PREPARED_DIAGNOSTIC'and p.get('all_adoption_gates_met')is True and p.get('adoption_decision_sha256')is None,'Sólo Discovery trasladada PREPARED mientras NATIVE sigue seleccionada')
 acquired(a);return p
def selected(a):return identity(a).get('life_id')==LIFE and selected_id()==LIFE
def _legacy_identity(a):
 if identity(a).get('life_id')==LIFE and selected_id()in(LIFE,PREDECESSOR):
  if selected_id()==LIFE:need(profile(a)is not None,'Falta el perfil D COMMITTED')
  else:validate_prepared_load(a)
  return identity(a)
 return _PRIOR_R03(a)
def install():
 global _INSTALLED,_PRIOR_R03
 if _INSTALLED:return
 from capacidades import pi07_regulacion_R03 as old
 need(sha(old.__file__)==PINS['pi07_regulacion_R03.py'],'Cambió el cuerpo R03 literal')
 # The product keeps Native's original global R02 scope. Discovery's private
 # ancestor uses its separately preserved scope; no scientific source changes.
 from capacidades import pi09_transporte_D_R02 as transport
 transport.base().SCOPE=Path(transport.__file__).with_name('PI09_TRANSPORTE_D_ANCESTRO_R02.json')
 _PRIOR_R03=old._identity;old._identity=_legacy_identity;_INSTALLED=True
def validate_external(a,row,*,payload):
 if identity(a).get('life_id')!=LIFE:return
 current=selected_id()
 if current==PREDECESSOR:
  validate_prepared_load(a)
  if isinstance(payload,dict)and payload.get('operacion')in('reanudar','pausar','guardar','detener'):need(set(payload)=={'operacion'}and row is None,'Control D administrativo exacto');return
  need(isinstance(payload,dict)and payload.get('operacion')=='sesion'and set(payload)<={'operacion','situaciones','actuador','retorno'}and payload.get('actuador','closed')=='closed'and payload.get('retorno','real')=='omit'and isinstance(row,dict)and set(row)=={'modo'}and row.get('modo')in STATES and payload.get('situaciones')==[row],'Antes de COMMITTED sólo controles y una STATE, sin avance ni material');return
 if current!=LIFE:return
 need(profile(a)is not None,'Falta permiso D COMMITTED')
 if not isinstance(row,dict):return
 mode=str(row.get('modo',''))
 if mode.startswith('eci01-pi09-'):need(mode in STATES|{D_EP,FI8_QUERY},'Sólo D actual/FI8; R02, controles y suministros son históricos o externos')
 if mode.startswith('eci01-pi07-'):need(mode in STATES,'No se reabre el calendario FI viejo ni R03')
 if mode.startswith('eci01-pi08-c2c-')or mode in('eci01-pi05-c2c-ampliar','eci01-pi05-c2c-extension-estado'):need(False,'Sólo stock C2C admitido; no resuministro ni reset implícito')
def routes_public(a,row):return isinstance(row,dict)and selected(a)and row.get('modo')=='eci01-balance'
def validate_public(a,row):
 need(routes_public(a,row)and profile(a)is not None,'Petición fuera del perfil público D exacto')
 from capacidades import acceso_integrado_eci01 as public,pi09_FI8_D_alias_R01 as access
 public.validate(a,row);return access.validate(a,{'modo':FI8_QUERY,'izquierda':row['izquierda'],'derecha':row['derecha']})
def execute_public(a,row,*,actuator='closed',directory=None):
 validate_public(a,row)
 from capacidades import pi09_FI8_D_alias_R01 as access
 value=access.dispatch(a,{'modo':FI8_QUERY,'izquierda':row['izquierda'],'derecha':row['derecha']},actuator=actuator,directory=directory)
 return {**value,'public_outer_request':dict(row),'PI09_D_public_permission':VERSION,'internal_C2C_FI_redirected':False}
def configure_C2C(component,a):
 if not selected(a):return component
 p=profile(a);need(p is not None and component.protocol()[1]==C2C_PROTOCOL,'Se requiere C2C32 literal con stock actual');need(component.OPERATIONAL_LIFE_ID in(ANCESTRAL_C2C,PREDECESSOR,LIFE,'ECI02_PI03_REPRO_PI04_MAIN_02','ECI02_PI03_REPRO_PI04_PI05_MAIN_01'),'Otra identidad C2C está protegida');component.OPERATIONAL_LIFE_ID=LIFE;return component
def propose_C2C_identity(metadata):
 need(metadata.get('life_id')in(ANCESTRAL_C2C,PREDECESSOR,LIFE)and not any(metadata.get(k)for k in('pending','uncertain','halted_reason')),'Sólo la hoja de identidad C2C cerrada');m=copy.deepcopy(metadata);old=m['life_id'];m['life_id']=LIFE
 return m,{'metadata_old_life_id':old,'metadata_new_life_id':LIFE,'changed_paths':[]if old==LIFE else['/life_id'],'new_ticks':0,'not_learning':True}
def code_files():return tuple([Path(__file__),Path(__file__).with_name('PI09_TRANSPORTE_D_ANCESTRO_R02.json'),*(Path(__file__).with_name(n)for n in PINS)])
