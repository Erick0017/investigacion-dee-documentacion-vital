"""Pure 3D scene models from the archived evidence. No DEE engine is used.

Physical reconstruction is discrete. No interpolated collisions or invented RAW.
The renderer may interpolate its camera, never physical state.
"""
from pathlib import Path
import functools
import gzip
import json
import math
import re

HERE = Path(__file__).resolve().parent
CYAN, AMBER, VIOLET, WHITE = '#46C7EB', '#F4C46B', '#B89BE8', '#E8F4F3'
DIM = '#456477'

@functools.lru_cache(None)
def data():
    return json.loads((HERE / 'datos/evidencia_fundamentos_R05.json').read_text(encoding='utf8'))

@functools.lru_cache(None)
def primary(name):
    p = HERE / 'datos/primarios_historicos_R05' / name
    b = p.read_bytes()
    return json.loads(gzip.decompress(b) if name.endswith('.gz') else b)

def xyz(p, center=(0, 0, 0), scale=1., offset=(0, 0, 0)):
    return [(float(p[i])-center[i])*scale+offset[i] for i in range(3)]

def model(case, tick, representation='Reconstrucción', bounds=((-18, -12, -12), (18, 12, 12))):
    return {'camera': {'eye': [-29, 23, 38], 'target': [0, 0, 0], 'fov': 42},
            'particles': [], 'paths': [], 'arrows': [], 'highlights': [], 'labels': [],
            'screen_labels': [], 'bounds': bounds, 'grid': False,
            'provenance': {'representation': representation, 'case': case, 'tick': str(tick)}}

def ball(m, p, color, label=None, direction=None, radius=.65):
    m['particles'].append({'position': p, 'radius': radius, 'color': color, 'shape': 'sphere'})
    if direction and any(direction):
        m['arrows'].append({'origin': p, 'direction': direction, 'length': 1.25, 'color': color})
    if label:
        m['labels'].append({'text': str(label), 'position': p, 'size': 70, 'offset': [0, -92], 'color': WHITE})

def title(m, text, y=102):
    m['screen_labels'].append({'text': text, 'xy': [960, y], 'size': 60, 'align': 'center', 'color': WHITE})

def focus(m, indices):
    selected={tuple(m['particles'][i]['position']) for i in indices}
    for i,p in enumerate(m['particles']):p['focus']=i in indices
    m['labels']=[l for l in m['labels'] if tuple(l['position']) in selected]

def observed(m, observations, center, scale=1., offset=(0, 0, 0), color=VIOLET, labels=()):
    seen=set()
    for k,o in observations.items():
        if not isinstance(o,dict) or not o.get('site',o.get('coordinate')) or int(o.get('raw',o.get('RAW',0)))==0:
            continue
        point=tuple(o.get('site',o.get('coordinate')))
        if point in seen: continue
        seen.add(point)
        ball(m, xyz(point,center,scale,offset), color, o.get('s_reg') if k in labels else None, o.get('direction'))

