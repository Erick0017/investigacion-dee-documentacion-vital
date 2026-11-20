# Arquitectura causal congelada

`B = <S, P, R, Gamma_in, Gamma_out, E>` se realiza en un único `Runtime`.

- `S`: cuatro escritores semantic=4 y el linaje recurrente R04.
- `P`: dirección A/B de la política móvil R14.
- `R`: normalizadores ambientales que convierten `ACTION0/ACTION1` de nuevo en A/B.
- `Gamma_in`: encuentros con `SENSOR`, `NORMALIZER` y `PENALTY0` preparados en t0.
- `Gamma_out`: portadores `ACTION0/ACTION1` producidos por el kernel.
- `E`: topología toroidal v27 y recursos finitos compartidos.

La cadena central es:

`A/B -> SENSOR -> ACTION0/ACTION1 -> NORMALIZER ambiental -> A/B -> vuelo -> SENSOR`.

Los nombres son metadatos externos. Los registros físicos contienen sólo campos v27.

La recurrencia es source-supported. El retorno acción→política tiene tres usos y no se presenta como autosostenimiento indefinido.
