"""10s editorial rendering of retained CPC9 stages. No DEE import/evolution.

All material centres use recorded sites. Opacity transitions are editorial,
not sub-tick trajectories. The admitted input at T207 is an interface marker,
not a retained RAW observation. No interpolation of carrier positions.
"""
from pathlib import Path
import sys, math, json, subprocess, hashlib, argparse, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TESTS = next(p for p in HERE.parents if p.name == 'tests')
sys.path.insert(0, str(HERE/'render'))
from renderer_r05 import WebGLRenderer
FFMPEG = TESTS/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
FPS, W, H = 30, 1920, 1080
CYAN, AMBER, VIOLET, WHITE = '#46C7EB', '#F4C46B', '#B89BE8', '#E8F4F3'
A, B, PRODUCT, PORT, USE = [19,8,13], [20,7,14], [20,8,14], [24,15,18], [24,12,18]

def smooth(a,b,t):
    u=max(0.,min(1.,(t-a)/(b-a))); return u*u*(3-2*u)

def lerp(a,b,u):return [x+(y-x)*u for x,y in zip(a,b)]

def camera(t,view):
    # Camera coordinates are editorial. Carrier coordinates never interpolate.
    if view=='first':
        center=[19.7,7.75,13.7];dist=3.6
    elif view=='admission':
        center=[24,15,18];dist=3.9
    else:
        center=[24,12.1,18];dist=3.35
    az=math.radians(38);el=math.radians(36)
    direction=[math.cos(el)*math.cos(az),math.cos(el)*math.sin(az),math.sin(el)]
    return {'eye':[v+dist*d for v,d in zip(center,direction)],'target':center,
            'fov':42,'lens_shift':[0,.02 if view=='first' else .13]}

def model(t,view='first'):
    formed=smooth(2.0,3.35,t)
    used=1.0 if view=='use' else 0.0
    particles=[];boxes=[];labels=[]
    def body(pos,color,alpha,shape='cube',r=.405):
        if alpha>0.001: particles.append({'position':pos,'shape':shape,'radius':r,'color':color,'opacity':alpha})
    # Known T205->T206 local predecessor/result, positions do not interpolate.
    if view=='first':
      body(A,CYAN,1-formed,'sphere',.39)
      body(B,AMBER,1-formed,'cube',.39)
      body(PRODUCT,VIOLET,formed,'cube',.425)
    # The second outcome is a retained T210 observation. No invented travel.
    if view=='use':body(USE,'#D4CDF5',used,'cube',.425)
    # Geometric cell scaffolds: editorial grid, not additional DEE material.
    for axis in range(3):
      others=[j for j in range(3) if j!=axis]
      starts=[18.5,6.5,12.5] if view=='first' else [22.5,11.5,16.5]
      for v in range(4):
       for w in range(4):
        p=[x+1.5 for x in starts];p[others[0]]=starts[others[0]]+v;p[others[1]]=starts[others[1]]+w
        sc=[.003]*3;sc[axis]=1.5
        boxes.append({'position':p,'scale':sc,'color':'#78ADBD','opacity':.026})
    for pos in ((PRODUCT,) if view=='first' else (USE,)):
      boxes.append({'position':pos,'scale':[.49]*3,'color':'#92C6D0','opacity':.055})
    # Prepared/admitted port shown as a hollow frame, not an observed particle.
    portalpha=.8 if view=='admission' else 0
    if portalpha>.001:
      for axis in range(3):
       others=[i for i in range(3) if i!=axis]
       for v in (-.44,.44):
        for w in (-.44,.44):
         p=PORT[:];p[others[0]]+=v;p[others[1]]+=w
         scale=[.012]*3;scale[axis]=.455
         boxes.append({'position':p,'scale':scale,'color':AMBER,'opacity':portalpha})
    if view=='first' and formed<.55:
      labels=[{'text':'A','position':A,'size':58,'offset':[-68,20],'leader':False,'color':CYAN},
              {'text':'B','position':B,'size':58,'offset':[70,-35],'leader':False,'color':AMBER}]
    elif view=='first':
      labels=[{'text':'Producto común','position':PRODUCT,'size':52,'offset':[0,230],'leader':False,'color':WHITE}]
    elif view=='use':
      labels=[{'text':'Lectura posterior','position':USE,'size':50,'offset':[0,220],'leader':False,'color':WHITE}]
    plane=12 if view=='first' else 17
    return {'camera':camera(t,view),'bounds':[[17,5,11.8],[28,18,21]],'grid':False,
      'spatial_grid':{'step':1,'plane_z':plane,'opacity':.13,'color':'#476B7B','verticals':False},
      'ground':{'z':plane-.06,'color':'#10232E','opacity':.62},
      'particles':particles,'boxes':boxes,'labels':labels,
      'provenance':{'representation':'Etapas'}}

