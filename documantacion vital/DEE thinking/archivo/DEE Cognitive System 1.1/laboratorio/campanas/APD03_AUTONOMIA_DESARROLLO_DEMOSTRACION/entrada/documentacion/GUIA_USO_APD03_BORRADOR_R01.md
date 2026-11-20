# APD03: uso en una terminal

Estado editorial: borrador basado en la prueba original `ENTRADA_NATIVA_R01`. No declara cerrada la campaña, actualizado el Word ni verificado el Full APD03. La entrada instalada es `sistema/app/usar_dee.py`, versión `APD03.single_terminal.R02`. La selección inicial de esta revisión apunta al padre APD02_MAIN T548407; no a una adquisición futura de APD03_MAIN.

## Qué está probado

Una copia diagnóstica aprendida se abrió mediante importación emparejada completa, realizó una solicitud numérica, recibió docencia explícita distinta de la última asociación documentada del padre, utilizó esa revisión, guardó y se abrió después en otro proceso con la misma identidad. Se utilizó un solo terminal de órdenes por sesión; el supervisor administró al propietario en segundo plano. El usuario no coordinó manualmente un segundo terminal.

La prueba fue un guion de operador con fuentes fijadas, no una sesión de una persona externa ni una prueba de exploración autónoma. Tampoco convirtió las 28 pruebas de transporte con mocks en 28 experimentos Native.

## Tres estados diferentes

- Aplicación abierta: hay una interfaz que acepta órdenes.
- Mundo en pausa: el propietario está cargado, pero no evoluciona entre peticiones. El inicio es explícitamente pausado.
- Mundo reanudado: el mismo propietario avanza con el calendario declarado y procesa las oportunidades presentadas. Estar reanudado no significa que DEE elija los objetivos del operador.

`estado` devuelve la observación pasiva publicada por el propietario, con su antigüedad de caché; no inserta una sonda para comprobar una memoria. `lenguaje`, `usar` y las demás interacciones materiales sí cambian la historia física.

## Abrir una copia nueva sin sustituir otra vida

Desde la raíz original de **DEE Cognitive System 1.1**, ejecute el script con el CPython 3.13 x64 que ya funciona con el motor oficial. Ésta es la forma real utilizada en la comprobación original; no requiere reinstalar el entorno:

```powershell
& 'D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\_dcs11_env_20261020_002458\Scripts\python.exe' -I -B -X utf8 '.\sistema\app\usar_dee.py' --nueva MI_APD03_01
```

`MI_APD03_01` es un ejemplo de identidad nueva, no una vida ya evaluada. `--nueva` importa el par seleccionado una sola vez: mundo, diario, colas, outbox, archivos y progreso. No crea un T0, cambia ACTIVO ni copia aprendizajes de otra bifurcación. Una identidad existente produce un error en vez de sobrescribirse.

La configuración única está en `sistema/contratos/ENTRADA_SENCILLA_APD03.json`. Antes del cierre APD03, su fuente admitida sigue siendo APD02_MAIN T548407, snapshot `64359d48edd49f8a1f5616ceacd04c4479a27383877c23381e217a39f0cc05a9`. Cambiar el código disponible no traslada automáticamente conocimientos a una copia anterior.

En la misma terminal aparece `DEE>`. Puede escribir:

```text
estado
reanudar
usar suma 18 7 --retorno omit
ensenar compara -1 --revision --retorno omit
lenguaje compara 23 gamma --retorno omit
guardar
detener
salir
```

Ésta reproduce la clase de operaciones ya ejecutadas, pero nuevas consultas y condiciones pueden producir otro resultado: no es una tabla de respuestas. En la prueba diagnóstica la suma seleccionó físicamente la vía externa, que produjo el JSON con 25. No se atribuye esa aritmética al cálculo nativo en ese caso. La docencia `compara -1` fue una revisión deliberada; después la forma seleccionó consulta de GAMMA, cuyo signo + se obtuvo mediante el lector RAW. El operador indicó el contexto.

`--retorno omit` omite la consecuencia material común del procedimiento en ese ensayo; no elimina suministros genéricos ni transforma una enseñanza explícita en retención. El retorno ordinario es `real`, salvo que el operador solicite el control omitido. La modalidad es parte de la experiencia declarada.

## Continuar la misma copia en otra sesión

Vuelva a ejecutar el mismo script con `--vida`, no `--nueva`:

```powershell
& 'D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\_dcs11_env_20261020_002458\Scripts\python.exe' -I -B -X utf8 '.\sistema\app\usar_dee.py' --vida MI_APD03_01
```

Después:

```text
estado
reanudar
lenguaje compara 23 gamma --retorno omit
guardar
detener
salir
```

La prueba real usó `DIAG_APD03_UI_R01`, una sola importación, dos propietarios secuenciales y los cortes T550353 y T550490. Antes de nuevas entradas en el segundo proceso coincidían N, tick, RAW, clocks y el testigo serializado del protocolo externo. Los metadatos de identidad documental pueden cambiar; no se afirma identidad byte a byte de todos los snapshots.

Tras `detener`, `continuar` permite cargar otra vez esa misma vida dentro de la sesión, en pausa. `reanudar` vuelve a permitir evolución. `salir` solicita STOP al propietario que pertenece a la sesión; no termina procesos ajenos.

## Peticiones pendientes o inciertas

Cada interacción imprime su ID y el recibo real. Si vence una espera, no vuelva a enviar la misma tarea con otro ID. Use:

