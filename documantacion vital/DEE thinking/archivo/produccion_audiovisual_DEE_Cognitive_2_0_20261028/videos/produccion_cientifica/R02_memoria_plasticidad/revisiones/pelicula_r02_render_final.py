"""Revisión offline de la película aprobada. No importa ni ejecuta DEE.

Reutiliza el renderizador, la paleta, la cámara y los materiales originales.
La única línea de tiempo que avanza es la editorial.
"""
from pathlib import Path
from functools import lru_cache
import ast,json,math,sys,re,wave,subprocess,time,hashlib,argparse,tempfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
W=Path(__file__).resolve().parent;PROD=W.parent;VIDEOS=PROD.parent
ROOT=next(p for p in W.parents if p.name=='DEE thinking');TEST=ROOT.parent.parent
FF=TEST/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
PROBE=TEST/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
FPS=30
BG='#09131F';WHITE='#F5F7FA';GRAY='#B9C4D0';CYAN='#44D8E8';AMBER='#FFBE66';VIOLET='#AC8BFA'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):
    t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8');t.replace(p)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
G=read(W/'guion_R02.json');CONTROL=read(W/'CONTROL_R02.json');E=read(PROD/'fuentes_g07/G07_EVIDENCIA_Y_GEOMETRIA.json')
OLD=read(PROD/'timeline.json');OLD_SCENES={s['scene']:s for s in OLD['scenes']}

@lru_cache(None)
def base_module():
    # Resolver sólo las ubicaciones archivadas. Los algoritmos de dibujo son
    # los mismos bytes del proyecto aprobado y se conservan sin modificar.
    path=PROD/'pelicula.py';tree=ast.parse(path.read_text(encoding='utf8'))
    names={'W','ROOT','BASE','FF','PROBE','G','E','PRIOR','ARCH','SRC'}
    tree.body=[n for n in tree.body if not isinstance(n,ast.Assign) or not any(isinstance(t,ast.Name) and t.id in names for t in n.targets)]
    ns=dict(__name__='editorial_base_reutilizada',__file__=str(path),W=PROD,ROOT=ROOT/'DEE Cognitive 2.0',BASE=TEST,FF=FF,PROBE=PROBE,G=read(PROD/'guion_literal.json'),E=E,PRIOR=VIDEOS/'edicion_experiencia',ARCH=read(VIDEOS/'edicion_experiencia/fuentes_y_control.json'),SRC=TEST/'_dee20_trabajo/video_publico_definitivo/fuentes/DEE_Cognitive_2_0_Demostracion_Completa_Original.mp4')
    exec(compile(tree,str(path),'exec'),ns)
    return type('Base',(),ns)

@lru_cache(None)
def font(size,bold=False):return ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf',size)
def text(im,xy,value,size=42,color=WHITE,bold=False,anchor=None,max_width=None):
    value=str(value);d=ImageDraw.Draw(im)
    if max_width:
        while size>28 and d.textlength(value,font=font(size,bold))>max_width:size-=1
    box=d.textbbox(xy,value,font=font(size,bold),anchor=anchor)
    assert box[0]>=85 and box[2]<=1835 and box[1]>=0 and box[3]<=1060,(value,box)
    d.text(xy,value,font=font(size,bold),fill=color,anchor=anchor,stroke_width=1,stroke_fill=BG)
def center(im,y,value,size=48,color=WHITE,bold=False):text(im,(960,y),value,size,color,bold,'mm',1720)
def wrap(value,size=44,width=1680):
    d=ImageDraw.Draw(Image.new('RGB',(1,1)));out=[];line=[]
    for word in value.split():
        if line and d.textlength(' '.join(line+[word]),font=font(size))>width:out.append(' '.join(line));line=[]
        line.append(word)
    if line:out.append(' '.join(line))
    return out
def header(im,title,provenance,detail=None,clock=None):
    layer=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(layer)
    # Bandas opacas: al reutilizar un plano editorial eliminan completamente
    # los rótulos anteriores, sin letras fantasma ni subtítulos superpuestos.
    d.rectangle((0,0,1920,224),fill=(5,12,22,255));d.rectangle((0,850,1920,1080),fill=(5,12,22,255))
    im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
    text(im,(100,54),title,64,WHITE,True,max_width=1720)
    if detail:text(im,(100,145),detail,40,GRAY,max_width=1720)
    text(im,(100,874),provenance,30,GRAY,max_width=1500)
    if clock is not None:text(im,(1820,874),'t = '+str(int(clock)),30,GRAY,anchor='rt')
    return im
