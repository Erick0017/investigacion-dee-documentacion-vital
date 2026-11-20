# Aplicación experimental CPC9

Ejecuta una preparación nueva real de `IntegralLifeSession` sobre el WHL oficial
4.5/v27. Es un instrumento con comandos JSON, no conversación libre, ni una
transcripción histórica. No importa targets, mapas de enseñanza, evaluaciones o
informes como memoria del participante. Los nombres de puertos seleccionados
por la persona no se presentan como atención o consulta autónoma del ente.

## Instalar y empezar

Requiere Windows x64 y CPython3.13 x64 previamente instalado. No descarga nada.
Desde la raíz del expediente:

```powershell
py -3.13 tools/preparar_entorno.py
.\.runtime_cpc9\Scripts\python.exe -I -B ejecutar.py demo --out runs/mi_demo
.\.runtime_cpc9\Scripts\python.exe -I -B ejecutar.py demo --control-no-order-a --out runs/control_sin_A
```

También: `./iniciar_cpc9.ps1 -Modo demo`. Si falta el venv local, lo prepara
offline con el WHL incluido y comprueba hashes. No sobrescribe otro venv ni un
directorio de salida existente. Los venvs generados no pertenecen al paquete.

En la máquina de validación, WindowsPowerShell bloqueó la ejecución del `.ps1`
por su política de seguridad antes de crear un Runtime. No se cambió esa política.
Si ocurre lo mismo, use directamente los comandos Python anteriores; no hace
falta habilitar scripts ni modificar seguridad para ejecutar la aplicación.

La demo llega por defecto a T606 y muestra el panel de orden actual posterior.
`--until 210` recorta el recorrido: la omisión del acontecimiento temporal A,
programado mucho después, todavía no puede diferenciar los recorridos en T210.
No compare ese control antes de su oportunidad física. Las ventanas son finitas;
un tick no equivale a un segundo de CPU ni a una medida de energía.

## Modo eventos e interacción

```powershell
.\.runtime_cpc9\Scripts\python.exe -I -B ejecutar.py eventos --events app/ejemplo_eventos.json --out runs/mi_secuencia
.\.runtime_cpc9\Scripts\python.exe -I -B ejecutar.py interactivo --out runs/mi_individuo
```

Cada línea interactiva es un objeto JSON. `ayuda` muestra ejemplos y `salir`
termina sin dejar una simulación activa. El fichero por eventos usa
`{"schema":"CPC9.events.v1","events":[...]}`. No admite floats, NaN, claves
duplicadas ni ejecución de código. Sus operaciones son:

- `nuevo`: `identifier` opcional y `options` del constructor científico. Prepara
  soportes/opciones desde T0; no ejecuta automáticamente el currículo.
- `curriculo`: una vez en T0, `params` contiene los parámetros explícitos del
  currículo integral publicado. Pueden cambiar orden, referentes o controles
  dentro de los dominios de sus módulos. El calendario lo inicia el currículo,
  no el participante. Se muestran recibos pendientes, aplicados y rechazados.
- `entrada`/`sonda`: `port`, `payload` uint16 y `tick` exactos. La sonda introduce
  materia. Un puerto es explícito; no hay un buscador externo de respuestas.
- `hasta` con `tick` absoluto; `pasos` con `count`. El límite instrumental por
  defecto es T2000, modificable con `--max-tick`; no amplía la validación física.
- `puertos`, `recibos`: contratos y recibos actuales, sin clasificación semántica.
- `ver`: vista física actual; `path` opcional, por ejemplo `two_memory`,
  `cpc9_query_loop` o `cpc9_current_order`. `observar` usa `site:[x,y,z]` y es
  pasivo. Ninguno convierte una lectura ausente o ambigua en frase correcta.
- `guardar`: `path` relativo a la salida y sufijo `.gz`; conserva mundo, clocks,
  cola y metadatos mediante persistencia oficial. Nunca sobrescribe un archivo.
- `cargar`: `path` relativo a la salida o absoluto explícito. Continuar el
  checkpoint actual conserva la vida. Cargar un pasado después de vivir su
  futuro requiere `allow_branch:true` y se etiqueta como otra rama, no MAIN.
- `evidencia`: `path` relativo a `revision/`. Es lectura **AUDITOR**, nunca una
  entrada al mundo. Limita a 256KiB; para archivos mayores use un editor.

Las etiquetas son **ENTORNO** para acontecimientos solicitados, **ENTE** para
campos/emisiones nativos actuales, **INSTRUMENTO** para operaciones/recibos y
**AUDITOR** para evidencias. No se completa contenido usando un LLM o el log.

## Registro y continuidad

Cada acción queda en `EVENTOS_Y_OBSERVACIONES.jsonl`: petición exacta, antes y
después (hashes RAW/clocks), recibos/observaciones, errores y tiempo real. RAW y
clocks observados permanecen como cadenas exactas. `PROGRESO.json` identifica
el último evento; el diario no es memoria del ente. `RESUMEN_EJECUCION.json`
resume operaciones, no produce un veredicto de mente o dominio semántico.

La persistencia4.5 necesita un temporal ASCII para el binario Windows. Se usa
el temporal del sistema si es ASCII; puede indicarse `--ascii-temp RUTA_ASCII`.
Las salidas/checkpoints pueden estar en rutas Unicode. Un error, rechazo,
ocupación, silencio o lectura cero se presenta como tal, no como conocimiento.

Las recetas son preparadas; las asociaciones y consecuencias provienen de
evolución nativa. Crear este mundo no acredita que todas las capacidades del
archivo histórico o las65 primitivas estén integradas. Consulte la evidencia
de cada capacidad por separado.

El segundo participante y sus rutas están preparados desde T0 en la receta.
Puede presentar sus experiencias o mensajes por puertos existentes sin copiar
su memoria ni añadir un cuerpo entrenado durante MAIN. Añadir una anatomía
diferente constituye otra preparación, no crecimiento nativo de esta vida.
