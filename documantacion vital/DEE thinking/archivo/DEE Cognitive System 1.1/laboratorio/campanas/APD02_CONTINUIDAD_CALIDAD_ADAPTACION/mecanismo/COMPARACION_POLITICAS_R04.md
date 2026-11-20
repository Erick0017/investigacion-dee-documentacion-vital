# Referencias externas separadas — R04

Este recálculo N0 no ejecuta DEE, no instala políticas en E1 y no realiza nuevos efectos de archivo. Siempre nativo, siempre externo y WSLS convencional son referencias **analíticas contrafactuales**. Su modelo supone dos proveedores disponibles, correctos, sin retraso ni fallo inyectado; la corrección de una vía no ejecutada en una oportunidad particular no se convierte por ello en una observación empírica. La cota ideal accede deliberadamente a la ley oculta actual y sólo pertenece al auditor.

El WSLS externo comienza en externo. Tras su propia acción obtiene su propia categoría simulada, calculada bajo la ley publicada; si falla alterna, si tiene éxito permanece. No recibe las categorías del learner ni la acción óptima. Las otras referencias tampoco controlan al learner.

| Secuencia | Leyes y oportunidades | DEE observado: coste / útil | Siempre nativo | Siempre externo | WSLS convencional | Ideal privado |
|---|---|---|---:|---:|---:|---:|
| AUX | A2/B3/A1/B2 | 24 / 4 de8 | 28 / 3 de8 | 20 / 5 de8 | 24 / 4 de8 | 8 / 8 de8 |
| MAIN | A3/B2/A4/B3 | 28 / 8 de12 | 32 / 7 de12 | 40 / 5 de12 | 28 / 8 de12 | 12 / 12 de12 |

Los precios son cantidades modeladas de un entorno sintético, no CPU, ticks, RAM ni energía. En MAIN se observaron doce efectos correctos; en AUX, ocho. Los denominadores no incluyen los controles omitido/sham/desfasado ni las preguntas de conservación.

La primera respuesta de cada bloque falló el criterio de recursos en ambas secuencias: el participante no recibió la nueva ley antes de actuar. En MAIN, la siguiente oportunidad del mismo bloque fue útil en los cuatro bloques (4/4 respuestas posteriores a un fallo informativo). En AUX, tres de cuatro respuestas inmediatamente posteriores a un fallo fueron útiles; la restante ocurrió después de otro cambio de ley. El bloque A de una sola oportunidad quedó censurado antes de que hubiera una respuesta útil: no se amplió ni se retocó.

El mecanismo nativo coincide con el comportamiento del WSLS preparado en estas leyes, no lo supera. MAIN presenta ventaja local de coste frente a las dos referencias constantes en esta secuencia concreta; AUX **no**: su coste24 es peor que siempre externo20. La desigual distribución de leyes explica por qué no corresponde extrapolar un ahorro general.

Fuentes originales inmutables: `evidencia/campanas/APD02_CONTINUIDAD_CALIDAD_ADAPTACION/mecanismo/R04_ACTUAL_ABAB/real/OP0..7/RESULTADO_COMPLETO.json.gz` y `evidencia/campanas/APD02_CONTINUIDAD_CALIDAD_ADAPTACION/MAIN_RUTA_R04_R01/{REGISTROS_VENTANA.json.gz,RESUMEN.json}`. Sólo se interpreta una vez cada tarea MAIN, mediante su ID exacto `apd02r4_task01..12_parsed`; no se suman la fila SQLite serializada, su caché parseada ni los controles como nuevos casos.

Stage cerrado y portable: `mecanismo/POLITICAS_R04_R3`, manifiesto SHA `18ef9f687cc2e8fa8b59a124969b8527c4afdc99b37624fc3a6171e34a02dceb`. Un caso stdlib recalcula todas las métricas desde los primarios exportados y reproduce la referencia byte a byte desde otra ubicación. Dos fallos instrumentales N0 previos (directorio reservado AUX y diferencia LF/CRLF) y sus preimágenes exactas se conservan en INSTRUMENTACION. Ninguno avanzó un mundo ni alteró las respuestas.
