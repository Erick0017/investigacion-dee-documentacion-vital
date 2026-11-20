"""10s editorial rendering of retained CPC9 stages. No DEE import/evolution.

All material centres use recorded sites. Opacity transitions are editorial,
not sub-tick trajectories. The admitted input at T207 is an interface marker,
not a retained RAW observation. No interpolation of carrier positions.
"""
from pathlib import Path
import sys, math, json, subprocess, hashlib, argparse, time
import numpy as np
from PIL import Image

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

def camera(t):
    # Editorial move in a continuous fixed coordinate system, never a carrier path.
    move=smooth(6.15,7.2,t)
    settle=smooth(7.9,8.85,t)
    latercenter=lerp([24,13.2,18],[24,12.25,18],settle)
    center=lerp([19.7,7.75,13.65],latercenter,move)
    dist=3.15+math.sin(math.pi*move)*3.2+1.9*(1-settle)*move
    az=math.radians(38-5*smooth(0,5.5,t));el=math.radians(28)
    direction=[math.cos(el)*math.cos(az),math.cos(el)*math.sin(az),math.sin(el)]
    return {'eye':[v+dist*d for v,d in zip(center,direction)],'target':center,
            'fov':42,'lens_shift':[0,.13]}

def model(t):
    formed=smooth(2.25,3.8,t)
    later=smooth(6.5,7.2,t)
    used=smooth(7.25,8.4,t)
    particles=[];boxes=[];labels=[]
    def body(pos,color,alpha,shape='cube',r=.405):
        if alpha>0.001: particles.append({'position':pos,'shape':shape,'radius':r,'color':color,'opacity':alpha})
    # Known T205->T206 local predecessor/result, positions do not interpolate.
    body(A,CYAN,(1-formed)*(1-later),'sphere',.39)
    body(B,AMBER,(1-formed)*(1-later),'cube',.39)
    body(PRODUCT,VIOLET,formed*(1-later),'cube',.425)
    # The second outcome is a retained T210 observation. No invented travel.
    body(USE,'#D4CDF5',used,'cube',.425)
    # Geometric cell scaffolds: editorial grid, not additional DEE material.
    for axis in range(3):
      others=[j for j in range(3) if j!=axis]
      starts=[18.5,6.5,12.5]
      for v in range(4):
       for w in range(4):
        p=[20,8,14];p[others[0]]=starts[others[0]]+v;p[others[1]]=starts[others[1]]+w
        sc=[.003]*3;sc[axis]=1.5
        boxes.append({'position':p,'scale':sc,'color':'#78ADBD','opacity':.027*(1-.7*later)})
    for pos in (PRODUCT,USE):
      boxes.append({'position':pos,'scale':[.49]*3,'color':'#92C6D0','opacity':.055})
    # Prepared/admitted port shown as a hollow frame, not an observed particle.
    portalpha=.65*later*(1-used)
    if portalpha>.001:
      for axis in range(3):
       others=[i for i in range(3) if i!=axis]
       for v in (-.44,.44):
        for w in (-.44,.44):
         p=PORT[:];p[others[0]]+=v;p[others[1]]+=w
         scale=[.012]*3;scale[axis]=.455
         boxes.append({'position':p,'scale':scale,'color':AMBER,'opacity':portalpha})
    if t<2.2:
      labels=[{'text':'A','position':A,'size':58,'offset':[-68,20],'leader':False,'color':CYAN},
              {'text':'B','position':B,'size':58,'offset':[70,-35],'leader':False,'color':AMBER}]
    elif t<6.35:
      labels=[{'text':'Producto común','position':PRODUCT,'size':54,'offset':[0,-250],'leader':False,'color':WHITE}]
    elif t<8:
      labels=[{'text':'Entrada admitida','position':PORT,'size':47,'offset':[0,-100],'leader':False,'color':AMBER}]
    else:
      labels=[{'text':'Nueva consecuencia','position':USE,'size':54,'offset':[0,-250],'leader':False,'color':WHITE}]
    return {'camera':camera(t),'bounds':[[17,5,11.8],[27,17,20]],'grid':False,
      'spatial_grid':{'step':1,'plane_z':12,'opacity':.15,'color':'#476B7B','verticals':False},
      'ground':{'z':11.94,'color':'#10232E','opacity':.62},
      'particles':particles,'boxes':boxes,'labels':labels,
      'provenance':{'representation':'Etapas'}}

def run(preview=False):
    out=HERE/'fotogramas';out.mkdir(exist_ok=True)
    wanted=[0,45,90,135,180,210,240,270,299]
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
        image=renderer.render(model(n/30))
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
