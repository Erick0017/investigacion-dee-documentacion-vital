"""Verify exact decoded scene identities, all frames, complete AAC and the13joins."""
from pathlib import Path
import sys,json,hashlib,subprocess
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H/'herramientas'))
from verificar_archivo import verify
T=next(x for x in H.parents if x.name=='tests');FF=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe';FP=T/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
rec=json.loads((H/'montaje/SELECCION_Y_ENSAMBLADO.json').read_text('utf8'));final=Path(rec['file']);out=H/'verificacion';out.mkdir(exist_ok=True)
result=verify(final,out);assert result['resolution']==[1920,1080]
def run(cmd):
 r=subprocess.run([str(x) for x in cmd],capture_output=True);assert r.returncode==0,r.stderr.decode('utf8','replace')[-2000:];return r
def md5(p):
 r=run([FF,'-v','error','-i',p,'-map','0:v:0','-an','-pix_fmt','yuv420p','-f','framemd5','-'])
 return [x.rsplit(',',1)[-1].strip() for x in r.stdout.decode().splitlines() if x and not x.startswith('#')]
allhash=md5(final);assert len(allhash)==9000
at=0;scenes=[]
for s in rec['selected_clips']:
 expected=md5(s['file']);actual=allhash[at:at+s['frames']];assert expected==actual,(s['scene'],'decoded content changed')
 if s['scene']==7:
  accepted=H/'PROYECTO_INTACTO/DEE_S07_DESPUES_1080p.mp4'
  assert hashlib.sha256(accepted.read_bytes()).hexdigest()=='7bb3ecac833399cb52d812082f0392d9044c26a16ea29feb3e8c9ec30fa64636'
  assert md5(accepted)==actual,'S07 final interval differs from the accepted protected video'
 scenes.append({'scene':s['scene'],'status':s['status'],'decoded_frames':len(expected),'every_decoded_frame_identical_to_selected_clip':True,
 'selected_source_sha256':s['sha256'],'decoded_sequence_hash':hashlib.sha256('\n'.join(expected).encode()).hexdigest()});at+=s['frames']
 print('Protected decoded interval',s['scene'],flush=True)
def apackets(p):return json.loads(run([FP,'-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=pts_time,dts_time,duration_time,data_hash,side_data_list','-of','json',p]).stdout)['packets']
source=Path(rec['audio_source']);aa,ab=apackets(source),apackets(final);assert aa==ab
def pcmhash(p):return run([FF,'-v','error','-i',p,'-map','0:a:0','-af','atrim=start_sample=0:end_sample=14400000','-c:a','pcm_f32le','-f','hash','-hash','sha256','-']).stdout.decode().strip()
pa,pb=pcmhash(source),pcmhash(final);assert pa==pb
joins=H/'montaje/empalmes';joins.mkdir(exist_ok=True)
from PIL import Image
boundaries=[s['start_s'] for s in rec['selected_clips'][1:]]
for i,b in enumerate(boundaries):
 ims=[];samples=[]
 for j,t in enumerate([b-.3,b-1/30,b,b+.3]):
  p=joins/f'J{i+1:02}_{j}.png';run([FF,'-v','error','-y','-ss',str(t),'-i',final,'-frames:v','1',p]);ims.append(Image.open(p).copy().resize((960,540),Image.Resampling.LANCZOS));samples.append({'time':t,'file':str(p)})
 sheet=Image.new('RGB',(1920,1080));
 for j,im in enumerate(ims):sheet.paste(im,(960*(j%2),540*(j//2)))
 sheet.save(joins/f'EMPALME_{i+1:02}.png')
 closed={'time':b,'samples':samples}
 (joins/f'J{i+1:02}.json').write_text(json.dumps(closed,ensure_ascii=False,indent=2),'utf8')
report={'master':result,'scene_identity':scenes,'complete_original_AAC_packets_identical':True,'AAC_packets':len(aa),
 'S07_every_frame_identical_to_accepted_source':True,
 'complete300s_PCM_identical':True,'PCM_hash':pa,'join_boundaries':boundaries,'join_visual_review':'PENDING_MODEL_INSPECTION',
 'SRT_source_unchanged':hashlib.sha256((H/'DEE_Cognitive_5min_EN.srt').read_bytes()).hexdigest()=='be37093f83c88dc0e7d04ae632f6f2f0a6a563e59197e1246585f7b10843b266'}
ass=[]
for n in range(1,15):
 original=H/f'PROYECTO_INTACTO/trabajo/subtitles_scene_{n:02}.ass'
 local=H/f'escenas/S{n:02}/subtitles.ass'
 assert original.read_bytes()==local.read_bytes(),('ASS changed',n)
 ass.append({'scene':n,'ASS_original_bytes_unchanged':True,'sha256':hashlib.sha256(local.read_bytes()).hexdigest()})
report['original_ASS_files_unchanged']=ass
(out/'IDENTIDAD_POR_INTERVALOS_Y_AUDIO.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print('All9000frames and complete soundtrack preserved as selected.',flush=True)
