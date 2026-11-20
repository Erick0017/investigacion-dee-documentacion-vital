"""Fixed PI09 instrument dispatch by explicit MODES, never by Native choice."""
from pathlib import Path
import hashlib,importlib.util,json
VERSION='DEE.PI09.fixed_instrument_dispatch.R02'
REGISTRY=Path(__file__).with_name('PI09_PLUGINS_R02.json')
_MODULES={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def registry():
 r=json.loads(REGISTRY.read_text('utf-8-sig'))
 if r.get('schema')!='DEE.PI09.fixed_plugins_source_registry.R01':raise ValueError('Registro PI09 explícito requerido')
 for name,digest in r['files_sha256'].items():
  if Path(name).name!=name or sha(Path(__file__).with_name(name))!=digest:raise ValueError('Cambió fuente PI09: '+name)
 return r
def modules():
 r=registry();answer=[];seen=set()
 for name in r['plugins']:
  if name+'.py'not in r['files_sha256']:raise ValueError('Plugin PI09 sin hash explícito')
  if name not in _MODULES:
   source=Path(__file__).with_name(name+'.py');sp=importlib.util.spec_from_file_location('capacidades._PI09_instrument_'+name,source)
   m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);_MODULES[name]=m
  m=_MODULES[name]
  if any(mode in seen or not mode.startswith('eci01-pi09-')for mode in m.MODES):raise ValueError('Modos PI09 repetidos/no propios')
  seen.update(m.MODES);answer.append(m)
 return answer
def _for(row):
 if not isinstance(row,dict)or not isinstance(row.get('modo'),str):raise ValueError('Literal PI09 explícito requerido')
 found=[m for m in modules()if row['modo']in m.MODES]
 if len(found)!=1:raise ValueError('Modo PI09 no registrado')
 return found[0]
def validate_literal(row):return _for(row).validate_literal(row)
def allowed(a):
 from capacidades import pi09_transporte_heredado_R02 as transport
 return transport.current(a)
def validate(a,row):
 allowed(a);module=_for(row)
 active=Path(__file__).resolve().parents[1]/'estado/ACTIVO.json'
 if active.exists()and Path(module.__file__).name!='pi09_consulta_selectiva_R02.py':
  raise ValueError('Los instrumentos diagnósticos PI09 no están autorizados en el principal seleccionado')
 return module.validate(a,row)
def dispatch(a,row,*,actuator='closed',directory=None):
 validate(a,row);return _for(row).dispatch(a,row,actuator=actuator,directory=directory)
def operational_dependencies(a,directory):
 from capacidades import pi09_transporte_heredado_R02 as transport
 if not transport.applies(a):return {'version':VERSION,'present':False,'new_native_ticks':0}
 allowed(a);return {m.VERSION:m.operational_dependencies(a,directory)for m in modules()}
def uncertain(a):
 from capacidades import pi09_transporte_heredado_R02 as transport
 if not transport.applies(a):return False
 allowed(a);return any(m.uncertain(a)for m in modules())
def code_files():
 r=registry();out=[Path(__file__),REGISTRY]
 out.extend(Path(__file__).with_name(n)for n in r['files_sha256'])
 for m in modules():out.extend(m.code_files())
 return tuple(dict.fromkeys(out))
