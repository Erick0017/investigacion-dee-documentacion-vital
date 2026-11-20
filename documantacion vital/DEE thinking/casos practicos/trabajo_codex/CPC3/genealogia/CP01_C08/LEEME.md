# Casos prácticos 01: ocho campos DEE

Proyecto: DEE Universe / INVESTIGACION DEE. Autor: Ivan Erick Tlaltecatl Morales.

Esta entrega contiene los ensayos ejecutados con DEE thinking **3.5.0**, kernel **v27** congelado, los controles, el código, una interfaz de sesión y checkpoints. Los datos son acontecimientos sintéticos; no mediciones de sensores reales. No se modifica ni se publica una nueva versión del producto.

## Instalación local

Requisitos: Windows x64, CPython 3.13 estándar de 64 bits y las dependencias del WHL oficial. No se necesita un LLM, internet ni un toolchain C++ para usar esta entrega. El WHL y sus avisos originales están en `runtime/`; no se ha añadido una licencia nueva. Los entornos virtuales usados en las pruebas no se incluyen.

Extraiga el ZIP. Desde la carpeta `CP01_8_CAMPOS`, por ejemplo:

```powershell
py -3.13 -m venv .venv_usuario
.\.venv_usuario\Scripts\python.exe -m pip install --no-index .\runtime\dee_thinking-3.5.0-cp313-cp313-win_amd64.whl
.\.venv_usuario\Scripts\python.exe -I -B .\conversar.py --work .\mi_sesion
```

El nombre `.venv_usuario` es sólo un ejemplo para el usuario; ese entorno no forma parte del ZIP. `runtime/PROVENANCE.json` y `resultados/INSTALLATION_PROBE.json` identifican el motor realmente utilizado. El wheel tiene SHA-256 `721d4ad1610d6efc7e7101b49b9d68c6925efdcf596361aca09aabd0e315bcaa`. La implementación integrada no delega en `dee_universe_v27`.

## Conversación experimental

La interfaz es un protocolo finito de señales, no conversación en lenguaje natural. El parser transporta comandos; no decide las respuestas. `s0` codifica carga 13 y `s1` carga 17. Esta asignación reside en la interfaz externa; no es un significado aprendido por el cuerpo.

Comandos admitidos:

| Comando | Operación real |
| --- | --- |
| `nuevo [slots]` | Preparación nueva, visible; 2–32 slots, por defecto 16. |
| `experiencia cue ref0 ref1` | Cuatro entradas físicas emparejadas a tick 0. El recorrido demostrado usa cue=0. No escribe un parámetro en la memoria. |
| `senal s0 [slot]` / `senal s1 [slot]` | Sonda física a dos vías de la misma organización; puede cambiarla. |
| `encuentro carga [slot]` | Acontecimiento físico externo, carga representable 0–65535; funcionalidad sólo demostrada en los dominios del informe. |
| `avanzar ticks` | Evolución hacia el futuro; máximo 2048 ticks por llamada, no avance oculto ilimitado. |
| `observar` | Lectura pasiva. Distingue puertos actuales y captura anterior explícitamente archivada. |
| `entorno on` / `entorno off` | Activa/desactiva la generación de futuros retornos del hábitat externo. No borra los ya programados. |
| `guardar ruta` | Snapshot nativo integral más metadata de la sesión y el hábitat. |
| `cargar ruta` | Continúa un snapshot existente; no reinstala el cuerpo. |
| `salir` | Cierra la interfaz. |

Las rutas relativas de guardar/cargar se resuelven respecto a `--work`. Las cargas inválidas, símbolos desconocidos, slots usados o pasados y comandos no gramaticales se rechazan explícitamente. El recibo Scheduled no significa Applied: los frames conservan el recibo efectivo después del avance. Una entrada cero tiene presencia física y no equivale a ausencia.

La arquitectura de sesión tiene dos relaciones móviles en **un Runtime N=34**. Sus rutas de consulta están declaradas antes de T0: slot k se presenta en tick `6+5k` y se observa en `11+5k`. Las posiciones siguen el desplazamiento toroidal previsto del recorrido publicado. No hay recolocación de materia o sensores después de observar una respuesta. Es seguimiento de segmentos conocidos, no certificación de genealogía arbitraria después de cualquier colisión.

El hábitat externo tiene recurso inicial 3 y una ley declarada:

```text
recurso_siguiente = (recurso_actual + carga_nativa_medida_en_via0) % 31
```

La salida DEE altera ese recurso virtual; el recurso puede volver como acontecimiento físico al siguiente slot. La ley no consulta targets de entrenamiento ni escribe la memoria o los clocks. Es **acoplamiento externo en sandbox**, no una demostración de autonomía de un mundo DEE cerrado. Nunca controla dispositivos reales.

Ejemplo inicial:

```text
nuevo 16
experiencia 0 12 16
avanzar 6
senal s0 0
avanzar 5
observar
guardar mi_ente.deetsnap
```

La salida medida es 25/29. Después de consultar, no se reconstruye la organización para restaurar un estado anterior. Para más contactos se utiliza otro slot de la misma continuidad. Al agotarse los slots, la aplicación informa el límite; no hace un reinicio invisible. La calibración emparejada inicial sólo está admitida en tick 0; nuevas experiencias posteriores utilizan `encuentro` o el retorno del entorno.

## Sesión por archivo y reproducción

