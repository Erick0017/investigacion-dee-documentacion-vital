# Ingeniería 05 — NRD06: especificidad de historia

## Veredicto

La identidad de la historia previa cambia reproduciblemente la transformación causada por el mismo probe físico BA.

Clasificación promovida provisionalmente:

`DEE_NATIVE_HISTORY_SPECIFIC_TRANSFORMATION`

El piloto condicional añadió un tercer cambio dependiente de historia y conservó capacidad para producir otra distinción causal bajo un challenge nuevo. Su clasificación provisional es:

`DEE_NATIVE_RECURRENT_HISTORY_CONDITIONED_ADAPTATION`

Esto no promueve RW3 ni L4.

## Diseño

Desde estados iniciales equivalentes se construyeron H0=NO_EVENT, HA=AB y HB=BA. A t*=4 cada estado se clonó en CONTROL y PROBE. El mismo probe BA congelado se aplicó a las tres ramas PROBE. Para cada historia se caracterizó el efecto emparejado PROBE frente a CONTROL mediante raw_a, clock_a, máscaras, fields, C0, C3 y RESPONSE en h=32 y h=64.

## Hallazgo temporal no previsto

En MAIN_S0, inmediatamente después del probe, T_P(H0) y T_P(HB) tenían el mismo efecto XOR público, pero sus efectos sobre los futuros C0/C3 ya eran distintos en h=32 y h=64. T_P(HA) era distinta de ambas. Tras 64 ticks libres, las tres transformaciones eran distintas tanto en su estado público como en sus futuros.

Por tanto, la transformación no puede adjudicarse sólo por el delta inmediato. El contexto histórico puede hacer que un mismo delta público tenga consecuencias experimentales posteriores distintas. Ésta fue una corrección metodológica del criterio de adjudicación, no una repetición de MAIN_S0.

## Retención, ruta y fresh

- MAIN_S0: especificidad en D0 y D64.
- SEPARATED_S0: especificidad en D0 y D64 con la ruta directa del probe disjunta de las rutas usadas por AB y BA previas.
- FRESH_V1 (N=19): especificidad en D0 y D64.
- FRESH_V2 (N=25): especificidad en D0 y D64.

La especificidad no requiere exclusivamente reutilizar la misma carretera física. La escala observada es mixta: el probe comienza con diferencias compactas de 2–7 posiciones RAW, pero la evolución condicionada por historia puede amplificarlas hasta decenas, centenas o miles de posiciones. Esto favorece una interacción entre evento local y estado del paisaje; no identifica todavía un soporte único ni demuestra globalidad universal.

## Piloto F3

El gate fresh autorizó una sola prueba recurrente. Se comparó el mismo tercer probe sobre tres historias acumuladas: G0=NO_EVENT, G1=AB y G2=AB→BA. Las tres transformaciones resultaron distintas bajo el panel congelado. En el mundo G2 continuo se obtuvieron F0→F1→F2→F3 sin copiar soporte RAW ni reconstruir estados adaptativos desde Python.

Después de F3, el challenge nuevo C4 de seis fuentes axiales produjo una nueva distinción inmediata y futuros distintos en h=32 y h=64. Esto demuestra capacidad causal futura en el dominio diagnóstico probado; no demuestra por sí solo competencia adaptativa autónoma.

## Alcance

La evidencia supera `DEE_NATIVE_SEQUENTIAL_REACHABILITY_CHANGE`: no sólo hay una secuencia de cambios, sino que qué historia ocurrió modifica qué hace después la misma experiencia. El piloto muestra una tercera actualización y capacidad para otra distinción.

Siguen faltando para RW3/L4 una función DEE nativa adjudicada por experiencia, contingencias ambientales autónomas, renovación demostrada bajo uso repetido, auditoría de recursos y cierre organización→entorno→nueva experiencia. Ingeniería 05 permanece abierta.

