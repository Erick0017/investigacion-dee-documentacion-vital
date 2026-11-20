# Resumen de validación antes de la entrega de control

Todas las pruebas aquí marcadas fueron ejecutadas. No se usa `PASS` para pruebas no corridas.

| ID | Prueba | Resultado |
|---|---|---|
| A | trayectoria continua vs guardar/cerrar/cargar/continuar | exacta en RAW, clock y tick |
| B | replay de ventana real | exacto, sin recibos duplicados |
| C | entrada durante sesión | solicitud, programación y aplicación registradas |
| D | pausa | tick sin avance por tiempo de pared |
| E | archivo | checkpoints sucesivos no sobrescriben anteriores |
| F | rama diagnóstica | mundo principal inalterado |
| G | checkpoint inválido | rechazo; último válido conservado |
| H | panel/observe | observación pasiva |
| I | independencia | lanzador terminó; worker sobrevivió con Job flags 0 |
| J | recolección viva | corte T64 inmutable; continuación escribió segmento siguiente |
| K | presupuesto reducido | parada segura T80 con checkpoint y causa |
| L | exclusión | segundo escritor rechazado; propietario siguió vivo |

Pruebas adicionales: DenseSequential coincidió con Lazy en RAW/clock en T64; el paquete se validó con `testzip`, hashes de manifiesto y rechazo de sobreescritura; una extracción limpia reprodujo T0→T64 con 23 recibos exactos y continuó hasta T65 en un linaje de prueba. Se reprodujeron y corrigieron dos defectos de envoltorio sin alterar el kernel: carrera transitoria de `status.json` en Windows y PID nulo durante el handshake de un corte congelado.
