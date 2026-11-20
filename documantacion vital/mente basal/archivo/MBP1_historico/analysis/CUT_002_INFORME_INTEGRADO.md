# Recolección científica CUT_002 — MENTE-BASAL-001

## Corte y continuidad

- Linaje: `MENTE-BASAL-001`; sesión: `SESSION-001-20261005T035032Z`.
- Inicio: T_ref=64, 2026-10-05 03:53:20.552 UTC / 2026-10-04 21:53:20.552 -06:00.
- Fin: T_collect=134856, 2026-10-05 07:29:05.490 UTC / 2026-10-05 01:29:05.490 -06:00.
- Intervalo: 134792 ticks en 12944.938 s humanos (3:35:44.938); promedio global 10.412719 ticks/s.
- El segmento contiene 16849 avances contiguos de 8 ticks, sin huecos ni solapamientos. Tiempo de kernel medido: 3747.3732714 s; tiempo de las llamadas de avance: 3747.7977882 s.
- Hubo una pausa inicial declarada entre el corte de T64 y `release_autonomy`: 265.209 s. Después no constan órdenes de pausa, reinicios, errores ni caídas. La política operativa incluyó esperas configuradas de 0.5 s entre bloques de 8 ticks; no son ticks DEE.
- Intervenciones operativas registradas: `release_autonomy` en la frontera T64 y `collect` en T134856. Entradas físicas nuevas: 0; cambios de recibos: 0; admisiones/rechazos posteriores: 0/0.
- Se crearon nueve checkpoints confirmados en el intervalo: uno de liberación, siete periódicos y el corte CUT_002.

La operación de recolección no detuvo el mundo. Una lectura posterior a la recolección observó el mismo mundo, sesión y PID 16864 en T168520, RUNNING y sin pausa, 33664 ticks después de T_collect.

## Comparación X64 → X134856

El soporte RAW y la ocupación permanecieron en 37 sitios. Cambiaron 10 coordenadas del RAW:

- Tres registros móviles conservaron exactamente contenido, estado, semántica, carga y dirección. Cada uno se desplazó 45 celdas toroidales por eje activo, porque 134792 mod 127 = 45: linaje relacional 4184, resultado de materia móvil 68 y contenido contextual 40. Sus tres coordenadas iniciales aparecen como retiradas y sus tres coordenadas finales como añadidas.
- Cuatro residuos ambientales estacionarios conservaron coordenada, dirección, estado y semántica, pero su s_reg cambió 0→344 en cada sitio.
- Los 30 soportes semantic=4 se conservaron registro por registro: 24 soportes ambientales 9300–9335 y seis soportes contextuales 9700–9705.

La suma s_reg cambió 4292→5668, explicada íntegramente por 4×344. No cambió el número de ocupados, el repertorio de estados, el repertorio semántico ni el recuento de direcciones. Los 2048383 clocks cambiaron uniformemente con delta modular 16802, igual a 134792 mod 19665; este avance uniforme no se interpreta como aprendizaje.

### Componentes documentados

- Linaje relacional: persiste como carga 4184 y se transporta según dirección (1,1,0).
- Materia alpha/beta: sus participantes separados ya no estaban presentes en T64; su resultado 68 persiste y se transporta según (0,1,1).
- Hub/contexto: el sitio fijo del hub no está ocupado en ninguno de los dos cortes; el contenido producido 40 persiste como portador móvil según (1,0,1).
- Rutas/fuentes: los 30 soportes semantic=4 permanecen exactos.
- Residuos ambientales: persisten en sus cuatro coordenadas y acumulan s_reg recurrentemente.

Clasificación descriptiva: PERSISTENCIA para 4184, 68, 40 y los soportes; DESPLAZAMIENTO para los tres portadores móviles; REORGANIZACIÓN local para los cuatro residuos; no se observó PÉRDIDA de soporte ni aparición de regiones nuevas.

## Eventos candidatos y replay dirigido

La telemetría mostró aumento reiterado de s_reg sin cambio de ocupación. Un replay diagnóstico aislado desde el checkpoint inmutable T64, sin entradas, localizó los primeros eventos en los residuos:

- T405, T409, T413 y T417: primer incremento 0→1, uno por sitio y separado por cuatro ticks.
- T796, T800, T804 y T808: segundo incremento 1→2.

Cada sitio repitió tras 391 ticks en esta ventana. El valor terminal 344 es compatible con la continuación de ese patrón hasta el corte. Es evidencia directa reconstruida por replay para las dos primeras recurrencias y evidencia terminal/telemetría para el intervalo largo; no se afirma una ley universal ni una causa única. El mecanismo candidato es una recurrencia de fase/ruta entre la preparación estacionaria y el paisaje semantic=4, no una región nueva ni una fuente externa.

No aparecieron nuevos estados, semánticas, direcciones, soportes o fusiones en los dos cortes. No se seleccionaron fenómenos sólo por ser favorables.

## Lectura funcional y límites

El lector congelado de `response1`, `response2`, `response3` y `context_hub` fue pasivo y devolvió cero tanto en T64 como en T_collect. Esto indica que esas coordenadas fijas estaban vacías en ambos cortes; no demuestra que los portadores móviles hayan desaparecido. El estado completo confirma la persistencia de 4184, 68 y 40.

No se reajustó el lector ni se aplicó una consulta transformativa al mundo principal. Por ello:

- persiste la estructura que contiene 40, pero su accesibilidad causal mediante una consulta futura no quedó comprobada en CUT_002;
- la acumulación de los cuatro residuos es una modificación histórica recurrente, pero no se demostró un uso funcional posterior;
- no se demostró fortalecimiento, degradación ni nueva combinación de capacidades;
- no se atribuye aprendizaje autónomo: después de T64 hubo evolución libre con fuentes/soportes preparados, sin experiencias externas nuevas.

## Integridad y reproducción

- Los checkpoints inicial y final, sus sidecars, el segmento histórico, telemetría y controles congelados forman la frontera inmutable del corte.
- 18/18 checkpoints examinados verificaron sus SHA-256 de sidecar.
- Un replay independiente T134088→T134856, sin eventos externos, coincidió exactamente con el checkpoint CUT_002 en RAW, clock, tick y recibos.
- Las herramientas de análisis y empaquetado creadas después de T_collect se rotulan como herramientas post-corte; no son datos generados por el mundo.
- El paquete incluye manifest y hashes propios. La prueba final valida CRC, hashes, carga de ambos checkpoints y extracción limpia.

No se registraron huecos, reinicios ni fallos del worker en el intervalo. El único fallo técnico durante el análisis fue un lanzamiento inicial con ruta Python incorrecta y un literal booleano corregido en una herramienta post-corte; ninguno tocó el linaje ni sus archivos inmutables.
