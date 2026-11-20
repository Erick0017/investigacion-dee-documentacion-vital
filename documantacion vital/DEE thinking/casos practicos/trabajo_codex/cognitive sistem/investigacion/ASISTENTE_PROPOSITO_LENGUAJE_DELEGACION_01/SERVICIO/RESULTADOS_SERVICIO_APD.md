# APD01: servicio persistente, resultados y continuación

Una genealogía física ASISTENTE_MAIN contiene el piloto, los dos futuros técnicos interrumpidos, R03 con recarga y R04 de un propietario. Las ventanas permanecen separadas. No se suman sus tiempos para declarar una hora, ni se transfieren aprendizajes desde controles.

## Ventanas anteriores conservadas

```json
[
  {
    "scope": "Technical negative",
    "seconds": 1461.598571,
    "single_owner_hour_claimed": false,
    "window": "R01"
  },
  {
    "scope": "Technical negative",
    "seconds": 1793.500268,
    "single_owner_hour_claimed": false,
    "window": "R02"
  },
  {
    "scope": "Continuous world across two owners; not one uninterrupted owner",
    "seconds": 4411.296152400053,
    "single_owner_hour_claimed": false,
    "window": "R03"
  }
]
```

R01 conservó la carrera de observación del WAL y siete filas FIFO. R02 conservó el supuesto instrumental erróneo de que un BEGIN en cola ya era una cascada material y ocho filas; sus docencias rechazadas no son aprendizajes. R03 consumió esos mismos IDs una vez y completó un FINISH heredado real. R03 monitorizó26 fuentes y omitió el actor APD; sus bytes P26 exactos están archivados por separado, sin fingir monitorización retroactiva. R04 monitorizó27, incluido ese actor.

## Una sola instancia R04

Tiempo propio R04 habilitado: 3720.089030300034s; prueba de una hora con un único PID: True. PID nativo=81368; avance entre muestras frescas=35737ticks; ocio añadido=21632ticks. No hubo crédito de los ensayos anteriores. Limpieza operativa=True; utilidad cognitiva y limpieza son dimensiones distintas.
Corte final realmente alcanzado: ASISTENTE_MAIN T361114 N67, snapshot `estado/checkpoints/ASISTENTE_MAIN.T361114.abf0889a22e6.deetsnap.gz`, SHA-256 `0046cae1a790ddb85867379148b5eeb9ec36569a9834993aade9049885c1bd33`. Propietario detenido=True; pendiente/incierto=False. Continúa exclusivamente con el par completo, no con un fork desnudo. ACTIVO global no se promueve.

## Denominadores y resultados independientes

```json
{
  "all_literal_attempts_excluding_valid_technical_controls": 25,
  "burst_attempts": 0,
  "deliberately_invalid_attempts": 0,
  "material_literal_attempts_including_deliberately_invalid": 25,
  "nominal_attempts": 25,
  "queued": 25,
  "reserved_pending_token_attempts": 0,
  "valid_technical_control_attempts": 5
}
```

| Dimensión R04 | Resultado |
|---|---|
| Entradas nativas aplicadas/solicitadas | 4244/4244 |
| Memorias conforme a historia efectivamente enseñada | 10/10 |
| Pasos APD cuyo código coincide con historia docente | 17/17 |
| Números correctos dada la operación física emitida | 17/17 |
| Artefactos realmente completados | 17/17 |
| Artefactos completados dentro del presupuesto modelado2 | 15/17 |

Los seis pares del panel final fueron fijados antes de R04 y comprobados ausentes del índice de entradas anteriores; no son seis réplicas independientes. Las repeticiones del resto del calendario se declaran como tales. El docente beta− es explícito: si ya era−, no acredita una revisión nueva. No se reenseñó otra forma ni se ajustaron lectores ante fallos.

## Paneles finales y docencia real

