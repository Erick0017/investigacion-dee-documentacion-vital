"""Fixed instrument routing for explicit PI04 protocols, never an actor policy.

Only the requested scientific operation selects a plugin. Neither correct
answers, Native action values nor environmental targets select these modules.
"""
from pathlib import Path
import importlib.util

VERSION='PI04.instrument_dispatcher.R01'
PLUGINS=(('eci01-pi04-e3-','pi04_e3_contingencia'),
         ('eci01-pi04-c2-','pi04_coordinacion_adquirida'),
         ('eci01-pi04-dg-','pi04_diagnostico_campo'),
         ('eci01-pi04-c2b-','pi04_coordinacion_simetrica_C2B'),
         ('eci01-pi04-c2c-','pi04_coordinacion_central_C2C'),
         ('eci01-pi04-dgc-','pi04_diagnostico_C2C_pasivo'))
_MODULES={}
def _load(name):
    if name not in _MODULES:
        file=Path(__file__).with_name(name+'.py')
        if not file.is_file():raise ValueError('PI04 scientific plugin is not installed: '+name)
        spec=importlib.util.spec_from_file_location('PI04_'+name,file)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        _MODULES[name]=m
    return _MODULES[name]
def _for(row):
    if not isinstance(row,dict)or not isinstance(row.get('modo'),str):raise ValueError('Explicit PI04 instrument mode required')
    for prefix,name in PLUGINS:
        if row['modo'].startswith(prefix):return _load(name)
    raise ValueError('Unknown fixed PI04 instrument family')
def validate_literal(row):return _for(row).validate_literal(row)
def validate(a,row):return _for(row).validate(a,row)
def dispatch(a,row,*,actuator='closed',directory=None):
    return _for(row).dispatch(a,row,actuator=actuator,directory=directory)
def operational_dependencies(a,directory):
    return {name:_load(name).operational_dependencies(a,directory)
            for _,name in PLUGINS if Path(__file__).with_name(name+'.py').is_file()}
def uncertain(a):
    return any(_load(name).uncertain(a)for _,name in PLUGINS
               if Path(__file__).with_name(name+'.py').is_file())
def code_files():
    root=Path(__file__).parent
    names=[name+'.py'for _,name in PLUGINS]+['e3_retorno_desacoplado_R01.py','pi04_selector_contextual_C2_R01.py','pi04_sensor_simetrico_C2B_R01.py','pi04_sensor_central_C2C_R01.py']
    return [Path(__file__)]+[root/name for name in names if(root/name).is_file()]
