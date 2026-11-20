# Recalcular EO02 desde esta distribución

El recálculo lee archivos archivados mediante stdlib; no ejecuta DEE, no arranca trabajadores y no es una reproducción cognitiva. Desde `investigacion/ENTE_DEE_EVOLUCION_02/`:

```bat
..\..\motor\python313\python.exe -I -B -X utf8 CIERRE\recalculo\recalcular_eo02.py --primarios EVIDENCIA_RAIZ --codigos EVIDENCIA_RAIZ\codigo_ejecutado --artefactos EVIDENCIA_RAIZ\recalculo\ARCHIVOS_SERVICIOS --indice-artefactos EVIDENCIA_RAIZ\recalculo\INDICE_ARTEFACTOS_FINAL.json --salida ..\..\trabajo_personal\resultados\RECALCULO_EO02
```

`CIERRE/recalculo/LEER_RECALCULO.md` explica argumentos, referencias independientes y los límites. El resultado se escribe en trabajo personal, no sobre los primarios. Los scripts de capacidad y contexto están en `CAPACIDAD_CODIGO/` y `CONTEXTO_CODIGO/`; sus datos originales conservan `EVIDENCIA_RAIZ/capacidad/` y `EVIDENCIA_RAIZ/contexto/`.

Se conservan primarios positivos, errores, preflight, fuentes exactas ejecutadas, outputs pequeños de servicios y recálculo finalV2. Se excluyen copias intermedias `CORTE_01..04`, `FINAL` anterior, snapshots de diagnóstico no seleccionados y cualquier staging científico en construcción. Las rutas históricas internas son procedencia, no requisito de ejecución.

Para volver a ejecutar física utilice los perfiles, snapshots completos y gestor de `sistema/`, sobre una copia. Los resultados de otras vidas no se suman a MAIN. La prueba de extracción del ZIP es una comprobación operativa distinta del recálculo.
