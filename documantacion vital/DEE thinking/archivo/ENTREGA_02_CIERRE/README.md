# DEE thinking — Entrega 02, cierre y frontera

Biblioteca C++20 nativa para ejecutar el kernel DEE v27 congelado, mantener un
mundo persistente y construir organizaciones parametrizadas en una composición
física compartida. No carga Python, el `.pyd` ni ejecuta subprocesses Python.

## Uso rápido

En una consola de PowerShell:

```powershell
.\tools\build_windows.ps1 -Configuration Release
```

El script localiza una única instalación de Visual Studio mediante `vswhere`,
usa el compilador, CMake y Ninja de esa misma instalación, compila, ejecuta
CTest e instala el paquete CMake. El comportamiento predeterminado de
`Runtime` continúa siendo el backend denso secuencial.

Desde otro proyecto CMake instalado:

```cmake
find_package(dee_thinking 2 CONFIG REQUIRED)
target_link_libraries(mi_programa PRIVATE DEE::thinking)
```

La API pública principal está en:

- `dee_thinking/runtime.hpp`: mundo, eventos, observación, snapshots y backends;
- `dee_thinking/organization_catalog.hpp`: descriptores, parámetros y puertos;
- `dee_thinking/composition.hpp`: análisis estático y mundo compuesto;
- `dee_thinking/kernel_v27.hpp`: transición exacta y selección técnica de
  `DenseSequential`, `DenseParallel` o `Lazy`.

Los ejemplos `dee_composition_a` y `dee_composition_b` construyen sus aparatos
mediante el catálogo y el planificador públicos. Las organizaciones comparten un
único `Runtime`; no se copian respuestas entre mundos.

El contrato catalogal es inspeccionable antes de ejecutar: descriptor de
footprint inicial, relación funcional, región de lectura, contexto requerido y
horizonte; registros inmutables de footprint, contratos de canal y presupuesto
de recursos por instancia; y capacidad máxima de conexión por puerto. Esa
metadata describe el aparato, pero no sustituye su evolución física.

## Mapa de capacidades

| Capacidad | Fuente concreta | Contrato público | Prueba | Estado de producto |
|---|---|---|---|---|
| Transporte/redirección | CORE05 / Entrega 01 E1 | `transport.axis.v1` | fixtures, regresión E1 | implementado y probado |
| Aprendizaje de relación | CORE06 C6H01 | `relation_learning.c6h01.v1` | consulta admitida en t6 | implementado y probado |
| Actualización/transferencia | C7H01/C7H03 y PENSAMIENTO 01 | `mobile_lineage.c7h03.v1`, `native_update_bridge.p01.v1` | Composición A y controles | implementado y probado |
| Memoria relativa/historia | Ingeniería 02 | `relative_history.i02.v1` | HA/HB en Composición B | implementado y probado en su dominio |
| Integración/separación multicanal | CORE07 / Procesos 02 | `contextual_multichannel_recurrence.p02.v1` | B ausente frente a B carga cero | implementado y probado en su dominio |
| Recurrencia/uso posterior | PENSAMIENTO 01 | puertos de consultas y suministro | respuestas sucesivas finitas | implementado y probado en horizonte finito |
| Contexto distribuido | Ingenierías 05–06 | `distributed_context.i05.v1` | testigo integrado en B | implementado y probado en su dominio |
| Memoria temporal por fase | CORE05 NRH04/NRH06 | `temporal_phase_memory.core05.v1` | controles, paridad, persistencia y multibackend | incorporado y probado en el dominio congelado |

Los estados anteriores son estados técnicos del producto, no dictámenes sobre
mente, autonomía, universalidad del aprendizaje o equivalencia física externa.

## Fidelidad y alcance

La fuente canónica consultada tiene SHA-256
`44a80f7863d78f596099ddf7d41c9947fa8513503f65067097f1f3b05a8207ab`.
La ruta de cinco argumentos de `tick` y el `Runtime` sin configuración explícita
mantienen denso secuencial. Lazy y paralelo sólo cambian la agenda técnica;
las pruebas comparan RAW y clock completos por tick.

Los snapshots v2 guardan estado, cola, recibos, metadatos inertes de la
composición y configuración de ejecución. El lector conserva snapshots v1; si
carecen de metadatos, se declaran *legacy* sin inventarlos. La publicación de un
snapshot usa un temporal del mismo directorio y sustitución atómica disponible
en el sistema. Esto evita publicar un archivo parcial durante errores normales;
no promete durabilidad absoluta frente a fallos de hardware o energía.
Una composición v2 puede recuperarse sin reconstruir manualmente su planner con
`ComposedWorld::load_snapshot(path)` (catálogo incorporado) o con la sobrecarga
que recibe un `OrganizationCatalog`; ambas validan receta, versiones y
manifiesto antes de instalar el estado operativo.

La validación de composición distingue A/C7 de la demostración C6H01. A incluye
controles no-update y no-learning independientes; B incluye un sham con los
mismos campos/tiempo que el corte pero trayectoria paralela. C6 presenta su
consulta posterior en un target separado. El CMake vigente configura 15 tests;
la corrida Release integrada registrada en `validation/` aprobó 15/15,
incluidos CORE05, el restore autocontenido y el consumidor instalado relocable.

`laboratory/` contiene dos exploraciones acotadas ejecutadas y sus controles.
Son evidencia experimental separada y no añaden funciones al catálogo estable.

El benchmark fuente separa tiempos del kernel y del wrapper, incluido coste de
agenda/aplicación del evento, restore y total E2E. El JSON entregado contiene 63
corridas, conserva los resultados desfavorables y registra igualdad RAW+clock
exacta en todas ellas.

Consulte `docs/ORGANIZATION_CATALOG.md`, `docs/API_CONTRACT.md`,
`docs/TECHNICAL_REPORT.md` y `docs/REPRODUCIBILITY.md` para contratos,
resultados de validación y límites.
