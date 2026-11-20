# Preguntas nativas e interfaz: resultados de esta área

El resultado principal es un acceso físico condicionado por el estado: una emisión del cuerpo, adquirida tras experiencias AB/BA, se compara por v27 con un acontecimiento actual; una discrepancia produce una pregunta antes de recibir la información de la fuente. Una coincidencia no produce esa pregunta horizontal. La fuente y el uso posterior se realizan dentro del mismo Runtime. El código no lee una respuesta esperada para elegir qué puerto activar.

Los datos primarios están en cada `MEASUREMENTS.json`, con entradas, recibos, campos físicos, vecindades y snapshots. `AREA_COVERAGE.json` enumera 47 preparaciones, no 47 capacidades. Las reconstrucciones, forks diagnósticos y cuatro continuaciones35→100 se cuentan aparte.

## 1. Comparación y nueva información

`COMPARISON_SUMMARY.json` reúne 12 preparaciones. Los hitos son emisión5, comparación15, pregunta19, contacto24 y uso físico29. En el contraste básico, coincidencia produce0 preguntas y discrepancia1; esa pregunta recibe1 producto acoplado de la fuente y permite1 producto de la sonda posterior. Una fuente con información negativa produce otro campo direccional real; una fuente ausente o con exposiciones desacopladas no produce el mismo producto acoplado.

Retirar una pregunta ya formada en20 suprime la recepción y el uso posterior. El sham conserva el futuro. Los estados completos antes del corte coinciden. Las comprobaciones del fork muestran un único RAW cambiado, ningún clock cambiado y el MAIN del instrumento intacto. Las reservas cambian historia, información y ubicación, incluida la altura42 utilizada para preparar una composición posterior.

El signo de la relación debe leerse, no heredarse de otra preparación: en este cuerpo CPC6/CPC7, AB tiene delta A−B=−1 y su primera emisión tiene x=+1. Los campos exactos están guardados.

## 2. Falta de información actual en una ventana finita

V1 permanece silencioso cuando no llega el informe actual: el portador esperado no visita sus sitios de consulta en z+4. Ese límite se conserva.

`comparison_need_v2.py` añade, antesT0, una oportunidad en la trayectoria que el portador esperado sigue cuando no fue transformado por el informe actual. `FALLBACK_SUMMARY.json` documenta seis preparaciones nuevas. La falta del informe en la apertura declarada produce pregunta19, información24 y uso29. La coincidencia actual sigue suprimiendo la pregunta; la discrepancia usa la ruta original. La reserva cambia historia y lugar. Un corte diagnóstico de la nueva pregunta formada suprime la recepción y el uso sin cambiar clocks ni el padre.

Esto detecta una ausencia físicamente definida en una ventana, no toda información incompleta. Sin lector, o sin una expectativa representada en el dominio de este aparato, el silencio sigue teniendo otra causa. La fuente ausente, un informe negativo explícito y una consulta rechazada tampoco se convierten en una misma respuesta. Las seis condiciones pedidas se distinguen en la auditoría por sus estados y controles; no se atribuye al participante un clasificador general de seis estados.

## 3. Renovación e inhibición preparadas

`RECURRENT_SUMMARY.json` describe cinco preparaciones. Una fuente interna semantic4 sostiene portadores de oportunidad +Y: en la ventana10–100 hay46 ticks con el patrón en el puerto, sobre91 ticks observados. Un contraflujo de carga0 suprime ese patrón. El sham fuera del plano y el cambio a dirección coincidente conservan la oportunidad. La reserva trasladada conserva la supresión.

Son fuentes y regulación fijas de diseño. Un portador de carga0 conserva presencia y dirección. Estos datos no demuestran que la organización aprendiera cuándo necesita preguntar; tampoco son46 réplicas independientes.

## 4. Interferencias y guardas locales

`REGULATION_SUMMARY.json` conserva las variantes favorables y adversas. Un primer absorbedor situado cuatro pasos después del normalizador coincide, en la rama de igualdad, con el propio comparador: elimina también la función buscada. El contraflujo balístico reduce sólo parte de los residuos y comienza dentro de planos que podrían alojar otro repertorio.

La corrección geométrica mueve el absorbedor fijo a ocho pasos residuales. Conserva preguntas, información y uso; las muestras de las rutas nominales muestran desaparición de los normalizadores descendentes después de la intercepción27, frente a su persistencia con el sham. Una extensión añade cuatro guardas para las posibles trayectorias de informes actuales no combinados, sin seleccionar desde el host cuál ocurrió.

Las guardas locales no cierran toda corriente del universo. El escaneo global conserva RAW y clocks exactos, incluidos registros inactivos con dirección, y revela tráfico Z en planos bajos incluso con esas guardas. Una trayectoria desviada no recibe una genealogía inventada.

## 5. Localización causal de una fuente de tráfico

`BODY_SOURCE_SUMMARY.json` compara dos cuerpos nuevos, sin adaptador. Sólo cambia, antes de la experiencia, s_reg=7→0 de la fuente escalar preparada sobre el cuerpo. Su ubicación, semantic4, state6100, dirección0, clock19 y presencia activa se conservan. Los RAW iniciales difieren en un sitio y los arrays completos de clocks coinciden.

Ambos adquieren la misma trayectoria de delta y producen en5 una emisión idéntica bit por bit: carga7, dirección(+1,−1,0). Con la fuente7, el cuerpo solo ya presenta42 registros activos dirigidos enZ en planos1–31 en35. Con la fuente0, ese contador es0 en35,50,67,70,72,91 y100. Este contraste identifica una contribución causal de la preparación; no se deduce la procedencia sólo porque varios portadores tengan carga7.

La segunda petición de lectura69 es rechazada por ocupación en ambos ensayos. La lectura actual72 no se cuenta como una nueva consulta admitida. La reducción de tráfico es una mejora de preparación disponible para probar una integración nueva; no es limpieza de un individuo antiguo, regulación aprendida ni garantía de acceso ilimitado.

## Reproducción

Los preparadores reutilizables están en `src/endogenous/`: `comparison_need.py`, su extensión `comparison_need_v2.py`, las guardas versionadas y `body_source.py`. Devuelven colocaciones, interfaces y geometría antes de crear el Runtime. No se deben instalar sobre un MAIN ya vivo para atribuir continuidad.

Los runners finitos reciben `--config` y `--out`; las configuraciones congeladas están en `configuraciones/endogenous/`. Deben ejecutarse con el WHL4.0 oficial del paquete en un entorno compatible. La supervisión de la campaña usa el deadline histórico compartido; una reproducción futura solicitada es otra operación explícita y no debe reiniciar aquel presupuesto. El lanzador público y sus timeouts corresponden a la entrega general.
