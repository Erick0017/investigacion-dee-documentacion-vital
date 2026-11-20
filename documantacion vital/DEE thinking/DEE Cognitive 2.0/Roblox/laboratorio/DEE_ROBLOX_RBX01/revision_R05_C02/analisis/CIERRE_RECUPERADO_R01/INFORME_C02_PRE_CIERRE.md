# DEE–Roblox R05-C02: memoria, composición y actuación verificable

**Borrador científico con resultados cerrados hasta el 15 de noviembre de 2026.** Fecha de inspección de este borrador: 15 de noviembre de 2026, aproximadamente 08:30 UTC (02:30, America/Mexico_City). Este documento distingue desarrollo, controles y evaluación. Las secciones de MAIN R02 y de los dos comparadores permanecen **PENDIENTES DE RESULTADOS**. No se adelanta su desenlace ni se considera terminado el benchmark.

Las rutas siguientes son relativas a `DEE Cognitive 2.0/laboratorio/DEE_ROBLOX_RBX01/revision_R05_C02/`, salvo indicación expresa. Ésta es la única sede de C02; los expedientes anteriores permanecen como antecedentes.

## 1. Qué se está investigando y qué se ha observado

La pregunta es si una continuación física de DEE puede utilizar asociaciones, números y resultados sucesivos para obtener un efecto dentro de Roblox, y cómo cambia ese uso después de nuevas experiencias. No basta emitir dos comandos de movimiento. Deben distinguirse la elección física de DEE, la selección de una operación mediante una asociación y la secuencia de dispositivos preparada por el investigador.

Ya hay tres resultados cerrados y un resultado adverso que deben conservarse:

1. **DEV4, Native y Roblox reales en una misma continuación:** una lección visible luma−/nara+ precedió a la lectura física luma−, que seleccionó una diferencia `6−2→4`. Después de guardar y reabrir la misma pareja, la lectura física nara+ seleccionó la suma `actual4+1→5`. El entero real 5 habilitó la recogida de una unidad del inventario simulado tras contacto espacial registrado. No hubo entrega en la base durante el horizonte de cuatro oportunidades.
2. **MEMPAIR, control focal Native cerrado:** en una sola vida, antes de la lección invertida, luma+ llevó a `6+2→8` y nara− a `actual8−1→7`; después, luma− llevó a `6−2→4` y nara+ a `actual4+1→5`. Una variante posterior `7−3→4` utilizó la asociación revisada. Las cinco oportunidades numéricas formaron resultado. Ésta es una adquisición y utilización contextual en una trayectoria; la especificidad de la enseñanza emparejada necesita todavía el brazo desincronizado.
3. **Corte ambiental del enlace B:** al reproducir externamente los mismos comandos registrados, conservar el entero Native 5 produjo una recogida; suprimir ese producto impidió la aceptación del código y la recogida. Son dos reproducciones del entorno con **cero ticks Native**, no nuevas decisiones ni aprendizaje de DEE.
4. **MAIN R01 adversa:** dos de las seis entradas solicitadas para la primera lección fueron rechazadas por ocupación RAW. El actor estricto preservó ese futuro y terminó la operación como `failed_preserved`. No se ha demostrado que se borrara la memoria ni que DEE fuera incapaz de utilizar todos sus contenidos.

Estos resultados no equivalen a una política de navegación aprendida, un plan multietapa autogenerado, aritmética adquirida desde cero, lenguaje general ni agencia general. Tampoco justifican un PASS global.

## 2. Identidad, genealogía y protección

El padre protegido comprobado es `ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01`, perfil `fisica_directa`, **N67, T947395**, selección principal COMMITTED. El Manual rector de Cognitive tiene contenido interno 1.40. El panel histórico 12/12 corresponde a un corte anterior, T943970; no se atribuye otro panel completo al último T947395 ni a los finales C02.

Todas las ramas C02 parten de un conjunto completo del mismo prefijo, no de una reconstrucción T0. Las ramas comparten pasado y no son réplicas independientes. Sus experiencias no se fusionan.

