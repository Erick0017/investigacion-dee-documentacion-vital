"""Taller sintético compartido. El entorno aplica salidas, nunca selecciona por DEE.

La vista es secuencial: dos propiedades elementales de fuente/objetivo llegan
al sensor; sólo INSPECT expone el dato completo. El cursor y cache son del
entorno, no memoria numérica nativa. Los veredictos se calculan postacción.
"""
from pathlib import Path
import json, random
from dee_thinking.persistence import encode_metadata, decode_metadata
from app.native_tools import physical
from capacidades import acciones_nativas_apd04 as native
from capacidades import sensor_componentes_apd04 as sensor
from capacidades import sensor_balanceado_apd04 as balanced_sensor
from capacidades import sensor_dos_pares_apd04 as two_pair_sensor
from capacidades import lexico_compartido_apd04 as lex
from capacidades import mente_unificada_01 as mu
from capacidades import ruta_adaptativa_apd02_04 as route

KEY='DEE.Cognitive.System.1.1.APD04.ecosystem.R01'
VERSION='APD04.shared_workshop.sequential_sources.R01'
ACTION_CODECS={'R01':{-1:'USE',0:'INSPECT',1:'INSPECT'},
               'R02':{-1:'INSPECT',0:'INSPECT',1:'USE'},
               'R03':{-1:'INSPECT',0:'WAIT',1:'USE'}}
VIEW_POLICIES=('circular_R01','inspeccion_persistente')
SELECT_CODEC=ACTION_CODECS['R01']  # Historical public constant; retained for existing callers.
TOOL_CODEC={1:'clasifica',-1:'equilibra'}
QUALITY_R03='APD04.posteffect_quality.relevant_gain_or_irrelevant_formed_wait.R03.v1'

def save(a,m):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m))
def get(a):
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:raise ValueError('El taller no esta admitido; no se reconstruye otra vida')
    m=decode_metadata(entries[KEY])
    if m['version']!=VERSION:raise ValueError('Otro contrato de taller; no migracion silenciosa')
    if m.get('action_codec','R01')not in ACTION_CODECS:raise ValueError('Codec de actuacion desconocido; no reparar silenciosamente')
    if m.get('action_codec','R01')=='R03'and m.get('quality_contract')!=QUALITY_R03:raise ValueError('Contrato posteffect R03 ausente o distinto; no reparar')
    if m.get('view_policy','circular_R01')not in VIEW_POLICIES:raise ValueError('Vista desconocida; no reparar cursor o cache')
    return m

