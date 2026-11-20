# APD01: servicio continuo y alcance funcional

Una misma genealogía ASISTENTE_MAIN conserva el piloto y los futuros R01, R02 y R03. Son ventanas de una vida, no aprendices independientes. Ningún minuto de los dos ensayos interrumpidos cuenta hacia R03. El componente contiene recálculo archivado y primarios; no reemplaza los estados operativos emparejados.

## Negativos instrumentales conservados

R01: 1461.598571s observados con evolución habilitada, no60min. La medición pasiva del tamaño de un WAL sufrió una carrera de desaparición del archivo. Se cerró T188466 con siete filas genuinas todavía queued. No es un fallo cognitivo demostrado.
R02: 1793.500268s descontando también la pausa que no se reanudó, no60min. BEGIN seguía en FIFO cuando PAUSAR obtuvo prioridad técnica; el control congelado exigía una cascada ya formada y falló. STOP explícito preservó T257480 y ocho filas queued. Tres docencias se intentaron y ninguna se ejecutó; no se presentan como aprendizaje ni olvido.
R03 reduce prospectivamente la tasa a120oportunidades en4500s y ya no confunde transporte queued con preparación material. Primero consume los ocho IDs heredados una vez y, sólo si el BEGIN realmente forma un pendiente, ofrece un FINISH explícito único. El mismo ID nunca se reemite como una experiencia nueva. Las pausas concluyen reanudadas o se aborta explícitamente. No se cambian respuestas, lectores o precios según aciertos.

## Tiempo, recursos y corte real

Horizonte observado R03: 4500.157235s; descuento completo pausa/recarga: 88.861083s; tiempo habilitado conservador: 4411.296152400053s. Al menos60min de evolución de esta ventana, sumando sus dos propietarios separados por recarga: True. No acredita un único propietario continuo de60min. Tiempo habilitado no significa CPU ocupada sin interrupción ni estabilidad24/7.
Corte: ASISTENTE_MAIN T325311 N67, snapshot `estado/checkpoints/ASISTENTE_MAIN.T325311.326579c015a2.deetsnap.gz`, SHA-256 `9f4f990bbbd5cf5b0dd57cfbf904616f339f6bdd2563c589fb9ef3da5b214e61`. Propietario detenido=True; pendiente/incierto=False. Continuar requiere snapshot, SQLite, outbox, artefactos y protocolo emparejados. No hay promoción global del E1 protegido.
Cada propietario estuvo en un Job Windows propio con límite duro512MiB y OMP1. Los recursos reales de sus árboles de procesos se registran antes de cerrar cada Job; cualquier terminación forzada se informa, no acredita limpieza íntegra ni aprendizaje. Recursos/tiempo de CPU no son energía nativa de DEE.

Negativo operativo R03 preservado: clean_closure=False. Ambos recibos Job registraron active_processes=1 inmediatamente después de launcher.wait y antes de close_job (KILL_ON_JOB_CLOSE configurado). No se puede decidir retrospectivamente entre publicación tardía del contador y un hijo todavía vivo al cierre. La comprobación posterior de los cuatro PIDs propios, lock, SQLite y par exacto acredita durabilidad actual por separado; no transforma ese cierre histórico en limpio. La fixture posterior CPython-pass no resuelve su causa histórica.

## Denominadores R03

```json
{
  "all_literal_attempts_excluding_valid_technical_controls": 140,
  "burst_attempts": 14,
  "deliberately_invalid_attempts": 4,
  "material_literal_attempts_including_deliberately_invalid": 139,
  "nominal_attempts": 120,
  "queued": 131,
  "rejected_queue_capacity": 6,
  "rejected_transport_validation": 3,
  "reserved_pending_token_attempts": 1,
  "valid_technical_control_attempts": 17
}
```

Las ejecuciones de los ocho pendientes heredados y el FINISH declarado aparecen separadas de los120nominales. El diario original de admisión conserva también rechazos por capacidad sin fila SQLite. El contador total heredado del dueño no se presenta como cantidad nueva de esta reserva.

