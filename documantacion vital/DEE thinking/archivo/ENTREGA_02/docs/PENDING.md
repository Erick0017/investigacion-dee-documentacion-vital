# Pendientes y límites técnicos

## Extensión explícitamente no implementada

- `temporal_phase_memory.core05.pending` permanece como descriptor no
  instanciable. Falta portar el constructor primario exacto y un oráculo
  reservado identificable de CORE05. El catálogo no exporta una función vacía
  ni sustituye este mecanismo por un acumulador `s_reg`.

Esta brecha es específica: no invalida transporte, C6H01, C7H03, historia
relativa, recurrencia o contexto dentro de sus dominios declarados, pero tampoco
autoriza a presentar esos testigos como memoria temporal por fase CORE05.

## Cobertura diferencial finita

La equivalencia multibackend se midió en doce fixtures WHL, configuraciones de
1/2/4 hilos y repeticiones. No constituye una prueba exhaustiva del espacio de
microestados. Quedan sin fixture primario específico:

- evolución/postpaso particular de huérfanos;
- saturación DEMUX sobre destino ya ocupado;
- guardas de tensión fuerte/protección de escritura.

Estas ramas pertenecen a la regla local compartida, no a código alternativo de
los schedulers. La cristalización no es alcanzable bajo el límite empacado de
16 bits de `s_reg` y su umbral actual; esa deducción tiene ese dominio exacto.

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

La compilación Release limpia registrada en `validation/` aprobó los 13 targets,
incluye JUnit, consumidor instalado relocable y procedencia de los 15 artefactos
Release. El benchmark ampliado fue regenerado con 63 corridas exactas y métricas
de aplicación de evento, restore y total E2E. Estos resultados eliminan el
pendiente operativo de regeneración, sin convertir una batería finita en prueba
de equivalencia universal.

## Fuera de Entrega 02

Gestión/borrado/migración automática de historia, capacidad prolongada,
normalización para aparentar reserva ilimitada, GPU/FPGA, GUI, servidor,
robots, Rosettas industriales y autoenseñanza no demostrada corresponden a otro
alcance. No se incluyeron stubs que las presenten como disponibles.

No hay un bloqueo técnico conocido para usar las capacidades marcadas como
disponibles dentro de sus contratos y plataforma probados. Los puntos anteriores
son límites de cobertura o extensiones pendientes, no incapacidades generales
del kernel DEE.
