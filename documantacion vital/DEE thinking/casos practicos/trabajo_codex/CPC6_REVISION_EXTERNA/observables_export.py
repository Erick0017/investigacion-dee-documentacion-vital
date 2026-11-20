"""CPC6 external-review observables: literal, bounded publication whitelist.

Read-only adapter. It never decodes physical records, traverses geometry,
reconstructs responses from traces, or imports the DEE participant library.
Empty published decoder lists remain explicit per recorded time window.
"""
from typing import Any

ORIGINS = frozenset(("salida_decodificada_publicada", "medicion_instrumental_reportada"))
STATES = frozenset(("respuesta_publicada", "lista_publicada_vacia", "codigo_publicado",
                    "recuento_publicado", "igualdad_publicada", "valor_no_admitido", "no_publicado"))
RETENTION_CODES = frozenset(("INPUT_NOT_APPLIED", "NO_ACTIVE_RESPONSE_IN_FIXED_WINDOW",
                             "DIRECTIONAL_RESPONSE", "OTHER_PHYSICAL_RESPONSE"))
STAGES = {"selection": "SELECCION_VALIDAS", "information": "INFORMACION_VALIDAS", "late_read": "LECTURA_POSTERIOR_VALIDAS"}
UNITS = {"U1": "U1", "U2": "U2", "U3": "U3", "U4": "U4"}
CLASS_ALIAS = {-1: "CLASE_A", 1: "CLASE_B"}
BASE_VARIABLES = frozenset(("FORMA_01", "FORMA_02", "FORMA_01_REMOTA_ORIGINAL", "FORMA_01_REMOTA",
    "retencion_estado_publicado", "SELECCION_VALIDAS", "INFORMACION_VALIDAS", "LECTURA_POSTERIOR_VALIDAS",
    "comparacion_salida_control", "comparacion_control_canal_1", "comparacion_control_canal_2",
    "integridad_principal_reportada", "integridad_operativa_principal_reportada",
    "declaracion_inerte_reportada", "respuesta_publicada"))
VARIABLES = BASE_VARIABLES | frozenset(unit + "_" + stage for unit in UNITS.values() for stage in STAGES.values())


def _integer(value: Any) -> bool:
    return type(value) is int


def _time(value: Any, fallback: int | None = None) -> int | None:
    return value if _integer(value) else fallback


def _item(t: int | None, variable: str, state: str, answers: list, n: int, origin: str, definition: str) -> dict:
    if variable not in VARIABLES or state not in STATES or origin not in ORIGINS:
        raise ValueError("Observable outside the declared export vocabulary")
    if (t is not None and not _integer(t)) or not _integer(n) or n < 0:
        raise ValueError("Observable time/count must be exact integers")
    if any(type(x) not in (str, int, bool) for x in answers):
        raise ValueError("Only scalar published response values may leave the adapter")
    return {"t": t, "variable": variable, "estado": state, "respuestas": list(answers),
            "n": n, "origen": origin, "definicion": definition}


def _published_decoder(row: dict, field: str, value_field: str, variable: str, definition: str) -> list[dict]:
    if field not in row:
        return []
    t = _time(row.get("tick"))
    published = row[field]
    if not isinstance(published, list):
        return [_item(t, variable, "valor_no_admitido", [], 0, "salida_decodificada_publicada",
                      "El campo publicado no es una lista; no se sustituyó con una lectura física.")]
    if not published:
        return [_item(t, variable, "lista_publicada_vacia", [], 0, "salida_decodificada_publicada",
                      definition + " Lista vacía en esta ventana; no acredita por sí sola consulta, rechazo ni olvido.")]
    # Access ONLY the explicitly published scalar response field. In particular,
    # never read the adjacent physical/location/provenance/translation objects.
    values = [CLASS_ALIAS[x[value_field]] for x in published
              if isinstance(x, dict) and value_field in x and _integer(x[value_field]) and x[value_field] in CLASS_ALIAS]
    state = "respuesta_publicada" if len(values) == len(published) else "valor_no_admitido"
    return [_item(t, variable, state, values, len(values), "salida_decodificada_publicada",
                  definition + " CLASE_A y CLASE_B son alias convencionales propios de esta variable, no significados adicionales." if state == "respuesta_publicada" else
                  definition + " Alguna entrada carece del valor escalar permitido; no se reconstruyó.")]


def _summary_counts(summary: Any) -> list[dict]:
    if not isinstance(summary, dict):
        return []
    result = []

    def append_stages(value: dict, prefix: str = "") -> None:
        for source, target in STAGES.items():
            if source not in value:
                continue
            published = value[source]
            if isinstance(published, list):
                result.append(_item(None, prefix + target, "recuento_publicado", [], len(published),
                    "medicion_instrumental_reportada",
                    "Número de salidas válidas ya incluidas en el resumen de esta etapa; no se inspeccionó su contenido. t=null: resumen sin instante público fijado."))
            else:
                result.append(_item(None, prefix + target, "valor_no_admitido", [], 0,
                    "medicion_instrumental_reportada", "Resumen de etapa con formato no admitido; no se transformó en cero respuestas."))

    if any(k in summary for k in STAGES):
        append_stages(summary)
    else:
        for source, target in UNITS.items():
            if isinstance(summary.get(source), dict):
                append_stages(summary[source], target + "_")
    return result


