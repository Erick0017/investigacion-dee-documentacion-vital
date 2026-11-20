"""Check the final Word package against its retained baseline without native ticks."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REF = ROOT / "DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_8_MI02_SIN_VALIDACION_VISUAL.docx"
FINAL = ROOT / "DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_9_CF01_SIN_VALIDACION_VISUAL.docx"
ALLOWED = {"word/document.xml", "word/header1.xml", "word/footer1.xml", "word/settings.xml", "docProps/core.xml"}

def package(path):
    with ZipFile(path) as z:
        if z.testzip() is not None: raise AssertionError("CRC error")
        return {name: z.read(name) for name in z.namelist()}

def txt(p): return "".join(t.text or "" for t in p.iter(W + "t"))
def style(p):
    s = p.find(f"{W}pPr/{W}pStyle")
    return s.get(W + "val") if s is not None else "Normal"

def main():
    left, right = package(REF), package(FINAL)
    assert set(left) == set(right), "Package members differ"
    changed = [n for n in right if right[n] != left[n]]
    assert set(changed) <= ALLOWED, changed
    old = E.fromstring(left["word/document.xml"])
    new = E.fromstring(right["word/document.xml"])
    assert [E.tostring(x) for x in old.iter(W + "sectPr")] == [E.tostring(x) for x in new.iter(W + "sectPr")]
    paras = list(new.find(W + "body").iter(W + "p"))
    heads = [txt(p) for p in paras if style(p) == "Heading1"]
    assert heads.count("26 Cierre funcional CF01 y uso independiente") == 1
    assert heads.index("26 Cierre funcional CF01 y uso independiente") < heads.index("Apéndice A. Inventario de las 73 entradas")
    toc = [txt(p) for p in paras if style(p) == "TOCline"]
    assert toc.count("26 Cierre funcional CF01 y uso independiente") == 1
    assert toc.index("26 Cierre funcional CF01 y uso independiente") < toc.index("Apéndice A. Inventario de las 73 entradas")
    field_parts = ("word/header1.xml", "word/footer1.xml", "word/document.xml")
    fields = lambda p: [n.text for name in field_parts for n in E.fromstring(p[name]).iter(W + "instrText")]
    assert fields(left) == fields(right)
    content = "\n".join(txt(p) for p in paras)
    for required in ("Edición documental 1.9", "CF01_MAIN T67723", "E1_SOCIAL_11 T3154", "CF01.R9.protocol.4", "servicio-cf01 MI_VIDA --mediciones=20:28,7:13,9:18", "18 de 18", "4 de 5"):
        assert required in content, required
    assert hashlib.sha256(REF.read_bytes()).hexdigest() == "1f37b20a860b50835b87bbfcf8bc783f23e31c37db7d230bf4bb350e9106504a"
    report = {
        "schema": "CF01.manual.fidelity.v1", "reference": str(REF), "reference_unchanged": True,
        "final": str(FINAL), "sha256": hashlib.sha256(FINAL.read_bytes()).hexdigest(),
        "bytes": FINAL.stat().st_size, "members": len(right), "changed_parts": changed,
        "preserved_parts": len(right) - len(changed), "section_geometry_preserved": True,
        "chapter26_before_appendices": True, "static_toc_updated_without_unverified_pages": True,
        "fields_preserved": fields(right), "opaque_parts_preserved": True,
        "visual_status": "NOT_VALIDATED_RENDERER_BUNDLED_LIBREOFFICE_ABSENT",
        "render_report": str(HERE / "qa_final_1_9_rev3/VERIFICACION_DOCUMENTO.json"),
        "native_ticks": 0,
    }
    (HERE / "VERIFICACION_MANUAL_CF01.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True))

if __name__ == "__main__": main()
