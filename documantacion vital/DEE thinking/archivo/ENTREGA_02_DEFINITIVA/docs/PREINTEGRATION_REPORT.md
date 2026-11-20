# Preintegración final de Entrega 02

## Alcance y baseline

Esta ejecución partió de
`DEE_thinking_ENTREGA_02_CIERRE_Y_FRONTERA_RESULTADOS.zip`, SHA-256
`532b195e2931c693f343ea782f399fd8b546f461f2e604f7b8c2b264c63e1c80`.
El kernel sigue siendo DEE v27 congelado; su fuente canónica registrada tiene
SHA-256 `44a80f7863d78f596099ddf7d41c9947fa8513503f65067097f1f3b05a8207ab`.
No se modificaron la biblioteca estable, el catálogo público ni los ZIP
anteriores. Los ports y el laboratorio sólo existen bajo `candidates/` y
`laboratory/preintegration/`.

El baseline directo ejecutó el consumidor instalado, memoria de fase CORE05
(144 comprobaciones), y persistencia entre procesos productor→consumidor con
RAW, clock, evento pendiente, conexión y futuro exactos. La reconstrucción
Release limpia del producto heredado ejecutó 15/15 tests y produjo los 18
artefactos esperados. Por ello no se reabrieron como pendientes:

- `temporal_phase_memory.core05.v1`;
- evolución orphan alcanzable;
- saturación DEMUX sobre destino ocupado;
- tensión fuerte y protección de escritura;
- cierre de regresión Dense/Lazy/paralelo.

## Matriz de recuperación histórica

| Línea | Fuente primaria consultada | Interpretación conservada | Estado previo | Trabajo de esta sesión | Prueba local | Pendiente antes de integrar |
|---|---|---|---|---|---|---|
| H1 retardo→posición | CORE05 NRD05/NRH05: runners, lock y resultados con hashes en `candidates/h1_delay_position/EVIDENCE.json` | La coincidencia física selecciona un hub espacial; no es la memoria de fase ya portada ni tiempo continuo | respaldado, no portado | constructor/API C++ `0.1.1-candidate`, controles y guardas de dominio | 11/11 labels nativos, calibración invertida 1/11, target ausente, Dense/Lazy exactos, dos rechazos de dominio | descriptor público, presupuesto, serialización de labels, persistencia del contrato y política de colisiones |
| H2 repertorios separados | CORE07 C7H02 runner, lock y resultado con hashes en `candidates/h2_destination_repertoires/EVIDENCE.json` | Fibras separadas conservan acceso individual; solapar produce composición con pérdida de identidad individual | respaldado, no portado | constructor/API C++ `0.1.1-candidate` para panel separado y solapado, con cargas/tiempos/wrap validados | K=3 Dense/Lazy, K=7 Lazy, presupuestos, solapamiento y off-fiber; dos rechazos de dominio | contrato dinámico de banco, footprint/puertos, vector de canales en snapshot y coste; K=40 histórico no se convierte en constante universal |
| H3 reparación funcional | CORE17 C17E02/C17E03, runners y holdout identificados en `candidates/SOURCE_REVIEW.md` | Reconstrucción desde una copia redundante entrenada por separado; no replicación adquirida | respaldado, no portado | runner C++ aislado, contrato, telemetría reducida y validador | 14 casos en dos geometrías: tratamiento y offpath 2/2; cinco controles causales 0/2 | API de alto nivel, decisión sobre daño acoplado, snapshot y confirmación multibackend; no publicar como replicación |
| H4 accesibilidad | Ingeniería 03–04.5/POST, NRD01/NRD02/P01R y hashes en `candidates/accessibility/primary_evidence_summary.json` | Efecto de challenge condicionado por historia; POST conserva acoplamiento corregido sin reinstanciación funcional | respaldado como diagnóstico, no como organización | contrato explícito y verificador de seis invariantes; no se inventó `make_reachable` | seis checks del resumen primario y separación nativo/diagnóstico | rutas primarias autocontenidas para recalcular hashes y, si se desea ejecución de producto, observer/aparato congelado; permanece contrato, no builder |

Los estados de la tabla son técnicos. Ninguno de los cuatro candidatos se
registró en `OrganizationCatalog`.

## Fichas de evidencia de los candidatos

### H1 — `delay_position_bank.core05.nrh05.candidate.v1`

- **Representación:** banco de fibras probe/target, labels espaciales y
  coincidencia en un hub.
- **Intervención:** el host codifica un retardo permitido; no escribe el canal
  ganador.