def scene03(t):
    """CORE06 fixed recipe and exact local end readings; omitted teaching control."""
    s=data()['scenes']['S03']
    if t < 24:
        if t<8: tick=min(4,int(t/8*5))
        elif t<15: tick=4+min(8,int((t-8)/7*9))
        else: tick=12+min(4,int((t-15)/7*5))
        m=model('CORE06 · consulta nueva +X',f'T{tick}')
        center=(20,26,20)
        if tick<4:
            ball(m,xyz([16+tick,20,20],center),CYAN,'Experiencia: 5' if t<3 else None,[1,0,0])
            ball(m,xyz([24-tick,16+tick,20],center),AMBER,'Docencia: 7' if t<3 else None,[-1,1,0])
            if t>=3:title(m,'Experiencia')
            if t<2:focus(m,[0])
            elif t<4:focus(m,[1])
        elif tick<12:
            ball(m,xyz([20,20+tick-4,20],center),VIOLET,None,[0,1,0])
            title(m,'Relación adquirida')
            tail=[[20,20+j-4,20] for j in range(max(4,tick-3),tick+1)]
            m['paths']=[{'points':[xyz(p,center) for p in tail],'color':VIOLET,'radius':.04,'opacity':.28}]
        elif tick<16:
            ball(m,xyz([20,20+tick-4,20],center),VIOLET,None,[0,1,0])
            ball(m,xyz([16+tick-12,32,20],center),CYAN,'103',[1,0,0])
            title(m,'Nueva entrada')
        else:
            ball(m,xyz([20,32,20],center),WHITE,'115',[1,1,0],.9)
            title(m,'Uso de la experiencia')
        # Motion between specified encounters follows the ballistic recipe on integer ticks.
        m['provenance']['reconstruction_rule']='Initial conditions and straight lattice directions; derived support atT4, local observed result atT16.'
        return m
    tick=min(16,12+int(t-24))
    m=model('CORE06 · enseñanza / omisión',f'T{tick}',bounds=((-24,-10,-10),(24,10,10)))
    m['camera']={'eye':[-26,22,50],'target':[0,0,0],'fov':48}
    if tick<16:
        for side in (-10,10):ball(m,[side+(tick-16)*.8,0,0],CYAN,None,[1,0,0],.9)
        ball(m,[-10,(tick-16)*.8,0],VIOLET,None,[0,1,0],.9)
    else:
        ball(m,[-10,0,0],WHITE,None,[1,1,0],1.15)
        ball(m,[10,0,0],CYAN,None,[1,0,0],1.15)
    m['labels'] += [{'text':'Con experiencia: '+('115' if tick==16 else '103'),'position':[-10,-3,0],'size':64,'offset':[0,38],'color':VIOLET},
                    {'text':'Sin enseñanza: 103','position':[10,-3,0],'size':64,'offset':[0,38],'color':CYAN}]
    m['provenance']['representation']='Registros DEE' if tick==16 else 'Reconstrucción'
    m['provenance']['coverage']='Two independent matched worlds. Discrete query approach is reconstructed; local T16 outcomes are primary. T16 is held briefly for comparison.'
    return m

def g07(t):
    """Two learned mobile supports, discrete documented ballistic reconstruction."""
    if t<5:tick=5+min(5,int(t/5*6))
    elif t<14:tick=10+min(10,int((t-5)/9*11))
    elif t<17:tick=20
    else:tick=10+min(10,int((t-17)/5*11))
    m=model('G07 · dos relaciones aprendidas',f'T{tick}')
    center=(23.5,25,25)
    if tick<13:
        ball(m,xyz([20,20+tick-10,30],center),VIOLET,'+3' if t<5 else None,[0,1,0])
        ball(m,xyz([27,30,20+tick-10],center),VIOLET,'+7',[0,0,1])
        if t>=5: ball(m,xyz([17+tick-10,23,30],center),CYAN,'20',[1,0,0])
        if t<2:focus(m,[0])
        elif t<4:focus(m,[1])
        elif t<5:pass  # One-second orientation of both documented supports.
        else:focus(m,[0,2])
    elif tick<20:
        ball(m,xyz([20+tick-13,23+tick-13,30],center),CYAN,'23',[1,1,0],.85)
        ball(m,xyz([27,30,20+tick-10],center),VIOLET,'+7',[0,0,1])
        m['provenance']['case']='G07 · intermedio23 derivado'
        if 8<=t<11 or 18.5<=t<20.5:focus(m,[0])
    else:
        ball(m,xyz([27,30,30],center),WHITE,'30',[1,1,1],1.)
    if len(m['labels'])<2 and not (2<=t<4):
        title(m,'Relación adquirida' if t<5 else ('Primer encuentro' if tick<13 else ('Resultado en tránsito' if tick<20 else 'Segundo encuentro')))
    m['provenance']['measurement_status']='G07 final30 retained; intermediate23 derived. Both supports formed simultaneouslyT5, earlier than this shot.'
    if t>=17:m['provenance']['case']='G07 · repetición explicativa'
    m['highlights']=[{'position':xyz([20,23,30],center),'radius':.45,'color':DIM,'opacity':.3},
                     {'position':xyz([27,30,30],center),'radius':.45,'color':DIM,'opacity':.3}]
    return m

