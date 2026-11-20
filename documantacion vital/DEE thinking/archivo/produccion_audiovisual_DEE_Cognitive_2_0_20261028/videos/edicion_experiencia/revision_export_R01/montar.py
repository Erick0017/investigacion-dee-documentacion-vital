"""Animación editorial y montaje de archivos. Cero ejecución/importación DEE."""
from __future__ import annotations
from pathlib import Path
from functools import lru_cache
from bisect import bisect_right
import argparse,hashlib,json,math,re,subprocess,time,wave
import numpy as np
from PIL import Image,ImageDraw,ImageFont
W=Path(__file__).resolve().parent;ROOT=W.parents[1];BASE=ROOT.parent.parents[1]
OLD=BASE/'_dee20_trabajo/video_publico_definitivo'
FF=BASE/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
PROBE=OLD/'herramientas/ffprobe.exe'
D=json.loads((W/'fuentes_y_control.json').read_text(encoding='utf8'))
G=json.loads((W/'guion_aplicado.json').read_text(encoding='utf8'))
SRC=Path(D['source_video']);OUT=W/'Experiencia_R01.mp4'
BG='#0B1420';FG='#F5F7FA';GRAY='#B9C4D0';TEAL='#44D8C1';AMBER='#FFBE66';LINE='#34485B';PANEL='#122437'

@lru_cache(None)
def font(size,b=False):return ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf' if b else 'C:/Windows/Fonts/segoeui.ttf',size)
def text(im,xy,s,size=60,color=FG,b=False,anchor=None):
    assert size>=34,(s,size)
    ImageDraw.Draw(im).text(xy,str(s),font=font(size,b),fill=color,anchor=anchor)
def middle(im,xy,s,size=60,color=FG,b=True):text(im,xy,s,size,color,b,'mm')
def lines(im,xy,ss,size=60,color=FG,b=True,gap=1.12):
    for j,s in enumerate(ss):middle(im,(xy[0],xy[1]+(j-(len(ss)-1)/2)*size*gap),s,size,color,b)
def wrap(s,size=50,width=1710,maxwords=13):
    rows=[];row=[];dd=ImageDraw.Draw(Image.new('RGB',(1,1)))
    for token in s.split():
        if row and (len(row)>=maxwords or dd.textlength(' '.join(row+[token]),font=font(size))>width):rows.append(' '.join(row));row=[]
        row.append(token)
    if row:rows.append(' '.join(row))
    return rows
def ease(x):x=min(1.,max(0.,x));return x*x*(3-2*x)
def lerp(a,b,p):return a+(b-a)*ease(p)
def base(scene,category='Explicación visual',context=None):
    im=Image.new('RGB',(1920,1080),BG);title=G['scenes'][scene-1]['title']
    dd=ImageDraw.Draw(im);assert dd.textlength(title,font=font(80,True))<=1720,title
    text(im,(100,55),title,80,FG,True);dd.line((100,176,1820,176),fill=LINE,width=2)
    text(im,(100,855),category,36,GRAY)
    if context:text(im,(1820,855),context,36,GRAY,False,'rt')
    dd.line((100,920,1820,920),fill=LINE,width=2)
    return im
def region_tag(im,xy,s):text(im,xy,s,36,GRAY)
def panel(im,box,color=LINE,fill=PANEL,radius=22,width=3):ImageDraw.Draw(im).rounded_rectangle(tuple(map(int,box)),radius=radius,fill=fill,outline=color,width=width)
def arrow(im,a,b,color=TEAL,width=5,head=15):
    dd=ImageDraw.Draw(im);a=np.array(a,float);b=np.array(b,float);v=b-a;n=np.linalg.norm(v)
    if n<1:return
    u=v/n;p=np.array([-u[1],u[0]])
    dd.line([tuple(a),tuple(b-u*head*.65)],fill=color,width=width)
    dd.polygon([tuple(b),tuple(b-u*head+p*head*.55),tuple(b-u*head-p*head*.55)],fill=color)
def flow(im,points,p,color=TEAL,r=16):
    seg=[math.dist(a,b) for a,b in zip(points,points[1:])];total=sum(seg);distance=ease(p)*total
    for a,b,L in zip(points,points[1:],seg):
        if distance<=L:
            t=distance/L;x=a[0]+t*(b[0]-a[0]);y=a[1]+t*(b[1]-a[1]);break
        distance-=L
    else:x,y=points[-1]
    dd=ImageDraw.Draw(im);dd.ellipse((x-r,y-r,x+r,y+r),fill=color,outline=FG,width=2)
