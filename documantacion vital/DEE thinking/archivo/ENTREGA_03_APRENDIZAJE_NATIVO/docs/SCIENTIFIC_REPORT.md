# Entrega 03 — aprendizaje ambiental nativo y lectura causal

## Alcance y baseline

Se utilizó DEE thinking 2.2.0 como instrumento C++ y el kernel DEE v27 sin
modificar. La comprobación inicial recuperó seis protocolos integrados, la
secuencia F2 `24,55,62,62,67` y una continuación F2 desde snapshot con igualdad
RAW y clock. El experimento nuevo no modifica la biblioteca publicada ni crea
un WHL nuevo.

La revisión fue dirigida a los contratos H1–H4/F1/F2, el informe del
laboratorio final, los capítulos pertinentes de *Procesamiento Nativo DEE* y
*Física DEE 4.0.1*, y el Documento Maestro disponible en la ubicación
documental conocida. No se encontró dentro de la raíz de DEE thinking una copia
editorial identificada literalmente como Libro Blanco/Manual 2.2.0; para las
decisiones de implementación se usaron los documentos técnicos exactos de la
Entrega 02 definitiva. No se reconstruyó el corpus ni se tomaron menciones
históricas como ejecuciones nuevas.

## Pregunta y preparación congelada

La pregunta ejecutada fue si una regularidad ambiental de coincidencia y fase
puede modificar una organización persistente y afectar interacciones
posteriores sin que el host escriba el resultado.

El mundo, de dimensión `N=127`, contiene:

- un linaje móvil C7H03 con la misma preparación base en todos los brazos;
- cuatro estaciones ambientales, cada una con seis soportes persistentes;
- dos propuestas por estación, de cargas 4149 y 15515;
- un único portador de actualización de carga inicial 23;
- una redirección física que hace llegar ese portador al mismo linaje en t38;
- consultas comunes en t46 y t58.

Las dos propuestas de cada estación coinciden en t13, t17, t21 y t25. La
coincidencia deja carga 19664. Sólo una ventana de fase receptiva permite que la
regla material añada una unidad, alcance el umbral y produzca mediante DEMUX un
delta `+1` sobre el portador que pasa por el destino en el tick siguiente. Los
niveles de dosis 0, 1, 2 y 4 son el número de ventanas receptivas; inventario,
cargas, rutas, edad y consultas permanecen fijos. Todas las entradas del panel
principal fueron colocadas en t0. Después de esa frontera sólo se llamó al
kernel y se realizaron lecturas pasivas.

La predicción se congeló antes de la confirmación:

`portador = 23 + experiencias efectivas`;

`uso1 = 4177 + experiencias efectivas`;

`uso2 = 4180 + experiencias efectivas`.

## Resultados principales

| Historia | Coincidencias efectivas | Overflows | Portador antes del linaje | Respuesta previa t34 | Uso 1 t46 | Uso 2 t58 |
|---|---:|---:|---:|---:|---:|---:|
| DOSE_0 | 0 | 0 | 23 | 4149 | 4177 | 4180 |
| DOSE_1 | 1 | 1 | 24 | 4149 | 4178 | 4181 |
| DOSE_2_EARLY | 2 | 2 | 25 | 4149 | 4179 | 4182 |
| DOSE_2_LATE | 2 | 2 | 25 | 4149 | 4179 | 4182 |
| DOSE_4 | 4 | 4 | 27 | 4149 | 4181 | 4184 |
| PHASE_CUT | 0 efectivos | 0 | 23 | 4149 | 4177 | 4180 |

Los nueve casos finales solicitaron 19 entradas cada uno; las 171 solicitudes
fueron admitidas y no hubo rechazos ni fallback de backend. La respuesta previa
a la actualización fue 4149 en todos los brazos interpretables. La diferencia
apareció primero en el portador, luego en el encuentro de revisión t38 y se
conservó en dos consultas transformativas posteriores.

Las historias de dosis dos temprana y tardía tuvieron trazas intermedias
distintas (`24,25,25,25` frente a `23,23,24,25`) y convergieron en la misma
función final. En este aparato el lector funcional conserva el conteo de
coincidencias efectivas, no su orden.

## Controles causales

`PHASE_CUT` conserva las cuatro coincidencias, cargas, rutas y consultas, pero
desplaza un tick la fase de las cuatro estaciones. La consecuencia no coincide
con el portador: no hubo overflow, el portador quedó en 23 y ambos usos fueron
idénticos a dosis cero. Este es el control causal principal del enlace
ambiente→DEMUX→portador→linaje.

