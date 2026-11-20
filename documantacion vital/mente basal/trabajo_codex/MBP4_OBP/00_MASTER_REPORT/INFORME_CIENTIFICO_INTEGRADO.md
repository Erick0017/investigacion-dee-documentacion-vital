# MBP4 — Organización Basal Persistente

Campaña: `MBP4-OBP-CONSTITUTION-CLOSED-LOOP`  
Autor del proyecto: Ivan Erick Tlaltecatl Morales  
Motor: DEE thinking 2.2.0, kernel DEE Universe v27 sin modificaciones

## Resultado ejecutivo

Se construyó y ejecutó una composición fresh en un único `Runtime` v27 que combina una recurrencia R04 soportada por fuentes persistentes con una política móvil R14. La política fue modificada por una consecuencia ambiental y después realizó tres usos enlazados en los ticks relativos 8, 16 y 24. En cada uso, una consulta física convirtió la política A/B en una acción; al tick siguiente, un normalizador ambiental preparado convirtió esa acción de nuevo en política A/B. No hubo escrituras del host después de t0.

El tratamiento produjo 3/3 acciones exactas. Los siete controles requeridos interrumpieron la cadena en puntos distintos: `NO_INPUT` 0/3, `NO_ACTION` 0/3, `NO_INTERNAL_MEDIATION` 0/3, `NO_ENVIRONMENT_CHANGE` 0/3, `NO_RETURN` 1/3, `SHAM` 0/3 y `ROUTE_CUT` 1/3. La recurrencia basal permaneció exacta 32/32 medios ciclos en todos esos brazos.

El mecanismo es finito y `source-supported/driven`: los sensores, normalizadores y recursos ambientales futuros estaban preparados en t0. El resultado no demuestra autonomía adaptativa indefinida, selección intencional ni conciencia.

## Cadena causal ejecutada

1. Una política A de la organización encuentra el transductor `SENSOR`.
2. El kernel produce `ACTION0`.
3. Una consecuencia ambiental formada por `NORMALIZER` y, según la historia, `PENALTY0`, escribe política A o B.
4. La política viaja seis ticks sin nuevas escrituras externas.
5. Una consulta común produce `ACTION0` para A o `ACTION1` para B.
6. La acción selecciona una rama ambiental; `NORMALIZER` la transforma otra vez en la misma familia A/B.
7. La política retornada viaja y vuelve a usarse. El proceso se comprobó tres veces.

El host preparó la geometría y todos los participantes en t0, avanzó el `Runtime`, observó y guardó. No leyó el resultado para escribir una respuesta posterior.

## Identidad funcional y plasticidad

La identidad no se definió por hash RAW, posición o suma de carga. El panel congelado `Phi_B` exige conjuntamente:

- recurrencia R04 exacta;
- presencia de cuatro fuentes semánticas 4;
- disponibilidad de la primera acción;
- persistencia de la recurrencia después de agotarse la secuencia finita;
- invariancia funcional bajo una perturbación off-path congelada.

La parte estable y la parte plástica ocupan grados distintos del mismo mundo. Las historias A y B conservan el panel basal, pero una consulta común genera direcciones distintas. Esta es la evidencia operacional de estabilidad más plasticidad en el dominio ensayado.

## Discovery, freeze y holdout

Discovery cubrió bit 0/1, traslación, marco firmado/permutado y perturbación off-path. Después se congelaron arquitectura, panel de identidad, envolvente de eventos, closed-loop y holdouts. Los tres holdouts fresh, no usados para modificar el aparato, pasaron recurrencia y 3/3 acciones:

- H0: N=47, bit=1, marco permutado;
- H1: N=53, bit=0, marco firmado/permutado;
- H2: N=47, bit=1, otra traslación y marco.

La equivalencia Dense/Lazy fue exacta en tick, RAW completo y clock uint64 completo.

## Memoria múltiple y multi-evento

