"""Montaje científico offline. Reconstrucciones editoriales; nunca ejecuta DEE."""
from pathlib import Path
from functools import lru_cache
import json,re,sys,math,wave,subprocess,time,hashlib,shutil,argparse
import numpy as np
from PIL import Image,ImageDraw,ImageFont
W=Path(__file__).resolve().parent;ROOT=W.parents[1];BASE=ROOT.parent.parents[1]
FF=BASE/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe';PROBE=BASE/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
G=json.loads((W/'guion_literal.json').read_text(encoding='utf8'))
E=json.loads((W/'fuentes_g07/G07_EVIDENCIA_Y_GEOMETRIA.json').read_text(encoding='utf8'))
PRIOR=ROOT/'videos/edicion_experiencia';ARCH=json.loads((PRIOR/'fuentes_y_control.json').read_text(encoding='utf8'));SRC=Path(ARCH['source_video'])
BG='#09131F';WHITE='#F5F7FA';GRAY='#B9C4D0';CYAN='#44D8E8';AMBER='#FFBE66';VIOLET='#AC8BFA'
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
@lru_cache(None)
def font(n,b=False):return ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf' if b else 'C:/Windows/Fonts/segoeui.ttf',n)
def txt(im,xy,s,n=60,color=WHITE,b=True,anchor=None):
    d=ImageDraw.Draw(im);box=d.textbbox(xy,str(s),font=font(n,b),anchor=anchor)
    assert box[0]>=85 and box[2]<=1835 and box[1]>=0 and box[3]<=1060,(s,box)
    d.text(xy,str(s),font=font(n,b),fill=color,anchor=anchor,stroke_width=1,stroke_fill='#09131F')
def center(im,y,s,n=60,color=WHITE,b=True):txt(im,(960,y),s,n,color,b,'mm')
def wrap(s,n=44,width=1680,maxwords=16):
    rows=[];a=[];d=ImageDraw.Draw(Image.new('RGB',(1,1)))
    for w in s.split():
        if a and (len(a)>=maxwords or d.textlength(' '.join(a+[w]),font=font(n))>width):rows.append(' '.join(a));a=[]
        a.append(w)
    if a:rows.append(' '.join(a))
    return rows
def sentences(s):return re.split(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÜ¿¡])',s)
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def mix(a,b,p):return (np.array(a)*(1-ease(p))+np.array(b)*ease(p)).tolist()
def plan():
    m=json.loads((W/'voz/narraciones.json').read_text(encoding='utf8'));records=m['sentences'];pcm=bytearray();params=None;offset=0;out=[];caps=[];vi=[]
    for sc in G['scenes']:
        start=offset;bounds=[];es=sentences(sc['es']);en=sentences(sc['en']);assert len(es)==len(en)
        for j,(a,b) in enumerate(zip(es,en)):
            r=next(r for r in records if r['scene']==sc['scene'] and r['sentence']==j);assert r['text']==a,(sc['scene'],j)
            with wave.open(r['path'],'rb') as f:pr=f.getparams();audio=f.readframes(f.getnframes());sec=f.getnframes()/f.getframerate()
            if params:assert pr[:3]==params[:3]
            params=pr;lead=.4 if j==0 else .0;pcm.extend(bytes(round(lead*pr.framerate)*pr.sampwidth*pr.nchannels));offset+=lead
            at=offset;pcm.extend(audio);offset+=sec;bounds.append([at-start,offset-start]);vi.append({'scene':sc['scene'],'sentence':j,'text':a,'start':at,'end':offset})
            rows=wrap(b);groups=[rows[i:i+2] for i in range(0,len(rows),2)];den=sum(len(' '.join(x).split()) for x in groups);past=0
            for group in groups:
                words=len(' '.join(group).split());caps.append({'start':at+sec*past/den,'end':at+sec*(past+words)/den,'lines':group,'text':' '.join(group),'scene':sc['scene']});past+=words
            pad=.45
            if sc['scene']==3:pad=1.8 if j in[1,2,3,4,5,6,7,9,11,12] else .7
            if j==len(es)-1:pad=2.6 if sc['scene']==8 else 1.3
            pcm.extend(bytes(round(pad*pr.framerate)*pr.sampwidth*pr.nchannels));offset+=pad
        end=math.ceil(offset*30)/30;pcm.extend(bytes(round((end-offset)*params.framerate)*params.sampwidth*params.nchannels));offset=end
        out.append({'scene':sc['scene'],'start':start,'duration':end-start,'end':end,'sentences':bounds})
    with wave.open(str(W/'voz/locucion_montada.wav'),'wb') as f:f.setparams(params);f.writeframes(pcm)
    assert ' '.join(c['text'] for c in caps)==' '.join(s['en'] for s in G['scenes'])
    save(W/'timeline.json',{'scenes':out,'captions':caps,'voice':vi,'duration':offset,'fps':30,'voice_metadata':m,'new_native_ticks':0})
    def stamp(t):
        q=round(t*1000);return f'{q//3600000:02}:{q//60000%60:02}:{q//1000%60:02},{q%1000:03}'
    (W/'subtitulos_EN.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n'+ '\n'.join(c['lines']) for i,c in enumerate(caps))+'\n',encoding='utf8')
    print('PLAN',round(offset,3),[(s['scene'],round(s['duration'],2)) for s in out],flush=True)

