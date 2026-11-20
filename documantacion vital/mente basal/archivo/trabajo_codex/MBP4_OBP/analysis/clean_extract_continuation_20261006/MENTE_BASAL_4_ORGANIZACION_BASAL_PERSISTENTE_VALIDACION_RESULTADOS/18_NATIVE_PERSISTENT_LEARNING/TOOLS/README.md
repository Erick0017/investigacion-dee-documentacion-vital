# Reproducción de la continuación MBP4

`run_mbp4_native_learning.py` reconstruye la campaña desde el checkpoint fresh MBP4 y escribe los locks, controles, atlas y checkpoints de la sección 18.

`validate_mbp4_native_learning.py` carga el checkpoint T0, reproduce 46 ticks mediante Dense y Lazy, compara ambos con `MBP4_NATIVE_MAIN_FINAL.deetsnap`, comprueba que `observe` sea pasivo y verifica el rechazo de un snapshot alterado.

Ambas herramientas requieren CPython 3.13 x64 y el wheel oficial `dee_thinking 2.2.0`. No modifican v27 ni los archivos 00–17 del paquete padre.
