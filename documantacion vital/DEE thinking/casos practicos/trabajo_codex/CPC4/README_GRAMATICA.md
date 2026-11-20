# Demostración lingüística finita CPC4

Esta aplicación usa DEE thinking4.0.0 y su kernelv27 congelados. No importa CPC3,
SEM01 ni sus resultados. El catálogo NSM es una referencia documental: consultar
65fichas no equivale a aprender65significados. Las formas HAY y NO se estudian
sólo como dos asociaciones físicas a presencia/ausencia de un recurso en una
ventana declarada; no se afirma semántica universal existencial o de negación.

## Instalación y ejecución

Use CPython3.13 estándar Windows x64 con el WHL4 incluido en `runtime/`, instalado
sin modo editable en un entorno propio. No se distribuye un entorno virtual.

```powershell
py -3.13 -m venv .venv_usuario
.venv_usuario\Scripts\python.exe -m pip install --no-index runtime\dee_thinking-4.0.0-cp313-cp313-win_amd64.whl
.venv_usuario\Scripts\python.exe -I -B demostracion.py --salida sesion_nueva
```

Modo reproducible: añada `--eventos casos\dialogo_principal.txt`. La salida debe
ser una carpeta nueva. `--cargar ruta.deetsnap` restaura explícitamente al inicio.
`--python` permite indicar otro CPython3.13 con el mismo WHL oficial instalado.

El programa conserva un único proceso trabajador y un único Runtime MAIN en
RAM entre las órdenes. Cada llamada tiene timeout120s y un Windows Job propio;
si vence se termina sólo ese proceso y sus descendientes. El uso futuro de la
demostración no depende del deadline de la campaña que la produjo.

## Gramática real

```text
crear
crear semilla 23
vivir - coherente -
enseñar HAY
diagnóstico
enseñar NO
consultar HAY
consultar NO
nombre zuvi W1
observar
vuelve a observar
guardar "ruta con espacios\sesion.deetsnap"
cargar "ruta con espacios\sesion.deetsnap"
catálogo
catálogo hay
catálogo NSM65.NOT
por qué
ayuda
salir
```

`vivir` admite signo A `+` o `-`, política B `coherente` o `invertida`, y signo
del contexto ambiental `+` o `-`, en ese orden. Son condiciones explícitas del
protocolo de experiencia; el programa no calcula una respuesta nativa a partir
de sus textos. La semilla sólo elige una traslación toroidal común: no selecciona
historia, teacher, significado, respuesta ni decoder. Una traslación nueva no es
por sí sola una nueva capacidad validada.

No se reinicia silenciosamente una instancia existente. Para una nueva
preparación termine la sesión y abra otra; `crear` dentro de un MAIN ya existente
se rechaza. `cargar` sí es una sustitución explícita pedida por el usuario.

## Continuidad y dominio físico

1. `crear` instala la preparación Research vacía N67 y35interfaces antes deT0.
2. `vivir` presenta experiencias mediante esas interfaces, produce el mensaje
   nativo A→B y deja evolucionar consecuencias hastaT169 en la misma continuidad.
   A es un núcleo emisor adquirido; B es una organización receptora distribuida
   en dos regiones. No se afirman dos cuerpos basales plenamente renovables.
3. Primera enseñanza: el sensor externo fijo lee el recurso actual de la rama
   plus enT169. Segunda: lee el recurso actual de la rama minus enT197. El mismo
   report físico se presenta a ambas regiones léxicas, y sólo la forma coincidente
   entra por su interfaz. No se almacena una tabla palabra→función en el ente.
4. Las dos formas se pueden presentar HAY,NO o NO,HAY. Las consultas físicas son
   finitas y siguen ese orden: señales enT236/264 y lecturas enT239/267. No se
   añaden memorias, clocks ni suministro para prolongar la conversación.
   La confirmación NO,HAY y su reserva conservaron la primera respuesta NO,
   pero la segunda HAY no tuvo expresión válida pese al recibo aplicado.
   No se reajustó ese orden después de verlo: no es un dominio robusto prometido.
5. `observar` es pasivo y no consume un turno. Las consultas sí evolucionan y
   pueden transformar los portadores; después de dos consultas termina este
   protocolo. Otras peticiones se rechazan, sin recrear al individuo.

W1/HAY y W2/NO son sólo códigos de forma. El decoder fijo exige recibo aplicado,
semantic1, actividad, carga21 y dirección(-1,+/-1,0). Puede devolver presencia,
ausencia o indeterminación. La misma forma HAY puede responder AUSENTE bajo una
historia opuesta; la interfaz no altera esa emisión para hacerla concordar con
el español. Entrada rechazada no equivale a olvido ni respuesta cero.

La relación se mantiene64ticks antes de la sonda y se expresa67ticks después de
su adquisición:172→236→239 y200→264→267. Una respuesta a una palabra no es lo
mismo que emitir esa palabra ante una situación.

## Diagnóstico explícito y observadores

`diagnóstico` sólo se admite enT172 después de enseñar HAY primero, antes de la
segunda enseñanza. Genera tres copias completas secuenciales: referencia,
eliminación localizada de la relación W1 y sham del portador13. Todas reciben
la misma segunda experiencia y el mismo panel físico. Muestra respuestas,
recibos, edición realizada y conservación del padre. Nunca sustituye MAIN por
un fork, no repara al individuo y no es introspección. MAIN permanece enT172.

