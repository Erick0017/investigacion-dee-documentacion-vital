# Mecanismos complementarios MA02: selección P1, restauración y límites

Este frente no sustituye a MA02_MAIN ni suma sus experiencias a las de E1. Ensaya preparaciones nuevas identificadas y controles de alcance finito, usando DEE thinking4.5/v27 oficial sin cambios. Las bifurcaciones, repeticiones técnicas y consultas no se cuentan como réplicas independientes. El recálculo es archivado, no una nueva simulación.

## Resultado operativo incorporado

`SELECTOR_P1_MA02` quedó incorporado en `sistema/capacidades/selector_p1_ma02.py` y `sistema/contratos/SELECTOR_P1_MA02.json`. El gestor común ofrece `mente2-p1-estado` y `mente2-p1-usar`. Vidas listas:

| Vida | Corte | Historia propia | Capacidad certificada |
|---|---:|---|---|
| MA02_SELECTOR_P1_H1 | T129 | Dos contenidos adquiridos y contacto genérico anterior | Mismo pedido genérico → selección nativa Y → contenido adquirido− en T205 |
| MA02_SELECTOR_P1_H0 | T129 | Los mismos contenidos, sin el contacto histórico | Mismo pedido genérico → selección nativa X → contenido adquirido+ en T205 |

Son mundos completos N67, perfil `fisica_directa`, importados explícitamente desde los estados vividos auxiliares; la importación no constituye nuevo aprendizaje. No descienden de MA_MAIN_R9, U0, EO02 ni del E1 histórico. Su clasificación es una organización compuesta experimental con dos soportes circulantes, un contexto físico local y una interfaz genérica; no dos mentes autónomas.

La preparación P0 consta de doce sitios SEM4 activos, una referencia fija escalar1, oportunidades de contacto, recursos iguales para ambas rutas y ambos signos y un lector fijo. Los dos contenidos se adquieren en encuentros T3 y T70, no están precargados en la receta. El contacto genérico de carga0 presentado T10 produce una configuración histórica, incluido D con SEM7/carga1 desde T14. Una consulta idéntica de carga0 alcanza E y el gradiente nativo elige X sin esa historia o Y con ella. El anfitrión no observa D para elegir banco. El lector examina siempre los cuatro sitios E+4v±Z y acepta únicamente una emisión SEM1 de dirección pura±Z.

Esta capacidad es **P1 local de primer uso**, no P2/R2, política competente, semántica NSM ni servicio de consulta repetible. El primer uso transforma materialmente la organización. Una segunda petición del adaptador se rechaza expresamente; no genera otro individuo ni reenseña el contenido.

## Controles decisivos del P1

| Primario | Selección/resultado | Qué discrimina |
|---|---|---|
| MA02_P1_TOUCH | Y/− | Historia de contacto con contenidos M0+,M1− |
| MA02_P1_NO_TOUCH | X/+ | Misma anatomía y consulta, sin contacto |
| MA02_P1_OPPOSITE | Y/+ | Con la misma huella y selección, invertir los contenidos adquiridos cambia la respuesta: selector y contenido no son lo mismo |
| MA02_P1_NO_QUERY | Sin emisión válida | La huella y los recursos no se convierten por sí solos en respuesta |
| MA02_P1_CAUSAL_CONTENT_CUT / SHAM | Y/sin respuesta frente a Y/− | El soporte adquirido seleccionado es necesario; no se paraliza la selección |
| MA02_P1_CRITICAL_CUT / SHAM | X/+ frente a Y/− | Cortar D ya formado en T133 cambia el gradiente crítico134 y el contenido utilizado138; control exacto conserva |
| MA02_P1_CAUSAL_HISTORY_CUT | D renace130; Y/− | El corte anterior129 no borra la historia: el contexto local la reconstituye. Negativo conservado, impide atribuir toda memoria exclusivamente a D |
| MA02_P1_CRITICAL_BLOCK_REBIRTH | X/+ | Diagnóstico externo SEM4state0 sobre D impide su renacimiento; no es una acción autónoma del ente |
| MA02_P1_RESERVE_TOUCH_197 / NO_TOUCH_197 | Y/− frente a X/+ | Reserva temporal fijada previamente, +67. Sólo prueba esta fase compatible; no intervalos arbitrarios |

