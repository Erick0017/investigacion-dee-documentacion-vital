"""R05 models of actual archived ECI observations, zero Native evolution.

Recorded material is placed only at recorded sites/ticks. Unknown passages use
labelled functional illustrations, not invented microscopic trajectories.
Camera movement and pedagogical markers are editorial, never physical lineage.
"""
from pathlib import Path
from functools import lru_cache
import json,math
from renderer_r05 import camera_for_bounds
W=Path(__file__).resolve().parent
C,A,V,O,D='#46C7EB','#F4C46B','#B89BE8','#E8F4F3','#3F5C6A'
@lru_cache(None)
def data():return json.loads((W/'datos/evidencia_actual_R05.json').read_text(encoding='utf8'))
@lru_cache(None)
def old():return json.loads((W/'datos/fragmento_R04_origen.json').read_text(encoding='utf8'))
@lru_cache(None)
def aggregation():return json.loads((W/'datos/agregacion_FI01_R05.json').read_text(encoding='utf8'))
@lru_cache(None)
def continuity():return json.loads((W/'datos/continuidad_publicada_ECI02_R05.json').read_text(encoding='utf8'))
@lru_cache(None)
def alt_actions():return json.loads((W/'datos/actuacion_ALT_R05.json').read_text(encoding='utf8'))
def base(case,rep='Reconstrucción',bounds=((39,3,42),(50,11,52)),tick=''):
    return {'camera':camera_for_bounds(bounds),'bounds':bounds,'grid':False,'particles':[],'paths':[],
            'arrows':[],'highlights':[],'labels':[],'screen_labels':[],
            'provenance':{'representation':rep,'case':case,'tick':str(tick)}}
def label(m,text,pos=None,size=60,xy=(960,112),color=O):
    if pos is None:m['screen_labels'].append({'text':str(text),'xy':list(xy),'size':size,'align':'center','color':color})
    else:m['labels'].append({'text':str(text),'position':list(pos),'size':size,'offset':[0,-210],'color':color})
def ball(m,pos,color=C,r=.65,d=None,shape='sphere',text=None):
    m['particles'].append({'position':list(pos),'radius':r,'color':color,'shape':shape})
    if d and any(d):m['arrows'].append({'origin':list(pos),'direction':list(d),'length':1.9,'color':color})
    if text is not None:label(m,text,pos)
def points(m,rows,color=V,r=.45):
    for row in rows:
        if str(row.get('raw','0'))=='0':continue
        ball(m,row['site'],color if row.get('state',1)>0 else D,r if row.get('state',1)>0 else r*.45,row.get('direction'))
def row(key):return data()[key]['recorded_result']['rows'][0]
def walk(o,key):
    out=[]
    if isinstance(o,dict):
        if key in o:out.append(o[key])
        for k,v in o.items():
            if k not in ('panel','requests','frames','all_material_receipts'):out+=walk(v,key)
    elif isinstance(o,list):
        for v in o:out+=walk(v,key)
    return out
def query_model(r,t,case,title='luma',span=7,bounds=((39,3,42),(50,11,52))):
    r=r.get('word',r)
    q=r['input_tick'];read=r['read_tick'];ticks=[q,q+2,q+3,read]
    phase=min(3,int(max(0,t)/max(.01,span)*4));tick=ticks[phase]
    m=base(case,bounds=bounds,tick='T'+str(tick))
    if phase<3:
        for req in r['requests']:
            if req['tick']==tick and req.get('receipt',{}).get('status')=='applied':
                ball(m,req['site'],C if req['value']==5 else V,.65,req['direction'])
        label(m,title if phase==0 else 'Encuentro preparado')
    else:
        candidates=r['reader']['candidates'];sel={tuple(c['site'])for c in candidates}
        for p in r['reader']['panel']:
            if tuple(p['site'])in sel:ball(m,p['site'],O,.85,p['direction'])
        label(m,'Respuesta '+('+' if r['reader']['formed_native_command']==1 else '−')+'1',next(iter(sel)) if sel else None,size=72)
    return m
