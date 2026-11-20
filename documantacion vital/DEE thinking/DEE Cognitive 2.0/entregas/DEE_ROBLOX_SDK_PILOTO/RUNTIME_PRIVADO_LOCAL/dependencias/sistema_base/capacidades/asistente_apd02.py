"""APD02 integrated, bounded assistant. No host route or answer selection.

The fixed verifier acts only after a terminal selected effect. Its private
reference remains in the audit report; only one generic consequence category
is projected to the native learner. All real files are synthetic and local.
"""
from pathlib import Path
import time
from dee_thinking.persistence import encode_metadata,decode_metadata
from app.native_tools import physical
from capacidades import asistente_proposito_01 as prior
from capacidades import aritmetica_apd_01 as arithmetic
from capacidades import ruta_adquirida_apd_03 as legacy_route
from capacidades import lexico_apd02_01 as words
from capacidades import evaluador_calidad_apd02 as quality
from capacidades import proveedores_prueba_apd02 as effects
from capacidades import acumulador_recirculante_apd02 as accumulator

KEY='DEE.Cognitive.System.1.1.APD02.assistant.R01'
VERSION='APD02.quality_and_continuity.R04.goal_and_native_trace'
DEFAULT_ENV={'precios':[1,5],'demora':[0,0],'disponibilidad':[True,True],'fallos':['none','none'],'presupuesto':2,'demora_maxima':8}
FAULTS={'none':{},'wrong_value':{'wrong_value_delta':1},'filesystem':{'fail_before_write':True},'invalid_json':{'corrupt_json':True}}

def save(a,m):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m))
def get(a):
    prior.get(a);e=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in e:raise ValueError('Explicit APD02 admission required; no silent new body or knowledge')
    return decode_metadata(e[KEY])
def state(a):
    m=get(a)
    references=native_learner(m).refs(a)if m['route_protocol']in('APD02.delayed_action_trace.R03','APD02.delayed_action_trace.R04')else None
    return{'version':VERSION,'physical':physical(a.world),'operational_environment':m['environment'],'route_protocol':m['route_protocol'],'route_references_passive':references,'external_uncertain':m.get('external_uncertain'),'goal_progress':m.get('goal_pending',{}).get('progress'),'new_lexical_forms':list(words.NEW_FORMS),'scope':'Prepared anatomy, codecs, comparator, arithmetic tree, generic maintenance, file writer and post-action quality verifier. Acquired content and subsequent choices require the recorded physical controls, not this metadata.'}

def admit(a,*,route_protocol='legacy_common_quality'):
    prior.get(a)
    if KEY in dict(a.world.runtime.snapshot_metadata_entries):raise ValueError('Already admitted; do not reset')
    if route_protocol!='legacy_common_quality':raise ValueError('New route mechanism requires separate validated admission, not a favorable silent switch')
    before=physical(a.world);lex=words.prepare(a);renew=accumulator.admit(a)
    m={'version':VERSION,'admitted_tick':a.tick,'episodes':0,'environment':dict(DEFAULT_ENV),'route_protocol':route_protocol,'external_uncertain':None,'correct_answers_or_preferred_routes_stored':False,'quality_return':'Fixed SUCCESS/FAILURE category after committed action; common route resource never contains the correct value or route.'}
    save(a,m);return{'kind':'explicit_APD02_system_admission','before':before,'language_preparation':lex,'accumulator_access_preparation':renew,'state':state(a),'preparation_is_not_new_learning':True}

def validate_environment(cfg):
    if not isinstance(cfg,dict)or set(cfg)!=set(DEFAULT_ENV):raise ValueError('Exact declared environmental fields required; no hidden block/target')
    for field,maximum in(('precios',28),('demora',4096)):
        if not isinstance(cfg[field],list)or len(cfg[field])!=2 or any(type(v)is not int or not 0<=v<=maximum for v in cfg[field]):raise ValueError('Two bounded exact environmental values')
    if not isinstance(cfg['disponibilidad'],list)or len(cfg['disponibilidad'])!=2 or any(type(v)is not bool for v in cfg['disponibilidad']):raise ValueError('Two actual provider availability flags')
    if not isinstance(cfg['fallos'],list)or len(cfg['fallos'])!=2 or any(v not in FAULTS for v in cfg['fallos']):raise ValueError('Two declared synthetic provider faults')
    if cfg['presupuesto']!=2 or type(cfg['presupuesto'])is not int or type(cfg['demora_maxima'])is not int or not 0<=cfg['demora_maxima']<=4096:raise ValueError('Frozen price budget2 and bounded delay ceiling')
    return True
