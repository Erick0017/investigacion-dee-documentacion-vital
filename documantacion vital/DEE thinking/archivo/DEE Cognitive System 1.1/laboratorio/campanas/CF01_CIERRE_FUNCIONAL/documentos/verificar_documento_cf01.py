"""Structural DOCX QA and one bounded bundled-render attempt, no desktop LO."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from xml.etree import ElementTree as ET
from zipfile import ZipFile

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
BUNDLE = Path(sys.executable).parent.parent
SKILL = Path(r"C:\Users\Erik\.codex\plugins\cache\openai-primary-runtime\documents\26.1011.51657\skills\documents")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("document", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--baseline", type=Path)
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    data = a.document.read_bytes()
    report = {"document": str(a.document.resolve()), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    with ZipFile(a.document) as z:
        report["crc_error"] = z.testzip()
        parts = {n: z.read(n) for n in z.namelist()}
        for name, value in parts.items():
            if name.endswith(".xml"): ET.fromstring(value)
        body = ET.fromstring(parts["word/document.xml"])
        report["headings"] = []
        for para in body.iter(W + "p"):
            style = para.find(f"{W}pPr/{W}pStyle")
            if style is not None and style.get(W + "val", "").startswith("Heading"):
                report["headings"].append("".join(t.text or "" for t in para.iter(W + "t")))
        report["sections"] = [ET.tostring(x, encoding="unicode") for x in body.iter(W + "sectPr")]
        report["fields"] = {name: [x.text for x in ET.fromstring(value).iter(W + "instrText")] for name, value in parts.items() if name.endswith(".xml") and ("document" in name or "header" in name or "footer" in name)}
        report["members"] = {n: {"bytes": len(v), "sha256": hashlib.sha256(v).hexdigest()} for n, v in parts.items()}
        if a.baseline:
            with ZipFile(a.baseline) as original:
                report["changed_parts"] = [n for n, v in parts.items() if n not in original.namelist() or v != original.read(n)]
                report["removed_parts"] = [n for n in original.namelist() if n not in parts]
    env = os.environ.copy()
    # Windows renderer otherwise searches user desktop LO from PATH. The skill
    # requires runtime-authoritative binaries, so this scope deliberately excludes it.
    env["PATH"] = os.pathsep.join(map(str, [Path(sys.executable).parent, BUNDLE / "bin/override", BUNDLE / "bin/fallback", BUNDLE / "native/poppler/bin"]))
    env["PYTHONIOENCODING"] = "utf-8"
    command = [sys.executable, str(SKILL / "render_docx.py"), str(a.document), "--output_dir", str(a.out / "render"), "--emit_pdf", "--verbose"]
    try:
        result = subprocess.run(command, cwd=Path(__file__).parent, env=env, capture_output=True, encoding="utf-8", errors="replace", timeout=50)
        report["render"] = {"command": command, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr, "bundled_path_only": env["PATH"], "pages": [str(x) for x in (a.out / "render").glob("page-*.png")]}
    except subprocess.TimeoutExpired as exc:
        report["render"] = {"command": command, "error": "timeout_50_seconds", "stdout": str(exc.stdout), "stderr": str(exc.stderr)}
    report["visual_validation"] = "NOT_AVAILABLE_RENDER_FAILED" if not report["render"].get("pages") else "PAGES_REQUIRE_HUMAN_OR_MODEL_REVIEW"
    path = a.out / "VERIFICACION_DOCUMENTO.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(path), "crc_error": report["crc_error"], "visual_validation": report["visual_validation"], "render": report["render"]}, ensure_ascii=True))

if __name__ == "__main__": main()
