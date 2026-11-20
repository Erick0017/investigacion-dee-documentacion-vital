# H1 — retardo relativo → posición

ID candidato: `delay_position_bank.core05.nrh05.candidate.v1`  
Versión: `0.1.1-candidate`

## Constructor respaldado

El constructor reproduce `run_bank`: para cada label `j`, instala una fibra
probe que llega al hub en `L+j` y una fibra target que llega en `L+delta`.
Exactamente el hub `j=delta` recibe ambas propuestas y su identidad espacial es
la medida `m_B(A)`. El resultado es categórico en ticks del kernel, no tiempo
continuo ni segundos físicos.

La API exige labels únicos, fondo vacío, direcciones y separación declaradas.
Expone tres brazos iniciales: `Native`, `ReversedCalibration` y `TargetAbsent`.
La observación busca exclusivamente la firma congelada: `state=1`,
`semantic=1`, dirección `sign(target+probe)` y `s_reg` reducido con cap 19664.

## Dominio y límites

El lock NRH05 cubre labels `[-5,5]`, `L=12`, cuatro frames ortogonales,
N=59/63/67/71, estados positivos, clocks uint64 y regímenes saturado/no
saturado. Este candidato mantiene un constructor parametrizado sólo dentro de
guardas explícitas: direcciones cardinales ortogonales, cargas sin saturación,
trayectorias positivas y ausencia conservadora de auto-wrap. Su test local
focal usa un frame de holdout, once clases, controles, dos rechazos de dominio y equivalencia
DenseSequential/Lazy. No afirma metrología universal, fondo denso, canales
solapados ni interpolación continua.

## Decisión de integración

Permanece aislado porque un banco de once canales consume 22 portadores y una
región amplia; antes de promoción deben fijarse `ResourceBudget`, puertos,
serialización de labels y política de colisión con otras organizaciones.