def m014(t):
    """Two distinct prepared order geometries, sampled actual local records."""
    if t<4:
        index=0 if t<2 else 1
        name=('M014_AB.json','M014_BA.json')[index]
        q=(11,16,19)[min(2,int((t%2)*1.5))]
        event={11:'first_encounter',16:'second_encounter',19:'environment_contact'}[q]
        j=primary(name);sites=j['primary_observations'][event]['sites']
        role=(('A','B')if index==0 else('B','A'))[0 if q==11 else 1]
        key=role+'.meeting' if q!=19 else('bank.V' if index==0 else 'bank.D')
        o=sites[key]
        m=model('M014 · '+('ORDERED_D01_AB' if index==0 else 'ORDERED_D02_BA'),f'T{q}','Registros DEE')
        observed(m,{k:v for k,v in sites.items()if 'backup'not in k and 'nominal'not in k},o['site'],1.,color=VIOLET)
        nearest=min(range(len(m['particles'])),key=lambda i:sum(v*v for v in m['particles'][i]['position']))
        focus(m,[nearest]);m['particles'][nearest]['color']=WHITE
        title(m,'Orden A → B' if index==0 else'Orden B → A')
    else:
        m=model('M014 · dos efectos registrados','T19','Registros DEE')
        for i,name in enumerate(('M014_AB.json','M014_BA.json')):
            j=primary(name);o=j['primary_observations']['environment_contact']['sites']['bank.V' if i==0 else'bank.D']
            p=[-3.5 if i==0 else 3.5,0,0]
            ball(m,p,WHITE,None,o['direction'],1.)
            m['labels'].append({'text':'A → B' if i==0 else'B → A','position':p,'size':56,'offset':[0,180],'color':WHITE})
    m['provenance']['coverage']='Sampled local fields. Prepared order/routing geometries differ; not a permutation control of addition.'
    return m

def scene06(t):
    return g07(t) if t<22 else m014(t-22)

@functools.lru_cache(None)
def actual():
    return json.loads((HERE/'datos/evidencia_actual_R05.json').read_text(encoding='utf8'))

def list_observed(m, items, center, scale=1., color=VIOLET, offset=(0,0,0), radius=.5):
    seen=set()
    for o in items:
        if not o.get('site') or not int(o.get('raw',0)): continue
        p=tuple(o['site'])
        if p in seen: continue
        seen.add(p)
        ball(m,xyz(p,center,scale,offset),color,None,o.get('direction'),radius)

