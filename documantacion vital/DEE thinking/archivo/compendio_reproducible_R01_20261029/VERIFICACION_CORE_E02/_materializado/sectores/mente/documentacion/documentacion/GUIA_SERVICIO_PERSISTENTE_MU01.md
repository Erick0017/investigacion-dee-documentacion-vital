# Servicio local persistente MU01

Instrumentación operativa sobre el gestor y Store existentes. Un proceso posee una sola instancia del mundo; los clientes escriben una cola SQLite acotada, sin puertos de red. No es otra mente ni un selector aprendido. La dirección de contexto y las fases siguen siendo preparación P0 del contrato nativo.

## Inicio explícito

Primero cree una copia completa de la vida seleccionada. Si ya tiene protocolo de servicio, importe su exportación emparejada; `bifurcar` por sí solo no copia la cola SQLite ni los artefactos. En el paquete de colaboración, `INICIAR.bat abrir MENTE_UNIFICADA MI_COPIA` materializa la copia emparejada del corte seleccionado. Nunca se sustituye una carga fallida por T0. En una terminal, usando el CPython 3.13 x64 ya compatible:

```powershell
python sistema/gestionar.py mente-unificada-importar --paquete CARPETA_EXPORTADA --vida MI_COPIA
python sistema/gestionar.py mente-unificada-iniciar --vida MI_COPIA --backend mente_unificada --intervalo 0.1 --ticks-ocio 1 --guardar-cada 15
```

En otra terminal:

```powershell
python sistema/gestionar.py mente-unificada-estado --vida MI_COPIA
python sistema/gestionar.py mente-unificada-pedir --vida MI_COPIA --id consulta_01 --situaciones '[{"modo":"memoria","contexto":"gamma"}]'
python sistema/gestionar.py mente-unificada-pausar --vida MI_COPIA --id pausa_01
python sistema/gestionar.py mente-unificada-guardar --vida MI_COPIA --id guardar_01
python sistema/gestionar.py mente-unificada-exportar --vida MI_COPIA --id exportacion_01
python sistema/gestionar.py mente-unificada-reanudar --vida MI_COPIA --id reanudar_01
python sistema/gestionar.py mente-unificada-detener --vida MI_COPIA --id detener_01
```

Las comillas de JSON deben conservarse al invocar Windows PowerShell 5; PowerShell 7 es preferible. Una respuesta de transporte contiene `status` y el resultado físico, no una frase que reemplaza al resultado nativo. Puede recuperarse después con `mente-unificada-resultado --vida MI_COPIA --id consulta_01` sin repetir la experiencia. Reutilizar un ID con bytes distintos se rechaza. Un ID no revela un target ni decide una acción.

## Tiempo y límites

Sin peticiones y sin pausa, el propietario avanza ticks reales mediante OrganizationalWorld. En pausa no avanza física; sí admite controles técnicos. Los controles preceden al FIFO material sólo en fronteras seguras para permitir pausar, guardar y detener; esa prioridad no es cognición. `estado` es una lectura cacheada con antigüedad, no el tick exacto del instante. No hay catch-up acelerado por tiempo perdido ni autoarranque al consultar.

Ocho peticiones materiales y ocho controles pueden estar pendientes. Hay validación de tamaños, modos, interfaces y nombres; no se aceptan instrucciones de shell, rutas de archivos de trabajo ni targets del evaluador. El trabajador externo sigue siendo el ejecutable exacto del protocolo existente. El audit hook reduce accesos accidentales; no se declara sandbox del sistema operativo.

## Continuidad completa e incertidumbre

El mundo oficial, sus agendas y metadatos se guardan completos. La cola, resultados exactos y artefactos del trabajador son estado operativo externo, no telemetría prescindible. No cambie el mismo individuo mediante comandos de una sola operación mientras su servicio lo posee; el lock lo impide. Una continuación posterior fuera del servicio puede desincronizar su protocolo y se rechaza, no se rebobina.

Una exportación emparejada genera `EXPORTACION_SERVICIO.json`, `VIDA.deetsnap.gz`, `cola.sqlite3`, resultados y artefactos. El manifiesto cubre todos los miembros. Para restaurar en identidad nueva:

```powershell
python sistema/gestionar.py mente-unificada-importar --paquete CARPETA_EXPORTADA --vida MI_IMPORTACION
python sistema/gestionar.py mente-unificada-iniciar --vida MI_IMPORTACION
```

Importar preserva el pasado físico y los IDs de transporte, pero declara otro mundo y otra identidad de continuación importada. No transfiere adquisiciones a la vida original. Importar no arranca el servicio ni repite automáticamente una acción. Una exportación con datos faltantes o alterados se rechaza antes de cargar el mundo.

Si se interrumpe un trabajo y no existe recibo nativo comprometido con resultado exacto, queda `uncertain`, en pausa, sin reintento ciego. Si existe ese recibo y su resultado con SHA correcto, se reconcilia el transporte sin ejecutar de nuevo. Una muerte entre ticks no comprometidos deja `FUTURO_INTERRUMPIDO.json`; la carga ordinaria queda bloqueada. La recuperación de ese fallo requiere una decisión explícita, no borrar el marcador para fingir continuidad.

## Evidencia y alcance actual

El piloto R01 fue breve, en una copia de MA02_MAIN_5, con dos accesos heredados y continuación entre procesos. Conserva el error de comparación de caché del harness; el recálculo archivado demuestra avance ocioso. R03 comprobó nativamente exportación/importación con cola pendiente y dos consultas heredadas. R09 añadió una interrupción real controlada del trabajador después de escribir y releer32bytes, en dos copias diagnósticas: CUT quedó incierto y pausado; SHAM recibió confirmación. Una segunda carga no repitió la acción ni cambió el archivo. No es recuperación cognitiva ni reparación automática del efecto incierto.

La ventana inicial de MU_MAIN T16433→16623 intercaló dos trabajos nativos útiles y tres consultas de memoria; después T16634 conservó una selección nativa nueva. No reenseñó esos contenidos. Los controles de cierre y compactación no añadieron ticks; su error de espera original permanece archivado y se delimitó al coste de serializar una ficha histórica de67MB. Hay23 tests de transporte stdlib, sin importar DEE.

El ensayo final R11 mantuvo la misma MU_MAIN deT34193 aT68473 durante un horizonte fijo de3605.0319406s: tres pausas técnicas y recarga en otro proceso enT51560 preservaron RAW/clocks, cola y un artefacto pendiente. Un suplemento separado sin consultas ni enseñanza avanzó hastaT68924 durante60.1862741s. Descontando27.417765s de pausa/recarga, se registraron3637.8004497s en modo operativo no pausado. No fue un único proceso ininterrumpido ni una prueba de estabilidad ilimitada.

Hubo499 intentos al cliente de admisión, incluidos498 payloads materiales y1 control inválido `guardar/shell`:487 encolados,9 rechazos por capacidad y3 por esquema;485 terminaron y2 fueron rechazados antes de introducir material. Las4100 entradas físicas solicitadas llegaron a aplicarse. En la misma historia coexistieron120 usos de asociaciones de signo (40/40 en cada régimen), revisión explícita beta−→+ con3/3 entradas,71 datos escalares y18 commits de19 oportunidades de cadena. La iniciativa de consultar, revisar y solicitar las dos etapas pertenece al operador; no es una política aprendida.

Los fallos R11 no se ocultan:216 trabajos individuales seleccionaron−,89 fueron útiles y127 no; el servicio no aprendió una política competente. RAW128 dio respuestas únicas10/12; las últimas entradas de los índices2 y127 quedaron sin candidato en los seis gates fijados, no con varios candidatos. Los seis últimos accesos de memoria acabaron enT67540; el corte completo continuó ocioso hastaT68924, por lo que no se afirma acceso actual después de ese intervalo sin una comprobación nueva en una copia. Los recálculos y primarios completos están en `evidencia/campanas/MENTE_UNIFICADA_Y_FI01/servicio/`. No se certifican regulación R2 general, NSM65 ni lenguaje general.

### Opción preferente explícita R3, conservando R11

