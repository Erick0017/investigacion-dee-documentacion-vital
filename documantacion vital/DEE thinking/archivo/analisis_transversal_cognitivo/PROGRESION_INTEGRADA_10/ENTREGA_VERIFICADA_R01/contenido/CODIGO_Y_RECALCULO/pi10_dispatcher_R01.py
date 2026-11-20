"""Fixed PI10 instrumentation routing; never selects an actor response."""
from pathlib import Path
import hashlib,importlib.util,json
VERSION='DEE.PI10.fixed_dispatcher.R01'
REGISTRY=Path(__file__).with_name('PI10_PLUGINS_R01.json');_MODULES={}
def registry():
 r=json.loads(REGISTRY.read_text('utf-8-sig'))
 if r.get('schema')!='DEE.PI10.fixed_plugins.v1':raise ValueError('Exact PI10 registry required')
 for name,digest in r['files_sha256'].items():
  if Path(name).name!=name or hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()!=digest:raise ValueError('Changed PI10 source/config '+name)
 return r
def modules():
 r=registry();out=[];seen=set()
 for name in r['plugins']:
  if name+'.py'not in r['files_sha256']:raise ValueError('Unpinned PI10 plugin')
  if name not in _MODULES:
   s=importlib.util.spec_from_file_location('capacidades._PI10_fixed_plugin_'+name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);_MODULES[name]=m
  m=_MODULES[name]
  if any(mode in seen or not mode.startswith('eci01-pi10-')for mode in m.MODES):raise ValueError('Duplicate/unowned PI10 mode')
  seen.update(m.MODES);out.append(m)
 return out
def plugin(row):
 if not isinstance(row,dict)or not isinstance(row.get('modo'),str):raise ValueError('Exact PI10 literal required')
 found=[m for m in modules()if row['modo']in m.MODES]
 if len(found)!=1:raise ValueError('PI10 mode not uniquely registered')
 return found[0]
def validate_literal(row):return plugin(row).validate_literal(row)
def validate(a,row):return plugin(row).validate(a,row)
def dispatch(a,row,*,actuator='closed',directory=None):validate(a,row);return plugin(row).dispatch(a,row,actuator=actuator,directory=directory)
def operational_dependencies(a,directory):
 from capacidades import pi10_transporte_ancestral_R01 as t
 if not t.applies(a):return {'version':VERSION,'present':False,'new_ticks':0}
 t.identity(a);return {m.VERSION:m.operational_dependencies(a,directory)for m in modules()}
def uncertain(a):
 from capacidades import pi10_transporte_ancestral_R01 as t
 return t.applies(a)and any(m.uncertain(a)for m in modules())
def code_files():
 r=registry();out=[Path(__file__),REGISTRY];out.extend(Path(__file__).with_name(n)for n in r['files_sha256'])
 for m in modules():out.extend(m.code_files())
 return tuple(dict.fromkeys(out))