| Rama | Padre | Corte observado en evidencia cerrada | Estado y atribución |
|---|---:|---:|---|
| Principal protegido REAL2_01 | Genealogía PI10 preservada | T947395 | Principal; no modificado por C02 |
| C02_DEV | REAL2_01 T947395 | **T953651** | Desarrollo cerrado; cuatro oportunidades; no seleccionado |
| C02_MAIN R01 | REAL2_01 T947395 | **T947852** | Futuro adverso preservado tras admisión parcial; no seleccionado |
| C02_MEMPAIR | REAL2_01 T947395 | **T956779** | Control focal cerrado; seis oportunidades; no seleccionado |
| C02_MEMCTRL | REAL2_01 T947395 | Sin resultado ejecutado acreditado en este borrador | Material/preparación no equivale a ejecución |
| C02_MAIN_R02 | REAL2_01 T947395 | **PENDIENTE DE RESULTADOS** | Candidata nueva explícita; no rebobina MAIN R01 ni hereda DEV/MEMPAIR |

Los IDs completos de las ramas añaden `ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_` al sufijo de la tabla. La nueva candidata es `ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_MAIN_R02`.

El prefijo estable se conserva en `DEE Cognitive 2.0/reproducibilidad/materiales/PI11_REAL2_PRE_T947395/`; su manifiesto de exportación tiene SHA-256 `f80c72145dc5b20e1c0c066d0bab9755183eea6e7c7ef89c8ce33b8339788d19` y el snapshot codificado `fd7372b7f2adc9040866fab8adfaca0d79e0bd18e997c0abc0651fe4fa3c23dc`. El snapshot solo no sustituye interfaces, agendas, progreso, SQLite, recibos y recursos del conjunto.

La cápsula de código preservado `reproducibilidad/codigo_preservado/PI11_HABITAT16_FAMILIA_R02/` comparte dependencias sin duplicarlas por función. Universe v27 y Thinking 4.5.0 permanecen congelados; no se atribuyen al núcleo cambios de Cognitive ni del transporte.

## 3. Mecanismo y frontera entre DEE y el anfitrión

### 3.1 Enseñanza y recuperación de una asociación

`capacidades/c02_funciones_native.py` adapta las interfaces legales ya existentes. La enseñanza reutiliza `lexico_generico_apd03_r02.teach`: entrada cue de magnitud 5 y teacher de magnitud 11, más el soporte de revisión declarado. No escribe una respuesta en RAW, no modifica clocks y no introduce un banco de palabras externo como memoria del participante.

El lector común36 de `lexico_compartido_apd04.query` permanece fijo. Su consulta es material: q+4 es la ventana de lectura y q+7 el fin de la consulta. Carga cero no se considera neutral por definición. Los signos permitidos de este contrato son +1 y −1; ausencia de firma no se transforma en cero ni se busca otro lector favorable.

Durante la estación ARCHIVE se hacen visibles luma/nara y sus signos. En los cálculos posteriores se ofrece la palabra sin el signo actual. Por tanto, la elección de operación depende de una salida física recuperada, no de volver a entregar el signo correcto con cada cálculo. Las oportunidades, el momento de enseñar y la identidad de las palabras son preparación externa.

### 3.2 De una salida física a una operación numérica

El codec es fijo: signo Native +1 corresponde a `suma`; signo −1 corresponde a `diferencia`. Es una correspondencia preparada y limitada. Python no calcula cuál de esas operaciones sería conveniente para esa oportunidad. La ausencia de signo produce ausencia de operación admitida; no una sustitución por la respuesta esperada.

El cálculo utiliza el árbol FI128 existente a través de `pi09_aritmetica_temporal_P0_R01.execute_public`/`aritmetica_apd_01.native_pair`. Los operandos admitidos son enteros 0..32. La conversión complementaria y el bias de diferencia son codificación fija; el resultado procede de la salida FI128, con su firma, no de una calculadora Python. Un cero material es válido y distinto de NULL. Los valores efectivamente formados no se corrigen para ajustarlos al objetivo.