def scene05(t):
    if t<2:
        tick=5+int(t*2)
        m=model('G08 · relación móvil',f'T{tick}')
        ball(m,xyz([20,15+tick-5,20],(20,18,20),1.6),VIOLET,None,[0,1,0],1.)
        title(m,'Una relación conservada')
        return m
    if t<4:
        s=data()['scenes']['S10_CP02']['cases'][0]['emission']['panel_before']['observations']
        m=model('CP02 · soporte relativo','T34','Registros DEE')
        observed(m,{k:s[k] for k in ('A','B')},(22,20,24),3.)
        title(m,'Relación entre componentes')
        return m
    if t<13:
        s=data()['scenes']['S05_ING05'];cut=s['frames'][0 if t<7 else 1]
        m=model('Ingeniería05 · SEPARATED_S0',f'T{cut["tick"]}','Registros DEE')
        for p in cut['points']:
            if int(p['with_history_raw']):
                emphasis=(int(t-4)%3)==(p['xyz'][0]%3)
                col=WHITE if p['raw_different'] and emphasis else(VIOLET if p['raw_different'] else DIM)
                ball(m,xyz(p['xyz'],(11,11,11),1.2),col,radius=.28 if p['raw_different'] else .19)
        title(m,'Historia distribuida')
        m['provenance']['coverage']='Full nonzero RAW sites from archived N23 cut. Violet/dynamic white are grouped editorial highlights of existing difference sites, not physical changes or proven individual memory attribution.'
        return m
    alt=actual()['S05_ALT']
    if t<15:
        m=model('ALT ECI01 · misma trayectoria','T702633 → T713353','Ilustración del mecanismo')
        # A world-volume symbol, not five invented physical memory sites or a simulated wait.
        m['particles'].append({'position':[0,0,0],'radius':3.2,'color':VIOLET,'shape':'cube'})
        title(m,'Salto temporal · 10 720 ticks')
        m['provenance']['coverage']='Editorial symbol of one continuing world and two retained cuts; no intermediate physical frames are generated.'
        return m
    if t>=18:
        s=data()['scenes']['S05_REOPEN']
        if t<20:
            m=model('ECI01_REAPERTURA_P0 · guardar/reabrir','T713886 · sin avance','Ilustración del mecanismo')
            m['particles'].append({'position':[0,0,0],'radius':3.,'color':VIOLET,'shape':'cube'})
            title(m,'Guardar · reabrir el mismo estado')
            m['provenance']['coverage']='Complete state after owner0 equals owner1 start, including RAW/clocks/tick. No animation of physical time during closure.'
        else:
            o=next(x for x in s['reopened_local_observations'] if x['tick']==714153)
            m=model('ECI01_REAPERTURA_P0 · uso posterior','T714153','Registros DEE')
            ball(m,[0,0,0],WHITE,'0',o['direction'],1.1)
            title(m,'Volver a utilizarlo')
            m['provenance']['original_coordinate']=o['site']
            m['provenance']['coverage']='Actual reopened APD05 USE-equilibra7/7 early observation. Nara/MA checks belonged to pre-export ALT, not this reopened fork.'
        return m
    use_nara=True
    label='R07_ALT_nara'
    item=alt[label]['recorded_result']['rows'][0]
    if not use_nara: item=item['result']['rows'][0]
    form='nara' if use_nara else'alfa'
    # The local read is primary; the recorded requests are shown as separate known events.
    native_tick=item['input_tick'] if t-15<.7 else item['read_tick']
    m=model('ALT ECI01 · '+form,f'T{native_tick}','Reconstrucción')
    candidate=item['reader']['candidates'][0]
    center=tuple(candidate['site'])
    if native_tick==item['input_tick']:
        req=next(x for x in item['requests'] if x.get('tick')==native_tick and x.get('site'))
        ball(m,xyz(req['site'],center,2),CYAN,form,req.get('direction'),1.)
    else:
        # Only actual readout sites; no intermediate route is invented.
        obs=[o for o in item['reader']['panel'] if o.get('site')==candidate['site']]
        list_observed(m,obs,center,2,WHITE,radius=1.)
        m['labels'].append({'text':'−','position':[0,0,0],'size':80,'offset':[0,-90],'color':WHITE})
    title(m,'Uso posterior de '+form)
    m['provenance']['coverage']='Known request and local reader frames only, joined by a temporal cut. No replayed or reintroduced teaching.'
    return m

