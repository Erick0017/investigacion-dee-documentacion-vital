"""Prepared material query circuit. No Python conditional selects the query.

A learned -Y native command follows the request conduit. A +Y command does
not. B alone receives the private raw magnitude. Both content paths have
the same generic resources, and no evaluator sign is used by this module.
"""
from capacidades.integracion_situada_01 import ic_native_core as n,ic_external as ext
from capacidades.conductos_acceso_aa01 import routes_for_common_arrival,turning_inputs
from . import saved,put

def enable_reply_wires(a):
    """Fixed simultaneous wiring of BOTH potential reply fields, no target."""
    B=list(a.transferred_quantity.geometry['center']);bridge=ext.saved(a)
    if not bridge or bridge['readout']!='magnitude':raise ValueError('Existing magnitude bridge required, no silent environment or profile creation')
    ports=list(bridge.get('social_ports',[]));new=[]
    for sign in(-1,1):
        target=n.move(n.move(B,(sign,-1,0),3),(sign,0,1),53)
        if not any(z['target']==target and z['sign']==sign for z in ports):
            b={'sign':sign,'target':target,'access':'MI01_fixed_native_query_return'};ports.append(b);new.append(b)
    bridge['social_ports']=ports;ext.store(a,bridge)
    return {'wires_added':new,'both_contents_wired':True,'native_ticks':0,'no_native_state_edited':True,'scope':'External transduction, not learned anatomy or a learned motor policy. All wire contributions and clipping remain visible.'}

def lift_corridor(route,steps=6):
    """Commute six Z+ steps before the final long X+ leg, same endpoint/time.
    An explicit physical recipe variant, never a host-chosen online repair.
    """
    travel=route['travel'];segments=[]
    start=list(route['turns'][0]['site']);incoming=list(route['turns'][0]['incoming']);t0=route['turns'][0]['tick']
    for z in travel:segments.append((list(z['direction']),z['steps']))
    candidates=[i for i in range(len(segments)-1)if segments[i][0]==[1,0,0]and segments[i][1]>30 and segments[i+1][0]==[0,0,1]and segments[i+1][1]>steps+4]
    if len(candidates)!=1:raise ValueError('Lift6 is admitted only for the identified final long X+/Z+ corridor')
    i=candidates[0];segments[i:i+2]=[([0,0,1],steps),segments[i],([0,0,1],segments[i+1][1]-steps)]
    turns=[];out=[];p=start;t=t0;vin=incoming
    for v,k in segments:
        pulses=turning_inputs(vin,v)
        if pulses:turns.append({'site':p[:],'tick':t,'incoming':vin[:],'outgoing':v[:],'pulses':pulses})
        p=n.move(p,v,k);t+=k;out.append({'site_after':p[:],'tick_after':t,'direction':v[:],'steps':k});vin=v
    if p!=route['destination']or t!=route['arrival_tick']:raise AssertionError('Route variant changed endpoint/clock')
    return{**route,'turns':turns,'travel':out,'route_revision':'lift6_fixed_before_response','prepared_not_learned_avoidance':True}

