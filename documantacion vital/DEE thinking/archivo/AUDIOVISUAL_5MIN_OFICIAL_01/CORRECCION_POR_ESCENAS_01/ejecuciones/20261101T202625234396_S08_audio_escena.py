"""S08 only. A prepared comparison conditions a native question and later use.

All functional motion is an illustrative schematic, never a reconstructed51tick
trajectory. Exact retained question/use vectors appear in separately labelled data.
"""
from pathlib import Path
import sys,copy,json
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent;ROOT=H.parents[1]
sys.path.insert(0,str(ROOT/'herramientas'))
from escena_base import (BG,BLUE,AMBER,PURPLE,WHITE,GREY,model,particle,wire,link,
 arrow,token,smooth,text,overlay_pair,CASES,model_from_case)
SCENE=8
SAMPLE_TIMES=[.5,4.5,6.8,8.9,10.8,12.6,15.5,18.8]
SOURCE='U0 · CPC7 · N67'
SOURCE_DATA=ROOT/'PROYECTO_INTACTO/trabajo/fuentes/ESCENAS_04_06_09.json'
_data=json.loads(SOURCE_DATA.read_text('utf8'))['scenes']['08']
_arm=_data['arms']['matching_current'];_stage=next(s for s in _arm['stages'] if s['tick']==72)
MATCH_USE=dict(id='08_matching_current_72',tick=72,life=_arm['life'],N=67,
 points=[_stage['reads']['actions']['own.use.minus']],focus_sites=[[33,8,46]],
 source_refs=[_arm['source']],classification='Etapas',prep_markers=[])
CAM={'eye':[1.8,-8.7,5.7],'target':[0,0,1.0],'fov':42,'lens_shift':[0,.10]}
def comparator(a,t,question=False):
 ims=[]
 for side in range(2):
  m=model(CAM,[[-3,-2,-.5],[3,2,3.5]])
  prev=[-1.25,.20,1.40];cur=[1.25,.20,1.40];hub=[0,-.50,.25]
  wire(m,prev,AMBER,.57);wire(m,cur,BLUE,.57);wire(m,hub,GREY,.50)
  particle(m,prev,.39,AMBER,alpha=.30);arrow(m,[prev[0]-.25,prev[1],prev[2]],[1,0,0],.51)
  u=smooth(3.1,5.4,t);start=[2.4,.7,2.5]
  pos=[start[k]+(cur[k]-start[k])*u for k in range(3)]
  particle(m,pos,.39,BLUE,alpha=.34)
  direction=[-1,0,0] if side==0 else [1,0,0]
  arrow(m,[pos[0]-.25*direction[0],pos[1],pos[2]],direction,.51)
  if t>=5.4:
   link(m,[prev,hub],AMBER,alpha=.45);link(m,[cur,hub],BLUE,alpha=.45)
  if question:
   # A symbolic emphasis of the measured distinction, not absent matter in control.
   particle(m,hub,.34,PURPLE if side==0 else GREY,alpha=.28)
   if side==0:
    u=smooth(6.52,8.05,t);pos=token(m,hub,[-.0,-1.45,.25],u,PURPLE,r=.22,arc=.20)
    arrow(m,[pos[0]-.20,pos[1],pos[2]],[1,0,0],.44)
   else:arrow(m,[hub[0],hub[1]-.10,hub[2]+.16],[0,1,-1],.44,GREY)
  im=a.render(m)
  text(im,(755,285),'Previo',34,AMBER,maxw=400);text(im,(755,323),'Earlier',28,GREY,maxw=400)
  text(im,(1160,285),'Actual',34,BLUE,maxw=400);text(im,(1160,323),'Current',28,GREY,maxw=400)
  ims.append(im)
 im=a.panels(ims);overlay_pair(im,('Discrepancia','Mismatch'),('Coincidencia','Match'))
 if question:
  for x,s,en,color in [(480,'Pregunta material','Material question',PURPLE),(1440,'Otra actividad','Other activity',GREY)]:
   text(im,(x,735),s,44,color,maxw=850);text(im,(x,783),en,34,GREY,maxw=850)
 return im
def actual_question(a):
 changes={'focus_sites':[[47,10,46]],'vectors':True,'prep_markers':[],'point_colors':{'47,10,46':PURPLE}}
 other={**changes,'point_colors':{'47,10,46':GREY}}
 im=a.pair('08_discrepant_19','08_matching_current_19',changes,other,True)
 overlay_pair(im,('Discrepancia','Mismatch'),('Coincidencia','Match'))
 text(im,(480,735),'Pregunta horizontal',44,PURPLE,maxw=850);text(im,(480,783),'Horizontal question',34,GREY,maxw=850)
 text(im,(1440,735),'Activo; no esa pregunta',42,GREY,maxw=850);text(im,(1440,783),'Active; not that question',34,GREY,maxw=850)
 return im
