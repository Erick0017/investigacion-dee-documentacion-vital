# Cribado de especialistas: una, dos y cuatro unidades

Se ejecutaron seis preparaciones independientes en un Runtime N=67 por mundo: tres configuraciones y tres reservas por mundos/historias completos. Cada unidad incorpora cuerpo relacional con fuente inicial de carga cero, comparación física, sus propias fuentes adquiridas y ocho guardas fijas desde T0. Todos los nombres de puerto, incluidos los del cuerpo, llevan prefijo de unidad. La comprobación inicial encontró cero superposiciones; no se efectuaron reparaciones de geometría ni escrituras RAW/clock después de T0.

La discrepancia física produjo pregunta en t19, información con el signo de la fuente en t24 y utilización por una sonda común en t29: 8/8 unidades discrepantes. Las 6/6 unidades con expectativa y acontecimiento coincidentes no produjeron esa pregunta X ni su consecuencia. Las 14 relaciones diferenciales observadas conservaron exactamente su valor entre t5 y t72; esta última medida es pasiva, no acredita consulta renovable después de t29. Las 182 solicitudes externas fueron aplicadas. El contexto sensorial se introduce después de registrar la emisión en t5 y no codifica el error ni la acción correcta.

El conjunto de cuatro no es un compuesto cooperante: son especialistas coexistentes, sin conexión entre unidades reivindicada. La clasificación es `REFERENCE_SPECIALIST_ENSEMBLE`. Los inventarios iniciales son 23/46/92 sitios y las entradas 13/26/52 para una/dos/cuatro unidades. El dominio y sus buffers básicos permanecen N67 (9 624 416 bytes); scratch, instantáneas y observación añaden coste. Aumentar el número multiplica componentes y dosis, de modo que no se atribuye ventaja arquitectónica a ese aumento.

## Evidencia y reproducción

- `ENSEMBLE_SUMMARY.json`: denominadores, recursos, admisión y las catorce filas recalculadas.
- `INDEX.json`: las seis identidades y sus hashes.
- Cada caso conserva configuración, código exacto, estados completos T0/T5/T19/T29/T72, lecturas y vecindades causales alrededor de comparación, pregunta, llegada y uso.
- `RESTORE_CHECK.json`: otro proceso cargó T19 del mundo reservado de cuatro unidades, que todavía contiene las sondas pendientes de t26. Su continuación hasta t72 coincidió en RAW completo, clocks, tick, recibos y progreso operativo con la trayectoria original. El metadato de frontera serializada se distingue de la física.

Desde la raíz extraída, con CPython3.13 y el WHL congelado instalado:

```powershell
python -I -B src/endogenous/ensemble.py --config configuraciones/endogenous/ensemble.json --out resultados_nuevos/ensemble
python -I -B src/endogenous/ensemble_audit.py --results resultados_nuevos/ensemble
```

El auditor recalcula resultados a posteriori. No forma parte de los participantes y no devuelve sus comparaciones a MAIN. Los catorce módulos no se cuentan como catorce réplicas independientes: el denominador de preparación es seis mundos.
