"""Small extension of the existing audiovisual renderer, not a DEE execution tool.
Frozen for this correction. A scene module supplies its own models and captions.
"""
from pathlib import Path
import sys,json,hashlib,subprocess,importlib.util,argparse,math,copy,time
from collections import OrderedDict
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;ROOT=H.parent;OLD=ROOT.parent/'trabajo'
T=next(x for x in H.parents if x.name=='tests')
FF=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
FP=T/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
sys.path.insert(0,str(H/'s07_render'))
from renderer_s07 import WebGLRenderer
from visual_core import model_from_case,camera_for,hollow
W,HEIGHT,FPS=1920,1080,30
BG='#07131D';BLUE='#46C7EB';AMBER='#F4C46B';PURPLE='#B89BE8';WHITE='#E8F4F3';GREY='#8BA1AD'
FONT=Path(r'C:\Windows\Fonts\segoeui.ttf');FONTS={n:ImageFont.truetype(str(FONT),n) for n in range(24,87,2)}
CASES=json.loads((H/'CASOS.json').read_text('utf8'));BLOCKS=json.loads((H/'guion.json').read_text('utf8'))['blocks']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def smooth(a,b,t):
 u=max(0,min(1,(t-a)/(b-a)));return u*u*(3-2*u)
def lerp(a,b,u):return [x+(y-x)*u for x,y in zip(a,b)]
def text(im,xy,txt,n=44,color=WHITE,anchor='mm',maxw=1740):
 d=ImageDraw.Draw(im);n=int(n)//2*2
 while n>24 and d.textlength(txt,font=FONTS[n])>maxw:n-=2
 d.text(xy,txt,font=FONTS[n],fill=color,anchor=anchor,stroke_width=2,stroke_fill=BG)
def model(camera=None,bounds=None):
 return {'camera':camera or {'eye':[3,-10,6.4],'target':[0,0,.9],'fov':42,'lens_shift':[0,.12]},
 'bounds':bounds or [[-5,-2,-.5],[5,2,3.3]],'particles':[],'boxes':[],'paths':[],'arrows':[],
 'spatial_grid':{'step':2,'plane_z':-.5,'opacity':.045,'color':'#476B7B'},
 'ground':{'z':-.55,'opacity':.56,'color':'#10232E'},'provenance':{'representation':'Esquema'}}
def particle(m,pos,r=.3,color=PURPLE,shape='cube',alpha=1):
 m['particles'].append({'position':list(pos),'radius':r,'shape':shape,'color':color,'opacity':alpha})
def wire(m,pos,color=GREY,size=.65,alpha=.48,thickness=.015):hollow(m['boxes'],list(pos),color,alpha,size,thickness)
def link(m,points,color=PURPLE,r=.025,alpha=.5):m['paths'].append({'points':[list(p) for p in points],'radius':r,'color':color,'opacity':alpha})
def arrow(m,pos,direction,length=.6,color=WHITE,r=.045):m['arrows'].append({'origin':list(pos),'direction':list(direction),'length':length,'radius':r,'color':color})
def token(m,a,b,u,color=PURPLE,r=.24,arc=.3):
 p=lerp(a,b,u);p[2]+=arc*math.sin(math.pi*u);particle(m,p,r,color);return p
def overlay_pair(im,left,right,y=224,en_y=266,size=44):
 for i,(es,en) in enumerate([left,right]):text(im,(480+960*i,y),es,size,maxw=850);text(im,(480+960*i,en_y),en,34,GREY,maxw=850)