def scene04_geometry_archive(t):
    if t<7:return query_model(row('S04_before'),t,'ECI02 · prefijo ALT','luma',7)
    if t<16:
        r=row('S04_teacher');s=t-7;m=base('ECI02 MINUS · revisión',tick='T'+str(r['input_tick'] if s<4 else r['end_tick']))
        if s<4:
            for x in r['requests']:ball(m,x['site'],C if x['value']==5 else A,.55,x['direction'])
            label(m,'Nueva experiencia',xy=(960,112))
            label(m,'luma',r['requests'][0]['site'],size=54)
        else:
            p=r['hub'];ball(m,p['site'],V,.85,p['direction'])
            label(m,'Relación revisada',p['site'])
            # Only the observed hub is shown. The next cut is a later query.
            if s>6.3:label(m,'Misma señal después',xy=(960,112),size=52)
        return m
    if t<24:return query_model(row('S04_after'),t-16,'ECI02 MINUS · misma consulta','luma',8)
    if t<28:
        m=query_model(row('S04_ret_nara'),t-24,'ECI02 MINUS · retención','nara',4,bounds=((42,-1,42),(52,7,52)))
        if t>=27: m['labels']=[];m['screen_labels']=[];label(m,'nara: conservada')
        return m
    r=row('S04_ret_MA')['result']['rows'][0]
    m=query_model(r,t-28,'ECI02 MINUS · memoria posterior','alfa',4,bounds=((31,27,28),(41,39,38)))
    if t>=31:m['labels']=[];m['screen_labels']=[];label(m,'alfa: conservada')
    return m

def association_flow(r,t,span,case,form):
    """Functional 3D reconstruction of a recorded query, no invented micro-route."""
    r=r.get('word',r);sign=r['reader']['formed_native_command'];u=min(1,t/span)
    if u>.88:
        candidates=r['reader']['candidates'];sites={tuple(c['site']) for c in candidates}
        observations=[p for p in r['reader']['panel'] if tuple(p['site'])in sites]
        m=base(case,'Registros DEE',tick='T'+str(r['read_tick']))
        points(m,observations,O,.9)
        if observations:label(m,('+' if sign==1 else '−')+'1',observations[0]['site'],size=78)
        return m
    m=base(case,'Ilustración del mecanismo',((-8,-3,-2),(8,3,4)))
    ball(m,[0,0,0],V,1.45,shape='cube')
    m['paths']=[{'points':[[-6,0,0],[0,0,0],[6,0,0]],'color':D,'radius':.08}]
    if u<.34:
        p=[-6+6*u/.34,0,0];ball(m,p,C,1.05)
        label(m,form,p,size=62);label(m,'Relación adquirida',[0,0,0],size=54)
        m['labels'][0]['offset']=[-230,-210]
        m['labels'][1]['offset']=[230,-175]
    elif u<.56:
        ball(m,[0,0,0],C,.7)
        m['highlights']=[{'position':[0,0,0],'radius':1.9,'color':C}]
        label(m,'La historia interviene')
    else:
        p=[6*(u-.56)/.32,0,0];ball(m,p,O,1.05,d=[0,0,sign])
        label(m,'Respuesta '+('+' if sign==1 else '−')+'1',p,size=66)
    m['provenance']['coverage']='Abstract input → acquired relation → observed sign; original source sites remain in the evidence. The connecting graphic is not a microscopic path.'
    return m

