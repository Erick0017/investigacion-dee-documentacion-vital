
"""Película R03 offline: voz local, dibujo editorial y registros ya producidos. Cero DEE."""
from pathlib import Path
from functools import lru_cache
import json,math,re,wave,subprocess,time,hashlib,argparse,importlib.util,sys
import numpy as np
from PIL import Image,ImageDraw
import estilo_r03 as S
W=Path(__file__).resolve().parent; PROD=W.parent; R02=PROD/'R02_memoria_plasticidad'
ROOT=next(p for p in W.parents if p.name=='DEE thinking'); TEST=ROOT.parent.parent
FF=TEST/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
PROBE=TEST/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
FPS=30
MAIN=W/'DEE_Cognitive_2_0_Inteligencia_Funcional_R03_1080p.mp4'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):
 tmp=Path(p).with_suffix(Path(p).suffix+'.tmp');tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(p)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
@lru_cache(None)
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def renderer():return module('r02_render_adapter',R02/'pelicula_r02.py').renderer()
@lru_cache(None)
def A():return read(W/'fuentes_extraidas/amplitud.json')
@lru_cache(None)
def script():return read(W/'guion_R03.json')
@lru_cache(None)
def old():return module('r02_render_adapter',R02/'pelicula_r02.py')
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
def splitlines(value,n=46,width=1690):
 # Cortes preferentes de cláusula sin cambiar ni una palabra.
 rows=S.lines(value,n,width);return [rows[i:i+2]for i in range(0,len(rows),2)]
def cues(es,en,marks,offset,language):
 out=[];assert len(es)==len(en)==len(marks)
 for a,b,m in zip(es,en,marks):
  assert m['text']==a and m['start'] is not None and m['end'] is not None,m
  value=a if language=='es'else b;groups=splitlines(value);total=sum(len(' '.join(g).split())for g in groups);past=0
  for g in groups:
   count=len(' '.join(g).split());length=m['end']-m['start']
   out.append(dict(start=offset+m['start']+length*past/total,end=offset+m['start']+length*(past+count)/total,lines=g,text=' '.join(g)))
   past+=count
 return out
def plan():
 voices={r['id']:r for r in read(W/'voz/timings.json')['scenes']}
 holds={'s01':1.3,'s02':4.8,'s03':3,'s04':8,'s05a':3,'s05b':3,'s05c':4,'s05d':3,'s06':4,'s07':3,'s08':5.5}
 pcm=bytearray();at=0;scenes=[];caps={'es':[],'en':[]};params=None
 for s in script()['scenes']:
  v=voices[s['id']];assert v['es']==s['es']and sha(W/v['file'])==v['wav_sha256']
  assert v['complete_model_waveform_retained'] and v['audio_sentence_splices']==0
  with wave.open(str(W/v['file']),'rb')as f:pr=f.getparams();audio=f.readframes(f.getnframes());frames=f.getnframes()
  if params:assert pr[:3]==params[:3]
  params=pr;count=math.ceil((frames/pr.framerate+holds[s['id']])*FPS)*int(pr.framerate/FPS)
  duration=count/pr.framerate;pcm.extend(audio);pcm.extend(bytes((count-frames)*pr.sampwidth*pr.nchannels))
  es=[r['text']for r in v['sentences']];en=re.split(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÜ¿¡])',s['en'])
  row=dict(s,start=at,end=at+duration,duration=duration,marks=v['sentences'],voice_duration=frames/pr.framerate,end_observation_pause=duration-frames/pr.framerate,frames=round(duration*FPS))
  scenes.append(row)
  for lang in caps:caps[lang].extend(cues(es,en,v['sentences'],at,lang))
  at+=duration
 with wave.open(str(W/'voz/locucion_continua_R03.wav'),'wb')as f:f.setparams(params);f.writeframes(pcm)
 for lang,rows in caps.items():
  assert ' '.join(x['text']for x in rows)==' '.join(s[lang]for s in script()['scenes'])
  path=W/('DEE_Cognitive_2_0_Inteligencia_Funcional_R03_EN.srt'if lang=='en'else'subtitulos_R03_ES.srt')
  path.write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n'+'\n'.join(c['lines'])for i,c in enumerate(rows))+'\n',encoding='utf-8')

 def ass_stamp(t):
  n=round(t*100);return f'{n//360000:01}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}'
 header='[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Main,Segoe UI,46,&H00FAF7F5,&H000000FF,&H00170D05,&H00000000,0,0,0,0,100,100,0,0,1,1.2,0,2,80,80,90,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
 body='\n'.join('Dialogue: 0,'+ass_stamp(c['start'])+','+ass_stamp(c['end'])+',Main,,0,0,0,,'+'\\N'.join(c['lines'])for c in caps['en'])
 (W/'subtitulos_R03_EN.ass').write_text(header+body+'\n',encoding='utf-8')
 save(W/'timeline_R03.json',dict(scenes=scenes,captions=caps,duration=at,fps=FPS,new_native_ticks=0,audio_speed_change=False))
 print('PLAN',round(at,3),'sec',[(s['id'],round(s['duration'],2))for s in scenes],flush=True)
