# Coordenadas del registro global de R07

La física, los sitios enviados a observe(), los cortes y los lectores fijos
usaron coordenadas correctas. La función global_frame convirtió el índice
lineal con X y Z intercambiados. El kernel indexa ((x*N)+y)*N+z.

No se modifican los bytes primarios. Para cada registro global, la coordenada
correcta es [site[2],site[1],site[0]]. El índice exacto se reconstruye como
((site[2]*67)+site[1])*67+site[0]. Los uint64 RAW/clocks guardados no cambian.
Reconstituir el array RAW con ceros en las posiciones omitidas debe producir
el RAW_sha256 del frame. Los clocks de sitios RAW0 sólo tienen compromiso
global SHA; los snapshots completos permanecen localmente.

La copia composicion_reserva_r07_ejecutado_xyz_invertido.py conserva el código
ejecutado. El recálculo aplica la corrección explícita, sin nuevos ticks. No
se presenta el error de etiquetado del instrumento como un fallo del ente.