- **Lectura:** firma completa de state, semantic, dirección y `s_reg` en el hub.
- **Controles:** calibración invertida y ausencia de target.
- **Dominio local ejecutado:** un frame del holdout histórico, once labels, fondo vacío,
  cardinalidad ortogonal, carga sin cap y sin auto-wrap.
- **Propuesta de integración posterior:** constructor versionado y experimental
  primero; añadir persistencia y consumidor antes de considerar catálogo.

### H2 — `destination_repertoires.core07.c7h02.candidate.v1`

- **Representación:** relaciones sobre fibras destino disjuntas; un panel
  separado y otro de solapamiento.
- **Lectura:** respuestas por canal y contabilidad de soporte/carga; no sólo la
  suma global.
- **Controles:** solapamiento que pierde identidad individual y ruta off-fiber
  con inventario comparable.
- **Dominio local ejecutado:** K=3 y K=7, semantic 1, fondo vacío, destinos
  inicialmente vacíos, tiempos ordenados y suma bajo cap.
- **Propuesta de integración posterior:** fijar capacidad/footprint por puerto y
  persistir la lista de canales sin convertir metadata en fan-out físico.

### H3 — `repair_core17.redundant_learned_copy.v0`

- **Representación:** dos copias presentes desde la preparación y entrenadas por
  interacciones separadas; daño explícito de la primera y transporte desde la
  segunda.
- **Controles:** copia no entrenada, dirección reseteada, ausencia, corte de
  ruta, corte fuera de ruta y receptor incorrecto.
- **Resultado local:** tratamiento y corte fuera de ruta reconstruyen y
  responden a la consulta fresh en ambas geometrías; los controles causales no.
- **Recursos:** las dos copias/portadores fuente se consumen en este aparato;
  su persistencia o reutilización no fue probada.
- **Límite:** modalidad `ACOPLADA_DIAGNOSTIC`; el host programa daño e
  inyecciones. No se crea una segunda copia a partir de la primera.
- **Propuesta de integración posterior:** mantener experimental hasta decidir
  el contrato del daño y completar snapshot/paridad Dense.

### H4 — `accessibility.history_conditioned.finite.v0`

- **Representación:** diferencia `challenge(H)-baseline(H)` sobre la misma
  historia, con diagnósticos en clones.
- **Resultado recuperado:** NRD01/NRD02 y POST distinguen acceso condicionado
  por historia; POST no demuestra reinstanciación ni el borde refractario→competente.
- **Límite:** esta sesión no reejecutó las campañas históricas ni creó un
  planificador. El resultado entregado es un contrato documental verificable.
- **Propuesta de integración posterior:** sólo como instrumento diagnóstico si
  se congela un aparato autocontenido y se incorpora la procedencia primaria.

## Laboratorio nuevo: experiencias sucesivas y retorno reutilizable

### Pregunta y preparación

Se mantuvo una sola organización y un mismo `Runtime`, sin reset, con tres
consultas del mismo canal admitidas en `t=6,40,74`; los readouts fueron
`t=11,45,79`. La carga de consulta fue 13. El entrenamiento inicial, las
consultas y el soporte común de fase son entradas externas registradas, por lo
que la modalidad es **ACOPLADA**.

Se compararon tres brazos con iguales admisiones de training, consultas y
soporte común:

1. `INTACT`;
2. `CUT_RETURN`, con corte físico en `t=27` y encuentro en `t=28`;
3. `SHAM_PARALLEL`, con intervención comparable fuera del enlace.

### Mediciones

| Backend | Filas de telemetría | Fallbacks | Intact | Sham | Cut |
|---|---:|---:|---|---|---|
| Lazy-4 | 1.200 | 0 | 25→38→51 | 25→38→51 | 25→13→13 |
| Dense-1 | 1.200 | 0 | 25→38→51 | 25→38→51 | 25→13→13 |

Las 1.200 filas físicas coinciden exactamente entre backends al excluir sólo
`backend`, `evaluated`, `used_backend` y `used_threads`; `tick` y `clock`
también coinciden, y el tiempo de pared no forma parte de la telemetría. En
`t=11` todos los brazos todavía son iguales.
Después del corte, el readout intacto/sham conserva los incrementos; el corte
no. El producto observado en `t=11` participa en el readout de `t=45`, y el de
`t=45` participa en el de `t=79`. El producto final de `t=79` no tiene otro uso
medido en este horizonte.

### Qué limitación anterior se superó y cuáles permanecen

