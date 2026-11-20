"""Create new editable FLAC copies and verify decoded S24 PCM byte identity.

No source WAV, voice model, production code, schedule or current render changes.
The PCM comparison follows the previous local R08 archival-audio verifier.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import wave

ROOT=Path(__file__).resolve().parents[1]
TESTS=next(p for p in ROOT.parents if (p/"_dee20_trabajo").is_dir())
FF=TESTS/"_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe"
PROBE=TESTS/"_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe"
PREVIOUS=ROOT.with_name("AUDIOVISUAL_R08")/"codigo/verificar_audio_flac_r08.py"


def sha(path):
    digest=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b""):digest.update(block)
    return digest.hexdigest()


def pcm(path):
    command=[str(FF),"-nostdin","-v","error","-threads","2","-i",str(path),"-map","0:a:0","-c:a","pcm_s24le","-f","s24le","pipe:1"]
    process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
        creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
    digest=hashlib.sha256();size=0
    for block in iter(lambda:process.stdout.read(4*1024*1024),b""):
        size+=len(block);digest.update(block)
    error=process.stderr.read();code=process.wait(timeout=120)
    assert code==0 and not error,(code,error)
    return {"PCM_s24le_bytes":size,"PCM_s24le_sha256":digest.hexdigest(),"command":command,"exit_code":code,"stderr":""}


def main():
    target=ROOT/"AUDITORIA/FLAC_SIN_PERDIDA_R12.json"
    assert not target.exists(),"Earlier proof is preserved"
    rows=[]
    for name in ("mezcla_R12_48k","locucion_R12_24k"):
        wav=ROOT/"audio"/(name+".wav");flac=wav.with_suffix(".flac")
        assert wav.is_file() and not flac.exists()
        signature=(wav.stat().st_size,wav.stat().st_mtime_ns,sha(wav))
        with wave.open(str(wav),"rb") as w:
            rate,channels,width,samples=w.getframerate(),w.getnchannels(),w.getsampwidth(),w.getnframes()
        assert width==3 and samples/rate==390
        command=[str(FF),"-nostdin","-hide_banner","-v","error","-n","-threads","2","-i",str(wav),
            "-map","0:a:0","-vn","-c:a","flac","-compression_level","12","-sample_fmt","s32",
            "-bits_per_raw_sample","24",str(flac)]
        result=subprocess.run(command,capture_output=True,timeout=240,
            creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
        assert result.returncode==0 and not result.stderr,(result.returncode,result.stderr)
        a,b=pcm(wav),pcm(flac)
        assert a["PCM_s24le_bytes"]==b["PCM_s24le_bytes"]==samples*channels*3
        assert a["PCM_s24le_sha256"]==b["PCM_s24le_sha256"]
        probe_command=[str(PROBE),"-v","error","-show_streams","-show_format","-of","json",str(flac)]
        probed=subprocess.run(probe_command,capture_output=True,text=True,encoding="utf-8",timeout=30,check=True)
        metadata=json.loads(probed.stdout);stream=metadata["streams"][0]
        assert stream["codec_name"]=="flac" and int(stream["sample_rate"])==rate and stream["channels"]==channels
        assert int(stream["bits_per_raw_sample"])==24 and int(stream["duration_ts"])==samples
        assert signature==(wav.stat().st_size,wav.stat().st_mtime_ns,sha(wav))
        rows.append({"source":str(wav.relative_to(ROOT)),"source_sha256":signature[2],"source_bytes":signature[0],
            "lossless_archive":str(flac.relative_to(ROOT)),"FLAC_sha256":sha(flac),"FLAC_bytes":flac.stat().st_size,
            "reduction_ratio":flac.stat().st_size/signature[0],"source_unchanged":True,
            "sample_rate":rate,"channels":channels,"sample_width_bytes":width,"sample_frames":samples,"duration_s":390,
            "compression_command":command,"compression_exit_code":result.returncode,"compression_stderr":"",
            "source_decode":a,"FLAC_decode":b,"PCM_bit_identical":True,
            "probe_command":probe_command,"FLAC_metadata":metadata})
        print(json.dumps({"completed":name,"FLAC_bytes":flac.stat().st_size,"PCM_bit_identical":True}),flush=True)
    report={"schema":"DEE.R12.lossless_editable_audio.R01","created_utc":datetime.now(timezone.utc).isoformat(),
        "new_Native_ticks":0,"new_synthesis_calls":0,"source_WAVs_unchanged":True,"new_files_only":True,
        "voice_model_redistributed":False,"purpose":"Lossless editable production-audio backup only; not a model or voice library.",
        "rows":rows,"tools":{"ffmpeg":{"path":str(FF),"sha256":sha(FF)},"ffprobe":{"path":str(PROBE),"sha256":sha(PROBE)}},
        "method_origin":{"local_R08_PCM_comparison_script":str(PREVIOUS),"source_sha256":sha(PREVIOUS)},
        "script_sha256":sha(__file__),"hearing_status":"NO EVALUADO","independent_ASR":False}
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open("x",encoding="utf-8",newline="\n") as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write("\n")
    print(json.dumps({"report":str(target),"report_bytes":target.stat().st_size,"report_sha256":sha(target),
        "FLACs":[{k:r[k] for k in("lossless_archive","FLAC_bytes","FLAC_sha256","PCM_bit_identical")} for r in rows]},ensure_ascii=False),flush=True)


if __name__=="__main__":main()
