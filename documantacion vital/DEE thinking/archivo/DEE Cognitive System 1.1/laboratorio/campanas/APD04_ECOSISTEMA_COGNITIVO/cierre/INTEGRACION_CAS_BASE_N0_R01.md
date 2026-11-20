# Base CAS APD04: reducción exacta, lista para selección de cierre

Esta es una extracción N0 separada, no un ZIP ni el cierre de APD04. No se modificaron los componentes archivados, S, Word, Full, vidas o snapshots. Se conservaron las844 rutas de la propuesta R02 y todos sus34053311 bytes originales. Las186 rutas duplicadas apuntan a658 objetos únicos. No hubo deduplicación por semejanza, reconstrucción de RAW/clocks ni exclusión de un resultado negativo.

Tamaño comprimido estimado de la base CAS:8306828 bytes, por debajo del objetivo de9000000. Antes:9652615 bytes; ahorro estimado1345787. Permanecen aproximadamente7693172 bytes bajo el límite16000000 para las dos AUX R03, nueva reserva, cuatro cohortes, Word y demás cierre. La estimación usa DEFLATE real en memoria y cabeceras conservadoras; no reemplaza la medida final del ZIP exacto.

## Ubicaciones y prueba efectuada

Directorio: `LAB/cierre/CANDIDATO_CAS_BASE_N0_R01/`.

`RUTAS_Y_HASHES.json` enlaza cada ruta original con su SHA y objeto. SHA del índice: `abfbb0a491b995de1edfaf443c234a5e83945071bd9ad8b1155629e16b7a29db`. SHA del manifiesto: `1e356771788adc92ba838d56673c35867a31fd70aee6fccbe30935b2de74e688`.

Primero se materializaron todas las rutas en un temporal nuevo y se compararon sus bytes con los hashes archivados. Después se ejecutaron las tres CLIs reales seleccionadas para el cierre adverso R04, el prefijo de reserva de dos oportunidades y el panel ancestral. Los tres resultados coincidieron byte por byte con sus referencias.

Se verificó además el CLI CAS sin subprocess dentro del ejecutor maestro real y su cerca de acceso. El trabajador sólo pudo leer el paquete y la biblioteca estándar y escribir en su salida nueva. Materializó la evidencia allí y ejecutó las tres CLIs en el mismo proceso. El resultado final fue byte-idéntico a la referencia CAS, SHA `5f1c7144b5dd28883a4f0d116adc2523e69552822ac16d9a9a82d6ce4062bf96`.

Comprobantes: `PRUEBA_MATERIALIZACION_Y_RECALCULO_CAS_N0_R01.json`, `PRUEBA_CAS_EN_CERCA_MAESTRA_N0_R01.json`, `REFERENCIA_CAS_PORTABLE_N0_R01.json` y `PRUEBA_TAMANOS_CAS_BASE_N0_R01.json`. Son cálculos de evidencia ya producida, no nuevas simulaciones, adquisición ni comprobación Full. Ningún ZIP fue creado.

## Incorporación a la selección final de Root

`FRAGMENTO_SELECCION_CAS_BASE_N0_R01.json` entrega un componente, dos archivos y un job compatibles con `RESULTADOS_FINAL.schema.json` y el ensamblador R01. Añadir ese fragmento a la selección final aprobada evita copiar otra vez sus844 rutas de forma convencional. Los acontecimientos posteriores deben añadirse como componentes nuevos, no atribuirse retroactivamente a esta base.

La entrada maestra emplea `recalcular_cas_en_proceso_apd04_n0_r01.py` y no lanza procesos hijos. Dentro del job usa la copia CAS de `RESTAURAR_Y_RECALCULAR_CAS.py`, las rutas resueltas y los tres calculadores archivados. El CAS puede distribuirse en `EVIDENCIA_CAS_BASE/`; el investigador lo restaura en una carpeta temporal, sin acceso al corpus original ni motor. Su mapa no es una memoria que consulte E1.

No se editará esta revisión después de la prueba. Para añadir otros cortes a un CAS futuro, crear otra revisión y repetir materialización/hash/recálculos afectados. No modificar objetos o manifestar un nuevo resultado debajo del mismo SHA. El informe científico y el Word final deben permanecer legibles fuera del CAS; no son reemplazados por nombres de objetos.