def extract_observables(m: dict, entry: dict) -> list[dict]:
    """Return only {t,variable,estado,respuestas,n,origen,definicion}.

    t=None marks an aggregate/equality without an explicit safe published tick.
    Per-tick empty decoder arrays are retained, not turned into numerical zero.
    A case with no approved output decoder/status gets no_publicado even if
    it has instrument counts, equality results or parent-integrity booleans.
    Those instrument results are not semantic answers by the participant.
    """
    if not isinstance(m, dict) or not isinstance(entry, dict):
        raise TypeError("Measurement and registry entry must be mappings")
    result = []
    public_decoder_or_status = False
    case = m.get("case") if isinstance(m.get("case"), dict) else {}
    # Software decoder version is public provenance, not a physical condition.
    bus_variable = "FORMA_01_REMOTA" if case.get("word_bus_decoder") == 2 else "FORMA_01_REMOTA_ORIGINAL"
    recorded_rows = m.get("rows", [])
    if isinstance(recorded_rows, list):
        for row in recorded_rows:
            if not isinstance(row, dict):
                continue
            for field, value, variable, text in (
                ("decoded_language", "directional_relation", "FORMA_01", "Clase del decoder publicado para FORMA_01."),
                ("decoded_order_language", "history_direction", "FORMA_02", "Clase del decoder publicado para FORMA_02."),
                ("decoded_word_bus", "directional_relation", bus_variable,
                 "Clase ya publicada por el decoder de acceso posterior; V1 y V2 permanecen separados, sin reclasificación retrospectiva.")):
                values = _published_decoder(row, field, value, variable, text)
                if values:
                    result.extend(values)
                    public_decoder_or_status = True

    retention = m.get("retention_decode")
    if isinstance(retention, dict):
        code = retention.get("status")
        t = None  # No timestamp is asserted by this standalone decoder status.
        if type(code) is str and code in RETENTION_CODES:
            result.append(_item(t, "retencion_estado_publicado", "codigo_publicado", [code], 1,
                "salida_decodificada_publicada", "Código literal del decoder de retención; admisión fallida, ausencia de respuesta y otra respuesta siguen separados."))
            public_decoder_or_status = True
        else:
            result.append(_item(t, "retencion_estado_publicado", "no_publicado", [], 0,
                "salida_decodificada_publicada", "No existe un código de retención admitido en la publicación; no se adivinó."))

    summary_values = _summary_counts(m.get("summary"))
    if summary_values:
        result.extend(summary_values)
    # Component publications have these same three already-filtered lists,
    # rather than a summary object. Only their lengths are accessed.
    component_fields = {"selected_actions": "SELECCION_VALIDAS", "received_information": "INFORMACION_VALIDAS",
                        "late_information_queries": "LECTURA_POSTERIOR_VALIDAS"}
    for source, variable in component_fields.items():
        if source not in m:
            continue
        value = m[source]
        if isinstance(value, list):
            result.append(_item(None, variable, "recuento_publicado", [], len(value), "medicion_instrumental_reportada",
                "Recuento de salidas válidas ya filtradas en la publicación del componente; no se abrió ningún registro físico."))

    # Equality fields are themselves published instrument results. Do not
    # recompute equalities from arrays, records, snapshots, hashes or vectors.
    equal = m.get("response97_identical_to_parent")
    if type(equal) is bool:
        result.append(_item(None, "comparacion_salida_control", "igualdad_publicada", [equal], 1,
            "medicion_instrumental_reportada", "Igualdad de la salida con su referencia, ya reportada por el instrumento de control."))
    comparison = m.get("comparison162")
    if isinstance(comparison, dict):
        for source, variable in (("right", "comparacion_control_canal_1"), ("left", "comparacion_control_canal_2")):
            value = comparison.get(source)
            if isinstance(value, dict) and type(value.get("equal")) is bool:
                result.append(_item(162, variable, "igualdad_publicada", [value["equal"]], 1,
                    "medicion_instrumental_reportada", "Igualdad de salida ya reportada para este canal y ventana; no equivale a una respuesta semántica del participante."))

    integrity = (("MAIN_unchanged", "integridad_principal_reportada"),
                 ("parent_physical_unchanged", "integridad_principal_reportada"),
                 ("MAIN_operational_unchanged", "integridad_operativa_principal_reportada"),
                 ("parent_operative_unchanged", "integridad_operativa_principal_reportada"),
                 ("declaration_physical_identity_verified", "declaracion_inerte_reportada"))
    seen_integrity = set()
    for source, variable in integrity:
        value = m.get(source)
        if type(value) is bool and variable not in seen_integrity:
            seen_integrity.add(variable)
            result.append(_item(None, variable, "igualdad_publicada", [value], 1,
                "medicion_instrumental_reportada", "Comprobación de integridad ya reportada; no es conocimiento ni respuesta semántica del participante."))

    if not public_decoder_or_status:
        result.append(_item(None, "respuesta_publicada", "no_publicado", [], 0,
            "medicion_instrumental_reportada", "Este esquema no publica una salida decodificada ni un código de decoder admitido. Los recuentos o igualdades instrumentales, cuando existen, no se presentaron como respuestas semánticas."))
    return result
