# Mente Basal Persistente 2 — informe integrado A/B/C

Campaña: `MBP2-ABC-TRIAL-60S`. Producto: DEE thinking 2.2.0; kernel DEE v27 congelado.
Este informe fue calculado fuera de los workers, desde checkpoints y segmentos conservados.

## Preparación y pregunta

A contiene la díada basal sin inventario ambiental adicional. B contiene dos portadores genéricos: el encuentro E1 cambia la ruta y hace accesible E2. C conserva el inventario de B, pero separa E1 en z; E2 queda presente y no es accesible sin el primer encuentro. Ningún mundo recibe entradas del host después de t0 por diseño.

La comparación principal B–C pregunta por contacto/contingencia con inventario inicial comparable. No es un control de orden con igual dosis efectiva: B puede recibir dos encuentros y C ninguno.

## Evidencia observada

- A: 0 encuentros predeclarados confirmados por el log; 0 entradas externas registradas; endpoint analizado T608.
- B: 2 encuentros predeclarados confirmados por el log; 0 entradas externas registradas; endpoint analizado T608.
- C: 0 encuentros predeclarados confirmados por el log; 0 entradas externas registradas; endpoint analizado T608.

## Comparaciones a edad DEE común

| Tick | carga A | carga B | carga C | B−C | query A | query B | query C |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 11 | 11 | 11 | 0 | 18 | 18 | 18 |
| 64 | 11 | 13 | 11 | 2 | 18 | 20 | 18 |
| 144 | 11 | 16 | 11 | 5 | 18 | 23 | 18 |
| 300 | 11 | 16 | 11 | 5 | 18 | 23 | 18 |
| 608 | 11 | 16 | 11 | 5 | 18 | 23 | 18 |

Los endpoints finales se informan por separado cuando sus ticks difieren; el analizador no retrodata un checkpoint posterior ni equipara tiempo de pared con edad DEE.

## Diagnóstico history ± query

Cada consulta se ejecutó en un fork aislado del checkpoint. La rama sin consulta avanzó la misma cantidad. Ningún estado diagnóstico volvió a A, B o C. Una diferencia de salida conserva el contenido físico disponible; por sí sola no demuestra aprendizaje general.

## Separación epistemológica

- **Observado:** RAW/clocks/métricas en snapshots, observaciones predeclaradas y entradas del log.
- **Ejecutado en diagnóstico:** ramas history+query y history sin query desde los cortes.
- **Reconstruido por replay:** no se atribuye replay tick a tick salvo que figure explícitamente en los artefactos de campaña; este analizador no inventa ticks de contacto ausentes del log.
- **Hipótesis:** que la diferencia B–C constituye adquisición ambiental acotada requiere que los contactos, retención y uso se sostengan conjuntamente bajo los controles.
- **No ensayado:** réplica estadística, aprendizaje universal, igual dosis con orden alternativo, autoenseñanza, continuidad indefinida y transferencia fuera de la consulta declarada.

## Límite de interpretación

A/B/C son condiciones, no réplicas independientes. El ambiente fue preparado con una contingencia física, aunque no contenía una respuesta de evaluación. El resultado máximo compatible con este análisis es una modificación histórica finita, retenida y funcionalmente accesible dentro del aparato; no un dictamen global de inteligencia o consciencia.
