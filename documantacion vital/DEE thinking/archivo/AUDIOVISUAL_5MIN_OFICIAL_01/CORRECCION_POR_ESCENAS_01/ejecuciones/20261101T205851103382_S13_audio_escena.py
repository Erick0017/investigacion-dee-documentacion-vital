"""S13: one ECI02 genealogy, consecutive uses, software roles, partial scope.

The three recorded readers are historical, consecutive states of the same
candidate, not simultaneous fields and not a combination of other CPC lives.
Software plates are editorial diagrams, never regions of the organism.
"""
from escena_base import *

SCENE=13
SAMPLE_TIMES=[.25,1.5,2.8,3.6,4.4,5.5,6.6,7.6,8.9,9.95,10.8,11.65,12.7,13.5,14.6,15.7,16.8,18.0,19.5]

def regions(a):
 # Same full snapshot, different local crops. No transplantation of matter.
 im=a.pair('13_principal_region_1','13_principal_region_2',
  changes_left=dict(focus_prepared=False,prep_markers=[]),
  changes_right=dict(focus_prepared=False,prep_markers=[]),same_camera=False)
 overlay_pair(im,('Región 1 del mismo estado','Region 1 of the same state'),('Región 2 del mismo estado','Region 2 of the same state'),size=40)
 return im

def consecutive(a,t):
 # Each native rendering is downsampled into a chronological comparison.
 # The moving amber border is attention guidance, not a physical change.
 ims=[]
 rows=[('13_LEX_luma','Asociación +','Association +','T725882'),
       ('13_MA_PRE','Memoria −','Memory −','T726150'),
       ('13_comparison','Comparación P0 +','Prepared comparison +','T726213')]
 for id,es,en,tick in rows:
  native=a.case(id,panel=True,vectors=True,focus_prepared=False,prep_markers=[],crop_radius=1.4)
  im=native.crop((480,240,1440,840)).resize((640,400),Image.Resampling.LANCZOS)
  ims.append(im)
 im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
 active=0 if t<5.25 else (1 if t<7.35 else 2)
 for i,(native,row) in enumerate(zip(ims,rows)):
  x=640*i;im.paste(native,(x,305))
  text(im,(x+320,230),row[1],40,PURPLE,maxw=600)
  text(im,(x+320,273),row[2],32,GREY,maxw=600)
  text(im,(x+320,720),row[3],32,GREY,maxw=600)
  if i<2:d.line((x+639,209,x+639,742),fill='#35505E',width=2)
  if i==active:d.rounded_rectangle((x+12,204,x+627,741),radius=14,outline=AMBER,width=3)
 return im

def software(a,t):
 # An explanatory software stack, distinct from the organism's anatomy.
 cam={'eye':[3.0,-10,6.0],'target':[0,0,1.35],'fov':42,'lens_shift':[0,.14]}
 m=model(cam,[[-4,-2,-.5],[4,2,3.6]])
 layers=[(.35,BLUE),(1.45,GREY),(2.55,AMBER)]
 for z,color in layers:
  m['boxes'].append({'position':[-1,0,z],'scale':[1.4,.75,.065],'color':color,'opacity':.35})
  for xx in [-2.2,.2]:wire(m,[xx,0,z],color,.15,.55)
 # Sequential emphasis follows the spoken role. This is editorial, not a
 # measured request packet travelling between physical DEE locations.
 k=0 if t<11.57 else (1 if t<12.92 else 2)
 z,color=layers[k]
 u=smooth([9.89,11.57,12.92][k],[11.0,12.5,14.7][k],t)
 token(m,[-2.05,-.2,z+.16],[-.05,-.2,z+.16],u,color,.17,.05)
 for zz in [.5,1.6]:link(m,[[-1,.52,zz],[-1,.52,zz+.73]],GREY,.020,.32)
 im=a.render(m)
 labels=[(675,'Universe','Dinámica / Dynamics',BLUE),
         (505,'Thinking','Ejecución / Execution',GREY),
         (335,'Cognitive','Accesos y continuidad',AMBER)]
 for i,(y,name,role,col) in enumerate(labels):
  text(im,(1370,y),name,52,col if i==k else GREY,maxw=830)
  text(im,(1370,y+46),role,36,GREY,maxw=830)
 text(im,(1370,426),'Access and continuity',32,GREY,maxw=830)
 return im

def base(a,t):
 if t<3.50:
  return regions(a),dict(mode='Registro',title_es='Una instancia con identidad y estado propios',title_en='One instance with its own identity and state',source='Nuevo corte · ECI02 · N67',phase_es='Dos regiones del mismo mundo guardado',phase_en='Two regions of the same saved world')
 if t<9.89:
  return consecutive(a,t),dict(mode='Etapas',title_es='Tres usos consecutivos en la misma candidata',title_en='Three consecutive uses in the same candidate',source='ECI02 · una trayectoria · N67',phase_es='Consultas preparadas, sin reiniciar la vida',phase_en='Prepared queries without resetting the life',phase_color=AMBER)
 if t<15.59:
  return software(a,t),dict(mode='Esquema',title_es='Tres funciones del software',title_en='Three software roles',source='Arquitectura de software',phase_es='No son partes anatómicas del ente',phase_en='These are not anatomical parts of the entity',phase_color=GREY)
 return regions(a),dict(mode='Registro',title_es='Integración parcial, no suma de todos los ensayos',title_en='Partial integration, not the sum of every trial',source='ECI02 · corte T727225',phase_es='Estado publicado de la misma genealogía',phase_en='Published state of the same genealogy',phase_color=AMBER)

def frame(a,t):
 im,meta=base(a,t)
 for cut in [3.50,9.89,15.59]:
  if cut<=t<cut+.18:
   old=base(a,cut-.001)[0];im=Image.blend(old,im,smooth(cut,cut+.18,t));meta=dict(meta,mode='Transición')
 return im,meta
