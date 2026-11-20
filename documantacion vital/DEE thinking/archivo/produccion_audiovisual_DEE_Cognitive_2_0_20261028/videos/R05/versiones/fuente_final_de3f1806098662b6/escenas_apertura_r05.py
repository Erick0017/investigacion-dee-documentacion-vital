"""S01/S02: real-source teasers plus a declared 3D neural-network illustration.

No DEE execution. Source scene callbacks retain their case and representation.
The neural network is an editorial 3-5-3 diagram, never a DEE microstate.
"""
from __future__ import annotations
import copy
import importlib
import math

FPS = 30
CYAN, AMBER, VIOLET, WHITE = '#46C7EB', '#F4C46B', '#B89BE8', '#E8F4F3'


def source_frame(scene, local_frame):
    name = 'escenas_historicas_r05' if scene in {'S03','S05','S06','S07','S08','S10'} else 'escenas_actuales_r05'
    return copy.deepcopy(importlib.import_module(name).frame(scene, int(local_frame)))


def _focus(model, distance=15):
    """Editorial close-up follows existing coordinates without moving matter."""
    points = [row['position'] for row in model.get('particles', [])]
    if not points:
        return model
    center = [sum(row[i] for row in points)/len(points) for i in range(3)]
    spread = max(math.dist(p, center)+float(row.get('radius',.6)) for p,row in zip(points,model['particles']))
    # A close-up must fit its actual protagonists, not retain a15-unit empty box.
    # The optional distance only widens a deliberately broad final view.
    d = max(spread*3.5, 6.6) * (1.12 if distance > 20 else 1)
    az, el = math.radians(-35), math.radians(25)
    direction = [math.cos(el)*math.cos(az),math.cos(el)*math.sin(az),math.sin(el)]
    model['camera'] = {'eye':[v+d*q for v,q in zip(center,direction)],'target':center,'fov':40,'lens_shift':[.04,.10]}
    lo=[min(p[i]-row.get('radius',.6) for p,row in zip(points,model['particles']))-1.5 for i in range(3)]
    hi=[max(p[i]+row.get('radius',.6) for p,row in zip(points,model['particles']))+1.5 for i in range(3)]
    z=min(p[2]-row.get('radius',.6) for p,row in zip(points,model['particles']))-.08
    model['bounds']=[lo,hi]
    model['grid']=False
    model['ground']={'z':z,'opacity':.25,'color':'#102531'}
    model['spatial_grid']={'plane_z':z+.04,'step':1,'opacity':.16}
    model.setdefault('editorial',{})['spatial_reference']='Neutral coordinate floor and cast shadows are editorial references, not DEE matter, interfaces or connections.'
    return model


def scene01(local_frame, callback=source_frame):
    t = local_frame/FPS
    if not 0 <= local_frame < 600:
        raise ValueError('S01 has exactly600 frames')
    if t < 5:
        model = _focus(callback('S03',round((17+t)*FPS)))
        model['screen_labels'] = []
        if .7 <= t < 4.8:
            model['labels'] = []
            model['screen_labels'] = [
                {'text':'DEE Cognitive 2.0','xy':[960,110],'size':70,'color':WHITE},
                {'text':'Inteligencia mediante interacciones','xy':[960,188],'size':54,'color':WHITE}]
    elif t < 10:
        model = _focus(callback('S03',round((2+t-5)*FPS)))
    elif t < 13:
        # The current functional illustration has its own frozen composition.
        model = callback('S04',round((18+t-10)*FPS))
    elif t < 16:
        model = callback('S12',round((15+t-13)*FPS))
    else:
        model = _focus(callback('S03',round((10+t-16)*FPS)),distance=23)
        model['screen_labels'] = []
    model.setdefault('editorial',{})['teaser_source']='Each cut retains the source callback case, history and coordinates. No shared biography is constructed.'
    return model


def network_model(t):
    """Literal conceptual 3-5-3: changing three drawn connection weights."""
    right=[math.sin(math.radians(35)),math.cos(math.radians(35)),0]
    layers=[]
    for col,count in enumerate((3,5,3)):
        layer=[]
        for row in range(count):
            horizontal=(col-1)*10
            layer.append([right[0]*horizontal,right[1]*horizontal,(row-(count-1)/2)*2.5])
        layers.append(layer)
    model={'camera':{'eye':[18,-12.6,10.25],'target':[0,0,0],'fov':40,'lens_shift':[.04,.04]},
           'bounds':[[-12,-12,-6],[12,12,6]],'grid':False,
           'particles':[],'paths':[],'labels':[],'screen_labels':[{'text':'Red neuronal: ajuste de conexiones','xy':[960,115],'size':60,'color':WHITE}],
           'provenance':{'representation':'Ilustración del mecanismo','case':'Red conceptual 3–5–3'}}
    revision=max(0,min(1,(t-7)/3))
    for col in range(2):
        for i,a in enumerate(layers[col]):
            for j,b in enumerate(layers[col+1]):
                selected=(col,i,j) in {(0,0,0),(0,2,3),(1,3,2)}
                model['paths'].append({'points':[a,b],'color':AMBER if selected and revision else '#426579',
                                       'radius':.055+(.15*revision if selected else 0),'opacity':.90 if selected else .45})
    for layer in layers:
        for point in layer:model['particles'].append({'position':point,'radius':.59,'color':VIOLET})
    phase=(t/7 if t<7 else(t-7)/4)*2
    stage=min(1,int(phase));q=max(0,min(1,phase-stage))
    for i in range(3):
        a=layers[stage][i if stage==0 else i+1]
        b=layers[stage+1][i+1 if stage==0 else i]
        model['particles'].append({'position':[x+(y-x)*q for x,y in zip(a,b)],'radius':.30,'color':CYAN})
    return model


def scene02(local_frame, callback=source_frame):
    t=local_frame/FPS
    if not 0 <= local_frame <720:
        raise ValueError('S02 has exactly720 frames')
    # Cue boundaries are fixed by the unchanged Spanish/English narration.
    # At30fps,26.240s maps to globalframe787(26.233333s):6.7ms early.
    #35.325s ->1060(35.333333s);40.666s ->1220(40.666667s).
    dee_first, rules_first, organization_first = 187, 460, 620
    if local_frame < dee_first:
        # Only the explicitly conceptual network animation is retimed.
        return network_model(t*11/(dee_first/FPS))
    if local_frame < rules_first:
        # CORE06 recipe runs forward continuously from sourceframe0 to239.
        source_index=round((local_frame-dee_first)*240/(rules_first-dee_first))
        model=_focus(callback('S03',source_index))
        model['labels']=[]
        model['screen_labels']=[{'text':'DEE: encuentros e historia','xy':[960,115],'size':60,'color':WHITE}]
        return model
    source_index=240+round((local_frame-rules_first)*180/(720-rules_first))
    model=_focus(callback('S03',source_index))
    model['labels']=[]
    model['screen_labels']=[{'text':'Reglas del motor' if local_frame<organization_first else'Organización que cambia','xy':[960,115],'size':60,'color':WHITE}]
    if local_frame>=organization_first:
        model['highlights']=[{'position':p['position'],'radius':max(.8,p.get('radius',.6)*1.4),'color':VIOLET} for p in model.get('particles',[]) if p.get('color')==VIOLET]
    return model


def frame(scene_id, local_frame):
    if scene_id=='S01':return scene01(local_frame)
    if scene_id=='S02':return scene02(local_frame)
    raise KeyError(scene_id)
