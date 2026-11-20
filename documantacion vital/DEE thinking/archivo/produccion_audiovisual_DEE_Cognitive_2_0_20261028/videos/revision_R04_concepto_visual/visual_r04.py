"""R04: edición audiovisual offline. No importa DEE ni modifica sus estados.

Se reutilizan fotografías, lecturas archivadas y recetas geométricas de R03.
Los movimientos de cámara, líneas guía y halos son recursos editoriales.
render_frame entrega RGB1080 sin subtítulos; pipeline_r04 conserva el reloj.
"""
from functools import lru_cache
from pathlib import Path
import math, json, sys
from PIL import Image, ImageDraw

HERE=Path(__file__).resolve().parent
R03=HERE.parent/'produccion_cientifica/R03'
if str(R03) not in sys.path: sys.path.insert(0,str(R03))
import estilo_r03 as S
import app_visual_r03 as APP
import mecanismos_g07_g08 as M
import agregacion_r03 as AG

CAT_APP='Captura de la aplicación / Application capture'
CAT_RECORD='Visualización de registros / Recorded-data visualization'
CAT_MODEL='Reconstrucción del mecanismo / Mechanism reconstruction'

def finish(im,title,en,category,source,detail=None):
    """Área central despejada y misma zona de subtítulos a lo largo del video."""
    im=im.convert('RGB');d=ImageDraw.Draw(im)
    d.rectangle((0,0,1920,191),fill=S.DARK)
    d.rectangle((0,798,1920,1080),fill=S.DARK)
    d.rectangle((90,177,1830,179),fill=S.MUTED)
    S.text(im,(90,25),title,54,S.WHITE,True,width=1740)
    S.text(im,(90,99),en,30,S.GRAY,width=1740)
    if detail:S.text(im,(90,146),detail,26,S.CYAN,width=1740)
    S.text(im,(90,806),category,26,S.GRAY,width=1740)
    S.text(im,(90,846),source,25,S.GRAY,width=1740)
    return im

def arrow(im,a,b,color=S.CYAN,width=5):
    d=ImageDraw.Draw(im);d.line((a,b),fill=color,width=width)
    ang=math.atan2(b[1]-a[1],b[0]-a[0]);q=18
    d.polygon([b,(b[0]-q*math.cos(ang-.45),b[1]-q*math.sin(ang-.45)),(b[0]-q*math.cos(ang+.45),b[1]-q*math.sin(ang+.45))],fill=color)

def fit(im,pic,box):
    APP._fit(im,pic,box,True)

def chip(im,x,y,es,en,value,color=S.CYAN,w=600):
    S.panel(im,(x,y,x+w,y+230),color,S.DARK)
    S.bi(im,(x+26,y+18),es,en,32,color,width=w-52)
    S.text(im,(x+w/2,y+166),value,86,color,True,'mm',w-52)

def application(phase,p=0.5):
    """Capturas auténticas; cualquier cifra ampliada se rotula como registro."""
    im=S.plain()
    if phase in ('overview','before','retained'):
        src=APP.FULL_RETAINED if phase=='retained' else APP.FULL_BEFORE
        photo=APP._crop(src,(0,87,1262,610))
        if phase=='overview':
            fit(im,photo,(105,205,1815,790))
        elif p<.38:
            # Plano de contexto, seguido de la petición y el recibo reales.
            fit(im,photo,(105,205,1815,790))
            ImageDraw.Draw(im).rounded_rectangle((275,254,732,301),12,outline=S.CYAN,width=5)
        elif p<.68:
            fit(im,APP._crop(src,(12,106,512,180)),(110,260,1810,580))
            S.bi(im,(960,671),'Petición real: palabra clasifica','Actual request: palabra clasifica',44,S.CYAN,'mm',1700)
        else:
            fit(im,APP._crop(src,(20,397,512,470)),(110,255,1810,560))
            S.bi(im,(960,667),'Recibo de la aplicación: '+('−1' if phase=='retained' else '+1'),'Application receipt: '+('−1' if phase=='retained' else '+1'),48,S.CYAN,'mm',1700)
    elif phase=='teach':
        photo=APP._frame('teach',p).crop((0,153,496,265))
        fit(im,photo,(110,220,1810,615))
        S.bi(im,(960,671),'Enseñanza explícita admitida: 3/3','Explicit teaching admitted: 3/3',48,S.AMBER,'mm',1700)
    elif phase=='after':
        fit(im,APP._frame('after',p),(110,243,1810,500))
        S.bi(im,(420,583),'Registro a22','Recorded result a22',34,S.GRAY,'mm',600)
        S.text(im,(1380,623),'−1',134,S.CYAN,True,'mm',600)
        arrow(im,(720,620),(1110,620))
        S.bi(im,(420,678),'Misma señal','Same signal',41,S.WHITE,'mm',600)
    elif phase=='compare':
        # Comparación editorial: no es una nueva GUI ni bifurcaciones.
        fit(im,APP._frame('after',p),(160,211,1760,420))
        chip(im,110,462,'Antes · a13','Before · a13','+1',S.CYAN,730)
        chip(im,1080,462,'Después · a22','After · a22','−1',S.VIOLET,730)
        arrow(im,(873,580),(1045,580),S.AMBER)
        S.text(im,(960,752),'Una misma vida · nueva enseñanza / One life · new teaching',31,S.GRAY,False,'mm',1720)
    elif phase=='save':
        fit(im,APP._frame('save',p).crop((0,0,494,192)),(170,205,1750,785))
    elif phase=='reopen':
        fit(im,APP._frame('reopen',p),(180,230,1740,620))
        S.bi(im,(960,681),'Reapertura registrada · b02','Archived reopening · b02',46,S.CYAN,'mm',1720)
    else: raise ValueError(phase)
    return im

