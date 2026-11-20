"""S10 only: acquired pulse direction, local interception, bounded later use.

Native frames never interpolate. Schematic motion explains the functional
contrast and is not a measured T3-to-T292 trajectory. The zero-load pulse is
active RAW and is rendered. This profile is separate from E1 and U0.
"""
from pathlib import Path
import sys,json,copy
from PIL import Image
H=Path(__file__).resolve().parent;ROOT=H.parents[1]
sys.path.insert(0,str(ROOT/'herramientas'))
from escena_base import (BLUE,AMBER,PURPLE,WHITE,GREY,CASES,model,particle,wire,
 link,arrow,token,smooth,text,overlay_pair,lerp,model_from_case)

SCENE=10
SAMPLE_TIMES=[.8,2.7,4.5,5.6,7.0,8.85,9.9,11.8,14.4,16.4,17.8,19.4]
CAM={'eye':[3.6,-10,5.3],'target':[0,0,.85],'fov':42,'lens_shift':[0,.12]}
DATA=json.loads((ROOT/'PROYECTO_INTACTO/trabajo/fuentes/ESCENAS_03_05_10_13.json').read_text('utf8'))['scenes']['S10']

# Frozen source contains this exact probe; derive a local view, not a new case
# in the shared catalogue. Both sides below are the same retained tick.
UNPAIRED3=copy.deepcopy(CASES['10_REG_PAIRED_3'])
_frame=next(f for f in DATA['source_frames_by_arm']['REG_UNPAIRED'] if f['tick']==3)
_point=copy.deepcopy(_frame['observations']['nominal_regulator_segment'])
_point['rawstr']=str(_point['raw']);_point['clockstr']=str(_point['clock'])
UNPAIRED3.update(id='S10_LOCAL_UNPAIRED_3',life='REG_UNPAIRED',points=[_point],
 label_es='Historia no emparejada',label_en='Unpaired history')
assert _point['rawstr']=='1225260573621485569' and _point['direction']==[1,0,1]
assert int(_point['state'])==1 and int(_point['s_reg'])==0
for _ref in UNPAIRED3['source_refs']:
 if 'REG_PAIRED' in _ref.get('pointer',''):
  _ref['pointer']=_ref['pointer'].replace('REG_PAIRED','REG_UNPAIRED')
 if 'REG_PAIRED' in _ref.get('path',''):
  _ref.update(path=_ref['path'].replace('REG_PAIRED','REG_UNPAIRED'),
   sha256='2ba51996a5534f51bc321c65e50fd2c8e2afcbcd0df43b60cff2393a4e3696ce',bytes=165778)

def pair_labels(im):
 overlay_pair(im,('Historia emparejada','Paired history'),('No emparejada','Unpaired history'))
 return im

def direction(a):
 c=copy.deepcopy(CASES['10_REG_PAIRED_3'])
 c.update(points=[p for p in c['points'] if p['site']==[22,40,56]],vectors=True)
 d=copy.deepcopy(UNPAIRED3);d['vectors']=True
 mm=[model_from_case(x,panel=True) for x in [c,d]]
 # Identical camera: same physical probe coordinate and spatial scale.
 mm[1]['camera']=copy.deepcopy(mm[0]['camera'])
 im=pair_labels(a.panels([a.render(m) for m in mm]))
 text(im,(960,751),'El pulso conserva direcciones distintas',46,AMBER,maxw=1700)
 text(im,(960,801),'The pulse retains different directions',36,GREY,maxw=1700)
 return im

def encounter(a,t):
 ims=[]
 for paired in [True,False]:
  m=model(CAM,[[-3,-2,-1],[3,2,3.5]])
  middle=[0,0,.55];start=[0,0,-.75];top=[0,0,2.05]
  # Hollow region is an editorial region marker, not another prepared body.
  wire(m,middle,GREY,.83,alpha=.30)
  u=smooth(4.0,6.3,t)
  if paired:
   p=lerp(start,middle,u);di=[0,0,1]
  else:
   p=lerp(start,[1.9,0,1.15],u);di=[1,0,1]
  q=lerp(top,middle,u)
  # By T293 both local observed sites are RAW0 in paired. The fade depicts
  # local absence, not annihilation throughout the world or unique lineage.
  if paired:
   alpha=1-smooth(6.35,7.1,t)
   if alpha>.01:
    particle(m,p,.33,AMBER,alpha=.30*alpha)
    particle(m,q,.32,BLUE,alpha=.30*alpha)
    if alpha>.45:
     arrow(m,[p[0],p[1],p[2]-.23],di,.55)
     arrow(m,[q[0],q[1],q[2]+.23],[0,0,-1],.55)
  else:
   particle(m,p,.33,AMBER,alpha=.30);arrow(m,[p[0]-.18,p[1],p[2]-.18],di,.55)
   q=lerp(middle,[0,0,-.20],smooth(6.35,7.3,t)) if t>6.3 else q
   particle(m,q,.32,BLUE,alpha=.30);arrow(m,[q[0],q[1],q[2]+.23],[0,0,-1],.55)
  if t<6.3:
   link(m,[start,p],AMBER,alpha=.25);link(m,[top,q],BLUE,alpha=.25)
  im=a.render(m)
  text(im,(620,490),'Pulso',38,AMBER,maxw=500)
  text(im,(1300,390),'Interferencia',36,BLUE,maxw=600)
  ims.append(im)
 im=pair_labels(a.panels(ims))
 text(im,(960,755),'La dirección cambia el encuentro local',44,WHITE,maxw=1700)
 text(im,(960,802),'Direction changes the local encounter',36,GREY,maxw=1700)
 return im