def configure(a,cfg):
    validate_environment(cfg);m=get(a)
    if m['route_protocol']!='legacy_common_quality'and max(cfg['demora'])>256:raise ValueError('Delayed native action trace supports at most256 extra ticks; do not miss its physical consequence window')
    before=m['environment'];m['environment']=cfg;save(a,m)
    return{'kind':'explicit_environment_change','before':before,'after':cfg,'new_native_ticks':0,'not_a_native_strategy_selection':True}

def upgrade_route(a):
    m=get(a)
    from capacidades import ruta_adaptativa_apd02_01 as learner
    if m['route_protocol']!='legacy_common_quality'or learner.KEY in dict(a.world.runtime.snapshot_metadata_entries):raise ValueError('No duplicate preparation, learned-state transplant or favorable reseed')
    before=physical(a.world);preparation=learner.prepare(a)
    m['prior_route_protocol']=m['route_protocol'];m['route_protocol']=learner.VERSION
    m['route_admitted_tick']=a.tick;save(a,m)
    return{'kind':'explicit_P0_delayed_native_route_admission','before':before,'preparation':preparation,'state':state(a),'seed_experience':None,'not_spontaneous_growth_or_transferred_choice':True}

def upgrade_route04(a):
    m=get(a)
    from capacidades import ruta_adaptativa_apd02_04 as learner
    if m['route_protocol']not in('legacy_common_quality','APD02.delayed_action_trace.R03')or learner.KEY in dict(a.world.runtime.snapshot_metadata_entries):raise ValueError('No duplicate R04 anatomy or silent favorable reset')
    before=physical(a.world);preparation=learner.prepare(a)
    m.setdefault('route_protocol_history',[]).append({'version':m['route_protocol'],'last_tick_before_external_new_anatomy':before['tick'],'preserved_not_erased':True})
    m['route_protocol']=learner.VERSION;m['route_admitted_tick']=a.tick;save(a,m)
    return{'kind':'explicit_R04_anatomical_reconnection','before':before,'preparation':preparation,'state':state(a),'seed_experience':None,'prior_body_and_adverse_future_preserved':True,'not_native_self_growth':True}

def native_learner(m):
    if m['route_protocol']=='APD02.delayed_action_trace.R03':
        from capacidades import ruta_adaptativa_apd02_01 as learner
    elif m['route_protocol']=='APD02.delayed_action_trace.R04':
        from capacidades import ruta_adaptativa_apd02_04 as learner
    else:raise ValueError('No delayed trace contract in this exact life; no alternative chosen by expected answer')
    return learner

def validate(a,row):
    mode=row.get('modo')
    if mode=='apd02-admitir':
        prior.get(a)
        if KEY in dict(a.world.runtime.snapshot_metadata_entries):raise ValueError('Already admitted')
        return True
    get(a)
    if mode=='apd02-ruta04-admitir':
        if get(a)['route_protocol']not in('legacy_common_quality','APD02.delayed_action_trace.R03'):raise ValueError('R04 already admitted or outside domain')
    elif mode=='apd02-ruta-admitir':
        if get(a)['route_protocol']!='legacy_common_quality':raise ValueError('New route already admitted; no resetting')
    elif mode=='apd02':
        if row['texto']not in prior.admitted_forms(a):raise ValueError('Unknown mathematical cue; no semantic guess')
    elif mode=='apd02-ambiente':
        validate_environment(row['configuracion'])
        if get(a)['route_protocol']!='legacy_common_quality'and max(row['configuracion']['demora'])>256:raise ValueError('Delayed action-trace domain: extra provider delay0..256ticks')
    elif mode in('apd02-docencia','apd02-lenguaje'):
        if row['texto']not in words.NEW_FORMS:raise ValueError('Unprepared new language cue')
    elif mode=='apd02-acumular':accumulator.get(a)
    elif mode=='apd02-componer':
        if any(f not in prior.admitted_forms(a)for f in row['formas']):raise ValueError('Unknown acquired math cue')
    elif mode in('apd02-meta','apd02-meta-iniciar','apd02-meta-paso'):
        m=get(a)
        if m['route_protocol']!='APD02.delayed_action_trace.R04':raise ValueError('Goal apparatus requires the explicit R04 route domain; no failed R03 substituted')
        pending=m.get('goal_pending')
        if mode=='apd02-meta-paso':
            if not pending or pending['progress']['verified_file_goal_completed']or pending['progress']['opportunities_used']>=4 or pending['progress']['uncertain_effect']is not None:raise ValueError('No exact continuing unfinished goal')
        else:
            if row['texto']not in prior.admitted_forms(a):raise ValueError('Only an existing literal mathematical cue')
            if pending and not pending['progress']['verified_file_goal_completed']and pending['progress']['opportunities_used']<4:raise ValueError('A real goal remains pending; do not replace its facts')
    else:raise ValueError('Unknown APD02 mode')
    return True

