"""Surgical Word 1.8 -> 1.9 edit. Execute only after CF01 results are fixed."""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from zipfile import ZipFile
from lxml import etree as E

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
DC = "{http://purl.org/dc/elements/1.1/}"
DCT = "{http://purl.org/dc/terms/}"
BASE_SHA = "1f37b20a860b50835b87bbfcf8bc783f23e31c37db7d230bf4bb350e9106504a"
ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_8_MI02_SIN_VALIDACION_VISUAL.docx"
OUT = ROOT / "DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_9_CF01_SIN_VALIDACION_VISUAL.docx"

def text(p): return "".join(n.text or "" for n in p.iter(W + "t"))

def set_text(p, content):
    original_run = p.find(W + "r")
    run_props = deepcopy(original_run.find(W + "rPr")) if original_run is not None and original_run.find(W + "rPr") is not None else None
    if list(p.iter(W + "instrText")): raise ValueError("Do not replace a paragraph containing fields")
    for child in list(p):
        if child.tag != W + "pPr": p.remove(child)
    r = E.SubElement(p, W + "r")
    if run_props is not None: r.append(run_props)
    for i, line in enumerate(content.split("\n")):
        if i: E.SubElement(r, W + "br")
        t = E.SubElement(r, W + "t")
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        t.text = line

