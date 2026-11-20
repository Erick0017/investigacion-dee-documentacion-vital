"""APD03 operational candidate; native choices, fixed sensors and real files.

No Runtime is created on import. Admission is explicit and finite. Context,
opportunity initiative, arithmetic, codec and verifier are prepared; acquired
state/choices need causal evidence from the named life, not this metadata.
"""
from pathlib import Path
from dee_thinking.persistence import encode_metadata,decode_metadata
from app.native_tools import physical
from app.protocolo_apd03 import validate_literal
from capacidades import asistente_apd02 as prior
from capacidades import asistente_proposito_01 as old_assistant
from capacidades import aritmetica_apd_01 as arithmetic
from capacidades import evaluador_calidad_apd02 as quality
from capacidades import proveedores_prueba_apd02 as effects
from capacidades import ruta_adaptativa_apd02_04 as route
from capacidades import sensor_balanceado_apd03_r02 as sensor
from capacidades import lexico_generico_apd03_r02 as words
from capacidades import mente_acumulativa_r02 as memory
from capacidades.entorno_compartido_apd03 import SharedGoalEnvironment,restore_operational

KEY='DEE.Cognitive.System.1.1.APD03.assistant.R02'
VERSION='APD03.operational_shared_goals.R02.K47_7_47.material_panel'
SENSOR_FAMILY='balanced_z_left'


def save(a,m):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m))


def get(a):
    previous=prior.get(a)
    if previous['route_protocol']!=route.VERSION:raise ValueError('Exact physically admitted R04 domain required')
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:raise ValueError('Explicit APD03 admission required; never prepare a replacement life')
    m=decode_metadata(entries[KEY])
    if m['version']!=VERSION or m['sensor_family']!=SENSOR_FAMILY:
        raise ValueError('APD03 executable contract differs; no silent codec migration')
    return m


def _old_goal_unfinished(previous):
    pending=previous.get('goal_pending')
    if not pending:return False
    p=pending['progress']
    return p['uncertain_effect']is not None or(not p['verified_file_goal_completed']and p['opportunities_used']<4)


def _environment_terminal(state):
    p=state['base_state']['progress']
    return p['verified_file_goal_completed']or p['opportunities_used']>=4 or p['uncertain_effect']is not None


def _available(a,m):
    previous=prior.get(a)
    if previous.get('external_uncertain')or _old_goal_unfinished(previous):
        raise ValueError('A previous APD02 goal/effect is pending or uncertain; do not replace it')
    if m.get('external_uncertain'):
        raise ValueError('A preserved APD03 uncertain/in-progress effect needs examination; no automatic retry')
    if route.get(a)['pending_window']is not None:
        raise ValueError('A real R04 action window is pending; never overwrite its future')


def state(a):
    m=get(a);pending=m.get('goal_pending');public=None;progress=None
    if pending:
        base=pending['base_state'];public={**base['public'],'context':pending['context']}
        progress=base['progress']
    return {'version':VERSION,'physical':physical(a.world),
        'sensor_family':m['sensor_family'],'consequence_mode':m['consequence_mode'],
        'generic_forms':list(words.NEW_FORMS),'operational_counters':m['counters'],
        'goal_public_observation':public,'goal_progress':progress,
        'external_uncertain':m.get('external_uncertain'),
        'private_environment_not_projected_to_native':True,
        'scope':'Installed possibilities do not certify learned signs, contextual policy, autonomous initiative or comprehension.'}