def native_sign(v):return '+1' if v==1 else '−1' if v==-1 else str(v)
def marks(scene):return scene['sentences']
def map_old(scene,t,old_id):
    old=OLD_SCENES[old_id];new=scene['sentences']
    pairs=[(0,0)]
    if old_id==3:
        pairs.append((new[5][0],old['sentences'][3][0]))
        for old_i in range(3,13):
            for j in [0,1]:pairs.append((new[old_i+2][j],old['sentences'][old_i][j]))
    elif len(new)==len(old['sentences']):
        for a,b in zip(new,old['sentences']):pairs.extend(zip(a,b))
    else:return t/scene['duration']*old['duration']
    pairs.append((scene['duration'],old['duration']));pairs=sorted(dict(pairs).items())
    return float(np.interp(t,[p[0] for p in pairs],[p[1] for p in pairs]))

def relation_labels(im,renderer,clock):
    # Líneas/posiciones del mismo recorrido documentado; no etiquetas físicas
    # nuevas en el motor ni linaje inferido por cargas iguales.
    for active,pos,label,col in [(5<=clock<13,[20,15+clock-5,30],'Relación aprendida +3',AMBER),(5<=clock<20,[27,30,15+clock-5],'Relación aprendida +7',VIOLET)]:
        if not active:continue
        q=renderer.project(pos)
        if q and 180<q[1]<740:
            x=max(350,min(1550,q[0]));y=max(260,min(760,q[1]+60))
            ImageDraw.Draw(im).line((q[0],q[1],x,y-12),fill=col,width=2)
            text(im,(x,y),label,32,col,True,'mm',500)

def g07(renderer,scene,t):
    b=base_module();old=OLD_SCENES[3];ot=map_old(scene,t,3)
    st=lambda i:old['sentences'][i][0]
    if ot>=st(11):
        cp=(ot-st(11))/(old['duration']-st(11));case=E['controls']['selected_cases'][0 if cp<.5 else 1]['value']
        where=case['collision_first'] if (cp*2)%1<.28 else case['collision_second']
        im=b.world(renderer,[b.particle(where,CYAN,.8)],b.mix([30,25,62],[27,31,58],cp),[9,49,43],bounds=([0,40,36],[22,60,50]),highlights=[{'position':case['collision_first'],'color':AMBER},{'position':case['collision_second'],'color':VIOLET}])
        im=header(im,'LA EXPERIENCIA CAMBIA EL RESULTADO','Datos registrados · Control C6H04 · Otra realización, N64',
                  'Ambas relaciones adquiridas' if cp<.5 else 'Segunda relación omitida')
        text(im,(100,760),'Se completa la transformación compuesta' if cp<.5 else 'La misma transformación ya no se completa',42,CYAN,max_width=1720)
        return im
    im=b.image_at(renderer,old,ot)
    # El reloj reconstruido es el mismo calendario original.
    if ot<st(3):clock=min(9,9*ot/st(3))
    elif ot<st(4):clock=10+2.98*(ot-st(3))/(st(4)-st(3))
    elif ot<st(5):clock=13
    elif ot<st(6):clock=13+6.98*(ot-st(5))/(st(6)-st(5))
    else:clock=20
    title='ENSEÑANZA' if clock<5 else 'RELACIÓN APRENDIDA' if clock<10 else 'UNA CONSULTA NUEVA' if clock<13 else 'LO APRENDIDO PARTICIPA EN LA RESPUESTA' if clock<20 else 'RESULTADO DE LA SECUENCIA'
    detail='Dos experiencias, dos relaciones' if clock<5 else 'Lo adquirido sigue su recorrido' if clock<10 else 'Consulta 20 · Encuentro con la relación aprendida' if clock<13 else 'La salida continúa hacia otra relación' if clock<20 else '30 · Resultado de dos relaciones aprendidas'
    im=header(im,title,'Reconstrucción geométrica · G07 · Experimento del motor',detail,clock)
    relation_labels(im,renderer,clock)
    return im

