"""Dormant exact B permission; no Native policy and no scientific-source edits.

Only a real COMMITTED adoption contract can enable selected B. The original
research module stays literal/research-only. A private Python namespace of that
same source changes only its identity permission; all Native functions remain.
Not installed or authorized by preparing this file.
"""
from pathlib import Path
import copy, hashlib, importlib.util, json, re

VERSION='DEE.PI08.B.exact_operational_permission.R01'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_REAL_01'
PREDECESSOR='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01'
SYSTEM_KEY='DEE.Cognitive.System.1.1.life.v1'
CONTRACT='PI08_B_USO_OPERATIVO_R01.json'
PINS={
 'pi08_revision_flexible_B_R01.py':'aebe20a4566046957b274b07b942a3843ab4b612a9214791ff38edeb6bc53480',
 'pi08_revision_flexible_B_episodio_R01.py':'a110b1de0953d86b1488f62a623f9623fad686885bd30d446c5f5a3deb44ab6f',
 'PROTOCOLO_PI08_B_R01.json':'8c7b1fc983b7279e9ec78cd0136d5bc8d80d072340668783446f8ec19dd34640',
 'SELLO_PI08_B_R01.json':'98a54759d0d4bae2e53a6f432962b08e92f2b3836ee98b98b3b44dad7ae8779e',
 'pi07_regulacion_R03.py':'40648fd81c5b1f278ee9c18d0d464c5a4b5e9fd808054afe6ff072a10fda0ac5',
 'pi07_acceso_FI_regulado_R01.py':'cefe1174debca3650fffeba22f1f1c2d03420211993734e319b9e47684c5db46'}
C2C32='0cf6bf8508e071a1c8cf1448023a096bc43336d66b8a1deb98f488b29b4205fd'
_PRIVATE=None;_INSTALLED=False;_PRIOR_IDENTITY=None;_PRIOR_FI_ROUTE=None

def _require(ok,text):
 if not ok:raise ValueError(text)
def _sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def _root():return Path(__file__).resolve().parents[1]
def _identity(a):return json.loads(dict(a.world.runtime.snapshot_metadata_entries)[SYSTEM_KEY])
def _selected():
 path=_root()/'estado/ACTIVO.json'
 return json.loads(path.read_text('utf-8-sig')).get('life_id')if path.is_file()else None
def _hash(value):return isinstance(value,str)and re.fullmatch('[0-9a-f]{64}',value)is not None

def profile(a):
 identity=_identity(a)
 if identity.get('life_id')!=LIFE:return None
 path=_root()/'contratos'/CONTRACT
 if not path.is_file():return None
 for node in(path,*path.parents):
  _require(not node.exists()or not(node.is_symlink()or getattr(node.lstat(),'st_file_attributes',0)&1024),'No linked operational permission')
 p=json.loads(path.read_text('utf-8-sig'))
 _require(p.get('schema')=='DEE.PI08.B.exact_operational_profile.v1'and p.get('life_id')==LIFE and p.get('status')in('PREPARED_DIAGNOSTIC','COMMITTED'),'Exact separately approved B profile required')
 _require(identity.get('profile')=='fisica_directa'and int(a.world.runtime.dimension)==67,'Actual inherited N67 direct-world identity required')
 _require(p.get('all_outer_FI_requests')is True and p.get('public_FI_domain')==[0,20]and p.get('internal_C2C_FI_redirected')is False,'All outer fixed FI requests, never operand-conditioned routing')
 _require(p.get('B_allowed_modes')==['eci01-pi08-b-episodio','eci01-pi08-b-estado']and p.get('C2C_allowed_modes')==['eci01-pi04-c2c-oportunidad','eci01-pi04-c2c-estado'],'Only admitted use/state, never selected preparation or controls')
 _require(p.get('frozen_files_sha256')==PINS and p.get('C2C_protocol_sha256')==C2C32,'Frozen B/R03/FI/C2C sources/protocols required')
 for name,digest in PINS.items():_require(_sha(Path(__file__).with_name(name))==digest,'Frozen source differs: '+name)
 if _selected()==LIFE:
  _require(p['status']=='COMMITTED'and p.get('all_adoption_gates_met')is True and _hash(p.get('adoption_decision_sha256')),'Selected B requires actual committed approval/evidence')
 return p

