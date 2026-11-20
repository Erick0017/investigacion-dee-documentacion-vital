# CPC3 SEM01 — significado funcional adquirido

Proyecto DEE Universe / INVESTIGACION DEE. Autor del proyecto: Ivan Erick
Tlaltecatl Morales. Instrumento: DEE thinking **4.0.0**, kernel **v27 congelado**.
El nombre histórico 3_5_0 del expediente CPC3 no indica el motor de esta ampliación.

## Capacidad, mecanismo y evidencia

Dos señales físicas de igual carga adquirieron correspondencias distintas con
dos clases de consecuencia. La misma señal S1 produjo U después de la historia
A y V después de B; S2 mostró el contraste recíproco. El lector y los puertos no
cambiaron. El producto nativo que expresó U continuó por una ruta preparada,
interceptó una perturbación y conservó un suministro. Una protección innecesaria
consumió un recurso opcional real. Estas trayectorias completas ocurrieron en
un único Runtime N67 por individuo, desde T0 hasta129, sin reconstruirlo entre
enseñanza, consulta y uso.

La relación adquirida es direccional y específica del puerto sensorial. No es
una tabla de respuestas del anfitrión. Se emplea una realización móvil, finita,
con rutas y período toroidal67 preparados. El acoplamiento entre dirección y
acción útil está diseñado; la utilidad de esa acción no se aprendió por un
segundo mecanismo independiente. La generalidad descrita aquí corresponde a
este dominio físico y a las variaciones efectivamente ejecutadas.

## Preparación y adquisición

La memoria comienza con RAW y clocks cero, en N67. S1 y S2 usan regiones fijas
centradas en (30,30,12) y (30,30,44). Ambos estímulos tienen carga5, semantic1,
state1 y dirección(-1,0,0); las reservas usan carga7 tanto al enseñar como al
consultar. La asignación A/B se elige después de crear el cuerpo y sus canales.
Los dos individuos parten de RAW, clocks, geometría e interfaces iguales.

Un banco ambiental tiene suministro primario de carga7 y recurso opcional de
carga3. El acontecimiento U interrumpe el suministro; V lo deja llegar. El sensor
externo fijo lee la entrega **actual**, no la etiqueta solicitada ni el futuro:
entrega7 con dirección+y se traduce a V; su ausencia dentro de esa ventana, a U.
Esta clasificación de ausencia es instrumentación externa declarada. Su paquete
de resultado de carga11 se difunde a **ambas** regiones, independientemente de
la señal presente. Sólo el encuentro con la señal local escribe la relación:

- Señal5(-1,0,0) + resultado11(1,+1,0) → relación16(0,+1,0).
- Señal5(-1,0,0) + resultado11(1,-1,0) → relación16(0,-1,0).

Las señales acompañan el efecto ambiental actual en17/45, no el lanzamiento
anterior de la perturbación. Los encuentros de adquisición ocurren en20/48.
La señal posterior, por el **mismo** puerto y con la misma codificación, encuentra
la relación tras su retorno toroidal y produce21(-1,+1,0) o21(-1,-1,0).
El decoder acepta esas dos direcciones activas; otras lecturas son indeterminadas.

La señal sola entra en84/112; la emisión ocurre en87/115, antes de presentar
el acontecimiento futuro en88/116. No hay U/V futuro ni recursos de ese episodio
en la cola durante la anticipación. Los archivos PREDICCIONES se escriben antes
de introducirlo. El participante recibe sólo señal, snapshot y parámetros neutros;
el generador y el evaluador conservan por separado asignaciones y targets.

## Función y coste físicos

El producto U(-1,+1,0) encuentra el recurso3: resulta24(0,+1,0), con pérdida de
la entrega opcional. Ese producto intercepta la perturbación U11 y resulta35
sin dirección. Así puede llegar el suministro primario7. El producto V(-1,-1,0)
no toma esa ruta. La fuente primaria se presenta seis ticks después de la emisión
para evitar una intersección instrumental con V identificada durante discovery.
Esta fase es idéntica en todas las historias confirmatorias.

