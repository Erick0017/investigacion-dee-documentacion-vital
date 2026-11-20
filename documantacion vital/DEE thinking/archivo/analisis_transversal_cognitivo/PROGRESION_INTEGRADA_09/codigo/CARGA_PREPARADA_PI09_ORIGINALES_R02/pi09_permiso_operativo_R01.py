"""Dormant exact PI09 public access permission; no actor or kernel edits.

Outer requests alone select the declared fixed public access. Internal FI
calls retain their original implementation and calendar. Importing this file
does not load DEE, create a world, change metadata or grant any permission.
"""
from pathlib import Path
import copy, hashlib, json, re

VERSION='DEE.PI09.exact_public_access_permission.R01'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01'
PREDECESSOR='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01'
SYSTEM_KEY='DEE.Cognitive.System.1.1.life.v1'
CONTRACT='PI09_CONSULTA_OPERATIVA_R01.json'
QUERY_KEY='DEE.Cognitive.PI09.selective_registered_consultation.R02'
C2C32='0cf6bf8508e071a1c8cf1448023a096bc43336d66b8a1deb98f488b29b4205fd'
PINS={
 'pi09_consulta_selectiva_R02.py':'3b81573f4dc0d9401db2210f3b23694e1f1f4a4d820d7654bcbd1e1b42b2dfbf',
 'PROTOCOLO_PI09_CONSULTA_R01.json':'cb6973e6f1bd747de8da73ecda37497579370330f828ea43d559a61c86e45ad5',
 'pi07_regulacion_R03.py':'40648fd81c5b1f278ee9c18d0d464c5a4b5e9fd808054afe6ff072a10fda0ac5',
 'pi07_acceso_FI_regulado_R01.py':'cefe1174debca3650fffeba22f1f1c2d03420211993734e319b9e47684c5db46',
 'PROTOCOLO_PI07_ACCESO_FI_R01.json':'4f15e2c892ab067c46338a7d89c0c6714b68f1436f936568e723a6bc1a7ccbc6'}
ARITHMETIC_SHA='ebff5dbe0d3b85000a33b7f789a72688e7c24c0151076558a01e32a803824656'
HISTORICAL_STATES={'eci01-pi07-estado','eci01-pi07-r02-estado','eci01-pi07-r03-estado'}
_INSTALLED=False;_PRIOR_IDENTITY=None

def _require(ok,message):
 if not ok:raise ValueError(message)

def _root():return Path(__file__).resolve().parents[1]
def _sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def _identity(a):return json.loads(dict(a.world.runtime.snapshot_metadata_entries)[SYSTEM_KEY])
def _hash(s):return isinstance(s,str)and re.fullmatch('[0-9a-f]{64}',s)is not None
def _selected():
 file=_root()/'estado/ACTIVO.json'
 return json.loads(file.read_text('utf-8-sig')).get('life_id')if file.is_file()else None

def profile(a):
 identity=_identity(a)
 if identity.get('life_id')!=LIFE:return None
 file=_root()/'contratos'/CONTRACT
 if not file.is_file():return None
 for node in(file,*file.parents):
  _require(not node.exists()or not(node.is_symlink()or getattr(node.lstat(),'st_file_attributes',0)&1024),'No se permiten enlaces en el permiso operativo PI09')
 p=json.loads(file.read_text('utf-8-sig'))
 _require(p.get('schema')=='DEE.PI09.exact_native_consultation_permission.v1'and p.get('life_id')==LIFE and p.get('profile')=='fisica_directa'and p.get('status')in('PREPARED_DIAGNOSTIC','COMMITTED'),'Se requiere el contrato PI09 exacto y separado')
 _require(identity.get('profile')=='fisica_directa'and int(a.world.runtime.dimension)==67,'Se requiere la identidad física N67 actual')
 _require(p.get('protocol_sha256')==PINS['PROTOCOLO_PI09_CONSULTA_R01.json']and p.get('allowed_modes')==['eci01-pi09-episodio','eci01-pi09-estado'],'Sólo uso/estado Native canónico; no preparación ni controles seleccionados')
 _require(p.get('all_outer_FI_requests')is True and p.get('public_FI_domain')==[0,20]and p.get('internal_C2C_FI_redirected')is False and p.get('FI_protocol_sha256')==PINS['PROTOCOLO_PI07_ACCESO_FI_R01.json'],'Se requiere el acceso FI externo fijo; las llamadas internas se conservan')
 _require(p.get('C2C_protocol_sha256')==C2C32 and p.get('C2C_allowed_modes')==['eci01-pi04-c2c-oportunidad','eci01-pi04-c2c-estado'],'Se requiere el protocolo C2C32 exacto con su stock actual')
 _require(p.get('frozen_files_sha256')==PINS,'Los pines científicos deben conservarse literalmente')
 for name,digest in PINS.items():_require(_sha(Path(__file__).with_name(name))==digest,'Cambió una fuente científica congelada: '+name)
 _require(p.get('public_arithmetic_policy')in('legacy_partial','P0_phase19_fixed'),'Se requiere una política aritmética pública explícita')
 if p['public_arithmetic_policy']=='P0_phase19_fixed':
  evidence=p.get('arithmetic_guard_actual_evidence',[])
  _require(isinstance(evidence,list)and len(evidence)>=2 and all(isinstance(r,dict)and _hash(r.get('sha256'))and r.get('path')for r in evidence)and p.get('arithmetic_guard_actual_gate_met')is True,'La guardia P0 requiere su pareja y reserva materiales reales aprobadas')
  _require(_sha(Path(__file__).with_name('pi09_aritmetica_temporal_P0_R01.py'))==ARITHMETIC_SHA,'Cambió el acceso aritmético P0 congelado')
 if _selected()==LIFE:
  _require(p['status']=='COMMITTED'and p.get('all_adoption_gates_met')is True and _hash(p.get('adoption_decision_sha256')),'El principal seleccionado requiere COMMITTED y la decisión real')
  entries=dict(a.world.runtime.snapshot_metadata_entries)
  _require(QUERY_KEY in entries,'No hay un lote PI09 adquirido en esta vida')
  m=json.loads(entries[QUERY_KEY]);c=m.get('control',{})
  _require(c.get('arm')=='native_real'and c.get('query_policy')=='native'and c.get('information_policy')=='real','Sólo la política Native con información material real puede seleccionarse')
 return p

