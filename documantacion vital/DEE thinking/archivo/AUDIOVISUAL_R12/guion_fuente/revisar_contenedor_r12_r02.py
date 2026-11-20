"""Repair our Windows CRLF/file-SHA mismatch without changing a literal word."""
from pathlib import Path
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    folder=ROOT/"guion_fuente"
    jp=folder/"SHOTLIST_R12_DERIVADO_DEL_DOCX.json"
    tp=folder/"LOCUCION_R12_LITERAL.txt"
    original_json=jp.read_bytes();original_text=tp.read_bytes()
    j=json.loads(original_json)
    expected=("\n\n".join(c["literal"] for c in j["scenes"])+"\n").encode("utf-8")
    assert original_text.replace(b"\r\n",b"\n")==expected
    assert original_text.split()==expected.split()
    assert sha(expected)==j["master_sha256"]
    with zipfile.ZipFile(Path(j["source"]["path"])) as z:
        r=ET.fromstring(z.read("word/document.xml"))
    ns={"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    ps=["".join(x.text or "" for x in p.findall(".//w:t",ns)) for p in r.findall(".//w:body/w:p",ns)]
    voices={}
    for i,line in enumerate(ps):
        m=re.fullmatch(r"(S\d\d)\.(\d)\s*/\s*\d\d:\d\d\s*-\s*\d\d:\d\d",line)
        if m:voices[f"{m[1]}.{m[2]}"]=ps[i+1]
    flat=[s for c in j["scenes"] for s in c["shots"]]
    assert len(voices)==len(flat)==42
    assert all(voices[s["original_shot_id"]]==s["anchor_exact"] for s in flat)
    backup=folder/"revisiones/R01"
    backup.mkdir(parents=True,exist_ok=False)
    (backup/jp.name).write_bytes(original_json)
    (backup/tp.name).write_bytes(original_text)
    tp.write_bytes(expected)
    j["container_revision"]={"revision":"R02","reason":"Our extractor computed the LF text SHA before Windows write_text converted27newlines toCRLF. No word or anchor changed.",
        "newline_contract":"UTF-8, LF bytes,14scene blocks separated by one blank line, one final LF",
        "prior_JSON_path":str((backup/jp.name).relative_to(ROOT)),"prior_JSON_sha256":sha(original_json),
        "prior_TXT_path":str((backup/tp.name).relative_to(ROOT)),"prior_TXT_sha256":sha(original_text),
        "prior_bytes":len(original_text),"prior_CRLF_count":original_text.count(b"\r\n"),
        "current_bytes":len(expected),"current_file_sha256":sha(expected),
        "all42_anchors_equal_original_DOCX":True,"all815_words_unchanged":True,
        "audio_changed":False,"schedule_changed":False,"original_ESPECIFICACION_recovered":False}
    jp.write_bytes((json.dumps(j,ensure_ascii=False,indent=2)+"\n").encode("utf-8"))
    print(json.dumps({"JSON_sha256":sha(jp.read_bytes()),"TXT_sha256":sha(tp.read_bytes()),
        "previous_JSON_sha256":sha(original_json),"previous_TXT_sha256":sha(original_text),
        "only_CRLF_fixed":True,"audio_and_schedule_unchanged":True}))


if __name__=="__main__":main()
