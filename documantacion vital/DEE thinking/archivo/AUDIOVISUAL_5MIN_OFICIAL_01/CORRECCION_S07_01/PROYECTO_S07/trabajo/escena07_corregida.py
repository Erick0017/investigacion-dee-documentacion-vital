"""Scene07 only: illustrative functional animation plus exact archived reader states.

No DEE import or execution. Schematic positions and motion are pedagogical,
never measurements of a portador's route, distance, speed, or anatomy.
The data comparison uses identical cameras and exact fields atT16619.
"""
from pathlib import Path
import sys,json,math,hashlib,subprocess,shutil,argparse,time
from PIL import Image,ImageDraw,ImageFont
import numpy as np
H=Path(__file__).resolve().parent;OUT=H.parents[1];T=next(x for x in H.parents if x.name=='tests')
FF=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
FP=T/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
LOCAL=H/'s07_render';LOCAL.mkdir(exist_ok=True)
# A scene-private copy, not a change to any shared renderer or protected project.
if not (LOCAL/'renderer_s07.py').exists():
 shutil.copy2(H/'render/renderer_r05.py',LOCAL/'renderer_s07.py')
 worker=(H/'render/render_common.cjs').read_text('utf8')
 worker=worker.replace('(.31+.68*key+.19*fill)','(.42+.62*key+.23*fill)')
 (LOCAL/'render_common.cjs').write_text(worker,'utf8')
sys.path.insert(0,str(LOCAL))
from renderer_s07 import WebGLRenderer
from visual_core import model_from_case,hollow
W,HIGH,FPS=1920,1080,30
BG='#07131D';BLUE='#46C7EB';AMBER='#F4C46B';PURPLE='#B89BE8';WHITE='#E8F4F3';GREY='#8BA1AD'
FONTP=Path(r'C:\Windows\Fonts\segoeui.ttf');FONTS={n:ImageFont.truetype(str(FONTP),n) for n in range(24,87,2)}
CASES=json.loads((H/'CASOS_S07_CONGELADOS.json').read_text('utf8'))
CAM={'eye':[2.7,-9,5.85],'target':[0,0,.9],'fov':42,'lens_shift':[0,.12]}
BS=[-3.0,0,1.0];ES=[3.0,0,1.0]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def sm(a,b,t):
 x=max(0,min(1,(t-a)/(b-a)));return x*x*(3-2*x)
def lerp(a,b,u):return [x+(y-x)*u for x,y in zip(a,b)]
def label(im,xy,txt,n=44,color=WHITE,anchor='mm',maxw=1740):
 d=ImageDraw.Draw(im)
 while n>24 and d.textlength(txt,font=FONTS[n])>maxw:n-=2
 d.text(xy,txt,font=FONTS[n],fill=color,anchor=anchor,stroke_width=2,stroke_fill=BG)
def project(pos,camera=CAM):
 eye=np.array(camera['eye']);target=np.array(camera['target']);z=eye-target;z/=np.linalg.norm(z)
 x=np.cross([0,0,1],z);x/=np.linalg.norm(x);y=np.cross(z,x);d=np.array(pos)-eye;dep=-d@z
 f=1/math.tan(math.radians(camera['fov']/2));shift=camera['lens_shift']
 return ((d@x*f/(W/HIGH)/dep+shift[0]+1)*W/2,(1-d@y*f/dep-shift[1])*HIGH/2)
def model():
 return {'camera':CAM,'bounds':[[-5,-2,-.5],[5,2,3.3]],'particles':[],'boxes':[],'paths':[],'arrows':[],
 'spatial_grid':{'step':2,'plane_z':-.5,'opacity':.045,'color':'#476B7B'},
 'ground':{'z':-.55,'opacity':.56,'color':'#10232E'},'provenance':{'representation':'Esquema'}}
def p(m,pos,r,color,shape='sphere',opacity=1):m['particles'].append({'position':pos,'radius':r,'shape':shape,'color':color,'opacity':opacity})
def participant(m,pos,sender=False,received=0,used=0):
 # Functional icons, not a proposed or measured physical anatomy.
 hollow(m['boxes'],pos,BLUE if sender else GREY,.52,.83,.018)
 if sender:
  p(m,pos,.44,AMBER,'cube',.42)
  m['arrows'].append({'origin':[pos[0]+.18,pos[1],pos[2]],'direction':[-1,0,0],'length':.40,'radius':.036,'color':WHITE})
 else:
  for dx,dy in [(-.58,.4),(.58,.4),(0,.65)]:p(m,[pos[0]+dx,pos[1]+dy,pos[2]-.26],.19,GREY,'cube',.8)
  if received>0:p(m,pos,.43,PURPLE,'cube',.30*received)
  if used>0:
   m['arrows'].append({'origin':[pos[0]+.28,pos[1]-.03,pos[2]],'direction':[-1,0,0],
     'length':.65*max(.04,used),'radius':.048,'color':WHITE})