def sentence(s,t):
 i=0
 for j,m in enumerate(s['marks']):
  if t>=m['start']:i=j
 a=s['marks'][i]['start'];b=(s['marks'][i+1]['start']if i+1<len(s['marks'])else s['duration'])
 return i,S.phase_between(t,a,b)
def markrange(s,a,b,t):
 start=s['marks'][a]['start'];end=s['marks'][b]['start']if b<len(s['marks'])else s['duration']
 return S.phase_between(t,start,end)
def label(im,es,en,y=225,color=S.WHITE):
 S.bi(im,(100,y),es,en,42,color,width=1700)
def progressrow(im,labels,index,y=727):
 d=ImageDraw.Draw(im);n=len(labels);gap=1710/n
 for j,(es,en)in enumerate(labels):
  col=S.CYAN if j<=index else S.MUTED;x=105+j*gap
  d.ellipse((x,y,x+14,y+14),fill=col)
  S.text(im,(x+24,y-10),es,27,col,j==index,width=gap-33)
  S.text(im,(x+24,y+28),en,24,S.GRAY,width=gap-33)
def aa(p):
 ev=A()['aa46'];im=S.plain();phase=min(3,int(p*4))
 label(im,['Contenido adquirido','La lectura habitual no lo distingue','Enseñanza de otro acceso','La misma consulta recupera el contenido'][phase],['Previously learned content','The usual reader no longer distinguishes it','Training a different access','The common query retrieves the content'][phase])
 for j,(key,sign,color)in enumerate([('plus','+1',S.AMBER),('minus','−1',S.VIOLET)]):
  x=110+j*900;S.panel(im,(x,340,x+820,685),color)
  S.bi(im,(x+35,360),'Rama '+('+'if j==0 else'−'),'Separate history '+('+'if j==0 else'−'),32,color,width=750)
  if phase==0:
   S.text(im,(x+250,520),sign,84,color,True,'mm',320)
   S.text(im,(x+585,520),sign,84,color,True,'mm',320)
   S.bi(im,(x+410,602),'Dos experiencias anteriores','Two earlier content experiences',30,S.GRAY,'mm',735)
  else:
   S.bi(im,(x+190,437),'Conservado','Retained content',27,S.GRAY,'mm',340)
   S.text(im,(x+190,540),sign,68,color,True,'mm',340)
   S.bi(im,(x+580,437),'Consulta'if phase!=2 else'Acceso','Query'if phase!=2 else'Access training',27,S.GRAY,'mm',360)
   value='—'if phase==1 else'↻'if phase==2 else sign
   S.text(im,(x+580,540),value,84,color,True,'mm',350)
   if phase==1:S.bi(im,(x+410,622),'Lectura sin código válido','The reader yields no valid code',29,S.GRAY,'mm',730)
   elif phase==2:S.bi(im,(x+410,622),'Misma enseñanza del acceso','Same access training',29,S.GRAY,'mm',730)
   else:S.bi(im,(x+410,622),'Uso de su propio contenido previo','Use of its own previously learned content',29,S.GRAY,'mm',730)
 progressrow(im,[('Adquirir','Learn'),('Lectura fallida','Failed access'),('Enseñar acceso','Access training'),('Utilizar','Use')],phase)
 return im
