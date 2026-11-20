"""Exact-life PI08 access/identity permission layer; no Native policy changes.

Original R03/FI/C2C files remain literal. Prepared diagnostic outer FI always
uses its declared alternative; selected use requires a real COMMITTED contract.
Internal arithmetic/C2C FI calls are never redirected by this layer.
"""
from pathlib import Path
import copy,hashlib,json,re
VERSION='DEE.PI08.exact_access_and_identity_permission.R01'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01'
SOURCE_C2C_LIFE='ECI02_PI03_REPRO_PI04_PI05_MAIN_01'
SYSTEM_KEY='DEE.Cognitive.System.1.1.life.v1'
CONTRACT='PI08_USO_OPERATIVO_R01.json'
R03_SHA='40648fd81c5b1f278ee9c18d0d464c5a4b5e9fd808054afe6ff072a10fda0ac5'
R03_PROTOCOL='f69e8558799558a1ccceb70e0684a061a971b9521ad8985205d1662aea55d269'
FI_SHA='cefe1174debca3650fffeba22f1f1c2d03420211993734e319b9e47684c5db46'
FI_PROTOCOL='4f15e2c892ab067c46338a7d89c0c6714b68f1436f936568e723a6bc1a7ccbc6'
_INSTALLED=False;_ORIGINAL_R03_IDENTITY=None;_ORIGINAL_FI_ROUTE=None
def _sha(data):return hashlib.sha256(data).hexdigest()
def _root():return Path(__file__).resolve().parents[1]
def _identity(a):return json.loads(dict(a.world.runtime.snapshot_metadata_entries)[SYSTEM_KEY])
def _selected():
 path=_root()/'estado/ACTIVO.json'
 return json.loads(path.read_text('utf-8-sig')).get('life_id')if path.is_file()else None
def profile(a):
 identity=_identity(a)
 if identity.get('life_id')!=LIFE:return None
 path=_root()/'contratos'/CONTRACT
 if not path.is_file():return None
 for node in(path,*path.parents):
  if node.exists()and(node.is_symlink()or getattr(node.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked exact PI08 profile')
 value=json.loads(path.read_text('utf-8-sig'))
 if value.get('schema')!='DEE.PI08.exact_operational_profile.v1'or value.get('life_id')!=LIFE or value.get('profile')!='fisica_directa'or value.get('status')not in('PREPARED_DIAGNOSTIC','COMMITTED'):raise ValueError('Exact explicit PI08 profile required')
 if value.get('R03_protocol_sha256')!=R03_PROTOCOL or value.get('FI_protocol_sha256')!=FI_PROTOCOL or value.get('all_outer_FI_requests')is not True or value.get('public_FI_domain')!=[0,20]or value.get('internal_C2C_FI_redirected')is not False:raise ValueError('Fixed all-outer alternative FI contract; internal calls unchanged')
 if identity.get('profile')!='fisica_directa'or int(a.world.runtime.dimension)!=67:raise ValueError('Actual inherited N67/direct physical identity required')
 if _selected()==LIFE:
  if value['status']!='COMMITTED'or not re.fullmatch('[0-9a-f]{64}',str(value.get('adoption_decision_sha256',''))):raise ValueError('Selected use requires real COMMITTED exact adoption SHA')
 return value
def _regulated_identity(a):
 current=_identity(a)
 if current.get('life_id')==LIFE and _selected()==LIFE:
  contract=profile(a)
  if contract is None:raise ValueError('No exact PI08 selected-use contract')
  return current
 return _ORIGINAL_R03_IDENTITY(a)
def _outer_FI_route(a,row):
 contract=profile(a)
 if contract is not None:
  return row.get('modo')=='eci01-balance'
 return _ORIGINAL_FI_ROUTE(a,row)
def install():
 global _INSTALLED,_ORIGINAL_R03_IDENTITY,_ORIGINAL_FI_ROUTE
 if _INSTALLED:return
 from capacidades import pi07_regulacion_R03 as regulation
 from capacidades import pi07_acceso_FI_regulado_R01 as access
 if _sha(Path(regulation.__file__).read_bytes())!=R03_SHA or _sha(Path(access.__file__).read_bytes())!=FI_SHA:raise ValueError('Frozen scientific R03/FI body differs')
 _ORIGINAL_R03_IDENTITY=regulation._identity;_ORIGINAL_FI_ROUTE=access.routes_selected_legacy
 regulation._identity=_regulated_identity;access.routes_selected_legacy=_outer_FI_route
 _INSTALLED=True
def configure_C2C(component,a):
 contract=profile(a)
 if contract is None or _selected()!=LIFE:return component
 if contract.get('C2C_allowed_modes')!=[component.OPPORTUNITY,component.STATE]or contract.get('C2C_protocol_sha256')!=component.protocol()[1]:raise ValueError('Exact adopted effective C2C protocol/use modes required')
 if component.OPERATIONAL_LIFE_ID not in('ECI02_PI03_REPRO_PI04_MAIN_02',SOURCE_C2C_LIFE,LIFE):raise ValueError('Another identity permission is protected')
 component.OPERATIONAL_LIFE_ID=LIFE
 return component
def administrative_C2C_identity_proposal(metadata):
 if metadata.get('life_id')not in(SOURCE_C2C_LIFE,LIFE)or any(metadata.get(k)for k in('pending','uncertain','halted_reason')):raise ValueError('Only the inherited coherent C2C identity leaf may migrate')
 updated=copy.deepcopy(metadata);old=updated['life_id'];updated['life_id']=LIFE
 if {k:v for k,v in updated.items()if k!='life_id'}!={k:v for k,v in metadata.items()if k!='life_id'}:raise RuntimeError('Unexpected C2C history edit')
 return updated,{'schema':'DEE.PI08.C2C.administrative_identity_mapping.v1','metadata_old_life_id':old,'metadata_new_life_id':LIFE,'changed_paths':[]if old==LIFE else['/life_id'],'new_native_ticks':0,'no_memory_transfer_or_acquisition':True}
