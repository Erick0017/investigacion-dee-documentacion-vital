"""Render and assemble the fourteen official chapters, native1920x1080.
No source experiment or operational DEE life is executed. All time is film time.
"""
from pathlib import Path
import argparse,bisect,subprocess,json,hashlib,time,datetime,shutil,math,re
from PIL import Image,ImageDraw
from plan_3d import SHOTS,SCENES
from visual_core import ArtRenderer,decorate,BG,FONTS,WHITE
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
T=next(p for p in HERE.parents if p.name=='tests')
FFMPEG=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
FFPROBE=T/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
W,H,FPS=1920,1080,30
STARTS=[s['start'] for s in SHOTS]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def read_srt():
 s=(ROOT/'DEE_Cognitive_5min_EN.srt').read_text('utf8')
 def seconds(x):
  a,b,c=x.replace(',','.').split(':');return float(a)*3600+float(b)*60+float(c)
 cues=[]
 for block in re.split(r'\n\s*\n',s.strip()):
  lines=block.splitlines();a,b=lines[1].split(' --> ')
  assert len(lines[2:])<=2
  cues.append({'start':seconds(a),'end':seconds(b),'lines':lines[2:]})
 assert len(cues)==83 and all(a['end']<=b['start'] for a,b in zip(cues,cues[1:]))
 return cues
CUES=read_srt()

def ass_time(t):
 n=max(0,round(t*100));h,n=divmod(n,360000);m,n=divmod(n,6000);s,cs=divmod(n,100)
 return f'{h}:{m:02}:{s:02}.{cs:02}'
def scene_ass(scene):
 text='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: EN,Segoe UI,84,&H00FFFFFF,&H00FFFFFF,&H00201008,&H70000000,0,0,0,0,100,100,0,0,1,3.4,1.5,2,120,120,48,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
 for cue in CUES:
  if cue['start']>=scene['end_s'] or cue['end']<=scene['start_s']:continue
  a=max(0,cue['start']-scene['start_s']);b=min(scene['duration_s'],cue['end']-scene['start_s'])
  text+=f'Dialogue: 0,{ass_time(a)},{ass_time(b)},EN,,0,0,0,,'+r'\N'.join(cue['lines'])+'\n'
 p=HERE/f'subtitles_scene_{scene["block"]:02}.ass';p.write_text(text,'utf8');return p

def frame_at(artist,t,preview_subs=False):
 idx=max(0,min(len(SHOTS)-1,bisect.bisect_right(STARTS,t)-1));s=SHOTS[idx]
 progress=(t-s['start'])/(s['end']-s['start'])
 image=artist.view(s,progress)
 if idx>0 and t-s['start']<.34:
  prev=SHOTS[idx-1];old=artist.view(prev,1)
  u=max(0,min(1,(t-s['start'])/.34));u=u*u*(3-2*u)
  image=Image.blend(old,image,u)
 scene=SCENES[s['scene']-1];local=t-scene['start_s']
 new=(s.get('new_trial') and t-s['start']<2.1)
 image=decorate(image,s,scene,local,new)
 if preview_subs:
  # Layout preview only. Actual MP4 subtitles are burned by libass below.
  cue=next((x for x in CUES if x['start']<=t<x['end']),None)
  if cue:
   d=ImageDraw.Draw(image);lines=cue['lines'];y=1006-(len(lines)-1)*88
   for line in lines:
    d.text((W/2,y),line,font=FONTS[84],fill=WHITE,anchor='ms',stroke_width=3,stroke_fill=BG);y+=88
 return image,s

def fingerprint(scene):
 inputs={'scene':scene,'shots':[s for s in SHOTS if s['scene']==scene['block']],
 'cues':[x for x in CUES if scene['start_s']<=x['start']<scene['end_s']],
 'core':sha(HERE/'visual_core.py'),'renderer':sha(HERE/'render/renderer_r05.py'),
 'worker':sha(HERE/'render/render_common.cjs'),'owner':sha(Path(__file__)),'config':'h264slowcrf18g60;native1080;30fps;ass84'}
 return hashlib.sha256(json.dumps(inputs,ensure_ascii=False,sort_keys=True).encode()).hexdigest()

