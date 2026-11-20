# Construcción y estado del corte 4.0

El WHL candidato fue compilado con CPython3.13.11 x64, pybind11 3.1.0,
setuptools81.0.0, wheel0.48.0 y build1.5.0. Se utilizó una sola instancia
Visual Studio18 Community, compilador19.50.35729, MSVC14.50.35717, C++20,
Release/O2. BUILD_PROVENANCE.json conserva rutas y comandos efectivos.

La fuente kernel_v27.cpp conserva SHA-256
`fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31`.
Las nuevas unidades son cognitive.cpp e informative.cpp y sus bindings.
Las herramientas 3.0/3.5 conservadas dentro de source/tools son referencias
históricas; no deben utilizarse para publicar 4.0. Use tools/build40.ps1.

```powershell
.\tools\build40.ps1 -SourcePath (Resolve-Path .\source) -BuildRoot C:\ruta_corta\build40 -ProductRoot (Get-Location) -Stage wheel
.\tools\build40.ps1 -SourcePath (Resolve-Path .\source) -BuildRoot C:\ruta_corta\build40 -ProductRoot (Get-Location) -Stage cpp
```

Requiere Visual Studio/CMake/Ninja externos y las dependencias anteriores.
Los caminos son ejemplos, no directorios que deban borrarse. No se promete
identidad binaria entre rebuilds o compatibilidad ABI C++ entre toolchains.

Los snapshots Runtime1/2 y OrganizationalWorld3.5 conservan su lectura física.
Las sesiones nativas nuevas guardan además su protocolo y metadatos versionados.
Una importación física de CPC3 no migra automáticamente el protocolo Python.
N47, N67 y N127 son perfiles separados, no vistas de un único MAIN universal.

El corte parcial anterior y sus incidencias se conservan en
validation/partial_cut. La continuación autorizada reconstruyó el WHL con las
correcciones Python pendientes, completó los dos módulos sin ejecutar y calificó
BLOQUE I antes de los ensayos nuevos. El binario nativo es el4.0 realmente
compilado y contrastado; no se repitió su física porque sus bytes y fuentes
permanecen idénticos. VALIDATION_REPORT.json registra la calificación final y la
instalación desde una extracción nueva. evidence/UNBUILT_CLOSURE_FIXES conserva
la genealogía de los cambios, ahora integrados y probados según
validation/RESUMPTION_INTEGRATION.json.

La referencia3.5 se incluye únicamente para comparaciones en un venv distinto:
evidence/REFERENCE_PRODUCT_3_5/. No es dependencia ni fallback del producto4.
Las rutas privadas en logs históricos son procedencia, no requisitos de uso.
