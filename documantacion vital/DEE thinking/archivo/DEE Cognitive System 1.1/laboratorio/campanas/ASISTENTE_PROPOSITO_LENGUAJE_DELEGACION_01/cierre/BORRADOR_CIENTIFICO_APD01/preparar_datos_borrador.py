"""Offline scientific draft inputs, immutable P26 cut; no Runtime/native imports."""
import ast,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[1];ROOT=LAB.parents[2];SYSTEM=ROOT/'sistema'
CUT=LAB/'recalculo/ANALISIS_APD_P01_P26_R05'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,data):
    with(HERE/name).open('xb')as f:f.write((json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8'))
def main():
    refs=read(CUT/'REFERENCIAS/ROOT.json');rows=[]
    columns=['vida','tick_del_momento','perfil','funcion_o_metrica','estado_en_ese_momento','numerador','denominador',
        'entradas_solicitadas_del_primario','entradas_aplicadas_del_primario','entradas_rechazadas_del_primario',
        'fuente_relativa_LAB','snapshot_sha256','atribucion','limite']
    def add(life,tick,fun,status,n,d,source,snapshot,attribution,limit,requests=None):
        requests=requests or{}
        rows.append([life,tick,'fisica_directa',fun,status,n,d,requests.get('unique_requested'),requests.get('applied'),requests.get('rejected'),
            source,snapshot,attribution,limit])
    for q in refs['files']:
        life=q['life_id'];tick=q['committed_tick'];source='recalculo/ANALISIS_APD_P01_P26_R05/PRIMARIOS/'+q['primary'];snap=q['snapshot_sha256'];req=q['request_denominators']
        if not life:continue
        for key,label,attr,limit in[
            ('native_numeric_counts','Operaciones numericas nativas preparadas','P0 aritmetico; eleccion lexica aprendida cuando la cadena la utiliza','No algoritmo aprendido; dos operandos0..32 y diferencia afin32'),
            ('prepared_count_counts','Agregacion de muestras de presencia','P0 sensorial y agregador nativo','Dos o tres muestras0/1; no cardinalidad general adquirida'),
            ('integrated_counts','Peticiones integradas con resultado correcto','Forma aprendida; ruta fisica; herramienta o agregador segun emision','Correcto no equivale a barato; todas las iniciativas de peticion son externas')]:
            metric=q[key];den=metric['denominator']
            if not den:continue
            numerator=metric.get('correct',metric.get('arithmetic_correct'))
            add(life,tick,label,'UTILIZADA_EN_ESTE_PRIMARIO',numerator,den,source,snap,attr,limit,req)
            if key=='integrated_counts':
                add(life,tick,'Archivos sinteticos completados','ACTUACION_EXTERNA_DECLARADA',metric['completed'],den,source,snap,
                    'Emision material controla byte; host escribe archivo acotado','completed mide artefacto existente; NO correccion matematica ni utilidad por si solo',req)
        if q['bounded_accumulation_counts']['denominator']:
            m=q['bounded_accumulation_counts'];add(life,tick,'Offset aprendido y acumulacion posterior','UTILIZADA_FINITA',m['correct_cumulative'],m['denominator'],source,snap,
                'Contenido adquirido mediante leccion explicita; propagacion y actualizacion nativas','Cinco oportunidades historicas validadas; contrato agotado; no sexto ensayo fisico ni perdida demostrada',req)
        if q['lexical_uses']:
            m=q['lexical_uses'];add(life,tick,'Emisiones de formas recuperadas','LECTURA_FISICA_COMPROBADA',sum(v['command']in(-1,1)for v in m),len(m),source,snap,
                'Contenido de signos adquirido; codec y consulta preparados','Cuenta usos no palabras nuevas ni replicas independientes',req)
        if q['explicit_reference_experiences']:
            add(life,tick,'Contactos materiales declarados sobre referencia','ASISTENCIA_MATERIAL_DECLARADA',None,len(q['explicit_reference_experiences']),source,snap,
                'Docencia o retorno preparado segun primario; v27 transforma referencia','No decision autonoma acreditada; P18 es readquisicion explicita',req)
    for rev in('R01','R02'):
        data=read(CUT/'LENGUAJE/REFERENCIAS'/(rev+'.json'))
        for q in data['cases']:
            source='recalculo/ANALISIS_APD_P01_P26_R05/LENGUAJE/EVIDENCIA/'+rev+'/'+q.get('primary_file',q.get('primary',''))
            fresh=q.get('correspondence',q.get('acquired_sign_matches',q.get('new_output',q.get('control_outputs',{}))))
            n=fresh.get('numerator',fresh.get('valid'));den=fresh.get('denominator')
            add(q['life_id'],q['tick'],'Correspondencias nuevas '+rev,'ADQUIRIDA_ACCESIBLE'if q['case']in('paired','reversed')else'CONTROL_SIN_ACCESO_NUEVO',n,den,source,q['snapshot_sha256'],
                'Enseñanza emparejada/invertida frente a omitida/desacoplada','Prefijo compartido; ausencia de salida no prueba perdida global')
            old=q.get('old_match_to_R17',q.get('old8_matches',{}))
            add(q['life_id'],q['tick'],'Acceso a asociaciones anteriores '+rev,'COMPROBADO_EN_PANEL',old.get('numerator'),old.get('denominator'),source,q['snapshot_sha256'],
                'Conocimiento de esta vida segun su propia historia','Panel material puede transformar estado; no garantia futura')
    r03=read(CUT/'REFERENCIAS/LEX_R03.json')
    for q in r03['cases']:
        source='recalculo/ANALISIS_APD_P01_P26_R05/FUNCION_LEXICA_R03/'+q['case']+'_01_PRIMARY.json.gz'
        add(q['life_id'],q['tick'],'Historia lexica selecciona funcion numerica','UTILIZADA_CON_OPERANDOS_COMUNES',q['numeric_correct'],q['numeric_denominator'],source,q['snapshot_sha256'],
            'Signo aprendido elige operador nativo preparado bajo transduccion fija','No adquisicion de reglas aritmeticas ni parser español semantico')
        add(q['life_id'],q['tick'],'Panel anterior de diez formas R03','RETENIDO_ACCESIBLE',q['old10_retained'],q['old10_denominator'],source,q['snapshot_sha256'],
            'Uso posterior a tres operaciones en misma vida','Dos ramas opuestas no se fusionan en MAIN')
    r04=read(CUT/'REFERENCIAS/LEX_R04.json')
    for q in r04['cases']:
        source='recalculo/ANALISIS_APD_P01_P26_R05/CURRICULO_LEXICO_R04/'+q['case']+'_01_PRIMARY.json.gz'
        new=q.get('new_association_matches',q.get('new_outputs',{}))
        add(q['life_id'],q['tick'],'total/quita tercera enseñanza','ADQUIRIDA_ACCESIBLE'if q['case']!='omitted'else'OMITIDO_SIN_NUEVA_EMISION',
            new.get('numerator',new.get('valid')),new.get('denominator'),source,q['snapshot_sha256'],
            'Nueva correspondencia dentro de dos clases existentes','No dos nuevos algoritmos, conceptos NSM o crecimiento adquirido')
        for group,label in[('old_first_old10','Diez anteriores ANTES de primera nueva consulta'),('later_panel_old10','Diez anteriores DESPUES de nuevas consultas')]:
            m=q[group];add(q['life_id'],q['tick'],label,'COMPROBADO_EN_PANEL',m['numerator'],m['denominator'],source,q['snapshot_sha256'],
                'Lector comun24 y calendario fijados antes de los datos','Omitido interfiere agrega/resta; no atribuir todo a falta de asociacion')
        m=q['native_regression'];add(q['life_id'],q['tick'],'Regresion SUM/DIFF/COUNT tras nueva enseñanza','FUNCIONES_PREPARADAS_CONSERVADAS',m['correct'],m['denominator'],source,q['snapshot_sha256'],
            'Tres operaciones nativas; lector C fijo','No cobertura exhaustiva de128variables ni estabilidad ilimitada')
    add('ASISTENTE_MAIN',None,'Reserva operativa3900s y nuevas total/quita','EN_CURSO_NO_EVALUADA',None,None,
        'servicio/CONFIGURACION_RESERVA_PROPUESTA_R01.json',None,'Debe utilizar datos reales al cerrar; no hereda resultados auxiliares',
        'No imputar intentos como respuestas, ni3900host como3600no pausados')
    write('DATOS_TABLA_CAPACIDADES.json',{'columns':columns,'rows':rows,'status':'BORRADOR_P26_RESERVA_PENDIENTE','native_ticks_generated':0})
    cfgpath=LAB/'servicio/CONFIGURACION_RESERVA_PROPUESTA_R01.json';cfg=read(cfgpath)
    source_paths=['capacidades/asistente_proposito_01.py','capacidades/lexico_apd_01.py','capacidades/lexico_apd_extendido_02.py',
        'capacidades/lexico_apd_extendido_04.py','capacidades/aritmetica_apd_01.py','capacidades/ruta_adquirida_apd_03.py',
        'capacidades/acumulador_adquirido_apd_01.py','app/servicio_persistente.py','app/access_guard.py','app/lives.py']
    source_checks=[]
    for relative in source_paths:
        p=SYSTEM/relative;tree=ast.parse(p.read_text(encoding='utf-8-sig'))
        source_checks.append({'relative_SYSTEM':relative,'sha256':sha(p),
            'functions':[{ 'name':n.name,'line':n.lineno,'end_line':n.end_lineno}for n in ast.walk(tree)if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))]})
    main=next(q for q in refs['files']if q['primary'].startswith('P26_'))
    coverage={'schema':'APD01.scientific_draft_coverage.R1','status':'BORRADOR_NO_CIERRE_RESERVA','native_ticks_generated':0,
        'root_primaries_in_verified_cut':26,'main_last_examined_complete_cut':{k:main[k]for k in('life_id','committed_tick','snapshot_sha256')},
        'retrospective_recalculation':{'RAW_ROOT':refs['RAW_observations_decoded'],'discrepancies':refs['discrepancies'],
            'auxiliary_lexical_history_cases':13,'independent_biographies_claimed':False},
        'reserve':{'proposal_relative_LAB':'servicio/'+cfgpath.name,'proposal_sha256':sha(cfgpath),'proposal_freeze_status':cfg['freeze_status'],
            'planned_host_seconds':cfg['seconds'],'planned_nominal_events':cfg['nominal_events'],'actual_results':None,
            'families':{k:len(v)for k,v in cfg['families'].items()},
            'new_forms_not_queried_before_SECONDS':cfg['new_forms_reserved_until'],'scheduled_new_lessons':[
                {'at_seconds':v['at_seconds'],'purpose':v['purpose']}for v in cfg['fixed_events']if'new_'in v['purpose']],
            'meaning':'Proposal is not the definitive executed source freeze, measured exposure or achieved acquisition'},
        'attribution_limits':{'Spanish_forms_prepared_before_reserve':6,'Spanish_forms_MAIN_acquired_before_reserve':4,
            'total_context_forms_in_common_reader':12,'native_arithmetic_learned_algorithm':False,'affine_difference_prepared':True,
            'validated_historical_opportunities':5,'declared_protocol_cursor_exhausted':True,'physical_sixth_use_tested':False,
            'physical_loss_after_fifth_demonstrated':False,'no_memory_destruction_claim':True,
            'composition_operator_order_external':True,'general_R2_or_P2':False,'new_NSM_entries_claimed':0,
            'OS_sandbox_certified':False,'operational_history_reads_universally_blocked':False,
            'task_answer_history_lookup_found_in_reviewed_decision_code':False,
            'Store_reads_life_and_journal_for_identity':True,'synthetic_file_action_not_general_OS_control':True},
        'consequence_objective':{'online_completed_definition':'Synthetic artifact exists','online_mathematical_correctness_checked':False,
            'online_common_return':'Prepared price plus4 on noncompletion; excess>2 transduction',
            'offline_mathematical_correctness':'Independent auditor only; never supplied as actor feedback',
            'quality_optimization_or_resistance_to_metric_gaming_proven':False},
        'source_functions_reviewed':source_checks,'not_claimed':['Reserve success','Life finalcut','New MAIN total/quita knowledge','AGI','Autonomous planner','General grammar','Automatic sandbox security']}
    write('COBERTURA.json',coverage)
    print(json.dumps({'rows':len(rows),'columns':len(columns),'root_RAW':refs['RAW_observations_decoded'],'source_files_reviewed':len(source_checks),'native_ticks':0}))
if __name__=='__main__':main()
