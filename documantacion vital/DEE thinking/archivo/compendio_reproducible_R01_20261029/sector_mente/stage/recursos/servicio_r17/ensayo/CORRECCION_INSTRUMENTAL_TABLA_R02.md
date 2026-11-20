# Corrección de tabla retrospectiva, cero ticks

`PANELES_Y_FUNCIONES_R01_ERROR_PREFIJO.json` y `CORTE_PARA_MANUAL_R01_ERROR_HEREDADO.json` son salidas instrumentales incorrectas, conservadas junto a sus fuentes ejecutadas `CODIGO_TABLA_R01_ERROR_PREFIJO.py` y `CODIGO_CORTE_R01_ERROR_HEREDADO.py`.

La primera tabla recorrió todas las filas del diario emparejado e incluyó también la enseñanza beta+ histórica R11. Al encontrar dos enseñanzas en vez de sólo la beta− R17, no fijó el tick de revisión y comparó seis consultas posteriores con la señal anterior. De ahí el falso114/120. No hubo fallo físico ni cambio de respuestas: los RAW y recibos originales permanecen intactos.

La revisión R02 filtra por el prefijo preregistrado `fi60r3_` antes de extraer las enseñanzas y las solicitudes actuales. La tabla final `PANELES_Y_FUNCIONES.json` obtiene una única revisión de beta,3/3entradas aplicadas, y120/120lecturas coincidentes con esa historia. `CORTE_PARA_MANUAL.json` se regeneró desde ella; el paquete postSTOP ya existente se reutilizó sólo después de verificar todos sus hashes y la igualdad con el mismo corte actual, sin copiar otro futuro ni ejecutar un Runtime.

No se cambió el protocolo, ningún primario, los criterios congelados, el estado DEE, la genealogía ni el motor. El recálculo de RAW/recibos/bytes y el de tiempo ya eran correctos y no se sustituyeron por una nueva trayectoria. Las versionesR01 no deben utilizarse como resultados físicos ni para redactar el Word.