def token(im,xy,label=None,kind='input',w=440,h=116,color=TEAL):
    x,y=xy;dd=ImageDraw.Draw(im)
    if kind=='A':
        dd.ellipse((x-68,y-68,x+68,y+68),fill=BG,outline=color,width=7)
        if label:middle(im,(x,y-2),label,86,color)
    elif kind=='B':
        dd.polygon([(x,y-82),(x+82,y),(x,y+82),(x-82,y)],fill=BG,outline=color,width=7)
        if label:middle(im,(x,y-2),label,86,color)
    else:
        panel(im,(x-w/2,y-h/2,x+w/2,y+h/2),color,fill=BG,radius=18,width=4)
        if label:middle(im,(x,y-4),label,56,color)
def module(im,box=(740,340,1180,680),learned=False,label='DEE',active=0):
    x0,y0,x1,y1=box;panel(im,box,TEAL if active else LINE,fill=PANEL,width=4)
    middle(im,((x0+x1)/2,y0+75),label,68)
    dd=ImageDraw.Draw(im);cy=y1-90
    for j in range(3):
        x=x0+80+j*(x1-x0-160)/2;dd.ellipse((x-16,cy-16,x+16,cy+16),fill=AMBER if learned and j==1 else LINE)
    if learned:dd.line((x0+72,cy,x1-72,cy),fill=AMBER,width=5)
    if active:dd.rounded_rectangle((x0+15,y0+15,x1-15,y1-15),radius=18,outline=TEAL,width=2)
def subtitles(im,cues,absolute):
    starts=[c['start'] for c in cues];i=bisect_right(starts,absolute)-1
    if i>=0 and absolute<cues[i]['end']:
        rows=cues[i]['lines'];ys=[973] if len(rows)==1 else [947,1007]
        for y,s in zip(ys,rows):middle(im,(960,y),s,50,FG,False)

def build_plan():
    jobs=json.loads((W/'voz/encargos.json').read_text(encoding='utf8'));marks=json.loads((W/'voz/marcas.json').read_text(encoding='utf-8-sig'))
    pads=[[.45,.6,1.5],[.5,.7,1.0,.5,1.0,2.5],[.35,1.7,.7,.7,1.1,1.0],[.3,.4,.55,.5,.5,.6,1.2],[.45,.9,4.8,.6,1.4],[.4,.6,.7,1.1,1.2],[.5,.6,.6,1.0],[.65,.7,.6,1.3],[.65,.8,2.7]]
    # Sentence counts are fixed by the supplied literal paragraphs, not by paraphrase.
    print('SENTENCE_COUNTS',[len(s['sentences']) for s in G['scenes']],flush=True)
    assert [len(x) for x in pads]==[len(s['sentences']) for s in G['scenes']]
    pcm=bytearray();params=None;captions=[];scenes=[];utterances=[];offset=0.;cursor=0
    for sc,padlist in zip(G['scenes'],pads):
        begin=offset;bound=[]
        for j,paragraph in enumerate(sc['sentences']):
            job=jobs[cursor];m=marks[cursor];cursor+=1;assert m['text']==paragraph==job['text']
            with wave.open(job['out'],'rb') as f:pr=f.getparams();raw=f.readframes(f.getnframes());sec=f.getnframes()/f.getframerate()
            if params:assert pr[:3]==params[:3]
            params=pr
            gap=.35 if j==0 else 0
            pcm.extend(bytes(round(gap*pr.framerate)*pr.sampwidth*pr.nchannels));offset+=gap
            at=offset;pcm.extend(raw);offset+=sec;bound.append([at-begin,offset-begin]);utterances.append({'scene':sc['scene'],'sentence':j,'start':at,'end':offset,'text':paragraph})
            events=[]
            for e in m['marks']:
                k=min(len(job['char_map'])-1,int(e['start']));events.append((job['char_map'][k],float(e['seconds'])))
            factor=min(1.,(sec-.10)/max((t for _,t in events),default=1))
            rows=wrap(paragraph);groups=[rows[k:k+2] for k in range(0,len(rows),2)];char=0
            for k,group in enumerate(groups):
                joined=' '.join(group);start=paragraph.find(joined,char);end=start+len(joined);assert start>=0;char=end
                ts=[t*factor for p,t in events if p>=start];te=[t*factor for p,t in events if p>=end]
                a=0 if k==0 else min(ts,default=sec*k/len(groups));b=min(te,default=sec) if k<len(groups)-1 else sec
                assert b>a,(paragraph,a,b)
                captions.append({'start':at+a,'end':at+b,'lines':group,'text':joined,'scene':sc['scene']})
            pad=padlist[j];pcm.extend(bytes(round(pad*pr.framerate)*pr.sampwidth*pr.nchannels));offset+=pad
        extra=math.ceil(offset*30)/30-offset;pcm.extend(bytes(round(extra*params.framerate)*params.sampwidth*params.nchannels));offset+=extra
        scenes.append({'scene':sc['scene'],'start':begin,'end':offset,'duration':offset-begin,'sentences':bound})
    assert ' '.join(x['text'] for x in utterances)==' '.join(s['narration'] for s in G['scenes'])
    with wave.open(str(W/'voz/locucion_completa.wav'),'wb') as f:f.setparams(params);f.writeframes(pcm)
    plan={'scenes':scenes,'voice':utterances,'captions':captions,'duration':offset,'fps':30,'literal_words':G['words'],'new_native_ticks':0}
    (W/'timeline.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8')
    def stamp(t):
        n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
    (W/'subtitulos.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n'+ '\n'.join(c['lines']) for i,c in enumerate(captions))+'\n',encoding='utf8')
    print('TIMELINE',round(offset,3),'SECONDS',[(s['scene'],round(s['duration'],2)) for s in scenes],flush=True)

