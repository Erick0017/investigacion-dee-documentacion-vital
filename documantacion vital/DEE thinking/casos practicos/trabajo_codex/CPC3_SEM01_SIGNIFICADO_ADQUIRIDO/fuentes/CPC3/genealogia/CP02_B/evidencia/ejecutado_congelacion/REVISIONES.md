# Versión auxiliar ejecutada en la congelación

Estos archivos conservan la versión del laboratorio usada por `frozen_past_outcome_predictor`, `assisted_finite_followup` y `assisted_reserved_confirmation`. Se reconstruyeron retirando exclusivamente las adiciones posteriores de API de lectura pasiva, factorización del decoder puro y corrección del campo de modalidad.

La versión pública en `src/` añade una lectura pasiva del puerto vivo y permite registrar `DIAGNOSTIC_PHYSICAL_PROBE_IN_DESCENDANT` antes del append. La implementación física, preparación, canales, evolución, objetivos y regla del decoder no cambian. Los primeros logs asistidos conservan un valor por defecto de modalidad incorrecto; su corrección contextual está enumerada en `resultados/METADATA_CORRECTIONS.json` sin reescribir el dato histórico.

La reproducción limpia utiliza la API pública corregida. Los antecedentes son herramientas auxiliares, no una modificación de v27 ni del wheel.

La configuración ejecutada se conserva aquí. El texto de hábitat de la configuración pública aclara después que los ticks objetivo son observaciones de un flujo independiente del pronóstico, no generación de paquetes mediante una predicción. No cambia parámetros, barrera, destinos, muestras, clocks ni transformación: la ley ya estaba determinada por el estado externo y `state_at(tick)`, y el control sin emisión resuelve los mismos resultados.
