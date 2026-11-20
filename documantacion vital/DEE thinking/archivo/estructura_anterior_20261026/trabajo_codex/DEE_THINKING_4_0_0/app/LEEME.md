# Interfaz española DEE thinking 4.0

## Estado de este corte reanudado

El corte anterior terminó parcial el 14 de octubre de 2026 a las 09:21:05 UTC, sin ejecutar BLOQUE II. Sus documentos y presupuesto se conservaron. Tras la autorización explícita de continuación se registró `RESUMPTION_BUDGET.json`, sin modificar el presupuesto original, y se ejecutaron 24 casos nuevos bajo el wheel 4.0.0 calificado.

Wheel utilizado: `17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623`. El gate `validation/BLOCK_I_QUALIFICATION.json` identifica binario y módulos instalados. Los fixes que antes quedaron sin construir se incorporaron a este corte reconstruido. Los experimentos CPC3 siguen siendo antecedentes de BLOQUE I, no ejecuciones nuevas de BLOQUE II. Los resultados nuevos y sus límites están en `experiments/EXPERIMENT_REPORT.md` y `experiments/PHENOMENA_AND_LANGUAGE.json`.

Esta aplicación utiliza el WHL 4.0.0 instalado; no importa el laboratorio ni un modelo de lenguaje. Requiere CPython 3.13 x64 estándar. El kernel continúa siendo v27.

```powershell
python -m pip install --no-index .\wheel\dee_thinking-4.0.0-cp313-cp313-win_amd64.whl
python -I -B .\app\conversar.py --perfil continuidad --sesion .\mi_sesion
```

También puede usarse `iniciar_mente.ps1 -Perfil continuidad -Python RUTA_AL_PYTHON`. El launcher no instala ni sustituye productos silenciosamente. Para conocer todos los flags: `python app/conversar.py --help`.

## Un individuo por perfil y sesión

Los perfiles son preparaciones distintas, no órganos fusionados entre sí:

- `continuidad`: cuerpo relacional H0, experiencia mediante A/B, lector MAIN y hábitat externo de paquetes con ley explícita. Las ocasiones publicadas son finitas. La ausencia del paquete se obtiene del sensor externo actual, no de un detector nativo de ausencia por timeout.
- `comparacion`: una expectativa física y una consecuencia observada se encuentran en el mismo Runtime. El marcador de comparación no se reutiliza como otra predicción. Un episodio finito.
- `politica`: individuo N67 con una regla de revisión preparada y fuentes complementarias. Una experiencia selecciona físicamente el estado de política; no se ha aprendido una regla general de utilidad. No implementa pronóstico reutilizable.
- `informacion`: otro individuo N47 con historia A/B física, comparación, acceso P/Q e información posterior dentro de su protocolo finito. No es la fusión de los perfiles anteriores.
- `relaciones`: dos rutas físicas, adquisición por encuentros cue/teacher y consultas consumibles. La familia es relacional aditiva; no implementa cualquier diccionario de significados.
- `composicion`: una cascada nativa de dos relaciones adquiridas dentro de un Runtime. Su consulta compuesta conserva los readouts de las etapas. La preparación y la adquisición no se repiten entre llamadas.

Los dominios exactos, fases, recursos y restricciones están en el contrato del producto. Dimensiones y recetas no son intercambiables. Una medida fuera del dominio no se convierte en una respuesta válida por conveniencia.

## Demostrador de mundo nativo: experiencia y preguntas en el mismo MAIN

`mundo_nativo.py` es una aplicación Research explícita sobre la API pública instalada, no un séptimo preset de `create_session`. Prepara en N47 tres recursos y dos interfaces físicas. El contacto ambiental llega al encuentro con un cue por v27; no se copia un teacher de otro Runtime ni se elige una respuesta desde Python.

```powershell
python -I -B app/mundo_nativo.py --preparacion principal --sesion mi_mundo --eventos app/ejemplos/mundo_nativo_principal.txt --transcripcion mundo.jsonl --json
python -I -B app/mundo_nativo.py --preparacion reservada --sesion mi_reserva --eventos app/ejemplos/mundo_nativo_reservado.txt --transcripcion reserva.jsonl --json
```