# All samples here are crops of the archived original movie. Their motion is not synthesized.
CLIPS={
 'before':(165.7,171.0,(22,408,512,473)),
 'teaching':(416.4,420.4,(18,513,514,625)),
 'after':(440.0,445.0,(18,355,512,418)),
 'save':(1278.9,1282.1,(18,375,512,591)),
 'close':(1299.1,1302.5,(16,183,514,359)),
 'open':(1376.8,1380.5,(18,314,514,458)),
 'old':(1401.5,1405.0,(22,407,512,472)),
 'revised':(1416.0,1421.0,(22,407,512,472)),
 'context':(69.0,72.0,(0,87,1262,710)),
 'ask':(165.7,169.0,(12,106,512,174)),
 'observe':(69.0,73.5,(552,302,1249,612)),
}
def prepare_clips():
    for name,(a,b,crop) in CLIPS.items():
        folder=W/'clips'/name;folder.mkdir(parents=True,exist_ok=True)
        if (folder/'complete.json').exists():
            meta=json.loads((folder/'complete.json').read_text())
            if meta['crop']==list(crop):continue
            archive=folder.with_name(name+'_encuadre_anterior')
            assert not archive.exists()
            folder.rename(archive);folder.mkdir()
        x,y,x1,y1=crop
        cmd=[str(FF),'-hide_banner','-v','error','-n','-ss',str(a),'-i',str(SRC),'-t',str(b-a),'-an','-vf',f'crop={x1-x}:{y1-y}:{x}:{y},fps=15','-q:v','1',str(folder/'%05d.jpg')]
        subprocess.run(cmd,check=True,timeout=60)
        count=len(list(folder.glob('*.jpg')));assert count>5
        (folder/'complete.json').write_text(json.dumps({'source':str(SRC),'start':a,'end':b,'crop':crop,'frames':count,'fps':15,'speed':1.0}),encoding='utf8')
        print('CLIP_READY',name,count,flush=True)
