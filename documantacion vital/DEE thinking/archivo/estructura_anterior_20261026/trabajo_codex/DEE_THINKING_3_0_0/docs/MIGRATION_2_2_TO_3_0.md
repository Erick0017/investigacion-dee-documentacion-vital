# Migración de DEE thinking 2.2.0 a 3.0.0

## Resumen de compatibilidad

3.0.0 es una ampliación de fuente, no una promesa de ABI binaria con 2.x. La
comparación del árbol actual con la entrega oficial 2.2.0 muestra:

- `kernel_v27.hpp/.cpp`, organizaciones, catálogo, composición y protocolos
  integrados permanecen sin cambios; el kernel conserva SHA-256
  `fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31`.
- Los headers públicos 2.2.0 permanecen iguales salvo `runtime.hpp`, que añade
  `ResearchStateEdit` y `Runtime::diagnostic_fork`, y `version.hpp`, que cambia
  el producto a 3.0.0.
- Se añaden cuatro headers/sources: `basal`, `observation`, `genealogy` y
  `diagnostics`, además de bindings Python y la semilla MBP4 T32.
- El escritor Runtime continúa en snapshot v2 y el lector continúa aceptando
  v1/v2. Se añade un schema basal dentro de los metadatos inertes de v2; no se
  cambia la ley ni el layout Runtime.
- El wheel conserva nombre de importación `dee_thinking`, plataforma
  `cp313-cp313-win_amd64` y la política de GIL de 2.2.0.

Debe recompilar todos los consumidores C++. El package config usa
`SameMajorVersion`, por lo que cambie:

```cmake
# 2.2.0
find_package(dee_thinking 2 CONFIG REQUIRED)

# 3.0.0
find_package(dee_thinking 3 CONFIG REQUIRED)
target_link_libraries(my_program PRIVATE DEE::thinking)
```

No enlace objetos 2.x con `dee_thinking.lib` 3.0.0 ni reutilice su cache CMake.

## Cambios de API

| Área 2.2.0 | Estado en 3.0.0 | Acción de migración |
|---|---|---|
| `Runtime`, eventos, observación, backends, fork y snapshots | Conservados | Recompilar; el código fuente existente no necesita adoptar la API basal |
| `OrganizationCatalog`, `CompositionPlanner`, `ComposedWorld` | Conservados | Mantener recetas/versiones existentes y sus snapshots de composición |
| H1–H4/F1–F2 y checkpoints | Conservados | Mantener IDs y funciones; no sustituirlos por presets MBP4 |
| CMake `DEE::thinking` | Conservado, major pasa a 3 | Actualizar `find_package` y usar un prefijo de instalación nuevo |
| Wheel/import `dee_thinking` | Mismo import, versión 3.0.0 | Crear un venv limpio e instalar el wheel 3.0.0 local |
| Mundo basal MBP4 | Nuevo | Usar `BasalConfig`/`BasalWorld` en C++ o `create_relational_world`/`create_contextual_world` en Python |
| Observación local/tracking | Nuevo | Usar `inspect_write_gate`, `compare_site_transition` y `PassiveTracker` sólo como lecturas |
| Intervención diagnóstica | Nuevo | Construir `ResearchStateEdit`, autorizar explícitamente y trabajar sobre fork |

En Python, la ruta mínima nueva es:

```python
import dee_thinking as dt

world = dt.create_relational_world(dt.BasalHistory.AB)
world.advance(1)
print(world.observe().delta)
```

En C++, la semilla es un argumento explícito; no hay búsqueda global oculta:

```cpp
#include <dee_thinking/basal.hpp>

auto config = dee::thinking::basal::Config::relational_reference(seed_path);
config.history = dee::thinking::basal::History::AB;
auto world = dee::thinking::basal::World::create(config);
world.advance(1);
```

La instalación CMake coloca la semilla en
`share/dee_thinking/fixtures/mbp4/OBP_FRESH_VALIDATED_T32.deetsnap`; una
aplicación C++ debe recibir o resolver esa ruta. El helper Python
`reference_seed_path()` usa recursos del paquete.

## Migración de snapshots

### Runtime y composiciones existentes

1. Conserve el snapshot 2.2.0 original sin modificarlo.
2. Cárguelo en 3.0.0 con `Runtime::load_snapshot`/`Runtime.load_snapshot`. Los
   v1 se marcan como legacy y reciben el backend secuencial predeterminado; los
   v2 conservan backend y metadatos.
3. Para `ComposedWorld`, use su loader y catálogo, igual que en 2.2.0. Un v1 no
   contiene receta autocontenida y nunca debe reinterpretarse como composición.
