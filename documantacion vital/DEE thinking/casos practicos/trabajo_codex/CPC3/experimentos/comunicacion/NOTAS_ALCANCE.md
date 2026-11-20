# Comunicación, asociación y composición: alcance medido

La traducción española de `conversar.py` solicita operaciones y redacta la
emisión actual. No lee el evaluador ni la transcripción para contestar. Los
alias son referencias externas explícitas; no acreditan una asociación
adquirida. Un propietario hijo mantiene el MAIN en RAM durante la sesión;
el padre puede detener sólo ese hijo si un comando supera treinta segundos.

Las pruebas de asociación utilizan dos rutas físicas publicadas de
`mobile_pair`. Las formas opacas identifican esas rutas de modo fijo. La
correspondencia funcional adquirida es el producto físico de cue y referente,
con consultas nuevas sobre esa relación. El mismo decoder devuelve la carga
activa observada: las historias invertidas intercambian las respuestas. No se
ha implementado una tabla arbitraria de significados ni una asociación textual
que pueda direccionar por sí misma cualquier situación del entorno.

La composición prepara `cascade` sin fuentes de entrenamiento y admite las
parejas por interfaces declaradas después de la preparación. Las relaciones se
forman por v27 y la consulta atraviesa ambas etapas en un Runtime. Se conserva
el control de omisión y el orden invertido. La transformación aditiva medida
es composición funcional; no demuestra aprendizaje de sintaxis o gramática.
El orden invertido cambia la salida intermedia (25 frente a 27), pero las dos
salidas terminales coinciden en 39. En reservas, 31/47 frente a 35/47 conserva
esa conmutatividad terminal. No se presenta como una distinción de orden que
esta cascada aditiva no realiza.

Las consultas secuenciales modifican los portadores. En el testigo las respuestas
son 25/29, 42/46 y 51/55. No se sustituyen por las respuestas de la primera
consulta ni se recrea al individuo. Los nombres cambiados sólo prueban que la
traducción externa conserva el mismo aparato, no generalización semántica.

Las reservas se fijaron antes de ejecutarlas en `EXPERIMENT_CONFIG.json`.
Cada caso es una preparación independiente; los ticks dentro de una secuencia
no se cuentan como réplicas independientes. Los oráculos de evaluación no
participan en las operaciones públicas.

## Uso de la interfaz

Desde CPython 3.13 con el wheel oficial instalado:

```
python conversar.py
python conversar.py --eventos experimentos/comunicacion/DIALOGO_EVENTOS.txt --sesion sesion_local --transcripcion DIALOGOS_LOCAL.jsonl
python conversar.py --cargar sesion_local/sesion.deetsnap --json
```

La ruta del segundo ejemplo se publica cuando el diálogo integrado se haya
ejecutado; no sustituye una transcripción por respuestas esperadas. `--json`
muestra campos completos. El modo normal muestra la frase atribuida y los
ticks; la transcripción conserva siempre toda la emisión.

La gramática real figura al escribir `ayuda`. La orden de cargar es una
restauración solicitada por el usuario, no un recurso operativo del lector.
`Instancia nueva` no resetea un MAIN ya activo. Una frase no admitida se
rechaza como mensaje de interfaz. El timeout no restaura un estado favorable.

## Diálogo ejecutado y correcciones técnicas

`DIALOGOS.jsonl` conserva la sesión primaria y su continuación solicitada:
pronósticos False en 37/67/164/293/555; después True en 813 para el objetivo
843. Los errores posteriores al cambio ambiental no se eliminan. La relación
delta era cero tanto en 555 como en 813: no se atribuye la diferencia de
expresión únicamente a delta. Los controles de continuidad se encuentran en
el frente nativo correspondiente.

En la primera continuación el guardado con ruta personalizada falló: el parser
no reconocía el acento de «sesión» y el binding congelado utilizó un nombre
Windows estrecho, produciendo `la sesiÃ³n en sesion_actualizada.deetsnap`.
Se conservan el archivo, el mensaje y la gramática ejecutada anterior. La
corrección acepta el acento y adapta únicamente los nombres no ASCII mediante
un archivo temporal ASCII y copia de bytes. No modifica el kernel ni el wheel.

`DIALOGOS_REPLAY_TECNICO.jsonl` repite una vez la continuación 555→843 para
verificar el guardado corregido; no es una nueva muestra independiente.
`DIALOGOS_LOAD_CHECK.jsonl` carga 843 y formula una pregunta nueva para 873,
avanza el Runtime y guarda el estado de 873. Las operaciones de restauración
son explícitas; no constituyen el lector ni un fallback operativo.

## Perfil de comparación central

```
python conversar.py --perfil comparacion
python conversar.py --perfil comparacion --eventos experimentos/comunicacion/DIALOGO_COMPARACION.txt --sesion mi_comparacion --transcripcion mi_comparacion.jsonl
python conversar.py --perfil comparacion --cargar mi_comparacion/comparada.deetsnap
```

Este perfil inaugura una preparación independiente en un único Runtime. No
fusiona el MAIN de continuidad con otro mundo. Tiene un solo episodio pendiente:
expectativa física en 37 para el objetivo 83; `compara esto con lo anterior`
observa la consecuencia real en 83, la codifica independientemente de la
expectativa y obtiene el marcador DEE en 84. El mismo MAIN se guarda y restaura
antes de ese encuentro en el diálogo real `DIALOGOS_COMPARACION.jsonl`.

La respuesta de comparación utiliza `comparison_decoder` y el marcador actual,
con expectativa representada y recibo aplicado. El signo de discrepancia no se
traduce como otra predicción de llegada/ausencia. Después del encuentro el perfil
devuelve `OUTSIDE_FORECAST_DOMAIN`, no fabrica una respuesta renovada ni instala
otro cuerpo. El perfil se conserva en el snapshot y en el estado textual; un
perfil incompatible se rechaza antes de sustituir un MAIN vivo. La operación
`source` permanece no implementada en este perfil, sin decisión Python oculta.

## Perfil de revisión finita de fuente

```
python conversar.py --perfil politica
python conversar.py --perfil politica --eventos experimentos/comunicacion/DIALOGO_POLITICA.txt --sesion mi_politica --transcripcion mi_politica.jsonl
```

Se prepara otro individuo N67; no se injerta ni se fusiona con el MAIN N47.
El diálogo real conserva una sola MAIN y su restauración explícita en tick6:
observación externa en2 → comparación física en6 → política modificada →
acción actual hacia Q en11 → dato recibido por esa ruta en14. La pregunta
«qué fuente necesitas observar» describe esa acción actual, no consulta los
campos privados de utilidad/verdad ni atribuye necesidad introspectiva.

La regla de preservar P ante coincidencia y cambiar a Q ante discrepancia es
parte de la preparación declarada; la experiencia determina qué transformación
física ocurre. No se presenta como una regla general de utilidad adquirida ni
como una revisión indefinidamente reutilizable. La señal recibida es una clase
explícita presente, no una ausencia inferida por timeout Python. El perfil no
exporta un pronóstico; pedirlo da un aviso INTERFAZ. Después de la ventana11,
la pregunta de fuente tampoco reproduce una respuesta histórica.
