# PI02 etapa B — interferencia de admisión y recuperación de función

Se recalcularon pasivamente 15 solicitudes FI completadas y se conservó el fallo técnico del primer sham. No se ejecutó Native ni se modificó una vida. El recálculo desde el núcleo exportado coincide con el local y tiene cero inconsistencias.

| Trayectoria | Casos / q+4 válidas | Signos correctos | Solicitadas / aplicadas / rechazadas | Salidasq+4 |
|---|---:|---:|---:|---|
| SYNC | 3 / 3 | 3 / 3 | 528 / 528 / 0 | [0, 1, -1] |
| ASYNC | 3 / 3 | 3 / 3 | 528 / 528 / 0 | [0, 1, -1] |
| ACTIVE | 3 / 3 | 1 / 3 | 531 / 519 / 12 | [-1, -1, -1] |
| GUARDED | 3 / 3 | 3 / 3 | 528 / 528 / 0 | [0, 1, -1] |
| MAIN_RECOVERY | 3 / 3 | 2 / 3 | 529 / 525 / 4 | [-1, 1, 0] |

SYNC/ASYNC/GUARDED recibieron (6,6), (12,4), (3,11). MAIN recibió (12,4)con competencia, después (12,4)sin ella y (6,6)sin ella. Las consultas de una trayectoria son usos sucesivos, no réplicas independientes.

La solicitud perturbadora carga 7 fue rechazada por conflicto en cada caso ACTIVE. El perjuicio demostrado ocurre en la admisión simultánea del conjunto: también se rechazaron entradas del marco FI. No se atribuye el cambio a un portador 7 que hubiese atravesado el mundo ni a daño subjetivo. La guarda fija evita presentar la solicitud; no fue aprendida por DEE.

En MAIN se pasó de −1 erróneo a +1 correcto para los mismos operandos después de retirar la competencia y luego se produjo 0 material para (6,6), sin restaurar ni reenseñar. Es recuperación del funcionamiento de comparación, no demostración de que se recuperó un recuerdo histórico borrado. El estado alcanza T740937 y retiene la misma genealogía.

El lector fijoq+4se mantiene distinto del lector q+6: para (6,6)el primero tiene cero material y el segundo NULL. Cambiar lectores después de observar resultados no forma parte del protocolo.

El sham original falló antes de avanzar ticks por el contrato inmutable de la fuente 600001 frente al helper que intentaba redeclarar state=1. El snapshot fallido T740343 se preservó: su hash fue comprobado y el parser documental encontró 176 eventos pendientes. Su RAW/clocks no avanzaron, pero la agenda completa no es idéntica al estado anterior; no se reintenta silenciosamente ni se puntúa como sham realizado. La rama corregida futura no se suma a estos datos.

La equivalencia global de los tres controles SYNC/ASYNC ya se verificó localmente sobre snapshots. En el paquete se incluye ese testimonio con localizadores; el recálculo portátil de B verifica directamente los primarios, codec, RAW, relojes, lector, fases y recibos, y no simula acceso a los snapshots locales omitidos.

No se acredita aquí regulación aprendida, anticipación, iniciativa nueva, actuación útil externa ni adopción. Es un resultado instrumental y una delimitación causal de acceso que permite evaluar después esos mecanismos.

Fuentes: `RECALCULO_PI02_B.json`, `control/COMPARACION_FI_ASYNC_R03.json`, `ensayos/PI02_R03_FI_*.json`, `ensayos/PI02_R03_MAIN_ACCESS_*.json`; rutas y hashes exactos en el JSON compañero.
