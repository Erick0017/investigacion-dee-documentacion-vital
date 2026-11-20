"""Native 1080p editorial renderer built on the accepted pilot's WebGL2.

Recorded sites never interpolate. Crossfades are editorial stage changes.
Prepared interfaces remain hollow. Direction glyphs annotate recorded vectors,
not reconstructed trajectories. Nothing in this module imports DEE.
"""
from pathlib import Path
from collections import OrderedDict
import sys,json,math,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'render'))
from renderer_r05 import WebGLRenderer
W,H,FPS=1920,1080,30
BG='#07131D';BLUE='#46C7EB';AMBER='#F4C46B';PURPLE='#B89BE8';WHITE='#E8F4F3';GREY='#8BA1AD'
FONT=Path(r'C:\Windows\Fonts\segoeui.ttf')
FONTS={s:ImageFont.truetype(str(FONT),s) for s in (28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60,64,68,72,78,84)}
def smooth(a,b,t):
 u=max(0,min(1,(t-a)/(b-a)));return u*u*(3-2*u)
def site(p):return p.get('site',p.get('position'))
def nonzero(p):return str(p.get('raw',p.get('rawstr','0')))!='0'
def prepared_sites(c):
 out=[]
 for p in c.get('prep_markers',[]):
  q=p if isinstance(p,(list,tuple)) else p.get('site')
  if q is not None and len(q)==3:out.append(list(q))
 return out
def roi(points,center,radius):
 return [p for p in points if max(abs(float(x)-float(y)) for x,y in zip(site(p),center))<=radius]
def clone_case(c,**kwargs):
 d=dict(c);d.update(kwargs);return d

def camera_for(sites,az=38,el=30,panel=False,zoom=1):
 if not sites:sites=[[0,0,0]]
 lo=np.min(np.array(sites,dtype=float),axis=0)-.48
 hi=np.max(np.array(sites,dtype=float),axis=0)+.48
 center=(lo+hi)/2
 az=math.radians(az);el=math.radians(el)
 outward=np.array([math.cos(el)*math.cos(az),math.cos(el)*math.sin(az),math.sin(el)])
 right=np.array([-outward[1],outward[0],0]);right/=np.linalg.norm(right)
 up=np.cross(outward,right)
 tangent=math.tan(math.radians(42)/2)
 corners=[np.array([x,y,z])-center for x in (lo[0],hi[0]) for y in (lo[1],hi[1]) for z in (lo[2],hi[2])]
 width=.43 if panel else .79
 height=.40 if panel else .49
 distance=max(max(abs(float(p@right))/(tangent*(W/H)*width),abs(float(p@up))/(tangent*height))+float(p@outward) for p in corners)
 distance=max(distance,2.8)*zoom
 return {'eye':(center+outward*distance).tolist(),'target':center.tolist(),'fov':42,'lens_shift':[0,.13]},[lo.tolist(),hi.tolist()]

def hollow(boxes,q,color=GREY,alpha=.20,size=.48,thickness=.006):
 for axis in range(3):
  others=[j for j in range(3) if j!=axis]
  for u in (-size,size):
   for v in (-size,size):
    pos=list(q);pos[others[0]]+=u;pos[others[1]]+=v
    scale=[thickness]*3;scale[axis]=size
    boxes.append({'position':pos,'scale':scale,'color':color,'opacity':alpha})

