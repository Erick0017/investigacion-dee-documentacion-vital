# 10 — Oportunidades causales equivalentes

## Pregunta

¿Las historias HA=AB y HB=BA rompen de manera distinta la equivalencia entre tres instancias P1/P2/P3 presentes desde `t0`, sin intervención posterior al `HOST_STOP`?

## Resultado bruto

P1/P2/P3 conservaron el mismo fingerprint rotacional en H0, HA y HB en `+0,+16,+32,+64,+128,+256,+391`. No hubo ventana positiva ni patrón HA/HB diferente.

## Control de sensibilidad

Las comparaciones FULL frente a OMIT_Pi conservaron una diferencia pública inmediata, pero esa diferencia fue cero en C0, C6 y RESPONSE a `h=32` y `h=64` en todos los checkpoints. Por ello las instancias probadas no fueron future-relevant bajo el panel congelado.

## Adjudicación científica

El resultado ejecutado queda preservado con su etiqueta instrumental `NO_HISTORY_DRIVEN_EQUIVALENCE_BREAKING`, pero la interpretación promovible es más estrecha:

`NO_EQUIVALENCE_BREAK_OBSERVED_WITH_INSENSITIVE_OPPORTUNITY_PANEL`.

El control geométrico de equivalencia pasó, pero el control de relevancia futura no. El aparato no demuestra ruptura histórica y tampoco autoriza una negación general de esa posibilidad. No se abre la validación condicional 11.

No apareció una contingencia no preinstalada. RW3 formal: no. L4: no.

