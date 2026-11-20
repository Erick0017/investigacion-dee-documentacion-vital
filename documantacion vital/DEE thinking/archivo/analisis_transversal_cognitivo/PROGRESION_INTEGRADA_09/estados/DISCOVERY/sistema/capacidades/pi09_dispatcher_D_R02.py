"""Exact D dispatch. Inherited R02 is STATE-only; D/FI8 are distinct modes."""
from pathlib import Path
import hashlib,importlib.util,json
VERSION='DEE.PI09.D.fixed_dispatch_and_ancestral_readonly.R02';REGISTRY=Path(__file__).with_name('PI09_PLUGINS_D_R02.json');_MODULES={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def registry():
    r=json.loads(REGISTRY.read_text('utf-8-sig'))
    if r.get('schema')!='DEE.PI09.D.fixed_plugins_source_registry.R02':raise ValueError('Exact closed D registry required')
    for name,digest in r['files_sha256'].items():
        if Path(name).name!=name or sha(Path(__file__).with_name(name))!=digest:raise ValueError('Changed D code/config source: '+name)
    return r
def modules():
    r=registry();out=[];seen=set()
    for name in r['plugins']:
        if name+'.py'not in r['files_sha256']:raise ValueError('Unpinned D plugin')
        if name not in _MODULES:
            file=Path(__file__).with_name(name+'.py');s=importlib.util.spec_from_file_location('capacidades._PI09_D_fixed_plugin_'+name,file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);_MODULES[name]=m
        m=_MODULES[name]
        if any(mode in seen or not mode.startswith('eci01-pi09-')for mode in m.MODES):raise ValueError('Duplicate/unowned D mode')
        seen.update(m.MODES);out.append(m)
    return out
def _for(row):
    if not isinstance(row,dict)or not isinstance(row.get('modo'),str):raise ValueError('Exact D literal required')
    found=[m for m in modules()if row['modo']in m.MODES]
    if len(found)!=1:raise ValueError('D mode is not uniquely registered; old R02 PREPARE/EPISODE are unavailable')
    return found[0]
def validate_literal(row):return _for(row).validate_literal(row)
def allowed(a):
    from capacidades import pi09_transporte_D_R02 as t
    return t.current(a)
def validate(a,row):
    identity=allowed(a);m=_for(row);active=Path(__file__).resolve().parents[1]/'estado/ACTIVO.json'
    if active.exists()and json.loads(active.read_text('utf-8-sig')).get('life_id')!=identity['life_id']and row['modo']not in('eci01-pi09-d-estado','eci01-pi09-estado','eci01-pi09-fi-lote-estado'):raise ValueError('Administrative prepared load permits only three public STATE requests; no material action before commit')
    if active.exists()and Path(m.__file__).name not in('pi09_entorno_persistente_D_R02.py','pi09_FI8_D_alias_R01.py','pi09_antecedente_R02_readonly_D_R01.py'):raise ValueError('Diagnostic/reference instruments never become selected capabilities')
    return m.validate(a,row)
def dispatch(a,row,*,actuator='closed',directory=None):validate(a,row);return _for(row).dispatch(a,row,actuator=actuator,directory=directory)
def operational_dependencies(a,directory):
    from capacidades import pi09_transporte_D_R02 as t
    if not t.applies(a):return {'version':VERSION,'present':False,'new_native_ticks':0}
    allowed(a);return {m.VERSION:m.operational_dependencies(a,directory)for m in modules()}
def uncertain(a):
    from capacidades import pi09_transporte_D_R02 as t
    if not t.applies(a):return False
    allowed(a);return any(m.uncertain(a)for m in modules())
def code_files():
    r=registry();out=[Path(__file__),REGISTRY];out.extend(Path(__file__).with_name(n)for n in r['files_sha256'])
    for m in modules():out.extend(m.code_files())
    return tuple(dict.fromkeys(out))