def model_from_case(c,panel=False,zoom=1):
 points=c.get('points',[]);focus=c.get('focus_sites') or [site(p) for p in points]
 prep=prepared_sites(c)
 if not focus:focus=prep or [[0,0,0]]
 camera,bounds=camera_for(focus,c.get('azimuth',38),c.get('elevation',30),panel,zoom)
 render_points=points
 # Cropping affects this observer only, never the saved world.
 if c.get('crop_radius'):
  ctr=np.mean(focus,axis=0);render_points=roi(points,ctr,c['crop_radius'])
 elif len(focus)<20:
  lower=np.min(focus,axis=0)-2;upper=np.max(focus,axis=0)+2
  render_points=[p for p in points if all(lower[i]<=site(p)[i]<=upper[i] for i in range(3))]
 particles=[];boxes=[];arrows=[]
 focused={tuple(s) for s in focus}
 marker_roles=c.get('point_colors',{})
 for p in render_points:
  q=site(p)
  if not q or not nonzero(p):continue
  active=int(p.get('state',0))!=0
  role=str(p.get('role',''))
  color=marker_roles.get(','.join(map(str,q)))
  if color is None:
   color=PURPLE if tuple(q) in focused else (AMBER if 'teach' in role or 'memory' in role or 'reference' in role else BLUE)
  if not active:
   hollow(boxes,q,GREY,.16,.36,.009)
  else:
   support=int(p.get('semantic',1))==4
   shape=c.get('point_shapes',{}).get(','.join(map(str,q)),'cube' if support or tuple(q) in focused else 'sphere')
   alpha=.28 if c.get('vectors') and tuple(q) in focused and not support else (.72 if support else 1)
   particles.append({'position':q,'radius':.34 if support else .39,'shape':shape,
                     'color':GREY if support else color,'opacity':alpha})
   if c.get('vectors') and tuple(q) in focused and any(p.get('direction',[0,0,0])):
    direction=p['direction'];norm=math.sqrt(sum(x*x for x in direction));u=[x/norm for x in direction]
    arrows.append({'origin':[q[i]-.24*u[i] for i in range(3)],'direction':direction,'length':.58,'radius':.045,'color':WHITE})
 for q in focus:hollow(boxes,q,'#88AEBB',.11,.49,.004)
 for q in prep:hollow(boxes,q,AMBER,.66,.46,.012)
 lo,hi=bounds
 # The floor/grid are declared editorial coordinate references, not DEE matter.
 minz=min([q[2] for q in focus]+[q[2] for q in prep] or [0])-.65
 minx=min(lo[0],*(q[0]-.6 for q in prep)) if prep else lo[0]
 maxx=max(hi[0],*(q[0]+.6 for q in prep)) if prep else hi[0]
 miny=min(lo[1],*(q[1]-.6 for q in prep)) if prep else lo[1]
 maxy=max(hi[1],*(q[1]+.6 for q in prep)) if prep else hi[1]
 bounds=[[minx-2,miny-2,minz],[maxx+2,maxy+2,max(hi[2],minz+3)]]
 return {'camera':camera,'bounds':bounds,'grid':False,
   'spatial_grid':{'step':1,'plane_z':minz,'opacity':.13,'color':'#476B7B','verticals':False},
   'ground':{'z':minz-.04,'color':'#10232E','opacity':.62},
   'particles':particles,'boxes':boxes,'arrows':arrows,'labels':[],
   'provenance':{'representation':'Esquema' if str(c.get('classification','')).startswith('Esquema') else 'Etapas'}}

class ArtRenderer:
 def __init__(self):self.native=WebGLRenderer();self.cache=OrderedDict();self.rendered=0
 def close(self):self.native.close()
 def world(self,c,panel=False,zoom=1):
  model=model_from_case(c,panel,zoom)
  key=hashlib.sha256(json.dumps(model,sort_keys=True,separators=(',',':')).encode()).hexdigest()
  if key in self.cache:
   im=self.cache.pop(key);self.cache[key]=im
  else:
   im=self.native.render(model);self.rendered+=1;self.cache[key]=im
   if len(self.cache)>48:self.cache.popitem(last=False)
  return im.copy()
 def view(self,spec,progress=1):
  if spec.get('kind')=='architecture':return self.architecture(progress)
  if spec.get('kind')=='service':return self.service(spec)
  if spec.get('kind')=='comparison_schema':return self.comparison_schema()
  cases=spec['cases']
  if len(cases)==1:
   z=1.04-.04*smooth(0,1,min(progress*3,1)) if spec.get('push') else 1
   image=self.world(cases[0],False,z)
  else:
   image=Image.new('RGB',(W,H),BG)
   for i,c in enumerate(cases[:2]):
    # Each is an independent native 1920px render, cropped at1:1 into its viewport.
    im=self.world(c,True)
    image.paste(im.crop((480,0,1440,H)),(960*i,0))
   d=ImageDraw.Draw(image);d.line((960,190,960,820),fill='#35505E',width=2)
  return image
 def architecture(self,p):
  # Schematic software roles, explicitly not an anatomy or DEE field snapshot.
  camera,bounds=camera_for([[-1.8,-.6,0],[1.8,.6,3.0]],az=38,el=23)
  boxes=[]
  for z,color in [(0,BLUE),(1.5,AMBER),(3,PURPLE)]:boxes.append({'position':[0,0,z],'scale':[1.8,.7,.20],'color':color,'opacity':.82})
  m={'camera':camera,'bounds':[[-4,-3,-1],[4,3,5]],'boxes':boxes,'particles':[],
   'spatial_grid':{'step':1,'plane_z':-.6,'opacity':.12},'ground':{'z':-.65,'opacity':.6},'provenance':{'representation':'Esquema'}}
  key='architecture';im=self.cache.get(key)
  if im is None:im=self.native.render(m);self.cache[key]=im
  return im.copy()
 def service(self,spec):
  # The external apparatus is an explanatory model of archived events, no new simulator.
  q=[[0,0,0],[3.5,0,0],[7,0,0]];camera,bounds=camera_for(q,az=30,el=20)
  boxes=[]
  for pos,color in zip(q,[BLUE,GREY,PURPLE]):hollow(boxes,pos,color,.72,.7,.018)
  particles=[{'position':q[0],'radius':.42,'shape':'cube','color':BLUE},
             {'position':q[-1],'radius':.42,'shape':'cube','color':PURPLE}]
  m={'camera':camera,'bounds':bounds,'boxes':boxes,'particles':particles,
     'spatial_grid':{'step':1,'plane_z':-1,'opacity':.13},'ground':{'z':-1.05,'opacity':.6},'provenance':{'representation':'Esquema'}}
  key='service';im=self.cache.get(key)
  if im is None:im=self.native.render(m);self.cache[key]=im
  return im.copy()
 def comparison_schema(self):
  # Prepared functional roles from the documented expected/current comparator.
  # Positions are an explicitly labelled diagram, not a claimed physical layout.
  pts=[[-1.4,0,1],[1.4,0,1],[0,0,-.7]]
  camera,bounds=camera_for(pts,az=38,el=23)
  boxes=[]
  for pos,color in zip(pts,[AMBER,BLUE,PURPLE]):
   boxes.append({'position':pos,'scale':[.6,.6,.4],'color':color,'opacity':.88})
  m={'camera':camera,'bounds':[[-4,-3,-2],[4,3,3]],'boxes':boxes,'particles':[],
     'spatial_grid':{'step':1,'plane_z':-1.4,'opacity':.12},'ground':{'z':-1.45,'opacity':.6},'provenance':{'representation':'Esquema'}}
  key='comparison_schema';im=self.cache.get(key)
  if im is None:im=self.native.render(m);self.cache[key]=im
  return im.copy()

