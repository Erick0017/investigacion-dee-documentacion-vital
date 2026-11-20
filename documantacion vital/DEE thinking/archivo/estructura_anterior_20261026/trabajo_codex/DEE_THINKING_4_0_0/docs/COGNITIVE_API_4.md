# API cognitiva nativa 4.0

El producto ejecuta el kernel v27 conservado. Esta API organiza preparaciones,
protocolos e instrumentos finitos; sus nombres no constituyen un dictamen de
mente, consciencia, comprensión general o equivalencia biológica.

Las implementaciones están en `include/dee_thinking/cognitive.hpp`,
`src/cognitive.cpp` y `bindings/cognitive_pybind.cpp`. Python facilita instalación,
gramática y exportación, pero no implementa otra física ni suministra respuestas
desde los resultados CPC3. El expediente histórico sólo se importa en el hijo de
referencia de `validation/compare_cognitive40.py`.

## Una sesión y su MAIN

```python
import dee_thinking as d

session = d.create_session("continuidad", initial_open=False, change_tick=80)
session.sense()                 # Dos experiencias iniciales efectivamente admitidas.
emission = session.predict()    # Lectura física actual, no simulación del objetivo futuro.
session.advance(30)
session.save_snapshot("main.deetsnap")
same_history = d.load_session("main.deetsnap", profile="continuidad")
```

`create_session` prepara una instancia nueva; `load_session` restaura, no vuelve a
preparar el cuerpo. Los protocolos de continuidad y comparación no llaman a
`fork`. Cada objeto administra un `OrganizationalWorld` con un Runtime. Un único
escritor mutable debe utilizarlo; `world` permite investigación explícita, no
autoriza a denominar autónoma una edición externa posterior.

En C++ se usan `CognitiveParameters` y `CognitiveSession::create(parameters)`; se
debe proporcionar `seed_path` del snapshot de referencia. En Python el facilitador
localiza ese recurso incluido en el paquete. La creación C++ comprueba el contrato
estructural de semilla; no recalcula su SHA-256. Para una ruta aportada desde fuera,
el consumidor debe verificar la identidad contra el contrato del producto.
El perfil nativo es `continuity` o
`comparison`; los nombres del facilitador son `continuidad` y `comparacion`.

`advance(n)` usa una duración y `run_until(t)` un tick absoluto. Un recibo
`scheduled` no acredita aplicación: hay que conservar su estado posterior
`applied` o el rechazo real.

## Continuidad, experiencias y lector

La preparación es el cuerpo relacional H0, N=47, tick absoluto 32; su clock local
inicial no es 32. La historia inicial se adquiere presentando acontecimientos
físicos, no escogiendo después un preset AB/BA a partir de la conversación.

- `observe()` es pasivo: panel A/B, delta cuando ambos centros están disponibles,
  soporte, lector, RAW, clocks, dirección y guardas locales. No avanza el mundo.
- `experience("A")` y `experience("B")` presentan carga cero por canales físicos
  fijos. Una presencia de carga cero puede cambiar la dinámica.
- `sense()` presenta observaciones de la barrera externa declarada. Al comenzar
  en T32 introduce un par real de observación y rama de referencia invertida.
  Después usa las fronteras absolutas 163, 292, 554, 812 y 945. Ese calendario es
  parte de la interfaz externa, no una elección temporal aprendida.
- `predict()` realiza la primera sonda física de carga cero sobre MAIN y avanza
  tres ticks. Si fue admitida, las solicitudes posteriores leen el lector actual
  sin restaurar ni clonar la organización. La consulta puede transformar el mundo.

El decoder fijo consulta sólo la actividad y el signo dx del registro actual:
positivo da `[True]`, negativo `[False]`, cero o ausencia da `[False, True]`.
La dirección puede depender de contexto y lector, no únicamente de delta.
`prediction_set` es la presentación externa de ese código, no una tabla de
respuestas ni una probabilidad calibrada. La falta de respuesta no se convierte
en una respuesta numérica cero.

El horizonte predeterminado es 30. Una emisión se registra antes de su objetivo;
la evaluación de un objetivo ya pasado es análisis externo y nunca realimenta
un error al Runtime. El panel declara cobertura hasta tick absoluto 1032; avanzar
más permite medir, pero no amplía por sí solo la validación funcional. Agotar las
cinco ocasiones posteriores produce un estado de límite, no otro cuerpo.

Los orígenes representables son tres enteros en 0–46 y `event_state` un uint32
positivo. Que esos parámetros puedan prepararse no declara funcional toda su
combinatoria. El testigo nuevo de paridad utiliza `(15,15,15)` y estado uno; las
otras preparaciones históricas conservan su propia evidencia. Los horizontes
deben ser positivos y no desbordar uint64; horizonte cero en la API nativa solicita
el predeterminado. Un horizonte distinto no obtiene por ese hecho validación
predictiva adicional.

## Barrera externa y comparación física

La barrera es una ley de entorno externa explícita: una clase booleana por tick,
con inversión opcional en `change_tick`. El sensor codifica su clase actual.
Esto no es un detector nativo de ausencia por timeout, ni aprendizaje de una ley
arbitraria del futuro. La configuración de evaluación es accesible al científico;
no se consulta desde el decoder ni se envía como respuesta futura al ente.

```python
entity = d.create_session("comparacion", initial_open=False, change_tick=80)
entity.sense()
expectation = entity.predict()  # Emisión T37, objetivo predeterminado T83.
measured = entity.compare()     # Consecuencia actual T83, producto nativo T84.
unavailable = entity.predict()  # OUTSIDE_FORECAST_DOMAIN; no recicla el marcador.
```

