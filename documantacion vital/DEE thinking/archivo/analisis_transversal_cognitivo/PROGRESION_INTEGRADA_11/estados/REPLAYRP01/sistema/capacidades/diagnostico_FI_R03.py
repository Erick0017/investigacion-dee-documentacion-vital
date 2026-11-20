"""PI02 R03 developmental FI/admission diagnostic; no experiments at import.

Root must install this file and fi_async_R03.py in the candidate capacidades
package, freeze that revision, and invoke it only through the owned world.
The investigator selects diagnostic conditions; no learned guard is claimed.
"""
from pathlib import Path
import hashlib

VERSION='PI02.FI128.admission_diagnostic.R03B'
MODE='eci01-pi02-fi-prueba'
RAW_NOISE_CHANNEL='PI02.R03.FI.noise.raw0'
SHAM_NOISE_CHANNEL='PI02.R03.FI.noise.sham'
SHAM_SITE=(1,11,0);SHAM_DIRECTION=(-1,1,0);SHAM_STATE=600001
NOISE_LOAD=7

def validate_literal(row):
    if not isinstance(row,dict)or row.get('modo')!=MODE:
        raise ValueError('Explicit PI02 FI diagnostic literal required')
    if set(row)!={'modo','izquierda','derecha','asincrono','ruido'}:
        raise ValueError('Exact modo/izquierda/derecha/asincrono/ruido fields; no target, desired sign or alternative reader')
    if any(type(row[name])is not int or not 0<=row[name]<=20 for name in ('izquierda','derecha')):
        raise ValueError('Two independent public integer loads0..20 required')
    if type(row['asincrono'])is not bool or row['ruido']not in ('none','active','sham','guarded'):
        raise ValueError('Declared boolean asynchronous flag and noise condition required')
    if not row['asincrono']and row['ruido']!='none':
        raise ValueError('Legacy synchronous comparison admits only noise=none; no adaptive rescue')

def validate(a,row):
    validate_literal(row)
    from capacidades import percepcion_cruda_fi01 as perception
    if int(a.world.runtime.dimension)!=67 or perception.get(a)['level']!=128:
        raise ValueError('The inherited N67 FI128 profile is required; never install or reset it silently')

def _declare_noise_apparatus(a,raw0):
    """Fixed legal interfaces only, never writes RAW/clocks or clears a site.

    All three noise conditions declare the same two channels, so active/sham/
    guarded differ in admitted pulses rather than availability of an interface.
    noise=none adds neither channel and remains the exact baseline extraction.
    """
    from capacidades import percepcion_cruda_fi01 as perception
    specs=[{'name':RAW_NOISE_CHANNEL,'site':list(raw0['site']),'direction':list(raw0['direction']),'state':1,'semantic':1},
           {'name':SHAM_NOISE_CHANNEL,'site':list(SHAM_SITE),'direction':list(SHAM_DIRECTION),'state':SHAM_STATE,'semantic':1}]
    present={interface.name for interface in a.world.interfaces};result=[]
    for spec in specs:
        pre=perception.observe(a,spec['site'])
        existed=spec['name']in present
        perception.declare(a,spec['name'],spec['site'],spec['direction'],state=spec['state'],semantic=1)
        result.append({**spec,'already_declared':existed,'pre_observation':pre,
                       'pre_RAW_is_zero':int(pre['raw'])==0,'site_not_cleared_or_rewritten':True})
    return result

def _submit_declared_noise(a,job,condition):
    from capacidades import percepcion_cruda_fi01 as perception
    raw0=job['noise_plan_auditor_environment_only']['raw_component0_source']
    scheduled=int(raw0['scheduled_submit_tick']);apparatus=_declare_noise_apparatus(a,raw0)
    request=None
    if condition=='active':
        request=perception.submit(a,RAW_NOISE_CHANNEL,raw0['site'],raw0['direction'],scheduled,NOISE_LOAD)
    elif condition=='sham':
        # The same submit-tick convention is used. Effective admission and its
        # actual clock are checked from receipts, not asserted from the plan.
        # This source was already declared with its exact experimental state.
        # perception.submit would redeclare defaultstate1 and reject600001.
        receipt=a.world.submit(SHAM_NOISE_CHANNEL,NOISE_LOAD,scheduled)
        request={'id':int(receipt.id),'port':SHAM_NOISE_CHANNEL,'site':list(SHAM_SITE),'direction':list(SHAM_DIRECTION),'tick':scheduled,'payload':NOISE_LOAD}
    elif condition!='guarded':raise ValueError('Noise diagnostic condition not admitted')
    return {'condition':condition,'apparatus':apparatus,'scheduled_submit_tick':scheduled,
            'request':request,'requested_noise_events':0 if request is None else 1,
            'load_per_requested_event':None if request is None else NOISE_LOAD,
            'raw0_frame_request_id':raw0['receipt_id'],'noise_submitted_after_entire_FI_frame_was_scheduled':True,
            'same_scheduled_tick_as_raw0':True,'guarded_is_prepared_closed_valve':condition=='guarded',
            'no_learned_regulation_attributed':True,'sham_state_differs_from_active':True,
            'dose_limit':'Active and sham each request one payload7 pulse at the same declared submit tick; their prepared state fields differ(1 versus600001). Do not claim fully matched material dose or effective arrival until receipts are inspected.'}