def u0(renderer,p):
 stages=[(5,[33,24,42],'Previsión emitida','Prediction emitted'),(11,None,'Llega el resultado','Outcome arrives'),(19,[47,10,46],'Se forma una consulta','A query is formed'),(70,[31,10,46],'Información recibida','Information received'),(72,[33,8,46],'Utilización posterior','Subsequent use')]
 k=min(4,int(p*5));tick,pos,es,en=stages[k]
 pts=[]if pos is None else[dict(position=pos,color=S.AMBER if k==0 else S.CYAN,radius=1.0)]
 im=renderer.render(pts,eye=[70,-12,69],target=[36,17,43],bounds=([22,2,36],[54,30,53]),highlights=[]if pos is None else[dict(position=pos,color=S.CYAN,radius=1.7)])
 # Cada foco es un acontecimiento distinto, no un linaje interpolado.
 label(im,es,en)
 if k==1:S.bi(im,(1110,425),'Resultado diferente','A different outcome',44,S.CYAN,width=650)
 S.bi(im,(105,365),'Antes del resultado'if k==0 else'Comparación registrada','Before the outcome'if k==0 else'Recorded comparison',34,S.AMBER,width=620)
 if k>=2:
  S.panel(im,(1080,325,1810,650),S.CYAN)
  S.bi(im,(1120,348),'Si difiere: consulta','Mismatch: query',36,S.CYAN,width=640)
  S.bi(im,(1120,486),'Si coincide: sin esa consulta','Match: no such query',33,S.GRAY,width=640)
 progressrow(im,[('Previsión','Prediction'),('Resultado','Outcome'),('Consulta','Query'),('Información','Information'),('Uso','Use')],k)
 return im
def consequence(p):
 cases=A()['ciclo02']['cases'];im=S.plain()
 real=next(v for v in cases.values()if v['mode']=='intact')
 rows=real['rows'];assert rows[1]['force_sensor']==2 and rows[1]['native_action']==-1
 phase=min(2,int(p*3))
 label(im,['La acción tiene una consecuencia','La experiencia modifica una referencia','Misma oportunidad, otra elección'][phase],['An action has a consequence','Experience changes a reference','Same opportunity, a different choice'][phase])
 if phase==0:
  S.bi(im,(130,375),'Acción realizada','Action performed',42,S.WHITE,width=750)
  S.bi(im,(1110,375),'Retorno ambiental','Environmental feedback',42,S.AMBER,width=700)
  S.text(im,(1435,568),'6',122,S.AMBER,True,'mm',600)
  S.text(im,(120,580),'El retorno participa en otro encuentro',34,S.GRAY,width=900)
 else:
  for j,(title,en,ref,choice,col)in enumerate([('Con retorno','With feedback','5 → 11','RETIRARSE / WITHDRAW',S.CYAN),('Sin retorno','Feedback omitted','5','INTENTAR / TRY',S.GRAY)]):
   x=110+j*900;S.panel(im,(x,340,x+820,688),col);S.bi(im,(x+35,360),title,en,38,col,width=750)
   S.text(im,(x+410,514),ref,95,col,True,'mm',730)
   S.text(im,(x+410,625),choice if phase==2 else'Referencia / Reference',34,col,True,'mm',730)
 if phase==2:S.text(im,(105,260),'Mismo estímulo: 2 / Same input: 2',32,S.AMBER,width=1700)
 progressrow(im,[('Acción','Action'),('Consecuencia','Consequence'),('Nuevo uso','New use')],phase)
 return im
def social(p):
 data=read(W/'fuentes_extraidas/comunicacion.json');story=data['story'];im=S.plain();k=min(3,int(p*4))
 label(im,['Información privada de B','B forma un mensaje','El mensaje alcanza E1','Un uso posterior cambia'][k],['B has private information','B forms a message','The message reaches E1','A later use changes'][k])
 # Visualización de acontecimientos: sin ruta microscópica ficticia.
 for x,es,en,col in[(140,'Participante B','Sender B',S.AMBER),(1150,'Participante E1','Receiver E1',S.CYAN)]:
  S.panel(im,(x,352,x+620,670),col);S.bi(im,(x+310,386),es,en,40,col,'mm',550)
 if k==0:
  S.text(im,(450,535),str(story['private_value']),110,S.AMBER,True,'mm',500)
  S.bi(im,(1460,535),'No recibe ese dato','Private data not supplied',30,S.GRAY,'mm',540)
 elif k in(1,2):
  d=ImageDraw.Draw(im);d.line((790,510,1100,510),fill=S.CYAN,width=4)
  S.text(im,(945,454),'−1',54,S.CYAN,True,'mm',300)
  S.text(im,(450,535),'B',110,S.AMBER,True,'mm',500)
  S.text(im,(1460,535),'−1'if k==2 else'E1',100,S.CYAN,True,'mm',500)
 else:
  S.text(im,(450,530),'−1',80,S.AMBER,True,'mm',520)
  S.text(im,(1460,535),'−1',59,S.CYAN,True,'mm',560)
  S.text(im,(1460,625),'Mensaje utilizado / Message used',28,S.GRAY,False,'mm',550)
  S.text(im,(100,712),'Acción externa (transducción fija): 0 con mensaje · 1 sin mensaje',33,S.GRAY,width=1700)
  S.text(im,(100,760),'External command, fixed transduction: 0 with message · 1 without message',25,S.GRAY,width=1700)
 return im
