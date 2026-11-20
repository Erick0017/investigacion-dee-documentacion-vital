# Corte instrumental no certificado

Este staging se conserva incompleto. No contiene PRUEBA_PORTABLE.json ni constituye una entrega validada.

Al ampliar la verificación estática de lectores, el auditor exigió seis puertas a todas las lecturas de selección. Los primarios históricos P09/P11 utilizaban legítimamente un lector fijo de tres puertas z=0 en (13,17,15), (15,17,15), (17,17,15); la revisión posterior añadió tres puertas z=−1. El recálculo se detuvo en `formed_route` con `ValueError: Incomplete, duplicated or unexpected fixed selector gates`.

No se ejecutó Runtime, no se modificó un primario y no se repitió física. Se preservaron el auditor fallido `recalcular_primarios_apd_R06_ERROR_DOMINIO6.py` y el diagnóstico 0ticks de los seis casos históricos afectados. La corrección admite exactamente las geometrías congeladas de tres o seis puertas, no lectores arbitrarios. Un staging posterior identificado debe acreditar el resultado; éste no lo hace.
