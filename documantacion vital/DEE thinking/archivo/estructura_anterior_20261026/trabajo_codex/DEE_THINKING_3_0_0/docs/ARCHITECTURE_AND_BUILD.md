# Arquitectura y reconstrucción — DEE thinking 2.2.0

## Capas del producto

```text
aplicación C++                 aplicación Python
       |                              |
headers instalados              dee_thinking/__init__.py
       |                              |
       +--------- API C++ <--- extensión nativa pybind11
                       |
     runtime + catálogo + composición + protocolos H1-H4/F1/F2
                       |
      kernel_v27.cpp: transición v27 única e inmutable
                       |
        RAW A/B + clock A/B, Dense/Lazy/Parallel
```

No existe un motor Python alternativo. Los ejemplos, protocolos y binding
delegan la evolución al mismo núcleo C++ del producto. `dee_universe_v27` es
una referencia externa de validación, no una importación de runtime.

## Mapa de fuente

| Ruta | Responsabilidad |
|---|---|
| `include/dee_thinking/kernel_v27.hpp`, `src/kernel_v27.cpp` | packing, decoding y transición v27 con tres agendas técnicas |
| `include/dee_thinking/runtime.hpp`, `src/runtime.cpp` | cuatro buffers, eventos, recibos, observación, fork y snapshots |
| `include/dee_thinking/organization_catalog.hpp`, `src/organization_catalog.cpp` | descriptores, contratos, parámetros, puertos y construcción inicial |
| `include/dee_thinking/composition.hpp`, `src/composition.cpp` | composición de organizaciones en un solo `Runtime` y receta autocontenida |
| `include/dee_thinking/organizations.hpp`, `src/organizations.cpp` | constructores de referencia heredados |
| `include/dee_thinking/integrated_protocols.hpp`, `src/integrated_protocols.cpp` | API pública H1/H2/H3/H4/F1/F2 |
| `bindings/dee_thinking_pybind.cpp` | traducción pybind11 de tipos y operaciones C++ reales |
| `python/dee_thinking/__init__.py` | interfaz Python y versión, sin motor físico alternativo |
| `pyproject.toml` | construcción del wheel nativo |
| `tests/` | regresiones C++, instalación, wheel y paridad |
| `examples/` | consumidores C++ y Python de interfaces públicas |

`setup.py` implementa sólo el adaptador de build `CMakeExtension`: invoca el
CMake raíz con `DEE_THINKING_BUILD_PYTHON=ON`. El target
`dee_thinking_python` enlaza `DEE::thinking`, de modo que C++ y wheel reciben la
misma lista de fuentes del target nativo; no existe una lista paralela en
setuptools ni un enlace a una biblioteca histórica por ruta absoluta. Las rutas
deben volver a verificarse antes del freeze contra el wheel realmente construido.

## Flujo de una experiencia

1. Un constructor o protocolo fija geometría, campos, recursos, fase y puertos.
2. `Runtime::experience`/`experience_batch` valida sintaxis y agenda un evento;
   un recibo `Scheduled` todavía no implica admisión física.
3. En la frontera efectiva se comprueba RAW vacío, conflictos y atomicidad.
   Una entrada admitida conserva el clock completo del sitio.
4. `advance` ejecuta una transición v27: lee A, escribe B, aplica DEMUX y copia
   B a A sin swap extra.
5. `observe` devuelve RAW, clock y decodificación sin avanzar ni aplicar cola.
   `probe` es una intervención registrada y requiere permiso del canal.
6. Snapshots conservan estado físico, tick, cola, recibos, canales, backend y
   metadatos/receta inertes; nunca serializan callbacks o direcciones RAM.

Los protocolos integrados añaden un registro propio de descriptores porque no
todos son organizaciones: H4 es un analizador puro y H3 incluye una intervención
diagnóstica opt-in. H1/H2/H3/F1/F2 ofrecen funciones de checkpoint/reanudación
que reutilizan el formato seguro de `Runtime` y metadatos de protocolo
versionados; su validación exige futuro exacto frente a la trayectoria continua.

## Decisiones críticas

- **Cuatro buffers.** Conservan el contrato canónico de transición y evitan
  aliasing entre estado fuente/destino.
- **Clock uint64 completo.** La fase forma parte de `Q0=(raw, clock)`; no se
  comprime ni pasa por `float` en Python.
- **Observe/probe separados.** La lectura pasiva no puede confundirse con una
  intervención que modifica el mundo.
- **Admisión en frontera.** Programar una entrada no garantiza que el sitio siga
  disponible cuando llegue su tick.
- **Versionado de constructores.** Una receta restaura el mismo contrato, no
  otro constructor con nombre parecido.
- **Modalidad visible.** H3 es acoplado/diagnóstico; H4 es análisis; F1 y F2 son
  protocolos finitos con preparación explícita.
- **C++/Python separados por interfaz, no por física.** La biblioteca puede
  usarse sin Python; el wheel enlaza el mismo source C++.

## Versiones de construcción del corte

