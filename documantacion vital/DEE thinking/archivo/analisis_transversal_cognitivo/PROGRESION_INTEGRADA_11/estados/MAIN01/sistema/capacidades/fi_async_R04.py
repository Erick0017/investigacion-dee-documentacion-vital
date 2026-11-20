"""PI02 experimental asynchronous FI128 access, extracted from existing code.

This module never advances Native time. Its owner schedules a frame with start,
calls observe_at_tick at each actually reached tick, and calls finish at the
exact recorded end_tick. The owner must checkpoint the JSON job and the whole
world together. There is no callback, external policy, target or answer table.

R04 only defers future input scheduling by an explicit prepared hardware delay.
The real started/last-observed tick is unchanged; no clocks are edited.
This extraction is NOT validated merely by matching the source text. Root must
compare complete control continuations with the legacy synchronous access.
"""
from pathlib import Path
import hashlib,json

VERSION='PI02.FI128.asynchronous_access.R04'
BASE_EXTRACTION_SHA256='370aecc46ff0f87e6670ff99e94790561b153d9211ca6ad784b6baad25ec46b5'
N=67;LEVEL=128;BIAS=20
REFERENCE_SOURCES={
    'percepcion_cruda_fi01.py':{'sha256':'0fb2e1f88ab1a6aedea2784791509b4e0a42fb94fdf15491f7b79596af6c3390','functions':['frame','submit','receipts','geometry']},
    'acceso_eci01.py':{'sha256':'33bee08fc31f30616180e0747721cd75aeaf8f6a97ec095c32eef53978000bfb','functions':['balance','decode_emission','_read_E']},
    'acciones_nativas_apd04.py':{'sha256':'f0fb1a3616c668d48bee8865956f12bd6c53367b7b2062a9a33f6ff966bf3f3a','functions':['balance'],'role':'Source of fixed independent operand codec; not called by this extraction.'}
}

def _modules():
    from capacidades import percepcion_cruda_fi01 as perception
    from capacidades import mente_unificada_01 as mu
    from capacidades import selector_acrecion_nativo as selector
    from capacidades import acceso_eci01 as access
    return perception,mu,selector,access

def _sources(perception,mu,selector,access):
    result=[]
    for module in (perception,access,mu,selector):
        path=Path(module.__file__);actual=hashlib.sha256(path.read_bytes()).hexdigest()
        reference=REFERENCE_SOURCES.get(path.name)
        if reference and actual!=reference['sha256']:
            raise ValueError('FI async source changed; declare another extraction revision before use: '+path.name)
        result.append({'module':path.name,'path':str(path),'sha256':actual,'pinned_reference':reference is not None})
    return result