def particle(pos,color,r=.45):return {'position':list(map(float,pos)),'color':color,'radius':r}
def g07_particles(t):
    if t>=20:return [particle([27,30,30],CYAN,.65)]
    pp=[]
    for path in E['paths']:
        lo,hi=path['from_time'],path['until_time']
        if lo<=t<hi or (t==hi and hi==max(p['until_time'] for p in E['paths'])):
            pos=np.array(path['origin'])+np.array(path['direction'])*(t-lo)
            color=CYAN if path['id'] in ['query','first_output'] else AMBER if '1' in path['id'] else VIOLET
            pp.append(particle(pos,color,.68 if color==CYAN else .60))
    # All paths are finite. Preserve the last recorded output instead of inventing extra travel.
    return pp
@lru_cache(None)
def demo_frame(final=False):
    d=json.loads((BASE/'_dee20_trabajo/video_publico_definitivo/datos_editoriales.json').read_text(encoding='utf8'));return d['final_frame'] if final else d['frame']
def demo_particles(final=False):
    return [particle(c['xyz'],AMBER if c['state']>0 else '#63B4C8',.50 if c['state']>0 else .28) for c in demo_frame(final)['cells']]
def u0_particles(t,match=False):
    pp=[]
    if t<70:
        pp.append(particle([31,(10-(t-3))%67,46],AMBER,.5))
        if not match and t>=19:pp.append(particle([(47+t-19)%67,10,46],CYAN,.55))
    elif t<72:
        pp.append(particle(np.array([31,10,46])+(t-70)*np.array([0,-1,0] if match else [1,-1,0]),AMBER if match else CYAN,.6))
    else:
        if match:pp.append(particle([31,8,46],AMBER,.5))
        pp.append(particle([33,8,46],GRAY if match else CYAN,.72))
    if 69<=t<72:pp.append(particle([33,8,43+(t-69)],'#E8ECF1',.48))
    return pp

def get_renderer():
    sys.path.insert(0,str(W/'render3d'))
    from dee_renderer import SceneRenderer
    return SceneRenderer(1920,1080)
def world(renderer,pp,eye,target,bounds=(0,66),paths=None,highlights=None):
    return renderer.render(pp,eye=eye,target=target,bounds=bounds,paths=paths or [],highlights=highlights or [])

CLIPS={'app':(69,74,(0,87,1262,710)), 'before':(165.7,170.7,(12,106,512,486)), 'teach':(416.4,421.4,(18,360,514,670)), 'after':(440,445,(18,355,512,418)), 'save':(1278.9,1282.1,(18,375,512,591)), 'reopen':(1376.8,1380.5,(18,314,514,458)), 'retained':(1416,1421,(20,407,512,472)), 'observe':(69,75,(552,302,1249,612))}
for name,a,b in [('before_receipt',170,173),('retained_receipt',1417,1420)]:
    CLIPS[name]=(a,b,(20,390,512,485))
    CLIPS[name+'_full']=(a,b,(0,87,1262,710))
