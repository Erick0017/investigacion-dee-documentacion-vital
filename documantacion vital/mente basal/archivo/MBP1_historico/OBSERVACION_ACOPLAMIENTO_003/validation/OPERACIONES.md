# Operaciones posteriores

Ejecutar desde la carpeta `mente basal`.

```powershell
# Estado del mundo principal
& .\tools\habitat.ps1 -Action status

# Estado del observador pasivo
& .\OBSERVACION_ACOPLAMIENTO_003\tools\observer.ps1 -Action status

# Recolección futura sin detener; use siempre un ID nuevo
& .\tools\habitat.ps1 -Action collect -RequestId 'OBS_003_NEXT_YYYYMMDDTHHMMSS'

# Recolección y detención explícita del mundo
& .\tools\habitat.ps1 -Action collect-stop -RequestId 'OBS_003_STOP_YYYYMMDDTHHMMSS'

# Detener únicamente el observador pasivo
& .\OBSERVACION_ACOPLAMIENTO_003\tools\observer.ps1 -Action stop
```

No reutilizar `OBS_003_REF` ni `OBS_003_FINAL`: el controlador rechaza o vuelve ambigua la procedencia si se recicla un identificador. Consultar estado o recolectar no renueva el deadline ni el presupuesto de ticks.

