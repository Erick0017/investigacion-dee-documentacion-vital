# Autopsia de supervisión de MAIN

Se enviaron 9 de 25 acontecimientos del plan; 8 constan completados. La petición del desplazamiento390 quedó procesándose. Ningún acontecimiento previsto desde500 se envió; no se evalúan como fallos cognitivos.

La experiencia explícita A cambió la diferencia de registros, recalculada desde RAW, de 20 a 21. El entorno se cambió a criterio19. Para valores20 y18 las salidas fueron negativas: 1/2 cumplen ese criterio ambiental. La enseñanza no ajustó la referencia a19 y no demuestra P2. No se corrigen retrospectivamente estos resultados.

El driver agotó la espera de la misma petición; STOP no quedó confirmado. Su Job nativo todavía tenía dos procesos activos y consumo CPU registrado al salir. El cierre externo registra después cero procesos. No hay evidencia para llamar a esto un crash cognitivo ni para afirmar la finalización del trabajo pendiente.

El último snapshot comprometido es T658938. El marcador conserva la posibilidad de futuro nativo no comprometido y bloquea la continuación normal. No se borra el marcador, no se limpian colas, no se repite la petición y no se avanza MAIN. APD04_CONTINUABLE_R01 es una bifurcación explícita desde el par completo T639374, no la reparación de ese futuro.

El recálculo portable utiliza EXTRACCION_SQLITE_PRIMARIA.json.gz y este script con --recalcular y --salida. Es análisis archivado, no reproducción nativa. Las cadenas SQLite payload/result se preservan completas; sus registros originales y hashes se localizan en el índice.
