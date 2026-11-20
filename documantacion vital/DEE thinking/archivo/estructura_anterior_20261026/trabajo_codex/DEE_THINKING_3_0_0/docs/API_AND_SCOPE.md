# API y alcance — DEE thinking 3.0.0

## Contrato del producto

DEE thinking 3.0.0 es una biblioteca estática C++20 y una extensión nativa
CPython 3.13 para Windows x64. Ejecuta la transición DEE v27 incorporada en
`src/kernel_v27.cpp`; no importa ni delega en `dee_universe_v27`. El source del
kernel es idéntico al de 2.2.0 y su SHA-256 es
`fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31`.

La versión 3.0.0 conserva Runtime, catálogo, composición y los protocolos
H1–H4/F1–F2 de 2.2.0. Añade presets físicos acotados derivados de MBP4,
observación pasiva, seguimiento de sitios declarados y diagnósticos que sólo
intervienen una copia profunda. Un preset instala una receta física antes de
`t0`; las respuestas posteriores las produce v27. Ni el wheel ni el snapshot
semilla contienen una respuesta terminal aprendida.

## Mapa trazable de capacidades nuevas

Las rutas de la columna MBP4 son miembros de
`MENTE_BASAL_4_ORGANIZACION_BASAL_PERSISTENTE_VALIDACION_RESULTADOS.zip`.
Las rutas de prueba nombran especificaciones ejecutables de este árbol; esta
tabla no afirma todavía que una corrida 3.0.0 haya aprobado.

| Capacidad | API e implementación 3.0.0 | Fuente MBP4 portada o consultada | Prueba que fija el contrato | Ejemplo |
|---|---|---|---|---|
| Mundo relacional por historia | `basal::Config::relational_reference`, `basal::World::create`; `src/basal.cpp::install_relational` | `12_CHECKPOINTS/OBP_FRESH_VALIDATED_T32.deetsnap`; `22_TRANSFORMATIVE_GENEALOGY_RELATIONAL_CONSOLIDATION/RUNNER/relational_body.py` y su `EXPERIMENT_CONFIG.json` | `tests/basal_tests.cpp`; `tests/python/test_basal_api.py`; regresiones R1/R2 en `tests/python/test_mbp4_regressions.py` | `examples/basal_product.cpp`; `create_relational_world()` |
| Reescritura contextual acotada | `basal::Config::contextual_reference`; `src/basal.cpp::install_contextual` | `23_NATIVE_FEEDBACK_RELATIONAL_REWRITE/RUNNER/run_feedback_rewrite.py`; replay y límites en `24_CONTEXTUAL_CAUSAL_MECHANISM` | `tests/basal_tests.cpp::contextual`; `tests/python/test_basal_api.py::test_contextual_write_gate_and_retention`; regresión R3 en `tests/python/test_mbp4_regressions.py` | `create_contextual_world()` y el bloque contextual de `README.md` |
| Inspector local pasivo | `observation::inspect_write_gate`, `observation::compare_site`; `src/observation.cpp` | `23_NATIVE_FEEDBACK_RELATIONAL_REWRITE/RUNNER/run_feedback_rewrite.py::sample_write_gate`; `24_CONTEXTUAL_CAUSAL_MECHANISM/TELEMETRY/INTACT_REPLAY_AND_GATE.json` y `24_CONTEXTUAL_CAUSAL_MECHANISM/TELEMETRY/TECHNICAL_CHECKS.json` | bloques de gate/transición en `tests/basal_tests.cpp` y `tests/python/test_basal_api.py` | `examples/basal_product.cpp` |
| Traza pasiva y acotada | `genealogy::PassiveTracker`; `src/genealogy.cpp` | instrumentación de `22_TRANSFORMATIVE_GENEALOGY_RELATIONAL_CONSOLIDATION/RUNNER/genealogy_tracker.py`, reducida deliberadamente a lecturas sin ablación; `22_TRANSFORMATIVE_GENEALOGY_RELATIONAL_CONSOLIDATION/TELEMETRY/TRACKER_INSTRUMENTAL.json` | bloques `PassiveTracker` de `tests/basal_tests.cpp` y `tests/python/test_basal_api.py` | `examples/basal_product.cpp`; `tests/consumer_basal/main.cpp` |
| Contraste intervenido en fork | `ResearchStateEdit`, `Runtime::diagnostic_fork`, `basal::World::diagnostic_fork`, `diagnostics::compare_fork`; `src/runtime.cpp` y `src/diagnostics.cpp` | política `diagnostic_clone_policy` y funciones `clone_with_edit`/`local_fork` de `24_CONTEXTUAL_CAUSAL_MECHANISM/RUNNER/run_contextual_mechanism.py` | bloques de autorización, aislamiento y phase miss en `tests/basal_tests.cpp` y `tests/python/test_basal_api.py`; R4/R7/R8 en `tests/python/test_mbp4_regressions.py` | `examples/basal_product.cpp`; `compare_diagnostic_fork()` |
| Continuación basal persistente | `basal::World::save_snapshot/load_snapshot` sobre snapshot Runtime v2 y metadatos basales schema 1 | checkpoints y equivalencias de continuación de las secciones 20 y 22–24 | round trip en `tests/basal_tests.cpp`; puente `tests/basal_checkpoint_bridge.cpp` + `tests/python/basal_cross_language_driver.py`; continuaciones R2/R3/R6 en `tests/python/test_mbp4_regressions.py` | `examples/basal_product.cpp`; consumidor `tests/consumer_basal` |
| Runtime, catálogo, composición, H1–H4/F1–F2 | APIs públicas de 2.2.0 sin sustitución; mismos sources de kernel, organizaciones, catálogo, composición y protocolos | No son capacidades nuevas de MBP4; proceden de 2.2.0 | suites heredadas `runtime_tests`, `reference_tests`, `composition_*`, `integrated_protocols_tests`, bridges y pruebas Python | ejemplos heredados de `examples/` |

