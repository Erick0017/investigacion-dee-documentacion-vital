"""R12 native1080 editorial projection. No DEE imports or physics updates.

Physical positions are discrete source coordinates. Schemes are explicitly
separate. Text bounds and projection regions are checked at render time.
"""
from pathlib import Path
from functools import lru_cache
import hashlib,itertools,json,math
from PIL import Image,ImageDraw,ImageFont

W,H,FPS=1920,1080,30
BG='#F6F7F9';INK='#152334';MUTED='#46586C';LIGHT='#D2D8DF'
COLORS={'input':'#007F9E','teaching':'#B96B00','difference':'#7544AC',
        'reader':INK,'control':'#84909E','site':'#829AB3'}
FONT=Path(r'C:\Windows\Fonts\arial.ttf')
FONT_BOLD=Path(r'C:\Windows\Fonts\arialbd.ttf')

def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
@lru_cache(maxsize=30)
def font(size,bold=True):return ImageFont.truetype(str(FONT_BOLD if bold else FONT),int(size))
def text(d,s,box,size=80,color=INK,lines=1,align='center'):
    s=str(s);f=font(size);x,y,w,h=box
    parts=[];line=''
    for word in s.split():
        trial=(line+' '+word).strip()
        if f.getlength(trial)<=w:line=trial
        else:
            if not line:raise ValueError('Word too wide: '+s)
            parts.append(line);line=word
    if line:parts.append(line)
    if len(parts)>lines:raise ValueError('Text needs another phase, not condensed/smaller font: '+s)
    heights=[f.getbbox(t)[3]-f.getbbox(t)[1] for t in parts]
    total=sum(heights)+12*max(0,len(parts)-1)
    if total>h:raise ValueError(f'Text clipping {s!r}: {total}>{h}')
    yy=y+(h-total)/2;boxes=[]
    for row,hh in zip(parts,heights):
        b=f.getbbox(row);width=f.getlength(row);xx=x+(w-width)/2 if align=='center' else x
        d.text((xx,yy-b[1]),row,font=f,fill=color)
        boxes.append([xx,yy,xx+width,yy+hh]);yy+=hh+12
    for a,b,c,e in boxes:
        if a<96-.01 or c>1824+.01 or b<60-.01 or e>890+.01:raise ValueError('Text outside safe/title/action region: '+s)
    return boxes

def shade(c,k):return tuple(max(0,min(255,round(int(c[i:i+2],16)*k)))for i in [1,3,5])
def project_camera(rect,bounds,az=42,el=28):
    lo,hi=bounds;center=[(a+b)/2 for a,b in zip(lo,hi)];az=math.radians(az);el=math.radians(el)
    right=(-math.sin(az),math.cos(az),0)
    up=(-math.sin(el)*math.cos(az),-math.sin(el)*math.sin(az),math.cos(el))
    dep=(math.cos(el)*math.cos(az),math.cos(el)*math.sin(az),math.sin(el))
    dot=lambda a,b:sum(x*y for x,y in zip(a,b))
    corners=list(itertools.product(*zip(lo,hi)))
    q=[(dot([a-b for a,b in zip(p,center)],right),dot([a-b for a,b in zip(p,center)],up))for p in corners]
    dx=max(x for x,y in q)-min(x for x,y in q);dy=max(y for x,y in q)-min(y for x,y in q)
    x,y,w,h=rect;scale=min((w-48)/max(.5,dx),(h-32)/max(.5,dy))
    def proj(p):
        v=[a-b for a,b in zip(p,center)]
        return x+w/2+dot(v,right)*scale,y+h/2-dot(v,up)*scale
    return proj,lambda p:dot(p,dep),scale

def cube(d,p,project,depth,color,wire=False):
    vertices=[tuple(a+b*.32 for a,b in zip(p,delta))for delta in itertools.product((-1,1),repeat=3)]
    projected=[project(x)for x in vertices]
    faces=[((0,1,3,2),1.03),((4,6,7,5),.85),((0,4,5,1),1.1),
           ((2,3,7,6),.72),((0,2,6,4),.80),((1,5,7,3),1.18)]
    faces.sort(key=lambda v:sum(depth(vertices[i])for i in v[0])/4)
    for face,k in faces:d.polygon([projected[i]for i in face],fill=None if wire else shade(color,k),outline=shade(color,.72),width=2)

