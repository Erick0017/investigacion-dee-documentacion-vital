"""Read-only ancestor audit; update only the new CPC7 capability map.

Archive identity, a verified selected member, an executed adaptation and an
exact historical reproduction are separate statements. Historical mains are
never launched. Documentary extracts do not become executable proof.
"""
import ast,collections,hashlib,json,os,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CASES=ROOT.parents[1];DOC=CASES.parent.parent


def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def put(p,x):
    p=Path(p);q=p.with_name(p.name+'.pending.'+str(os.getpid()))
    q.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n');os.replace(q,p)


def source_closure(files):
    """Conservative local-import closure, read as syntax without loading DEE."""
    found=set(files);queue=[ROOT/f for f in files if f.endswith('.py')]
    while queue:
        current=queue.pop()
        if not current.exists():continue
        tree=ast.parse(current.read_text(encoding='utf-8-sig'))
        names=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):names.extend(a.name for a in node.names)
            elif isinstance(node,ast.ImportFrom) and node.module:names.append(node.module)
        for name in names:
            rel=Path(*name.split('.'));candidates=[current.parent/rel.with_suffix('.py'),ROOT/'src'/rel.with_suffix('.py')]
            for candidate in candidates:
                if candidate.is_file() and candidate.resolve().is_relative_to((ROOT/'src').resolve()):
                    value=candidate.relative_to(ROOT).as_posix()
                    if value not in found:found.add(value);queue.append(candidate)
                    break
    return sorted(found)


def capacity65_reference():
    p=ROOT/'resultados/reference_capacity65_01/REFERENCE.json'
    if not p.exists():return None
    ref=read(p);source=ROOT/'src/repertoire_reference.py'
    if ref.get('same_source_as_published_CPC5')!=sha(source):raise ValueError('K65 reference source changed')
    children=[]
    for result in ref['results']:
        child=p.parent/result['primary']
        if sha(child)!=result['primary_sha256']:raise ValueError('K65 child primary changed')
        primary=read(child);by_round={}
        for row in primary.get('readouts',[]):
            key=str(row['round']);r=by_round.setdefault(key,{'queries':0,'receipt_status_counts':{},'decoder_valid':0})
            r['queries']+=1;status=row.get('receipt',{}).get('status','UNREPORTED')
            r['receipt_status_counts'][status]=r['receipt_status_counts'].get(status,0)+1
            r['decoder_valid']+=row.get('decoder_valid') is True
        for key,r in by_round.items():
            r['recalculated_rejected_queries']=sum(n for state,n in r['receipt_status_counts'].items() if state.startswith('rejected'))
            r['published_rejected_queries']=result['calculations'].get(key,{}).get('rejected')
            r['published_rejected_count_matches_receipts']=r['published_rejected_queries']==r['recalculated_rejected_queries']
        children.append({'file':child.relative_to(ROOT).as_posix(),'sha256':sha(child),'id':result['id'],
          'published_calculations_unchanged':result['calculations'],'audit_admission_by_round':by_round,
          'checkpoint_restoration_equal':result['checkpoint_restoration_equal'],
          'audit_note':'Frozen source calculations and actual query receipts are separate. In the no-event control, rejected=0 in the old summary differs from65RejectedOccupied per round; no source or primary was rewritten.'})
    return {'state':'REPRODUCCION_TECNICA_DOS_PREPARACIONES_K65_N131','native_run_performed':True,
      'technical_preparations':ref['technical_preparations'],'integrated_in_central_U0':False,
      'full_historical_capacity_campaign_reproduced':False,'source':source.relative_to(ROOT).as_posix(),
      'source_sha256':sha(source),'reference_file':p.relative_to(ROOT).as_posix(),'reference_sha256':sha(p),
      'children':children,'scope':ref['scope'],
      'note':'Dos preparaciones históricas seleccionadas, con tres rondas cada una. No son65significadosNSM ni65correspondencias integradas enU0.'}


