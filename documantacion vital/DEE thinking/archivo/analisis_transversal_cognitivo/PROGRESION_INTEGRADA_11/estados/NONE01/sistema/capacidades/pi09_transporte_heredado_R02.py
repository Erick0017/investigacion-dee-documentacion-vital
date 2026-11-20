"""Exact-clone read-only access to literal PI08 C/B ancestors.

Only private Python identity namespaces differ. No Native metadata, bank,
clock, history, protocol or material operation is rewritten or reset.
"""
from pathlib import Path
import hashlib,importlib.util,json,re,types

VERSION='DEE.PI09.exact_inherited_C_B_readonly_transport.R02'
SYSTEM_KEY='DEE.Cognitive.System.1.1.life.v1'
C_KEY='DEE.Cognitive.PI08.conditional_sensor_register_access.C.R02'
B_KEY='DEE.Cognitive.PI08.successive_contextual_regulation.B.R01'
SCOPE=Path(__file__).with_name('PI09_TRANSPORTE_HEREDADO_R02.json')
SOURCE_SNAPSHOT='ef52add3d7a6a5b9e310efb815bf8ae7dd47cb968104e7b1fa5c8a2b9f726d22'
_PRIVATE={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def require(ok,msg):
 if not ok:raise ValueError(msg)
def config():
 value=read(SCOPE)
 require(value.get('schema')=='DEE.PI09.exact_inherited_transport_scope.R01'and
         re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_[A-Za-z0-9_]{1,32}',str(value.get('life_id','')))and
         value.get('source_C_snapshot_sha256')==SOURCE_SNAPSHOT and value.get('source_C_tick')==884835,
         'Se requiere la identidad PI09 exacta derivada del prefijo C fijado')
 for name,digest in value['literal_sources_sha256'].items():
  require(Path(name).name==name and sha(Path(__file__).with_name(name))==digest,'Cambió una fuente heredada: '+name)
 return value
def applies(a):
 entries=dict(a.world.runtime.snapshot_metadata_entries)
 if not SCOPE.is_file():
  require(not any(k.startswith('DEE.Cognitive.PI09.')for k in entries),'Falta el contrato de transporte de un futuro PI09')
  return False
 identity=json.loads(entries[SYSTEM_KEY]);value=read(SCOPE)
 return identity.get('life_id')==value.get('life_id')
def current(a):
 scope=config();entries=dict(a.world.runtime.snapshot_metadata_entries);identity=json.loads(entries[SYSTEM_KEY])
 require(identity.get('life_id')==scope['life_id']and identity.get('profile')=='fisica_directa'and int(a.world.runtime.dimension)==67,
         'Sólo la copia PI09 exacta N67/fisica_directa')
 root=Path(__file__).resolve().parents[1]
 active=root/'estado/ACTIVO.json'
 if active.exists():
  require(read(active).get('life_id')==identity['life_id'],'ACTIVO no coincide con la identidad PI09 exacta')
  # Dormant administrative permission. The scientific helper validates the
  # exact canonical native-real ID, prepared KEY/control, COMMITTED contract
  # and adoption SHA. It does not call this transport function recursively.
  from capacidades import pi09_consulta_selectiva_R02 as consultation
  consultation._operational_permission(a,identity,read(consultation.SEAL))
 for key,digest in scope['inherited_metadata_sha256'].items():
  require(key in entries and hashlib.sha256(entries[key].encode('utf8')).hexdigest()==digest,
          'Cambió metadata histórica protegida; no se permite reiniciar ni reinterpretar '+key)
 return identity
def _component(a,original,kind):
 current(a);scope=config();source=Path(original.__file__)
 require(source.name in scope['literal_sources_sha256']and sha(source)==scope['literal_sources_sha256'][source.name],'Cuerpo original no coincide')
 key=(str(source.resolve()),kind,scope['life_id'])
 if key not in _PRIVATE:
  spec=importlib.util.spec_from_file_location('capacidades._PI09_private_ancestor_'+kind+'_'+hashlib.sha256(scope['life_id'].encode()).hexdigest()[:10],source)
  private=importlib.util.module_from_spec(spec);spec.loader.exec_module(private)
  original_validate=private.validate;original_files=private.code_files
  if kind=='C':
   # Home belongs to the CURRENT transport identity. The unchanged historical
   # protocol must still validate its original literal seal, not pretend that
   # seal was reissued for the new clone. Only function globals are separated.
   protocol_globals=dict(private.protocol.__globals__)
   private.protocol=types.FunctionType(private.protocol.__code__,protocol_globals,
                                       private.protocol.__name__,private.protocol.__defaults__,private.protocol.__closure__)
   private.LIFE=scope['life_id']
  private._identity=current
  def validate(a,row):
   current(a)
   require(row=={'modo':private.STATE},'El antecedente '+kind+' sólo admite STATE; no PREPARE/START/EPISODE ni doble calendario')
   return original_validate(a,row)
  private.validate=validate
  private.code_files=lambda:tuple(dict.fromkeys([Path(__file__),SCOPE,*original_files()]))
  _PRIVATE[key]=private
 return _PRIVATE[key]
def component_B(a,original):
 if applies(a):return _component(a,original,'B')
 entries=dict(a.world.runtime.snapshot_metadata_entries)
 if C_KEY in entries:
  from capacidades import pi08_identidad_B_readonly_C_R01 as old_transport
  return old_transport.component(a,original)
 return original
def component_C(a,original):return _component(a,original,'C')if applies(a)else original
def scope():return {'version':VERSION,'administrative_identity_only':True,'old_B_C_material_modes_allowed':False,
                   'Native_state_modified':False,'source_C_snapshot_sha256':SOURCE_SNAPSHOT}
