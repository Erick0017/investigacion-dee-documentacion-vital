from pathlib import Path
import sys,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'herramientas'))
from escena_base import *
SCENE=3
SAMPLE_TIMES=[.3,2.5,3.8,5.6,7.8,9.5,11.5,12.9,15,17.8]
CAM={'eye':[3,-10,6.3],'target':[0,0,.8],'fov':42,'lens_shift':[0,.13]}
def saved_model(a,id,panel=False):
 c=CASES[id];m=a.case_model(id,panel,focus_sites=[p['site'] for p in c['points']],prep_markers=[])
 # RAW-nonzero/state0 fields remain wireframes, never made into active matter.
 for b in m['boxes']:
  if b.get('opacity',1)<.3:b['opacity']=min(.48,b['opacity']*2.4)
 m['spatial_grid']['opacity']=.035
 return m
def diagram(a,t,later=False):
 m=model(CAM,[[-5,-2,-.5],[5,2,3.4]])
 # A functional illustration of full operational state, not a localised memory.
 for q in [[-.5,0,1],[.3,.35,1.7],[.35,-.25,.35]]:
  wire(m,q,GREY,.6,.6)
 particle(m,[-.5,0,1],.38,PURPLE,'cube',.32)
 particle(m,[.3,.35,1.7],.27,GREY,'cube',.6)
 particle(m,[.35,-.25,.35],.25,AMBER,'cube',.52)
 progress=smooth(10.9,11.8,t) if later else smooth(3.35,5.6,t)
 if progress<1:token(m,[-3.9,0,1],[-.5,0,1],progress,BLUE,.27,.22)
 if later and t>11.8:
  link(m,[[-.5,0,1],[2.8,0,1]],PURPLE,alpha=.45)
  wire(m,[2.8,0,1],PURPLE,.55,.55);particle(m,[2.8,0,1],.34,PURPLE,'cube',.3)
  arrow(m,[2.8,0,1.25],[0,0,-1],.56)
 im=a.render(m)
 text(im,(1440,325),'Estado con historia',44,maxw=700);text(im,(1440,371),'State with history',34,GREY,maxw=700)
 if not later:
  text(im,(480,650),'Entrada nueva',44,BLUE,maxw=750);text(im,(480,695),'New input',34,GREY,maxw=750)
 else:
  text(im,(1410,650),'Uso posterior',44,PURPLE,maxw=800);text(im,(1410,695),'Later use',34,GREY,maxw=800)
 return im
def view(a,t):
 if t<3.3:
  im=a.render(saved_model(a,'03_saved_memory_roi'))
  return im,dict(mode='Registro',title_es='Una organización con historia',title_en='An organisation with history',
   source='ECI02 · MINUS · N67 · T720458',phase_es='Estado y contexto, antes de continuar',phase_en='State and context before continuing')
 if t<7.36:
  return diagram(a,t),dict(mode='Esquema',title_es='La entrada encuentra un estado anterior',title_en='New input encounters a previous state',source='ECI02 · Continuidad / Continuity',
   phase_es='Nueva entrada sobre el contexto conservado',phase_en='New input uses the retained context')
 if t<10.85:
  mm=[saved_model(a,'03_saved_memory_roi',True),saved_model(a,'03_loaded_memory_roi',True)]
  # Same data sites, camera, scale and appearance; labels denote process roles.
  mm[1]['camera']=copy.deepcopy(mm[0]['camera']);im=a.panels([a.render(x) for x in mm])
  overlay_pair(im,('Guardado','Saved'),('Reabierto','Reopened'))
  text(im,(960,753),'Mismo estado físico y contexto operativo',46,PURPLE)
  text(im,(960,801),'Same physical state and operational context',36,GREY)
  return im,dict(mode='Etapas',title_es='Guardar y volver a utilizar',title_en='Save and use again',source='ECI02 · T720458 · Guardar / Cargar')
 if t<12.55:
  return diagram(a,t,True),dict(mode='Esquema',title_es='Consultar después de reabrir',title_en='Query after reopening',source='ECI02 · Consulta preparada / Prepared query')
 im=a.case('03_postreopen_memory',vectors=True,prep_markers=[],point_colors={'37,33,32':PURPLE,'37,33,34':GREY})
 text(im,(1430,307),'Recurso de consulta',38,GREY,maxw=740);text(im,(1430,348),'Query resource',30,GREY,maxw=740)
 text(im,(1430,590),'Estado leído',40,PURPLE,maxw=740);text(im,(1430,632),'Read state',32,GREY,maxw=740)
 return im,dict(mode='Registro',title_es='Lo conservado tiene un uso posterior',title_en='Retained information has a later use',source='ECI02 · MINUS · T720589',
  phase_es='Respuesta física − después de cargar',phase_en='Physical response − after loading')
def frame(a,t):
 im,meta=view(a,t)
 for cut in [3.3,7.36,10.85,12.55]:
  if cut<=t<cut+.22:
   im=Image.blend(view(a,cut-.001)[0],im,smooth(cut,cut+.22,t));meta=dict(meta,mode='Transición')
 return im,meta