def arrow(d,a,b,color=INK,width=4):
    dx,dy=b[0]-a[0],b[1]-a[1];n=math.hypot(dx,dy)
    if n<2:return
    ux,uy=dx/n,dy/n
    d.line((*a,*b),fill=BG,width=width+5)
    d.polygon([b,(b[0]-ux*17-uy*10,b[1]-uy*17+ux*10),(b[0]-ux*17+uy*10,b[1]-uy*17-ux*10)],fill=BG)
    d.line((*a,*b),fill=color,width=width)
    d.polygon([b,(b[0]-ux*13-uy*7,b[1]-uy*13+ux*7),(b[0]-ux*13+uy*7,b[1]-uy*13-ux*7)],fill=color)

def physical_world(im,panel,rect,bounds):
    layer=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(layer)
    pts=panel.get('points',[]);n=panel.get('N')
    assert isinstance(n,int) and n>0
    for point in pts:
        assert 'raw'in point and len(point['site'])==3
        assert all(isinstance(x,int)and 0<=x<n for x in point['site'])
        assert 0<=int(point['raw'])<2**64
    az=panel.get('camera_azimuth_degrees',42);el=panel.get('camera_elevation_degrees',28)
    proj,depth,scale=project_camera(rect,bounds,az,el)
    lo,hi=bounds
    # Faint lattice is a coordinate reference, never extra active material.
    z=lo[2]
    for axis in [0,1]:
        count=max(1,math.ceil(hi[axis]-lo[axis]));step=max(1,math.ceil(count/12))
        for v in range(math.ceil(lo[axis]),math.floor(hi[axis])+1,step):
            a=list(lo);b=list(hi);a[2]=b[2]=z;a[axis]=b[axis]=v
            d.line((*proj(a),*proj(b)),fill='#DCE1E8',width=2)
    for point in sorted(pts,key=lambda v:depth(v['site'])):
        raw=int(point['raw'])
        if raw==0:continue
        color=COLORS.get(point.get('role','site'),COLORS['site'])
        cube(d,point['site'],proj,depth,color,wire=(raw&0xffffffff)==0)
        if point['site'] in panel.get('direction_sites',[]) and any(point.get('direction',[])):
            end=[a+.78*b for a,b in zip(point['site'],point['direction'])]
            arrow(d,proj(point['site']),proj(end),INK)
    for role in ['input','teaching','reader','difference']:
        sites=list(panel.get(role+'_sites',[]))
        if panel.get(role+'_site')is not None:sites.append(panel[role+'_site'])
        for site in sites:
            assert all(0<=v<n for v in site)
            x,y=proj(site);rad=max(16,min(44,scale*.62))
            d.rectangle((x-rad,y-rad,x+rad,y+rad),outline=COLORS[role],width=5)
    x,y,w,h=rect;im.paste(layer.crop((x,y,x+w,y+h)),(x,y))
    return {'N':n,'tick':panel.get('tick'),'observed_points':len(pts),'bounds':bounds,'pixels_per_cell':scale,
            'camera_azimuth':az,'camera_elevation':el,'lattice_is_annotation':True}