def text(d,xy,s,size=54,color=WHITE,anchor='mm',maxwidth=1720):
 while size>34 and d.textlength(s,font=FONTS.get(size,FONTS[54]))>maxwidth:
  sizes=sorted(FONTS);size=max(x for x in sizes if x<size)
 d.text(xy,s,font=FONTS[size],fill=color,anchor=anchor,stroke_width=2,stroke_fill=BG)

def decorate(image,spec,scene,local_t,case_new=False):
 d=ImageDraw.Draw(image)
 klass=spec.get('classification','Etapas')
 badge={'Registro':'Registro · Recorded','Etapas':'Etapas · Stages','Esquema':'Esquema · Diagram'}.get(klass,'Etapas · Stages')
 text(d,(62,48),badge,30,GREY,'lm',420)
 text(d,(960,63),spec.get('header_es',''),64)
 if spec.get('header_en'):text(d,(960,116),spec['header_en'],48,GREY)
 case=spec.get('case_tag','')
 if case:text(d,(1858,48),case,30,GREY,'rm',460)
 if case_new or spec.get('new_trial'):
  text(d,(1858,98),'Nuevo ensayo · New trial',32,GREY,'rm',520)
 if len(spec.get('cases',[]))>1:
  for i,c in enumerate(spec['cases'][:2]):
   text(d,(480+960*i,178),c.get('short_es',c.get('label_es','')),46,WHITE,maxwidth=850)
   if c.get('short_en'):text(d,(480+960*i,213),c['short_en'],46,GREY,maxwidth=850)
   out=c.get('output_es','');en=c.get('output_en','')
   if out:text(d,(480+960*i,752),out,52,PURPLE,maxwidth=850)
   if en and en!=out:text(d,(480+960*i,799),en,42,WHITE,maxwidth=850)
 else:
  if spec.get('phase_es'):text(d,(960,762),spec['phase_es'],52,AMBER)
  if spec.get('phase_en'):text(d,(960,808),spec['phase_en'],46,GREY)
 if spec.get('kind')=='architecture':
  # Role labels are editorial; their relative screen positions do not claim anatomy.
  for y,s,en in [(350,'Cognitive','Acceso y continuidad · Access & continuity'),(510,'Thinking','Ejecución · Execution'),(665,'Universe','Dinámica · Dynamics')]:
   text(d,(960,y),s,60);text(d,(960,y+48),en,36,GREY)
 if spec.get('kind')=='service':
  for x,s,en in [(435,'Salida DEE','DEE output'),(960,'Puente preparado','Prepared bridge'),(1485,'Servicio','Service')]:
   text(d,(x,675),s,46);text(d,(x,719),en,34,GREY)
 if spec.get('kind')=='comparison_schema':
  for xy,s,en in [((620,385),'Información previa','Earlier information'),((1320,385),'Información actual','Current information'),((960,660),'Comparación preparada','Prepared comparison')]:
   text(d,xy,s,48);text(d,(xy[0],xy[1]+44),en,34,GREY)
 # A subtle continuous progress mark is editorial film time, not a DEE clock.
 d.rectangle((0,H-3,int(W*(scene['start_s']+local_t)/300),H),fill='#41616F')
 return image
