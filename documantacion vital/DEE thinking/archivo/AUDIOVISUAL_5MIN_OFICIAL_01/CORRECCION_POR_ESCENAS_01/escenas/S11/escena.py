"""S11 only: distinguish teaching/experience, later cue, and a retained native use.

Schematic bands denote a history-dependent functional relation, never a claim
that the named reader cell stayed occupied: that actual site is RAW0 atT139.
No literal Spanish word is asserted to exist in a physical DEE field.
"""
from escena_base import *
import numpy as np
SCENE=11
SAMPLE_TIMES=[.25,1.5,2.8,3.8,4.9,5.8,6.6,7.6,9.0,10.5,11.9,13.1,14.3,15.6,17.3,18.6]
CAM={'eye':[2.3,-9.4,6.3],'target':[0,0,1.0],'fov':42,'lens_shift':[0,.13]}

def project(pos):
 eye=np.array(CAM['eye']);z=eye-np.array(CAM['target']);z=z/np.linalg.norm(z)
 x=np.cross([0,0,1],z);x=x/np.linalg.norm(x);y=np.cross(z,x);d=np.array(pos)-eye;depth=-d@z
 f=1/math.tan(math.radians(CAM['fov']/2));return ((d@x*f/(1920/1080)/depth+1)*960,(1-d@y*f/depth-.13)*540)

def support(m,history=0):
 wire(m,[0,0,1],GREY,.95,.58)
 # These three supports are an icon of the organization, not a recovered anatomy.
 for q in [[-.55,.45,.65],[0,.6,.65],[.55,.45,.65]]:particle(m,q,.20,GREY,'cube',.78)
 if history>0:
  for q in [[-.74,-.25,1.0],[0,-.25,1.0],[.74,-.25,1.0]]:particle(m,q,.17,AMBER,'cube',.80*history)

def signal_shape(m,pos,alpha=1):
 particle(m,pos,.26,BLUE,'cube',alpha)
 m['particles'][-1]['rotation_z']=math.pi/4

def pairing(a,t):
 m=model(CAM,[[-5,-2,-.6],[5,2,3.2]]);support(m,smooth(1.4,2.8,t))
 cue=[-3.1,1.0,1.65];prior=[-3.1,-1.0,.75];center=[0,0,1]
 wire(m,cue,BLUE,.43,.6);signal_shape(m,cue)
 wire(m,prior,AMBER,.43,.6);arrow(m,[prior[0]+.20,prior[1],prior[2]],[-1,0,0],.43,AMBER)
 u=smooth(.55,2.15,t)
 if .55<t<2.25:
  q=lerp(cue,center,u);q[2]+=.25*math.sin(math.pi*u);signal_shape(m,q)
  token(m,prior,center,u,AMBER,.18,.15)
 if t>=1.8:link(m,[cue,center],BLUE,.024,.42);link(m,[prior,center],AMBER,.024,.42)
 im=a.render(m)
 text(im,(425,295),'Señal docente',42,BLUE,maxw=550);text(im,(425,337),'Teaching cue',34,GREY,maxw=550)
 text(im,(385,668),'Uso previo',42,AMBER,maxw=550);text(im,(385,709),'Prior use',34,GREY,maxw=550)
 text(im,(1150,660),'Asociación por experiencia',44,AMBER,maxw=1000);text(im,(1150,705),'Association through experience',34,GREY,maxw=1000)
 return im

