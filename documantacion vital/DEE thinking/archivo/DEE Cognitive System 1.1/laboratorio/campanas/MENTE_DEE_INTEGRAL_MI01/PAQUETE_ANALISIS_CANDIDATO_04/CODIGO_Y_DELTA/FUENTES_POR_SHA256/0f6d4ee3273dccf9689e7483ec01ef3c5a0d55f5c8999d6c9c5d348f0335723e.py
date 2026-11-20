"""Experimental native content return to the SAME decision support.
Fixed anatomy can make a private reply alter a subsequent command. This is
not a learned policy law and does not clone the original recipient message.
"""
from capacidades.integracion_situada_01 import ic_native_core as n
from capacidades.conductos_acceso_aa01 import routes_for_common_arrival
from . import saved,put

def prepare(a,*,query_name,name,mode='intact',common=True):
    if mode not in('intact','omit','cut','sham'):raise ValueError('Declared reply-to-selector contrast required')
    cfg=saved(a);p=cfg.get('material_queries',{}).get(query_name)
    if p is None:raise ValueError('Existing future native material query required; no source content supplied here')
    returns=cfg.setdefault('selector_returns',{})
    if name in returns:raise ValueError('Return already prepared, no hidden renewal')
    t=p['turn_tick']+3;S=p['S'];starts={};ends={};rr=[]
    for b in p['banks']:
        sign=b['sign'];starts[str(sign)]={'site':n.move(b['turn'],(sign,0,1),3),'direction':[sign,0,1]};ends[str(sign)]={'site':S,'direction':[0,sign,0]}
    routes=routes_for_common_arrival(starts,ends,t,phase=29)
    arrival=next(iter(routes.values()))['arrival_tick'];prefix='MI01.return.'+name
    if mode!='omit':
        for key,route in routes.items():
            for i,turn in enumerate(route['turns']):
                for j,pulse in enumerate(turn['pulses']):rr.append(n.arrive(a,prefix+'.'+key+'.'+str(i)+'.'+str(j),turn['site'],pulse['direction'],turn['tick'],pulse['payload']))
    if mode in('cut','sham'):
        for b in p['banks']:
            site=n.move(b['turn'],(b['sign'],0,1),1)
            if mode=='sham':site=n.move(site,(0,1,0),19)
            rr.append(n.submit(a,prefix+'.postformed.'+str(b['sign']),site,(0,0,0),p['turn_tick'],0,4))
    if common:rr.append(n.arrive(a,prefix+'.generic_next_command',S,(1,0,0),arrival,0))
    record={'name':name,'query_name':query_name,'source_tick':t,'arrival_tick':arrival,'S':S,'routes':routes,'mode':mode,'common':common,'requests':rr,
      'assistance':'All possible content routes, fixed generic query and transformation law prepared before B responds. No private sign/expected action inspected by host.',
      'tradeoff':'These turn opportunities can divert the actual reply away from its original recipient route. No claim that the same matter supplies both destinations.',
      'history':[]}
    returns[name]=record;put(a,cfg);return record

def advance(a,*,name):
    cfg=saved(a);p=cfg['selector_returns'][name];events={}
    for key,route in p['routes'].items():
        for i,turn in enumerate(route['turns']):
            if turn['tick']>a.tick:events.setdefault(turn['tick'],[]).append((key,i,turn))
    rows=[]
    for t in sorted(events):
        a.run_until(t)
        rows.append({'tick':t,'turns':[{'route':key,'index':i,'expected':z,'native':n.obs(a,z['site'])}for key,i,z in events[t]]})
    a.run_until(p['arrival_tick']);output=n.obs(a,p['S']);p['history'].append({'tick':a.tick,'output':output});put(a,cfg)
    return{'turns':rows,'output':output,'requests':n.receipts(a,p['requests']),'scope':'Measured reply-to-decision circuit. A fixed transformation with learned content is not itself a learned strategy.'}