| Dimensión | Resultado nuevo R03 |
|---|---|
| Entradas nativas de la ventana, incluidas continuaciones heredadas | 15406/15406 aplicadas; 0 rechazadas |
| Usos de memoria/historia documentada, incluyendo usos dentro de trabajo | 40/40 |
| Pasos APD nuevos, incluidos intermediarios de composición | 61 |
| Palabra emitida coincide con historia docente admitida | 61/61 |
| Número correcto dado el operador realmente emitido | 61/61 |
| Artefactos materiales completados | 61/61 |
| Artefactos completados dentro del presupuesto modelado2 | 42/61 |
| Rutas físicas −/0/+/sin respuesta | {"-1": 61, "0": 0, "1": 0, "None": 0} |
| Conteo preparado: numéricos correctos / nominales | 9/9 |
| Composiciones asistidas completas / nominales | 10/10 |
| Crudos128 coincide con relación fija / nominales | 5/5 |
| Pares nuevos utilizados: numéricos correctos condicionados / usos observados | 23/23 |

Una palabra correcta por historia, un número correcto condicionado a la operación física, un archivo completado y un coste bajo son cuatro hechos distintos. No se sustituyen por un veredicto global. Las ocho parejas nuevas se eligieron por enumeración literal antes de ejecutar, excluyendo P01–P26 y todos los casos planificados de R01/R02; RESERVA_PARES_NUEVOS conserva algoritmo, conjuntos e índiceSHA. Las composiciones públicas repetidas no son nuevas reservas.

## Docencia, regímenes y retención

```json
[
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
]
```

Las horas1900/1910/2000 no demuestran enseñanza por sí solas. PANELES_Y_FUNCIONES contrasta recibos docentes, emisiones posteriores e historia realmente admitida para total/quita y beta. Seis formas españolas invocan dos clases de operador preparadas; no son seis conceptos nuevos ni un repertorioNSM65.

| Régimen | Nominales | Transporte real | Memoria/historia | Palabra/historia | Número/operador |
|---|---:|---|---:|---:|---:|
| 1 | 31 | {"completed": 31} | 9/9 | 17/17 | 17/17 |
| 2 | 39 | {"completed": 39} | 11/11 | 19/19 | 19/19 |
| 3 | 50 | {"completed": 50} | 15/15 | 25/25 | 25/25 |

## Primera oportunidad de las ocho parejas

Todas tienen primer operando17: cobertura deliberadamente estrecha. La primera solicitud se conserva aunque sea rechazada o no emita respuesta. La primera observación física posterior, si la primera no se admitió, se lista aparte y nunca sustituye ese negativo. Las repeticiones posteriores no son nuevas reservas independientes.