def access(a,t,opportunity=False):
 cam={'eye':[2.6,-10.2,6.2],'target':[0,0,1.0],'fov':42,'lens_shift':[0,.12]}
 m=model(cam,[[-5,-2,-.5],[5,2,3.5]])
 query=[-3.15,0,1.0];bank=[0,0,1.0];use=[3.15,0,1.0]
 for pos,col in [(query,PURPLE),(bank,AMBER),(use,PURPLE)]:wire(m,pos,col,.73)
 particle(m,bank,.43,AMBER,alpha=.34);arrow(m,[-.2,0,1],[1,-1,0],.51)
 if not opportunity:
  u=smooth(9.965,11.25,t);q=token(m,query,bank,u,PURPLE,r=.25);link(m,[query,q],PURPLE,alpha=.42)
  if t>11.25:
   v=smooth(11.25,13.00,t);p=token(m,bank,use,v,AMBER,r=.25);link(m,[bank,p],AMBER,alpha=.46)
  if t>=13:
   particle(m,use,.40,PURPLE,alpha=.28);arrow(m,[use[0]-.18,0,.8],[1,-1,1],.58)
 else:
  link(m,[query,bank,use],GREY,alpha=.25);particle(m,use,.40,PURPLE,alpha=.28);arrow(m,[use[0]-.18,0,.8],[1,-1,1],.58)
  # External generic resource is explicitly identified; it does not select the question.
  res=[3.0,1.4,2.1];u=smooth(14.32,16.2,t);token(m,res,use,u,GREY,r=.22,arc=.1)
 im=a.render(m)
 for x,es,en,col in [(560,'Pregunta','Question',PURPLE),(960,'Información adquirida','Acquired information',AMBER),(1395,'Uso posterior','Later use',PURPLE)]:
  text(im,(x,645),es,40,col,maxw=650);text(im,(x,688),en,32,GREY,maxw=650)
 if opportunity:
  text(im,(1500,265),'Recurso genérico preparado',34,GREY,maxw=650);text(im,(1500,306),'Prepared generic resource',28,GREY,maxw=650)
 return im
def actual_use(a):
 changes={'focus_sites':[[33,8,46]],'vectors':True,'prep_markers':[],'point_colors':{'33,8,46':PURPLE}}
 left=a.case_model('08_discrepant_72',True,**changes)
 c=copy.deepcopy(MATCH_USE);c.update(vectors=True,point_colors={'33,8,46':GREY})
 right=model_from_case(c,panel=True);right['camera']=left['camera']
 im=a.panels([a.render(left),a.render(right)])
 overlay_pair(im,('Con la pregunta previa','With the earlier question'),('Control coincidente','Matching control'))
 text(im,(480,735),'Uso dependiente de información',40,PURPLE,maxw=850);text(im,(480,784),'Information-dependent use',32,GREY,maxw=850)
 text(im,(1440,735),'Aporte común; no ese uso',40,GREY,maxw=850);text(im,(1440,784),'Common input; not that use',32,GREY,maxw=850)
 return im
def raw(a,t):
 if t<6.52:return comparator(a,t),dict(mode='Esquema',title_es='Comparar lo previo con lo actual',title_en='Comparing earlier and current information',source=SOURCE)
 if t<8.3:return comparator(a,t,True),dict(mode='Esquema',title_es='La diferencia condiciona una pregunta',title_en='The mismatch conditions a question',source=SOURCE)
 if t<9.965:return actual_question(a),dict(mode='Etapas',title_es='La pregunta es un estado material',title_en='The question is a material state',source=SOURCE+' · T19')
 if t<14.32:return access(a,t),dict(mode='Esquema',title_es='Pregunta → información → uso',title_en='Question → information → use',source=SOURCE)
 if t<17.3:return access(a,t,True),dict(mode='Esquema',title_es='Oportunidades y tiempos preparados',title_en='Prepared opportunities and timing',source=SOURCE)
 return actual_use(a),dict(mode='Etapas',title_es='La información intervino en el uso',title_en='The information contributed to use',source=SOURCE+' · T72')
def frame(a,t):
 im,meta=raw(a,t)
 for cut in [6.52,8.3,9.965,14.32,17.3]:
  if cut<=t<cut+.20:
   im=Image.blend(raw(a,cut-.001)[0],im,smooth(cut,cut+.20,t));meta={**meta,'mode':'Transición'}
 return im,meta
