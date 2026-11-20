"""Read-only DOCX extraction and ONE packaged-renderer attempt, zero Native.

This helper never modifies its input and never marks an authoring operation.
Child PATH is limited to bundled dependency folders: no desktop LibreOffice.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from xml.etree import ElementTree as ET
from zipfile import ZipFile


NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
W = "{" + NS["w"] + "}"


def text(node):
    parts = []
    for part in node.iter():
        if part.tag == W + "t":
            parts.append(part.text or "")
        elif part.tag in (W + "br", W + "cr"):
            parts.append("\n")
        elif part.tag == W + "tab":
            parts.append("\t")
    return "".join(parts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--renderer", required=True)
    parser.add_argument("--extract-only", action="store_true")
    args = parser.parse_args()
    source = Path(args.input).resolve(strict=True)
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    marker = output / "RENDER_MANUAL_1_17_INTENTO_UNICO.json"
    if marker.exists() and not args.extract_only:
        raise SystemExit("Read-only attempt already recorded; refusing repeated render")
    initial = source.read_bytes()
    before_hash = hashlib.sha256(initial).hexdigest()
    blocks = []
    with ZipFile(source) as z:
        root = ET.fromstring(z.read("word/document.xml"))
        styles_root = ET.fromstring(z.read("word/styles.xml"))
        style_names = {}
        for style in styles_root.findall("w:style", NS):
            name = style.find("w:name", NS)
            style_names[style.get(W + "styleId")] = name.get(W + "val") if name is not None else ""
        core = z.read("docProps/core.xml").decode("utf-8") if "docProps/core.xml" in z.namelist() else None
        headers_footers = [{"member": name, "text": text(ET.fromstring(z.read(name)))}
                           for name in z.namelist() if re.match(r"word/(?:header|footer)\d+\.xml$", name)]
        for index, child in enumerate(root.find("w:body", NS)):
            if child.tag == W + "p":
                style_node = child.find("w:pPr/w:pStyle", NS)
                style_id = style_node.get(W + "val") if style_node is not None else None
                content = text(child)
                style_name = style_names.get(style_id, style_id or "")
                outline = child.find("w:pPr/w:outlineLvl", NS)
                heading = bool(re.search(r"heading|t.tulo", style_name, re.I)) and style_name.lower() not in ("title", "subtitle")
                if outline is not None:
                    heading = True
                blocks.append({"body_index": index, "kind": "paragraph", "style_id": style_id,
                               "style_name": style_name, "text": content, "heading": heading})
            elif child.tag == W + "tbl":
                rows = [[text(cell) for cell in row.findall("w:tc", NS)] for row in child.findall("w:tr", NS)]
                blocks.append({"body_index": index, "kind": "table", "rows": rows, "heading": False})
    headings = [{"body_index": b["body_index"], "style": b.get("style_name"), "text": b["text"]}
                for b in blocks if b["heading"]]
    sections = []
    current = {"heading": "Preliminares", "blocks": []}
    sections.append(current)
    for block in blocks:
        if block["heading"]:
            current = {"heading": block["text"], "blocks": []}
            sections.append(current)
        current["blocks"].append(block)
    pattern = re.compile(r"APD0[123]|iniciativa|atenci.n|composici.n|continuidad|estado.*vida|vida.*estado|informaci.n.*acceso|continuar|arquitectura|actualizaci.n", re.I)
    selected = [s for s in sections if s is sections[0] or pattern.search(s["heading"])
                or re.match(r"^3[1-4](?:[ .])", s["heading"])
                or s["heading"] in ("Control documental", "Qué se revisó realmente", "Índice de consulta")]
    extraction = {"schema": "DEE.APD04.manual_read_only.N0.R01", "source_path": str(source),
                  "source_bytes": len(initial), "source_sha256": before_hash,
                  "logical_manual_id_expected_not_reassigned": "DCS11-MM-001",
                  "input_unchanged": None, "author_operation_marked": False,
                  "new_native_ticks": 0, "visual_page_numbers_not_established": True,
                  "core_xml": core, "headers_footers": headers_footers,
                  "outline": headings, "selected_sections": selected,
                  "scope": "Structural extraction only; body_index identifies OOXML body order, not a page number."}
    lines = ["EXTRACCIÓN ESTRUCTURAL DE SOLO LECTURA DEL MISMO MANUAL", str(source),
             "SHA-256 " + before_hash, "No valida diseño ni números de página.", "", "ÍNDICE ESTRUCTURAL"]
    lines.extend(str(h["body_index"]) + " | " + h["text"] for h in headings)
    lines.extend(["", "APARTADOS PERTINENTES EN SU TEXTO ORIGINAL"])
    for section in selected:
        lines.extend(["", "SECCIÓN: " + section["heading"]])
        for block in section["blocks"]:
            if block["kind"] == "paragraph":
                lines.append(str(block["body_index"]) + " | " + block["text"])
            else:
                lines.append(str(block["body_index"]) + " | TABLA")
                lines.extend(" | ".join(row) for row in block["rows"])
    (output / "SECCIONES_RELEVANTES_MANUAL_1_17.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if args.extract_only:
        extraction["input_unchanged"] = source.read_bytes() == initial
        (output / "INSPECCION_DOCUMENTAL_1_17.json").write_text(json.dumps(extraction, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"selected_sections": len(selected), "new_render_attempts": 0,
                          "input_unchanged": extraction["input_unchanged"]}))
        return
    dependencies = Path(sys.executable).parent.parent
    child_env = dict(os.environ)
    allowed_dirs = [dependencies / "bin" / "override", dependencies / "bin" / "fallback", Path(sys.executable).parent]
    child_env["PATH"] = os.pathsep.join(map(str, allowed_dirs))
    command = [sys.executable, "-I", "-B", str(Path(args.renderer).resolve(strict=True)), str(source),
               "--output_dir", str(output / "render_1_17"), "--verbose"]
    start = time.monotonic()
    try:
        proc = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace",
                              env=child_env, cwd=output, timeout=60)
        receipt = {"command": command, "returncode": proc.returncode, "stdout": proc.stdout,
                   "stderr": proc.stderr, "timeout": False}
    except subprocess.TimeoutExpired as error:
        receipt = {"command": command, "returncode": None, "timeout": True,
                   "stdout": str(error.stdout), "stderr": str(error.stderr)}
    receipt.update(schema="DEE.APD04.manual_render_read_only.N0.R01", source_sha256=before_hash,
                   elapsed_seconds=time.monotonic() - start, child_PATH=str(child_env["PATH"]),
                   desktop_LibreOffice_permitted=False, render_attempts=1,
                   pages_generated=len(list((output / "render_1_17").glob("page-*.png"))),
                   pages_visually_reviewed=0, new_native_ticks=0)
    extraction["input_unchanged"] = source.read_bytes() == initial
    (output / "INSPECCION_DOCUMENTAL_1_17.json").write_text(json.dumps(extraction, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    marker.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"source_sha256": before_hash, "body_blocks": len(blocks), "headings": len(headings),
                      "selected_sections": len(selected), "input_unchanged": extraction["input_unchanged"],
                      "render_returncode": receipt["returncode"], "pages_generated": receipt["pages_generated"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