El cálculo A crea un objeto numérico real. El dispositivo B recibe ese **valor actual**, no el previsto. Un nuevo A invalida el antiguo B mediante versionado de transporte. Si A está ausente o fuera del dominio de entrada, el dispositivo no inventa 0 ni ejecuta una función con un operando ficticio: deja constancia del impedimento. Esa guarda es asistencia de interfaz, no abstención autónoma de DEE.

### 3.3 De DEE al personaje y a la consecuencia

Q1 recibe el estímulo escalar fijo `1+zona+8·llave+16·recurso+32·fallo_previo`, además de disponibilidad de consulta. Q2 puede recibir la señal pagada del panel local o una omisión de muestra. El rango utilizado es legal para el puerto 0..65535. Que el escalar sea invertible para el auditor no demuestra que DEE descomponga sus bits como variables.

Las salidas físicas seleccionan ASK/SKIP/espera y EXIT_0/EXIT_1/espera. El cuerpo sigue una geometría y trayectos por puerto preparados; el motor no descubre aquí un modelo locomotor. El contacto con cada dispositivo ofrece su función. **DEE selecciona acciones locales y, mediante memoria, el opcode; el anfitrión prepara el orden de herramientas asociado a los lugares.** La secuencia memoria→operación→segunda operación→cerradura es integración asistida P0, no un plan nativo demostrado.

La ley genérica de retorno usa colisión, acción inválida o rechazo de código. Los peajes y consultas se contabilizan aparte. Un falso de consecuencia conserva su canal material: no es omisión del retorno. Se distingue suministro ambiental, estado Native y RAM/CPU del anfitrión. La unidad recogida pertenece al entorno simulado; no es energía nativa, metabolismo ni alimento físico.

### 3.4 Instrumentación y rechazo parcial R02

Los resultados completos y recibos de cada función se conservan fuera de los metadatos compactos. La versión R01 detenía la operación si no se admitían todas las entradas. La versión R02 preserva todos los recibos y el futuro físico, pero devuelve `formedFalse/numeric_result=None/reason=NATIVE_PARTIAL_ADMISSION` y continúa por el camino normal NO_RESULT→consecuencia. No reintenta las entradas, no limpia puertos y no inserta un recuerdo.

Ese NO_RESULT es una decisión conservadora del contrato de admisión. **No prueba que la memoria nativa no haya cambiado.** En una lección completamente admitida, `formed=False` significa que se enseñó sin consultar todavía; el Body R02 distingue este caso del rechazo parcial por `reason`/`capability_execution_admitted`, no por el campo formed aislado. El contenido se comprueba en una consulta posterior.

Los diarios y el estado privado del evaluador son del auditor. Los logs completos se preservan por generaciones/chunks; las colas Tail de hasta 64 eventos no se confunden con toda la historia ni alimentan las decisiones.

## 4. Repertorio reutilizado y alcance comprobado

La lectura C02 fue dirigida a contratos, código y primarios necesarios. No se declara una nueva lectura integral de los manuales Thinking ni de toda la biblioteca. Se reutilizan la cobertura previa y los localizadores de `fuentes/LOCALIZADORES_REPERTORIO_BASE.json`. El Manual Cognitive se consultó parcialmente como OOXML textual; no se declara revisión visual completa ni modificación del Manual.