def memory(renderer,scene,t):
    b=base_module();s=scene['sentences'];st=lambda i:s[i][0]
    if t<st(1):clock=4+1.5*max(0,t)/max(.01,st(1))
    elif t<st(2):clock=5.5+4*(t-st(1))/max(.01,st(2)-st(1))
    elif t<st(3):clock=10+3*(t-st(2))/max(.01,st(3)-st(2))
    else:clock=13
    focus=[20,20,30];eye=[38,-2,48]
    im=b.world(renderer,b.g07_particles(clock),eye,focus,bounds=([10,8,7],[38,40,40]),highlights=[{'position':[20,23,30],'color':AMBER}])
    im=header(im,'MEMORIA','Reconstrucción geométrica · G07 · La misma experiencia explicada',
              'LO APRENDIDO INFLUYE DESPUÉS',clock)
    relation_labels(im,renderer,clock)
    tag='La experiencia deja una relación' if clock<5.5 else 'La relación se conserva durante el recorrido' if clock<10 else 'Otra consulta la encuentra y la utiliza'
    text(im,(100,775),tag,40,CYAN,max_width=1720)
    return im

def revision(scene,t):
    b=base_module();ev=CONTROL['evidence']['revision']['events'];s=scene['sentences']
    st=lambda i:s[i][0]
    if t<st(1):phase='before'
    elif t<st(2):phase='teach'
    elif t<st(4):phase='after'
    else:
        p=(t-st(4))/max(.01,scene['duration']-st(4))
        phase='save' if p<.22 else 'reopen' if p<.48 else 'retained'
    if phase=='before':
        im=b.app('before_receipt',0,'',native_sign(ev['before']['sign']))
        im=header(im,'MISMA SEÑAL','Captura auténtica · DEE20_DEMO_01 · Imagen detenida','palabra clasifica · +1 y −1 son dos respuestas del código')
    elif phase=='teach':
        im=Image.new('RGB',(1920,1080),BG)
        # Sólo el panel docente auténtico; se excluye el comando anterior.
        m=b.meta('teach');k=min(m['frames']-1,int(max(0,t-st(1))*15))
        pic=b.photo('teach',k).crop((0,153,496,265));pic=pic.resize((1587,358),Image.Resampling.LANCZOS)
        im.paste(pic,(166,310));ImageDraw.Draw(im).rectangle((163,307,1756,671),outline=AMBER,width=3)
        im=header(im,'NUEVA EXPERIENCIA','Captura auténtica del panel docente · Misma DEE20_DEMO_01','clasifica · Docente −1 · Revisión declarada')
        text(im,(100,755),'Experiencia admitida: 3 de 3 entradas materiales',40,GRAY,max_width=1720)
    elif phase=='after':
        im=b.app('after',min(3,max(0,t-st(2))),'')
        im=header(im,'RESPUESTA REVISADA','Petición auténtica y visualización del registro a22 · DEE20_DEMO_01','palabra clasifica · La misma consulta, respuesta del código −1')
        d=ImageDraw.Draw(im);d.rounded_rectangle((1130,460,1805,790),radius=18,fill=BG,outline=CYAN,width=3)
        text(im,(1468,510),'Respuesta registrada',34,GRAY,anchor='mm')
        text(im,(1468,620),native_sign(ev['after']['sign']),116,CYAN,True,'mm')
        text(im,(1468,732),'7 de 7 entradas aplicadas',32,GRAY,anchor='mm')
        if t>=st(3):text(im,(100,775),'PLASTICIDAD · La experiencia revisa la relación',40,CYAN,max_width=1720)
    elif phase in ['save','reopen']:
        im=b.app(phase,max(0,t-st(4)),'')
        im=header(im,'GUARDAR Y REABRIR','Captura auténtica · DEE20_DEMO_01','Se retoma la misma vida guardada')
    else:
        im=b.app('retained_receipt',0,'',native_sign(ev['retained']['sign']))
        im=header(im,'LA REVISIÓN SE CONSERVA','Captura auténtica · Consulta posterior a la reapertura · Imagen detenida','palabra clasifica · Respuesta revisada −1')
    return im