def apd(scene,t):
 ev=A()['apd03']['events'];idx,p=sentence(scene,t);im=S.plain()
 if idx<=1:
  # Primera frase contiene adquisición, usos anteriores y continuidad.
  q=markrange(scene,0,2,t)
  if q<.5:
   label(im,'Aprender dos señales','Learning two signals')
   for j,(word,sign)in enumerate([('luma','+1'),('nara','−1')]):
    x=120+j*900;S.panel(im,(x,360,x+800,675),S.CYAN);S.bi(im,(x+400,392),'Enseñanza admitida','Teaching admitted',32,S.GRAY,'mm',720);S.text(im,(x+400,520),word+'  →  '+sign,78,S.CYAN,True,'mm',730)
  else:
   label(im,'Usar lo anterior después de aprender','Using prior learning after new teaching')
   for j,(es,en,value)in enumerate([('Señales anteriores','Previous signals','14 / 14'),('Consultas de memoria','Memory uses','6 / 6'),('Señales nuevas','New signals','2 / 2')]):
    x=110+j*590;S.panel(im,(x,350,x+560,680),S.CYAN);S.bi(im,(x+280,390),es,en,30,S.GRAY,'mm',510);S.text(im,(x+280,545),value,78,S.CYAN,True,'mm',490)
   S.text(im,(105,744),'Panel de usos después de las nuevas enseñanzas / Uses after new teaching',25,S.GRAY,width=1700)
  return im
 query=next(x for x in ev if x['kind']=='information_query');act=next(x for x in ev if x['kind']=='use_received_information')
 assert query['public_observation']['left']==28 and query['revealed_observation']['second']==13 and act['native_numeric_result']==15
 q=markrange(scene,2,4,t);step=min(3,int(q*4));S.text(im,(105,226),'Tarea / Task: apd03_goal_4',32,S.GRAY,width=1700)
 es=['Petición con un dato pendiente','DEE solicita y recibe el dato','La respuesta procede de DEE','La herramienta externa crea el archivo'][step]
 en=['Request with a missing datum','DEE requests and receives the datum','The response comes from DEE','The external tool creates the file'][step]
 S.bi(im,(105,300),es,en,42,S.WHITE,width=1710)
 if step==0:
  S.text(im,(960,557),'28 − ?',132,S.CYAN,True,'mm',1600)
 elif step==1:
  S.text(im,(500,555),'28 − ?',110,S.GRAY,True,'mm',700);S.text(im,(1430,555),'13',128,S.CYAN,True,'mm',650)
  S.bi(im,(1430,650),'Dato recibido','Received datum',32,S.GRAY,'mm',650)
 elif step==2:
  S.text(im,(960,555),'28 − 13 → 15',120,S.CYAN,True,'mm',1700)
 else:
  S.panel(im,(200,430,1720,712),S.CYAN)
  S.text(im,(245,453),'apd03_goal_4_attempt2.json',43,S.AMBER,True,width=1430)
  S.text(im,(245,551),'operands: [28, 13]     result: 15',47,S.CYAN,True,width=1430)
  S.text(im,(245,644),'Trabajador externo / External worker',31,S.GRAY,width=1430)
 progressrow(im,[('Petición','Request'),('Dato','Datum'),('Respuesta DEE','DEE response'),('Archivo','File')],step)
 return im
def body_demo(renderer,p=.5):
 b=old().base_module();parts=b.demo_particles(True)
 return renderer.render(parts,eye=S.lerp([95,-40,95],[90,-36,92],p),target=[32,32,32],bounds=(0,66),fov=48)