def validate(a,row):
    from app.protocolo_apd04 import validate_literal
    validate_literal(row)
    mode=row.get('modo')
    allowed={'apd04-vista','apd04-actuador','apd04-r04-admitir','apd04-sensor-calibrar','apd04-calibrar','apd04-iniciar','apd04-ampliar','apd04-cambio','apd04-vivir','apd04-estado','apd04-leccion-referencia','apd04-lex-admitir','apd04-docencia','apd04-palabra'}
    if mode not in allowed:raise ValueError('Modo APD04 no admitido')
    route.get(a)
    if route.get(a)['pending_window'] is not None:raise ValueError('Traza R04 pendiente; no reemplazar futuro')
    if mode=='apd04-r04-admitir':return
    if mode=='apd04-sensor-calibrar':
        if row['familia']=='R04':two_pair_sensor._get(a)
        return
    if mode=='apd04-calibrar':
        if set(row)!={'modo','casos'} or not isinstance(row['casos'],list) or not 1<=len(row['casos'])<=8:raise ValueError('1..8casos literales, sin targets')
        for c in row['casos']:
            if c.get('tipo')=='clasifica':
                if set(c)!={'tipo','valor'} or type(c['valor']) is not int or not 0<=c['valor']<=512:raise ValueError('Escalar exacto')
            elif c.get('tipo')=='equilibra':
                if set(c)!={'tipo','cargas'} or not isinstance(c['cargas'],list) or len(c['cargas'])!=2 or any(type(x)is not int or not 0<=x<=20 for x in c['cargas']):raise ValueError('Dos cargas independientes0..20')
            else:raise ValueError('Tipo de calibracion desconocido')
        return
    if mode=='apd04-iniciar':
        if set(row)-{'modo','semilla','fuentes','criterio','etiqueta_objetivo','palabra','cargas'}:raise ValueError('Configuracion ambiental literal, no respuesta o plan')
        if type(row.get('semilla'))is not int or row.get('fuentes')not in(2,5,10,20):raise ValueError('Semilla y dominio2/5/10/20')
        if type(row.get('criterio',20))is not int or not 1<=row.get('criterio',20)<=40:raise ValueError('Criterio del evaluador acotado')
        if row.get('etiqueta_objetivo',0)not in(0,1):raise ValueError('Propiedad elemental0/1')
        if row.get('palabra','clasifica')not in('clasifica','equilibra'):raise ValueError('Peticion ambiental acotada')
        if not isinstance(row.get('cargas',[8,4]),list) or len(row.get('cargas',[8,4]))!=2 or any(type(x)is not int or not 0<=x<=20 for x in row.get('cargas',[8,4])):raise ValueError('Cargas materiales0..20')
        if KEY in dict(a.world.runtime.snapshot_metadata_entries) and get(a).get('in_progress'):raise ValueError('Operacion incierta: conservar')
        return
    if mode=='apd04-leccion-referencia':
        if set(row)!={'modo','lado'} or row['lado']not in('A','B'):raise ValueError('Una experiencia explicita A/B')
        return
    if mode=='apd04-lex-admitir':
        if set(row)!={'modo'}:raise ValueError('Preparacion sin signo ni respuesta')
        return
    if mode=='apd04-docencia':
        if set(row)-{'modo','texto','senal','docente','revision'} or row.get('texto')not in('clasifica','equilibra') or type(row.get('senal'))is not int or row['senal']not in(-1,1):raise ValueError('Docencia explicita separada')
        if row.get('docente','paired')not in('paired','omitted','desync'):raise ValueError('Modalidad docente')
        if type(row.get('revision',False))is not bool:raise ValueError('Revision booleana explicita')
        return
    if mode=='apd04-palabra':
        if set(row)!={'modo','texto'} or row['texto']not in lex.FORM_CODEC:raise ValueError('Consulta literal sin target')
        return
    if mode=='apd04-vivir' and row.get('sensor')=='independent_two_pairs':two_pair_sensor._get(a)
    m=get(a)
    if m.get('in_progress'):raise ValueError('Futuro incierto conservado; no reintentar')
    if mode=='apd04-ampliar' and row['fuentes']<=len(m['objects']):raise ValueError('Ampliar agrega objetos; no elimina ni reinicia mundo/cursor/cache')
    if mode=='apd04-cambio' and any(x['fuente']not in{o['id']for o in m['objects']}for x in row.get('mutaciones',[])):raise ValueError('Fuente no existente; no crearla silenciosamente')
    if mode=='apd04-vivir' and (set(row)-{'modo','oportunidades','lexico','sensor','actuador','retorno','desacoplado'} or type(row.get('oportunidades'))is not int or not 1<=row['oportunidades']<=4):raise ValueError('1..4oportunidades genericas')
    if mode=='apd04-vivir' and row.get('sensor','independent')not in('independent','independent_balanced','independent_two_pairs','tag_only','zero'):raise ValueError('Sensor prospectivo fijo')
    if mode=='apd04-vivir' and any(type(row.get(k,v))is not bool for k,v in [('lexico',True),('desacoplado',False)]):raise ValueError('Controles booleanos explicitos')

def start(a,row):
    validate(a,row);rng=random.Random(row['semilla']);old=get(a)if KEY in dict(a.world.runtime.snapshot_metadata_entries)else None
    objects=[{'id':i,'tag':i%2,'value':rng.randrange(5,37),'observed':None,'bin':None,'version':0} for i in range(row['fuentes'])]
    m={'version':VERSION,'seed_environment_only':row['semilla'],'objects':objects,'cursor':0,
       'goal_tag':row.get('etiqueta_objetivo',0),'criterion_auditor_only':row.get('criterio',20),
       'word':row.get('palabra','clasifica'),'loads':list(row.get('cargas',[8,4])),
       'episode':0,'world_serial':1 if old is None else old['world_serial']+1,
       'previous_worlds':[] if old is None else old['previous_worlds']+[{'serial':old['world_serial'],'episodes':old['episode'],'counters':old['counters']}],
       'counters':{'inspect':0,'use':0,'invalid':0,'useful':0,'correct_classifications':0,'moves':0},'in_progress':None,
       'action_codec':'R01','native_answers_in_metadata':False,'environment_cache_is_not_native_memory':True}
    save(a,m)
    return {'kind':'prepared_local_workshop','native_ticks':0,'world_serial':m['world_serial'],'sources':len(objects),
        'scope':'External environment initialization only. Raw tag and goal tag are independently transduced; criterion is evaluator only. No Native state reset.'}

