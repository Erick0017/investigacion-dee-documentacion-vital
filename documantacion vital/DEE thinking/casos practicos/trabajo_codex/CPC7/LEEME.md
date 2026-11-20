# CPC7 — base operativa y evidencia privada

Proyecto DEE Universe / INVESTIGACION DEE. Autor del proyecto: Ivan Erick Tlaltecatl Morales.

Este expediente ejecuta organizaciones nuevas sobre DEE thinking 4.0.0 y v27 congelado. Separa la base operativa de sus generadores y auditores. Los expedientes CPC1–6 permanecen intactos. Comience por `revision/LEER_PRIMERO.md` y `revision/LECTURA_PROVISIONAL.md`: capacidad, evidencia, controles y dominio no son una etiqueta global de «mente».

## Instalación y demostración

Requiere Windows x64, CPython **3.13 estándar x64** y espacio para estados de trabajo. No requiere compilador, NumPy, PyTorch, conexión a Internet ni reconstruir el motor. El WHL oficial incluido se instala sin dependencias externas. Ejecute en PowerShell desde la carpeta CPC7 extraída:

```powershell
.\iniciar_cpc7.ps1
```

El lanzador crea solamente una `.venv` local si falta e instala el WHL incluido mediante `--no-index --no-deps`. La aplicación comprueba versión, procedencia de `site-packages` y SHA-256 del binario. No desactive la política de seguridad de su equipo para ejecutar scripts: alternativamente use los comandos explícitos siguientes según sus permisos.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -I -m pip install --no-index --no-deps .\runtime\dee_thinking-4.0.0-cp313-cp313-win_amd64.whl
.\.venv\Scripts\python.exe -I -B .\ejecutar.py demo --out .\mi_demostracion
.\.venv\Scripts\python.exe -I -B .\ejecutar.py demo-repertorio --out .\mi_revision
```

Cada salida debe ser una carpeta nueva. `demo` ejecuta experiencias, comparación/pregunta física, acceso al repertorio propio, interacción de uso y enseñanza posterior de un signo opaco. Guarda, restaura en otro proceso y después actualizaL03 y consultaL03/L04/L09 en472. `demo-repertorio` muestra adquisición, nueva relación, revisión de L01 con un segundo docente y retención de las otras relaciones del panel. **Son perfiles distintos**, no se concatenan como una sola vida. El ensayo científico integrado de14 consultas tras actualización se identifica en `resultados/integrated_revision/`; la demostración evalúa un panel menor de tres relaciones.

Modo por eventos, con entradas físicas reales y transcripción nueva:

```powershell
.\iniciar_cpc7.ps1 -Eventos .\configuraciones\demo_u0.eventos -Transcripcion .\mi_sesion.json
```

Los archivos de eventos usan rutas relativas al directorio de ejecución. No vuelva a escribir sobre estados de una sesión anterior. El ejecutor de demostración crea su directorio y coordina los dos procesos automáticamente.

## Gramática real

No hay conversación libre ni LLM. `ayuda` muestra estas operaciones:

- `nuevo u0` o `nuevo repertorio`: preparación nueva, sólo si no hay individuo activo.
- `historia AB` / `historia BA`: acontecimientos distintos en el cuerpo de orden de U0, sólo en T0. No selecciona una memoria entrenada.
- `experiencia L03 -1 0`: programa señal opaca y consecuencia observada actual (+1 o -1), por interfaces fijas. Recibo programado no implica aplicado.
- `consecuencia -1`: programa el sensor actual de U0 en T11; no es un flag de error calculado por Python.
- `accion`: ofrece las dos oportunidades físicas comunes de uso en T69. No elige la rama ganadora.
- `ensenar-forma`: presenta todas las señales candidatas en T72, después del acceso en T70, para el encuentro de T75.
- `preguntar-forma 139`: sonda por señal sola; lectura en T142. Muestra bancos físicos y registros, no significados NSM generales.
- `consultar L03,L04,L09 201`: sondas consumibles por las interfaces explícitamente solicitadas; lectura tres ticks después. Este enrutamiento nombrado es de interfaz, no una selección aprendida.
- `actualizar L01 +1 268`: sólo perfil `repertorio`; segundo docente preparado. Otros tiempos pertenecen a investigación fuera de la cadencia publicada.
- `actualizar L03 +1 402`: U0 integrado; consecuencia actual por señal, acontecimiento y segundo docente. Sólo se publica esta actualización finita; no se simula una política de mantenimiento general.
- `hasta 338`: tick **absoluto**, creciente; ventana de interfaz finita hasta T1024.
- `observar L03`, `observar-red`, `recibos`: observación pasiva o estados de admisión.
- `guardar "sesion.deetsnap"`, `cargar "sesion.deetsnap"`: estado físico, cola, canales, recibos y protocolo. Cargar exige no tener otra instancia activa.
- `reiniciar confirmar`: descarta visiblemente la instancia en memoria; no borra archivos.
- `salir`.

Las entradas fuera de gramática se rechazan. Las sondas pueden modificar el individuo. Un rechazo, cero, silencio o lectura fuera del decoder no se intercambian: `respuesta_a_esta_consulta` es nula cuando no hay una respuesta admitida válida.

## Reproducción y revisión

```powershell
.\.venv\Scripts\python.exe -I -B .\ejecutar.py referencia --out .\mi_referencia
.\.venv\Scripts\python.exe -I -B .\ejecutar.py recalcular --out .\mis_calculos
.\.venv\Scripts\python.exe -I -B .\ejecutar.py vida --config .\configuraciones\integrated_revision.json --case-id IR_R607_GUARDED_M1 --out .\mi_reserva
.\.venv\Scripts\python.exe -I -B .\ejecutar.py control --config .\configuraciones\integrated_revision.json --case-id IR_C02_AUX_OFFPATH --out .\mi_control
```

`vida`/`control` ejecutan una preparación identificada; no leen respuestas terminales. El contrato público exige exactamente 16 valores de experiencia. El intento histórico con 17 conserva su evidencia, pero no se acepta silenciosamente en la entrada pública. Los forks históricos requieren su padre y se reproducen mediante sus módulos identificados, no fabricando un individuo nuevo equivalente.

`recalcular` no importa ni ejecuta el motor: vuelve a unir cada consulta observable y cada respuesta primaria con el evaluador **después** de la trayectoria. Comprueba que las métricas coinciden y conserva denominadores. Las fórmulas se describen en `revision/CALCULOS.json` y en `src/comparadores/evaluate_common.py`.

`revision/INDICE_EVIDENCIA.json` distingue preparaciones, continuaciones, forks y reproducciones técnicas. Sus rutas apuntan a `MEASUREMENTS.json`, `TRAJECTORY.json` y las verificaciones primarias, no a capturas de pantalla. Los resúmenes de observaciones no reemplazan RAW/clocks exactos ni las vecindades conservadas en esos archivos.

Los datos son sintéticos de un universo experimental DEE; no son mediciones externas de sensores reales. Ticks del modelo y segundos de ordenador tienen unidades distintas. No se midió electricidad.

## Estados y compresión sin pérdida

En el ZIP, los snapshots nativos se codifican en `.deetsnap.gz` para evitar duplicación de varios GB de buffers. `LOGICAL_STATES_CPC7.json` conserva ruta lógica, longitud y SHA-256 de los bytes originales, además del archivo comprimido. La construcción verifica la descompresión byte-exacta y CRC. `src/snapshot_storage.py` y la aplicación materializan una copia temporal cuando la API nativa necesita un archivo plano; no crean otra receta ni editan campos.

Los documentos históricos, datos adversos y cortes de código usados en intentos corregidos se preservan selectivamente con miembro y hash en `genealogia/`. Los ZIP completos previos no se anidan. Un archivo histórico referenciado pero no incluido no se declara autocontenido; el mapa distingue ese estado.

La comprobación final instala el WHL desde la extracción del ZIP exacto y ejecuta referencia, trayectoria, control y continuación. Su informe `VERIFICACION_FINAL_EXTERNA.json` queda **fuera** del ZIP y contiene el hash exacto probado. Integridad y función son comprobaciones diferentes. El manifiesto excluye su propio hash; el SHA del contenedor se informa fuera.

Si el contenedor supera 20 MiB comprimidos se entregan exactamente dos segmentos `.zip.001` y `.zip.002`, además del canónico. Son bytes consecutivos, no dos ZIP independientes. `transporte_CPC7/PARTES.json` y `REUNIR_CPC7.py` verifican ambos y su reconstrucción. No se prometen límites de descarga de otra aplicación por el mero hecho de dividirlo.

## Alcance y privacidad

La comparación preparada produce una pregunta física condicionada por estados adquiridos; no demuestra una política general aprendida de cuándo/a quién preguntar. Los interceptores son regulación física preparada; su eficacia se contrasta con cortes y shams, no se rebautiza como atención aprendida. Los signos opacos/direccionales y las 65 entradas documentales NSM se contabilizan aparte. Los especialistas coexistentes no se declaran varios compuestos cooperantes sin esa prueba.

Este es un expediente **privado y reconstructivo**. Lea `USO_PRIVADO.md`; no es una edición redactada para terceros. No se publica otro WHL ni se modifica v27. Las propuestas de actualización futura del producto se identifican como propuestas, no como funciones ya publicadas.
