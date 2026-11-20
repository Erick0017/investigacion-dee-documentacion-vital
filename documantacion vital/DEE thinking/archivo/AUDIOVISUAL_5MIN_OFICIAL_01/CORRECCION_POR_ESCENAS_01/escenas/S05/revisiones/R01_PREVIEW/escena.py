"""S05 only: one acquired relation changes; documented witnesses keep their values.

The four-cell panel is a functional schematic, not a transplanted physical
layout. Exact before/after L03 and post-revision witness fields follow separately.
No new teaching, queries, DEE ticks, audio, or subtitle changes are executed.
"""
from pathlib import Path
import sys,copy,math
from PIL import Image
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parents[1]/'herramientas'))
from escena_base import *
SCENE=5
SAMPLE_TIMES=[.5,2.8,4.6,5.8,7.4,9.5,11.4,13.2,15.3,17.2,19.1]
CAM={'eye':[1.8,-10,7],'target':[0,.2,1],'fov':42,'lens_shift':[0,.12]}
TARGET=[-2.5,0,1.0];WITNESSES=[[.2,.2,.8],[2.6,.2,.8],[1.4,1.5,1.3]]
def panel(a,t):
 m=model(CAM,[[-4,-2,-.5],[4,3,3.3]])
 changed=t>=6.9
 for i,q in enumerate([TARGET]+WITNESSES):
  wire(m,q,AMBER if i==0 else GREY,size=.66 if i==0 else .56,alpha=.58)
  particle(m,q,.43 if i==0 else .35,PURPLE,'cube',.28)
  direction=[-1,-1,0] if i==0 and not changed else [-1,1,0]
  arrow(m,[q[0]+.17,q[1],q[2]],direction,length=.62 if i==0 else .53,color=WHITE,r=.045)
 if 4.15<=t<6.95:
  u=smooth(4.15,6.65,t)
  token(m,[-4.1,-.9,1.40],TARGET,u,BLUE,r=.23,arc=.15)
  token(m,[-3.4,1.45,1.50],TARGET,u,AMBER,r=.25,arc=.15)
 if t>=6.95:link(m,[[-4.1,-.9,1.40],TARGET],BLUE,r=.018,alpha=.18)
 # Editorial emphasis identifies tested witnesses; it is not another DEE event.
 if 8.9<=t<12.23:
  focus=int(min(2,max(0,(t-8.9)/1.05)))
  wire(m,WITNESSES[focus],WHITE,size=.61,alpha=.70,thickness=.018)
 im=a.render(m)
 text(im,(470,230),'Asociación revisada',44,AMBER,maxw=760)
 text(im,(470,272),'Revised association',34,GREY,maxw=760)
 text(im,(1320,230),'Tres testigos del panel',42,GREY,maxw=900)
 text(im,(1320,272),'Three panel witnesses',34,GREY,maxw=900)
 sign='+' if changed else '−'
 text(im,(470,740),('Después: ' if changed else 'Antes: ')+sign,46,PURPLE,maxw=850)
 text(im,(470,790),('After: ' if changed else 'Before: ')+sign,36,GREY,maxw=850)
 text(im,(1370,740),'Mismos valores cualificados',42,PURPLE,maxw=930)
 text(im,(1370,790),'Same qualified values',34,GREY,maxw=930)
 return im
def measured_revision(a):
 models=[a.case_model(x,panel=True,vectors=True,prep_markers=[]) for x in ['05_L03_338','05_L03_472']]
 for m in models:m['camera']=copy.deepcopy(models[0]['camera'])
 im=a.panels([a.render(m) for m in models])
 overlay_pair(im,('Antes de revisar','Before revision'),('Después de revisar','After revision'))
 for i,s in enumerate(['−','+']):
  text(im,(480+960*i,740),'Lectura '+s,46,PURPLE,maxw=850)
  text(im,(480+960*i,790),'Qualified read '+s,34,GREY,maxw=850)
 return im
def measured_witnesses(a):
 im=a.panels([a.case(x,panel=True,vectors=True,prep_markers=[]) for x in ['05_witness_L04','05_witness_L05']])
 overlay_pair(im,('Testigo L04','Witness L04'),('Testigo L05','Witness L05'))
 for i in range(2):
  text(im,(480+960*i,740),'Conserva su lectura +',44,PURPLE,maxw=850)
  text(im,(480+960*i,790),'Its qualified reading remains +',34,GREY,maxw=850)
 return im
def base(a,t):
 if t<12.23:
  title='Una asociación ya adquirida' if t<4.15 else 'Una nueva experiencia cambia la respuesta' if t<8.9 else 'Se comprueban las demás asociaciones'
  en='An already acquired association' if t<4.15 else 'A new experience changes the response' if t<8.9 else 'The other associations are checked'
  return panel(a,t),{'mode':'Esquema','title_es':title,'title_en':en,'source':'U0 · L03'}
 if t<16.5:return measured_revision(a),{'mode':'Etapas','title_es':'La misma relación, antes y después','title_en':'The same relation, before and after','source':'U0 · T338 → T472'}
 return measured_witnesses(a),{'mode':'Registro','title_es':'Ejemplos de trece testigos comprobados','title_en':'Examples from thirteen tested witnesses','source':'U0 · T472'}
def frame(a,t):
 im,meta=base(a,t)
 for cut in [12.23,16.5]:
  if cut<=t<cut+.20:
   im=Image.blend(base(a,cut-.001)[0],im,smooth(cut,cut+.20,t));meta=dict(meta,mode='Transición')
 return im,meta
