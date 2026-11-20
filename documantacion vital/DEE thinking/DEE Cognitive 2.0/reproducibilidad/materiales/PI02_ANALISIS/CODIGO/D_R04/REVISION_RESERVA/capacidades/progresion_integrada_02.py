"""PI02 R04 opt-in continuous habitat through the existing Cognitive owner.

Literal validation imports no Native. New habitat preparation and bridge
enable/disable are operator actions, never attributed as acquired regulation.
Legacy R03/R02 protocols remain available through their exact saved module.
"""
VERSION='PI02.continuous_habitat_owner_interface.R04'
PREPARE='eci01-pi02-habitat-preparar'
TIME='eci01-pi02-tiempo'
PAUSE='eci01-pi02-pausar-habitat'
RESUME='eci01-pi02-reactivar-habitat'
STATE='eci01-pi02-habitat-estado'
EXTEND='eci01-pi02-habitat-extender'
NEW_MODES={PREPARE,TIME,PAUSE,RESUME,STATE,EXTEND}

def _base():
    from capacidades import pi02_desarrollo_base as base
    return base
def _habitat():
    from capacidades import pi02_habitat_R04 as habitat
    return habitat
def _admitted(a):
    return _habitat().KEY in dict(a.world.runtime.snapshot_metadata_entries)

def validate_literal(row):
    mode=row.get('modo')if isinstance(row,dict)else None
    if mode=='eci01-pi02-observar-OH':
        from capacidades import diagnostico_puertos_OH_R04 as diagnostic
        return diagnostic.validate_literal(row)
    if mode==PREPARE:
        if set(row)!={'modo','serie','historia','brazo'}or row['serie']not in('development','reserved')or row['historia']not in('paired','unpaired','no_training','report_only')or row['brazo']not in('real','warning_cut','actuator_null','valence_omit'):
            raise ValueError('Exact declared habitat series/history/arm; no target, reader or action field')
        return
    if mode==TIME:
        if set(row)!={'modo','ticks'}or type(row['ticks'])is not int or not 1<=row['ticks']<=12000:
            raise ValueError('A finite generic time window of1..12000 exact ticks required')
        return
    if mode in(PAUSE,RESUME,STATE,EXTEND):
        if set(row)!={'modo'}:raise ValueError('This habitat operation accepts only modo; no replacement state or answer')
        return
    return _base().validate_literal(row)

def validate(a,row):
    validate_literal(row)
    if row['modo']=='eci01-pi02-observar-OH':
        from capacidades import diagnostico_puertos_OH_R04 as diagnostic
        return diagnostic.validate(a,row)
    if row['modo']not in NEW_MODES:return _base().validate(a,row)
    if row['modo']in(PAUSE,STATE)and not _admitted(a):return
    from capacidades.adapter_habitat_R04 import HabitatAdapter
    if not isinstance(a,HabitatAdapter):raise ValueError('The admitted existing owner must supply its same-world habitat adapter')
    if row['modo']!=PREPARE:_habitat().get(a)

def dispatch(a,row,*,directory=None,actuator='closed'):
    validate(a,row);mode=row['modo']
    if mode=='eci01-pi02-observar-OH':
        from capacidades import diagnostico_puertos_OH_R04 as diagnostic
        return diagnostic.dispatch(a,row,directory=directory,actuator=actuator)
    if mode not in NEW_MODES:return _base().dispatch(a,row,directory=directory,actuator=actuator)
    habitat=_habitat()
    if mode in(PAUSE,STATE)and not _admitted(a):
        return {'version':VERSION,'habitat_admitted':False,'external_bridge_enabled':False,'new_native_ticks':0,'no_op':True,'native_memory_reset':False,'scope':'No preparation exists. State/pause do not create one or advance the world.'}
    if directory is None:raise ValueError('Existing owner operational directory required; no laboratory lookup')
    if mode==PREPARE:return habitat.admit(a,directory,row['serie'],row['historia'],row['brazo'])
    if mode==PAUSE:return habitat.set_enabled(a,False)
    if mode==RESUME:return habitat.set_enabled(a,True)
    if mode==EXTEND:return habitat.extend_retention(a,directory)
    if mode==STATE:return {'version':VERSION,'habitat_admitted':True,'habitat':habitat.status(a,directory),'scope':'Administrative state view, no material query or reconstruction.'}
    before=habitat.status(a,directory);start=int(a.tick)
    # HabitatAdapter advances the same owned base and processes fixed physical
    # events. Neither this request nor the caller issues an action per episode.
    a.run_until(start+row['ticks'])
    return {'version':VERSION,'before_tick':start,'after_tick':int(a.tick),'generic_ticks_requested':row['ticks'],'before_habitat':before,'after_habitat':habitat.status(a,directory),'initiative_scope':'A single generic time window is provided by the operator. Returning physical events trigger fixed transducers; recurrence/busy/cost/codec remain prepared, history effects need controls.'}

def operational_dependencies(a,directory):
    return {'legacy_PI02':_base().operational_dependencies(a,directory),'R04':_habitat().operational_dependencies(a,directory),'scope':'Complete local progress/artifact validation; not participant knowledge or an external policy.'}
def uncertain(a):return _base().uncertain(a)or _habitat().uncertain(a)
