# Informe técnico integrado — DEE thinking Entrega 02

## Base preservada y procedencia

La implementación vive en un árbol separado de Entrega 01. El ZIP oficial de
Entrega 01 se verificó antes de trabajar y conservó SHA-256
`e263f27243e73cb8f348319ecfe858310cb1ff8e4b137bbe014b99429dc16661`.

La regla local y los drivers se trazan al source v27 de SHA-256
`44a80f7863d78f596099ddf7d41c9947fa8513503f65067097f1f3b05a8207ab`.
El WHL, binario y paquete de fixtures se identifican en
`KERNEL_PROVENANCE.md`. La comparación normalizada de las secciones puras 1–7
del source canónico y la adaptación entregada cubrió 16 874 caracteres y no
halló diferencias de regla local.

## Implementación

### Runtime, build y snapshots

- El backend predeterminado y la firma histórica de cinco argumentos conservan
  denso secuencial.
- Se añadieron selección explícita densa paralela/Lazy, hilos y telemetría de
  agenda, trabajo y tiempos.
- Snapshot v2 guarda configuración y metadatos inertes; el lector conserva v1.
- Los snapshots de `ComposedWorld` v2 añaden una receta canónica autocontenida.
  `ComposedWorld::load_snapshot(path[, catalog])` reconstruye el plan mediante
  `OrganizationCatalog`, regenera organizaciones/conexiones/landmarks y valida
  esquema, versión de constructor, manifiesto, dimensión y canales antes de
  mover el `Runtime`. El formato v1 sigue siendo importable por `Runtime`, pero
  no permite esa reconstrucción porque nunca almacenó la receta.
- La prueba v1 usa un archivo real escrito por Entrega 01, con evento pendiente
  en `t=5`, y compara su futuro.
- Escritura de snapshot: temporal exclusivo en el mismo directorio, cierre y
  publicación por reemplazo/movimiento de la plataforma sin borrar primero el
  destino anterior.
- El paquete CMake instalado exporta `DEE::thinking` y su dependencia de
  threads. El consumidor se configura en un build separado y sólo incluye
  headers públicos.

### Catálogo y composición

Las siete familias requeridas tienen representación. Las entradas marcadas
disponibles poseen descriptor, rangos, builder, puertos, ejemplo o recorrido
ejecutable y prueba. CORE05 temporal por fase se incorporó como
`temporal_phase_memory.core05.v1`, recuperado de NRH04/NRH06 con controles,
paridad, persistencia y comparación multibackend.

El contrato público ya no reduce una organización a nombre y puertos. Cada
descriptor separa `initial_footprint`, `functional_relation`, `read_region`,
`required_context` y `context_horizon`; cada instancia expone registros de
footprint inmutables, contratos de canal y `ResourceBudget`. Los puertos declaran
`maximum_connections`, que el planificador usa como capacidad explícita y no
como permiso para clonar portadores.

`CompositionPlanner` comprueba lo estáticamente decidible y separa condiciones
que requieren simulación. Rechaza roles/tipos/rangos/direcciones/rutas,
solapamientos, fan-out físico y conexiones obligatorias ausentes cuando el
contrato no las admite. Las composiciones A y B usan un único `Runtime`: no
copian resultados entre mundos ni calculan respuestas esperadas en C++.

La composición A cubre linaje/actualización C7H03 con controles separados:
tratamiento intacto, marcador omitido, **no-update** (teacher conservado y ambos
reactivos del puente omitidos), **no-learning** (teacher omitido y recursos
comunes de actualización conservados), valor reservado y corte físico. No se
usa el testigo C6H01 como sustituto de A. C6 permanece en una composición
independiente que presenta una consulta nueva en `t=6` después de avanzar el
mismo mundo.

La composición B integra historia, contexto distribuido, canales y recurrencia.
Compara HA/HB, B ausente/B con carga cero, corte que alcanza el redirect y un
**sham** de igual admisión/campos que recorre una trayectoria paralela y no
alcanza el redirect dentro del horizonte probado.

## Validación ejecutada

Plataforma: Windows 10.0.19045 x64, Visual Studio Community 2026 18.5.0,
MSVC 19.50.35729 (toolset 14.50.35717), CMake 4.2.3-msvc3, Ninja y Release.