FONTS={s:ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',s) for s in (30,34,42,52,58,72)}
def editorial(image,t):
    d=ImageDraw.Draw(image)
    def text(x,y,s,size=52,color=WHITE,anchor='mm'):
      d.text((x,y),s,font=FONTS[size],fill=color,anchor=anchor,stroke_width=2,stroke_fill='#07131D')
    stage=0 if t<2 else 1 if t<4.5 else 2 if t<7 else 3
    titles=['Aportes · T205','Producto · T206','Admisión preparada · T207','Consecuencia · T210']
    title='T205 → T206 · Producto' if 2<=t<3.35 else titles[stage]
    text(960,63,title,72)
    # The sequential headers carry time. Omit the optional miniature guide:
    # its T205 label encroached on the contribution's top face in close-up.
    if 4.35<=t<5.05 or 6.7<=t<7.7:text(960,784,'Salto de registro',52)
    elif 4.5<=t<6.7:text(960,784,'Recurso 7 · sin cuadro físico',52,AMBER)
    return image

def frame(renderer,t):
    # A short editorial dissolve changes the view, not the material trajectory.
    if 4.35<t<4.95:
      a=renderer.render(model(4.35,'first'))
      b=renderer.render(model(4.95,'admission'))
      image=Image.blend(a,b,smooth(4.35,4.95,t))
    elif 6.7<t<7.3:
      a=renderer.render(model(6.7,'admission'))
      b=renderer.render(model(7.3,'use'))
      image=Image.blend(a,b,smooth(6.7,7.3,t))
    else:image=renderer.render(model(t,'first' if t<=4.35 else 'admission' if t<=6.7 else 'use'))
    return editorial(image,t)

def run(preview=False):
    out=HERE/'fotogramas';out.mkdir(exist_ok=True)
    wanted=[0,60,90,120,150,180,210,240,297]
    start=time.monotonic()
    if preview: frames=wanted
    else:frames=range(300)
    writer=None
    if not preview:
      log=(HERE/'encode_mudo.log').open('wb')
      writer=subprocess.Popen([str(FFMPEG),'-hide_banner','-y','-f','rawvideo','-pixel_format','rgb24',
        '-video_size','1920x1080','-framerate','30','-i','pipe:0','-an','-c:v','libx264','-preset','slow',
        '-crf','17','-pix_fmt','yuv420p','-r','30','-frames:v','300','-vf','setsar=1',
        '-movflags','+faststart',str(HERE/'piloto_mudo.mp4')],stdin=subprocess.PIPE,stderr=log,stdout=subprocess.DEVNULL,
        creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    try:
      with WebGLRenderer() as renderer:
       for n in frames:
        image=frame(renderer,n/30)
        if n in wanted:image.save(out/f'f{n:03}.png')
        if writer:writer.stdin.write(image.tobytes())
        if n%30==0:print(f'frame {n}/300; host {time.monotonic()-start:.1f}s',flush=True)
       info=renderer.info
      if writer:
       writer.stdin.close();code=writer.wait(timeout=180)
       if code:raise RuntimeError('FFmpeg encode failed; see encode_mudo.log')
    finally:
      if writer and writer.poll() is None:writer.terminate();writer.wait(timeout=15)
    (HERE/('PREVIEW_RENDER.json' if preview else 'RENDER_NATIVE_1080.json')).write_text(json.dumps({
       'native_canvas':[W,H],'frames_rendered':len(frames),'fps':FPS,'host_seconds':time.monotonic()-start,
       'browser':info,'new_DEE_ticks':0,'physical_interpolation':False,
       'editorial_interpolation':'camera, opacity between retained stages; no position interpolation',
       'empty_grid':'editorial coordinate scaffold, not invented active DEE matter'},ensure_ascii=False,indent=2),'utf8')
    thumbs=[]
    for n in wanted:
      im=Image.open(out/f'f{n:03}.png').convert('RGB');im.thumbnail((640,360));thumbs.append(im)
    sheet=Image.new('RGB',(1920,1080))
    for i,im in enumerate(thumbs):sheet.paste(im,((i%3)*640,(i//3)*360))
    sheet.save(HERE/'CONTACTO_RENDER.png')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--preview',action='store_true');a=p.parse_args();run(a.preview)
