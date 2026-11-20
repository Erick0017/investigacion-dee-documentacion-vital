# Recálculo archivado del preflightR3

Se examinaron exclusivamente los13primarios cerradosR3_01…R3_13. El recálculo
ejecuta0ticks, no cargaRuntime, no usa el gestor actual ni ejecuta trabajadores.
Todos los primarios son de`MU_MAIN_FASE_R3` y la misma revisión ejecutada
`4ce1da2ec1d5bc638aadc273b1d1e60f5600d2bdbcc607a4d4be584ac489459d`.
No hubo códigos de proceso adversos, timeouts ni mensajesstderr omitidos.

| Función observada | Evidencia | Resultado y denominador |
|---|---|---|
| Revisión explícita de referencia |R3_01–02|A120/B141→A121/B141;D−21→−20;unaB0,1/1admitida|
| Habilitación del calendarioP0 |R3_03|0ticks y mismos hashes completosRAW/clocks queR3_02|
| Seis contenidos previos, antes |R3_04|−,+,+,−,−,+;6/6lecturas,42/42insumos|
| Sensores13y32 |R3_05–06|−y+, respectivamente;4/4insumos cada uno|
| Trama simultánea128,index4 |R3_07|19en0,2en4,resto0;+,176/176insumos|
| Memoria gamma→preparación real |R3_08|+,7/7insumos;archivo comprimido13bytes|
| Guardar/cargar y concluir |R3_09–10|mismosRAW/clocks de prefijo;13bytes reales→−,4/4insumos;commit aceptado|
| Seis contenidos previos, después |R3_11|misma secuencia,6/6lecturas,42/42insumos|
| Guardado y lectura final |R3_12–13|T70223,A123/B143,D−20;sin rebobinado físico entre operaciones|

Los recibos nativos únicos son6511…6790: **280solicitados,280admitidos,
0rechazados,0sin resolver**. Incluyen docencia y recursos genéricos, no sólo
entradas crudas. Hay17lecturas funcionales válidas dentro de una misma vida;
no17capacidades nuevas ni17réplicas independientes. Los dos trabajadores
realizaron2operaciones aceptadas que cerraron **una** transacción.

El pending llevaba los bytes exactos del artefacto13B y su payload122B. El
recálculo verifica base64, hashes, descompresión y correspondencia con la
medición13B y el testigo de lectura/restauración del verificador. También
verifica el producto32B de compromiso. La identidad comprobable desde estos
primarios comprende vida declarada, hashes físicos del prefijo y bytes externos
serializados; no se afirma identidad byte a byte de toda agenda y metadatos
de los completos, que no se reabrieron para este recálculo.

## Límite decisivo de atribución

**B0 fue reenseñanza/revisión explícita**, no retención intacta, reparación por
el flag, ni recuperación iniciada porE1. El número de docencias explícitas pasó
20→21y permaneció21; la cadena no añadió retornos docentes ocultos.

**P0 fue prevención preparada.** Todos los sensores/trama/finalización del
preflight tuvieronwait0. Estos13primarios prueban que el protocolo habilitado
puede utilizarse con las otras funciones; no prueban por sí solos que haya
evitado una nueva fase crítica. El desplazamiento efectivo6ticks y su efecto
causal corresponden aR16, conservado por separado. El nuevo ensayo3720sR04
no forma parte de este recálculo y requiere su propio cierre.

Los seis contenidos son asociaciones físicas opacas previamente adquiridas,
no seis procedimientos ni significadosNSM. Tampoco se deduce128conceptos,
control general, estabilidad ilimitada o regulaciónP2/R2.

## Repetición del cálculo

Desde esta carpeta:

`python -I -B RECALCULO/recalcular_preflight_r3.py --evidencia PRIMARIOS --salida RECALCULADO/PREFLIGHT_R3.json`

La salida debe coincidir byte a byte con`RECALCULO_REFERENCIA.json`.
`PLAN_RECALCULO.json` declara script, argumentos y referencia; el paquete
contiene las copias exactas de todos los13primarios, preprotocolo y fuentes
pertinentes de la revisión archivada. No es un paquete continuable del ente.
