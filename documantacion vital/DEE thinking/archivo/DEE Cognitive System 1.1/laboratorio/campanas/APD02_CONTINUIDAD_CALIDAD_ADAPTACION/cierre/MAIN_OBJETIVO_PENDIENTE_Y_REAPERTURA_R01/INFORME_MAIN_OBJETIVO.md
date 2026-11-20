# Objetivos y continuidad pendiente en la misma vida MAIN

## Resultado observado

Las dos ventanas cerradas pertenecen a APD02_MAIN, N = 67, desde T443018 hasta T454808. No se trasladaron aprendizajes del auxiliar a esta vida. Esta revisión es retrospectiva: cero ticks nuevos y ningún motor importado.

En una secuencia continua se ejecutaron tres objetivos reales, no cuatro objetivos independientes. El tercero se dividió entre dos propietarios:

| Objetivo | Datos públicos iniciales | Actuación física observada | Resultado real |
| --- | --- | --- | --- |
| goal_1 suma 7 y 4 | Segundo operando oculto | QUERY material 0, después ACT − | Archivo con 11 |
| goal_2 diferencia 19 y 6 | Ambos operandos visibles | ACT − | Archivo con 13 |
| goal_3 total 9 y 5 | Segundo operando oculto | ACT − falla por dato no observado; después de guardar y cambiar de proceso, QUERY 0 y ACT − | Archivo con 14 |

Hubo seis oportunidades materiales: dos QUERY, tres ACT con archivo correcto y un ACT sin el dato necesario que falló sin ejecutar proveedor numérico. Los cuatro fragmentos de ejecución de la referencia corresponden a estos tres objetivos. Los archivos se verifican en sus miembros exactos del export emparejado, no se reconstruyen desde Base64.

Después de completar la petición pendiente se admitió una entrada nueva suma [0, 32], con archivo 32. El panel viejo conservó 6/6 signos históricos [−, −, +, −, −, +]. Las dos formas nuevas siguieron activando funciones distintas: compara produjo − en el lector actual y recuerda produjo + al consultar gamma. La acumulación renovada con incremento 0 y demora de tres períodos produjo 45; el cursor monótono pasó de 15 a 16, sin reiniciarlo.

## Continuidad exacta entre propietarios

El primer propietario, PID 90468, guardó T449274 con SHA-256 6623df064dd0855ce409e46fa0b254d9edf6138ef1a92f0249e62236a33052ef. El segundo, PID 92020, comenzó desde exactamente ese archivo completo. La petición apd02g1_goal_next conservó ID, secuencia 1629, payload, hash y tiempos de llegada. Se admitió una sola vez: el segundo propietario esperó el ID existente, sin volver a insertarlo. El contador ambiental continuó de la oportunidad 1 a la 2, con el segundo operando todavía no observado; no se reinició el objetivo.

Las 17 admisiones nuevas corresponden a 17 filas completadas: 9 materiales y 8 controles. Las 915 solicitudes nativas únicas quedaron aplicadas: 915/915, cero rechazos y cero pendientes al cierre observado. El epoch 6 permaneció abierto; los propietarios terminaron y el Job quedó sin procesos, sin terminación forzada. El corte T454808 no es el corte futuro de la reserva larga, que no se atribuye a esta evidencia.

La copia SQLite archivada durante exportar conserva legítimamente su propia fila export processing. El recibo nativo comprometido y el outbox coinciden exactamente y satisfacen el criterio de reconciliación sin reejecutar la acción. Esto no prueba una importación de esa copia: el segundo propietario de esta ejecución utilizó el diario real postSTOP. El auditor no ejecuta reconciliaciones ni callbacks.

## Evidencia, cálculo y límites

REFERENCIA_MAIN_OBJETIVO_R02.json verifica 5447 condiciones y decodifica 1327 observaciones RAW, sin discrepancias. Comprueba las 28 puertas léxicas exactas, las tres puertas del selector R04, las puertas fijas de los lectores anteriores, los números nativos, archivos reales, recibos y la identidad FIFO. Los cinco testigos de estado permiten reconstruir RAW y clocks completos, interfaces, entradas pendientes y metadatos operativos, cotejados con sus hashes físicos y con los archivos completos locales. Se omite el historial completo de recibos nativos; estos testigos no son snapshots continuables.

El código de extracción conserva el vínculo de cada artefacto con su episodio en la fuente MU.session congelada. No busca una respuesta favorable por nombre: calcula el episodio a partir del contador final y la posición de la fila, verifica el miembro relativo exacto del export, sus bytes y su SHA-256. Los nombres y hashes de los snapshots completos omitidos constan en EVIDENCIA/CONTEXTO_ARCHIVADO.json.

La ampliación instrumental que agregó los lectores antiguos tuvo inicialmente un TypeError por sombrear una variable local. Se corrigió únicamente el auditor y se repitió el recálculo de archivos, no la física. La referencia anterior R01 permanece para genealogía; R02 es la referencia vigente con el panel adicional.

La selección ACT/QUERY procede del lector físico. El mapa − → ACT y 0/+ → QUERY, los recursos, las oportunidades, la aritmética y el criterio de terminación siguen siendo preparación P0. Los controles causales de consecuencias proceden de los experimentos auxiliares R04 y GOAL AUX; estas dos ventanas MAIN acreditan uso consecutivo e integración, no son por sí mismas una réplica causal emparejada adicional. El orden variable observado no demuestra percepción semántica de un dato ausente, iniciativa de calendario, planificación general ni R2 general. El estado privado b pertenece al mundo externo serializado y no se suministra a los codecs nativos ni al selector antes de QUERY; no se afirma una prohibición universal de lectura del host.

## Recálculo

Ejecutar con Python estándar: `python RECALCULO/recalcular_main_objetivo_r01.py --evidence EVIDENCIA --output resultado_nuevo.json`. El destino debe ser nuevo. PLAN_RECALCULO.json identifica la referencia vigente; PRUEBA_PORTABLE.json documenta una ejecución desde una copia en otro directorio sin imports del motor ni ticks.