def record_background(title,detail):
    im=Image.new('RGB',(1920,1080),BG)
    # El diseño es una visualización de registros; nunca una interfaz 2.0 falsa.
    return header(im,title,'Trayectoria experimental · APD03 · Visualización de registros originales',detail)
def apd03(scene,t):
    events=CONTROL['evidence']['apd03']['events'];s=scene['sentences'];p=t/scene['duration']
    # Primera frase abre la trayectoria; segunda contiene las tres funciones.
    intro=s[1][0];end=s[1][1];q=max(0,min(.999,(t-intro)/max(.01,end-intro)))
    stage=0 if t<intro else min(2,int(q*3)) if t<end else 2
    if stage==0:
        im=record_background('CAPACIDADES EN UNA MISMA TRAYECTORIA','APD03_MAIN · APRENDE')
        lessons=events[0]['lessons']
        for j,item in enumerate(lessons):
            y=345+j*220
            text(im,(230,y),item['form'],76,WHITE,True)
            text(im,(1230,y),'→  '+native_sign(item['teacher_sign']),84,CYAN,True)
        text(im,(100,780),'Experiencias de enseñanza y usos posteriores registrados',39,GRAY,max_width=1720)
    elif stage==1:
        panel=events[1];forms={x['form']:x for x in panel['forms']}
        im=record_background('CONSERVA LO ANTERIOR','APD03_MAIN · Panel posterior a las nuevas adquisiciones')
        for j,name in enumerate(['alfa','beta','luma','nara']):
            x=250 if j%2==0 else 1070;y=330+200*(j//2)
            text(im,(x,y),name,62,WHITE,True);text(im,(x+300,y),native_sign(forms[name]['sign']),76,CYAN,True)
        text(im,(100,760),'Coinciden las asociaciones anteriores muestreadas',41,GRAY,max_width=1720)
    else:
        query=events[2];use=events[3]
        im=record_background('UTILIZA INFORMACIÓN','APD03_MAIN · Consulta, dato recibido y uso posterior')
        text(im,(160,285),'Consulta',45,GRAY,True);text(im,(160,345),'28 − ?',76,WHITE,True)
        text(im,(820,285),'Información recibida',45,GRAY,True);text(im,(820,345),'13',84,CYAN,True)
        ImageDraw.Draw(im).line((500,390,750,390),fill=CYAN,width=4)
        text(im,(160,520),'Uso posterior',43,GRAY,True);text(im,(160,585),'28 − 13  →  '+str(use['native_numeric_result']),76,CYAN,True)
        text(im,(160,740),'Resultado DEE → archivo mediante herramienta externa',39,GRAY,max_width=1720)
    # Un orden de eventos, no una animación de señales microscópicas ausentes.
    return im

def cognition(renderer,scene,t):
    b=base_module();p=t/scene['duration'];stage=min(4,int(p*5));v=(p*5)%1
    if stage==0:
        clock=4+2*v;im=b.world(renderer,b.g07_particles(clock),[49,-11,50],[23,21,22],bounds=([10,8,7],[38,40,40]));prov='Reconstrucción geométrica · G07';title='APRENDER'
    elif stage==1:
        clock=10+3*v;im=b.world(renderer,b.g07_particles(clock),[38,-2,48],[20,20,30],bounds=([10,8,7],[38,40,40]));prov='Reconstrucción geométrica · G07';title='RECORDAR'
    elif stage==2:
        synthetic=dict(scene,sentences=[[0,.1],[.1,.2],[.2,.3],[.3,.4],[scene['duration'],scene['duration']]])
        im=revision(synthetic,1);prov='Visualización de datos registrados · DEE20_DEMO_01';title='REVISAR'
    elif stage==3:
        clock=13+7*v;im=b.world(renderer,b.g07_particles(clock),[43,2,47],[23,24,27],bounds=([10,8,7],[38,40,40]));prov='Reconstrucción geométrica · G07';title='COMBINAR'
    else:
        old=OLD_SCENES[5];im=b.image_at(renderer,old,old['duration']*.85);prov='Reconstrucción geométrica · U0/CPC7';title='UTILIZAR INFORMACIÓN'
    return header(im,'FUNCIONES DE INTELIGENCIA',prov,title)

def image_at(renderer,scene,t):
    b=base_module();identifier=scene['id'];p=t/scene['duration']
    if identifier=='g07':return g07(renderer,scene,t)
    if identifier=='b1':return memory(renderer,scene,t)
    if identifier=='b2':return revision(scene,t)
    if identifier=='c1':return apd03(scene,t)
    if identifier=='c2':return cognition(renderer,scene,t)
    if identifier=='activo':
        im=b.app('app',min(4,t),'')
        return header(im,'UNA BASE TECNOLÓGICA TRANSVERSAL','Captura auténtica de la aplicación · Imagen detenida después del extracto','Motor · Aprendizaje y memoria · Experimentación · Aplicación')
    old_id=scene['old_scene'];old=OLD_SCENES[old_id]
    ot=map_old(scene,t,old_id);im=b.image_at(renderer,old,ot)
    if identifier in ['s01','s02','cierre']:
        if identifier=='s01' and .37<p<.49:return im
        if identifier=='s02' and ot/old['duration']>.25:return im
        title='DEE COGNITIVE 2.0' if identifier=='s01' else 'UN UNIVERSO COMPUTACIONAL 3D' if identifier=='s02' else 'DE LA INVESTIGACIÓN A LOS PILOTOS'
        detail='Aprender de la experiencia' if identifier=='s01' else 'Una misma dinámica. Distintas organizaciones.' if identifier=='s02' else 'INVESTIGACIÓN DESARROLLADA EN PUEBLA' if .36<p<.82 else 'ARQUITECTURA · MECANISMOS · EVIDENCIA' if p<.36 else 'DEE COGNITIVE 2.0'
        im=header(im,title,'Visualización de datos reales · DEE20_DEMO_01 · Captura fija y cámara editorial',detail)
    if identifier=='aplicaciones':
        title=['ASISTENTES CON CONTINUIDAD','SISTEMAS ADAPTATIVOS','INVESTIGACIÓN COGNITIVA'][min(2,int(p*3))]
        im=header(im,title,'Posibles aplicaciones · Ejemplos visuales de mecanismos ya explicados','POSIBLES APLICACIONES')
    return im

def captions(scene,voice,offset):
    out=[]
    assert len(scene['sentences_es'])==len(voice['sentences'])
    for es,en,mark in zip(scene['sentences_es'],scene['sentences_en'],voice['sentences']):
        assert mark['text']==es and mark['start'] is not None and mark['end'] is not None
        lines=wrap(en);groups=[lines[i:i+2] for i in range(0,len(lines),2)]
        total=sum(len(' '.join(g).split()) for g in groups);past=0;length=mark['end']-mark['start']
        for group in groups:
            words=len(' '.join(group).split());out.append(dict(start=offset+mark['start']+length*past/total,end=offset+mark['start']+length*(past+words)/total,lines=group,text=' '.join(group),scene=scene['id']));past+=words
    return out
def stamp(t):
    n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
def plan():
    vm=read(W/'voz/timings.json');byid={v['id']:v for v in vm['scenes']};pcm=bytearray();at=0;scenes=[];caps=[];params=None
    for s in G['scenes']:
        v=byid[s['id']];assert v['es']==s['es'] and v['audio_sentence_splices']==0 and v['complete_model_waveform_retained']
        file=W/v['file'];assert sha(file)==v['wav_sha256']
        with wave.open(str(file),'rb') as f:
            pr=f.getparams();audio=f.readframes(f.getnframes());frames=f.getnframes()
        if params:assert pr[:3]==params[:3]
        params=pr;count=math.ceil(frames/(pr.framerate/FPS))*int(pr.framerate/FPS);pad=count-frames
        duration=count/pr.framerate;pcm.extend(audio);pcm.extend(bytes(pad*pr.sampwidth*pr.nchannels))
        row=dict(s,start=at,end=at+duration,duration=duration,sentences=[[m['start'],m['end']] for m in v['sentences']],voice_sha256=v['wav_sha256'],voice_file=v['file'],complete_voice_samples=frames,editorial_end_padding_samples=pad)
        scenes.append(row);caps.extend(captions(s,v,at));at+=duration
    output=W/'voz/locucion_continua_R02.wav'
    with wave.open(str(output),'wb') as f:f.setparams(params);f.writeframes(pcm)
    assert ' '.join(c['text'] for c in caps)==' '.join(s['en'] for s in G['scenes'])
    assert all(0<c['end']-c['start'] and len(c['lines'])<=2 for c in caps)
    result=dict(scenes=scenes,captions=caps,duration=at,fps=FPS,native_ticks=0,voice_word_speed_changed=False)
    save(W/'timeline_R02.json',result)
    (W/'subtitulos_R02_EN.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n'+'\n'.join(c['lines']) for i,c in enumerate(caps))+'\n',encoding='utf8')
    print('PLAN',round(at,3),'seconds',[(s['id'],round(s['duration'],2)) for s in scenes],flush=True)