Las intervenciones son copias diagnósticas, nunca reparaciones importadas a MAIN. Se conservan RAW y clocks exactos, pre/post de cortes, contexto local, interfaces, recibos y snapshots completos. El estado T129 contiene también el futuro de la consulta y recursos ya encolados, no sólo los arrays físicos.

## Incorporación y comprobación entre procesos

El adaptador no crea anatomías. `admit` sólo acepta la preparación completa certificada T129; verifica protocolo y recursos, sin leer el contenido de los bancos para decidir. El texto histórico en metadatos se muestra como procedencia, nunca como respuesta.

Los primarios `MA02_P1_OPERATION_*` comprueban admisión sin ticks, uso desde otro proceso hasta T212, guardado y recarga, así como rechazo explícito de un segundo uso. `MA02_P1_SYSTEM_FORK_USE/RELOAD` comprueban el módulo realmente incorporado mediante Store. `MA02_P1_GESTOR_COMPLETO` comprueba doce comandos reales en copias CLI: bifurcar, estado, usar, guardar, recargar/estado y segundo uso rechazado. H1/H0 permanecen T129. Las copias de evaluación llegaron T212. Repeticiones operativas deterministas no aumentan la muestra científica.

Ejemplo real desde `sistema/` con el intérprete compatible ya disponible:

```text
python gestionar.py bifurcar MA02_SELECTOR_P1_H1 P1_MI_PRUEBA --modalidad DIAGNOSTIC_COPY
python gestionar.py mente2-p1-estado --vida P1_MI_PRUEBA
python gestionar.py mente2-p1-usar --vida P1_MI_PRUEBA --detalle
python gestionar.py guardar --vida P1_MI_PRUEBA
python gestionar.py mente2-p1-estado --vida P1_MI_PRUEBA
```

Los nombres de copia deben ser nuevos. Volver a bifurcar desde el corte listo crea otra trayectoria; no rebobina la copia que ya fue utilizada. Continuar físicamente después del primer uso es posible, pero queda fuera del contrato de acceso exitoso.

## Restauración U0 complementaria

No se llamó a `experience_order`, `consequence` ni `action` oficiales fuera de su horario. La preparación U0 oficial se reutilizó y los nuevos acontecimientos se presentaron por interfaces de investigación legales, declarando su asistencia.

`MA02_U0_REPEAT_READ` y `MA02_U0_SINGLE_READ` produjeron cinco acciones+ recurrentes, pero sólo una pregunta horizontal nueva en T19. Repetir comandos por recurrencia no demuestra cinco consultas selectivas nuevas.

Se ensayó después una excursión física con cuatro encuentros genéricos posuso, ambos signos de recursos y solicitudes izquierda/derecha/izquierda/derecha/izquierda. Resultado:

| Primario | Cinco ventanas | Alcance |
|---|---|---|
| MA02_U0_RESTORE_REQUESTED | 5 únicas: +,−,+,−,+ | La restauración de ruta solicitada permite reutilización acotada del contenido adquirido |
| MA02_U0_RESTORE_NONE | 1 única, 4 ambiguas | Productos recurrentes sin restauración contaminan usos posteriores |
| MA02_U0_RESTORE_ALL | 1 única, 4 vacías | Aprovisionar indiscriminadamente también las rutas no solicitadas interfiere |
| MA02_U0_RESTORE_NOQUERY | 1 inicial, 4 vacías | Los recursos no aportan por sí mismos los contenidos posteriores |

La identidad de la solicitud y el aprovisionamiento de su ruta se fijan externamente P0, no por un selector aprendido. Es un procedimiento experimental complementario reproducible, no una extensión tácita del contrato U0 oficial ni una nueva habilidad del MAIN. El código y los estados quedan conservados, sin sumar estos resultados a las cinco memorias inferiores de MA01.

## Tap nativo sin consumir el portador

`MA02_TAP_FULL` prepara siete sitios SEM4 de carga0 y deja vacía una octava posición de una configuración de vecinos opuestos. El paso de un portador por esa posición provoca el nacimiento nativo SEM7 en un detector adyacente T2, persistente en la ventana T2–T6. El portador original continúa con RAW, carga y dirección exactos. `MA02_TAP_PAYLOAD53` confirma lo mismo con otra carga; la preparación principal utilizaba37.

