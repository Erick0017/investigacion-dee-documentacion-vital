# Auditoría de ramas microscópicas y agendas

## Autoridad del oráculo

Los tres fixtures añadidos se generaron ejecutando el WHL oficial, no la
biblioteca C++ bajo prueba. Antes de importarlo, el generador exige estas
identidades SHA-256:

| Artefacto | SHA-256 |
|---|---|
| WHL `dee_universe_v27-27.0.0-cp313-cp313-win_amd64.whl` | `69297e6f06761c8b2f65d24a3fd7a2f16a3f67595a7f9660739ab65f47abc939` |
| `dee_universe_v27/__init__.py` instalado | `7e2991b1fc8a053ee44ead6e177b129855ae9265dea68505a8e545f0c3fdf8b4` |
| extensión CPython cargada | `0b17ba32037935a255b0f2182a52137bceab424f7e09126b761076b63e42c6ff` |

El manifiesto `fixtures/whl_v27/manifest.json` conserva además versión de
Python/Numpy, dimensiones, ticks, contadores y hash de cada `.dtr`.

## Clasificación exacta

| Grupo | Clasificación | Testigo o argumento |
|---|---|---|
| Evolución propia de huérfano | Alcanzable | `orphan_reachable_evolution.dtr`: `(state,s_reg,dir,sem)` pasa de `(9,7,(0,0,0),5)` a `(1,8,(-1,0,0),5)` |
| Postpaso DEMUX sobre huérfano | Helper defensivo, inalcanzable desde `tick` | todo productor de delta omite candidatos con semántica 5; la pasada base tampoco convierte una entrada no huérfana en huérfana |
| DEMUX sobre destino ya ocupado | Alcanzable | `demux_occupied_saturation.dtr`: dos overflows llegan a un destino nacido con `s_reg=19664` y el resultado permanece saturado en 19664 |
| Tensión fuerte | Alcanzable | `strong_tension_write_protection.dtr`: cuatro vecinos con firma tetraédrica dejan el foco en `state=2, s_reg=5`; la tensión electrodébil daría regla cero |
| Protección de escritura | Alcanzable | el segundo foco del mismo fixture tiene siete vecinos y suma vectorial cero; en fase cero conserva `s_reg=42`, donde la ruta no protegida lo incrementaría |
| Cristalización | Inalcanzable con el packing actual | `s_reg<=65535` y 26 vecinos acotan `|grad_x|+|grad_y|+|grad_z|` por `3*26*65535=5,111,730`; la división entera por 19,665 da como máximo 259, menor que 966 |
| `demux_edge_min` / `ORPHAN_TTL` | Helper/constante sin uso | no existe llamada/lectura en el source vigente; no se atribuye cobertura física a su mera presencia |

Hashes de los nuevos testigos:

| Fixture | SHA-256 |
|---|---|
| `orphan_reachable_evolution.dtr` | `fcf6661e1bb2ca187d38d28281e4ee77c584e6af41c043037c1251a5a1ece3a4` |
| `demux_occupied_saturation.dtr` | `d5974c7b00c8a83db7f3805059cd210f378da6f5f3ee1a8b0a1e5e8a2c5d61da` |
| `strong_tension_write_protection.dtr` | `b8271c5168bbae71c9a8572325bcc7f969ac867788d2bef1bf7fd2e6a85aef3d` |

La prueba de inalcanzabilidad del postpaso no depende de haber omitido un caso
en la búsqueda. Un delta sólo se emite después de leer el candidato en el
buffer A y descartar `semantic==5`. Para ese mismo sitio, la pasada base
preserva una semántica no huérfana o produce void/normal/XNOR; nunca produce 5.
Por tanto, si `delta[i]>0`, el buffer B previo al postpaso no puede ser huérfano.
La rama se conserva como defensa interna, pero un fixture público que afirmara
alcanzarla inventaría un estado intermedio que el oráculo no expone.

