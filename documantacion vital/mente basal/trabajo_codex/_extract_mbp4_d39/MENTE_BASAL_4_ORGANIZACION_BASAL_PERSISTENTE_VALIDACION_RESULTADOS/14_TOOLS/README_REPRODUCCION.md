# Reproducción

Entorno comprobado: CPython 3.13, Windows amd64, wheel `dee_thinking` 2.2.0 incluido en `01_PROVENANCE`.

Desde una extracción limpia:

```powershell
py -3.13 -m venv .verify_env
& .\.verify_env\Scripts\python.exe -m pip install --no-index .\01_PROVENANCE\dee_thinking-2.2.0-cp313-cp313-win_amd64.whl
& .\.verify_env\Scripts\python.exe .\14_TOOLS\validate_mbp4.py
```

La validación reconstruye T0→T32, compara el checkpoint MAIN, comprueba `observe` pasivo, continúa desde snapshot con Dense y Lazy y verifica rechazo de un snapshot truncado.

Para inspeccionar un checkpoint sin mutarlo:

```powershell
& .\.verify_env\Scripts\python.exe -c "import dee_thinking as d; r=d.Runtime.load_snapshot(r'.\12_CHECKPOINTS\OBP_FRESH_VALIDATED_T32.deetsnap'); print(r.current_tick, r.dimension, r.metrics().raw_support)"
```

`run_mbp4.py` contiene la campaña completa. Al ejecutarlo de nuevo crea mundos nuevos de reproducción; no modifica los checkpoints entregados ni el padre MBP3.

El checkpoint MAIN oficial de esta campaña es `OBP_FRESH_VALIDATED_T32.deetsnap`. La rama MBP3 es evidencia de integración negativa y no sustituye al MAIN.
