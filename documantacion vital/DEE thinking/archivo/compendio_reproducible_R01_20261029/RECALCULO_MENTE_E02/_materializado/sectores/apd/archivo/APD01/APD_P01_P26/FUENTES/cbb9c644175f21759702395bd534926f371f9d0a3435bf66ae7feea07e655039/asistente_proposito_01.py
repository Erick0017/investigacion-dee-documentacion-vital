"""APD01 candidate in the existing lived world, not a host semantic solver.

Forms encode arbitrary cues. The fixed physical lexical emission selects a
prepared operation; another acquired native emission selects the procedure.
The inline calculator is explicitly EXTERNAL and is never called on native
trials. Outcome wiring is prepared credit assignment, not general regulation.
"""
from pathlib import Path
import hashlib,time
from dee_thinking.persistence import encode_metadata,decode_metadata
from app.native_tools import physical
from capacidades import mente_unificada_01 as mu
from capacidades import lexico_apd_01 as lex
from capacidades import lexico_apd_extendido_02 as lex2
from capacidades import aritmetica_apd_01 as arithmetic

KEY='DEE.Cognitive.System.1.1.APD01.assistant.R01'
VERSION='APD01.shared_world.R02.common_lexical_reader'
DEFAULT_ENV={'precios':[5,1],'demora':[0,2],'disponibilidad':[True,True],'presupuesto':2}
def get(a):
    mu.get(a);lex.get(a)
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:raise ValueError('Explicit APD admission required; no silent new individual or teaching')
    return decode_metadata(entries[KEY])
def save(a,m):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m))
def state(a):
    m=get(a)
    return {'version':VERSION,'physical':physical(a.world),'operational':m['environment'],
            'admitted_forms':list(lex.FORMS)+(list(lex2.NEW_FORMS)if lex2.KEY in dict(a.world.runtime.snapshot_metadata_entries)else []),
            'external_uncertain':m.get('external_uncertain'),
            'prepared_operation_domain':'two exact integers0..32, SUM0..64, affine DIFF−32..32',
            'assistance':'fixed form codec and gates, native operator tree, output conversion, consequence wiring and operator initiative; not learned general arithmetic or free Spanish'}
def validate_literal(a,row):
    get(a)
    if row.get('modo') in ('apd','apd-docencia'):
        known=(*lex.FORMS,*lex2.NEW_FORMS)if lex2.KEY in dict(a.world.runtime.snapshot_metadata_entries)else tuple(lex.FORMS)
        if row.get('texto')not in known:raise ValueError('Unknown physical form outside admitted channel domain; no meaning or correct-route lookup')
    return True
def admit(a):
    mu.get(a);lex.get(a)
    if KEY in dict(a.world.runtime.snapshot_metadata_entries):raise ValueError('Already admitted; no resetting environmental history')
    m={'version':VERSION,'admitted_tick':int(a.tick),'environment':dict(DEFAULT_ENV),
       'episodes':0,'external_calls':0,'external_uncertain':None,
       'outcome_wiring':'Two zero contacts for an actual costly/noncompleted action: native action returns viaB; external/help viaA. Prepared action-specific credit assignment; never a computed optimal route.',
       'answer_or_correct_route_stored':False}
    save(a,m);return state(a)
def configure(a,configuration):
    m=get(a)
    if set(configuration)!={'precios','demora','disponibilidad','presupuesto'}:raise ValueError('Exact environmental law fields required')
    for field in ('precios','demora'):
        if not isinstance(configuration[field],list)or len(configuration[field])!=2 or any(type(x)is not int or not 0<=x<=4096 for x in configuration[field]):raise ValueError('Two bounded integers for each native/external price and simulated tick delay')
    if not isinstance(configuration['disponibilidad'],list)or len(configuration['disponibilidad'])!=2 or any(type(x)is not bool for x in configuration['disponibilidad']):raise ValueError('Two actual availability flags')
    if type(configuration['presupuesto'])is not int or not 0<=configuration['presupuesto']<=4096:raise ValueError('Bounded modeled task budget')
    before=m['environment'];m['environment']=configuration;save(a,m)
    return {'kind':'explicit_environment_change','before':before,'after':configuration,'native_ticks':0,'not_a_learned_policy':True}
def teach(a,text,sign,revision=False):
    get(a)
    if text in lex2.NEW_FORMS:return lex2.teach(a,text,sign,revision=revision)
    return lex.teach(a,text,sign,revision=revision)
