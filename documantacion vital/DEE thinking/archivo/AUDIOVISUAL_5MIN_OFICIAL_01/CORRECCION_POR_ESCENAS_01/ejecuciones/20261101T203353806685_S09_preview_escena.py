"""S09 only: consequence-reference-action, then a separately identified external trial.
Schematic motion depicts functional links, not measured routes or fixture geometry.
No simulation, policy, voice synthesis, or engine invocation is performed here.
"""
from pathlib import Path
import sys,math
from PIL import Image
H=Path(__file__).resolve().parent;ROOT=H.parents[1]
sys.path.insert(0,str(ROOT/'herramientas'))
from escena_base import (BLUE,AMBER,PURPLE,WHITE,GREY,model,particle,wire,link,arrow,
 token,smooth,text,overlay_pair,lerp)
SCENE=9
SAMPLE_TIMES=[.8,2.5,4.0,5.6,7.6,10.1,12.1,14.8,16.7,20.3]
CAM={'eye':[2.7,-10,6.1],'target':[0,0,1],'fov':42,'lens_shift':[0,.12]}
def gate(m,x,opened=0,jam=False):
 # Designed environment icon, not a reconstruction of native matter or a robot.
 for dx in [-.65,.65]:m['boxes'].append({'position':[x+dx,.1,.75],'scale':[.07,.12,.88],'color':GREY,'opacity':.9})
 m['boxes'].append({'position':[x,.1,1.65],'scale':[.72,.12,.07],'color':GREY,'opacity':.9})
 m['boxes'].append({'position':[x,.12,.78+opened*1.45],'scale':[.56,.09,.72],
  'color':AMBER if jam else GREY,'opacity':.55})
def reference(m,pos,value):
 wire(m,pos,AMBER,.72)
 height=.15+.50*(value/11)
 m['boxes'].append({'position':[pos[0],pos[1],pos[2]-.55+height],
  'scale':[.43,.40,height],'color':AMBER,'opacity':.62})
def initial(a,t):
 m=model(CAM,[[-5,-2,-.5],[5,2,3.5]])
 ref=[-3,0,1];act=[0,0,1];g=[3.05,0,1]
 reference(m,ref,5+6*smooth(2.65,3.65,t));wire(m,act,PURPLE,.65)
 particle(m,act,.37,PURPLE,alpha=.28);arrow(m,[.25,0,1],[-1,0,0],.55)
 opening=smooth(.85,1.55,t);gate(m,g[0],opening)
 if t<1.7:
  u=smooth(.30,1.15,t);p=token(m,act,g,u,PURPLE,r=.25,arc=.15);link(m,[act,p],PURPLE,alpha=.40)
 if 1.55<=t<3.25:
  u=smooth(1.55,3.05,t);p=token(m,g,ref,u,AMBER,r=.26,arc=.55);link(m,[g,p],AMBER,alpha=.42)
 im=a.render(m)
 for x,es,en,col in [(560,'Referencia','Reference',AMBER),(960,'Acción','Action',PURPLE),(1400,'Consecuencia','Consequence',GREY)]:
  text(im,(x,650),es,42,col,maxw=650);text(im,(x,695),en,32,GREY,maxw=650)
 text(im,(560,310),'5 → 11' if t>=3.3 else '5',44,AMBER,maxw=500)
 return im
def common(a,t):
 ims=[]
 for i,value in enumerate([11,5]):
  cam={'eye':[1.8,-9.3,5.9],'target':[0,0,.9],'fov':42,'lens_shift':[0,.10]}
  m=model(cam,[[-3,-2,-.5],[3,2,3.2]])
  ref=[-1.15,0,1];out=[1.15,0,1];reference(m,ref,value);wire(m,out,PURPLE,.65)
  u=smooth(4.46,6.2,t);p=token(m,[0,1.55,2.1],ref,u,BLUE,r=.25,arc=.12)
  if t>=6.2:
   link(m,[ref,out],AMBER,alpha=.40);particle(m,out,.39,PURPLE,alpha=.28)
   direction=[1,0,0] if i==0 else [-1,0,0]
   arrow(m,[out[0]-.25*direction[0],0,1],direction,.55)
  im=a.render(m);text(im,(755,650),'Referencia '+str(value),38,AMBER,maxw=700)
  text(im,(1160,650),'−' if i==0 else '+',54,PURPLE,maxw=450)
  ims.append(im)
 im=a.panels(ims);overlay_pair(im,('Con retorno','With feedback'),('Sin retorno','Without feedback'))
 text(im,(960,310),'Misma oportunidad actual / Same current opportunity',38,BLUE,maxw=1650)
 return im
