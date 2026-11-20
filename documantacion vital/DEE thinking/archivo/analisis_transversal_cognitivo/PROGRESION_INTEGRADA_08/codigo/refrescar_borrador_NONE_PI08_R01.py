"""Actualización documental acotada de borradores; stdlib, cero Native/Word.

Conserva la versión previa exacta antes de añadir el control NONE ya cerrado.
No autoriza autoría, no publica documentos ni modifica el producto.
"""
from __future__ import annotations
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

P = Path(__file__).resolve().parents[1]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def preserve(p: Path) -> None:
    folder = p.parent / "revisiones"
    folder.mkdir(exist_ok=True)
    out = folder / (p.stem + "_ANTES_NONE_" + sha(p)[:12] + p.suffix)
    if out.exists():
        assert out.read_bytes() == p.read_bytes()
    else:
        out.write_bytes(p.read_bytes())


def write_json(p: Path, d: object) -> None:
    preserve(p)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_csv(p: Path, edit) -> None:
    with p.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        keys, rows = reader.fieldnames, list(reader)
    edit(rows)
    preserve(p)
    with p.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    proof = P / "control/PI08_B_NONE_AUTOPSIA_PANEL_R02.json"
    d = json.loads(proof.read_text(encoding="utf-8-sig"))
    assert sha(proof) == "7d815d25059e2bcf2e344ffa710a3314bade0eedffffd3d36953bf4535ee6ba3"
    assert d["closed"] and d["owner_closed"] and d["adopted_A_unchanged"]
    assert (d["initial_tick"], d["final_tick"], d["new_Native_ticks"]) == (875451, 878310, 2859)
    assert (d["panel_correct"], d["panel_witnesses"]) == (10, 12)
    assert d["Native_inputs"] == {"unique_requested": 947, "status_counts": {"applied": 947}}
    rows = {r["label"]: r for r in d["rows"]}
    assert rows["number13"]["observed"] == 7
    assert rows["number8"]["literal"]["izquierda"] == 7
    assert rows["number8"]["observed"] == 2
    functional = [r for r in d["rows"] if "correct" in r]
    assert len(functional) == 12 and sum(r["correct"] for r in functional) == 10
    comparison = {r["label"]: r for r in d["phase_and_dose_comparison"]}
    for r in functional:
        c = comparison[r["label"]]
        assert c["before_tick_equal"] and c["after_tick_equal"]
        assert c["current_Native_inputs"] == c["reference_Native_inputs"]
    evidence = {
        "proof": str(proof), "sha256": sha(proof),
        "source_T": 875451, "final_T": 878310, "new_Native_ticks": 2859,
        "correct": 10, "total": 12, "Native_requested": 947, "Native_applied": 947,
        "observed_SUM": 7, "actual_DIF_left_input": 7, "observed_DIF": 2,
        "same_before_after_ticks_and_dose_for_12_witnesses": True,
        "C2C_material_use": False, "C2C_resource_unchanged": True,
        "A_unchanged": True, "new_Native_by_documentary_update": 0,
    }
    paragraph = (
        "El control NONE también fue ensayado desde T875451. Terminó en T878310 tras 2.859 ticks, "
        "con diez de doce testigos y 947/947 entradas aplicadas. En las doce pruebas, las ventanas "
        "temporales y las dosis coincidieron con las del panel REAL. La suma produjo el mismo 7 y "
        "la diferencia recibió ese 7 real y produjo 2. NONE no ejecutó el trabajo C2C posterior y "
        "su recurso quedó intacto. El error no requiere los retornos adversos del brazo REAL en "
        "este contraste; no queda aislada una causa única de edad, fase o historia compartida."
    )
    facts_path = P / "documentos/HECHOS_1_36_BORRADOR.json"
    facts = json.loads(facts_path.read_text(encoding="utf-8-sig"))
    assert not facts["closed_for_authoring"]
    section = facts["manual_sections"][4]
    if paragraph not in section["paragraphs"]:
        section["paragraphs"].append(paragraph)
        section["sources"].append("control/PI08_B_NONE_AUTOPSIA_PANEL_R02.json; doce filas evaluadas y phase_and_dose_comparison")
    facts["B_NONE_native_panel_control"] = evidence
    facts["cut_utc"] = datetime.now(timezone.utc).isoformat()
    facts["document_description"] = (
        "PI08: A consolidado y adoptado en N67/T861426. B mostró revisión contextual y 14/18 "
        "condiciones conjuntas frente a 13/18 sin retorno adverso y 9/18 con retorno desacoplado; "
        "empató 14/18 con WSLS material. No se adoptó B por conservación 10/12. El control NONE "
        "también produjo 7 y después 2 en el panel; el panel RP desde A produjo 13 y después 8, "
        "con 12/12. F1 se detuvo antes del corte por auditoría de identidad. C material y cierre "
        "final siguen pendientes en este borrador."
    )
    facts["front"]["conservation_summary"] = (
        "A mantiene su corte principal T861426. Una copia completa de ese corte, abierta por el CLI "
        "de reproducibilidad, produjo doce de doce respuestas correctas y 947/947 entradas aplicadas, "
        "incluidas suma 6+7=13 y diferencia con ese 13 real menos 5=8. REAL y NONE obtuvieron 10/12 "
        "desde T875451: suma 7 y diferencia 2, con las mismas ventanas y dosis en los doce testigos. "
        "B no se adoptó. Este control impide atribuir el error exclusivamente a los retornos adversos; "
        "no aísla una causa única ni implica que se consultara materialmente al principal A."
    )
    facts["instruction"] = (
        "BORRADOR documental: A y su panel RP, B, el panel NONE y F1 tienen evidencia cerrada. "
        "C y el cierre final siguen pendientes. Root completa los resultados actuales y cierra "
        "antes de la autoría; este borrador no inicia autoría, no repite marcador ni escribe Word."
    )
    facts["scope"] = "DRAFT only. A principal unchanged; A RP12 and B/NONE panel actual; B/F1 closed. C episodes and final ledger/publication pending."
    facts["pending_sections"] = [
        "Resultado material C_R04 y su alcance: PENDING",
        "Cierre Native/recursos final, verificación del ZIP y publicación 1.36: PENDING",
    ]
    last = facts["manual_sections"][-1]
    last["paragraphs"][-1] = (
        "PENDING: incorporar el cierre real de C, el ledger Native y almacenamiento final, la "
        "verificación del ZIP y la publicación 1.36. El control NONE ya se ejecutó y conserva el "
        "resultado adverso descrito en 52.5. No se promete disponibilidad indefinida ni una "
        "explicación microcausal completa de la regresión. Antes de adoptar otra continuación, "
        "deben distinguirse acceso interferido y pérdida de contenido, y verificarse la conservación."
    )
    facts["compendium_sections"][0]["paragraphs"].append(paragraph)
    facts["compendium_sections"][0]["sources"].append("PROGRESION_INTEGRADA_08/control/PI08_B_NONE_AUTOPSIA_PANEL_R02.json")
    # Mejoras de espaciado sólo de prosa nueva; nunca se reescribe historia del Manual.
    substitutions = {"obtuvo14/18,16/18": "obtuvo 14/18, 16/18", "deREAL": "de REAL",
                     "enT879361": "en T879361", "y1.133": "y 1.133", "produjera15": "produjera 15",
                     "aesto": "a esto", "auna": "a una", "frente aWSLS": "frente a WSLS",
                     "física deIngenierías": "física de Ingenierías", "reutilizaPI01": "reutiliza PI01",
                     "específicas deIngenierías01/02": "específicas de Ingenierías 01/02",
                     "primariosPI08": "primarios PI08", "sonlectura": "son lectura",
                     "ejecucionesNative": "ejecuciones Native", "como principal los futuros": "como principal los futuros"}
    def tidy(x):
        if isinstance(x, str):
            for a, b in substitutions.items(): x = x.replace(a, b)
            return x
        if isinstance(x, list): return [tidy(v) for v in x]
        if isinstance(x, dict): return {k: tidy(v) for k, v in x.items()}
        return x
    write_json(facts_path, tidy(facts))
    continuity_path = P / "mapas/CONTINUIDAD_PI08_BORRADOR.json"
    continuity = json.loads(continuity_path.read_text(encoding="utf-8-sig"))
    continuity["B_NONE_control"] = evidence
    continuity["status"] = "DRAFT_A_PANEL_B_NONE_F1_CLOSED_C_PENDING"
    continuity["inspected_utc"] = datetime.now(timezone.utc).isoformat()
    continuity["known_closed_Native_ticks_subtotal"] = 78582
    continuity["subtotal_not_final_campaign_total"] = True
    continuity["pending_excluded"] = ["C_R04 episodes and final ledger; no assumed future Native"]
    write_json(continuity_path, continuity)

    def matrix_edit(rows):
        for row in rows:
            if row["familia"] == "Aritmética y transporte del dato real":
                row["PI08_ejecutado"] += "; NONE a misma edad inicial875451 produjo SUM7 y DIF2 en ventanas/dosis iguales"
                row["pendiente_al_borrador"] = "Microcausa no aislada; el error no requiere retornos adversos REAL en este contraste"
                row["fuente_localizador"] += "; control/PI08_B_NONE_AUTOPSIA_PANEL_R02.json"
            if row["familia"] == "Conservación y no adopción B":
                row["PI08_ejecutado"] += "; panel NONE10/12,947/947,2859ticks; sin C2C posterior"
                row["pendiente_al_borrador"] = "Causa única no aislada; retorno adverso REAL no necesario para observar mismo error"
                row["fuente_localizador"] += "; control/PI08_B_NONE_AUTOPSIA_PANEL_R02.json"
            if row["familia"] == "Comparación física y acceso FI":
                row["pendiente_al_borrador"] = "A RP panel12 actual PASS; C y cierre final pendientes"
    update_csv(P / "mapas/MATRIZ_ANTES_DESPUES_PI08_BORRADOR.csv", matrix_edit)

    def coverage_edit(rows):
        for row in rows:
            if row["familia_fuente"] == "Panelconservación B":
                row["limite"] = "Causa no aislada; A RP12 correcto y NONE10/12 con mismo7→2 ya ejecutados"
        rows.append({
            "familia_fuente": "Autopsia panel B NONE",
            "cobertura_real": "Proof cerrado y doce resultados con ventanas/dosis contrastados pasivamente",
            "material_leido": "17 filas de transporte,12testigos;947/947; SUM7→DIF2;2859ticks",
            "contenido_pertinente": "Mismo error que REAL sin retornos adversos; A protegido",
            "uso_en_PI08": "Acotar atribución causal del fallo de conservación",
            "limite": "No ensayo de edad sola ni causa única; NONE no ejecutó C2C posterior",
            "localizador": "control/PI08_B_NONE_AUTOPSIA_PANEL_R02.json",
        })
    update_csv(P / "mapas/COBERTURA_FUENTES_PI08_BORRADOR.csv", coverage_edit)
    print(json.dumps({"Native": 0, "DOCX_written": 0,
                      "updated": [{"file": str(p.relative_to(P)), "sha256": sha(p)} for p in (
                          facts_path, continuity_path,
                          P / "mapas/MATRIZ_ANTES_DESPUES_PI08_BORRADOR.csv",
                          P / "mapas/COBERTURA_FUENTES_PI08_BORRADOR.csv")]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