def external_calculator(command,left,right):
    """Declared external tool. Its arithmetic is never native computation."""
    start=time.perf_counter()
    if command==1:value=left+right
    elif command==-1:value=left-right
    else:raise ValueError('No formed operator request')
    return {'tool':'bounded_inline_external_calculator.R01','value':value,
            'host_wall_seconds':time.perf_counter()-start,'not_a_DEE_operation':True}
def execute(a,texto,operandos,directory,*,actuator='closed',feedback='real',detailed=False):
    m=get(a)
    if texto not in (*lex.FORMS,*lex2.NEW_FORMS):raise ValueError('Unknown physical form; no semantic parser or alias fallback')
    if not isinstance(operandos,list)or len(operandos)!=2 or any(type(x)is not int or not 0<=x<=32 for x in operandos):raise ValueError('Two raw operands0..32')
    if actuator not in ('closed','nulled')or feedback not in ('real','omit'):raise ValueError('Frozen actuator and consequence modes')
    if m.get('external_uncertain'):raise ValueError('Uncertain external effect requires explicit review; no retry')
    start=time.perf_counter();before=physical(a.world)
    if lex2.KEY in dict(a.world.runtime.snapshot_metadata_entries):word=lex2.query(a,texto,detailed=detailed)
    else:word=lex.query(a,texto,detailed=detailed)
    command=word['reader']['formed_native_command']
    route=mu.use(a,detail=detailed) if command in (-1,1) else None
    choice=route['reader']['choice'] if route else None
    env=dict(m['environment']);numeric=None;native=None;tool=None;result_use=None;artifact=None
    procedure='native' if choice==-1 else ('external' if choice==1 else ('material_help_external' if choice==0 else None))
    index=0 if choice==-1 else 1
    formed=command in (-1,1) and choice in (-1,0,1)
    available=formed and env['disponibilidad'][index]
    if available and actuator=='closed':
        if choice==-1:
            native=arithmetic.native_pair(a,'suma' if command==1 else 'diferencia',*operandos,detailed=detailed)
            numeric=native['numeric_reader']['numeric_result']
        else:
            m['external_uncertain']={'stage':'before_inline_tool','native_command':command,'operands':operandos,'tick':int(a.tick)};save(a,m)
            tool=external_calculator(command,*operandos);m['external_calls']+=1
            numeric=tool['value'];m['external_uncertain']=None;save(a,m)
        delay=env['demora'][index]
        if delay:a.run_until(int(a.tick)+delay)
        if numeric is not None:
            # A fixed affine unit conversion carries the actual result back.
            # No expected result or optimal command is computed here.
            result_use=mu.current(a,numeric+32,detail=detailed)
            emission=result_use['reader']['choice']
            if emission in (-1,0,1):
                folder=Path(directory);folder.mkdir(parents=True,exist_ok=True)
                path=folder/('apd_action_'+str(m['episodes']+1)+'.bin')
                payload=bytes([165 if emission==1 else (90 if emission==-1 else 0)])*(numeric+32)
                with path.open('xb') as f:f.write(payload)
                actual=path.read_bytes()
                artifact={'name':path.name,'bytes':len(actual),'sha256':hashlib.sha256(actual).hexdigest(),'native_actuator':emission,
                          'conversion':'Physical scalar result+32 determines bounded output length; physical post-result direction selects fixed byte. Host writes only synthetic files.'}
    completed=artifact is not None
    price=env['precios'][index] if formed else None
    costly=bool(formed and price>env['presupuesto'])
    returns=[]
    if formed and feedback=='real' and (costly or not completed):
        # Fixed environment return wiring, contingent on the action actually
        # emitted, not a policy that identifies the best available route.
        side='B' if choice==-1 else 'A'
        returns=[mu.experience(a,side),mu.experience(a,side)]
    m['episodes']+=1;save(a,m)
    return {'kind':'APD01_integrated_request','literal_form':texto,'raw_operands':operandos,
            'before':before,'word':word,'route':route,'native_operator_command':command,
            'native_route_command':choice,'procedure':procedure,'environment':env,
            'available':available,'native_numeric':native,'external_tool':tool,'numeric_result':numeric,
            'result_material_use':result_use,'artifact':artifact,'completed':completed,
            'modeled_price':price,'costly':costly,'outcome_returns':returns,
            'actuator_mode':actuator,'feedback_mode':feedback,'after':physical(a.world),
            'elapsed_host_seconds':time.perf_counter()-start,
            'attribution':'Acquired cue content and relative-reference route are native; anatomy, codecs, generic resources, actuation, credit-assignment wiring and opportunity initiative are prepared. Causal policy learning requires paired controls.'}
