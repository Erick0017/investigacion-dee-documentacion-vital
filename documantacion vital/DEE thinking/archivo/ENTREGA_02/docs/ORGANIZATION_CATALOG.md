# Catálogo y composición física

Esta capa instala plantillas antes de ejecutar y produce **un solo `Runtime`**.
Una conexión aceptada no copia salidas, no observa una respuesta para elegir una
ruta y no ejecuta un segundo mundo. El diagnóstico estático verifica lo que puede
deducirse de contratos y geometría; supervivencia, precedencia de ramas, fase e
interferencia permanecen como resultados de simulación v27.

## Cobertura

| Familia | Constructor público | Fuente | Estado y dominio |
|---|---|---|---|
| Transporte/redirección | `transport.axis.v1` | CORE05 / E1 | Disponible; ejes representables, distancia 1–20 |
| Aprendizaje relacional | `relation_learning.c6h01.v1`, `mobile_lineage.c7h03.v1` | CORE06 C6H01, C7H03 | Disponible; teacher explícito |
| Actualización/transferencia | `native_update_bridge.p01.v1` + `mobile_lineage.c7h03.v1` | PENSAMIENTO 01 | Disponible; consecuencia nativa en t12, cap v27 |
| Memoria relativa/selección histórica | `relative_history.i02.v1` | Ingeniería 02 | Disponible para H0/HA/HB sobre scaffold declarado |
| Integración/separación multicanal | `contextual_multichannel_recurrence.p02.v1` | Procesos 02 | Disponible para A/B/C; ausencia y carga cero no se identifican |
| Recurrencia/uso posterior | `query_recurrence.p01.v1`, `contextual_multichannel_recurrence.p02.v1` | PENSAMIENTO 01 / Procesos 02 | Disponible sólo en horizontes finitos documentados |
| Contexto/memoria distribuida | `distributed_context.i05.v1` | Ingenierías 05–06 | Disponible; dos centros, soporte persistente y lector |
| Memoria temporal por fase | `temporal_phase_memory.core05.pending` | CORE05 | **Pendiente**: falta portar constructor primario y oráculo reservado exactos; no es función exportable |

El catálogo no transforma la entrada pendiente en una incapacidad de DEE. Sólo
declara que Entrega 02 aún no dispone de una implementación pública auditable de
ese constructor CORE05.

## Contratos relevantes

- Los nombres y versiones son metadatos: nunca se escriben en `state`, `clock` o
  `s_reg`.
- Cada descriptor separa footprint inicial, relación funcional, región de
  lectura, contexto requerido y horizonte. Cada instancia expone parámetros,
  puertos, landmarks, registros inmutables de footprint, contratos de canal y
  `ResourceBudget`; no expone una API para mutar esas plantillas después de
  construir.
- Los canales instalados se cualifican como `instancia.canal`. El usuario presenta
  experiencias mediante `ComposedWorld::experience`, `experience_batch` o `probe`;
  estas operaciones validan rol, rango y tick del puerto antes de delegar la
  admisión física a `Runtime`. No editan vóxeles.
- Las conexiones verifican rol, tipo de contribución, dirección, orden temporal y
  llegada toroidal. `PortSpec::maximum_connections` limita explícitamente la
  capacidad por puerto. Una incompatibilidad o exceso produce un diagnóstico y
  bloquea `build()`; el valor no clona portadores.
- `build()` instala todas las organizaciones de una sola vez y antes de `advance()`.
  No se implementa inserción inocua de estructuras en mundos ya evolucionados.
- Las consultas C6/C7 son transformativas. No se usan clones ocultos para conservar
  una memoria aparente.
- `cut_update_link` es un control físico declarado: una propuesta de carga cero
  común alcanza el encuentro t12 y redirige el producto fuera de la ruta de consulta.
  No retira el suministro ni copia un resultado.
- El snapshot v2 incorpora tanto el manifiesto inerte como una receta canónica
  autocontenida: dimensión, IDs y versiones exactas de constructores, IDs de
  instancia, anchors, parámetros validados y conexiones (incluido `purpose`).
  `ComposedWorld::load_snapshot(path[, catalog])` vuelve a instanciar esa receta
  mediante `OrganizationCatalog`, regenera puertos/landmarks/conexiones, valida
  versión, esquemas, canales y manifiesto, y sólo entonces instala el `Runtime`
  guardado. Rechaza v1 porque ese formato no contiene una receta. La operación
  `restore_snapshot` conserva además la exigencia de que el plan receptor tenga
  la misma identidad. Tick, RAW, clocks, colas y backend siguen perteneciendo al
  payload operativo, no al manifiesto de composición.
- Un mismo puerto de salida no puede conectarse dos veces: el planificador no
  implementa fan-out clonando una relación física.

## Composiciones ejecutables

`composition_a_learning_update.cpp` selecciona tres organizaciones por catálogo:
linaje C7H03, puente de actualización y tren de consultas. Las conexiones se
declaran explícitamente. La prueba incluye tratamiento, ausencia de marcador,
no-update real (sin reactivos del puente pero con teacher), no-learning (sin
teacher y con recursos comunes), valor reservado y corte físico. C6H01 no se usa
como sustituto de esta composición A/C7.

`composition_b_context_multichannel.cpp` selecciona scaffold distribuido,
historia HA y recurrencia A/B. La prueba adicional compara HA/HB, ausencia de B,
portador B de carga cero, corte de la recurrencia y sham de igual carga/estado/
dirección/tiempo cuya trayectoria paralela no visita el redirect en el horizonte.

La prueba C6H01 presenta la consulta en t6, después de haber avanzado el mismo
mundo. Esto comprueba continuidad por API y evita llamar *streaming* a una agenda
enteramente instalada en t0.

Todos estos contratos son finitos: sólo cubren los rangos, geometrías y
horizontes declarados. La memoria temporal por fase CORE05 continúa como entrada
`Pending`; ninguna de las composiciones disponibles se documenta como reemplazo.
