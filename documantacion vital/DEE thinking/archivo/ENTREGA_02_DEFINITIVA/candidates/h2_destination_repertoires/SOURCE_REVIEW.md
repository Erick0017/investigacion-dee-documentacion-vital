# Revisión dirigida H2

Fuente de autoridad: `DEE_CORE01_16_MASTER_DOC_WORK/REPRO_PAYLOAD_EXTRACTED/CORE07`.

Se leyeron completos el runner C7H02, su lock y su resultado. El runner contiene
los constructores `separated_panel` y `overlap_panel`, la inyección posterior,
los controles off-fiber y las identidades globales. El SHA-256 del lock
recalculado coincide con `EXPECTED_LOCK_SHA256`; el runner es byte-idéntico a
la copia `R16QA`. `core07_common.py` tiene SHA-256
`ce72b556...eced68` y carga el mismo kernel v27 sellado.

El port conserva dos APIs porque la evidencia distingue capacidad en fibras
separadas de pérdida de identidad al compartir destino. El test focal cubre
K=3 y K=7, no reejecuta el panel congelado K=40; ese límite inferior permanece
respaldado sólo por el resultado primario hash-pinned.
