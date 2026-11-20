# Servicio persistente: corte del bloque A

Instrumento incorporado al gestor existente, no una política cognitiva nueva. Una sola instancia de OrganizationalWorld permanece cargada; el propietario avanza ticks ociosos, procesa una cola local limitada y guarda estado completo. No hay puerto público, autoarranque ni reintento ciego de trabajos inciertos.

## Comprobaciones realizadas

|Caso|Resultado observado|Alcance|
|---|---|---|
|Piloto R01, copia de MA02_MAIN_5|Gamma positivo y epsilon negativo,14/14 entradas aplicadas;9 ticks ociosos entre recibos y18 en otro proceso|Accesos heredados, no adquisiciones nuevas. Conserva un falso assert del harness que utilizó una caché antigua.|
|Emparejado R02|El comprobador no reconoció el propietario porque comparó PID del lanzador Windows y PID del intérprete|Fallo del harness previo a sus consultas. Se conservó el avance real y se pidió parada; no se rebobinó la copia.|
|Emparejado R03|Snapshot+cola pendiente+resultados importados en identidad nueva;epsilon− y gamma+;14/14 entradas;16 ticks después de recargar|El par completo fue verificado antes de importar. Deducción de IDs y reconciliación no reejecutaron acciones. Una interfaz desconocida se rechazó antes de introducir entradas.|
|MAIN R04→R05|La misma MU_MAIN pasó T16433→16623;dos selecciones nativas− ejecutaron sendos trabajos reales aceptados de32B;memorias zeta+,alfa−,gamma+;10 ticks ociosos|El operador eligió el momento y las tres direcciones de memoria P0. Ninguna respuesta objetivo se envió a la selección nativa. No se volvió a enseñar.|
|Cierre R05|La pausa que había quedado pendiente se ejecutó una vez;exportar/guardar/detener y cerrar epoch1 no añadieron ticks ni repitieron trabajo|La espera original R04 falló por coste de serialización/fin de horizonte técnico, no por pérdida cognitiva. Todo el futuro alcanzado se conservó.|
|Compactación R06|67.206.496 bytes de ficha original archivados idénticos, gzip1.013.198B; ficha operativa4.412B|Cero ticks. Comparación binaria de snapshots completos, normalizando únicamente metadata de identidad del sistema: RAW,clocks,canales,recibos,entradas pendientes y todo el propietario son idénticos. No es aprendizaje.|
|Uso posterior R07|Epoch2 explícita, una consulta nativa nueva−,T16623→16634, sin trabajador externo; cierre limpio|Contador final5, no repetición de las4 sesiones anteriores. El assert que leyó contador cacheado anterior se conserva como error del harness.|

`recalcular_servicio_a.py` recodifica45 observaciones RAW y30 recibos aplicados de30 solicitudes. Lee los64 bytes reales de los dos archivos de trabajador exportados y comprueba SHA, contenido, longitud y ley de admisión. No ejecuta DEE ni vuelve a producir los archivos.

Se conservaron18 tests de transporte de biblioteca estándar, sin importar DEE: capacidades de cola, dos clientes, validación, deduplicación, pausa, cierre de admisión, epochs y errores sintéticos inciertos. Una interrupción sintética no se anuncia como interrupción comprobada de un trabajador nativo real.

## Causa del retraso operativo

Store.commit estaba serializando la ficha de operaciones heredada completa, de aproximadamente67MB, después de cada petición. R04 completó cuatro sesiones, pero terminó por su horizonte en una frontera segura antes de atender la pausa. R05 continuó esa misma cola: no volvió a enviar las cuatro sesiones. La compactación autorizada guarda el original byte a byte, mantiene HISTORIA append-only y utiliza `operation_count_offset` explícito. No cambia cuerpos, cargas, clocks, experiencias o mecanismos de decisión.

## Estado e incorporación

El corte A alcanzado por MU_MAIN fue T16634, snapshot `estado/checkpoints/MU_MAIN.T16634.ba61eac94a01.deetsnap.gz`, SHA-256 `b6c02df2e804b167b85f9e8fd849e091227b81ccfd7a49e442f67156944c71ad`. La historia viene de su padre MA02_MAIN_5; no es una reconstrucción desde T0 ni otro individuo elegido para cada pregunta. Epoch2 quedó detenida y cerrada explícitamente, sin cola pendiente ni resultado incierto, habilitando la continuación declarada del bloque B. El corte no se presenta como el estado más reciente si B ya continuó.

El par completo previo a ese cierre está en `sistema/estado/servicios_persistentes/MU_MAIN/exportaciones/closed_epoch_5057efcaf3e4/`:23 miembros,191.713B; manifiesto SHA-256 `0457caa911d8b52a0f800b8b785a5cffd26b1f096efae4b65c23dfd8807fff17`. El snapshot del par y el corte posterior comparten estado físico; difieren en la metadata documental del cierre explícito. No se finge identidad de bytes entre ambos.

Comandos incorporados: `mente-unificada-iniciar/estado/pedir/continuar/pausar/reanudar/guardar/exportar/importar/resultado/detener/finalizar-protocolo/compactar-historia`. Los modos y backend se declaran antes de actuar. El backend `mente_unificada` utiliza selección nativa; su modo `memoria` mantiene explícita la asistencia del operador para direccionar un contexto.

Una vida ya servida necesita snapshot, cola, outbox y estado del entorno externo. Un fork genérico que copie sólo el snapshot no se acepta como continuación de ese protocolo: use exportación/importación emparejada. El archivo histórico de operaciones no es memoria accesible al actor ni dependencia para restaurar el estado nativo completo.

## Límites

Esto no es aún el ensayo final de60 minutos. Dos trabajos útiles no demuestran por sí solos aprendizaje de su selección: la evidencia causal de adquisición corresponde a los contrastes del bloque A del investigador principal. Sólo se consultaron tres de las seis memorias durante esta ventana, no se certifican las restantes por inferencia. No se acreditan R2 general, lenguaje general, NSM65 o estabilidad indefinida. Los errores de observación y del harness permanecen en sus primarios.