def paragraph(style, content):
    if style != "Code":
        # Restore ordinary prose spacing from compact research messages without
        # altering life IDs, protocol names, shell flags or hexadecimal hashes.
        for old, new in (
            ("Cognitive1.1", "Cognitive 1.1"), ("thinking4.5", "thinking 4.5"),
            ("Universev27", "Universe v27"), ("permanece4.5", "permanece 4.5"),
            ("es1.9", "es 1.9"), ("B61/19", "B 61/19"),
            ("propios116/113", "propios 116/113"), ("conserva165/162", "conserva 165/162"),
            ("contexto0/5", "contexto 0/5"), ("contexto7/5", "contexto 7/5"),
            ("fueron24trabajos", "fueron 24 trabajos"), ("en33actuaciones", "en 33 actuaciones"),
            ("completó3de24trabajos", "completó 3 de 24 trabajos"), ("en36intentos", "en 36 intentos"),
            ("produjo0de24trabajos", "produjo 0 de 24 trabajos"), ("conservó36salidas", "conservó 36 salidas"),
            ("y34contactos", "y 34 contactos"), ("de2a3", "de 2 a 3"), ("mantuvo2al", "mantuvo 2 al"),
            ("nueva52entró", "nueva 52 entró"), ("referencias61/19ni", "referencias 61/19 ni"),
            ("carga2y", "carga 2 y"), ("fijo5y", "fijo 5 y"), ("izquierda7en", "izquierda 7 en"),
            ("anterior5y", "anterior 5 y"), ("propios116/113permanecieron", "propios 116/113 permanecieron"),
            ("desacoplada36no", "desacoplada 36 no"), ("dieron1de4usos", "dieron 1 de 4 usos"),
            ("obtuvieron18de18usos", "obtuvieron 18 de 18 usos"), ("produjo16de18con", "produjo 16 de 18 con"),
            ("produjo0de18usos", "produjo 0 de 18 usos"), ("a18salidas", "a 18 salidas"),
            ("obtuvo1de9", "obtuvo 1 de 9"), ("mediciones0/7y", "mediciones 0/7 y"),
            ("propia3a2mediante", "propia 3 a 2 mediante"), ("conservó3", "conservó 3"),
            ("nuevo18/25falló", "nuevo 18/25 falló"), ("diferencia3", "diferencia 3"),
            ("siguiente19/26fue", "siguiente 19/26 fue"), ("T63813preserva", "T63813 preserva"),
            ("de7a8", "de 7 a 8"), ("valor8como", "valor 8 como"),
            ("18/26,19/27,7/16,8/15y13/21", "18/26, 19/27, 7/16, 8/15 y 13/21"),
            ("logró4de5usos", "logró 4 de 5 usos"), ("logró2de5", "logró 2 de 5"),
            ("de165/162a167/163y", "de 165/162 a 167/163 y"), ("de3a4", "de 3 a 4"),
            ("nueva19/27produjo", "nueva 19/27 produjo"), ("diferencia3y", "diferencia 3 y"),
            ("separación8", "separación 8"), ("Windowsx64", "Windows x64"),
            ("vida:8en", "vida: 8 en"), ("y7en", "y 7 en"), ("calibración7", "calibración 7"),
            ("omit_returnes", "omit_return es"), ("enteras0a64", "enteras 0 a 64"),
            ("a32situaciones", "a 32 situaciones"), ("anatomíaR9con", "anatomía R9 con"),
            ("los21/21de", "los 21/21 de"), ("los16/18del", "los 16/18 del"),
            ("entradasNSM65ni", "entradas NSM65 ni"), ("R10quedó", "R10 quedó"),
            ("R9_01aR9_05", "R9_01 a R9_05"), ("R2/R3y", "R2/R3 y"),
            ("CAL8_OMITy", "CAL8_OMIT y"), ("edición1.8se", "edición 1.8 se"),
            ("propios175/171", "propios 175/171"), ("diferencia4", "diferencia 4"),
            ("social7/5", "social 7/5"), ("ambiental8", "ambiental 8"),
            ("ambiental7", "ambiental 7"), ("116/113permanecieron", "116/113 permanecieron"),
            ("nuevos:18/26", "nuevos: 18/26"), ("diferencia 3y", "diferencia 3 y"),
        ):
            content = content.replace(old, new)
        content = re.sub(r"(?<=es)(?=[0-9a-f]{64}\b)", " ", content)
    p = E.Element(W + "p")
    props = E.SubElement(p, W + "pPr")
    st = E.SubElement(props, W + "pStyle"); st.set(W + "val", style)
    run = E.SubElement(p, W + "r")
    # Existing named styles control typography and spacing.
    for i, line in enumerate(content.split("\n")):
        if i: E.SubElement(run, W + "br")
        t = E.SubElement(run, W + "t")
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        t.text = line
    return p

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=OUT)
    args = ap.parse_args()
    results = json.loads(args.results.read_text(encoding="utf-8"))
    if results.get("status") != "FINAL_RESULTS_APPROVED_FOR_MANUAL":
        raise ValueError("Final, attributed CF01 results must be explicitly provided before authoring")
    if hashlib.sha256(BASE.read_bytes()).hexdigest() != BASE_SHA:
        raise ValueError("Retained reference changed; stop before editing")
    if args.output.exists(): raise FileExistsError("Preserve prior edition output; use an explicitly new candidate path")
    with ZipFile(BASE) as source:
        members = {i.filename: source.read(i.filename) for i in source.infolist()}
        infos = source.infolist()
    doc = E.fromstring(members["word/document.xml"])
    body = doc.find(W + "body")
    paras = list(doc.iter(W + "p"))
    by_text = {text(p): p for p in paras}
    replacements = {
        "Edición documental 1.8  |  DCS11-MM-001": "Edición documental 1.9  |  DCS11-MM-001",
        "DCS11-MM-001 / Edición documental 1.8": "DCS11-MM-001 / Edición documental 1.9",
        "22/10/2026; MI02 MAIN T81207; alternativa operativa R9 T20021": results["control_cut"],
        "Edición1.7 MI01 preservada; estados y resultados ejecutados de MI02": "Edición1.8 MI02 preservada; resultados ejecutados y distribución independiente de CF01.",
        "Word actualizado realmente y estructura comprobada. Validación visual no acreditada; consulte el registro de render MI02.": "Word actualizado y estructura comprobada. Validación visual no acreditada; el comprobante editorial CF01 conserva el intento de render y sus límites.",
        "No incluye una vida entrenada seleccionada.": "El corte original no incluía una vida entrenada de este perfil; las preparaciones MI02 y CF01 admitidas se identifican con sus vidas reales y dominios en los capítulos25 y26.",
        "Mundo nuevo sin capacidades cognitivas instaladas automáticamente. No incluye una vida entrenada seleccionada.": "Un mundo nuevo no contiene aprendizaje automáticamente. Este perfil también conserva mundos vividos específicos de MI02 y CF01, con anatomía, conocimientos y contratos propios; véanse los capítulos25 y26.",
        "Vidas seleccionadas: ninguna vida aprendida incluida.": "Vidas seleccionadas posteriores: R9 y sus descendientes CF01 expresamente catalogados. No son el E1 protegido ni una receta vacía presentada como memoria.",
    }
    changes = []
    for old, new in replacements.items():
        if old in by_text:
            set_text(by_text[old], new); changes.append({"old": old, "new": new})
    cover = next(p for p in paras if text(p).startswith("Corte documental actualizado:"))
    set_text(cover, results["cover"])
    changes.append({"slot": "cover_cut", "new": results["cover"]})
    for p in paras:
        value = text(p)
        if "Edición documental 1.8  |  DCS11-MM-001" in value:
            set_text(p, "DEE thinking 4.5.0  |  DEE Cognitive System 1.1.0\nEdición documental 1.9  |  DCS11-MM-001")
            changes.append({"slot": "cover_edition"})
            continue
        if value.startswith("Qué se revisó realmente"): continue
        if value.startswith("La edición original se basó en el resumen funcional"):
            set_text(p, value + " El capítulo26 cierra CF01, distingue plantilla funcional y futuro final de su única vida, y documenta el servicio utilizable y su distribución. Los estados descritos en capítulos anteriores siguen siendo cortes históricos; la continuidad vigente de CF01 está en su ficha específica. El predeterminado protegido no cambia sin una promoción documentada.")
            changes.append({"slot": "coverage_authority"})
        elif value.startswith("Entorno documentado: Windows x64"):
            set_text(p, "Entorno: Windows x64 y ABI CPython3.13 regular de64bits para DEE thinking4.5. La distribución cognitive sistem incluye los intérpretes portátiles y dependencias declaradas; Universe v27 ya está integrado, no requiere un segundo motor. El entorno ambiental puede usar otro intérprete, con puente explícito. Los requisitos restantes y su comprobación constan en la guía del investigador; no se certifican otras plataformas.")
            changes.append({"slot": "dependencies"})
        elif value.startswith("El software permanece 1.1.0"):
            set_text(p, "El software permanece en la capa Cognitive1.1 sobre DEE thinking4.5.0 y Universev27 congelados. Esta edición documental es1.9 CF01. Una nueva vida no cambia automáticamente el perfil ni recibe memorias de otra. La edición1.8 y sus fuentes quedan preservadas como genealogía; los cambios de software del cierre se identifican en el manifiesto de liberación.")
            changes.append({"slot": "software_document_versions"})
        elif value.startswith("Como antecedente, la edición1.5 integró"):
            set_text(p, "Las ediciones1.5–1.8 incorporaron respectivamente Integración Situada, Ciclo02, MI01 y MI02, conservadas como antecedentes. La edición1.9 incorpora el cierre funcional CF01 y los procedimientos de investigación independiente de cognitive sistem. Los resultados y funciones se atribuyen a cada vida y corte; un máximo histórico no sustituye al estado continuable actual.")
            changes.append({"slot": "current_change_log"})
        elif value.startswith("La campaña 1.1 dejó constancia de que no localizó los dos DOCX 4.5."):
            set_text(p, "La campaña1.1 registró la ausencia de los dos DOCX técnicos4.5; una edición documental posterior declara haber recibido sus textos por tramos. CF01 no recuperó esos DOCX originales ni convierte aquella declaración en acceso actual. La ingeniería y la entrega utilizan los archivos técnicos4.5 efectivamente disponibles, los contratos instalados y la especificación aplicable, con su cobertura identificada.")
            changes.append({"slot": "effective_source_access"})
    toc = next(p for p in body if p.tag == W + "p" and text(p).startswith("Apéndice A. Inventario") and p.find(f"{W}pPr/{W}pStyle") is not None and p.find(f"{W}pPr/{W}pStyle").get(W + "val") == "TOCline")
    body.insert(list(body).index(toc), paragraph("TOCline", "26 Cierre funcional CF01 y uso independiente"))
    anchor = next(p for p in body if p.tag == W + "p" and text(p).startswith("Apéndice A. Inventario") and p.find(f"{W}pPr/{W}pStyle") is not None and p.find(f"{W}pPr/{W}pStyle").get(W + "val") == "Heading1")
    insertion = [paragraph("Heading1", "26 Cierre funcional CF01 y uso independiente")]
    for item in results["chapter"]:
        if item["style"] not in ("Heading2", "Heading3", "Normal", "Code", "Source", "Small"):
            raise ValueError("Unapproved existing style " + item["style"])
        insertion.append(paragraph(item["style"], item["text"]))
    position = list(body).index(anchor)
    for i, node in enumerate(insertion): body.insert(position + i, node)
    members["word/document.xml"] = E.tostring(doc, xml_declaration=True, encoding="UTF-8", standalone=True)
    changed_parts = ["word/document.xml"]
    for name in ("word/header1.xml", "word/footer1.xml"):
        xml = E.fromstring(members[name])
        for t in xml.iter(W + "t"):
            if t.text and "1.8" in t.text: t.text = t.text.replace("1.8", "1.9")
        # Footer field runs are preserved: replace literal w:t only, never field structure.
        members[name] = E.tostring(xml, xml_declaration=True, encoding="UTF-8", standalone=True)
        changed_parts.append(name)
    settings = E.fromstring(members["word/settings.xml"])
    update = settings.find(W + "updateFields")
    if update is None: update = E.SubElement(settings, W + "updateFields")
    update.set(W + "val", "true")
    members["word/settings.xml"] = E.tostring(settings, xml_declaration=True, encoding="UTF-8", standalone=True)
    changed_parts.append("word/settings.xml")
    if "docProps/core.xml" in members:
        core = E.fromstring(members["docProps/core.xml"])
        for n in core:
            if n.tag == DC + "title": n.text = "DEE Cognitive System 1.1 Manual Maestro Edicion 1.9 CF01"
            elif n.tag == DCT + "modified": n.text = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        members["docProps/core.xml"] = E.tostring(core, xml_declaration=True, encoding="UTF-8", standalone=True)
        changed_parts.append("docProps/core.xml")
    with ZipFile(args.output, "w") as output:
        for info in infos: output.writestr(info, members[info.filename])
    if hashlib.sha256(BASE.read_bytes()).hexdigest() != BASE_SHA: raise AssertionError("Baseline changed")
    proof = {"schema": "CF01.manual.edit.v1", "source": str(BASE), "source_sha256": BASE_SHA, "output": str(args.output), "output_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(), "bytes": args.output.stat().st_size, "modified_parts_expected": changed_parts, "changes": changes, "new_chapter_items": len(results["chapter"]), "results_source": str(args.results), "results_sha256": hashlib.sha256(args.results.read_bytes()).hexdigest(), "visual_validation": "REQUIRES_RENDER_ATTEMPT_AND_REVIEW"}
    proof_path = Path(__file__).parent / "EDICION_MANUAL_1_9_CF01.json"
    proof_path.write_text(json.dumps(proof, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(proof, ensure_ascii=True))

if __name__ == "__main__": main()
