"""S12: history changes first action, not a universally useful policy.

Every moving token here is an explicitly pedagogical schematic. EO02 N26
readings and FI01 N67 readings are separate existing experiments. In the
opposite-rule trained condition, output + is retained from T125495, while
the actual three reader fields are all empty at T125496.
"""
from escena_base import *

SCENE=12
SAMPLE_TIMES=[.25,1.1,2.3,3.15,4.4,5.7,7.1,7.9,8.8,9.8,10.6,11.7,12.9,13.5,14.7,15.8,16.7,18.1,19.6,20.6]
CAM={'eye':[1.2,-9.5,6.0],'target':[0,0,1.0],'fov':40,'lens_shift':[0,.14]}

def organism(m,history=True):
 wire(m,[0,0,1.0],GREY,1.0,.62)
 for x in [-.50,.50]:
  particle(m,[x,.22,.85],.24,AMBER if history else GREY,'cube',.74)
  wire(m,[x,.22,.85],GREY,.52,.4)
 particle(m,[0,-.28,1.14],.18,GREY,'cube',.58)

def introduction(a,t):
 # Two different histories, shown at matching scale; no physical path claim.
 ims=[]
 for history,sgn in [(True,1),(False,-1)]:
  m=model(CAM,[[-3,-2,-.5],[3,2,2.8]]);organism(m,history)
  # Blue frame stands for the second, externally prepared context.
  for x in [-1.5,1.5]:wire(m,[x,.58,1],BLUE,.64,.38)
  u=smooth(.55,2.1,t)
  if u>0:
   dest=[sgn*1.45,-.55,.95]
   token(m,[0,-.25,1.0],dest,u,PURPLE,.23,.20)
   if u>.6:arrow(m,dest,[sgn,0,0],.48,PURPLE,.055)
  ims.append(a.render(m))
 im=a.panels(ims)
 overlay_pair(im,('Retorno previo recibido','Prior feedback received'),('Retorno previo omitido','Prior feedback omitted'),size=42)
 text(im,(480,674),'Primera acción +',44,PURPLE,maxw=820)
 text(im,(1440,674),'Primera acción −',44,GREY,maxw=820)
 text(im,(960,756),'Otro contexto, antes de su nueva consecuencia',46,WHITE,maxw=1750)
 text(im,(960,803),'Another context, before its new feedback',36,GREY,maxw=1750)
 return im

def first_data(a):
 im=a.pair('12_first_trained','12_first_control',
  changes_left=dict(vectors=True,focus_prepared=False,prep_markers=[]),
  changes_right=dict(vectors=True,focus_prepared=False,prep_markers=[]))
 overlay_pair(im,('Con experiencia: +','With experience: +'),('Control: −','Control: −'),size=44)
 text(im,(480,708),'Cumplió la tarea',42,PURPLE,maxw=800)
 text(im,(1440,708),'No cumplió la tarea',42,GREY,maxw=800)
 return im

def rule_diagram(a,t):
 # A task icon, not a reconstruction of EO02 material routes or distances.
 # The useful side is fixed for this opposite-rule context before action.
 ims=[]
 u=smooth(7.9,9.25,t)
 for history,sgn in [(True,1),(False,-1)]:
  m=model(CAM,[[-3,-2,-.5],[3,2,2.8]]);organism(m,history)
  for side in [-1,1]:
   dest=[side*1.55,-.45,.9]
   wire(m,dest,BLUE if side==-1 else GREY,.72,.75)
   if side==1:
    # X is an editorial outcome mark, never a native obstruction claim.
    link(m,[[1.3,-.60,.65],[1.8,-.60,1.15]],GREY,.035,.8)
    link(m,[[1.3,-.60,1.15],[1.8,-.60,.65]],GREY,.035,.8)
  token(m,[0,-.25,1], [sgn*1.55,-.45,.9],u,PURPLE,.23,.18)
  if u>.8:arrow(m,[sgn*1.55,-.45,.9],[sgn,0,0],.46,PURPLE)
  ims.append(a.render(m))
 im=a.panels(ims)
 overlay_pair(im,('Historia transferida: +','Transferred history: +'),('Control: −','Control: −'),size=42)
 if u>.7:
  text(im,(480,690),'No cumplió la tarea',42,AMBER,maxw=820)
  text(im,(1440,690),'Cumplió la tarea',42,PURPLE,maxw=820)
 return im

