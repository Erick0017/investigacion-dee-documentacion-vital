# Recálculo de la hora de servicio APD03, sin física nueva

Este instrumento examina únicamente primarios ya escritos. No importa DEE, no abre SQLite vivo, no inicia procesos y no avanza ticks. No duplica la auditoría de aprendizaje o de RAW del actor.

Verifica identidad y padre, primer estado cargado, propietario/epoch, solicitudes literales e IDs, SHA del payload, orden del programa congelado, ventanas monotónicas y pausas registradas. Al existir el cierre comprueba los dos STOP, el estado físico anterior a la reapertura, el ID pendiente original con su llegada/seq/payload intactos, la reconciliación sin reenvío y las atestaciones de fuentes/protegidos.

Durante la ejecución el informe dice `incremental_not_closed`; no acredita una hora antes de recibir FIN y los cortes de cierre. Las observaciones de heartbeat son muestras pasivas almacenadas en caché, no una traza de cada tick. Los recursos de un Job y sus descendientes no son energía.

## Uso sobre los primarios existentes

```text
python recalcular_servicio_hora_apd03_n0.py --evidencia RUTA_MAIN_INTEGRADO_R01 --salida RECALCULO_NUEVO.json
```

Al cerrar definitivamente, exigir los comprobantes completos:

```text
python recalcular_servicio_hora_apd03_n0.py --evidencia RUTA_MAIN_INTEGRADO_R01 --salida RECALCULO_CERRADO.json --requiere-cierre
```

La extracción compacta copia bytes exactos de JSON/GZip/fuentes congeladas y lista por hash los estados operativos omitidos. Se utiliza un destino nuevo, después del cierre:

```text
python recalcular_servicio_hora_apd03_n0.py --evidencia RUTA_MAIN_INTEGRADO_R01 --extraer DESTINO_NUEVO --salida RECALCULO_EXTRAIDO.json --requiere-cierre
```

El conjunto extraído no es un respaldo operativo. No contiene todas las colas, snapshots ni archivos de una vida continuable. No debe utilizarse para restaurar MAIN.

## Cierre portable preparado, no ejecutado antes de FIN

`cerrar_servicio_hora_apd03_n0.py --origen RUTA_MAIN_INTEGRADO_R01 --salida CARPETA_NUEVA` exige los seis primarios finales, recalcula en origen, copia la evidencia exacta y los scripts, recalcula de nuevo y compara en una tercera raíz temporal. No inicia procesos ni restaura un mundo. Si falta el cierre real se detiene sin fabricar un resultado final. El manifiesto del conjunto excluye su propio hash.

## Límite de la métrica de E/S

Los campos `job_io` obtenidos de `Extended.IoInfo` de Windows clase9 pertenecen a una estructura reservada: sus ceros **no son una medición de E/S cero** y este recálculo no los utiliza como métrica. El observador OS separado usa clase8 para los Jobs Native y sus trabajadores; son contadores lógicos acumulados desde la creación de cada Job, no tráfico físico de almacenamiento ni todo el anfitrión. Su unión tardía no aporta fronteras de fase anteriores sin muestras. CPU/RAM del árbol exterior conservan su alcance independiente. No sumar contadores anidados; energía sigueNO MEDIDA.

Los fixtures sintéticos R03 son15/15 y comprueban el instrumento, no la capacidad de E1; incluyen un cierre sintético completo para ejercitar el mismo ID en dos procesos y el vaciado confirmado del primer Job antes de abrir el segundo. El primer recálculo incremental real R01 verificó452 condiciones sin incidencias, pero la hora y reapertura seguían explícitamente pendientes en ese corte. El cierre real requiere otro archivo de recálculo, sin reescribir aquel resultado. El recálculo contabiliza por separado la petición intencionalmente encolada durante pausa y su finalización después de reapertura: no cuenta esa lectura del mismo ID como una segunda petición.

## Precisión sobre FIN y cierre real

El campo `owner` de `FIN_VENTANA_CONGELADA.json` reutiliza el objeto de inicio, con la observación inicial T548407/paused=true. No es una lectura final ni prueba de que el mundo quedara pausado al terminar la hora. Este recálculo sólo compara ese campo como identidad de propietario. El fin temporal se obtiene de los dos valores monotónicos registrados; el estado durante la ventana se documenta con sus heartbeats propios —mismo PID, paused=false, ticks crecientes— y los controles. El corte final se obtiene de los primarios STOP/reapertura y no del `owner.observation` almacenado en FIN. Se preservan sus bytes y se identifica esta limitación instrumental, sin alterar la historia física.

El primer recálculo retrospectivo cerrado real verificó1445condiciones, sin incidencias y sin primarios finales pendientes. Los informes incrementales anteriores conservan su alcance histórico; no fueron reescritos.
