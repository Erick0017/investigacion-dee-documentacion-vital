# Continuidad hasta T1051 desde el MAIN social adquirido

Capacidad conservada: en las cuatro continuaciones del estado real SOC_I21/T690, las63 relaciones previamente accesibles en T658 siguen consultables en T1051 y conservan63/63 valores. Entre ambas ventanas ocurren nuevas exposiciones actuales sin reenseñar esas relaciones. Se conservan el mismo Runtime N131, su historia, cola, canales, recibos y clocks; no se instala una nueva receta ni se vacían puertos.

La fuente es `SOC_I21_SOCIAL_THEN_L01_REVISION/FINAL_T690.deetsnap.gz`, SHA-256 `9df3359c70224cb8d4a8df7a3e9f7346e2527eec4901bf54aab04c3f695f9399`. El snapshot conserva259 interfaces y15 sitios materiales iniciales. Su metadata histórica de recursos enumeraba219 interfaces de la base antes de añadir40 sociales; se mantiene intacta y se registra además el conteo real. No se atribuyen a esta preparación los21 sitios de las cohortes E1 con guardas.

## Protocolo congelado y experiencia recibida

La hipótesis se fijó antes de ejecutar: algunas oportunidades antiguas podrían regresar tras6N=786 ticks. Desde T690 se solicitaron acontecimientos A/B en T786/787, una consulta externa de orden en T788, una nueva señal RIGHT y su acontecimiento direccional -1 en T786, y el sensor actual -1 en T797. No se introdujeron nuevas acciones, preguntas B, cues B, contextos, reguladores ni interfaces.

La pareja RIGHT se admite y forma un portador móvil de dirección(0,-1,0), carga16, observado en T920. Es una distinción adquirida en la continuidad, posterior a la conservación social y a la revisión L01. Su uso por la cadena nativa propuesta no se consiguió en esta ventana.

La segunda experiencia de orden no se admite: A/B y el lector común encuentran `rejected_occupied`. El replay técnico conserva pre/post estados exactos785–789: los puertos ya contienen registros de cargas8,8 y7. Los observadores pasivos del kernel indican que no están protegidos por su compuerta microscópica; eso no elimina la condición RAW-vacío de admisión de la interfaz del host. No se abrió ninguna compuerta ni se borró estado para forzar recepción.

## Controles y consecuencia

El pilotoAB, el controlBA y la rama sin nuevos A/B producen estados físicos completos idénticos en T805/T926/T952/T1051. Los nuevos acontecimientos rechazados no cambiaron el conocimiento de orden, aunque el cuerpo continúe emitiendo actividad de su historia anterior. No aparece en esas ramas la nueva acción tridimensional prevista en T922.

El control sin señal RIGHT conserva el acontecimiento actual. Su sitio RIGHT observado en T920 está vacío, pero aparece un producto distinto de carga18 y dirección(+1,-1,+1) en la acciónT922 y en el hub B de T926. No se normaliza a la memoria B esperada ni se expresa una nueva consulta/uso/entrega RIGHT en las ventanas congeladas. Los huecos entre ventanas no autorizan una genealogía única de ese portador.

Las cuatro ramas contienen exactamente la misma entrega anterior LEFT.plus en T952: dirección(+1,+1,+1), carga122. Su presencia incluso sin nuevo orden o sin la señal nueva impide contarla como utilización de la nueva información RIGHT. Se conserva como actividad funcional previa que sigue circulando, no como una respuesta fabricada para la nueva tarea.

## Evidencia y alcance

`resultados/integracion/LONGITUDINAL_INDEX.json` registra4 continuaciones del mismo padre y sus snapshots690/805/926/952/1051. `LONGITUDINAL_ANALYSIS.json` distingue observaciones, cálculos e interpretación. Sus32 copias de fuentes declaradas coinciden con los hashes; no hay nuevas preparaciones iniciales ni forks editados en esta extensión.

`LIF_ENTRY_REPLAY` es una reproducción técnica pasiva690→805: RAW/clocks/tick y recibos pasados coinciden exactamente con el piloto. Añade observación de admisión y vecindarios Moore27, no una réplica independiente.

La conclusión local es conservación funcional prolongada y nueva asociación física RIGHT, junto a una frontera de acceso del cuerpo de orden y de reutilización de la cadena social. No se ensayaron otras fases ni una cronología de rescate. La interpretación no se generaliza al kernel v27 completo.

## Segunda y última extensión: acceso instrumental a la nueva relación

Después del corte anterior se congeló un único lector exploratorio: `U.right.signal`, probe9 en T1179, lectura nativa C++ en el hub declarado desde T0, T1182. El lector selecciona explícitamente el investigador; no se presenta como pregunta autónoma ni como reserva confirmatoria retrospectiva. Las dos continuaciones ya guardadas en T1051 se cargan sin reconfiguración. Una tercera cohorte parte del mismo T690 con cue787 y acontecimiento786, conservando las dosis de la experiencia emparejada.

USE_P11_RIGHT_PAIRED responde con RAW `1224697731042246657`, carga25, dirección(-1,-1,0), valor-1 y recibo `applied`. La rama sin cue y la de igual dosis desfasada responden sólo con el probe de carga9, dirección(-1,0,0), valor nulo y estado `PROBE_ONLY_OR_INSUFFICIENT_LOAD`. No se sustituye ese nulo por cero.

Así se completa, en el mismo MAIN emparejado, la secuencia concreta: conocimiento anterior adquirido → nueva asociación RIGHT en T786 → uso posterior de63/63 relaciones antiguas T1051 → consulta funcional de la nueva RIGHT T1182. Los conocimientos anteriores no se reenseñan. La tercera cohorte también conserva63/63 en T1051. Este acceso no repara retrospectivamente la admisión del orden ni la cadena social que faltó en la primera extensión.

Los3 registros están en `USE_*`; `RIGHT_ACCESS_INDEX.json` y `RIGHT_ACCESS_ANALYSIS.json` conservan datos y lectura de alcance. Son3 continuaciones controladas adicionales, cero nuevas preparaciones físicas, con24 copias de fuentes verificadas sin discrepancias. No se ensayan otras cadencias después de este resultado.
