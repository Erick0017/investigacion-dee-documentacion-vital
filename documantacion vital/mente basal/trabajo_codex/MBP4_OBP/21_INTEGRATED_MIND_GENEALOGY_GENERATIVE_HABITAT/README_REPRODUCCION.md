# Reproducción técnica de la sección 21

Requisitos: Windows amd64, CPython 3.13 y el wheel incluido en
`01_PROVENANCE/dee_thinking-2.2.0-cp313-cp313-win_amd64.whl`.

Desde la raíz extraída del paquete, crear un entorno limpio e instalar el wheel:

```powershell
py -3.13 -m venv .repro_runtime
& .\.repro_runtime\Scripts\python.exe -I -m pip install .\01_PROVENANCE\dee_thinking-2.2.0-cp313-cp313-win_amd64.whl
```

Ejecutar la campaña reproducible y validar sus checkpoints:

```powershell
& .\.repro_runtime\Scripts\python.exe -I -B .\21_INTEGRATED_MIND_GENEALOGY_GENERATIVE_HABITAT\RUNNER\run_integrated_mind.py
& .\.repro_runtime\Scripts\python.exe -I -B .\21_INTEGRATED_MIND_GENEALOGY_GENERATIVE_HABITAT\RUNNER\validate_section21.py
```

Reanudar una copia aislada del checkpoint MAIN por 49 ticks:

```powershell
& .\.repro_runtime\Scripts\python.exe -I -B .\21_INTEGRATED_MIND_GENEALOGY_GENERATIVE_HABITAT\RUNNER\run_integrated_mind.py `
  --resume .\21_INTEGRATED_MIND_GENEALOGY_GENERATIVE_HABITAT\CHECKPOINTS\MAIN_FINAL.deetsnap `
  --ticks 49 `
  --output .\MAIN_FINAL_PLUS_49_REPRO.deetsnap
```

La ejecución confirmatoria usa un solo Runtime por mundo, no escribe estado después
de T0 y conserva los controles/forks separados de la genealogía MAIN.
