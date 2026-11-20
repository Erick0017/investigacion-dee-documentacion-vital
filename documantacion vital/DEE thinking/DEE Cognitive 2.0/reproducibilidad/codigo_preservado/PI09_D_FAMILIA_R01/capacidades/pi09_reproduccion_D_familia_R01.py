"""Reusable diagnostic D real-only family over the literal c993 D actor.

Only current transport identity and PREPARE's reproduction identity admission
change in a private namespace. No Native function, reader, input, calendar,
sample, guard, control or generic return is modified. Never selected.
"""
from pathlib import Path
import ast,hashlib,importlib.util,json,re
VERSION='DEE.PI09.D.diagnostic_reproduction_family.R01';SOURCE=Path(__file__).with_name('pi09_entorno_persistente_D_R02.py');SOURCE_SHA='c9938b50fbdf68d94954eaf341abae025faa307e4c8d24d23862c7b78bf085f8';CONFIG=Path(__file__).with_name('PI09_REPRODUCCION_D_FAMILIA_R01.json')
PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DRF_';PATTERN=re.compile(re.escape(PREFIX)+r'[A-Z0-9]{1,10}\Z');SYSTEM='DEE.Cognitive.System.1.1.life.v1';PREPARE='eci01-pi09-d-preparar';EPISODE='eci01-pi09-d-episodio';STATE='eci01-pi09-d-estado';MODES={PREPARE,EPISODE,STATE};_PRIVATE=None
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def allowed_life(life):return isinstance(life,str)and PATTERN.fullmatch(life)is not None
def _identity(a):
 root=Path(__file__).resolve().parents[1];config=read(CONFIG);identity=json.loads(dict(a.world.runtime.snapshot_metadata_entries)[SYSTEM]);life=identity.get('life_id')
 need(config.get('schema')=='DEE.PI09.D.explicit_diagnostic_family.v1'and config.get('prefix')==PREFIX and config.get('scientific_source_sha256')==SOURCE_SHA and config.get('only_real')is True,'Exact D family contract required')
 need(allowed_life(life)and life==config.get('bound_life_id')and identity.get('profile')=='fisica_directa'and int(a.world.runtime.dimension)==67 and not(root/'estado/ACTIVO.json').exists(),'Only a fresh bound D diagnostic family N67; never ACTIVO')
 old=read(Path(__file__).with_name('PI09_TRANSPORTE_HEREDADO_R02.json'));scope=read(Path(__file__).with_name('PI09_TRANSPORTE_D_R02.json'));need(old.get('life_id')==scope.get('life_id')==life and old.get('source_C_tick')==884835 and scope.get('source_D_tick')==907543,'Both exact inherited identity scopes must match')
 private()._bridge()._C().LIFE=life;return identity
def private():
 global _PRIVATE
 if _PRIVATE is None:
  need(sha(SOURCE)==SOURCE_SHA,'Literal scientific D source changed');sp=importlib.util.spec_from_file_location('capacidades._PI09_DRF_literal_D2',SOURCE);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
  text=SOURCE.read_text('utf-8-sig');node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name=='validate');body=ast.get_source_segment(text,node)
  before="repro=row['brazo']=='real'and identity['life_id']in REPRO_IDS";after="repro=row['brazo']=='real'and _family_allowed(identity['life_id'])";need(body.count(before)==1,'Exact reproduction-only D PREPARE anchor changed')
  m._identity=_identity;m._family_allowed=allowed_life;exec(compile(body.replace(before,after),str(SOURCE)+':D_family_identity_only','exec'),m.__dict__);_PRIVATE=m
 return _PRIVATE
def install_transport():
 # Source files and seal aliases remain literal. Only the new diagnostic
 # process's current identity callback changes, as in prior PI09 transports.
 from capacidades import pi09_transporte_D_R02 as transport
 transport.current=_identity;transport.base().current=_identity
def validate_literal(row):
 need(isinstance(row,dict)and row.get('modo')in MODES,'Fixed D reproduction operation required')
 if row['modo']==PREPARE:need(row=={'modo':PREPARE,'brazo':'real'},'Only D real reproduction; no control/plan/action/answer parameter')
 else:need(set(row)=={'modo'},'Only the fixed D episode/state literal')
def validate(a,row):validate_literal(row);return private().validate(a,row)
def dispatch(a,row,*,actuator='closed',directory=None):validate(a,row);return private().dispatch(a,row,actuator=actuator,directory=directory)
def operational_dependencies(a,directory):return private().operational_dependencies(a,directory)
def uncertain(a):return private().uncertain(a)
def code_files():return tuple(dict.fromkeys([Path(__file__),CONFIG,*private().code_files()]))
