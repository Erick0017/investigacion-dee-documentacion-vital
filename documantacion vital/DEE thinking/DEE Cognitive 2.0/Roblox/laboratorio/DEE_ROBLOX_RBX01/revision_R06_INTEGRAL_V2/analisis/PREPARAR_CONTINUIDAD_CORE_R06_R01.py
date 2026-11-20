"""Prepare closed three-arm core transfer notes only; E6 remains explicitly pending.

Reads declared frozen JSON/JSONL and their metadata. No Native/SQLite/Studio/model,
no active LOAD/CTRL state traversal. Does not edit the scientific report or Manual.
"""
from pathlib import Path
import datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V2_MAIN'
PARENT='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_DEV'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(rel):
    path=ROOT/rel;b=path.read_bytes();return json.loads(b.decode('utf-8-sig')),{'relative':rel,'absolute':str(path),'bytes':len(b),'sha256':sha(b)}
def write_new(rel,value):
    path=ROOT/rel
    with path.open('x',encoding='utf-8')as f:
        f.write(value if isinstance(value,str)else json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def main():
    facts,fs=read('analisis/FINAL_TRES_BRAZOS_RECALCULO_R03/HECHOS_RECALCULADOS.json')
    pair,ps=read('evidencia/PAR28/PAREJA_INTEGRAL_V2.json');b=pair['boundary']
    resources,rs=read('analisis/RECURSOS_CORE_CERRADO_R06_R01/RECURSOS_RECALCULADOS.json')
    latency,ls=read('analisis/LATENCIAS_VIDEO_Q1_Q2_R06_R01/LATENCIAS_Q1_Q2.json')
    card,cs=read('native/MAIN/sistema/estado/vidas/'+LIFE+'/VIDA.json')
    model,ms=read('comparadores/MODELO_LOCAL_PREPARADO_R06.json')
    quota,qs=read('comparadores/CUOTA_LLM_R06.json')
    scope,ss=read('native/MAIN/sistema/capacidades/RBX06_NATIVE_SCOPE_INTEGRAL_V2.json')
    if b['life_id']!=LIFE or b['native_tick']!=991187 or card['physical']['tick']!=991187 or b['completed_opportunities']!=28 or scope['max_cycles']!=24:
        raise ValueError('EXACT_CLOSED_CORE_CUT_REQUIRED')
    close=b['last_owner_close'];status=close['final_status']
    if close['exit_code']!=0 or status['running']is not False or status.get('uncertain_external_result')is not False:raise ValueError('CLOSED_CERTAIN_SOURCE_REQUIRED')
    counts=b['queue']['status_counts']
    if any(counts.get(k,0)for k in('queued','processing','uncertain')):raise ValueError('NO_PENDING_NATIVE_QUEUE_REQUIRED')
    if any(facts['totals'][a]['opportunities_completed']!=24 for a in('LIVE_NATIVE','PROGRAMMED','CONVENTIONAL_AI')):raise ValueError('THREE_ACTUAL24_REQUIRED')
    totals={}
    fields=('opportunities_completed','new_resources_collected','resources_delivered_total_in_this_continuation',
        'delivered_inherited_resource','delivered_new_resources','numeric_opportunities','numeric_formed','numeric_NULL_or_absent',
        'arithmetic_correct_for_actual_opcode','arithmetic_accuracy_among_evaluable','partial_lesson_admissions',
        'function_transport_requests_completed','function_transport_requests_accepted_explicitly','function_capability_execution_not_admitted',
        'prepared_assisted_contract_opportunities','assisted_route_overrides')
    for arm,value in facts['totals'].items():totals[arm]={k:value.get(k)for k in fields}
    utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
    final_result='evidencia/NATIVE_CONTINUACION_C16_R01/RESULTADO.json'
    result,final_source=read(final_result)
    world_relative='evidencia/NATIVE_CONTINUACION_C16_R01/WORLD_CHECKPOINT.json'
    world,ws=read(world_relative)
    if ws['sha256']!=b['world_sha256']or result.get('owner_closed')is not True:raise ValueError('MATCHING_LITERAL_FINAL_WORLD_AND_CLOSURE_REQUIRED')
    continuity={'schema':'DEE.INTEGRAL.V2.continuity_core.R01','prepared_utc':utc,
        'status':'CORE_THREE_ARMS_CLOSED_E6_AND_FINAL_DELIVERY_PENDING','scientific_report_owner':'Root/repertoire; this file is a transfer locator, not a second scientific report or Manual.',
        'protected_global_main':{'life_id':'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01','tick':947395,'selection_modified':False,
            'Manual_internal_edition_reported': '1.40','Manual_modified':False,'protection_reference':'control/CRITICOS_ANTES_R06.json','final_eleven_hash_comparison':'Required again by final ZIP build; baseline is not an instantaneous whole-project audit.'},
        'experimental_candidate':{'life_id':LIFE,'parent_life_id':PARENT,'parent_tick':953651,'N':67,'final_tick':991187,'new_native_ticks':37536,
            'selected_global_or_adopted':False,'Native_root_local':str(ROOT/'native/MAIN'),'profile':card.get('profile','fisica_directa'),
            'last_closed_owner_run':close['run'],'owner_pid_at_historical_close':close['pid'],'owner_exit_code':0,'closed_status_source':ps,
            'live_process_probe_performed_here':False,'queue_status_at_close':counts,'preserved_adverse_queue_records':{'failed_preserved':counts.get('failed_preserved',0),'rejected_invalid':counts.get('rejected_invalid',0)},
            'physical':card['physical'],'snapshot_local':str(ROOT/'native/MAIN/sistema'/card['snapshot']),'snapshot_sha256_from_pair':b['native_snapshot_sha256'],
            'World':ws,'checkpoint_id':b['checkpoint_id'],'scenario_sha256':b['scenario_sha256'],'world_id':b['world_id'],
            'parent_environment':{'global_completed':4,'carry_in_resource':1,'carry_in_A':4,'carry_in_B':5},
            'completed_global_opportunities':28,'new_opportunities_completed':24,'actor_max_new_opportunities':24,'remaining_actor_opportunity_supply':0,
            'next_cursor_value':29,'next_cursor_is_not_permission_to_start':True,
            'resume_rule':'Do not implicitly START29. Actual24-new actor supply is exhausted. A future campaign needs explicit prospective contract/budget and same complete genealogical continuation; never reset counters or rewind to PAR10 to pretend remaining supply.',
            'complete_pair':{'path':str(ROOT/'evidencia/PAR28'),'manifest':ps,'members':len(pair['members']),
                'member_bytes_sum':sum(x['bytes']for x in pair['members']),'native_source_bytes':pair['native_source_bytes'],
                'source_hashes_before_after_equal_reported':pair['source_all_file_hashes_before_after_equal'],
                'transport':'DIRECT_ROOT_MCP_NO_HTTP_BRIDGE_DATABASE','pair_is_locally_full_not_in_small_ZIP':True,
                'save_is_not_alone_reopen_proof':'Review World restore comparison plus same-session later use; preserve all known prequeue16/reconciliation evidence.'}},
        'core_blocks':[
            {'participant':'LIVE_NATIVE','path':'evidencia/NATIVE_BLOQUE_01','scope':'global5–10; closed full pair PAR10, then actual restore/later use'},
            {'participant':'LIVE_NATIVE','path':'evidencia/NATIVE_BLOQUE_02','scope':'pre-apply parse/transport attempt preserved; not added as new experience'},
            {'participant':'LIVE_NATIVE','path':'evidencia/NATIVE_BLOQUE_02_R02','scope':'global11–15 complete; Q1/Q2/motion16 already executed; FUNCTION16 malformed host packet known not admitted'},
            {'participant':'LIVE_NATIVE','path':'evidencia/NATIVE_CONTINUACION_C16_R01','scope':'same operation16 function/feedback reconciled, no Q1/Q2/motion replay; continuation through28 closed'},
            {'participant':'PROGRAMMED','path':'evidencia/PROGRAMMED_BLOQUE_01','scope':'first block; same environmental parent with prepared reference policy,0Native'},
            {'participant':'PROGRAMMED','path':'evidencia/PROGRAMMED_BLOQUE_02','scope':'same policy history restored; total24 new opportunities,0Native'},
            {'participant':'CONVENTIONAL_AI','path':'evidencia/AI_BLOQUE_01','scope':'own model history, first block;0Native'},
            {'participant':'CONVENTIONAL_AI','path':'evidencia/AI_BLOQUE_02','scope':'same model history restored; total24 new opportunities,0Native'}],
        'three_arm_results':totals,'latency_Q1_Q2_actual':{k:v['Q1_Q2_combined']for k,v in latency['summary'].items()},
        'closed_resources_core':{'source':rs,'owner_aggregate':resources['closed_owner_aggregate'],'scope':'MAIN owned Jobs only; import0/model service separately reported. No CPU efficiency/energy verdict.'},
        'model':{'model_metadata':ms,'quota':qs,'calls_used_global':quota['used'],'inference_responses_own_history':55,'preflight_calls_separate':1,
            'weight_updates':False,'own_history_is_not_DEE_memory':True,'local_service_closed_record':'comparadores/SERVIDOR_MODELO_R06.jsonl:CLOSED 2026-11-16T01:44:58.764026+00:00'},
        'pending_E6':{'load':'Root conducting bounded1→2→3 focal owner test; no active LOAD roots or journals read here. Add only actual closed stages/results.',
            'live_clean_connector':'CTRL1 import0 verified; at this core note no LIVE result is asserted. Preserve separate technical0Native clean XML proof.',
            'video':'Pending actual final MP4/container/visual evidence and delivery hash; do not mark finished from code alone.'},
        'scientific_limits':['Prepared locomotion/order remains assistance; Native selected operation/memory/numeric content and overridden route must remain separated.',
            'One Native lesson admitted only partially; transport acceptance is not full capability acquisition.',
            'Native10/10 arithmetic results for actual opcode is not proof of a learned arithmetic algorithm or general plan.',
            'AI5numeric requests without formed integer are NULL, not material zero; arithmetic accuracy among evaluable cases is null.',
            'Carry-in resource delivery is separated from new resources. Three continued histories are not independent populations.',
            'No scientific claim of agency generality, superiority, consciousness or unassisted problem solving follows.'],
        'source_recalculation':fs,'source_final_result':final_source,'finalization_required':['actual E6 load/prototype outcomes','video outputs/QC','final protected11 hash control','final complete ZIP selection/integrity/extracted passive recalculation']}
    omissions={'schema':'DEE.INTEGRAL.V2.localized_omissions_core.R01','prepared_utc':utc,'status':'CORE_SELECTION_PENDING_FINAL_E6_AND_VIDEO',
        'ZIP_is_executable_backup':False,'selection_criterion':'Full small decisive scientific primaries and controls, exact code, portable recalcs. Exclude full states/dependencies and repeated SDK envelopes; retain adverse results.',
        'items':[
            {'category':'full_closed_pair','path':str(ROOT/'evidencia/PAR28'),'kind':'directory','bytes_from_member_manifest':sum(x['bytes']for x in pair['members']),
                'members':len(pair['members']),'folder_sha256':None,'folder_hash_not_claimed':True,'manifest':ps,
                'why':'Full local executable-state components exceed the small evidence budget; no component is deleted or reduced.',
                'needed_for':'Material same-state Native continuation/reproduction; requires shared official runtime as well.',
                'retained_small':'Matching final World, closed proof, summarized map and original manifest locator/hash; no claim that summary is full manifest.'},
            {'category':'full_pair_manifest','path':ps['absolute'],'bytes':ps['bytes'],'sha256':ps['sha256'],
                'why':'3.077.232-byte member map is preserved locally; compact map copies only decisive file anchors. Avoid using a large-primary exception for administrative duplication.'},
            {'category':'current_experimental_native_root','path':str(ROOT/'native/MAIN'),'bytes_from_closed_seal':pair['native_source_bytes'],'folder_sha256':None,
                'why':'Complete operational root remains local. Snapshot/card alone cannot replace queue, interfaces, artifacts, outbox, environment and related resources.'},
            {'category':'shared_official_runtime','local_metadata':pair['shared_read_only_runtime'],'why':'Shared frozen official runtime; not duplicated inside a15MB analysis ZIP. No laws/binaries changed.'},
            {'category':'model_weights','metadata':ms,'actual_file_anchors_as_recorded':model,'why':'Large existing model files stay local; metadata identifies comparator. No private identity/key contents copied.'},
            {'category':'historical_source_and_pairs','paths':[str(ROOT/'evidencia/PAR10'),str(ROOT/'native/MAIN/PREFIJO_DEV4_COMPLETO')],
                'bytes':None,'bytes_status':'Not remeasured here; consult each existing local full manifest. No recursive rescan.',
                'why':'Historical complete states stay intact; include their locators/control hashes and actual relevant parent World, not nested huge ZIPs.'},
            {'category':'LOAD_CTRL_states','path_scope':str(ROOT/'native'),'selected_roots':['LOAD1','LOAD2','LOAD3','CTRL1'],
                'bytes':None,'hash':None,'status':'Active or awaiting real E6 outcome; not hashed or traversed in this core preparation.',
                'why':'Their complete state remains local; only closed stage/result/connector proofs may be added later.'},
            {'category':'raw_MCP_transport','path_scope':str(ROOT/'evidencia'),'bytes':None,'hash':None,
                'why':'Long repeated SDK inventories, base64/hex staging and chunk envelopes omitted; full literal World and exact scientific events/decisions/functions retained.'},
            {'category':'protected_global_main_and_Manual','reference':'control/CRITICOS_ANTES_R06.json','why':'Protected originals unchanged; V2 does not require transporting or editing Manual1.40 or adopting the experimental candidate.'},
            {'category':'video','status':'Pending final render/QC','why':'Separate viewing artifact; final ZIP may carry code/manifest/QC and external MP4 hash instead of embedding a large MP4.'}],
        'unavailable_or_unverified':['No new global protection hash sweep performed here; final packager must compare exact11.',
            'E6 outcomes pending; the source code and import0 are not counted as material success.']}
    members=pair['members'];suffixes=('VIDA.json','cola.sqlite3','RBX06_NATIVE_SCOPE_INTEGRAL_V2.json','RBX06_NATIVE_INTEGRAL_V2/events.jsonl')
    critical=[x for x in members if x['file']in('WORLD_CHECKPOINT.json','CIERRE_CONCILIADO.json','LEDGER_R06_AL_CORTE.json')or any(x['file'].endswith(s)for s in suffixes)or x['sha256']==b['native_snapshot_sha256']]
    mapping={'schema':'DEE.INTEGRAL.V2.compact_closed_state_map.R01','scope':'Selected anchors, not a full state manifest or a full executable backup.',
        'complete_manifest':ps,'members_in_full_manifest':len(members),'full_member_bytes':sum(x['bytes']for x in members),
        'selected_original_member_records':critical,'references':[fs,rs,ls,cs,ss,ws,final_source],
        'scientific_function_primary_sources':[x for x in facts['sources']if '/functions/'in x['path'].replace('\\','/')],
        'same_source_paths_remain_local':True}
    guide=f'''DEE ROBLOX INTEGRAL V2 — NÚCLEO CERRADO, E6 AÚN PENDIENTE\nCorte de esta nota: {utc}\n\nLa candidata experimental N67 terminó enT991187:37536ticks nuevos desde DEV4\nT953651. Completó24oportunidades nuevas/global28 y quedó cerrada, con cola sin\npendientes. No es el principal global: PI10_REAL2_01 sigueT947395 y el Manual\nMaestro1.40 se conserva intacto. No se actualizó ACTIVO ni se adoptó esta candidata.\n\nResultados comprobados, un historial por brazo (24oportunidades cada uno):\nDEE:2recursos nuevos,3entregas totales (1heredada+2nuevas);10/10números\nformados correctos para su operación real. Una enseñanza tuvo admisión parcial.\nProgramado:3recursos nuevos,4entregas totales (1heredada+3nuevas);10/10números.\nIA local:0recursos nuevos,1entrega heredada;5solicitudes numéricas sin entero\nformado. No se convierte NULL en cero ni se atribuye exactitud aritmética a0casos.\nEl orden/locomoción fue asistido;5rutas de DEE y13de IA fueron efectivamente\nsustituidas por el contrato preparado. Esto no es una prueba de plan autónomo.\n\nLectura: 1)analisis/INFORME_INTEGRAL_V2.md;2)CONTINUIDAD_CORE_R06.json;\n3)FINAL_TRES_BRAZOS_RECALCULO_R03/HECHOS_RECALCULADOS.json y matrices;\n4)EVENTS/RESULTADO, funciones y controles citados;5)OMISIONES_CORE_R06.json\ny MAPA_CORE_CERRADO_R06.json. Las fuentes leídas y sus límites se conservan\nen FUENTES_LEIDAS_INTEGRAL_V2_R01.json; esto no declara nueva lectura de manuales.\n\nPunto exacto: la oferta Native de24episodios está AGOTADA. El cursor29 no autoriza\nSTART29. El par completo está en evidencia/PAR28:11143miembros/1071589175B;\nmanifest3.077.232B SHA256c4638b02ea660f2e32d13c015637e817a28d471e96c3bee0284918f1d55cf2c2.\nWorld final SHA25648544f655382bdf97b4930200158e35371d878c29d17c1ce918077aa27cf6930.\nConservar Native completo, snapshot, SQLite/recibos/interfaces/agenda/outbox,\nartefactos y World/entorno emparejado. El ZIP pequeño no es respaldo ejecutable.\nNo reemplazarlo por PAR10 antiguo ni recrear desdeT0. Cualquier oferta futura\nrequiere un contrato/corte/budget prospectivo explícito sin reiniciar memoria.\n\nRecálculo pasivo de recursos cerrado: RECURSOS_CORE_CERRADO_R06_R01/\nRECURSOS_RECALCULADOS.json;3248sCPU de los3Jobs MAIN, no CPU exclusiva\ndel kernel;4180,6679s suma de vidas de propietarios, no duración de campaña.\nLos recursos de LOAD/CTRL quedan fuera hasta sus cierres. El modelo tuvo55\ninferencias propias y1preflight separado; pesos e historia no equivalen a DEE.\nLatencia Q1/Q2 real p50:29,9934s DEE(n48),0,011851s programado(n48),\n12,9242s IA(n47); no utilizar S.latency heredada como medición actual.\n\nPara repetir estos cálculos sin motor, usar los scripts y CLI de las carpetas de\nrecálculo; PRIMARIOS/ y REPETIR_PORTABLE.json de recursos funcionan desde\nuna extracción sin abrir rutas originales de procedencia. Native material exige\nlos estados/runtimes locales completos y sólo se ejecuta en una copia explícita.\n\nPENDIENTES DE ESTA NOTA: carga focal1→2→3, episodio Native en conector limpio,\nvídeo5–8min y sus QC, comparación final de11críticos, ZIP/extracción/recálculos.\nRoot está cerrando E6: añadir únicamente lo efectivamente ejecutado y comprobado.\nEl XML limpio técnico0Native sí se comprobó; sus guías están en prototipo/.\nNo afirmar carga3, LIVE ni vídeo final por existir código o una importación0.\n'''
    write_new('analisis/CONTINUIDAD_CORE_R06.json',continuity)
    write_new('analisis/OMISIONES_CORE_R06.json',omissions)
    write_new('analisis/MAPA_CORE_CERRADO_R06.json',mapping)
    write_new('analisis/LEER_PRIMERO_CORE_R06.txt',guide)
    print(json.dumps({'status':continuity['status'],'Native_tick':991187,'full_pair_members':len(members),'full_pair_bytes':sum(x['bytes']for x in members),'function_primary_sources':len(mapping['scientific_function_primary_sources']),'Native_Studio_model_SQLite_calls':0},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
