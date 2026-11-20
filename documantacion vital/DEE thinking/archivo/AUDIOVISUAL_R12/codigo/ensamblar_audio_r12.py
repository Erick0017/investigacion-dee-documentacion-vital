"""R12 exact-model PCM assembly with shorter externally-added zero margins.

All complete TTS WAVs remain intact. Only the known all-zero padding added by
the apparatus is replaced; not one sample of the emitted model block is cut.
"""
from pathlib import Path
import copy
import csv
import hashlib
import json
import sys
import textwrap
import wave

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "codigo"))
import audio_r12 as base

SR = 24000
LEAD = 1200   #0.05s, externally prepared silence only
TAIL = 1200   #0.05s, externally prepared silence only


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    data = base.source()
    index = ROOT / "audio/PROVENIENCIA_AUDIO_R12.json"
    p = json.loads(index.read_text(encoding="utf-8"))
    selected = {k: next(r for r in p["takes"] if r["id"] == v) for k, v in p["selected"].items()}
    assert len(selected) == 42
    new = copy.deepcopy(selected)
    cores = {}
    proof = []
    for sid, row in new.items():
        lead, tail = (480, 720) if sid.startswith("S14_") else (LEAD, TAIL)
        src = ROOT / row["file"]
        assert sha(src) == row["wav_sha256"]
        with wave.open(str(src), "rb") as w:
            assert (w.getframerate(), w.getnchannels(), w.getsampwidth()) == (SR, 1, 3)
            raw = w.readframes(w.getnframes())
        a = row["leading_margin_samples"]
        n = row["model_samples"]
        b = row["trailing_margin_samples"]
        assert len(raw) == (a+n+b)*3
        assert not any(raw[:a*3]) and not any(raw[(a+n)*3:])
        core = raw[a*3:(a+n)*3]
        assert len(core) == n*3
        cores[sid] = core
        shift = (lead-a)/SR
        row["total_samples"] = lead+n+tail
        row["duration"] = row["total_samples"]/SR
        row["leading_margin_samples"] = lead
        row["trailing_margin_samples"] = tail
        for cue in row["subtitle_chunks"]:
            assert cue["start"] is not None and cue["end"] is not None
            cue["start"] += shift
            cue["end"] += shift
            assert 0 <= cue["start"] < cue["end"] <= row["duration"]
        proof.append({"shot_id": sid, "source": row["file"], "source_WAV_sha256": row["wav_sha256"],
            "original_external_lead_samples": a, "original_external_tail_samples": b,
            "original_external_margins_verified_zero": True,
            "complete_model_samples": n, "complete_model_PCM_sha256": hashlib.sha256(core).hexdigest(),
            "new_external_lead_samples": lead, "new_external_tail_samples": tail,
            "new_prepared_duration_s": row["duration"], "no_model_samples_removed": True,
            "no_time_stretch": True})
    schedule = base.plan_schedule(data, new)
    schedule["external_padding_policy"] = {"leading_s": LEAD/SR, "trailing_s": TAIL/SR,
        "S14_override": {"leading_s": 0.02, "trailing_s": 0.03,
            "reason": "The full intrinsic-pause S14 model blocks plus2s final reading fit only with shorter external zero margins."},
        "scope": "Replace only verified all-zero padding added by the apparatus. Original complete WAVs and complete model PCM preserved.",
        "no_model_trim": True, "speed": 1.0, "last_2_seconds_reading_reserve": True}
    exported_schedule = copy.deepcopy(schedule)
    literal_ids = {s["shot_id"]: s["original_shot_id"] for c in data["scenes"] for s in c["shots"]}
    for row in exported_schedule["rows"]:
        row["shot_id_internal"] = row["shot_id"]
        row["shot_id"] = literal_ids[row["shot_id"]]
    exported_schedule["identifier_contract"] = "shot_id preserves supplied DOCX notation S01.1; shot_id_internal links the immutable S01_P01 take IDs."
    base.atomic_json(ROOT / "audio/TIEMPOS_ANCLAS_R12.json", exported_schedule)
    if not schedule["all_fit"]:
        base.atomic_json(ROOT / "audio/FACTIBILIDAD_AUDIO_R12.json", {"all_fit": False, "schedule": schedule,
            "takes_preserved": True, "no_speed_change_or_phoneme_trim": True})
        raise RuntimeError("Complete model blocks do not fit fixed scene windows; see FACTIBILIDAD")
    output = ROOT / "audio/locucion_R12_24k.wav"
    if output.exists():
        raise FileExistsError("Preserve existing master")
    pcm = bytearray(390*SR*3)
    captions = []
    for sh in schedule["rows"]:
        sid = sh["shot_id"];row=new[sid]
        start = sh["start_sample_24k"]+row["leading_margin_samples"]
        core = cores[sid]
        end = start+row["model_samples"]
        assert end+row["trailing_margin_samples"] <= sh["end_sample_24k"]
        assert not any(pcm[start*3:end*3])
        pcm[start*3:end*3] = core
        r = next(x for x in proof if x["shot_id"] == sid)
        r.update(master_model_start_sample=start, master_model_end_sample_exclusive=end,
            master_model_PCM_sha256=hashlib.sha256(pcm[start*3:end*3]).hexdigest(),
            exact_model_PCM_in_master=pcm[start*3:end*3] == core)
        for i,cue in enumerate(row["subtitle_chunks"]):
            next_start = row["subtitle_chunks"][i+1]["start"] if i+1<len(row["subtitle_chunks"]) else row["duration"]
            endcue = min(cue["end"]+.12, next_start-.02, row["duration"])
            assert endcue > cue["start"]
            wrapped=textwrap.wrap(cue["literal"],width=43,break_long_words=False,break_on_hyphens=False)
            assert len(wrapped)<=2
            captions.append({"scene_id":sh["scene_id"],"shot_id":literal_ids[sid],"shot_id_internal":sid,
                "start":sh["actual_start_s"]+cue["start"],"end":sh["actual_start_s"]+endcue,
                "literal":cue["literal"],"text":"\n".join(wrapped),"alignment":cue["method"],
                "phoneme_index":cue["model_phoneme_first_index"]})
    for scene in data["scenes"]:
        assert " ".join(c["literal"] for c in captions if c["scene_id"]==scene["scene_id"])==scene["literal"]
    assert all(0<=c["start"]<c["end"]<=388 for c in captions)
    assert all(a["end"]<=b["start"] for a,b in zip(captions,captions[1:]))
    assert not any(pcm[388*SR*3:])
    with wave.open(str(output),"wb") as w:
        w.setnchannels(1);w.setsampwidth(3);w.setframerate(SR);w.writeframes(pcm)
    with wave.open(str(output),"rb") as w:
        assert w.getnframes()==390*SR
        for row in proof:
            w.setpos(row["master_model_start_sample"])
            assert hashlib.sha256(w.readframes(row["complete_model_samples"])).hexdigest()==row["complete_model_PCM_sha256"]
    srt=ROOT/"audio/R12_ES.srt"
    srt.write_text("\n\n".join(str(i)+"\n"+base.timecode(c["start"])+" --> "+base.timecode(c["end"])+"\n"+c["text"] for i,c in enumerate(captions,1))+"\n",encoding="utf-8-sig")
    base.atomic_json(ROOT/"audio/SUBTITULOS_ALINEADOS_R12.json",{"model_timing_not_ASR":True,"cues":captions})
    base.atomic_json(ROOT/"audio/PRUEBA_PCM_R12.json",{"model_blocks":proof,"all_42_exact":all(x["exact_model_PCM_in_master"] for x in proof),
        "source_takes_unchanged":True,"no_time_stretch":True,"no_model_trim":True,
        "source_synthesis_code_sha256":p["audio_r12_source_sha256"],"assembly_code_sha256":sha(__file__),
        "raw_PCM_model_hashes_are_not_WAV_file_hashes":True,"human_listening":False,"independent_ASR":False})
    table=[]
    for sc in data["scenes"]:
        ss=[x for x in schedule["rows"] if x["scene_id"]==sc["scene_id"]]
        table.append({"scene":sc["scene_id"],"fixed_window_s":sc["duration_s"],
            "full_model_blocks_s":sum(selected[x["shot_id"]]["model_samples"] for x in ss)/SR,
            "prepared_external_silence_s":sum(new[x["shot_id"]]["leading_margin_samples"]+new[x["shot_id"]]["trailing_margin_samples"] for x in ss)/SR,
            "additional_free_window_s":sc["duration_s"]-sum(new[x["shot_id"]]["total_samples"] for x in ss)/SR})
    base.atomic_json(ROOT/"audio/FACTIBILIDAD_AUDIO_R12.json",{"all_fit":True,"scene_count":14,"anchor_count":42,
        "speed":1.0,"no_time_stretch":True,"no_model_trim":True,"models_and_original_WAVs_preserved":True,
        "outer_padding_policy":schedule["external_padding_policy"],"scenes":table,
        "adjustments":[{"shot_id":x["shot_id"],"start":x["start_adjustment_s"],"end":x["end_adjustment_s"]} for x in schedule["rows"] if x["start_adjustment_s"] or x["end_adjustment_s"]]})
    p["assembly"]={"duration_s":390,"samples_24k":390*SR,"caption_count":len(captions),
        "each_complete_model_PCM_exact_in_master":True,"original_complete_WAVs_preserved":True,
        "externally_added_zero_padding_replaced":True,"no_time_stretch":True,"no_model_trim":True,
        "schedule_sha256":sha(ROOT/"audio/TIEMPOS_ANCLAS_R12.json"),
        "files":{str(f.relative_to(ROOT)):{"sha256":sha(f),"bytes":f.stat().st_size} for f in(output,srt)},
        "source_sha256":sha(__file__),"human_listening":False,"independent_ASR":False}
    base.atomic_json(index,p)
    print(json.dumps({"all_fit":True,"scenes":14,"anchors":42,"cues":len(captions),"last_caption_end":captions[-1]["end"],
        "samples24k":390*SR,"duration_s":390,"master_sha256":sha(output),"schedule_sha256":sha(ROOT/"audio/TIEMPOS_ANCLAS_R12.json"),"no_Native":True},ensure_ascii=False))


if __name__ == "__main__":
    main()