def platform(renderer,scene,t):
 import app_visual_r03 as app
 i,p=sentence(scene,t)
 if i in(0,3):return app.draw('overview',min(1,p*2))
 if i==1:im=body_demo(renderer,p)
 elif i==2:im=app.draw('teach',p)
 elif i>=5:
  im=S.plain();label(im,'Líneas de desarrollo','Development directions')
  for j,(a,b)in enumerate([('Asistentes con continuidad','Assistants with continuity'),('Respuestas ajustables','Responses that can be revised'),('Estudiar el aprendizaje','Studying learning')]):
   y=365+j*130;S.bi(im,(130,y),a,b,42,S.CYAN,width=1650)
  return im
 else:
  im=S.plain();label(im,'Una biblioteca que puede examinarse','An inspectable experimental library')
  for j,m in enumerate(read(W/'fuentes_extraidas/catalogo_R01_seleccion.json')['mechanisms']):
   S.text(im,(130,365+j*130),m['id']+' · '+m['name'],43,S.CYAN,True,width=1650)
   S.text(im,(130,422+j*130),'Ficha real del catálogo / Actual catalogue record',28,S.GRAY,width=1650)
  S.text(im,(1100,245),'Catálogo real R01',28,S.GRAY,width=700);return im
 # Tres capas relacionadas de una base; no tres productos independientes.
 for j,(a,b)in enumerate([('Universe','Motor / Engine'),('thinking','Herramientas / Tools'),('Cognitive','Aplicación / Application')]):
  x=105+j*590;S.panel(im,(x,665,x+560,790),S.CYAN if j==i-1 else S.MUTED)
  S.text(im,(x+280,691),a,32,S.WHITE,True,'mm',510);S.text(im,(x+280,747),b,26,S.GRAY,False,'mm',510)
 return im