| Familia | Base reutilizada | Comprobación C02 cerrada y límite |
|---|---|---|
| Asociaciones/revisión | luma+, nara−, clasifica−, suma+ en panel PI10 | MEMPAIR usa dos signos antes y después de una lección invertida; desincronía todavía no ejecutada/acreditada |
| Memoria contextual/retención | alfa− y contextos en cortes PI10 | nara+ utilizada en DEV después de reapertura; no nuevo panel alfa/contextos en final C02 |
| Comparación +/−/0 | FI128 y ventanas históricas distintas | No nuevo panel de los tres signos; no equiparar q+6 NULL con q+4 cero |
| Aritmética | Árbol Native y codec preparado | DEV2/2 y MEMPAIR5/5 salidas numéricas formadas, con denominadores dependientes de una sola vida por rama |
| Composición/transporte | Resultado real utilizado en otra operación | DEV A4→B5→recogida; control ambiental suprime B y pierde el efecto; orden preparado |
| Percepción/selección | Dos trazas y consulta pagada | DEV cuatro ciclos locales; ningún efecto de separabilidad de bits supuesto |
| Consecuencias | Selección física histórica; controles PI10 acotados | Retorno real integrado; no nueva prueba exclusiva de contingencia frente a yoke |
| Iniciativa/recurrencia | Recurrencias y oportunidades preparadas | No plan, iniciativa de tarea o exploración aprendida acreditados por estas pruebas |
| Protección/regulación | Mecanismos históricos PI02/PI10 | No nuevo resultado de regulación; ocupación/rechazo no equivalen a dolor |
| Comunicación | Resultados IC/MI en vidas concretas | Lección ambiental C02 no es conversación de dos participantes independientes |
| Acceso/recuperación | Recuperación asistida histórica | Dos admisiones rechazadas localizadas en R01; no recuperación Native probada aquí |
| Continuidad/integración | Prefijo completo y reaperturas documentadas | DEV misma sesión/vida tras reapertura; principal protegido; ningún nuevo panel12/12 al final |

La tabla detallada, con localizadores y límites, está en `fuentes/MATRIZ_REPERTORIO_C02_DEV4_R01.csv`. Su corte precede a MEMPAIR terminal; éste se añade mediante los primarios y el recálculo descritos a continuación, sin reescribir la historia de aquella matriz.

## 5. Resultados cerrados

### 5.1 DEV: misma vida, reapertura y efecto ambiental

Vida `...RBX01_C02_DEV`, N67, T947395→**953651**, **6256 ticks nuevos**, cuatro oportunidades completas. Hubo ocho IDs de acción distintos, cuatro IDs de retorno y **424 entradas Native únicas: 424 aplicadas**. Son eventos materiales, no 424 conceptos ni ensayos independientes. El cursor se reabrió desde T950523 con la misma sesión lógica `60224961780f4f319bb573508864c02b` y sin volver a enseñar.

| Función | Intervalo Native | Salida observada | Primario |
|---|---:|---|---|
| Lección luma−/nara+ | 947773–947852 | 6/6 entradas aplicadas; contenido comprobado después | `0ae4fd42937b4de4953188bb6d4c5be7.json` |
| A, luma, 6 y2 | 949337–949595 | Signo−1; diferencia; entero4 | `f80862fee3d44e9689934783fe50e16b.json` |
| B, nara, actual4 y1, tras reapertura | 950901–951136 | Signo+1; suma; entero5 | `cb40497d81d34483b120e97e2209c7ee.json` |

Los primarios están en `native/DEV/sistema/estado/servicios_locales/<vida>/RBX02_NATIVE_C02/functions/`. Cada cálculo solicitó 183 entradas únicas, todas aplicadas. La cerradura examinó el código real5 y lo aceptó; se registró contacto espacial de recurso. `resourceUnits` pasó12→11, `resourceCount`0→1 e `inventoryResource`false→true; hubo cero colisiones. El mesh reutilizable no desapareció y no se afirma una apertura geométrica de puerta.

La entrega a la base fue0. El horizonte de cuatro oportunidades concluyó en estación5, antes de una quinta oportunidad de retorno: no se presenta como un intento de entrega fallido ni como entrega completada.

