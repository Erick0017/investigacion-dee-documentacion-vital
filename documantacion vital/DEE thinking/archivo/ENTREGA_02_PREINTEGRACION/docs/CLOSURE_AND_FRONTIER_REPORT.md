# Cierre y ampliación de Entrega 02

Este informe registra la continuación ejecutada sobre una copia aislada de la
Entrega 02 verificada. La ley local DEE v27 no fue modificada. Los estados son
técnicos o experimentales acotados; no constituyen un dictamen científico
global ni autorizan automáticamente Entrega 03.

## Procedencia y frontera de cambios

- ZIP Entrega 01 preservado: SHA-256
  `e263f27243e73cb8f348319ecfe858310cb1ff8e4b137bbe014b99429dc16661`.
- ZIP Entrega 02 preservado: SHA-256
  `b3d31cbee36f765456da7ee610c949193a8b888a140fa017ae3f535414218f0f`.
- Source canónico v27 consultado: SHA-256
  `44a80f7863d78f596099ddf7d41c9947fa8513503f65067097f1f3b05a8207ab`.
- El producto candidato se construyó en `ENTREGA_02_CIERRE`; los ZIP, source,
  WHL y binarios canónicos no fueron sobrescritos.
- Los cambios de producto se limitan a constructores, contratos, pruebas,
  fixtures, documentación y herramientas de validación. El laboratorio usa la
  misma biblioteca y el mismo kernel, pero queda fuera del catálogo estable.

La revisión dirigida consultó Entregas 01/02, los runners y locks primarios de
CORE05, source/WHL v27, los índices integrados y las fuentes concretas necesarias
para las composiciones. `DIRECTED_SOURCE_REVIEW.md` distingue qué se abrió de lo
que sólo se usó como antecedente.

## Línea T — deuda conocida

### Memoria temporal CORE05

La deuda `temporal_phase_memory.core05.pending` se cerró en la revisión
candidata mediante `temporal_phase_memory.core05.v1`, versión `1.0.0`. El port
procede de los runners primarios `run_nrh04_distributed_phase_memory_holdout.py`
y `run_nrh06_toroidal_phase_parity_holdout.py`; los locks verificados tienen
SHA-256 `e3e361808515f0a949d2cf6978edf6b73a4631927927f0ca1557cefeaffcd7a8`
y `569a95b3850f3317ffa570164b07e7700b59d66612b958e665e38e9938b19b58`.

Se conservaron cuatro fuentes, hub, bocas, distancias, clocks, geometría,
transformaciones ortogonales y cuatro brazos iniciales: intacto, bloqueo
transitorio, ablación y rewire. No existe contador externo, escritura posterior
en clock ni tabla de respuesta. Las pruebas cubren controles NRH04, paridad
NRH06, persistencia de `ComposedWorld`, DenseSequential, DenseParallel y Lazy.
El consumidor instalado instancia, ejecuta y restaura el constructor sólo con
headers y biblioteca nativos.

El dominio sigue siendo finito: NRH04 hasta `distance+12` antes del wrap
diseñado y NRH06 hasta `distance+3N`. No se extrapola `T_div=N+L` a geometrías
no colineales, fondos densos o tiempos ilimitados.

### Fixtures microscópicos

Se añadieron tres fixtures generados por el WHL oficial, elevando la matriz a
15 transiciones exactas:

- evolución alcanzable de orphan: salida `state=1`, `s_reg=8`, dirección
  `(-1,0,0)`, semántica 5;
- saturación DEMUX sobre destino ocupado con dos overflows: `s_reg=19664`;
- tensión fuerte y protección de escritura: salidas respectivas
  `state=2,s_reg=5` y `state=1,s_reg=42`.

RAW y clock exactos se conservan como inputs/outputs. El análisis separó estas
transiciones de dos clases no presentadas como fixtures dinámicos: el helper
DEMUX-to-orphan no es producido por el tick completo en este dominio, y la
cristalización no alcanza el umbral 966 con el packing actual (cota calculada
259). `demux_edge_min` y `ORPHAN_TTL` permanecen sin uso. Son afirmaciones de
inalcanzabilidad condicionadas al source, packing y productor actuales, no
prohibiciones ontológicas del kernel.

### Schedulers Dense, Lazy y paralelo

La justificación estructural y las regresiones comprueban que Lazy parte de todo
RAW no nulo —incluidos `state=0` y fuentes—, añade el halo Moore-26 para el
trabajo local, avanza todos los clocks y conserva postpaso DEMUX/copy-back
globales. El halo de selección no se identifica con el radio causal máximo.
DenseParallel mantiene lectura compartida de A, escritura disjunta de B por
slabs, barreras antes de DEMUX y copy-back, y acumuladores aislados/reiniciados.

La batería diferencial ejecutó los 15 fixtures con DenseSequential,
DenseParallel y Lazy, 1/2/4 hilos cuando aplica y tres repeticiones. Las
regresiones adicionales cubren eventos, restore, fork, cambio de backend,
reutilización de scratch y localización del primer tick discrepante. El target
de backend informó 10 146 checks y cero fallos. Esto combina deducción del
source con pruebas finitas; no se presenta como demostración universal de
ausencia de carreras o equivalencia para todo estado posible.

## Línea F — laboratorio de frontera

Se ejecutaron dos familias pequeñas, ocho casos terminados y cero parciales.
El panel primario Lazy-4 se repitió con DenseSequential-1: los resultados
físicos estructurados coincidieron exactamente entre agendas. Los archivos
completos están bajo `laboratory/` y ninguna función se promovió al catálogo.

