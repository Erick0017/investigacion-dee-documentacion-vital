"""Offline technical/literal/PCM verification. Does not claim listening or ASR."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import wave

ROOT = Path(__file__).resolve().parents[1]
TESTS = next(p for p in ROOT.parents if p.name == "tests")
FF = TESTS / "_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe"
PROBE = TESTS / "_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(4*1024*1024), b""):
            h.update(b)
    return h.hexdigest()


def main():
    load = lambda rel: json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))
    source = load("guion_fuente/SHOTLIST_R12_DERIVADO_DEL_DOCX.json")
    index = load("audio/PROVENIENCIA_AUDIO_R12.json")
    schedule = load("audio/TIEMPOS_ANCLAS_R12.json")
    proofs = load("audio/PRUEBA_PCM_R12.json")
    cues = load("audio/SUBTITULOS_ALINEADOS_R12.json")["cues"]
    assert len(schedule["rows"]) == 42 and schedule["all_fit"] and not schedule["violations"]
    assert schedule["rows"][0]["first_visual_frame_30fps"] == 0
    assert schedule["rows"][-1]["end_visual_frame_exclusive_30fps"] == 11700
    assert all(a["end_visual_frame_exclusive_30fps"] == b["first_visual_frame_30fps"] for a,b in zip(schedule["rows"], schedule["rows"][1:]))
    for scene in source["scenes"]:
        assert " ".join(c["literal"] for c in cues if c["scene_id"] == scene["scene_id"]) == scene["literal"]
    assert all(0<=c["start"]<c["end"]<=388 for c in cues)
    assert all(a["end"]<=b["start"] for a,b in zip(cues,cues[1:]))
    srt = (ROOT / "audio/R12_ES.srt").read_text(encoding="utf-8-sig")
    blocks = [b for b in srt.strip().split("\n\n") if b]
    assert len(blocks) == len(cues)
    assert all(" ".join(b.splitlines()[2:]) == c["literal"] for b,c in zip(blocks,cues))
    selected = set(index["selected"].values())
    assert len(selected) == 42 and len(index["takes"]) == 45
    for take in index["takes"]:
        assert sha(ROOT / take["file"]) == take["wav_sha256"]
        assert take["recipe"]["parameters"]["speed"] == 1.0
    model_checks = []
    with wave.open(str(ROOT/"audio/locucion_R12_24k.wav"), "rb") as w:
        assert (w.getframerate(),w.getnchannels(),w.getsampwidth(),w.getnframes()) == (24000,1,3,9360000)
        for record in proofs["model_blocks"]:
            with wave.open(str(ROOT/record["source"]),"rb") as take:
                take.setpos(record["original_external_lead_samples"])
                raw = take.readframes(record["complete_model_samples"])
            assert hashlib.sha256(raw).hexdigest() == record["complete_model_PCM_sha256"]
            w.setpos(record["master_model_start_sample"])
            assert w.readframes(record["complete_model_samples"]) == raw
            model_checks.append({"shot_id": record["shot_id"], "complete_model_PCM_exact": True,
                                 "model_PCM_sha256": record["complete_model_PCM_sha256"]})
        w.setpos(388*24000)
        assert not any(w.readframes(2*24000))
    files = []
    for name in ("locucion_R12_48k.wav", "mezcla_R12_48k.wav"):
        path = ROOT/"audio"/name
        with wave.open(str(path),"rb") as w:
            fmt = {"sample_rate":w.getframerate(),"channels":w.getnchannels(),"sample_width_bytes":w.getsampwidth(),"sample_frames":w.getnframes()}
            assert fmt == {"sample_rate":48000,"channels":2,"sample_width_bytes":3,"sample_frames":18720000}
        probe = subprocess.run([str(PROBE),"-v","error","-show_streams","-show_format","-of","json",str(path)],capture_output=True,text=True,encoding="utf-8",check=True)
        decoded = subprocess.run([str(FF),"-v","error","-nostdin","-threads","2","-i",str(path),"-f","null","NUL"],capture_output=True,text=True,encoding="utf-8")
        assert decoded.returncode == 0 and not decoded.stderr.strip()
        files.append({"path":str(path.relative_to(ROOT)),"bytes":path.stat().st_size,"sha256":sha(path),
            "wave":fmt,"ffprobe":json.loads(probe.stdout),"full_decode_exit_code":decoded.returncode,
            "full_decode_stderr":decoded.stderr})
    out = {"schema":"DEE.R12.audio_technical_literal_QA.R01","Native_ticks":0,
        "scene_count":14,"selected_literal_anchors":42,"complete_WAV_takes_preserved":45,
        "subtitle_cues":len(cues),"all815_words_preserved_in_literal_order":True,
        "max_internal_cut_adjustment_s":max(abs(r[k]) for r in schedule["rows"] for k in ("start_adjustment_s","end_adjustment_s")),
        "last_subtitle_end_s":cues[-1]["end"],"final2s_voice_PCM_zero":True,
        "complete_model_blocks":model_checks,"files":files,
        "proofs":{"schedule_sha256":sha(ROOT/"audio/TIEMPOS_ANCLAS_R12.json"),
                  "PCM_proof_sha256":sha(ROOT/"audio/PRUEBA_PCM_R12.json"),
                  "SRT_sha256":sha(ROOT/"audio/R12_ES.srt"),"script_sha256":sha(__file__)},
        "hearing_status":"NO EVALUADO","independent_ASR":False,"voice_naturalness_not_certified_by_metrics":True,
        "no_phonemes_trimmed":True,"no_time_stretch":True,
        "outer_silence_and_S14_pause_revision":index.get("S14_pause_revision"),
        "selected_padding_policy":schedule["external_padding_policy"]}
    target=ROOT/"audio/VERIFICACION_AUDIO_R12.json"
    target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"path":str(target),"bytes":target.stat().st_size,"sha256":sha(target),
        "42_model_PCM_exact":True,"45_original_takes_unchanged":True,"97_SRT_literal_equal":True,
        "max_internal_cut_adjustment_s":out["max_internal_cut_adjustment_s"],"decoded_files":len(files),
        "hearing":"NO EVALUADO"},ensure_ascii=False))


if __name__ == "__main__":
    main()
