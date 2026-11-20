"""Two-pass delivery copy; preserves the entire existing AAC track."""
from pathlib import Path
import json,subprocess,hashlib,argparse,sys,math,time
H=Path(__file__).resolve().parent;T=next(x for x in H.parents if x.name=='tests')
FF=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
FP=T/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
ap=argparse.ArgumentParser();ap.add_argument('--height',type=int,choices=[1080,720],default=1080);args=ap.parse_args()
source=H/'DEE_Cognitive_5min_MASTER_CORREGIDO_1080p_ES_ENsub.mp4'
assert source.is_file()
out=H/f'DEE_Cognitive_5min_CORREO_CORREGIDO_{args.height}p_ES_ENsub.mp4'
assert not out.exists(), 'Never overwrite a delivered candidate'
work=H/'correo';work.mkdir(exist_ok=True)
probe=subprocess.run([str(FP),'-v','error','-select_streams','a:0','-show_packets','-show_entries','packet=size','-of','json',str(source)],capture_output=True,check=True)
audio_bytes=sum(int(x['size']) for x in json.loads(probe.stdout)['packets'])
video_kbps=math.floor(((19_000_000-250_000-audio_bytes)*8/300)/1000)
assert 180<video_kbps<600,video_kbps
scale=[] if args.height==1080 else ['-vf','scale=1280:720:flags=lanczos,setsar=1']
base=[str(FF),'-hide_banner','-n','-i',str(source),'-map','0:v:0',*scale,'-c:v','libx264','-preset','veryslow','-threads','6','-b:v',str(video_kbps)+'k','-maxrate','1200k','-bufsize','2400k','-pix_fmt','yuv420p','-r','30','-fps_mode','cfr','-g','60','-keyint_min','60','-sc_threshold','0','-passlogfile',str(work/f'x264_{args.height}p')]
commands=[base+['-pass','1','-an','-t','300','-f','null','NUL'],base+['-pass','2','-map','0:a:0','-c:a','copy','-t','300','-use_editlist','1','-avoid_negative_ts','disabled','-video_track_timescale','15360','-movflags','+faststart',str(out)]]
started=time.monotonic()
for i,cmd in enumerate(commands,1):
 print('Email pass',i,'video kbps',video_kbps,flush=True)
 with (work/f'PASS{i}_{args.height}p.log').open('wb') as log:
  r=subprocess.run(cmd,stdout=log,stderr=log)
 assert r.returncode==0, f'Pass {i} failed; see local log'
print('Email encoded',out.stat().st_size,flush=True)
sys.path.insert(0,str(H/'herramientas'))
from verificar_archivo import verify
result=verify(out,H/'verificacion')
assert result['resolution']==([1920,1080] if args.height==1080 else [1280,720])
def packets(p):
 r=subprocess.run([str(FP),'-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=pts_time,dts_time,duration_time,data_hash,side_data_list','-of','json',str(p)],capture_output=True,check=True)
 return json.loads(r.stdout)['packets']
assert packets(out)==packets(source),'Soundtrack packets changed'
receipt={'file':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source_master_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'video_kbps':video_kbps,'AAC_bytes':audio_bytes,'AAC_packets_and_timing_identical_to_master':True,'commands':commands,'host_seconds':time.monotonic()-started,'visual_review':'PENDING','status':'FINAL PARA REVISION'}
(work/f'EXPORTACION_{args.height}p.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),'utf8')
print('Email export complete',receipt['bytes'],receipt['sha256'],flush=True)