def preview():
 out=HERE/'previsualizacion';out.mkdir(exist_ok=True)
 artist=ArtRenderer();summary=[]
 try:
  for n,s in enumerate(SHOTS):
   t=(s['start']+s['end'])/2;image,_=frame_at(artist,t,True)
   p=out/(s['id']+'.png');image.save(p)
   summary.append({'shot':s['id'],'time':t,'native_size':image.size,'path':str(p),'classification':s['classification'],'case_ids':[c['id'] for c in s['cases']]})
   if n%10==0:print('preview',n,'/',len(SHOTS),flush=True)
 finally:artist.close()
 for scene in SCENES:
  rows=[x for x in summary if x['shot'].startswith(f'S{scene["block"]:02}_')]
  h=360*math.ceil(len(rows)/3);sheet=Image.new('RGB',(1920,h),BG)
  for i,row in enumerate(rows):
   im=Image.open(row['path']);im=im.resize((640,360),Image.Resampling.LANCZOS);sheet.paste(im,((i%3)*640,(i//3)*360))
  sheet.save(out/f'CONTACTO_S{scene["block"]:02}.png')
 (HERE/'PREVISUALIZACION.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),'utf8')
 print('Preview complete:',len(summary),'native1080 source images; no video delivered.',flush=True)

def render(selected=None):
 clips=HERE/'clips';clips.mkdir(exist_ok=True)
 png=HERE/'fotogramas_fuente';png.mkdir(exist_ok=True)
 logs=HERE/'logs';logs.mkdir(exist_ok=True)
 artist=ArtRenderer();host=time.monotonic()
 # Preserve the exact code before producing a candidate; source hashes are in every clip stamp.
 revision=HERE/'revisiones/R01';revision.mkdir(parents=True,exist_ok=True)
 for n in ['producir_5min.py','visual_core.py','plan_3d.py','datos_c_3d.py','datos_m_3d.py']:
  dst=revision/n
  if not dst.exists():shutil.copyfile(HERE/n,dst)
 try:
  for scene in SCENES:
   num=scene['block']
   if selected and num not in selected:continue
   fprint=fingerprint(scene);stamp=clips/f'S{num:02}.json';out=clips/f'S{num:02}.mp4'
   if out.exists() and stamp.exists():
    old=json.loads(stamp.read_text('utf8'))
    if old['fingerprint']==fprint and old['sha256']==sha(out):
     print('Reusing closed scene',num,flush=True);continue
    raise RuntimeError(f'Scene{num} differs from its stamp; preserve previous candidate before replacing.')
   ass=scene_ass(scene);frames=round(scene['duration_s']*FPS)
   log=(logs/f'encode_S{num:02}.log').open('wb')
   cmd=[str(FFMPEG),'-hide_banner','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','30','-i','pipe:0',
    '-an','-vf',f'ass={ass.name},setsar=1','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-r','30','-fps_mode','cfr',
    '-g','60','-keyint_min','60','-sc_threshold','0','-video_track_timescale','15360','-frames:v',str(frames),str(out)]
   proc=subprocess.Popen(cmd,cwd=HERE,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=log,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
   records=[];saved=[]
   source_frames=set()
   for s in SHOTS:
    if s['scene']==num:
     source_frames.update([round((s['start']-scene['start_s'])*FPS),round(((s['start']+s['end'])/2-scene['start_s'])*FPS),min(frames-1,round((s['end']-scene['start_s'])*FPS)-1)])
   try:
    for n in range(frames):
     t=scene['start_s']+n/FPS;image,spec=frame_at(artist,t)
     raw=image.tobytes();records.append(hashlib.sha256(raw).hexdigest())
     if n in source_frames:
      path=png/f'S{num:02}_F{n:04}.png';image.save(path);saved.append({'frame':n,'global_frame':round(t*FPS),'file':str(path),'sha256':sha(path)})
     proc.stdin.write(raw)
     if n%300==0:print(f'S{num:02} {n}/{frames} frames; host {time.monotonic()-host:.1f}s',flush=True)
    proc.stdin.close();code=proc.wait(timeout=180)
    if code:raise RuntimeError(f'FFmpeg scene{num} failed; see{logs}')
   finally:
    if proc.poll() is None:proc.terminate();proc.wait(timeout=15)
    log.close()
   probe=subprocess.run([str(FFPROBE),'-v','error','-show_streams','-show_format','-of','json',str(out)],capture_output=True,check=True)
   info=json.loads(probe.stdout);v=info['streams'][0]
   assert v['width']==1920 and v['height']==1080 and int(v['nb_frames'])==frames and v['r_frame_rate']=='30/1'
   stamp.write_text(json.dumps({'fingerprint':fprint,'sha256':sha(out),'bytes':out.stat().st_size,'frames':frames,
    'source_canvas':[W,H],'source_RGB_frame_sha256':records,'source_PNG':saved,'native_renderer':artist.native.info,'ffprobe':info,
    'new_DEE_ticks':0,'scope':'Archived-state render; editorial stage dissolves only'},ensure_ascii=False,indent=2),'utf8')
   print(f'Closed scene{num}/14',flush=True)
 finally:artist.close()

def assemble():
 clips=HERE/'clips';names=[clips/f'S{n:02}.mp4' for n in range(1,15)]
 assert all(x.exists() for x in names)
 total=0
 for scene,p in zip(SCENES,names):
  st=json.loads(p.with_suffix('.json').read_text('utf8'));assert st['sha256']==sha(p) and st['fingerprint']==fingerprint(scene);total+=st['frames']
 assert total==9000
 listing=HERE/'clips.ffconcat';listing.write_text('ffconcat version 1.0\n'+'\n'.join("file 'clips/"+p.name+"'" for p in names)+'\n','utf8')
 out=ROOT/'DEE_Cognitive_5min_MASTER_1080p_ES_ENsub.mp4'
 cmd=[str(FFMPEG),'-hide_banner','-y','-f','concat','-safe','0','-i',str(listing),'-i',str(HERE/'audio/mezcla_final_300s_48k.wav'),
  '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-t','300',
  '-metadata:s:a:0','language=spa','-video_track_timescale','15360','-movflags','+faststart',str(out)]
 r=subprocess.run(cmd,capture_output=True);(HERE/'logs/ensamblado_master.log').write_bytes(r.stderr)
 if r.returncode:raise RuntimeError(r.stderr.decode('utf8','replace')[-3000:])
 print('Master assembled',out.stat().st_size,'bytes',sha(out),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--preview',action='store_true');p.add_argument('--render',action='store_true');p.add_argument('--assemble',action='store_true');p.add_argument('--scenes',nargs='*',type=int)
 a=p.parse_args()
 if a.preview:preview()
 if a.render:render(a.scenes)
 if a.assemble:assemble()
