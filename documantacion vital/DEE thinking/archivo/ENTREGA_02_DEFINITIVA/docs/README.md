# DEE thinking — Entrega 02 de 03

Esta entrega amplía la biblioteca C++20 nativa de Entrega 01 con tres piezas:

1. un catálogo de organizaciones parametrizadas y contratos de puertos;
2. composición física de varias organizaciones en un único `Runtime`;
3. agendas equivalentes densa secuencial, densa paralela y Lazy del kernel
   congelado DEE v27.

El producto ejecutable no carga Python, el WHL ni el `.pyd`. Python sólo se
usa en herramientas separadas de generación/verificación de fixtures y del ZIP.

## Estructura

```text
include/dee_thinking/   API pública
src/                    kernel, runtime, catálogo y composición
tests/                  regresiones, equivalencia y consumidor instalado
examples/               composiciones y consumidor por API pública
benchmarks/             medición técnica reproducible de backends
fixtures/               oráculos WHL y snapshot v1 real
cmake/                  paquete CMake instalable
tools/                  build, validación y empaquetado
validation/             resultados de esta compilación/ejecución
docs/                   contratos, alcance, informe y pendientes
build/Release/          binarios Release incluidos sólo en el ZIP final
```

## Construcción e instalación

Desde la raíz extraída:

```powershell
& .\tools\build_windows.ps1 -Configuration Release
```

El script selecciona una sola instalación de Visual Studio con `vswhere`, usa
su MSVC, CMake y Ninja, ejecuta CTest, instala el paquete y construye en un
directorio independiente corto un consumidor que sólo conoce la instalación.

Un proyecto externo usa:

```cmake
find_package(dee_thinking 2 CONFIG REQUIRED)
target_link_libraries(mi_programa PRIVATE DEE::thinking)
```

El target instalado es `DEE::thinking`; la dependencia de threads se propaga
por el paquete CMake.

## Contrato operacional resumido

- `Runtime` conserva RAW, clock, tick, cola, recibos y fase.
- `observe()` es pasivo; `probe()` y `experience()` son intervenciones.
- Las entradas posteriores preservan el clock del sitio y nunca limpian una
  ocupación para forzar admisión.
- Una composición se construye antes del primer tick en un solo mundo. No hay
  copia de respuestas entre mundos ni cálculo de la respuesta en C++.
- El backend predeterminado sigue siendo denso secuencial. Lazy y paralelo son
  selecciones explícitas y sus contadores/timings no forman parte de la física.
- Snapshot v2 añade metadatos inertes y configuración de ejecución; el lector
  mantiene compatibilidad con un snapshot v1 real de Entrega 01.

## Familias del catálogo

El catálogo disponible cubre transporte/redirección, aprendizaje C6H01,
actualización/transferencia C7H03, historia relativa, integración multicanal,
recurrencia, contexto distribuido y memoria temporal por fase CORE05. Cada
entrada disponible tiene constructor, contrato y prueba. CORE05 se expone como
`temporal_phase_memory.core05.v1`, portado desde los runners y locks primarios
NRH04/NRH06 con oráculos finitos; el antiguo descriptor `.pending` no es alias.

## Lectura de resultados

Consulte:

- `TECHNICAL_REPORT.md` para la ejecución efectivamente realizada;
- `TEST_MATRIX.md` para cobertura y dominio de las pruebas;
- `ORGANIZATION_CATALOG.md` y `API_CONTRACT.md` antes de componer;
- `PENDING.md` para límites y trabajo no implementado;
- `REPRODUCIBILITY.md` para reconstrucción y consumo instalado.

Los nombres aprendizaje, memoria, historia o *thinking* describen aparatos y
contratos operacionales. Esta entrega no adjudica consciencia, AGI, autonomía
ilimitada ni equivalencia universal de todos los estados posibles del kernel.