def scene04(t):
    if t<7:return association_flow(row('S04_before'),t,7,'ECI02 · prefijo ALT','luma')
    if t<16:
        s=t-7;r=row('S04_teacher')
        if s>7:
            m=base('ECI02 MINUS · hub observado','Registros DEE',tick='T719851')
            ball(m,r['hub']['site'],V,1,r['hub']['direction']);label(m,'Relación revisada',r['hub']['site'],size=58)
            return m
        m=base('ECI02 MINUS · revisión','Ilustración del mecanismo',((-8,-4,-2),(8,4,4)))
        ball(m,[0,0,0],V,1.45,shape='cube')
        if s<4.5:
            u=s/4.5
            for j,(x,y) in enumerate(((-6,-3),(-6,0),(-6,3))):
                ball(m,[x*(1-u),y*(1-u),.8],C if j==0 else A,1.0)
            label(m,'Nueva experiencia')
            if s<2.2:label(m,'luma',[-6*(1-u),-3*(1-u),.8],size=58)
        else:
            m['highlights']=[{'position':[0,0,0],'radius':1.9,'color':A}]
            ball(m,[0,0,2],O,.9,d=[0,0,-1]);label(m,'Relación revisada')
        return m
    if t<24:return association_flow(row('S04_after'),t-16,8,'ECI02 MINUS · misma señal','luma')
    if t<28:return association_flow(row('S04_ret_nara'),t-24,4,'ECI02 MINUS · nara conservada','nara')
    r=row('S04_ret_MA')['result']['rows'][0]
    return association_flow(r,t-28,4,'ECI02 MINUS · alfa conservada','alfa')

def abstract_access(t):
    # No geometric claim: abstract functional input/support/output nodes.
    m=base('AA46 · acceso aprendido','Ilustración del mecanismo',((-10,-6,-3),(10,6,5)))
    nodes=[[-7,0,0],[0,0,1],[7,0,0]]
    ball(m,nodes[1],V,1.05,shape='cube')
    if t<2.2:
        ball(m,[-7+3*t,0,0],A,.7);label(m,'Enseñar el acceso')
        label(m,'Contenido conservado',nodes[1],size=52)
    elif t<4.5:
        ball(m,[-7+(t-2.2)*2.8,0,0],C,.7);label(m,'Consulta nueva')
        label(m,'Sin reenseñar contenido',xy=(960,190),size=48)
    else:
        p=[min(7,(t-4.5)*2),0,0];ball(m,p,O,.8);label(m,'Información utilizada',p,size=54)
        m['paths']=[{'points':nodes,'color':D,'radius':.05}]
        label(m,'Acceso a memoria',xy=(960,112),size=54)
    return m
def scene09(t):
    if t<9:return abstract_access(t)
    if t<19:
        s=t-9;r=row('S09_neutral');e=r['early_observation'];q=r['query_tick']
        m=base('ECI02 · clase neutra P0','Reconstrucción',((10,11,10),(20,19,20)),tick='q+4' if s<6 else 'q+6')
        if s<6:
            ball(m,e['site'],O,1,e['direction']);label(m,'0 · emisión física',e['site'],size=72)
            label(m,'Lectura temprana',xy=(960,112),size=56)
            # Cursor is explicitly an observer overlay, not interacting matter.
            m['highlights']=[{'position':e['site'],'radius':1.5+.12*math.sin(s*2),'color':C}]
        else:
            # Missing full q6 microgeometry: functional absence, not an invented annihilation.
            m=base('ECI02 · lector histórico','Ilustración del mecanismo',((-7,-5,-2),(7,5,4)),tick='q+6')
            ball(m,[0,0,0],D,1.3,shape='cube');label(m,'Lectura tardía: sin respuesta')
            label(m,'Ausencia ≠ cero',xy=(960,194),size=50)
        return m
    s=t-19;on=data()['S09_probe_on']['captures'];off=data()['S09_probe_off']['captures'];index=(1,2,4,5)[min(3,int(s/9*4))]
    a,b=on[index],off[index];pa={tuple(p['site']):p for p in a['points']};pb={tuple(p['site']):p for p in b['points']}
    changed={p for p in set(pa)|set(pb)if pa.get(p,{}).get('raw','0')!=pb.get(p,{}).get('raw','0')}
    # Two complete observed worlds, shown in a common editorial comparison space.
    m=base('ECI02 R04 · sonda / omisión','Registros DEE',((-14,-10,-5),(14,10,5)),tick='T'+str(a['tick']))
    # Translate both local views along the camera's screen-right vector. No
    # rotation, internal rearrangement or invented matter in either world.
    right=(.573576436,.819152044,0.)
    for rows,side in ((a['points'],-1),(b['points'],1)):
        for p in rows:
            if all(abs(p['site'][i]-[25,13,53][i])<=3 for i in range(3)):
                xyz=[(p['site'][i]-[25,13,53][i])*.9+side*7*right[i] for i in range(3)]
                ball(m,xyz,A if tuple(p['site'])in changed else V,.8,p['direction'])
    label(m,'Con sonda',[-7*x for x in right],size=54);label(m,'Sin sonda',[7*x for x in right],size=54)
    m['provenance']['context']='Changes highlighted from complete buffers. Shared E carrier is not credited to the query.'
    return m

