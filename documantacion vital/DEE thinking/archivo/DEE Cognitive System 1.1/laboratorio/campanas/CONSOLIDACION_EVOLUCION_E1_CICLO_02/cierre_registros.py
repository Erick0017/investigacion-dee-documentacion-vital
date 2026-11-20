"""Current-state documentation from complete saved bytes; zero native ticks.
Updates generated continuity data, preserving the previous generated editions.
No Runtime, native engine, external simulator or participant is constructed.
"""
from pathlib import Path
import datetime,hashlib,importlib.util,json,shutil,time
L=Path(__file__).resolve().parent;R=L.parents[2];S=R/'sistema';E=R/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
sp=importlib.util.spec_from_file_location('snapshot_only',S/'capacidades/observador_causal_retrospectivo_01.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def backup(p,name):
    q=L/name
    if p.exists()and not q.exists():shutil.copy2(p,q)
now=datetime.datetime.now(datetime.timezone.utc).isoformat();budget=json.loads((L/'PRESUPUESTO.json').read_bytes());assert time.monotonic()<budget['monotonic_deadline']
freeze=E/'FIN_EXPERIMENTAL.json'
if not freeze.exists():save(freeze,{'utc':now,'monotonic':time.monotonic(),'native_phase_closed':True,'last_native_operation':'C02_SEPOP_362_USO_TRAS_APRENDER; subsequent save/state364 has0ticks','clock_not_restarted':True,'budget':budget})
scopes={
 'E1_SOCIAL_11':('PREDETERMINADO_PROTEGIDO','Dominio heredado anterior: cuatro formas sociales y comparadores documentados; sin sondas nuevas C2. No hereda capacidades de otros perfiles.',None),
 'E1_CICLO02_MAIN':('CONTINUACION_PRINCIPAL_REAL','21/21 acciones útiles de puerta en su propia historia. Mensaje negativo actual utilizable; antiguo positivo pierde acceso tras nueva comunicación. Futuro adverso conservado.','C02_MAIN_175_EXTERNO'),
 'E1_CICLO02_SEPARACION_TRIPLE_01':('COMPLEMENTO_OPERATIVO_ACOTADO','Tres códigos físicamente separados: positivo anterior, contribución negativa recuperada y mensaje lateral positivo nuevo. Se usan después de adquirir desgaste1 y de dos comparaciones anteriores. P0/P1, no P2.','C02_SEPOP_362_USO_TRAS_APRENDER'),
 'E1_CICLO02_RETENCION_01':('COMPLEMENTO_DE_CONSERVACION','Dos códigos anteriores usados antes y después de nueva consecuencia escalar R87→88; comparadores anteriores y continuidad externa. No incorpora actualizaciones de ramas divergentes.','C02_FINAL_320_USO'),
 'E1_CICLO02_COMUNICACION_01':('VARIANTE_SOCIAL_OPERATIVA','Actualización social protegida con desvío de productos; nuevo24 utilizado en dos procesos y consulta final. Perdió acceso al antiguo positivo. Conserva referencia de puerta y dos comparaciones anteriores.','C02_FINAL_323_USO'),
 'E1_CICLO02_LATERAL_LOCAL_01':('EXPERIMENTAL_CON_FALLOS_CONSERVADOS','Nuevo código lateral positivo sigue utilizable; positivo anterior perdió acceso. Primera coexistencia comprobada, no acumulación estable ni solución de la expansión tardía.','C02_FINAL_326_USO'),
 'C02_CAPAS_210_OPERATIVO_R2':('ACCESO_P0_P1_DE_DOS_CAPAS','Dos consultas comunes y cinco usos reales del positivo anterior sin reenseñanza ni reparación posterior. Recurso finito; no nueva iniciativa P2. Episodio externo cerca de su límite.','C02_CAPAS_217_CONTINUACION'),
 'E1_SELECTOR_CONSERVADO_C02':('SELECTOR_APRENDIDO_CONSERVADO','EstadoY140 en el corte3312, conservado como fuente exacta de bifurcación. No aprendizaje nuevo por importación ni selector actual de MAIN.',None),
 'C02_SELECTOR_USO_151':('SELECTOR_FINITO_UTILIZADO','Una continuación normal emite acciónXY140 en3431; otros ensayos pierden acceso. No generalizar estabilidad ni competencia de control.',None),
 'E1_INTEGRADO_MAIN':('FUTURO_ADVERSO_IC01_PROTEGIDO','T3899 adverso anterior intacto. No reemplazado por un futuro favorable.',None),
 'E1_INTEGRADO_CONTINUABLE_01':('CONTINUIDAD_IC01_ADMITIDA','Estado aprendido histórico16485, código social y referencia física, sin trasladar conocimiento de nuevas ramas.',None),
 'E1_INTEGRADO_RECUPERACION_01':('PADRE_IC01_ADMITIDO','Estado17155 con recuperación asistida y puente completo. Fue elegido antes de evaluar MAIN.',None),
 'E1_CICLO02_CORTE_VALIDADO_20927':('BIFURCACION_PREVIA_IDENTIFICADA','Corte creado antes de las nuevas actualizaciones adversas. Padre de alternativas; no rebobinado de MAIN.',None)
}
rows=[];maps=[]
for name,(status,scope,last_id)in scopes.items():
    p=S/'estado/vidas'/name/'VIDA.json';d=json.loads(p.read_bytes());path=S/d['snapshot'];x=m.Snapshot(path)
    assert x.encoded_sha256==d['snapshot_sha256']and x.tick==d['physical']['tick']
    assert m.sha(m.pbytes(x.raw))==d['physical']['RAW_sha256']and m.sha(m.pbytes(x.clocks))==d['physical']['clocks_sha256']
    bridge=None;gate=None
    if 'DEE.Cognitive.System.1.1.IC01.external.v1'in x.metadata:bridge=json.loads(json.loads(x.metadata['DEE.Cognitive.System.1.1.IC01.external.v1'])['bridge_json'])
    if 'DEE.Cognitive.System.1.1.CICLO02.gate.v1'in x.metadata:gate=json.loads(json.loads(x.metadata['DEE.Cognitive.System.1.1.CICLO02.gate.v1'])['environment_json'])
    social=[]
    if bridge and bridge.get('social_ports'):
        for b in bridge['social_ports']:
            v=x.observation(b['target']);q=v['state']==1 and v['semantic']==1 and v['s_reg']>0 and v['direction']==[b['sign'],0,0]
            social.append({'bank':b['sign'],'site':b['target'],'read':v,'qualified':q,'phase_eligible':x.tick%67==3})
    native_gate=None
    if gate:
        site=[49,(35+(x.tick-22)%67)%67,35];native_gate=x.observation(site)
        assert native_gate['state']==1 and native_gate['s_reg']==gate['resistance']+5 and native_gate['direction']==[0,1,0],('Gate current state',name,native_gate,gate['resistance'])
    meaningful=next((o for o in reversed(d.get('operations',[]))if o.get('kind')not in('EXPLICIT_CHECKPOINT','CANDIDATE','EXACT_FORK','DIAGNOSTIC_COPY')),None)
    row={'life_id':name,'world_id':d.get('world_id'),'profile':d['profile'],'branch':d['branch'],'parent':d.get('parent'),'tick':x.tick,'N':x.N,
         'snapshot':d['snapshot'],'snapshot_sha256':x.encoded_sha256,'snapshot_encoded_bytes':x.encoded_bytes,'native_state_complete':True,
         'physical':d['physical'],'state_zero_RAW_nonzero':sum(bool(v)and not(v&0xffffffff)for v in x.raw),
         'pending_inputs':x.pending,'interfaces':len(x.channels),'native_backend_code':x.backend,'native_threads':x.threads,
         'current_status':status,'current_scope':scope,'latest_functional_access_primary':last_id,
         'fixed_social_readers_current':social,'native_gate_reference_current':native_gate,
         'gate_environment_instrument':None if not gate else{k:gate[k]for k in('name','resistance','index','reference_phase','comparison_phase','next_earliest_tick')},
         'external_progress':None if not bridge else{'environment':bridge['environment']['schema'],'index_in_current_episode':bridge['index'],'maximum_steps':200,
               'remaining_steps_without_explicit_reset':200-int(bridge['environment']['elapsed']),'readout':bridge['readout'],'feedback':bridge['feedback'],'reader':bridge['reader'],
               'last_motor_tick':bridge.get('last_motor_tick'),'last_feedback_input_tick':bridge.get('last_feedback_input_tick'),
               'scope':'Bridge is external instrumentation; exact state/RNG/queues remain in the complete native snapshot metadata.'},
         'last_operation':None if not meaningful else{'kind':meaningful['kind'],'before_tick':meaningful.get('before',{}).get('tick'),'after_tick':meaningful.get('after',{}).get('tick')},
         'record_source':str(p.relative_to(R)),'record_source_sha256':sha(p),'knowledge_is_not_the_whole_library':True}
    rows.append(row)
    maps.append({'id':name,'parent':d.get('parent'),'kind':'EXACT_PHYSICAL_PREFIX_AND_DECLARED_FUTURE','snapshot':d['snapshot'],'sha256':d['snapshot_sha256']})
protected=next(r for r in rows if r['life_id']=='E1_SOCIAL_11');adverse=next(r for r in rows if r['life_id']=='E1_INTEGRADO_MAIN')
assert protected['snapshot_sha256']=='51e2ec6a41f906607848c003c6a22e3e33690f57d20dcae90c8dbbc7ab9ad396'
assert adverse['snapshot_sha256']=='a1846c45abe0c7c64a74b9f7c19c6cc90384f380744653a52c7184dc96800f9c'
assert len([z for z in next(r for r in rows if r['life_id']=='E1_CICLO02_SEPARACION_TRIPLE_01')['fixed_social_readers_current']if z['qualified']])==3
active=json.loads((S/'estado/ACTIVO.json').read_bytes())
out={'campaign':'CONSOLIDACION_EVOLUCION_E1_CICLO_02','updated_utc':now,'native_phase_closed':True,'analysis_and_seal_state':'LOCAL_RESULTS_FINAL; consult the separately sealed exact-ZIP external verification',
 'software_version':'1.1.0','engine':'DEE thinking4.5.0/v27 frozen','python_executable':json.loads((E/'INICIO_Y_PADRE.json').read_bytes())['python'],
 'protected_default':'E1_SOCIAL_11','active_pointer':active,'protected_unchanged':True,'original_adverse_unchanged':True,
 'principal_life':'E1_CICLO02_MAIN','recommended_bounded_complement':'E1_CICLO02_SEPARACION_TRIPLE_01','lives':rows,'genealogy':maps,
 'commands':[{'purpose':'estado pasivo','argv':['integrado-estado','--vida','E1_CICLO02_SEPARACION_TRIPLE_01']},
             {'purpose':'uso real que cambia estado','argv':['integrado-externo','--vida','E1_CICLO02_SEPARACION_TRIPLE_01','--pasos','1']},
             {'purpose':'guardar','argv':['guardar','--vida','E1_CICLO02_SEPARACION_TRIPLE_01']},
             {'purpose':'bifurcar sin reemplazar el pasado','argv':['bifurcar','E1_CICLO02_SEPARACION_TRIPLE_01','MI_NUEVA_RAMA','--modalidad','CANDIDATE']}],
 'host_assistance':'Geometry, interfaces, fixed opportunity/calendar, content-free resources, scalar external-world law, transduction and decoder are prepared. Native acquisition/use are history dependent. No P2 initiation demonstrated.',
 'known_limits':'New private52 in330 loses lateral current content while old recovered contributions survive; adverse future retained. No automatic promotion, NSM65 elevation, general policy or indefinite stability.',
 'analysis_is_not_full_operational_backup':True,'budget_original':budget}
save(R/'CONTINUIDAD_CICLO02.json',out);save(E/'CONTINUIDAD_FINAL_LOCAL.json',out)
current=S/'documentacion/ESTADO_ACTUAL_DE_VIDAS.json';backup(current,'ESTADO_VIDAS_ANTES_CICLO02.json');old=json.loads(current.read_bytes());ids={r['life_id']:i for i,r in enumerate(old['lives'])}
for row in rows:
    if not row['life_id'].startswith(('E1_CICLO02','C02_','E1_SELECTOR')):continue
    if row['life_id']in ids:old['lives'][ids[row['life_id']]]=row
    else:old['lives'].append(row)
old['preferred_life']='E1_SOCIAL_11';old['latest_campaign']='CONSOLIDACION_EVOLUCION_E1_CICLO_02';old['latest_continuity']='CONTINUIDAD_CICLO02.json';save(current,old)
re=R/'REANUDACION.json';backup(re,'REANUDACION_ANTES_CICLO02.json');save(re,{'campaign':out['campaign'],'state':'CLOSED_LOCAL_RESULTS; no automatic new native runs','active':'E1_SOCIAL_11','continuity':'CONTINUIDAD_CICLO02.json','recommended_bounded_complement':out['recommended_bounded_complement'],
  'lives':[{'life_id':r['life_id'],'tick':r['tick'],'snapshot':r['snapshot'],'sha256':r['snapshot_sha256'],'scope':r['current_scope'],'pending_count':len(r['pending_inputs'])}for r in rows],
  'fixed_budget':budget,'previous_record_preserved':'laboratorio/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02/REANUDACION_ANTES_CICLO02.json',
  'next_operation':'Load the selected current life, do not rebuildT0 or silently restart Pendulum. Any new branch/experience is a new continuation, not a replacement for adverse MAIN.',
  'selection_not_acquired':'No native learned loss detector or P2 strategy was established. Preparation and query initiative remain explicit.',
  'no_process_restart_or_time_extension_authorized':True})
ficha={'type':'Composite native organization plus material participantB in one whole N67 Runtime; external gate/Pendulum are declared host environments, not extra DEE minds.',
 'criterion':'History-dependent comparison/reference supports, finite route selector, delayed native carriers and recipient supports interact through the same v27 world. Geometric region/view alone does not establish autonomy or another body.',
 'components':[{'id':'E1.quantity','function':'Native comparison and acquired scalar reference, prepared phase0and20contexts.'},
   {'id':'TM','function':'Inherited double-memory comparison; only the brief affected panel re-used.'},
   {'id':'finite_selector','function':'Native consequence-conditioned route state. Current late MAIN not qualified; separate conserved/used151state has finite140 access.'},
   {'id':'B.quantity','function':'Own physical reference36 observed; new private objects useformat+5. Native comparison emits the message, not a host label.'},
   {'id':'social_supports','function':'Acquired signs live in circulating/transformed distributed carriers and declared reader contexts, not a Python answer table.'}],
 'boundaries':{'native':'Complete physical world saved once per checkpoint, shared by its component/participant views. Do not call all universe matter the mind by default.',
   'host':'Schedules exposures/resources, modelgatecontact/wear, fixed sin codec and torque mapping, process persistence and passive measurements. It does not read expected answers to choose the native action.',
   'auditor':'Loads records/RAW/clocks and scores only afterward. Its atlas and old JSON results are denied as response sources in normal integrated commands.',
   'external_bridge':'Separate process and explicit67ticksper0.05Pendulumseconds; native-only intervals pause external world. Not closed purely-v27 communication with the external simulator.'},
 'prepared':'Geometry, ports, reference/comparison phases, opportunities, generic0supports, private teaching events, decoders, actuator gains. These are not invented anatomy or acquired attention.',
 'acquired':'Native scalar consequence reference, B-dependent circulating codes, transformed supports and changed later physical responses. Attributes belong only to the life that experienced them.',
 'lives':rows,'diagnostic_lineage_rule':'Forks share past; they are not independent learning replications. No memories or successful futures were merged.',
 'not_established':['General mind/consciousness','65NSM meanings','Learned P2 initiation of access','Unlimited retention','Competent Pendulum control','YO/TU functional perspective']}
save(E/'FICHAS_ENTES_Y_ASISTENCIA.json',ficha)
print(json.dumps({'updated_lives':len(rows),'main':next(r['tick']for r in rows if r['life_id']=='E1_CICLO02_MAIN'),'triple':next({'tick':r['tick'],'snapshot':r['snapshot'],'sha256':r['snapshot_sha256'],'current_codes':len([q for q in r['fixed_social_readers_current']if q['qualified']]),'gate_R':r['gate_environment_instrument']['resistance']}for r in rows if r['life_id']=='E1_CICLO02_SEPARACION_TRIPLE_01'),'native_ticks':0},ensure_ascii=False))