@lru_cache(maxsize=100)
def clip_frame(name,index):return Image.open(W/'clips'/name/f'{index+1:05}.jpg').convert('RGB')
def real_clip(im,name,t,box=(100,290,1080,470)):
    meta=json.loads((W/'clips'/name/'complete.json').read_text());idx=min(meta['frames']-1,max(0,int(t*15)))
    src=clip_frame(name,idx);x,y,w,h=map(int,box);ratio=min(w/src.width,h/src.height)
    pic=src.resize((round(src.width*ratio),round(src.height*ratio)),Image.Resampling.LANCZOS)
    panel(im,(x-5,y-5,x+w+5,y+h+5));im.paste(pic,(x+(w-pic.width)//2,y+(h-pic.height)//2))
def proof(scene,name,t,label=None,value=None,context='DEE Cognitive 2.0'):
    im=base(scene,'Grabación real',context)
    if label is None:
        real_clip(im,name,t,(100,248,1720,565));return im
    region_tag(im,(100,235),'Grabación real');region_tag(im,(1220,235),'Datos de una prueba')
    real_clip(im,name,t,(100,323,1040,437))
    panel(im,(1210,324,1820,760),TEAL,fill=BG)
    rows=wrap(label,56,550,10);lines(im,(1515,410),rows,56)
    if value is not None:
        tag='A' if value==1 else 'B';token(im,(1515,555),tag,tag,color=TEAL if tag=='A' else AMBER)
        middle(im,(1515,688),'+1' if value==1 else '−1',86,TEAL if tag=='A' else AMBER)
    else:middle(im,(1515,585),'−1' if name=='teaching' else '',110,AMBER)
    return im

def association(im,p,after=False,teaching=False,initial=False):
    a=(355,505);m=(960,505);z=(1600,505)
    arrow(im,(645,505),(725,505),LINE);arrow(im,(1200,505),(1500,505),LINE)
    module(im,learned=after or (teaching and p>.5),label='DEE',active=1 if .28<p<.72 else 0)
    # The same rounded rectangular signal is used before and after teaching.
    token(im,a,'Nueva enseñanza' if teaching else 'Señal de prueba',w=540 if teaching else 500,color=AMBER if teaching else TEAL)
    if p<.5:flow(im,[(645,505),(960,505)],p*2,AMBER if teaching else TEAL,20)
    if teaching:
        if p>=.5:
            dd=ImageDraw.Draw(im);dd.line((820,590,1100,590),fill=AMBER,width=8)
            middle(im,(960,745),'Nueva enseñanza',60,AMBER)
    elif not initial and p>.45:
        kind='B' if after else 'A';token(im,(lerp(1210,z[0],(p-.45)/.40),505),kind,kind,color=AMBER if after else TEAL)
        if p>.8:middle(im,(1600,660),'Respuesta '+kind,56)

def comparison(im,p=1,retained=False):
    labels=['Señal de prueba','Otra asociación'] if retained else ['Antes','Después']
    for i,x in enumerate([520,1400]):
        panel(im,(x-390,270,x+390,755),TEAL if i==0 else AMBER,fill=BG)
        middle(im,(x,333),labels[i],60)
        kind=('B' if i==0 else 'A') if retained else ('A' if i==0 else 'B')
        token(im,(x,485),kind,kind,color=AMBER if kind=='B' else TEAL)
        middle(im,(x,657),'−1' if kind=='B' else '+1',100,AMBER if kind=='B' else TEAL)
    if not retained:
        arrow(im,(925,525),(1005,525),GRAY,5)
        middle(im,(960,805),'La respuesta cambió',58)
    else:middle(im,(960,805),'Aprendizaje conservado',58)

def grid(im,p,learned=False,output=False,mini=False):
    # Deliberately schematic fixed projection. No measured XYZ or trajectories are claimed.
    cx,cy=960,495;dd=ImageDraw.Draw(im)
    points={(x,y):(cx+(x-y)*78,cy+(x+y-2)*44) for x in range(3) for y in range(3)}
    for (x,y),(px,py) in points.items():
        for k in [(x+1,y),(x,y+1)]:
            if k in points:dd.line(((px,py),points[k]),fill=LINE,width=3)
        fill=AMBER if learned and (x,y)==(1,1) else PANEL
        dd.polygon([(px,py-30),(px+43,py-7),(px+43,py+25),(px,py+48),(px-43,py+25),(px-43,py-7)],fill=fill,outline=TEAL if (x,y)==(1,1) and .35<p<.65 else LINE,width=3)
    middle(im,(330,320),'Experiencia' if learned and not output else 'Entrada',60,AMBER if learned and not output else TEAL)
    middle(im,(960,273),'DEE',68);middle(im,(1610,320),'Respuesta',60)
    arrow(im,(500,505),(750,505),LINE);arrow(im,(1200,505),(1480,505),LINE)
    if p<.55:flow(im,[(390,505),(960,505)],p/.55,AMBER if learned and not output else TEAL,22)
    if output and p>.55:
        kind='B' if learned else 'A';token(im,(lerp(1150,1620,(p-.55)/.35),505),None,kind,color=AMBER if learned else TEAL)
    if mini:
        for x,name,kind in [(510,'Antes','A'),(1410,'Después','B')]:
            middle(im,(x,729),name,56);token(im,(x+210,729),None,kind,color=TEAL if kind=='A' else AMBER)

def cascade(im,p,mode):
    if mode=='separate':
        module(im,(350,310,800,730),p>.48,'',0);module(im,(1120,310,1570,730),p>.48,'',0)
        middle(im,(575,385),'Aprendizaje 1',60);middle(im,(1345,385),'Aprendizaje 2',60)
        if p<.6:
            flow(im,[(215,510),(575,510)],p/.6,TEAL,22)
            flow(im,[(1710,510),(1345,510)],p/.6,AMBER,22)
        if p>.6:arrow(im,(815,510),(1105,510),TEAL,6)
        return
    centers=[(680,480),(1280,480)]
    for j,(x,y) in enumerate(centers):
        panel(im,(x-235,y-160,x+235,y+155),TEAL,fill=PANEL)
        middle(im,(x,y-80),'Aprendizaje '+str(j+1),58)
        dd=ImageDraw.Draw(im);dd.line((x-135,y+65,x+135,y+65),fill=AMBER,width=6)
    arrow(im,(915,480),(1045,480),LINE);arrow(im,(245,480),(445,480),LINE);arrow(im,(1515,480),(1740,480),LINE)
    middle(im,(250,716),'Entrada',56);middle(im,(960,716),'Resultado intermedio',56);middle(im,(1600,716),'Resultado final',56)
    if mode=='stage1':
        x=lerp(245,960,p);token(im,(x,480),None,'input',w=100,h=100,color=TEAL)
        if p>.65:ImageDraw.Draw(im).line((x-28,468,x+28,492),fill=TEAL,width=6)
    elif mode=='stage2':
        x=lerp(960,1710,p);token(im,(x,480),None,'input',w=100,h=100,color=AMBER)
        if p>.65:ImageDraw.Draw(im).line((x-28,490,x+28,470),fill=AMBER,width=6)
    else:
        flow(im,[(245,480),(1710,480)],p,TEAL,22)
        middle(im,(960,805),'Dos aprendizajes participan juntos',58)

def cascade_data(im,p,control=False):
    vals=[17,38,65]
    labels=['Entrada','Resultado intermedio','Resultado final']
    for x,value,label in zip([340,960,1580],vals,labels):
        middle(im,(x,318),label,56);middle(im,(x,440),str(value),142,TEAL)
    for a,b in [(520,790),(1130,1400)]:arrow(im,(a,440),(b,440),TEAL,6)
    if control:
        middle(im,(960,606),'Sin el segundo aprendizaje',56,GRAY)
        for x,value in zip([340,960,1580],[17,38,38]):middle(im,(x,726),str(value),106,AMBER)
        for a,b in [(520,790),(1130,1400)]:arrow(im,(a,726),(b,726),GRAY,5)
    else:
        idx=min(2,int(p*3));x=[340,960,1580][idx]
        ImageDraw.Draw(im).rounded_rectangle((x-155,365,x+155,535),radius=20,outline=AMBER,width=4)

def query(im,p,mode):
    if mode=='compare':
        for x,label in [(450,'Respuesta anterior'),(1470,'Dato nuevo')]:
            middle(im,(x,300),label,60);token(im,(x,470),None,'A' if x<900 else 'B',color=TEAL if x<900 else AMBER)
        arrow(im,(620,470),(880,470),LINE);arrow(im,(1300,470),(1040,470),LINE)
        flow(im,[(620,470),(960,470)],p,TEAL,20);flow(im,[(1300,470),(960,470)],p,AMBER,20)
        if p>.6:middle(im,(960,703),'Diferencia',68,AMBER)
        return
    nodes=[(440,380,'Diferencia'),(1450,380,'Consulta'),(1450,690,'Información recibida'),(440,690,'Información utilizada')]
    for j,(x,y,label) in enumerate(nodes):
        if j>1 and mode=='request':continue
        if j==3 and mode=='receive':continue
        panel(im,(x-345,y-66,x+345,y+66),AMBER if j==0 else TEAL,fill=BG)
        middle(im,(x,y-3),label,56)
    arrow(im,(790,380),(1100,380),LINE);flow(im,[(790,380),(1100,380)],p,TEAL,18)
    if mode in ['receive','use','summary']:
        arrow(im,(1450,450),(1450,615),LINE)
        flow(im,[(1450,450),(1450,615)],p,AMBER,22)
    if mode in ['use','summary']:
        arrow(im,(1100,690),(790,690),LINE);flow(im,[(1100,690),(790,690)],p,AMBER,22)

def application(im,p,mode):
    dd=ImageDraw.Draw(im)
    if mode=='continuity':
        middle(im,(960,265),'Asistentes con continuidad',64)
        q=1 if p<.36 or p>.65 else max(.06,abs(p-.50)*6.8)
        x0=460;y0=350;y1=y0+375*q
        panel(im,(x0,y0,1460,y1),TEAL,fill=BG)
        if q>.6:
            dd.line((x0,y0+65,1460,y0+65),fill=LINE,width=3)
            for j in range(2):
                yy=y0+132+j*100
                if yy<y1-35:
                    dd.line((550,yy,575,yy+22,620,yy-27),fill=TEAL,width=7);dd.line((680,yy,1350,yy),fill=GRAY,width=8)
        if p<.35:flow(im,[(250,515),(450,515)],p/.35,TEAL,24)
    elif mode=='changing':
        middle(im,(960,265),'Sistemas que se ajustan a cambios',64)
        module(im,(740,360,1180,715),p>.5,label='DEE',active=.3<p<.65)
        if p<.48:token(im,(lerp(295,720,p/.48),515),'Dato anterior',w=480,color=GRAY)
        if p>=.25 and p<.75:token(im,(lerp(295,900,(p-.25)/.5),515),'Dato nuevo',w=460,color=AMBER)
        token(im,(1570,515),None,'B' if p>.65 else 'A',color=AMBER if p>.65 else TEAL)
        middle(im,(1570,692),'Respuesta',60)
    elif mode=='research':
        middle(im,(960,265),'Investigar el aprendizaje',64)
        module(im,(750,335,1170,720),p>.42,label='DEE',active=.3<p<.65)
        token(im,(lerp(280,720,p/.6),520),'Experiencia',w=410,color=TEAL)
        if p>.5:token(im,(lerp(1200,1610,(p-.5)/.4),520),None,'B',color=AMBER)
        middle(im,(1590,705),'Respuesta',60)
        dd.line((380,790,1610,790),fill=LINE,width=5)
    else:
        lines(im,(960,333),['¿Qué podemos aprender sobre','el aprendizaje natural?'],72)
        middle(im,(360,638),'Experiencia',60);middle(im,(1580,638),'Respuesta',60)
        arrow(im,(600,638),(810,638),LINE);arrow(im,(1110,638),(1350,638),LINE)
        token(im,(960,638),None,'B' if p>.5 else 'A',color=AMBER if p>.5 else TEAL)
        if p<.5:flow(im,[(600,638),(810,638)],p*2,TEAL,22)
        else:flow(im,[(1110,638),(1350,638)],(p-.5)*2,AMBER,22)

def closing(im,p,mode):
    if mode=='end':
        middle(im,(960,330),'DEE Cognitive',88)
        middle(im,(960,515),'Buscamos aliados',86,TEAL)
        middle(im,(960,693),'Aprender de la experiencia',68)
        return
    labels=[['Elegir un','problema'],['Desarrollar una','solución'],['Medir la','mejora']]
    for j,x in enumerate([390,960,1530]):
        active=p*3>=j
        panel(im,(x-255,345,x+255,677),TEAL if active else LINE,fill=PANEL)
        lines(im,(x,510),labels[j],60,FG if active else GRAY)
    arrow(im,(655,510),(695,510),TEAL);arrow(im,(1225,510),(1265,510),TEAL)
    if p<1:flow(im,[(135,720),(1785,720)],p,AMBER,16)
    middle(im,(960,270),'DEE Cognitive',68)

def continued(im,p):
    association(im,p,after=True)
    middle(im,(960,800),'Aprendizaje conservado',58)

def shots_for(s):
    c=s['scene'];end=s['duration'];b=s['sentences'];st=lambda j:b[j][0];mid=lambda j:(b[j][0]+b[j][1])/2
    if c==1:
        cuts=[(0,'intro_in'),(mid(0),'intro_keep'),(st(1),'intro_change'),(st(2),'intro_summary')]
    elif c==2:
        cuts=[(0,'query_intro'),(st(1),'before_real'),(st(2),'teach_motion'),(mid(2),'teach_real'),(st(3),'after_real'),(st(4),'changed_motion'),(st(5),'compare_records')]
    elif c==3:
        step=(st(2)-st(1))/3
        cuts=[(0,'retained_b'),(st(1),'save_real'),(st(1)+step,'close_real'),(st(1)+step*2,'open_real'),(st(2),'revised_real'),(st(3),'old_real'),(st(4),'continuity_motion'),(st(5),'retained_records')]
    elif c==4:
        cuts=[(0,'grid_before'),(st(2),'grid_teach'),(st(3),'grid_after'),(st(4),'grid_reuse'),(st(5),'grid_summary'),(st(6),'grid_after')]
    elif c==5:
        cuts=[(0,'cascade_separate'),(st(1),'cascade_first'),(mid(1),'cascade_second'),(st(2),'cascade_control'),(st(3),'cascade_joint'),(st(4),'cascade_values')]
    elif c==6:
        cuts=[(0,'query_compare'),(st(2),'query_request'),(mid(2),'query_receive'),(st(3),'query_use'),(st(4),'query_summary')]
    elif c==7:
        cuts=[(0,'app_full'),(2.7,'app_ask'),(st(1),'app_observe'),(mid(1),'app_save'),(st(2),'app_reply'),(st(3),'app_continue')]
    elif c==8:
        cuts=[(0,'future_continuity'),(st(1)+(b[1][1]-st(1))*.40,'future_change'),(st(1)+(b[1][1]-st(1))*.73,'future_research'),(st(3),'nature_question')]
    else:cuts=[(0,'closing_steps'),(st(1),'closing_steps'),(st(2),'closing_end')]
    shots=[]
    for j,(at,mode) in enumerate(cuts):
        stop=cuts[j+1][0] if j+1<len(cuts) else end
        assert stop>at,(c,mode,at,stop)
        shots.append({'scene':c,'start':at,'end':stop,'mode':mode})
    assert shots[0]['start']==0 and abs(shots[-1]['end']-end)<.00001
    return shots

def frame(s,shots,t):
    shot=next(q for q in shots if q['start']<=t<q['end']+1e-6);mode=shot['mode'];elapsed=t-shot['start'];duration=shot['end']-shot['start'];p=min(1,elapsed/max(.001,duration-.65));c=s['scene']
    category='Explicación visual';context='Archivo de investigación' if c in [5,6] else None
    if mode.endswith('_real') or mode.startswith('app_'):category='Grabación real';context='DEE Cognitive 2.0'
    if mode in ['compare_records','retained_records','retained_b','cascade_control','cascade_values']:category='Datos de una prueba';context='Archivo de investigación' if c==5 else 'DEE Cognitive 2.0'
    if mode.startswith('future_') or mode.startswith('closing_'):category='Aplicación posible'
    im=base(c,category,context)
    if mode.startswith('intro_'):
        if mode=='intro_in':
            module(im);token(im,(lerp(310,960,p),505),'Experiencia',w=410)
        elif mode=='intro_keep':
            module(im,learned=True);token(im,(lerp(1210,1570,p),505),'Lo aprendido',w=460)
        elif mode=='intro_change':
            module(im,learned=p>.4);token(im,(lerp(390,960,p),505),'Nueva experiencia',w=540,color=AMBER)
            if p>.65:middle(im,(1510,505),'Respuesta revisada',58,AMBER)
        elif mode=='intro_learn':
            module(im,learned=True);token(im,(lerp(310,960,min(1,p*1.8)),505),'Experiencia',w=410)
            if p>.5:token(im,(lerp(1210,1570,(p-.5)*2),505),'Lo aprendido',w=460)
        else:
            module(im,learned=True);token(im,(lerp(390,940,p),505),'Nueva experiencia',w=540,color=AMBER)
            if p>.5:lines(im,(1510,505),['Respuesta','revisada'],60,AMBER)
        middle(im,(960,270),'DEE Cognitive',68);middle(im,(960,795),'Tecnología experimental',56,GRAY)
    elif mode in ['query_intro','changed_motion','teach_motion']:
        association(im,p,mode=='changed_motion',mode=='teach_motion',mode=='query_intro')
        if mode!='teach_motion':middle(im,(960,260),'A = +1 · B = −1',56,GRAY)
    elif mode in ['before_real','after_real','revised_real','old_real','teach_real']:
        name={'before_real':'before','after_real':'after','revised_real':'revised','old_real':'old','teach_real':'teaching'}[mode]
        val={'before_real':1,'after_real':-1,'revised_real':-1,'old_real':1,'teach_real':None}[mode]
        label='Otra asociación' if mode=='old_real' else 'Nueva enseñanza' if mode=='teach_real' else 'Respuesta A' if val==1 else 'Respuesta B'
        im=proof(c,name,elapsed,label,val)
        if c==2:middle(im,(960,815),'A = +1 · B = −1',56,GRAY)
    elif mode in ['compare_records','retained_records']:comparison(im,p,mode=='retained_records')
    elif mode=='retained_b':
        middle(im,(960,285),'Señal de prueba',62);token(im,(960,485),'B','B',color=AMBER);middle(im,(960,705),'−1',100,AMBER)
    elif mode in ['save_real','close_real','open_real']:
        name=mode.split('_')[0];im=proof(c,name,elapsed)
        title={'save':'Guardar','close':'Cerrar','open':'Volver a abrir'}[name];middle(im,(960,235),title,68,TEAL)
    elif mode=='continuity_motion':continued(im,p)
    elif mode.startswith('grid_'):
        learned=mode not in ['grid_before'];out=mode not in ['grid_teach']
        grid(im,p,learned,out,mode in ['grid_summary','grid_reuse'])
        if mode=='grid_summary':middle(im,(960,805),'Lo ocurrido antes influye después',58)
    elif mode in ['cascade_control','cascade_values']:cascade_data(im,p,mode=='cascade_control')
    elif mode.startswith('cascade_'):
        name={'cascade_separate':'separate','cascade_first':'stage1','cascade_second':'stage2','cascade_joint':'joint'}[mode];cascade(im,p,name)
    elif mode.startswith('query_'):query(im,p,mode.split('_')[1])
    elif mode.startswith('app_'):
        if mode=='app_full':real_clip(im,'context',elapsed,(390,225,1140,565))
        elif mode=='app_ask':
            real_clip(im,'ask',elapsed,(100,330,1720,350));middle(im,(960,255),'Probar',68,TEAL)
        elif mode=='app_observe':
            real_clip(im,'observe',elapsed,(100,280,1720,490));middle(im,(960,235),'Observar',68,TEAL)
        elif mode=='app_save':
            real_clip(im,'save',elapsed,(100,295,1720,490));middle(im,(960,235),'Continuar',68,TEAL)
        elif mode=='app_reply':im=proof(c,'before',elapsed,'Respuesta A',1)
        else:
            real_clip(im,'open',elapsed,(100,305,1720,470));middle(im,(960,235),'DEE Cognitive 2.0',68,TEAL)
    elif mode.startswith('future_'):application(im,p,{'future_continuity':'continuity','future_change':'changing','future_research':'research'}[mode])
    elif mode=='nature_question':application(im,p,'nature')
    elif mode.startswith('closing_'):closing(im,p,'end' if mode=='closing_end' else 'steps')
    else:raise ValueError(mode)
    return im,shot

def preview():
    plan=json.loads((W/'timeline.json').read_text(encoding='utf8'));out=W/'previas';out.mkdir(exist_ok=True);rows=[]
    for s in plan['scenes']:
        shots=shots_for(s)
        for j,q in enumerate(shots):
            tt=(q['start']+q['end'])/2;im,_=frame(s,shots,tt);subtitles(im,plan['captions'],s['start']+tt)
            name=f'escena_{s["scene"]:02}_plano_{j:02}.png';im.save(out/name);rows.append({'scene':s['scene'],'file':name,'mode':q['mode'],'at':s['start']+tt})
    for page in range(math.ceil(len(rows)/8)):
        sheet=Image.new('RGB',(1280,4*384),BG)
        for j,r in enumerate(rows[page*8:page*8+8]):
            im=Image.open(out/r['file']).resize((640,360),Image.Resampling.LANCZOS);sheet.paste(im,((j%2)*640,(j//2)*384))
            ImageDraw.Draw(sheet).text(((j%2)*640+8,(j//2)*384+360),f'{r["scene"]}: {r["mode"]}',font=font(18),fill=GRAY)
        sheet.save(out/f'contacto_{page:02}.jpg',quality=92)
    plan['shots']=[{**q,'absolute_start':s['start']+q['start'],'absolute_end':s['start']+q['end']} for s in plan['scenes'] for q in shots_for(s)]
    (W/'timeline.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8')
    (out/'indice.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8');print('PREVIEW',len(rows),'SHOTS',flush=True)
def render(selected=None):
    plan=json.loads((W/'timeline.json').read_text(encoding='utf8'));folder=W/'escenas';folder.mkdir(exist_ok=True)
    for s in plan['scenes']:
        c=s['scene']
        if selected and c not in selected:continue
        out=folder/f'escena_{c:02}.mp4'
        if out.exists():raise FileExistsError(out)
        cmd=[str(FF),'-hide_banner','-v','warning','-n','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','30','-i','pipe:0','-an','-c:v','libx264','-threads','4','-preset','fast','-crf','17','-profile:v','high','-pix_fmt','yuv420p','-r','30','-fps_mode','cfr','-video_track_timescale','90000',str(out)]
        log=(folder/f'escena_{c:02}.log').open('wb');proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=log);start=time.monotonic();shots=shots_for(s);count=round(s['duration']*30)
        try:
            for n in range(count):
                t=n/30;im,_=frame(s,shots,t);subtitles(im,plan['captions'],s['start']+t);proc.stdin.write(im.tobytes())
                if n and n%600==0:print('RENDER',c,n,'/',count,flush=True)
            proc.stdin.close();code=proc.wait(timeout=120);assert code==0,(c,code)
        finally:
            if proc.poll() is None:proc.terminate();proc.wait(timeout=15)
            log.close()
        print('SCENE_COMPLETE',c,count,'FRAMES',round(time.monotonic()-start,1),'HOST_SECONDS',flush=True)
def mux():
    plan=json.loads((W/'timeline.json').read_text(encoding='utf8'));assert not OUT.exists()
    cat=W/'concatenar.txt';cat.write_text('\n'.join(f"file 'escenas/escena_{s['scene']:02}.mp4'" for s in plan['scenes'])+'\n',encoding='utf8')
    subprocess.run([str(FF),'-hide_banner','-v','warning','-n','-f','concat','-safe','0','-i',str(cat),'-i',str(W/'voz/locucion_completa.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-af','loudnorm=I=-16:TP=-1.5:LRA=9','-c:a','aac','-b:a','192k','-ar','48000','-t',str(plan['duration']),'-movflags','+faststart','-metadata','title=DEE Cognitive 2.0 — Aprender de la experiencia','-metadata','artist=Ivan Erick Tlaltecatl Morales',str(OUT)],check=True,timeout=180)
    print('MUX_COMPLETE',OUT.stat().st_size,flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['plan','clips','preview','render','mux']);ap.add_argument('--scenes',nargs='*',type=int);a=ap.parse_args()
    {'plan':build_plan,'clips':prepare_clips,'preview':preview,'render':lambda:render(a.scenes),'mux':mux}[a.action]()