`fixtures/mbp4/regressions/MANIFEST.json` enumera 15 oráculos congelados y
vincula cada uno con miembro, tamaño y SHA-256 del archivo MBP4 fuente, cuyo
SHA-256 declarado es
`4d20d893d04486de047c66ce76c9f7dad067158941b553025bd946b7dc6ce086`.
La prueba `test_fixture_manifest_integrity` vuelve a calcular esos hashes; el
Runtime normal no lee este árbol. R1–R4 y R6–R8 ejercitan API pública o
continuación física contra esos oráculos. R5 sólo fija la evidencia primaria
congelada de rescates y distingue escrituras absolutas de igualdad del delta;
no reconstruye el rescate desde cero. La existencia de la suite no sustituye
el resultado de ejecutarla en la entrega final.

## API pública nueva

### C++

Los headers nuevos son `dee_thinking/basal.hpp`,
`dee_thinking/observation.hpp`, `dee_thinking/genealogy.hpp` y
`dee_thinking/diagnostics.hpp`.

- `basal::Config` selecciona `Preset`, `History`, `Control`, `DomainMode`,
  origen, backend y semilla. `relational_reference(path)` y
  `contextual_reference(path)` crean las configuraciones de referencia.
- `basal::World::create(config)` valida y carga la frontera semilla, instala la
  receta pre-`t0` y devuelve un mundo nuevo. `attach(...)` sólo adjunta una
  vista no propietaria suministrada por el llamador a un Runtime existente: no
  instala materia ni duplica sus buffers. En C++ el llamador debe conservar el
  `Runtime` durante toda la vida de la vista; el binding Python aplica
  `keep_alive` para conservarlo automáticamente.
- `basal::World` expone `advance`, `observe`, `fork`, `diagnostic_fork`,
  `save_snapshot` y `load_snapshot`. `ports()` identifica sitios declarados;
  `observe()` informa ticks absoluto/relativo, disponibilidad, A/B/comparador,
  `delta = A.s_reg - B.s_reg`, proyección del eje y soportes.
- `observation::inspect_write_gate(runtime, site, include_neighbors)` describe
  centro, vecindad Moore-26, regla material, protección, periodo/fase y la rama
  local. `compare_site(before, after, site)` compara dos fronteras ya existentes.
- `genealogy::PassiveTracker(sites, frame_budget)` captura únicamente los
  sitios declarados y registra cambios observados. El presupuesto predeterminado
  es 4096 frames; al agotarse, `capture_stopped()` se vuelve verdadero y dejan
  de acumularse frames.
- `Runtime::diagnostic_fork(edits, authorization)` copia estado, scratch,
  canales, cola, recibos, fase y metadatos antes de aplicar ediciones RAW/clock
  a la rama. Rechaza falta de autorización, ediciones vacías, coordenadas
  repetidas o fuera de rango. `diagnostics::compare_fork` avanza una referencia
  y una rama intervenida durante un horizonte explícito y cuenta diferencias.

### Python

El binding nativo refleja esas clases y añade dos helpers en
`python/dee_thinking/__init__.py`:

```python
import dee_thinking as dt

world = dt.create_relational_world(dt.BasalHistory.AB)
world.advance(1)
reading = world.observe()

context = dt.create_contextual_world()
context.advance(131)
gate = dt.inspect_write_gate(context.runtime, context.ports.b, True)
```

