# Alcance instrumental del corte

Los intentos técnicos fallidos se conservan. La adaptación de referencia corrigió el cue heredado 5/9, el nombre real del backend `DENSE_SEQUENTIAL` y una importación de `coord`. No se modificó el kernel ni el WHL.

La primera reproducción desde extracción limpia llegó a estados iguales en todos los checkpoints comparados de P01/independent5, pero rechazó comparar literalmente los diccionarios de entradas: los registros iniciales aún no incluían `payload` y `runtime_ref`. El hotfix compara todos los campos realmente registrados, la cantidad y orden de llamadas, los recibos completos por Runtime, los payloads de consulta del protocolo y las intervenciones. Registra explícitamente los campos ausentes del formato temprano; no rellena los registros históricos ni afirma que contenían esos datos. Los estados RAW, clocks y ticks siguen exigiendo igualdad exacta.

Los valores de payload temprano también están determinados por configuración, runner y series de consultas. Esto permite reproducción, pero no sustituye un log explícito contemporáneo. Las llamadas posteriores sí incluyen payload y referencia estable de Runtime.

`inspect_write_gate` informa condiciones locales anteriores al paso. Su nombre de rama es una lectura instrumental de esas guardas, no un reemplazo de la trayectoria ejecutada. El postpaso DEMUX aparece como no resuelto cuando esta lectura pasiva no basta. Los contadores expuestos corresponden al último tick y no detectan necesariamente todas las colisiones. Los observadores balísticos son segmentos con predicción toroidal contrastada, no un tracker universal de descendencia.

Las reservas trasladadas no avalan invariancia universal signed/permuted. Los frentes con contrastes registrados no tienen por ello resueltas todas sus preguntas; el factorial completo historia×experiencia, la adquisición de contingencia, la defensa activa y la adquisición de preferencia informativa continúan limitados por las interfaces probadas.

Los dos cortes trasladados del flujo de P14 son replicaciones de una intervención nueva sobre preparaciones cuya evolución sin corte ya había sido observada. La intervención se fijó antes de ejecutarlas; no se cuentan como geometrías históricamente desconocidas ni como nuevas preparaciones virgin nunca ensayadas.