def generic_scheme(im,kind,phase):
    """Prepared explanatory diagrams. Never emitted with Registro/Etapas."""
    d=ImageDraw.Draw(im);boxes=[]
    if kind in ['universe','site_state','close','future']:
        # A recognisable 3D coordinate lattice, distinct from data-driven sites.
        proj,depth,scale=project_camera((250,300,1420,420),[[-1,-1,-1],[5,5,3]],35,25)
        for z in [0,1,2]:
            for x in range(5):
                for y in range(5):
                    color='#B9C6D5';wire=True
                    if [x,y,z]==[2,2,1]:color=COLORS['input'] if phase<1 else COLORS['teaching'];wire=False
                    if kind=='future' and [x,y,z] in [[1,1,0],[3,3,2]]:color=COLORS['difference'];wire=False
                    cube(d,[x,y,z],proj,depth,color,wire)
        if kind=='site_state':
            boxes+=text(d,'Lugar fijo',(110,720,600,100),80)
            boxes+=text(d,'Estado que cambia',(850,720,950,100),80,color=COLORS['teaching'])
    elif kind in ['layers','codec','agenda']:
        labels=['Universe','Thinking','Cognitive'] if kind=='layers' else ['Señal','Codificación','Entrada DEE'] if kind=='codec' else ['Oportunidad','Encuentro DEE','Pregunta']
        for i,label in enumerate(labels):
            x=125+i*580;c=COLORS['input'] if i==min(2,phase) else '#74869A'
            d.rounded_rectangle((x,370,x+510,610),radius=16,outline=c,width=5,fill='#FFFFFF')
            boxes+=text(d,label,(x+10,400,490,170),80,lines=2)
            if i<2:arrow(d,(x+520,490),(x+565,490),MUTED)
    else:raise KeyError(kind)
    return boxes

def render(m):
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im);boxes=[];worlds=[]
    boxes+=text(d,m['title'],(96,60,1728,104),84)
    category=m['evidence_type']
    assert category in ['Registro','Etapas','Esquema']
    notice=m.get('notice','')
    boxes+=text(d,category+(' · '+notice if notice else ''),(96,166,1728,80),64,color=MUTED)
    panels=m.get('panels',[])
    if panels:
        assert len(panels)<=2
        external=m.get('external_service_stage') is not None
        slots=[(96,330,816,390)] if external else [(96,330,1728,390)] if len(panels)==1 else [(96,330,816,390),(1008,330,816,390)]
        for panel,rect in zip(panels,slots):
            x,y,w,h=rect
            boxes+=text(d,panel.get('label',''),(x,250,w,82),80,lines=1)
            bounds=panel.get('bounds') or m.get('bounds')
            if bounds is None:
                sites=[p['site']for p in panel['points']]+panel.get('reader_sites',[])
                if panel.get('input_site')is not None:sites.append(panel['input_site'])
                assert sites
                bounds=[[min(p[i]for p in sites)-1 for i in range(3)],[max(p[i]for p in sites)+1 for i in range(3)]]
            worlds.append(physical_world(im,panel,rect,bounds))
            d=ImageDraw.Draw(im)
            if panel.get('output_text')is not None:
                assert panel.get('reader_evidence'),'Never draw a target without its qualified reader'
                boxes+=text(d,'Salida '+str(panel['output_text']),(x,716,w,112),110)
            elif panel.get('bottom'):
                boxes+=text(d,panel['bottom'],(x,722,w,100),80,lines=1)
        if external:
            # A state diagram of the real external service, not a claimed
            # coordinate trajectory of a robot or a DEE region.
            stage=m['external_service_stage'];record=m['external_service_record']
            boxes+=text(d,'Servicio externo',(1008,250,816,82),80)
            d.rounded_rectangle((1100,365,1740,630),radius=16,outline=LIGHT,width=4,fill='#FFFFFF')
            boxes+=text(d,'Esquema',(1110,375,620,80),64,color=MUTED)
            label='Por actuar'if stage==0 else'Contacto'
            if stage>0:assert record['observed_result']['contact'] is True
            boxes+=text(d,label,(1120,485,600,105),80,color=INK)
            arrow(d,(994,490),(923,490),MUTED)if stage==2 else arrow(d,(923,490),(994,490),MUTED)
            boxes+=text(d,'Puente preparado',(1008,710,816,100),80)
    else:
        assert category=='Esquema'
        boxes+=generic_scheme(im,m['scheme']['kind'],m.get('phase',0));d=ImageDraw.Draw(im)
    if m.get('footer'):
        boxes+=text(d,m['footer'],(96,822,1728,68),64,color=MUTED)
    # No burned-in subtitles. y890..1020 stays genuinely clear.
    return im,{'width':W,'height':H,'font_condensed':False,'text_boxes':boxes,'worlds':worlds,
               'evidence_type':category,'subtitle_reserved_y':[890,1020]}