`reference_seed_path()` resuelve la semilla incluida en el wheel. Los enteros
RAW/clock siguen siendo `uint64` nativos; el binding no los convierte a
`float`. Igual que en 2.2.0, `Runtime.advance` no libera el GIL y una instancia
mutable admite un solo escritor.

## Pasivo no significa diagnóstico

| Operación | ¿Muta el Runtime observado? | Interpretación permitida |
|---|---:|---|
| `Runtime::observe`, `observe_many`, `metrics`; `basal::World::observe` | No | Lectura de la frontera actual |
| `inspect_write_gate`, `compare_site` | No | Descripción local o diferencia entre fronteras; `demux_status` permanece `UNRESOLVED_FROM_PASSIVE_PRESTATE` |
| `PassiveTracker::capture` | No; sólo cambia el historial interno del tracker | Cambios en sitios declarados, con scope `DECLARED_SITES_ONLY`; no procedencia universal |
| `probe` | Sí, agenda una escritura física | Intervención, aunque el recibo la distinga de una experiencia |
| `diagnostic_fork` / `compare_fork` | Sí, pero sólo en copias profundas | Contraste diagnóstico; la edición nunca ocurrió en el padre |

La genealogía experimental MBP4 incluía ablaciones. La API estable no las
disfraza de observación: las lecturas quedaron en `PassiveTracker` y las
ediciones se trasladaron al contrato explícito de fork diagnóstico.

## Dominio y límites

La receta publicada exige N=47, semilla en tick absoluto 32 y
`action_distance=5`. La semilla canónica es
`OBP_FRESH_VALIDATED_T32.deetsnap`, SHA-256
`cd09a4d94f72e00d9a5163c8dfd1d62e1528f1d146e4cb44ae23d261b3da09e6`.
`World::create` comprueba N, tick y ausencia de canales/recibos, pero no calcula
ese hash; un consumidor C++ que acepte rutas no confiables debe verificarlo.

En `DomainMode::Validated` sólo se aceptan los orígenes `(15,15,15)`,
`(22,20,24)` y `(28,26,18)`. El preset relacional representa las historias
`AB`, `BA`, `H0`, `simultaneous` y `sham`. El contextual acepta sólo historia
`AB` y controles `full`, `no_action`, `return_cut`, `off_path` y `phase_miss`.
`DomainMode::Research` relaja únicamente la lista de orígenes; no relaja N,
distancia, semilla ni las guardas del preset, y no convierte una traducción en
resultado validado.

El oráculo contextual codificado es una transición B 100→101 y delta +1→0 de
tick relativo 131 a 132, con lectura de retención finita. MBP4 también mostró
que `return_cut` reprodujo esa escritura y que las intervenciones selectivas
probadas en los productos exteriores de acción no los hicieron necesarios.
Por ello 3.0.0 no publica causalidad de feedback exterior ni generaliza esa
ausencia a otras geometrías.

No se afirma consciencia, AGI, biología, energía de `s_reg`, aprendizaje
ilimitado, procedencia DEMUX desde un preestado pasivo, identidad causal a
partir de un observer parcial ni seguridad para mutaciones concurrentes. Una
geometría aceptada sólo es preparación: debe ejecutarse con v27 y medirse.

## Snapshots

`Runtime::save_snapshot` sigue escribiendo formato v2; `load_snapshot` acepta
v1 y v2. El payload contiene dimensión/tick/pausa, RAW y clock activos, canales,
eventos pendientes, recibos, fase, backend solicitado y metadatos inertes. Los
scratch se reconstruyen; los metadatos no ejecutan código ni alteran v27. El
checksum FNV-1a detecta corrupción accidental, no autentica a un adversario, y
el lector limita el archivo a 2 GiB.

`basal::World::save_snapshot` añade `dee_thinking.basal.*` con schema 1:
receta, preset, historia, control, dominio, origen, distancia, `t0` e id de
semilla. El loader exige schema, preset, historia, control, dominio, origen,
distancia y `t0`; reconstruye la vista sin reinstalar la receta. Para schema 1
también exige la receta `mbp4.reference.v1`, la identidad de semilla
`OBP_FRESH_VALIDATED_T32` y `t0=32`, con un tick físico igual o posterior. Estas
comprobaciones son compatibilidad de formato y coherencia, no autenticación
criptográfica del estado. Un snapshot Runtime 2.2.0 sin schema basal debe
cargarse como `Runtime`, no como `BasalWorld`. Los frames/transiciones de
`PassiveTracker` y el detalle completo del ledger de ediciones diagnósticas no
se serializan.

La escritura usa un temporal exclusivo en el mismo directorio y la primitiva
de reemplazo de la plataforma. Un fallo de publicación conserva el destino
anterior; esto no promete durabilidad frente a pérdida de energía o hardware.
