"""Surgical Word 1.9 -> 1.10 update, only after final result authorization.

No DEE import and no native ticks. All unedited ZIP members are kept byte-identical.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
DC = "{http://purl.org/dc/elements/1.1/}"
DCT = "{http://purl.org/dc/terms/}"
ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_9_CF01_SIN_VALIDACION_VISUAL.docx"
BASE_SHA = "a48eb2c28d26ce7162a851800e98d2fff82775a672aa3cd64cc62ec4f338269e"
OUT = ROOT / "DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_10_ENTE01_SIN_VALIDACION_VISUAL.docx"


def text(node):
    return "".join(n.text or "" for n in node.iter(W + "t"))


def set_text(p, value):
    if list(p.iter(W + "instrText")):
        raise ValueError("Do not replace a paragraph containing fields")
    run = p.find(W + "r")
    props = deepcopy(run.find(W + "rPr")) if run is not None and run.find(W + "rPr") is not None else None
    for child in list(p):
        if child.tag != W + "pPr":
            p.remove(child)
    run = E.SubElement(p, W + "r")
    if props is not None:
        run.append(props)
    for i, line in enumerate(value.split("\n")):
        if i:
            E.SubElement(run, W + "br")
        item = E.SubElement(run, W + "t")
        item.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        item.text = line


def paragraph(style, value):
    p = E.Element(W + "p")
    props = E.SubElement(p, W + "pPr")
    E.SubElement(props, W + "pStyle").set(W + "val", style)
    set_text(p, value)
    return p


def style(p):
    item = p.find(f"{W}pPr/{W}pStyle")
    return item.get(W + "val") if item is not None else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=OUT)
    args = ap.parse_args()
    results = json.loads(args.results.read_text(encoding="utf-8"))
    if results.get("status") != "FINAL_RESULTS_APPROVED_FOR_MANUAL":
        raise ValueError("Parent authorization of final attributed results is required")
    if hashlib.sha256(BASE.read_bytes()).hexdigest() != BASE_SHA:
        raise ValueError("Reference 1.9 changed; stop before editing")
    if args.output.exists():
        raise FileExistsError("Output exists; preserve it and use an explicitly new candidate path")
    with ZipFile(BASE) as source:
        infos = source.infolist()
        members = {i.filename: source.read(i.filename) for i in infos}
    document = E.fromstring(members["word/document.xml"])
    body = document.find(W + "body")
    paras = list(document.iter(W + "p"))
    changes = []

    exact = {
        "DCS11-MM-001 / Edición documental 1.9": "DCS11-MM-001 / Edición documental 1.10",
        "Edición1.8 MI02 preservada; resultados ejecutados y distribución independiente de CF01.": "Edición 1.9 CF01 preservada; continuación y resultados ejecutados de ENTE_DEE_OPERATIVO_01.",
        "Word actualizado y estructura comprobada. Validación visual no acreditada; el comprobante editorial CF01 conserva el intento de render y sus límites.": "Word actualizado y estructura comprobada. La validación visual y el intento del renderizador autorizado se registran en el comprobante editorial ENTE_DEE_OPERATIVO_01.",
    }
    for p in paras:
        value = text(p)
        replacement = exact.get(value)
        slot = None
        if replacement is not None:
            slot = "exact_control"
        elif value.startswith("DEE thinking 4.5.0  |  DEE Cognitive System 1.1.0") and "Edición documental 1.9" in value:
            replacement = "DEE thinking 4.5.0  |  DEE Cognitive System 1.1.0\nEdición documental 1.10  |  DCS11-MM-001"
            slot = "cover_edition"
        elif value.startswith("Corte documental CF01 del"):
            replacement = results["cover"]
            slot = "cover_cut"
        elif value.startswith("23/10/2026 UTC; CF01_MAIN T67723;"):
            replacement = results["control_cut"]
            slot = "documentary_cut"
        elif value.startswith("La edición original se basó en el resumen funcional"):
            replacement = value + " " + results["authority_note"]
            slot = "authority"
        elif value.startswith("El software permanece en la capa Cognitive1.1"):
            replacement = results["version_note"]
            slot = "version_identity"
        elif value.startswith("Las ediciones1.5–1.8 incorporaron respectivamente"):
            replacement = results["change_log"]
            slot = "change_log"
        elif value.startswith("Un mundo nuevo no contiene aprendizaje automáticamente."):
            replacement = value.replace("MI02 y CF01", "MI02, CF01 y ENTE01").replace("capítulos25 y26", "capítulos 25 a 27")
            slot = "profile_scope"
        elif value.startswith("Vidas seleccionadas posteriores: R9 y sus descendientes CF01"):
            replacement = results["profile_lives"]
            slot = "profile_lives"
        if replacement is not None:
            set_text(p, replacement)
            changes.append({"slot": slot, "old": value, "new": replacement})

    heading = "27 Ente DEE operativo y consecuencias observadas"
    toc_anchor = next(p for p in body if p.tag == W + "p" and style(p) == "TOCline" and text(p).startswith("Apéndice A. Inventario"))
    body.insert(list(body).index(toc_anchor), paragraph("TOCline", heading))
    anchor = next(p for p in body if p.tag == W + "p" and style(p) == "Heading1" and text(p).startswith("Apéndice A. Inventario"))
    insertion = [paragraph("Heading1", heading)]
    for item in results["chapter"]:
        if item["style"] not in ("Heading2", "Heading3", "Normal", "Code", "Source", "Small"):
            raise ValueError("Unapproved paragraph style " + item["style"])
        insertion.append(paragraph(item["style"], item["text"]))
    pos = list(body).index(anchor)
    for offset, node in enumerate(insertion):
        body.insert(pos + offset, node)
    members["word/document.xml"] = E.tostring(document, xml_declaration=True, encoding="UTF-8", standalone=True)
    for name in ("word/header1.xml", "word/footer1.xml"):
        xml = E.fromstring(members[name])
        for item in xml.iter(W + "t"):
            if item.text:
                item.text = item.text.replace("DOCUMENTAL 1.9", "DOCUMENTAL 1.10").replace("documental 1.9", "documental 1.10")
        members[name] = E.tostring(xml, xml_declaration=True, encoding="UTF-8", standalone=True)
    core = E.fromstring(members["docProps/core.xml"])
    for item in core:
        if item.tag == DC + "title":
            item.text = "DEE Cognitive System 1.1 Manual Maestro Edicion 1.10 ENTE01"
        elif item.tag == DCT + "modified":
            item.text = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    members["docProps/core.xml"] = E.tostring(core, xml_declaration=True, encoding="UTF-8", standalone=True)
    with ZipFile(args.output, "w") as output:
        for info in infos:
            output.writestr(info, members[info.filename])
    if hashlib.sha256(BASE.read_bytes()).hexdigest() != BASE_SHA:
        raise AssertionError("Reference changed")
    proof = {
        "schema": "ENTE01.manual.edit.v1", "source": str(BASE), "source_sha256": BASE_SHA,
        "output": str(args.output), "output_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "bytes": args.output.stat().st_size, "changes": changes,
        "new_chapter_items": len(results["chapter"]), "results_source": str(args.results),
        "results_sha256": hashlib.sha256(args.results.read_bytes()).hexdigest(),
        "visual_validation": "REQUIRES_AUTHORIZED_RENDER_AND_REVIEW",
    }
    proof_path = Path(__file__).parent / "EDICION_MANUAL_1_10_ENTE01.json"
    proof_path.write_text(json.dumps(proof, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(proof, ensure_ascii=True))


if __name__ == "__main__":
    main()