def put_subs(im,scenes,at):
    for c in scenes:
        if c['start']<=at<c['end']:
            ys=[985] if len(c['lines'])==1 else [960,1014]
            for y,line in zip(ys,c['lines']):text(im,(960,y),line,44,WHITE,False,'mm')
            return
def renderer():
    # Windows no carga ciertas DLL desde la ruta larga archivada. Este alias
    # sólo acorta el acceso de las bibliotecas gráficas, sin alterar sus bytes.
    alias=Path(tempfile.gettempdir())/'DEE_R02_RENDER_PROD'
    assert alias.is_junction() and alias.resolve()==PROD.resolve()
    sys.path.insert(0,str(alias/'python_deps'))
    path=PROD/'render3d/dee_renderer.py';tree=ast.parse(path.read_text(encoding='utf8'))
    tree.body=[n for n in tree.body if not isinstance(n,ast.Assign) or not any(isinstance(t,ast.Name) and t.id=='HERE' for t in n.targets)]
    ns={'__name__':'renderizador_base_R02','__file__':str(path),'HERE':alias/'render3d'}
    exec(compile(tree,str(path),'exec'),ns)
    result=ns['SceneRenderer'](1920,1080)
    result.info.update(source=str(path),source_sha256=sha(path),recreatable_short_alias=str(alias),alias_target=str(PROD),source_modified=False)
    return result
