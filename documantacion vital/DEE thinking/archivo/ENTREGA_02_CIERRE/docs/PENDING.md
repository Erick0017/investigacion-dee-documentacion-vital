# Pendientes y límites técnicos

## Deuda CORE05 cerrada con dominio finito

El descriptor provisional `temporal_phase_memory.core05.pending` fue sustituido
en esta revisión candidata por `temporal_phase_memory.core05.v1`, versión
`1.0.0`. El constructor procede de los runners primarios NRH04/NRH06 y sus locks
verificados; no se reconstruyó desde una narración ni se reemplazó por un
contador externo o un acumulador `s_reg`. El paquete incluye contrato,
controles, paridad, persistencia, ejemplo y comparación multibackend.

No se conserva un alias ejecutable del id provisional: nunca representó una
organización instanciable ni existe información de estado legacy que permita
restaurarlo como si fuese el constructor versionado. Los límites del port son
los horizontes, geometrías y transformaciones declarados en
`CORE05_PHASE_MEMORY.md`; no se extrapola `T_div=N+L` fuera de su familia.

## Cobertura diferencial finita

La matriz diferencial contiene ahora quince fixtures WHL y ejecuta cada
transición con denso secuencial, denso paralelo y Lazy en configuraciones de
1/2/4 hilos y tres repeticiones. Los tres grupos microscópicos antes abiertos
tienen testigo primario: evolución alcanzable de un huérfano, saturación DEMUX
de un destino ocupado, y tensión fuerte/protección de escritura. Los resultados
focales y sus hashes están en `MICROSCOPIC_BRANCH_AUDIT.md` y en el manifiesto
de fixtures.

Esto no convierte la batería finita en prueba exhaustiva. Además, no todas las
ramas preservadas en el source son alcanzables desde `tick`:

- el caso especial de huérfano en el postpaso DEMUX es un helper defensivo; el
  único productor de deltas omite todo destino cuyo estado de entrada tenga
  semántica huérfana, y la pasada base no crea esa semántica en otro destino;
- la cristalización es inalcanzable con `s_reg` empacado en 16 bits: incluso el
  máximo L1 de 26 vecinos da `floor(5,111,730 / 19,665) = 259`, por debajo del
  umbral 966;
- `demux_edge_min` y `ORPHAN_TTL` permanecen como elementos internos sin uso;
  no se cuentan como transiciones verificadas.

Estas ramas pertenecen a la regla local compartida, no a código alternativo de
los schedulers. Las afirmaciones de inalcanzabilidad tienen exactamente el
dominio del packing, constantes y productor DEMUX actuales.

Las organizaciones disponibles están verificadas sólo en los tamaños,
parámetros, geometrías y horizontes finitos descritos por `tested_domain` y
`context_horizon`. No se ha probado composición arbitraria, vida útil ilimitada,
fan-out físico implícito, inserción de estructuras después del primer tick ni
extrapolación de respuestas más allá del último readout declarado. C6H01 es un
testigo independiente de consulta posterior; no reemplaza los controles
no-update/no-learning de la composición A.

## Plataforma y persistencia

- Los binarios entregados se probaron en Windows x64 con MSVC 19.50. No se
  promete ABI compatible con otros toolchains.
- El snapshot usa checksum FNV para daño accidental, no autenticación contra
  modificaciones maliciosas.
- `Runtime::load_snapshot` conserva compatibilidad v1. La restauración
  autocontenida de `ComposedWorld` requiere v2: v1 no guardó catálogo, versiones,
  parámetros ni conexiones y no pueden inferirse sin inventar información.
- La publicación temporal y el reemplazo del mismo volumen reducen el riesgo de
  archivo parcial; no garantizan durabilidad frente a pérdida de energía o
  fallo de hardware/firmware.

## Rendimiento

Los benchmarks pertenecen a una sola máquina y ejecución, con tres repeticiones
por configuración. No se midió consumo energético. Lazy conserva recorridos
globales para clocks y postpaso, y no se anuncia como complejidad dispersa
completa. El selector de backend permanece explícito: no hay política adaptativa
oculta.

## Evidencia integrada vigente

La compilación Release limpia registrada en `validation/` aprobó los 15 targets,
incluye JUnit, consumidor instalado relocable y procedencia de los 18 artefactos
Release. El benchmark ampliado fue regenerado con 63 corridas exactas y métricas
de aplicación de evento, restore y total E2E. Estos resultados eliminan el
pendiente operativo de regeneración, sin convertir una batería finita en prueba
de equivalencia universal.

## Fuera de Entrega 02

Gestión/borrado/migración automática de historia, capacidad prolongada,
normalización para aparentar reserva ilimitada, GPU/FPGA, GUI, servidor,
robots, Rosettas industriales y autoenseñanza no demostrada corresponden a otro
alcance. También siguen sin promoverse actualización multiexperiencia
reutilizable, cierre ambiental nativo, enseñanza endógena, fan-out funcional o
replicación adquirida. No se incluyeron stubs que las presenten como
disponibles.

No hay un bloqueo técnico conocido para usar las capacidades marcadas como
disponibles dentro de sus contratos y plataforma probados. Los puntos anteriores
son límites de cobertura o extensiones pendientes, no incapacidades generales
del kernel DEE.