Sin portador, con sólo seis soportes o sin el marco no nace el detector. Los controles de seis/sin marco conservan el portador. Es una transducción preparada no consumidora de **presencia**, no copia de contenido escalar, significado o memoria de trabajo. No se integró este tap como una habilidad de MAIN ni como composición no destructiva: esa aplicación no fue demostrada por este frente.

## Intento explícito de ciclo por consecuencias: resultado negativo

Las variantes `MA02_P1_CYCLE_*`, `MA02_P1_R03_*` y `MA02_P1_R04_*` son once vidas nuevas, no reparaciones del P1 ya validado. Se usó el trabajador local EO02 existente: una dirección nativa± elige una operación real de archivo, y una transacción preparada exige después el trabajador opuesto para verificar. Rechazo real se traduce de forma fija a un contacto genérico de carga0, no a la ruta ni a la respuesta correcta. Se fijaron cuatro ventanas138,205,272,339 y no se terminaron favorablemente después de la primera.

Cada variante emitió sólo la primera dirección válida y abstuvo en las tres ventanas posteriores. Las guardadas con contenidos +/− prepararon correctamente un archivo real, pero no llegaron a la segunda actuación ni al retorno decisivo. Los controles de actuador anulado conservaron la emisión nativa inicial, sin ejecutar el servicio. Las variantes con contenidos opuestos emitieron−, el servicio rechazó y el contacto de retorno se admitió/aplicó, pero no produjo una capacidad posterior de uso.

La observación local explica dos obstáculos concretos, no una incapacidad general de v27:

1. En R02 el primer relé de salida permanecía activo con dirección0, bloqueando futuras emisiones. Terminadores preparados impidieron que recursos sobrantes alterasen el gradiente de E, pero no resolvieron ese relé.
2. R03/R04 modificaron anclas de preparación para mantenerlo direccional; las siguientes ventanas siguieron sin respuesta válida. Además, el contacto que creaba huella antes de activar E ya no completaba el mismo patrón XNOR con E activo: el contexto de vecinos había cambiado. Admitir correctamente la entrada no demuestra que ésta alcance una experiencia plástica útil.

No se infiere P2/R2, aprendizaje de política útil, recuperación autónoma ni estabilidad del servicio. La primera acción aprendida/seleccionada y la capacidad P1 finita se preservan; el fallo del ciclo no las elimina. Tampoco se promocionó ninguna variante adversa a predeterminada.

### R05: corrección dirigida y nuevo fallo anterior a la decisión

Una revisión adicional acotada, autorizada a partir de los estados anteriores, identificó tres contrapartes de actividad vacías en torno a D: E+(2,−2,+1), E+(2,−2,0) y E+(1,−2,0). Las tres están fuera del Moore de E y se prepararon como SEM4state1/carga0. También se fijó una ruta diagonal de contacto genérico para evitar el SEM4 que interceptaba el retorno anterior. Son dos factores de ingeniería P0, no reorganización aprendida.

Se ejecutaron cinco mundos R05 hasta el horizonte354: retorno intacto, retorno omitido, actuador anulado, contenidos opuestos y contenidos opuestos con retorno omitido. Todos produjeron **0/4 emisiones válidas**. La activación130 fue `rejected_occupied`; E ya estaba ocupado antes de la consulta. No se evaluó una política peor: faltó una entrada funcional y no llegó a ejercerse el canal diagonal de retorno. Ninguna de estas vidas reemplaza el P1 finito validado ni MAIN.

`MA02_R05_PREQUERY_CONTRAST` compara, con **cero nuevos ticks**, los snapshots completos R04 y R05 enT0 yT129. Inicialmente difieren exactamente los tres RAW de preparación y ningún clock. EnT129 difieren2,570sitiosRAW, ningún clock, y las solicitudes materiales y recibos siguen siendo iguales. Todavía no hubo acción ni retorno, por lo que el canal de contacto nuevo no explica esa divergencia previa: el cambio de soporte inicial alteró la propagación de las propias adquisiciones y bloqueó posteriormente la interfaz. Se conserva la lista íntegra de diferencias y el contexto de26vecinos/13pares de D en los primarios R05.

Este contraste demuestra sensibilidad a esa preparación y un fallo de interfaz/paisaje en su dominio. No establece que toda simetría, soporte adicional, composición o plasticidad sea perjudicial ni que v27 carezca de capacidad. El retorno alternativo preparado quedó sin prueba funcional, no refutado por una entrada que nunca se produjo.

