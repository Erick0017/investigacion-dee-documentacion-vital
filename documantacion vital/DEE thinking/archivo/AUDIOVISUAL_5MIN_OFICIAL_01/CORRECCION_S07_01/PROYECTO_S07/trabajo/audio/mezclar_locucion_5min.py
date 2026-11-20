"""Closed300s narration plus one continuous approved R03 ambience segment."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import math
import subprocess
import sys
import tempfile

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
A=ROOT/"trabajo/audio"
ORIGINAL=ROOT.parent/"produccion_audiovisual_DEE_Cognitive_2_0_20261028/videos/produccion_cientifica/R03/voz/ambiente_R03.wav"
ORIGINAL_SHA="1935a6162d8487471ce09b6135c222ab84d0ae4b9fdcf63aa0ddd1efd03edcd0"
NARRATION=A/"locucion_5min_48k.wav"
NARRATION_SHA="ce167ca11a83862d81cb02366f9d921734c171579427d98524c97ba2fcf6e7ce"
sys.path.insert(0,str(Path(tempfile.gettempdir())/"dee_r03_voice_312cdd7b/pydeps"))
import numpy as np
import soundfile as sf


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
    with p.open("x",encoding="utf-8",newline="\n") as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write("\n")


def main():
    assert not (A/"MEZCLA_FINAL_300s_R01.json").exists(),"Preserve prior complete mix before a new revision"
    assert sha(ORIGINAL)==ORIGINAL_SHA and sha(NARRATION)==NARRATION_SHA
    tests=next(p for p in ROOT.parents if p.name=="tests");ff=tests/"_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe"
    logs=[]
    def call(label,args):
        command=[str(ff),"-nostdin","-hide_banner","-v","info",*map(str,args)]
        p=subprocess.run(command,stdin=subprocess.DEVNULL,capture_output=True,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
        log=A/(label+".stderr.txt")
        with log.open("xb") as f:f.write(p.stderr)
        logs.append({"label":label,"command":command,"returncode":p.returncode,"stderr_path":str(log.relative_to(ROOT)),"stderr_sha256":sha(log)})
        assert p.returncode==0,p.stderr.decode(errors="replace")
        return p.stderr.decode(errors="replace")
    def measure(label,path):
        text=call(label,["-xerror","-err_detect","explode","-i",path,"-af","loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json","-f","null","-"])
        return json.loads(text[text.rfind("{"):text.rfind("}")+1])
    faded=A/"ambiente_R03_000_300s_fades.flac"
    call("mix01_extraer_ambiente",["-n","-i",ORIGINAL,"-af","atrim=start_sample=0:end_sample=14400000,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.8,afade=t=out:st=298:d=2",
        "-ar","48000","-ac","2","-c:a","flac","-sample_fmt","s32","-bits_per_raw_sample","24",faded])
    voice_meter=measure("mix02_medir_voz",NARRATION)
    music_meter=measure("mix03_medir_ambiente",faded)
    gain=float(voice_meter["input_i"])-21-float(music_meter["input_i"])
    bed=A/"ambiente_R03_cama_menos21LU.flac"
    call("mix04_ajustar_cama",["-n","-i",faded,"-af",f"volume={gain:.12f}dB","-ar","48000","-ac","2","-c:a","flac","-sample_fmt","s32","-bits_per_raw_sample","24",bed])
    bed_meter=measure("mix05_verificar_nivel_cama",bed)
    relative=float(voice_meter["input_i"])-float(bed_meter["input_i"])
    assert 18<=relative<=24
    premix=A/"mezcla_300s_pre_normalizacion.flac"
    call("mix06_sumar_stems",["-n","-i",NARRATION,"-i",bed,"-filter_complex","[0:a][1:a]amix=inputs=2:normalize=0:duration=first[a]","-map","[a]",
        "-ar","48000","-ac","2","-c:a","flac","-sample_fmt","s32","-bits_per_raw_sample","24",premix])
    first=measure("mix07_loudnorm_primera_pasada",premix)
    filt=("loudnorm=I=-16:TP=-1.5:LRA=9:measured_I="+first["input_i"]+":measured_TP="+first["input_tp"]+
        ":measured_LRA="+first["input_lra"]+":measured_thresh="+first["input_thresh"]+":offset="+first["target_offset"]+":linear=true:print_format=json")
    output=A/"mezcla_final_300s_48k.wav"
    text=call("mix08_loudnorm_segunda_pasada",["-n","-i",premix,"-af",filt,"-ar","48000","-ac","2","-c:a","pcm_s24le",output])
    second=json.loads(text[text.rfind("{"):text.rfind("}")+1])
    final_meter=measure("mix09_medicion_final_y_decode_completo",output)
    samples=frames=clipped=0;energy=peak=0.0
    with output.open("rb") as f:
        with sf.SoundFile(f) as w:
            assert (w.frames,w.samplerate,w.channels,w.subtype)==(14400000,48000,2,"PCM_24")
            while len(chunk:=w.read(480000,dtype="float64",always_2d=True)):
                frames+=len(chunk);samples+=chunk.size;energy+=float(np.sum(chunk*chunk));peak=max(peak,float(np.max(abs(chunk))))
                clipped+=int(np.count_nonzero(abs(chunk)>=1))
    assert frames==14400000 and clipped==0
    for p in (faded,bed,premix):
        with p.open("rb") as f:
            with sf.SoundFile(f) as w:assert (w.frames,w.samplerate,w.channels)==(14400000,48000,2)
    assert sha(ORIGINAL)==ORIGINAL_SHA and sha(NARRATION)==NARRATION_SHA
    report={"schema":"DEE.5MIN.final_editorial_mix.R01","created_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"new_Native_ticks":0,"new_TTS_inference":False,
        "narration":{"path":str(NARRATION.relative_to(ROOT)),"sha256":NARRATION_SHA,"unaltered_original":True,"speed":1.0,"no_window_or_internal_pause_changes":True},
        "ambience":{"path":str(ORIGINAL),"sha256":ORIGINAL_SHA,"original_procedural_R03_reuse":True,"source_segment_s":[0,300],"continuous":True,"loops":0,"restarts":0,
            "fade_in_s":.8,"fade_out_s":2,"fade_out_window_s":[298,300],"gain_dB":gain,"target_LU_below_voice":21,"measured_LU_below_voice":relative,
            "voice_before_normalization":voice_meter,"music_before_gain":music_meter,"music_after_gain":bed_meter,"level_scope":"Integrated loudness relative to the voice; no assertion that every quiet phoneme has the same instantaneous ratio."},
        "optional_effects":{"included":False,"reason":"Conservative omission to prioritise voice clarity; no independent listening tool available. Music alone supplies editorial ambience.","never_audio_from_DEE":True},
        "normalization":{"passes":2,"target_I_LUFS":-16,"target_TP_dBTP":-1.5,"requested_LRA_LU":9,"pass1":first,"pass2":second,"measured_final":final_meter,
            "no_time_stretch":True,"processing_scope":"Standard loudness/true-peak normalization only; no denoising, phoneme trimming, gate or time rearrangement."},
        "final_audio":{"path":str(output.relative_to(ROOT)),"bytes":output.stat().st_size,"sha256":sha(output),"duration_s":300,"sample_rate":48000,"channels":2,"PCM_bits":24,"sample_frames":frames,
            "sample_peak_dBFS":20*math.log10(peak),"RMS_dBFS":20*math.log10(math.sqrt(energy/samples)),"samples_at_or_above_fullscale":clipped,"all_frames_decoded":True},
        "stems":[{"path":str(p.relative_to(ROOT)),"bytes":p.stat().st_size,"sha256":sha(p),"duration_s":300,"encoding":"FLAC24 lossless media stem"} for p in (faded,bed,premix)],
        "FFmpeg":{"path":str(ff),"sha256":sha(ff),"calls":logs},"code_sha256":sha(__file__),"listening":"NO EVALUADO","ASR":"NO EVALUADO",
        "limits":"Meters and complete decode verify technical scope only. No human hearing, intelligibility or DEE physical-sound claim."}
    out=A/"MEZCLA_FINAL_300s_R01.json";save(out,report)
    print(json.dumps({"audio":str(output),"sha256":sha(output),"duration":300,"frames":frames,"measured_final":final_meter,"music_LU_below_voice":relative,
        "metadata":str(out),"metadata_sha256":sha(out)},ensure_ascii=False),flush=True)


if __name__=="__main__":main()