def clips():
    for name,(a,b,box) in CLIPS.items():
        folder=W/'clips'/name;folder.mkdir(parents=True,exist_ok=True)
        if (folder/'ready.json').exists():continue
        x,y,x1,y1=box;subprocess.run([str(FF),'-hide_banner','-v','error','-threads','2','-n','-ss',str(a),'-i',str(SRC),'-t',str(b-a),'-an','-vf',f'crop={x1-x}:{y1-y}:{x}:{y},fps=15','-q:v','1',str(folder/'%05d.jpg')],check=True,timeout=60)
        save(folder/'ready.json',{'frames':len(list(folder.glob('*.jpg'))),'source':str(SRC),'range':[a,b],'crop':box,'fps':15})
        print('CLIP',name,flush=True)
@lru_cache(maxsize=64)
def photo(name,k):return Image.open(W/'clips'/name/f'{k+1:05}.jpg').convert('RGB')
@lru_cache(None)
def meta(name):return json.loads((W/'clips'/name/'ready.json').read_text())
def app(name,t,title,result=None):
    im=Image.new('RGB',(1920,1080),BG);m=meta(name);pic=photo(name,min(m['frames']-1,max(0,int(t*15))))
    if name.endswith('_receipt'):
        # Hold the exact verified frame; later footage already concerns another request.
        source=Image.open(W/'fuentes_g07'/('demo_t170.png' if name=='before_receipt' else 'demo_t1418.png')).convert('RGB')
        full=source.crop((0,87,1262,710));pic=source.crop((20,390,512,485))
        full=full.resize((1262,623),Image.Resampling.LANCZOS);im.paste(full,(330,210))
        pic=pic.resize((1300,round(pic.height*1300/pic.width)),Image.Resampling.LANCZOS)
        im.paste(pic,(130,540))
        ImageDraw.Draw(im).rectangle((128,538,1432,542+pic.height),outline=CYAN,width=2)
    else:
        ratio=min(1720/pic.width,630/pic.height);pic=pic.resize((round(pic.width*ratio),round(pic.height*ratio)),Image.Resampling.LANCZOS)
        im.paste(pic,((1920-pic.width)//2,230+(630-pic.height)//2))
    if result is not None:
        ImageDraw.Draw(im).rounded_rectangle((1400,635,1815,815),radius=20,fill=BG,outline=CYAN,width=3)
        txt(im,(1608,725),result,105,CYAN,True,'mm')
        if name=='after':txt(im,(1608,602),'Datos registrados',30,GRAY,False,'mm')
    return im
def header(im,title=None,provenance='',clock=None):
    # Subtle image masks preserve a large 3D viewport while keeping captions readable.
    layer=Image.new('RGBA',(1920,1080));dd=ImageDraw.Draw(layer)
    dd.rectangle((0,0,1920,188),fill=(5,12,22,210));dd.rectangle((0,850,1920,1080),fill=(5,12,22,230));im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
    if title:txt(im,(100,56),title,64)
    if provenance:txt(im,(100,874),provenance,30,GRAY,False)
    if clock is not None:txt(im,(1820,874),f't = {int(clock)}',32,GRAY,False,'rt')
    return im

def image_at(renderer,s,t):
    c=s['scene'];duration=s['duration'];p=t/duration;b=s['sentences'];st=lambda i:b[i][0];et=lambda i:b[i][1]
    provenance='Reconstrucción geométrica · G07 · Archivo de investigación';clock=None
    if c in [1,2,8]:
        if c==1 and .37<p<.49:
            return header(app('app',(p-.37)*duration,'DEE COGNITIVE 2.0'),'DEE COGNITIVE 2.0',provenance='Captura auténtica · DEE20_DEMO_01')
        if c==2 and p>.25:
            clock=8*(p-.25)/.75
            im=world(renderer,g07_particles(clock),mix([49,-11,50],[48,-8,49],(p-.25)/.75),[23,21,22],bounds=([10,8,7],[38,40,40]))
            im=header(im,'UN UNIVERSO COMPUTACIONAL 3D',provenance,clock)
            if p>.7:txt(im,(100,151),'Una misma dinámica. Distintas organizaciones.',42,GRAY)
            return im
        # Recorded sparse world, not an invented point cloud.
        pp=demo_particles(c==8);eye=mix([104,-62,93],[62,2,57] if c==1 else [80,-15,76],p);target=[32,29,32]
        im=world(renderer,pp,eye,target)
        title='DEE COGNITIVE 2.0' if c==1 else 'UN UNIVERSO COMPUTACIONAL 3D' if c==2 else 'DE LA INVESTIGACIÓN A LOS PILOTOS'
        im=header(im,title,'Visualización de datos reales · DEE20_DEMO_01 · '+str(demo_frame(c==8)['tick']))
        if c==1:txt(im,(100,145),'Aprender de la experiencia',50,CYAN)
        if c==2 and p<.25:txt(im,(100,150),'Ejemplo: 67 × 67 × 67 posiciones',38,GRAY,False)
        if c==2 and p>.70:txt(im,(100,151),'Una misma dinámica. Distintas organizaciones.',42,GRAY)
        if c==8:
            if p<.36:txt(im,(100,151),'ARQUITECTURA · MECANISMOS · EVIDENCIA',42,GRAY)
            elif p<.82:txt(im,(100,151),'INVESTIGACIÓN DESARROLLADA EN PUEBLA',42,CYAN)
            else:txt(im,(100,151),'DEE COGNITIVE 2.0',58,CYAN)
        return im
    if c==3:
        if t>=st(11):
            cp=(t-st(11))/(duration-st(11));a=E['controls']['selected_cases'][0 if cp<.5 else 1]['value'];where=a['collision_first'] if (cp*2)%1<.28 else a['collision_second'];value=a['record_first']['sreg'] if (cp*2)%1<.28 else a['record_second']['sreg']
            im=world(renderer,[particle(where,CYAN,.8)],mix([30,25,62],[27,31,58],cp),[9,49,43],bounds=([0,40,36],[22,60,50]),highlights=[{'position':a['collision_first'],'color':AMBER},{'position':a['collision_second'],'color':VIOLET}])
            im=header(im,'La experiencia participa en la respuesta','Datos reales · Control C6H04 · N64 · '+('ambas adquisiciones' if cp<.5 else 'segunda omitida'))
            txt(im,(1600,230),str(value),76,CYAN,True,'mm');return im
        # One continuous physical calendar; both initial contacts are simultaneous.
        if t<st(3):
            clock=min(9,9*t/st(3));title='EXPERIENCIA 1 / EXPERIENCIA 2' if clock<5 else 'La experiencia participa en la respuesta'
            eye=mix([49,-11,50],[48,-8,49],min(1,t/st(3)));target=[23,21,22]
        elif t<st(7):
            if t<st(4):clock=10+2.98*(t-st(3))/(st(4)-st(3));title='CONSULTA: 20'
            elif t<st(5):clock=13.;title='PRIMER ENCUENTRO'
            elif t<st(6):clock=13+6.98*(t-st(5))/(st(6)-st(5));title='La experiencia participa en la respuesta'
            else:clock=20.;title='SEGUNDO ENCUENTRO'
            focus=np.array([20,23,30]) if clock<13 else np.array([20,23,30])+(clock-13)/7*np.array([7,7,0]);target=focus.tolist();eye=(focus+np.array([23,-31,25])).tolist()
        else:
            clock=20.;title='SEGUNDO ENCUENTRO' if t<st(7)+1.4 else 'RESULTADO: 30' if t<st(9) else 'La experiencia participa en la respuesta';target=[23,24,27];eye=mix([40,6,45],[43,2,47],(t-st(7))/(duration-st(7)))
        pp=g07_particles(clock)
        if clock>=20:pp=[particle([27,30,30],CYAN,.85)]
        paths=[{'points':[[17,23,30],[20,23,30],(np.array([20,23,30])+max(0,min(7,clock-13))*np.array([1,1,0])).tolist()],'color':CYAN}] if clock>=13 else []
        if clock>=20:
            paths += [{'points':[[20,15,30],[20,23,30]],'color':AMBER},{'points':[[27,30,15],[27,30,30]],'color':VIOLET}]
        if 10<=clock<=20 and t<st(7):eye=(np.array(target)+np.array([11,-15,11])).tolist()
        im=world(renderer,pp,eye,target,bounds=([10,8,7],[38,40,40]),paths=paths,highlights=[{'position':[20,23,30],'color':AMBER},{'position':[27,30,30],'color':VIOLET}] if clock>12 else [])
        im=header(im,title,provenance,clock)
        if 13<=clock<20:txt(im,(100,148),'20 → 23',42,GRAY)
        if clock>=20:txt(im,(100,148),'8222 − 8192 = 30',42,GRAY)
        return im
    if c==4:
        length=et(3)-st(3)
        cuts=[0,st(2),st(3),st(3)+length*.35,st(3)+length*.60,st(4),duration];modes=['before_receipt','teach','after','save','reopen','retained_receipt'];titles=['ANTES','NUEVA EXPERIENCIA','DESPUÉS','GUARDAR Y REABRIR','GUARDAR Y REABRIR','EL CAMBIO SE CONSERVA']
        j=max(i for i,a in enumerate(cuts[:-1]) if a<=t);name=modes[j];title=titles[j];result='+1' if name=='before_receipt' else '−1' if name in ['after','retained_receipt'] else None
        im=app(name,t-cuts[j],title,result)
        return header(im,title,provenance='Petición auténtica · Respuesta del registro primario a22 · 7/7' if name=='after' else 'Captura auténtica · Imagen detenida · DEE20_DEMO_01' if name.endswith('_receipt') else 'Captura auténtica · DEE20_DEMO_01')
    if c==5:
        # Routes reconstructed from code and selected observations, not a dense observed lineage.
        receive=st(1)+(et(1)-st(1))*.44
        if t<receive:q=19+51*t/receive
        elif t<st(2):q=70+2*(t-receive)/(st(2)-receive)
        else:q=72
        clock=q
        if q<66:
            focus=[32,29,46];eye=mix([87,-28,87],[78,-22,81],p);bounds=(0,66)
        else:
            focus=[32,10,46];eye=[47,-10,61];bounds=([24,0,39],[43,21,54])
            if q>=72:
                eye=mix([47,-10,61],[55,-2,63],(t-st(2))/(duration-st(2)))
        im=world(renderer,u0_particles(q),eye,focus,bounds=bounds,highlights=[{'position':[31,10,46],'color':AMBER},{'position':[33,8,46],'color':CYAN}])
        title='CONSULTAR' if q<70 else 'RECIBIR INFORMACIÓN' if q<72 else 'UTILIZARLA'
        im=header(im,title,'Reconstrucción geométrica · U0/CPC7 · Archivo de investigación',clock)
        if q>=72:
            txt(im,(100,148),'UNA RESPUESTA DEPENDIENTE DEL ENTORNO',40,GRAY)
            txt(im,(1600,220),'53 → 60',60,CYAN,True,'mm')
        return im
    if c==6:
        if p<.23:
            im=world(renderer,demo_particles(),mix([105,-80,85],[90,-52,74],p/.23),[32,29,32]);return header(im,'DEE UNIVERSE','Visualización de datos reales · DEE20_DEMO_01')
        name='observe' if p<.5 else 'app' if p<.75 else 'reopen';title='DEE THINKING 4.5' if p<.5 else 'DEE COGNITIVE 2.0'
        return header(app(name,t,'DEL UNIVERSO A LA APLICACIÓN'),title,'Captura auténtica · DEE Cognitive 2.0')
    if c==7:
        # Future application ideas are connected to different existing mechanisms.
        stage=min(2,int(p*3));local=(p*3)%1
        if stage==0:im=app('retained_receipt',local*5,'',result='−1')
        elif stage==1:im=app('before_receipt' if local<.5 else 'after',local*5,'',result='+1' if local<.5 else '−1')
        else:
            clock=10+10*local;pp=g07_particles(clock)
            im=world(renderer,pp,mix([42,0,43],[40,6,45],local),[23,23,26],bounds=([10,8,7],[38,40,40]))
        title=['ASISTENTES CON CONTINUIDAD','SISTEMAS ADAPTATIVOS','INVESTIGACIÓN COGNITIVA'][stage]
        im=header(im,title,'Concepto de aplicación · '+('Captura auténtica · Imagen detenida' if stage==0 or stage==1 and local<.5 else 'Petición auténtica · Datos del registro a22' if stage==1 else 'Reconstrucción geométrica · G07'))
        if p<.1:txt(im,(100,150),'POSIBLES APLICACIONES',42,GRAY)
        return im
    raise ValueError(c)

def subs(im,plan,at):
    for q in plan['captions']:
        if q['start']<=at<q['end']:
            ys=[985] if len(q['lines'])==1 else [960,1014]
            for y,line in zip(ys,q['lines']):txt(im,(960,y),line,44,WHITE,False,'mm')
            return
def preview():
    p=json.loads((W/'timeline.json').read_text(encoding='utf8'));r=get_renderer();folder=W/'previas';folder.mkdir(exist_ok=True)
    for s in p['scenes']:
        for j,x in enumerate([.12,.35,.62,.88]):
            im=image_at(r,s,s['duration']*x);subs(im,p,s['start']+s['duration']*x);im.save(folder/f'{s["scene"]:02}_{j}.png')
    print('PREVIEWS_READY',flush=True)
def render(selected=None):
    p=json.loads((W/'timeline.json').read_text(encoding='utf8'));r=get_renderer();out=W/'escenas';out.mkdir(exist_ok=True)
    for s in p['scenes']:
        c=s['scene']
        if selected and c not in selected:continue
        target=out/f'escena_{c:02}.mp4';assert not target.exists();log=(out/f'escena_{c:02}.log').open('wb')
        cmd=[str(FF),'-hide_banner','-v','warning','-n','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','30','-i','pipe:0','-an','-c:v','libx264','-threads','4','-preset','fast','-crf','17','-profile:v','high','-pix_fmt','yuv420p','-r','30','-fps_mode','cfr',str(target)]
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log,stdout=subprocess.DEVNULL);now=time.monotonic();count=round(s['duration']*30)
        try:
            for f in range(count):
                im=image_at(r,s,f/30);subs(im,p,s['start']+f/30);proc.stdin.write(im.tobytes())
                if f and f%600==0:print('FRAME',c,f,'/',count,flush=True)
            proc.stdin.close();assert proc.wait(timeout=120)==0
        finally:
            if proc.poll() is None:proc.terminate();proc.wait()
            log.close()
        print('SCENE_DONE',c,round(time.monotonic()-now,1),flush=True)
def music():
    p=json.loads((W/'timeline.json').read_text(encoding='utf8'));rate=48000;count=round(p['duration']*rate);out=np.zeros((count,2),np.float32)
    chords=[[130.8128,155.5635,195.9977],[103.8262,155.5635,207.6523],[116.5409,146.8324,174.6141],[97.9989,130.8128,195.9977]]
    for begin in np.arange(0,p['duration'],18):
        a=int(begin*rate);n=min(count-a,round(22*rate));t=np.arange(n)/rate;env=np.minimum(1,t/3)*np.minimum(1,(n/rate-t)/5);v=np.zeros((n,2))
        for j,hz in enumerate(chords[int(begin/18)%4]):
            sig=(np.sin(2*np.pi*hz*t)+.22*np.sin(2*np.pi*2*hz*t))*.0028*env
            v[:,0]+=sig;v[:,1]+=np.sin(2*np.pi*hz*t+.12)*.0028*env
        out[a:a+n]+=v.astype(np.float32)
    out*=np.minimum(1,np.arange(count)/(rate*2))[:,None];out*=np.minimum(1,(count-np.arange(count))/(rate*3))[:,None]
    with wave.open(str(W/'voz/ambiente_original_estereo.wav'),'wb') as f:f.setparams((2,2,rate,0,'NONE','not compressed'));f.writeframes((np.clip(out,-1,1)*32767).astype('<i2').tobytes())
    print('ORIGINAL_MUSIC',count,flush=True)
def mux():
    p=json.loads((W/'timeline.json').read_text(encoding='utf8'));cat=W/'concatenar.txt';cat.write_text('\n'.join(f"file 'escenas/escena_{s['scene']:02}.mp4'" for s in p['scenes']),encoding='utf8')
    target=W/'Cientifica_R02.mp4';assert not target.exists()
    cmd=[str(FF),'-hide_banner','-v','warning','-n','-f','concat','-safe','0','-i',str(cat),'-i',str(W/'voz/locucion_montada.wav'),'-i',str(W/'voz/ambiente_original_estereo.wav'),'-filter_complex','[1:a]aformat=channel_layouts=stereo[v];[v][2:a]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.8:LRA=9[a]','-map','0:v:0','-map','[a]','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-t',str(p['duration']),'-movflags','+faststart','-metadata','title=DEE Cognitive 2.0 — Presentación científica','-metadata','artist=Ivan Erick Tlaltecatl Morales',str(target)]
    subprocess.run(cmd,check=True,timeout=240);print('MUX_DONE',target.stat().st_size,flush=True)
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('action',choices=['plan','clips','preview','render','music','mux']);a.add_argument('--scenes',nargs='*',type=int);n=a.parse_args();{'plan':plan,'clips':clips,'preview':preview,'render':lambda:render(n.scenes),'music':music,'mux':mux}[n.action]()
