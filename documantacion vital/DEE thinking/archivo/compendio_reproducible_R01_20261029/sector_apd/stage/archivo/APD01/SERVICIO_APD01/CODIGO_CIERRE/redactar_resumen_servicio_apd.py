"""Compact deterministic service report from completed archived calculations."""
import argparse,json
from pathlib import Path
def read(p):return json.loads(p.read_bytes())
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--r01',type=Path,required=True);p.add_argument('--r02',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();old=read(a.r01/'RECALCULO_INTERRUPCION.json');calc=read(a.r02/'RECALCULO_SERVICIO_APD.json');f=read(a.r02/'PANELES_Y_FUNCIONES.json');t=read(a.r02/'RECALCULO_TIEMPO_APD.json');cut=read(a.r02/'CORTE_PARA_MANUAL.json');primitive=f['APD_primitive_uses_including_composition_stages'];new=[r for r in primitive if r['id'].startswith('apd61_')];memory=f['memory_uses'];raw=f['raw128'];native=calc['native_receipts'];den=calc['transport_admission_denominators']
    lines=['# Servicio APD01: resultados de una continuidad real','',
      'Este componente conserva el piloto, R01 interrumpida y R02 posterior en la misma ASISTENTE_MAIN. No son tres aprendices independientes. El protocolo R02 no rebobina R01 y no acredita sus minutos. Los archivos completos para continuar permanecen locales y en la distribución operativa; este componente es evidencia de análisis.','',
      '## Tiempo y continuidad','',
      f"R01 falló por una carrera de medición pasiva del archivo SQLite WAL: {old['observed_mode_enabled_seconds']:.6f}s observados en modo habilitado, no60min. El cierre guardó T188466 y siete solicitudes reales todavía encoladas. El RESULTADO original y la revisión instrumental errónea se conservan; no se atribuye un fallo mental al sistema de archivos.",
      f"R02 tuvo horizonte fijo de {t['fixed_horizon_seconds']:.6f}s; se descontaron {t['conservative_pause_reload_discount_seconds']:.6f}s de pausa/guardado/exportación/recarga, dejando {t['unpaused_operational_seconds']}s. Criterio mínimo60min sin pausas: {t['checks']['at_least_sixty_unpaused_operational_minutes']}. No es tiempo CPU continuo, ni garantía24/7. CPU integral no medida.",
      f"Corte real final: {cut['main']['life_id']}, T{cut['main']['tick']}, N{cut['main']['N']}; snapshot `{cut['main']['snapshot']}`, SHA-256 `{cut['main']['snapshot_sha256']}`. Propietario parado: {cut['persistent_service']['owner_stopped']}; pendiente/incierto: {cut['persistent_service']['pending_or_uncertain']}. Para continuar hacen falta el snapshot y el diario/artefactos emparejados, no sólo arrays.",'',
      '## Denominadores de R02','',
      '```json',json.dumps(den,sort_keys=True,ensure_ascii=False,indent=2),'```','',
      'Las siete filas ya encoladas en R01 se contabilizan aparte:','',
      '```json',json.dumps(calc['inherited_pending_execution_outcomes'],sort_keys=True,ensure_ascii=False,indent=2),'```','',
      '## Funciones observadas, sin veredicto global','',
      '| Dimensión | Resultado |','|---|---|',
      f"| Entradas físicas nuevas en la ventana (incluye las siete solicitudes heredadas al ejecutarse) | {native.get('applied',0)}/{native['requested']} applied; {native.get('rejected',0)} rechazadas |",
      f"| Usos de memoria histórica | {sum(r['matches_expected']for r in memory)}/{len(memory)} coincidieron con la historia docente realmente admitida |",
      f"| Pasos APD nuevos, incluidos pasos de composición | {len(new)} |",
      f"| Código de palabra según historia | {sum(r['word_matches_history']for r in new)}/{len(new)} |",
      f"| Número correcto dada la operación física emitida | {sum(r['correct_given_actual_operator']is True for r in new)}/{len(new)} |",
      f"| Artefacto material completado | {sum(r['real_artifact_completed']for r in new)}/{len(new)} |",
      f"| Artefacto completado dentro del presupuesto modelado2 | {sum(r['completed_within_prepared_modeled_budget2']for r in new)}/{len(new)} |",
      f"| Rutas físicas −/0/+ o sin salida | {json.dumps({str(v):sum(r['route']==v for r in new)for v in(-1,0,1,None)},sort_keys=True)} |",
      f"| Conteo preparado: números correctos / oportunidades nominales | {f['native_count']['numeric_correct_given_actual_operator']}/{f['native_count']['scheduled']} |",
      f"| Composición asistida: números completos / oportunidades nominales | {f['composition']['numeric_correct_given_actual_operator']}/{f['composition']['scheduled']} |",
      f"| Crudos128: coincide con criterio fijo / oportunidades nominales | {sum(r['matches_expected']for r in raw)}/{len(raw)} |",
      f"| Cadena transaccional: commit real / FINISH nominal | {f['chains']['transaction_commits']}/{f['chains']['nominal_finish']} |",'',
      'Una emisión léxica correcta, un número correcto condicionado a esa emisión, un archivo escrito y un coste bajo son resultados distintos. Los rechazos y las abstenciones no desaparecen. Los criterios de coste son propiedades del entorno preparado, no termodinámica o CPU de DEE. El evaluador no introduce esas comprobaciones en las decisiones online.','',
      '## Docencias y regímenes efectivamente recibidos','',
      '```json',json.dumps(f['explicit_teaching'],sort_keys=True,ensure_ascii=False,indent=2),'```','',
      'La docencia de total/quita y la revisión de beta son iniciativas explícitas del operador. Una hora programada no acredita admisión, adquisición ni retención. Los primeros usos y posteriores de ambas formas se conservan en PANELES_Y_FUNCIONES.json; seis interfaces españolas representan dos clases de operador preparadas, no seis conceptos nuevos.','',
      '| Régimen | Nominales | Estados de transporte | Memoria/historia | Palabra/historia | Número/operador |','|---|---:|---|---:|---:|---:|']
    for r in f['regimes']:lines.append(f"| {r['regime']} | {r['nominal_scheduled']} | {json.dumps(r['nominal_transport'],sort_keys=True)} | {r['memory_matches_history']}/{r['memory_uses']} | {r['APD_word_matches_history']}/{r['APD_primitive_executions']} | {r['APD_numeric_correct_given_actual_operator']}/{r['APD_primitive_executions']} |")
    lines+=['','El último panel observado precede al ocio final; no certifica acceso después de un futuro no consultado. No se suman controles o ramas alternativas como recuerdos de MAIN.','',
      '## Atribución y límites','',
      'Anatomía, formas/canales, árbol aritmético, conteo, calendarioP0, recursos genéricos, actuador de bytes, secuencia solicitada por el usuario y puente son preparados. La asociación de signo y sus cambios se verifican en la dinámica DEE. La ruta se lee de O2; el calculador externo sólo se invoca cuando la emisión física lo solicita y se declara como herramienta, no cálculo nativo. La composición transporta el resultado realmente producido, no recalcula el intermedio ni aprende un plan. Los controles causales y límites de aprendizaje de política están en los componentes científicos correspondientes, no se infieren de esta hora sola.','',
      'Los descriptores antiguos del audit-hook se preservan. Su bandera universal sobre históricos sobreestimaba la lógica efectiva: S/estado era legible para continuidad. La revisión del código decisor y los controles son evidencia distinta; este registro no es un sandboxOS ni prueba de imposibilidad de un lector oculto arbitrario. La corrección posterior de esa descripción no reescribe primarios ni cambia permisos/física.','',
      '## Recálculo y omisiones','',
      f"Recálculo: {calc['serialized_RAW_observations_checked']} observacionesRAW serializadas y {calc['complete_uint64_checked']} uint64 completos; discrepancias={len(calc['issues'])}. Repetir una observación archivada no es otro individuo. PLAN_RECALCULO.json ejecuta sólo Python estándar desde los datos exportados, sin motor/Runtime/trabajador. Reproducción nativa, comprobación operativa del ZIP exacto y análisis archivado son pruebas diferentes.",
      'INDICE_OMISIONES.json y los manifiestos emparejados localizan snapshots, SQLite y telemetría completa conservados localmente. REGISTROS_APD exporta todos los campos de las filas del prefijo propio y de los siete pendientes heredados, con selección reproducible y SHA/tamaño del contenedor original. No se afirma identidad binaria de un gzip proyectado ni respaldo operativo autosuficiente.','']
    with a.salida.open('x',encoding='utf8')as out:out.write('\n'.join(lines))
    print(json.dumps({'report':str(a.salida),'new_native_ticks':0}))
if __name__=='__main__':main()
