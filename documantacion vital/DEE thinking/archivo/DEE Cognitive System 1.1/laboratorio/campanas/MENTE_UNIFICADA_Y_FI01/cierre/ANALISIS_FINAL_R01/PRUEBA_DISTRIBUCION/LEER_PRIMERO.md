# Comprobación operativa de la entrega exacta

El primer ZIP se importó correctamente; su cliente dejó de esperar una exportación completa a los40s, aunque terminó a los49.78s. Se preservó el fallo y se continuó esa misma copia sin reenviar FINISH. Después se revisó sólo el harness (export120s/safety420s), se selló otro ZIP y se comprobó desde otra extracción. Ningún resultado de las copias se atribuye a MAIN original.

PLAN_RECALCULO.json describe tres recálculos estándar con Python, sin importar DEE ni avanzar ticks. Son aritmética de RAW/lectores/recibos y verificación de archivos reales exportados; no reproducen la física ni el ZIP omitido. La reproducción nativa necesita el paquete completo y sus estados. PRUEBA_PORTABLE.json acredita comparación byte a byte desde otro directorio.

Los comandos y sus salidas físicas, incluidos el negativo instrumental y los resultados de los dos participantes separados, están íntegros en EVIDENCIA/. El código ejecutado relevante está en CODIGO_EJECUTADO/.