```json
[
  {
    "first_physical_observation_if_any": {
      "abstention": false,
      "after_tick": 279178,
      "audit_issues": [],
      "before_tick": 278651,
      "completed_within_prepared_modeled_budget2": false,
      "composition_stage": null,
      "correct_given_actual_operator": true,
      "expected_from_explicit_history": 1,
      "form": "suma",
      "id": "apd62_00031",
      "literal_pair_reserved_before_R03": true,
      "literal_pair_reserved_before_this_window": true,
      "modeled_price": 5,
      "numeric_result": 18,
      "procedure": "native",
      "raw_operands": [
        17,
        1
      ],
      "real_artifact_completed": true,
      "regime": 2,
      "route": -1,
      "word_command": 1,
      "word_matches_history": true
    },
    "first_scheduled_form": "suma",
    "first_scheduled_id": "apd62_00031",
    "first_scheduled_native_result": {
      "abstention": false,
      "after_tick": 279178,
      "audit_issues": [],
      "before_tick": 278651,
      "completed_within_prepared_modeled_budget2": false,
      "composition_stage": null,
      "correct_given_actual_operator": true,
      "expected_from_explicit_history": 1,
      "form": "suma",
      "id": "apd62_00031",
      "literal_pair_reserved_before_R03": true,
      "literal_pair_reserved_before_this_window": true,
      "modeled_price": 5,
      "numeric_result": 18,
      "procedure": "native",
      "raw_operands": [
        17,
        1
      ],
      "real_artifact_completed": true,
      "regime": 2,
      "route": -1,
      "word_command": 1,
      "word_matches_history": true
    },
    "first_scheduled_seconds": 1323.0,
    "first_transport_status": "completed",
    "later_physical_observations": 2,
    "pair": [
      17,
      1
    ],
    "scope": "First opportunity is never replaced by a later correct response. Physical first use, if transport previously rejected, is listed separately. These are finite literal operand pairs, not independent learners or distinct meanings."
  },
  {
    "first_physical_observation_if_any": {
      "abstention": false,
      "after_tick": 279960,
      "audit_issues": [],
      "before_tick": 279553,
      "completed_within_prepared_modeled_budget2": false,
      "composition_stage": null,
      "correct_given_actual_operator": true,
      "expected_from_explicit_history": -1,
      "form": "diferencia",
      "id": "apd62_00033",
      "literal_pair_reserved_before_R03": true,
      "literal_pair_reserved_before_this_window": true,
      "modeled_price": 5,
      "numeric_result": 15,
      "procedure": "native",
      "raw_operands": [
        17,
        2
      ],
      "real_artifact_completed": true,
      "regime": 2,
      "route": -1,
      "word_command": -1,
      "word_matches_history": true
    },
    "first_scheduled_form": "diferencia",
    "first_scheduled_id": "apd62_00033",
    "first_scheduled_native_result": {
      "abstention": false,
      "after_tick": 279960,
      "audit_issues": [],
      "before_tick": 279553,
      "completed_within_prepared_modeled_budget2": false,
      "composition_stage": null,
      "correct_given_actual_operator": true,
      "expected_from_explicit_history": -1,
      "form": "diferencia",
      "id": "apd62_00033",
      "literal_pair_reserved_before_R03": true,
      "literal_pair_reserved_before_this_window": true,
      "modeled_price": 5,
      "numeric_result": 15,
      "procedure": "native",
      "raw_operands": [
        17,
        2
      ],
      "real_artifact_completed": true,
      "regime": 2,
      "route": -1,
      "word_command": -1,
      "word_matches_history": true
    },
    "first_scheduled_seconds": 1389.0,
    "first_transport_status": "completed",
    "later_physical_observations": 2,
    "pair": [
      17,
      2
    ],
    "scope": "First opportunity is never replaced by a later correct response. Physical first use, if transport previously rejected, is listed separately. These are finite literal operand pairs, not independent learners or distinct meanings."
  },
  {
    "first_physical_observation_if_any": {
      "abstention": false,
      "after_tick": 281524,
      "audit_issues": [],
      "before_tick": 280707,
      "completed_within_prepared_modeled_budget2": false,
      "composition_stage": null,
      "correct_given_actual_operator": true,
      "expected_from_explicit_history": 1,
      "form": "agrega",
      "id": "apd62_00037",
      "literal_pair_reserved_before_R03": true,
      "literal_pair_reserved_before_this_window": true,
      "modeled_price": 5,
      "numeric_result": 20,
      "procedure": "native",
      "raw_operands": [
        17,
        3
      ],
      "real_artifact_completed": true,
      "regime": 2,
      "route": -1,
      "word_command": 1,
      "word_matches_history": true
    },
    "first_scheduled_form": "agrega",
    "first_scheduled_id": "apd62_00037",
    "first_scheduled_native_result": {
      "abstention": false,
      "after_tick": 281524,
      "audit_issues": [],
      "before_tick": 280707,
      "completed_within_prepared_modeled_budget2": false,
      "composition_stage": null,
      "correct_given_actual_operator": true,
      "expected_from_explicit_history": 1,
      "form": "agrega",
      "id": "apd62_00037",
      "literal_pair_reserved_before_R03": true,
      "literal_pair_reserved_before_this_window": true,
      "modeled_price": 5,
      "numeric_result": 20,
      "procedure": "native",
      "raw_operands": [
        17,
        3
      ],
      "real_artifact_completed": true,
      "regime": 2,
      "route": -1,
      "word_command": 1,
      "word_matches_history": true
    },
    "first_scheduled_seconds": 1521.0,
    "first_transport_status": "completed",
    "later_physical_observations": 2,
    "pair": [
      17,
      3
    ],
    "scope": "First opportunity is never replaced by a later correct response. Physical first use, if transport previously rejected, is listed separately. These are finite literal operand pairs, not independent learners or distinct meanings."
  },
  {
    "first_physical_observation_if_any": {
      "abstention": false,
      "after_tick": 282306,
      "audit_issues": [],
      "before_tick": 281854,
      "completed_within_prepared_modeled_budget2": false,
      "composition_stage": null,
      "correct_given_actual_operator": true,
      "expected_from_explicit_history": -1,
      "form": "resta",
      "id": "apd62_00039",
      "literal_pair_reserved_before_R03": true,
      "literal_pair_reserved_before_this_window": true,
      "modeled_price": 5,
      "numeric_result": 13,
      "procedure": "native",
      "raw_operands": [
        17,
        4
      ],
      "real_artifact_completed": true,
      "regime": 2,
      "route": -1,
      "word_command": -1,
      "word_matches_history": true
    },
    "first_scheduled_form": "resta",
    "first_scheduled_id": "apd62_00039",
    "first_scheduled_native_result": {
      "abstention": false,
      "after_tick": 282306,
      "audit_issues": [],
      "before_tick": 281854,
      "completed_within_prepared_modeled_budget2": false,
      "composition_stage": null,
      "correct_given_actual_operator": true,
      "expected_from_explicit_history": -1,
      "form": "resta",
      "id": "apd62_00039",
      "literal_pair_reserved_before_R03": true,
      "literal_pair_reserved_before_this_window": true,
      "modeled_price": 5,
      "numeric_result": 13,
      "procedure": "native",
      "raw_operands": [
        17,
        4
      ],
      "real_artifact_completed": true,
      "regime": 2,
      "route": -1,
      "word_command": -1,
      "word_matches_history": true
    },
    "first_scheduled_seconds": 1587.0,
    "first_transport_status": "completed",
    "later_physical_observations": 2,
    "pair": [
      17,
      4
    ],
    "scope": "First opportunity is never replaced by a later correct response. Physical first use, if transport previously rejected, is listed separately. These are finite literal operand pairs, not independent learners or distinct meanings."
  },
  {
    "first_physical_observation_if_any": {
      "abstention": false,
      "after_tick": 285434,
      "audit_issues": [],
      "before_tick": 284869,
      "completed_within_prepared_modeled_budget2": false,
      "composition_stage": null,
      "correct_given_actual_operator": true,
      "expected_from_explicit_history": 1,
      "form": "suma",
      "id": "apd62_00043",
      "literal_pair_reserved_before_R03": true,
      "literal_pair_reserved_before_this_window": true,
      "modeled_price": 5,
      "numeric_result": 22,
      "procedure": "native",
      "raw_operands": [
        17,
        5
      ],
      "real_artifact_completed": true,
      "regime": 2,
      "route": -1,
      "word_command": 1,
      "word_matches_history": true
    },
    "first_scheduled_form": "suma",
    "first_scheduled_id": "apd62_00043",
    "first_scheduled_native_result": {
      "abstention": false,
      "after_tick": 285434,
      "audit_issues": [],
      "before_tick": 284869,
      "completed_within_prepared_modeled_budget2": false,
      "composition_stage": null,
      "correct_given_actual_operator": true,
      "expected_from_explicit_history": 1,
      "form": "suma",
      "id": "apd62_00043",
      "literal_pair_reserved_before_R03": true,
      "literal_pair_reserved_before_this_window": true,
      "modeled_price": 5,
      "numeric_result": 22,
      "procedure": "native",
      "raw_operands": [
        17,
        5
      ],
      "real_artifact_completed": true,
      "regime": 2,
      "route": -1,
      "word_command": 1,
      "word_matches_history": true
    },
    "first_scheduled_seconds": 1719.0,
    "first_transport_status": "completed",
    "later_physical_observations": 2,
    "pair": [
      17,
      5
    ],
    "scope": "First opportunity is never replaced by a later correct response. Physical first use, if transport previously rejected, is listed separately. These are finite literal operand pairs, not independent learners or distinct meanings."
  },
  {
    "first_physical_observation_if_any": {
      "abstention": false,
      "after_tick": 286216,
      "audit_issues": [],
      "before_tick": 285771,
      "completed_within_prepared_modeled_budget2": false,
      "composition_stage": null,
      "correct_given_actual_operator": true,
      "expected_from_explicit_history": -1,
      "form": "diferencia",
      "id": "apd62_00045",
      "literal_pair_reserved_before_R03": true,
      "literal_pair_reserved_before_this_window": true,
      "modeled_price": 5,
      "numeric_result": 10,
      "procedure": "native",
      "raw_operands": [
        17,
        7
      ],
      "real_artifact_completed": true,
      "regime": 2,
      "route": -1,
      "word_command": -1,
      "word_matches_history": true
    },
    "first_scheduled_form": "diferencia",
    "first_scheduled_id": "apd62_00045",
    "first_scheduled_native_result": {
      "abstention": false,
      "after_tick": 286216,
      "audit_issues": [],
      "before_tick": 285771,
      "completed_within_prepared_modeled_budget2": false,
      "composition_stage": null,
      "correct_given_actual_operator": true,
      "expected_from_explicit_history": -1,
      "form": "diferencia",
      "id": "apd62_00045",
      "literal_pair_reserved_before_R03": true,
      "literal_pair_reserved_before_this_window": true,
      "modeled_price": 5,
      "numeric_result": 10,
      "procedure": "native",
      "raw_operands": [
        17,
        7
      ],
      "real_artifact_completed": true,
      "regime": 2,
      "route": -1,
      "word_command": -1,
      "word_matches_history": true
    },
    "first_scheduled_seconds": 1785.0,
    "first_transport_status": "completed",
    "later_physical_observations": 2,
    "pair": [
      17,
      7
    ],
    "scope": "First opportunity is never replaced by a later correct response. Physical first use, if transport previously rejected, is listed separately. These are finite literal operand pairs, not independent learners or distinct meanings."
  },
  {
    "first_physical_observation_if_any": {
      "abstention": false,
      "after_tick": 303420,
      "audit_issues": [],
      "before_tick": 302910,
      "completed_within_prepared_modeled_budget2": true,
      "composition_stage": null,
      "correct_given_actual_operator": true,
      "expected_from_explicit_history": 1,
      "form": "agrega",
      "id": "apd62_00079",
      "literal_pair_reserved_before_R03": true,
      "literal_pair_reserved_before_this_window": true,
      "modeled_price": 1,
      "numeric_result": 25,
      "procedure": "native",
      "raw_operands": [
        17,
        8
      ],
      "real_artifact_completed": true,
      "regime": 3,
      "route": -1,
      "word_command": 1,
      "word_matches_history": true
    },
    "first_scheduled_form": "agrega",
    "first_scheduled_id": "apd62_00079",
    "first_scheduled_native_result": {
      "abstention": false,
      "after_tick": 303420,
      "audit_issues": [],
      "before_tick": 302910,
      "completed_within_prepared_modeled_budget2": true,
      "composition_stage": null,
      "correct_given_actual_operator": true,
      "expected_from_explicit_history": 1,
      "form": "agrega",
      "id": "apd62_00079",
      "literal_pair_reserved_before_R03": true,
      "literal_pair_reserved_before_this_window": true,
      "modeled_price": 1,
      "numeric_result": 25,
      "procedure": "native",
      "raw_operands": [
        17,
        8
      ],
      "real_artifact_completed": true,
      "regime": 3,
      "route": -1,
      "word_command": 1,
      "word_matches_history": true
    },
    "first_scheduled_seconds": 2907.0,
    "first_transport_status": "completed",
    "later_physical_observations": 1,
    "pair": [
      17,
      8
    ],
    "scope": "First opportunity is never replaced by a later correct response. Physical first use, if transport previously rejected, is listed separately. These are finite literal operand pairs, not independent learners or distinct meanings."
  },
  {
    "first_physical_observation_if_any": {
      "abstention": false,
      "after_tick": 287780,
      "audit_issues": [],
      "before_tick": 287112,
      "completed_within_prepared_modeled_budget2": false,
      "composition_stage": null,
      "correct_given_actual_operator": true,
      "expected_from_explicit_history": -1,
      "form": "resta",
      "id": "apd62_00051",
      "literal_pair_reserved_before_R03": true,
      "literal_pair_reserved_before_this_window": true,
      "modeled_price": 5,
      "numeric_result": 8,
      "procedure": "native",
      "raw_operands": [
        17,
        9
      ],
      "real_artifact_completed": true,
      "regime": 2,
      "route": -1,
      "word_command": -1,
      "word_matches_history": true
    },
    "first_scheduled_form": "resta",
    "first_scheduled_id": "apd62_00051",
    "first_scheduled_native_result": {
      "abstention": false,
      "after_tick": 287780,
      "audit_issues": [],
      "before_tick": 287112,
      "completed_within_prepared_modeled_budget2": false,
      "composition_stage": null,
      "correct_given_actual_operator": true,
      "expected_from_explicit_history": -1,
      "form": "resta",
      "id": "apd62_00051",
      "literal_pair_reserved_before_R03": true,
      "literal_pair_reserved_before_this_window": true,
      "modeled_price": 5,
      "numeric_result": 8,
      "procedure": "native",
      "raw_operands": [
        17,
        9
      ],
      "real_artifact_completed": true,
      "regime": 2,
      "route": -1,
      "word_command": -1,
      "word_matches_history": true
    },
    "first_scheduled_seconds": 1983.0,
    "first_transport_status": "completed",
    "later_physical_observations": 2,
    "pair": [
      17,
      9
    ],
    "scope": "First opportunity is never replaced by a later correct response. Physical first use, if transport previously rejected, is listed separately. These are finite literal operand pairs, not independent learners or distinct meanings."
  }
]
```

