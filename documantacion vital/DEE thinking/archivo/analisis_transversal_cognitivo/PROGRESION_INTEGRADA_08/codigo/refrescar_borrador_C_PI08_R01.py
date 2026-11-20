"""Añade sólo el resultado C real cerrado a hechos/mapas documentales PI08."""
from __future__ import annotations
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

P = Path(__file__).resolve().parents[1]


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def preserve(p):
    folder = p.parent / "revisiones"
    folder.mkdir(exist_ok=True)
    backup = folder / (p.stem + "_ANTES_C_" + sha(p)[:12] + p.suffix)
    if backup.exists(): assert backup.read_bytes() == p.read_bytes()
    else: backup.write_bytes(p.read_bytes())


def put(p, d):
    preserve(p)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def csv_edit(p, transform):
    with p.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        keys, rows = reader.fieldnames, list(reader)
    transform(rows)
    preserve(p)
    with p.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def main():
    proof = P / "control/PI08_C_EVALUAR_R04.json"
    d = json.loads(proof.read_text(encoding="utf-8-sig"))
    assert sha(proof) == "a6d19f5e2190e1877fab54b16b8c8857e27d92d56da6ca95de92ab1d43f4b6a8"
    assert d["closed"] and not d["error"] and d["no_adoption"]
    assert (d["initial_tick"], d["final_tick"], d["new_Native_ticks"]) == (875454, 884835, 9381)
    assert (d["opportunities_completed"], d["joint_useful"], d["questions_applied"], d["extra_bits_released"]) == (6, 5, 4, 4)
    assert d["Native_inputs"] == {"unique_requested": 1141, "status_counts": {"applied": 1141}}
    assert d["protected_before"] == d["protected_after"]
    rows = d["records"]
    assert [r["ordinal"] for r in rows] == list(range(6))
    assert [r["extra_bit_entered_second_TC"] for r in rows] == [0, 1, 0, 0, 1, 0]
    assert [r["first_stage"]["reader"]["choice"] for r in rows] == [0, 1, 1, 0, 1, 1]
    assert [r["second_stage"]["reader"]["choice"] for r in rows] == [-1, 1, 0, 0, 1, 0]
    assert sum(r["actual_failed"] for r in rows) == 1 and rows[0]["actual_failed"]
    assert sum(r["new_native_ticks"] for r in rows) == 9381
    assert sum(r["Native_inputs"]["applied"] for r in rows) == 1141
    assert all(r["no_first_trace_credit_claim"] for r in rows)
    evidence = {
        "proof": str(proof), "sha256": sha(proof), "life_id": d["life_id"],
        "source_B_T": 875451, "prepared_T": 875454, "final_T": 884835,
        "preparation_Native_ticks": 3, "preparation_Native_inputs": 1,
        "evaluation_Native_ticks": 9381, "evaluation_Native_requested": 1141,
        "evaluation_Native_applied": 1141, "completed": 6, "joint_useful": 5,
        "questions_scheduled": 4, "questions_applied": 4, "bits_released": 4,
        "actual_second_stage_bits": [0, 1, 0, 0, 1, 0],
        "Native_first_choices": [0, 1, 1, 0, 1, 1],
        "Native_second_choices": [-1, 1, 0, 0, 1, 0],
        "first_error_preserved": True, "first_trace_credit_isolated": False,
        "technical_register_explicit": True, "adopted_in_A": False,
        "A_protected_before_after_equal": True,
    }
    facts_path = P / "documentos/HECHOS_1_36_BORRADOR.json"
    facts = json.loads(facts_path.read_text(encoding="utf-8-sig"))
    assert facts["closed_for_authoring"] is False
    facts["C_actual"] = evidence
    facts["C_preparation_actual"]["status"] = "PREPARATION_AND_SIX_EXPERIENCES_ACTUALLY_CLOSED"
    facts["cut_utc"] = datetime.now(timezone.utc).isoformat()
    facts["document_description"] = (
        "PI08: A consolidado y adoptado en N67/T861426. B mostró revisión contextual: 14/18 frente "
        "a 13/18 sin retorno adverso, 9/18 desacoplado y 14/18 de WSLS material. No se adoptó B por "
        "conservación 10/12. NONE produjo el mismo 7→2 y el panel RP desde A produjo 13→8, con "
        "12/12. F1 se detuvo antes del corte por auditoría de identidad. C cerró seis oportunidades, "
        "cinco útiles, cuatro consultas admitidas y cuatro bits reales liberados mediante un "
        "registro técnico explícito; no se incorporó a A."
    )
    facts["front"]["edition_summary"] = (
        "Edición documental 1.36 — PI08. A consolidado y operativo. B mostró revisión contextual "
        "y no se incorporó por conservación insuficiente. El panel RP desde A pasó 12/12; NONE "
        "repitió el error 7→2. F1 se detuvo antes del corte; C produjo un flujo condicional "
        "material de dos etapas con cinco de seis resultados útiles."
    )
    replacements = facts["front"]["control_table_exact_text_replacements"]
    for key, value in list(replacements.items()):
        if "C: PENDING" in value:
            replacements[key] = value.replace("C: PENDING al preparar este borrador.", "C cerró seis oportunidades, cinco útiles y cuatro consultas admitidas; su estado no se incorporó al principal.")
        if "C requiere cierre real antes" in value:
            replacements[key] = value.replace("C requiere cierre real antes de autorizar la autoría.", "C cerró seis oportunidades en una copia diagnóstica; el principal A no avanzó por ese ensayo.")
    facts["manual_sections"][6] = {
        "heading": "C: consulta condicional y uso material de información adicional",
        "paragraphs": [
            "C se ejecutó desde una copia del futuro B congelado en T875451, nunca desde el "
            "principal A. El inicio R03 falló antes de READY con cero ticks Native por una "
            "restricción de identidad del transporte. La corrección posterior quedó limitada "
            "a la copia diagnóstica. La preparación R04 instaló un sumidero P0 con una entrada "
            "y tres ticks; las seis oportunidades posteriores añadieron 9.381 ticks hasta "
            "T884835, con 1.141/1.141 entradas aplicadas y ningún error de ejecución.",
            "Hubo cinco resultados conjuntos útiles de seis. La primera oportunidad tuvo una "
            "lectura previa STATE1, una selección Native cero válida que el contrato convirtió "
            "en no consultar, y una comparación posterior adversa. Cero material no fue NULL. "
            "En cuatro oportunidades siguientes se solicitó y admitió la consulta, su firma "
            "se verificó y se liberó un bit procedente del registro de la lectura física real. "
            "Las entradas a la segunda etapa fueron 0, 1, 0, 0, 1 y 0; dos ceros declarados "
            "sin consulta se distinguen de dos ceros obtenidos al consultar.",
            "Las consultas sobre una misma lectura STATE1 permitieron distinguir orientaciones "
            "físicas que el primer vocabulario no distinguía. En los casos consultados con bit1, "
            "la segunda selección produjo pulso y comparación útil; con bit0 no pulsó y dejó "
            "pasar mensajes reales de 64 bytes. En el caso de lectura previa STATE0 tampoco "
            "consultó, no pulsó y conservó el mensaje. Las selecciones Native de la segunda "
            "etapa fueron −1, +1, cero, cero, +1 y cero, conservando la traducción fija del cero.",
            "El registro temporal, el orden de dos etapas, las oportunidades y la traducción "
            "del bit son preparados por el anfitrión. El retorno se dirigió a la segunda "
            "traza; no se aisló aprendizaje del valor de la primera consulta ni una necesidad "
            "causal de la información mediante su ablación. Se demuestra un flujo condicional "
            "observado con selecciones Native y consecuencias reales, no una pregunta "
            "espontánea, un plan inventado o memoria Native del registro externo. C no se "
            "adoptó, y A permaneció en T861426.",
        ],
        "sources": [
            "control/PI08_C_PREPARAR_R03.json; control/FIX_C_IDENTIDAD_TRANSPORTE_APLICADO_PI08_R02.json; control/PI08_C_PREPARAR_R04.json",
            "control/PI08_C_EVALUAR_R04.json; ensayos/PI08_C_EVALUAR_R04_EP00.json a EP05.json; seis testigos inmediatos q1+8 conservados por índice C",
        ],
    }
    facts["manual_sections"][-1]["paragraphs"][-1] = (
        "El cierre de C y el control NONE ya están documentados. Quedan para el sellado "
        "el ledger Native y de almacenamiento final, la extracción y verificación del ZIP "
        "y la publicación real 1.36. No se promete disponibilidad indefinida ni una "
        "explicación microcausal completa de la regresión. La continuación debe distinguir "
        "acceso interferido y pérdida de contenido y comprobar la conservación antes de "
        "adoptar otra vida descendiente."
    )
    facts["manual_sections"][-1]["sources"] = [
        "control/DECISION_NO_ADOPCION_B_PI08_R01.json; control/PI08_C_EVALUAR_R04.json; mapas/CONTINUIDAD_PI08_BORRADOR.json; cierre final y publicación aún no afirmados por este borrador"
    ]
    facts["compendium_sections"][1]["heading"] = "F1, reproducción preservada y consulta C observada"
    facts["compendium_sections"][1]["paragraphs"][-1] = (
        "Las recetas A y B preservan conjuntos completos con requisitos CLI comprobados. El "
        "frontend RP ejecutó un panel desde A T861426 en copia: 12/12, 947/947 y 3.551 ticks "
        "hasta T864977; suma13 y diferencia8 correctas, sin avanzar el principal. La nueva "
        "repetición Native de la receta de adquisición B no se ejecutó. C cerró seis "
        "oportunidades de dos etapas, cinco útiles, con cuatro consultas admitidas que "
        "liberaron bits del registro técnico de observaciones reales. Conservó el error "
        "inicial y todos los datos: 1.141 entradas aplicadas en 9.381 ticks. El registro y "
        "la secuencia están preparados; no se aisló aprendizaje de la primera pregunta ni "
        "valor causal de la información. No se incorporó C al principal A."
    )
    facts["compendium_sections"][1]["sources"].append("PROGRESION_INTEGRADA_08/control/PI08_C_EVALUAR_R04.json")
    facts["instruction"] = (
        "BORRADOR: A/B/F1/C y paneles A/NONE tienen evidencia real cerrada. closed_for_authoring "
        "permanece false hasta que Root cierre la ciencia, revise ledger/recursos y autorice "
        "la autoría. No se repite marcador, no se escribe Word y no se modifica el producto."
    )
    facts["scope"] = "Actual closed science inputs. A remains principal; B no adoption; C diagnostic and F1 no-cut stop. Root final closure, publication and package witnesses still required."
    facts["pending_sections"] = ["Cierre científico autorizado por Root", "Ledger/almacenamiento y publicación1.36/extracción final reales"]
    put(facts_path, facts)
    cont_path = P / "mapas/CONTINUIDAD_PI08_BORRADOR.json"
    cont = json.loads(cont_path.read_text(encoding="utf-8-sig"))
    cont["status"] = "ACTUAL_SCIENCE_CLOSED_INPUTS_ROOT_FINAL_SEAL_PENDING"
    cont["C"] = evidence
    cont["known_closed_Native_ticks_subtotal"] = 87963
    cont["subtotal_not_final_campaign_total"] = True
    cont["pending_excluded"] = ["No assumed future Native; Root authoritative final ledger, writer scope and packaging witnesses pending"]
    cont["inspected_utc"] = datetime.now(timezone.utc).isoformat()
    put(cont_path, cont)

    def matrix(rows):
        for r in rows:
            if r["familia"] == "C consulta condicional":
                r.update({
                    "PI08_ejecutado": "R03 inicio0 Nativefallido; R04preparación3/1P0;6oportunidades9381ticks/1141Applied",
                    "resultado_positivo": "5/6conjuntas;4/4consultas+firmas+bits; bits0,1,0,0,1,0 y mensajes64B reales",
                    "adverso_y_limites": "Error inicial conservado; registro técnico/orden preparados; no crédito aislado primera consulta ni valor causal de información",
                    "vida_y_corte": "C diagnóstico875451→875454→884835; MAIN861426sin avance",
                    "modalidades_A_B_C_D_E": "A datos/recalc; B uso material dos etapas; C primera adquisición aislada no probada; D NO enA; E no recuperación",
                    "fuente_localizador": r["fuente_localizador"] + "; control/PI08_C_EVALUAR_R04.json",
                    "pendiente_al_borrador": "FENCE portable y sellado final; no más experimentos asumidos",
                })
            elif "Cierre final C/ledger" in r["pendiente_al_borrador"]:
                r["pendiente_al_borrador"] = "C real cerrado; ledger y sellado final pendientes"
    csv_edit(P / "mapas/MATRIZ_ANTES_DESPUES_PI08_BORRADOR.csv", matrix)

    def coverage(rows):
        for r in rows:
            if r["familia_fuente"] == "C_R03/R04":
                r.update({"cobertura_real": "Proof real de seis oportunidades cerrado; campos de etapas/registros/recibos inspeccionados",
                          "material_leido": "Inicio0Nativefix;P0 3ticks/1entrada;6filas1141/1141,9381ticks",
                          "contenido_pertinente": "5/6útiles;4consultas/firmas/bits; error0 y cero material frenteNULL conservados",
                          "limite": "Recálculo no es nueva ejecución ni demuestra crédito de la pregunta; C no incorporada aA",
                          "localizador": r["localizador"] + "; control/PI08_C_EVALUAR_R04.json"})
    csv_edit(P / "mapas/COBERTURA_FUENTES_PI08_BORRADOR.csv", coverage)
    print(json.dumps({"Native": 0, "DOCX_written": 0, "closed_for_authoring": False,
        "updated": [{"file": str(q.relative_to(P)), "sha256": sha(q)} for q in (
            facts_path, cont_path, P / "mapas/MATRIZ_ANTES_DESPUES_PI08_BORRADOR.csv",
            P / "mapas/COBERTURA_FUENTES_PI08_BORRADOR.csv")]}, ensure_ascii=False))


if __name__ == "__main__": main()
