# Contrato de API — DEE thinking Entrega 02

## Estado y propiedad

`dee::thinking::Runtime` posee cuatro buffers contiguos de `uint64_t`:
`raw_a`, `raw_b`, `clock_a` y `clock_b`. Los buffers `a` son el estado activo.
La indexación es `(x*N + y)*N + z`. Cada instancia posee sus propios buffers,
canales, cola y recibos; no existe un mundo global mutable.

La construcción ordinaria `Runtime(N)` crea un mundo RAW/clock cero. La función
`Runtime::import_research_state(...)` es una importación explícita de
investigación, valida tamaños y copia el estado a buffers propios. No es una
entrada ordinaria y no se invoca de forma oculta.

`raw_copy()` y `clock_copy()` devuelven copias. No exponen una vista mutable al
mundo.

## Núcleo v27

La API de bajo nivel `dee::v27::tick(...)` ejecuta una transición completa con
el contrato histórico de cuatro arrays:

1. lee `gA` y `clockA` como estado de la frontera actual;
2. escribe `gB` y `clockB`;
3. acumula y aplica DEMUX;
4. copia los destinos de vuelta a `gA` y `clockA`.

No se realiza un intercambio adicional de buffers. `TickInfo` informa contadores
técnicos de overflow, génesis y registros evaluados; no es un veredicto
científico.

`pack_record()` conserva el ancho y layout de la palabra v27. Las componentes
de dirección admitidas por la API pública de canales están en `[-8,7]`. El cap
del reducer (`19664`) no convierte en inválido todo `s_reg` representable por
16 bits.

### Backends de ejecución

`Runtime::set_execution_options()` selecciona explícitamente backend y número
solicitado de hilos para la siguiente frontera. La configuración se cambia sólo
entre ticks; no se permiten dos transiciones simultáneas de la misma instancia.
`last_tick_info()` informa backend solicitado/usado, hilos solicitados/usados,
fallback, celdas evaluadas, soporte RAW y tiempos técnicos. Un trabajo Lazy
vacío usa cero workers y sigue avanzando todos los clocks.

`DenseSequential` con un hilo continúa siendo el valor predeterminado.
`DenseParallel` divide slabs de x entre workers que leen el mismo A; espera sus
barreras, aplica DEMUX y sólo entonces copia B. `Lazy` evalúa cada RAW no nulo y
su halo Moore-26, pero mantiene el recorrido necesario de clocks y el postpaso
DEMUX. Esas agendas no forman parte del estado físico ni de un snapshot.

## Convención temporal

El estado etiquetado `t` es el estado después de `t` transiciones del kernel.

- Un evento destinado a `t` se intenta aplicar en la frontera `t`, justo antes
  de calcular `t -> t+1`.
- `observe()` en `t` no aplica eventos y no avanza.
- `advance(0)` no aplica eventos ni cambia buffers, clock, tick o recibos.
- `advance(n)` realiza exactamente `n` transiciones.
- `run_until(T)` termina en la frontera `T`; no aplica eventos pendientes para
  `T` hasta que una transición posterior empiece.
- `run_until(T)` rechaza `T < current_tick()`.
- Las llamadas por bloques respetan el mismo orden de frontera que `n`
  llamadas a `advance(1)`.

El tick DEE no representa por sí mismo tiempo de pared ni tiempo real de una
aplicación.

## Canales y entradas

Un `ChannelSpec` fija:

- nombre de metadatos;
- sitio de inyección;
- `state`, dirección y semántica del portador;
- permiso separado para `experience` y `probe`.

El nombre del canal y el identificador de evento no se escriben en RAW o clock.
El cliente sólo aporta `s_reg` mediante `InputRequest`; la geometría y campos
restantes pertenecen al contrato congelado del canal.

`experience(channel, t, s)` agenda una experiencia individual.
`experience_batch(inputs, t)` agenda un lote atómico. `probe(channel, t, s)`
agenda la misma clase de escritura física pero queda distinguida en el recibo
como `EventKind::Probe` y requiere permiso explícito del canal.

La programación valida canal, rango de campos, tiempo y límite de cola. La
admisión física se decide otra vez en la frontera efectiva:

- un destino con `raw != 0` se rechaza; no se borra para admitir la entrada;
- dos eventos simultáneos que apunten al mismo registro se rechazan por
  conflicto; no existe “última escritura gana”;
