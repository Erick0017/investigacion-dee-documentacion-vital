"""Scientific JSON intermediates; final CSVs are authored with artifact-tool."""
from pathlib import Path
import json,hashlib
import recalcular as rc
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01';OUT=LAB/'entrega_analisis'
OUT.mkdir(exist_ok=True);calc=rc.compute(EV);(EV/'CALCULOS.json').write_text(json.dumps(calc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
by={m['file']:m for m in calc['trial_metrics']};data={p.name:rc.read(p)for p in EV.glob('*.json')if p.name in by}
tables=[]
headers=['fuente_primaria','sha256_fuente','vida','operacion','tick_final','oportunidades_nativas','acciones_con_contenido','acciones_utiles_contexto_actual','pasos_externos','lecturas_nativas_principales_en_codec','acciones_externas_no_neutras','usos_del_contenido_social','peticiones_visibles_distintas','aplicadas','pendientes','rechazadas','alcance_denominador']
rows=[]
for m in calc['trial_metrics']:
    e=m.get('external',{});rows.append([m['file'],rc.sha(EV/m['file']),m['life'],m['operation'],m['tick'],m['native_actions_requested'],m['native_actions_with_payload'],m['native_actions_useful_in_current_prepared_context'],e.get('opportunities'),e.get('qualified_native_actuator_readings'),e.get('nonzero_executed_actions'),e.get('received_relation_used_at_motor'),m['requests_visible_distinct'],m['applied'],m['pending'],m['rejected'],m['receipt_scope']])
failed=EV/'OPERACIONES_Y_FALLOS_EXTRAIDOS.json'
if failed.exists():
    for j,f in enumerate(rc.read(failed)['failures']):
        op=f['operation'];rows.append(['OPERACIONES_Y_FALLOS_EXTRAIDOS.json#/failures/'+str(j),f['source_sha256'],f['life'],op['kind'],op.get('after',{}).get('tick'),None,None,None,None,None,None,None,None,None,None,None,'Fallo instrumental preservado. Denominadores no reconstruidos desde el mensaje de error; no se rellenan ceros. Fuente original: '+f['source_file']])
tables.append({'name':'ENSAYOS_Y_CONTRASTES.csv','headers':headers,'rows':rows})
cap=[]
for name,m in by.items():
    if'old_social_forms_with_response'in m:
        cap.append([m['life'],m['tick'],'Formas sociales heredadas',str(m['old_social_forms_with_response'])+'/8 formas con la firma física preparada','Uso con sondas materiales','Copia diagnóstica'if'PANEL_'in name and not name.startswith(('SYSTEM','FINAL_OPERATIONAL'))else'Uso consecutivo real en la vida',name,'No son ocho significados; direcciones [0,signo,1] concordantes con cada rama. No contar el X− ajeno de S06 como forma válida.'])
        cap.append([m['life'],m['tick'],'Huellas direccionales sociales transformadas',str(m['old_social_forms_with_residual_trace_not_automatically_functional'])+'/8 con contenido mayor que el lector y componenteY concordante','Distinción externa, no función recuperada automáticamente','Auditor; no sustituye el contrato del lector',name,'Una firma X−/Y/Z posterior a sondas repetidas no se cuenta como la firma histórica [0,Y,Z]. S04 perdió lectura al final prolongado.'])
        for f in m['old_panel_quantity']:
            read=f['read'];cap.append([m['life'],f['tick'],'Comparación cuantitativa'if f['kind']=='quantity'else'Comparador anterior R36/O16',','.join(map(str,read['direction']))+'; state='+str(read['state'])+'; carga='+str(read['s_reg']),'Uso material observado', 'Copia diagnóstica'if'PANEL_'in name and not name.startswith(('SYSTEM','FINAL_OPERATIONAL'))else'Uso consecutivo real en la vida',name,'La referencia revisada no conserva necesariamente el valor78 ni su signo anterior.'])
    if m['native_actions_requested']and name in('TIGHT_R6_16.json','TRANSIENT_A_43.json','RESERVED_SHUNT_46.json','WARM_RESERVE_57.json','WARM_SHAM_58.json','WARM_RETURN_OMIT_59.json','INTERLEAVE_NATIVE_EXTERNAL_141.json','INTERLEAVE_NO_NATIVE_RETURN_142.json','INTERLEAVE_NO_NATIVE_TEACH_143.json'):
        cap.append([m['life'],m['tick'],'Decisión nativa por consecuencias',str(m['native_actions_with_payload'])+'/'+str(m['native_actions_requested'])+' con contenido; '+str(m['native_actions_useful_in_current_prepared_context'])+' útiles','Preparación fija + estado adquirido','Ventana finita de esta vida',name,'No confundir respuesta válida con elección útil; no política general R2 ni estabilidad ilimitada.'])
    if 'external'in m and name.startswith(('INTEGRATED_COST_SOCIAL_132_','INTERLEAVE_NATIVE_EXTERNAL_141','LONG_SYSTEM_CONTINUATION_8','FINAL_OPERATIONAL_2','SYSTEM_CONTINUATION_3','STRESS_NOMINAL_MAIN_145_WITHDRAW_REMAINING5')):
        e=m['external'];cap.append([m['life'],m['tick'],'Referencia adquirida + transmisión social + actuación externa',str(e['qualified_native_actuator_readings'])+'/'+str(e['opportunities'])+' en codec; '+str(e['received_relation_used_at_motor'])+' usos sociales','Acción física propia y transducción externa fija','Misma vida; no suma de perfiles',name,'El mezclador es diseñado; contenido y referencia evolucionan en DEE. Control competente no demostrado.'])
tables.append({'name':'CAPACIDADES_POR_VIDA_Y_MOMENTO.csv','headers':['vida','tick_observado','funcion','resultado','naturaleza','atribucion','fuente','limites'],'rows':cap})
rows=[]
for c in calc['common_history_opportunities']:rows.append([c['file'],c['life'],c['tick'],c['public_object'],c['whole_period_delay'],c['reference_s_reg'],','.join(map(str,c['direction'])),c['qualified'],c['raw'],'Consulta material en bifurcación propia; la diferencia del hub posterior no se sustituye por el mecanismo causal del tick completo.'])
tables.append({'name':'COMPARACION_HISTORIAS_COMUNES.csv','headers':['fuente','vida_de_prueba','tick','objeto_actual','demora_adicional','carga_hub_posterior','direccion_nativa','en_dominio','RAW_exacto','alcance'],'rows':rows})
rows=[]
for name,d in data.items():
    life=d.get('INSTRUMENTO',{}).get('life_id')
    for x in rc.extrows(d):
        r=x.get('native',x.get('native_body',{}));social=x.get('social_reads',[]);requests=x.get('requests',[])
        rows.append([name,life,x['index'],x['tick'],json.dumps(x.get('observation_before'),separators=(',',':')),x.get('q_sin'),json.dumps(r.get('direction')),r.get('s_reg'),r.get('raw'),json.dumps([s.get('prepared_gain1_command',s.get('prepared_wire_command'))for s in social]),x.get('native_command',x.get('native_wire_command')),x.get('executed_torque'),x['response']['reward'],x.get('raw_cost_codec'),x.get('feedback_input_tick'),sum(r.get('receipt',{}).get('status')=='applied'for r in requests),sum(r.get('receipt',{}).get('status','').startswith('rejected')for r in requests),x.get('native_ticks_since_previous_motor'),'Preparado: codec/cableado; nativo: campos y decisión; entorno: consecuencia. No política óptima externa.'])
tables.append({'name':'FLUJO_CAUSAL_EXTERNO.csv','headers':['fuente','vida','paso_entorno','tick_DEE','observacion_externa','codigo_sin','direccion_DEE','carga_DEE','RAW_exacto','aportaciones_sociales_fijas','comando_nativo_transducido','torque_ejecutado','recompensa_real','coste_bruto_cuantizado','tick_retorno','peticiones_aplicadas_visibles','rechazos_visibles','ticks_desde_motor_anterior','frontera'],'rows':rows})
(LAB/'TABLAS_INTERMEDIAS.json').write_text(json.dumps({'out':str(OUT),'tables':tables},ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8');print(json.dumps({'tables':{t['name']:len(t['rows'])for t in tables},'primary_records':calc['primary_record_count']}))
