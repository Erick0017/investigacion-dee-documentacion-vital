"""Prepare exact rectangular data for the artifact-tool CSV authoring step.
Only archived primaries/current-state documents; no engine, ticks or policy.
"""
from pathlib import Path
import gzip,json
L=Path(__file__).resolve().parent;R=L.parents[2];E=R/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02';O=E/'EXPORTACION'
M=json.loads((E/'CALCULOS_REPETIBLES.json').read_bytes());C=json.loads((R/'CONTINUIDAD_CICLO02.json').read_bytes())
catalog=json.loads((R/'sistema/capacidades/CATALOGO_CAPACIDADES.json').read_bytes())['entries']
def text(v):
    if v is None:return 'ND'
    if isinstance(v,(dict,list)):return json.dumps(v,ensure_ascii=False,separators=(',',':'))
    if isinstance(v,bool):return 'sí'if v else'no'
    return str(v)
tables=[]
def table(name,columns,rows):tables.append({'file':name,'columns':columns,'rows':[[text(v)for v in row]for row in rows]})
cap=[]
for v in catalog:
    if not v['id'].startswith(('C02_','IC01_')):continue
    cap.append([v['id'],v.get('version'),v.get('origin'),v.get('implementation'),v.get('availability'),v.get('integration'),v.get('knowledge'),v.get('execution_command'),v.get('limits'),v.get('contract')])
table('CAPACIDADES_INCORPORADAS.csv',['id','version','origen_y_casos','implementacion','disponibilidad','vida_o_integracion','adquisicion_o_uso','comando','limites','contrato'],cap)
rows=[]
for v in C['lives']:
    qualified=[{'bank':q['bank'],'site':q['site'],'raw':str(q['read']['raw']),'clock':str(q['read']['clock'])}for q in v['fixed_social_readers_current']if q['qualified']]
    rows.append([v['life_id'],v['tick'],v['N'],v['profile'],v['parent'],v['current_status'],v['current_scope'],qualified,
        v['gate_environment_instrument'],v['external_progress'],len(v['pending_inputs']),v['snapshot'],v['snapshot_sha256'],v['latest_functional_access_primary'],
        'Foto pasiva actual más uso identificado; no suma conocimientos de ramas. Puertos fuera de fase no se puntúan como olvido.'])
table('CAPACIDADES_POR_VIDA_Y_MOMENTO.csv',['vida','tick','N','perfil','padre','estado','alcance_actual_y_limites','lecturas_sociales_actuales_validas','puerta','progreso_externo','entradas_pendientes','snapshot_completo_local','sha256_snapshot','ultimo_uso_primario','modalidad'],rows)
rows=[]
for id,v in M['case_inventory'].items():
    metrics={};unit='Operación de gestor o registro nativo; no implica individuo independiente';responses=correct=incorrect=abstention=out_domain=None
    if id in M['gate_cases']:
        q=M['gate_cases'][id];unit='Oportunidades de decisión con acción ambiental';metrics={k:q[k]for k in('opportunities','valid','native_choice_useful','useful','utility')}
        responses=q['valid'];correct=q['useful'];incorrect=q['opportunities']-q['useful'];abstention=sum(r['abstention_empty']for r in q['rows']);out_domain=sum(r['outside_actuator_codec_material']for r in q['rows'])
    elif id in M['social_cases']:
        q=M['social_cases'][id]
        if 'episodes'in q:unit='Episodios sociales privados de una vida';metrics={k:q[k]for k in('episodes','correct','valid')};responses=q['valid'];correct=q['correct'];incorrect=q['episodes']-q['correct']
        else:unit='Muestras pasivas de puerto en fase3; NO consultas ni réplicas';metrics={k:q[k]for k in('correct_phase_samples','correct_phase_native_valid','correct_phase_matches_private')};responses=q['correct_phase_native_valid'];correct=q['correct_phase_matches_private']
    elif id in M['external_cases']:
        q=M['external_cases'][id];unit='Pasos externos con transducción fija; código válido no prueba control competente';metrics={'steps':q['steps'],'social_counts':[r['qualified_social_count']for r in q['rows']]}
    elif id in M['selector_cases']:
        q=M['selector_cases'][id];unit='Oportunidades de selector finito';metrics={k:q[k]for k in('opportunities','valid','useful')};responses=q['valid'];correct=q['useful'];incorrect=q['opportunities']-q['useful']
    elif id in M['separation_cases']:
        q=M['separation_cases'][id];unit='Usos en etapas de una misma rama, no réplicas';metrics={'three_codes_first_uses':q['three_codes_first_uses'],'stages':len(q['stages'])}
    elif id in M['lateral_cases']:
        q=M['lateral_cases'][id];unit='Episodios laterales con futuros negativos preservados';metrics={k:q[k]for k in('completed','new_lateral','old_positive','both','final_occupation')}
    elif id in M['detour_cases']:
        q=M['detour_cases'][id];unit='Actualizaciones sociales';metrics={'opportunities':q['opportunities'],'both':q['both_count']}
    ledger=M['exact_input_ledger']['operations'][id]
    rows.append([id,v['life'],v['initial_tick'],v['final_tick'],unit,metrics,
        ledger.get('new_requests'),ledger.get('new_request_status_at_close'),ledger.get('applied_in_window_including_prior_queue'),ledger.get('rejected_in_window_including_prior_queue'),ledger.get('pending_at_close'),
        responses,correct,incorrect,abstention,out_domain,v.get('returncode'),v.get('error'),v['original']['path'],v['original']['sha256'],
        'Solicitudes nuevas y aplicaciones de cola previa tienen denominadores distintos. ND no significa cero. Correcto/incorrecto se refiere a la unidad declarada, no a todos los bytes.'])