### Actualización nativa y ruta contextual

En cuatro mundos, dos portadores preparados en `t=0` con cargas 20 y 17
produjeron en `t=1` un registro de carga 37 y dirección `(1,1,0)`. Contextos
también preparados en `t=0` transformaron en `t=3` esa dirección en las cuatro
predicciones congeladas: `(1,1,0)`, `(1,0,0)`, `(1,1,1)` y `(1,0,1)`. En `t=6`
cada mundo tuvo exactamente uno de los endpoints declarados, con carga y
dirección previstas. Tras `t=0` sólo hubo kernel y lecturas pasivas.

El control de carga cero cambió dirección sin añadir carga. Con ambos
selectores apareció una única ruta combinada: no hubo fan-out en este aparato.
El caso mide una actualización y transferencia por contexto preexistente; no
mide adquisición de ese contexto, múltiples experiencias ni replicación.

### Consulta posterior sobre el mismo mundo C6

Cuatro casos ACOPLADOS conservaron el mundo C6 sin reset hasta `t=46`. La
respuesta entrenada inicial fue 25; el retorno nativo reapareció en `t=45`.
Una consulta externa posterior de carga 13, aplicada en `t=40`, produjo 38 en
`t=45`; una carga cero dejó una diferencia durante el tránsito pero convergió al
control ausente en `t=45`; el caso cue-only rechazó la consulta posterior por
destino ocupado. La escritura de `t=40` es una experiencia externa declarada,
no retorno endógeno.

El resultado muestra admisión y transformación posterior en un mismo mundo ya
evolucionado. La desigualdad de admisión del cue-only impide atribuirla sólo al
entrenamiento, y no se midió un segundo uso funcional de la carga 38. Permanecen
experimentales `native_update_route.laboratory.v1` y
`c6_later_query_reuse.laboratory.v1`.

## Validación integrada

La copia candidata se compiló en Release con MSVC 19.50 y configuró 15 targets
CTest. Los 15/15 targets, el consumidor instalado/relocable y los 18 artefactos
Release se registran en `validation/`, junto con JUnit, hashes y procedencia.
El benchmark regenerado contiene 63 corridas y conserva igualdad RAW+clock
exacta, incluidos resultados de rendimiento desfavorables.

El paquete se acepta sólo después de verificar MANIFEST/HASHES, extraerlo a una
ruta limpia, recompilar allí el producto y ejecutar nuevamente CTest,
instalación, consumidor y ejemplos. Esas operaciones se documentan en los logs
del ZIP; no sustituyen la validación independiente con el WHL oficial usada por
los fixtures.

La prueba `cross_process_persistence` ejecuta dos procesos distintos y compara
el futuro exacto de una composición con evento pendiente; el proceso consumidor
no recibe planner ni estado en memoria del productor.

Los tiempos medidos por categoría se conservan en
`validation/CONTINUATION_TIMING.json`. La ejecución de laboratorio acumuló
15,313 s entre Lazy-4 y Dense-1; la reconstrucción limpia del primer candidato
consumió 393,158 s, incluidos 227,18 s de CTest (15/15). Revisión,
implementación y análisis se solaparon entre frentes concurrentes y se registran
con límites observables, no como duraciones aditivas inventadas.

## Matriz de estado y dependencia para Entrega 03

| Elemento | Clase | Evidencia nueva | Estado de esta revisión | Dependencia para Entrega 03 |
|---|---|---|---|---|
| Memoria temporal CORE05 | deuda conocida | constructor primario, controles, paridad, persistencia y multibackend | cerrada en producto candidato | mantener dominio/versionado al crear adapters |
| Fixtures microscópicos | deuda conocida | tres fixtures WHL exactos y análisis de alcanzabilidad | cerrada para los tres grupos definidos | conservar separación fixture/helper/deducción |
| Dense/Lazy/paralelo | deuda conocida | razonamiento del source, 15 fixtures y 10 146 checks | regresiones fortalecidas; equivalencia universal no afirmada | operación prolongada requiere vigilancia y perfiles propios |
| Ruta contextual nativa | candidato experimental | 4/4 predicciones y endpoint único | ejecutado, no promovido | revisión científica y prueba de adquisición/reutilización |
| Consulta C6 posterior | candidato experimental | carga 13, cero, ausencia y cue-only | ejecutado, ACOPLADO, no promovido | control de admisión comparable y segundo uso funcional |
| Actualización multiexperiencia | hipótesis no confirmada | no ejecutada en este laboratorio | pendiente | aparato reutilizable sin memoria nueva por episodio |
| Retorno/enseñanza endógena | hipótesis no confirmada | la consulta posterior fue externa | pendiente | mediación ambiental intacta/corte/sham y uso posterior |
| Fan-out/replicación | hipótesis no confirmada | salida única en los cuatro casos | no observado en este aparato | constructor y controles específicos; catálogo experimental |
| Adapters/aplicaciones | alcance reservado | no construidos | no ejecutado | sólo usar capacidades estables y mantener explícitos los supervisores |

## Límites, bloqueos y decisiones pendientes

La base comprobada permite que Entrega 03 consuma el runtime, persistencia,
schedulers, catálogo estable y CORE05 dentro de sus contratos. Antes de ofrecer
operación aplicada prolongada debe decidirse qué políticas externas de recursos
y supervisión serán parte explícita del producto. Actualización multiexperiencia,
cierre ambiental, enseñanza endógena y fan-out general necesitan evidencia y
revisión científica antes de cualquier promoción. Ninguna ausencia observada en
este laboratorio se generaliza a una imposibilidad de DEE.