SELECT={
 'CP02_B':(['CPC3'],['/CP02_B/']),
 'CPC3_MAIN_AND_COMPARISON':(['CPC3'],['/core/entity.py','/core/central_comparison.py','/core/comparison_entity.py','/central_discovery/open_changed/MEASUREMENTS.json']),
 'CPC3_POLICY':(['CPC3','ING01'],['/core/revisable_selection.py','/core/policy_session.py','run_r14_feedback_holdout.py','DEE_REUSABLE_FEEDBACK_LOOP.json']),
 'SEM01':(['CPC3'],['/SEM01_SIGNIFICADO_ADQUIRIDO/']),
 'CPC4_AB':(['CPC4'],['/INFORME.md','/CAPACIDADES.json','recipe_v3.py','session_v3.py']),
 'CPC4_REGULATION_ABCD':(['CPC4'],['regulated_session.py','regulated_experiment.py','regulated_curriculum.py','/RETENCION.json']),
 'CPC5_COMPOUND':(['CPC5'],['/src/compound.py','/src/network.py','/src/relative_compound.py','/revision/LECTURA_PROVISIONAL.md']),
 'CPC5_CAPACITY65':(['CPC5'],['/src/capacity.py','/capacity_discovery/INDEX.json','/capacity_confirmation/INDEX.json']),
 'CPC5_LONGITUDINAL65':(['CPC5'],['/src/capacity_longitudinal.py','/capacity_longitudinal/INDEX.json']),
 'CPC5_ORDER_AND_DIALOGUE':(['CPC5'],['/src/order_stream.py','/src/ordered_composition.py','/src/network_dialogue.py','/src/network_session.py']),
 'CPC6_INTEGRATED':(['CPC6'],['/src/integrated.py','/src/order_memory.py','/src/life.py','/revision/LECTURA_PROVISIONAL.md']),
 'CPC6_TWO_FORMS':(['CPC6'],['/src/word_bus.py','/src/order_language.py','/configuraciones/R03_WORD_BUS_V2.json']),
 'CPC6_RETENTION_CAUSAL':(['CPC6'],['/src/consolidation_controls.py','/src/word_bus_controls.py','/src/retention_access.py','/src/late_access.py','RETENTION_SYNTHESIS.json','LATE_ACCESS_CALCULATIONS.json']),
 'CPC6_ARCHITECTURES':(['CPC6'],['/src/architecture_screen.py','/src/architecture_bridge_delayed.py','ARCHITECTURES_AND_DIALOGUE.json']),
 'CORE06_RELEARNING':(['CORE06'],['C6D04','c6d04','LEARNING_CAUSAL_MECHANISM.md']),
 'CORE07_REPROGRAMMING':(['CORE07'],['W_REPROGRAMMING.json','run_c7h03','LEARNING_TRANSFER.md']),
 'ING01_R04_R14':(['ING01'],['run_r04','run_r14','DEE_REUSABLE_FEEDBACK_LOOP.json','DEE_NATIVE_RESET_REPLENISHMENT.json']),
 'ING02_RELATIVE':(['ING02'],['paired_relative_apparatus','run_d09','TEMPORAL_HISTORY','DISTRIBUTED_MEMORY']),
 'ING05_06_CONTEXT':(['ING05','ING06'],['SCIENTIFIC_REPORT.md']),
 'PROCESOS_OBSERVERS':(['PROC01','PROC02','PROC03'],['.md','CONTRACT.json','SUMMARY.json']),
 'PRODUCT4_CONTRACT':(['PRODUCT4'],['PRODUCT_CONTRACT.json','API_AND_SCOPE.md','cognitive.hpp','informative.hpp','integrated_protocols.hpp','test_cognitive_api.py'])}

NEED=['resultados/endogenous/comparison_confirm/NEED_C02_SOURCE_NONE/MEASUREMENTS.json',
 'resultados/endogenous/comparison_confirm/NEED_C03_SOURCE_UNPAIRED/MEASUREMENTS.json',
 'resultados/endogenous/comparison_confirm/NEED_C07_FORMED_QUESTION_CUT/MEASUREMENTS.json',
 'resultados/endogenous/comparison_confirm/NEED_C08_FORMED_QUESTION_SHAM/MEASUREMENTS.json',
 'resultados/endogenous/comparison_confirm/NEED_H01_OPPOSITE_HISTORY_NEW_LOCATION/MEASUREMENTS.json']
CENTRAL=['resultados/central/PILOT_01/MEASUREMENTS.json','resultados/central/PILOT_02/MEASUREMENTS.json']
CAPACITY=['resultados/native_direct/ordinary_DIR_101_paired/MEASUREMENTS.json',
 'resultados/native_direct/ordinary_DIR_101_unpaired/MEASUREMENTS.json',
 'resultados/native_direct/double_teacher_DIR_101_paired/MEASUREMENTS.json',
 'resultados/native_direct/symmetric_counterflow_DIR_101_paired/MEASUREMENTS.json',
 'resultados/native_direct/symmetric_counterflow_DIR_211_paired/MEASUREMENTS.json']