### R06: suministro tardío desde estados completos existentes

Una última comprobación dirigida separó la interferencia durante adquisición del uso posterior. Se bifurcaron los snapshots completos R04 T129, con sus memorias y futuras entradas originales intactas; no se reconstruyó desde T0 ni se utilizó el corte opuestoT138 que ya contenía un retorno antiguo en agenda. Un cálculo previo de los13pares identificó una cuarta contraparte necesaria del segundo relé. La propuesta de sólo tres se descartó **antes de ejecutarla**, no cuenta como un ensayo fallido.

Se fijaron cuatro suministros externos de calendario, SEM4state1/carga0/dirección0, enT140: (35,31,34), (35,31,33), (34,31,33) y (33,31,33). Todos estaban RAW0 enT129 yT139; los cuatro se admitieron/aplicaron y permanecieron como soportes preparados desde141. Este aprovisionamiento P0 fue idéntico en los seis brazos y no dependió del contenido esperado. La consulta130, el lector138 y las ventanas205/272/339 permanecieron exactamente como en el padre. El retorno real por rechazo usó el contacto diagonal genérico de carga0; se incluyeron omisión, actuador anulado y retardo+67 sin rescatar la fase del lector.

La primera acción volvió a ser válida: + y servicio aceptado en historia normal; − y servicio rechazado en historia opuesta; el actuador anulado dejó la emisión nativa sin ejecutar servicio. Los seis brazos dieron **1/4 emisiones y tres abstenciones**, sin commits. El suministro tardío evitó el bloqueo de admisión anterior a la consulta observado enR05, pero no completó el aprendizaje de una acción más útil.

El retorno opuesto real fue admitido y llegó aP=(34,32,34) en145. No nació D ni cambió la selecciónX. La causa local quedó registrada: el propio recorrido dejó activo el sitio previo (33,31,34), mientras su opuesto (35,33,32) era SEM4state0. En145 hubo25vecinosactivos y12/13pares iguales, no13. Sin contacto, después del aprovisionamiento hubo23activos y12/13pares; tampoco nació una huella espuria. El criterio necesario calculado sobre el vecindario estático138 no anticipaba la actividad que el mismo contacto conservaría en144–145. Esto explica por qué entrada admitida y llegada al objetivo no bastan para una experiencia plástica útil.

Los seis controles y sus futuros T354 se conservan. No se ejecutó otra modificación para completar el par restante, no se editó el SEM4state0 existente ni se cambió la lectura para aceptar una salida distinta. R06 queda como procedimiento experimental delimitado, no nueva vida promovida ni capacidad de recuperación adquirida. El P1 finito original y MAIN_5 permanecen intactos.

## Recálculo y cobertura

`recalcular_mecanismo_ma02.py` usa sólo Python estándar. Reconstruye state, s_reg, semantic y dirección desde uint64 RAW; coteja campos publicados, candidatos del lector, comandos, abstenciones, recibos, ley del trabajador, pares opuestos de D, suministros tardíos y conservación de las vidas listas. No importa DEE ni avanza ticks. La referencia definitiva es `RECALCULO_MECANISMO_MA02_R06_FINAL.json`; incorpora todos los positivos y negativos, incluidos R05, su contraste previo y los seis brazosR06. Las referencias anteriores de46/52primarios se conservan como cortes históricos. La cifra de observaciones verificadas no es número de aprendizajes ni de individuos. Los archivos pequeños del trabajador se incluyen con sus hashes; este recálculo de mecanismo comprueba sus recibos/ley, no vuelve a abrir esos archivos. Su relectura puede verificarse aparte.

```text
python recalcular_mecanismo_ma02.py --evidencia EVIDENCIA_CAUSAL/mecanismo_repetible --salida RECALCULADO_MECANISMO_MA02.json
```

El análisis transportable puede omitir los snapshots completos y archivos operativos voluminosos; sus localizadores y SHA-256 deben acompañar el índice. Para continuar una vida se necesita el sistema local y su snapshot completo, no este informe ni la extracción RAW. Los fallos puramente instrumentales de arranque (metadatos tuple no JSON y modalidad CLI no admitida) ocurrieron sin ticks útiles; sus revisiones de código se conservaron y no se cuentan como fallos cognitivos.
