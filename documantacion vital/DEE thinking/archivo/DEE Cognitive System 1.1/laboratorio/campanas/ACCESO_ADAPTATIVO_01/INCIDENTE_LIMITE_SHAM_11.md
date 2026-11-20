# Control sham con crecimiento y límite de ejecución

El control `initialup_feedback_sham_c11` alcanzó el límite supervisado de 300 segundos. Su traza y los snapshots completos de aprendizaje y B se conservaron, pero el proceso terminó antes de guardar el estado final en el registro de vidas. No se considera una respuesta cognitiva incorrecta ni un control selectivo limpio; su evolución tardía no está cubierta por un checkpoint final completo.

Se marca explícitamente la brecha para impedir cargar silenciosamente el antiguo puntero como si fuera el final de esa vida. Se conserva el último snapshot completo identificable como corte anterior, no como reparación retroactiva. Los nuevos trabajadores incorporan un límite cooperativo mediante el propietario de avance; guardan el estado alcanzado y registran el prefijo parcial antes del límite duro. Se comprobará una reproducción representativa sin diferencias físicas bajo ese fraccionamiento.

No se repite el control denso para obtener un resultado favorable. Los controles restantes se ejecutan por separado, conservando este resultado adverso y el detalle local.
