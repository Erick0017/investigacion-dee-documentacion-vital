# Reproducción aislada

Los comandos se ejecutan desde la raíz `ENTREGA_02_PREINTEGRACION` y no
modifican el CMake ni el catálogo estable.

## H3

```powershell
New-Item -ItemType Directory -Force candidates\repair_core17\build, `
  candidates\repair_core17\results | Out-Null

$compile = 'call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat" >nul && cl /nologo /std:c++20 /O2 /EHsc /MD /I".\include" candidates\repair_core17\repair_core17_candidate.cpp /Fo:candidates\repair_core17\build\ /link /LIBPATH:".\build\Release\lib" dee_thinking.lib /OUT:candidates\repair_core17\build\repair_core17_candidate.exe'
cmd.exe /d /c $compile

& .\candidates\repair_core17\build\repair_core17_candidate.exe `
  .\candidates\repair_core17\results\repair_results.json
& 'D:\Descargas\ANACONDA MINICONDA\python.exe' -I -B `
  .\candidates\repair_core17\verify_repair_results.py
```

El directorio `build` es temporal y se elimina después de validar. La
biblioteca Release del producto conserva la implementación exacta del kernel.

## H4

```powershell
& 'D:\Descargas\ANACONDA MINICONDA\python.exe' -I -B `
  .\candidates\accessibility\verify_accessibility_contract.py
```

H4 verifica integración semántica y procedencia de evidencia primaria
reducida; no vuelve a ejecutar las campañas históricas ni finge un builder.