def model(renderer,phase,p):
    """Sólo rutas de la receta G07; cámara editorial, no nuevos estados."""
    original=M._world
    def camera(r,particles,eye=M.G07_EYE,target=M.G07_TARGET,bounds=M.G07_BOUNDS,paths=(),highlights=()):
        # Desplazamiento óptico suave alrededor de coordenadas verificadas.
        if tuple(eye)==tuple(M.G07_EYE):
            eye=[eye[0]+1.2*math.sin(p*math.pi),eye[1]-.8*math.sin(p*math.pi),eye[2]]
        return r.render(particles,eye=eye,target=target,bounds=bounds,paths=list(paths),highlights=list(highlights),fov=42).convert('RGB')
    M._world=camera
    try: im=M.g07(renderer,phase,p)
    finally: M._world=original
    return im

def opening(renderer,t,duration):
    if t<8:
        im=application('before',.4+.6*min(1,t/8));cat=CAT_APP
        source='DEE20_DEMO_01 · a13 · Consulta registrada: palabra clasifica'
    elif t<15:
        im=application('overview',.5);cat=CAT_APP
        source='DEE20_DEMO_01 · Aplicación real · Captura original ampliada'
    else:
        im=application('teach' if t<19 else 'after',min(1,(t-15)/max(.1,duration-15)))
        cat=CAT_APP if t<19 else CAT_APP+' + '+CAT_RECORD
        source='DEE20_DEMO_01 · Después de nueva enseñanza: a21 → a22'
    return finish(im,'DEE COGNITIVE 2.0','Inteligencia mediante interacciones / Intelligence through interactions',cat,source,'Tecnología experimental / Experimental technology')

def mechanism(renderer,scene,t):
    p=t/scene['duration']
    if p<.19:
        im=application('overview',.5)
        S.panel(im,(1230,280,1780,510),S.CYAN,S.DARK)
        S.bi(im,(1270,310),'Computadora: soporte','Computer: execution support',36,S.CYAN,width=480)
        cat=CAT_APP;source='DEE20_DEMO_01 · La computadora ejecuta el programa'
    else:
        q=(p-.19)/.81
        phase='orientacion' if q<.34 or t>=25.4 else 'primer_encuentro' if q<.64 else 'resultado'
        im=model(renderer,phase,min(1,q*2))
        cat=CAT_MODEL;source='G07 · Otro experimento · Señal, relaciones y resultado identificados'
        if phase=='primer_encuentro':
            S.text(im,(111,720),'Encuentro reconstruido de la receta',29,S.GRAY,width=720)
        if phase=='resultado':
            S.text(im,(112,720),'La historia interviene en una consulta',29,S.GRAY,width=720)
    return finish(im,'REGLAS FIJAS · HISTORIA QUE CAMBIA','Fixed rules · History changes the response',cat,source)