Dos historias independientes coexistieron en un `Runtime` N=59. `FULL` conservó seis expresiones: tres `ACTION1` para E1 y tres `ACTION0` para E2. `FULL−E1` conservó sólo E2; `FULL−E2` conservó sólo E1. Esto demuestra contribuciones causales separables en el panel declarado. No se interpretan como bits independientes ni como una composición semántica superior.

## Recurrencia y closed-loop

La recurrencia R04 fue exacta y source-supported. El retorno acción→política se ejecutó tres veces con recursos finitos. Se promueve `OBP-10` dentro de ese dominio finito porque las ablaciones localizaron entrada, mediación, acción, cambio ambiental, retorno y ruta. No se promueve una adaptación autosostenida: Ingeniería 01 había dejado ese mecanismo como no construido y MBP4 no convierte los recursos t0 en una fuente endógena.

## Continuidad MBP3

Se verificó el checkpoint original de MBP3 en tick 276832 con SHA-256 `6b7a646a2f48fc7f707c09ab10e16788878b326f712ed11719a727d501d586de`. Antes de instalar el entorno se observaron q34 y q27. La instalación congelada no sobrescribió ninguno de los registros ocupados del padre.

Tras 32 ticks, q34 y q27 conservaron cargas, direcciones y clocks completos en sus posiciones toroidales predichas. Una consulta diagnóstica sobre un fork volvió a utilizar q34. Sin embargo, al retirar ambos portadores históricos la firma OBP fue idéntica. Por tanto el resultado es:

`MBP3_PRESERVED_BUT_NOT_FUNCTIONALLY_INTEGRATED`.

No se escribió `s_reg=34`, no se reinsertaron recuerdos y ninguna rama control regresó a MAIN.

## Gates

- PASS: OBP-0, 1, 2, 3, 4, 5, 6, 8, 9, 10 y 11.
- PARTIAL: OBP-7; la familia admite traslaciones y marcos, pero conserva puertos relativos preparados.
- FAIL: OBP-12; MBP3 fue preservado y accesible, no causalmente integrado con OBP.
- NOT_TESTED: OBP-13; evolución larga se difirió explícitamente.

El mejor gate alcanzado es OBP-11. El ledger JSON es la autoridad automática de estados.

## Validación técnica

- reconstrucción T0→T32 igual al checkpoint entregado;
- `observe` pasivo;
- reanudación Dense/Lazy T32→T48 con RAW y clocks completos iguales;
- snapshot truncado rechazado por checksum sin alterar el válido;
- checkpoint MAIN T32 SHA-256 `cd09a4d94f72e00d9a5163c8dfd1d62e1528f1d146e4cb44ae23d261b3da09e6`;
- checkpoint MBP3+entorno T276864 SHA-256 `1b078daec248d8891f33e9d5df7d81ccb57b427dad8a1abaca65c8a59fcfdddd`.

## Límites

- La secuencia cerrada es finita y preabastecida.
- La interfaz sigue siendo una envolvente de colisiones relativas; no acepta eventos arbitrarios.
- La memoria móvil se consume y reconstruye mediante recursos ambientales preparados.
- Las dos historias múltiples están separadas; no se demostró combinación no entrenada entre ellas.
- MBP3 no cambió la respuesta OBP.
- El Documento Maestro V1 solicitado no estaba físicamente disponible en el árbol inspeccionado; se registra la ausencia y se incluye este addendum, sin fabricar ni sustituir el original.

## Clasificación epistemológica

Hecho computacional: ejecuciones, estados, snapshots y comparaciones exactas.  
Física interna DEE: colisiones, direcciones, semántica, clocks, rutas y fuentes v27.  
Interpretación operacional: identidad funcional, política, acción, ambiente y retorno.  
Hipótesis no confirmada: autonomía adaptativa indefinida e integración causal del conocimiento MBP3.  
Analogía excluida: cerebro, neurona, pensamiento o conciencia.
