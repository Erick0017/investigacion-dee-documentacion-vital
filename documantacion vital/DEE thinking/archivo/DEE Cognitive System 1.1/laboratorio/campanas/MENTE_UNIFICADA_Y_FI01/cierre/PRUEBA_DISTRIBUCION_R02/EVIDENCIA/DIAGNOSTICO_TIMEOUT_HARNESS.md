# Timeout del cliente, no de la evolución DEE

Primera extracción del ZIP a4fe33ff9c84c6eb6af586e4fff3ef024cd6d12a0d9e0142a07230d04b33001d.

La fila `delivery_pending_export` comenzó a15:27:57.697742UTC y terminó a15:28:47.475454UTC:49.777712s. Su estado final fue `completed`, errornull. El cliente del harness esperaba40s y devolvió `waiting_or_processing`; el harness interpretó esto como una comprobación técnica no concluida y solicitó un STOP cortés. El propietario guardó T105605 sin incertidumbre externa. `delivery_chain_finish` seguía `queued`, con `started_utc=null`; no había vuelto a ejecutar la acción pendiente.

El primer comprobante conserva `FAILED_WITH_STATE_PRESERVED`, junto con sus fuentes y salidas. Una revisión instrumental posterior esperó el resultado del mismo FINISH en la misma copia, sin repetir panel inicial, dato, vectorRAW, enseñanza ni BEGIN. La continuación completa y sus tres filas SQLite anteriores figuran en `CONTINUACION_R02_MISMA_COPIA.json`.

La revisión del helper cambió sólo la espera del export técnico a120s y el límite de seguridad de cada propietario a420s, y permitió esa continuación explícita. No se modificaron el códigoS, el motor, el lector, el calendario físico, el criterio del vector125 ni las vidas fuente. El segundo ZIP exacto tiene su propio comprobante y una copia personal distinta; no sustituye al primer resultado negativo.