def image_at(renderer,scene,t):
 import app_visual_r03 as app
 import mecanismos_g07_g08 as M
 import agregacion_r03 as AG
 i,p=sentence(scene,t);sid=scene['id'];cat='Visualización de registros / Recorded-data visualization';source='';es='';en=''
 if sid=='s01':
  if i==0:phase='overview'
  elif i==1:phase='before'
  elif i==2:phase='overview'
  elif i==3:phase='teach'if p<.42 else'after'
  else:phase='after'
  im=app.draw(phase,p);es='DEE COGNITIVE 2.0';en='Tecnología experimental de inteligencia / Experimental intelligence technology'
  cat='Captura de la aplicación / Application capture'if phase!='after'else'Captura y resultado registrado / Application capture and recorded result'
  source='DEE20_DEMO_01 · Misma señal, nueva enseñanza, respuesta revisada'
 elif sid=='s02':
  phase='overview'if i<=1 else'before'if i<=3 else'teach'if i in(4,6)else'compare'if i==8 else'after'if i in(5,7)else ('save'if p<.25 else'reopen'if p<.55 else'retained')if i==9 else'retained'
  if i==2:p=0
  if i==3:p=1
  im=app.draw(phase,p)
  es='MISMA SEÑAL'if i<=3 else'NUEVA ENSEÑANZA'if i==4 else'RESPUESTA REVISADA'if i==5 else'APRENDIZAJE'if i==6 else'MEMORIA'if i==7 else'PLASTICIDAD'if i==8 else'GUARDAR Y REABRIR'
  en={'MISMA SEÑAL':'SAME SIGNAL','NUEVA ENSEÑANZA':'NEW TEACHING','RESPUESTA REVISADA':'REVISED RESPONSE','APRENDIZAJE':'LEARNING','MEMORIA':'MEMORY','PLASTICIDAD':'PLASTICITY','GUARDAR Y REABRIR':'SAVE AND REOPEN'}[es]
  cat='Captura y lectura del registro / Application capture and recorded readout'
  source='DEE20_DEMO_01 · a13 → a21 → a22 → b09 · Revisión de una asociación heredada'
 elif sid=='s03':
  tt=10 if i<=2 else 10+2.97*p if i==3 else 13 if i in(4,5)else 5 if i==6 else 13
  im=M._world(renderer,M.g07_particles(tt))
  S.bi(im,(112,235),'Elementos del modelo','Elements of the model',40,S.WHITE,width=600)
  for yy,col,a,b in[(397,S.CYAN,'Señal','Signal'),(570,S.AMBER,'Relaciones adquiridas','Learned relationships')]:
   ImageDraw.Draw(im).ellipse((116,yy+8,140,yy+32),fill=col);S.bi(im,(166,yy),a,b,38,col,width=600)
  es='INFORMACIÓN EN UN ESPACIO 3D';en='INFORMATION IN A 3D SPACE'
  cat='Reconstrucción del mecanismo / Mechanism reconstruction';source='G07 · Otro experimento · Colores editoriales para seguir las funciones'
  if i>=0:ImageDraw.Draw(im).ellipse((132,596,156,620),fill=S.VIOLET)
  if i>=5:S.bi(im,(1140,245),'Mismas reglas','Same rules',39,S.GRAY,width=620)
 elif sid=='s04':
  if i<=1:phase='enseñanza';pp=.0
  elif i==2:phase='enseñanza';pp=p
  elif i==3:phase='consulta';pp=p
  elif i==4:phase='primer_encuentro';pp=p
  elif i==5:phase='viaje';pp=p
  elif i==6:phase='segundo_encuentro';pp=p
  elif i in(7,8):phase='resultado';pp=p
  elif i==9:phase='control';pp=p
  else:phase='recap';pp=p
  im=M.g07(renderer,phase,pp);es='COMBINAR LO APRENDIDO';en='COMBINING ACQUIRED RELATIONSHIPS';cat='Reconstrucción del mecanismo / Mechanism reconstruction'
  source='G07 · Consulta nueva 20 · Dos relaciones adquiridas'if phase!='control'else'Comparación experimental separada · C6H04 · N64 · Dos registros reales'
  if phase=='control':es='COMPARACIÓN EXPERIMENTAL';en='EXPERIMENTAL COMPARISON';cat='Visualización de registros / Recorded-data visualization'
 elif sid=='s05a':
  if i<=1:
   pp=markrange(scene,0,2,t);im=social(pp);es='COMUNICAR';en='COMMUNICATE';source='IC01 · B y E1 · Mensaje formado y uso posterior registrados'
  else:
   pp=markrange(scene,2,4,t);im=M.g08(renderer,pp);es='TRANSFERIR';en='TRANSFER';source='G08 · Otra realización · La relación −5 viaja y se utiliza';cat='Reconstrucción del mecanismo / Mechanism reconstruction'
 elif sid=='s05b':
  im=aa(min(1,t/max(.01,scene['voice_duration'])));es='ACCEDER A LO APRENDIDO';en='ACCESS WHAT WAS LEARNED';source='AA46 · Dos historias opuestas · Contenido previo y enseñanza del acceso'
 elif sid=='s05c':
  if i==0:im=u0(renderer,p);es='PREVER Y COMPARAR';en='PREDICT AND COMPARE';source='U0 · Emisión anterior al resultado · Eventos discretos registrados'
  else:im=consequence(markrange(scene,1,3,t));es='APRENDER DE CONSECUENCIAS';en='LEARN FROM CONSEQUENCES';source='Ciclo 02 · Retorno intacto frente a retorno omitido'
 elif sid=='s05d':
  im=AG.draw(renderer,min(1,t/max(.1,scene['voice_duration'])));es='INTEGRAR INFORMACIÓN';en='INTEGRATE INFORMATION';source='MU/FI01 · 128 componentes de entrada · Pruebas emparejadas con un cambio'
 elif sid=='s06':
  im=apd(scene,t);es='FUNCIONES EN UNA MISMA TRAYECTORIA';en='FUNCTIONS IN ONE TRAJECTORY';source='APD03_MAIN · Historia propia · El archivo lo produce la herramienta externa'
 elif sid=='s07':
  im=platform(renderer,scene,t);es='MOTOR · HERRAMIENTAS · APLICACIÓN';en='ENGINE · TOOLS · APPLICATION';source='DEE Universe · DEE thinking · DEE Cognitive · Base para evaluación y desarrollo'
  if i>=5:cat='Línea de desarrollo / Development direction'
  elif i in(0,3):cat='Captura de la aplicación / Application capture'
  elif i==1:cat='Configuración guardada · Cámara editorial / Saved configuration · Editorial camera'
 elif sid=='s08':
  if i==0:im=app.draw('retained',1)
  elif i==1:im=M.g07(renderer,'recap',1);cat='Reconstrucción del mecanismo / Mechanism reconstruction'
  elif i==2:im=apd(next(s for s in read(W/'timeline_R03.json')['scenes']if s['id']=='s06'),999)
  elif i in(3,4):im=app.draw('overview',p);cat='Captura de la aplicación / Application capture'
  else:im=app.draw('retained',1);cat='Captura de la aplicación / Application capture'
  es='INTELIGENCIA FUNCIONAL';en='FUNCTIONAL INTELLIGENCE';source='Recapitulación · Asociación revisada · Composición · Información y actuación'
  if i>=3:es='INVESTIGACIÓN DESARROLLADA EN PUEBLA';en='RESEARCH DEVELOPED IN PUEBLA'
  if i>=4:es='DEE COGNITIVE 2.0';en='La experiencia cambia cómo responde el sistema / Experience changes how the system responds'
 else:raise ValueError(sid)
 detail=None
 if sid in('s01','s02') and (phase=='before' or (sid=='s02' and i==5)):detail='+1 / −1: dos códigos de respuesta / two response codes'
 return S.finish(im,es,en,cat,source,detail)