def state(a):
    m=get(a);result={'version':VERSION,'physical':physical(a.world),'sources':len(m['objects']),'cursor_environment':m['cursor'],
       'world_serial':m['world_serial'],'episode':m['episode'],'counters':m['counters'],'in_progress':m['in_progress'],
       'action_codec':m.get('action_codec','R01'),'fixed_signed_action_map':dict(ACTION_CODECS[m.get('action_codec','R01')]),
       'memory_scope':'Cache and cursor belong to simulated environment. Not Native retained numbers or autonomous source-address learning.'}
    if m.get('action_codec','R01')=='R03':result.update(quality_contract=QUALITY_R03,quality_domain_actuator='closed')
    if 'view_policy'in m:result['view_policy']=m['view_policy']
    return result

def configure_actuator(a,row):
    """Explicit external P0 transducer preparation; no learned association."""
    m=get(a);before=m.get('action_codec','R01');version=row['version']
    if version not in ACTION_CODECS:raise ValueError('Codec fijo R01/R02/R03')
    m['action_codec']=version
    if version=='R03':
        m['quality_contract']=QUALITY_R03;m['counters'].setdefault('wait',0);m['counters'].setdefault('quality_success',0)
    else:m.pop('quality_contract',None)
    save(a,m)
    result={'kind':'explicit_prepared_actuator_codec','before':before,'after':version,
       'fixed_signed_map':dict(ACTION_CODECS[version]),'new_native_ticks_in_operation':0,
       'scope':'External transduction preparation only. No RAW, clock, source cache, world reset, target or learned-policy edit.'}
    if version=='R03':result.update(quality_contract=QUALITY_R03,quality_domain_actuator='closed',old_work_gain_still_separate=True)
    return result


def next_cursor_prepared_view(policy,cursor,source_count,action,formed_unique,actuator):
    """P0 environment transition only; no object, cache, value, goal or score input."""
    if policy not in VIEW_POLICIES:raise ValueError('Unknown fixed view')
    if type(cursor)is not int or type(source_count)is not int or source_count<1 or not 0<=cursor<source_count:raise ValueError('Invalid current cursor; never reset it')
    retain=policy=='inspeccion_persistente'and action=='INSPECT'and formed_unique is True and actuator=='closed'
    return cursor if retain else(cursor+1)%source_count


def configure_view(a,row):
    """External P0 affordance selection, not learned source addressing."""
    m=get(a);policy=row['politica'];before=m.get('view_policy','circular_R01')
    if policy not in VIEW_POLICIES:raise ValueError('Fixed view enum only')
    m['view_policy']=policy;save(a,m)
    return {'kind':'explicit_prepared_environment_view','before':before,'after':policy,
        'new_native_ticks_in_operation':0,'cursor_preserved':m['cursor'],
        'scope':'P0 affordance only. No RAW/clock, cache, object, loads or cursor reset. Only later formed INSPECT may retain the current source; Native selects the emission.'}


def task_env_signature(m):
    """Exact environmental objects/loads audit copy, never an actor input."""
    return json.loads(json.dumps({'objects':m['objects'],'loads':m['loads']},sort_keys=True,separators=(',',':')))


def formed_native_choice(sign,reader):
    candidates=reader.get('candidates',[])
    return type(sign)is int and sign in(-1,0,1) and reader.get('choice')==sign and len(candidates)==1 and candidates[0].get('choice')==sign


def posteffect_quality_r03(sign,action,reader,old_gain,tag,goal,before,after,actuator):
    """Postemission environment score. No strategy/content is returned to Native."""
    formed=formed_native_choice(sign,reader)
    if actuator!='closed':
        return {'contract':QUALITY_R03,'status':'out_of_domain','old_work_gain':bool(old_gain),'new_quality':None,
            'actuator':actuator,'no_feedback_category_is_defined':True}
    quality=False
    if formed:
        if action=='WAIT':quality=sign==0 and tag!=goal and before==after
        elif action in('INSPECT','USE'):quality=bool(old_gain)
    return {'contract':QUALITY_R03,'status':'in_domain','old_work_gain':bool(old_gain),'new_quality':quality,
        'formed_unique':formed,'formed_native_sign':sign,'transduced_action':action,'actuator':actuator,
        'tag_auditor_after_effect':tag,'goal_auditor_after_effect':goal,
        'task_env_before':before,'task_env_after':after,'task_env_unchanged':before==after,
        'not_an_actor_input':True,'SUCCESS_adds_no_new_positive_reinforcement_port':True}


