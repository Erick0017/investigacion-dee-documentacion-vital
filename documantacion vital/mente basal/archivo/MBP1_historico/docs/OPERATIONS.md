# Mente Basal: guia breve de operaciones

Esta guia opera el linaje local `MENTE-BASAL-001` mediante el unico punto de entrada admitido, `tools\habitat.ps1`. Los ejemplos suponen Windows PowerShell y no requieren red.

## Preparar la consola

```powershell
$Habitat = 'D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\mente basal'
Set-Location -LiteralPath $Habitat
```

El script usa explicitamente `D:\Descargas\ANACONDA MINICONDA\python.exe` y la copia local de `dee_thinking` dentro de `baseline\python_site`. Si esa ruta de Python no existe, el habitat no debe iniciarse hasta corregir la instalacion local. No se instala nada sobre el entorno historico de DEE thinking.

## Ciclo de vida

Estas dos operaciones son solamente para una instalacion nueva:

```powershell
& .\tools\habitat.ps1 -Action bootstrap
& .\tools\habitat.ps1 -Action create
```

`bootstrap` instala el WHL congelado en la carpeta local del habitat, sin buscar dependencias en Internet. `create` escribe X0, registra la instancia y crea el primer checkpoint con entradas preparadas pendientes. Se niega a sobrescribir un linaje existente; no vuelva a ejecutarlo para reanudar.

Iniciar el worker independiente y consultar su estado:

```powershell
& .\tools\habitat.ps1 -Action start
& .\tools\habitat.ps1 -Action status
& .\tools\habitat.ps1 -Action panel
```

`start` restaura exclusivamente el checkpoint al que apunta `world\latest_checkpoint.txt`; no llama al constructor inicial. Si falta ese checkpoint o no es valido, el inicio falla. El worker adquiere `world\writer.lock`, por lo que un segundo escritor sobre el mismo linaje es rechazado. Cerrar esta consola o dejar de consultar estado no constituye una orden de parada.

`panel` carga una copia del último checkpoint confirmado y genera `analysis\panel_latest.html` y su JSON asociado. Rotula campo, región, agregación y tick, muestra sitios funcionales fijos y la cola temporal reciente. Es pasivo respecto del Runtime vivo; cerrar el archivo no detiene el worker.

Avance manual acotado, pausa y reanudacion:

```powershell
& .\tools\habitat.ps1 -Action advance -Count 64
& .\tools\habitat.ps1 -Action pause
& .\tools\habitat.ps1 -Action status
& .\tools\habitat.ps1 -Action resume
```

`advance` ejecuta exactamente el numero positivo de ticks solicitado, incluso si el modo continuo estaba pausado, y luego conserva el estado de pausa previo. `pause` actua en una frontera completa: el tiempo humano transcurrido no agrega ticks. `resume` quita la pausa del mismo Runtime; no crea otro mundo. Si el proceso termino de forma segura, ejecute primero `start` y despues `resume`.

Liberar la continuacion autonoma, una sola vez y solamente despues de alcanzar `T_ref`:

```powershell
& .\tools\habitat.ps1 -Action release
& .\tools\habitat.ps1 -Action status
```

`release` es distinto de `resume`: registra la entrega de control, quita la pausa y fija `tick_budget_end = reference_tick + max_ticks_after_reference`. Falla si el mundo aun no llego a `T_ref`. Confirme en la salida que `autonomy_released` sea `true`, que `reference_tick` sea el corte esperado y que `tick_budget_end` no sea nulo. Repetir `status`, guardar o recolectar no reinicia ninguno de esos limites.

Guardar o detener con guardado:

```powershell
& .\tools\habitat.ps1 -Action save
& .\tools\habitat.ps1 -Action stop
```

Cada guardado publica un archivo nuevo en `world\checkpoints`; nunca reemplaza checkpoints historicos. `stop` termina en frontera, guarda y deja el estado `STOPPED_SAFE` cuando concluye normalmente.

## Presentar una experiencia explicita

El puerto generico instalado es `external.port.alpha`. Para pedir una entrada en la frontera actual:

```powershell
& .\tools\habitat.ps1 -Action experience -Channel 'external.port.alpha' -Load 41
```

Para programarla en un tick futuro conocido:

```powershell
& .\tools\habitat.ps1 -Action experience -Channel 'external.port.alpha' -Load 41 -Tick 1000
```

La respuesta del comando contiene el ID y el estado inicial del recibo. El segmento historico conserva orden recibida, canal, carga, tick solicitado y, mediante los cambios de recibo, tick efectivo o causa de rechazo. Una solicitud para un tick pasado se rechaza; nunca se antedata. Tras un comando rechazado el worker queda pausado por seguridad: revise `status` y reanude solamente despues de entender la causa.

No use este puerto para inyectar una etiqueta de regimen, una metrica global ni el resultado esperado. Toda escritura posterior del host es una entrada **acoplada**, aunque el canal haya sido instalado en X0.

## Recoleccion reproducible

Cortar, rotar segmentos, empaquetar archivos inmutables y continuar:

```powershell
& .\tools\habitat.ps1 -Action collect -RequestId 'CUT_002'
```

Cortar, empaquetar y detener:

```powershell
& .\tools\habitat.ps1 -Action collect-stop -RequestId 'CUT_003_STOP'
```