class Artist:
 def __init__(self):self.native=WebGLRenderer();self.cache=OrderedDict()
 def close(self):self.native.close()
 def render(self,m):
  k=hashlib.sha256(json.dumps(m,sort_keys=True).encode()).hexdigest()
  if k in self.cache:im=self.cache.pop(k);self.cache[k]=im
  else:
   im=self.native.render(m);self.cache[k]=im
   if len(self.cache)>64:self.cache.popitem(last=False)
  return im.copy()
 def case_model(self,id,panel=False,**changes):
  c=copy.deepcopy(CASES[id]);c.update(changes);return model_from_case(c,panel=panel)
 def case(self,id,panel=False,**changes):return self.render(self.case_model(id,panel,**changes))
 def pair(self,left,right,changes_left=None,changes_right=None,same_camera=True):
  mm=[self.case_model(left,True,**(changes_left or {})),self.case_model(right,True,**(changes_right or {}))]
  if same_camera:
   # Union of exactly the drawn data; positions are never transplanted between cases.
   sites=[p['position'] for m in mm for p in m.get('particles',[])]+[b['position'] for m in mm for b in m.get('boxes',[])]
   if sites:
    cam,_=camera_for(sites,panel=True,radius=.43)
    for m in mm:m['camera']=cam
  ims=[self.render(m) for m in mm];return self.panels(ims)
 def panels(self,ims):
  im=Image.new('RGB',(W,HEIGHT),BG)
  for i,x in enumerate(ims[:2]):im.paste(x.crop((480,0,1440,HEIGHT)),(960*i,0))
  ImageDraw.Draw(im).line((960,240,960,830),fill='#35505E',width=2);return im
def decorate(im,meta,num,t):
 b=BLOCKS[num-1]
 text(im,(960,63),meta.get('title_es',''),58,maxw=1740)
 text(im,(960,116),meta.get('title_en',''),40,GREY,maxw=1740)
 mode=meta.get('mode','Esquema')
 labels={'Esquema':'Esquema explicativo / Illustrative schematic','Etapas':'Etapas registradas / Recorded stages',
 'Registro':'Registro / Recorded state','Transición':'Transición editorial / Editorial transition'}
 text(im,(56,171),labels[mode],28,GREY,'lm',1600)
 if meta.get('source'):text(im,(1862,25),meta['source'],28,GREY,'rm',1100)
 if meta.get('phase_es'):text(im,(960,755),meta['phase_es'],48,meta.get('phase_color',PURPLE),maxw=1740)
 if meta.get('phase_en'):text(im,(960,804),meta['phase_en'],38,GREY,maxw=1740)
 ImageDraw.Draw(im).rectangle((0,1077,int(W*(b['start_s']+t)/300),1079),fill='#41616F')
 return im