def packet(m,u,start=BS,end=ES,alpha=1):
 pos=lerp(start,end,u);pos[1]-=.25*math.sin(math.pi*u);pos[2]+=.35*math.sin(math.pi*u)
 p(m,pos,.27,PURPLE,'cube',alpha)
 # This line is explicitly schematic: it encodes a functional link, no source trajectory.
 m['paths'].append({'points':[start,pos],'radius':.023,'color':PURPLE,'opacity':.48*alpha})
 return pos
def connect(m,a,b,color=PURPLE,opacity=.3):m['paths'].append({'points':[a,b],'radius':.022,'color':color,'opacity':opacity})
class Scene:
 def __init__(self):self.gl=WebGLRenderer();self.cache={};self.native_frames=0
 def close(self):self.gl.close()
 def image(self,m):
  k=hashlib.sha256(json.dumps(m,sort_keys=True).encode()).hexdigest()
  if k not in self.cache:
   if len(self.cache)>80:self.cache.clear()
   self.cache[k]=self.gl.render(m);self.native_frames+=1
  return self.cache[k].copy()
 def main(self,t,closing=False):
  m=model();recv=sm(3.65,4.3,t) if not closing else 1;used=sm(5.05,5.8,t) if not closing else 1
  participant(m,BS,True);participant(m,ES,False,recv,used)
  pos=None
  if 1.9<=t<4.25 and not closing:pos=packet(m,sm(1.9,4.15,t),alpha=1-sm(4.05,4.25,t))
  if closing or t>=4.25:connect(m,BS,ES,opacity=.24)
  # Prepared query is non-specific. It contains no private45 or negative answer.
  if closing or t>=4.4:
   q=[ES[0]+.30,1.55,1.75];p(m,q,.19,GREY,'cube',.92)
   progress=sm(4.4,5.0,t) if not closing else 1
   m['paths'].append({'points':[q,lerp(q,ES,progress)],'radius':.024,'color':GREY,'opacity':.6})
  im=self.image(m)
  for pos0,es,en,color in [(BS,'B · Emisor','B · Sender',BLUE),(ES,'E1 · Receptor','E1 · Receiver',WHITE)]:
   x,y=project([pos0[0],pos0[1],pos0[2]+.85]);label(im,(x,y-54),es,46,color,maxw=650);label(im,(x,y-11),en,36,GREY,maxw=650)
  if pos is not None:
   x,y=project(pos);label(im,(x,y+68),'Mensaje / Message',38,PURPLE,maxw=620)
  if not closing and t<1.9:
   x,y=project(BS);label(im,(x,y+153),'Información adquirida',40,AMBER,maxw=620);label(im,(x,y+194),'Acquired information',34,GREY,maxw=620)
  if closing or t>=4.4:
   x,y=project([ES[0]+.30,1.55,1.75]);ImageDraw.Draw(im).line((x,y,1550,315),fill=GREY,width=2)
   label(im,(1650,263),'Consulta genérica',34,GREY,maxw=440);label(im,(1650,303),'Generic query',30,GREY,maxw=440)
  if closing or t>=5.8:
   x,y=project(ES);label(im,(x,y+157),'Uso posterior −',44,PURPLE,maxw=630);label(im,(x,y+201),'Later qualified use −',34,GREY,maxw=630)
  return im
 def schematic_comparison(self,t):
  im=Image.new('RGB',(W,HIGH),BG);u=sm(7.35,9.1,t)
  for panel in range(2):
   # Precisely the same camera, geometry, scale and timing, apart from the control.
   m=model();b=[-1.45,0,1];e=[1.45,0,1]
   m['camera']={'eye':[2,-9,5.4],'target':[0,0,1],'fov':42,'lens_shift':[0,.10]}
   m['bounds']=[[-3,-2,-.5],[3,2,3.2]]
   participant(m,b,True);participant(m,e,False,sm(8.85,9.3,t) if panel==0 else 0,sm(9.35,9.9,t) if panel==0 else 0)
   if t<9.5 and u>0:
    if panel==0:packet(m,u,b,e,1-sm(9.15,9.5,t))
    elif u<.46:packet(m,u,b,e)
    else:
     # Control marker represents the prepared SEM4 cut after formation, not host cleanup.
     block=[-.15,0,1.1];p(m,block,.32,GREY,'cube',.95)
     stop=lerp(b,e,.46);p(m,stop,.21,PURPLE,'cube',1-sm(8.4,9.4,t))
   if panel==1:
    m['boxes'].append({'position':[-.10,0,1.1],'scale':[.075,.58,.58],'color':GREY,'opacity':.66})
    # Remaining receiver activity is not absence, zero output or erased memory.
    p(m,e,.36,BLUE,'cube',.24)
    m['arrows'].append({'origin':[e[0],e[1],e[2]+.24],'direction':[0,0,-1],'length':.52,'radius':.042,'color':GREY})
   image=self.image(m);im.paste(image.crop((480,0,1440,HIGH)),(960*panel,0))
  d=ImageDraw.Draw(im);d.line((960,235,960,830),fill='#35505E',width=2)
  for i,es,en in [(0,'Mensaje intacto','Intact message'),(1,'Interrumpido tras formarse','Interrupted after forming')]:
   label(im,(480+960*i,228),es,44,maxw=850);label(im,(480+960*i,270),en,34,GREY,maxw=850)
  if t>=9.4:
   label(im,(480,742),'Lectura válida −',46,PURPLE,maxw=850);label(im,(480,789),'Qualified read −',36,GREY,maxw=850)
   label(im,(1440,742),'Actividad sin lectura válida',42,GREY,maxw=850);label(im,(1440,789),'Activity; no qualified read',34,GREY,maxw=850)
  return im
 def recorded(self,comparison):
  im=Image.new('RGB',(W,HIGH),BG)
  ids=['07_later_full','07_later_cut'] if comparison else ['07_later_full']
  for i,key in enumerate(ids):
   c=dict(CASES[key]);c['vectors']=True;c['prep_markers']=[]
   c['point_colors']={'31,59,29':PURPLE if i==0 else BLUE}
   m=model_from_case(c,panel=comparison)
   # This observer excludes the distant bank; the data and full source remain intact.
   m['spatial_grid']['opacity']=.055;m['provenance']['representation']='Etapas'
   image=self.image(m)
   if comparison:im.paste(image.crop((480,0,1440,HIGH)),(960*i,0))
   else:im=image
  if comparison:
   d=ImageDraw.Draw(im);d.line((960,235,960,835),fill='#35505E',width=2)
   for i,es,en,out,outen in [(0,'Mensaje intacto','Intact message','Lectura válida −','Qualified read −'),
       (1,'Mensaje interrumpido','Interrupted message','Activo; sin lectura válida','Active; no qualified read')]:
    label(im,(480+960*i,220),es,44,maxw=850);label(im,(480+960*i,264),en,34,GREY,maxw=850)
    label(im,(480+960*i,735),out,44,PURPLE if i==0 else BLUE,maxw=850);label(im,(480+960*i,784),outen,36,GREY,maxw=850)
  else:
   label(im,(960,755),'La información intervino en un uso posterior',48,PURPLE,maxw=1740)
   label(im,(960,804),'Received information affected later use',38,GREY,maxw=1740)
  return im
 def base(self,t):
  if t<7.125:return self.main(t),'Esquema','Información de otro participante','Information from another participant'
  if t<10.6:return self.schematic_comparison(t),'Esquema','¿Qué cambia al interrumpir el mensaje?','What changes when the message is interrupted?'
  if t<12.525:return self.recorded(True),'Etapas','El mismo lector, dos resultados físicos','The same reader, two physical outcomes'
  if t<17.6:return self.main(t,True),'Esquema','Información recibida → utilización posterior','Received information → later use'
  return self.recorded(False),'Registro','Un uso posterior ligado al mensaje','Later use linked to the received message'
 def frame(self,t,preview_subs=False):
  im,kind,es,en=self.base(t)
  for cut in [7.125,10.6,12.525,17.6]:
   if cut<=t<cut+.22:
    old=self.base(cut-.001)[0];im=Image.blend(old,im,sm(cut,cut+.22,t));kind='Transición'
  # All labels stay above the unchanged subtitle safe area.
  label(im,(960,67),es,58,maxw=1700);label(im,(960,120),en,40,GREY,maxw=1730)
  if kind=='Esquema':
   label(im,(56,171),'Esquema explicativo / Illustrative schematic',28,GREY,'lm',1600)
  elif kind=='Transición':label(im,(56,176),'Transición editorial / Editorial transition',28,GREY,'lm',1100)
  else:
   label(im,(56,171),'Etapas registradas / Recorded stages · T16619' if kind=='Etapas' else 'Registro del receptor / Receiver record · T16619',28,GREY,'lm',1600)
  label(im,(1862,25),'IC01 · B → E1 · N67',28,GREY,'rm',850)
  # Identical film-progress reference to the surrounding scenes, no DEE clock.
  ImageDraw.Draw(im).rectangle((0,1077,int(W*(130+t)/300),1079),fill='#41616F')
  if preview_subs:
   for a,b,lines in CUES:
    if a<=t<b:
     for j,line in enumerate(lines):label(im,(960,990-(len(lines)-1-j)*90),line,84,WHITE,maxw=1720)
  return im,kind