def start(a,left,right,*,start_delay=0):
    """Schedule exactly the inherited FI128 codec/query, with no time advance.

    Left and right are independent public loads. The only transformation is
    component0=left, component1=20-right, remaining126 material components0.
    No sum, useful action or expected sign is calculated here.
    """
    if type(start_delay)is not int or start_delay<0:
        raise ValueError('Declared hardware start_delay must be an exact nonnegative integer; no clock edit or hidden catch-up')
    if any(type(v)is not int or not 0<=v<=BIAS for v in (left,right)):
        raise ValueError('Two independent literal integer loads0..20 required')
    perception,mu,selector,access=_modules()
    sources=_sources(perception,mu,selector,access)
    m=perception.get(a)
    if int(a.world.runtime.dimension)!=N or m['level']!=LEVEL:
        raise ValueError('Only the inherited N67 FI128 preparation is admitted')
    if not mu.get(a).get('current_frontend'):
        raise ValueError('The existing common six-class frontend is required; no implicit installation')
    from app.native_tools import physical
    g=perception.geometry(LEVEL)
    components=[0]*LEVEL;components[0]=left;components[1]=BIAS-right
    started=int(a.tick);before=physical(a.world)
    leaf=started+start_delay+2;root=leaf-g['raw_relative_tick'];datum=root+38
    timing=mu.query_timing(a,int(datum-3));shift=timing['wait_ticks']
    leaf+=shift;root+=shift;datum+=shift;q=timing['effective_query_tick']
    points={'E':list(perception.E),'S':list(perception.S),'A':[14,14,15],'B':[16,14,15],'C':list(g['remote_aggregate_site'])}
    datum_pre=perception.observe(a,perception.S)
    refs_pre=[perception.observe(a,p)for p in ((14,14,15),(16,14,15))]
    raw0=next(s for s in g['raw_sources']if s['component_index']==0)
    raw0_before=perception.observe(a,raw0['site'])
    requests=[];raw0_request=None
    for s in g['raw_sources']:
        request=perception.submit(a,'MU.raw.L'+str(LEVEL)+'.'+s['id'],s['site'],s['direction'],root+s['injection_tick_relative'],components[s['component_index']])
        requests.append(request)
        if s['component_index']==0:raw0_request=dict(request)
    for s in g['generic_sources']:
        requests.append(perception.submit(a,'MU.raw.L'+str(LEVEL)+'.'+s['id'],s['site'],s['direction'],root+s['injection_tick_relative'],0))
    requests.extend(selector.query(a.world,q,5,'MU.selector'))
    if int(a.tick)!=started:raise RuntimeError('Async submission unexpectedly advanced Native time; preserve reached state')
    job={'schema':'PI02.FI128.async_job.R04','version':VERSION,'phase':'active','started_tick':started,'start_delay':start_delay,'base_extraction_sha256':BASE_EXTRACTION_SHA256,'before':before,
         'raw_components':components,'public_independent_loads':[left,right],'level':LEVEL,'input_tick':leaf,'root_tick':root,'datum_tick':datum,
         'query_tick':q,'early_read_tick':q+4,'legacy_read_tick':q+6,'end_tick':q+8+2*N,'timing':timing,
         'requests':requests,'raw_request_count':len(g['raw_sources']),'generic_source_count':len(g['generic_sources']),
         'perception_counters_before':{key:m[key]for key in ('frames','raw_requests','generic_requests')},
         'points':points,'frame_ticks':sorted({datum-2,datum-1,datum,datum+1,q+6,q+8}),'frames':[],
         'last_observed_tick':started,'early_observation':None,'early_choice':None,'early_event_delivered':False,
         'legacy_reader':None,'datum_pre':datum_pre,'references_pre':refs_pre,'source_modules':sources,
         'reader_contract':'FixedE atq+4 through unchanged acceso_eci01.decode_emission; q+6 is legacy diagnostic only, never a fallback.',
         'noise_plan_auditor_environment_only':{
             'raw_component0_source':{'id':raw0['id'],'component_index':0,'site':list(raw0['site']),'direction':list(raw0['direction']),
                                      'port':raw0_request['port'],'scheduled_submit_tick':raw0_request['tick'],'receipt_id':raw0_request['id']},
             'pre_source_observation':raw0_before,'pre_source_RAW_is_zero':int(raw0_before['raw'])==0,
             'generic_frame_input_tick':leaf,'native_query_tick':q,'early_read_tick':q+4,'declared_hardware_start_delay':start_delay,
             'tick_convention':'Scheduled tick is the literal argument to OrganizationalWorld.submit; effective admission is read from its final receipt, never guessed.',
             'scope':'For a separately frozen exogenous environmental perturbation protocol. No noise is injected by this module. No target or decoded action may choose its dose or port.'},
         'scope':'Experimental scheduling decomposition, not newly learned perception/reader/initiative or regulation. All128zero/nonzero raw inputs and generic query resources remain material.'}
    json.dumps(job,ensure_ascii=False,allow_nan=False)
    return job

