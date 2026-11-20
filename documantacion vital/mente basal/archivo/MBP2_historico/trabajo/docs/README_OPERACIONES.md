# Mente Basal Persistente 2

Campaña A/B/C sobre DEE thinking 2.2.0 y el kernel v27 congelado. La aplicación
nueva coordina preparación, observación, persistencia y archivo; no implementa
otra transición física.

## Condiciones

- **A — aislamiento:** díada basal móvil, sin inventario ambiental adicional.
- **B — interactivo:** la misma díada y dos portadores genéricos. El encuentro
  E1 en `t=16` cambia carga/dirección y habilita el encuentro E2 en `t=80`.
- **C — control:** mismo inventario que B; sólo E1 se desplaza de `z=63` a
  `z=66`. E2 queda idéntico, pero resulta inaccesible sin la primera relación.

A no está emparejado en recursos; el contraste causal principal es B frente a
C. Los tres mundos son condiciones, no tres réplicas estadísticas. Todo queda
instalado en `t0` y no se programan entradas físicas posteriores.

## Operaciones

Desde esta carpeta:

```powershell
& .\tools\mbp2.ps1 -Action status
& .\tools\mbp2.ps1 -Action stop
& .\tools\mbp2.ps1 -Action repackage
```

`stop` solicita un único `collect_stop` determinista por mundo. `repackage`
jamás vuelve a cortar ni reinicia un worker: sólo reutiliza los tres cortes
terminales ya validados.

El supervisor independiente publica el resultado final en:

`MENTE_BASAL_PERSISTENTE_2_ABC_2H_RESULTADOS.zip`

## Límites de interpretación

Las consultas Q_XY y Q_XZ se ejecutan únicamente en forks diagnósticos de los
checkpoints; no vuelven a A/B/C. Una diferencia confirma disponibilidad
funcional de la historia física bajo ese lector. No constituye por sí sola
aprendizaje universal, consciencia, autonomía o replicación.

