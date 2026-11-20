"""Preserve candidate R01 and remux its identical video with safer AAC headroom."""
from pathlib import Path
import subprocess,hashlib,json,shutil
H=Path(__file__).resolve().parent;R=H.parent;T=next(x for x in H.parents if x.name=='tests')
FF=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
out=R/'DEE_Cognitive_5min_CORREO_1080p_ES_ENsub.mp4';master=R/'DEE_Cognitive_5min_MASTER_1080p_ES_ENsub.mp4'
old=H/'revisiones/R01_correo'/out.name;old.parent.mkdir(parents=True,exist_ok=True)
assert out.exists() and not old.exists()
assert hashlib.sha256(out.read_bytes()).hexdigest()=='67ef878ecca303f9cde00f85f076f094ea445e2ac5fe2ba4831be4df94cedc27'
shutil.move(str(out),str(old))
cmd=[str(FF),'-hide_banner','-y','-i',str(old),'-i',str(master),'-map','0:v:0','-map','1:a:0','-c:v','copy',
 '-af','volume=-0.75dB','-c:a','aac','-b:a','96k','-ar','48000','-ac','2','-t','300',
 '-metadata:s:a:0','language=spa','-video_track_timescale','15360','-movflags','+faststart',str(out)]
r=subprocess.run(cmd,capture_output=True);(H/'verificacion/correo_audio_R02.log').write_bytes(r.stderr);assert r.returncode==0
rec={'source_video':str(old),'source_video_file_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),
 'source_audio':str(master),'source_audio_file_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),
 'reason':'First96kAAC candidate measured -0.84dBTP, above the <=-1dBTP reference; applying uniform -0.75dB gain without altering the video or relative voice/music mix.',
 'file':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'command':cmd}
(H/'verificacion/CORREO_AUDIO_R02.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({k:rec[k] for k in ['file','bytes','sha256']}),flush=True)