Se miden dos entregas, no sólo un score: F=función primaria y R=recurso opcional.
El auditor congeló utilidad2F+R, que no vuelve a la memoria.

| Episodio | Sin protección | Protección nativa |
|---|---|---|
| U | F0,R1 | F1,R0 |
| V | F1,R1 | F1,R0 si se protege innecesariamente |

En un par equilibrado U/V, las historias emparejadas obtuvieron utilidad5,
frente a4 sin acción y4 protegiendo siempre. Las historias aplicadas al futuro
opuesto obtuvieron3. El coste y el beneficio dependen de entregas físicas,
no de premiar desde Python la etiqueta preferida.

## Batería congelada y reservas

`configuraciones/EXPERIMENT_CONFIG.json` congeló geometría, código, lector,
ventanas, controles y dos variantes antes de ejecutarlas. Hay **14 registros**:
cuatro cruces historia/futuro, cuatro controles de enseñanza, cuatro controles
de acción y dos reservas. Dos consultas por registro no son dos réplicas de una
población. Los replays técnicos y las sesiones de interfaz tampoco se suman
como nuevos individuos confirmatorios.

| Tratamiento | Emisiones S1/S2 | Entregas F,R por episodio | Utilidad total |
|---|---|---|---|
| A, futuro U/V | U/V | 1,0; 1,1 | 5 |
| B, futuro V/U | V/U | 1,1; 1,0 | 5 |
| A, futuro V/U | U/V | 1,0; 0,1 | 3 |
| B, futuro U/V | V/U | 0,1; 1,0 | 3 |
| Desacoplado, misma dosis | indeterminado/indeterminado | 0,1; 1,1 | 4 |
| Consecuencias sin señal | indeterminado/indeterminado | 0,1; 1,1 | 4 |
| Sin enseñanza | indeterminado/indeterminado | 0,1; 1,1 | 4 |
| Acción suprimida tras emisión | conserva la emisión previa | pierde beneficio U | 4 |
| Acción fija tras emisión | conserva la emisión previa | protege y paga siempre | 4 |
| Reserva A: traslación(5,3,2), carga7 | U/V | 1,0; 1,1 | 5 |
| Reserva B: traslación(9,-4,7), carga7, orden S2/S1 | U/V en ese orden | 1,0; 1,1 | 5 |

Los cuatro puestos de anticipación de las dos historias emparejadas y los cuatro
de las reservas expresaron la clase correspondiente. No se interpreta 8/8 como
estimación de precisión poblacional. Los cruces con futuros opuestos conservan
las anticipaciones históricas aunque el generador posterior las contradiga.

El control «señales sin consecuencias» recibió las señales iniciales, pero sus
dos consultas fueron **rechazadas por ocupación**: un portador retornó al puerto
a+67. Se conserva en cobertura/admisión, no como evidencia de olvido ni como
consulta negativa igualada. Los otros controles citados sí permiten examinar
la exposición y la ausencia de una asociación expresada con entradas admitidas.

## Atribución causal selectiva

Desde un mismo snapshotT83 se retiró exactamente un RAW de la relación de S1,
con todos los clocks intactos. Su consulta quedó indeterminada y U dejó de
proteger el suministro; la respuesta V de S2 y su función permanecieron. Un
sham que retiró otro portador real conservó U/V y ambos efectos útiles. Un
desafío de acción directa tras la lesión conservó la capacidad del actuador;
se retrasó un tick para no borrar el puerto ocupado. Es rescate diagnóstico,
no aprendizaje ni restauración de la asociación.

Estos tres forks y dos preparaciones reservadas sólo de memoria se documentan
en `resultados/causal_memory02/SUMMARY.json`. El contraste identifica el efecto
de esa intervención localizada; no prueba que exista una única causa universal.
La acción y la memoria comparten el producto retirado en los controles de acción.