def _route(a,m):
    if m['route_protocol']=='legacy_common_quality':return legacy_route.use(a)
    learner=native_learner(m)
    return learner.use(a)
def _return(a,m,category,feedback):
    if m['route_protocol']=='legacy_common_quality':
        return legacy_route.return_cost(a,0 if category=='SUCCESS'else 3,mode='real'if feedback=='real'else'omit')
    learner=native_learner(m)
    return learner.consequence(a,category,mode='real'if feedback=='real'else'omit')

def execute(a,text,operands,directory,*,feedback='real',actuator='closed',detailed=False):
    m=get(a)
    if text not in prior.admitted_forms(a)or not isinstance(operands,list)or len(operands)!=2 or any(type(v)is not int or not 0<=v<=32 for v in operands):raise ValueError('Literal admitted mathematical cue and two raw operands0..32 required')
    if feedback not in('real','omit')or actuator not in('closed','nulled'):raise ValueError('Declared feedback and actuator only')
    if m.get('external_uncertain'):raise ValueError('Uncertain effect preserved; no replacement or retry')
    started=time.perf_counter();before=physical(a.world);word=words.query(a,text,detailed=detailed);command=word['reader']['formed_native_command']
    route=_route(a,m)if command in(-1,1)else None;choice=route['reader']['choice']if route else None
    # Action is physically committed before the verifier receives semantics.
    operation='add'if command==1 else'sub'if command==-1 else None
    procedure='native'if choice==-1 else'external'if choice in(0,1)else None
    env=m['environment'];folder=Path(directory);folder.mkdir(parents=True,exist_ok=False);task_id='task_'+str(m['episodes']+1)
    public={'task_id':task_id,'text':text,'operands':list(operands)};native_result=None;tool_result=None
    def native_callback(op,values):
        nonlocal native_result
        native_result=arithmetic.native_pair(a,'suma'if op=='add'else'diferencia',*values,detailed=detailed)
        return native_result['numeric_reader']['numeric_result']
    def external_callback(op,values):
        nonlocal tool_result
        tool_result=prior.external_calculator(1 if op=='add'else-1,*values)
        return tool_result['value']
    if operation is None or procedure is None or actuator=='nulled':
        committed={'task_id':task_id,'state':'no_output','selected_operation':operation,'selected_procedure':procedure,'artifact':None,'price':0,'delay_ticks':0,'provider_calls':{'native':0,'external':0},'no_silent_replacement':True}
    else:
        index=0 if procedure=='native'else 1
        m['external_uncertain']={'stage':'before_selected_effect','task_id':task_id,'tick':a.tick};save(a,m)
        committed=effects.execute_selected(public,{'operation':operation,'procedure':procedure},sandbox_root=folder,native_value_reader=native_callback,external_calculator=external_callback,law={'price':env['precios'][index],'delay_ticks':env['demora'][index],'available':env['disponibilidad'][index]},fault=FAULTS[env['fallos'][index]],synthetic_fixture=False)
        if committed['state']=='uncertain':
            m['external_uncertain']={'stage':'possible_unconfirmed_file_effect','task_id':task_id,'tick':a.tick,'preserved_effect':committed};save(a,m)
            raise RuntimeError('Unconfirmed file effect preserved; no evaluation, feedback, alternative provider or retry')
        if env['demora'][index]:a.run_until(int(a.tick)+env['demora'][index])
        m['external_uncertain']=None;save(a,m)
    committed_at=physical(a.world)
    policy={'max_operand':32,'max_artifact_bytes':4096,'max_price':env['presupuesto'],'max_delay_ticks':env['demora_maxima'],'resource_limits_required_for_success':True}
    # This function computes a private reference only AFTER the real effect;
    # no expected value, correct operator or recommended route enters DEE.
    report=quality.evaluate_literal_committed(public,committed,sandbox_root=folder,policy=policy)
    projected=quality.actor_feedback(report,binary=True);returned=_return(a,m,projected['category'],feedback)if route else None
    m['episodes']+=1;save(a,m)
    return{'kind':'APD02_quality_request','literal_form':text,'raw_operands':operands,'before':before,'word':word,'route':route,'native_operator_command':command,'native_route_command':choice,'selected_operation':operation,'selected_procedure':procedure,'environment':env,'native_numeric':native_result,'external_tool':tool_result,'committed_effect':committed,'effect_directory':str(folder),'commit_before_verification':committed_at,'quality':report,'feedback_to_participant':projected,'native_consequence':returned,'feedback_mode':feedback,'after':physical(a.world),'host_elapsed_seconds':time.perf_counter()-started,'attribution':'Native learned cue and route emissions select the sole provider. Anatomy, external calculator, real JSON writer, independent verifier, feedback transduction and opportunity initiative are prepared. Bidirectional adaptation requires actual paired controls; metadata does not certify it.'}

