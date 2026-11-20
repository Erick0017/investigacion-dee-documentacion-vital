"""Prepared material query circuit. No Python conditional selects the query.

A learned -Y native command follows the request conduit. A +Y command does
not. B alone receives the private raw magnitude. Both content paths have
the same generic resources, and no evaluator sign is used by this module.
"""
from capacidades.integracion_situada_01 import ic_native_core as n,ic_external as ext
from capacidades.conductos_acceso_aa01 import routes_for_common_arrival
from . import saved,put

def prepare(a,*,name,private_value,query_tick=None,drive=True,mode='intact',wire_external=True):
    if mode not in('intact','no_command','cut','sham'):raise ValueError('Explicit bounded query/cut control')
    if type(private_value)is not int or not 0<=private_value<=145:raise ValueError('Only actual B private raw magnitude0..145')
    cfg=saved(a);plans=cfg.setdefault('material_queries',{})
    if name in plans:raise ValueError('Query name already declared; never replay its learned state')
    g=n.configuration(a);S=g['center'];q=query_tick
    if q is None:q=g['last_selector_tick']+67*max(1,(a.tick+5-g['last_selector_tick']+66)//67)
    if q<a.tick+4:raise ValueError('Freeze future query opportunities before response; no favorable timing repair')
    B=list(a.transferred_quantity.geometry['center']);rr=[]
    route=routes_for_common_arrival({'q':{'site':n.move(S,(1,-1,0),2),'direction':[1,-1,0]}},{'q':{'site':B,'direction':[0,0,1]}},q+2,phase=13)['q']
    T=route['arrival_tick'];source=T+1;turn=source+3;end=turn+53
    prefix='MI01.query.'+name
    if drive and mode!='no_command':rr.append(n.arrive(a,prefix+'.common',S,(1,0,0),q,5))
    for i,t in enumerate(route['turns']):
        for j,pulse in enumerate(t['pulses']):rr.append(n.arrive(a,prefix+'.turn.'+str(i)+'.'+str(j),t['site'],pulse['direction'],t['tick'],pulse['payload']))
    for port,payload in [('B.quantity.object.cue',5),('B.quantity.object.resource',private_value)]:
        rec=a.world.submit(port,payload,T-5);rr.append({'id':int(rec.id),'port':port,'tick':T-5,'payload':payload})
    banks=[]
    for sign in(-1,1):
        P=n.move(B,(sign,-1,0),3);target=n.move(P,(sign,0,1),53)
        for label,vector in [('Y',[0,1,0]),('Z',[0,0,1])]:rr.append(n.arrive(a,prefix+'.assoc.'+str(sign)+'.'+label,P,vector,turn,0))
        rr.append(n.arrive(a,prefix+'.read.'+str(sign),target,(0,0,-1),end,0));banks.append({'sign':sign,'turn':P,'target':target,'access':'native_query_B_return'})
    # A legal predeclared interceptor is inserted AFTER the command forms,
    # before it moves to the adjacent site; no field erasure/clock change.
    if mode in('cut','sham'):
        site=n.move(S,(1,-1,0),1)
        if mode=='sham':site=n.move(site,(0,0,1),19)
        rr.append(n.submit(a,prefix+'.interceptor',site,(0,0,0),q,0,4))
    p={'name':name,'prepared_tick':a.tick,'query_tick':q,'comparison_arrival':T,'source_tick':source,'turn_tick':turn,'end_tick':end,'S':S,'B':B,'route':route,'banks':banks,'requests':rr,'drive':drive,'mode':mode,
       'private_raw_B_only':private_value,'history':[],
       'attribution':'Native command selects request physically; no Python query/answer callback. Common drive, transport, B private sample and reply readers are prepared. NOT a learned missing-information detector or general autonomous inquiry.'}
    plans[name]=p;put(a,cfg)
    if wire_external:
        bridge=ext.saved(a)
        if not bridge or bridge['readout']!='magnitude':raise ValueError('Existing magnitude bridge required, no silent new environment/profile')
        ports=list(bridge.get('social_ports',[]))
        for b in banks:
            if not any(z['target']==b['target']and z['sign']==b['sign']for z in ports):ports.append({'sign':b['sign'],'target':b['target'],'access':'MI01_fixed_native_query_return'})
        bridge['social_ports']=ports;ext.store(a,bridge)
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