Su gramática finita es distinta de la de `conversar.py`:

```text
Instancia nueva
Vive el encuentro
A esto lo llamaremos encuentro diagonal
Presenta consulta13
Guarda pendiente11.deetsnap
Carga pendiente11.deetsnap
Observa respuesta
Presenta consulta19
Guarda pendiente16.deetsnap
Carga pendiente16.deetsnap
Observa respuesta
Muestra el estado
Por qué
Guarda MAIN_FINAL.deetsnap
Salir
```

`Vive el encuentro` deja evolucionar los recursos nativos hasta la ocasión de consulta; no introduce una respuesta aprendida. `Presenta consulta13` solicita la sonda y conserva la cola pendiente; `Observa respuesta` la hace evolucionar y lee el producto físico actual. `Consulta nueva13` combina ambas operaciones explícitas. `Muestra el estado` es pasivo. El usuario no calcula coordenadas, clocks o ticks.

El mismo MAIN principal produjo respuestas físicas 54 y 73 ante 13/19. La realización reservada trasladada produjo 58 y 81 ante 17/23. Esta demostración de interfaz reutiliza la preparación reservada ya medida: no se cuenta como otro holdout físico inédito. Las consultas transforman la relación móvil: no es una memoria inmutable ni una capacidad de conversación ilimitada. Los cortes de contacto o cue del experimento dieron sólo las contribuciones de consulta 13/19; el fundamento de la comparación está en la evidencia, no en el texto del parser.

Para continuar un snapshot pendiente en otro proceso, sin crear un mundo nuevo:

```powershell
python -I -B app/mundo_nativo.py --cargar mi_mundo/pendiente11.deetsnap --sesion continuacion --eventos app/ejemplos/mundo_nativo_continuar.txt --transcripcion continuacion.jsonl --json
```

Guardar/cargar preserva RAW, clocks, cola, recibos y el cursor externo de la interfaz. El loader contrasta receta, geometría, interfaces, preparación, IDs y estados de recibos antes de reemplazar MAIN; un archivo rechazado no activa una preparación de reserva. El código anterior a sus fixes se conserva y las comprobaciones técnicas dirigidas están en `experiments/BLOCK_II/online_application_technical/`.

El nombre humano es metadato externo asignado después de la experiencia; no es un diccionario arbitrario adquirido. `Por qué` explica el contrato como `EXPLICACION_DOCUMENTAL`, no introspección. Las respuestas `ENTE` presentan campos físicos actuales; `INSTRUMENTO` identifica preparación, sondas, admisión y límites. Hay dos sondas consumibles dentro de esta geometría, no renovación ilimitada ni cuerpo basal completo.

El motor vive en un único hijo persistente, con timeout por orden de 60 segundos, configurable hasta 180. La aplicación no reinicia MAIN al agotarse una ventana. Los ejemplos, sesiones y transcripciones están separados de los perfiles cognitivos anteriores; no se fusionan snapshots entre ellos.

## Gramática real

Las órdenes se normalizan por mayúsculas y acentos, pero no se acepta lenguaje natural arbitrario:

```text
Ayuda
Instancia nueva
Observa otra vez
Muestra el estado
Presenta experiencia A
Presenta experiencia B
¿Qué pasará después?
Predice antes de observar
¿Ocurrirá lo mismo?
Compara esto con lo anterior
¿Qué fuente necesitas observar?
¿Qué información llegó?
Avanza el entorno
Avanza 5 ticks
A esto lo llamaremos brisa
Guarda la sesión
Guarda la sesión en sesión.deetsnap
Carga sesión.deetsnap
Continúa desde la sesión guardada
Por qué
Salir
```

`Observa otra vez` puede producir una interacción y avanzar a una ocasión declarada; `Muestra el estado` es una lectura pasiva. `Avanza el entorno` equivale a treinta ticks. No hay reinicios implícitos: otra orden `Instancia nueva` con MAIN activo se rechaza. Cargar es una operación expresa de restauración, no otra preparación.

En el perfil `relaciones`:

```text
Instancia nueva
A la ruta 1 la llamaremos zuvi
A la ruta 2 la llamaremos pako
Enseña relaciones con señal 5 y referencias 7 y 11
Guarda la sesión
Consulta secuencia 13,17,19
```