def preview(ids=None):
 plan=read(W/'timeline_R03.json');r=renderer()
 for s in plan['scenes']:
  if ids and s['id']not in ids:continue
  times=sorted(set([.2,s['duration']-.4]+[m['start']+.3 for m in s['marks']]+[s['duration']*.5]))
  for k,t in enumerate(times):
   t=min(t,s['duration']-.01);im=image_at(r,s,t)
   cap=next((c for c in plan['captions']['en']if c['start']<=s['start']+t<c['end']),None)
   if cap:S.caption(im,cap['lines'])
   im.save(W/'previas'/f'{s["id"]}_{k:02}.png')
  print('PREVIEW',s['id'],len(times),flush=True)
 save(W/'qc/renderer.json',r.info);r.close()
def render(ids=None):
 plan=read(W/'timeline_R03.json');r=renderer()
 for s in plan['scenes']:
  if ids and s['id']not in ids:continue
  out=W/'escenas_limpias'/f'{s["id"]}.mp4'
  if out.exists():
   print('EXISTING_SCENE',s['id'],'not overwritten',flush=True);continue
  versions={}
  (W/'revisiones').mkdir(exist_ok=True)
  for f in W.glob('*.py'):
   digest=sha(f);versions[f.name]=digest;target=W/'revisiones'/(f.stem+'_'+digest[:16]+'.py')
   if not target.exists():target.write_bytes(f.read_bytes())
  log=(W/'escenas_limpias'/f'{s["id"]}.log').open('wb')
  proc=subprocess.Popen([str(FF),'-v','warning','-nostdin','-n','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','30','-i','pipe:0','-an','-c:v','libx264','-threads','3','-preset','fast','-crf','16','-pix_fmt','yuv420p','-r','30','-fps_mode','cfr',str(out)],stdin=subprocess.PIPE,stderr=log)
  start=time.monotonic();cached_key=None;cached=None
  try:
   for frame in range(s['frames']):
    t=frame/30
    # La imagen se conserva cuando el acontecimiento registrado está detenido.
    # Los movimientos de las reconstrucciones se calculan a30FPS.
    key=frame
    if t>s['voice_duration']:key='end_hold'
    if key!=cached_key:cached=image_at(r,s,t).tobytes();cached_key=key
    proc.stdin.write(cached)
    if frame and frame%600==0:print('FRAME',s['id'],frame,'/',s['frames'],flush=True)
   proc.stdin.close();assert proc.wait(timeout=180)==0
  finally:
   if proc.poll()is None:proc.terminate();proc.wait(timeout=30)
   log.close()
  save(W/'escenas_limpias'/f'{s["id"]}.json',dict(frames=s['frames'],host_seconds=time.monotonic()-start,sha256=sha(out),new_native_ticks=0,executed_sources=versions))
  print('SCENE_DONE',s['id'],s['frames'],round(time.monotonic()-start,1),flush=True)
 r.close()
