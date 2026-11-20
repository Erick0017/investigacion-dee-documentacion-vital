"""Diagnostic family identity/admission over literal scientific R02 only.

No Native/DEE import on load. The sole source-local adaptation is PREPARE's
reproduction identity permission. All Native episode, readers, inputs, timing,
old histories and second-stage consequence remain the literal R02/C sources.
"""
from pathlib import Path
import ast,hashlib,importlib.util,json,re
VERSION='DEE.PI09.diagnostic_reproduction_family.transport.R01'
SOURCE=Path(__file__).with_name('pi09_consulta_selectiva_R02.py');SOURCE_SHA='3b81573f4dc0d9401db2210f3b23694e1f1f4a4d820d7654bcbd1e1b42b2dfbf'
CONFIG=Path(__file__).with_name('PI09_REPRODUCCION_FAMILIA_R01.json')
PREPARE='eci01-pi09-preparar';EPISODE='eci01-pi09-episodio';STATE='eci01-pi09-estado';MODES={PREPARE,EPISODE,STATE}
PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_RPF_';PATTERN=re.compile(re.escape(PREFIX)+r'[A-Z0-9]{1,10}\Z');SYSTEM='DEE.Cognitive.System.1.1.life.v1';_PRIVATE=None
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def family_config():
 value=read(CONFIG);need(value.get('schema')=='DEE.PI09.explicit_diagnostic_reproduction_family.v1'and value.get('prefix')==PREFIX and value.get('scientific_source_sha256')==SOURCE_SHA and value.get('only_native_real')is True,'Exact diagnostic family transport contract required');return value
def allowed_life(life):return isinstance(life,str)and PATTERN.fullmatch(life)is not None
def _identity(a):
 identity=json.loads(dict(a.world.runtime.snapshot_metadata_entries)[SYSTEM]);c=family_config();life=identity.get('life_id');root=Path(__file__).resolve().parents[1]
 need(allowed_life(life)and life==c.get('bound_life_id')and identity.get('profile')=='fisica_directa'and int(a.world.runtime.dimension)==67,'Only the exact freshly bound diagnostic family life N67/direct')
 need(not(root/'estado/ACTIVO.json').exists(),'Diagnostic family can never be ACTIVO or operate inside a selected system')
 scope=read(Path(__file__).with_name('PI09_TRANSPORTE_HEREDADO_R02.json'));need(scope.get('life_id')==life and scope.get('source_C_tick')==884835,'Actual inherited transport binding differs')
 private()._C().LIFE=life
 return identity
def private():
 global _PRIVATE
 if _PRIVATE is None:
  need(sha(SOURCE)==SOURCE_SHA,'Literal scientific R02 source changed');sp=importlib.util.spec_from_file_location('capacidades._PI09_family_identity_R02_literal',SOURCE);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
  text=SOURCE.read_text('utf-8-sig');tree=ast.parse(text);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='validate');body=ast.get_source_segment(text,node)
  before="reproduction = row['brazo'] == 'native_real' and identity['life_id'] in seal.get('native_reproduction_ids',[])"
  after="reproduction = row['brazo'] == 'native_real' and _family_allowed(identity['life_id'])"
  need(body.count(before)==1,'Exact identity-only PREPARE admission anchor changed');body=body.replace(before,after)
  m._identity=_identity;m._family_allowed=allowed_life;exec(compile(body,str(SOURCE)+':diagnostic_family_identity_only','exec'),m.__dict__)
  _PRIVATE=m
 return _PRIVATE
def validate_literal(row):
 need(isinstance(row,dict)and row.get('modo')in MODES,'Fixed reproduction-family operation required')
 if row['modo']==PREPARE:need(row=={'modo':PREPARE,'brazo':'native_real'},'Only the native-real reproduction; no plan/control/action/answer parameter')
 else:need(set(row)=={'modo'},'Only the fixed episode/state literal')
def validate(a,row):validate_literal(row);return private().validate(a,row)
def dispatch(a,row,*,actuator='closed',directory=None):
 validate(a,row);return private().dispatch(a,row,actuator=actuator,directory=directory)
def operational_dependencies(a,directory):return private().operational_dependencies(a,directory)
def uncertain(a):return private().uncertain(a)
def code_files():return tuple(dict.fromkeys([Path(__file__),CONFIG,*private().code_files()]))
