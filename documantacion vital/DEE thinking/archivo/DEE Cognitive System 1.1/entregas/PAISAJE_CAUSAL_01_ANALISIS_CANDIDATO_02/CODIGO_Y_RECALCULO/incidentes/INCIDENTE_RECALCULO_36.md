# Incidente de lectura de metadatos del recálculo

La primera ejecución del auditor portátil encontró un campo documental `parent` como cadena en un ensayo antiguo de esta campaña y se detuvo con AttributeError antes de emitir resultados. No se modificó física, decodificador ni criterio. Se admite ahora que ese campo identificativo pueda ser cadena o registro; se conserva como desconocido el tick no contenido en esa forma. Los RAW, relojes y resultados físicos siguen verificándose sin omitir casos.

Se conservaron los bytes de la revisión inicial en `versiones_codigo/objetos/` antes de corregirla. No es un resultado negativo del ente ni una nueva simulación.
