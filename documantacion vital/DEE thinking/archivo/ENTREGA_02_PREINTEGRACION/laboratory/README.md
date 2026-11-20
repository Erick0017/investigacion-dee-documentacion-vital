# Laboratorio de cierre — Entrega 02

Este directorio contiene experimentos pequeños, exploratorios y no exportados
al catálogo estable. No modifica el kernel, la API pública, el `CMakeLists.txt`
principal ni los scripts de empaquetado.

Modalidades:

- **NATIVA**: todos los portadores y selectores existen en `t=0`; después sólo
  se llama al kernel y se observa.
- **ACOPLADA**: el mismo mundo continúa sin reset, pero el host introduce una
  consulta posterior explícita. Esta modalidad mide admisión y transformación
  bajo una interfaz externa; no se describe como cierre autónomo.

Los resultados primarios Lazy-4 se generan en `results/`; la confirmación
DenseSequential-1, en `results_dense/`. Los objetos físicos estructurados
coinciden exactamente al ignorar únicamente backend y duración; la telemetría
conserva los contadores técnicos propios de cada agenda. Las conclusiones
descriptivas están en `docs/LABORATORY_REPORT.md`.