def observe_at_tick(a,job):
    """Record only the current physical tick; return q+4 emission once, orNone.

    The owner advances through OrganizationalWorld.run_until. A skipped fixed
    milestone is an error, never grounds to search another reader/window.
    """
    if job.get('version')!=VERSION or job.get('phase')!='active':raise ValueError('An active declared FI async job is required')
    perception,mu,selector,access=_modules()
    t=int(a.tick);previous=job['last_observed_tick']
    if t<previous:raise ValueError('No time reversal in async observation')
    if t>job['end_tick']:raise ValueError('Async end horizon passed without finalization; preserve the future')
    if t==previous:return None
    milestones=set(job['frame_ticks'])|{job['early_read_tick'],job['legacy_read_tick']}
    missed=sorted(x for x in milestones if previous<x<t)
    if missed:raise ValueError('Fixed FI reader/frame boundary skipped: '+repr(missed))
    if t in job['frame_ticks']:
        job['frames'].append({'tick':t,'fields':{name:perception.observe(a,p)for name,p in job['points'].items()}})
    event=None
    if t==job['early_read_tick']:
        # Same physical read and exact RAW/clock cross-check as the original
        # EarlyAdapter. The decoder receives only that observation, not operands.
        observation=access._read_E(a)
        choice=access.decode_emission(observation)
        job['early_observation']=observation;job['early_choice']=choice
        if job['early_event_delivered']:raise ValueError('Early event already delivered; no second action')
        job['early_event_delivered']=True
        event={'kind':'FI128_fixed_q4_emission','version':VERSION,'tick':t,'query_tick':job['query_tick'],
               'physical_choice':choice,'valid_emission':choice is not None,'observation':observation,
               'NULL_is_not_zero':True,'operands_or_reference_in_decoder':False,
               'scope':'A formed emission event; the fixed external actuator, if any, belongs to its separate environment contract.'}
    if t==job['legacy_read_tick']:job['legacy_reader']=mu.current_read(a)
    if int(a.tick)!=t:raise RuntimeError('Observer advanced Native time; preserve exact future')
    job['last_observed_tick']=t
    return event

def finish(a,job):
    """Finalize at exactq+8+2N, update inherited frame counters once; noadvance."""
    if job.get('version')!=VERSION or job.get('phase')!='active':raise ValueError('Only an unfinished declared FI async job may finish')
    if int(a.tick)!=job['end_tick']:raise ValueError('Finish requires the exact frozen FI end_tick; do not advance or rewind inside the adapter')
    if not job['early_event_delivered'] or job['early_observation'] is None or job['legacy_reader'] is None:
        raise ValueError('The frozen early/legacy read was not recorded; no fallback')
    if [frame['tick']for frame in job['frames']]!=job['frame_ticks']:
        raise ValueError('Legacy fixed frame coverage incomplete; no reconstruction of missed states')
    perception,mu,selector,access=_modules()
    from app.native_tools import physical
    m=perception.get(a)
    for key,before in job['perception_counters_before'].items():
        if m[key]!=before:raise ValueError('Concurrent FI operation changed counters; one admitted FI job at a time')
    m['frames']+=1;m['raw_requests']+=job['raw_request_count'];m['generic_requests']+=job['generic_source_count']+3
    perception.save(a,m)
    result={'kind':'native_joint_raw_perception','version':perception.VERSION,'async_version':VERSION,'level':LEVEL,
            'raw_components':job['raw_components'],'input_tick':job['input_tick'],'all_components_same_tick':True,
            'datum_tick':job['datum_tick'],'query_tick':job['query_tick'],'read_tick':job['legacy_read_tick'],'timing':job['timing'],
            'reader':job['legacy_reader'],'early_physical_choice':job['early_choice'],'early_observation':job['early_observation'],'early_tick':job['early_read_tick'],
            'before':job['before'],'after':physical(a.world,occupation=True),'datum_pre':job['datum_pre'],
            'datum_after':perception.observe(a,perception.S),'references_pre':job['references_pre'],
            'references_after':[perception.observe(a,p)for p in ((14,14,15),(16,14,15))],
            'requests':perception.receipts(a,job['requests']),'frames':job['frames'],'minimum_passive_horizon_ticks':2*N,
            'source_modules':job['source_modules'],'NULL_is_not_zero':True,'noise_injected_here':False,
            'scope':'Same prepared FI128 codec and fixed q4 transducer split across an existing owner. Physical equivalence/use must be checked against complete synchronous controls before any incorporation claim.'}
    if int(a.tick)!=job['end_tick']:raise RuntimeError('Async finish advanced Native time')
    job['phase']='completed';job['finished_tick']=int(a.tick)
    json.dumps(result,ensure_ascii=False,allow_nan=False)
    return result