def srt_cues():
 import re
 def seconds(s):
  h,m,s=s.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(s)
 out=[]
 for b in re.split(r'\n\s*\n',(H.parent/'DEE_Cognitive_5min_EN.srt').read_text('utf8').strip()):
  x=b.splitlines();a,c=x[1].split(' --> ');a,c=seconds(a),seconds(c)
  if 130<=a<150:out.append((a-130,c-130,x[2:]))
 assert len(out)==6
 return out
CUES=srt_cues()
def preview():
 out=H/'S07_PREVIAS';out.mkdir(exist_ok=True);scene=Scene();rows=[]
 try:
  for i,t in enumerate([.2,1.6,2.6,3.7,4.7,6.2,7.6,8.5,9.8,11.4,12.8,14.8,17.9,19.7]):
   im,k=scene.frame(t,True);p=out/f'P{i:02}_{t:05.2f}.png';im.save(p);rows.append({'t':t,'kind':k,'file':str(p)})
 finally:scene.close()
 sheet=Image.new('RGB',(1920,360*math.ceil(len(rows)/3)),BG)
 for i,r in enumerate(rows):sheet.paste(Image.open(r['file']).resize((640,360),Image.Resampling.LANCZOS),((i%3)*640,(i//3)*360))
 sheet.save(out/'CONTACTO.png');(out/'INDICE.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf8')
 print('14native preview frames',flush=True)
def render():
 out=H/'S07_CORREGIDA_VIDEO_SIN_AUDIO.mp4';assert not out.exists(),'Preserve previous render before replacement.'
 scene=Scene();log=(H/'S07_RENDER.log').open('wb')
 cmd=[str(FF),'-hide_banner','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','30','-i','pipe:0',
 '-an','-vf','ass=subtitles_scene_07.ass,setsar=1','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p',
 '-r','30','-fps_mode','cfr','-g','60','-keyint_min','60','-sc_threshold','0','-video_track_timescale','15360','-frames:v','600',str(out)]
 proc=subprocess.Popen(cmd,cwd=H,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=log,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));hashes=[];classes={};start=time.monotonic()
 try:
  for n in range(600):
   im,k=scene.frame(n/30);b=im.tobytes();hashes.append(hashlib.sha256(b).hexdigest());classes[k]=classes.get(k,0)+1;proc.stdin.write(b)
   if n%150==0:print(n,'/600',round(time.monotonic()-start,1),'s',flush=True)
  proc.stdin.close();assert proc.wait(timeout=180)==0
 finally:
  if proc.poll() is None:proc.terminate();proc.wait(timeout=15)
  scene.close();log.close()
 rec={'file':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'source_canvas':[1920,1080],'frames':600,'duration':20,
 'RGB_sha256_per_frame':hashes,'classification_frames':classes,'native_renderer':scene.gl.info,
 'code_sha256':sha(Path(__file__)),'local_worker_sha256':sha(LOCAL/'render_common.cjs'),'command':cmd,'new_DEE_ticks':0,
 'scope':'S07 only; symbolic functional motion is explicitly labelled, archived fields remain at source sites. No other chapter rendered.'}
 (H/'SELLO_RENDER_S07.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),'utf8');print('Closed600 native frames',out.stat().st_size,flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--preview',action='store_true');ap.add_argument('--render',action='store_true');a=ap.parse_args()
 if a.preview:preview()
 if a.render:render()
