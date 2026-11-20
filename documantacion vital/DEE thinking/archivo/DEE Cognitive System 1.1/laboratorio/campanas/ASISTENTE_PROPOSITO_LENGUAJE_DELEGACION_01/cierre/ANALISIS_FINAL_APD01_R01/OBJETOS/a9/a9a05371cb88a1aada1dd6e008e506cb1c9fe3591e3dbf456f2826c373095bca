"""Close scientific draft from immutable R04 records; no DEE Runtime or DOCX edits."""
import copy
import gzip
import hashlib
import json
import re
import shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
EV=ROOT/'evidencia/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01'
R04=EV/'servicio/SERVICIO_60MIN_APD_R04'
CUT_SHA='c69dec061e1090118028389af32fa67bc5d20c4864d16fe2b48ae48ea5836631'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
    with p.open('xb') as f:f.write((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
def overwrite(p,x):
    with p.open('wb') as f:f.write((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
def rel(p):return str(p.relative_to(ROOT)).replace('\\','/')

def main():
    assert sha(R04/'CORTE_PARA_MANUAL.json')==CUT_SHA
    c=read(R04/'CORTE_PARA_MANUAL.json');p=read(R04/'PANELES_Y_FUNCIONES.json');tm=read(R04/'RECALCULO_TIEMPO_APD.json')
    assert c['issues']==[] and c['operational_issues']==[]
    assert c['main']['tick']==361114 and c['persistent_service']['clean_closure'] is True
    assert c['persistent_service']['one_owner_proof']['sixty_minutes_one_native_owner_proved'] is True
    apd=p['APD_primitive_uses_including_composition_stages'];mem=p['memory_uses']
    assert len(apd)==17 and len(mem)==10
    assert all(r['word_matches_history'] and r['correct_given_actual_operator'] and r['real_artifact_completed'] for r in apd)
    assert sum(r['completed_within_prepared_modeled_budget2'] for r in apd)==15
    assert {r['route'] for r in apd}=={-1} and all(r['matches_expected'] for r in mem)
    fn=c['functional_results'];ps=c['persistent_service']
    assert fn['native_receipts']['requested']==fn['native_receipts']['applied']==4244
    assert ps['epoch']==6 and not ps['epoch_closed'] and not ps['pending_or_uncertain']
    sources=[{'relative_ROOT':rel(R04/n),'sha256':sha(R04/n)} for n in [
        'CORTE_PARA_MANUAL.json','RECALCULO_TIEMPO_APD.json','PANELES_Y_FUNCIONES.json',
        'RESULTADOS_SERVICIO_APD.md','RECALCULO_SERVICIO_APD.json','REGISTROS_APD.json.gz']]
    records=json.loads(gzip.decompress((R04/'REGISTROS_APD.json.gz').read_bytes()))
    final_record=next(r for r in records if r['id']=='apd63_post_funciones')
    final_result=json.loads(final_record['result'])
    last_forms=[]
    for i,r in enumerate(final_result['result']['rows'][:6]):
        word=r['word'];reader=word['reader']
        assert reader['reader_sites']==24 and not reader['reader_uses_target_or_token']
        last_forms.append({'form':r['literal_form'],'sign':reader['formed_native_command'],
            'tick':word['read_tick'],'use_end_tick':r['after']['tick'],
            'raw_operands':r['raw_operands'],'numeric_result':r['numeric_result'],
            'route':r['native_route_command'],'artifact':r['artifact'],
            'request_id':final_record['id'],'source_relative_ROOT':rel(R04/'REGISTROS_APD.json.gz'),
            'source_path_after_result_JSON_parse':f'$.result.rows[{i}].word.reader'})
    assert [r['sign'] for r in last_forms]==[1,-1,1,-1,1,-1]
    last_contexts=[dict(v,source_relative_ROOT=rel(R04/'PANELES_Y_FUNCIONES.json'),
        source_path='$.last_memory_observations.'+k)for k,v in sorted(fn['last_memory_observations'].items())]
    facts={'schema':'APD01.final_incorporation_facts.R1','status':'SCIENTIFIC_R04_CLOSED_FULL_PACKAGE_NOT_YET_TESTED',
        'native_ticks_for_this_tool':0,'Word_authored_by_this_tool':False,
        'main':c['main'],'paired_export':c['paired_export'],
        'last_observed_forms':last_forms,'last_observed_contexts':last_contexts,
        'scope_after_last_observations':'Last observations precede remaining idle; no extra query at final361114 or indefinite availability is asserted',
        'functional_results':{'APD_stages':17,'word_history_correct':17,'numeric_correct_given_emitted_operator':17,
            'real_artifacts_completed':17,'within_modeled_budget2':15,'native_routes':17,'external_routes':0,
            'memory_queries_matches_history':10,'memory_queries':10,'final_panel_contexts':6,
            'count_requests_correct':3,'count_requests':3,'composition_requests_correct':2,'composition_requests':2,
            'raw128_frames_correct':2,'raw128_frames':2,'total_uses_without_reteaching':3,'quita_uses_without_reteaching':3,
            'beta_explicit_lesson':fn['explicit_teaching'],'competent_reversal_demonstrated':False},
        'native_admission':{'requested':4244,'applied':4244,'rejected':0,'pending':0},
        'transport_admission':dict(fn['transport_denominators'],completed_material=25,rejected_capacity=0,rejected_validation=0),
        'strict_hour':{'own_enabled_seconds':ps['world_evolving_wall_seconds'],'one_native_PID':81368,
            'proof':ps['one_owner_proof'],'pauses':tm['pause_intervals'],'no_old_minutes_added':True,
            'different_load_from_R03':True,'not_a_matched_cognitive_improvement_contrast':True,
            'prior_opportunities23_at_least150_seconds_then_two_sequential_panels':True},
        'closure':{'owner_stopped':True,'clean_closure':True,'epoch':6,'epoch_closed':False,
            'native_pending':0,'queue_pending':0,'external_or_cascade_or_uncertain':False,
            'actual_seconds':tm['closure_bound']['recorded_seconds'],'limit_seconds':600,
            'Job_wait_is_infrastructure_not_learned_function':True},
        'source_capture_scope':c['source_capture_scope'],'sources':sources,
        'full_new_zip_test':{'status':'NOT_EXECUTED_YET','proof_external_required':True,'no_future_hash_inserted':True},
        'attribution':['Same MAIN acquired total/quita during SERVICIO_R03 and reused them during SERVICIO_R04',
            'LEX controls are auxiliary histories; no knowledge transplant',
            'SUM/affineDIFF/COUNT/codecs/initiative/composition order are prepared apparatus',
            'No NSM increment, AGI, general grammar, reversibleR2 or OSsandbox claim',
            'Accumulator five validated historical opportunities; no physical sixth trial or memory destruction proved'],
    }
    write(HERE/'DATOS_INCORPORACION_APD01.json',facts)
    archive=HERE/'_VERSIONES_INSTRUMENTALES/PRE_R04_FINAL';archive.mkdir(parents=True,exist_ok=False)
    for n in ['COBERTURA.json','DATOS_TABLA_CAPACIDADES.json','CAPACIDADES_POR_VIDA.csv']:
        shutil.copy2(HERE/n,archive/n)
    cov=read(HERE/'COBERTURA.json');cov['status']='SCIENTIFIC_R04_CLOSED_FULL_PACKAGE_PENDING'
    cov['main_last_examined_complete_cut']=c['main']
    cov['reserve_execution_revisions']['R04'].update(status='CLOSED_ONE_OWNER_CLEAN',actual_results=facts)
    cov['reserve_execution_revisions']['R04']['matched_R03_load_or_age_or_dose_claimed']=False
    cov['not_claimed']=['AGI','Autonomous planner','General grammar','Universal sandbox',
        'Competent reversal of route usefulness','Sixth physical accumulator use','Full new ZIP already independently verified']
    cov['full_new_package_verification']={'status':'PENDING_EXTERNAL_EXACT_PACKAGE_TEST','proof':None}
    cov['attribution_limits']['latest_observation_not_final_idle_query']=True
    overwrite(HERE/'COBERTURA.json',cov)
    table=read(HERE/'DATOS_TABLA_CAPACIDADES.json')
    rows=[r for r in table['rows'] if r[4]!='RESULTADOS_FINALES_PENDIENTES']
    for r in rows:
        if r[0]=='ASISTENTE_MAIN' and r[3].startswith('R03 '):
            r[3]='SERVICIO_R03 '+r[3][4:]
    nold=len(rows);ss=c['main']['snapshot_sha256'];source='ROOT:'+rel(R04/'PANELES_Y_FUNCIONES.json')
    def row(label,status,num=None,den=None,tick=361114,limit='',req=None,applied=None,rejected=None):
        rows.append(['ASISTENTE_MAIN',tick,'fisica_directa',label,status,num,den,req,applied,rejected,source,ss,
            'SERVICIO_R04 misma MAIN; no sumar controles LEX ni ventanas distintas',limit])
    for label in ['signo concordante con historia','numero correcto dada operacion emitida','artefacto real completado']:
        row('SERVICIO_R04 '+label,'USO_CONSECUTIVO_VALIDADO',17,17,limit='17etapas; no17individuos ni procedimientos aprendidos')
    row('SERVICIO_R04 artefacto dentro presupuesto2','UTILIDAD_LIMITADA',15,17,
        limit='Todas17rutas−;2caras fuera presupuesto; no reversión competente')
    row('SERVICIO_R04 consultas memorias','USO_POSTERIOR_SEGUN_HISTORIA',10,10,
        limit='Beta reenseñada−3/3; ultimas observaciones antes de ocio restante')
    for r in last_forms:
        row('SERVICIO_R04 ultima forma '+r['form']+' signo'+str(r['sign']),'LECTURA_FECHADA_Y_USO',1,1,
            tick=r['tick'],limit='Numero'+str(r['numeric_result'])+'; no consulta posterior en361114')
    for r in last_contexts:
        row('SERVICIO_R04 ultimo contexto '+r['context']+' signo'+str(r['choice']),'LECTURA_FECHADA',1,1,
            tick=r['tick'],limit='Panel6/6; previo a usos españoles y ocio final')
    row('SERVICIO_R04 conteo','FUNCION_PREPARADA_UTILIZADA',3,3,limit='Presencias0/1 preparadas; no cardinalidad general aprendida')
    row('SERVICIO_R04 composiciones','COMPOSICION_ASISTIDA',2,2,limit='Orden externo; etapas incluidas en17APD')
    row('SERVICIO_R04 crudos128','USO_RELACION_RESERVADA',2,2,limit='2tramas finitas; no128conceptos')
    row('SERVICIO_R04 entradas nativas','RECIBOS_APLICADOS',4244,4244,req=4244,applied=4244,rejected=0,
        limit='Denominador nativo distinto de25peticiones y17etapas')
    row('SERVICIO_R04 transporte material','ADMISION_Y_COMPLECION',25,25,
        limit='5controles técnicos separados; sin burst/invalidas; no carga emparejada conR03')
    row('SERVICIO_R04 3720.089s un propietario','CONTINUIDAD_INFRAESTRUCTURA_ACOTADA',
        limit='PID81368; cierre limpio; epoch6abierto; no aprendizaje derivado de duración')
    table.update(rows=rows,status='SCIENTIFIC_R04_CLOSED_FULL_PACKAGE_PENDING',native_ticks_generated=0,
        historical_rows_before_final=nold)
    overwrite(HERE/'DATOS_TABLA_CAPACIDADES.json',table)
    candidate=read(HERE/'DATOS_MANUAL_APD01_CANDIDATO_R04.json')
    chapter=candidate['chapter']
    for para in chapter:
        t=para['text']
        if t.startswith('Los contrastes léxicos invirtieron'):
            para['text']=t.replace('R03 recibió','LEX_R03 recibió')
        elif t.startswith('R04 amplió el currículo'):
            para['text']=t.replace('R04 amplió','LEX_R04 amplió',1)
        elif t.startswith('P26 preparó la ampliación'):
            para['text']=('P26 preparó la ampliación sin enseñar total/quita: diez formas anteriores correctas y regresión numérica11/11/2. '
                'SERVICIO_R03 continuó la misma MAIN y aplicó2/2entradas para total+,2/2para quita− y3/3para revisar beta+. '
                'Después usó total5/5 y quita4/4; total3/5 y quita4/4 quedaron dentro de presupuesto. '
                'SERVICIO_R04 reutilizó total y quita tres veces cada una sin volver a enseñarlas. Son adquisiciones de MAIN, no recuerdos trasplantados de LEX_R04.')
        elif t.startswith('R01 se interrumpió por una carrera'):
            para['text']=t.replace('R01 se','SERVICIO_R01 se',1).replace('R02 encontró','SERVICIO_R02 encontró')
        elif t.startswith('R03 alcanzó T325311'):
            para['text']=('SERVICIO_R03 alcanzó T325311 con4411,296152s habilitados tras pausas y recarga entre dos propietarios. '
                'El prefijo nuevo produjo61/61signos concordantes,61/61números correctos dada la operación emitida y61/61archivos;42/61dentro del presupuesto. '
                'Todas las61rutas fueron nativas− y no hubo reversión competente. Las36/36consultas nuevas de memorias concordaron con su historia revisada. '
                'Los totales65etapas y40consultas incluyen cuatro heredadas de cada tipo, no nuevas. Conteo9/9, composiciones10/10 y crudos1285/5 tienen denominadores separados. '
                'Las últimas observaciones preceden al ocio restante.')
        elif t.startswith('R03 registró140intentos'):
            para['text']=t.replace('R03 registró','SERVICIO_R03 registró',1)
        elif t.startswith('El mapa R03 de26fuentes'):
            para['text']=t.replace('El mapa R03','El mapa SERVICIO_R03',1).replace('prospectivo R04','prospectivo SERVICIO_R04')
    at=next(i for i,x in enumerate(chapter) if x['text'].startswith('32.7 Perímetro'))
    chapter[at:at]=[
        {'style':'Normal','text':('SERVICIO_R04 completó3720,089030300034s propios con un único PID nativo81368, sin pausa, recarga o reinicio intermedios. '
            'Cierre limpio, propietario detenido y cola vacía se comprobaron por separado. Hubo25/25peticiones materiales admitidas/completadas,5controles técnicos aparte y4244/4244entradas nativas aplicadas. '
            'Los17pasos APD tuvieron signos, números y archivos correctos;15/17dentro del presupuesto2. Todas las rutas continuaron nativas−, incluidas las dos oportunidades caras. '
            'Conteo3/3, composiciones2/2 y crudos1282/2 no se suman como nuevas mentes o conceptos.')},
        {'style':'Normal','text':('Se reenseñó beta− con3/3entradas y las10/10consultas de memoria concordaron con historia. '
            'El panel posterior fue alfa−,beta−,gamma+,delta−,epsilon−,zeta+,6/6 entreT355305yT355640. '
            'Después, seis pares reservados produjeron suma28,diferencia20,agrega21,resta19,total23,quita19 y la actuación del conjunto terminóT360704. '
            'Las lecturas y actuaciones preceden al ocio final: no se inventa una consulta adicional enT361114 ni disponibilidad indefinida.')},
        {'style':'Normal','text':('SERVICIO_R04 fue un protocolo distinto y más espaciado:23oportunidades previas separadas al menos150s y dos paneles secuenciales, '
            'frente a120nominales,14burst y4inválidas de SERVICIO_R03. Misma genealogía no implica oportunidades, edad o dosis emparejadas. '
            'La hora de un propietario y la espera del Job hasta vaciarse son resultados de infraestructura, no mejora cognitiva ni mayor tolerancia bajo la misma carga. '
            'No se sumaron minutos entre reservas. No se demostró política reversible niR2general.')}
    ]
    values={'FECHA_CORTE_FINAL':'25/10/2026 UTC','TICK_CORTE_FINAL':'361114',
        'SNAPSHOT_FINAL_RELATIVO':c['main']['snapshot'],'SNAPSHOT_FINAL_SHA256':c['main']['snapshot_sha256'],
        'CONTINUIDAD_FINAL_RELATIVA':rel(R04/'PAQUETE_FINAL_POSTSTOP/EXPORTACION_SERVICIO.json'),
        'INCORPORACIONES_FINALES_COMPROBADAS':('Los componentes APD de asociación léxica, aritmética preparada, selección material de procedimiento, retorno común, acumulación finita y actuación sintética permanecen ejecutables en Cognitive. '
            'La vida ASISTENTE_MAIN conserva su estado alcanzado y exportación postSTOP completa. Su epoch6 permanece abierto y el propietario está detenido; no se libera a una continuación desnuda ni se promueve a ACTIVO global')}
    def substitute(x):
        if isinstance(x,str):
            for k,v in values.items():x=x.replace('{{'+k+'}}',v)
            return x
        if isinstance(x,list):return [substitute(v)for v in x]
        if isinstance(x,dict):return {k:substitute(v)for k,v in x.items()}
        return x
    candidate=substitute(candidate)
    candidate['status']='FINAL_RESULTS_READY_FOR_ROOT_APPROVAL'
    candidate['schema']='APD01.manual_content_final.R1'
    candidate['pending_results']={'new_FullZIP_external_test':'NOT_EXECUTED_YET; referenced externally, not certified in Word'}
    candidate['source_limit']='Closed scientific R04 only; no new FullZIP verification asserted; Root approval required before existing Word helper.'
    candidate['approval_requirements']=['Root review and approval before setting FINAL_RESULTS_APPROVED_FOR_MANUAL',
        'Do not change historical headings or chapters20–31','No future FullZIP hash or verification claim in Word']
    for para in candidate['chapter']:
        if para['style'] in ('Heading2','Heading3'):
            para['text']=' '.join(re.sub(r'[^\w\s]',' ',para['text']).split())
    candidate['chapter'][-1]['text']=('Fuentes: primariosP01–P26; LEX_R01–LEX_R04; acumulación y retorno común; REFERENCIAS_EJECUTADAS_R2; '
        'corrección descriptiva del perímetroN0; ventanas SERVICIO_R01–SERVICIO_R04, corte finalT361114 y par postSTOP. '
        'Las verificaciones de paquetes exactos se consultan externamente; no se anticipa un nuevo FullZIP verificado.')
    candidate['closed_R04_sources']=sources
    assert '{{' not in json.dumps(candidate,ensure_ascii=False)
    assert all(re.fullmatch(r'[\w\s]+',x['text'])for x in candidate['chapter']if x['style']in('Heading2','Heading3'))
    write(HERE/'DATOS_MANUAL_APD01_FINAL_PARA_APROBACION.json',candidate)
    print(json.dumps({'incorporation':sha(HERE/'DATOS_INCORPORACION_APD01.json'),
        'manual_candidate':sha(HERE/'DATOS_MANUAL_APD01_FINAL_PARA_APROBACION.json'),
        'rows':len(rows),'prior_rows_preserved':nold,'new_ticks':0,'Word_authored':False},ensure_ascii=False))

if __name__=='__main__':main()
