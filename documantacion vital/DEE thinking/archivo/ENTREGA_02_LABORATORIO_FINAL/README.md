# DEE thinking — Laboratorio final focalizado de Entrega 02

Paquete experimental aislado. No modifica el kernel DEE v27, la Entrega 02
estable, la preintegración ni el catálogo público.

## Contenido

- `runners/final_laboratory_runner.cpp`: runner C++ realmente ejecutado.
- `bin/dee_final_laboratory.exe`: binario Release ejecutado.
- `baseline/`: headers, biblioteca estática y copia de consulta del kernel
  procedentes de la preintegración identificada en `validation/BASELINE_IDENTITY.json`.
- `results/final_run/`: resultados, telemetría y checkpoints decisivos.
- `results/exploratory/`: resultados mínimos de los pilotos que localizaron la
  colisión bloqueada y verificaron la ruta corregida.
- `config/CAMPAIGN_CONFIG.json`: aparato, brazos y observadores finales.
- `docs/SCIENTIFIC_REPORT.md`: informe científico-técnico integrado.
- `docs/INTEGRATION_PROPOSAL.md`: decisiones que quedan para revisión.
- `tools/reproduce.ps1`: construcción y repetición nativa sin Python.
- `tools/verify_results.ps1`: comprobación de relaciones técnicas congeladas.

El resultado nuevo permanece en laboratorio. Ningún candidato fue añadido al
catálogo estable y no se inició Entrega 03.

## Reproducción

En PowerShell, desde una extracción limpia:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\reproduce.ps1
powershell -ExecutionPolicy Bypass -File .\tools\verify_results.ps1 `
  -ResultPath .\reproduced_results\results.json
```

La reproducción completa ejecuta los brazos Lazy y las cuatro confirmaciones
DenseParallel. El binario usa exclusivamente la biblioteca C++ incluida; Python
no participa en la evolución.