Fuentes completas: `evidencia/DEV_REAPERTURA_R04/WORLD_RESTORED_BEFORE_NATIVE.json` (206557B,SHA `3f330b9d6bee4f3f3e9872ccfeabbdf273233d23f16d69e79d9717f08ee761dd`) y `WORLD_FINAL.json` (277074B,SHA `7813c015dbf7a8b0eef33006ce0a3864b591359c68609051fec746a6d3890435`). Recálculo: `analisis/DEV_FINAL_RECALCULO_R02/RECALCULO.json` y `HECHOS_Y_ATRIBUCION_DEV_R02.json`; 52 eventos World únicos tras deduplicar el prefijo repetido, tres primarios y cero incidencias del recálculo. No se repitió el motor para obtener este recálculo.

### 5.2 MAIN R01 adversa: admisión conocida, no desaparición demostrada

La primera lección de MAIN R01 ofreció luma+/nara−. La operación `6fbe0205c45a49d183107acf83c21170`, cola seq3615, terminó `failed_preserved` el 15-11-2026 a06:50:47.697994UTC. El intervalo real fue **T947773→947852:79 ticks**. Se preservó su snapshot, SHA `361bf334e05241fb825de6752b20bd0a0bd84a23424adb4b6fede38ba4da44cf`.

Se solicitaron seis entradas: cuatro aplicadas, dos `rejected_occupied`. Los rechazos fueron `revision.luma.1`, payload11, sitio[44,7,44], tick947782, y `revision.nara.-1`, payload11, sitio[47,4,50], tick947849. El motivo fue «target register is not RAW-empty at application boundary». Cue y teacher sí se aplicaron. No se limpiaron esos sitios para forzar admisión.

DEV y MAIN tenían exactamente los mismos N/T/RAW/clocks antes de la primera lección, pero pedían signos y, por tanto, rutas de revisión diferentes. DEV admitió6/6. Esta comparación localiza una diferencia de admisión dependiente de la ruta material; no identifica todavía la genealogía del ocupante ni demuestra borrado del contenido antiguo. La operación Native era terminal conocida, aunque la capa puente la clasificó genéricamente UNCERTAIN. La conciliación posterior del transporte y de los79ticks debe consultarse en su comprobante específico; la inspección científica no modificó colas ni ledger.

Fuente: `analisis/MAIN_PRIMERA_LECCION_ADMISION_R01.json`, más primario `native/MAIN/.../RBX02_NATIVE_C02/functions/6fbe0205c45a49d183107acf83c21170.json`, SHA `d332a973938ffce74f551dd29bf17f502764209276655fc456f194737ca12f3d`. El futuro adverso R01 no fue reescrito para crear R02.

### 5.3 MEMPAIR: cambio de referencia y de operación en una sola trayectoria

Vida `...RBX01_C02_MEMPAIR`, N67, **T947395→956779**, +9384ticks. Sesión focal `FOCAL_MEMPAIR_890d8c97759d`; protocolo congelado SHA `d2ba5f6bde24d9f3d3f60955e42fa5b25ae8bbf6e04fcd76651063ca0f1f93cc`. El propietario terminó cerrado y guardó el corte final.

| Oportunidad | Experiencia/consulta | Signo Native y resultado real | Corte después del retorno |
|---:|---|---|---:|
|1|luma,6 y2|+1→suma→8|948959|
|2|nara,actual8 y1|−1→diferencia→7|950523|
|3|Lección luma−/nara+,revision legal|6/6 entradas aplicadas; aún sin consulta de palabra|952087|
|4|luma,6 y2|−1→diferencia→4|953651|
|5|nara,actual4 y1|+1→suma→5|955215|
|6|luma,7 y3, variante posterior|−1→diferencia→4|956779|

Son **cinco salidas numéricas de cinco oportunidades numéricas**: dos testigos iniciales de memoria heredada, dos usos tras la revisión y una variante de operandos. No son cinco aprendizajes independientes. Las seis oportunidades generaron 24 solicitudes focales, todas completed; **987/987 entradas únicas aplicadas**. La diferencia respecto de la dosis DEV procede también de la consulta omitida en este protocolo focal; no se fuerza una igualdad de cantidades entre diseños distintos.