def music():
 plan=read(W/'timeline_R03.json');rate=48000;n=round(plan['duration']*rate);out=np.zeros((n,2),np.float32)
 chords=[[130.8128,155.5635,195.9977],[103.8262,155.5635,207.6523],[116.5409,146.8324,174.6141],[97.9989,130.8128,195.9977]]
 for begin in np.arange(0,plan['duration'],18):
  a=round(begin*rate);length=min(n-a,round(20*rate));t=np.arange(length)/rate;env=np.minimum(1,t/2)*np.maximum(0,np.minimum(1,(20-t)/3));v=np.zeros((length,2))
  for hz in chords[int(begin/18)%4]:
   v[:,0]+=(np.sin(2*np.pi*hz*t)+.22*np.sin(2*np.pi*2*hz*t))*.0028*env
   v[:,1]+=np.sin(2*np.pi*hz*t+.12)*.0028*env
  out[a:a+length]+=v.astype(np.float32)
 out*=np.minimum(1,np.arange(n)/(rate*2))[:,None];out*=np.minimum(1,(n-np.arange(n))/(rate*3))[:,None]
 with wave.open(str(W/'voz/ambiente_R03.wav'),'wb')as f:f.setparams((2,2,rate,0,'NONE','not compressed'));f.writeframes((np.clip(out,-1,1)*32767).astype('<i2').tobytes())
 print('MUSIC original procedural design',flush=True)
def mux():
 plan=read(W/'timeline_R03.json');cat=W/'concatenar_R03.txt'
 cat.write_text('\n'.join("file 'escenas_limpias/"+s['id']+".mp4'"for s in plan['scenes'])+'\n',encoding='utf-8')
 clean=W/'montaje_limpio_R03.mp4';assert not clean.exists()
 com=[str(FF),'-hide_banner','-nostdin','-i',str(W/'voz/locucion_continua_R03.wav'),'-i',str(W/'voz/ambiente_R03.wav')]
 meas=subprocess.run(com+['-filter_complex','[0:a]aformat=channel_layouts=stereo[v];[v][1:a]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json[a]','-map','[a]','-f','null','NUL'],capture_output=True,text=True,encoding='utf-8',errors='replace',check=True)
 m=json.loads(re.findall(r'\{\s*"input_i".*?\}',meas.stderr,re.S)[-1])
 norm=f'loudnorm=I=-16:TP=-1.5:LRA=9:measured_I={m["input_i"]}:measured_TP={m["input_tp"]}:measured_LRA={m["input_lra"]}:measured_thresh={m["input_thresh"]}:offset={m["target_offset"]}:linear=true:print_format=json'
 cmd=[str(FF),'-hide_banner','-nostdin','-n','-f','concat','-safe','0','-i',str(cat),'-i',str(W/'voz/locucion_continua_R03.wav'),'-i',str(W/'voz/ambiente_R03.wav'),'-filter_complex','[1:a]aformat=channel_layouts=stereo[v];[v][2:a]amix=inputs=2:normalize=0,'+norm+'[a]','-map','0:v:0','-map','[a]','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-t',str(plan['duration']),'-movflags','+faststart',str(clean)]
 done=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace',check=True)
 (W/'qc/mux_audio.log').write_text(done.stderr,encoding='utf-8')
 rec=read(W/'REGISTRO_R03.json');rec['quality']['mix']={'measurement':m,'export':json.loads(re.findall(r'\{\s*"input_i".*?\}',done.stderr,re.S)[-1]),'music':'Original procedural design reused, no third-party music','human_listening':'pendiente'};save(W/'REGISTRO_R03.json',rec)
 print('CLEAN_MASTER',clean.stat().st_size,flush=True)
def export():
 assert not MAIN.exists()
 vf="ass=subtitulos_R03_EN.ass,setsar=1"
 # ASS con PlayRes1920x1080 y fuente46px; sin reducción de resolución.
 cmd=[str(FF),'-hide_banner','-nostdin','-n','-i',str(W/'montaje_limpio_R03.mp4'),'-vf',vf,'-map','0:v:0','-map','0:a:0','-c:v','libx264','-threads','6','-preset','medium','-crf','19','-profile:v','high','-pix_fmt','yuv420p','-r','30','-fps_mode','cfr','-c:a','copy','-movflags','+faststart','-metadata','title=DEE Cognitive 2.0 — Inteligencia funcional R03','-metadata','artist=Ivan Erick Tlaltecatl Morales',str(MAIN)]
 with (W/'qc/export_R03.log').open('wb')as log:subprocess.run(cmd,cwd=W,stdout=log,stderr=log,check=True)
 print('EXPORTED',MAIN.stat().st_size,sha(MAIN),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['plan','preview','render','music','mux','export']);p.add_argument('--ids',nargs='*');a=p.parse_args()
 {'plan':plan,'preview':lambda:preview(a.ids),'render':lambda:render(a.ids),'music':music,'mux':mux,'export':export}[a.action]()