def change(a,row):
    """Explicit exogenous event; keeps the actual world, effects and Native life."""
    m=get(a);before={'goal_tag':m['goal_tag'],'word':m['word'],'loads':list(m['loads']),'cursor':m['cursor']}
    for key,dest in [('etiqueta_objetivo','goal_tag'),('palabra','word'),('cargas','loads'),('criterio','criterion_auditor_only')]:
        if key in row:m[dest]=list(row[key])if key=='cargas'else row[key]
    for event in row.get('mutaciones',[]):
        obj=next(o for o in m['objects']if o['id']==event['fuente'])
        obj['value']=event['valor'];obj['version']+=1
    if row.get('rotar'):m['objects']=m['objects'][row['rotar']%len(m['objects']):]+m['objects'][:row['rotar']%len(m['objects'])]
    if row.get('retirar_observados'):
        for obj in m['objects']:obj['observed']=None
    m['exogenous_events']=m.get('exogenous_events',0)+1;save(a,m)
    return {'kind':'explicit_exogenous_change','before':before,'literal_event':row,'after':state(a),
       'scope':'Environment event, not learned Native adaptation or a correct action. Stale cached versions remain unless explicit withdrawal control.'}

def expand(a,row):
    m=get(a);before=len(m['objects']);rng=random.Random(row['semilla'])
    for i in range(before,row['fuentes']):
        m['objects'].append({'id':i,'tag':i%2,'value':rng.randrange(5,37),'observed':None,'bin':None,'version':0})
    m['exogenous_events']=m.get('exogenous_events',0)+1;save(a,m)
    return {'kind':'exogenous_workshop_expansion','before_sources':before,'after_sources':len(m['objects']),
        'scope':'New environmental sources only; same Native N67, history, cursor, old objects, bins and cache. Sequential two-bit view, not20simultaneous full records.'}

