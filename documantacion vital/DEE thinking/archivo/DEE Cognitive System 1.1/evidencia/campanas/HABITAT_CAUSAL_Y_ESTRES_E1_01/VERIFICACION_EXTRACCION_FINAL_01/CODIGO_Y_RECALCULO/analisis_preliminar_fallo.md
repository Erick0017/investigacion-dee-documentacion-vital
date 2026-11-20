# Fallo de acceso: análisis primario previo a nuevas intervenciones

Lectura retrospectiva de registros existentes; cero ticks por este análisis. Es un diagnóstico provisional, no prueba de pérdida global de información, aprendizaje o muerte del ente. Rutas relativas a `evidencia/campanas/HABITAT_CAUSAL_Y_ESTRES_E1_01/` salvo indicación.

## Recuentos comprobados

“Calificada” significa únicamente state1, semantic1 y dirección±X o0 dentro del codec fijado; no equivale a respuesta correcta ni aprendizaje.

|Registro|Ventana|Salidas calificadas|Lectores ambientales solicitados|Recibos nuevos applied/occupied/conflict|
|---|---:|---:|---:|---:|
|MAIN_NOISE_NOMINAL_03.json|4492→5296|10/12|12|30/14/4|
|MATCHED_NO_STRESS_04.json|4492→5296|12/12|12|24/12/0|
|MAIN_DEMANDING_R5_06.json|5296→6368|0/16|16|39/17/4|
|MATCHED_NO_NOISE_R5_07.json|5296→6368|0/16|16|32/16/0|
|ACTION_NULL_R5_08.json|5296→6368|0/16|16|39/17/4|
|MAIN_SCARCITY_09.json|6368→7172|0/12|4|24/4/0|

Denominador de recibos nuevos: `requested_tick > result.initial.tick`, estados finales de `receipts`. Denominador de respuestas: todas las filas, incluidas ocho oportunidades sin lector en escasez. Cada bloque es una trayectoria, no12/16 individuos independientes.

SHA-256 de los primarios leídos:

- MAIN_NOISE_NOMINAL_03: `7c9ec799285edbbaace8363df0cdbe1a7300481bb6da60306e34bcee6a907450`.
- MATCHED_NO_STRESS_04: `1a2b790d832f38ed2d72ae86ca46506f6c10c21df4ae10c98dc36d929376859f`.
- MAIN_DEMANDING_R5_06: `129bc0270989ac58d86b74935d3ce9f612ae91f4644f9369fdd1ca67033cd48d`.
- MATCHED_NO_NOISE_R5_07: `20c7e69c6ca6ca146a13599e2f9b0bf4c958911d7ed7ce38958e3e5b54e76488`.
- ACTION_NULL_R5_08: `6b079a8f988e79ec426e094c8ef1475a982b9c9435f8e4bcc30abaf7580031ec`.
- MAIN_SCARCITY_09: `1218f80269af8eec4edd83565a410cd78f30a490c9ce9eff9357e6e87f90db64`.

## 1. Omisiones intermitentes T4827 y T5162

`MAIN_NOISE_NOMINAL_03.result.rows[4]`, lectura4827: magnitud74, ruido adicional `quantity.object.cue` carga3 en4822, ID1676. Los DOS cue simultáneos1673/1676 fueron `rejected_conflict`; recurso1674 se aplicó; lector1675 fue `rejected_occupied`. Falta el operando formateado en `[51,36,35]` y centroRAW0. ReferenciaY78 sigue en `[49,36,35]`, y lectorZ7 en `[50,35,36]`.

`rows[9]`, lectura5162: magnitud74, ruido cue5 en5157, ID1696. Cue1693/1696 rechazados por conflicto; recurso1694 aplicado; lector1695 rechazado por ocupación. Otra vez centroRAW0, objeto formateado ausente y referenciaY78 visible. Un portadorXY13 aparece en `[50,34,35]`, inexistente en la muestra previa5095.

Lecturas posteriores4894 y5229 vuelven a emitir direcciones calificadas sin restauración del ente. Es una pérdida intermitente de uso en esos episodios, no evidencia de destrucción de la referencia78.

El mero rechazo del lector más reciente NO basta como explicación: en MATCHED_NO_STRESS_04 los12 lectores nuevos fueron rechazados por ocupación y aun así hubo12 salidas calificadas. Algún lector material anterior o contexto ya presente participa. No adjudicar el linaje sin la traza de ticks.

Limitación del control04: el R4 original usa el mismo RNG para ruido y perturbación del depósito. `noise_rate=0` cambia cuántos draws se consumen, así que sus perturbaciones exógenas no coinciden exactamente con03; además acciones distintas producen futuros legítimamente distintos. El control conserva valor descriptivo pero no aísla perfectamente el ruido. El wrapper nuevo de omisión consume los mismos draws antes de omitir las entradas físicas.

## 2. Inicio del fallo persistente es anterior al ruido exigente R5

En `MAIN_NOISE_NOMINAL_03.result.rows[10]` T5229, referencia `[49,36,35]`=Y78; XY13 en `[50,34,35]`; salida+X7.