def scene07(t):
    s=data()['scenes']['S07_IC01']
    if t<6:
        m=model('IC01 · información privada de B','T16557 → T16562','Reconstrucción')
        center=(21,59,40)
        # The private input is a functional overlay at B, not invented input microgeometry.
        if t<3:
            ball(m,[-8,4,0],AMBER,'45',radius=1.)
            ball(m,xyz([21,59,40],center,1.5),VIOLET,None,radius=1.2)
            m['provenance']['representation']='Ilustración del mecanismo'
            title(m,'Experiencia privada de B')
        else:
            ball(m,xyz([21,59,40],center,1.5),WHITE,None,[-1,0,0],.75)
            m['provenance']['representation']='Registros DEE'
            m['provenance']['tick']='T16562'
            title(m,'Mensaje formado en B')
        m['provenance']['coverage']='Private value45 is an editorial functional marker; source message atT16562 is recorded, payload7/direction−X.'
        return m
    if t<13:
        fs=s['passive_local_frames'];f=fs[min(len(fs)-1,int((t-6)/7*len(fs)))]
        # All positions are retained local samples. Camera follows observations, not a made-up carrier identity.
        focus=next((o['site'] for o in f['observations'] if o['pointer'].endswith('/read') and o['pointer'].startswith('/0/')),[20,59,40])
        m=model('IC01 · mensaje recibido',f'T{f["tick"]}','Registros DEE')
        list_observed(m,f['observations'],focus,1.7,radius=.7)
        title(m,'Información recibida')
        m['provenance']['coverage']='Local sampled read and context points, not complete global lineage; periodic jumps are kept discrete.'
        return m
    if t<18:
        s=data()['scenes']['S07_CPC9'];fs=[f for f in s['frames'] if f['observations']];f=fs[min(len(fs)-1,int((t-13)/5*len(fs)))]
        m=model('CPC9 · consulta y retorno',f'T{f["tick"]}','Registros DEE')
        list_observed(m,f['observations'],(22,60,43),.9,WHITE,radius=.65)
        title(m,'Consulta · respuesta · uso')
        m['provenance']['coverage']='Different historical realization from IC01. First valid exchange only, not rejected later B updates.'
        return m
    # Return to the actual IC01 subsequent use, not a CPC9 future.
    row=s['subsequent_uses'][-1 if t>=20 else 0]
    m=model('IC01 · uso posterior',f'T{row["tick"]}','Ilustración del mecanismo')
    ball(m,[-6,0,0],VIOLET,'Mensaje −',[-1,0,0],1.2)
    ball(m,[6,0,0],WHITE,'Acción 0',radius=1.2)
    m['provenance']['coverage']='Functional schematic: social−1 with public/nativequantity+1 gives command0 by the declared fixed codec; not a microscopic path.'
    return m

def g08(t):
    if t<2.8: tick=5+min(7,int(t/2.8*8))
    elif t<4.2: tick=12+min(6,int((t-2.8)/1.4*7))
    else: tick=18+min(5,int((t-4.2)/2.8*6))
    m=model('G08 · transferencia funcional',f'T{tick}')
    center=(25,20,20)
    if tick<12:
        ball(m,xyz([20,15+tick-5,20],center),VIOLET,'−5',[0,1,0],.85)
    elif tick<23:
        ball(m,xyz([20+tick-12,22,20],center),VIOLET,'−5',[1,0,0],.85)
        if tick>=18: ball(m,xyz([31,17+tick-18,20],center),CYAN,'4',[0,1,0],.7)
    else:
        ball(m,xyz([31,22,20],center),WHITE,'−1',[1,1,0],1.)
    if len(m['labels'])<2:title(m,'Transferir y utilizar')
    m['provenance']['coverage']='Recipe-based reconstruction; same support redirects at zero-load relayT12, not copied. Final−1 retained.'
    return m

def scene08(t):
    if t<7: return g08(t)
    if t<14:
        s=data()['scenes']['S08_TRANSFER']['T'];i=min(1,int((t-7)/3.5));row=s['rows'][i]
        fs=row['frames'];f=fs[min(len(fs)-1,int(((t-7)%3.5)/3.5*len(fs)))]
        m=model('ENTE02 · otro contexto',f'T{f["tick"]}','Registros DEE')
        items=[o for o in f['observations'] if o['pointer'].startswith(('/own','/sensory_fanin_targets','/context_A','/A'))]
        list_observed(m,items,(6,14,14),2.2,VIOLET,radius=.6)
        title(m,'Reutilizar una referencia')
        m['provenance']['coverage']='EO02 learned relative reference used in the declared external transaction domain. Operator selects domain; fixed bridge, not an autonomous task choice.'
        return m
    s=data()['scenes']['S08_PROTECTION'];q=t-14
    if q<2.5:
        tick=3360+min(2,int(q/2.5*3));m=model('Ciclo02 · contraflujo preparado',f'T{tick}')
        for x in s['prepared_inputs']:
            p=[x['site'][k]+(tick-x['tick'])*x['direction'][k] for k in range(3)]
            ball(m,xyz(p,(21,58,41),1.6),AMBER,None,x['direction'],.7)
        ball(m,xyz([21,59,40],(21,58,41),1.6),VIOLET,None,radius=.8)
        title(m,'Protección preparada de la ruta')
        m['provenance']['coverage']='Exact admitted zero-load counterflow input positions and directions; no invisible shield or host deletion.'
        return m
    fs=[f for f in s['frames'] if f['observations'] and f['tick']>=3420]
    f=fs[min(len(fs)-1,int((q-2.5)/5.5*len(fs)))];m=model('Ciclo02 · comunicación conservada',f'T{f["tick"]}','Registros DEE')
    # Local visualization ROI only; the full two-port observations remain in evidence.
    items=[o for o in f['observations'] if o.get('site')==[31,59,29]]
    list_observed(m,items,(21,59,29),1.5,WHITE,radius=.95)
    title(m,'El mensaje sigue siendo utilizable')
    m['provenance']['coverage']='Local minus-port ROI at (31,59,29); distant generic plus-port omitted from this closeup, full observations preserved. Sampled material social access with committed agenda; prepared protection, not acquired regulation.'
    return m