Use IDs nuevos y sin espacios. Los ZIP se escriben en `history\collections` con el tick de corte en el nombre. `collect` guarda un checkpoint completo, registra telemetria de corte, cierra el segmento activo, abre el siguiente y solo entonces comprime los archivos ya inmutables. No reinicia el reloj autonomo. `collect-stop` hace el mismo corte y solicita la parada segura.

## Replay de un intervalo cerrado

El modo menos propenso a errores toma las rutas de un descriptor de recoleccion. Este ejemplo selecciona `CUT_002`, reconstruye su intervalo y compara el resultado con el checkpoint final del corte:

```powershell
$CutPath = (Get-ChildItem -LiteralPath .\history\collections -Filter 'cut_CUT_002_t*.json' |
    Sort-Object LastWriteTimeUtc -Descending |
    Select-Object -First 1).FullName
$Cut = Get-Content -LiteralPath $CutPath -Raw | ConvertFrom-Json
$StartCheckpoint = Join-Path $Habitat $Cut.start_checkpoint
$HistorySegment = Join-Path $Habitat $Cut.history_segment
$ExpectedCheckpoint = Join-Path $Habitat $Cut.end_checkpoint
& .\tools\habitat.ps1 -Action replay `
    -StartCheckpoint $StartCheckpoint `
    -Segment $HistorySegment `
    -ToTick ([int64]$Cut.end_tick) `
    -ExpectedCheckpoint $ExpectedCheckpoint
```

El replay carga un Runtime separado y escribe `analysis\replay_T...deetsnap`. Nunca adquiere el papel de escritor del mundo principal ni devuelve su estado al linaje. Con `-ExpectedCheckpoint`, el resultado informa igualdad exacta de RAW, clock y tick.

## Evaluacion congelada

```powershell
$Checkpoint = Join-Path $Habitat ((Get-Content -LiteralPath .\world\latest_checkpoint.txt -Raw).Trim())
& .\tools\habitat.ps1 -Action evaluate -StartCheckpoint $Checkpoint
```

Esto lee `response1`, `response2`, `response3` y `context_hub` desde una carga separada del checkpoint y escribe un JSON nuevo en `analysis`. Es una lectura diagnostica; no demuestra aprendizaje y no altera el mundo vivo.

## Donde mirar

- `world\status.json`: estado publicado, PID, tick, pausa, plazo, ultimo checkpoint, recibos y recursos.
- `world\instance.json`: identidad, procedencia, canales y checkpoints iniciales.
- `world\controller.json`: estado persistente del coordinador.
- `history\segments`: eventos ordenados; los archivos sin `.active` estan cerrados.
- `history\telemetry`: telemetria pasiva por segmento.
- `history\collections`: descriptores y ZIP de cada corte.
- `world\worker.stdout.log` y `world\worker.stderr.log`: diagnostico del proceso.

`status` muestra la ultima publicacion, no una prueba aislada de vida. Para confirmar avance compare dos consultas separadas y verifique que cambian `tick` y `last_activity_utc`; un heartbeat sin cambio de tick no prueba evolucion.

## Clases de operacion

- **Nativo tras preparacion:** los portadores finitos ya admitidos, la materia y la organizacion evolucionan bajo v27 dentro del unico Runtime. El controlador no calcula ni escribe las respuestas atribuidas a DEE.
- **Acoplado a entrada externa:** `experience` y cualquier entrada programada por el host. Su solicitud, programacion, admision o rechazo quedan registradas.
- **Diagnostico:** `evaluate`, replay y ramas de prueba. Sus estados no regresan al linaje principal. La telemetria y `status` son observacion pasiva.

Una consulta aplicada deliberadamente al mundo principal no es diagnostico externo: pasa a ser parte de su historia fisica y debe interpretarse como experiencia.

## Limites y condiciones de Windows

La configuracion inicial impone: 16 horas maximas desde la primera ejecucion confirmada de `release`; un hilo; bloques de 8 ticks; 900000 ticks maximos despues de la referencia; 1 GiB de working set; 1.5 GB para mundo mas historia; y una reserva de disco de al menos 2 GiB o dos checkpoints, lo que resulte mayor. La telemetria se intenta cada 64 ticks y el checkpoint periodico cada 1800 segundos. `status` es la fuente autoritativa para `autonomous_deadline_utc`, `tick_budget_end`, memoria, archivo y disco. Un `tick_budget_end` nulo significa que `release` no quedo aplicado y no debe declararse una continuacion de produccion plenamente transferida.

Al alcanzar un limite, el worker pausa, guarda un checkpoint verificado y termina en estado seguro; no borra historia ni se reinicia. Consultar, guardar o recolectar no reinicia el plazo.

Para continuar, Windows debe permanecer encendido y sin suspension, la sesion y la unidad `D:` deben seguir disponibles, y no debe finalizarse el proceso desde el Administrador de tareas. El lanzador no instala un servicio, no configura inicio tras reinicio y no cambia politicas de energia. No se promete continuidad durante cierre de sesion, suspension, reinicio, apagado, fallo de disco o perdida del proceso. El lanzador comprueba que el worker no quede en un Job Object con politica de muerte al cerrar; si Windows no permite separarlo, falla en vez de declarar independencia.