En `rows[11]` T5296, esa ubicación ya contiene XZ85, RAW`1225260938693705729`, dirección[1,0,1]. XY pasó a20, RAW`1157706665110274049`; el lector en `[50,35,36]` sigueZ7. La última salida del centro todavía es−X7. Por tanto una última respuesta calificada no certifica que la referencia original siga intacta.

Snapshot completo origen R5: `sistema/estado/checkpoints/E1_ECO_MAIN.T5296.12f47048f2e7.deetsnap.gz`, SHA `f5128d5abc430dd865f4e5180bd4cb9f5ea661515387c95605bd36c069a1261d`, cero entradas pendientes. Se cotejaron los campos de esa región con `rows[11]`; coincidieron. Búsqueda global exacta no encontró s_reg78 en ese corte. Esa ausencia de valor no prueba que la información78 sea globalmente irrecuperable: puede haber transformaciones o diferencias distribuidas, y no se compararon historias completas alternativas.

En T5363, MAIN_R5 y su control SIN NUEVO RUIDO muestran ambos XYZ92 en `[49,36,35]`, RAW`1292814963169034241`, dirección[1,−1,1]. En5430 esa ubicación está vacía en ambos. Sus16 respuestas son todas no calificadas. La dosis4/amplitud25 nueva no es necesaria para iniciar este fallo; heredan un paisaje ya transformado en5296. La identidad aritmética85=78+7 y92=85+7 sugiere una contribución del lector pero NO establece el encuentro ni su linaje: eso exige la traza y cortes/sham.

Índices lineales N67 para revisar ventanas decisivas:

- `[49,36,35]` →222408: soporte de referencia observado.
- `[50,34,35]` →226763: XY13→20 candidato contextual.
- `[50,35,35]` →226830: salida/ingreso del lector habitual.
- `[50,35,36]` →226831: Z7 recurrente visible.

Las lecturas coinciden en clock=tick en las muestras examinadas. No se encontró indicio de conversión float o rechazo de unidades del codec en estos primarios: las solicitudes son enteros legales y las respuestas inválidas son RAW0 real. Esto no certifica ausencia de otros fallos de interfaz o ventanas.

## 3. Entradas concretas para ablaciones mínimas

Primera ventana nominal4822→4827: omitir únicamente ruido1676, conservando cue1673/recurso1674/lector1675 y mismos otros inputs, permite examinar conflicto de admisión sin editar memoria.

Segunda5157→5162: omitir únicamente ruido1696; seguimiento posterior debe conservar resto de inputs. No repararMAIN.

Origen de transformación5229→5296: ruido ID1700 `quantity.reader` carga2 en5225 pertenece al episodio5229, pero fue rechazado por ocupación: no se aplicó esa materia. El siguiente ruido1704 `quantity.object.cue` carga0 en5293 sí fue aplicado y pertenece al episodio5296. Carga0 no equivale a ausencia: conserva state1 y dirección−X. En5291 cue1701 y recurso1702 de magnitud78 fueron aplicados; reader1703 en5295 fue rechazado por ocupación. IDs y estados válidos según recibos del primario03. No atribuir la transformación a1704 sin intervenir y comparar.

Ruido R5 inicial:1708 resource16@5361;1709 resource0@5358 (conflicto con recurso normal1706);1710 cue24@5361;1711 resource7@5359. Pero omitir todos ya produjo el mismo fallo inicial en07. Su corte por sí solo no explica el origen anterior.

Para el origen conviene trazar desde el último estado completo anterior a5229. El wrapper `diagnostico_origen_nominal_R4.py` reutiliza fuenteR4 exacta desde4492 y sólo captura5200..5296. La reproducción debe igualar campos/recibos/filas originales antes de utilizar sus trazas como evidencia nueva. El wrapper está preparado; esta nota no afirma que se ejecutó ni que pasó.

## 4. Recuperación y alcance

Tras tres fallos consecutivos se detuvo nuevo ruido exigente. Los13 episodios restantes sin él siguieron sin salida; retirar estrés no recuperó por sí solo el uso hasta6368. La posterior escasez comenzó sobre ese estado ya fallido y obtuvo0/12: no permite afirmar que la escasez causó la pérdida inicial ni que el ente murió. Las cuatro solicitudes de lector fueron rechazadas; las ocho omitidas no deben contarse como rechazos.

ACTION_NULL_R5 produjo el mismo silencio y el mismo futuro ambiental observable que MAIN porque no hubo comandos no neutros que anular; es un control degenerado para demostrar efecto causal de acciones en esa ventana. Debe usarse una ventana con salidas efectivas para esa pregunta.

Los datos sostienen al menos dos mecanismos candidatos diferentes: conflicto de admisión de acontecimientos actuales con referencia visible, y transformación posterior del soporte/ruta de referencia heredada. No se concluye conservación funcional total, convergencia causal irreversible, autorregulación, techo cognitivo o pérdida global a partir de ellos.