`MENTE_UNIFICADA` en colaboración selecciona la vida `MU_MAIN_FASE_R3`, no cambia el ACTIVO global ni el E1 protegido. Se importó el corte completo R11T68924 con diario y artefactos; una enseñanza B0 **declarada** cambió D−21→−20 antes de la reserva y se admitió protección temporalR3P0. No es recuperación espontánea ni conservación intacta de la referencia anterior. La protección desplaza el protocolo sensorial completo0..10ticks según un calendario entero fijo, sin consultar valores, contenidos ni respuesta correcta. No selecciona un lector favorable. Consulte `GUIA_FASE_SENSOR_R3P0.md` para su dominio.

La reserva nueva R04/R17 mantuvo la misma vida T70223→T104472 durante3720s; descontando las tres pausas y la recarga intermedia quedaron3684.000645800042s de modo no pausado. EnT87197 se guardaron RAW/clocks y una cadena con artefacto real, se detuvo el propietario y otro proceso continuó la misma identidad y la misma petición pendiente una sola vez. No se repitió la interrupción destructiva del trabajadorR09 ni hubo restauración favorable duranteR17.

Se intentaron las480 oportunidades nominales:499payloads al cliente de admisión incluían498materiales y1control inválido;486fueron encolados,10rechazados por capacidad y3por esquema. De los encolados,484terminaron y2fallaron preflight antes de entrar al mundo. Las4097entradas nativas se aplicaron4097/4097. Son denominadores distintos: un rechazo de FIFO no es una incapacidad cognitiva ni una entrada física rechazada.

Las120lecturas de asociaciones coincidieron con la historia declarada(40/40por régimen):102consultas directas y18lecturas de inicio de cadena. Beta se revisó de+ a− explícitamente enT88074→88108, con3/3entradas docentes; no se cuenta como adaptación autónoma. Los12casos crudos128, incluidos los índices reservados3/64/126, produjeron la relación fijada12/12. Se verificaron101calendarios sensoriales desde los recibos. La capacidad sigue siendo una agregación/uso sensorial acotado de128componentes, no128conceptos.

Hubo18preparaciones y18commits reales de19oportunidades nominales de cadena; el intento sin preparación real se conserva como rechazo. Los215trabajos individuales eligieron−:89útiles y126no útiles. En total se ejecutaron251trabajadores(125aceptados/126no útiles). La protección del sensor no enseñó por sí sola una política competente ni un planificador.

El último panel observado terminó enT102782 con alfa−,beta−,gamma+,delta−,epsilon−,zeta+. Después hubo evolución ociosa hastaT104472. No se afirma acceso ilimitado ni se interroga el original para mejorar la entrega. El corte final está detenido, epoch4 **abierto**, sin entradas nativas, colas, cadena externa ni incertidumbre pendientes; su continuación sigue requiriendo el **par completo**, no una bifurcación ordinaria. El snapshot actual postSTOP es `estado/checkpoints/MU_MAIN_FASE_R3.T104472.cb632d5d0e08.deetsnap.gz`, SHA-256 `f389f64325390daa31b8f684ac14e0a0c4c75a65e4713af4c861effd9e38a97a`.

El paquete local postSTOP se identifica en `servicio/SERVICIO_60MIN_FASE_R17/CORTE_PARA_MANUAL.json`:1624miembros, manifiesto SHA-256 `4f9949bf12207136f8d9a569ec334688fbdbfb42cbfc6ce49d23ee53aeba4f75`. El export explícito anterior aSTOP tenía los mismos RAW/clocks, pero **otros bytes de snapshot/metadatos**; no se intercambian ni se anuncian idénticos. La distribución guarda el checkpoint nativo una vez y sus dependencias emparejadas aparte.

R11 yR17 no son gemelos con agendas futuras idénticas: cambiaron preparación, edades, reservas y la FIFO rechazó9frente10peticiones por capacidad. La evidencia causal más delimitada de protección temporal procede de los controlesR15/R16; no se infiere superioridad general sólo de10/12frente12/12. El R11adverso sigue disponible como `MENTE_UNIFICADA_R11`, sin copiarle los aprendizajes deR3.

