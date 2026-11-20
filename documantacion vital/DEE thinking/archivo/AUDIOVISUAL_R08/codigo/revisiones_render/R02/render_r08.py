"""Native 1920x1080 editorial projection of recorded DEE sites.

No engine imports, physics, inferred trajectories, or response computation.
Input positions remain in the coordinates of their own source world. The
orthographic camera and all outlines/text are editorial annotations.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import itertools
import json
import math
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

W,H,FPS=1920,1080,30
BACKGROUND='#0B1220'
COLORS={'input':'#47D7F2','teaching':'#FFBF54','difference':'#B794F4',
        'reader':'#F5F7FA','control':'#B3B9C6','site':'#C2CBD8'}
ROOT=Path(__file__).resolve().parents[1]
FONT=Path(r'C:\Windows\Fonts\bahnschrift.ttf')


@lru_cache(maxsize=30)
def font(size,weight=600):
    f=ImageFont.truetype(str(FONT),int(size))
    # Bahnschrift supplied locally by Windows. Condensed at origin, not
    # a raster stretch of a rendered image. 75 is this font's width minimum.
    f.set_variation_by_axes([weight,75])
    return f


def wrap(text,size,width,max_lines=2):
    f=font(size); words=str(text).split(); lines=[]; line=''
    for word in words:
        candidate=(line+' '+word).strip()
        if f.getlength(candidate)<=width:
            line=candidate
        else:
            if not line: raise ValueError('Unbreakable label outside its box: '+text)
            lines.append(line); line=word
    if line: lines.append(line)
    if len(lines)>max_lines: raise ValueError('Label needs another shot, not a smaller font: '+text)
    if any(f.getlength(s)>width for s in lines): raise ValueError(text)
    return lines


def text(draw,value,box,size=96,color='#F5F7FA',max_lines=2,align='center'):
    x,y,w,h=box; lines=wrap(value,size,w,max_lines); f=font(size)
    # Actual glyph bounding boxes, not nominal font size.
    heights=[f.getbbox(s)[3]-f.getbbox(s)[1] for s in lines]
    height=sum(heights)+max(0,len(lines)-1)*16
    if height>h: raise ValueError(f'Text overflow {value!r}: {height}>{h}')
    yy=y+(h-height)/2
    bounds=[]
    for s,hh in zip(lines,heights):
        bb=f.getbbox(s); length=f.getlength(s)
        xx=x+(w-length)/2 if align=='center' else x
        draw.text((xx,yy-bb[1]),s,font=f,fill=color)
        bounds.append([xx,yy,xx+length,yy+hh]); yy+=hh+16
    return bounds


def shade(color,factor):
    vals=[int(color[i:i+2],16) for i in (1,3,5)]
    return tuple(min(255,max(0,round(v*factor))) for v in vals)


def valid_point(p):
    site=p.get('site',p.get('xyz'))
    if len(site)!=3 or any(not isinstance(v,int) for v in site):
        raise ValueError('Source coordinates must be three exact integers')
    if 'raw' not in p: raise ValueError('Every physical cell needs its observed RAW')
    # Python integer: uint64 values are never converted to lossy JSON floats.
    value=int(p['raw'])
    if not 0<=value<2**64: raise ValueError('Invalid RAW')
    return site,value


def camera(points,rect,bounds=None,roll_degrees=0,azimuth_degrees=-35,elevation_degrees=27):
    if bounds is None:
        sites=[valid_point(p)[0] for p in points]
        if not sites: raise ValueError('No measured sites: do not invent a world')
        bounds=[[min(p[i] for p in sites)-1 for i in range(3)],
                [max(p[i] for p in sites)+1 for i in range(3)]]
    lo,hi=bounds; center=[(a+b)/2 for a,b in zip(lo,hi)]
    # Fixed oblique orthographic reference. No physical movement implied.
    az,el=math.radians(azimuth_degrees),math.radians(elevation_degrees)
    right=(-math.sin(az),math.cos(az),0)
    up=(-math.sin(el)*math.cos(az),-math.sin(el)*math.sin(az),math.cos(el))
    depth=(math.cos(el)*math.cos(az),math.cos(el)*math.sin(az),math.sin(el))
    roll=math.radians(roll_degrees)
    right,up=tuple(a*math.cos(roll)+b*math.sin(roll) for a,b in zip(right,up)),tuple(-a*math.sin(roll)+b*math.cos(roll) for a,b in zip(right,up))
    def dot(a,b): return sum(x*y for x,y in zip(a,b))
    corners=list(itertools.product(*zip(lo,hi)))
    projected=[(dot([v-c for v,c in zip(p,center)],right),dot([v-c for v,c in zip(p,center)],up)) for p in corners]
    spanx=max(x for x,y in projected)-min(x for x,y in projected)
    spany=max(y for x,y in projected)-min(y for x,y in projected)
    x,y,w,h=rect; scale=min((w-36)/max(1,spanx),(h-36)/max(1,spany))
    def project(p):
        q=[v-c for v,c in zip(p,center)]
        return x+w/2+dot(q,right)*scale,y+h/2-dot(q,up)*scale
    return project,lambda p:dot(p,depth),scale,bounds


def cube(draw,site,project,color,wire=False):
    # Each glyph occupies less than a single source cell. Nothing is enlarged
    # to suggest a physical collision that its source does not contain.
    r=.34; x,y,z=site
    vertices=[project((x+dx*r,y+dy*r,z+dz*r)) for dx,dy,dz in itertools.product((-1,1),repeat=3)]
    faces=((1,3,7,5),(2,3,7,6),(4,5,7,6))
    for face,factor in zip(faces,(1.02,.64,.84)):
        draw.polygon([vertices[i] for i in face],fill=None if wire else shade(color,factor),outline=shade(color,.8))


def dashed(draw,a,b,fill,width=3,dash=12):
    dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
    if not length:return
    for start in range(0,math.ceil(length),dash*2):
        end=min(length,start+dash)
        draw.line((a[0]+dx*start/length,a[1]+dy*start/length,a[0]+dx*end/length,a[1]+dy*end/length),fill=fill,width=width)


def world(draw,panel,rect,bounds=None):
    points=panel['points']; proj,depth,scale,bounds=camera(points,rect,bounds,panel.get('camera_roll_degrees',0),panel.get('camera_azimuth_degrees',-35),panel.get('camera_elevation_degrees',27))
    n=panel['N']
    for p in points:
        site,raw=valid_point(p)
        if any(v<0 or v>=n for v in site):raise ValueError('Point outside its original world')
    for p in sorted(points,key=lambda v:depth(valid_point(v)[0])):
        site,raw=valid_point(p)
        if raw==0:continue
        role=p.get('role','site'); color=COLORS[role]
        cube(draw,site,proj,color,wire=(raw&0xffffffff)==0)
        if site in panel.get('direction_sites',[]) and p.get('direction') and any(p['direction']):
            # Arrow is a field annotation, not motion or a physical carrier.
            end=[v+.8*q for v,q in zip(site,p['direction'])]
            a,b=proj(site),proj(end); dx,dy=b[0]-a[0],b[1]-a[1]
            length=math.hypot(dx,dy)
            if length>2:
                draw.line((*a,*b),fill=COLORS['reader'],width=4)
                ux,uy=dx/length,dy/length
                draw.polygon([b,(b[0]-ux*12-uy*6,b[1]-uy*12+ux*6),(b[0]-ux*12+uy*6,b[1]-uy*12-ux*6)],fill=COLORS['reader'])
    # A frame is a measurement annotation. It is never a luminous particle.
    for kind in ('reader','input','teaching','difference'):
        sites=panel.get(kind+'_sites',[])
        if kind+'_site' in panel:sites=sites+[panel[kind+'_site']]
        for site in sites:
            if len(site)!=3:raise ValueError('Annotation requires measured coordinates')
            x,y=proj(site); radius=max(14,min(38,scale*.68)); c=COLORS[kind]
            for a,b in (((x-radius,y-radius),(x+radius,y-radius)),((x-radius,y-radius),(x-radius,y+radius)),((x+radius,y-radius),(x+radius,y+radius)),((x-radius,y+radius),(x+radius,y+radius))):
                dashed(draw,a,b,c,3,7)
    value_boxes=[]
    for tag in panel.get('value_labels',[]):
        if not tag.get('source_field'):raise ValueError('Numeric label requires its exact recorded field pointer')
        site=tag['site']; xy=proj(site); off=tag.get('offset',[0,-90]); cx,cy=xy[0]+off[0],xy[1]+off[1]
        label=str(tag['text']); f=font(96); width=f.getlength(label)
        # Fit the annotation to this viewport, never displace its source cell.
        cx=max(rect[0]+width/2,min(rect[0]+rect[2]-width/2,cx))
        cy=max(rect[1]+48,min(rect[1]+rect[3]-48,cy))
        dashed(draw,xy,(cx,cy+40),COLORS['control'],2,9)
        value_boxes.extend(text(draw,label,(cx-width/2-4,cy-48,width+8,96),96,max_lines=1))
    return {'source_bounds':bounds,'scale_pixels_per_cell':scale,'point_count':len(points),'N':n,'tick':panel.get('tick'),'value_boxes':value_boxes,'camera_roll_degrees':panel.get('camera_roll_degrees',0),'camera_azimuth_degrees':panel.get('camera_azimuth_degrees',-35),'camera_elevation_degrees':panel.get('camera_elevation_degrees',27)}


def render(model):
    im=Image.new('RGB',(W,H),BACKGROUND); d=ImageDraw.Draw(im)
    boxes=[]
    boxes.extend(text(d,model['title'],(120,72,1680,132),112,max_lines=1))
    panels=model.get('panels',[])
    if len(panels)>2:raise ValueError('At most two comparison panels')
    stats=[]
    if panels:
        shared_bounds=model.get('bounds')
        if len(panels)==2:
            if panels[0]['N']!=panels[1]['N']:raise ValueError('Do not compare different worlds as one geometry')
            if shared_bounds is None:
                allp=panels[0]['points']+panels[1]['points']
                _,_,_,shared_bounds=camera(allp,(120,446,780,354))
            for panel,x in zip(panels,(120,1020)):
                boxes.extend(text(d,panel['label'],(x,230,780,192),96,color=panel.get('label_color',COLORS['reader'])))
                stats.append(world(d,panel,(x,446,780,354),shared_bounds))
                if panel.get('output_text') is not None:
                    # A physical result must be furnished by a source adapter.
                    if not panel.get('reader_evidence'):raise ValueError('Result without source-qualified reader')
                    boxes.extend(text(d,str(panel['output_text']),(x+540,584,220,180),144,max_lines=1))
        elif model.get('scheme',{}).get('kind') in ('bridge','external_service'):
            panel=panels[0]
            boxes.extend(text(d,panel['label'],(120,230,780,192),96))
            stats.append(world(d,panel,(120,446,780,354),shared_bounds))
            if panel.get('output_text') is not None:
                if not panel.get('reader_evidence'):raise ValueError('Result without source-qualified reader')
                boxes.extend(text(d,str(panel['output_text']),(660,580,220,180),144,max_lines=1))
            dashed(d,(960,230),(960,800),COLORS['control'],3,14)
        else:
            panel=panels[0]
            if panel.get('label'):boxes.extend(text(d,panel['label'],(120,230,1680,112),96))
            stats.append(world(d,panel,(120,354,1680,446) if panel.get('label') else (120,230,1680,570),shared_bounds))
            if panel.get('output_text') is not None:
                if not panel.get('reader_evidence'):raise ValueError('Result without source-qualified reader')
                boxes.extend(text(d,str(panel['output_text']),(1500,560,260,190),144,max_lines=1))
    if model.get('scheme'):
        draw_scheme(d,model['scheme'],boxes)
    rep=model['evidence_type']
    if rep not in ('Visualización de registros','Reconstrucción de etapas','Esquema explicativo','Registros y esquema','Etapas y esquema'):
        raise ValueError('Explicit A/B/C designation required')
    if rep in ('Registros y esquema','Etapas y esquema'):
        left='VISUALIZACIÓN DE REGISTROS' if rep=='Registros y esquema' else 'RECONSTRUCCIÓN DE ETAPAS'
        boxes.extend(text(d,left,(120,824,780,72),72,max_lines=1))
        boxes.extend(text(d,'ESQUEMA EXPLICATIVO',(1020,824,780,72),72,max_lines=1))
    else:
        rep_label=rep.upper()+(' · RECORTE AMPLIADO' if model.get('crop_notice') else '')+(' · SALTO TEMPORAL' if model.get('stage_jump') else '')
        boxes.extend(text(d,rep_label,(120,824,1680,72),72,max_lines=1))
    # The bottom180pixels remain empty for optional separate captions.
    if any(b[0]<119 or b[2]>1801 or b[1]<71 or b[3]>897 for b in boxes):
        raise ValueError('Text outside declared safe zones')
    return im,{'text_boxes':boxes,'panels':stats,'evidence_type':rep,'source_data_hash':model.get('source_data_hash')}


def draw_scheme(draw,scheme,boxes):
    """Editorial shapes only, explicitly C. Never interpreted as DEE matter."""
    kind=scheme['kind']
    if kind=='layers':
        labels=scheme['labels']; active=scheme.get('active',0)
        for i,label in enumerate(labels):
            yy=300+i*155; c=COLORS['input'] if i==active else COLORS['control']
            draw.rounded_rectangle((210,yy,1710,yy+120),radius=14,outline=c,width=4)
            if i==active:boxes.extend(text(draw,label,(240,yy+5,1440,110),96,color=c,max_lines=1))
    elif kind=='bridge':
        # The bridge already exists before a response arrives. Its topology
        # is fixed in all frames; the active route is an editorial highlight.
        left=(1005,530); middle=(1080,530); destinations=((1160,390),(1160,690))
        draw.rectangle((left[0]-18,left[1]-18,left[0]+18,left[1]+18),outline=COLORS['reader'],width=4)
        dashed(draw,left,middle,COLORS['control'])
        for j,end in enumerate(destinations):
            c=COLORS['input'] if scheme.get('active')==j else COLORS['control']
            dashed(draw,middle,end,c,width=5)
        for label,y in (('+ : LECTURA ACTUAL',280),('- : MEMORIA',610)):
            boxes.extend(text(draw,label,(1200,y,600,210),96,max_lines=2))
    elif kind=='external_service':
        # An external prepared link, not a model of a robot or DEE anatomy.
        # The source adapter controls which documented step is highlighted.
        draw.rounded_rectangle((1055,420,1780,720),radius=18,outline=COLORS['control'],width=4)
        dashed(draw,(980,570),(1040,570),COLORS['control'],4,12)
        boxes.extend(text(draw,scheme['label'],(1080,440,675,220),96,max_lines=2))
    elif kind=='network':
        pts=[(340+430*k,400+140*j) for k in range(3) for j in range(2)]
        for k in range(2):
            for a in pts[k*2:k*2+2]:
                for b in pts[(k+1)*2:(k+1)*2+2]:
                    draw.line((*a,*b),fill=COLORS['control'],width=scheme.get('weight',5))
        for x,y in pts:draw.rectangle((x-25,y-25,x+25,y+25),fill=COLORS['input'])
        phase=scheme.get('phase',0)%1
        segment=min(1,int(phase*2)); mix=phase*2-segment
        a,b=pts[segment*2],pts[(segment+1)*2]
        x=a[0]+(b[0]-a[0])*mix;y=a[1]+(b[1]-a[1])*mix
        draw.rectangle((x-13,y-13,x+13,y+13),fill=COLORS['teaching'])
    else:raise ValueError('Unknown explicit explanatory scheme')


def data_hash(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
