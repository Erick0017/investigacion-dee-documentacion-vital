# APD04 — corrección científica de denominadores A/B/C, R07

Este suplemento N0 corrige los totales de entradas físicas descritos como completos en los borradores R02–R05 y en los primeros recálculos A/B/C. No modifica sus bytes ni sus primarios. R06 sigue siendo el suplemento de actuador R02 y reserva parcial; este archivo debe leerse junto a él. Ninguno es el cierre de la campaña.

## Recuento completo por ID Native, no por forma del envoltorio

| Rama | Oportunidades completas | Envoltorio port | Envoltorio channel | Solicitadas totales | Aplicadas | Rechazadas por ocupación |
|---|---:|---:|---:|---:|---:|---:|
|A |12|204|42|246|246|0|
|B |12|186|90|276|276|0|
|C |6|102|21|123|100|23|

Los valores204/186/102 de las versiones anteriores son subconjuntos `port`, no la dosis completa. Todos los recibos ahora se unifican por ID exacto en ambos esquemas y se concilian contra el delta del snapshot Native completo histórico. Los90171 recibos del padre permanecen intactos. Los cortes comprometidos no tienen entradas Native pendientes. Esta extracción es retrospectiva y no añadió ticks, no reenvió entradas y no cambió el protocolo.

La comparación A/C de las primeras seis oportunidades conserva123 especificaciones por rama, no102. Siguen existiendo sólo tres cambios de payload entre sus especificaciones solicitadas. Los21 registros `channel` adicionales por rama no cambian ese conjunto de tres diferencias. Los calendarios, RAW, clocks, salidas, utilidad, densificación y23 rechazos ya descritos no se alteran por esta corrección de contabilidad.

En C, las seis oportunidades completas suman100 aplicadas y23 rechazadas de123. Las cuatro oportunidades solicitadas dentro de la petición C5 sin resultado no se agregan como cuatro rechazos o fracasos: su inicio individual sigue sin establecerse. Tampoco se agregan oportunidades de peticiones que nunca fueron enviadas. Es incorrecto presentar los102 registros `port` como todos los estímulos que recibió C.

La corrección fortalece la trazabilidad de dosis; no demuestra atención útil. A/B siguen con12 respuestas válidas y0 útiles; C mantiene3 USE y3 NULL,0 útiles en seis oportunidades completas. Las diferencias de dosis e historia entre A/B/C siguen impidiendo tratarlos como un factorial de dosis perfectamente equiparadas.

## Evidencia que debe viajar

Componente: `evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/ATENCION_ABC_DOSIS_COMPLETA_N0_R02/`.

Contiene `RECALCULO_ABC_Y_CONCILIACION_FULL_R02.json`, `auditar_dosis_abc_port_channel_n0_r02.py` y el parser externo congelado. El recálculo conserva los IDs, estados, ticks, canales y SHA de las fuentes originales. Los snapshots completos permanecen locales y sus localizadores/hash constan en el dossier. Es un complemento necesario de la evidencia portátil A/B/C, no su sustituto ni una repetición Native.

Para el cierre, informes, Word y tablas deben utilizar246/276/123 como totales físicos de los alcances declarados y mantener identificados los antiguos subconjuntos204/186/102 para explicar por qué cambió el recuento. La misma regla se aplica a ACTUADOR_R02:211/140 en las diez oportunidades, no179/140. El panel antiguo es una dosis material separada y no una observación pasiva.
