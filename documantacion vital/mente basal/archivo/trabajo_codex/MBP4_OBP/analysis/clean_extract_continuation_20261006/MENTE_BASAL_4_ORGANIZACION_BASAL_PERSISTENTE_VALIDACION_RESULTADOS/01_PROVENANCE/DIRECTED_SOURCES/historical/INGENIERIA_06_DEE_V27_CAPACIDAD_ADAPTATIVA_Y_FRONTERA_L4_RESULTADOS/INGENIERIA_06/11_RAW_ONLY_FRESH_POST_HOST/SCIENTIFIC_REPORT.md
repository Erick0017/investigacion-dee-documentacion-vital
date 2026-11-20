# 11 — Dinámica RAW-only post-HOST_STOP

El gate principal excluyó `clock_a`. En MAIN_S0, FRESH_V1 y FRESH_V2, los efectos temporales RAW de HA=AB y HB=BA fueron distintos y sus respuestas futuras RAW divergieron en `h=32` y `h=64`.

Los intervalos `0→16`, `16→32`, `32→64` y `64→128` pasaron en las tres configuraciones y conservaron diferencia durante dos checkpoints posteriores. Después de `t=4` los mundos principales sólo recibieron ticks y checkpoints.

Adjudicación: `DEE_NATIVE_HISTORY_CONDITIONED_POST_HOST_RAW_DYNAMICS`.

Esto excluye que el resultado anterior fuese producido únicamente por el avance de `clock_a`. No demuestra una contingencia nueva no preinstalada, RW3 formal ni L4.

