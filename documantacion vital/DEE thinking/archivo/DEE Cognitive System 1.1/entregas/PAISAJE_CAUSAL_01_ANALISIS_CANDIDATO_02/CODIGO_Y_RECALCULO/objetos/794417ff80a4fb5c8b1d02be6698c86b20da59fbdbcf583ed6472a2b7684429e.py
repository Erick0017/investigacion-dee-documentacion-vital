"""Static scientific figures from indexed measurements, never an E1 renderer."""
from pathlib import Path
import argparse,json,math,textwrap
from collections import Counter
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser();p.add_argument('--stage',type=Path,required=True);p.add_argument('--evidence',type=Path,required=True);a=p.parse_args();out=a.stage/'ATLAS_CAUSAL';out.mkdir(parents=True,exist_ok=True)
fontpath='C:/Windows/Fonts/segoeui.ttf';boldpath='C:/Windows/Fonts/seguisb.ttf'
def font(n,bold=False):return ImageFont.truetype(boldpath if bold else fontpath,n)
def canvas(title,subtitle,h=820):
    im=Image.new('RGB',(1400,h),'white');d=ImageDraw.Draw(im);d.text((45,28),title,font=font(32,True),fill='#111111');d.text((45,78),subtitle,font=font(20),fill='#333333');return im,d
def wrapped(d,text,xy,width=75,size=20,fill='#222222'):
    x,y=xy
    for line in textwrap.wrap(text,width=width):d.text((x,y),line,font=font(size),fill=fill);y+=size+8
    return y
def box(d,xy,text,positive=None):
    fill='#eef4f7'if positive is None else'#e4f2eb'if positive else'#fbeae9';d.rounded_rectangle(xy,radius=6,fill=fill,outline='#adb7bf',width=1);l,t,r,b=xy;bounds=d.textbbox((0,0),text,font=font(27,True));d.text(((l+r-(bounds[2]-bounds[0]))/2,(t+b-34)/2),text,font=font(27,True),fill='#102b3f')
def native(v):
    n=int(v['raw']);s=lambda k:((n>>k)&15)-16 if((n>>k)&15)&8 else(n>>k)&15
    return n&0xffffffff,(n>>60)&15,(n>>32)&65535,[s(48),s(52),s(56)]
def read(group,case):return json.loads((a.evidence/group/case/'PRIMARIOS.json').read_bytes())

calc=json.loads((a.stage/'ATLAS_CAUSAL/CALCULOS_CAUSALES.json').read_bytes());key='PROCEDENCIA_01/reference_trace/CAMPO_COMPLETO.jsonl.gz';q=calc['global_atlas'][key];counts=Counter()
for position,n in q['encounter_sites']:
    x,y,z=map(int,position.split(','));counts[x,y]+=n
im,d=canvas('Concentración local observada','Proyección XY de candidatos balísticos, suma en Z. No es un mapa causal exhaustivo.');x0,y0,step=90,145,8;maximum=max(counts.values(),default=1)
for x in range(67):
    for y in range(67):
        value=counts[x,y];scale=math.log1p(value)/math.log1p(maximum);color=(int(244-195*scale),int(248-145*scale),int(250-100*scale));px=x0+x*step;py=y0+(66-y)*step;d.rectangle((px,py,px+step-1,py+step-1),fill=color)
d.rectangle((x0,y0,x0+67*step,y0+67*step),outline='#555555',width=1)
for v in(0,16,32,48,66):
    d.text((x0+v*step-10,y0+67*step+8),str(v),font=font(17),fill='black');d.text((x0-35,y0+(66-v)*step-10),str(v),font=font(17),fill='black')
d.text((x0+250,y0+67*step+38),'x',font=font(21),fill='black');d.text((45,y0+250),'y',font=font(21),fill='black')
text='Rama reference_trace. T'+str(q['timeline'][0]['tick'])+'–'+str(q['timeline'][-1]['tick'])+'. '+str(q['sampled_frames'])+' campos registrados. Ocupación máxima: '+str(q['max_occupied'])+'/'+str(67**3)+' sitios. '+str(q['visited_sites_in_sampled_frames'])+' posiciones RAW≠0 visitadas en las muestras.'
y=wrapped(d,text,(690,155),width=51,size=23);y=wrapped(d,'Los focos no significan pensamientos, energía ni funciones localizadas. Incluyen campos no nulos con state=0. La influencia puede entrar desde otras regiones.',(690,y+25),width=53,size=21);y=wrapped(d,'Los enlaces decisivos se contrastan con historias, cortes y shams. Los candidatos se calculan en campos previos a nuevas entradas de frontera; las admisiones decisivas se incorporan en el recálculo 21.',(690,y+24),width=53,size=21)
d.text((45,775),'Datos: COBERTURA_Y_OCUPACION.csv, CONCENTRACION_CANDIDATOS.csv y campo original indexado.',font=font(17),fill='#444444');im.save(out/'01_CONCENTRACION_LOCAL.png')

