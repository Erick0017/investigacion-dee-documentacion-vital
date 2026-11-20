# Objetivo y aclaración mediante dos acciones físicas

El retorno común de un objetivo todavía incompleto cambió una selección posterior de CONSULTAR a ACTUAR. Ese cambio produjo un archivo correcto; omitir el retorno conservó CONSULTAR y agotó las cuatro oportunidades sin completar el objetivo. El resultado pertenece a las bifurcaciones AUX aquí identificadas, no a MAIN.

## Organización y preparación

Se utilizó el snapshot completo APD02_R04_ACTUAL_real T407640, N67, perfil fisica_directa, SHA 1f35915466a68bb54be12da863757d9c44d90ce03cec5692f84f758da7acf6af. Este padre había adquirido previamente la historia de ocho tareas R04 del frente de mecanismo. No se trasplantó a MAIN. Las cuatro trayectorias son copias deterministas de ese mismo prefijo, no cuatro individuos que aprendieron independientemente.

El selector R04 y el circuito numérico ya existían físicamente. Se reconciliaron explícitamente los metadatos operativos del asistente R03→R04 sólo en cada copia, porque el padre había ensayado R04 mediante su módulo directo, aunque conservaba el antiguo nombre operativo. Antes y después se comprobaron RAW, clocks, tick, entradas pendientes, canales y contadores de agenda iguales; no se instalaron semillas ni se editaron campos aprendidos. Se conservaron los bytes y snapshots de ambas descripciones.

La transducción preparada fue −ACTUAR, 0/+CONSULTAR; 0 es una emisión material, no silencio. CONSULTAR revela el segundo operando real y no calcula la respuesta. ACTUAR sólo puede llamar al árbol aritmético nativo cuando sus operandos ya son observables; después se escribe un JSON real y un evaluador externo post-terminal comprueba semántica, número, bytes y hash. La condición de éxito y la terminación son asistencia declarada. No hubo calculador externo ni llamada alternativa al fallar.

El dato privado b reside legítimamente en el estado operativo del entorno, serializado junto con el estado completo para continuidad. Ni el codec léxico ni el selector lo leen antes de una CONSULTA. El núcleo no recibe desde ese estado el número correcto ni una lista de pasos. La disponibilidad de b tampoco se codificó como un sensor aprendido para seleccionar una acción.

## Resultados prospectivos

| Trayectoria | Objetivo y disponibilidad inicial | Acciones físicas | Archivo correcto | Panel antiguo final | Admisión nativa |
|---|---|---|---|---|---|
| hidden_real | suma 7,4; b oculto | CONSULTAR→ACTUAR | 11, 142 bytes | 14/14 | 315/315 |
| hidden_omit | mismo objetivo; retorno omitido | CONSULTAR cuatro veces | Ninguno | 14/14 | 174/174 |
| visible_real | suma 7,4; ambos visibles | CONSULTAR→ACTUAR | 11, 142 bytes | 14/14 | 315/315 |
| reserved_difference | diferencia 17,5; b oculto | CONSULTAR→ACTUAR | 12, 143 bytes | 14/14 | 315/315 |

No hubo rechazos nativos ni abstenciones de acción en estos cuatro protocolos. Son diez oportunidades en total entre las cuatro ramas, no diez réplicas independientes. Tres de cuatro objetivos se completaron; no se interpreta esa fracción como estimación estadística de generalidad. El control con datos visibles no constituye una adquisición independiente del caso oculto: ambos emitieron inicialmente CONSULTAR y, después de ese efecto, sus cortes finales completos resultaron byteidénticos.

En hidden_real y hidden_omit la primera acción fue 0 material en el mismo q=T407967. Ambas hicieron observable b=4 y llegaron a T409392 con el mismo objetivo incompleto y el mismo estado público. Después de guardar y restaurar en otro proceso, la segunda consulta del selector se fijó en q=T409531 en ambas. Con retorno real emitió − y actuó; con retorno omitido emitió 0 y volvió a consultar. El cambio útil depende de la consecuencia anterior, no de que Python haya elegido ACTUAR al detectar un dato disponible. La ausencia de archivo en el control no se sustituyó por una acción favorable.

La reserva de resta utiliza otra forma adquirida y otros operandos, bajo el mismo lector y mapeo de acciones. Su valor 12 procede del registro nativo observado en C, con la representación afín preparada de resta, y coincide con el archivo real; no es una resta aprendida desde cero ni un algoritmo numérico adquirido.

## Continuidad y límites

El primer proceso PID91308 guardó cada trayectoria después de una sola CONSULTA en T409392: b ya era observable, el objetivo seguía incompleto y el contador era uno. El segundo PID91204 restauró los campos físicos completos y exactamente los hechos operativos del entorno, sin repetir la primera acción. Los positivos finalizaron en T411856 y el control omitido en T415005, después de sus respectivos paneles de catorce formas. No se clonó ni verificó un servicio SQLite con estas pruebas; es continuidad nativa completa más estado ambiental en copias diagnósticas.

La consulta inicial fue igual incluso cuando b ya estaba visible. Por ello no se demuestra reconocimiento semántico de información ausente, elección inicial óptima ni un orden general de pasos dependiente del contexto. Se demuestra una revisión local de acción por consecuencias, con mejora funcional frente al retorno omitido y conservación del repertorio de señales en estas ventanas. La anatomía, el retorno binario, las oportunidades, el codec de acciones y el criterio de objetivo permanecen preparados P0. La evidencia permite atribuir el cambio posterior al estado físico adquirido de R04; no autoriza R2 general, planificación libre, iniciativa de calendario ni invención de objetivos.

Los procesos terminaron RC0, sin terminación forzada y con cero procesos activos. El tiempo conjunto supervisado fue 386,5286944 segundos; el máximo de memoria comprometida del Job fue 235876352 bytes, inferior al límite 536870912. La exploración respetó el corte fijado sin reiniciar presupuesto.

Recálculo archivado: ocho primarios, cuatro trayectorias, 18993 observaciones RAW exactas y cero discrepancias; reconstruye lectores, signos, acciones, valores nativos, archivos reales, retorno y denominadores por rama. Referencia OBJETIVO_NATIVO_R03_RECALCULO.json, SHA 2015db31ca60f57218c8dd1edcf3355e2da3ce059edd0e595af14e54c517706c. Protocolo previo SHA 8b412e3057e5d527097783be9651542d2a83f218117a70b2e6dd439f8367d285. No se avanzaron ticks durante el recálculo.

Los estados completos permanecen en evidencia/campanas/APD02_CONTINUIDAD_CALIDAD_ADAPTACION/OBJETIVO_NATIVO_R03/{prefix,suffix}/<caso>/. La exportación científica compacta conserva fuentes, primarios, archivos y controles; no reemplaza esos snapshots ni constituye un paquete completo de servicio.
