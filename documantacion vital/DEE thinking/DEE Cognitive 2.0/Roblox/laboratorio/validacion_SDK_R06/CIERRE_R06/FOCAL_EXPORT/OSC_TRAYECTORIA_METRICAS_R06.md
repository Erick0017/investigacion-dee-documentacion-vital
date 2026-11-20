## OSC cerrado: trayectoria y exposición observadas

Fuente/ScopeBorn **T991187**, cierre **T1000571**, +9384 ticks; seis oportunidades. Estado y IDs completos en el JSON adjunto.

**Zonas:** 0 → 3 → 2 → 3 → 2 → 3 → 2. Fracción de movimientos exitosos 2↔3: **5/6 (83,33 %)**; racha consecutiva máxima **5 movimientos** (ciclos2–6). El denominador es6 movimientos exitosos, no5 pares de ensayos ni6consultas.

| Ciclo | Tránsito | Acción Q2 | Panel pagado (p0,p1; señal) | Peaje | Stock después | Datum/recibo |
|---:|---|---|---|---:|---:|---|
| 1 | 0→3 | EXIT_1 | 0,0; 1 | 0 | 163 | 155159 / applied |
| 2 | 3→2 | EXIT_1 | 0,0; 1 | 0 | 162 | 155172 / applied |
| 3 | 2→3 | EXIT_1 | 0,0; 1 | 0 | 161 | 155185 / applied |
| 4 | 3→2 | EXIT_1 | 0,2; 0 | 2 | 158 | 155198 / applied |
| 5 | 2→3 | EXIT_1 | 0,2; 0 | 2 | 155 | 155211 / applied |
| 6 | 3→2 | EXIT_1 | 0,0; 1 | 0 | 154 | 155224 / applied |

**Consulta y coste:**6ASK pagados y6datos Q2 aplicados;0 omisiones. La consulta cuesta1 en Q1 y no se cobra de nuevo en Q2. Cuatro pasos libres y dos con peaje2 (ciclos4/5): coste6+4=10, stock164→154;78 inputs Native aplicados/0 rechazados.

**Exposición:** los paneles agotados de ciclos4/5 se consultaron realmente (señal0, no NoQuery). Hubo tres eventos ambientales de reposición: estación0/puerto1/época4, estación3/puerto1/época5 y estación2/puerto1/época6. Sólo la reposición de estación3 fue consultada de nuevo en esta ventana, en ciclo6 con señal1 y datum aplicado. No se cuentan las otras dos como exposición Native.

**Salida sostenida:** no se observó ninguna salida de {2,3} a otra estación. Por tanto no se demostró el criterio de dos llegadas posteriores fuera; no se sustituye por un cambio aislado ni se extrapola más allá del horizonte6. La nueva muestra agotada de estación2 en ciclo5 deja sólo una oportunidad posterior: no permite exigir/evaluar dos futuras llegadas tras ella.

**Retorno:** peaje no equivale a fallo genérico. En ambos pasos pagados constan actualPhysicalFailed=false y appliedGenericFailed=false; se conservan los dos pulsos de retorno por ciclo. No se infiere aprendizaje de política. n=1; CONTROL sigue fuera de este resumen.