def opposite_data(a):
 im=a.pair('12_opposite_trained','12_opposite_control',
  changes_left=dict(vectors=True,focus_prepared=False,prep_markers=[]),
  changes_right=dict(vectors=True,focus_prepared=False,prep_markers=[]))
 overlay_pair(im,('Salida previa +','Previous output +'),('Salida actual −','Current output −'),size=44)
 text(im,(480,650),'Retenida desde T125495',38,AMBER,maxw=850)
 text(im,(480,693),'Lector vacío en T125496',36,GREY,maxw=850)
 text(im,(1440,690),'Cumplió la tarea',42,PURPLE,maxw=820)
 return im

def aggregate_diagram(a,t):
 m=model({'eye':[3,-10,6.4],'target':[0,0,1.1],'fov':42,'lens_shift':[0,.13]},[[-5,-2,-.5],[5,2,3.0]])
 center=[.4,0,1.05];wire(m,center,GREY,1.05,.62)
 # Four illustrative branches denote multiple inputs, not a count of leaves.
 for i,p in enumerate([[-3,-1.15,.55],[-3,-.40,1.5],[-3,.5,.75],[-3,1.25,1.7]]):
  wire(m,p,AMBER,.45,.65)
  u=smooth(13.5+i*.1,15.1+i*.1,t)
  if 0<u<1:token(m,p,center,u,AMBER,.16,.13)
  if u>.8:link(m,[p,center],AMBER,.021,.32)
 if t>14.8:particle(m,center,.34,PURPLE,'cube',.4)
 dest=[3.0,0,1.0];wire(m,dest,GREY,.60,.56)
 if t>15.05:token(m,center,dest,smooth(15.05,15.7,t),PURPLE,.23,.17)
 im=a.render(m)
 text(im,(470,330),'Aportes múltiples',44,AMBER,maxw=800)
 text(im,(470,375),'Multiple contributions',34,GREY,maxw=800)
 text(im,(1400,675),'Resultado integrado',44,PURPLE,maxw=850)
 text(im,(1400,720),'Combined result',34,GREY,maxw=850)
 return im

def aggregate_data(a):
 im=a.pair('12_aggregate_ref_sham_zero','12_aggregate_ref_sham_two',
  changes_left=dict(vectors=True,focus_prepared=False,prep_markers=[]),
  changes_right=dict(vectors=True,focus_prepared=False,prep_markers=[]))
 overlay_pair(im,('Contenido contrastado 1: −','Contrasting content 1: −'),('Contenido contrastado 2: +','Contrasting content 2: +'),size=40)
 return im

def base(a,t):
 if t<3.35:
  return introduction(a,t),dict(mode='Esquema',title_es='La historia cambia la primera actuación',title_en='History changes the first action',source='Nuevo ensayo · EO02 · N26')
 if t<7.78:
  return first_data(a),dict(mode='Registro',title_es='La diferencia aparece antes del nuevo retorno',title_en='The difference precedes the new feedback',source='EO02 · T125496',phase_es='Primera actuación, sin nueva enseñanza',phase_en='First action, without new teaching')
 if t<10.53:
  return rule_diagram(a,t),dict(mode='Esquema',title_es='Con la regla opuesta, la misma historia perjudica',title_en='With the opposite rule, the same history harms',source='EO02 · regla opuesta preparada')
 if t<13.40:
  return opposite_data(a),dict(mode='Etapas',title_es='La historia influye; no garantiza acertar',title_en='History influences; it does not guarantee success',source='EO02 · T125495 / T125496',phase_es='Misma escala; lector vacío ≠ salida cero',phase_en='Same scale; empty reader does not mean zero output',phase_color=AMBER)
 if t<15.85:
  return aggregate_diagram(a,t),dict(mode='Esquema',title_es='Otro ensayo integró múltiples contribuciones',title_en='Another trial combined multiple contributions',source='OTRO ensayo · FI01 · N67')
 return aggregate_data(a),dict(mode='Registro',title_es='Resultados distintos en un ensayo separado',title_en='Different results in a separate trial',source='OTRO ensayo · FI01 · T16702',phase_es='Con límites de acceso y continuidad',phase_en='With limits to access and continuity',phase_color=AMBER)

def frame(a,t):
 im,meta=base(a,t)
 for cut in [3.35,7.78,10.53,13.40,15.85]:
  if cut<=t<cut+.16:
   old=base(a,cut-.001)[0];im=Image.blend(old,im,smooth(cut,cut+.16,t));meta=dict(meta,mode='Transición')
 return im,meta
