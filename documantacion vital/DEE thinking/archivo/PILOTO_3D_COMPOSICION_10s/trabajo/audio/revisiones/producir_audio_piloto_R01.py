"""Two literal phrases, existing local voice, natural speed, exact 10 s by silence only."""
from pathlib import Path
import copy
import datetime as dt
import hashlib
import importlib.abc
import json
import os
import subprocess
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/"trabajo"
AUDIO=WORK/"audio"
ARCHIVE=ROOT.parent
R12=ARCHIVE/"AUDIOVISUAL_R12"
sys.path.insert(0,str(R12/"codigo"))
import audio_r12 as reuse

ES=["En composición, dos contribuciones formaron un producto común.","Ese producto se utilizó en otra interacción del mismo mundo."]
EN=["In composition, two contributions\nformed a common product.","That product was used in another\ninteraction within the same world."]


class NoNative(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname.split(".")[0] in {"dee_thinking","sqlite3","_sqlite3"}:raise RuntimeError("No Native/SQLite in audio production")
        return None


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def stamp(t):
    ms=round(t*1000);return f"{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}"
def save(p,x):
    with p.open("x",encoding="utf-8",newline="\n") as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write("\n")


def boundary():
    def guard(event,args):
        if event=="socket.connect":raise PermissionError("Offline local audio only")
        if event=="open":
            p,mode,flags=args
            if not isinstance(p,(str,bytes,os.PathLike)):return
            write=isinstance(mode,str) and any(c in mode for c in "wax+")
            write=write or bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
            if write and not Path(os.fsdecode(p)).resolve().is_relative_to(ROOT):raise PermissionError("Write outside pilot audio scope")
    sys.addaudithook(guard)


def main():
    sys.meta_path.insert(0,NoNative());boundary()
    assert not (AUDIO/"PROVENIENCIA_AUDIO_PILOTO.json").exists(),"Preserve prior revision before another synthesis"
    reuse.ROOT=WORK
    module,np,sf,synth,assets,runner=reuse.setup()
    module.PARAMS=copy.deepcopy(module.PARAMS)
    module.PARAMS.update(speed=1.0)
    row=module.synthesize({"id":"dos_frases_R01","es":" ".join(ES)},np,sf,synth,assets,runner,{})
    take=WORK/row["file"]
    measured={"schema":"DEE.pilot10.audio.measurement.R01","literal_sentences":ES,"take":row,"new_Native_ticks":0,
        "voice":"em_alex","speed":1.0,"source_runner":{"path":str(reuse.TTS),"sha256":sha(reuse.TTS)},"assets":assets,"model_runner":runner,
        "timing_scope":"Emitted model phoneme durations only; no ASR or human listening."}
    save(AUDIO/"MEDICION_TOMA_COMPLETA_R01.json",measured)
    print(json.dumps({"complete_take_seconds":row["duration"],"model_block_seconds":row["speech_block_seconds"],"sentences":row["sentences"]},ensure_ascii=False),flush=True)
    lead=round(.15*24000);length=240000
    assert lead+row["model_samples"]<=length,"Natural full model waveform does not fit10s; do not stretch or cut."
    with take.open("rb") as f:raw,sr=sf.read(f,dtype="int32")
    assert sr==24000
    start=row["leading_margin_samples"];speech=raw[start:start+row["model_samples"]]
    master=np.zeros(length,dtype=np.int32);master[lead:lead+len(speech)]=speech
    master24=AUDIO/"locucion_10s_24k.wav"
    with master24.open("xb") as f:sf.write(f,master,sr,subtype="PCM_24",format="WAV")
    shift=lead/sr-start/sr
    marks=row["sentences"];assert len(marks)==2
    assert [r["text"] for r in marks]==ES
    assert all(r["method"]=="exact_full_sentence_phonemes" for r in marks),"Unresolved sentence phoneme alignment; do not invent timings"
    cues=[]
    for i,(mark,en) in enumerate(zip(marks,EN),1):
        cues.append({"index":i,"literal_ES":mark["text"],"literal_EN":" ".join(en.splitlines()),"lines_EN":en.splitlines(),
            "start":mark["start"]+shift,"end":mark["end"]+shift,"method":mark["method"]})
    srt=ROOT/"DEE_PILOTO_3D_COMPOSICION_10s_EN.srt"
    with srt.open("x",encoding="utf-8",newline="\n") as f:
        for c in cues:f.write(f"{c['index']}\n{stamp(c['start'])} --> {stamp(c['end'])}\n"+"\n".join(c["lines_EN"])+"\n\n")
    tests=next(p for p in ROOT.parents if p.name=="tests")
    ff=tests/"_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe"
    out=AUDIO/"locucion_10s_48k.wav"
    command=[str(ff),"-nostdin","-hide_banner","-v","error","-n","-i",str(master24),"-ar","48000","-ac","2","-c:a","pcm_s24le",str(out)]
    result=subprocess.run(command,stdin=subprocess.DEVNULL,capture_output=True,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
    assert result.returncode==0,result.stderr.decode(errors="replace")
    with master24.open("rb") as f:check,sr=sf.read(f,dtype="int32")
    with out.open("rb") as f:final,fr=sf.read(f,dtype="int32")
    assert np.array_equal(check[lead:lead+len(speech)],speech)
    assert len(final)==480000 and fr==48000 and final.shape==(480000,2)
    assert np.array_equal(final[:,0],final[:,1])
    assert all(sha(reuse.VOICE_SOURCE/name)==asset["sha256"] for name,asset in assets.items())
    report={**measured,"completed":True,"cues":cues,"assembly":{"duration_seconds":10,"sample_rate":48000,"channels":2,"sample_frames":480000,
        "model_waveform_24k_exact_retained":True,"model_PCM_segment_sha256":hashlib.sha256(speech.tobytes()).hexdigest(),"native_waveform_no_phoneme_trim":True,
        "speed":1.0,"post_synthesis_time_stretch":False,"only_added_silence_repositioned":True,"model_start_seconds":.15,
        "model_end_seconds":(lead+len(speech))/24000,"resampling":"24000mono→48000stereo; playback duration unchanged"},
        "FFmpeg":{"path":str(ff),"sha256":sha(ff),"command":command,"stderr":result.stderr.decode(errors="replace")},
        "files":[{"path":str(p.relative_to(ROOT)),"bytes":p.stat().st_size,"sha256":sha(p)} for p in (take,master24,out,srt)],
        "code_sha256":sha(__file__),"created_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "limitations":["No human listening or independent ASR performed; metrics and model phoneme alignment do not certify naturalness or intelligibility.","No DEE experiments, model downloads, remote services, protected-source copies or video generation."]}
    save(AUDIO/"PROVENIENCIA_AUDIO_PILOTO.json",report)
    print(json.dumps({"output":str(out),"sha256":sha(out),"srt":str(srt),"srt_sha256":sha(srt),"duration":10,"frames_48k":480000,"cues":cues},ensure_ascii=False),flush=True)


if __name__=="__main__":main()
