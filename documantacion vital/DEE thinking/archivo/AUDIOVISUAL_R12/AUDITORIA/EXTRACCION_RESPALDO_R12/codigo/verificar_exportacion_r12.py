"""Offline integrity of the R04 media-sidecar export, not a video/science verdict."""
from pathlib import Path
import datetime as dt
import gzip
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]


def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")
def digest(x):return hashlib.sha256(canonical(x)).hexdigest()
def file_hash(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def points(m):return [{"N":p.get("N"),"tick":p.get("tick"),"points":p.get("points",[])} for p in m.get("panels",[])]


def main():
    paths=[ROOT/"MANIFIESTO_EJECUCION_R12.json",ROOT/"AFIRMACIONES_VERIFICADAS.json",ROOT/"PROYECTO_EDITABLE/MODELOS_POR_INTERVALO_R12.json.gz",
        ROOT/"AUDITORIA/COMPARACION_EDITORIAL_EXPORTACIONES_R02_R04.json",ROOT/"codigo/exportar_manifestos_r12.py"]
    manifest,claims=map(load,paths[:2]);models=json.loads(gzip.decompress(paths[2].read_bytes()));comparison=load(paths[3])
    prior=json.loads(gzip.decompress((ROOT/"AUDITORIA/EXPORTACION_R02/MODELOS_POR_INTERVALO_R12.json.gz").read_bytes()))
    assert manifest["schema"].endswith("R04") and claims["schema"].endswith("R04")
    assert manifest["export_code_sha256"]==file_hash(paths[4])
    assert manifest["editable_models"]["sha256"]==file_hash(paths[2])
    assert manifest["editorial_R02_R04_comparison"]["sha256"]==file_hash(paths[3])
    assert all(digest(m)==mid for mid,m in models["models"].items())
    intervals=models["intervals"];assert intervals[0]["start_frame"]==0 and intervals[-1]["end_frame_exclusive"]==11700
    assert all(a["end_frame_exclusive"]==b["start_frame"] for a,b in zip(intervals,intervals[1:]))
    assert all(x["model_id"] in models["models"] and x["start_frame"]<x["end_frame_exclusive"] for x in intervals)
    assert len(manifest["shots"])==len(claims["claims"])==42
    assert len({s["scene_id"] for s in manifest["shots"]})==14
    literal=load(ROOT/"guion_fuente/SHOTLIST_R12_DERIVADO_DEL_DOCX.json")
    anchors={s["original_shot_id"]:s["anchor_exact"] for c in literal["scenes"] for s in c["shots"]}
    for shot,claim in zip(manifest["shots"],claims["claims"]):
        assert shot["shot_id"]==claim["shot_id"] and shot["literal_anchor"]==claim["frase_literal"]==anchors[shot["shot_id"]]
        assert shot["life_or_branch_list_is_partial"] and claim["lista_vidas_conocidas_no_exhaustiva"]
        assert shot["attribution_by_binding"]==claim["atribucion_por_binding"]
        assert len(shot["three_phases_and_four_voice_bound_keyframes"]["phases"])==3
        assert len(shot["three_phases_and_four_voice_bound_keyframes"]["keyframes_voice_bound"])==4
    assert manifest["source_hashes_before"]==manifest["source_hashes_after"]==models["source_hashes_before"]==models["source_hashes_after"]
    source_checks=[]
    for name,h in manifest["source_hashes_after"].items():
        p=ROOT/name
        if not p.is_file():p=ROOT/"codigo"/name
        actual=file_hash(p);assert actual==h,"Frozen source changed after export: "+name
        source_checks.append({"path":str(p.relative_to(ROOT)),"sha256":actual})
    old_i=new_i=0;outside=selected=0;selected_ids=set()
    for frame in range(11700):
        while intervals[new_i]["end_frame_exclusive"]<=frame:new_i+=1
        while prior["intervals"][old_i]["end_frame_exclusive"]<=frame:old_i+=1
        new=models["models"][intervals[new_i]["model_id"]];old=prior["models"][prior["intervals"][old_i]["model_id"]]
        if new["shot_id"]=="S12.1":selected+=1;selected_ids.add(intervals[new_i]["model_id"])
        else:assert canonical(points(new))==canonical(points(old));outside+=1
    selection=comparison["S12_1_source_selection"]
    assert set(selection["selected_models_verified_to_exact_SHA_checked_primaries"])==selected_ids
    assert selected==selection["frames_checked"] and selection["all_selected_points_match"]
    for checks in selection["selected_models_verified_to_exact_SHA_checked_primaries"].values():
        for c in checks:
            assert c["tick"] in {121681,124809,125496} and c["N"]==26 and c["actual_file_sha_verified"]
    assert not comparison["physical_differences"] and not comparison["authentic_evidence_binding_differences"] and not comparison["unexpected_nonannotation_changes"]
    # The selected U0 temporal footer must describe the matching observed stage.
    footer_checks=[]
    for m in models["models"].values():
        if m["shot_id"]!="S05.1":continue
        ticks={p["tick"] for p in m.get("panels",[])};footer=m.get("footer","")
        if 338 in ticks:assert footer=="Antes de la revisión"
        elif ticks&{402,405}:assert footer=="Experiencia de revisión"
        elif 472 in ticks:assert footer=="Consulta posterior"
        else:raise AssertionError("Unexpected S05.1 temporal cut")
        footer_checks.append({"ticks":sorted(ticks),"footer":footer})
    report={"schema":"DEE.R12.final_export_integrity.LOCAL.R04","created_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "completed":True,"new_Native_ticks":0,"rendered_frames":0,"video_or_listening_verdict":"NOT_ASSESSED_BY_THIS_TOOL",
        "frames_checked":11700,"unchanged_physical_frames_outside_S12_1":outside,"S12_1_frames_selecting_verified_archived_cuts":selected,
        "models":len(models["models"]),"intervals":len(intervals),"scenes":14,"shots":42,"literal_anchors":42,"phases":126,"voice_keyframes":168,
        "unknown_attribution_retained_per_binding":True,"selected_S05_1_temporal_footers":footer_checks,"frozen_source_files_verified":source_checks,
        "files":[{"path":str(p.relative_to(ROOT)),"bytes":p.stat().st_size,"sha256":file_hash(p)} for p in paths],
        "verifier_code_sha256":file_hash(Path(__file__)),"limitations":["Local media cards only; not full causal states or a continuable DEE life.","Original R12 package/toolkit unavailable: NO EVALUADO.","No video perception, human listening, ASR or general cognitive verdict."]}
    p=ROOT/"AUDITORIA/EXPORTACION_FINAL_R04.json"
    with p.open("x",encoding="utf-8",newline="\n") as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write("\n")
    print(json.dumps({"path":str(p),"bytes":p.stat().st_size,"sha256":file_hash(p),"completed":True,"outside_S12_1":outside,"S12_1":selected},ensure_ascii=False))


if __name__=="__main__":main()
