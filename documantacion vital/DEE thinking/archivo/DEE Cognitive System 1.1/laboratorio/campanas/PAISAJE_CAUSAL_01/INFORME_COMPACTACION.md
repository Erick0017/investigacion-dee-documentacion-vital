# Compactación y cobertura del análisis

Se transportan los 159 JSON primarios de Paisaje Causal 01 y los payloads exactos de todos los campos registrados, recibos, ejecuciones y revisiones indexadas: 906 miembros, 526,903,956 bytes expandidos. Una compresión sólida XZ sin pérdida los reduce a 3,768,628 bytes. La verificación compara cada payload con su SHA-256 original antes de usarlo. Esta cifra no incluye la documentación, código y mapas que se añaden en el ZIP externo.

No se seleccionaron sólo éxitos ni se recortaron los campos registrados para lograr el límite. Se conserva evidencia de controles, shams, pérdida de funciones, entradas rechazadas, fallos instrumentales y la rama principal adversa. La tabla de 169 ejecuciones no representa 169 individuos independientes: incluye controles, bifurcaciones, continuaciones y reproducciones técnicas. La tabla de usos desglosa observaciones, no personas ni significados.

Las trazas JSONL se descomprimieron y recomprimieron conjuntamente; su contenido descomprimido es idéntico byte por byte. Las cabeceras y representaciones binarias gzip anteriores no viajan. El índice conserva por separado el hash del gzip original y el de su payload. No se anuncia identidad de los contenedores comprimidos, ni se borran los originales locales.

Se excluyen motor, WHL, ZIP históricos, manuales científicos extensos, caches, entornos y la mayoría de snapshots operativos completos. Estos estados no se regeneran ni se sustituyen por arrays en este paquete: permanecen localmente, con ruta, tamaño y hash en las fichas/índices. Los dos preestados nativos incluidos son diagnósticos; no tienen todo el progreso de sesión Python necesario para continuar E1. El análisis no es un respaldo operativo autosuficiente.

Las fuentes relevantes se deduplican por SHA-256, conservando bytes y mapas de revisiones. Las copias actuales legibles de las interfaces afectadas facilitan la revisión. Las fuentes capturadas pero no invocadas no se presentan como funciones probadas. Revisiones fallidas se incluyen como genealogía textual, no para ejecutar su código defectuoso.

La cobertura física es finita. Los campos muestreados y regiones reconstruidas no representan todos los ticks posibles ni todo el corpus CPC. Los enlaces decisivos se apoyan en pre/postestados, agendas admitidas y controles; los mapas balísticos restantes son candidatos. Ninguna exclusión autoriza a sustituir ausencia de observación por una explicación causal.

La verificación externa identifica el tamaño final exacto, su SHA-256, el recálculo independiente desde la extracción y las limitaciones de ese procedimiento. No se guarda dentro del ZIP el hash del propio ZIP.
