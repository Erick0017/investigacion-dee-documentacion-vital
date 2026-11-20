# Lenguaje adquirido: alcance y reproducción

Esta ampliación utiliza el WHL oficial DEE thinking 4.0.0 y kernel v27 sin modificarlos. Los módulos de esta carpeta son facilitadores experimentales de la aplicación, no una nueva versión de la biblioteca. La experiencia, la memoria móvil y las respuestas se realizan mediante entradas físicas y evolución Native en un único Runtime por trayectoria.

## Dos dominios observados sobre una continuidad

| Fase | Experiencia y consulta | Qué se midió |
|---|---|---|
| Red y currículo |0→431→931→1431|El individuo anterior continúa; no se borran estados para reinstalar los núcleos.|
| Disponibilidad funcional |Lecciones 1431/1459; lecturas 1501/1529|Dos perfiles actuales: F7 presente / R3 ausente frente a F7 ausente / R3 presente.|
| Dirección física |Partículas 1533/1561, observación y enseñanza 1536/1564, lecturas 1606/1634|Signo actual de dz en el marco de la retícula, con fuente y carga reservadas.|
| Panel de formas anteriores |Sondas 1565/1593, lectura 1568/1596|No apareció la firma 26 de participación en este panel; no se infiere por ello destrucción del estado causal completo.|

Los nombres BUENO/MALO corresponden sólo a los perfiles funcionales indicados. ARRIBA/DEBAJO corresponden sólo al signo de dz en el marco declarado: no gravedad, verticalidad universal ni semántica espacial general. El signo de la salida léxica se representa en dy; no se identifica ese eje de salida con el eje observado dz.

La clasificación de F/R y de dz la realiza un sensor externo fijo sobre campos físicos actuales. Su transmisión es explícita y el mismo reporte llega a las cuatro regiones léxicas. El host no selecciona una respuesta leyendo el ID del caso, la historia esperada o una tabla palabra→función. No hay optimizador ni política de maximización de recompensa: la clasificación de tarea presentada por el maestro externo se declara como experiencia.

## Qué hizo cada parte

- INTERFAZ: convierte una forma textual en un ID/puerto físico y transmite experiencias declaradas.
- SENSOR EXTERNO: observa paquetes actuales bajo una ventana física finita y codifica una clase. La ausencia de un paquete en esa ventana no es un detector nativo universal de ausencia.
- ENTE/NATIVE: conserva una relación direccional adquirida y transforma la sonda posterior mediante v27.
- INSTRUMENTO: registra RAW, clock, dirección, carga, admisión, firmas y comparaciones. Las evaluaciones de acierto no alimentan el Runtime.

Las palabras humanas son formas externas. La evidencia de adquisición es que invertir su emparejamiento invierte la respuesta física con las mismas formas y el mismo decoder; omitir o desfasar las señales no reproduce el readout cualificado.

## Resultados conservados

`continuous02/` conserva 10 trayectorias: principal, nombres invertidos, señales omitidas, reportes omitidos, desfase de un tick, segundo episodio omitido, dos paneles comunes y dos preparaciones fresh reservadas. Estas últimas evolucionaron 0→1529 en la misma instancia Native y expresaron ambas relaciones; una usó el orden de formas invertido.

`direction03/` conserva 7 trayectorias. La principal y la inversión expresaron las dos relaciones; también lo hicieron las variantes reservadas de fuente C, cargas 17/23 y orden. Estas variantes partieron de mundos ya observados en el dominio anterior: son reservas de parámetros de la nueva tarea, no nuevas réplicas independientes de preparación.

En ambos dominios, el control sin señal y el desfase aceptaron las consultas pero no expresaron 21. El control sin reporte rechazó las sondas por ocupación: no se presenta como prueba de olvido. Se conservan todos los recibos y los campos reales, incluso cuando no se cualifica una respuesta.

El panel común de situación→forma produjo BUENO en 1501 en una continuación y MALO en 1529 en otra, por selección física de región con carga 26 y recibos locales Applied. Las dos continuaciones no se fusionaron ni se presentan como una sola conversación bidireccional ilimitada. No existe un nuevo brazo de omisión emparejado dentro de ese panel inverso exacto; sus emisiones se distinguen de los controles de palabra→clase y del mecanismo heredado M1.

## Acceso renovado heredado, sin rescate asistido