def scene10(t):
    s=data()['scenes']['S10_CP02'];pair=s['cases'][0];none=s['cases'][1]
    if t<5:
        before=t<2;panel=pair['emission']['panel_before' if before else'panel_after']
        m=model('CP02 · experiencia y emisión',f'T{panel["tick"]}','Registros DEE')
        observed(m,{k:panel['observations'][k]for k in ('A','B','comparator')},(22,20,24),2.3)
        title(m,'Experiencia anterior' if before else'Emisión antes del acontecimiento')
        return m
    if t<8:
        m=model('CP02 · resultado independiente','T37 → T70','Ilustración del mecanismo')
        ball(m,[-8,0,0],WHITE,'Emite T37',[1,0,0],1.)
        ball(m,[8,0,0],CYAN,'Ocurre T70',radius=.8 if t<6 else 1.3)
        m['provenance']['coverage']='Two archived events arranged on an editorial timeline, not a physical trajectory fromT37 toT70. Future habitat packet actually arrives.'
        return m
    if t<14:
        m=model('CP02 · experiencia / omisión','T37','Registros DEE',((-24,-10,-10),(24,10,10)))
        m['camera']={'eye':[-26,22,50],'target':[0,0,0],'fov':48}
        for x,pos in [(pair,[-10,0,0]),(none,[10,0,0])]:
            o=x['emission']['physical_output'];ball(m,pos,WHITE if x['history']=='paired' else CYAN,None,o['direction'],1.)
        m['labels'] += [{'text':'Con experiencia' if t<11 else 'Anticipa llegada','position':[-10,-3,0],'size':48,'offset':[0,38],'color':VIOLET},
                        {'text':'Sin experiencia' if t<11 else 'No distingue','position':[10,-3,0],'size':48,'offset':[0,38],'color':CYAN}]
        m['provenance']['coverage']='Without history the fixed decoder is unresolved{false,true}, not a wrong/absent zero; both futures arrive atT70.'
        return m
    s=data()['scenes']['S10_PENS01'];geom=s['geometry']
    entries=[(6,'consequence_t6',geom['consequence_site'],'Consecuencia material'),
             (12,'U1_t12',geom['program_site'],'Cambio conservado'),
             (38,'U2_t38',geom['action_sites'][0],'Nueva consecuencia'),
             (58,'response3_t58',geom['query_receivers'][2],'Utilización posterior')]
    e=entries[min(3,int((t-14)/1.5))];tick,key,p,heading=e
    m=model('Pensamiento01 · HA_INTACT',f'T{tick}','Registros DEE')
    # Whole archived RAW cuts exist here. Render their actual local context instead of
    # drawing an isolated symbolic product; do not fabricate the missing interval.
    cut=next(x for x in s['physical_cuts'] if x['tick']==tick)
    for point in cut['points']:
        if all(abs(point['xyz'][i]-p[i])<=12 for i in range(3)) and point['xyz']!=p:
            ball(m,xyz(point['xyz'],p),VIOLET,None,radius=.3)
    o=s['measured'][key];ball(m,[0,0,0],WHITE,None,o['direction'],.9)
    m['particles'][-1]['focus']=True
    title(m,heading)
    m['provenance']['original_coordinate']=p
    m['provenance']['coverage']='Actual nonzero RAW sites in a ±12 local window of full archived N127 cutsT6/12/38/58, including state0 when RAWnonzero. Temporal cuts, not invented travel or global lineage. Finite prepared supplies; no postT0 host writes.'
    return m

