"""Two-pass delivery encode derived exclusively from the closed 1080p master."""
from pathlib import Path
import subprocess,json,hashlib,time
H=Path(__file__).resolve().parent;R=H.parent;T=next(x for x in H.parents if x.name=='tests')
FF=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
src=R/'DEE_Cognitive_5min_MASTER_1080p_ES_ENsub.mp4'
dst=R/'DEE_Cognitive_5min_CORREO_1080p_ES_ENsub.mp4'
assert src.is_file() and not dst.exists(),'Preserve a previous candidate before another encode.'
logs=H/'verificacion';logs.mkdir(exist_ok=True)
prefix=str(logs/'correo_1080_R01')
base=[str(FF),'-hide_banner','-y','-i',str(src),'-map','0:v:0','-c:v','libx264','-preset','veryslow','-b:v','380k',
 '-maxrate','760k','-bufsize','1520k','-pix_fmt','yuv420p','-r','30','-fps_mode','cfr','-g','60','-keyint_min','60',
 '-sc_threshold','0','-video_track_timescale','15360','-passlogfile',prefix,'-t','300']
commands=[];started=time.monotonic()
for n in [1,2]:
 cmd=base+['-pass',str(n)]
 if n==1:cmd+=['-an','-f','null','-']
 else:cmd+=['-map','0:a:0','-c:a','aac','-b:a','96k','-ar','48000','-ac','2','-metadata:s:a:0','language=spa','-movflags','+faststart',str(dst)]
 commands.append(cmd)
 with (logs/f'correo_pass{n}.log').open('wb') as log:
  ret=subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=log)
 assert ret.returncode==0,f'Encoding pass{n} failed.'
 print('Closed email pass',n,flush=True)
result={'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'file':str(dst),
 'bytes':dst.stat().st_size,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'commands':commands,'host_seconds':time.monotonic()-started,
 'content':'Same complete300s master; no edits, retiming, caption changes or scaling.'}
(logs/'CORREO_RECIPE_R01.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({k:result[k] for k in ['file','bytes','sha256','host_seconds']},ensure_ascii=False),flush=True)
