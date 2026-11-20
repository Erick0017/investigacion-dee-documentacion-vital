# APD01: reutilización del propietario persistente

Preparación instrumental, cero ticks. No es un resultado cognitivo ni otra
plataforma. El servicio actual, su Store y sus contratos siguen siendo la base.

## Contrato que ya existe

`app/servicio_persistente.py` posee un OrganizationalWorld y un escritor por
vida. `session(a, situations, directory, actuator, feedback, detailed)` recibe
filas literales; `get(a)` confirma la preparación y expone incertidumbre. El
cliente escribe SQLite, no abre otro Runtime. Las peticiones no desaparecen de
la evaluación por rechazo, silencio o error. `resultado --id` espera el mismo
efecto, no vuelve a ejecutarlo. La exportación incluye snapshot completo,
SQLite, outbox y artefactos, y la importación declara nueva identidad.

El padre APD es el par postSTOP de MU_MAIN_FASE_R3 T104472, snapshot f389f643…,
epoch4 abierto y propietario detenido. No se continúa desde arrays ni se
recupera T0. La copia principal debe importarse emparejada; para mutaciones
ordinarias debe cerrar explícitamente su epoch sin descartar pendientes.

## Enlace mínimo al nuevo actor

Preferencia: mantener el backend explícito `mente_unificada` y extender su
capacidad con un modo APD, preservando los modos MUFI. No elegir el backend por
aciertos. Si se adopta otro backend, hace falta una transición explícita: hoy
el propietario rechaza un backend distinto del registrado incluso después de
un cierre, y ese rechazo no debe eludirse editando la historia.

La validación de transporte sólo comprobará tipos, límites y admisión de la
interfaz. No interpretará español para elegir una operación o herramienta.
Las filas de uso podrán transportar formas/secuencias y operandos literales;
los nombres exactos esperan la API física seleccionada. La docencia explícita
será un modo separado. No pasar target, respuesta, ruta favorable ni metadatos
del evaluador durante uso. Los IDs sólo sirven a deduplicación y recibos.

El acuerdo operativo APD01 concreta `modo=apd`, texto literal1..128bytesUTF8 y
dos operandos enteros0..32. `apd-docencia` admite texto,señal±1 y revisionbool
opcional en una solicitud separada. `apd-ambiente` admite una configuración
exacta: precios[2] enteros0..28,demora[2]0..4096 en ticksDEE,
disponibilidad[2] y presupuesto modelado fijo2 en el perfil R03.
La admisión pasiva de formas y ambiente se comprueba antes de la mutación;
un rechazo de dominio no se confunde con un efecto externo incierto.
`apd-conteo` transporta dos o tres muestras0/1 enteras, no una suma anfitriona.
`apd-componer` transporta dos o tres formas y sus datos públicos: el operador
indica el orden, sin acreditar planificación adquirida. `apd-ruta-docencia`
recibe un lado materialA/B en una petición docente aislada, nunca en evaluación.
El backend sigue siendo mente_unificada. Las pruebas de transporte no acreditan
por sí solas que una forma tenga significado ni que se haya aprendido a delegar.

## Herramienta, ambiente y seguridad

La guardia actual autoriza un único argv exacto para el trabajador EO02. Un
trabajador calculador nuevo necesita otra autorización exacta y acotada, no un
shell o un módulo elegidos por la petición. Otra opción es una función de
herramienta en el mismo proceso anfitrión, declarada externa al kernel y llamada
sólo después de una emisión nativa válida. En ambos casos se registrarán ruta
antes de ejecutar, operandos recibidos, bytes/respuesta, costo, consecuencia y
retorno. No ejecutar ambas vías y seleccionar el mejor resultado.

El candidato R03 sustituyó la antigua selección externa del retornoA/B por
un costo literal a un puerto comúnS de una referencia de ruta periférica en el
mismo Runtime. Calendario y compuerta de exceso sobre2 siguen siendo aparatoP0;
la experiencia sólo se atribuye cuando sus contrastes físicos la demuestran.