def preview(ids=None):
    vm=read(W/'voz/timings.json');byid={v['id']:v for v in vm['scenes']};r=renderer();out=W/'previas';out.mkdir(exist_ok=True)
    for s in G['scenes']:
        if ids and s['id'] not in ids:continue
        if s['id'] not in byid:continue
        v=byid[s['id']];sc=dict(s,start=0,duration=v['duration'],sentences=[[m['start'],m['end']] for m in v['sentences']]);cs=captions(s,v,0)
        times=sorted(set([v['duration']*x for x in [.08,.30,.55,.82,.95]]+[m['start']+.2 for m in v['sentences']]))
        for j,t in enumerate(times):
            im=image_at(r,sc,min(t,v['duration']-.01));put_subs(im,cs,t);im.save(out/f'{s["id"]}_{j:02}.png')
        print('PREVIEW',s['id'],len(times),flush=True)
    save(W/'renderer_R02.json',r.info)
def render(ids=None):
    plan=read(W/'timeline_R02.json');r=renderer();out=W/'escenas';out.mkdir(exist_ok=True)
    for s in plan['scenes']:
        if ids and s['id'] not in ids:continue
        target=out/(s['id']+'.mp4');assert not target.exists(),target
        with (out/(s['id']+'.log')).open('wb') as log:
            cmd=[str(FF),'-hide_banner','-v','warning','-n','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-threads','4','-preset','fast','-crf','17','-profile:v','high','-pix_fmt','yuv420p','-r',str(FPS),'-fps_mode','cfr',str(target)]
            proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log,stdout=subprocess.DEVNULL);start=time.monotonic();count=round(s['duration']*FPS)
            try:
                for frame in range(count):
                    t=frame/FPS;im=image_at(r,s,t);put_subs(im,plan['captions'],s['start']+t);proc.stdin.write(im.tobytes())
                    if frame and frame%600==0:print('FRAME',s['id'],frame,'/',count,flush=True)
                proc.stdin.close();assert proc.wait(timeout=120)==0
            finally:
                if proc.poll() is None:proc.terminate();proc.wait(timeout=30)
        print('SCENE_DONE',s['id'],count,'frames',round(time.monotonic()-start,2),'host seconds',flush=True)
    save(W/'renderer_R02.json',r.info)
