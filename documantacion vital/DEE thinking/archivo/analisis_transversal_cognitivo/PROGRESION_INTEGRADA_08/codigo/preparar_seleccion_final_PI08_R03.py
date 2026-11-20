"""Construye sólo configuración aditiva abierta; no ZIP, Native ni producto."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parents[1]


def main() -> None:
    source = P / "codigo/SELECCION_PAQUETE_PI08_PLANTILLA.json"
    addon_path = P / "fuentes/F1_IDENTITY_PORTABLE_R04/CONFIG_F1_NEGATIVO_PARA_PLAN.json"
    d = json.loads(source.read_text(encoding="utf-8-sig"))
    addon = json.loads(addon_path.read_text(encoding="utf-8-sig"))
    d["closed_plan"] = False
    d["instruction"] = (
        "Actual bounded selections A/B4/F1 identity failure/A_RP13/NONE17. OPEN: Root fills actual "
        "C bundle and completed final gates plus published1.36 hashes. Default constructor is "
        "read-only; no future files, results, ZIP or publication are asserted. Exact20 A sources "
        "remain in estados/RP_A01/sistema. A861426 remains MAIN; B is not adopted."
    )
    for group in d["primary_groups"]:
        if group["id"] == "B_technical_administrative_not_B_material":
            group.setdefault("exclude", []).append("PI08_B_NONE_AUTOPSIA_PANEL_R02_*.json")
    d["primary_groups"].append({
        "id": "B_NONE_actual_panel12_plus5administrative",
        "directory": "ensayos",
        "include": ["PI08_B_NONE_AUTOPSIA_PANEL_R02_*.json"],
        "minimum": 17,
        "instruction": "All seventeen actual material transport primaries: twelve scored witnesses, five administrative/state operations. No final C2C use in NONE. No Native replay by packaging.",
    })
    d["small_F1_snapshot_mode"] = addon["small_F1_snapshot_mode"]
    d["small_F1_snapshots"] = addon["small_F1_snapshots"]
    d["files"].extend(addon["files_to_append"])
    d["portable_verifications_additional"].extend(addon["portable_verifications_to_append"])
    explicit = [
        ("fuentes/F1_IDENTITY_AUDITORIA_ORGANIZACIONAL_R03.json", "04_EVIDENCIAS/F1_Q8/F1_IDENTITY_AUDITORIA_ORGANIZACIONAL_R03.json", "Decoded audit receipt and two diagnostic flags; no functional cut"),
        ("fuentes/F1_DOSIS_PARCIAL_NATIVE_RECALCULADA_R03.json", "04_EVIDENCIAS/F1_Q8/F1_DOSIS_PARCIAL_NATIVE_RECALCULADA_R03.json", "Actual seven applied Native requests before strict identity stop; runner aggregate was incomplete"),
        ("pares/PI08_B_NONE_POST18_T875451/EXPORTACION_SERVICIO.json", "04_EVIDENCIAS/LOCALIZADORES/EXPORTACION_B_NONE_POST18_T875451.json", "Original complete frozen pair locator/manifest; large operative files remain local"),
        ("control/A_PANEL12_PORTABLE_R01/MANIFIESTO_ESTABLE.json", "04_EVIDENCIAS/CONTROL/MANIFIESTO_ESTABLE_A_PANEL12_R01.json", "Actual independently preserved Native RP panel witness, not another replay"),
    ]
    # Un nombre de manifiesto puede variar; no se inventa ni se busca todo el árbol.
    for src, target, role in explicit:
        if not (P / src).is_file():
            if src.endswith("A_PANEL12_PORTABLE_R01/MANIFIESTO_ESTABLE.json"):
                root = P / "control/A_PANEL12_PORTABLE_R01"
                matches = [x for x in root.iterdir() if x.is_file() and "MANIFIESTO_ESTABLE" in x.name]
                if len(matches) != 1:
                    raise FileNotFoundError(src)
                src = matches[0].relative_to(P).as_posix()
            else:
                raise FileNotFoundError(src)
        d["files"].append({"source": src, "file": target, "role": role})
    d["final_documents"] = {"Manual": None, "Compendium": None}
    d["gates"] = {"scientific_closure": None, "operational_writer_scope": None,
                  "literal_document_publication": None}
    d["visual_QA_status"] = None
    d["C_bundle"] = None
    d["closure_inputs_to_fill_by_root"] = {
        "actual_C_bundle": "Set C_bundle.source to actual complete exported closed C bundle; prefix04_EVIDENCIAS/C; indexINDICE_C_PI08_R03.json. Include all startup negatives, attempts and immediate witnesses.",
        "final_documents": "Only actual literal published Manual1.36 and Compendium, exact hashes/bytes from publication proof",
        "gates": "Actual scientific closure, scoped absence of active writers, literal document publication; never all criteria true by assumption",
        "visual": "Actual attempted validation and limits; missing soffice is not visual approval",
        "ledger": "Actual closed Native subtotal78582 before C episodes; preparation3 already included. Final authoritative ledger may update, not guessed.",
        "public_current": "A861426 selected. B conservationfalse and NO_ADOPTION retained; no B/C/F1 memory merge.",
    }
    d["omissions"].append({
        "scope": "Q8_PARENT_AFTER_IDENTITY duplicate binary",
        "reason": "Exact encoded bytes and SHA equal Q8_PARENT_BEFORE; comparison proof included. Two distinct before/identity Native snapshots travel; no cut snapshot exists.",
    })
    out = P / "fuentes/SELECCION_FINAL_PI08_R03_ABIERTA.json"
    if out.exists():
        raise FileExistsError(out)
    out.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"file": str(out), "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
                      "closed_plan": False, "Native": 0, "ZIP_created": False,
                      "C_bundle": None}, ensure_ascii=False))


if __name__ == "__main__":
    main()