El `CMakeLists.txt` vigente configura **15 targets CTest**, incluidos
`composition_snapshot_restore`, `core05_phase_memory` y
`cross_process_persistence`. Una compilación Release con MSVC 19.50.35729 aprobó
**15/15**; JUnit, log, hashes de evidencia y procedencia de los 18 artefactos
Release están vinculados en `validation/`. El consumidor
instalado se configuró contra una copia relocada del paquete CMake y terminó con
código cero.

La persistencia entre procesos se ejecutó literalmente: un proceso A construyó
learner→reader, aplicó entrenamiento, dejó una consulta pendiente, guardó un
checkpoint y un futuro de referencia y terminó. Un proceso B nuevo reconstruyó
ambos `ComposedWorld` sin planner proporcionado por el llamador, continuó y
comparó RAW, clock, recibos, tick efectivo, conexión, manifiesto y respuesta 25.

La validación integrada informó:

- 15 fixtures WHL: igualdad RAW+clock exacta;
- runtime: 89 checks, cero fallos;
- organizaciones de referencia: 44 checks, cero fallos;
- persistencia v1/v2: 53 checks, cero fallos, incluidas regresiones de payload
  malformado con checksum válido;
- backend: 10 146 checks, cero fallos (15 fixtures × 7 configuraciones × 3
  repeticiones, comparación por tick);
- catálogo/composición ampliado, controles no-update/no-learning y sham: target
  aprobado;
- restore de composición autocontenido: 22 checks, cero fallos;
- consumidor instalado: entrada posterior, restore autocontenido v2 y futuro
  RAW+clock exacto tras cambiar de backend.

## Benchmark técnico

`validation/backend_benchmark.json` conserva 63 corridas nuevas: tres estados
(escaso N=31, denso N=17 e histórico/evolucionado N=31), siete configuraciones,
tres repeticiones y cuatro ticks. Todas fueron RAW+clock exactas y ninguna usó
fallback.

Medianas del bucle de cuatro ticks (milisegundos):

| Caso | Denso sec. | Denso paralelo 2 | Denso paralelo 4 | Lazy 1 | Lazy 2 | Lazy 4 |
|---|---:|---:|---:|---:|---:|---:|
| escaso | 182.65 | 138.50 | 111.19 | 4.71 | 7.93 | 4.68 |
| histórico/evolucionado | 189.22 | 125.06 | 122.50 | 5.26 | 3.94 | 3.92 |
| denso | 28.95 | 17.17 | 17.12 | 35.20 | 26.74 | 23.43 |

El resultado desfavorable Lazy-1/denso se conserva. La dispersión entre
repeticiones impide convertir la mediana de cuatro hilos en garantía frente a
dos. El JSON separa inicialización, construcción del trabajo,
evaluación local, postpaso/copia, total del kernel, agenda de evento, 100
observaciones y persistencia. No se deriva una afirmación de energía ni de
aceleración universal.

El benchmark añade, fuera de las filas del kernel, coste
de agenda del evento, pared de la frontera que lo aplica, tiempo reportado por el
kernel, estimación etiquetada de aplicación/wrapper, restore del snapshot y total
end-to-end. En esta ejecución fueron 0.015 ms de agenda, 5.587 ms de frontera,
0.012 ms estimados de aplicación/wrapper, 0.967 ms de restore y 78.303 ms E2E;
son medidas de una corrida local, no garantías universales.

## Correcciones realizadas durante integración

- Se eliminó la mezcla de instalaciones Visual Studio y el consumidor se movió
  a una ruta de build corta para evitar el límite de ruta de MSVC.
- Se absolutizó el prefijo instalado antes de configurar el consumidor.
- La nomenclatura distingue C6H01 de C7H03 y conserva el alias anterior.
- Los límites del escritor/lector de snapshot y sus invariantes se alinearon;
  contenido inválido se rechaza antes de sustituir una instancia.
- El manifiesto de composición identifica el plan estable, no el tick mutable.
- El consumidor usa un snapshot temporal único, sin depender de un directorio
  de trabajo escribible compartido.

## Alcance del estado técnico

El estado técnico global se determina tras compilar, ejecutar CTest, benchmark,
consumidor instalado, dependencias nativas, extracción limpia, reconstrucción y
verificación de MANIFEST/HASHES. Esas operaciones no son un dictamen científico.
Los límites exactos de CORE05 y las preguntas experimentales no promovidas
están en `PENDING.md` y `CLOSURE_AND_FRONTIER_REPORT.md`.
