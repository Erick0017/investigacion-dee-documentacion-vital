"""Read-only final service report; independent windows are never added."""
import argparse,json
from pathlib import Path

def read(p):return json.loads(p.read_bytes())

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in('r01','r02','r03','r04','salida'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();c=read(a.r04/'RECALCULO_SERVICIO_APD.json');f=read(a.r04/'PANELES_Y_FUNCIONES.json');t=read(a.r04/'RECALCULO_TIEMPO_APD.json');cut=read(a.r04/'CORTE_PARA_MANUAL.json');r=read(a.r04/'RESULTADO.json');prefix='apd63_';primitives=[x for x in f['APD_primitive_uses_including_composition_stages']if x['id'].startswith(prefix)];mem=f['memory_uses']
    windows=[]
    for label,path in(('R01',a.r01),('R02',a.r02),('R03',a.r03)):
        z=read(path/('RECALCULO_INTERRUPCION.json'if label in('R01','R02')else'RECALCULO_TIEMPO_APD.json'));windows.append({'window':label,'seconds':z.get('observed_mode_enabled_seconds',z.get('unpaused_operational_seconds')),'single_owner_hour_claimed':False,'scope':'Technical negative'if label in('R01','R02')else'Continuous world across two owners; not one uninterrupted owner'})
    lines=['# APD01: servicio persistente, resultados y continuación','',
      'Una genealogía física ASISTENTE_MAIN contiene el piloto, los dos futuros técnicos interrumpidos, R03 con recarga y R04 de un propietario. Las ventanas permanecen separadas. No se suman sus tiempos para declarar una hora, ni se transfieren aprendizajes desde controles.','',
      '## Ventanas anteriores conservadas','', '```json',json.dumps(windows,sort_keys=True,ensure_ascii=False,indent=2),'```','',
      'R01 conservó la carrera de observación del WAL y siete filas FIFO. R02 conservó el supuesto instrumental erróneo de que un BEGIN en cola ya era una cascada material y ocho filas; sus docencias rechazadas no son aprendizajes. R03 consumió esos mismos IDs una vez y completó un FINISH heredado real. R03 monitorizó26 fuentes y omitió el actor APD; sus bytes P26 exactos están archivados por separado, sin fingir monitorización retroactiva. R04 monitorizó27, incluido ese actor.','',
      '## Una sola instancia R04','',
      f"Tiempo propio R04 habilitado: {t['unpaused_operational_seconds']}s; prueba de una hora con un único PID: {t['operational_criteria']['sixty_minutes_one_native_owner_proved']}. PID nativo={t['one_native_pid']}; avance entre muestras frescas={t['strict_native_tick_advance_between_fresh_end_samples']}ticks; ocio añadido={t['idle_ticks_added']}ticks. No hubo crédito de los ensayos anteriores. Limpieza operativa={t['clean_closure']}; utilidad cognitiva y limpieza son dimensiones distintas.",
      f"Corte final realmente alcanzado: {cut['main']['life_id']} T{cut['main']['tick']} N{cut['main']['N']}, snapshot `{cut['main']['snapshot']}`, SHA-256 `{cut['main']['snapshot_sha256']}`. Propietario detenido={cut['persistent_service']['owner_stopped']}; pendiente/incierto={cut['persistent_service']['pending_or_uncertain']}. Continúa exclusivamente con el par completo, no con un fork desnudo. ACTIVO global no se promueve.",'',
      '## Denominadores y resultados independientes','', '```json',json.dumps(c['transport_admission_denominators'],sort_keys=True,ensure_ascii=False,indent=2),'```','',
      '| Dimensión R04 | Resultado |','|---|---|',
      f"| Entradas nativas aplicadas/solicitadas | {c['native_receipts'].get('applied',0)}/{c['native_receipts']['requested']} |",
      f"| Memorias conforme a historia efectivamente enseñada | {sum(x['matches_expected']for x in mem)}/{len(mem)} |",
      f"| Pasos APD cuyo código coincide con historia docente | {sum(x['word_matches_history']for x in primitives)}/{len(primitives)} |",
      f"| Números correctos dada la operación física emitida | {sum(x['correct_given_actual_operator']is True for x in primitives)}/{len(primitives)} |",
      f"| Artefactos realmente completados | {sum(x['real_artifact_completed']for x in primitives)}/{len(primitives)} |",
      f"| Artefactos completados dentro del presupuesto modelado2 | {sum(x['completed_within_prepared_modeled_budget2']for x in primitives)}/{len(primitives)} |",'',
      'Los seis pares del panel final fueron fijados antes de R04 y comprobados ausentes del índice de entradas anteriores; no son seis réplicas independientes. Las repeticiones del resto del calendario se declaran como tales. El docente beta− es explícito: si ya era−, no acredita una revisión nueva. No se reenseñó otra forma ni se ajustaron lectores ante fallos.','',
      '## Paneles finales y docencia real','', '```json',json.dumps({'last_memory_observations':f['last_memory_observations'],'new_teaching':f['explicit_teaching'],'prior_teaching':f.get('prior_explicit_teaching'),'first_final_pair_opportunities':f.get('novel_pair_first_opportunities'),'native_count':f['native_count'],'composition':f['composition'],'raw128':f['raw128']},sort_keys=True,ensure_ascii=False,indent=2),'```','',
      'Los últimos paneles son usos en la misma MAIN, no verificaciones sumadas desde clones. Ocurrieron antes del ocio final registrado: no garantizan acceso indefinido. Los bytes exactos y paneles completos, incluidos silencios, rechazos y errores, se conservan para recálculo.','',
      '## Atribución y reproducción','',
      'El operador instala anatomía, codec, calendario, oportunidades y docencia. DEE determina operadores y rutas físicas; el host no selecciona la respuesta útil. El cálculo externo es herramienta declarada, no aritmética aprendida. Seis formas corresponden a dos clases operativas, no seis conceptos ni español general. COUNT y composición tienen mecanismos preparados; el orden de composición es solicitado, no plan inventado. Coste modelado, exactitud numérica, historia lexical y compleción del artefacto no se sustituyen por un PASS global.',
      'El perímetro son hooks Python y no un sandboxOS. Los diarios operativos bajo sistema/estado no estaban universalmente bloqueados; los descriptores antiguos no se reescriben. La revisión del código decisor y los contrastes físicos aportan evidencia diferente sobre ausencia de ayudas ocultas.',
      f"Recálculo archivado R04: {c['serialized_RAW_observations_checked']} observaciones RAW y {c['complete_uint64_checked']} uint64 completos; discrepancias={len(c['issues'])}. PLAN_RECALCULO se ejecuta con Python estándar sin Runtime ni nuevo trabajador. Los snapshots, SQLite y outbox completos siguen locales y en el FullZIP; el análisis compacto no es su reemplazo.",'']
    with a.salida.open('x',encoding='utf8')as out:out.write('\n'.join(lines))
    print(json.dumps({'file':str(a.salida),'native_ticks':0}))
if __name__=='__main__':main()
