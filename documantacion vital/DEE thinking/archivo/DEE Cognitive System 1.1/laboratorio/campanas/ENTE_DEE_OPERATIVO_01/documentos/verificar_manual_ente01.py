"""Structural fidelity and an optional bounded bundle-only DOCX render attempt."""
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
BASE_SHA = "a48eb2c28d26ce7162a851800e98d2fff82775a672aa3cd64cc62ec4f338269e"
SKILL = Path(r"C:\Users\Erik\.codex\plugins\cache\openai-primary-runtime\documents\26.1011.51657\skills\documents")


def contents(path):
    with ZipFile(path) as z:
        if z.testzip() is not None:
            raise AssertionError("ZIP CRC error")
        return {name: z.read(name) for name in z.namelist()}


def text(p):
    return "".join(n.text or "" for n in p.iter(W + "t"))


def style(p):
    item = p.find(f"{W}pPr/{W}pStyle")
    return "" if item is None else item.get(W + "val", "")


def fieldmap(parts):
    return {name: [x.text for x in E.fromstring(value).iter(W + "instrText")]
            for name, value in parts.items() if name.endswith(".xml") and name.startswith(("word/document", "word/header", "word/footer"))}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("document", type=Path)
    p.add_argument("--baseline", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--results", type=Path)
    p.add_argument("--try-render", action="store_true")
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    if hashlib.sha256(a.baseline.read_bytes()).hexdigest() != BASE_SHA:
        raise AssertionError("Reference 1.9 identity changed")
    original, final = contents(a.baseline), contents(a.document)
    if original.keys() != final.keys():
        raise AssertionError("DOCX members added or removed")
    parsed = {name: E.fromstring(value) for name, value in final.items() if name.endswith(".xml")}
    changed = [name for name in final if original[name] != final[name]]
    allowed = {"word/document.xml", "word/header1.xml", "word/footer1.xml", "docProps/core.xml"}
    if not set(changed) <= allowed:
        raise AssertionError("Unexpected changed DOCX part " + repr(set(changed) - allowed))
    old_doc = E.fromstring(original["word/document.xml"])
    doc = parsed["word/document.xml"]
    sections = [E.tostring(x) for x in doc.iter(W + "sectPr")]
    if sections != [E.tostring(x) for x in old_doc.iter(W + "sectPr")]:
        raise AssertionError("Page geometry changed")
    if fieldmap(original) != fieldmap(final):
        raise AssertionError("Field structure changed")
    body = doc.find(W + "body")
    paragraphs = list(body.iter(W + "p"))
    index = [(style(x), text(x)) for x in paragraphs]
    h27 = index.index(("Heading1", "27 Ente DEE operativo y consecuencias observadas"))
    toc27 = index.index(("TOCline", "27 Ente DEE operativo y consecuencias observadas"))
    appendix = next(i for i, x in enumerate(index) if x[0] == "Heading1" and x[1].startswith("Apéndice A."))
    if not toc27 < h27 < appendix:
        raise AssertionError("New chapter or TOC order invalid")
    # The retained CF01 chapter and all appendices are scientific history.
    old_paras = list(old_doc.find(W + "body").iter(W + "p"))
    old_index = [(style(x), text(x)) for x in old_paras]
    old_start = old_index.index(("Heading1", "26 Cierre funcional CF01 y uso independiente"))
    old_app = next(i for i, x in enumerate(old_index) if x[0] == "Heading1" and x[1].startswith("Apéndice A."))
    new_start = index.index(("Heading1", "26 Cierre funcional CF01 y uso independiente"))
    if old_index[old_start:old_app] != index[new_start:h27]:
        raise AssertionError("Historical CF01 chapter was changed")
    if old_index[old_app:] != index[appendix:]:
        raise AssertionError("Appendix text changed")
    complete = "\n".join(x[1] for x in index)
    for required in ("Edición documental 1.10", "E1_SOCIAL_11", "67723", "capítulo 27"):
        if required not in complete:
            raise AssertionError("Missing identity text " + required)
    if a.results:
        results = json.loads(a.results.read_text(encoding="utf-8"))
        for required in results.get("qa_required_text", []):
            if required not in complete:
                raise AssertionError("Required approved result missing " + required)
    report = {
        "schema": "ENTE01.manual.fidelity.v1", "document": str(a.document.resolve()),
        "bytes": a.document.stat().st_size, "sha256": hashlib.sha256(a.document.read_bytes()).hexdigest(),
        "baseline": str(a.baseline.resolve()), "baseline_sha256": BASE_SHA,
        "members": len(final), "changed_parts": changed, "unchanged_member_count": len(final) - len(changed),
        "page_geometry_unchanged": True, "fields_unchanged": True,
        "cf01_chapter_unchanged": True, "appendices_unchanged": True,
        "headings": [x[1] for x in index if x[0].startswith("Heading")],
        "member_hashes": {name: hashlib.sha256(value).hexdigest() for name, value in final.items()},
        "visual_validation": "NOT_ATTEMPTED",
    }
    if a.try_render:
        dependency_root = Path(sys.executable).parent.parent
        env = os.environ.copy()
        env["PATH"] = os.pathsep.join(map(str, [Path(sys.executable).parent,
            dependency_root / "bin/override", dependency_root / "bin/fallback",
            dependency_root / "native/poppler/bin"]))
        env["PYTHONIOENCODING"] = "utf-8"
        command = [sys.executable, str(SKILL / "render_docx.py"), str(a.document.resolve()),
                   "--output_dir", str((a.out / "render").resolve()), "--emit_pdf", "--verbose"]
        try:
            run = subprocess.run(command, env=env, cwd=a.out, capture_output=True,
                                 encoding="utf-8", errors="replace", timeout=50)
            report["render"] = {"command": command, "exit_code": run.returncode,
                "stdout": run.stdout, "stderr": run.stderr, "authorized_bundle_PATH": env["PATH"]}
        except subprocess.TimeoutExpired as exc:
            report["render"] = {"command": command, "error": "timeout_50_seconds",
                "stdout": str(exc.stdout), "stderr": str(exc.stderr), "authorized_bundle_PATH": env["PATH"]}
        report["render"]["pages"] = [str(x) for x in (a.out / "render").glob("page-*.png")]
        report["visual_validation"] = "PAGES_REQUIRE_FULL_REVIEW" if report["render"]["pages"] else "NOT_AVAILABLE_RENDER_FAILED"
    target = a.out / "VERIFICACION_MANUAL_ENTE01.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(target), "sha256": report["sha256"], "changed_parts": changed,
                      "visual_validation": report["visual_validation"], "render": report.get("render")}, ensure_ascii=True))


if __name__ == "__main__":
    main()
