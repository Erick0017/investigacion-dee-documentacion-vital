"""Closed-media/phrase checks only; not listening, ASR or DEE execution."""
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
ALIAS=Path(tempfile.gettempdir())/"dee_r03_voice_312cdd7b"
sys.path.insert(0,str(ALIAS/"pydeps"))
import numpy as np
import soundfile as sf


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding="utf-8-sig"))


def main():
    p=A/"CONTINUIDAD_AUDIO_300s_R01.json";continuity=load(p);index=load(A/"PROVENIENCIA_TOMAS_14.json");guion=load(A/"guion.json")
    assert sha(A/"guion.json")==continuity["guion_sha256"]==index["guion_sha256"]
    assert sha(A/"PROVENIENCIA_TOMAS_14.json")==continuity["take_index_sha256"]
    assert len(guion["blocks"])==len(index["takes"])==len(continuity["block_waveform_proofs"])==14
    assert sum(len(b["literal_ES"].split()) for b in guion["blocks"])==616
    for b in guion["blocks"]:
        row=next(t for t in index["takes"] if t["block_id"]==b["id"])
        assert row["es"]==b["literal_ES"]==row["recipe"]["literal_es"]
        assert row["recipe"]["parameters"]["speed"]==1.0 and row["recipe"]["parameters"]["voice"]=="em_alex"
        assert sha(ROOT/"trabajo"/row["file"])==row["wav_sha256"]
    counters={}
    for name,key in (("sentences","phrase_model_timings"),("clauses","clause_model_timings")):
        rows=continuity[key];resolved=unresolved=0
        for row in rows:
            text=next(b["literal_ES"] for b in guion["blocks"] if b["id"]==row["block_id"])
            a,b=row["character_range_0based_exclusive"];assert text[a:b]==row["literal_ES"]
            if row["start_s_in_master"] is None:unresolved+=1;continue
            resolved+=1
            window=next(b for b in guion["blocks"] if b["id"]==row["block_id"])
            assert window["start_s"]<=row["start_s_in_master"]<row["end_s_in_master"]<=window["end_s"]
        counters[name]={"total":len(rows),"resolved_exact_model_phonemes":resolved,"unresolved_explicit":unresolved}
    audio=A/"locucion_5min_48k.wav";audio_hash=sha(audio)
    expected=next(f for f in continuity["final_files"] if f["path"].endswith("locucion_5min_48k.wav"))
    assert expected["sha256"]==audio_hash
    frames=count=clipped=0;energy=peak=0.0;channel_equal=True
    with audio.open("rb") as handle:
        with sf.SoundFile(handle) as w:
            assert (w.samplerate,w.channels,w.subtype,w.frames)==(48000,2,"PCM_24",14400000)
            while len(block:=w.read(480000,dtype="float64",always_2d=True)):
                frames+=len(block);count+=block.size;energy+=float(np.sum(block*block));peak=max(peak,float(np.max(abs(block))))
                clipped+=int(np.count_nonzero(abs(block)>=1));channel_equal=channel_equal and np.array_equal(block[:,0],block[:,1])
    assert frames==14400000 and clipped==0 and channel_equal
    tests=next(p for p in ROOT.parents if p.name=="tests");ff=tests/"_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe"
    cmd=[str(ff),"-nostdin","-hide_banner","-v","error","-xerror","-err_detect","explode","-threads","2","-i",str(audio),"-f","null","-"]
    result=subprocess.run(cmd,stdin=subprocess.DEVNULL,capture_output=True,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
    assert result.returncode==0 and not result.stderr.strip()
    assert sha(audio)==audio_hash
    report={"schema":"DEE.5MIN.closed_audio_verification.R01","created_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"completed":True,"new_Native_ticks":0,"new_TTS_inference":False,
        "audio":{"path":str(audio.relative_to(ROOT)),"bytes":audio.stat().st_size,"sha256":audio_hash,"duration_s":300,"sample_rate":48000,"channels":2,"sample_frames":frames,
            "sample_peak_dBFS":20*math.log10(peak),"RMS_dBFS":20*math.log10(math.sqrt(energy/count)),"samples_at_full_scale":clipped,"dual_channels_equal":channel_equal},
        "blocks":14,"literal_words":616,"literal_ES_matches_guion_and_recipe":True,"voice":"em_alex","speed":1.0,"phrase_and_clause_checks":counters,
        "all14_takes_unchanged":True,"no_title_paragraph_spoken":True,"whole_model_waveform_proof":str(p.relative_to(ROOT)),"whole_model_waveform_proof_sha256":sha(p),
        "minimum_model_fit_margin_s":min(t["model_fit_margin_s"] for t in index["takes"]),
        "strict_full_audio_decode":{"command":cmd,"returncode":result.returncode,"stderr":result.stderr.decode(errors="replace"),"FFmpeg_sha256":sha(ff)},
        "code_sha256":sha(__file__),"listening":"NO EVALUADO","independent_ASR":"NO EVALUADO","meaning_or_scientific_verdict":"OUTSIDE_AUDIO_TOOL_SCOPE"}
    out=A/"VERIFICACION_AUDIO_300s_R01.json"
    with out.open("x",encoding="utf-8",newline="\n") as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write("\n")
    print(json.dumps({"report":str(out),"sha256":sha(out),"phrases_and_clauses":counters,"peak_dBFS":report["audio"]["sample_peak_dBFS"],"RMS_dBFS":report["audio"]["RMS_dBFS"],"strict_decode":True},ensure_ascii=False))


if __name__=="__main__":main()
