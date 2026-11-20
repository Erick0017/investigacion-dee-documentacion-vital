"""PI02 R03 development: interface decomposition and learned warning apparatus."""
from capacidades import pi02_retornos_base as base
VERSION='PI02.warning_and_interface_development.R03'
def validate_literal(row):
    mode=row.get('modo')if isinstance(row,dict)else None
    if mode=='eci01-pi02-fi-prueba':
        from capacidades import diagnostico_FI_R03 as d;return d.validate_literal(row)
    if mode=='eci01-pi02-advertencia-preparar':
        if set(row)!={'modo'}:raise ValueError('No geometry, target or answer fields')
        return
    if mode=='eci01-pi02-advertencia-adquirir':
        if set(row)!={'modo','historia'}or row['historia']not in('paired','unpaired','omit','no_training','report_only'):raise ValueError('Declared history only')
        return
    if mode=='eci01-pi02-advertencia-usar':
        if set(row)!={'modo','periodos','aviso'}or type(row['periodos'])is not int or row['periodos']not in(2,3,5)or type(row['aviso'])is not bool:raise ValueError('Fixed phase interval and visible signal only')
        return
    return base.validate_literal(row)
def validate(a,row):
    validate_literal(row)
    if row['modo']=='eci01-pi02-fi-prueba':
        from capacidades import diagnostico_FI_R03 as d;d.validate(a,row)
    elif row['modo'].startswith('eci01-pi02-advertencia-'):
        if row['modo']!='eci01-pi02-advertencia-preparar':
            from capacidades import pi02_advertencia_R03 as w;w.get(a)
    else:base.validate(a,row)
def dispatch(a,row,*,directory=None,actuator='closed'):
    validate(a,row);mode=row['modo']
    if mode=='eci01-pi02-fi-prueba':
        from capacidades import diagnostico_FI_R03 as d;return d.dispatch(a,row,directory=directory,actuator=actuator)
    if mode.startswith('eci01-pi02-advertencia-'):
        from capacidades import pi02_advertencia_R03 as w
        if mode.endswith('-preparar'):return w.prepare(a)
        if mode.endswith('-adquirir'):return w.train(a,row['historia'])
        return w.probe(a,row['periodos'],row['aviso'])
    return base.dispatch(a,row,directory=directory,actuator=actuator)
def operational_dependencies(a,directory):
    from capacidades import pi02_advertencia_R03 as w
    from dee_thinking.persistence import decode_metadata
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    warning=decode_metadata(entries[w.KEY])if w.KEY in entries else None
    return {'R02':base.operational_dependencies(a,directory),'R03_warning_protocol':warning,'scope':'Protocol provenance/calendar are not an actor answer. No lookup outside operational state.'}
def uncertain(a):
    from capacidades import pi02_advertencia_R03 as w
    from dee_thinking.persistence import decode_metadata
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    warning=decode_metadata(entries[w.KEY])if w.KEY in entries else {}
    return base.uncertain(a)or bool(warning.get('uncertain')or warning.get('in_progress'))
