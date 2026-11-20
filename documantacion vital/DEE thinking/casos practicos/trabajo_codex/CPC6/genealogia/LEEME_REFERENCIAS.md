# Genealogía seleccionada y referencias breves

`SOURCE_MANIFEST.json` relaciona cada archivo con el miembro exacto y el SHA-256 del ZIP canónico del que procede. Son extracciones byte-exactas; los paquetes históricos permanecen intactos. No se incluyen sus ZIP completos.

`revision/MAPA_CPC1_A_5.json` diferencia las funciones heredadas, los dominios y las preguntas nuevas. La genealogía no cuenta una reproducción como descubrimiento.

Las tres referencias ejecutadas sobre la instalación aislada CPC6 de DEE thinking 4.0.0 están en `resultados/referencias/REFERENCE_REPRODUCTION_CHECK.json`:

- CP02_B: historia de resultados pasados, emisión en37 y evaluación en60/100/150. El entorno de barrera es una ley externa declarada; el pronóstico depende de la salida física nativa.
- CPC3: expectativa emitida en37, consecuencia actual presentada en83 y comparación física en84. La fuente congelada incorpora posteriormente límites documentales del observador que no estaban en el resultado discovery original; se conserva la discrepancia JSON y la igualdad física.
- SEM01: experiencias en17/45, señales solas en84/112, uso físico y continuación hasta129.

Las tres reproducen RAW completo, clocks completos y tick del snapshot final histórico, además de los recibos y observaciones indicados. Cinco ejecuciones incluyen dos repeticiones técnicas después de corregir la comparación de metadatos; no son cinco muestras independientes. Los errores y la primera versión del adaptador permanecen en resultados/jobs.

Reproducción de una referencia en un directorio **nuevo**, usando la instalación aislada local:

```powershell
.\.venv\Scripts\python.exe src\supervisor.py --name referencia_cp02_nueva --timeout 120 -- .\.venv\Scripts\python.exe src\reference_replay.py --case cp02 --output resultados\referencia_cp02_nueva
```

Sustituir `cp02` por `central` o `sem01` para las otras referencias. `central` conserva una comprobación JSON estricta que señala explícitamente los metadatos documentales distintos; el análisis offline `src/reference_reconcile.py` contiene el contraste físico/metadatos del corte ejecutado. La salida final histórica nunca se usa como entrada ni respuesta del participante.

`src/genealogy_sources.py` es una herramienta de procedencia, no necesaria para ejecutar estos casos: para volver a seleccionar los originales requiere los tres ZIP canónicos junto al workspace. La reproducción nativa utiliza sólo los archivos seleccionados incluidos aquí y el WHL oficial instalado; no requiere rutas privadas antiguas.