- un lote que repite un destino es rechazado antes de entrar en la cola;
- al aplicar una entrada se escribe RAW y se conserva la palabra clock que ya
  tenía el sitio;
- no existe aplazamiento automático.

La implementación inicial limita la cola a 4096 eventos pendientes. Los
estados del recibo son:

| Estado | Significado |
|---|---|
| `Scheduled` | La sintaxis y la cola fueron aceptadas; la admisión física sigue pendiente |
| `Applied` | Todas las escrituras del evento se aplicaron en su frontera |
| `RejectedLate` | La frontera solicitada precedía al tick actual |
| `RejectedInvalid` | Canal, permiso, lote o campo inválido |
| `RejectedOccupied` | Al menos un destino no estaba RAW-vacío al aplicar |
| `RejectedConflict` | Escrituras del lote o eventos simultáneos colisionaban |
| `RejectedQueueFull` | Se alcanzó el límite de eventos pendientes |

`effective_tick` sólo tiene valor para un evento aplicado. Un recibo no afirma
que el kernel produjo una respuesta funcional.

## Evolución, pausa y observación

`advance(count)` aplica eventos de cada frontera y llama al kernel. Si el
runtime está pausado, `advance(count>0)` lanza `std::logic_error`.
`advance(0)` continúa siendo un no-op. `resume()` sólo habilita futuras llamadas;
no recupera tiempo de pared y no altera el estado.

`observe(q)`, `observe_many(qs)` y `metrics()` son `const`. No aplican cola, no
ejecutan sondas y no avanzan. `WorldMetrics` separa:

- soporte RAW (`raw != 0`);
- ocupación (`state != 0`);
- suma descriptiva de `s_reg`.

Estas magnitudes no son intercambiables ni constituyen por sí solas actividad,
memoria, energía o aprendizaje.

## Fork

`fork()` devuelve una copia profunda del runtime: estado activo y scratch,
canales, pendientes, recibos, fase y contadores. Las ramas no comparten memoria
mutable. No existe fusión automática con el mundo origen.

## Snapshot y restore

El snapshot se guarda únicamente desde una frontera estable, fuera de una
transición. El lector acepta el formato v1 de Entrega 01 y el escritor produce
v2. El v2 añade, tras los campos físicos y de protocolo:

- configuración solicitada de backend e hilos;
- metadatos clave/valor inertes para ids/versiones de organizaciones,
  contratos, composición y parámetros.

Los metadatos nunca ejecutan código ni alteran `F_DEE`. Un v1 se carga con
denso secuencial y `imported_legacy_snapshot()==true`; no se inventan
organizaciones que ese formato no almacenaba.

`ComposedWorld::load_snapshot(path[, catalog])` es una operación distinta de
`Runtime::load_snapshot`: sólo acepta v2 autocontenido creado desde una
composición. Decodifica una receta canónica con límites explícitos, comprueba la
versión exacta de cada constructor, vuelve a construir el plan por
`OrganizationCatalog`, regenera organizaciones, conexiones y landmarks, y
compara receta, manifiesto, dimensión y nombres de canal antes de mover el
Runtime cargado al resultado. No hay ejecución de texto ni restauración parcial.

Formato base de Entrega 01:

- magic ASCII `DEETSNP1`;
- versión `1`;
- enteros little-endian;
- dimensión, tick, pausa, ids y fase de protocolo;
- RAW y clock activos completos como `uint64_t`;
- canales;
- eventos pendientes con orden de secuencia;
- recibos;
- checksum FNV-1a de 64 bits sobre el payload precedente.

Los buffers scratch se reconstruyen desde los buffers activos porque el kernel
los sobrescribe íntegramente antes de volver a leerlos. No se serializan
punteros, callbacks ni código ejecutable.

`load_snapshot(path)` valida magic, versión, checksum, tamaños, límites y
consumo completo del payload. Rechaza truncamiento, dimensiones incoherentes,
versiones incompatibles y contenido fuera de límites. El tamaño máximo aceptado
es 2 GiB y la dimensión está limitada por el runtime a `[1,512]`.

`restore_snapshot(path)` carga primero en una instancia temporal y sólo reemplaza
el mundo si toda la validación termina. Por tanto, un fallo no deja una
restauración parcial.