`UNPAIRED_SAME_INVENTORY` conserva inventario y duración, adelanta un miembro de
cada par y registró 0 overflows. También produjo interferencia física: el
portador dejó de estar disponible después de la primera estación y las consultas
quedaron aisladas (`5` y `3`). Por ello este brazo evidencia sensibilidad de
accesibilidad al orden, pero no se usa como control limpio para estimar la
magnitud del aprendizaje.

La preparación DOSE_4 fue repetida con Lazy, DenseSequential y DenseParallel.
RAW y clock finales coincidieron exactamente entre los tres backends, y los
tres produjeron 4184 en el segundo uso.

Dos pilotos pertinentes se conservaron:

1. propuestas ambientales opuestas dejaron 19664 pero su vecindad quedó
   protegida y no produjo overflow;
2. al usar una historia no emparejada como niveles intermedios de dosis, los
   residuos alteraron la accesibilidad del portador.

Esas discrepancias motivaron, respectivamente, reutilizar la dirección upstream
verificada de F2 y separar dosis de orden mediante ventanas de fase.

## Transferencia y retención

Una evaluación reservada cambió las cargas de consulta de `5/3` a `9/4` sin
cambiar el constructor ni el lector. Dosis cero produjo `4181→4185`; dosis
cuatro produjo `4185→4189`. El contraste de cuatro unidades se conservó en ambas
consultas reservadas. Esto es transferencia acotada a nuevos contenidos de
consulta dentro de la misma familia física, no generalización universal.

La última modificación ambiental ocurrió en t26, alcanzó al linaje en t38 y se
utilizó en t46 y t58. La retención funcional medida es, por tanto, de 20 ticks
desde la revisión hasta el segundo uso, y 32 ticks desde la última experiencia
ambiental hasta ese uso. No se estudió retención indefinida.

## Checkpoint reutilizable

`learned_dose4_t40.deetsnap` conserva RAW, clock, tick, canales, recibos,
metadatos y la organización después de las cuatro experiencias, antes de las
consultas reservadas. En un proceso nuevo se cargó el checkpoint, se aplicaron
las consultas reservadas en t40 y reaparecieron `4185` y `4189`. El futuro RAW y
clock en t60 fue idéntico al de la continuación de referencia. La consulta de
reanudación es una intervención ACOPLADA y no se contabiliza como parte del
brazo nativo post-HOST_STOP.

## Perfil medido

- **Adquisición:** conteo 0/1/2/4 de coincidencias ambientales en fase,
  transportado como carga 23/24/25/27 y utilizado por el linaje.
- **Dosis:** una unidad funcional por experiencia efectiva en el dominio
  ensayado; no se extrapola fuera de cuatro.
- **Retención:** dos usos, hasta t58, sin reconstrucción del mundo.
- **Especificidad:** control de fase vuelve a dosis cero; edad, inventario,
  cargas y consultas se mantienen.
- **Transferencia:** diferencia de cuatro unidades conservada con consultas
  reservadas 9/4.
- **Revisión/interferencia:** dosis dos temprana/tardía converge; la secuencia
  no emparejada interfiere con la ruta y no permite separar aprendizaje de
  accesibilidad.
- **Uso causal:** el portador modificado revisa una relación móvil y cambia dos
  interacciones posteriores.
- **Recursos:** 24 soportes persistentes, 19 entradas admitidas por caso y un
  portador reutilizable; no se observó saturación del linaje.

## Qué realizó el host y qué realizó DEE

El host preparó t0, geometría, soportes, fases, propuestas, consultas y recursos;
seleccionó los brazos y midió el estado. No leyó una respuesta para escoger el
siguiente update y no escribió las cargas 24–27, 4177–4184 o 4181–4189. Esas
transformaciones procedieron de los encuentros, overflow, DEMUX, transporte,
redirección y consultas de v27.

La organización base ya contenía una relación C7H03 entrenada. El resultado
nuevo es una **revisión ambiental adquirida y reutilizada**, no aprendizaje
desde sustrato virgen ni generación endógena de su propio teacher.

## Límites y aspectos no ensayados

No se ejecutó una segunda familia contextual porque el candidato temporal
proporcionó una cadena completa y consumió el presupuesto de confirmación. No
se estudió inversión de la relación, aprendizaje de orden, preacondicionamiento
para otra tarea, bucle de acción propia que genere el siguiente feedback,
sostenibilidad prolongada ni localización de la memoria fuera del conjunto
linaje+contexto. La salida aditiva no implica acceso global al mundo.

Estado de esta campaña: **adquisición ambiental contrastada en el dominio
de coincidencia-fase declarado**, con transferencia y reanudación acotadas. Esa
descripción no constituye un dictamen de inteligencia, consciencia o autonomía.

