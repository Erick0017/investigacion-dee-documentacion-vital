# Integración de build, instalación y snapshots — Entrega 02

## Toolchain Windows

`tools/build_windows.cmd` delega en `tools/build_windows.ps1`. El script localiza
una instalación de Visual Studio mediante `vswhere`, inicializa **esa misma**
instalación y usa su CMake/Ninja integrado. Sólo si esa instalación no los
incluye acepta ambos desde `PATH`. No mezcla rutas absolutas de dos versiones
de Visual Studio ni cambia el `PATH` global.

La compilación normal crea y prueba la biblioteca (13 targets CTest en el CMake
vigente), la instala en
`build/install`, y compila un proyecto consumidor separado que ejecuta:

```cmake
find_package(dee_thinking 2 CONFIG REQUIRED)
target_link_libraries(my_target PRIVATE DEE::thinking)
```

La exportación instalada declara también su dependencia `Threads`.
El consumidor instalado guarda un mundo compuesto y lo recupera mediante
`ComposedWorld::load_snapshot` sin reconstruir el planner, verificando que la
API autocontenida también existe a través del paquete exportado.

El build del consumidor se coloca por defecto en un directorio temporal corto y
único (`dt2-consumer-<id>`). Esto evita tanto reutilizar una caché residual como
el límite de longitud de nombres de objeto de MSVC cuando la raíz extraída ya es
profunda. Puede fijarse explícitamente con
`-ConsumerBuildDirectory`; no se reutiliza la caché del árbol principal.

## Persistencia segura

El escritor v2 serializa primero el snapshot completo en memoria, añade su
checksum y escribe un temporal junto al destino (por tanto, en el mismo
volumen). Cierra y vacía el temporal antes de publicar. En Windows usa
`ReplaceFileW(..., REPLACEFILE_WRITE_THROUGH)` para reemplazar un snapshot
existente y `MoveFileExW(..., MOVEFILE_WRITE_THROUGH)` para el primero. Si la
escritura, el cierre, el flush o el reemplazo falla, elimina solamente el
temporal y conserva el destino anterior. En POSIX usa `rename` dentro del mismo
sistema de archivos.

Esto reduce la ventana de fallo y evita borrar primero la última copia válida;
no promete inmunidad universal frente a fallos de hardware, firmware o pérdida
de energía. La aplicación puede mantener copias versionadas si requiere una
política adicional de recuperación.

## Compatibilidad v1 → v2

El formato conserva el magic `DEETSNP1`. El lector acepta las versiones 1 y 2.
Un fixture real `fixtures/legacy_v1/pending_event_v1.deetsnap`, creado con la
biblioteca liberada de Entrega 01 y con una entrada pendiente, valida estado,
cola, recibo y futuro. Como v1 no contenía metadatos de organización, el lector
no los inventa: `imported_legacy_snapshot()` devuelve `true` y el mapa queda
vacío.

Esa compatibilidad pertenece a `Runtime::load_snapshot`. Un v1 no contiene
receta de composición, por lo que `ComposedWorld::load_snapshot` lo rechaza en
lugar de inferir organizaciones o conexiones. No es una regresión del lector
legacy, sino una separación explícita entre estado Runtime y restore compuesto.

La versión 2 añade al final un mapa ordenado de texto inerte. Las capas de
catálogo/composición pueden conservar allí identificadores, versiones,
contratos, parámetros y selección de ejecución. Esos textos no cargan código,
no contienen punteros y no alteran la física. RAW, clock, tick, canales,
eventos, recibos y fase siguen siendo los datos operativos del runtime.

Los mundos creados por `CompositionPlanner` guardan una receta canónica de
composición además del manifiesto. `ComposedWorld::load_snapshot(path)` usa el
catálogo incorporado; la sobrecarga `load_snapshot(path, catalog)` permite
seleccionar explícitamente el catálogo. Ambas exigen snapshot v2, esquema de
catálogo/receta conocido, versión exacta de cada constructor y coincidencia del
manifiesto y de los canales regenerados. Un snapshot Runtime v2 genérico sigue
siendo válido para `Runtime::load_snapshot`, pero no se presenta como mundo
compuesto si carece de estos metadatos.

`restore_snapshot()` mantiene semántica transaccional: primero carga y valida
una instancia temporal; sólo reemplaza la instancia activa si toda la lectura
termina correctamente.

Los archivos bajo `validation/` documentan una corrida Release limpia de los 13
targets, el consumidor instalado relocable y el benchmark ampliado con coste de
aplicación de evento, restore y total E2E. La evidencia incluye JUnit, logs y
procedencia por hash; la configuración del build por sí sola no se contabiliza
como resultado aprobado.