```powershell
.\.venv_usuario\Scripts\python.exe -I -B .\conversar.py --events .\casos\C08_SESION_REPRODUCIBLE.txt --work .\otra_sesion --transcript .\otra_sesion\transcripcion.json
.\.venv_usuario\Scripts\python.exe -I -B .\src\reproduce.py --package . --output .\reproduccion_dirigida
```

El segundo comando crea físicamente una calibración C02, consulta q=17 y obtiene 29/33. También restaura `casos/C08_INTERFACE_V2/C08_MAIN_FINAL.deetsnap` en tick 26, presenta una nueva señal y **evoluciona** a tick 31, obteniendo 106/110. No lee respuestas desde una tabla ni se limita a cargar un snapshot terminal.

Para repetir un caso completo en otra carpeta vacía:

```powershell
$deePython = (Resolve-Path .\.venv_usuario\Scripts\python.exe).Path
& $deePython -I -B .\ejecutar.py --python $deePython --reproduce-case C02 --output C:\ruta\vacia\repeticion_C02
```

`--python` debe ser una ruta absoluta cuando el proceso cambia de carpeta. Por ejemplo use `(Resolve-Path .\.venv_usuario\Scripts\python.exe).Path`. Las salidas de reproducción deben estar fuera de este paquete y no contener datos previos. Cada proceso reproducido tiene timeout 240s y sólo se termina su árbol propio. `C07` reutiliza C05: para repetirlo independientemente debe aportar los datos de C05 en su carpeta; el contraste reservado reutilizable se ejecuta con la herramienta siguiente.

```powershell
.\.venv_usuario\Scripts\python.exe -I -B .\src\causal_lab.py --snapshot .\casos\C05\TRANSFER_IN_FLIGHT_12.deetsnap --spec .\casos\INTEGRATIONS\CAUSAL_PANEL_SPEC.json --output .\diagnostico.json
```

Este diagnóstico crea forks independientes, corta sólo el RAW declarado, conserva el clock y prueba una consulta común. MAIN no cambia. Es una herramienta del investigador, no introspección del ente.

El modo original de `ejecutar.py` reanuda la campaña bajo `CAMPAIGN_BUDGET.json`, salta los resultados ya concluidos y **no reinicia** el presupuesto de tres horas. No utilice `--retry` para alterar esta evidencia sellada. La reproducción explícita es una ejecución técnica nueva en otra carpeta, no continuación ni nueva réplica científica independiente.

## Dónde está la evidencia

| Ubicación | Contenido |
| --- | --- |
| `casos/EXPERIMENT_CONFIG.json` | Preparaciones, controles, criterios y reservas congeladas. |
| `casos/C01` … `C07` | Resultados, recibos y snapshots del campo. |
| `casos/C08` | Intento inicial conservado con sondas rechazadas; no se usa como demostración funcional válida. |
| `casos/C08_INTERFACE_V2` | Preparación corregida, contraste reservado distinto, snapshots y sesiones. |
| `casos/INTEGRATIONS` | Puente nativo online, retorno repetido, retención 500, dominio fásico y diagnóstico reservado. |
| `casos/SATURATION_OBSERVERS` | Comparación de RAW/clocks y consulta posterior bajo saturación. |
| `casos/VALIDACION_DIRIGIDA` | Baselines, backends, observación y persistencia. |
| `resultados/TRANSCRIPCION_C08_REGISTRO_V2.json` | Transcripción cronológica corregida; las lecturas antiguas no se modifican por referencias mutables. |
| `resultados/ACTUAL_RECEIPT_AUDIT.json` | Recibos nativos reales recuperados de snapshots, incluidas entradas pendientes. |
| `resultados/RELECTURA_CORRECCIONES.json` | Cambios de lectura explícitos sin borrar el resultado previo. |
| `evidencia/` | Fuentes pertinentes, procedencia y versiones exactas anteriores a hotfixes. |
| `resultados/supervision/` | Comandos, códigos de salida, stdout/stderr y timeout por ensayo. |

`INFORME_CIENTIFICO.md` explica los alcances. `MATRIZ_RESULTADOS.json` vincula las ocho preguntas con sus métricas y archivos. Hay 14 registros de caso, incluyendo discovery, validación, análisis y un intento inválido: **no son 14 capacidades ni 14 réplicas independientes**. Un ensayo compartido no se cuenta dos veces por servir a varios campos.

## Verificación y cierre

```powershell
py -3.13 -I -B .\src\package_verify.py C:\ruta\CASOS_PRACTICOS_01_DEE_THINKING_3_5_0_8_CAMPOS_RESULTADOS.zip
```

El verificador comprueba CRC, inventario, SHA-256, wheel, runners, configuración y checkpoint. `MANIFEST.json` excluye su propio hash; `HASHES.sha256` excluye a sí mismo y al manifiesto. El hash del ZIP cerrado se publica fuera del ZIP. `finalizar.py` reempaqueta los mismos archivos sellados sin repetir la ciencia y sólo publica mediante reemplazo atómico. Las comprobaciones nativas están documentadas separadamente: un CRC correcto no prueba una función.

La campaña registró inicio/deadline y contador monotónico en su primer comando. Cada llamada potencialmente larga se ejecutó en un hijo supervisado. El guard independiente y el observador de cierre comparten ese presupuesto original, terminan exclusivamente procesos propios identificados y no relanzan simulaciones. El cierre de esta entrega deja todos esos procesos detenidos.