```json
{
  "composition": {
    "archived_complete_execution_results": 2,
    "attempted": 2,
    "completed_transport": 2,
    "numeric_correct_given_actual_operator": 2,
    "partial_or_uncertain_transport_rows": 0,
    "queued_rows": 2,
    "scheduled": 2,
    "scheduled_transport_requests": 2,
    "scope": "New reserve situations only; scheduled_transport_requests/attempted/queued/completed count requests, which may contain several situations in the fixed final panel. Declared inherited actions remain separate. Complete results do not cover every possible partial execution. Numeric correctness, lexical history, artifacts and route usefulness stay separate."
  },
  "first_final_pair_opportunities": [
    {
      "first_physical_observation_if_any": {
        "abstention": false,
        "after_tick": 360704,
        "audit_issues": [],
        "before_tick": 355644,
        "completed_within_prepared_modeled_budget2": true,
        "composition_stage": null,
        "correct_given_actual_operator": true,
        "expected_from_explicit_history": 1,
        "form": "suma",
        "id": "apd63_post_funciones",
        "literal_pair_reserved_before_R03": false,
        "literal_pair_reserved_before_this_window": true,
        "modeled_price": 1,
        "numeric_result": 28,
        "procedure": "native",
        "raw_operands": [
          8,
          20
        ],
        "real_artifact_completed": true,
        "regime": 3,
        "route": -1,
        "word_command": 1,
        "word_matches_history": true
      },
      "first_scheduled_form": "suma",
      "first_scheduled_id": "apd63_post_funciones",
      "first_scheduled_native_result": {
        "abstention": false,
        "after_tick": 360704,
        "audit_issues": [],
        "before_tick": 355644,
        "completed_within_prepared_modeled_budget2": true,
        "composition_stage": null,
        "correct_given_actual_operator": true,
        "expected_from_explicit_history": 1,
        "form": "suma",
        "id": "apd63_post_funciones",
        "literal_pair_reserved_before_R03": false,
        "literal_pair_reserved_before_this_window": true,
        "modeled_price": 1,
        "numeric_result": 28,
        "procedure": "native",
        "raw_operands": [
          8,
          20
        ],
        "real_artifact_completed": true,
        "regime": 3,
        "route": -1,
        "word_command": 1,
        "word_matches_history": true
      },
      "first_scheduled_seconds": 3600,
      "first_transport_status": "completed",
      "later_physical_observations": 0,
      "pair": [
        8,
        20
      ],
      "scope": "First opportunity is never replaced by a later correct response. Physical first use, if transport previously rejected, is listed separately. These are finite literal operand pairs, not independent learners or distinct meanings."
    },
    {
      "first_physical_observation_if_any": {
        "abstention": false,
        "after_tick": 360704,
        "audit_issues": [],
        "before_tick": 355644,
        "completed_within_prepared_modeled_budget2": true,
        "composition_stage": null,
        "correct_given_actual_operator": true,
        "expected_from_explicit_history": -1,
        "form": "diferencia",
        "id": "apd63_post_funciones",
        "literal_pair_reserved_before_R03": false,
        "literal_pair_reserved_before_this_window": true,
        "modeled_price": 1,
        "numeric_result": 20,
        "procedure": "native",
        "raw_operands": [
          30,
          10
        ],
        "real_artifact_completed": true,
        "regime": 3,
        "route": -1,
        "word_command": -1,
        "word_matches_history": true
      },
      "first_scheduled_form": "diferencia",
      "first_scheduled_id": "apd63_post_funciones",
      "first_scheduled_native_result": {
        "abstention": false,
        "after_tick": 360704,
        "audit_issues": [],
        "before_tick": 355644,
        "completed_within_prepared_modeled_budget2": true,
        "composition_stage": null,
        "correct_given_actual_operator": true,
        "expected_from_explicit_history": -1,
        "form": "diferencia",
        "id": "apd63_post_funciones",
        "literal_pair_reserved_before_R03": false,
        "literal_pair_reserved_before_this_window": true,
        "modeled_price": 1,
        "numeric_result": 20,
        "procedure": "native",
        "raw_operands": [
          30,
          10
        ],
        "real_artifact_completed": true,
        "regime": 3,
        "route": -1,
        "word_command": -1,
        "word_matches_history": true
      },
      "first_scheduled_seconds": 3600,
      "first_transport_status": "completed",
      "later_physical_observations": 0,
      "pair": [
        30,
        10
      ],
      "scope": "First opportunity is never replaced by a later correct response. Physical first use, if transport previously rejected, is listed separately. These are finite literal operand pairs, not independent learners or distinct meanings."
    },
    {
      "first_physical_observation_if_any": {
        "abstention": false,
        "after_tick": 360704,
        "audit_issues": [],
        "before_tick": 355644,
        "completed_within_prepared_modeled_budget2": true,
        "composition_stage": null,
        "correct_given_actual_operator": true,
        "expected_from_explicit_history": 1,
        "form": "agrega",
        "id": "apd63_post_funciones",
        "literal_pair_reserved_before_R03": false,
        "literal_pair_reserved_before_this_window": true,
        "modeled_price": 1,
        "numeric_result": 21,
        "procedure": "native",
        "raw_operands": [
          9,
          12
        ],
        "real_artifact_completed": true,
        "regime": 3,
        "route": -1,
        "word_command": 1,
        "word_matches_history": true
      },
      "first_scheduled_form": "agrega",
      "first_scheduled_id": "apd63_post_funciones",
      "first_scheduled_native_result": {
        "abstention": false,
        "after_tick": 360704,
        "audit_issues": [],
        "before_tick": 355644,
        "completed_within_prepared_modeled_budget2": true,
        "composition_stage": null,
        "correct_given_actual_operator": true,
        "expected_from_explicit_history": 1,
        "form": "agrega",
        "id": "apd63_post_funciones",
        "literal_pair_reserved_before_R03": false,
        "literal_pair_reserved_before_this_window": true,
        "modeled_price": 1,
        "numeric_result": 21,
        "procedure": "native",
        "raw_operands": [
          9,
          12
        ],
        "real_artifact_completed": true,
        "regime": 3,
        "route": -1,
        "word_command": 1,
        "word_matches_history": true
      },
      "first_scheduled_seconds": 3600,
      "first_transport_status": "completed",
      "later_physical_observations": 0,
      "pair": [
        9,
        12
      ],
      "scope": "First opportunity is never replaced by a later correct response. Physical first use, if transport previously rejected, is listed separately. These are finite literal operand pairs, not independent learners or distinct meanings."
    },
    {
      "first_physical_observation_if_any": {
        "abstention": false,
        "after_tick": 360704,
        "audit_issues": [],
        "before_tick": 355644,
        "completed_within_prepared_modeled_budget2": true,
        "composition_stage": null,
        "correct_given_actual_operator": true,
        "expected_from_explicit_history": -1,
        "form": "resta",
        "id": "apd63_post_funciones",
        "literal_pair_reserved_before_R03": false,
        "literal_pair_reserved_before_this_window": true,
        "modeled_price": 1,
        "numeric_result": 19,
        "procedure": "native",
        "raw_operands": [
          28,
          9
        ],
        "real_artifact_completed": true,
        "regime": 3,
        "route": -1,
        "word_command": -1,
        "word_matches_history": true
      },
      "first_scheduled_form": "resta",
      "first_scheduled_id": "apd63_post_funciones",
      "first_scheduled_native_result": {
        "abstention": false,
        "after_tick": 360704,
        "audit_issues": [],
        "before_tick": 355644,
        "completed_within_prepared_modeled_budget2": true,
        "composition_stage": null,
        "correct_given_actual_operator": true,
        "expected_from_explicit_history": -1,
        "form": "resta",
        "id": "apd63_post_funciones",
        "literal_pair_reserved_before_R03": false,
        "literal_pair_reserved_before_this_window": true,
        "modeled_price": 1,
        "numeric_result": 19,
        "procedure": "native",
        "raw_operands": [
          28,
          9
        ],
        "real_artifact_completed": true,
        "regime": 3,
        "route": -1,
        "word_command": -1,
        "word_matches_history": true
      },
      "first_scheduled_seconds": 3600,
      "first_transport_status": "completed",
      "later_physical_observations": 0,
      "pair": [
        28,
        9
      ],
      "scope": "First opportunity is never replaced by a later correct response. Physical first use, if transport previously rejected, is listed separately. These are finite literal operand pairs, not independent learners or distinct meanings."
    },
    {
      "first_physical_observation_if_any": {
        "abstention": false,
        "after_tick": 360704,
        "audit_issues": [],
        "before_tick": 355644,
        "completed_within_prepared_modeled_budget2": true,
        "composition_stage": null,
        "correct_given_actual_operator": true,
        "expected_from_explicit_history": 1,
        "form": "total",
        "id": "apd63_post_funciones",
        "literal_pair_reserved_before_R03": false,
        "literal_pair_reserved_before_this_window": true,
        "modeled_price": 1,
        "numeric_result": 23,
        "procedure": "native",
        "raw_operands": [
          15,
          8
        ],
        "real_artifact_completed": true,
        "regime": 3,
        "route": -1,
        "word_command": 1,
        "word_matches_history": true
      },
      "first_scheduled_form": "total",
      "first_scheduled_id": "apd63_post_funciones",
      "first_scheduled_native_result": {
        "abstention": false,
        "after_tick": 360704,
        "audit_issues": [],
        "before_tick": 355644,
        "completed_within_prepared_modeled_budget2": true,
        "composition_stage": null,
        "correct_given_actual_operator": true,
        "expected_from_explicit_history": 1,
        "form": "total",
        "id": "apd63_post_funciones",
        "literal_pair_reserved_before_R03": false,
        "literal_pair_reserved_before_this_window": true,
        "modeled_price": 1,
        "numeric_result": 23,
        "procedure": "native",
        "raw_operands": [
          15,
          8
        ],
        "real_artifact_completed": true,
        "regime": 3,
        "route": -1,
        "word_command": 1,
        "word_matches_history": true
      },
      "first_scheduled_seconds": 3600,
      "first_transport_status": "completed",
      "later_physical_observations": 0,
      "pair": [
        15,
        8
      ],
      "scope": "First opportunity is never replaced by a later correct response. Physical first use, if transport previously rejected, is listed separately. These are finite literal operand pairs, not independent learners or distinct meanings."
    },
    {
      "first_physical_observation_if_any": {
        "abstention": false,
        "after_tick": 360704,
        "audit_issues": [],
        "before_tick": 355644,
        "completed_within_prepared_modeled_budget2": true,
        "composition_stage": null,
        "correct_given_actual_operator": true,
        "expected_from_explicit_history": -1,
        "form": "quita",
        "id": "apd63_post_funciones",
        "literal_pair_reserved_before_R03": false,
        "literal_pair_reserved_before_this_window": true,
        "modeled_price": 1,
        "numeric_result": 19,
        "procedure": "native",
        "raw_operands": [
          26,
          7
        ],
        "real_artifact_completed": true,
        "regime": 3,
        "route": -1,
        "word_command": -1,
        "word_matches_history": true
      },
      "first_scheduled_form": "quita",
      "first_scheduled_id": "apd63_post_funciones",
      "first_scheduled_native_result": {
        "abstention": false,
        "after_tick": 360704,
        "audit_issues": [],
        "before_tick": 355644,
        "completed_within_prepared_modeled_budget2": true,
        "composition_stage": null,
        "correct_given_actual_operator": true,
        "expected_from_explicit_history": -1,
        "form": "quita",
        "id": "apd63_post_funciones",
        "literal_pair_reserved_before_R03": false,
        "literal_pair_reserved_before_this_window": true,
        "modeled_price": 1,
        "numeric_result": 19,
        "procedure": "native",
        "raw_operands": [
          26,
          7
        ],
        "real_artifact_completed": true,
        "regime": 3,
        "route": -1,
        "word_command": -1,
        "word_matches_history": true
      },
      "first_scheduled_seconds": 3600,
      "first_transport_status": "completed",
      "later_physical_observations": 0,
      "pair": [
        26,
        7
      ],
      "scope": "First opportunity is never replaced by a later correct response. Physical first use, if transport previously rejected, is listed separately. These are finite literal operand pairs, not independent learners or distinct meanings."
    }
  ],
  "last_memory_observations": {
    "alfa": {
      "choice": -1,
      "context": "alfa",
      "expected_from_declared_history": -1,
      "id": "apd63_post_memorias",
      "matches_expected": true,
      "regime": 3,
      "request_mode": "memoria",
      "tick": 355305
    },
    "beta": {
      "choice": -1,
      "context": "beta",
      "expected_from_declared_history": -1,
      "id": "apd63_post_memorias",
      "matches_expected": true,
      "regime": 3,
      "request_mode": "memoria",
      "tick": 355372
    },
    "delta": {
      "choice": -1,
      "context": "delta",
      "expected_from_declared_history": -1,
      "id": "apd63_post_memorias",
      "matches_expected": true,
      "regime": 3,
      "request_mode": "memoria",
      "tick": 355506
    },
    "epsilon": {
      "choice": -1,
      "context": "epsilon",
      "expected_from_declared_history": -1,
      "id": "apd63_post_memorias",
      "matches_expected": true,
      "regime": 3,
      "request_mode": "memoria",
      "tick": 355573
    },
    "gamma": {
      "choice": 1,
      "context": "gamma",
      "expected_from_declared_history": 1,
      "id": "apd63_post_memorias",
      "matches_expected": true,
      "regime": 3,
      "request_mode": "memoria",
      "tick": 355439
    },
    "zeta": {
      "choice": 1,
      "context": "zeta",
      "expected_from_declared_history": 1,
      "id": "apd63_post_memorias",
      "matches_expected": true,
      "regime": 3,
      "request_mode": "memoria",
      "tick": 355640
    }
  },
  "native_count": {
    "archived_complete_execution_results": 3,
    "attempted": 3,
    "completed_transport": 3,
    "numeric_correct_given_actual_operator": 3,
    "partial_or_uncertain_transport_rows": 0,
    "queued_rows": 3,
    "scheduled": 3,
    "scheduled_transport_requests": 3,
    "scope": "New reserve situations only; scheduled_transport_requests/attempted/queued/completed count requests, which may contain several situations in the fixed final panel. Declared inherited actions remain separate. Complete results do not cover every possible partial execution. Numeric correctness, lexical history, artifacts and route usefulness stay separate."
  },
  "new_teaching": [
    {
      "admissions": {
        "by_status": {
          "applied": 3
        },
        "conflicting_receipt_ids": [],
        "requested_unique": 3
      },
      "after_tick": 336946,
      "before_tick": 336903,
      "context": "beta",
      "id": "apd63_00009",
      "mode": "memoria",
      "path": "$.rows[0].result.rows[0]",
      "signal": -1
    }
  ],
  "prior_teaching": [
    {
      "admissions": {
        "by_status": {
          "applied": 2
        },
        "conflicting_receipt_ids": [],
        "requested_unique": 2
      },
      "after_tick": 286629,
      "before_tick": 286563,
      "context": "total",
      "id": "apd62_00048",
      "mode": "apd-docencia",
      "path": "$.rows[0]",
      "signal": 1
    },
    {
      "admissions": {
        "by_status": {
          "applied": 3
        },
        "conflicting_receipt_ids": [],
        "requested_unique": 3
      },
      "after_tick": 286696,
      "before_tick": 286636,
      "context": "beta",
      "id": "apd62_00049",
      "mode": "memoria",
      "path": "$.rows[0].result.rows[0]",
      "signal": 1
    },
    {
      "admissions": {
        "by_status": {
          "applied": 2
        },
        "conflicting_receipt_ids": [],
        "requested_unique": 2
      },
      "after_tick": 287835,
      "before_tick": 287815,
      "context": "quita",
      "id": "apd62_00052",
      "mode": "apd-docencia",
      "path": "$.rows[0]",
      "signal": -1
    }
  ],
  "raw128": [
    {
      "choice": -1,
      "component_count": 128,
      "frozen_test_relation": -1,
      "id": "apd63_00004",
      "matches_expected": true,
      "native_read_tick": 330870,
      "nonzero": [
        {
          "index": 0,
          "value": 19
        }
      ],
      "regime": 1,
      "transport_status": "completed"
    },
    {
      "choice": 1,
      "component_count": 128,
      "frozen_test_relation": 1,
      "id": "apd63_00015",
      "matches_expected": true,
      "native_read_tick": 344233,
      "nonzero": [
        {
          "index": 0,
          "value": 19
        },
        {
          "index": 124,
          "value": 2
        }
      ],
      "regime": 3,
      "transport_status": "completed"
    }
  ]
}
```