def dispatch(a,row,*,directory=None,actuator='closed'):
    """Execute only the frozen developmental literal; no automatic retry.

    The owning NativeWorld calls before_mutation/checkpoint and preserves failed
    futures. This function performs a diagnostic, not a resource action, and
    does not alter the operator's current life pointer or external environment.
    """
    validate(a,row)
    if actuator not in ('closed','nulled'):raise ValueError('Undeclared actuator flag')
    from app.native_tools import physical
    from capacidades import percepcion_cruda_fi01 as perception
    from capacidades import acceso_eci01 as access
    before=physical(a.world,occupation=True);started=int(a.tick)
    module_source={'file':Path(__file__).name,'sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    if not row['asincrono']:
        result=access.balance(a,row['izquierda'],row['derecha'])
        return {'version':VERSION,'condition':dict(row),'implementation':'existing synchronous acceso_eci01.balance',
                'before':before,'after':physical(a.world,occupation=True),'early_physical_choice':result['early_physical_choice'],
                'early_observation':result['early_observation'],'early_tick':result['early_tick'],
                'legacy_q6_choice':result['old_q6_choice'],'NULL_is_not_zero':True,'native_trial':result,
                'all_FI_receipts':result['all_material_receipts'],'noise_requests':[],'noise_admission':None,
                'no_resource_actuation_or_target_evaluation':True,'source':module_source,
                'scope':'Developmental technical comparison only; not a new independent acquisition or an adaptive guard.'}
    from capacidades import fi_async_R03 as async_fi
    job=async_fi.start(a,row['izquierda'],row['derecha'])
    noise=None
    if row['ruido']!='none':noise=_submit_declared_noise(a,job,row['ruido'])
    if int(a.tick)!=started:raise RuntimeError('FI scheduling changed time unexpectedly; preserve pending frame, no retry')
    early_events=[]
    for tick in range(started+1,job['end_tick']+1):
        a.run_until(tick)
        event=async_fi.observe_at_tick(a,job)
        if event is not None:early_events.append(event)
    trial=async_fi.finish(a,job)
    noise_requests=[]
    if noise is not None and noise['request']is not None:
        noise_requests=perception.receipts(a,[noise['request']])
    if noise is not None:noise['final_receipts']=noise_requests
    # Status counts are admission denominators, never a cognitive verdict.
    statuses=[item['receipt']['status']for item in trial['requests']+noise_requests]
    denominators={'requested':len(statuses),'applied':sum(status=='applied'for status in statuses),
                  'rejected':sum(status.startswith('rejected')for status in statuses),
                  'other_statuses':[status for status in statuses if status!='applied'and not status.startswith('rejected')]}
    return {'version':VERSION,'condition':dict(row),'implementation':'owner-advanced fi_async_R03 extraction',
            'before':before,'after':physical(a.world,occupation=True),'early_physical_choice':trial['early_physical_choice'],
            'early_observation':trial['early_observation'],'early_tick':trial['early_tick'],
            'legacy_q6_choice':trial['reader']['choice'],'NULL_is_not_zero':True,
            'native_trial':trial,'early_events':early_events,'all_FI_receipts':trial['requests'],
            'noise_requests':noise_requests,'noise_admission':noise,'denominators':denominators,
            'finished_job':job,'no_resource_actuation_or_target_evaluation':True,'source':module_source,
            'scope':'Unscored developmental admission/reader contrast. active tests another legal pulse at the same raw0 site/direction/state and submit tick after FI scheduling; guarded omits it through a prepared valve. Neither is learned regulation. No direct RAW/clock edits or fallback reader.'}
