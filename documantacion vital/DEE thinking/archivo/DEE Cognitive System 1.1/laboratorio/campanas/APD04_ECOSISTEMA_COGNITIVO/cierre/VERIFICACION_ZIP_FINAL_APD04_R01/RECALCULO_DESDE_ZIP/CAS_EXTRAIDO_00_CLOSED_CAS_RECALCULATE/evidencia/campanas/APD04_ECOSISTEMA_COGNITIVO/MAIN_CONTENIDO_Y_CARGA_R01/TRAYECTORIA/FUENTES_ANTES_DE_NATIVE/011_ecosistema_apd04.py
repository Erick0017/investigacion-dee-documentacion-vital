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
from capacidades import lexico_compartido_apd04 as lex
from capacidades import mente_unificada_01 as mu
from capacidades import ruta_adaptativa_apd02_04 as route

KEY='DEE.Cognitive.System.1.1.APD04.ecosystem.R01'
VERSION='APD04.shared_workshop.sequential_sources.R01'
SELECT_CODEC={-1:'USE',0:'INSPECT',1:'INSPECT'}
TOOL_CODEC={1:'clasifica',-1:'equilibra'}

def save(a,m):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m))
def get(a):
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:raise ValueError('El taller no esta admitido; no se reconstruye otra vida')
    m=decode_metadata(entries[KEY])
    if m['version']!=VERSION:raise ValueError('Otro contrato de taller; no migracion silenciosa')
    return m

def validate(a,row):
    from app.protocolo_apd04 import validate_literal
    validate_literal(row)
    mode=row.get('modo')
    allowed={'apd04-sensor-calibrar','apd04-calibrar','apd04-iniciar','apd04-ampliar','apd04-cambio','apd04-vivir','apd04-estado','apd04-leccion-referencia','apd04-lex-admitir','apd04-docencia','apd04-palabra'}
    if mode not in allowed:raise ValueError('Modo APD04 no admitido')
    route.get(a)
    if route.get(a)['pending_window'] is not None:raise ValueError('Traza R04 pendiente; no reemplazar futuro')
    if mode=='apd04-sensor-calibrar':return
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
    m=get(a)
    if m.get('in_progress'):raise ValueError('Futuro incierto conservado; no reintentar')
    if mode=='apd04-ampliar' and row['fuentes']<=len(m['objects']):raise ValueError('Ampliar agrega objetos; no elimina ni reinicia mundo/cursor/cache')
    if mode=='apd04-cambio' and any(x['fuente']not in{o['id']for o in m['objects']}for x in row.get('mutaciones',[])):raise ValueError('Fuente no existente; no crearla silenciosamente')
    if mode=='apd04-vivir' and (set(row)-{'modo','oportunidades','lexico','sensor','actuador','retorno','desacoplado'} or type(row.get('oportunidades'))is not int or not 1<=row['oportunidades']<=4):raise ValueError('1..4oportunidades genericas')
    if mode=='apd04-vivir' and row.get('sensor','independent')not in('independent','independent_balanced','tag_only','zero'):raise ValueError('Sensor prospectivo fijo')
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
       'native_answers_in_metadata':False,'environment_cache_is_not_native_memory':True}
    save(a,m)
    return {'kind':'prepared_local_workshop','native_ticks':0,'world_serial':m['world_serial'],'sources':len(objects),
        'scope':'External environment initialization only. Raw tag and goal tag are independently transduced; criterion is evaluator only. No Native state reset.'}

def state(a):
    m=get(a);return {'version':VERSION,'physical':physical(a.world),'sources':len(m['objects']),'cursor_environment':m['cursor'],
       'world_serial':m['world_serial'],'episode':m['episode'],'counters':m['counters'],'in_progress':m['in_progress'],
       'memory_scope':'Cache and cursor belong to simulated environment. Not Native retained numbers or autonomous source-address learning.'}

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
    m=get(a);before=physical(a.world);rows=[];folder=Path(directory)/'synthetic_workshop';folder.mkdir(parents=True,exist_ok=True)
    for _ in range(count):
        m['episode']+=1;ep=m['episode'];obj=m['objects'][m['cursor']]
        public={'source_id':obj['id'],'tag':obj['tag'],'goal_tag':m['goal_tag'],'word':m['word'],
           'cached_value':None if obj['observed']is None else obj['observed']['value'],'loads':list(m['loads'])}
        m['in_progress']={'episode':ep,'tick':int(a.tick)};save(a,m)
        bit0=obj['tag']if sensor_mode!='zero'else 0;bit1=m['goal_tag']if sensor_mode in('independent','independent_balanced')else bit0 if sensor_mode=='tag_only'else 0
        selected=(balanced_sensor if sensor_mode=='independent_balanced'else sensor).selecciona(a,bit0,bit1,detail=detailed);sign=selected['physical_choice'];action=SELECT_CODEC.get(sign)
        effect={'action':action,'actuator':actuator,'new_fact':False,'useful':False,'valid_native':sign is not None}
        operation=None;word=None;artifact=None;expected=None
        if action is None:m['counters']['invalid']+=1
        elif actuator=='nulled':effect['reason']='post_emission_action_nulled'
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
        category='SUCCESS'if effect['useful']else'FAILURE'
        returned=sensor.finish(a,category if not decoupled else ('SUCCESS'if ep%2 else'FAILURE'),mode=feedback)
        if effect['useful']:m['counters']['useful']+=1
        m['cursor']=(m['cursor']+1)%len(m['objects']);m['in_progress']=None;save(a,m)
        rows.append({'episode':ep,'public_before':public,'raw_sensor_components':[bit0,bit1],'selection':selected,
             'physical_action':action,'word':word,'native_operation':operation,'committed_effect':effect,
             'auditor_only_after_effect':{'actual_source_value':obj['value'],'source_version':obj['version'],
                 'observed_version':None if obj['observed']is None else obj['observed']['version'],
                 'observed_value':None if obj['observed']is None else obj['observed']['value'],
                 'criterion':m['criterion_auditor_only'],'not_an_actor_input':True},
             'feedback':{'category':category,'modality':feedback,'decoupled':decoupled},'native_return':returned,
             'artifact':None if artifact is None else str(artifact),'expected_class_auditor_only_after_action':expected,
             'cursor_rule':'Prepared circular view after any opportunity; Native decides INSPECT/USE, not an arbitrary numeric source address'})
    return {'kind':VERSION,'before':before,'rows':rows,'after':physical(a.world),'state':state(a),
        'assistance':'Fixed sequential view, tool pipeline, cadence, codecs and postaction verifier. No target-aware source filter. Not simultaneous full20-input attention, learned planner or free language.'}

def dispatch(a,row,directory,*,feedback='real',actuator='closed',detailed=False):
    validate(a,row);mode=row['modo']
    if mode=='apd04-iniciar':return start(a,row)
    if mode=='apd04-cambio':return change(a,row)
    if mode=='apd04-ampliar':return expand(a,row)
    if mode=='apd04-estado':return state(a)
    if mode=='apd04-sensor-calibrar':
        rows=[]
        for bits in row['pares']:
            selected=(sensor if row['familia']=='R02'else balanced_sensor).selecciona(a,*bits,detail=detailed)
            diagnostic=balanced_sensor.diagnostic_gates9(a)
            returned=sensor.finish(a,'SUCCESS',mode='omit')
            rows.append({'raw_components':bits,'selection':selected,'auditor_only_gates9':diagnostic,'return':returned})
        return {'kind':'explicit_auxiliary_sensor_calibration_without_quality_feedback','family':row['familia'],'rows':rows,'no_task_success_or_attention_claim':True}
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
