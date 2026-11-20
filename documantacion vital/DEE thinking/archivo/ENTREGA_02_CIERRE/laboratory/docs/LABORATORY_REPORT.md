# Informe del laboratorio de cierre — Entrega 02

## Alcance

Se ejecutaron dos familias pequeñas, ocho casos terminados y ningún caso
parcial. La corrida primaria Lazy-4 y la confirmación DenseSequential-1 se
repitieron contra la biblioteca Release integrada. Los objetos físicos de los
ocho casos coincidieron exactamente entre agendas al excluir sólo backend y
duración; los contadores técnicos de trabajo se conservaron por separado. Todo
el código y los productos están aislados en `laboratory/`; no se
modificaron el kernel, la API estable, el catálogo, CMake ni los scripts de
paquete. El backend solicitado fue `Lazy` con cuatro hilos, que evalúa la misma
regla congelada v27.

Al diseñar y ejecutar este laboratorio, CORE05 aún figuraba en la copia de
trabajo sin constructor y oráculo integrados; no se abrió una tercera familia
para evitar inventar un aparato. El port primario CORE05 se completó después en
la línea técnica independiente y no altera retrospectivamente estos ocho casos.

## Familia 1 — actualización y ruta contextual (NATIVA)

### Pregunta y preparación

Dos portadores presentes desde `t=0`, con cargas 20 y 17, llegan juntos al
sitio `[4,4,4]`. La predicción era un producto de carga 37 y dirección
`[1,1,0]`. Ese producto alcanza en `t=3` el cruce `[6,6,4]`. En cuatro mundos
se prepararon desde el inicio: ningún selector, un selector de carga cero que
cancela Y, otro que añade Z, o ambos. Después de `t=0` el host sólo llamó al
kernel y leyó.

### Mediciones

- En 4/4 casos apareció en `t=1` el producto `s_reg=37`, dirección `[1,1,0]`.
- En 4/4 casos el registro del cruce en `t=3` coincidió con la suma direccional
  preregistrada: `[1,1,0]`, `[1,0,0]`, `[1,1,1]` y `[1,0,1]`.
- En `t=6` hubo exactamente un endpoint declarado ocupado en cada caso; su
  posición, carga 37 y dirección coincidieron con la predicción.

El contraste ausencia/portador de carga cero es físicamente informativo: el
selector de carga cero no añade carga, pero sí cambia la dirección mediante su
registro ocupado. Con ambos selectores se obtiene un único producto por una
ruta combinada. En este aparato no apareció copia física ni fanout: la salida
se transfirió por una sola ruta. Esto caracteriza un límite y un mecanismo de
selección; no demuestra que DEE carezca de todo fanout en otros dominios.

El caso sólo contiene una actualización y una transferencia. No mide aún
reutilización de ese cruce durante ciclos múltiples ni adquisición del selector
por una historia anterior.

## Familia 2 — nueva consulta sobre el mismo mundo C6 (ACOPLADA)

### Pregunta y contrato

Se reutilizó la composición pública C6 de aprendizaje relacional y consulta.
Cada caso evolucionó sin reset: entrenamiento o control en `t=0`, consulta
inicial de carga 13 en `t=6`, lectura en `t=11`, continuación hasta `t=40` y,
cuando correspondía, una segunda entrada externa en el canal físico de consulta.

La segunda entrada queda clasificada como **ACOPLADA**: el host decide y escribe
la consulta en `t=40`. Se usa deliberadamente la interfaz pública de `Runtime`
porque el contrato de puerto del catálogo sólo promete la ventana validada
original. Ningún resultado de este brazo se exporta al catálogo estable.

### Mediciones y controles

- Los mundos entrenados dieron la respuesta inicial conocida `s_reg=25`.
- Sin segunda entrada, ese registro volvió al sitio de respuesta en `t=45` con
  `s_reg=25`, consistente con retorno toroidal del portador en N=34.
- Con una segunda consulta de carga 13, el evento fue aplicado y la lectura de
  `t=45` fue `s_reg=38`. Frente al control ausente hubo una sola celda RAW
  distinta y cero diferencias de clock en todos los checkpoints posteriores a
  la aplicación hasta `t=46`.
- Un portador de carga cero también fue aplicado. Produjo una diferencia RAW
  durante el tránsito, pero en `t=45` convergió exactamente al control ausente
  en RAW y clock; la respuesta permaneció 25.
- En el control con sólo cue, la primera respuesta fue 13. La segunda consulta
  fue rechazada como `rejected_occupied` en el límite de aplicación. Por ello
  este caso informa que admisión depende del estado/fase presente, pero no es
  una comparación causal limpia de entrenamiento frente a no entrenamiento
  bajo una segunda consulta igualmente admitida.

El contraste separa ausencia de portador y carga cero, y demuestra que una
entrada posterior puede ser admitida y transformada en el mismo mundo ya
evolucionado. La suma 25+13=38 describe este aparato concreto; no se interpreta
como asociación nueva, auto-retorno ambiental ni aprendizaje de una regla.

### Límites

- El retorno del registro existente es nativo, pero la nueva consulta es una
  escritura externa declarada; no constituye cierre ambiental autónomo.
- El horizonte terminó en `t=46`. La diferencia de carga seguía transportada,
  pero no se midió un segundo uso funcional de ese nuevo producto.
- El rechazo del control cue-only impide atribuir la admisión exclusivamente al
  entrenamiento: geometría, fase y ocupación siguen siendo explicaciones
  compatibles.
- No se midieron fanout físico, capacidad indefinida, generalización amplia ni
  actualización adquirida de los selectores.

Cada corrida duró segundos y escribió su colección al terminar. No existió una
trayectoria larga que necesitara reanudación; este runner no implementa guardado
caso-a-caso y esa limitación queda explícita.

## Archivos de evidencia

- `runners/laboratory_runner.cpp`: constructor, controles y mediciones exactas.
- `config.json`: parámetros congelados de ambas familias.
- `results/results.json`: registros y contrastes estructurados.
- `results/telemetry.csv`: trazas por tick y sitios declarados.
- `results_dense/`: repetición DenseSequential-1 del mismo panel.
- `results/run_metadata.json`: comandos, duraciones e identidades SHA-256.
- `REPRODUCE.md`: compilación y ejecución independientes.

Los datos sostienen dos observaciones acotadas: una actualización nativa puede
ser transferida por una ruta condicionada sin clonación en este montaje, y una
interfaz física C6 puede aceptar una entrada posterior y combinarla con un
retorno existente en el mismo mundo. No se adjudican candidatos para el
catálogo estable ni se emite una clasificación científica global.