def composition(renderer,scene,t,base):
    i,p=base.sentence(scene,t)
    if i<=1:phase='enseñanza';pp=0
    elif i==2:phase='enseñanza';pp=p
    elif i==3:phase='consulta';pp=p
    elif i==4:phase='primer_encuentro';pp=p
    elif i==5:phase='viaje';pp=p
    elif i==6:phase='segundo_encuentro';pp=p
    elif i in (7,8):phase='resultado';pp=p
    elif i==9:phase='control';pp=p
    else:phase='recap';pp=p
    if phase=='control':
        im=M.g07(renderer,'control',p)
        return finish(im,'OTRA PRUEBA DE CONTROL','Separate control test',CAT_RECORD,'C6H04 · N64 · Consulta 0 · Relaciones −5 y +2','−4101: lectura del acceso; no una respuesta aritmética válida / readout, not a valid arithmetic answer')
    im=model(renderer,phase,pp)
    if phase=='primer_encuentro':
        S.text(im,(1170,680),'23: valor derivado del protocolo',27,S.GRAY,width=620)
    return finish(im,'DOS ENCUENTROS CONECTADOS','Two connected encounters',CAT_MODEL,'G07 · N67 · Consulta 20 → valor intermedio 23 → resultado 30','Ámbar y violeta: relaciones adquiridas · Cian: señal / Amber and violet: learned relations · Cyan: signal')

def social(scene,t,base,renderer):
    i,p=base.sentence(scene,t)
    if i<=1:
        q=base.markrange(scene,0,2,t);im=base.social(q)
        k=min(3,int(q*4))
        if k in (1,2):arrow(im,(790,510),(1100,510),S.CYAN,7)
        return finish(im,'MENSAJE PRIVADO · USO POSTERIOR','Private message · Subsequent use',CAT_RECORD,'IC01 · B y E1 · Información de B; transmisión y efecto registrados')
    q=base.markrange(scene,2,4,t)
    im=M.g08(renderer,q)
    return finish(im,'TRANSFERIR UNA RELACIÓN','Transferring a relationship',CAT_MODEL,'G08 · Otra realización · Relación −5 recibida y utilizada: 4 → −1','No es copia de una mente / Not a copy of a mind')

def apd(scene,t,base):
    i,p=base.sentence(scene,t);im=S.plain()
    if i<=1:
        q=base.markrange(scene,0,2,t)
        if q<.48:
            word,value=('luma','+1') if q<.24 else ('nara','−1')
            S.bi(im,(110,224),'Nueva asociación registrada','New recorded association',44,S.WHITE,width=1700)
            chip(im,110,366,'Señal enseñada','Taught signal',word,S.AMBER,650)
            chip(im,1160,366,'Señal al consultar','Signal on query',value,S.CYAN,650)
            arrow(im,(800,490),(1115,490))
        else:
            S.bi(im,(110,224),'Después: lo anterior sigue utilizable','Later: prior learning remains usable',43,S.WHITE,width=1700)
            S.bi(im,(110,370),'luma → +1      nara → −1','New associations used after teaching',52,S.CYAN,width=1700)
            S.bi(im,(110,535),'También se consulta memoria anterior','Earlier memory is queried as well',44,S.AMBER,width=1700)
            S.text(im,(110,700),'Panel: 14/14 señales anteriores · 6/6 consultas de memoria · 2/2 nuevas',32,S.GRAY,width=1700)
    else:
        im=base.apd(scene,t)
    return finish(im,'UNA MISMA TRAYECTORIA','One continuous trajectory',CAT_RECORD,'APD03_MAIN · Registros reales · Tarea apd03_goal_4; el archivo lo crea la herramienta externa')

def platform(renderer,scene,t,base):
    i,p=base.sentence(scene,t)
    if i>=5:
        return base.image_at(renderer,scene,t)
    if i in (0,3):im=application('overview',p);cat=CAT_APP
    elif i==2:im=application('teach',p);cat=CAT_APP
    elif i==1:im=base.body_demo(renderer,p);cat='Configuración guardada / Saved configuration'
    else:im=application('reopen',p);cat=CAT_APP
    # Retirar sólo los rótulos editoriales de la toma reutilizada antes de
    # colocar la leyenda. La foto auténtica y sus controles quedan arriba.
    ImageDraw.Draw(im).rectangle((0,650,1920,797),fill=S.BG)
    # Leyenda editorial de tres capas, sin simular una nueva interfaz.
    for j,(es,en) in enumerate([('Universe','Reglas del mundo / World rules'),('thinking','Instrumentos / Tools'),('Cognitive','Aplicación / Application')]):
        x=110+j*585;col=S.CYAN if j==max(0,min(2,i-1)) else S.GRAY
        S.panel(im,(x,658,x+550,785),col,S.DARK)
        S.text(im,(x+275,688),es,39,col,True,'mm',500)
        S.text(im,(x+275,747),en,26,S.GRAY,False,'mm',500)
        if j<2:arrow(im,(x+553,719),(x+578,719),S.CYAN,3)
    return finish(im,'UNIVERSE → THINKING → COGNITIVE','Motor → instrumentos → aplicación / Engine → tools → application',cat,'Tres capas conectadas · La computadora proporciona el soporte / Three connected layers · Computer support')

