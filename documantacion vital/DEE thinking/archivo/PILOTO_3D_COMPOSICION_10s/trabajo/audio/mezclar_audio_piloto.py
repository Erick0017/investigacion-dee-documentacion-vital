"""Ten-second local mix from the closed narration and approved R03 ambience."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
A=ROOT/"trabajo/audio"
VOICE=ROOT.parent/"produccion_audiovisual_DEE_Cognitive_2_0_20261028/videos/produccion_cientifica/voz"
ALIAS=Path(tempfile.gettempdir())/"dee_r03_voice_312cdd7b"
assert ALIAS.is_junction() and ALIAS.resolve()==VOICE.resolve()
sys.path.insert(0,str(ALIAS/"pydeps"))
import numpy as np
import soundfile as sf
SR=48000
TOTAL=480000


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def save(p,x):
    with p.open("x",encoding="utf-8",newline="\n") as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write("\n")
def wav(p,data):
    with p.open("xb") as f:sf.write(f,data,SR,subtype="PCM_24",format="WAV")
def read(p):
    with p.open("rb") as f:x,sr=sf.read(f,dtype="float64",always_2d=True)
    assert sr==SR
    return x
def rms_db(x):return 20*math.log10(max(1e-12,float(np.sqrt(np.mean(x*x)))))
def metrics(x):return {"sample_frames":len(x),"channels":x.shape[1],"rms_dBFS":rms_db(x),"peak_dBFS":20*math.log10(max(1e-12,float(np.max(np.abs(x))))),"samples_at_or_above_full_scale":int(np.count_nonzero(abs(x)>=1))}


def main():
    assert not (A/"MEZCLA_AUDIO_10s_R01.json").exists(),"Preserve a prior mix revision; no silent overwrite"
    ref=load(ROOT/"trabajo/referencia_R05/REFERENCIA_R05_Y_RENDERER.json")
    music_source=Path(ref["music"]["path"])
    assert sha(music_source)==ref["music"]["sha256"]
    narration=A/"locucion_10s_48k.wav";before_voice=sha(narration)
    assert before_voice=="97e1fe32955cc451f676111e9c997af0c7ee3fe8aadf0807a2206f7b1bfac5c4"
    voice=read(narration);assert voice.shape==(TOTAL,2)
    with music_source.open("rb") as f:
        with sf.SoundFile(f) as source:
            assert source.samplerate==SR and source.channels==2
            source.seek(100*SR);music=source.read(TOTAL,dtype="float64",always_2d=True)
    assert music.shape==(TOTAL,2)
    # One continuous source segment, no restart between the four visual phases.
    t=np.arange(TOTAL)/SR
    envelope=np.minimum(np.clip(t/.5,0,1),np.clip((10-t)/.8,0,1))
    music*=envelope[:,None]
    music_faded=A/"ambiente_continuo_100_110s_con_fades.wav";wav(music_faded,music)
    tests=next(p for p in ROOT.parents if p.name=="tests")
    ff=tests/"_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe"
    logs=[]
    def call(label,args):
        command=[str(ff),"-nostdin","-hide_banner","-v","info",*map(str,args)]
        p=subprocess.run(command,stdin=subprocess.DEVNULL,capture_output=True,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
        log=A/(label+".ffmpeg.stderr.txt")
        with log.open("xb") as f:f.write(p.stderr)
        logs.append({"label":label,"command":command,"returncode":p.returncode,"stderr_path":str(log.relative_to(ROOT)),"stderr_sha256":sha(log)})
        assert p.returncode==0,p.stderr.decode(errors="replace")
        return p.stderr.decode(errors="replace")
    def loudness(label,p):
        text=call(label,["-i",p,"-af","loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json","-f","null","-"])
        return json.loads(text[text.rfind("{"):text.rfind("}")+1])
    v_loud=loudness("01_medicion_voz",narration)
    m_loud=loudness("02_medicion_ambiente_con_fades",music_faded)
    gain_db=float(v_loud["input_i"])-21-float(m_loud["input_i"])
    music*=10**(gain_db/20)
    music_stem=A/"ambiente_bajo_voz_21LU.wav";wav(music_stem,music)
    effects=np.zeros((TOTAL,2),dtype=np.float64);effects_rows=[]
    for start,duration,freq in ((3.0,.12,520),(8.3,.14,660)):
        n=round(duration*SR);u=np.arange(n)/SR
        env=np.sin(np.pi*np.arange(n)/(n-1))**2
        tone=(.8*np.sin(2*np.pi*freq*u)+.2*np.sin(2*np.pi*freq*1.5*u))*env*10**(-36/20)
        offset=round(start*SR);effects[offset:offset+n]+=tone[:,None]
        effects_rows.append({"start_s":start,"duration_s":duration,"fundamental_Hz":freq,"max_amplitude_bound_dBFS":-36,
            "origin":"Original procedural sine effect; editorial emphasis only, not a recorded DEE event or sound"})
    effects_stem=A/"efectos_editoriales_3_0_y_8_3.wav";wav(effects_stem,effects)
    unnormalized=A/"mezcla_10s_pre_normalizacion.wav";mixed=voice+music+effects
    assert np.max(abs(mixed))<1
    wav(unnormalized,mixed)
    first=loudness("03_loudnorm_primera_pasada",unnormalized)
    output=A/"mezcla_10s_48k.wav"
    filt=("loudnorm=I=-16:TP=-1.5:LRA=9:measured_I="+first["input_i"]+":measured_TP="+first["input_tp"]+
        ":measured_LRA="+first["input_lra"]+":measured_thresh="+first["input_thresh"]+":offset="+first["target_offset"]+":linear=true:print_format=json")
    second_text=call("04_loudnorm_segunda_pasada",["-n","-i",unnormalized,"-af",filt,"-ar",SR,"-ac",2,"-c:a","pcm_s24le",output])
    second=json.loads(second_text[second_text.rfind("{"):second_text.rfind("}")+1])
    final_loud=loudness("05_medicion_mezcla_final",output)
    final=read(output);assert final.shape==(TOTAL,2)
    assert sha(narration)==before_voice and sha(music_source)==ref["music"]["sha256"]
    srt=ROOT/"DEE_PILOTO_3D_COMPOSICION_10s_EN.srt"
    old=srt.read_bytes();old_hash=sha(srt);assert old_hash=="9d6bb44977e4ac522ae82910d073a45d199b5b48e75e137d9ca2714b4c9dcb42"
    backup=A/"revisiones/DEE_PILOTO_3D_COMPOSICION_10s_EN_R01.srt"
    with backup.open("xb") as f:f.write(old)
    text=old.decode("utf-8");assert text.count("00:07,630")==1
    updated=text.replace("00:07,630","00:09,800")
    temp=srt.with_suffix(".srt.pending")
    with temp.open("x",encoding="utf-8",newline="\n") as f:f.write(updated)
    temp.replace(srt)
    report={"schema":"DEE.pilot10.editorial_audio_mix.R01","created_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"new_Native_ticks":0,"new_TTS_inference":False,
        "narration":{"path":str(narration.relative_to(ROOT)),"sha256":before_voice,"unaltered":True,"speed":1.0,"no_audio_time_stretch":True},
        "music":{"source":ref["music"],"segment_start_s":100,"segment_end_s":110,"continuous_without_loop_or_restarts":True,"fade_in_s":.5,"fade_out_s":.8,
            "gain_dB":gain_db,"target_integrated_loudness_below_narration_LU":21,"voice_measurement":v_loud,"faded_source_measurement":m_loud,
            "rms_level_difference_after_gain_dB":rms_db(voice)-rms_db(music)},
        "effects":effects_rows,"normalization":{"target_I_LUFS":-16,"target_true_peak_dBTP":-1.5,"target_LRA_LU":9,"pass1":first,"pass2":second,"final_measurement":final_loud},
        "final_audio":{"path":str(output.relative_to(ROOT)),"bytes":output.stat().st_size,"sha256":sha(output),"sample_rate":SR,"duration_s":10,"metrics":metrics(final)},
        "subtitles":{"path":str(srt.relative_to(ROOT)),"sha256":sha(srt),"previous_sha256":old_hash,"previous_preserved":str(backup.relative_to(ROOT)),
            "cue1_s":[.15,4.18],"cue2_phoneme_s":[4.23,7.63],"cue2_display_s":[4.23,9.8],"extension_kind":"Editorial reading hold after the actual voice; no changed phoneme timestamp or English text"},
        "files":[{"path":str(p.relative_to(ROOT)),"bytes":p.stat().st_size,"sha256":sha(p)} for p in (music_faded,music_stem,effects_stem,unnormalized,output,srt)],
        "FFmpeg":{"path":str(ff),"sha256":sha(ff),"calls":logs},"code_sha256":sha(__file__),
        "perceptual_audio_review":"NO EVALUADO: no audio-listening/transcription tool available in this agent; no personal hearing or ASR claimed.",
        "scope":"Prepared audiovisual ambience and effects, never a DEE sensory trace, internal decision or physical sound. Closed original narration and R03 source untouched."}
    save(A/"MEZCLA_AUDIO_10s_R01.json",report)
    print(json.dumps({"output":str(output),"sha256":sha(output),"exact_48k_frames":TOTAL,"music_LU_below_voice":21,"final_LUFS":final_loud["input_i"],"final_TP_dBTP":final_loud["input_tp"],"final_LRA":final_loud["input_lra"],"srt_sha256":sha(srt)},ensure_ascii=False))


if __name__=="__main__":main()
