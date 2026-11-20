# Cobertura de telemetría

- Ventana fresh principal: ticks 0–32.
- Puntos funcionales: escrituras en 1–2; acciones en 8, 16 y 24; retornos en 9, 17 y 25.
- Recurrencia: observación puntual pasiva en cada tick.
- Estado completo: RAW y clock al inicio, al final, en checkpoints y en comparación de backends.
- MBP3: padre 276832, instalación t0 sin sobrescritura, final 276864.
- No hubo entradas del host después de t0 en los casos científicos.

Los resultados contienen trazas locales y hashes de estado completo. No se afirma que cada microinteracción haya sido registrada como evento independiente; las ventanas son reproducibles desde checkpoint y preparación.
