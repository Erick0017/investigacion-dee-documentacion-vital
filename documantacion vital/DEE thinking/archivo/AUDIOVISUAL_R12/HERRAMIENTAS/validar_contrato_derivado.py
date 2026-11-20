"""Check the local DOCX-derived R12 literal/schedule, NOT the missing package.

This tool is newly written locally. It is not original validar_paquete.py and
cannot certify source science, video fidelity, listening or comprehension.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def check_contract(source_docx=None):
    path = ROOT / "guion_fuente/SHOTLIST_R12_DERIVADO_DEL_DOCX.json"
    schedule_path = ROOT / "audio/TIEMPOS_ANCLAS_R12.json"
    text_path = ROOT / "guion_fuente/LOCUCION_R12_LITERAL.txt"
    source, schedule = load(path), load(schedule_path)
    scenes, actual = source["scenes"], schedule["rows"]
    checks = []

    def check(name, ok, expected, observed):
        checks.append({"check":name,"ok":bool(ok),"expected":expected,"actual":observed})

    check("explicitly_a_derivative_NOT_original_JSON", source.get("not_original_specification") is True,
          True, source.get("not_original_specification"))
    check("14_scene_ids", [c["scene_id"] for c in scenes] == [f"S{i:02d}" for i in range(1,15)],
          "S01..S14", [c["scene_id"] for c in scenes])
    flat = [s for c in scenes for s in c["shots"]]
    expected = {s["original_shot_id"]:s for s in flat}
    check("42_unique_literal_shot_ids", len(flat)==len(expected)==42 and all(len(c["shots"])==3 for c in scenes),
          42, [len(flat),len(expected)])
    check("fixed390s_scenes_no_gaps", scenes[0]["start_s"]==0 and scenes[-1]["end_s"]==390 and
          all(a["end_s"]==b["start_s"] for a,b in zip(scenes,scenes[1:])) and
          all(c["duration_s"]==c["end_s"]-c["start_s"] for c in scenes), "0..390, contiguous", [(c["start_s"],c["end_s"]) for c in scenes])
    check("42_nominal_shots_match_parent_intervals", all(c["shots"][0]["start_s"]==c["start_s"] and c["shots"][-1]["end_s"]==c["end_s"] and
          all(a["end_s"]==b["start_s"] for a,b in zip(c["shots"],c["shots"][1:])) for c in scenes), True, "three contiguous shots per scene")
    check("literal815_words", sum(len(s["anchor_exact"].split()) for s in flat)==815, 815,
          sum(len(s["anchor_exact"].split()) for s in flat))
    check("all42_literal_SHA_values", all(hashlib.sha256(s["anchor_exact"].encode()).hexdigest()==s["anchor_sha256_utf8"] for s in flat), True, len(flat))
    check("all14_scene_literal_concatenations_SHA", all(" ".join(s["anchor_exact"] for s in c["shots"])==c["literal"] and
          hashlib.sha256(c["literal"].encode()).hexdigest()==c["literal_sha256_utf8"] for c in scenes), True, len(scenes))
    check("master_TXT_literal_and_SHA", text_path.read_text(encoding="utf-8")=="\n\n".join(c["literal"] for c in scenes)+"\n" and sha(text_path)==source["master_sha256"],
          source["master_sha256"],sha(text_path))
    check("three_literal_phases_per_shot", all(set(s["phases_exact"])=={"orientar","mostrar","leer"} and all(s["phases_exact"].values()) for s in flat), True, len(flat))
    check("K0_K1_K2_K3_required_not_fabricated", all(s["keyframes_required"]==["K0","K1","K2","K3"] and isinstance(s["evidence_bindings"],list) for s in flat),
          "four required bindings, not empirical verification", len(flat))
    check("42_actual_voice_rows_unique", len(actual)==42 and {r["shot_id"] for r in actual}==set(expected),42,len(actual))
    check("actual_voice_anchor_literal_matches", all(r["anchor_exact"]==expected[r["shot_id"]]["anchor_exact"] for r in actual),True,len(actual))
    check("actual_schedule_all_fit_no_violations",schedule.get("all_fit") is True and not schedule.get("violations"),True,[schedule.get("all_fit"),schedule.get("violations")])
    check("actual_internal_adjustments_at_most2s",all(abs(r[k])<=2 for r in actual for k in ("start_adjustment_s","end_adjustment_s")),"<=2",max(abs(r[k]) for r in actual for k in ("start_adjustment_s","end_adjustment_s")))
    check("actual_schedule_preserves_scene_boundaries",all(next(r for r in actual if r["scene_id"]==c["scene_id"])["actual_start_s"]==c["start_s"] and
          [r for r in actual if r["scene_id"]==c["scene_id"]][-1]["actual_end_s"]==c["end_s"] for c in scenes),True,len(scenes))
    check("actual11700_frame_schedule_contiguous",actual[0]["first_visual_frame_30fps"]==0 and actual[-1]["end_visual_frame_exclusive_30fps"]==11700 and
          all(a["end_visual_frame_exclusive_30fps"]==b["first_visual_frame_30fps"] for a,b in zip(actual,actual[1:])),11700,actual[-1]["end_visual_frame_exclusive_30fps"])
    document = Path(source_docx) if source_docx else Path(source["source"]["path"])
    doc_status = "NO EVALUADO: original DOCX unavailable at supplied locator"
    if document.is_file():
        check("supplied_DOCX_byte_SHA",sha(document)==source["source"]["sha256"],source["source"]["sha256"],sha(document))
        with zipfile.ZipFile(document) as z:
            root=ET.fromstring(z.read("word/document.xml"))
        ns={"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        ps=["".join(t.text or "" for t in p.findall(".//w:t",ns)) for p in root.findall(".//w:body/w:p",ns)]
        voices={}
        for i,line in enumerate(ps):
            m=re.fullmatch(r"(S\d\d)\.(\d)\s*/\s*\d\d:\d\d\s*-\s*\d\d:\d\d",line)
            if m:voices[f"{m[1]}.{m[2]}"]=ps[i+1]
        check("all42_literal_anchors_equal_supplied_DOCX",set(voices)==set(expected) and all(voices[k]==v["anchor_exact"] for k,v in expected.items()),True,len(voices))
        doc_status="BYTE_AND_LITERAL_COMPARISON_PERFORMED"
    return {"schema":"DEE.R12.LOCAL_DERIVED.contract_consistency.v1","created_utc":datetime.now(timezone.utc).isoformat(),
        "tool_origin":"New local checker of explicit DOCX derivative; NOT original R12 validar_paquete.py",
        "checks":checks,"failed_checks":[x for x in checks if not x["ok"]],
        "derived_document_consistency":"PASS" if all(x["ok"] for x in checks) else "FAIL",
        "original_R12_package_validation":"NO EVALUADO: original ESPECIFICACION_R12.json/package/validator not recovered",
        "DOCX_comparison":doc_status,"scientific_evidence":"NO EVALUADO by this tool",
        "keyframe_factual_bindings":"NO EVALUADO by this tool; required bindings are not automatically satisfied",
        "video_perception":"NO EVALUADO","voice_listening":"NO EVALUADO","audience_comprehension":"NO EVALUADO",
        "inputs":[{"path":str(p),"bytes":p.stat().st_size,"sha256":sha(p)} for p in(path,schedule_path,text_path)],
        "script_sha256":sha(__file__),"new_Native_ticks":0,"rendered_frames":0}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report",type=Path,default=Path("AUDITORIA/CONTRATO_DERIVADO_R12.json"))
    parser.add_argument("--source-docx",type=Path)
    args=parser.parse_args()
    report=args.report if args.report.is_absolute() else ROOT/args.report
    report=report.resolve()
    if ROOT not in report.parents:parser.error("Report must stay inside AUDIOVISUAL_R12")
    if report.exists():parser.error("Existing report preserved; choose a new path")
    result=check_contract(args.source_docx)
    report.parent.mkdir(parents=True,exist_ok=True)
    with report.open("x",encoding="utf-8") as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write("\n")
    print(json.dumps({"report":str(report),"sha256":sha(report),"derived_document_consistency":result["derived_document_consistency"],
        "checks":len(result["checks"]),"failed_checks":result["failed_checks"],"original_R12_package_validation":result["original_R12_package_validation"]},ensure_ascii=False))
    return 0 if not result["failed_checks"] else 1


if __name__=="__main__":
    sys.exit(main())