SELECTIVE=['resultados/selective_native/SEL_P21_AB/MEASUREMENTS.json',
 'resultados/selective_native/SEL_C21_CUT/MEASUREMENTS.json','resultados/selective_native/SEL_C22_SHAM/MEASUREMENTS.json',
 'resultados/selective_native/SEL_N21_UNPAIRED/MEASUREMENTS.json','resultados/selective_native/SEL_N22_OMITTED/MEASUREMENTS.json']

ADAPT={
 'CPC3_MAIN_AND_COMPARISON':('ADAPTADO_E_INTEGRADO_PARCIAL',NEED+CENTRAL,'Comparación física reflejada adaptada a pregunta19/información24 y a U0 nuevo; no reproducción del marcador84 ni de todo CPC3.'),
 'CPC3_POLICY':('ADAPTADO_COMPONENTE_ANTECEDENTE',NEED,'Se reutiliza el antecedente de comparación/selección finita derivado deR14; no se ha reproducido aquí FinitePolicySession completa ni una política renovable de utilidad.'),
 'SEM01':('MECANISMO_HEREDADO_ADAPTADO_NO_FLUJO_EXACTO',CAPACITY+SELECTIVE,'Asociación por encuentro emparejado y consulta de forma sola reutilizadas; el calendario17/45/84/112 y hábitat SEM01 no se reprodujeron.'),
 'CPC4_AB':('ADAPTADO_MECANISMO_TRANSPORTE_Y_RECEPTOR',NEED,'Información de una fuente adquirida viaja y es utilizada por U0 en un Runtime; no se presenta como reproducción de la pareja A/B histórica completa.'),
 'CPC4_REGULATION_ABCD':('ADAPTADO_CONTRAFLUJO_FINITO',CAPACITY[3:],'Contraflujo físico preparado para revisión; no red A/B/C/D ni elección de regular aprendida por consecuencias.'),
 'CPC5_CAPACITY65':('ADAPTADO_K16_NO_REPRODUCIDO_K65',CAPACITY+SELECTIVE,'CPC7 ejecutó8→16, revisión localM1/M2 y retención selectiva. K65,N131 de la referencia no se reejecutó en este corte.'),
 'CPC5_LONGITUDINAL65':('ADAPTADO_CURRICULO_8_MAS_8_NO_REPRODUCIDO_32_MAS_33',CAPACITY,'Intercalación y retención del currículo actual8+8, no la trayectoria histórica32+33 de65.'),
 'CPC5_ORDER_AND_DIALOGUE':('ADAPTADO_SOLO_COMPONENTE_ORDEN',CENTRAL+NEED,'El cuerpo relativo sensible al orden participa en U0. No se reivindica diálogo de1..4compuestos ni composición completa CPC5.'),
 'CPC6_INTEGRATED':('ADAPTADO_E_INTEGRADO_PARCIAL',CENTRAL+SELECTIVE,'Dos candidatosU0 y la realización selectiva integran mecanismos heredados. No se atribuyen todas las funciones, brazos ni resultados de CPC6 a la nueva preparación.'),
 'CPC6_RETENTION_CAUSAL':('ADAPTADO_METODO_DIAGNOSTICO',SELECTIVE[1:],'Forks y shams actuales contrastan acceso y función; no reproducen los ensayos97/162 ni localizan una memoria universal.'),
 'ING01_R04_R14':('ADAPTADO_R14_REFERENCIA_R04',NEED,'La comparación/selección finitaR14 es antecedente de la adaptación endógena; el osciladorR04 y su renovación no se dan por integrados en un aprendiz ilimitado.'),
 'ING02_RELATIVE':('ADAPTADO_COMPONENTE_RELATIVO',CENTRAL+SELECTIVE,'Relación soportada y expresión de orden por experiencias reales; nueva geometríaN67 heredada víaCPC6, no reproducción íntegra deING02.'),
 'PRODUCT4_CONTRACT':('INSTRUMENTO_CONGELADO_UTILIZADO',CENTRAL+['resultados/reference_order_01/REFERENCE.json'],'WHL4.0/PYD yv27 se verifican por identidad y ejecución. No se modificó producto ni se reejecutó toda su suite histórica.')}


def archive_path(a):
    sid=a['id'];folder=CASES if sid in('CPC3','CPC4','CPC5','CPC6') else CASES.parent/'4.0' if sid=='PRODUCT4' else DOC/('ingenieria' if sid.startswith('ING') else 'cores' if sid.startswith('CORE') else 'procesos')
    return folder/a['file']


