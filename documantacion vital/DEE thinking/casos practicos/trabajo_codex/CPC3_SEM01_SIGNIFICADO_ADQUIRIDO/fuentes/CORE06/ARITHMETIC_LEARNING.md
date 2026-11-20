# Aprendizaje aritmético

## Representación congelada

Para ejemplos `x -> y` se fijó antes del holdout:

- cue: `s_reg = B-x`;
- teacher: `s_reg = y`;
- memoria resultante: `B-x+y = B+delta`, con `delta=y-x`;
- consulta no vista: `s_reg=n`;
- readout: `s_reg_out-B = n+delta`.

`B` evita valores negativos y todos los casos se mantuvieron bajo el cap 19664. El encoder contiene `x`, `y` o `n` en sus papeles declarados; no contiene la respuesta del holdout `n+delta`.

## Resultado de regla

Cuatro learners entrenados con ejemplos de una traslación fija generalizaron a valores `n` no presentes en training. En nuevos tamaños, marcos y deltas se obtuvieron 24/24 mundos y 96/96 canales exactos. El subconjunto `delta=1` confirmó SUCCESSOR en 6/6.

El aprendizaje no es lookup literal: las consultas fueron valores no usados como `x` de entrenamiento, la misma `delta` se aplicó a cuatro canales y los controles barajados/ablacionados no acertaron.

## Composición

Dos memorias separadas, `d1` y `d2`, fueron interrogadas secuencialmente. El output fue:

`n -> n+d1 -> n+d1+d2`.

Los dos órdenes dieron 15/15 exactos; 270 controles que eliminaban o corrompían cualquiera de las memorias fallaron la regla completa.

## Frontera de suma

La prueba M2/M3 no mostró aprendizaje adicional. Una colisión no entrenada con cargas de los dos operandos implementa la suma capada directamente:

`s_out=min(s_a+s_b,19664)`.

Resolvió 16/16 combinaciones de dos bits y 64/64 de tres bits, incluidos 44 casos con carry. Por MDL y control causal, la explicación es primitive reducer, no training. Esta rama queda como `UNTRAINED_INTRINSIC_ADDITION_REDUCER_WINS_SIMPLER_MODEL`.

## Dictamen

`NATIVE_ARITHMETIC_LEARNING_CONFIRMED_WITHIN_TRANSLATION_DOMAIN` es válido y literal. Las etiquetas sin sufijo de dominio, multiplicación, carry aprendido y aritmética universal permanecen no demostradas.
