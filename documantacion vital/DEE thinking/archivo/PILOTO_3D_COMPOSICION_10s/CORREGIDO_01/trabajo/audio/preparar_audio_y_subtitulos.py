"""Reuse the closed continuous mix; exact English subtitles within150ms of voice."""
from pathlib import Path
import datetime as dt
import hashlib
import importlib.util
import json
import wave

ROOT=Path(__file__).resolve().parents[2]
ORIGINAL=ROOT.parent
OUT=ROOT/"trabajo/audio"
ES=["En composición, dos contribuciones formaron un producto común.","Ese producto se utilizó en otra interacción del mismo mundo."]
EN=["In composition, two contributions\nformed a common product.","That product was used in another\ninteraction within the same world."]


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def save(p,x):
    with p.open("x",encoding="utf-8",newline="\n") as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write("\n")


def main():
    source=ORIGINAL/"trabajo/audio/mezcla_tiempo_visual_10s.wav"
    prior=ORIGINAL/"trabajo/audio/AJUSTE_VISUAL_AUDIO_R02.json"
    adjusted=load(prior)
    assert sha(source)==adjusted["sha256"]=="563b2a2a434ecbdb55c3847857a9db656184a9f73ea21a13bcd09bbfe510e17a"
    synthesis=load(ORIGINAL/"trabajo/audio/MEDICION_TOMA_COMPLETA_R01.json")
    assert synthesis["literal_sentences"]==ES and synthesis["take"]["es"]==" ".join(ES)
    assert synthesis["speed"]==1.0
    marks=synthesis["take"]["sentences"]
    assert all(m["method"]=="exact_full_sentence_phonemes" for m in marks)
    # The preserved source take used350ms lead; its first assembly used150ms;
    # the supplied closed R02 mix shifts that entire uninterrupted voice +920ms.
    offset=-.2+.92
    physical_voice=[{"literal_ES":m["text"],"start_s":round(m["start"]+offset,3),"end_s":round(m["end"]+offset,3),
        "alignment":"exact_full_sentence_phonemes from the selected existing model take, translated as one complete narration"} for m in marks]
    assert [[m["start_s"],m["end_s"]] for m in physical_voice]==adjusted["voice_phonemes_s"]==[[1.07,5.1],[5.15,8.55]]
    with wave.open(str(source),"rb") as f:
        params=f.getparams();pcm=f.readframes(f.getnframes());extra=f.readframes(1)
    assert (params.nchannels,params.sampwidth,params.framerate,params.nframes,params.comptype)==(2,3,48000,480000,"NONE")
    assert len(pcm)==2880000 and not extra
    destination=OUT/"mezcla_tiempo_visual_10s.wav"
    with destination.open("xb") as f:f.write(source.read_bytes())
    assert sha(destination)==sha(source)
    cues=[{"index":1,"start_s":1.07,"end_s":5.1,"EN_lines":EN[0].splitlines()},
        {"index":2,"start_s":5.15,"end_s":8.65,"EN_lines":EN[1].splitlines()}]
    for cue,voice in zip(cues,physical_voice):
        assert abs(cue["start_s"]-voice["start_s"])<=.15
        assert abs(cue["end_s"]-voice["end_s"])<=.15
        cue["start_error_vs_model_s"]=round(cue["start_s"]-voice["start_s"],3)
        cue["end_hold_after_model_s"]=round(cue["end_s"]-voice["end_s"],3)
        assert len(cue["EN_lines"])==2
    text=("1\n00:00:01,070 --> 00:00:05,100\n"+EN[0]+"\n\n"
        "2\n00:00:05,150 --> 00:00:08,650\n"+EN[1]+"\n\n")
    srt=ROOT/"DEE_PILOTO_3D_COMPOSICION_10s_EN.srt"
    with srt.open("x",encoding="utf-8",newline="\n") as f:f.write(text)
    available={name:importlib.util.find_spec(name) is not None for name in ("whisper","faster_whisper","vosk","speech_recognition")}
    report={"schema":"DEE.pilot10.corrected_subtitle_alignment.R01","created_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "new_DEE_ticks":0,"new_TTS_inference":False,"new_models_downloaded":False,"literal_ES":ES,"literal_EN":[" ".join(s.splitlines()) for s in EN],
        "continuous_narration":{"voice":"em_alex","speed":1.0,"complete_model_block_duration_s":7.6,"model_block_in_corrected_mix_s":[1.07,8.67],
            "entire_narration_shift_seconds":.92,"no_internal_segmentation":True,"no_time_stretch":True,
            "verification_scope":"Original synthesis records and supplied closed R02 adjustment provenance; the exact supplied mix is copied byte for byte. No independent ASR or inferred acoustic word timing."},
        "voice_timing_from_actual_model_phonemes":physical_voice,"English_subtitle_cues":cues,"tolerance_seconds":.15,"all_cues_within_tolerance":True,
        "audio":{"path":str(destination.relative_to(ROOT)),"bytes":destination.stat().st_size,"sha256":sha(destination),"sample_rate":48000,"channels":2,"PCM_bits":24,
            "sample_frames":480000,"duration_seconds":10,"all_PCM_bytes_read":len(pcm),"complete_PCM_sha256":hashlib.sha256(pcm).hexdigest(),"copy_byte_identical":True},
        "source_audio":{"path":str(source),"sha256":sha(source),"unchanged":True},
        "source_provenance":[{"path":str(p),"sha256":sha(p)} for p in (prior,ORIGINAL/"trabajo/audio/MEDICION_TOMA_COMPLETA_R01.json",ORIGINAL/"trabajo/audio/PROVENIENCIA_AUDIO_PILOTO.json")],
        "subtitles":{"path":str(srt.relative_to(ROOT)),"sha256":sha(srt),"cue_count":2,"max_lines_per_cue":2,"text_unchanged":True,
            "revision_scope":"Only a new SRT is created for CORREGIDO_01; original pilot SRT/audio remain untouched. The second subtitle ends100ms after the measured model phrase."},
        "ASR_library_presence_in_bundled_environment":available,"independent_ASR_performed":False,"human_listening_performed":False,
        "perceptual_verdict":"NO EVALUADO: model timing and valid PCM do not certify human intelligibility or naturalness; no available listening tool or preconfigured ASR model was invoked.",
        "scope":"Audiovisual synchronization only, not DEE dynamics, memory, Native replay, or a scientific claim.","code_sha256":sha(__file__)}
    output=OUT/"AUDIO_Y_SRT_CORREGIDO_01.json";save(output,report)
    print(json.dumps({"audio":str(destination),"audio_sha256":sha(destination),"srt":str(srt),"srt_sha256":sha(srt),"metadata":str(output),"metadata_sha256":sha(output),"duration":10,"cue_tolerance_ok":True,"ASR_available":available},ensure_ascii=False))


if __name__=="__main__":main()
