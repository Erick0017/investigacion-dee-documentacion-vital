# PI02 R01: observación y calibración directa

Recálculo documental independiente de cuatro capturas cerradas y dos checkpoints históricos, sin importar DEE, abrir propietarios ni ejecutar ticks. El script `recalcular_R01_pasivo.py` conserva fuentes, bytes, hashes y sus límites en `RECALCULO_R01_PASIVO.json`. Los checkpoints T735977 pertenecen al corte histórico del control de observación; las dos vidas continuaron después en la calibración y no se presentan como su estado vivo actual.

## Control de observación

Dos clones del mismo pasado T735843 avanzaron134ticks hastaT735977. ON observó el origen fijo cada tick; OFF no registró puntos intermedios. Se verificaron las capturas terminales y los bytes gzip de ambos snapshots. El parser pasivo revisado de PI01 se reutilizó extrayendo por AST solamente `Reader` y `snapshot_view`; no se importó ni ejecutó el módulo de promoción.

El resultado independiente fue igualdad de N/tick, RAW, clocks y prefijo causal serializado, que incluye interfaces, pendientes, recibos y progreso Native representado por ese formato. Los dos tienen1009interfaces,0pendientes y112829recibos heredados. No hubo diferencia de metadata no administrativa después de excluir explícitamente identidad de vida/servicio y sus colas. Los hashes codificados de los contenedores pueden diferir por esa identidad administrativa.

RAW final: `02b4251782ead94c700d2d23b6512bab6222602ff4ac749dcfb7418a7a1e72b1`.

Clocks final: `b6b89ec2148d440ec76e54f3397dccfa2450c5bfd0190d0a88afb74410a957fa`.

Prefijo causal: `31a9218143a5c7bf431c3182c6bd053970725e0979beb272651f61f5ed3608c7`.

La igualdad respalda ese lector fijo y la segmentación por tick durante esa trayectoria134ticks. No es una certificación universal de pasividad para todo instrumento ni una comparación de todos los artefactos externos. El parser comprueba gzip y hashes, pero no recalcula FNV interno del formato.

## Calibración física, sin tarea útil todavía

Ambos brazos continuaron desde el mismo estado físico T735977 durante268ticks, hastaT736245. No se añadieron SENSOR ni NORMALIZER. Se decodificaron de RAW las cuatro llegadas de cada brazo, con enteros exactos y comprobación de los campos reportados:

| Tick de retorno | ON, ruta/carga | OFF, ruta/carga |
|---:|---|---|
|736004|A=(1,0,0),937|A=(1,0,0),937|
|736071|B=(0,1,0),942|A=(1,0,0),937|
|736138|B=(0,1,0),942|A=(1,0,0),937|
|736205|B=(0,1,0),942|A=(1,0,0),937|

ON recibió una entrada genérica de valencia sobre el portador que retornaba: recibo112830, solicitado/aplicado enT736070, encuentro leído enT736071. Su denominador nuevo es1solicitada/1aplicada/0rechazada. OFF no recibió ese pulso:0solicitadas. El centro y el contexto cercano se preservaron durante los cinco cuadros deT736069–736073. Los112829recibos anteriores no se cuentan como nuevas experiencias de la calibración.

El cotejo no encontró inconsistencias de campos RAW, rutas, horizontes o denominadores. Esto delimita una posibilidad física: un portador ya existente puede conservar A o transformarse a B mediante una contribución legal, sin tener que recibir SENSOR/NORMALIZER en cada retorno. La recurrencia cada67ticks está preparada por la trayectoria toroidal. La valencia se impuso para calibrar: **todavía no demuestra utilidad, aprendizaje de un dispositivo, selección temporal adquirida, anticipación ni regulación**. Esas afirmaciones corresponden a ensayos posteriores con consecuencia de una acción real y controles adecuados.

Los cuatro retornos pertenecen a cada misma trayectoria; no son cuatro adquisiciones independientes. La comparación global de snapshots y el recuento documental no modificaron ninguna de las vidas.
