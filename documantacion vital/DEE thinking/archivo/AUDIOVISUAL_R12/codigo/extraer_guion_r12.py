"""Literal R12 extraction from the supplied DOCX; NOT the missing original JSON."""
from pathlib import Path
import hashlib
import json
import re
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(r"C:\Users\Erik\.codex\codex-remote-attachments\01a0921e-4727-7f93-8ad0-0b605c9afe96\DE2ED0F2-96FC-4A5F-8DEC-84B34B02566F\1-PROMPT_CODEX_DEE_R12_AUDITADO.docx")
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def seconds(text):
    a, b = map(int, text.split(":"))
    return 60 * a + b


def main():
    with zipfile.ZipFile(SOURCE) as z:
        xml = ET.fromstring(z.read("word/document.xml"))
        paragraphs = ["".join(t.text or "" for t in p.findall(".//w:t", NS)) for p in xml.findall(".//w:body/w:p", NS)]
        embedded = [n for n in z.namelist() if n.startswith("word/embeddings/")]
        rels = z.read("word/_rels/document.xml.rels")
    scene_pattern = re.compile(r"GUION LITERAL / (S\d\d)$")
    shot_pattern = re.compile(r"(S\d\d)\.(\d)\s*/\s*(\d\d:\d\d)\s*-\s*(\d\d:\d\d)$")
    scenes = []
    for i, line in enumerate(paragraphs):
        match = scene_pattern.fullmatch(line)
        if not match:
            continue
        scene_id = match.group(1)
        window = re.match(r"(\d\d:\d\d)\s*-\s*(\d\d:\d\d)\s*\|\s*(\d+) s", paragraphs[i + 2])
        assert window, paragraphs[i + 2]
        start, end = seconds(window[1]), seconds(window[2])
        scene = {"scene_id": scene_id, "title": paragraphs[i + 1], "start_s": start, "end_s": end,
                 "duration_s": end - start, "capacity_exact": paragraphs[i + 3], "source_paragraph_1based": i + 1,
                 "shots": []}
        j = i + 4
        while j < len(paragraphs) and not scene_pattern.fullmatch(paragraphs[j]):
            sm = shot_pattern.fullmatch(paragraphs[j])
            if sm and sm[1] == scene_id:
                p = paragraphs[j:j + 7]
                assert p[2].startswith("Orientar: ") and p[3].startswith("Mostrar: ") and p[4].startswith("Leer: ")
                assert p[5].startswith("Rótulos: ") and p[6].startswith("Rechazar si: ")
                shot = {"shot_id": f"{scene_id}_P{int(sm[2]):02d}", "original_shot_id": f"{scene_id}.{sm[2]}",
                        "start_s": seconds(sm[3]), "end_s": seconds(sm[4]), "anchor_exact": p[1],
                        "anchor_source_paragraph_1based": j + 2, "labels_exact": p[5][9:],
                        "phases_exact": {"orientar": p[2][10:], "mostrar": p[3][9:], "leer": p[4][6:]},
                        "rejection_exact": p[6][13:], "keyframes_required": ["K0", "K1", "K2", "K3"],
                        "keyframe_binding_status": "Pending actual source and actual audio timing; no physical tick or arbitrary fixed phase fractions inferred.",
                        "evidence_bindings": [], "explicit_silence": False}
                shot["duration_s"] = shot["end_s"] - shot["start_s"]
                shot["word_count_orthographic"] = len(shot["anchor_exact"].split())
                shot["design_words_per_minute"] = round(60 * shot["word_count_orthographic"] / shot["duration_s"], 3)
                shot["anchor_sha256_utf8"] = sha(shot["anchor_exact"].encode())
                scene["shots"].append(shot)
                j += 7
                continue
            if paragraphs[j].startswith("Fuentes que se contrastan: "):
                scene["source_contract_exact"] = paragraphs[j][27:]
                break
            j += 1
        assert len(scene["shots"]) == 3, scene_id
        scene["literal"] = " ".join(s["anchor_exact"] for s in scene["shots"])
        scene["literal_sha256_utf8"] = sha(scene["literal"].encode())
        assert scene["shots"][0]["start_s"] == start and scene["shots"][-1]["end_s"] == end
        assert all(a["end_s"] == b["start_s"] for a, b in zip(scene["shots"], scene["shots"][1:]))
        scenes.append(scene)
    assert len(scenes) == 14 and sum(len(s["shots"]) for s in scenes) == 42
    assert scenes[0]["start_s"] == 0 and scenes[-1]["end_s"] == 390
    assert all(a["end_s"] == b["start_s"] for a, b in zip(scenes, scenes[1:]))
    words = sum(s["word_count_orthographic"] for c in scenes for s in c["shots"])
    out = ROOT / "guion_fuente"
    out.mkdir(parents=True, exist_ok=True)
    literal = "\n\n".join(c["literal"] for c in scenes) + "\n"
    (out / "LOCUCION_R12_LITERAL.txt").write_text(literal, encoding="utf-8")
    for scene in scenes:
        (out / f"{scene['scene_id']}_LOCUCION_LITERAL.txt").write_text(scene["literal"] + "\n", encoding="utf-8")
    data = {"schema": "DEE.R12.DERIVED_DOCX_LITERAL.R01", "not_original_specification": True,
            "original_ESPECIFICACION_R12_json": "Not supplied in this DOCX or its relationships; root directed search has not recovered it. This extracted derivative is explicitly separate.",
            "source": {"path": str(SOURCE), "sha256": sha(SOURCE.read_bytes()), "paragraphs": len(paragraphs),
                       "tables": len(xml.findall(".//w:tbl", NS)), "embeddings": embedded,
                       "relationships_sha256": sha(rels), "read_coverage": "All591body paragraphs and3tables read substantively via OOXML stdout in six blocks."},
            "total_duration_s": 390, "fps": 30, "frame_count": 11700, "scene_count": 14, "shot_count": 42,
            "word_count_orthographic": words, "maximum_design_wpm": max(s["design_words_per_minute"] for c in scenes for s in c["shots"]),
            "master_text_path": "LOCUCION_R12_LITERAL.txt", "master_sha256": sha(literal.encode()),
            "global_contracts_exact": {str(i): paragraphs[i-1] for i in [6,7,8,58,59,60,61,62,63,79,80,81,82,83,84,88,89,90,91,98,100,104,106,107,115,116]},
            "keyframe_contract": "42shots×K0/K1/K2/K3 required from real evidence; three literal phases are kept. Original JSON and six motion-reference clips absent; no substitute is represented as original.",
            "scenes": scenes}
    path = out / "SHOTLIST_R12_DERIVADO_DEL_DOCX.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(path), "bytes": path.stat().st_size, "sha256": sha(path.read_bytes()),
                      "scenes": len(scenes), "shots": 42, "words": words, "max_design_wpm": data["maximum_design_wpm"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