El recálculo verificó seis primarios íntegros, recibos, calendario y transporte del valor actual8 y luego4. La cola terminal se abrió exclusivamente `mode=ro/query_only`, sin WAL no vacío y con hash idéntico antes/después. No hubo Native Q1 NULL ni fallo genérico en esta secuencia. El estado físico final guardado tiene RAWsha `d6613b0e2e57c8edcfad195b569edbcd79473fc5e5820539235d657f8d136002` y clockssha `6c47e7a54f3bfa2397bec5b471cff2cea1da78cb21984231d7f1a32ab8d42541`.

Esto acredita uso antes/después de una experiencia legal en esa genealogía, no sólo un catálogo. No aísla por sí solo enseñanza emparejada frente a edad, otras experiencias o desincronía. **MEMCTRL no tiene ejecución terminal acreditada aquí.** No se transfiere el resultado MEMPAIR a MAIN_R02 ni al principal. La oportunidad y el orden de funciones fueron preparados; esta prueba focal no ejecutó Roblox.

Fuentes: `evidencia/CONTROL_MEMPAIR_R01/{RESULTADO.json,Fases.jsonl}`, seis primarios bajo `native/MEMPAIR/.../RBX02_NATIVE_C02/functions/`, y `analisis/CONTROL_MEMPAIR_RECALCULO_R01/{RECALCULO.json,HECHOS_Y_ATRIBUCION.json,COLA_TERMINAL.json,RECIBOS_UNICOS.csv}`. El recálculo conserva sus hashes y arroja cero incidencias.

### 5.4 Corte del producto B: control del efecto en Roblox

Los dos brazos R02 restauraron el mismo estado ambiental archivado y reprodujeron externamente los cuatro mismos comandos posteriores. En INTACT se transportó el producto Native5 ya registrado. En CUT_B se suprimió su disponibilidad; no se reemplazó por0.

| Medida del intervalo de reproducción | INTACT | CUT_B |
|---|---:|---:|
|Consultas / movimientos|2 /2|2 /2|
|Variación de permisos / peaje|−2 /0|−2 /0|
|Tiempo ambiental / ticks Native nuevos|20.25s /0|20.25s /0|
|Colisiones|0|0|
|Recurso recogido / unidades consumidas|1 /1|0 /0|
|Rechazo de código|0|1|

El estado inicial S y los comandos fuente eran exactamente iguales. Se conservaron todas las trece diferencias finales de S; la geometría final tuvo cero diferencias. El resultado es una dependencia de la recogida respecto del producto transportado bajo esa ley ambiental. No es evidencia de nuevo aprendizaje ni de reacción Native al corte: el anfitrión seleccionó todos los comandos de reproducción y no devolvió consecuencias a DEE.

En ambos brazos Native quedó archivado en T950523/dos ciclos mientras el entorno llegó a cuatro. Por ello **no son checkpoints de pareja continuables**. Las diferencias posteriores de lastFailure/observación son consecuencias legítimas del corte; no se impusieron futuros endógenos idénticos.

Fuentes: `evidencia/CONTROL_ENLACE_NUMERICO_{INTACT,CUT_B}_R02/RESULTADO_AMBIENTAL_REPLAY_C02.json` y `analisis/CONTROL_ENLACE_NUMERICO_RECALCULO_R02/{RECALCULO.json,TODAS_DIFERENCIAS_ESTADO.csv}`. Los hashes de los primarios y estados fuente se recalcularon y coincidieron. El intento ambiental R01 anterior conserva su negativo separado en `evidencia/CONTROL_ENLACE_NUMERICO_INTACT_R01/LIMITE_CONOCIDO.json`: error Lua `C02_EXACT_CURSOR`, cero ticks Native; no se contabiliza como un brazo CUT_B ejecutado.

## 6. Evaluación prospectiva R02 de tres participantes

