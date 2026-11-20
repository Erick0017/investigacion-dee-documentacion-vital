"""Fixed O/H passive-observer control on explicit diagnostic clones only.

Importing creates nothing and imports no DEE module. Both branches advance
134ticks using identical one-tick OrganizationalWorld calls; only fixed-point
observe calls differ. No sensor, material query, warning or valence is submitted.
"""
MODE='eci01-pi02-observar-OH'
VERSION='PI02.fixed_OH_observation.R04'
TICKS=134
SYSTEM_KEY='DEE.Cognitive.System.1.1.life.v1'
HABITAT_KEY='DEE.Cognitive.PI02.continuous_workbench.R04'
DIAGNOSTIC_PREFIXES=('ECI02_PI02_OH_','ECI02_PI02_DIAG_OH_')

def validate_literal(row):
    if not isinstance(row,dict)or set(row)!={'modo','registro'}or row.get('modo')!=MODE or type(row['registro'])is not bool:
        raise ValueError('Fixed O/H diagnostic accepts exactly modo and boolean registro; no reader, time, target or life override')

def validate(a,row):
    validate_literal(row)
    if int(a.world.runtime.dimension)!=67:raise ValueError('Existing N67 diagnostic clone required')
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    if HABITAT_KEY in entries:raise ValueError('O/H isolation control requires a clone without admitted R04 habitat; no silent bridge disable')
    if SYSTEM_KEY not in entries:raise ValueError('Recorded complete-life identity required; no untracked reconstructed world')
    from dee_thinking.persistence import decode_metadata
    life=decode_metadata(entries[SYSTEM_KEY]).get('life_id')
    if not isinstance(life,str)or not life.startswith(DIAGNOSTIC_PREFIXES):
        raise ValueError('This observer control is restricted to explicit ECI02_PI02_OH_ / DIAG_OH_ clones, never MAIN')

def dispatch(a,row,*,directory=None,actuator='closed'):
    validate(a,row)
    from capacidades import pi01_traza_legal_base as trace
    from capacidades import pi02_advertencia_R03 as warning
    from app.native_tools import physical
    before=physical(a.world,occupation=True);start=int(a.tick)
    points={'O':list(trace.get(a)['origin']),'H':list(warning.H)}
    frames=[]
    for tick in range(start+1,start+TICKS+1):
        a.run_until(tick)
        if int(a.tick)!=tick:raise RuntimeError('Owner did not reach the exact fixed observation tick; preserve future')
        if row['registro']:
            frames.append({'tick':tick,'O':trace.obs(a,points['O']),'H':warning._observation(a,points['H'])})
    return {'version':VERSION,'record_enabled':row['registro'],'ticks':TICKS,'before':before,'after':physical(a.world,occupation=True),
            'points':points,'frames':frames,'fixed_site_observations':2*TICKS if row['registro']else 0,
            'new_material_inputs':[],'new_sensor_requests':[],'new_query_requests':[],
            'one_tick_run_until_calls':TICKS,'bridge_not_admitted':True,
            'life_identity_used_only_for_diagnostic_safety_guard':True,
            'scope':'External fixed O/H observer, not actor perception or cognition. Matched source clones and final global snapshot comparison determine passivity only within this134tick history. No field, time window or alternate reader is selected from correctness.'}
