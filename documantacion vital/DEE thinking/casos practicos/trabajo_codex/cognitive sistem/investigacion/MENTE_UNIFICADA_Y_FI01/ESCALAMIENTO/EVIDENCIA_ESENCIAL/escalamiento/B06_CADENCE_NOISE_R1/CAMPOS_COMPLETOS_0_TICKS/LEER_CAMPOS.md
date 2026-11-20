# Campos completos, exportados sin avanzar DEE

`INDICE_CAMPOS.json` identifica los mundos completos originales, sus hashes y los bloques comprimidos deduplicados. Cada bloque descomprimido contiene exactamente N³ enteros uint64 little-endian en el orden del motor: el desplazamiento lineal de x/y/z es `((x*N)+y)*N+z`. RAW y clocks se conservan por separado, sin conversión a coma flotante.

Estos archivos permiten volver a calcular ocupación y distribuciones de campos globales, además de examinar cualquier región del mundo exportado. No contienen por sí solos interfaces, colas y progreso operativo; **no son snapshots continuables**. Los snapshots completos permanecen localmente en las rutas indexadas.

El corte inicial es T16640, con las dos tramas futuras ya encoladas. Ambos mundos tienen entonces24sitios activos y campos físicos idénticos, pero el calendario de su segunda trama difiere. El corte final es T17427, **después** de las seis consultas materiales del panel antiguo: Δ2 tiene297621sitios activos y Δ16 tiene25. No se deben confundir con la medición pasiva anterior T17038, que dio283382y24respectivamente y no se guardó como snapshot completo en ese tick.

La igualdad o diferencia de campos, y la ocupación, no acreditan por sí solas memoria funcional destruida ni linaje de un portador. El recálculo de estos bloques está incluido en `recalcular_b06_b07.py`.
