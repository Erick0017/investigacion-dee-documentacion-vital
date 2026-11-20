"""Planos de agregación R03 a partir de registros existentes; cero ticks DEE."""
from pathlib import Path
from functools import lru_cache
import json,math
from PIL import Image,ImageDraw
import estilo_r03 as S
W=Path(__file__).resolve().parent
@lru_cache(None)
def evidence():
 return json.loads((W/'fuentes_extraidas/amplitud.json').read_text(encoding='utf-8'))['aggregate128']
def clamp(p):return max(0.,min(1.,float(p)))
def particle(v,colour,radius=.75):
 return dict(position=list(v),color=colour,radius=radius)
@lru_cache(maxsize=24)
def view(renderer,case,tick,prepared=False):
 data=evidence()['pair'][case];g=data['geometry']
 pts=[];hi=[]
 if prepared:
  for src in g['raw_sources']:
   i=src['component_index'];v=data['raw_components'][i]
   pts.append(particle(src['site'],S.CYAN if v else S.MUTED,.9 if v else .42))
   if v:hi.append(dict(position=src['site'],color=S.CYAN,radius=1.65))
  eye=[116,-91,125];target=[33,33,32];fov=48
 else:
  if tick==data['fixed_reader_tick']:
   fields=data['reader']['observations']
  else:
   f=next(f for f in data['frames']if f['tick']==tick)
   nodes={n['id']for n in g['nodes']}
   fields=[v for k,v in f['fields'].items()if k in nodes or k in('E','D','A','B') or(k.endswith('.meeting')and v['s_reg']>0)]
  for f in fields:
   if not(f.get('state',0)>0 or int(f.get('raw','0'))!=0):continue
   colour=S.CYAN if f['s_reg']==2 else S.AMBER if f['site']in([14,14,15],[16,14,15])else S.VIOLET if tick==data['fixed_reader_tick']else S.MUTED
   pts.append(particle(f['site'],colour,1.0 if colour!=S.MUTED else .50))
   if f['s_reg']==2 or(tick==data['fixed_reader_tick']and f.get('state',0)>0):hi.append(dict(position=f['site'],color=colour,radius=1.7))
  if tick>=16680:
   eye=[45,-37,60];target=[15,17,17];fov=45
  else:
   eye=[116,-91,125];target=[33,33,32];fov=48
 image=renderer.render(pts,eye=eye,target=target,bounds=(0,66),highlights=hi,fov=fov,grid=True)
 # Sólo la imagen 3D se encuadra; no se añaden trayectorias entre muestras.
 image=image.resize((995,560),Image.Resampling.LANCZOS)
 return image
def vector(im,data):
 d=ImageDraw.Draw(im);x0,y0=96,360;cw,ch=27,31
 for i,v in enumerate(data):
  row,col=divmod(i,16);x=x0+col*cw;y=y0+row*ch
  d.rounded_rectangle((x,y,x+23,y+26),radius=3,fill='#123745'if v else'#0D1B29',outline=S.CYAN if v else'#23394B',width=2 if v else 1)
  # Los valores del vector son auxiliares; el cambio decisivo se amplía debajo.
  d.text((x+11.5,y+12),str(v),font=S.font(18,bool(v)),fill=S.CYAN if v else S.GRAY,anchor='mm')
def draw(renderer,p):
 p=clamp(p);ev=evidence();pair=ev['pair']
 if p<.16:case='ref_sham_zero';prepared=True;tick=16642
 elif p<.32:case='ref_sham_two';prepared=True;tick=16642
 elif p<.80:
  case='ref_sham_two';prepared=False
  ticks=[16643,16649,16661,16680,16699];tick=ticks[min(4,int((p-.32)/.48*5))]
 else:
  case='ref_sham_zero'if p<.90 else'ref_sham_two';prepared=False;tick=16702
 d=pair[case];im=S.plain()
 image=view(renderer,case,tick,prepared)
 im.paste(image,(760,217))
 S.bi(im,(95,218),'128 componentes','128 input components',38,width=580)
 S.text(im,(95,302),'Prueba A · todo 0'if case.endswith('zero')else'Prueba B · sólo cambia uno',30,S.AMBER,True,width=605)
 vector(im,d['raw_components'])
 S.bi(im,(95,630),'Componente 1','Component 1',31,width=530)
 S.text(im,(95,704),'0'if case.endswith('zero')else'0 → 2',64,S.CYAN,True,width=530)
 if prepared:
  label='Posiciones de entrada';en='Input locations'
 else:
  label='Evento registrado · T'+str(tick);en='Recorded event · sampled sites'
 S.bi(im,(730,215),label,en,30,width=1100)
 # Más de una prueba nunca se representa como una sola vida.
 if p>=.80:
  S.panel(im,(770,620,1230,772),S.MUTED)
  S.panel(im,(1255,620,1808,772),S.CYAN)
  S.bi(im,(790,630),'A · todo 0','A · all 0',27,width=410)
  S.bi(im,(1275,630),'B · componente 1 = 2','B · component 1 = 2',27,width=495)
  S.text(im,(1025,722),'−1',61,S.GRAY,True,'mm',350)
  S.text(im,(1530,722),'+1',61,S.CYAN,True,'mm',420)
 elif tick==16699:
  S.panel(im,(1280,652,1808,770),S.VIOLET)
  S.bi(im,(1300,659),'Llegada registrada: 2','Recorded arrival: 2',30,width=490)
 elif not prepared:
  S.text(im,(760,738),'Cian: aporte observado · Ámbar: referencias',26,S.GRAY,width=1080)
 return im
