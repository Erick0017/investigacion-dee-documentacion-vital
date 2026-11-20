"""Structural preservation and bounded bundle-only render; never import DEE."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile
from lxml import etree as E

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
BASE_SHA = "c9b962d1efa14145b6c7d93d3695892475dc4ca0ba52c66731c86b07de33abf5"
HEADING = "28 Capacidad transferencia y continuidad de ENTE02"
SKILL = Path(r"C:\Users\Erik\.codex\plugins\cache\openai-primary-runtime\documents\26.1011.51657\skills\documents")


def contents(path):
    with ZipFile(path) as z:
        if z.testzip() is not None:
            raise AssertionError("DOCX CRC error")
        if len(z.namelist()) != len(set(z.namelist())):
            raise AssertionError("Duplicate DOCX member")
        return {name: z.read(name) for name in z.namelist()}


def text(node):
    return "".join(n.text or "" for n in node.iter(W + "t"))


def style(p):
    node = p.find(f"{W}pPr/{W}pStyle")
    return node.get(W + "val", "") if node is not None else ""


def fields(parts):
    return {name: [n.text for n in E.fromstring(value).iter(W + "instrText")]
            for name, value in parts.items() if name.endswith(".xml") and name.startswith(("word/document", "word/header", "word/footer"))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("document", type=Path)
    ap.add_argument("--baseline", type=Path, required=True)
    ap.add_argument("--results", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--try-render", action="store_true")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    if hashlib.sha256(args.baseline.read_bytes()).hexdigest() != BASE_SHA:
        raise AssertionError("Baseline 1.10 identity changed")
    old, final = contents(args.baseline), contents(args.document)
    if old.keys() != final.keys():
        raise AssertionError("DOCX members added or removed")
    parsed = {name: E.fromstring(value) for name, value in final.items() if name.endswith(".xml")}
    changed = [name for name in final if old[name] != final[name]]
    if not set(changed) <= {"word/document.xml", "word/header1.xml", "word/footer1.xml", "docProps/core.xml"}:
        raise AssertionError("Unexpected changed DOCX part")
    olddoc = E.fromstring(old["word/document.xml"])
    doc = parsed["word/document.xml"]
    if [E.tostring(x) for x in olddoc.iter(W + "sectPr")] != [E.tostring(x) for x in doc.iter(W + "sectPr")]:
        raise AssertionError("Page geometry or section configuration changed")
    if fields(old) != fields(final):
        raise AssertionError("Field structure changed")
    oi = [(style(x), text(x)) for x in olddoc.find(W + "body").iter(W + "p")]
    ni = [(style(x), text(x)) for x in doc.find(W + "body").iter(W + "p")]
    h28 = ni.index(("Heading1", HEADING))
    toc28 = ni.index(("TOCline", HEADING))
    oa = next(i for i, x in enumerate(oi) if x[0] == "Heading1" and x[1].startswith("Apéndice A."))
    na = next(i for i, x in enumerate(ni) if x[0] == "Heading1" and x[1].startswith("Apéndice A."))
    if not toc28 < h28 < na:
        raise AssertionError("Invalid chapter and TOC order")
    o26 = oi.index(("Heading1", "26 Cierre funcional CF01 y uso independiente"))
    n26 = ni.index(("Heading1", "26 Cierre funcional CF01 y uso independiente"))
    if oi[o26:oa] != ni[n26:h28]:
        raise AssertionError("Historical CF01 or EO01 text changed")
    if oi[oa:] != ni[na:]:
        raise AssertionError("Historical appendix text changed")
    whole = "\n".join(x[1] for x in ni)
    result = json.loads(args.results.read_text(encoding="utf-8"))
    for value in ["Edición documental 1.11", "E1_SOCIAL_11", "121681", "capítulo 28"] + result.get("qa_required_text", []):
        if value not in whole:
            raise AssertionError("Required approved text missing: " + value)
    report = {"schema": "ENTE02.manual.fidelity.v1", "document": str(args.document.resolve()),
              "bytes": args.document.stat().st_size, "sha256": hashlib.sha256(args.document.read_bytes()).hexdigest(),
              "baseline": str(args.baseline.resolve()), "baseline_sha256": BASE_SHA,
              "members": len(final), "changed_parts": changed, "unchanged_member_count": len(final) - len(changed),
              "page_geometry_unchanged": True, "fields_unchanged": True, "cf01_eo01_chapters_unchanged": True,
              "appendices_unchanged": True, "headings": [x[1] for x in ni if x[0].startswith("Heading")],
              "member_hashes": {n: hashlib.sha256(v).hexdigest() for n, v in final.items()},
              "visual_validation": "NOT_ATTEMPTED", "native_ticks": 0}
    if args.try_render:
        deps = Path(sys.executable).parent.parent
        env = os.environ.copy()
        env["PATH"] = os.pathsep.join(map(str, [Path(sys.executable).parent, deps / "bin/override", deps / "bin/fallback", deps / "native/poppler/bin"]))
        env["PYTHONIOENCODING"] = "utf-8"
        command = [sys.executable, str(SKILL / "render_docx.py"), str(args.document.resolve()), "--output_dir", str((args.out / "render").resolve()), "--emit_pdf", "--verbose"]
        try:
            proc = subprocess.run(command, cwd=args.out, env=env, capture_output=True, encoding="utf-8", errors="replace", timeout=50)
            report["render"] = {"command": command, "exit_code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr, "authorized_bundle_PATH": env["PATH"]}
        except subprocess.TimeoutExpired as exc:
            report["render"] = {"command": command, "error": "timeout_50_seconds", "stdout": str(exc.stdout), "stderr": str(exc.stderr), "authorized_bundle_PATH": env["PATH"]}
        pages = list((args.out / "render").glob("page-*.png"))
        report["render"]["pages"] = [str(x) for x in pages]
        report["visual_validation"] = "PAGES_REQUIRE_FULL_REVIEW" if pages else "NOT_AVAILABLE_RENDER_FAILED"
    target = args.out / "VERIFICACION_MANUAL_ENTE02.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(target), "sha256": report["sha256"], "bytes": report["bytes"], "changed_parts": changed, "visual_validation": report["visual_validation"], "render": report.get("render")}, ensure_ascii=True))


if __name__ == "__main__":
    main()
