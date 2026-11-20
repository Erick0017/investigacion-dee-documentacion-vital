# MENTE BASAL — OBSERVACIÓN Y ACOPLAMIENTO 003

Este corte conserva el linaje `MENTE-BASAL-001` y documenta trabajo diagnóstico posterior a `CUT_002`. Ningún experimento de este paquete escribió en el mundo principal: las consultas funcionales y el acoplamiento se ejecutaron sobre ramas completas cargadas desde checkpoints inmutables.

## Cortes

- Referencia experimental: `T=193536`, `OBS_003_REF`, 2026-10-05 09:03:57.931 UTC.
- Corte final: `T=214872`, `OBS_003_FINAL`, 2026-10-05 09:39:02.276 UTC.
- Mundo: `MENTE-BASAL-001`.
- Sesión preservada: `SESSION-001-20261005T035032Z`.

## Resultado en una frase

Los lectores móviles localizaron exactamente los portadores 4184, 68 y 40; el contenido 40 produjo una transformación funcional controlada `40 + 7 -> 47`, seguida por un segundo uso `47 + 5 -> 52`; y una rama preparada mostró mediación causal DEMUX `23 -> 24 -> 55 -> 62 -> 62 -> 67`. Esta última composición requirió soportes y un sesgo instalados externamente y, por tanto, no demuestra adquisición ambiental autónoma.

## Reproducción breve

Desde una extracción limpia, con CPython 3.13 x64:

```powershell
& .\tools\reproduce_package.ps1
```

El recorrido carga el checkpoint entregado, valida que la observación sea pasiva y reproduce en Lazy una ventana que contiene el incremento ambiental de `T=193559`. No se conecta al mundo vivo.

Los resultados completos están en `INFORME_INTEGRADO.md`. `HASHES.sha256` cubre todos los archivos de evidencia excepto el propio archivo de hashes y `MANIFEST.json`; este último enumera el contenido y la convención.