`save_snapshot(path)` serializa primero, escribe un archivo temporal exclusivo
en el mismo directorio, cierra/flush de la biblioteca y publica mediante la
operación de sustitución atómica disponible en la plataforma. Si la publicación
falla, elimina sólo el temporal y conserva el destino previo. La garantía no se
extiende a pérdida de energía, firmware o hardware.

El snapshot no activa dispositivos externos. La integridad FNV detecta daños
accidentales; no es autenticación criptográfica frente a un atacante.

## Organizaciones y composición

`ReferenceWorld` combina un `Runtime`, landmarks de lectura y un contrato
textual. Los constructores públicos son:

- `make_transport_world(occupied_destination)`;
- `make_relational_learning_world()`;
- `make_reprogramming_world()` como alias compatible y deprecado del anterior;
- `make_history_world(HistoryMode)`;
- `make_recurrence_multichannel_world(HistoryMode)`.

Los constructores preparan geometría y recursos iniciales. Después, el cliente
usa canales, avance y observación públicos; no necesita editar coordenadas una
por una. Sus respuestas se calculan mediante el kernel y no se cargan desde
snapshots futuros.

La actualización C7H03 no se renombra como C6H01: se construye en el catálogo
con `mobile_lineage.c7h03.v1` y `native_update_bridge.p01.v1`.

`OrganizationCatalog` expone descriptores, parámetros con rangos, puertos,
recursos, interferencias, retención/saturación y dominio. `instantiate()` valida
una solicitud y devuelve una instancia todavía no ejecutada.

La memoria temporal por fase CORE05 se expone exclusivamente como el
constructor catalogal `temporal_phase_memory.core05.v1`, versión `1.0.0`. Sus
parámetros fijan dimensión, distancia, ancla, transformación ortogonal de las
cuatro rutas, clocks fuente y uno de cuatro brazos iniciales declarados
(intacto, bloqueo transitorio, ablación o rewire). Los puertos de hub, fuentes y
bocas son pasivos: no existe una escritura del host posterior a `t=0` dentro de
este contrato. El id histórico `.pending` no es un alias ni puede aparecer en
una receta autocontenida válida.

El descriptor mantiene cinco facetas públicas separadas:

- `initial_footprint`: qué se instala en la frontera inicial;
- `functional_relation`: relación física que el aparato pretende realizar;
- `read_region`: dónde/cuándo se inspecciona el resultado declarado;
- `required_context`: scaffold, recursos e interferencias relevantes;
- `context_horizon`: dominio finito y retención/saturación documentados.

`OrganizationInstance::initial_footprint()` devuelve registros inmutables con
sitio relativo, RAW, clock y propósito; `channel_contracts()` expone la interfaz
de entrada instalada; `resource_budget()` resume vóxeles iniciales, fuentes
persistentes, canales, puertos y capacidad de conexiones. Son vistas de
construcción, no mutadores del mundo. Cada `PortSpec::maximum_connections`
declara capacidad física; excederla produce diagnóstico. Un valor mayor que uno
no crea copias ni autoriza fan-out implícito.

`CompositionPlanner` recibe instancias y conexiones. `analyze()` separa
compatibilidad estática, condiciones que requieren simulación e
incompatibilidades. `build()` instala las plantillas y canales antes del primer
tick en un solo `Runtime`; nunca observa una respuesta para construir una ruta,
ni copia salidas entre mundos. El alta de estructuras en un mundo ya evolucionado
no forma parte de este contrato.

Los controles también forman parte del contrato de prueba, no de un selector
de respuestas: A/C7 separa no-update (teacher conservado, reactivos del puente
omitidos) de no-learning (teacher omitido, recursos comunes conservados); B
separa corte de un sham con igual admisión pero ruta que no alcanza el redirect.
La consulta C6H01 a `t=6` vive en otra composición y no se presenta como control
ni como implementación de A.

## Errores y excepciones

Errores de contrato programático usan excepciones estándar (`invalid_argument`,
`out_of_range`, `logic_error`, `runtime_error`, `length_error` o
`overflow_error`). Rechazos normales de entrada se devuelven como recibos y no
como excepciones. No se garantiza seguridad de hilo para mutaciones concurrentes
de una misma instancia.