def scene11(t):
    if t<15:
        # A functional causal chain; abstract nodes are not claimed to be native sites.
        m=base('Ciclo02 · consecuencias','Ilustración del mecanismo',((-12,-6,-3),(12,6,6)))
        phase=min(5,int(t/2.5));xs=[-8,0,8]
        ball(m,[0,0,0],V,1.3,shape='cube')
        if phase<2:
            # C: continuous editorial action/environment diagram, not a measured lattice path.
            p=[-8+16*t/5,0,1]
            ball(m,p,O,.8);label(m,'Acción propia')
            if phase==1:label(m,'Consecuencia ambiental',p,size=48)
        elif phase<4:
            p=[8*(1-(t-5)/5),0,1];ball(m,p,A,.85);label(m,'Consecuencia vuelve')
            label(m,'Referencia: 5 → 11',[0,0,0],size=56)
        else:
            real=old()['cycle02']['cases']['C02_GATE_050_RETORNO']['rows'][1]
            omit=old()['cycle02']['cases']['C02_GATE_051_SIN_RETORNO']['rows'][1]
            assert real['native_action']==-1 and omit['native_action']==1
            ball(m,[-6,0,0],V,1,d=[0,0,-1]);ball(m,[6,0,0],A,1,d=[0,0,1])
            label(m,'Con retorno: evita',[-6,0,0],size=52)
            label(m,'Sin retorno: insiste',[6,0,0],size=52)
            m['provenance']['case']='Ciclo02 · retorno / omisión'
        return m
    s=t-15;phase=min(2,int(s/3));loads=((8,4),(7,5),(6,6))[phase]
    m=base('ECI01 ALT · entorno acoplado','Ilustración del mecanismo',((-13,-7,-3),(13,7,7)))
    m['boxes']=[{'position':[.6,0,0],'scale':[17,9,5],'color':C,'opacity':.035}]
    # A sphere outside the load enclosure is the DEE command; cubes are external units.
    ball(m,[-10,5,1.5],O,.75,d=[1,0,0] if phase<2 else [0,0,0])
    # Twelve external load units are conserved during each fixed transduction.
    # The moving cube is removed from its origin, not added as a thirteenth unit.
    for side,n in ((-1,loads[0]),(1,loads[1])):
        for i in range(n):
            if phase<2 and side==-1 and i==n-1:continue
            ball(m,[side*6+(i%2)*1.2,(i//2)*1.2-2,0],C if side<0 else V,.45,shape='cube')
    if phase<2:
        u=(s%3)/3;ball(m,[-6+12*u,4,2],O,.45,shape='cube')
        label(m,str(loads[0])+' / '+str(loads[1]),size=76)
        label(m,'Entorno externo · transducción fija',xy=(960,196),size=48)
    else:
        label(m,'6 / 6 · HOLD',size=76)
        label(m,'Acción neutra explícita',xy=(960,196),size=52)
    return m

def scene12(t):
    if t<14:
        ag=aggregation();ag=ag.get('aggregate128',ag)
        pair=ag['pair'];case='ref_sham_zero' if t<4 else 'ref_sham_two'
        rec=pair[case];inputs=rec['geometry']['raw_sources']
        assert len(inputs)==128
        bounds=((0,0,0),(66,66,66));m=base('FI01 · '+('control cero' if t<4 else 'un componente cambia'),'Reconstrucción',bounds)
        sites=[r['site'] for r in inputs]
        lo=[min(p[i]for p in sites)-2 for i in range(3)];hi=[max(p[i]for p in sites)+2 for i in range(3)]
        m['camera']=camera_for_bounds([lo,hi]);m['bounds']=[lo,hi]
        if t<8:
            selected=list(enumerate(inputs))
            if t>=4:
                # Editorial local view of the intervention, retaining exact source coordinates.
                origin=inputs[0]['site']
                selected=sorted(selected,key=lambda item:sum((item[1]['site'][k]-origin[k])**2 for k in range(3)))[:6]
                m['provenance']['case']='FI01 · componente intervenido · vista local'
                m['provenance']['ROI']='Six nearest recorded input sites to component0; full128-source geometry remains in data and in preceding shot.'
            for i,r in selected:ball(m,r['site'],A if i==0 and t>=4 else C,.95 if i==0 and t>=4 else .52,r.get('direction'))
            if t<4:label(m,'128 componentes que contribuyen',size=60)
            else:label(m,'Un componente: 0 → 2',inputs[0]['site'],size=60)
        elif t<11:
            samples=rec['frames'];f=samples[min(len(samples)-1,int((t-8)/3*len(samples)))]
            fields=[x for x in f['fields'].values()if isinstance(x,dict)and x.get('site')]
            unique={tuple(x['site']):x for x in fields if str(x.get('raw','0'))!='0'}
            m=base('FI01 · contribución registrada','Registros DEE',((8,8,8),(61,61,61)),tick='T'+str(f['tick']))
            shown=list(unique.values())
            if len(shown)>2 and max(max(x['site'][k] for x in shown)-min(x['site'][k] for x in shown) for k in range(3))>12:
                # A local pair from this exact retained frame; no inferred ancestry or new trajectory.
                pairs=[(a,b) for i,a in enumerate(shown) for b in shown[i+1:]]
                a,b=min(pairs,key=lambda pair:sum((pair[0]['site'][k]-pair[1]['site'][k])**2 for k in range(3)))
                shown=[a,b]
                m['provenance']['case']='FI01 · contribución registrada · vista local'
                m['provenance']['ROI']='Closest pair of distinct retained sites in this frame; distant retained sites are outside this displayed ROI, not removed from data.'
            points(m,shown,C,.65)
            label(m,'Contribución registrada')
        else:
            m=base('FI01 · control / intervención','Registros DEE',((-12,-5,-3),(12,5,5)),tick='T16702')
            # Two recorded reader outcomes in an explicitly paired editorial layout.
            ball(m,[-7,0,0],C,1,d=[-1,1,0]);ball(m,[7,0,0],O,1,d=[1,1,-1])
            label(m,'Control: −1',[-7,0,0],size=68);label(m,'Un cambio: +1',[7,0,0],size=68)
            m['provenance']['comparison_layout']='Reader positions translated uniformly within separate labelled views; exact original positions in data.'
        return m
    s=t-14;v=data()['S12_W11'];frames=v['captures'];f=frames[min(len(frames)-1,int(s/8*len(frames)))]
    m=base('ECI02 W11 · un mundo','Registros DEE',((8,9,8),(44,40,40)),tick='T'+str(f['tick']))
    # Full captured nonzeroRAW state, not just nominal ports. Values remain strings in data.
    for p in f['points']:
        nearMA=sum((p['site'][i]-[35,33,33][i])**2 for i in range(3))<160
        nearFI=sum((p['site'][i]-[15,15,15][i])**2 for i in range(3))<160
        if nearMA or nearFI:ball(m,p['site'],V if nearMA else C,.7,p['direction'])
    if s<8:
        label(m,'Memoria',[35,33,33],size=60);label(m,'Comparación',[15,15,15],size=60)
    else:
        key='S12_W11_afterMA' if s<10 else 'S12_W11_afterFI'
        r=data()[key]['recorded_result'];readers=[x for x in walk(r,'reader') if isinstance(x,dict)and x.get('candidates')]
        if key.endswith('afterFI'):
            e=r['rows'][0]['early_observation'];readers=[{'panel':[e],'candidates':[{'site':e['site']}]}]
        m['particles']=[];m['arrows']=[]
        rr=readers[-1] if readers else None
        if rr:
            sites={tuple(x.get('site',x.get('observation',{}).get('site')))for x in rr['candidates']}
            selected=[p for p in rr.get('panel',rr.get('observations',[])) if tuple(p['site'])in sites]
            for p in selected:ball(m,p['site'],O,.85,p['direction'])
            if selected:
                c=selected[0]['site'];b=[[c[i]-4 for i in range(3)],[c[i]+4 for i in range(3)]]
                m['camera']=camera_for_bounds(b);m['bounds']=b
        label(m,'Memoria: uso posterior' if s<10 else 'Comparación: uso posterior')
    m['provenance']['material_intervals']={'MA':[719915,719922],'FI':[719861,719923]}
    return m

def scene13(t):
    if t<6:return query_model(row('S04_before'),t,'ECI02 · asociación luma','luma',6)
    if t<14:
        s=t-6;minus=s>=4;r=row('S04_after') if minus else row('S13_plus')
        word=r['word'];sign=word['reader']['formed_native_command']
        m=base('ECI02 MINUS' if minus else 'ECI02 PLUS','Ilustración del mecanismo',((-14,-6,-3),(14,6,5)))
        ball(m,[-9,0,0],V,1,d=[0,0,sign]);ball(m,[8,0,0],C,.95,shape='cube')
        p=[-8+16*((s%4)/4),0,1];ball(m,p,O,.7)
        m['paths']=[{'points':[[-7,0,0],[7,0,0]],'color':D,'radius':.07}]
        m['planes']=[{'position':[0,0,0],'scale':[.13,6,6],'color':O,'opacity':.16}]
        label(m,'Conexión preparada',xy=(960,112),size=56)
        label(m,'MA: memoria' if minus else 'MU: comparación',[8,0,0],size=56)
        return m
    r=row('S04_after')['interaction'];m=query_model(r,t-14,'ECI02 MINUS · uso de MA','alfa',8,bounds=((31,27,28),(41,39,38)))
    return m

def scene14(t):
    if t<7:
        # ExistingAPD03 recipe/events, not a new scenario.
        a=old()['apd03']['events'][0];phase=min(3,int(t/1.75))
        if phase<2:
            m=base('APD03 MAIN · misma trayectoria','Reconstrucción',((39,0,42),(51,12,52)))
            lesson=a['lessons'][phase];h=lesson['acquired_hub'];ball(m,h['site'],A,.85,h['direction'])
            label(m,'Adquiere '+lesson['form'])
        else:
            use=a['first_uses'][phase-2]
            m=base('APD03 MAIN · uso posterior','Ilustración del mecanismo',((-10,-5,-3),(10,5,4)),tick='T'+str(use['interaction_tick']))
            ball(m,[-6,0,0],V,.9,d=[0,0,use['word_sign']]);ball(m,[6,0,0],O,.9,d=[0,0,use['interaction_response_sign']])
            label(m,'luma → comparación' if phase==2 else 'nara → memoria')
        return m
    if t<14:
        s=t-7;m=base('ECI02 · operaciones directas','Ilustración del mecanismo',((-16,-6,-3),(16,6,6)))
        if s<2.2:
            ball(m,[-10,0,0],C,.9);ball(m,[0,0,0],V,1.1,shape='cube');label(m,'8 + 3',[-10,0,0],size=76)
            label(m,'11',[0,0,0],size=76)
        elif s<4.7:
            p=[(s-2.2)/2.5*9,0,1];ball(m,p,O,.9);ball(m,[10,0,0],V,1.1,shape='cube')
            label(m,'11',p,size=76);label(m,'Enlace preparado',xy=(960,112),size=54)
        else:
            ball(m,[10,0,0],O,1.1);label(m,'11 − 4 = 7',[10,0,0],size=76)
        return m
    s=t-14;case=continuity()['sources'][1]
    m=base('Otro caso: ECI02 MINUS','Ilustración del mecanismo',((-9,-6,-3),(9,6,6)),tick='T720458')
    if s<4:
        # Paired-save/reopen of the same complete MINUS microstate, not a new emission.
        for p in ((-4,0,0),(0,0,2),(4,0,0)):ball(m,p,V,.9,shape='cube')
        label(m,'Estado completo guardado' if s<2 else 'Mismo estado reabierto')
    else:
        interaction=case['cycles'][1]['recorded_result']['rows'][0]['interaction']
        m=query_model(interaction,(s-4)*3,'ECI02 MINUS · tras reabrir','alfa',6,bounds=((31,27,28),(41,39,38)))
        if s>=5.5:
            m['labels']=[];m['screen_labels']=[];label(m,'Memoria utilizada después')
    return m

def scene15(t):
    if t<6:
        m=base('Plataforma DEE','Ilustración del mecanismo',((-13,-8,-5),(13,8,8)))
        for z,c in ((-3,D),(0,C),(3,V)):
            for x in(-6,0,6):ball(m,[x,0,z],c,.7,shape='cube')
        if t<2:label(m,'Motor')
        elif t<4:label(m,'Herramientas')
        else:label(m,'Organizaciones con historia')
        return m
    if t<13:
        if t<8.4:m=scene04(18+(t-6)*1.5)
        elif t<10.8:
            from escenas_historicas_r05 import frame
            m=frame('S07',int(30*(9+(t-8.4)*2)))
        else:m=scene12(16+(t-10.8)*2)
        m['labels']=[];m['screen_labels']=[];label(m,'Líneas de desarrollo')
        return m
    from escenas_historicas_r05 import frame
    m=frame('S03',int(30*(15+(t-13)*1.2)))
    m['labels']=[];m['screen_labels']=[]
    label(m,'DEE Cognitive 2.0',xy=(960,135),size=72)
    label(m,'Puebla, México · Colaboremos',xy=(960,232),size=52)
    return m

def focus_visible(m):
    """Editorial closeup from the displayed geometry, never a DEE observer."""
    p=m.get('particles',[])
    if not p:return m
    lo=[min(x['position'][i]-x.get('radius',.6)for x in p)for i in range(3)]
    hi=[max(x['position'][i]+x.get('radius',.6)for x in p)for i in range(3)]
    for i in range(3):
        center=(lo[i]+hi[i])/2;half=max(1.65,(hi[i]-lo[i])/2+.65);lo[i]=center-half;hi[i]=center+half
    # A spatial wire enclosure is a scale reference, not additional matter.
    m['bounds']=[lo,hi];m['camera']=camera_for_bounds([lo,hi],fill=.83);m['grid']=True
    m['spatial_grid']={'step':max(.5,(hi[0]-lo[0])/12),'plane_z':lo[2],'opacity':.12,'verticals':True}
    m['ground']={'z':lo[2]-.15,'opacity':.18,'color':'#102531'}
    m['provenance']['editorial_focus']='Camera and wireframe crop only. Particle source coordinates remain unchanged; marker radii are graphical glyph sizes.'
    return m

SCENES={'S04':scene04,'S09':scene09,'S11':scene11,'S12':scene12,'S13':scene13,'S14':scene14,'S15':scene15}
def frame(scene_id,local_frame):return focus_visible(SCENES[scene_id](local_frame/30))