def current_sequence(t):
    """Lecturas archivadas a26; no se anima una ruta interna que no se registró."""
    im=S.plain();second=t>=3.8
    S.bi(im,(110,230),'El resultado se utiliza en la operación siguiente','The result is used in the next operation',43,S.WHITE,width=1700)
    S.text(im,(960,429),'4 + 5 → 9',112,S.CYAN,True,'mm',1700)
    if second:
        arrow(im,(1380,470),(1380,552),S.AMBER,6)
        S.text(im,(960,648),'9 − 2 → 7',112,S.VIOLET,True,'mm',1700)
    else:
        S.bi(im,(960,646),'Salida nativa: 9','Native output: 9',43,S.AMBER,'mm',1700)
    return finish(im,'DEE COGNITIVE 2.0 · USO CONECTADO','Connected use',CAT_RECORD,'DEE20_DEMO_01 · a26_composition · Secuencia preparada; proveedor nativo en ambos pasos')

def closing(renderer,scene,t,base):
    i,p=base.sentence(scene,t)
    # Inserción dentro del cierre existente: ocho segundos, sin audio adicional.
    if 10.49<=t<18.49:return current_sequence(t-10.49)
    if i==0:im=application('compare',p);cat=CAT_APP+' + '+CAT_RECORD
    elif i==2:im=base.apd(next(s for s in base.read(R03/'timeline_R03.json')['scenes'] if s['id']=='s06'),999);cat=CAT_RECORD
    else:im=application('overview' if i in (3,4) else 'retained',p);cat=CAT_APP
    title='INVESTIGACIÓN DESARROLLADA EN PUEBLA' if i==3 else 'DEE COGNITIVE 2.0'
    en='Research developed in Puebla' if i==3 else 'La experiencia cambia la respuesta / Experience changes the response'
    return finish(im,title,en,cat,'Recapitulación de registros · Funciones demostradas en sus dominios; no fiabilidad universal')

def render_frame(renderer,scene,local_frame,base):
    t=local_frame/30;sid=scene['id']
    if sid=='s01':return opening(renderer,t,scene['duration'])
    if sid=='s02':
        i,p=base.sentence(scene,t)
        phase='overview' if i<=1 else 'before' if i<=3 else 'teach' if i in (4,6) else 'compare' if i==8 else 'after' if i in (5,7) else ('save' if p<.25 else 'reopen' if p<.55 else 'retained') if i==9 else 'retained'
        if i==2:p=.45
        if i==3:p=.95
        im=application(phase,p)
        title='MISMA SEÑAL' if i<=3 else 'NUEVA ENSEÑANZA' if i in (4,6) else 'RESPUESTA REVISADA' if i in (5,7,8) else 'GUARDAR · REABRIR · UTILIZAR'
        return finish(im,title,'Same signal · Experience revises the response' if i<=8 else 'Save · Reopen · Use',CAT_APP+' + '+CAT_RECORD,'DEE20_DEMO_01 · a13 → a21 → a22 → a44 → b02 → b09','+1 y −1 son códigos de respuesta / +1 and −1 are response codes')
    if sid=='s03':return mechanism(renderer,scene,t)
    if sid=='s04':return composition(renderer,scene,t,base)
    if sid=='s05a':return social(scene,t,base,renderer)
    if sid=='s06':return apd(scene,t,base)
    if sid=='s07':return platform(renderer,scene,t,base)
    if sid=='s08':return closing(renderer,scene,t,base)
    # AA46, U0, Ciclo02 y MU/FI01: se conservan los datos y secuencias originales.
    # El driver aplica sus subtítulos dentro de la misma zona segura.
    return base.image_at(renderer,scene,t)
