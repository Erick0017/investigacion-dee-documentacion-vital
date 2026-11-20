# Reproducibilidad de Cognitive

Este apartado conserva recetas y materiales compartidos. No es otro ente principal ni un respaldo universal. El estado aprendido, su adquisición, el recálculo de registros y la recuperación de acceso se identifican por separado.

Desde `DEE Cognitive 2.0`, usando el Python oficial ya incluido:

```bat
motor\python313\python.exe -I -B -X utf8 reproducibilidad\reproducir.py listar
motor\python313\python.exe -I -B -X utf8 reproducibilidad\reproducir.py verificar
motor\python313\python.exe -I -B -X utf8 reproducibilidad\reproducir.py recalcular --destino D:\destino_nuevo_recalculo --grupos E
motor\python313\python.exe -I -B -X utf8 reproducibilidad\reproducir.py reproducir panel_12 --variante principal --vida PI03_REPRO_PANEL_01 --destino D:\destino_nuevo_panel
```

Sustituya los destinos por carpetas nuevas cuyo padre ya exista. Las dos primeras órdenes sólo leen archivos y no importan DEE. `recalcular` sólo ejecuta verificadores documentales stdlib sobre el material preservado: no ejecuta el motor. `reproducir` sí presenta experiencias materiales a una copia completa y consume su historia; exige destino explícito y un ID diagnóstico nuevo. Nunca cambia ACTIVO ni promueve controles.

`RECURSOS.json` resuelve materiales grandes dentro del producto. `recetas/` fija prefijo, variantes, entradas, lectores, ventanas ya implementadas por los módulos preservados, criterios y asistencia. `codigo_preservado/PI02_R04_OP1` conserva la revisión compartida, separada de modificaciones posteriores del producto. `codigo_preservado/historico_PI02` conserva los originales exactos y su procedencia; esos originales se estudian como texto, porque sus rutas históricas no son portables. Las adaptaciones ejecutables son los scripts de este apartado y tienen revisión propia.

Una coincidencia de resultados con la receta no implica inteligencia general, determinismo binario universal ni adquisición nueva del principal. La comparación al importar comprueba RAW, clocks, interfaces, agenda y recibos sin nuevos ticks, permitiendo sólo el cambio administrativo de identidad. El diario completo se importa con el contrato existente y reconcilia recibos; no se purgan pendientes ni se repiten operaciones ambiguas.

Cada ejecución conserva `CONTEXTO_EJECUCION.json`, `IMPORTACION_DIAGNOSTICA.json`, `RESULTADO_REPRODUCCION.json`, primarios, diario, stdout/stderr y el estado diagnóstico completo. Los controles comparten un prefijo: no son réplicas independientes. El panel es material; cambiar de lector o consultar repetidamente puede alterar lo que se estudia.

Si falla el acceso: primero use `verificar`, sin actuar. Distinga material faltante, recurso agotado, fase/lector, rechazo de admisión, interferencia y contenido no demostrado. La receta `fi_recuperacion` documenta un caso concreto de retirada de interferencia sin restauración ni reenseñanza; no garantiza recuperar cualquier contenido. Cargar un prefijo antiguo sólo conserva su historia anterior, perdiendo las experiencias posteriores de la copia: es restauración externa, no autorreparación del ente.

No vuelva a ejecutar una operación incierta con otro ID. Un bloqueo `EJECUCION_MATERIAL.lock` preservado exige comprobar su PID, propietario y futuro interrumpido antes de retirarlo. El sistema no mata propietarios ni borra bloqueos automáticamente. La rueda se comparte mediante enlace duro de sólo uso previsto; si el destino está en otro volumen, use un destino diagnóstico en el volumen del producto. No se reinstala ni se modifica el motor.

La sección `verification` de cada receta distingue preparada, ejecutada en una copia, adquisición, uso y control. Una receta preparada no se declara comprobada hasta que su evidencia de ejecución y alcance estén registrados.