`../continuidad/M1_TEMPORAL_ACCESS/` conserva 6 trayectorias y `../continuidad/M1_RENEWED_CYCLES/` otras 7. Parten de checkpoints reales de la genealogía heredada. Se utiliza el primer retorno de la relación adquirida mediante una señal de carga 5 y un reporte actual de carga 5 idénticos en ambas regiones, antes de la interferencia destructiva del protocolo antiguo. No hay clearRAW, edición de clocks, trasplante ni reinstalación de interfaces.

En contexto emparejado, una función produjo 26→36→46 durante tres ciclos. Omitir el reporte, omitir la historia de señales, desfasar la llegada o cambiar el contexto no conservó ese readout. El lector y el suministro son un protocolo externo fijo; no constituyen regulación aprendida por la organización. La geometría alternativa ya se había observado y no se renombra como holdout fresh.

## API finita para la demostración

El orquestador de la ampliación puede utilizar:

```python
from lenguaje.session_safe import GroundedSession

# network es el MISMO NetworkSessionV3 después de1431.
language = GroundedSession.attach(network)
language.teach_next()
language.teach_next()
language.query_next_word("L1")
language.save("despues_primera_consulta.deetsnap")

# En otro proceso; no vuelve a preparar el individuo.
language = GroundedSession.load("despues_primera_consulta.deetsnap")
language.query_next_word("L2")
```

`observe()` es pasivo y no avanza. `query_next_word()` es una sonda física que puede consumir o modificar el estado. `name_next_profile()` admite `"role"` o `"second"`: es otro panel físico, no una traducción obtenida desde una caché. Cada vista admite exactamente dos experiencias y dos consultas en las ventanas declaradas; una tercera consulta se rechaza explícitamente.

La extensión direccional usa `lenguaje.directions.run(network,case,output)` sobre el mismo NetworkSession en 1529. Una vez avanzó esa extensión, la vista léxica anterior se conserva como protocolo histórico terminado, no como un lector restaurable a su viejo tick. Cargar el Runtime posterior mediante NetworkSession no significa reproducir desde una tabla la antigua respuesta.

El loader público `session_safe.py` añade validación únicamente. Rechaza estados pausados, fases/campos inválidos y entradas futuras Scheduled en fronteras publicadas que no admiten una cola pendiente. Un teacher oculto futuro no puede pasar silenciosamente a la demostración de una consulta de palabra sola.

## Reproducir y verificar

Los runners nuevos se ejecutan desde la raíz de la ampliación con el intérprete oficial4 aislado, mediante `src/supervision.py` y el presupuesto original de esta ampliación. Conservan la configuración congelada y saltan los casos que ya tienen mediciones completas:

```text
src/continuidad/run_temporal.py
src/continuidad/renewed_access.py
src/lenguaje/discover.py
src/lenguaje/run_continuous.py
src/lenguaje/run_directions.py
```

Las copias `EXECUTED_SOURCE/` contienen el código exacto de cada corte. El origen de los checkpoints heredados y su SHA está en cada configuración. El programa normal no importa datos terminales para responder.

`TECHNICAL_CHECKS/` conserva 12 comprobaciones: carga en procesos distintos, experiencia posterior a restauración, pregunta nueva con evolución, equivalencia RAW/clocks/tick frente a continuación directa, observación pasiva y rechazo de operaciones fuera del dominio. `LOADER_HARDENING/` conserva 8 comprobaciones adicionales sin avanzar Native, incluido el caso adverso de un teacher futuro que el loader experimental anterior aceptaba. Estas 20 comprobaciones técnicas no se suman como nuevas muestras científicas.

`LANGUAGE_SUMMARY.json` y `NSM65_EVOLUCION.json` contienen matrices por caso y estados independientes. El catálogo heredado de 65 formas permanece intacto. Se registran cuatro formas nuevas con asociaciones de tarea acotadas y dos formas heredadas con un nuevo acceso físico; cero adquisiciones de semántica NSM universal y cero composiciones NSM medidas. No se afirma conservación simultánea de seis significados.

Los nombres documentales proceden del inventario humano de referencia, no de una ontología impuesta a DEE: [NSM Resources](https://nsm-approach.net/resources), [diagrama español 2021](https://nsm-approach.net/wp-content/uploads/2021/10/Primes_Diagram_Spanish_2021.png). La atribución/licencia del recurso se conserva en el catálogo original y no se extiende por ello al conjunto del código.
