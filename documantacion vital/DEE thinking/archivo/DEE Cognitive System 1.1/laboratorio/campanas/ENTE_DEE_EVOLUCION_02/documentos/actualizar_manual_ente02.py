"""Narrow 1.10 -> 1.11 Word update after final result authorization. Zero DEE ticks."""
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
BASE = ROOT / "DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_10_ENTE01_SIN_VALIDACION_VISUAL.docx"
BASE_SHA = "c9b962d1efa14145b6c7d93d3695892475dc4ca0ba52c66731c86b07de33abf5"
OUT = ROOT / "DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_11_ENTE02_SIN_VALIDACION_VISUAL.docx"
HEADING = "28 Capacidad transferencia y continuidad de ENTE02"


def text(node):
    return "".join(n.text or "" for n in node.iter(W + "t"))


def style(p):
    node = p.find(f"{W}pPr/{W}pStyle")
    return node.get(W + "val", "") if node is not None else ""


def set_text(p, value):
    if list(p.iter(W + "instrText")):
        raise ValueError("Refuse replacement of a paragraph containing a Word field")
    run = p.find(W + "r")
    props = deepcopy(run.find(W + "rPr")) if run is not None and run.find(W + "rPr") is not None else None
    for node in list(p):
        if node.tag != W + "pPr":
            p.remove(node)
    run = E.SubElement(p, W + "r")
    if props is not None:
        run.append(props)
    for i, line in enumerate(value.split("\n")):
        if i:
            E.SubElement(run, W + "br")
        node = E.SubElement(run, W + "t")
        node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        node.text = line