Los últimos paneles son usos en la misma MAIN, no verificaciones sumadas desde clones. Ocurrieron antes del ocio final registrado: no garantizan acceso indefinido. Los bytes exactos y paneles completos, incluidos silencios, rechazos y errores, se conservan para recálculo.

## Atribución y reproducción

El operador instala anatomía, codec, calendario, oportunidades y docencia. DEE determina operadores y rutas físicas; el host no selecciona la respuesta útil. El cálculo externo es herramienta declarada, no aritmética aprendida. Seis formas corresponden a dos clases operativas, no seis conceptos ni español general. COUNT y composición tienen mecanismos preparados; el orden de composición es solicitado, no plan inventado. Coste modelado, exactitud numérica, historia lexical y compleción del artefacto no se sustituyen por un PASS global.
El perímetro son hooks Python y no un sandboxOS. Los diarios operativos bajo sistema/estado no estaban universalmente bloqueados; los descriptores antiguos no se reescriben. La revisión del código decisor y los contrastes físicos aportan evidencia diferente sobre ausencia de ayudas ocultas.
Recálculo archivado R04: 2786 observaciones RAW y 1203052 uint64 completos; discrepancias=0. PLAN_RECALCULO se ejecuta con Python estándar sin Runtime ni nuevo trabajador. Los snapshots, SQLite y outbox completos siguen locales y en el FullZIP; el análisis compacto no es su reemplazo.