Se corrigió la desigualdad de admisión del control: las tres consultas se
aplicaron en los mismos ticks de los tres brazos. También se midieron dos
reutilizaciones físicas acumulativas del mismo estado/readout, no sólo una
nueva carga final. El sham reproduce los readouts intactos, aunque no iguala el
estado global completo.

Permanecen dos límites deliberadamente visibles: el contexto está preparado y
las consultas posteriores son externas. El experimento no muestra adquisición
del contexto, derivación de una relación, autoenseñanza, cierre ambiental
autónomo, fan-out ni sostenibilidad indefinida. La secuencia es una composición
aditiva finita y un retorno físico reutilizado; no se renombra como aprendizaje
multiexperiencia.

## Validación técnica

- Baseline heredado: 15/15 tests Release; consumidor instalado relocable;
  persistencia entre procesos; 18 artefactos Release.
- Panel candidato: siete tests CTest (H1, H2, H3 runner, H3 validator, H4
  contract, laboratorio Lazy y Dense). El JUnit entregado registra el resultado
  final limpio.
- H1/H2: equivalencia RAW+clock Dense/Lazy donde se declara.
- H3: validador causal separado; por ahora el runner local usa Lazy-4.
- Laboratorio: igualdad física exacta Lazy/Dense, cero fallbacks y admisiones
  comparables.
- La comprobación final se ejecuta desde una extracción limpia antes de publicar
  el ZIP; `MANIFEST.json` y `HASHES.sha256` se regeneran durante el empaquetado.

## Trabajo no ejecutado o no promovido

- No se intentó fan-out o replicación adquirida: CORE17 aportó reparación desde
  copia redundante, no un receptor genérico que aprenda a convertirse en copia.
- No se ejecutó una nueva familia de transferencia entre representaciones;
  H1 aporta retardo→posición como port histórico candidato.
- No se obtuvo adquisición/revisión de una relación por dosis sucesivas; sólo
  tres experiencias admitidas y transformación acumulativa en un mismo aparato.
- H4 no se convirtió en builder y sus campañas primarias no se reejecutaron.
- Ningún candidato se añadió al catálogo estable ni se abrió Entrega 03.

## Decisiones para una autorización posterior

| Componente | Evidencia disponible | Decisión de integración requerida | Regresión mínima si se autoriza |
|---|---|---|---|
| H1 retardo→posición | port + controles + paridad local | versión pública, presupuesto y labels persistentes | constructor/API, snapshot entre procesos, Dense/Lazy y consumidor |
| H2 repertorios | port + panel separado/solapado | contrato de banco dinámico y límites de capacidad | K reservado, overlap/off-fiber, snapshot vectorial, consumidor |
| H3 reparación | realización candidata: 14 casos emparejados y seis controles | si el protocolo acoplado pertenece al catálogo o sólo al laboratorio | Dense/Lazy, snapshot, daño/cortes, recursos consumibles y fresh reservado |
| H4 accesibilidad | contrato + procedencia reducida | si se integra como herramienta diagnóstica | fuentes primarias verificables y observer congelado |
| Retorno reutilizable | dos usos posteriores, corte y sham | mantener experimental o diseñar adquisición real | otra geometría/contenido, relación adquirida y control de contexto |

## Dependencias hacia Entrega 03

| Necesidad potencial | Disponible ahora | Candidato necesario | Hipótesis todavía abierta | Consecuencia |
|---|---|---|---|---|
| Codificación temporal a ubicación | memoria de fase estable; H1 aislado | integrar H1 si la aplicación requiere readout espacial | generalidad fuera del dominio congelado | no bloquea usos que lean fase directamente |
| Repertorios independientes | mecanismos históricos y H2 aislado | integrar H2 para API de banco | capacidad fuera de K probado | bloquea afirmar repertorio dinámico general, no composiciones fijas |
| Recuperación desde redundancia | realización candidata H3 ejecutada | definir contrato acoplado y recursos consumibles | replicación adquirida no demostrada | permite estudiar redundancia preparada, no auto-replicación |
| Continuidad/retorno | composición finita ejecutada | candidato experimental F1/F2 | adquisición y cierre ambiental siguen abiertos | no anunciar aprendizaje continuo ni autonomía |
| Accesibilidad | diagnóstico H4 | observer/aparato autocontenido | planificador nativo universal no existe | no bloquea builders explícitos; sí cualquier promesa de reachability general |

La siguiente acción no es abrir Entrega 03 automáticamente: corresponde revisar
qué filas se autorizan para integración estable y bajo qué versión y dominio.