def paragraph(st, value):
    p = E.Element(W + "p")
    props = E.SubElement(p, W + "pPr")
    E.SubElement(props, W + "pStyle").set(W + "val", st)
    set_text(p, value)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=OUT)
    args = ap.parse_args()
    data = json.loads(args.results.read_text(encoding="utf-8"))
    if data.get("status") != "FINAL_RESULTS_APPROVED_FOR_MANUAL":
        raise ValueError("Final approved result cut required")
    if hashlib.sha256(BASE.read_bytes()).hexdigest() != BASE_SHA:
        raise ValueError("Reference 1.10 identity changed")
    if args.output.exists():
        raise FileExistsError("Preserve existing edition; choose an explicitly new output")
    with ZipFile(BASE) as source:
        infos = source.infolist()
        members = {i.filename: source.read(i.filename) for i in infos}
    document = E.fromstring(members["word/document.xml"])
    body = document.find(W + "body")
    changes = []
    slots = set()
    for p in list(document.iter(W + "p")):
        old = text(p)
        new = None
        slot = None
        if old == "DCS11-MM-001 / Edición documental 1.10":
            new, slot = "DCS11-MM-001 / Edición documental 1.11", "control_edition"
        elif old.startswith("DEE thinking 4.5.0  |  DEE Cognitive System 1.1.0") and "Edición documental 1.10" in old:
            new = "DEE thinking 4.5.0  |  DEE Cognitive System 1.1.0\nEdición documental 1.11  |  DCS11-MM-001"
            slot = "cover_edition"
        elif old.startswith("Corte documental ENTE01 del"):
            new, slot = data["cover"], "cover_cut"
        elif old.startswith("24/10/2026 UTC; EO01_MAIN T121681,"):
            new, slot = data["control_cut"], "control_cut"
        elif old == "Edición 1.9 CF01 preservada; continuación y resultados ejecutados de ENTE_DEE_OPERATIVO_01.":
            new, slot = "Edición 1.10 ENTE01 preservada; continuación y resultados ejecutados de ENTE_DEE_EVOLUCION_02.", "source_edition"
        elif old.startswith("Word actualizado y estructura comprobada. La validación visual y el intento del renderizador autorizado"):
            new = "Word actualizado y estructura comprobada. La validación visual y el intento del renderizador autorizado se registran en el comprobante editorial ENTE_DEE_EVOLUCION_02."
            slot = "validation_scope"
        elif old.startswith("La edición original se basó en el resumen funcional"):
            new, slot = old + " " + data["authority_note"], "authority_note"
        elif old.startswith("El software permanece en la capa Cognitive 1.1.0"):
            new, slot = data["version_note"], "version_note"
        elif old.startswith("Las ediciones 1.5 a 1.9 incorporaron Integración Situada"):
            new, slot = data["change_log"], "change_log"
        elif old.startswith("Un mundo nuevo no contiene aprendizaje automáticamente."):
            new = old.replace("MI02, CF01 y ENTE01", "MI02, CF01, ENTE01 y ENTE02").replace("capítulos 25 a 27", "capítulos 25 a 28")
            slot = "profile_scope"
        elif old.startswith("Vidas seleccionadas posteriores: R9, sus descendientes CF01 y EO01_MAIN"):
            new, slot = data["profile_lives"], "profile_lives"
        if new is not None:
            if slot in slots:
                raise AssertionError("Ambiguous editable source slot " + slot)
            slots.add(slot)
            set_text(p, new)
            changes.append({"slot": slot, "old": old, "new": new})
    needed = {"control_edition", "cover_edition", "cover_cut", "control_cut", "source_edition", "validation_scope", "authority_note", "version_note", "change_log", "profile_scope", "profile_lives"}
    if slots != needed:
        raise AssertionError("Missing or unexpected edit slots " + repr(slots ^ needed))
    toc = next(p for p in body if p.tag == W + "p" and style(p) == "TOCline" and text(p).startswith("Apéndice A. Inventario"))
    body.insert(list(body).index(toc), paragraph("TOCline", HEADING))
    app = next(p for p in body if p.tag == W + "p" and style(p) == "Heading1" and text(p).startswith("Apéndice A. Inventario"))
    nodes = [paragraph("Heading1", HEADING)]
    for item in data["chapter"]:
        if item["style"] not in {"Heading2", "Heading3", "Normal", "Code", "Source", "Small"}:
            raise ValueError("Unapproved existing style " + item["style"])
        nodes.append(paragraph(item["style"], item["text"]))
    at = list(body).index(app)
    for offset, node in enumerate(nodes):
        body.insert(at + offset, node)
    members["word/document.xml"] = E.tostring(document, xml_declaration=True, encoding="UTF-8", standalone=True)
    for name in ("word/header1.xml", "word/footer1.xml"):
        tree = E.fromstring(members[name])
        for node in tree.iter(W + "t"):
            if node.text:
                node.text = node.text.replace("DOCUMENTAL 1.10", "DOCUMENTAL 1.11").replace("documental 1.10", "documental 1.11")
        members[name] = E.tostring(tree, xml_declaration=True, encoding="UTF-8", standalone=True)
    core = E.fromstring(members["docProps/core.xml"])
    for node in core:
        if node.tag == DC + "title":
            node.text = "DEE Cognitive System 1.1 Manual Maestro Edicion 1.11 ENTE02"
        elif node.tag == DCT + "modified":
            node.text = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    members["docProps/core.xml"] = E.tostring(core, xml_declaration=True, encoding="UTF-8", standalone=True)
    with ZipFile(args.output, "w") as output:
        for info in infos:
            output.writestr(info, members[info.filename])
    if hashlib.sha256(BASE.read_bytes()).hexdigest() != BASE_SHA:
        raise AssertionError("Retained source changed")
    proof = {"schema": "ENTE02.manual.edit.v1", "source": str(BASE), "source_sha256": BASE_SHA,
             "output": str(args.output), "output_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
             "bytes": args.output.stat().st_size, "changes": changes, "chapter_items": len(data["chapter"]),
             "results_source": str(args.results.resolve()), "results_sha256": hashlib.sha256(args.results.read_bytes()).hexdigest(),
             "visual_validation": "REQUIRES_AUTHORIZED_RENDER_AND_REVIEW"}
    target = Path(__file__).parent / "EDICION_MANUAL_1_11_ENTE02.json"
    target.write_text(json.dumps(proof, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(proof, ensure_ascii=True))


if __name__ == "__main__":
    main()
