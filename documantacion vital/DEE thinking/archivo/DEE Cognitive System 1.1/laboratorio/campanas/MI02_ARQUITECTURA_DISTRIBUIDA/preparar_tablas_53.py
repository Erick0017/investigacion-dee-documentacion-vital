"""Prepare scientific table matrices from independently decoded recorded evidence.
CSV authoring is performed by the bundled Artifact Tool, not this script.
"""
import json,re,sys
from pathlib import Path
L=Path(__file__).resolve().parent;R=L.parents[2];E=R/'evidencia/campanas/MI02_ARQUITECTURA_DISTRIBUIDA';S=R/'sistema'
d=json.loads((L/'RECALCULO_FINAL_MI02.json').read_bytes());fichas=json.loads((E/'FICHAS_ENTES_MI02.json').read_bytes());idx={x['id']:x for x in d['summaries']};tables=[]
def table(name,headers,rows):
    assert all(len(r)==len(headers)for r in rows);tables.append({'filename':name,'headers':headers,'rows':rows})
def compact(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'))
def normalize(t):
    t=re.sub(r'(?<=\d)(?=[A-Za-zÀ-ÿ])',' ',t);t=re.sub(r'(?<=[a-záéíóúñ])(?=(?:R\d|T\d|N\d|NSM\d|MI\d|RAW\d|MAIN\b))',' ',t);return re.sub(r'\b(a|de|en|tras|con|y|sin)(?=\d)',r'\1 ',t)

table('CAPACIDADES_POR_VIDA.csv',['vida','funcion_o_perfil','tipo_organizacion','N','tick_real','capacidad_adquirida_o_utilizada','limite_y_asistencia','snapshot_local','sha256_snapshot','entradas_pendientes'],[[r['life'],normalize(r['role']),normalize(r['organization']),r['N'],r['tick'],normalize(r['acquired']),normalize(r['limit']),r['snapshot'],r['snapshot_sha256'],len(r['pending_inputs'])]for r in fichas])

rows=[]
for r in d['summaries']:
    m=r.get('motor',{});w=r.get('word_use',{});q=r.get('ephemeral',{});e=r.get('external',{});statuses=r['receipt_statuses'];invalid=bool(r['error'])
    rows.append([r['id'],r['life'],r['tick_before'],r['tick_after'],'INVALIDO_INSTRUMENTAL_ESTADO_ALCANZADO_CONSERVADO'if invalid else'REGISTRO_EJECUTADO_NO_VEREDICTO_COGNITIVO',None if invalid else r['requests_unique'],None if invalid else statuses.get('applied',0),None if invalid else sum(v for k,v in statuses.items()if k.startswith('reject')),compact(statuses),m.get('opportunities'),m.get('useful'),m.get('wrong'),m.get('absent'),m.get('conflicts'),m.get('old_absence_flags_disagree'),w.get('trials'),w.get('valid'),w.get('intended_label_correct'),q.get('uses'),q.get('valid'),e.get('steps'),e.get('executed_nonzero'),e.get('reward_sum'),compact(r['error'])if invalid else'',r['source'],r['source_sha256']])
table('ENSAYOS_Y_CONTROLES.csv',['experimento','vida','tick_inicial','tick_final','estado_de_ejecucion','solicitudes_unicas_registradas','aplicadas','rechazadas','estados_recibos_exactos','oportunidades_motoras','utiles_regla_contacto_comun','incorrectas','sin_emision_material','conflictos','flags_historicos_ausencia_discrepantes','pruebas_senal','senal_respuesta_valida','coincide_etiqueta_no_semantica','consultas_auxiliares','aux_respuesta_valida','pasos_externos','acciones_externas_no_neutras','recompensa_externa_suma','error_conservado','fuente_original','sha256_fuente'],rows)

rows=[]
for r in sorted((r for r in d['summaries']if r['life']=='D1_MI02_MAIN'),key=lambda x:(x['tick_before']or-1,x['id'])):
    rows.append([r['id'],r['tick_before'],r['tick_after'],'CONTINUACION_EXPLORATORIA_DECLARADA'if r['id'].startswith('CONT34')else'PROGRAMA_FIJADO_29',r['requests_unique'],r.get('motor',{}).get('opportunities'),r.get('motor',{}).get('useful'),r.get('motor',{}).get('wrong'),r.get('motor',{}).get('absent'),r.get('external',{}).get('steps'),r.get('word_use',{}).get('trials'),r.get('word_use',{}).get('intended_label_correct'),r['source'],r['source_sha256']])
table('TRAYECTORIA_MAIN.csv',['operacion','tick_inicial','tick_final','etapa','solicitudes_registradas','oportunidades_motoras','contactos_utiles','incorrectos','ausencias','pasos_externos','pruebas_de_senal','coincide_etiqueta_no_semantica','fuente','sha256_fuente'],rows)

descriptions=[('MI02_CONTROLADOR_90','Local R8','Seleccion revisada por consecuencias','Fase y suministros preparados; sin prueba de cognicion general'),('E1_MI02_HEREDADA_R8','Heredada N67','Nuevo aprendizaje periferico sobre una biografia real','No uso acreditado de los conocimientos antiguos por la region nueva'),('D1_MI02_MAIN','Distribuida R6','Historia local, consulta nativa, signo privado y actuacion externa','Desfase, interferencia de senales y asistencia P0; no control aprendido'),('MI02_SOCIAL_EFIMERO_220','Candidata R7','Referencia privada mantenida','No libero el lector; hipotesis fallida conservada'),('MI02_SOCIAL_NEUTRO_230','Candidata R8 social','Lector neutro y codigo generico posterior','Persistio un soporte no previsto; no libero el lector'),('MI02_SOCIAL_REUSABLE_240','Alternativa R9','Lector privado liberable y consultas nativas repetidas','Primer contexto retenido; no actualizacion arbitraria'),('MI02_R9_OPERATIVA47','R9 despues de uso externo','Continuidad entre procesos y retorno a tarea nativa','2/4contactos utiles posteriores; sin politica competente del simulador'),('MI02_EFIMERO_210','Auxiliar efimero','Referencia32/10 y lectura reutilizable','No integrado enMAIN; sonda del operador y sesgo preparado')]
rows=[]
for life,variant,gain,limit in descriptions:
    rec=json.loads((S/'estado/vidas'/life/'VIDA.json').read_bytes());p=rec['physical'];rows.append([life,variant,p['N'],p['N']**3,p['tick'],p.get('occupied'),p.get('max_s_reg'),p.get('basic_buffers_bytes'),normalize(gain),normalize(limit),'NO_HAY_GANADORA_UNIVERSAL',rec['snapshot'],rec['snapshot_sha256']])
table('COMPARACION_ARQUITECTURAS.csv',['vida','variante','N','sitios','tick','sitios_state_no_cero','max_s_reg','buffers_basicos_bytes_no_RAM_total','funcion','limite','decision','snapshot','sha256_snapshot'],rows)

table('INTERACCION_EXTERNA.csv',['experimento','vida','pasos','recompensa_suma','acciones_ejecutadas_no_neutras','torques_dee_menos2','torques_dee_mas2','torques_dee_cero','solicitudes_sensores','sensores_aplicados','modo','sensores','codec','fuente','sha256_fuente'],[[r['experiment'],r['life'],r['steps'],r['reward_sum'],r['executed_nonzero'],r['native_torques'].get('-2',0),r['native_torques'].get('2',0),r['native_torques'].get('0',0),r['sensor_requests'],r['sensor_applied'],r['mode'],r['sensor_mode'],r['codec_revision'],r['source'],r['source_sha256']]for r in d['external_trajectories']])

table('SENALES_Y_CONTROLES.csv',['experimento','vida','pruebas','respuestas_validas','coincidencias_etiqueta','palabras','comandos_nativos','limite_de_atribucion'],[[r['experiment'],r['life'],r['trials'],r['valid'],r['intended_label_correct'],compact(r['words']),compact(r['commands']),r['semantic_attribution']]for r in d['word_signal_tests']])

table('LECTOR_AUXILIAR.csv',['experimento','vida','usos','respuestas_validas','lector_state_cero_despues','lector_RAW_cero_despues','datos_actuales','clases_nativas','alcance'],[[r['experiment'],r['life'],r['uses'],r['valid'],r['empty_reader_after_use'],r['RAW_zero_reader_after_use'],compact(r['values']),compact(r['classes']),'Perfil independiente; dato ausente/clase indeterminada no se traduce como NO']for r in d['ephemeral_tests']])

rows=[]
for r in d['social_reader_tests']:
    gates={z['reader_activation']:z for z in r['activations_with_gate_witness']}
    for run in r['reader_state_runs']:
        g=gates.get(run['start']);rows.append([r['experiment'],r['life'],run['start'],run['end'],run['active'],run['end']-run['start']+1,g['preceding_last_gate_tick']if g else None,g['gate']['raw']if g else None,'Cada tick observado; episodios de un tren, no consultas independientes'])
table('LECTOR_SOCIAL_REUTILIZACION.csv',['experimento','vida','inicio_tick','fin_tick','lector_activo','duracion_ticks','giro_solicitud_tres_ticks_antes','RAW_giro_exacto','cobertura'],rows)

rows=[]
for label,count,cap in[('none',0,0),('nominal',32,20),('amplitude',32,1000),('destructive',320,1000),('away_sham',320,1000)]:
    exp='ESTRES37R2_'+label;z=json.loads((E/(exp+'.json')).read_bytes())['data']['result'];r=idx['ESTRES37R2_USO_'+label];m=r['motor'];rows.append([label,count,cap,compact(idx[exp]['receipt_statuses']),m['opportunities'],m['useful'],m['wrong'],m['absent'],'Perturbacion legal; dosis y tasa se conservan por separado',r['source'],r['source_sha256']])
for mode in('none','sham','treatment'):
    r=idx['RESERVA38_'+mode+'_USE'];m=r['motor'];rows.append(['recuperacion_reservada_'+mode,0 if mode=='none'else 2,0 if mode=='none'else 1000,compact(idx['RESERVA38_'+mode+'_RESOURCE']['receipt_statuses']),m['opportunities'],m['useful'],m['wrong'],m['absent'],'Mismo recurso generico P0; no palabra o referencia original',r['source'],r['source_sha256']])
table('ESTRES_Y_ACCESO.csv',['condicion','paquetes','max_carga_por_paquete','admisiones','oportunidades_posteriores','utiles','incorrectas','sin_emision','alcance','fuente','sha256_fuente'],rows)

out={'tables':tables,'scope':'Scientific recorded data. Each row keeps numerators, denominators, scope and source; no inferred semantics or global PASS. Counts of calls are not independent learners.','raw_and_hash_fields_are_text':True,'numeric_counts_typed':True,'native_ticks':0}
(L/'TABLAS_DATOS_MI02.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8');sys.stdout.reconfigure(encoding='utf8');print(json.dumps([(t['filename'],len(t['rows']),len(t['headers']))for t in tables]))
