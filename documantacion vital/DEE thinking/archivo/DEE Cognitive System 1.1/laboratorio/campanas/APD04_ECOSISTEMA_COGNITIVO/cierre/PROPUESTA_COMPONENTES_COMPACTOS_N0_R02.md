# APD04 — propuesta de análisis compacto, todavía sin ensamblar

No se creó ningún ZIP, no se editó S o Word y no se ejecutó Native. La lista medida está en `PROPUESTA_COMPONENTES_Y_TAMANOS_N0_R02.json`, SHA `2d31e38e74bd8eb0d7a3d12bacf0a782c8305c08d4b8be1ee4425b40cb8d01f7`. Son844 archivos seleccionados,34053311 bytes expandidos, aproximadamente9652615 bytes DEFLATE+cabeceras sin deduplicar rutas. Las cabeceras se estiman conservadoramente; el tamaño final deberá comprobarse en el ZIP exacto.

| Componente propuesto | Archivos | Comprimido estimado, bytes | Qué no debe perderse |
|---|---:|---:|---|
|MAIN: piloto fallido, piloto real, preparación, adquisición, prologue adverso, bifurcación y90s |144|871287|Incidencias instrumentales, fuentes ejecutadas, agenda no enviada y un pendiente exacto, no sólo éxitos|
|Controles léxicos/docenteB/referencias |172|855242|Omisiones, signos opuestos, A que pasa a NULL, REF_OMIT con continuación no perfectamente emparejada|
|Autopsia de supervisión MAIN |16|202322|SQLite extraído sin modificar, marcador incierto, STOP no confirmado; no llamarlo crash cognitivo|
|Recálculo MAIN y panel heredado |6|175606|RAW del panel16+6 y localizadores exactos;16 ya incluye luma/nara|
|Sensores, A/B/C y contexto de densificación |135|2290711|C6 completas/10 solicitadas en bloques; cuatro sin resultado no son cuatro fallos|
|R04 cerrado adverso |31|446408|Cuatro oportunidades0 útiles, panel final0/22 y rechazos; no inferir borrado|
|ActuadorR02 REAL/OMIT y corrección |145|617983|Dos historias, panel antiguo, primera divergenciaop4, dosis211/140 completas|
|Reserva: sólo dos oportunidades comprometidas |40|3499118|Global RAW/clocks y contextos; útil SUCCESS antes de densificación, luego NULL; sigue siendo prefijo parcial|
|Corrección completa de dosis A/B/C |3|16980|246/276/123 y conciliación Full por ID; no reutilizar204/186/102 como totales|
|Arranque, admisión, calibraciones e incidencias |76|376315|Todos los intentos, incluyendo negativos; sólo raíz de admisión, no su respaldo heredado completo|
|Revisiones exactas de drivers y planes |32|107711|R01 reconstruido con SHA confirmado, R02 y R03 distintos, calendario y criterios congelados|
|Propuestas prospectivas NO_NATIVE |23|77178|WAITR03 y pruebas N0 son preparación; no adjudicarles ejecución o capacidad|
|Borradores científicos y herramientas N0 |21|115732|Correcciones R06/R07 y calculadores portátiles; el informe final puede consolidar texto sin borrar su procedencia|

## Reserva de espacio y componentes todavía abiertos

Se propone reservar1.6 MB para las cuatro cohortes breves2/5/10/20,2.6 MB para el cierre de la reserva y un eventual R03 ejecutado, y1.2 MB para Word, informe final, tablas, pruebas Full exactas e índice. Total orientativo15052615 bytes, con947385 bytes de margen bajo16000000. Esas cifras futuras son presupuestos de empaquetado, no datos ya generados ni cuotas que autoricen eliminar evidencia indispensable.

Controls informó N2 cerrado y N5 todavía abierto al preparar esta propuesta. Su componente previsto es `NIVELES_BREVES_AUX_R02/EVIDENCIA_NIVELES_BREVES_CERRADOS_N0_R01` cuando existan los cuatro cierres. Se incorporarán las cuatro ramas y sus desenlaces reales, incluidos timeouts, pendientes y pérdidas. Ninguna ausencia de resultado se convertirá en éxito o fallo cognitivo.

La reserva larga sigue en `RESERVA60_REAL_R02_R01/TRAYECTORIA/EVENTOS.jsonl`. Una hora de pared no acredita por sí sola64 acontecimientos o43 oportunidades. La agenda pendiente, los niveles no alcanzados y los rechazos deben quedar separados. El esquema y el criterio del plan no se debilitarán después de mirar el resultado.

## Compactación permitida y exclusiones

La estimación mantiene copias byte-idénticas en rutas distintas para no romper importaciones ni calculadores. Existe ahorro adicional posible, pero sólo podrá usarse mediante materialización o deltas sin pérdida verificados. No se deduplicarán revisiones diferentes bajo el supuesto de equivalencia, ni se omitirán resultados adversos para conseguir el tamaño.

Los snapshots completos, SQLite y artefactos heredados completos permanecen locales con sus manifiestos y localizadores. En particular, `ADMISION_LEXICA_R01/PREFIJO_LEX_P0_POSTSTOP/` es un respaldo operativo heredado, no2750 nuevos ensayos APD04; la propuesta conserva sus documentos raíz, manifiesto y resultado de admisión, no ese árbol entero. Los arrays exportados de C y reserva no son snapshots continuables.

No viajarán el motor, WHL, binarios, ZIP históricos, Full de colaboración ni todos los checkpoints. La evidencia de la prueba del Full exacto sí viajará cuando se ejecute; nunca se la reemplazará por una copia de su guion todavía no ejecutado. El Word y la fuente seleccionada para el Full esperan autorización/corte de Root. Seleccionar un prefijo aprendido T639374 como perfil operativo no autoriza atribuirle la duración o la historia del futuro adverso.

## Preparación disponible para el cierre

`preparar_entrega_apd04_r01.py` recibe un `RESULTADOS_FINAL.json` aprobado explícitamente por Root y ensambla sólo la selección con hashes. `recalcular_analisis_apd04_n0_r01.py` ejecuta calculadores portátiles sin motor, red, procesos externos ni accesos a los históricos. La etapa de sellado abre el ZIP exacto, comprueba CRC/miembros/hashes, extrae en otra ubicación y repite los recálculos seleccionados. Ninguna de esas etapas está ejecutada sobre el corte final todavía.