La primera tabla retrospectivaR17 incluyó por error la enseñanzaR11heredada y produjo114/120. Código y salida incorrectos quedaron archivados como `R01_ERROR`; se corrigió exclusivamente el filtro `fi60r3_`, obteniendo120/120. No hubo nuevos ticks, cambio de criterio ni reparación del estado para corregir esa tabla. Los cuatro recálculos portables finales coinciden byte por byte con sus referencias desde otra carpeta; esto es recálculo archivado, no repetición nativa ni otra computadora.

## Backend explícito y epochs

`--backend ma02` conserva el acceso de contexto preparado. `--backend mente_unificada` requiere que esa anatomía ya esté admitida físicamente en la vida; usa los actuadores nativos. No cambia de backend buscando el que acierte. Ejemplo de solicitud nativa sin indicar un banco:

```powershell
python sistema/gestionar.py mente-unificada-iniciar --vida MI_COPIA --backend mente_unificada
python sistema/gestionar.py mente-unificada-pedir --vida MI_COPIA --id trabajo_01 --situaciones '[{"modo":"trabajo","valores":[3,11]}]'
```

Una memoria direccionada por el operador se declara como `{"modo":"memoria","contexto":"zeta"}`; no es selección autónoma de ese banco. Para enseñanza explícita del selector se usa `{"modo":"experiencia","lado":"A"}` o B, sólo en una etapa declarada. El servicio no genera esa enseñanza buscando la respuesta correcta.

El backend unificado admite además `{"modo":"dato","valor":13}` (entero0..512), `{"modo":"crudos","componentes":[...]}` (exactamente128 enteros0..32 cuando ese frente ya está preparado), y dos solicitudes separadas `{"modo":"cadena-iniciar","contexto":"gamma","valores":[23,4]}` / `{"modo":"cadena-finalizar"}`. La primera utiliza la asociación física del contexto indicado; la segunda mide bytes reales de su artefacto pendiente mediante el sensor fijo. El servicio no calcula la suma de los128 componentes ni la acción correcta. Si no hay una cadena realmente preparada, FINISH se rechaza antes de introducir material; no se inventa un fixture o una salida. La dirección del contexto y la iniciativa de las dos etapas siguen asistidas.

Los recibos de guardado contienen un testigo pasivo con existencia y SHA de la serialización exacta de artefacto/progreso externo pendiente. Sirve para comprobar continuidad entre procesos; ese SHA no entra al participante ni selecciona respuestas.

Después de detener un propietario, se puede cerrar explícitamente su epoch si la cola está vacía y no hay resultados inciertos:

```powershell
python sistema/gestionar.py mente-unificada-finalizar-protocolo --vida MI_COPIA
```

La operación guarda otro par completo previo al cierre, bloquea nuevas admisiones y modifica sólo metadata documental, no RAW/clocks/tick. Permite luego continuar esa misma vida mediante las operaciones normales de Store. Un próximo `iniciar` abre otra epoch explícita sin perder los IDs anteriores ni reiniciar la física. Sin ese cierre, avanzar el mundo fuera del servicio produce un error de vinculación al reabrir; no se rebobina para ocultarlo.

`mente-unificada-compactar-historia --vida MI_COPIA` es una migración técnica opcional de fichas mayores de8MB, después de cerrar el servicio. Guarda el original exacto en gzip con hashes y deja `HISTORIA.jsonl` append-only; `operation_count_offset` conserva el cómputo total. El archivo es evidencia retrospectiva, no contenido leído para responder ni una cadena de deltas de la memoria. Los estados nativos completos no dependen de ese archivo para restaurarse. Las vidas originales protegidas no se compactan con este comando.

Los resultados de petición incluyen contadores exactos del propietario en esa frontera. Para interpretar una petición use esos recibos comprometidos, no un heartbeat de antigüedad desconocida. Los horizontes `--max-segundos` se comprueban en fronteras seguras: una operación/guardado en curso puede terminarlos después, y ese coste del anfitrión se registra como tal.