def prepare(a,*,name,private_value,query_tick=None,drive=True,mode='intact',wire_external=True,route_revision='original',reader_guard=False,late_protection='none'):
    if mode not in('intact','no_command','cut','sham'):raise ValueError('Explicit bounded query/cut control')
    if type(private_value)is not int or not 0<=private_value<=145:raise ValueError('Only actual B private raw magnitude0..145')
    cfg=saved(a);plans=cfg.setdefault('material_queries',{})
    if name in plans:raise ValueError('Query name already declared; never replay its learned state')
    g=n.configuration(a);S=g['center'];q=query_tick
    if q is None:q=g['last_selector_tick']+67*max(1,(a.tick+5-g['last_selector_tick']+66)//67)
    if q<a.tick+4:raise ValueError('Freeze future query opportunities before response; no favorable timing repair')
    B=list(a.transferred_quantity.geometry['center']);rr=[]
    route=routes_for_common_arrival({'q':{'site':n.move(S,(1,-1,0),2),'direction':[1,-1,0]}},{'q':{'site':B,'direction':[0,0,1]}},q+2,phase=13)['q']
    if route_revision not in('original','lift6'):raise ValueError('Explicit route revision required')
    if route_revision=='lift6':route=lift_corridor(route)
    T=route['arrival_tick'];source=T+1;turn=source+3;end=turn+53
    prefix='MI01.query.'+name
    protections=[]
    if late_protection not in('none','corridor','full','sham_ghosts'):raise ValueError('Explicit finite late protection variant')
    if late_protection!='none':
        if S!=[40,35,55]:raise ValueError('Late protection is validated only for the identified extension geometry, not arbitrary organisms')
        when=2+67*max(0,(a.tick+2-2+66)//67)
        site=[66,59,53];pre=n.obs(a,site)
        if not(pre['state']==1 and pre['semantic']==4 and pre['direction']==[0,0,0]):
            r=n.submit(a,prefix+'.late_Z7_interceptor',site,(0,0,0),when,0,4);rr.append(r);protections.append({'role':'identified_corridor_influence','site':site,'tick':when,'request':r,'pre':pre})
        else:protections.append({'role':'identified_corridor_influence','site':site,'existing_support':True,'pre':pre})
    if drive and mode!='no_command':rr.append(n.arrive(a,prefix+'.common',S,(1,0,0),q,5))
    for i,t in enumerate(route['turns']):
        for j,pulse in enumerate(t['pulses']):rr.append(n.arrive(a,prefix+'.turn.'+str(i)+'.'+str(j),t['site'],pulse['direction'],t['tick'],pulse['payload']))
    for port,payload in [('B.quantity.object.cue',5),('B.quantity.object.resource',private_value)]:
        rec=a.world.submit(port,payload,T-5);rr.append({'id':int(rec.id),'port':port,'tick':T-5,'payload':payload})
    banks=[];guards=[]
    for sign in(-1,1):
        P=n.move(B,(sign,-1,0),3);target=n.move(P,(sign,0,1),53)
        if late_protection in('full','sham_ghosts'):
            site=n.move(P,(0,1,1),6)
            if late_protection=='sham_ghosts':site=n.move(site,(1,0,0),19)
            pre=n.obs(a,site)
            if pre['state']==1 and pre['semantic']==4 and pre['direction']==[0,0,0]:protections.append({'role':'association_resource_only_path','site':site,'existing_support':True,'pre':pre})
            else:
                r=n.submit(a,prefix+'.association_ghost_guard.'+str(sign),site,(0,0,0),a.tick,0,4);rr.append(r);protections.append({'role':'association_resource_only_path','site':site,'request':r,'pre':pre})
        for label,vector in [('Y',[0,1,0]),('Z',[0,0,1])]:rr.append(n.arrive(a,prefix+'.assoc.'+str(sign)+'.'+label,P,vector,turn,0))
        rr.append(n.arrive(a,prefix+'.read.'+str(sign),target,(0,0,-1),end,0));banks.append({'sign':sign,'turn':P,'target':target,'access':'native_query_B_return'})
        if reader_guard:
            guard=n.move(target,(0,0,-1),4);pre=n.obs(a,guard)
            if pre['state']==1 and pre['semantic']==4 and pre['direction']==[0,0,0]:guards.append({'site':guard,'reused_native_support':True,'pre':pre})
            else:
                r=n.submit(a,prefix+'.reader_guard.'+str(sign),guard,(0,0,0),a.tick,0,4);rr.append(r);guards.append({'site':guard,'pre':pre,'legal_preparation_request':r,'no_overwrite':True})
    # A legal predeclared interceptor is inserted AFTER the command forms,
    # before it moves to the adjacent site; no field erasure/clock change.
    if mode in('cut','sham'):
        site=n.move(S,(1,-1,0),1)
        if mode=='sham':site=n.move(site,(0,0,1),19)
        rr.append(n.submit(a,prefix+'.interceptor',site,(0,0,0),q,0,4))
    p={'name':name,'prepared_tick':a.tick,'query_tick':q,'comparison_arrival':T,'source_tick':source,'turn_tick':turn,'end_tick':end,'S':S,'B':B,'route':route,'banks':banks,'requests':rr,'drive':drive,'mode':mode,'reader_guard':reader_guard,'reader_guards':guards,'route_revision':route_revision,'late_protection':late_protection,'protections':protections,
       'private_raw_B_only':private_value,'history':[],
       'attribution':'Native command selects request physically; no Python query/answer callback. Common drive, transport, B private sample and reply readers are prepared. NOT a learned missing-information detector or general autonomous inquiry.'}
    plans[name]=p;put(a,cfg)
    if wire_external:
        enable_reply_wires(a)
    return p

def advance(a,*,until):
    if until<a.tick:raise ValueError('No query-life rewind')
    cfg=saved(a);rows=[]
    events={}
    for name,p in cfg.get('material_queries',{}).items():
        for kind,t in [('command',p['query_tick']),('arrival',p['comparison_arrival']),('source',p['source_tick']),('association',p['turn_tick']),('received',p['end_tick'])]:
            if a.tick<t<=until:events.setdefault(t,[]).append((name,kind))
    for tick in sorted(events):
        a.run_until(tick)
        for name,kind in events[tick]:
            p=cfg['material_queries'][name]
            site=p['S']if kind=='command'else p['B']
            row={'name':name,'kind':kind,'tick':tick,'native':n.obs(a,site)}
            if kind in('association','received'):row['banks']=[{'sign':b['sign'],'native':n.obs(a,b['turn']if kind=='association'else b['target'])}for b in p['banks']]
            p['history'].append(row);rows.append(row)
    a.run_until(until);put(a,cfg)
    return{'events':rows,'tick':a.tick,'requests':{name:n.receipts(a,p['requests'])for name,p in cfg.get('material_queries',{}).items()}}