**PENDIENTE DE RESULTADOS.** El lanzamiento de la nueva sesión Native fue informado por el coordinador a08:26UTC; este borrador no lo convierte en oportunidades completadas ni en una ejecución verificada. La evaluación Native y los dos comparadores se incorporarán aquí después de sus registros y cierres.

El protocolo definitivo es `protocolo/PROTOCOLO_EVALUACION_C02_R04.json`, WorldId `RBX01_R05_C02_R02`, escenario SHA-256 **`562d277322ab2a2094bc34009aad03b352d151b2865f4843965e6eb1bc6964d7`**. Se fijaron, antes de su primera petición material: **18 oportunidades**, frontera de guardado/reapertura6, periodos1–6/7–12/13–18 y reserva13–18. Las versiones anteriores42 y36 se conservan, sin contarlas como evaluaciones completadas.

Los signos se invierten en8..13 y vuelven desde14; precios cambian en9/12/15/17. Las tuplas reservadas comienzan13 y se capturan al adquirir una llave. La cerradura evalúa la ley de signos vigente al llegar, no necesariamente la de la última visita a ARCHIVE. Una ronda que cruza un cambio puede sufrir rechazo sin que haya olvido o error aritmético; el análisis debe registrar esa distinción.

El horizonte se ajustó prospectivamente usando latencias observadas, sin ampliar la cuota Native máxima48 ni el límite agregado200000ticks/seis mundos. La última Q1 nueva está fijada10:00UTC y el corte Native10:30UTC; cierre global12:15UTC. Las cantidades CPU/RAM del anfitrión se reportarán separadas del tiempo y memoria causal DEE.

Hay dos residuos editoriales en el JSON congelado que no cambian la evaluación: el texto libre de `measures` conserva intervalos del diseño36, mientras `opportunities`, `periods`, `reserve` y Config fijan18; la descripción de sensor omite la constante+1 que sí aplica el código. Las tablas finales deben utilizar los campos estructurados y el codec ejecutado, sin modificar retrospectivamente el protocolo sellado.

### 6.1 Native MAIN_R02

**PENDIENTE DE RESULTADOS:** oportunidades solicitadas/completadas, retornos, lecciones, signos, admisiones, números, códigos, costes, recursos, entrega, conservación, reapertura y corte final. No se sumarán los resultados DEV o MEMPAIR a esta vida. No se tratará NULL como0 ni una operación failed_preserved como no ejecutada.

### 6.2 PROGRAMMED

**PENDIENTE DE RESULTADOS:** trayectoria con referencia programada, mismo entorno e información admisible y contrato de actuadores. La política escrita por el diseñador se declarará como referencia externa y nunca controlará a DEE. Deben documentarse el código exacto, las decisiones, la memoria exterior permitida en esta referencia, las oportunidades reales y su coste.

### 6.3 CONVENTIONAL_AI

**PENDIENTE DE RESULTADOS:** modelo local, identidad/configuración efectiva, contexto, fallos de formato, latencia, decisiones y resultados. No se atribuirá a DEE conocimiento preentrenado del modelo. Si no se ejecuta o no produce un resultado válido, se registrará ese impedimento concreto y no una inferioridad cognitiva universal.

### 6.4 Qué hará comparable la tabla final y qué no

Los tres brazos deben compartir escenario/leyes, horizonte, información perceptible y oportunidades. Los comparadores reciben sólo el percepto legal, sus señales y herramientas visibles, nunca el mapa privado, futuros, código objetivo ni diario del auditor. La representación escalar Native y la representación textual de una IA no son cómputos idénticos; la información disponible y la asistencia deben quedar explícitas.

Una trayectoria por participante no constituye una población estadística. Las ramas de DEE comparten prefijo; los ciclos no son individuos independientes. Deben conservarse números formados, utilidad ambiental, costes, rechazos y oportunidades perdidas por separado. Ni una victoria puntual ni la ausencia de un recurso por horizonte justifican superioridad o incapacidad general.

## 7. Reproducción, continuidad y punto de reanudación

