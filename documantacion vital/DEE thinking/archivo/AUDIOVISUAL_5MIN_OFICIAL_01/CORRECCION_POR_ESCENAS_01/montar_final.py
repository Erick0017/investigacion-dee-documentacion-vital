"""Select reviewed clips and remux the unchanged complete soundtrack."""
from pathlib import Path
import json,subprocess,hashlib
H=Path(__file__).resolve().parent;T=next(x for x in H.parents if x.name=='tests')
FF=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe';FP=T/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
blocks=json.loads((H/'herramientas/guion.json').read_text('utf8'))['blocks']
old=H/'PROYECTO_INTACTO';orig=old/'DEE_Cognitive_5min_MASTER_1080p_ES_ENsub.mp4'
assert sha(orig)=='7beec0b2fde67b09b4b81171ce03b788610223c124553e67d46346f0990327cc'
protected=old/'DEE_S07_DESPUES_1080p.mp4';assert sha(protected)=='7bb3ecac833399cb52d812082f0392d9044c26a16ea29feb3e8c9ec30fa64636'
work=H/'montaje';work.mkdir(exist_ok=True)
clip7=work/'S07_ACEPTADA_SOLO_VIDEO.mp4'
if not clip7.exists():subprocess.run([str(FF),'-v','error','-n','-i',str(protected),'-map','0:v:0','-an','-c:v','copy','-video_track_timescale','15360',str(clip7)],capture_output=True,check=True)
selection=[]
for n in range(1,15):
 if n==7:p=clip7;status='CORREGIDA';decision={'status':status,'scope':'S07 accepted by user, protected, not redesigned.'}
 else:
  d=H/f'escenas/S{n:02}';decision=json.loads((d/'REVISION.json').read_text('utf8'));status=decision['status'];assert status in ['CONSERVADA','CORREGIDA','BLOQUEADA']
  p=d/'CORREGIDA_SIN_AUDIO.mp4' if status=='CORREGIDA' else old/f'trabajo/clips/S{n:02}.mp4'
  if status=='CORREGIDA':
   seal=json.loads((d/'SELLO_RENDER.json').read_text('utf8'));assert sha(p)==seal['sha256'] and seal['scene_code_sha256']==sha(d/'escena.py')
   assert seal['base_code_sha256']==sha(H/'herramientas/escena_base.py'),'Shared rendering code changed after local review'
   assert seal['ASS_sha256']==sha(d/'subtitles.ass'),'Scene subtitles changed after local review'
   assert (d/'comparacion/INDICE.json').exists() and (d/'comparacion/AUDIO_IDENTICO.json').exists()
 r=subprocess.run([str(FP),'-v','error','-select_streams','v:0','-show_streams','-of','json',str(p)],capture_output=True,check=True)
 v=json.loads(r.stdout)['streams'][0];assert v['width']==1920 and v['height']==1080 and int(v['nb_frames'])==blocks[n-1]['duration_s']*30 and v['avg_frame_rate']=='30/1'
 selection.append({'scene':n,'status':status,'file':str(p),'sha256':sha(p),'frames':int(v['nb_frames']),'start_s':blocks[n-1]['start_s'],'end_s':blocks[n-1]['end_s'],'decision':decision})
assert sum(x['frames'] for x in selection)==9000
listing=work/'seleccion.ffconcat';listing.write_text('ffconcat version 1.0\n'+'\n'.join("file '"+str(Path(s['file'])).replace('\\','/')+"'" for s in selection)+'\n','utf8')
out=H/'DEE_Cognitive_5min_MASTER_CORREGIDO_1080p_ES_ENsub.mp4';assert not out.exists()
cmd=[str(FF),'-hide_banner','-n','-f','concat','-safe','0','-i',str(listing),'-i',str(orig),'-map','0:v:0','-map','1:a:0',
 '-c:v','copy','-c:a','copy','-t','300','-use_editlist','1','-avoid_negative_ts','disabled','-metadata:s:a:0','language=spa','-video_track_timescale','15360','-movflags','+faststart',str(out)]
r=subprocess.run(cmd,capture_output=True);(work/'ENSAMBLADO.log').write_bytes(r.stderr);assert r.returncode==0,r.stderr.decode('utf8','replace')[-2000:]
rec={'file':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'selected_clips':selection,'command':cmd,
 'audio_source':str(orig),'audio_encoded':False,'global_visual_filter':False,'S07_protected_source_sha256':sha(protected),
 'scope':'FINAL PARA REVISION; no publication or send authorization.'}
(work/'SELECCION_Y_ENSAMBLADO.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),'utf8')
print('Assembled300s',out.stat().st_size,sha(out),flush=True)