El perfil declara dos canales diagonales antes de la primera experiencia. En el
objetivo, sólo la clase actual de la barrera elige su código de carga uno. v27
produce el gradiente/marcador; no se calcula una diferencia pronóstico–resultado
para escribirla en RAW. El decoder de comparación conserva registro físico,
representación anterior, admisión y ventana válida. Presenta coincidencia o
discrepancia direccional únicamente en el dominio singleton finito y la ventana
de un tick; después la presentación queda indisponible.

Esta API publica **un episodio** de comparación por preparación. Bloquea otra
expectativa pendiente, la ventana vencida, una representación nativa cambiada o
una expectativa invalidada por otra experiencia. Tras el encuentro no interpreta
el marcador como un nuevo pronóstico. No demuestra comparación y aprendizaje
renovables ilimitados en esta misma arquitectura. El perfil de continuidad y los
perfiles informativos son aparatos distintos; no se fusionan sus resultados.

## Asociaciones y composición adquiridas

```python
relations = d.create_session("relaciones")
relations.train([7, 11], cue=5)
panel = relations.query(13)  # Ambas rutas: respuestas físicas 25 y 29 en este testigo.

chain = d.create_session("composicion", depth=2)
chain.train_all([(3, 9), (3, 11)])
composed = chain.query(13)   # Etapas nativas del testigo: 25 y 39.
```

Esos números son resultados de ejemplo, no valores almacenados por la API. Las
recetas implementan una familia móvil aditiva con rutas declaradas, no un
diccionario semántico arbitrario. Los nombres de las rutas son externos. La
adquisición requiere frontera inicial cero; no reconstruye al individuo para
aceptar otra llamada de enseñanza.

`NativeAssociationSession` usa N=34, dos cargas de referencia y cue representables
en uint16 (0–65535); distingue `paired`, `unpaired` y `omitted`. La lectura de una
ruta concreta es una sonda consumible. Los sitios de respuesta fijos no certifican
por sí solos el seguimiento indefinido de portadores móviles. Para consultas
sucesivas se publica el protocolo móvil con intervalo de cinco ticks y capturas
nativas; sus respuestas posteriores pueden cambiar por el uso anterior.

`create_learnable_cascade` usa N=127 y profundidad 1–8. Las entradas cue/teacher se
declaran antes de T0 y todas las parejas se presentan en esa frontera dentro de
un único Runtime. Las consultas avanzan cinco ticks por etapa. No se copian
outputs entre mundos mediante callbacks. Los controles de omisión son explícitos;
una preparación fuera de contrato no acredita incapacidad universal del kernel.

## Persistencia, copias y observación

La persistencia nativa conserva el Runtime operativo completo de
`OrganizationalWorld`, canales, cola, recibos, recetas y protocolos, más los campos
de sesión: fases, slots usados, lector preparado, expectativas pendientes,
predicciones, muestras, evaluaciones marcadas y metadatos de interfaz. El formato
es binario versionado, acotado y verificado; los uint64 no pasan por float. No se
serializan callbacks Python ni pickle.

`set_interface_metadata` guarda etiquetas externas inertes, no recuerdos DEE:
clave 1–128 bytes, valor hasta 1 MiB, hasta 128 claves y 2 MiB en total. El journal
cognitivo admite 64–262144 entradas (predeterminado 32768); el registro de
predicciones 1–32768 (predeterminado 4096). Un límite se informa; no resetea ni
repara la organización. Los errores se propagan y no se convierten en respuestas.

`fork()` es una copia diagnóstica profunda y explícita: copia Runtime, progreso y
metadatos sin compartir buffers mutables. No se reintegra en MAIN. En C++ la copia
ordinaria de sesión es privada, para impedir alias accidentales con dos protocolos;
se permiten movimiento y fork explícito. `observe` y `TraceSession` son herramientas
del investigador, no percepción de la organización. Agotar el presupuesto de una
traza detiene la captura, no la evolución física.

Los snapshots Runtime v1/v2 y OrganizationalWorld de 3.5 conservan sus loaders.
`CognitiveSession::load_legacy_physical_snapshot` restaura explícitamente el Runtime
físico de un archivo histórico. **No** interpreta silenciosamente el protocolo
JSON de una Entity CPC3 como sesión nativa 4.0. `CognitiveSession.load_snapshot`
requiere su metadato nativo y canales ya declarados; no instala los que falten.
Los facilitadores salvan/cargan rutas Unicode mediante una copia byte-exacta a una
ruta temporal ASCII. La API nativa directa mantiene el límite instrumental de
rutas del build Windows; el usuario debe proporcionar una ruta accesible al loader.

## Evidencia técnica y alcance

`cognitive_tests.cpp`, `test_cognitive_api.py` y los testigos públicos comprueban
adquisición, admisión, lectura, rechazo de reuso falso, persistencia y aislamiento.
La validación dirigida conserva 24 estados completos iguales al recorrido CPC3
3.5, incluyendo MAIN T32–T1032, cuatro encuentros de comparación, adquisición
móvil y cascada online. No son 24 réplicas científicas independientes.

`validation/cognitive_technical_01/TECHNICAL_CHECKS.json` documenta igualdad completa
Dense/Parallel/Lazy en las ventanas declaradas, observación/trace on-off y
continuación C++→Python→C++. Los perfiles no garantizan rendimiento temporal
industrial, selección informativa general, reparación universal, ni comunicación
natural ilimitada. La gramática española solicita operaciones y presenta lecturas
actuales; las frases y alias pertenecen a la interfaz, no a una comprensión
semántica adicional demostrada por esos nombres.