El último panel observado precede al ocio posterior; sólo una consulta nueva en una copia puede acreditar accesibilidad después. No se suman recuerdos de controles ni futuros incompatibles.

## Atribución y reproducibilidad

Aparato, canales, lectores comunes, aritmética espacial, conteo, calendarioP0, actuador y reglas ambientales son preparados. Las asociaciones y transformaciones nativas se leen de RAW. El calculador externo es una herramienta explícita sólo cuando la salida DEE la invoca; no se ejecutan ambas rutas para elegir un acierto. La composición sigue el orden solicitado por el operador y transporta el intermedio realmente producido; no es planificación aprendida. Esta hora sola no demuestra una política general ni R2.

Los descriptores históricos de audit-hook que afirmaban bloqueo universal de diarios se conservan como fueron emitidos. Antes de R03 se corrigieron sólo esas descripciones, con AST que acredita algoritmos/permisos idénticos. S/estado seguía siendo legible para continuidad. No es un sandboxOS; la revisión del decisor y los controles físicos son evidencia separada sobre ausencia de ayuda decisional.

El mapa de fuentes de R03 monitorizó26 archivos declarados, no todo el sistema: omitió asistente_proposito_01.py. Sus bytes exactos de13866B, SHA fb93ee43d34ea88fb053f0b6a4e996d9aaf63981ec6edf76607c7271f1c4f86d, están preservados y vinculados a P26 en el componente científico anterior. Esto no reconstruye una monitorización continua retroactiva. R04 añade explícitamente ese actor a su mapa27 antes de ejecutar.

El recálculo R03 comprueba 10708 observacionesRAW serializadas, 1203052 uint64 de campos completos y bytes reales de artefactos; discrepancias=0. Las observaciones repetidas no son individuos independientes. PLAN_RECALCULO usa sólo Python estándar sin Runtime, nuevo cálculo del trabajador ni nuevas experiencias.
Los estados completos, SQLite, outbox y telemetría profunda permanecen locales y en el paquete operativo. El análisis exporta cada fila propia y heredada declarada con todos sus campos, registros de admisión íntegros y proyección completaRAW/clocks. La igualdad de filas de JSON proyectado no es identidad binaria del gzip original. Manifiestos e INDICE_OMISIONES dan sus localizadores y hashes.
