# Recálculo CF01 sin motor

Desde la raíz extraída, con CPython 3.12 o3.13 y sólo su biblioteca estándar:

`python RECALCULO/recalcular_todo.py --evidence EVIDENCIA_CAUSAL --out SALIDA_RECALCULO`

Verifica hashes de primarios, materializa temporalmente los códigos exactos deduplicados, recalcula inventario, campos RAW, recibos, reservas, controles sociales, panel antiguo, servicio y CAL8. No importa DEE, no genera ticks ni necesita rutas históricas. No ejecuta los códigos nativos archivados; sólo los localiza y verifica.

Las referencias locales comprimidas preservan recálculos anteriores con comprobaciones de snapshots completos. Estos snapshots no viajan: el recálculo exportado no repite ni finge esas comprobaciones. El paquete reducido no permite continuar vidas. El índice identifica todos los snapshots CF01 omitidos y sus hashes.

`materializar_codigo_cf01.py` puede reconstruir las versiones fuente archivadas en un directorio nuevo. R10 es una receta prospectiva NO EJECUTADA; no tiene Runtime, vida ni resultados físicos.