def selected(a):return _identity(a).get('life_id')==LIFE and _selected()==LIFE

def _legacy_identity(a):
 if selected(a):
  _require(profile(a)is not None,'Falta el permiso PI09 COMMITTED')
  return _identity(a)
 return _PRIOR_IDENTITY(a)

def install():
 """Install after PI08 permission, before any dependency reads; no material."""
 global _INSTALLED,_PRIOR_IDENTITY
 if _INSTALLED:return
 from capacidades import pi07_regulacion_R03 as old
 _require(_sha(old.__file__)==PINS['pi07_regulacion_R03.py'],'Cambió el cuerpo R03 congelado')
 _PRIOR_IDENTITY=old._identity;old._identity=_legacy_identity;_INSTALLED=True
 from capacidades import pi09_carga_preparada_R01 as prepared_load
 prepared_load.install()

def validate_selected_external(a,row):
 from capacidades import pi09_carga_preparada_R01 as prepared_load
 prepared_load.guard_external(a,row)
 if not isinstance(row,dict)or not selected(a):return
 _require(profile(a)is not None,'Falta el permiso operativo PI09')
 mode=str(row.get('modo',''))
 if mode.startswith('eci01-pi07-'):
  _require(mode in HISTORICAL_STATES|{'eci01-pi07-fi-regulada','eci01-pi07-fi-acceso-estado'},'El calendario PI07 es histórico; no se reabre un lote material paralelo')
 if mode.startswith('eci01-pi08-c2c-')or mode in('eci01-pi05-c2c-ampliar','eci01-pi05-c2c-extension-estado'):
  _require(False,'El principal sólo usa el stock C2C admitido; no prepara ni repite suministros')

def routes_public(a,row):
 if not isinstance(row,dict)or not selected(a):return False
 p=profile(a);_require(p is not None,'Falta el contrato público exacto')
 return row.get('modo')=='eci01-balance'or(row.get('modo')=='eci01-aritmetica-directa'and p['public_arithmetic_policy']=='P0_phase19_fixed')

def validate_public(a,row):
 _require(routes_public(a,row),'Petición fuera de la ruta pública PI09 aprobada')
 if row['modo']=='eci01-balance':
  from capacidades import acceso_integrado_eci01 as public,pi07_acceso_FI_regulado_R01 as access
  public.validate(a,row)
  return access.validate(a,{'modo':access.QUERY,'izquierda':row['izquierda'],'derecha':row['derecha']})
 from capacidades import aritmetica_directa_eci02 as legacy
 return legacy.validate(a,row)

def execute_public(a,row,*,actuator='closed',directory=None):
 validate_public(a,row)
 if row['modo']=='eci01-balance':
  from capacidades import pi07_acceso_FI_regulado_R01 as access
  value=access.dispatch(a,{'modo':access.QUERY,'izquierda':row['izquierda'],'derecha':row['derecha']},actuator=actuator,directory=directory)
 else:
  from capacidades import pi09_aritmetica_temporal_P0_R01 as arithmetic
  value=arithmetic.execute_public(a,row,actuator=actuator)
 return {**value,'public_outer_request':dict(row),'PI09_public_access_permission':VERSION,'internal_C2C_FI_redirected':False}

def configure_C2C(component,a):
 if not selected(a):return component
 p=profile(a)
 _require(p is not None and component.protocol()[1]==C2C32,'Falta el permiso C2C32 exacto')
 _require(component.OPERATIONAL_LIFE_ID in('ECI02_PI03_REPRO_PI04_MAIN_02','ECI02_PI03_REPRO_PI04_PI05_MAIN_01',PREDECESSOR,LIFE),'Otra identidad operativa está protegida')
 component.OPERATIONAL_LIFE_ID=LIFE
 return component

def administrative_C2C_identity_proposal(metadata):
 _require(metadata.get('life_id')in(PREDECESSOR,LIFE)and not any(metadata.get(k)for k in('pending','uncertain','halted_reason')),'Sólo puede vincularse la hoja de identidad C2C cerrada')
 result=copy.deepcopy(metadata);old=result['life_id'];result['life_id']=LIFE
 _require({k:v for k,v in result.items()if k!='life_id'}=={k:v for k,v in metadata.items()if k!='life_id'},'Cambió un campo ajeno a la identidad administrativa')
 return result,{'metadata_old_life_id':old,'metadata_new_life_id':LIFE,'changed_paths':[]if old==LIFE else['/life_id'],'new_native_ticks':0,'not_learning_or_memory_transfer':True}

def code_files():
 files=[Path(__file__),Path(__file__).with_name('pi09_carga_preparada_R01.py'),*(Path(__file__).with_name(n)for n in PINS)]
 arithmetic=Path(__file__).with_name('pi09_aritmetica_temporal_P0_R01.py')
 if arithmetic.is_file():files.append(arithmetic)
 return tuple(files)
