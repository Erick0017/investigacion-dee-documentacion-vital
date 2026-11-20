# Enlace perceptivo reutilizable: resultado preparado P0

Se trabajó con copias físicas AUX del snapshot completo de APD02_MAIN T548407, SHA-256 `64359d48edd49f8a1f5616ceacd04c4479a27383877c23381e217a39f0cc05a9`. Cada brazo cargó los mismos bytes, RAW, clocks y metadatos antes de declarar su canal. No se importó SQLite ni se presentó este diagnóstico como una vida operativa emparejada. MAIN, el padre protegido y sistema/ no se modificaron.

## Obstáculo y primer contraste negativo

El antecedente APD02 había distinguido dos causas: un sensor lateral estacionario modificaba la primera salida, pero su fuente quedaba ocupada; el sensor superior se vaciaba, pero el bit1 suprimía el producto del lector. La ROI completa de aquel corte no reveló un producto alternativo oculto. Esos resultados no se repitieron como una nueva campaña.

R01 probó únicamente si dar dirección al sensor lateral resolvía su reutilización, conservando la geometría y el lector R04. Tres direcciones/fuentes declaradas —lateral−X, lateral+Y y lateral opuesta+X— produjeron las siguientes primeras respuestas:

| Familia | Bit0 | Bit1 | Fuentes finales |
|---|---:|---:|---|
| left_x | 0 | +1 | Ambas no nulas |
| left_y | 0 | +1 | Ambas no nulas |
| right_x | 0 | −1 | Ambas no nulas |

Las seis entradas fueron aplicadas y las seis salidas físicas fueron válidas. Cada brazo terminó después de la primera entrada porque su fuente permanecía no nula: no se insistió para acumular rechazos conocidos. Dirección inicial no equivale a vaciado del lugar de inyección. No se limpió ni se reubicó materia.

R01: seis consultas materiales, seis entradas sensoriales aplicadas y 78 peticiones nativas únicas aplicadas, contando también los recursos genéricos. Duración 128.32161510013975 s; pico del Job 255,070,208 bytes; un propietario. El recálculo N0 R02 realiza 6,010 comprobaciones sin discrepancias.

## Segundo contraste: par sensorial simétrico

R02 utilizó dos puertos fijos en E+(-1,0,+1) y E+(-1,0,-1), con E=(25,13,53), N67. Un codec fijo duplicó el mismo bit crudo en ambos: dos entradas state1/SEM1/dirección0 en q+3 para los dos valores. No se retiró ninguna guarda, no se introdujo la acción correcta y no se cambió el lector de tres gates R04.

Se congelaron dos órdenes desde el mismo padre:

| Orden de hechos | Salidas físicas | Fuentes vacías al acabar |
|---|---|---|
| 0 → 1 → 0 | 0 → +1 → 0 | 6/6 lugares observados |
| 1 → 0 → 1 | +1 → 0 → +1 | 6/6 lugares observados |

Las doce entradas sensoriales fueron aplicadas, las seis consultas produjeron salida válida y ambas fuentes fueron RAW0 antes de reutilizarse. Las 84 peticiones nativas únicas se aplicaron; no hubo rechazo. El par conservó la respuesta al mismo bit en órdenes distintos y siguió disponible sin limpieza externa.

R02: duración 106.59165970003232 s; pico del Job 253,894,656 bytes; un propietario. El recálculo N0 R02 realiza 6,074 comprobaciones sin discrepancias.

## Mecanismo delimitado por los registros

Las observaciones de current_tick=q+3 ocurren antes de aplicar durante el paso q+3→q+4 las entradas programadas para q+3. Por eso sería erróneo tratar la foto q+3 como un preestado que ya contuviera los sensores.

La ROI conserva todo Moore26 del encuentro central y los recibos exactos. El gradiente central calculado desde la foto previa es [0,784,0]. Incorporar exclusivamente las dos entradas efectivamente admitidas añade [2,0,0] para bit1 y [0,0,0] para bit0. Las direcciones centrales observadas después del paso son respectivamente [+1,+1,0] y [0,+1,0]. La simetría cancela la contribución Z, en vez de retirar el soporte que limitaba el sensor superior único. Ambas entradas están presentes en q+4 y se vacían nativamente en q+5.

Este contraste apoya una vía causal de la información actual hacia la salida. No reconstruye un linaje único después de un encuentro ni afirma cubrir toda la dependencia compuesta del tick fuera de la región registrada.

## Qué aporta y qué no aporta

Quedó demostrado un enlace sensorial preparado, repetible en el horizonte de tres usos por brazo. El bit es un hecho crudo de una interfaz, no una palabra aprendida ni la respuesta correcta. Si se usa para informar «dato observado o ausente», ese flag es parte explícita del diseño P0.

Los signos 0 y +1 son materialmente diferentes, pero el codec heredado convierte ambos a QUERY. Por tanto R02 solo no demuestra elegir ACT frente a QUERY, reconocer semánticamente qué falta, aprender por consecuencias ni iniciativa. No se le atribuye P2/R2. La aplicación contextual posterior debe conservar este lector y comprobar qué cambia por historia real frente a retorno omitido.

## Localizadores y reproducción

Primarios: evidencia/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/SENSOR_MOVIL_R01 y SENSOR_BALANCEADO_R02. Cada uno conserva RESULTADOS.json, eventos comprimidos por brazo, fuentes exactas, recibos, recursos y checkpoints completos.

Código de los dos candidatos y sus protocolos: esta carpeta mecanismo/. `recalcular_cribados_sensores_n0.py` reconstruye campos RAW exactos, lectores, entradas y denominadores desde los primarios exportados sin importar el motor ni avanzar ticks. Los snapshots completos permanecen locales; los arrays de observación no los sustituyen.