```text
resultado ID_QUE_YA_APARECIO
```

`resultado` consulta ese identificador; no reejecuta el trabajo. Si la petición continúa pendiente, su identidad y hash permanecen en el protocolo. Una ausencia de fila no se convierte en una ejecución exitosa ni autoriza un reenvío automático. Un efecto incierto bloquea nuevas entradas y reanudación hasta examinar los recibos preservados. El programa no regresa silenciosamente a un checkpoint favorable.

## Otras órdenes implementadas y su asistencia

`ayuda` enumera los argumentos admitidos por esta versión. También existen `pausar`, `exportar`, `lenguaje`, `acumular`, `componer`, `meta`, `meta-paso` y `evento`. La revisión N0 comprobó su transporte literal; no todas estas variantes fueron ejecutadas nativamente durante la prueba breve UI.

- `ensenar`: el operador da explícitamente la señal y si es revisión; no es adquisición sin docente.
- `lenguaje`: el operador indica una forma, un dato y un contexto; no es español libre ni selección autónoma de memoria.
- `componer`: el orden de formas lo escribe el operador; no se acredita un plan aprendido por recibir esa lista.
- `meta` y `meta-paso`: presentan hechos y oportunidades al aparato preparado. El código físico elige la acción en su dominio; el calendario no es iniciativa cognitiva.
- `evento ARCHIVO.json`: transporta las situaciones literales contenidas en un JSON del operador. No calcula orden, respuesta, ruta ni utilidad. El contrato del gestor decide si los modos son admisibles. Un archivo con situaciones APD03 todavía candidatas no se vuelve operativo sólo porque exista esta orden.

## Distribución: qué falta en este corte editorial

### Ampliación literal APD03 todavía candidata

En `LAB/entrada/usar_dee.py` hay una revisión candidata `APD03.single_terminal.R03.typed_contextual_candidate`, no la versión R02 utilizada en la prueba UI anterior. Añade seis comandos mediante transporte literal, sin calcular una acción ni seleccionar el próximo paso. Las 35 pruebas N0 de esta revisión siguen siendo mocks; su instalación y prueba nativa se deben confirmar antes de presentarla como disponible.

```text
admitir-apd03 --consecuencia local_useful
ensenar-nueva luma -1
lenguaje-nuevo luma 23 gamma
objetivo diferencia 19 6 --contexto-ambiente 1
paso 1
panel --nuevas --memorias
```

`admitir-apd03` prepara posibilidades generales y declara el criterio de consecuencia; no enseña una respuesta ni reinicia una anatomía ya admitida. Su alternativa `file_only` mantiene otro criterio de utilidad explícito, no una reparación automática.

`ensenar-nueva` admite únicamente las dos formas genéricas finitas `luma` y `nara`, signo explícito ±1 y `--revision` cuando corresponda. No las interpreta como palabras españolas ni permite un diccionario oculto. `lenguaje-nuevo` transporta forma, dato y contexto del operador.

`objetivo` transporta los dos hechos ambientales y su visibilidad; `--oculto` indica que el segundo no está inicialmente observado por el participante. `--contexto-ambiente` transporta un bit0/1, no la acción conveniente. `paso 1..4` ofrece oportunidades, no una lista de acciones. El contexto de la consulta y el dato público de ausencia son aportes preparados declarados.

`panel` es una **sonda material**, no la observación pasiva de `estado`. Sus opciones solicitan incluir formas nuevas y/o memorias: un panel puede consumir recursos o modificar el paisaje. No lo ejecute constantemente para tranquilizar al auditor. Las órdenes heredadas `usar`, `meta` y `meta-paso` conservan sus modos APD02: no se retargetean silenciosamente a otra función.

Las filas literales son `apd03-admitir`, `apd03-docencia`, `apd03-lenguaje`, `apd03-tarea-iniciar`, `apd03-paso` y `apd03-panel`. La admisibilidad final pertenece al contrato/actor instalado, no a la interfaz. No se debe ejecutar este ejemplo en una vida que no admita el aparato ni declarar aprendidas sus formas por incorporar el código.

La prueba aquí descrita pertenece al sistema original. El nuevo Full y la acción propuesta `INICIAR.bat usar` todavía no están certificados en este borrador. No publique ese comando como disponible hasta que el cierre incorpore el delta con el actualizador existente y pruebe el ZIP exacto. La futura configuración debe apuntar al corte APD03 seleccionado, no abrir por accidente el activo histórico o el padre anterior.

La distribución no debe depender de las rutas absolutas del equipo del autor. La ruta extensa mostrada arriba sólo identifica el intérprete realmente utilizado en la prueba original; no es una dependencia que deba conservar el colaborador.

## Evidencia y límites

Localizador original: `evidencia/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/ENTRADA_NATIVA_R01/`.

Recálculo: `laboratorio/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/entrada/CIERRE_ENTRADA_UI_R03/`. Comprueba 10/10 solicitudes completadas —cuatro materiales, seis controles— y 50/50 entradas Native aplicadas, sin rechazos. Reconstruye cinco lectores desde 238 observaciones RAW y verifica el archivo real. Sus 1822 comprobaciones son cálculos archivados, no 1822 ensayos físicos.

No se afirma lenguaje general, selección autónoma de tarea o contexto, metaaprendizaje, dominio NSM65, estabilidad ilimitada ni energía medida. La interfaz es una contribución de instrumentación y usabilidad; las capacidades pertenecen a las vidas donde sus experiencias y usos están documentados.
