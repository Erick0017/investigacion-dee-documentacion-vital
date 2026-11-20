"""S04 only. Two documented taught histories, a common query, distinct uses.

Schematic support icons and teaching/query motion are functional illustrations,
not measured anatomy, spatial routes, or an untrained control. Exact native
readers follow under Etapas. No DEE execution, audio or subtitle modification.
"""
from pathlib import Path
import sys,json,copy,math
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parents[1]/'herramientas'))
from escena_base import *
SCENE=4
SAMPLE_TIMES=[.4,1.3,2.6,4.3,5.5,6.5,7.9,9.2,12.4,14.5,16.6,19.2,22.3]
CAM={'eye':[1.6,-7.2,5.4],'target':[0,0,1],'fov':42,'lens_shift':[0,.12]}
def core(m,direction,amount=1):
 wire(m,[0,0,1],AMBER,size=.70,alpha=.52)
 for q in [[-.78,.62,.45],[.78,.62,.45],[0,.82,1.6]]:particle(m,q,.18,GREY,'cube',.66)
 if amount>0:
  particle(m,[0,0,1],.43,AMBER,'cube',.29*amount)
  arrow(m,[0,-.02,1],direction,length=.58,color=WHITE,r=.047)
def history_panel(a,t,sign):
 m=model(CAM,[[-3,-2,-.5],[3,2,3.1]])
 d=[0,sign,0] if t<7.0 else [-1,sign,0]
 core(m,d,smooth(1.9,2.65,t))
 if .45<t<2.65:
  u=smooth(.45,2.40,t)
  token(m,[-1.8,-.45,1.30],[0,0,1],u,BLUE,r=.25,arc=.18)
  q=lerp([1.8,.45,1.30],[0,0,1],u);q[2]+=.18*math.sin(math.pi*u)
  particle(m,q,.28,AMBER,'cube',.32)
  arrow(m,[q[0],q[1]-.15*sign,q[2]],[0,sign,0],length=.35,color=WHITE,r=.033)
 if t>=2.65:
  link(m,[[-1.8,-.45,1.30],[0,0,1]],BLUE,r=.018,alpha=.20)
 if 4.95<t<7.20:
  u=smooth(4.95,6.85,t);token(m,[-1.8,-.75,1.45],[0,0,1],u,BLUE,r=.27,arc=.24)
 if t>=7.0:
  particle(m,[0,0,1],.43,PURPLE,'cube',.27)
  arrow(m,[.18,0,1],[-1,sign,0],length=.78,color=WHITE,r=.047)
 return a.render(m)
def illustrate(a,t):
 im=a.panels([history_panel(a,t,-1),history_panel(a,t,1)])
 overlay_pair(im,('Historia 1','History 1'),('Historia 2','History 2'))
 if t<2.65:
  for i,s in enumerate(['−','+']):text(im,(480+960*i,740),'Experiencia de contenido '+s,44,AMBER,maxw=850);text(im,(480+960*i,790),'Experience with content '+s,34,GREY,maxw=850)
 elif t<4.95:
  for i in range(2):text(im,(480+960*i,740),'Cambio adquirido',44,AMBER,maxw=850);text(im,(480+960*i,790),'Acquired change',34,GREY,maxw=850)
 elif t<7.0:
  for i in range(2):text(im,(480+960*i,740),'La misma consulta',44,BLUE,maxw=850);text(im,(480+960*i,790),'The same query',34,GREY,maxw=850)
 else:
  for i,s in enumerate(['−','+']):text(im,(480+960*i,740),'Uso posterior '+s,46,PURPLE,maxw=850);text(im,(480+960*i,790),'Later use '+s,36,GREY,maxw=850)
 return im
def measured(a):
 models=[a.case_model(x,panel=True,vectors=True,prep_markers=[]) for x in ['04_AB_minus_338','04_BA_plus_338']]
 # Both readers occupy the exact same source site; use the identical native
 # single-case camera, avoiding the double padding of wire-box corner bounds.
 for m in models:m['camera']=copy.deepcopy(models[0]['camera'])
 im=a.panels([a.render(m) for m in models])
 overlay_pair(im,('Historia 1','History 1'),('Historia 2','History 2'))
 for i,s in enumerate(['−','+']):text(im,(480+960*i,740),'Lectura '+s,48,PURPLE,maxw=850);text(im,(480+960*i,790),'Qualified read '+s,36,GREY,maxw=850)
 return im
def repertoire(a,t):
 # Four functional contents are backed by the acquired L03 and three documented
 # witnesses BEFORE revision. Their display layout is explicitly schematic.
 d=json.loads((OLD/'fuentes/ESCENAS_03_05_10_13.json').read_text('utf8'))['scenes']['S05']
 ws=d['controls']['witnesses'][:3];assert all(w['before']['covered'] for w in ws)
 m=model({'eye':[3,-8,6],'target':[0,0,1],'fov':42,'lens_shift':[0,.12]},[[-3,-2,-.5],[3,2,3.3]])
 coords=[[-1.25,-.65,1],[1.25,-.65,1],[-1.25,1.0,1],[1.25,1.0,1]]
 dirs=[[-1,-1,0]]+[w['before']['physical']['direction'] for w in ws]
 for i,(q,direction) in enumerate(zip(coords,dirs)):
  wire(m,q,AMBER if i==0 else GREY,size=.56,alpha=.48)
  particle(m,q,.34,PURPLE,'cube',.29)
  arrow(m,[q[0]+.20,q[1],q[2]],direction,length=.53,color=WHITE,r=.04)
 im=a.render(m)
 text(im,(960,740),'L03 y tres testigos documentados',44,PURPLE,maxw=1740)
 text(im,(960,790),'L03 and three documented witnesses',34,GREY,maxw=1740)
 return im
def base(a,t):
 if t<8.55:return illustrate(a,t),{'mode':'Esquema','title_es':'La experiencia cambia el uso posterior','title_en':'Experience changes later use','source':'U0 · dos historias / two histories'}
 if t<13.94:return measured(a),{'mode':'Etapas','title_es':'Misma consulta, respuestas distintas','title_en':'Same query, different responses','source':'U0 · T335 → T338 · N67'}
 if t<17.3:return repertoire(a,t),{'mode':'Esquema','title_es':'Relaciones disponibles en un repertorio','title_en':'Relations available in a repertoire','source':'U0 · Historia 1 / History 1'}
 im=a.case('04_AB_minus_338',vectors=True,prep_markers=[])
 return im,{'mode':'Registro','title_es':'Conservar y acceder son pruebas distintas','title_en':'Retention and access are different tests','source':'U0 · T338','phase_es':'La lectura aquí sí está comprobada','phase_en':'This readout is verified; access is not universally guaranteed'}
def frame(a,t):
 im,meta=base(a,t)
 for cut in [8.55,13.94,17.3]:
  if cut<=t<cut+.20:
   old=base(a,cut-.001)[0];im=Image.blend(old,im,smooth(cut,cut+.20,t));meta=dict(meta,mode='Transición')
 return im,meta