def live(a,count,directory,*,use_lexicon=True,sensor_mode='independent',actuator='closed',feedback='real',decoupled=False,detailed=False):
    m=get(a);codec_version=m.get('action_codec','R01');action_codec=ACTION_CODECS[codec_version]
    if codec_version=='R03'and actuator!='closed':return {'kind':'APD04_R03_quality_out_of_domain','out_of_domain':True,'rows':[],'new_native_ticks_in_operation':0,'actuator':actuator,'no_feedback_or_native_answer_substituted':True}
    before=physical(a.world);rows=[];folder=Path(directory)/'synthetic_workshop';folder.mkdir(parents=True,exist_ok=True)
    for _ in range(count):
        m['episode']+=1;ep=m['episode'];obj=m['objects'][m['cursor']]
        task_before=task_env_signature(m)if codec_version=='R03'else None;quality_witness=None
        public={'source_id':obj['id'],'tag':obj['tag'],'goal_tag':m['goal_tag'],'word':m['word'],
           'cached_value':None if obj['observed']is None else obj['observed']['value'],'loads':list(m['loads'])}
        m['in_progress']={'episode':ep,'tick':int(a.tick)};save(a,m)
        bit0=obj['tag']if sensor_mode!='zero'else 0;bit1=m['goal_tag']if sensor_mode in('independent','independent_balanced','independent_two_pairs')else bit0 if sensor_mode=='tag_only'else 0
        selected={'independent_balanced':balanced_sensor,'independent_two_pairs':two_pair_sensor}.get(sensor_mode,sensor).selecciona(a,bit0,bit1,detail=detailed);sign=selected['physical_choice'];actuator_sign=sign if codec_version!='R03'or formed_native_choice(sign,selected['reader'])else None;action=action_codec.get(actuator_sign)
        effect={'action':action,'actuator':actuator,'prepared_action_codec':codec_version,'new_fact':False,'useful':False,'valid_native':actuator_sign is not None}
        operation=None;word=None;artifact=None;expected=None
        if action is None:m['counters']['invalid']+=1
        elif actuator=='nulled':effect['reason']='post_emission_action_nulled'
        elif action=='WAIT':
            m['counters']['wait']+=1;effect['reason']='formed_zero_WAIT_no_task_environment_change'
        elif action=='INSPECT':
            previous=obj['observed'];obj['observed']={'value':obj['value'],'version':obj['version']}
            effect['new_fact']=previous!=obj['observed']
            effect['useful']=effect['new_fact'] and obj['tag']==m['goal_tag']
            effect['reason']='environmental_fact_exposed_by_emission';m['counters']['inspect']+=1
        elif action=='USE':
            m['counters']['use']+=1;tool=m['word']
            if use_lexicon:
                word=lex.query(a,m['word'],detailed=detailed);tool=TOOL_CODEC.get(word['reader']['formed_native_command'])
            if tool=='clasifica' and public['cached_value']is not None:
                operation=native.classify(a,public['cached_value'],detail=detailed);direction=operation['physical_choice']
                if direction in(-1,0,1):
                    prior_bin=obj['bin'];obj['bin']=direction
                    expected=(obj['value']>m['criterion_auditor_only'])-(obj['value']<m['criterion_auditor_only'])
                    correct=direction==expected and obj['observed']['version']==obj['version']
                    effect.update(correct=correct,actual_bin=direction,previous_bin=prior_bin)
                    effect['useful']=correct and obj['tag']==m['goal_tag'] and prior_bin!=direction
                    if correct:m['counters']['correct_classifications']+=1
                else:effect['reason']='no_unique_native_classification'
            elif tool=='equilibra':
                observed=list(m['loads']);operation=native.balance(a,*observed,detail=detailed);direction=operation['physical_choice']
                before_loads=list(m['loads'])
                if direction==1 and m['loads'][0]>0 and m['loads'][1]<20:m['loads'][0]-=1;m['loads'][1]+=1;m['counters']['moves']+=1
                elif direction==-1 and m['loads'][1]>0 and m['loads'][0]<20:m['loads'][1]-=1;m['loads'][0]+=1;m['counters']['moves']+=1
                if direction is not None:
                    old_gap=abs(before_loads[0]-before_loads[1]);new_gap=abs(m['loads'][0]-m['loads'][1])
                    effect['useful']=(new_gap<old_gap or(direction==0 and old_gap==0)) and obj['tag']==m['goal_tag']
                    effect.update(loads_before=before_loads,loads_after=list(m['loads']),gap_before=old_gap,gap_after=new_gap,physical_move_direction=direction)
            else:effect['reason']='unavailable_public_fact_or_unformed_word'
            body={'schema':'APD04.synthetic.effect.v1','world_serial':m['world_serial'],'episode':ep,'source_id':obj['id'],
                  'tool_emitted':tool,'effect':effect,'native_tick':int(a.tick),'not_a_target_template':True}
            artifact=folder/('world'+str(m['world_serial'])+'_episode'+str(ep)+'.json')
            with artifact.open('x',encoding='utf8') as f:json.dump(body,f,ensure_ascii=False,sort_keys=True);f.write('\n')
        # Evaluation happens after the physical emission and the real local effect.
        feedback_success=effect['useful']
        if codec_version=='R03':
            quality_witness=posteffect_quality_r03(sign,action,selected['reader'],effect['useful'],obj['tag'],m['goal_tag'],task_before,task_env_signature(m),actuator)
            effect.update(old_work_gain=effect['useful'],new_quality=quality_witness['new_quality'],quality_contract=QUALITY_R03)
            feedback_success=quality_witness['new_quality']
            if feedback_success:m['counters']['quality_success']+=1
        category='SUCCESS'if feedback_success else'FAILURE'
        returned=sensor.finish(a,category if not decoupled else ('SUCCESS'if ep%2 else'FAILURE'),mode=feedback)
        if effect['useful']:m['counters']['useful']+=1
        cursor_before=m['cursor'];view_policy=m.get('view_policy','circular_R01')
        m['cursor']=next_cursor_prepared_view(view_policy,cursor_before,len(m['objects']),action,formed_native_choice(sign,selected['reader']),actuator);m['in_progress']=None;save(a,m)
        result_row={'episode':ep,'public_before':public,'raw_sensor_components':[bit0,bit1],'selection':selected,
             'physical_action':action,'word':word,'native_operation':operation,'committed_effect':effect,
             'auditor_only_after_effect':{'actual_source_value':obj['value'],'source_version':obj['version'],
                 'observed_version':None if obj['observed']is None else obj['observed']['version'],
                 'observed_value':None if obj['observed']is None else obj['observed']['value'],
                 'criterion':m['criterion_auditor_only'],'not_an_actor_input':True},
             'feedback':{'category':category,'modality':feedback,'decoupled':decoupled},'native_return':returned,
             'artifact':None if artifact is None else str(artifact),'expected_class_auditor_only_after_action':expected,
             'cursor_rule':'Prepared circular view after any opportunity; Native decides INSPECT/USE, not an arbitrary numeric source address'}
        if quality_witness is not None:
            result_row['posteffect_quality']=quality_witness
            result_row['cursor_rule']='Prepared circular view after any opportunity; Native emits INSPECT/WAIT/USE through the fixed R03 map, not an arbitrary numeric source address.'
        if view_policy=='inspeccion_persistente':
            result_row.update(view_policy=view_policy,cursor_before=cursor_before,cursor_after=m['cursor'],
                cursor_rule='P0 persistent view retains only formed native INSPECT with closed actuator; USE/WAIT advance. NULL, ambiguity or nulled output advance by declared environmental default, not intelligent Native choice.')
        rows.append(result_row)
    return {'kind':VERSION,'before':before,'rows':rows,'after':physical(a.world),'state':state(a),
        'assistance':'Fixed sequential view, tool pipeline, cadence, codecs and postaction verifier. No target-aware source filter. Not simultaneous full20-input attention, learned planner or free language.'}