def main():
    target=ROOT/'revision/MAPA_CPC1_A_6.json';m=read(target);original=sha(target);manifest=read(ROOT/'genealogia/SOURCE_MANIFEST.json')
    archives={};opened={};verified=[];problems=[]
    try:
        for a in manifest['archives']:
            path=archive_path(a);actual=sha(path)
            if actual!=a['sha256']:raise ValueError('Canonical archive changed: '+a['id'])
            archives[a['id']]={**a,'identity_verified_in_this_audit':True};opened[a['id']]=zipfile.ZipFile(path)
        for r in manifest['selected_members']:
            z=opened[r['source_id']];data=z.read(r['member']);h=hashlib.sha256(data).hexdigest();local=ROOT/r['file']
            if h!=r['member_sha256'] or sha(local)!=h:raise ValueError('Selected member or copy mismatch: '+r['file'])
            verified.append({**r,'status':'ARCHIVO_MIEMBRO_Y_COPIA_LOCAL_VERIFICADOS',
              'role':'source_code' if local.suffix=='.py' else 'historical_result_or_report',
              'archive_identity_verified':True,'member_verified':True,'local_copy_verified':True})
        docs=[]
        for d in manifest['documentary_extracts']:
            local=ROOT/d['file'];path=(CASES.parent/'4.0'/d['source_file']) if d['source_file'].startswith('DEE_thinking') else DOC/'FISICA DEE Y PROCESAMIENTO NATIVO'/d['source_file']
            if sha(local)!=d['hash'] or sha(path)!=d['source_sha256']:raise ValueError('Document or extract changed: '+d['file'])
            with zipfile.ZipFile(path) as z:xml_hash=hashlib.sha256(z.read('word/document.xml')).hexdigest()
            docs.append({**d,'source_container_type':'DOCX_DOCUMENTAL','source_member':'word/document.xml','source_member_sha256':xml_hash,
              'status':'ORIGINAL_Y_EXTRACTO_DOCUMENTAL_VERIFICADOS_NO_EJECUTABLES'})
        capacity_reference=capacity65_reference()
        for row in m['rows']:
            rid=row['id'];is_cp01=rid.startswith('CP01_')
            ids,tokens=(['CPC3'],['/CP01_C08/']) if is_cp01 else SELECT.get(rid,([],[]))
            evidence=[r.copy() for r in verified if r['source_id'] in ids and any(t in r['member'] for t in tokens)]
            if rid in('PROCESAMIENTO_NATIVO','FISICA_META_ROSETTA'):
                keyword='PROCESAMIENTO' if rid=='PROCESAMIENTO_NATIVO' else 'FISICA'
                evidence=[d.copy() for d in docs if keyword in d['file']]
            elif rid=='PRODUCT4_CONTRACT':evidence.extend(d.copy() for d in docs if any(x in d['file'] for x in('MAESTRO','MANUAL')))
            row['evidence']=evidence;row['source_archives']=[{'id':sid,'file':archives[sid]['file'],'sha256':archives[sid]['sha256'],'status':'HASH_ARCHIVO_VERIFICADO'} for sid in ids]
            row['historical_API_or_code_as_reported']=row.get('historical_API_or_code_as_reported',row.get('API_or_code',[]))
            code_files=[e['file'] for e in evidence if e['file'].endswith(('.py','.hpp'))]
            row['API_or_code']=code_files or [e['file'] for e in evidence]
            row['historical_controls']={'reported':row['controls'],'status':'CONTROLES_DEL_ANTECEDENTE_NO_REEJECUTADOS_POR_ESTA_AUDITORIA',
                 'evidence_files':[e['file'] for e in evidence]}
            row['historical_execution_command']={'status':'COMANDO_HISTORICO_DEPENDE_EXPEDIENTE_EXTERNO','command':None,
                 'reason':'Selección de referencia no es un expediente histórico ejecutable completo. No se lanzó su main ni se afirma reproducción.'}
            row['state']={'reference_selected':bool(evidence),'source_identity_verified':bool(evidence),
                'verified_source_member_or_document':bool(evidence),'reproduced_in_CPC7':False,'adapted_in_CPC7':False,'integrated_in_CPC7':False}
            row['CPC7_state']='REFERENCIA_DOCUMENTAL_CON_MIEMBROS_VERIFICADOS';row['CPC7_evidence']=[];row['CPC7_commands']=[]
            if is_cp01:row['verified_code_anchor']='fronts.py::'+rid.replace('CP01_','')
            if rid in ADAPT:
                state,paths,scope=ADAPT[rid];row['CPC7_state']=state;row['CPC7_scope']=scope
                row['state']['adapted_in_CPC7']=rid!='PRODUCT4_CONTRACT';row['state']['integrated_in_CPC7']=rid in('CPC3_MAIN_AND_COMPARISON','CPC6_INTEGRATED','PRODUCT4_CONTRACT','SEM01')
                for name in paths:
                    p=ROOT/name
                    if not p.exists():problems.append({'row':rid,'missing_CPC7_evidence':name});continue
                    row['CPC7_evidence'].append({'file':name,'sha256':sha(p),'schema':read(p).get('schema'),'status':'PRIMARIO_CPC7_EXISTENTE_ADAPTACION_NO_REPRODUCCION_TOTAL'})
            if rid in('CPC5_CAPACITY65','CPC5_LONGITUDINAL65'):
                row['CPC7_K65_reproduction']={'state':'NO_REPRODUCIDO_65_EN_CPC7','native_run_performed':False,
                  'code_available':'src/repertoire_reference.py','note':'Fuente/configuración histórica preservada; no confundir un código disponible con una corridaN131K65.'}
                if capacity_reference and rid=='CPC5_CAPACITY65':
                    row['CPC7_K65_reproduction']=capacity_reference
                    row['CPC7_state']='ADAPTADO_K16_Y_REFERENCIA_K65_REPRODUCIDA_PARCIAL'
                    row['state']['technical_reference_reproduced_in_CPC7']=True
                    row['CPC7_scope']='CPC7 ejecutó8→16 y revisiónM1/M2; además se reprodujeron dos preparaciones históricasK65,N131 como referencia técnica separada, no incorporadas aU0 ni toda la campaña de capacidad.'
                elif capacity_reference:
                    row['CPC7_K65_reproduction']={'state':'TRAYECTORIA_LONGITUDINAL_32_MAS_33_NO_REPRODUCIDA',
                      'native_run_performed':False,'related_technical_capacity_reference':capacity_reference['reference_file'],
                      'note':'La referencia técnicaK65 existe, pero no reejecuta la adquisición longitudinal32+33.'}
            if rid=='ING01_R04_R14':row['subcomponents']={'R04':'REFERENCIA_NO_REPRODUCIDA','R14':'ANTECEDENTE_ADAPTADO_A_COMPARACION_Y_SOLICITUD_FINITA'}
            row['evidence_scope']='Documento/código/primario referenciado conserva su tipo; un miembro verificado no certifica todas las afirmaciones históricas.'
            if not evidence:problems.append({'row':rid,'missing_verified_historical_member_or_document':True})
        # Only commands whose scripts/configurations and exact prior command
        # records are present are advertised; no historical runner is invented.
        for row in m['rows']:
            rid=row['id']
            if rid in ADAPT and rid!='PRODUCT4_CONTRACT':
                command='python -I -B src/plasticity.py --stream configuraciones/comparadores/fixtures_v1/RESERVED/DIR_101_paired/STREAM.json --revision-method symmetric_counterflow --out resultados/REPRODUCCION_NUEVA_M2' if rid in('SEM01','CPC4_REGULATION_ABCD','CPC5_CAPACITY65','CPC5_LONGITUDINAL65') else 'python -I -B src/endogenous/run_need.py --config configuraciones/endogenous/comparison_confirm.json --out resultados/REPRODUCCION_NUEVA_NEED'
                files=['src/plasticity.py','src/repertoire_reference.py','src/update_methods.py','configuraciones/comparadores/fixtures_v1/RESERVED/DIR_101_paired/STREAM.json'] if command.startswith('python -I -B src/plasticity') else ['src/endogenous/run_need.py','src/endogenous/comparison_need.py','configuraciones/endogenous/comparison_confirm.json']
                files=source_closure(files+['runtime/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'])
                absent=[f for f in files if not (ROOT/f).exists()]
                row['CPC7_commands'].append({'command':command,'status':'COMANDO_CPC7_INCLUIDO' if not absent else 'COMANDO_NO_CERTIFICADO_DEPENDENCIA_FALTANTE',
                    'required_files':[{'file':f,'sha256':sha(ROOT/f)} for f in files if (ROOT/f).exists()],'missing_files':absent,
                    'scope':'Reproduce un mecanismo adaptado actual, no toda la capacidad histórica. Usar una salida nueva y entorno conWHLoficial instalado.'})
            if rid in('CPC6_INTEGRATED','ING02_RELATIVE','PRODUCT4_CONTRACT'):
                ref=ROOT/'resultados/reference_order_01/REFERENCE.json'
                if ref.exists():row['component_reference_reproduction']={'file':'resultados/reference_order_01/REFERENCE.json','sha256':sha(ref),
                    'status':'REPRODUCCION_TECNICA_COMPONENTE_ORDEN_AB_BA','trajectories':2,'scope':'Sólo cuerpo relativo y emisiónT5; no todo CPC6,ING02 o producto4.0.'}
                command='python -I -B src/reference_smoke.py --out resultados/REPRODUCCION_NUEVA_ORDEN'
                files=source_closure(['src/reference_smoke.py','runtime/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'])
                row['CPC7_commands'].append({'command':command,'status':'COMANDO_CPC7_INCLUIDO','required_files':[{'file':f,'sha256':sha(ROOT/f)} for f in files],
                    'scope':'Sólo reproducción técnica del componente de orden heredado, no campaña histórica completa.'})
            if rid=='CPC6_INTEGRATED':
                files=source_closure(['src/central.py','configuraciones/central/PILOT_02.json',
                    'configuraciones/comparadores/fixtures_v1/PILOT/DIR_23_paired/STREAM.json','runtime/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'])
                row['CPC7_commands'].append({'command':'python -I -B src/central.py --case configuraciones/central/PILOT_02.json --stream configuraciones/comparadores/fixtures_v1/PILOT/DIR_23_paired/STREAM.json --out resultados/REPRODUCCION_NUEVA_U0',
                    'status':'COMANDO_CPC7_INCLUIDO','required_files':[{'file':f,'sha256':sha(ROOT/f)} for f in files],
                    'scope':'CandidatoU0CPC7preparaciónV2; conserva sus fallos y no equivale a todas las funciones CPC6.'})
            if rid=='CPC5_CAPACITY65' and capacity_reference:
                files=source_closure(['src/reproduce_capacity65.py','src/repertoire_reference.py',
                    'genealogia/CPC5/ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO/configuraciones/capacity_confirmation.json',
                    'runtime/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'])
                row['CPC7_commands'].append({'command':'python -I -B src/reproduce_capacity65.py --out resultados/REPRODUCCION_NUEVA_REFERENCIA_K65',
                    'status':'COMANDO_CPC7_INCLUIDO','required_files':[{'file':f,'sha256':sha(ROOT/f)} for f in files],
                    'scope':'Dos preparaciones históricasK65seleccionadas, no aprendizaje65enU0 ni todas las variantes publicadas.'})
            row['CPC7_operational_sources']=sorted({f['file'] for c in row['CPC7_commands'] for f in c['required_files'] if f['file'].endswith('.py')})
        m['source_manifest']={'file':'genealogia/SOURCE_MANIFEST.json','sha256':sha(ROOT/'genealogia/SOURCE_MANIFEST.json')}
        m['audit']={'schema':'CPC7.genealogy_map.audit.v1','before_first_audit_map_sha256':m.get('audit',{}).get('before_first_audit_map_sha256',original),
            'audit_source_sha256':sha(__file__),'rows':len(m['rows']),'canonical_archives_verified':len(archives),'selected_members_and_local_copies_verified':len(verified),
            'documentary_extracts_verified':len(docs),'historical_mains_executed':False,'new_native_runs_performed':False,
            'missing_or_unresolved':problems,'coverage_warning':'A verified archive name/hash alone is not a recovered member or a reproduced capability. Some reference rows intentionally include only code/reports, not a complete local historical runner or every primary measurement.'}
        m['pending']={'historical_exact_reproductions':'Only separately recorded order-body and two selected finiteK65 technical references are reproduced, not their complete historical campaigns; reference status is not a failed capability.',
            'K65_CPC7':'REFERENCIA_TECNICA_DOS_PREPARACIONES_REPRODUCIDA_NO_INTEGRADA_EN_U0' if capacity_reference else 'NO_REPRODUCIDO_65_EN_CPC7','public_universal_command':'INCLUIDO: ejecutar.py referencia/vida/control/demo/demo-repertorio/recalcular with finite operation contracts; public_recalculation_01 records an executed branch. Per-mechanism commands above remain scoped.',
            'unresolved_members_or_local_evidence':problems}
        put(target,m);print(json.dumps({'rows':len(m['rows']),'verified_members':len(verified),'archives':len(archives),'unresolved':len(problems)}))
    finally:
        for z in opened.values():z.close()


if __name__=='__main__':main()