def fit(m):
    """Uniform camera framing of the displayed protagonists, fixed axis orientation."""
    ps=[p for p in m['particles'] if p.get('focus')] or m['particles']
    if not ps:return m
    lo=[min(p['position'][i]-p.get('radius',.5) for p in ps) for i in range(3)]
    hi=[max(p['position'][i]+p.get('radius',.5) for p in ps) for i in range(3)]
    center=[(lo[i]+hi[i])/2 for i in range(3)]
    # Meetups use their actual ROI, never the complete N-cubed bounding box.
    az,el=math.radians(-35),math.radians(25)
    direction=[math.cos(el)*math.cos(az),math.cos(el)*math.sin(az),math.sin(el)]
    right=[-direction[1],direction[0],0]
    norm=math.hypot(*right);right=[v/norm for v in right]
    up=[direction[1]*right[2]-direction[2]*right[1],direction[2]*right[0]-direction[0]*right[2],direction[0]*right[1]-direction[1]*right[0]]
    corners=[[x-center[0],y-center[1],z-center[2]] for x in(lo[0],hi[0])for y in(lo[1],hi[1])for z in(lo[2],hi[2])]
    dot=lambda a,b:sum(x*y for x,y in zip(a,b))
    tangent=math.tan(math.radians(21))
    distance=max(3.,max(max(abs(dot(p,right))/(tangent*(1920/1080)*.8),abs(dot(p,up))/(tangent*.66))+dot(p,direction)for p in corners))
    m['camera']={'eye':[center[i]+direction[i]*distance for i in range(3)],'target':center,'fov':42,'lens_shift':[.04,.14]}
    m['bounds']=[[lo[i]-4 for i in range(3)],[hi[i]+4 for i in range(3)]]
    floor=lo[2]-1.1
    m['spatial_grid']={'step':1.,'opacity':.105,'plane_z':floor,'verticals':False}
    m['ground']={'z':floor,'opacity':.16}
    m['provenance']['editorial_reference']='Local lattice/ground and encounter rings are graphical spatial references, not new physical matter or connections.'
    # Place short event labels outside the projected sphere, with a leader.
    for l in m['labels']:
        if l['text'].startswith(('Con experiencia:','Sin enseñanza:','A →','B →')):continue
        matches=[p for p in m['particles'] if p['position']==l['position']]
        if not matches:continue
        p=matches[0];delta=[l['position'][i]-center[i] for i in range(3)]
        depth=max(.5,distance-sum(delta[i]*direction[i] for i in range(3)))
        projected_x=998.4+1406.8*sum(delta[i]*right[i] for i in range(3))/depth
        projected_radius=1406.8*p.get('radius',.65)/depth
        halfwidth=len(l['text'])*l.get('size',70)*.29
        side=-1 if projected_x<960 else 1
        l['offset']=[side*max(180,projected_radius+halfwidth+45),-50]
        l['leader']=True
    return m

def frame(scene_id, local_frame):
    t=max(0,int(local_frame))/30.
    if scene_id=='S03': return fit(scene03(t))
    if scene_id=='S05': return fit(scene05(t))
    if scene_id=='S06': return fit(scene06(t))
    if scene_id=='S07': return fit(scene07(t))
    if scene_id=='S08': return fit(scene08(t))
    if scene_id=='S10': return fit(scene10(t))
    raise KeyError('Scene not completed yet: '+str(scene_id))
