# Interfaz española DEE thinking 4.0

## Estado de entrega: PARTIAL

El presupuesto original terminó el 14 de octubre de 2026 a las 09:21:05 UTC y no se reinició. La aprobación operativa pendiente llegó después del límite. No se ejecutó BLOQUE II: sus 19 casos principales y cuatro contrastes opcionales quedaron `NO_EJECUTADO_POR_PRESUPUESTO`. Esta entrega no aporta nuevos resultados de adquisición, fenómenos o lenguaje.

El wheel conservado es el build05 real. Los ajustes de cierre posteriores a ese build se conservan separadamente como `UNBUILT_CLOSURE_FIXES` en la evidencia: no se presentan como compilados, instalados o validados dentro del wheel. Los ejemplos y la gramática siguientes describen la superficie implementada/documentada, no una calificación integral de este corte parcial. Los experimentos CPC3 son antecedentes de BLOQUE I, no ejecuciones nuevas de BLOQUE II. Véanse `experiments/EXPERIMENT_REPORT.md` y `experiments/PHENOMENA_AND_LANGUAGE.json`.

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