def contact(a,t):
 tick=292 if t<9.6 else 293
 changes={'vectors':True,'focus_sites':[[22,40,10],[22,40,11]],'prep_markers':[],
  'crop_radius':2,'point_colors':{'22,40,10':AMBER if tick==292 else BLUE,'22,40,11':BLUE}}
 im=a.pair('10_REG_PAIRED_'+str(tick),'10_REG_UNPAIRED_'+str(tick),changes,changes,True)
 pair_labels(im)
 if tick==292:
  left,right='Pulso y contribución','Contribución presente'
  le,re='Pulse and contribution','Contribution present'
 else:
  left,right='Zona local sin esos campos','Contribución conservada'
  le,re='Those fields absent locally','Contribution retained'
 for x,es,en in [(480,left,le),(1440,right,re)]:
  text(im,(x,740),es,38,maxw=870);text(im,(x,790),en,32,GREY,maxw=870)
 return im

def use(a):
 changes={'vectors':True,'focus_sites':[[20,44,12]],'prep_markers':[]}
 im=a.pair('10_REG_PAIRED_437','10_REG_UNPAIRED_437',changes,changes,True)
 pair_labels(im)
 for x,es,en in [(480,'Función local disponible','Local function available'),
                  (1440,'Sin lectura local válida','No valid local reading')]:
  text(im,(x,738),es,42,PURPLE,maxw=880);text(im,(x,789),en,34,GREY,maxw=880)
 return im

def prepared(a,t):
 m=model({'eye':[3,-10.3,5.4],'target':[0,0,.8],'fov':42,'lens_shift':[0,.12]},[[-5,-2,-.6],[5,2,3.1]])
 left=[-2.8,0,1];right=[2.8,0,1];center=[0,0,1]
 for p in [left,center,right]:wire(m,p,GREY,.67,alpha=.65)
 particle(m,left,.40,AMBER,alpha=.30);arrow(m,[-2.8,0,.74],[0,0,1],.57)
 particle(m,right,.40,BLUE,alpha=.30);arrow(m,[2.8,0,1.26],[0,0,-1],.57)
 # The opportunity is installed/scheduled, not chosen autonomously by E1.
 u=smooth(15.85,17.6,t)
 if t<17.75:
  token(m,[-.1,1.7,2.6],center,u,GREY,r=.24,arc=.12)
 im=a.render(m)
 for x,es,en,col in [(550,'Estado adquirido','Acquired state',AMBER),
                     (960,'Oportunidad preparada','Prepared opportunity',GREY),
                     (1420,'Perturbación','Perturbation',BLUE)]:
  text(im,(x,655),es,36,col,maxw=600);text(im,(x,700),en,30,GREY,maxw=600)
 text(im,(960,775),'No se demostró decidir cuándo intervenir',44,WHITE,maxw=1760)
 text(im,(960,822),'Choosing when to intervene was not demonstrated',34,GREY,maxw=1760)
 return im

def raw(a,t):
 if t<3.85:return direction(a),dict(mode='Etapas',title_es='Otra historia, otra dirección adquirida',title_en='Different history, different acquired direction',source='Otro perfil · CPC5 · N67 · T3')
 if t<8.8:return encounter(a,t),dict(mode='Esquema',title_es='El pulso interviene sobre una interferencia',title_en='The pulse acts on an interference',source='CPC5 · vínculo local ilustrativo')
 if t<11.12:return contact(a,t),dict(mode='Etapas',title_es='El encuentro cambia los campos locales',title_en='The encounter changes local fields',source='CPC5 · T292/T293 · N67')
 if t<15.625:return use(a),dict(mode='Etapas',title_es='La consecuencia funcional es diferente',title_en='The functional consequence differs',source='CPC5 · lector Flat · T437')
 if t<18.9:return prepared(a,t),dict(mode='Esquema',title_es='El alcance de la regulación es local',title_en='Regulation is local in scope',source='Perfil experimental preparado')
 return use(a),dict(mode='Etapas',title_es='Historia, interferencia y uso posterior',title_en='History, interference and later use',source='CPC5 · lector Flat · T437')

def frame(a,t):
 im,meta=raw(a,t)
 for cut in [3.85,8.8,9.6,11.12,15.625,18.9]:
  if cut<=t<cut+.20:
   im=Image.blend(raw(a,cut-.001)[0],im,smooth(cut,cut+.20,t));meta={**meta,'mode':'Transición'}
 return im,meta
