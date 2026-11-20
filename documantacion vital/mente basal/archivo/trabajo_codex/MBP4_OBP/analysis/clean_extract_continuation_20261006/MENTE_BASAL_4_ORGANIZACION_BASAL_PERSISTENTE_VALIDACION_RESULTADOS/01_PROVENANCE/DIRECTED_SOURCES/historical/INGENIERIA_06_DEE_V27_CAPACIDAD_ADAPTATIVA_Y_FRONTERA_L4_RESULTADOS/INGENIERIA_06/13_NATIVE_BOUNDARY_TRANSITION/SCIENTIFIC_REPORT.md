# 13 — Gate de frontera causal nativa

Se buscó primero en evidencia ya ejecutada, sin nueva física ni barrido. El criterio se congeló antes del análisis:

- C0 y C3 debían pertenecer exactamente a la misma clase RAW;
- C4 debía producir una clase RAW distinta en el mismo estado y horizonte.

Se evaluaron 126 combinaciones de configuración, checkpoint, historia y horizonte. Hubo diez intervalos H0 con RAW principal estable, pero cero casos `C0 == C3` y `C4 != C0`.

Adjudicación: `NO_PREVALIDATED_NEAR_BOUNDARY_CANDIDATE_IN_TESTED_PANEL`.

No se introdujo un umbral post hoc, no se construyeron Q1/Q2/Q3 y no se ejecutó mediación. Método C queda inconcluso, no negativo en general.