La secuencia se ejecuta mediante el protocolo nativo de consultas móviles, con intervalo publicado de cinco ticks. Sus capturas son un panel del investigador producido durante esa ejecución, no una tabla de respuestas del entrenamiento. Las consultas pueden transformar el portador y afectar consultas posteriores. El facilitador no inicia silenciosamente una secuencia nueva sobre una anterior.

`Consulta nueva 13` consulta el panel común; `Consulta zuvi con 13` selecciona el puerto físico nombrado. La consulta fija individual tiene su geometría/edad admitida; una solicitud tardía o rechazada no se presenta como olvido. Los nombres seleccionan referencias de interfaz, no escriben resultados aprendidos. Invertir nombres externos y adquirir historias invertidas son tratamientos diferentes.

En `composicion`:

```text
Instancia nueva
Enseña dos relaciones 3,9 y 3,11
A esto lo llamaremos dos trazas
Guarda la sesión en antes_consulta.deetsnap
Carga antes_consulta.deetsnap
Consulta nueva 17
Guarda la sesión en final.deetsnap
```

Todas las contribuciones se presentan antes de la frontera de adquisición declarada. No se instala una relación nueva al consultar ni se recrea el individuo para otra orden. Los números son datos del protocolo físico; el programa no calcula la respuesta que debe producir el mundo.

`¿Cuál llegará primero?`, `Si cambia la ruta` y `Retira mediador` se reconocen como solicitudes distintas, pero sólo llaman una operación si el perfil la publica. En otro caso devuelven fuera de alcance, no una deducción desde metadatos. La API de diagnóstico explícito `diagnostic_fork` continúa disponible para componentes seleccionados por el investigador; la interfaz no borra materia automáticamente para fabricar una explicación.

## Atribución y datos

Cada respuesta se identifica como:

- `ENTE`: presentación fija de un producto físico o una emisión nativa medida.
- `INSTRUMENTO`: preparación, interfaz, admisión, panel temporal, observación o límite de operación.
- `EXPLICACION_DOCUMENTAL`: explicación del contrato; no introspección ni una prueba contrafactual por sí sola.

`Por qué` muestra el alcance documental y una lectura actual. No inventa una causa necesaria. Una comparación física tampoco se decodifica como llegada/ausencia futura. Falta de emisión no equivale a cero.

El modo `--json` muestra la medición completa junto al texto. La transcripción JSONL conserva siempre entradas, atribución, campos físicos, recibos, perfil, hora y PID propietario, aunque la presentación en pantalla sea breve. Un recibo `scheduled` sólo es programación; debe comprobarse `applied` después de avanzar.

## Archivo de eventos y persistencia

```powershell
python -I -B app/conversar.py --perfil comparacion --eventos ordenes.txt --sesion sesion_comparacion --transcripcion dialogos.jsonl --json
python -I -B app/conversar.py --perfil comparacion --cargar sesion_comparacion/sesion.deetsnap
```

El archivo es UTF-8, una orden por línea; las líneas vacías o que comienzan con `#` se omiten. `--preparacion parametros.json` declara parámetros de creación, no respuestas ni código ejecutable. Los flags del perfil son explícitos: cargar con otro perfil se rechaza antes de sustituir MAIN.

El snapshot nativo contiene estado físico y operativo, cola, recibos, progreso, trazas conservadas y metadatos de interfaz. Los alias y el referente textual se guardan en metadatos versionados, sin pickle ni sidecar `.ui.json`. Un alias no almacena una salida. El adaptador de nombres de archivo Unicode copia bytes de un snapshot explícitamente guardado; no modifica RAW/clocks.

El motor vive en RAM en un único proceso hijo durante la sesión. El watchdog de la aplicación limita cada orden a sesenta segundos, configurable a un valor mayor que cero y hasta 180 con `--timeout`. Si vence, termina sólo su proceso propio; no reconstruye MAIN ni devuelve una respuesta anterior. Guarda antes de un recorrido largo para disponer de un punto de continuación explícito. `Salir` cierra el propietario. No quedan mundos simulando en segundo plano.
