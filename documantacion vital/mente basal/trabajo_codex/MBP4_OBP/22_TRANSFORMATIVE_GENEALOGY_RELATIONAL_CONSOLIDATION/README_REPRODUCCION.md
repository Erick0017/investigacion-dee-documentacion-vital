# Reproducción técnica de la sección 22

Esta sección usa exclusivamente DEE thinking 2.2.0 y el kernel v27 congelado.
El tracker es un observador externo: reconstruye transiciones sobre copias y no
escribe identificadores en RAW o clock. La composición relacional se prepara
antes de T0; después sólo se ejecutan `advance`, observación pasiva y guardado.

Desde una extracción del ZIP cuyo directorio envolvente sea `<PACKAGE_ROOT>`:

```powershell
python 22_TRANSFORMATIVE_GENEALOGY_RELATIONAL_CONSOLIDATION/RUNNER/run_consolidation.py `
  --package-root <PACKAGE_ROOT> --validate-only
```

Para repetir la ciencia en una copia del paquete padre (nunca sobre el ZIP
oficial ya ampliado), ejecute el mismo runner sólo con `--package-root`. Los
controles diagnósticos están identificados en telemetría y jamás se fusionan en
MAIN. `EXPERIMENT_CONFIG.json` fija origen, horizontes, reservas y cortes.
