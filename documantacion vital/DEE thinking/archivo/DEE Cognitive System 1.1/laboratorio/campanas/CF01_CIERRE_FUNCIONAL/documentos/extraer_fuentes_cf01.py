"""Read-only source extraction for CF01; no DEE imports or physical ticks."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"

def extract(path: Path) -> tuple[str, dict]:
    data = path.read_bytes()
    info = {"source": str(path), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    if path.suffix.lower() != ".docx":
        text = data.decode("utf-8-sig")
        info["extraction"] = "COMPLETE_UTF8_TEXT"
        return text, info
    chunks = []
    with ZipFile(path) as z:
        parts = [n for n in z.namelist() if n.replace("\\", "/") == "word/document.xml"]
        parts += [n for n in z.namelist() if n.replace("\\", "/").startswith(("word/header", "word/footer", "word/footnotes", "word/endnotes")) and n.endswith(".xml")]
        for name in parts:
            chunks.append("PART " + name)
            root = ET.fromstring(z.read(name))
            for i, paragraph in enumerate(root.iter(W + "p")):
                words = []
                for node in paragraph.iter():
                    if node.tag in (W + "t", M + "t"): words.append(node.text or "")
                    elif node.tag == W + "tab": words.append("\t")
                    elif node.tag in (W + "br", W + "cr"): words.append("\n")
                text = "".join(words)
                if text:
                    props = paragraph.find(W + "pPr")
                    style = props.find(W + "pStyle") if props is not None else None
                    label = style.get(W + "val", "") if style is not None else ""
                    chunks.append(f"P{i:05d} [{label}] {text}")
        info["parts"] = parts
        info["extraction"] = "COMPLETE_TEXT_AND_LINEAR_OMML_TOKENS_IN_DOCUMENT_HEADERS_FOOTERS_NOTES_NO_IMAGE_OCR"
        info["math_caveat"] = "OMML token order is preserved, not visual fraction/superscript layout; inspect source XML for equations."
    return "\n".join(chunks) + "\n", info

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sources", nargs="+")
    parser.add_argument("--out", type=Path, default=Path(__file__).parent / "textos")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    index_path = args.out.parent / "INDICE_FUENTES_EXTRAIDAS.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else []
    by_path = {item["source"]: item for item in index}
    for source in args.sources:
        path = Path(source).resolve()
        text, info = extract(path)
        suffix = "" if path.suffix.lower() == ".docx" else "__" + hashlib.sha256(str(path.parent).encode("utf-8")).hexdigest()[:10]
        target = args.out / (path.stem + suffix + ".txt")
        target.write_text(text, encoding="utf-8")
        info.update(extract=str(target), extract_sha256=hashlib.sha256(target.read_bytes()).hexdigest(), characters=len(text))
        by_path[str(path)] = info
        print(json.dumps(info, ensure_ascii=True))
    index_path.write_text(json.dumps(list(by_path.values()), ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__": main()