def compose(a,forms,data,directory,*,feedback='real',actuator='closed',detailed=False):
    if not isinstance(forms,list)or not 2<=len(forms)<=3 or len(data)!=len(forms)+1 or any(type(v)is not int or not 0<=v<=16 for v in data):raise ValueError('Bounded operator-supplied sequence only')
    value=data[0];rows=[];program=[]
    for i,form in enumerate(forms):
        if type(value)is not int or not 0<=value<=32:break
        r=execute(a,form,[value,data[i+1]],Path(directory)/('stage_'+str(i)),feedback=feedback,actuator=actuator,detailed=detailed);rows.append(r)
        program.append({'actual_operation':r['selected_operation'],'actual_procedure':r['selected_procedure'],'data_source':'actual_previous_output_and_next_literal_operand'})
        if not r['quality']['task_success']:value=None;break
        value=r['committed_effect']['used_value']
    return{'kind':'APD02_assisted_quality_sequence','rows':rows,'actual_instructions':program,'result':value if len(rows)==len(forms)else None,'scope':'Operator supplies order. Each learned cue and acquired route chooses a real primitive; actual output is transported unchanged. The fixed verifier may stop invalid work but never replaces it. Not a learned planner, syntax or tool invention.'}

def _run_goal_environment(a,m,environment,maximum,*,feedback,detailed):
    from capacidades import aparato_objetivo_apd02 as apparatus
    before=physical(a.world);m['external_uncertain']={'stage':'goal_opportunity_in_progress','tick':a.tick};save(a,m)
    try:
        r=apparatus.run_opportunities(a,environment,native_learner(m),words=words,arithmetic=arithmetic,maximum=maximum,feedback_mode='real'if feedback=='real'else'omit',detailed=detailed)
        m['goal_pending']=environment.operational_state()
        if m['goal_pending']['progress']['uncertain_effect']is not None:
            m['external_uncertain']={'stage':'uncertain_goal_effect','progress':m['goal_pending']['progress']};save(a,m)
            raise RuntimeError('Goal file effect uncertain; no feedback, alternate route or retry')
        m['external_uncertain']=None;save(a,m)
    except BaseException:
        m['goal_pending']=environment.operational_state();save(a,m);raise
    return{'kind':'APD02_native_goal_opportunities','before':before,'result':r,'after':physical(a.world),'operational_environment_state':m['goal_pending'],'assistance':'Prepared ACT/QUERY codec and opportunity loop; generic failure includes an incomplete file goal. A private raw operand is exposed only by a physically selected QUERY. No semantic missing-data perception, autonomous goal invention or learned general planner is claimed.'}

def start_goal(a,text,operands,visible,directory,*,run=False,feedback='real',detailed=False):
    m=get(a)
    if m.get('external_uncertain'):raise ValueError('Unresolved effect; no new goal')
    pending=m.get('goal_pending')
    if pending and not pending['progress']['verified_file_goal_completed']and pending['progress']['opportunities_used']<4:raise ValueError('Continue the actual goal; never replace a pending world')
    from capacidades.entorno_objetivo_apd02 import GoalEnvironment
    serial=m.get('goal_serial',0)+1
    environment=GoalEnvironment(task_id='goal_'+str(serial),text=text,left=operands[0],second=operands[1],second_initially_public=visible,directory=Path(directory)/'world',quality=quality,effects=effects)
    m['goal_serial']=serial;m['goal_pending']=environment.operational_state();save(a,m)
    if run:return _run_goal_environment(a,m,environment,4,feedback=feedback,detailed=detailed)
    return{'kind':'explicit_external_goal_initialization','native_ticks':0,'public_observation':environment.observation(),'progress':environment.progress(),'environment_private_setup':{'second':operands[1],'not_sent_to_native_codec_or_selector':True},'no_correct_step_list_supplied':True}

def continue_goal(a,maximum,directory,*,feedback='real',detailed=False):
    m=get(a)
    if m.get('external_uncertain')or not m.get('goal_pending'):raise ValueError('No exact unambiguous pending goal')
    from capacidades.entorno_objetivo_apd02 import restore_operational
    environment=restore_operational(m['goal_pending'],directory=Path(directory)/'world',quality=quality,effects=effects)
    return _run_goal_environment(a,m,environment,maximum,feedback=feedback,detailed=detailed)