Tres ventanas cortas de replay reconstruyen encuentro/coste90→91, intercepción
94→95 y suministro100→101. Incluyen los26 vecinos, ausencias, RAW y clocks;
sus estados completos coinciden con fronteras ya guardadas. La reconstrucción
de participantes y los efectos contrafactuales se presentan por separado.

## Extensión1: nueva experiencia en la misma genealogía

Cinco continuaciones parten del MAIN usado en129 y llegan a330, sin reset,
ediciones RAW ni modificación de clocks. En la primera fase el generador pidió
V/U/V/U, pero el sensor actual recibió **V/V/V/V**: un V antiguo toroidal se
encontró con U nuevo y desvió la perturbación. El replay154→181 reproduce ese
encuentro y el suministro posterior. Las emisiones fueron V/V; se conserva el
resultado en lugar de escribir el teacher que «debía» haber llegado.

Una segunda fase exploratoria, congelada por separado, adelantó **todos** los
acontecimientos de enseñanza dos ticks, sin cambiar señales, recursos ni consultas.
Los eventos de evaluación continuaron siendo posteriores a la emisión. Los
sensores recibieron V/U/V/U y MAIN expresó **V/U**, con carga37 y consultas
aplicadas en285/313. Esto muestra reexpresión dependiente de nuevas experiencias
en la misma continuidad.

El seguimiento balístico de un portador previo dejó de ser válido entre129 y153.
S1 ya había transformado su relación al actuar. Por eso no se afirma sobrescritura
de un mismo microportador continuamente identificado: readquisición o reorganización
son compatibles con los datos. El control sin informe de resultado rechazó ambas
consultas, por lo que no adjudica selectivamente la ausencia de asociación.
El último U conservó F aun sin la nueva acción; la acción completa sólo añadió
coste R. La utilidad incremental después de la revisión **no quedó establecida**.

## Extensión2: cuatro señales y asignaciones no globalmente inversas

Un Runtime N67 por cohorte contiene cuatro regiones sensoriales, cuatro experiencias
y cuatro consultas sucesivas. A adquirió U/U/V/V y B U/V/U/V: S1 y S4 mantienen
su correspondencia mientras cambian S2/S3. La reserva traslada toda la preparación
por(3,5,7). Cada una de esas tres cohortes expresó4/4 clases y conservó cuatro
suministros, pagando dos costes. La cohorte desacoplada tuvo0/4 anticipaciones
válidas con las32 entradas de enseñanza aplicadas; conservó dos suministros.

Se ejecutaron192 solicitudes entre las cuatro cohortes, todas aplicadas. Se
amplió la cantidad de regiones, fuentes y episodios respecto del núcleo de dos
señales, conservando N67; no se atribuye la ampliación exclusivamente a una
ventaja organizacional con inventario igual. Tampoco son cuatro bits independientes
ni cuatro nuevas capacidades por cambiar el nombre del puerto. La última lectura
funcional ocurre en252. Una restauración150→154 reprodujo el estado completo
sin acceso al mapa ni al historial externo.

Se eligieron estas dos extensiones por probar revisión temporal y especificidad
de señal más allá de una inversión global. Uso flexible por devaluación, composición
nueva y selección informativa no se evaluaron en esta ampliación. No se sustituyen
por resultados históricos con nombres semejantes.

## Comunicación y separación de procedencias

Zuvi/pako son alias externos de S1/S2. El visitante elige experiencias después
de crear el individuo. La coincidencia física adquiere S1/S2→U/V. La sintaxis
española y los nombres U/V los aporta el renderer fijo; no los aprende un léxico
arbitrario general. La aplicación registra señal, recibo, RAW, dirección, tick,
traducción, acción y entrega física. Una consulta rechazada se muestra como tal.

La consulta restaura el mismo MAIN completo en otro proceso y recibe sólo el
snapshot y S1/S2. El cursor contiene alias y fase, no una tabla de correspondencias.
Las cargas con teachers futuros pendientes se rechazan antes de avanzar. El
audit de aperturas Python se declara como instrumento, no como sandbox del SO.
Una prueba adversa conservada muestra por qué esa validación de cola es necesaria.

