"""PI11 fixed plugin routing. Pure import; no world, owner or Native call."""
from pathlib import Path
import hashlib, importlib.util, json
VERSION='DEE.PI11.fixed_dispatcher.R01'
REGISTRY=Path(__file__).with_name('PI11_PLUGINS_R01.json')
_MODULES={}
def registry():
    r=json.loads(REGISTRY.read_text('utf-8-sig'))
    if r.get('schema')!='DEE.PI11.fixed_plugins.R01':raise ValueError('Exact PI11 registry required')
    for name,digest in r['files_sha256'].items():
        if Path(name).name!=name or hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()!=digest:raise ValueError('Changed PI11 dependency '+name)
    return r
def modules():
    r=registry();out=[];seen=set()
    for name in r['plugins']:
        if name+'.py' not in r['files_sha256']:raise ValueError('Unpinned PI11 plugin')
        if name not in _MODULES:
            s=importlib.util.spec_from_file_location('capacidades._PI11_'+name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);_MODULES[name]=m
        m=_MODULES[name]
        if any(mode in seen or not mode.startswith('eci01-pi11-')for mode in m.MODES):raise ValueError('Duplicate or unowned PI11 mode')
        seen.update(m.MODES);out.append(m)
    return out
def plugin(row):
    if not isinstance(row,dict)or not isinstance(row.get('modo'),str):raise ValueError('Exact PI11 literal required')
    found=[m for m in modules()if row['modo']in m.MODES]
    if len(found)!=1:raise ValueError('PI11 mode not uniquely registered')
    return found[0]
def validate_literal(row):return plugin(row).validate_literal(row)
def validate(a,row):return plugin(row).validate(a,row)
def dispatch(a,row,*,actuator='closed',directory=None):
    validate(a,row);return plugin(row).dispatch(a,row,actuator=actuator,directory=directory)
def operational_dependencies(a,directory):return {m.VERSION:m.operational_dependencies(a,directory)for m in modules()}
def uncertain(a):return any(m.uncertain(a)for m in modules())
def code_files():
    r=registry();out=[Path(__file__),REGISTRY]
    out.extend(Path(__file__).with_name(n)for n in r['files_sha256'])
    for m in modules():out.extend(m.code_files())
    return tuple(dict.fromkeys(out))