def dispatch(a,row,directory,*,feedback='real',actuator='closed',detailed=False):
    validate(a,row);mode=row['modo']
    if mode=='apd04-iniciar':return start(a,row)
    if mode=='apd04-vista':return configure_view(a,row)
    if mode=='apd04-actuador':return configure_actuator(a,row)
    if mode=='apd04-cambio':return change(a,row)
    if mode=='apd04-ampliar':return expand(a,row)
    if mode=='apd04-estado':return state(a)
    if mode=='apd04-sensor-calibrar':
        rows=[]
        for bits in row['pares']:
            selected={'R02':sensor,'R03':balanced_sensor,'R04':two_pair_sensor}[row['familia']].selecciona(a,*bits,detail=detailed)
            diagnostic=balanced_sensor.diagnostic_gates9(a)
            returned=sensor.finish(a,'SUCCESS',mode='omit')
            rows.append({'raw_components':bits,'selection':selected,'auditor_only_gates9':diagnostic,'return':returned})
        return {'kind':'explicit_auxiliary_sensor_calibration_without_quality_feedback','family':row['familia'],'rows':rows,'no_task_success_or_attention_claim':True}
    if mode=='apd04-r04-admitir':
        screen=two_pair_sensor.preflight(a)
        if not screen['admissible']:
            return {'kind':'APD04_R04_P0_admission_rejected_without_material_write','admitted':False,'preflight':screen,'new_native_ticks_in_operation':0}
        return two_pair_sensor.prepare(a)
    if mode=='apd04-calibrar':
        return {'kind':'explicit_auxiliary_native_calibration','rows':[native.classify(a,c['valor'],detail=detailed)if c['tipo']=='clasifica'else native.balance(a,*c['cargas'],detail=detailed)for c in row['casos']]}
    if mode=='apd04-leccion-referencia':return mu.experience(a,row['lado'])
    if mode=='apd04-lex-admitir':
        screen=lex.preflight(a)
        if not screen['admissible']:
            return {'kind':'APD04_P0_admission_rejected_without_material_write','admitted':False,'preflight':screen,'new_native_ticks_in_operation':0}
        return lex.prepare(a)
    if mode=='apd04-docencia':return lex.teach(a,row['texto'],row['senal'],mode=row.get('docente','paired'),revision=row.get('revision',False))
    if mode=='apd04-palabra':return lex.query(a,row['texto'],detailed=detailed)
    if mode=='apd04-vivir':return live(a,row['oportunidades'],directory,use_lexicon=row.get('lexico',True),sensor_mode=row.get('sensor','independent'),actuator=actuator,feedback=feedback,decoupled=row.get('desacoplado',False),detailed=detailed)
    raise ValueError('Modo no ejecutable')
