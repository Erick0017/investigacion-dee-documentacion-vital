"""Post-hoc evidence annotation of TWO forms; never an operational decoder."""
from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common import put, sha


def main():
    path = ROOT / "NSM65_CATALOGO.json"
    original = json.loads(path.read_text(encoding="utf-8"))
    first_copy = ROOT / "fuentes/NSM/versiones/NSM65_CATALOGO_documental_pre_medicion.json"
    if original.get("catalogue_version") == "2026-10-17.2-measured-finite":
        correction_parent = ROOT / "fuentes/NSM/versiones/NSM65_CATALOGO_v2_antes_precision_emision.json"
        if correction_parent.exists(): raise FileExistsError(correction_parent)
        correction_parent.write_bytes(path.read_bytes())
        original = json.loads(first_copy.read_text(encoding="utf-8"))
    if original.get("catalogue_version") != "2026-10-17.1":
        raise ValueError("Evidence update expects the preserved documentary first cut")
    value = deepcopy(original)
    names = ("MAIN_MINUS", "FULL_PLUS", "RESERVED_TRANSLATION_PLUS", "RESERVED_TRANSLATION_MINUS_SWAPPED",
             "LEX_NAMES_SWAPPED", "LEX_REPORT_OMITTED", "LEX_SIGNAL_OMITTED", "LEX_UNPAIRED", "LEX_MEMORY_CUT", "LEX_SHAM")
    paths = {name: ROOT / "resultados/confirmacion" / name / "MEASUREMENTS.json" for name in names}
    evidence = {name: {"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p)} for name, p in paths.items()}
    records = {name: json.loads(p.read_text(encoding="utf-8"))["language"] for name, p in paths.items()}
    by_form = {name: {q["form_id"]: q for q in r["queries"]} for name, r in records.items()}
    for form in ("W1", "W2"):
        assert all(by_form[name][form]["available"] and by_form[name][form]["receipt"]["status"] == "applied"
                   for name in ("MAIN_MINUS", "FULL_PLUS", "RESERVED_TRANSLATION_PLUS", "LEX_SHAM"))
        assert by_form["MAIN_MINUS"][form]["resource_class"] != by_form["FULL_PLUS"][form]["resource_class"]
    assert not by_form["LEX_MEMORY_CUT"]["W1"]["available"] and by_form["LEX_MEMORY_CUT"]["W2"]["available"]
    for name in ("LEX_SIGNAL_OMITTED", "LEX_UNPAIRED"):
        assert all(q["receipt"]["status"] == "applied" and not q["available"] for q in records[name]["queries"])
    assert all(q["receipt"]["status"] == "rejected_occupied" for q in records["LEX_REPORT_OMITTED"]["queries"])
    inverse_file = ROOT / "resultados/inverse01/RESULTS_COMPLETED.json"
    inverse = json.loads(inverse_file.read_text(encoding="utf-8"))
    assert len(inverse["cases"]) == 5 and all(not x["symbols"] for x in inverse["cases"])
    original_copy = first_copy
    if not original_copy.exists():
        original_copy.parent.mkdir(parents=True, exist_ok=True)
        original_copy.write_bytes(path.read_bytes())
    m2_file = ROOT / "resultados/inverse_access2/RESULTS.json"
    m2 = json.loads(m2_file.read_text(encoding="utf-8"))
    m2_cases = {row["id"]: row for row in m2["cases"]}
    assert m2_cases["ORIGINAL_MAIN_NO_RESCUE"]["symbols"] == []
    assert m2_cases["ASSISTED_RESCUE_W1"]["symbols"] == ["HAY"]
    assert m2_cases["ASSISTED_RESCUE_THEN_MEMORY_CUT"]["symbols"] == []
    assert m2_cases["FRESH_RESERVED_TRANSLATION"]["symbols"] == ["HAY"]
    for entry in value["entries"]:
        if entry["id"] not in ("NSM65.THERE_IS", "NSM65.NOT"):
            continue
        form = "W1" if entry["id"] == "NSM65.THERE_IS" else "W2"
        dims = entry["dimensiones_independientes"]
        dims["interfaz_registrada"] = {"estado": "FORMA_FISICA_FIJA_PREDECLARADA_PRE_T0", "evidencia": ["src/channel.py", "configuraciones/EXPERIMENT_CONFIG.json"],
                                         "alcance": form + ": forma textual fija, port señal5/-x; no respuesta ni función guardada en el alias"}
        dims["fisica_realizable"] = {"estado": "SONDA_APLICADA_Y_EMISION_FISICA_OBSERVADA", "evidencia": [evidence[x] for x in ("MAIN_MINUS", "FULL_PLUS", "RESERVED_TRANSLATION_PLUS")],
                                     "alcance": "Dominio finito N67, señal5, emisión21 diagonal; no dominio universal de la palabra"}
        dims["asociacion_entrenada"] = {"estado": "ASOCIACION_FUNCIONAL_LIMITADA_OBSERVADA", "evidencia": [evidence[x] for x in ("MAIN_MINUS", "FULL_PLUS", "LEX_SIGNAL_OMITTED", "LEX_UNPAIRED", "LEX_MEMORY_CUT", "LEX_SHAM")],
                                        "alcance": "Misma señal y decoder con historias opuestas; teacher actual externo idéntico a ambas regiones; control sin señal/desacoplado sin emisión. Report omitido rechaza consultas: NO es control de olvido."}
        dims["retencion"] = {"estado": "RETENCION64_HASTA_SONDA_Y_EXPRESION67", "evidencia": [evidence["MAIN_MINUS"], evidence["FULL_PLUS"]],
                              "alcance": "Adquisición172/200; sonda física236/264 tras64ticks; emisión239/267 tras67ticks. No retención indefinida ni renovación después de la consulta."}
        reserve_ok = by_form["RESERVED_TRANSLATION_MINUS_SWAPPED"][form]["available"]
        dims["reservada"] = {"estado": "DOS_RESERVAS_CON_EMISION" if reserve_ok else "UNA_RESERVA_CON_EMISION_Y_OTRA_SIN_ACCESO", "evidencia": [evidence[x] for x in ("RESERVED_TRANSLATION_PLUS", "RESERVED_TRANSLATION_MINUS_SWAPPED")],
                              "alcance": "Traslaciones e historia/orden congelados; NO reparados al observarlos. En orden NO,HAY la segunda forma HAY no expresa21 pese admisión aplicada."}
        dims["emision"] = {"estado": "DIAGNOSTIC_RESCUED_SITUACION_A_SIMBOLO" if form == "W1" else "SITUACION_A_SIMBOLO_NO_OBSERVADA", "evidencia": [{"path": m2_file.relative_to(ROOT).as_posix(), "sha256": sha(m2_file)}],
                            "native_main": False, "external_class_sensor": True,
                            "alcance": "Emisión significa situación→símbolo, NO respuesta a palabra. MAIN original0símbolos. Método2: HAY sólo después de rescate ambiental diagnóstico y nuevo acceso transversal predeclarado; confirmado fresh y suprimido por corte de memoria. No emisión autónoma de MAIN ni semántica universal."}
        entry["respuesta_a_palabra"] = {"estado": "RESPUESTA_FISICA_21_DIRECCIONAL_MEDIDA", "evidencia": [evidence["MAIN_MINUS"], evidence["FULL_PLUS"]],
                                          "alcance": "Palabra→clase física, distinta de emisión situación→palabra; Native real sin tabla de respuestas"}
        dims["composicion"] = {"estado": "COMPOSICION_SEMANTICA_NO_DEMOSTRADA", "evidencia": [{"path": inverse_file.relative_to(ROOT).as_posix(), "sha256": sha(inverse_file)}],
                                "alcance": "La continuidad A→B→consecuencia→enseñanza externa→respuesta es física, pero no prueba sintaxis NSM. Emisión asistida de HAY no constituye composición de primitivas o bidireccionalidad autónoma en MAIN."}
        entry["full_NSM_semantics"] = False
        entry["native_domain_meaning"] = "Asociación adquirida con presencia/ausencia de un portador de recurso3 dentro de una ventana sensorial externa fija"
        entry["observed_forms_by_case"] = {name: {"available": queries[form]["available"], "class": queries[form]["resource_class"], "receipt": queries[form]["receipt"]["status"]} for name, queries in by_form.items()}
    value["catalogue_version"] = "2026-10-17.3-measured-finite-directional"
    value["evidence_updated_utc"] = datetime.now(timezone.utc).isoformat()
    value["documentary_parent_sha256"] = sha(original_copy)
    value["measured_scope_summary"] = {"catalogued_forms": 65, "forms_with_limited_physical_association": 2,
                                        "other_forms_only_documentary": 63, "general_NSM_meanings_acquired_claim": 0,
                                        "native_main_situation_to_symbol_forms": 0,
                                        "diagnostic_assisted_situation_to_symbol_forms": 1,
                                        "NSM_composition_demonstrated": 0,
                                        "full_NSM_semantics": False, "distinct_independent_experiments_claimed_by_catalogue": 0,
                                        "scope": "Evidence index over existing cases, not new Native executions or an operational response dictionary"}
    temporary = path.with_suffix(".new.json")
    put(temporary, value)
    os.replace(temporary, path)
    print(json.dumps({"catalogue_sha256": sha(path), "forms_with_limited_association": 2, "general_NSM_meanings_claimed": 0}))


if __name__ == "__main__": main()