table('ENSAYOS_Y_CONTROLES.csv',['id','vida','tick_inicio','tick_final','unidad_de_evaluacion','metricas_recalculadas','solicitudes_nuevas','estados_solicitudes_al_cierre','aplicadas_en_ventana_incluye_cola_previa','rechazadas_en_ventana_incluye_cola_previa','pendientes_al_cierre','respuestas_validas','usos_utiles_o_muestras_correctas','usos_no_utiles','abstencion_vacia','forma_material_fuera_codec','codigo_salida_proceso','error_instrumental','original','sha256_original','denominadores_y_limites'],rows)
rows=[]
for id,q in M['gate_cases'].items():
    for r in q['rows']:rows.append([id,q['mode'],r['index'],r['tick'],r['force'],r['wear_available'],r['resistance_before'],r['resistance_after'],r['reference_load'],r['native_raw'],r['native_clock'],r['native_fields'],r['native_action'],r['executed_action'],r['valid'],r['native_choice_useful'],r['useful'],r['opened'],r['jam'],r['utility'],r['abstention_empty'],r['outside_actuator_codec_material']])
table('ACCIONES_Y_CONSECUENCIAS.csv',['id','modo','indice_en_vida','tick','fuerza_actual','desgaste_disponible','resistencia_previa','resistencia_posterior','referencia_fisica','RAW_decimal_exacto','clock_decimal_exacto','campos','accion_emitida','accion_ejecutada','fisicamente_valida','eleccion_nativa_util','accion_ejecutada_util','abrio','atasco','utilidad','abstencion_vacia','material_fuera_codec'],rows)
rows=[]
for id,q in M['recovery_cases'].items():
    rows.append([id,'Usos externos reales de códigos adquiridos',q['uses'],q['positive_usable'],q['negative_usable'],[r['qualified_social_count']for r in q['rows']],
      'P0/P1 acotado; no reparación tras ver el target ni P2. Ausencia de contenido en controles no es una respuesta incorrecta. Recursos y consultas preparados.',M['case_inventory'][id]['original']['path'],M['case_inventory'][id]['original']['sha256']])
for id,q in M['separation_cases'].items():
    rows.append([id,'Separación y recuperación de contribución previa',len(q['stages']),None,None,[r['roles']for r in q['stages']],q['scope'],M['case_inventory'][id]['original']['path'],M['case_inventory'][id]['original']['sha256']])
table('ACCESO_Y_RETENCION.csv',['id','tipo','usos','positivo_utilizable','negativo_utilizable','roles_por_uso','asistencia_y_limites','original','sha256_original'],rows)
out={'method':'Data from exact primary recalc + complete saved life scope. All CSV cells authored as strings to preserve uint64 and literal identifiers. artifact-tool is used only by the separate export step. No native work.','tables':tables}
(E/'TABLAS_DATOS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'tables':[{ 'file':t['file'],'rows':len(t['rows']),'columns':len(t['columns'])}for t in tables],'native_ticks':0},ensure_ascii=False))