def actual_action(a):
 base={'vectors':True,'focus_sites':[[50,35,35]],'prep_markers':[]}
 im=a.pair('09_action_full_1','09_action_omit_1',base,base,True)
 overlay_pair(im,('Con retorno','With feedback'),('Sin retorno','Without feedback'))
 text(im,(480,735),'Acción − · sin atasco',44,PURPLE,maxw=850);text(im,(480,784),'Action − · no jam',34,GREY,maxw=850)
 text(im,(1440,735),'Acción + · atasco',44,PURPLE,maxw=850);text(im,(1440,784),'Action + · jam',34,GREY,maxw=850)
 return im
def external(a,t):
 m=model(CAM,[[-5,-2,-.5],[5,2,3.7]])
 d=[-3.15,0,1];bridge=[-.3,0,1];target=[3.15,0,1]
 wire(m,d,PURPLE,.72);particle(m,d,.40,PURPLE,alpha=.28)
 wire(m,bridge,GREY,.62)
 m['boxes'].append({'position':bridge,'scale':[.42,.29,.33],'color':GREY,'opacity':.45})
 gate(m,target[0]+.15)
 if t<13.2:
  u=smooth(11.95,13.15,t);token(m,d,bridge,u,PURPLE,r=.24,arc=.20)
 elif t<14.35:
  u=smooth(13.2,14.35,t);token(m,bridge,[2.35,0,1],u,PURPLE,r=.24,arc=.20)
 pos=[2.15+.58*smooth(14.0,14.85,t),-.15,.78]
 m['boxes'].append({'position':pos,'scale':[.30,.28,.25],'color':PURPLE,'opacity':.80})
 if t>=14.85:
  wire(m,[2.99,0,.78],WHITE,.32,alpha=.50,thickness=.017)
 if 15.2<=t<17.45:
  u=smooth(15.2,17.35,t);p=token(m,[2.99,0,.78],d,u,AMBER,r=.23,arc=.60);link(m,[[2.99,0,.78],p],AMBER,alpha=.35)
 if t>=17.35:
  # Recorded admission receipt, no measured RAW for this return interface.
  wire(m,[d[0],-.9,1],AMBER,.35,alpha=.75,thickness=.017)
 im=a.render(m)
 for x,es,en in [(560,'Salida DEE','DEE output'),(960,'Puente preparado','Prepared bridge'),(1400,'Servicio externo','External service')]:
  text(im,(x,650),es,40,maxw=650);text(im,(x,693),en,32,GREY,maxw=650)
 if t>=14.85:
  text(im,(1440,300),'Contacto, sin completar tarea',34,GREY,maxw=800)
  text(im,(1440,338),'Contact; task incomplete',28,GREY,maxw=800)
 if t>=17.35:
  text(im,(510,730),'Retorno admitido',38,AMBER,maxw=700);text(im,(510,774),'Admitted feedback',30,GREY,maxw=700)
 return im
def raw(a,t):
 if t<4.46:return initial(a,t),dict(mode='Esquema',title_es='Una acción cambia la experiencia posterior',title_en='An action changes later experience',source='Nuevo ensayo · Ciclo02 · N67')
 if t<8.74:return common(a,t),dict(mode='Esquema',title_es='La referencia conserva la consecuencia',title_en='The reference retains the consequence',source='Ciclo02 · C02_GATE · N67')
 if t<11.665:return actual_action(a),dict(mode='Etapas',title_es='La historia cambia una actuación posterior',title_en='History changes a later action',source='Ciclo02 · T17510 · N67')
 return external(a,t),dict(mode='Esquema',title_es='Otro ensayo: actuación y retorno',title_en='Another trial: action and feedback',source='Nuevo ensayo · EO01 · N26')
def frame(a,t):
 im,meta=raw(a,t)
 for cut in [4.46,8.74,11.665]:
  if cut<=t<cut+.20:
   im=Image.blend(raw(a,cut-.001)[0],im,smooth(cut,cut+.20,t));meta={**meta,'mode':'Transición'}
 return im,meta