def admit(a,*,consequence_mode='local_useful'):
    previous=prior.get(a)
    if previous['route_protocol']!=route.VERSION:raise ValueError('APD03 requires the existing R04 body, never an automatic new route')
    if consequence_mode not in('local_useful','file_only'):raise ValueError('Frozen consequence modality required')
    if KEY in dict(a.world.runtime.snapshot_metadata_entries):raise ValueError('APD03 already admitted; no reset')
    _available(a,{'external_uncertain':None})
    if words.KEY in dict(a.world.runtime.snapshot_metadata_entries):
        raise ValueError('Generic lexical body already present without this assistant; explicit migration review required, no reinstall')
    if set(sensor.port_names(SENSOR_FAMILY))&set(a.world.runtime.channel_names):
        raise ValueError('Sensor channels already present without this assistant; no silent replacement')
    lexical_screen=words.preflight(a);sensor_screen=sensor.preflight(a,SENSOR_FAMILY)
    if not lexical_screen['admissible']or not sensor_screen['admissible']:
        raise ValueError('Complete-source preflight rejected; no clearing, alternate ports or partial installation')
    before=physical(a.world)
    lexical_preparation=words.prepare(a)
    sensor_preparation=sensor.declare(a,SENSOR_FAMILY)
    m={'version':VERSION,'admitted_tick':int(a.tick),'sensor_family':SENSOR_FAMILY,
        'consequence_mode':consequence_mode,'goal_pending':None,'external_uncertain':None,
        'counters':{'goals':0,'opportunity_invocations':0,'native_opportunities':0,'teaching':0,'language_uses':0,'material_panels':0},
        'learned_signs_banks_or_answers_in_metadata':False,
        'assistance':'Raw missing bit sensor P0, operator opportunities/context, original R04 codec, prepared native arithmetic, file writer and post-action verifier.'}
    save(a,m)
    return {'kind':'explicit_APD03_P0_admission','before':before,
        'preflight':{'lexical':lexical_screen,'sensor':sensor_screen},
        'lexical_preparation':lexical_preparation,'sensor_preparation':sensor_preparation,
        'state':state(a),'installation_is_not_new_learning':True}


def validate(a,row):
    validate_literal(row)
    if row['modo']=='apd03-panel':
        prior.get(a)
        admitted=KEY in dict(a.world.runtime.snapshot_metadata_entries)
        if row.get('nuevas',False)and not admitted:raise ValueError('New-slot panel requires explicit APD03 admission')
        _available(a,get(a)if admitted else{'external_uncertain':None})
        return True
    if row['modo']=='apd03-admitir':
        previous=prior.get(a)
        if KEY in dict(a.world.runtime.snapshot_metadata_entries):raise ValueError('Already admitted; no reset')
        if previous['route_protocol']!=route.VERSION:raise ValueError('Only the current R04 domain')
        _available(a,{'external_uncertain':None});return True
    m=get(a);_available(a,m)
    if row['modo']=='apd03-tarea-iniciar':
        if row['texto']not in old_assistant.admitted_forms(a):raise ValueError('Only a currently admitted literal mathematical cue')
        if m.get('goal_pending')and not _environment_terminal(m['goal_pending']):
            raise ValueError('Continue the same unfinished environmental task; no replacement')
        if m.get('goal_pending')and m['goal_pending']['base_state']['progress']['uncertain_effect']is not None:
            raise ValueError('Uncertain goal cannot be replaced')
    elif row['modo']=='apd03-paso':
        if not m.get('goal_pending')or _environment_terminal(m['goal_pending']):raise ValueError('No exact unfinished task to continue')
    return True


def panel(a,*,new_forms=False,memories=False,detailed=False):
    validate(a,{'modo':'apd03-panel','nuevas':new_forms,'memorias':memories})
    admitted=KEY in dict(a.world.runtime.snapshot_metadata_entries)
    before=physical(a.world);forms=[];contexts=[]
    query=words.query if admitted else prior.words.query
    for form in prior.words.FORM_CODEC:
        forms.append({'form':form,'result':query(a,form,detailed=detailed)})
    if new_forms:
        for form in words.NEW_FORMS:
            forms.append({'form':form,'result':words.query(a,form,detailed=detailed)})
    if memories:
        for context in memory.codec(a):
            contexts.append({'context':context,'result':memory.query(a,context,detail=detailed)})
    if admitted:
        m=get(a);m['counters']['material_panels']=m['counters'].get('material_panels',0)+1;save(a,m)
    return {'kind':'APD03_explicit_material_panel','before':before,'after':physical(a.world),
        'forms':forms,'memories':contexts,'forms_requested':len(forms),'memory_queries_requested':len(contexts),
        'material_not_passive':True,'new_slot_admission_was_not_implicit':True,
        'common_lexical_reader_sites':32 if admitted else 28,
        'scope':'Literal old14 forms, optional2generic forms and optional6explicit context queries. No target, automatic verdict or acquired autonomous bank choice. Every query can change the landscape.'}


def teach(a,text,sign,*,revision=False):
    m=get(a);_available(a,m)
    result=words.teach(a,text,sign,revision=revision)
    m['counters']['teaching']+=1;save(a,m);return result


