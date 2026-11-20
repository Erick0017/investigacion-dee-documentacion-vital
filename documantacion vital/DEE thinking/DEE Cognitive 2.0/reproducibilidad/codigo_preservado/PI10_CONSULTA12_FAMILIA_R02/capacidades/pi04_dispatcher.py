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
def _effective_plugin(a,name,for_dependencies=False):
    base=_load(name)
    if name=='pi04_coordinacion_central_C2C':
        component=_load('pi08_integracion_c2c_R01').effective_component(a,base,for_dependencies=for_dependencies)
        return _load('pi09_permiso_operativo_D_R01').configure_C2C(_load('pi09_permiso_operativo_R01').configure_C2C(_load('pi08_permisos_operativos_R01').configure_C2C(_load('pi05_permiso_principal_R01').configure(component,a),a),a),a)
    return base
def _material_for(a,row):
    # Only an explicit external-extension key changes the protocol instance.
    # Native actions/results never choose an instrument or expected output.
    original=_for(row)
    if getattr(original,'KEY',None)=='DEE.Cognitive.PI04.C2C.coordination.R01':
        component=_load('pi08_integracion_c2c_R01').effective_component(a,original)
        return _load('pi09_permiso_operativo_D_R01').configure_C2C(_load('pi09_permiso_operativo_R01').configure_C2C(_load('pi08_permisos_operativos_R01').configure_C2C(_load('pi05_permiso_principal_R01').configure(component,a),a),a),a)
    return original
def validate(a,row):return _material_for(a,row).validate(a,row)
def dispatch(a,row,*,actuator='closed',directory=None):
    return _material_for(a,row).dispatch(a,row,actuator=actuator,directory=directory)
def operational_dependencies(a,directory):
    result={name:_effective_plugin(a,name,for_dependencies=True).operational_dependencies(a,directory)
            for _,name in PLUGINS if Path(__file__).with_name(name+'.py').is_file()}
    result['PI05_explicit_environment30']=_load('pi05_c2c_ofertas_R01').operational_dependencies(a,directory)
    result['PI08_integration32']=_load('pi08_integracion_c2c_R01').operational_dependencies(a,directory)
    return result
def uncertain(a):
    if _load('pi08_integracion_c2c_R01').uncertain(a):return True
    if _load('pi05_c2c_ofertas_R01').uncertain(a):return True
    return any(_effective_plugin(a,name,for_dependencies=True).uncertain(a)for _,name in PLUGINS
               if Path(__file__).with_name(name+'.py').is_file())
def code_files():
    root=Path(__file__).parent
    names=[name+'.py'for _,name in PLUGINS]+['e3_retorno_desacoplado_R01.py','pi04_selector_contextual_C2_R01.py','pi04_sensor_simetrico_C2B_R01.py','pi04_sensor_central_C2C_R01.py']
    paths=[Path(__file__)]+[root/name for name in names if(root/name).is_file()]
    paths.extend(_load('pi05_c2c_ofertas_R01').code_files())
    paths.append(root/'pi05_permiso_principal_R01.py')
    paths.extend(_load('pi08_integracion_c2c_R01').code_files())
    paths.append(root/'pi08_permisos_operativos_R01.py')
    paths.extend(_load('pi09_permiso_operativo_R01').code_files())
    return list(dict.fromkeys(paths))