Precios, demora y disponibilidad son propiedades del ambiente, no una regla
Python para escoger vía. Su estado actual, cambios programados, generador si
existe, artefactos y efectos inciertos deben viajar en el par. El estado de
ambiente puede cambiar por intervención pública del operador, pero sólo su
observación/transducción fijada llega al participante.

El testigo `operational_dependencies()` actual cubre external_pending,
cascade_pending y external_uncertain de MUFI. Para acreditar el ambiente APD
debe incorporar su serialización completa pertinente mediante una API pasiva
declarada, o utilizar esos campos comunes con un contrato inequívoco. No
comparar sólo RAW/clocks y declarar preservados precios o solicitudes externas.

No llamar recuperación cognitiva a reconciliar SQLite y un recibo ya
comprometido. Incertidumbre detiene la repetición. No borrar marcadores, colas,
clocks o material para rescatar una reserva.

## Reserva continua preparada antes de datos

Propuesta: 480 oportunidades nominales, tres regímenes y horizonte fijo3900s,
IDs nuevos `apd60_`, ocio1tick/.1s, tres pausas técnicas y una recarga de la misma
vida. Se descontarán íntegramente pausas y recarga para medir si quedaron al
menos3600s en modo no pausado. No sumar sesiones reiniciadas ni extender el
ensayo según aciertos. Conservar los numeradores de solicitado, encolado,
rechazado, terminado, respuesta válida, correcto y tarea útil por separado.

Intercalar peticiones aprendidas, operaciones con operandos nuevos, usos
anteriores antes de feedback, una docencia/revisión declarada y cambios fijos de
costo/disponibilidad con reversión. El orden se congela sin conocer respuestas.
El calendario es preparación; sólo una elección material dependiente de la
experiencia acredita adaptación. No elevar nivel semántico por tener más IDs.

Si APD es síncrono, una pausa no puede fabricar una delegación pendiente. Se
comprobarán su ambiente y memoria completos y podrá conservarse una cadena MUFI
real pendiente para el transporte. Si existe API APD de solicitud y finalización
durables, se probará esa cola real sin reenvío. Dos etapas iniciadas por operador
no acreditan un planificador aprendido.

## Cierre y distribución

El límite vigente se conserva desde17:48:11UTC hasta01:48:11UTC del26octubre;
no se reinicia al construir un harness. Máximo dos Runtime y536870912bytes por
trabajador. El candidato de servicio añade600s de margen técnico de cierre a
su plazo único de proceso, sin ampliar el horizonte físico ni el presupuesto.

No actualizar `cognitive sistem` durante exploración. Al cerrar: elegir una sola
candidata alcanzada, guardar el par postSTOP completo y su genealogía, mantener
R3 y demás originales, actualizar el mismo manual lógico y registrar el corte
cerrado mediante el actualizador existente. No tocar trabajo_personal ni
promocionar globalmente por tick máximo.

La prueba del ZIP exacto usará otra extracción y su motor, entradas nuevas y una
continuación en otro proceso. Los límites de exportación del harness serán
120s y seguridad420s como en la reparación MUFI, sin confundir espera de cliente
con fallo del ente. El análisis compacto incluirá primarios y código, no sólo
veredictos, y distinguirá recálculo estándar, reproducción v27 y experiencias.

## Fuentes efectivamente consultadas para este frente

Prompt APD01 completo; PRESUPUESTO APD01; servicio_persistente.py,
cola_local.py, cliente_mente_unificada.py, access_guard.py,
finalizar_protocolo.py, comienzo de mente_unificada_01.py y guía persistente
vigente; preparación/cierre del ensayo R04/R17 y su recálculo de tiempo.
Estos archivos se consultaron por las interfaces necesarias. Este documento no
afirma una nueva lectura del corpus histórico ni nuevas pruebas físicas.
