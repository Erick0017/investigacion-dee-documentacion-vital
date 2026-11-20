# CPC6 Mente DEE integrada

Proyecto DEE Universe. Autor del proyecto: Ivan Erick Tlaltecatl Morales.

CPC6 ejecuta una organización nueva en DEE thinking 4.0.0 con kernel v27 congelado. Integra experiencias de orden, comparación prospectiva, selección física de información, comunicación, dos asociaciones opacas y conservación posterior. Es una aplicación experimental finita; las palabras españolas de esta consola no son conversación libre ni un modelo de lenguaje.

Empiece por `revision/LEER_PRIMERO.md` y `revision/LECTURA_PROVISIONAL.md`. Los datos originales, rechazos y controles están enlazados en `revision/INDICE_EVIDENCIA.json`. Ninguna tabla de resultados alimenta las respuestas de la aplicación.

## Instalación y demostración

Requiere Windows x64 y CPython 3.13 estándar de 64 bits. No requiere compilador, internet, CPC3–5 ni reconstruir el laboratorio.

Desde PowerShell, dentro de la carpeta CPC6 extraída:

```powershell
.\iniciar_cpc6.ps1 -Demo -Semilla 1
```

El lanzador crea un venv local si falta e instala únicamente el WHL incluido, sin índice de red. Para instalar manualmente:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --no-index .\runtime\dee_thinking-4.0.0-cp313-cp313-win_amd64.whl
.\.venv\Scripts\python.exe app.py --demo --seed 1 --salida dialogo.jsonl --snapshot sesion105.deetsnap
```

Para el modo interactivo use `iniciar_cpc6.ps1` sin `-Demo`. La ejecución por eventos acepta un JSON con `{"commands":["nuevo renovada", ...]}` mediante `app.py --eventos archivo.json`. La demostración genera trayectorias nuevas, no transcripciones almacenadas.

## Gramática efectiva

`ayuda` devuelve la gramática completa. Los argumentos son tokens separados por espacios; para guardar/cargar use nombres relativos sin espacios.

| Orden | Operación real |
|---|---|
| `nuevo renovada` | Nuevo U0 con soportes bilaterales, codec Q de dosis equiparadas y suministro remoto de lector |
| `nuevo central`, `nuevo bilateral`, `nuevo simple` | Otras preparaciones explícitas; iniciar otra elimina la referencia de consola, no modifica archivos anteriores |
| `experiencia AB 5` o `experiencia BA 5` | Acontecimientos físicos en T0/1; no preset entrenado |
| `fuentes 1 -1` | Experiencias presentes de P y Q; sus productos se forman nativamente |
| `lector` | Sonda física común en T2 |
| `avanzar 5`, `predecir` | Evolución y lectura de emisión prospectiva T5, horizonte10 hacia T15 |
| `consecuencia -1` o `consecuencia 1` | Sensor fijo de consecuencia actual, solicitado después del pronóstico; entrada física T11 |
| `consultar informacion` | Sondas de acceso T30, lectura T33; alias idénticos se agrupan sin leer el estado |
| `ensenar FORMA_01` | Experiencia posterior al uso nativo; enseñanza física T40→43 |
| `preguntar FORMA_01` | Primera ventana T34..50: estímulo50, respuesta53; perfil renovado añade transporte remoto44ticks |
| `consultar anterior` | Lector físico de historia en T69, sin reenseñar A/B |
| `ensenar FORMA_02`, `preguntar FORMA_02` | Ventana71..77/87; enseñanza80 y consulta90 de expresión histórica renovada |
| `preguntar FORMA_01` desde T105..117 | Segunda oportunidad del perfil renovado: estímulo117, llegada remota161, lectura162 |
| `consultar memoria`, `consultar consolidada` | Instrumentos adicionales94/161; modifican el contexto del lector. No forman parte del perfil remoto reservado y pueden sacar su decoder de dominio |
| `observar` | Lecturas pasivas, campos originales y emisiones disponibles en la ventana actual |
| `guardar sesion.deetsnap`, `cargar sesion.deetsnap` | Persistencia integral; cargar no vuelve a preparar ni reenseña |
| `salir` | Termina la interfaz |

El horizonte interactivo publicado es T0..170. Una entrada tardía u ocupada conserva su recibo; no se despejan puertos, reponen memorias ni corrigen fases automáticamente. Una lectura vacía, un rechazo y una dirección fuera del decoder son estados diferentes. Las consultas pueden cambiar al individuo.

## Continuar la misma sesión

La demo termina en105. En el mismo proceso, o cargando `sesion105.deetsnap` en otro:

```text
cargar sesion105.deetsnap
preguntar FORMA_01
avanzar 162
observar
avanzar 170
guardar sesion170.deetsnap
```

La traducción de T162 conserva su registro físico y el decoder `CPC6.wordbus.late.v2`. La regla sólo clasifica la firma `(v,0,-1)` en esa ventana. No rellena silencios con una respuesta ni generaliza a otra cadencia.

## Reproducción científica y almacenamiento

`ejecutar.py --config configuraciones/R03_WORD_BUS_V2.json --salida resultados/MI_REPRODUCCION` organiza un trabajador supervisado. Omite casos ya completos para reanudar; use otra salida para una reproducción independiente. Durante la campaña respeta el BUDGET original. Para una reproducción expresamente iniciada después del deadline añada `--reproduccion`: usa un timeout local acotado y no altera el registro histórico del presupuesto.

Los checkpoints completos residen junto a cada ensayo. En el ZIP se almacenan sin pérdida como `.deetsnap.gz`, con ruta lógica, SHA y tamaño originales en `LOGICAL_STATES.json`. `Session.load` admite la ruta lógica ausente o el `.gz` y materializa un temporal propio, verificado por CRC, antes de cargar el Runtime. No es pickle ni una receta de reconstrucción. Para herramientas antiguas que exijan archivos planos:

```powershell
.\.venv\Scripts\python.exe src\snapshot_storage.py materialize-all --root . --report estados_restaurados.json
```

Esta descompresión explícita puede ocupar varios GB; no se necesita para la demostración. Los estados originales del workspace se conservaron. El ZIP incluye el WHL una sola vez, fuentes experimentales exactas, configuraciones, resultados adversos y genealogía seleccionada; no incluye venvs ni ZIP históricos completos.

`ENTE` identifica una emisión física; `INSTRUMENTO`, una operación o medición externa; las explicaciones causales del expediente son análisis del investigador. Dos formas opacas no equivalen a dos primitivas NSM generales. Las65 entradas documentadas tienen sus estados y alcances en `revision/NSM65_EVIDENCIAS.json`.

No se modifica el producto4.0 ni se asigna una licencia nueva. Se conserva el artefacto de proyecto suministrado, sus avisos y las identidades de procedencia.
