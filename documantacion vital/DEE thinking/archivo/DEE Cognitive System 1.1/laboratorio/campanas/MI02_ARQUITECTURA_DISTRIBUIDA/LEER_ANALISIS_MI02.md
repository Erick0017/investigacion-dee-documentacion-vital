# Análisis MI02

La campaña construyó dos realizaciones y una alternativa posterior R9. Hay aprendizaje local por consecuencias, solicitud nativa y uso privado comprobado. La integración no fue sostenida en todos los bloques; siguen siendo necesarias preparación y asistencia relevantes.

Empiece por `INFORME_CIENTIFICO_MI02.md`, después `CAPACIDADES_POR_VIDA.csv` y `TRAYECTORIA_MAIN.csv`. Las tablas separan MAIN, la vida heredada, las alternativas y los perfiles auxiliares. `ENSAYOS_Y_CONTROLES.csv` conserva errores, rechazos, respuestas incorrectas y ausencias; no es un veredicto de inteligencia.

El Word 1.8 está actualizado realmente, con validación estructural pero **sin validación visual**, porque falta `soffice.exe`. La edición anterior permanece localmente intacta.

## Comprobar los resultados

Desde esta carpeta extraída, con Python 3.10 o posterior:

```text
python RECALCULO/recalcular_mi02.py --raiz . --comparar RECALCULO/RESULTADO_REFERENCIA.json
python RECALCULO/verificar_tablas.py
```

El primer comando lee primarios y snapshots, vuelve a decodificar campos exactos y recalcula métricas sin importar DEE ni avanzar ticks. El segundo comprueba los CSV contra sus matrices exportadas. No son reproducciones físicas nuevas.

La evidencia agrupada está en `EVIDENCIA_ESENCIAL/REGISTROS_PRIMARIOS.jsonl.gz`. Cada línea tiene el archivo de origen y su SHA256; `INDICE_EVIDENCIA.json` indica línea y hash de la proyección. Se conserva completo el resultado científico de los primarios seleccionados; las historias repetidas del gestor se proyectaron sin sus duplicados. Los datos originales profundos no se borraron.

## Utilizar el sistema

El sistema operativo completo permanece localmente. `GUIA_MI02.md` y la ficha de continuidad explican comandos reales y los estados disponibles. El delta de código requiere una base Cognitive 1.1 compatible; **no incluye el motor ni instala un ente que ya sabe**.

`DELTA_APLICACION/aplicar_delta_mi02.py --sistema RUTA_A_SISTEMA` sólo prepara un plan. `--aplicar` exige revisiones reconocidas, crea un respaldo y no modifica snapshots, vidas o ACTIVO. No utilice un lock de otra vida como pretexto para borrarlo; la aplicación se bloquea mientras haya escritores o locks pendientes de revisar.

Este ZIP no es un archivo histórico íntegro ni una copia autosuficiente para continuar cualquier vida. Incluye estados completos seleccionados para examinar los casos centrales, pero no toda la instalación y genealogía. No mezcle snapshots ni interprete cuadros de mando como memoria de E1.

El SHA256 del ZIP se comunica fuera del propio contenedor. Su comprobante exacto se guarda localmente en `entregas/VERIFICACION_FINAL_EXTERNA_MI02.json`.