panel=json.loads((a.stage/'ATLAS_CAUSAL/PANEL_R33_POR_FUNCION.json').read_bytes());im,d=canvas('Conservación por función y preparación','Mismo estado inicial completo T32583. Doce bloques y panel final; las funciones no se suman en una puntuación.',h=700);columns=[('magnitude','Magnitud'),('spatial','Espacio'),('contact','Toca'),('free','No toca')];labels=[('far_guard','Protección'),('far_guard_sham','Sham de protección'),('far_divert','Desvío'),('far_divert_sham','Sham de desvío')]
for j,(key,label)in enumerate(columns):d.text((480+j*215,145),label,font=font(24,True),fill='black')
for i,(key,label)in enumerate(labels):
    y=200+i*88;d.text((45,y+22),label,font=font(24),fill='black');r=panel['PROTECCION_BIDIRECCIONAL_33/'+key]
    for j,(field,_)in enumerate(columns):
        num,den=r[field];box(d,(445+j*215,y,635+j*215,y+65),str(num)+'/'+str(den),num==den)
wrapped(d,'El acceso a «no toca» cambia sin una pérdida global de las otras funciones. Intervenciones P0 preparadas, no estrategia P2. Horizonte finito de 96 oportunidades de retorno N67, no estabilidad ilimitada.',(45,590),width=112,size=20);im.save(out/'02_CONSERVACION_POR_FUNCION.png')

im,d=canvas('El mismo contexto puede ayudar o perjudicar','R44 compara dos lectores y una consecuencia bajo corte selectivo y sham, sin editar RAW.',h=650)
for j,label in enumerate(('Forma en lector original','Forma en nuevo lector','Acción del nuevo lector')):wrapped(d,label,(440+j*290,145),width=22,size=21)
for i,(key,label)in enumerate((('uncut','Sin corte'),('cut','Corte de la corriente'),('sham','Sham'))):
    v=read('CONTEXTO_UTIL_MIXTO_44',key);old=v['old_reader']['ENTE'][0]['records']['d1'];goodold=native(old)[0]==1 and native(old)[1]==1 and native(old)[3]==[1,1,1];flags=[goodold,bool(v['SPANISH_DECODED']),v['NATIVE_ACTION_OBSERVED']];y=230+i*95;d.text((45,y+20),label,font=font(24),fill='black')
    for j,flag in enumerate(flags):box(d,(430+j*290,y,695+j*290,y+65),'Sí'if flag else'No',flag)
wrapped(d,'El corte conserva la firma antigua y priva al nuevo lector de su ruta. El aporte fijo del nuevo lector participa en el código: reconocimiento asistido, no recuperación autónoma de significados.',(45,550),width=112,size=20);im.save(out/'03_CONTEXTO_MIXTO.png')

v=read('LECTOR_POST_TRANSFORMACION_41','full');im,d=canvas('Uso nativo de una influencia transformada','La historia es necesaria y el lector también aporta componentes preparados. No se reenseña después del encuentro.',h=740)
values=[('Experiencia y señal',39823,'XYZ11'),('Encuentro con contexto',39836,'YZ'+str(native(v['transformed'])[2])),('Lector material fijo',39844,'XYZ'+str(native(v['reader'])[2])),('Consecuencia',39848,'Z'+str(native(v['action'])[2]))]
for i,(label,tick,text)in enumerate(values):
    x=50+i*340;d.rounded_rectangle((x,160,x+290,365),radius=8,fill='#f1f5f7',outline='#8b9aa5',width=2);wrapped(d,label,(x+16,180),width=18,size=22);d.text((x+18,270),text,font=font(29,True),fill='#154d66');d.text((x+18,322),'T'+str(tick),font=font(20),fill='#333333')
    if i<3:d.line((x+294,260,x+329,260),fill='#4e626f',width=3);d.polygon([(x+329,260),(x+319,253),(x+319,267)],fill='#4e626f')
wrapped(d,'Controles sin señal docente, sin acontecimiento A y sham: no firma cualificada ni acción. Reservas: dosis docente 5 y retraso de un período conservaron el efecto con el mismo criterio. La rama sin acción permitió una consulta posterior.',(50,420),width=112,size=22)
wrapped(d,'Continuidad operativa: PC01_NORMALIZADO45 T41318 intercaló funciones anteriores, guardó y consultó el código en otros procesos. No prueba interpretación actual de una nueva escena +1 ni selección autónoma del lector.',(50,555),width=112,size=21);im.save(out/'04_INFLUENCIA_REUTILIZADA.png')
print(json.dumps({'figures':[p.name for p in sorted(out.glob('*.png'))],'static_only_no_engine':True}))
