# CORE05: memoria temporal por fase

## Procedencia primaria recuperada

El constructor público `temporal_phase_memory.core05.v1` se porta únicamente
desde el payload reproducible preservado, no desde una reconstrucción narrativa:

- `DEE_CORE01_16_MASTER_DOC_WORK/REPRO_PAYLOAD_EXTRACTED/CORE05/DEE_V27_NATIVE_REALITY_DISCOVERY_AND_SYNTHESIS_RESULTADOS/RUNNERS/run_nrh04_distributed_phase_memory_holdout.py`;
- `.../RUNNERS/run_nrh06_toroidal_phase_parity_holdout.py`;
- lock NRH04, SHA-256
  `e3e361808515f0a949d2cf6978edf6b73a4631927927f0ca1557cefeaffcd7a8`;
- lock NRH06, SHA-256
  `569a95b3850f3317ffa570164b07e7700b59d66612b958e665e38e9938b19b58`.

Los hashes calculados sobre los JSON coinciden con los valores fijados por los
runners y con sus archivos `.sha256`. Los runners contienen tanto `prepare`
como `simulate`; por eso el port no necesita inferir el constructor a partir de
un resultado final.

## Geometría y controles portados

La familia base de direcciones es `(1,0,0)`, `(1,1,0)`, `(1,0,1)` y
`(1,1,1)`. Cada fuente es un registro `state=0`, `semantic=4`, situado a
`anchor - distance*direction`. La API admite las seis permutaciones de ejes y
las ocho combinaciones de signo; éstas preservan la transformación exacta del
runner. Los relojes fuente `uint64` se pasan sin pérdida mediante parámetros
`sourceK_clock_high` y `sourceK_clock_low`.

`control_mode` selecciona exactamente:

| Valor | Brazo |
|---:|---|
| 0 | baseline intacto |
| 1 | bloqueo transitorio normal, dirección cero, en la boca elegida |
| 2 | ablación permanente de la fuente elegida |
| 3 | rewire espacial con los cuatro offsets NRH04 transformados |

El footprint, los puertos pasivos `hub/sourceK/mouthK`, los landmarks, los
recursos y la versión `1.0.0` son inspeccionables antes de `build()`. No hay un
canal que mutile el mundo después del tick cero: los brazos son estados iniciales
distintos y declarados.

## Oráculos finitos

`core05_phase_memory` prueba el contrato público, los controles NRH04, la
predicción NRH06 (divergencia de bloqueo frente a ablación en `distance+N` para
N par y ausencia de divergencia hasta `distance+3N` para N impar), persistencia
de `ComposedWorld` y equivalencia RAW+clock entre DenseSequential,
DenseParallel y Lazy. El consumidor instalado también instancia, ejecuta y
restaura el constructor usando sólo `find_package(dee_thinking 2)`.

Estas pruebas no amplían el claim: quedan fuera fondos densos, fuentes
arbitrarias, bordes no toroidales, tiempos infinitos y una interpretación física
del contador de tick. NRH04 está limitado a `distance+12` antes del primer wrap
diseñado; NRH06, a `distance+3N`. La campaña Release integrada fue regenerada
después del port y su target forma parte de los 15 tests archivados en
`validation/`; los logs históricos de 13 tests no se usan para validar este
constructor.
