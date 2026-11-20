# Revisión dirigida H1

Fuente de autoridad: `DEE_CORE01_16_MASTER_DOC_WORK/REPRO_PAYLOAD_EXTRACTED/CORE05/DEE_V27_NATIVE_REALITY_DISCOVERY_AND_SYNTHESIS_RESULTADOS`.

Se leyeron completos los runners NRD05 y NRH05, el lock previo al holdout y el
resultado congelado. `run_bank` contiene el constructor, el control de
calibración invertida, el target ausente y el decoder; no fue necesario inferir
geometría desde la narrativa. El SHA-256 del lock recalculado coincide con
`EXPECTED_LOCK_SHA256` y el runner NRH05 es byte-idéntico a la copia `R16QA`.
`native_core.py` (`5f6f3440...a84210f`) sólo adapta el wheel sellado; el candidato
usa directamente la API C++ heredada verificada contra ese wheel.

No se portaron los seeds PCG64 como una nueva fuente de verdad. Los tests
locales usan estados/clocks deterministas y comprueban la relación geométrica;
el resultado congelado conserva la evidencia estadística de cuatro seeds,
frames y tamaños no usados por el test focal.
