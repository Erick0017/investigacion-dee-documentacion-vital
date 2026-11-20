# Interrupción externa después de una salida real

R09 utilizó dos importaciones explícitas del mismo par completo A de MU_MAIN en T16634. No continuó MAIN ni alteró su padre. El trabajador original y el motor permanecieron intactos; sólo una copia diagnóstica del trabajador esperó tres segundos después de escribir y releer el archivo, antes de emitir la confirmación.

Ambos brazos recibieron trabajo público `[3,11]` con retorno nativo omitido y eligieron el trabajador negativo. Escribieron el mismo archivo real de32bytes. CUT terminó exclusivamente el PID de ese trabajador después de observar su recibo de escritura; SHAM dejó concluir la misma espera. Ambos alcanzaron T16645 y tuvieron RAW/clocks finales iguales, pero **no estados causales completos iguales**: sus metadatos, recibos y resultado externo pendiente de confirmación difieren.

En CUT, la solicitud quedó `uncertain`, el propietario pausado y el efecto real conservado. El mismo ID no ejecutó otra acción. Una carga posterior de esa misma copia siguió pausada e incierta, conservando los archivos sin repetición. SHAM terminó `completed` y su carga posterior tampoco repitió el trabajo. Este resultado valida conservación técnica de incertidumbre y ausencia de retry ciego, no recuperación autónoma de contenido ni aprendizaje de una política.

El recálculo independiente comprueba los bytes exportados, recibos, deduplicación, continuidad de campos completos RAW/clocks y resultados. Reconstruye601526uint64 exactos de una base común deduplicada (dos campos N67), sin importar DEE o ejecutar ticks. La extracción no pretende sustituir los snapshots completos conservados localmente.

## Intento previo preservado

R08 terminó antes de ejecutar el trabajo en ambas copias porque el harness confundía el estado `queued` con un terminal. Se detuvo en T16634, sin escritura ni nuevo tick. El primario y su fuente ejecutada se conservan; no se atribuye ese error a DEE ni se presenta como una interrupción realizada. R09 corrigió sólo la espera de transporte y empezó en otras identidades diagnósticas.

Fuentes y primarios: `evidencia/campanas/MENTE_UNIFICADA_Y_FI01/servicio/INTERRUPCION_REAL_R08/` y `INTERRUPCION_REAL_R09/`. Los scripts `exportar_interrupcion.py` y `recalcular_interrupcion.py` realizan extracción pasiva y recálculo, respectivamente. El hook diagnóstico y los hashes del trabajador original/copias están en PREPARACION; el hook no se incorpora al trabajador operativo.
