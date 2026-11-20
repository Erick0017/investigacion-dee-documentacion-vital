"""RP-capsule-only administrative identity mapping for an acquired B clone.

No Source/Native mutation, admission, stimulus, decoder or action is changed.
The literal validator still runs; its role identity is mapped only while that
validator executes. Outside validation the actual new SYSTEM identity is used
for journals/state/effects. No selected life or reference/control may enter.
Material CLI replay remains pending until an actual completed run is recorded.
"""
from pathlib import Path
import hashlib, importlib.util, json

VERSION='DEE.PI08.B.RP.explicit_identity_transport.R02'
PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_BRP_'
SOURCE_LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_REAL_01'
SYSTEM_KEY='DEE.Cognitive.System.1.1.life.v1'
B_KEY='DEE.Cognitive.PI08.successive_contextual_regulation.B.R01'
SOURCE_SHA='aebe20a4566046957b274b07b942a3843ab4b612a9214791ff38edeb6bc53480'
SOURCE_A_MANIFEST='dfadc5037b804f3c6112263eb0af84f6215d53fd3cb138ae143676a56dfcc00c'
_PRIVATE=None;_VALIDATION_IDENTITY=False

def _require(ok,message):
 if not ok:raise ValueError(message)

def _current(a):
 identity=json.loads(dict(a.world.runtime.snapshot_metadata_entries)[SYSTEM_KEY])
 _require(identity.get('life_id','').startswith(PREFIX)and identity.get('profile')=='fisica_directa'and int(a.world.runtime.dimension)==67,'Explicit fresh acquired-B RP diagnostic identity required')
 active=Path(__file__).resolve().parents[1]/'estado/ACTIVO.json'
 _require(not active.exists(),'RP identity transport never admits a selected/ACTIVO system')
 entries=dict(a.world.runtime.snapshot_metadata_entries)
 if B_KEY in entries:
  m=json.loads(entries[B_KEY])
  _require(m.get('control',{}).get('arm')=='real'and m.get('ordinal')in range(12,33)and 'reference_policy'not in m,'Only a real B continuation, never control/reference policy')
 return identity

def _identity(a):
 identity=_current(a)
 return {**identity,'life_id':SOURCE_LIFE}if _VALIDATION_IDENTITY else identity

def component(a,research_component):
 global _PRIVATE
 _current(a)
 if _PRIVATE is None:
  path=Path(research_component.__file__)
  _require(hashlib.sha256(path.read_bytes()).hexdigest()==SOURCE_SHA,'Frozen B research source differs')
  spec=importlib.util.spec_from_file_location('capacidades._PI08_B_RP_identity_transport_R02',path)
  private=importlib.util.module_from_spec(spec);spec.loader.exec_module(private)
  original_validate=private.validate
  private._identity=_identity
  def validate(a,row):
   global _VALIDATION_IDENTITY
   _current(a)
   if row.get('modo')=='eci01-pi08-b-iniciar':
    _require(B_KEY not in dict(a.world.runtime.snapshot_metadata_entries)and row=={'modo':'eci01-pi08-b-iniciar','brazo':'real','prefijo_sha256':SOURCE_A_MANIFEST,'registro_global':False},'Only one explicit real admission from the exact A prefix; no reset/control/recording override')
   else:_require(set(row)=={'modo'}and row.get('modo')in('eci01-pi08-b-estado','eci01-pi08-b-episodio'),'Only real continuation state/next-use, no supply/force')
   _require(not _VALIDATION_IDENTITY,'No recursive identity-projection scope')
   _VALIDATION_IDENTITY=True
   try:return original_validate(a,row)
   finally:_VALIDATION_IDENTITY=False
  private.validate=validate
  _PRIVATE=private
 return _PRIVATE

def transport_scope():
 return {'version':VERSION,'new_life_prefix':PREFIX,'source_role_identity':SOURCE_LIFE,
         'actual_SYSTEM_identity_never_modified':True,'role_identity_only_during_original_validation':True,
         'old_validator_not_removed':True,'reference_or_yoked_omit_policy_allowed':False,'real_admission_only_from_exact_A_prefix':True,
         'Native_policy_or_inputs_modified':False,'Native_replay_verified':False}