- Producto: `2.2.0`.
- Kernel: v27, `P_KERNEL=19665`, cap 19664.
- Lenguaje nativo: C++20.
- Plataforma inicial del wheel: Windows amd64.
- Python inicial: CPython 3.13, tags reales `cp313-cp313-win_amd64`.
- Binding usado: pybind11 3.1.0.
- Backend de wheel: setuptools + pybind11 mediante `pyproject.toml` y el target
  CMake raíz.

No se declara `abi3`, `py3-none-any`, free-threaded, subintérpretes, Linux o
macOS sin una implementación y validación separadas.

## Reconstrucción C++

Los comandos exactos y versiones efectivamente ejecutados deben conservarse en
`validation/`. El recorrido esperado desde una extracción limpia es:

```powershell
cmake -S . -B <build-corto> -G Ninja -DCMAKE_BUILD_TYPE=Release `
  -DDEE_THINKING_BUILD_TESTS=ON -DDEE_THINKING_BUILD_EXAMPLES=ON
cmake --build <build-corto> --config Release
ctest --test-dir <build-corto> -C Release --output-on-failure
cmake --install <build-corto> --config Release --prefix <install-limpio>
```

Después, el consumidor independiente debe configurar contra
`<install-limpio>/lib/cmake/dee_thinking`; no puede incluir `.cpp` ni buscar
headers/libs en el árbol fuente.

## Construcción e instalación del wheel

El wheel debe construirse desde `pyproject.toml` y el mismo conjunto de
`src/*.cpp`. El recorrido de aceptación requiere:

1. construir `dee_thinking-2.2.0-cp313-cp313-win_amd64.whl`;
2. crear un entorno o target limpio sin paquetes de usuario;
3. instalar el archivo wheel, no `-e` ni el source;
4. cambiar a un directorio externo al proyecto;
5. importar `dee_thinking`, comprobar `__version__ == "2.2.0"` y verificar la
   ruta del módulo nativo;
6. ejecutar Runtime, snapshot/fork/catálogo y H1–H4/F1/F2;
7. confirmar que `dee_universe_v27` no se importa ni se necesita;
8. ejecutar cruces C++→Python y Python→C++ de snapshot.

El cruce genérico de `Runtime` con una entrada pendiente prueba compatibilidad
del formato base, pero no sustituye una reanudación en proceso nuevo de la fase
propia de H1/H2/H3/F1/F2. La aceptación conserva ambos niveles como pruebas
distintas.

## Concurrencia del binding

El binding 2.2.0 conserva el GIL durante `Runtime.advance` y `run_until`. Esta
decisión evita que otra llamada Python ejecute simultáneamente
`experience`/`observe`/`restore` sobre la misma instancia; no convierte el
`Runtime` C++ en thread-safe fuera de ese contrato. `DenseParallel` mantiene su
paralelismo interno C++, pero dos mundos invocados desde hilos Python no se
prometen concurrentes en esta versión. La matriz debe comprobar esta semántica
y no anunciar liberación de GIL, subintérpretes o free-threaded.

## Estado de reconstrucción

El build limpio 2.2.0 y sus 17 tests C++, el consumidor instalado, el wheel
CPython 3.13, su instalación no editable, 11 pruebas Python y la persistencia
cruzada genérica/H1/H2/H3/F1/F2 fueron ejecutados favorablemente tras corregir
la captura de metadata funcional H2-overlap en t14. Esa corrección pertenece al
wrapper de checkpoint; RAW, clock, kernel y trayectoria no se modificaron.

El ZIP candidato se extrajo en `tests/x22f`: se reconstruyeron 49 targets, el
panel limpio CTest aprobó 8/8 en 9,78 s, el install tree limpio sirvió a un
consumidor externo por `find_package` y el source extraído reconstruyó el wheel
CPython 3.13 en `tests/xwheel22f`. El estado técnico es `VERIFIED`; consulte
`TEST_MATRIX_DEFINITIVE.md` y `validation/FINAL_VALIDATION_SUMMARY.json`.

## Empaquetado definitivo

`tools/package_definitive.py` y `tools/verify_definitive_delivery.py` son
utilidades nuevas; no importan los empaquetadores legacy fijados a
preintegración. El primero construye el ZIP con su nombre final dentro de una
ruta temporal, genera `MANIFEST.json` y `HASHES.sha256`, llama al verificador y
sólo entonces sustituye atómicamente el destino solicitado. El verificador
exige el wheel externo y el interno byte-idénticos, metadata 2.2.0, los dos
hashes de procedencia del kernel con significado distinto, install tree,
binarios ejecutados y ausencia de caches, egg-info, venvs o ZIP históricos.
El stage conserva también `benchmarks/backend_benchmark.cpp`: el CMake público
y `build_definitive.ps1` habilitan ese target, por lo que omitir su fuente
rompería una reconstrucción limpia aunque el benchmark no sea evidencia
científica adicional.

La ejecución final debe producir
`validation/FINAL_VALIDATION_SUMMARY.json` con schema
`dee-thinking-definitive-validation-v1`. Sus seis checks separan CTest nativo,
consumidor instalado, instalación limpia del wheel, API Python, persistencia
cruzada y reconstrucción desde extracción. `VERIFIED` requiere los seis en
`PASS`; el corte entregado queda `VERIFIED` porque los seis fueron ejecutados.