El código operativo nuevo está localizado en los paquetes experimentales; el producto principal y su Manual no se modificaron para esta tarea. La preparación R02 utiliza `native/preparar_descendiente_C02_R02.py`, el importador oficial aislado `native/rbx02_import0_C02_R02.py` y `native/r02_bundle/`. El helper es byteidéntico al de R01; el cambio del actor trata resultados de admisión conocidos sin reinterpretar la física ni reparar la respuesta. Los hashes y la configuración efectivos deben tomarse del scope R02 y del sellado prospectivo, no de este texto.

La ejecución Native requiere un clon diagnóstico explícito, su estado completo y los guardas del propietario/ledger; no se proporciona aquí una orden informal que eluda esas protecciones. No se abre el principal para revisar este informe. Las herramientas siguientes sólo recalculan registros; no importan DEE ni ejecutan Roblox:

- `analisis/RECALCULO_FUNCIONES_Y_MUNDO_C02.py`: primarios de función, journal Native y estados completos World; salida nueva explícita mediante `--output`. No considera un Tail como historia completa.
- `analisis/RECALCULO_ENLACE_NUMERICO_AMBIENTAL_C02.py`: contrasta los dos controles ambientales cerrados y conserva todas las diferencias, con salida nueva sin sobrescritura.
- `analisis/INSPECCION_COLA_CONTROL_MEMORIA_C02.py MEMPAIR`: requiere resultado terminal/propietario cerrado; lectura SQLite mode=ro y hash antes/después. No enviar a una vida activa.
- `analisis/RESUMIR_CONTROL_MEMORIA_C02.py MEMPAIR`: contrasta resultado focal, primarios, recálculo, cola terminal y VIDA. Requiere salida ausente para no sustituir un comprobante.
- `analisis/COMPARAR_CONTROLES_MEMORIA_C02.py`: preparado para comparar ambos controles **sólo cuando existan dos cierres terminales**; no representa un contraste ya realizado ni ejecuta el brazo que falta.

Cada receta y salida distingue recálculo documental, ejecución Native y reproducción exclusivamente ambiental. El expediente compacto es análisis, no respaldo ejecutable del ente. Los conjuntos operativos y telemetría íntegra permanecen locales.

**Punto de reanudación de este borrador:** completar MAIN_R02 sin modificar el padre protegido; conservar cada operación y su recibo, exportar World completo en fronteras coherentes, comprobar reapertura sin reenvíos ambiguos, y completar o declarar no ejecutados los dos comparadores. Después recalcular los nuevos primarios con el lector previamente fijado y sustituir únicamente los apartados pendientes de este mismo informe. No reconstruir resultados a partir de resúmenes ni fusionar futuros.

## 8. Conclusión provisional y límites concretos

DEE ya ha contribuido algo distinto de un controlador binario: una emisión de memoria física eligió una operación numérica y su resultado real se utilizó en otra operación y en una consecuencia ambiental. DEV muestra esa integración asistida con continuidad tras reapertura. MEMPAIR añade un testigo antes/después en una sola trayectoria: cambió el signo recuperado y con él cambió la operación posterior. El control de B confirma que, en el caso registrado, el entorno no obtiene la misma recogida si se le quita el producto pertinente.

Lo que falta no se sustituye por una afirmación de autonomía. Permanecen preparados el cuerpo, el codec, las oportunidades y la secuencia por estaciones. Falta el cierre de la evaluación larga, la comparación real de participantes y el brazo de enseñanza desincronizada. La entrada ocupada de MAIN R01 es un límite de admisión localizado; no demuestra pérdida global de contenido. La gestión NO_RESULT de R02 es una mejora técnica declarada, no autorreparación aprendida.

**Incorporación al principal:** ninguna acreditada en este corte; el encargo protege el principal. **Manual Maestro:** no modificado por C02. **Resultado científico final de los tres brazos:** pendiente. Este borrador queda preparado para integrar registros reales sin convertir planes, preparaciones o fallos técnicos en capacidades demostradas.
