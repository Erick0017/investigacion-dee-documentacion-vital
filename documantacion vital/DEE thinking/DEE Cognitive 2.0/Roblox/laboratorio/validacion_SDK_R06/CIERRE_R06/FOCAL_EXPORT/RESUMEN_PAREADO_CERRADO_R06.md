## Focal cerrado: comparación de dos descendientes emparejados

Ambos brazos completaron **6 oportunidades**, desde **N67/T991187** hasta **T1000571**, +9384 ticks cada uno. La trayectoria observada fue idéntica: **0→3→2→3→2→3→2**. En ambos,5/6 movimientos exitosos fueron2↔3 (83,33%), con racha máxima5; no hubo salida verificada desde{2,3}, por lo que no se demostró el criterio prospectivo de dos llegadas posteriores fuera. Se conserva horizonte6, desarrollo1–4/reserva5–6; no se evalúan oportunidades inventadas.

| Métrica observada | OSCILANTE | CONTROL |
|---|---:|---:|
| ASK / EXIT_1 |6 /6|6 /6|
| Datos Q2 realmente aplicados / omitidos |6 /0|6 /0|
| Inputs Native únicos aplicados / rechazados |78 /0|78 /0|
| Pasos libres / con peaje |4 /2|6 /0|
| Consulta / peaje / coste total |6 /4 /10|6 /0 /6|
| Stock inicial→final |164→154|164→158|
| Paneles agotados realmente consultados |2 (ciclos4/5)|0|
| Cambios de secuencia de acciones entre brazos |0|0|

En OSC, señal0 en ciclos4/5 fue un **panel pagado con datum Native aplicado**, no NoQuery. Se conservan los IDs y los recibos en el JSON; la consulta se cobró en Q1 y no otra vez en Q2. La ley consumible generó tres reposiciones ambientales; sólo el panel de estación3 posterior a su reposición se consultó nuevamente, en ciclo6. No se atribuye al Native observación del evento interno ni de las otras dos reposiciones.

Ambos peajes2 coexistieron con `actualPhysicalFailed=false` y `appliedGenericFailed=false`: el peaje no equivale a fallo genérico. Los datos muestran contraste de coste/exposición, **sin cambio de acciones ni salida sostenida observada**. Es n=1 por condición, no réplicas independientes, ni prueba de aprendizaje de política. El origen cerrado, la proyección RAW→DTO y los primarios literales permanecen preservados.

Exports: `EXPORT_CHATGPT/FOCAL_OSC_R06_R02/MANIFIESTO.json` y `EXPORT_CHATGPT/FOCAL_CONTROL_R06_R02/MANIFIESTO.json`. Comparación pasiva única: `DEMOSTRACION/COMPARACION_FOCAL_R06_R02/COMPARACION_DESCRIPTIVA.json`. No se ejecutó Native/SQLite ni se editó el informe para producir este snippet.