def later(a,t,recap=False):
 m=model(CAM,[[-5,-2,-.6],[5,2,3.2]]);support(m,1)
 cue=[-3.1,0,1.30];core=[0,0,1];reader=[3.05,0,.95]
 wire(m,cue,BLUE,.43,.6);signal_shape(m,cue);wire(m,reader,GREY,.53,.60)
 local=t-4.65 if not recap else 2.4
 u=smooth(.1,1.0,local)
 if not recap and .1<local<1.1:
  q=lerp(cue,core,u);q[2]+=.25*math.sin(math.pi*u);signal_shape(m,q)
 if local>=.8:link(m,[cue,core],BLUE,.025,.42)
 v=smooth(.95,1.8,local)
 if .95<local<1.85 and not recap:token(m,core,reader,v,PURPLE,.22,.15)
 if local>=1.55 or recap:
  link(m,[core,reader],PURPLE,.025,.45);particle(m,reader,.34,PURPLE,'cube',.30)
  arrow(m,[reader[0]+.24,reader[1]+.14,reader[2]],[-1,-1,0],.62,WHITE)
 im=a.render(m)
 text(im,(400,300),'Señal posterior',42,BLUE,maxw=650);text(im,(400,342),'Later cue',34,GREY,maxw=650)
 text(im,(965,660),'Organización con historia',42,AMBER,maxw=1050);text(im,(965,702),'Organization with a history',34,GREY,maxw=1050)
 if local>=1.55 or recap:
  text(im,(1530,658),'Respuesta −',42,PURPLE,maxw=600);text(im,(1530,701),'Related response −',34,GREY,maxw=600)
 return im

def codec(a,t):
 m=model(CAM,[[-5,-2,-.6],[5,2,3.2]])
 source=[-3.2,0,1.15];encoder=[0,0,1.15];entry=[3.2,0,1.15]
 wire(m,encoder,GREY,.77,.65);wire(m,entry,BLUE,.5,.60)
 particle(m,source,.48,GREY,'cube',.24)
 v=smooth(8.8,10.2,t)
 if v>0:signal_shape(m,lerp(encoder,entry,v))
 link(m,[source,encoder],GREY,.025,.5)
 if v>.1:link(m,[encoder,lerp(encoder,entry,v)],BLUE,.025,.5)
 im=a.render(m)
 text(im,(400,360),'Palabra',46,WHITE,maxw=650);text(im,(400,406),'Word',36,GREY,maxw=650)
 text(im,(965,660),'Codificación preparada',44,GREY,maxw=1050);text(im,(965,705),'Prepared external encoding',34,GREY,maxw=1050)
 text(im,(1510,356),'Entrada',46,BLUE,maxw=650);text(im,(1510,402),'Input',36,GREY,maxw=650)
 return im

def data(a,id):
 return a.case(id,vectors=True,focus_prepared=False,prep_markers=[],focus_sites=[[36,5,49]])

def base(a,t):
 source='Nuevo ensayo · U0 · N67'
 if t<3.35:
  return pairing(a,t),dict(mode='Esquema',title_es='Una señal se vincula con un uso',title_en='A cue becomes linked to a use',source=source)
 if t<4.65:
  return data(a,'11_cue_75'),dict(mode='Etapas',title_es='La experiencia dejó una asociación',title_en='Experience formed an association',source='U0 · T75',phase_es='Asociación registrada',phase_en='Recorded association')
 if t<7.0:
  return later(a,t),dict(mode='Esquema',title_es='Más tarde llega la señal, sin repetir la enseñanza',title_en='Later the cue arrives without reteaching',source='U0 · señal posterior')
 if t<8.65:
  return data(a,'11_cue_142'),dict(mode='Registro',title_es='La consulta permite una respuesta relacionada',title_en='The query recovers a related response',source='U0 · T139 → T142',phase_es='Lectura válida −',phase_en='Qualified response −')
 if t<11.42:
  return codec(a,t),dict(mode='Esquema',title_es='El programa convierte palabras en entradas',title_en='The program converts words into inputs',source='Codificador externo / Host codec')
 if t<14.95:
  return later(a,t,True),dict(mode='Esquema',title_es='Adquirir y utilizar una relación concreta',title_en='Acquiring and using a specific relation',source='U0 · recapitulación / Recap')
 return data(a,'11_cue_142'),dict(mode='Registro',title_es='Uso funcional concreto',title_en='A specific functional use',source='U0 · T142',phase_es='No es conversación libre',phase_en='Not free conversation',phase_color=AMBER)

def frame(a,t):
 im,meta=base(a,t)
 for cut in [3.35,4.65,7.,8.65,11.42,14.95]:
  if cut<=t<cut+.18:
   old=base(a,cut-.001)[0];im=Image.blend(old,im,smooth(cut,cut+.18,t));meta=dict(meta,mode='Transición')
 return im,meta
