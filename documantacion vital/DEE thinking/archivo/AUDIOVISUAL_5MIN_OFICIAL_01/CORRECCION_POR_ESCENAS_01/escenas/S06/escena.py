"""S06 only. Functional composition diagram, then exact CPC9 stages and controls.

Schematic motion explains dependency, not measured collisions or trajectories.
The product icon remains at its functional role; no source carrier is animated
through the unrecorded207–209 interval. Prepared resource admission stays hollow.
"""
from pathlib import Path
import sys,copy,math
from PIL import Image
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parents[1]/'herramientas'))
from escena_base import *
SCENE=6
SAMPLE_TIMES=[.4,1.3,2.6,3.7,4.7,6.3,7.7,8.7,9.35,9.9,10.9,12.2,14.6,16.8,19.2]
CAM={'eye':[3,-9,6.4],'target':[.4,.1,1],'fov':42,'lens_shift':[0,.12]}
A=[-2.4,-.35,1.1];B=[-.7,1.7,1.2];P=[-.4,0,1.1];U=[2.6,0,1.1];RESOURCE=[2.6,1.65,1.2]
def schema(a,t):
 m=model(CAM,[[-4,-2,-.5],[4.5,3,3.3]])
 wire(m,P,GREY,size=.69,alpha=.40);wire(m,U,GREY,size=.69,alpha=.40)
 for q in [[-1.45,.55,.35],[.65,.6,.35],[1.7,.5,.35]]:particle(m,q,.17,GREY,'cube',.6)
 if t<2.45:
  u=smooth(.45,2.30,t);qa=lerp(A,P,u);qb=lerp(B,P,u)
  particle(m,qa,.34,BLUE,'sphere',1-smooth(2.2,2.45,t));particle(m,qb,.34,AMBER,'cube',1-smooth(2.2,2.45,t))
  if u>0:link(m,[A,qa],BLUE,r=.022,alpha=.48);link(m,[B,qb],AMBER,r=.022,alpha=.48)
 if t>=2.05:
  formed=smooth(2.05,2.55,t);particle(m,P,.44,PURPLE,'cube',.3*formed)
  if formed>.2:arrow(m,[P[0]-.20,P[1]-.20,P[2]-.20],[1,1,1],length=.65,color=WHITE,r=.044)
 if t>=3.9:
  # A growing functional connector, not a portador travelling between coordinates.
  connect=smooth(3.9,5.8,t);link(m,[P,lerp(P,U,connect)],PURPLE,r=.032,alpha=.62)
  wire(m,RESOURCE,GREY,size=.31,alpha=.65,thickness=.016)
  link(m,[RESOURCE,lerp(RESOURCE,U,smooth(4.45,5.9,t))],GREY,r=.022,alpha=.52)
 if t>=5.8:
  particle(m,U,.44,PURPLE,'cube',.3*smooth(5.8,6.35,t));arrow(m,[U[0]-.2,U[1],U[2]-.2],[1,0,1],length=.64,color=WHITE,r=.044)
 im=a.render(m)
 if t<2.45:
  text(im,(470,240),'Dos aportes',44,WHITE,maxw=650);text(im,(470,282),'Two contributions',34,GREY,maxw=650)
 if t>=2.45:
  text(im,(750,705),'Producto común',44,PURPLE,maxw=800);text(im,(750,750),'Common product',34,GREY,maxw=800)
 if t>=3.9:
  text(im,(1660,266),'Recurso preparado',34,GREY,maxw=400);text(im,(1660,307),'Prepared resource',30,GREY,maxw=400)
 if t>=5.8:
  text(im,(1435,704),'Uso posterior',44,PURPLE,maxw=800);text(im,(1435,750),'Later use',34,GREY,maxw=800)
 return im
def pair(a,ids):
 ms=[a.case_model(x,panel=True,vectors=True,prep_markers=[]) for x in ids]
 for m in ms:m['camera']=copy.deepcopy(ms[0]['camera'])
 return a.panels([a.render(m) for m in ms])
def base(a,t):
 if t<7.4:
  im=schema(a,t)
  if t<1.8:text(im,(56,25),'Nuevo ensayo / New trial',28,GREY,'lm',500)
  return im,{'mode':'Esquema','title_es':'Un producto común puede reutilizarse','title_en':'A common product can be used again','source':'CPC9 · EI_D01'}
 if t<8.35:return a.case('06_inputs'),{'mode':'Etapas','title_es':'Dos contribuciones registradas','title_en':'Two recorded contributions','source':'CPC9 · T205'}
 if t<9.1:return a.case('06_product',vectors=True),{'mode':'Etapas','title_es':'Un producto común registrado','title_en':'A recorded common product','source':'CPC9 · T206'}
 if t<9.65:return a.case('06_admission'),{'mode':'Esquema','title_es':'Admisión preparada entre los registros','title_en':'Prepared admission between recorded states','source':'CPC9 · T207','phase_es':'Recurso admitido; no se observó el trayecto','phase_en':'Resource admitted; its route was not recorded'}
 if t<10.44:return a.case('06_use',vectors=True),{'mode':'Etapas','title_es':'Consecuencia registrada después','title_en':'A later recorded consequence','source':'CPC9 · T210'}
 if t<12.0:
  im=pair(a,['06_inputs','06_cut_pre']);overlay_pair(im,('Original','Original'),('Un aporte retirado','One contribution removed'),y=740,en_y=790)
  return im,{'mode':'Etapas','title_es':'Se retira una contribución en el control','title_en':'One contribution is removed in the control','source':'CPC9 · corte diagnóstico'}
 if t<16.10:
  im=pair(a,['06_use','06_cut_use']);overlay_pair(im,('Original','Original'),('Corte selectivo','Selective cut'))
  for i,(es,en) in enumerate([('Consecuencia original','Original outcome'),('Consecuencia distinta','Different outcome')]):text(im,(480+960*i,740),es,44,PURPLE,maxw=850);text(im,(480+960*i,790),en,34,GREY,maxw=850)
  return im,{'mode':'Etapas','title_es':'El corte cambia la consecuencia','title_en':'The cut changes the outcome','source':'CPC9 · T210 · 63 / 7'}
 im=pair(a,['06_use','06_sham_use']);overlay_pair(im,('Original','Original'),('Intervención simulada','Sham intervention'))
 for i in range(2):text(im,(480+960*i,740),'Mismo resultado',46,PURPLE,maxw=850);text(im,(480+960*i,790),'Same outcome',34,GREY,maxw=850)
 return im,{'mode':'Etapas','title_es':'El control simulado conserva el resultado','title_en':'The sham control preserves the outcome','source':'CPC9 · T210 · 63 / 63'}
def frame(a,t):
 im,meta=base(a,t)
 for cut in [7.4,8.35,9.1,9.65,10.44,12.0,16.10]:
  if cut<=t<cut+.16:
   im=Image.blend(base(a,cut-.001)[0],im,smooth(cut,cut+.16,t));meta=dict(meta,mode='Transición')
 return im,meta