def _legacy_identity(a):
 identity=_identity(a)
 if identity.get('life_id')==LIFE and _selected()==LIFE:
  _require(profile(a)is not None,'Exact committed selected B permission missing')
  return identity
 return _PRIOR_IDENTITY(a)

def _outer_FI_route(a,row):
 if profile(a)is not None:return row.get('modo')=='eci01-balance'
 return _PRIOR_FI_ROUTE(a,row)

def install_legacy_access():
 """Called after predecessor A permission installation, before dependencies."""
 global _INSTALLED,_PRIOR_IDENTITY,_PRIOR_FI_ROUTE
 if _INSTALLED:return
 from capacidades import pi07_regulacion_R03 as old
 from capacidades import pi07_acceso_FI_regulado_R01 as access
 _require(_sha(Path(old.__file__))==PINS['pi07_regulacion_R03.py']and _sha(Path(access.__file__))==PINS['pi07_acceso_FI_regulado_R01.py'],'Frozen legacy sources differ')
 _PRIOR_IDENTITY=old._identity;_PRIOR_FI_ROUTE=access.routes_selected_legacy
 old._identity=_legacy_identity;access.routes_selected_legacy=_outer_FI_route;_INSTALLED=True

def _selected_B_identity(a):
 identity=_identity(a)
 _require(identity.get('life_id')==LIFE and _selected()==LIFE and profile(a)is not None,'Only exact actually adopted selected B')
 return identity

def component(a,research_component):
 """Research module remains untouched; selected B receives one private copy."""
 global _PRIVATE
 if _identity(a).get('life_id')!=LIFE or _selected()!=LIFE:return research_component
 _require(profile(a)is not None,'Missing committed selected B permission')
 if _PRIVATE is None:
  path=Path(research_component.__file__)
  _require(_sha(path)==PINS['pi08_revision_flexible_B_R01.py'],'Literal research actor changed')
  spec=importlib.util.spec_from_file_location('capacidades._PI08_B_operational_identity_only_R01',path)
  private=importlib.util.module_from_spec(spec);spec.loader.exec_module(private)
  private._identity=_selected_B_identity
  _PRIVATE=private
 m=_PRIVATE._get(a)
 _require(m.get('control',{}).get('arm')=='real'and m.get('ordinal')in(30,31,32)and not any(m.get(k)for k in('pending','uncertain'))and 'reference_policy'not in m,'Only actual closed real learned B history; no external policy/control')
 return _PRIVATE

def configure_C2C(current,a):
 if _identity(a).get('life_id')!=LIFE or _selected()!=LIFE:return current
 _require(profile(a)is not None and current.protocol()[1]==C2C32,'Exact selected effective32 C2C permission required')
 _require(current.OPERATIONAL_LIFE_ID in('ECI02_PI03_REPRO_PI04_MAIN_02','ECI02_PI03_REPRO_PI04_PI05_MAIN_01',PREDECESSOR,LIFE),'Another operational identity is protected')
 current.OPERATIONAL_LIFE_ID=LIFE
 return current

def administrative_C2C_identity_proposal(metadata):
 _require(metadata.get('life_id')in(PREDECESSOR,LIFE)and not any(metadata.get(k)for k in('pending','uncertain','halted_reason')),'Only the closed inherited C2C identity leaf may map')
 result=copy.deepcopy(metadata);old=result['life_id'];result['life_id']=LIFE
 _require({k:v for k,v in result.items()if k!='life_id'}=={k:v for k,v in metadata.items()if k!='life_id'},'Unexpected history change')
 return result,{'metadata_old_life_id':old,'metadata_new_life_id':LIFE,'changed_paths':[]if old==LIFE else['/life_id'],'new_native_ticks':0,'not_learning_or_memory_transfer':True}