def language(a,text,datum,context,*,detailed=False):
    m=get(a);_available(a,m)
    result=words.use_relation(a,text,datum,context,detailed=detailed)
    m['counters']['language_uses']+=1;save(a,m);return result


def start_task(a,text,operands,visible,directory,*,context=0):
    row={'modo':'apd03-tarea-iniciar','texto':text,'operandos':operands,
        'segundo_visible':visible,'contexto_ambiente':context};validate(a,row)
    m=get(a);serial=m['counters']['goals']+1
    environment=SharedGoalEnvironment(task_id='apd03_goal_'+str(serial),text=text,left=operands[0],
        second=operands[1],second_initially_public=visible,directory=Path(directory)/'world',
        quality=quality,effects=effects,context=context,feedback_mode=m['consequence_mode'])
    m['goal_pending']=environment.operational_state();m['counters']['goals']=serial;save(a,m)
    return {'kind':'explicit_APD03_environment_initialization','native_ticks':0,
        'public_observation':environment.observation(),'progress':environment.progress(),
        'environment_private_fact':'The second actual operand is stored in the environment; only a selected QUERY exposes it.',
        'no_correct_action_or_step_list_supplied':True}


def step(a,maximum,directory,*,feedback='real',detailed=False):
    validate(a,{'modo':'apd03-paso','oportunidades':maximum})
    if feedback not in('real','omit'):raise ValueError('Declared generic consequence or omission only')
    m=get(a);environment=restore_operational(m['goal_pending'],directory=Path(directory)/'world',
        quality=quality,effects=effects)
    m['counters']['opportunity_invocations']+=1
    before=physical(a.world);rows=[]
    for _ in range(maximum):
        if environment.terminal():break
        public=environment.observation()
        m['external_uncertain']={'stage':'APD03_opportunity_in_progress','tick':int(a.tick),
            'opportunity_before':environment.progress()['opportunities_used']};save(a,m)
        try:
            word=words.query(a,public['text'],detailed=detailed)
            operation_sign=word['reader']['formed_native_command']
            raw_missing_bit=int(public['second']is None)
            selection=sensor.use(a,raw_missing_bit,family=SENSOR_FAMILY)
            action_sign=selection['reader']['choice'];native_numeric=[]
            def native_value(operation,values):
                result=arithmetic.native_pair(a,'suma'if operation=='add'else'diferencia',*values,detailed=detailed)
                native_numeric.append(result)
                return result['numeric_reader']['numeric_result']
            effect=environment.commit_selected(action_sign,operation_sign,
                native_value_reader=native_value,synthetic_fixture=False)
            m['goal_pending']=environment.operational_state();save(a,m)
            projected=effect['feedback'];returned=None
            if projected is not None:
                returned=route.consequence(a,projected['category'],mode=feedback)
            m['counters']['native_opportunities']+=1
            m['goal_pending']=environment.operational_state()
            if environment.progress()['uncertain_effect']is not None:
                m['external_uncertain']={'stage':'APD03_uncertain_goal_file',
                    'progress':environment.progress(),'effect':effect}
                save(a,m)
            else:m['external_uncertain']=None;save(a,m)
            rows.append({'opportunity':effect['opportunity'],'public_observation':public,
                'word':word,'raw_missing_fact_codec':{'raw_value':raw_missing_bit,
                    'meaning':'int(public second is None); not correct action or private operand'},
                'native_selection':selection,'environment_effect':effect,
                'native_numeric':native_numeric,'common_return':returned,'return_mode':feedback,
                'actor_received_private_audit':False,'original_ACTION_CODEC':{-1:'ACT',0:'QUERY',1:'QUERY'}})
            if projected is None:break
        except BaseException as error:
            m['goal_pending']=environment.operational_state()
            m['external_uncertain']={'stage':'APD03_interrupted_native_opportunity',
                'type':type(error).__name__,'tick':int(a.tick),
                'no_automatic_retry_or_rollback':True};save(a,m);raise
    return {'kind':VERSION,'before':before,'opportunities':rows,'after':physical(a.world),
        'progress':environment.progress(),'operational_environment_state':m['goal_pending'],
        'scope':'Operator offers opportunities; a fixed raw missing-bit sensor and acquired R04 state determine ACT/QUERY. Exactly one native arithmetic provider is possible after ACT; no external fallback. Local usefulness and final-file completion are distinct.'}
