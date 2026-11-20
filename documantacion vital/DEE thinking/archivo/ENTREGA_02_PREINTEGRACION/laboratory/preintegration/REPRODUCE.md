# Reproducción del laboratorio de preintegración

Ejecutar desde este directorio en un entorno MSVC x64 compatible con la
biblioteca heredada:

```powershell
cl /nologo /std:c++20 /O2 /EHsc /MD /I"..\..\include" `
  runners\preintegration_runner.cpp /link `
  /LIBPATH:"..\..\build\Release\lib" dee_thinking.lib `
  /OUT:build\preintegration_runner.exe
& .\build\preintegration_runner.exe .\results_lazy lazy-4
& .\build\preintegration_runner.exe .\results_dense dense-1
```

El ejecutable enlaza `dee_thinking.lib` ya construida. No recompila ni modifica
el kernel, `organization_catalog.cpp` o sus contratos. `config.json` congela
los valores también compilados en el runner. Las corridas Lazy y Dense crean
`results.json` y `telemetry.csv` independientes.

La API de composición admite el primer query en la ventana estable `t=6`. Los
queries posteriores se registran de forma explícita mediante el mismo canal
público `reader.query` del mismo `Runtime`; por eso el resultado se clasifica
como evidencia de laboratorio acoplada, no como ampliación del catálogo.