## Regresión de agendas

### Justificación estructural del conjunto de trabajo

La suficiencia Lazy se deriva de la lectura exacta de `actualizar_voxel`, no de
una hipótesis de baja ocupación. Primero se copia todo RAW A a B y se calcula
`clockB[i]=clockA[i]+1` para **todos** los registros. Después se selecciona cada
palabra `raw!=0`, aunque `state==0`, y todo su halo Moore-26 con wrapping
modular. Esto incluye fuentes semantic=4, campos no nulos sin ocupación y toda
materia existente. Un sitio RAW-cero fuera de ese halo no tiene vecino RAW no
nulo: las ramas de vacío no pueden leer un vivo, fuente, gradiente o XNOR que
produzca un resultado distinto del default ya copiado. Todo nacimiento posible
en una frontera está, por tanto, dentro del halo. Esta es una propiedad de la
dependencia local de un tick; el halo de agenda no se confunde con el radio
causal de varios ticks.

Cada índice del vector `work` es propiedad de un solo worker y sólo ese worker
escribe `gB[i]` y `clockB[i]`. Las lecturas físicas provienen exclusivamente de
A/clockA, que permanecen inmutables hasta terminar la evaluación. Los únicos
efectos no locales son los deltas DEMUX: se acumulan con `fetch_add` atómico en
un array que se inicializa a cero en cada tick. Tras hacer `join` de todos los
workers, un postpaso **global** recorre cada destino, consume su delta con
`exchange(0)` y aplica saturación/semántica. Por eso un destino DEMUX no se
pierde aunque no estuviera en el conjunto de trabajo local.

DenseParallel divide slabs de x disjuntos. Mantiene la misma propiedad de una
escritura B por índice, comparte A sólo para lectura y usa contadores/deltas
atómicos para los efectos combinados. El `join` es la barrera que precede al
postpaso; no hay lectura de B por otro worker durante la regla local. Finalmente
ambas agendas copian B y clockB sobre A y clockA exactamente una vez. El
wrapping usa la misma aritmética modular y no se añade un swap. Scratch B puede
contener una frontera anterior al entrar: Dense lo sobrescribe por índice y
Lazy restablece primero el default global, lo que fundamenta las regresiones de
reutilización de scratch.

Este argumento demuestra cobertura y ausencia de escrituras B solapadas según
la estructura actual. Las pruebas 1/2/4 hilos y las repeticiones complementan,
pero no convierten el razonamiento en una prueba formal universal del modelo de
memoria o de todas las plataformas.

`execution_backends` conserva un estado de referencia después de cada tick y
compara sin tolerancia RAW, clock, overflows y genesis contra:

- denso secuencial 1 hilo;
- denso paralelo 1, 2 y 4 hilos;
- Lazy 1, 2 y 4 hilos;
- tres repeticiones de cada agenda.

Después de cada transición también exige igualdad entre buffer activo y
scratch. Todo fallo informa fixture, tick, repetición, backend, hilos y el
primer índice lineal divergente, evitando que una convergencia posterior o un
mensaje genérico oculte el primer desacuerdo.

`integration_persistence` guarda en tick 1 un evento pendiente para la frontera
4 y construye cuatro continuaciones: denso secuencial, carga Lazy-4, fork
denso-paralelo-2 y `restore_snapshot` in-place Lazy-2. Avanza una frontera por
vez hasta tick 8. En cada frontera compara RAW, clock y recibos completos con
diagnóstico de primera divergencia; verifica que el recibo siga `Scheduled`
hasta tick 4 y pase a `Applied` con `effective_tick=4` después de aplicar esa
frontera. El primer tick posterior al restore también comprueba de forma
observable que los scratch reconstruidos no alteran la continuación.

Esta evidencia prueba esas trayectorias finitas. No demuestra equivalencia de
todos los microestados ni convierte helpers inalcanzables en API física.