def music():
    plan=read(W/'timeline_R02.json');rate=48000;count=round(plan['duration']*rate);output=np.zeros((count,2),np.float32)
    chords=[[130.8128,155.5635,195.9977],[103.8262,155.5635,207.6523],[116.5409,146.8324,174.6141],[97.9989,130.8128,195.9977]]
    for begin in np.arange(0,plan['duration'],18):
        a=round(begin*rate);n=min(count-a,round(20*rate));t=np.arange(n)/rate;env=np.minimum(1,t/2)*np.minimum(1,(20-t)/3);v=np.zeros((n,2))
        for hz in chords[int(begin/18)%4]:
            v[:,0]+=(np.sin(2*np.pi*hz*t)+.22*np.sin(2*np.pi*2*hz*t))*.0028*env
            v[:,1]+=np.sin(2*np.pi*hz*t+.12)*.0028*env
        output[a:a+n]+=v.astype(np.float32)
    output*=np.minimum(1,np.arange(count)/(rate*2))[:,None];output*=np.minimum(1,(count-np.arange(count))/(rate*3))[:,None]
    with wave.open(str(W/'voz/ambiente_R02.wav'),'wb') as f:f.setparams((2,2,rate,0,'NONE','not compressed'));f.writeframes((np.clip(output,-1,1)*32767).astype('<i2').tobytes())
    print('MUSIC',count,'samples; same prepared instrumental design',flush=True)
def mux():
    plan=read(W/'timeline_R02.json');cat=W/'concatenar_R02.txt';cat.write_text('\n'.join("file 'escenas/"+s['id']+".mp4'" for s in plan['scenes'])+'\n',encoding='utf8')
    target=W/'montaje_R02.mp4';assert not target.exists()
    # Primera pasada de medición; no modifica la voz ni su velocidad.
    common=[str(FF),'-hide_banner','-v','info','-i',str(W/'voz/locucion_continua_R02.wav'),'-i',str(W/'voz/ambiente_R02.wav')]
    measure=subprocess.run(common+['-filter_complex','[0:a]aformat=channel_layouts=stereo[v];[v][1:a]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json[a]','-map','[a]','-f','null','-'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,check=True,timeout=180)
    m=json.loads(re.findall(r'\{\s*"input_i".*?\}',measure.stderr,re.S)[-1])
    norm=f'loudnorm=I=-16:TP=-1.5:LRA=9:measured_I={m["input_i"]}:measured_TP={m["input_tp"]}:measured_LRA={m["input_lra"]}:measured_thresh={m["input_thresh"]}:offset={m["target_offset"]}:linear=true:print_format=json'
    cmd=[str(FF),'-hide_banner','-v','info','-n','-f','concat','-safe','0','-i',str(cat),'-i',str(W/'voz/locucion_continua_R02.wav'),'-i',str(W/'voz/ambiente_R02.wav'),'-filter_complex','[1:a]aformat=channel_layouts=stereo[v];[v][2:a]amix=inputs=2:normalize=0,'+norm+'[a]','-map','0:v:0','-map','[a]','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-t',str(plan['duration']),'-movflags','+faststart','-metadata','title=DEE Cognitive 2.0 — Memoria, plasticidad e inteligencia funcional R02','-metadata','artist=Ivan Erick Tlaltecatl Morales',str(target)]
    result=subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,check=True,timeout=240)
    control=read(W/'CONTROL_R02.json');control['audio']['loudnorm_measurement']=m;control['audio']['loudnorm_export']=json.loads(re.findall(r'\{\s*"input_i".*?\}',result.stderr,re.S)[-1]);save(W/'CONTROL_R02.json',control)
    print('MUX_DONE',target.stat().st_size,flush=True)
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('action',choices=['plan','preview','render','music','mux']);a.add_argument('--ids',nargs='*');n=a.parse_args()
    {'plan':plan,'preview':lambda:preview(n.ids),'render':lambda:render(n.ids),'music':music,'mux':mux}[n.action]()
