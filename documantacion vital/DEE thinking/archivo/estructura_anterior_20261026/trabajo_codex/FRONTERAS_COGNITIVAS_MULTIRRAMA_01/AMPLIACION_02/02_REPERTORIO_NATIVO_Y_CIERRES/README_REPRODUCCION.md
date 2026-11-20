# MULTIRRAMA 01 — AMPLIACIÓN 02

Instrumento: Windows x64, CPython 3.13, DEE thinking 3.0.0 y kernel v27 congelados. El expediente conserva los 1155 miembros heredados. Sólo se añade esta sección; los HASHES y resúmenes antiguos conservan su alcance original.

## Preparar una extracción aislada

Extraer el ZIP completo a una ruta corta, por ejemplo `C:\DEE_A02`. No usar instalaciones de trabajo anteriores ni iniciar mundos históricos. El WHL necesario ya está en `SHARED_TOOLS`.

```powershell
py -3.13 -m venv C:\DEE_A02_ENV
& C:\DEE_A02_ENV\Scripts\python.exe -m pip install --no-index C:\DEE_A02\SHARED_TOOLS\dee_thinking-3.0.0-cp313-cp313-win_amd64.whl
$taskPython = 'C:\DEE_A02_ENV\Scripts\python.exe'
$taskRoot = 'C:\DEE_A02\02_REPERTORIO_NATIVO_Y_CIERRES'
$taskRunner = "$taskRoot\RUNNER\run_extension_02.py"
```

El expediente no incluye entornos virtuales ni caches. `apparatus.py`, `observers.py`, `frontiers.py` y los auxiliares de verificación son versiones experimentales, no un producto nuevo. Las respuestas físicas siempre proceden del Runtime.

## Verificar el paquete

```powershell
& $taskPython -B $taskRunner --mode verify --output 'C:\DEE_thinking_3_0_0_FRONTERAS_COGNITIVAS_MULTIRRAMA_01_RESULTADOS.zip'
```

Este comando comprueba CRC, los 1155 contenidos heredados y todos los hashes de la sección nueva. `PARENT_MEMBERS.json` contiene sus identidades; el ZIP padre sellado se conserva en el workspace, no anidado en la entrega.

## Ejecutar/reproducir un caso sin tocar la evidencia

```powershell
& $taskPython -B $taskRunner --root $taskRoot --package-root C:\DEE_A02 --mode reproduce --case P09/mobile_basal_full --replica-out C:\DEE_A02_REPLAY01
& $taskPython -B $taskRunner --root $taskRoot --package-root C:\DEE_A02 --mode reproduce --case P14/flux_cut_replication1 --replica-out C:\DEE_A02_REPLAY02
```

Cada destino debe ser nuevo y estar fuera de la sección sellada. El runner crea una réplica técnica, utiliza los checkpoints requeridos del paquete y compara todos sus checkpoints homólogos en RAW, clock uint64 y tick, además de las llamadas físicas de entrada. No fusiona forks ni modifica el corte original. El límite de 15 minutos de esta réplica técnica no renueva el presupuesto científico de la campaña.

Los registros tempranos no contenían `payload` ni `runtime_ref` como campos explícitos. La comparación exige igualdad de todos los campos realmente registrados, los recibos por Runtime y el orden de payloads de consulta fijado por protocolo; declara los campos ausentes, sin rellenar retrospectivamente el log original.

Los casos `A` son relecturas, no nuevas simulaciones. `B` identifica cierres metodológicos; `C`, preparaciones nuevas. Las modalidades separan evolución nativa, protocolo explícito de experiencias, edición diagnóstica y reconstrucción asistida. Los tratamientos con sondas muestran por separado la continuidad intacta y los forks consultados.

## Reanudar una ejecución interrumpida

```powershell
& $taskPython -B $taskRunner --root $taskRoot --package-root C:\DEE_A02 --mode resume
```

Antes del sellado y dentro del plazo original, `resume` verifica hashes, omite casos completados y conserva los intentos fallidos y el presupuesto acumulado. El expediente entregado está sellado y no tiene casos pendientes: rechaza `run`, `resume` y `case` para impedir que se altere evidencia final. Para volver a ejecutar un caso, usar `reproduce` y un destino nuevo, no quitar el sello ni resetear el plazo.

## Localizar datos y continuar un estado

Cada caso tiene `BRANCHES/Pxx/ID/MEASUREMENTS.json`. Su `attempt_###` conserva configuración, preparación, telemetría y `OPERATIONS.json`: llamadas externas reales, ediciones diagnósticas y recibos por Runtime. Los prefijos de recibos heredados por forks no son nuevas exposiciones. Los archivos `MAIN_FINAL.deetsnap` son continuidades guardadas, no resultados reconstruidos manualmente.

```python
import dee_thinking as dt
rt = dt.Runtime.load_snapshot(r'C:\DEE_A02\02_REPERTORIO_NATIVO_Y_CIERRES\CHECKPOINTS\P06\continued_distributed_HA\attempt_001\MAIN_FINAL.deetsnap')
assert rt.current_tick == 700
rt.run_until(704)  # sólo en una copia diagnóstica aislada
```

El análisis descriptivo está en `ANALYSIS`. `COMBINATIONS/COMBINATION_MEASUREMENTS.json` referencia dos cruces físicos ya contados en sus casos: no duplica ejecuciones. `TECHNICAL_PREFLIGHT`, `TECHNICAL_WINDOWS` y la verificación de extracción limpia separan igualdad instrumental de las preguntas funcionales todavía abiertas. No hay un dictamen cognitivo automático.

`RUN_SUMMARY.technical_reproductions` cuenta la referencia técnica inicial. Las tres reproducciones de extracción limpia y las cuatro ventanas técnicas se contabilizan por separado en `ANALYSIS/COMPARACION_CORTE_ANTERIOR.json`; no aumentan el número de casos científicos.