El modo interactivo y los archivos de eventos ejecutan trayectorias reales.
Después del primer uso completo, `revisar V U` presenta las cuatro nuevas
experiencias de la fase ya medida y continúa el mismo MAIN129→284. El mapa del
generador se retira antes de las nuevas consultas285/313. Un snapshot284 cargado
en otro proceso, sin historial ni asignación, produce V288/U316. La aplicación
coincide en RAW/clocks con las fronteras284/288/316/330 de la extensión científica;
25 comprobaciones de esa integración están en `UI_REVISION_QUALIFICATION`.
La revisión está publicada sólo para esa preparación principal y ese protocolo
finito: no se simula una inversión general editando una tabla. En particular,
la equivalencia citada se comprobaron desde A enseñada U/V y usada U/V; la API
no inspecciona un mapa previo para impedir otras historias de geometría principal,
cuyos resultados de revisión no están garantizados. El repertorio y
las ventanas son finitos; una nueva creación es explícita, nunca una reparación
silenciosa al consultar. La emisión inversa U→palabra no se estudió.

## Relecturas y fronteras instrumentales conservadas

- «Más carga implica memoria» → relaciones de igual carga21 difieren por dirección
  y efecto; la carga sola no identifica la correspondencia adquirida.
- «No responder implica olvidar» → el retorno al puerto puede rechazar una entrada;
  se separa relación, disponibilidad del lector y admisión.
- «El evento solicitado es la experiencia recibida» → la reversión expuso una
  modificación de la experiencia por historia ambiental; se usa el sensor actual.
- «Basta esperar para quitar transitorios» → productos antiguos pueden retornar
  por el toro e interferir. Se conservan ventanas y contrafactuales pertinentes.
- Dos calibraciones fallidas del banco y sus replays explican una tercera
  contribución residual y una colisión V/suministro. Las fases nuevas son discovery
  anterior al freeze; no un reajuste de las reservas confirmatorias.

Las incidencias de código, recibos, longitud de ruta y validación de carga se
conservan junto a sus fuentes y logs. No se corrigió v27, no se modificó el WHL4
ni se borraron resultados adversos para formar este corte.

## Integridad, reproducción y alcance

Se comprobó el WHL oficial, su PYD y el payload instalado en site-packages.
Observación pasiva repetida no altera RAW/clocks. Lazy, Dense y Parallel coinciden
en una continuación con entrada pendiente; save/load reproduce el futuro. Los
snapshots contienen estado operativo, canales, cola, recibos y metadatos neutros.
Las verificaciones de extracción limpia y publicación se registran por separado
en los resultados de cierre; la integridad de ZIP no sustituye estos ensayos.

La extracción candidata se instaló sin red ni dependencias del laboratorio en
un venv nuevo de CPython3.13. Desde una carpeta distinta se ejecutó otra trayectoria
completa A0→129: RAW/clocks/tick inicial y final, enseñanza, recibos y los dos usos
coincidieron con la referencia. La comparación se abrió **después** de evolucionar.
El demostrador también creó y enseñó de nuevo; otro proceso cargó su emisión87,
recibió una consulta posterior y terminó129 con idéntica respuesta. La revisión
del mismo estado usado llegó a330 y coincidió con la física de su referencia.
Los8+6+5 checks respectivos, comandos, instalación, procedencia site-packages y
payload exacto ejecutado están en `resultados/reproduccion_limpia/`. Son pruebas
técnicas de reproducción, no nuevas muestras independientes del efecto aprendido.

El expediente conserva los1563 miembros heredados, sus manifiestos históricos y
sus datos byte-exactos. Sólo se añade esta sección, con manifiesto propio. La
lectura científica se apoya en estados, controles y código; no en una etiqueta
automática de mente, vida, inteligencia o resultado global.
