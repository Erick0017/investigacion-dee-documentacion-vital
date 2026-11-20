# CP02 B — ente predictivo persistente

Windows x64, CPython3.13 estándar y DEE thinking3.5.0. El wheel congelado se incluye en `runtime/`; no se necesita internet, LLM ni el laboratorio histórico.

Instalación y uso desde la carpeta extraída:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --no-index .\runtime\dee_thinking-3.5.0-cp313-cp313-win_amd64.whl
.\.venv\Scripts\python.exe -I -B ejecutar.py --mode demo --output nueva_demo
.\.venv\Scripts\python.exe -I -B ejecutar.py --mode reproduce --output nueva_reproduccion
.\.venv\Scripts\python.exe -I -B conversar.py --output mi_sesion
```

Cada comando nativo se ejecuta en un proceso propio con timeout30s; el lanzador completo tiene límite180s. Estos límites portables no reutilizan el presupuesto agotado de la campaña. Los resultados nuevos van al directorio de salida elegido; no sobrescriben la evidencia registrada.

## Gramática real

Una línea por orden; `#` comenta una línea. Se permiten rutas entre comillas.

- `nuevo semilla [directo|asistido] [cambio_tick|none]`: reinicio visible, individuo nuevo; semilla sólo del hábitat/evaluador.
- `experiencia`: en tick32, dos resultados pasados realmente observados, canal primario y referencia inversa.
- `experiencia tick`: una observación pasada nueva en ese tick futuro, máximo1500ticks por llamada.
- `predice tick_objetivo [tick_objetivo...]`: salida física antes de objetivos estrictamente futuros.
- `resultado tick_objetivo`: avanza y evalúa una predicción previamente registrada.
- `avanzar cantidad_ticks`:0..1500; no resetea al individuo.
- `observar`: lecturas pasivas actuales; observador externo, no introspección nativa.
- `guardar ruta.deetsnap`: estado operativo completo y hábitat externo.
- `cargar ruta.deetsnap`: continúa el estado nativo, hábitat y emisiones guardadas; cambia explícitamente a interfaz asistida. El sidecar de UI crea un nuevo `run_id` y vacía `completed_goals`: esos dos campos y el modo previo no se preservan, aunque las emisiones pendientes conservan sus IDs de origen dentro del snapshot.
- `salir`.

La demostración reproducible es `SESION_REPRODUCIBLE.txt`. Muestra acierto inicial, error tras cambio de contexto, dos predicciones no resueltas, nueva adquisición dependiente de fase, pronóstico correcto posterior, guardar/cargar y continuación. No fabrica conversación ilimitada mediante recreaciones ocultas.

## Dos interfaces distintas

`directo` introduce la consulta en MAIN; es una sonda física consumible y puede comprometer futuras entradas. `asistido` consulta un descendiente-fork del estado nativo, mientras MAIN y hábitat avanzan los mismos3ticks. No copia materia, clocks ni resultados futuros a MAIN. Es una interfaz externa de lectura física, no autonomía ni introspección del individuo.

La salida direccional positiva/negativa corresponde a llegada/ausencia dentro del hábitat declarado. Cero, ausencia o consulta rechazada se traduce a un conjunto no resuelto; no representa probabilidad aprendida. El hábitat es una barrera externa determinista con condición inicialmente estable y un cambio opcional fijo. Un paquete intenta pasar cada tick entero, exista o no predicción; se materializan las observaciones seleccionadas sin guardar todos los ticks. Nunca lee la predicción para generar el resultado.

El codec suministra resultados PASADOS, no etiquetas futuras. La regla de persistencia y el significado del decoder están diseñados: no se afirma aprendizaje de un diccionario arbitrario precursor→consecuencia.

## Localizar evidencia

`EXPERIMENT_CONFIG.json` y `ASSISTED_EXTENSION_CONFIG.json`: congelaciones y reservas. `PREDICCIONES*.jsonl`: emisiones append/flush/fsync y evaluaciones posteriores. `resultados/`: estados, recibos, errores y controles. `AUDITORIA_INFORMACION.json`: información permitida y controles de no filtración. `checkpoints/`: MAIN y cortes relevantes. `demo_session/`: sesión ejecutada. `RESULTADOS.json` e `INFORME.md`: alcance medido. `resultados/METADATA_CORRECTIONS.json` declara el rótulo erróneo de modalidad en los primeros logs asistidos; no altera esos logs ni la física.

Para reejecutar una batería física completa, copie ambas configuraciones a un directorio nuevo y ejecute `src/worker.py confirmed --root nuevo_directorio`, después `src/assisted_confirm.py nuevo_directorio`. Los scripts rechazan sobrescribir una batería ya concluida. Discovery se conserva como tal; las repeticiones técnicas no son réplicas independientes.

`resultados/CLEAN_EXTRACTION_CHECK.json` registra instalación no editable y sin red desde una extracción independiente, cuatro evaluaciones prospectivas de reproducción/continuación y seis de la sesión pública hasta900. La precedencia se comprobó mediante ticks y registros monotónicos no vacíos. La rama técnica restaurada que evalúa una emisión pendiente bajo otro nombre se vincula mediante un alias explícito derivado de `src/reproduce.py`; no se adivinan ancestros por igualdad de carga. Los informes auxiliares iniciales se conservan junto a su corrección. No se necesitan archivos del workspace privado ni extraer el ZIP de A.