def load(path):
 path=Path(path).resolve();assert path.is_relative_to(ROOT/'escenas') and path.name=='escena.py'
 spec=importlib.util.spec_from_file_location('local_scene',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 assert 1<=m.SCENE<=14 and m.SCENE!=7
 return m,path
def frame(a,m,t):
 im,meta=m.frame(a,t);assert im.size==(W,HEIGHT)
 return decorate(im,meta,m.SCENE,t),meta
def preview(path):
 m,path=load(path);b=BLOCKS[m.SCENE-1];out=path.parent/'previas';out.mkdir(exist_ok=True)
 times=sorted(set([round(b['duration_s']*f,4) for f in [.15,.4,.65,.9]]+list(getattr(m,'SAMPLE_TIMES',[]))))
 a=Artist();rows=[]
 try:
  for i,t in enumerate(times):
   im,meta=frame(a,m,t);im.save(out/f'{i:02}_{t:06.2f}.png');rows.append({'time':t,'meta':meta,'file':str(out/f'{i:02}_{t:06.2f}.png')})
 finally:a.close()
 (out/'INDICE.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf8')
 print('Preview complete',m.SCENE,len(rows),flush=True)
def render(path):
 m,path=load(path);b=BLOCKS[m.SCENE-1];out=path.parent/'CORREGIDA_SIN_AUDIO.mp4';assert not out.exists()
 log=(path.parent/'RENDER.log').open('wb');a=Artist();hashes=[];start=time.monotonic()
 cmd=[str(FF),'-hide_banner','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','30','-i','pipe:0','-an',
 '-vf','ass=subtitles.ass,setsar=1','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-r','30','-fps_mode','cfr',
 '-g','60','-keyint_min','60','-sc_threshold','0','-video_track_timescale','15360','-frames:v',str(round(b['duration_s']*30)),str(out)]
 p=subprocess.Popen(cmd,cwd=path.parent,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=log,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 try:
  for n in range(round(b['duration_s']*30)):
   im,_=frame(a,m,n/30);raw=im.tobytes();hashes.append(hashlib.sha256(raw).hexdigest());p.stdin.write(raw)
   if n%300==0:print(f'S{m.SCENE:02} {n} frames; {time.monotonic()-start:.1f}s',flush=True)
  p.stdin.close();assert p.wait(timeout=180)==0
 finally:
  if p.poll() is None:p.terminate();p.wait(timeout=15)
  a.close();log.close()
 rec={'scene':m.SCENE,'file':str(out),'sha256':sha(out),'bytes':out.stat().st_size,'frames':len(hashes),'source_canvas':[W,HEIGHT],
 'RGB_sha256_per_frame':hashes,'scene_code_sha256':sha(path),'base_code_sha256':sha(__file__),'renderer':a.native.info,
 'ASS_sha256':sha(path.parent/'subtitles.ass'),'new_DEE_ticks':0,'scope':'Only this scene. Audio is retained separately, no inference or engine execution.'}
 (path.parent/'SELLO_RENDER.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),'utf8');print('Closed',out,flush=True)
def compare(path):
 m,path=load(path);b=BLOCKS[m.SCENE-1];new=path.parent/'CORREGIDA_SIN_AUDIO.mp4';assert new.exists()
 out=path.parent/'comparacion';out.mkdir(exist_ok=True)
 times=sorted(set([round(b['duration_s']*f,4) for f in [.15,.4,.65,.9]]+list(getattr(m,'SAMPLE_TIMES',[]))))
 # Closely spaced frames of the entire sequence, plus the mandatory aligned anchors.
 sequence=sorted(set(times+[round(x/2,4) for x in range(math.ceil(b['duration_s']*2))]));rows=[]
 for side,p in [('ANTES',OLD/f'clips/S{m.SCENE:02}.mp4'),('DESPUES',new)]:
  for i,t in enumerate(sequence):
   f=out/f'{side}_{i:03}.png';subprocess.run([str(FF),'-v','error','-y','-ss',str(t),'-i',str(p),'-frames:v','1',str(f)],capture_output=True,check=True)
   rows.append({'side':side,'time':t,'file':str(f),'aligned_anchor':t in times,'sha256':sha(f)})
 # Each aligned pair is shown with the same scale; telephone versions are explicitQA.
 for i,t in enumerate(times):
  pair=Image.new('RGB',(1920,1080),BG)
  for j,side in enumerate(['ANTES','DESPUES']):
   r=next(r for r in rows if r['side']==side and r['time']==t)
   im=Image.open(r['file']);pair.paste(im.resize((960,540),Image.Resampling.LANCZOS),(960*j,225))
   text(pair,(480+960*j,170),side,44)
  pair.save(out/f'PAR_{i:02}_{t:06.2f}.png')
  pair.resize((1080,608),Image.Resampling.LANCZOS).save(out/f'TELEFONO_PAR_{i:02}.png')
 # Contact sheets cover every half-second, not only first frames.
 for side in ['ANTES','DESPUES']:
  rs=[r for r in rows if r['side']==side];chunk=12
  for base in range(0,len(rs),chunk):
   group=rs[base:base+chunk];sheet=Image.new('RGB',(1920,360*math.ceil(len(group)/3)),BG)
   for i,r in enumerate(group):sheet.paste(Image.open(r['file']).resize((640,360),Image.Resampling.LANCZOS),((i%3)*640,(i//3)*360))
   sheet.save(out/f'SECUENCIA_{side}_{base//chunk:02}.png')
 (out/'INDICE.json').write_text(json.dumps({'scene':m.SCENE,'start_s':b['start_s'],'duration':b['duration_s'],'samples':rows,'audio_context':str(ROOT/'PROYECTO_INTACTO/DEE_Cognitive_5min_MASTER_1080p_ES_ENsub.mp4'),
 'audio_context_rule':'The unchanged master supplies the exact locution at start_s+local time; no new voice or soundtrack.'},ensure_ascii=False,indent=2),'utf8')
 print('Comparison complete',m.SCENE,len(rows),'aligned/sequence samples',flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('module',type=Path);ap.add_argument('--preview',action='store_true');ap.add_argument('--render',action='store_true');ap.add_argument('--compare',action='store_true');args=ap.parse_args()
 if args.preview:preview(args.module)
 if args.render:render(args.module)
 if args.compare:compare(args.module)
