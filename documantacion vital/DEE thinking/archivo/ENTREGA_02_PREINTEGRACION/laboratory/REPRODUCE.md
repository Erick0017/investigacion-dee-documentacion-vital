# Reproducción

Desde un `Developer PowerShell for VS 2026`/entorno MSVC compatible con el
binario de Entrega 02, situado en `laboratory`:

```powershell
New-Item -ItemType Directory -Force build | Out-Null
cl /nologo /std:c++20 /O2 /EHsc /MD /I"..\include" `
  runners\laboratory_runner.cpp /link `
  /LIBPATH:"..\build\Release\lib" dee_thinking.lib `
  /OUT:build\laboratory_runner.exe
& .\build\laboratory_runner.exe .\results lazy-4
& .\build\laboratory_runner.exe .\results_dense dense-1
```

El runner usa únicamente cabeceras públicas y la biblioteca compilada de la
Entrega 02. No recompila ni sustituye el kernel. El brazo NATIVA no realiza
escrituras después de `t=0`; el brazo ACOPLADA declara la segunda consulta del
host en `t=40`. Cada corrida completa dura segundos y escribe su par JSON/CSV
al final; no se presenta ese guardado como checkpoint caso-a-caso.