4. Continúe en una copia y guarde bajo otro nombre. Compare tick, RAW, clock,
   recibos y observaciones antes de promoverla.

El formato v2 es compartido, pero este corte no promete lectura inversa de
snapshots 3.0.0 por software 2.2.0. Mantenga el entorno 2.2.0 para rollback y no
sobrescriba su último checkpoint.

### Snapshots basales

`BasalWorld.load_snapshot` sólo acepta un Runtime v2 que incluya
`dee_thinking.basal.schema=1` y los campos preset, historia, control, dominio,
origen, distancia y `t0`. Un snapshot 2.2.0 o un checkpoint MBP4 histórico
carece normalmente de ese schema: cárguelo como `Runtime`. El loader basal no
autentica `recipe`/`seed_id` ni vuelve a comprobar el hash de la semilla. No
llame a `create_*` para “migrarlo”, porque eso construye un mundo basal nuevo
desde la semilla T32.

Si conoce de forma independiente `Config`, `Ports` y `t0`,
`basal::World::attach` puede adjuntar una vista a un Runtime cargado. `attach`
no instala ni verifica la receta y sólo comprueba que las dimensiones
coincidan; la corrección de los puertos queda bajo responsabilidad del
llamador. La vista no posee ni copia el `Runtime`: en C++ éste debe sobrevivir
a la vista; en Python el binding conserva el objeto origen mediante
`keep_alive`. Mantenga además un único escritor mutable por Runtime.

Los snapshots basales guardan la descripción del mundo, no el historial del
`PassiveTracker`. Una rama diagnóstica guarda las marcas
`dee_thinking.diagnostic_fork` y el número de ediciones, no el ledger completo
con todas sus etiquetas. Conserve el resultado `DiagnosticComparison` aparte
si forma parte de la evidencia.

## Cambio conceptual obligatorio

La migración no debe confundir tres operaciones:

- **Pasiva:** `observe`, `inspect_write_gate`, `compare_site` y
  `PassiveTracker::capture` no cambian el Runtime. Un gate local no resuelve
  por sí solo procedencia DEMUX.
- **Evolución:** `advance` ejecuta v27 y sí cambia la trayectoria. El preset
  sólo prepara el estado anterior a `t0`.
- **Diagnóstico:** `diagnostic_fork` edita una copia profunda y requiere el
  booleano de autorización. `compare_fork` avanza referencia y diagnóstico;
  ninguna edición se atribuye al padre.

`probe` sigue siendo una escritura física programada, no una lectura pasiva.

## Dominio al adoptar los presets

No traslade automáticamente parámetros de una aplicación 2.2.0 al constructor
basal. La implementación 3.0.0 fija N=47, tick semilla 32 y distancia 5. En
modo validado restringe los orígenes a `(15,15,15)`, `(22,20,24)` y
`(28,26,18)`; el contextual acepta historia AB y los cinco controles
declarados. `Research` sólo abre otras traducciones y no amplía la evidencia.

El contextual reproduce como contrato esperado la ventana finita MBP4 de tick
relativo 131→132. No demuestra que el camino exterior de acción sea necesario:
los controles MBP4 publicados no sostienen esa atribución. No convierta el
nombre “feedback” ni una diferencia de fork en una afirmación causal más amplia.

## Procedimiento recomendado

1. Congele wheel, install prefix, snapshots y logs 2.2.0.
2. Cree directorios de build/install 3.0.0 nuevos y un venv CPython 3.13.11
   nuevo; no haga instalación editable ni superpuesta.
3. Reconstruya biblioteca, pruebas, instalación, consumidor externo y wheel con
   VS 18/MSVC 19.50, CMake 4.2.3 y Ninja 1.12.1 según
   `BUILD_AND_RECONSTRUCTION.md`.
4. Ejecute primero la suite heredada para detectar regresiones 2.2.0 y después
   las pruebas basales C++/Python, `test_mbp4_regressions.py` y el puente
   bidireccional. La regresión R5 fija telemetría primaria congelada; no la
   presente como reconstrucción independiente del rescate.
5. Registre resultados reales y hashes; no copie cifras históricas de 2.2.0 ni
   resultados MBP4 como si fueran resultados de una corrida 3.0.0.
6. Sólo entonces ensamble la entrega con `tools/package_3_0.py` y vuelva a
   comprobarla con `tools/verify_delivery_3_0.py`; no reutilice scripts 2.2.0.
7. Cambie consumidores de producción sólo después de comparar sus propios
   snapshots y observables dentro de su dominio.

La reconstrucción exacta y los comandos de instalación limpia están en
`docs/BUILD_AND_RECONSTRUCTION.md`; el contrato y sus límites están en
`docs/API_AND_SCOPE.md`.
