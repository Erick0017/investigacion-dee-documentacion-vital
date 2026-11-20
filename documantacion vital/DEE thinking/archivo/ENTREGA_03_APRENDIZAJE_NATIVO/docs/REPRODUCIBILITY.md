# Reproducción

## Requisitos

- Windows x64;
- Visual Studio 2026 / MSVC 19.50;
- CMake y Ninja;
- el árbol `baseline/dee_thinking_2_2_0` incluido.

El runner enlaza la biblioteca nativa 2.2.0 incluida. Python no participa en la
evolución; `tools/validate_results.py` sólo verifica tablas ya producidas.

## Construcción

Desde una extracción limpia, active el entorno MSVC x64 y ejecute:

```powershell
cmake -S . -B build -G Ninja `
  -DCMAKE_BUILD_TYPE=Release `
  -DCMAKE_PREFIX_PATH="$PWD\baseline\dee_thinking_2_2_0"
cmake --build build --config Release
```

## Panel principal

```powershell
.\build\dee_entrega03_native_learning.exe --baseline .\reproduced\baseline.txt
.\build\dee_entrega03_native_learning.exe --panel .\reproduced\panel
```

`--panel-lazy` reproduce el panel sin la confirmación densa/paralela.

## Estado aprendido y proceso nuevo

El checkpoint entregado se encuentra en
`checkpoints/learned_dose4_t40.deetsnap`. Para repetir la consulta reservada en
otro proceso:

```powershell
.\build\dee_entrega03_native_learning.exe --resume `
  .\checkpoints\learned_dose4_t40.deetsnap `
  .\checkpoints\learned_dose4_holdout_reference_t60.deetsnap `
  .\reproduced\resume.csv `
  .\reproduced\resumed_t60.deetsnap
```

La salida esperada es `holdout_use1=4185`, `holdout_use2=4189`,
`raw_exact=1` y `clock_exact=1`.

## Verificación de resultados

```powershell
python -I .\tools\validate_results.py `
  --root . `
  --output .\reproduced\VALIDATION_SUMMARY.json
```

El panel completo ejecutado se conserva en `results/panel_final`. Los pilotos
`panel_v2` y `panel_v3` documentan los reajustes de mecanismo y no deben contarse
como confirmaciones independientes.