`observar` y `vuelve a observar` leen el mismo MAIN sin avanzar: O1 en los puertos,
O2 en campos enteros y O4 en grafos toroidales a escalas1,2,4,8. La captura está
limitada a256registros RAW no nulos y declara truncamiento. Incluye dirección,
actividad, semantic y clocks enteros. Los grafos no son genealogía certificada,
necesidad causal ni homología persistente. Se verifica que observar conserva
RAW, clocks y tick.

## Persistencia y atribución

Guardar conserva Runtime físico, RAW, clocks, tick, canales, recibos y metadatos
neutrales de fase, orden de formas y alias externos. No conserva una tabla de
clases para contestar. Cargar valida fase/tick,35interfaces y su geometría,
aliases normalizados, Runtime no pausado y ausencia de entradas externas pendientes en los límites
quiescentes publicados. Una carga rechazada no reemplaza MAIN.
Las consultas comprueban el tick realmente alcanzado antes de inyectar y leer;
un Runtime pausado no produce una respuesta nominal ficticia.

La respuesta guarda junto al texto el RAW actual y recibo físico. Etiquetas:

- ENTE: emisión física actual admisible bajo el decoder declarado.
- GENERADOR_EXTERNO: sensor actual y experiencia por una interfaz externa.
- INSTRUMENTO: observación/diagnóstico del investigador, no introspección.
- INTERFAZ: parser, alias, persistencia o rechazo de una orden.
- EXPLICACION_DOCUMENTAL: catálogo NSM o explicación externa del mecanismo.

La consulta de palabra sola activa una auditoría Python de aperturas que rechaza
lecturas de resultados, logs, staging y fuentes CPC3/SEM01. Es una comprobación
instrumental de `open`, no un sandbox del sistema operativo ni intercepta
`fopen` nativo. Los testigos físicos y la reproducción independiente se enlazan
en el resumen de la campaña; no se cargan para generar respuestas.

## Acceso inverso: extensión instrumental, no MAIN autónomo

El primer intento situación→símbolo no produjo símbolos: se conservaron tres
trayectorias y dos cortes no aplicables, sin fabricar memoria para lesionarla.
Un rescate ambiental diagnóstico removió sólo un teacher11 no emparejado y
conservó la relación W1, pero la sonda colineal fue rechazada por ocupación.

El método2 es otro protocolo de acceso, congelado antes de ejecutarse. Usa
puertos outcome ya existentes antes deT0, una sonda5 transversal idéntica en
ambas regiones y otro decoder estricto: sólo26vertical, nunca5o21. HAY fue
seleccionado físicamente después del rescate y en una preparación fresh
reservada con el mismo rescate; el corte de la memoria suprimió esa selección.
El original sin rescate no emitió símbolo. Se registra como
DIAGNOSTIC_RESCUED/NOT_NATIVE_MAIN, con sensor externo actual. No modifica el
producto4.0 ni instala un conversador general; no demuestra emisión autónoma de
MAIN, emisión de NO o composición semántica NSM.

## Evidencia ejecutada y reproducción portable

- `resultados/demo02/DEMONSTRATION_SUMMARY.json`: crear→experiencia→comunicación→
  enseñanza→consulta opaca W1 en239; otro proceso carga239 y responde una pregunta
  nueva NO en267. RAW/clocks/tick finales coinciden con la referencia científica.
- `resultados/DEMO_DIAGNOSTIC/RESULTS.json`:10comprobaciones del comando diagnóstico;
  MAIN172 preservado. La preparación de este test sólo añadió metadatos UI
  neutrales a un snapshot172 ya medido, sin cambiar su estado físico.
- `resultados/DEMO_CONTRACTS/RESULTS.json`:13comprobaciones de carga, admisión,
  entradas pendientes, datos corruptos y límites, sin evolución futura.
- `resultados/DEMO_PAUSE_AND_OBSERVERS/RESULTS.json`:10comprobaciones de pausa y
  observación O1/O2/O4 pasiva, sin evolución futura.
- `resultados/LANGUAGE_SUMMARY.json`: índice de evidencias y conteos independientes.

Son comprobaciones técnicas y relecturas de trayectorias; no se suman como
réplicas científicas independientes. El intento inicial con incompatibilidad
de codificación IPC quedó preservado en `resultados/demo01`.

Reproducción técnica desde una extracción independiente y entorno4.0 limpio:

```powershell
python -I -B src\demo_validation.py --output "D:\salida_nueva_CPC4" --expected resultados\confirmacion\MAIN_MINUS\MEASUREMENTS.json
```

El validador sustituye sólo `@SALIDA@` en los nombres de archivo de
`configuraciones/demo_principal.txt` y `demo_continuacion.txt`, ejecuta dos
procesos públicos y usa el fixture opcional exclusivamente DESPUÉS para comparar
RAW/clocks. No depende de rutas privadas ni del presupuesto ya vencido de la
campaña para que el usuario ejecute la aplicación. El pico de memoria del Job,
si Windows lo informa, es memoria comprometida medida, no RAM física; los
9,624,416bytes de cuatro buffers son una estimación aparte.
