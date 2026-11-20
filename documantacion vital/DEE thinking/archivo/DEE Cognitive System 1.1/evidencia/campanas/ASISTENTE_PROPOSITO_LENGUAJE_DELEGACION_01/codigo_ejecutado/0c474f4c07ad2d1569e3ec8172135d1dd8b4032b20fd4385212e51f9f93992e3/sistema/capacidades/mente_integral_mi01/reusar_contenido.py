"""Generic material recall of an ALREADY acquired E1 reply into its selector.
No teacher, private magnitude, old snapshot or correct sign is supplied.
Both possible recipient paths receive identical fixed opportunities. This
may MOVE/transform the carrier, not copy its knowledge for free.
"""
from capacidades.integracion_situada_01 import ic_native_core as n
from capacidades.conductos_acceso_aa01 import routes_for_common_arrival
from . import saved,put

def prepare(a,*,name,mode='intact',common=False):
    if mode not in('intact','cut','sham'):raise ValueError('Declared generic recall/cut control')
    cfg=saved(a);records=cfg.setdefault('own_content_recalls',{})
    if name in records:raise ValueError('This recall opportunity already exists; no hidden new memory')
    S=n.configuration(a)['center'];B=list(a.transferred_quantity.geometry['center']);T=3+67*max(0,(a.tick+8-3+66)//67);rr=[];banks=[];starts={};ends={}
    for sign in(-1,1):
        source=n.move(n.move(B,(sign,-1,0),3),(sign,0,1),53);rr.append(n.arrive(a,'MI01.own.'+name+'.genericZ.'+str(sign),source,(0,0,1),T,0))
        p=n.move(source,(sign,0,1),3);banks.append({'sign':sign,'source':source,'turn':p});starts[str(sign)]={'site':p,'direction':[sign,0,1]};ends[str(sign)]={'site':S,'direction':[0,sign,0]}
    routes=routes_for_common_arrival(starts,ends,T+3,phase=29);end=next(iter(routes.values()))['arrival_tick']
    for key,route in routes.items():
        for j,t in enumerate(route['turns']):
            for k,pulse in enumerate(t['pulses']):rr.append(n.arrive(a,'MI01.own.'+name+'.route.'+key+'.'+str(j)+'.'+str(k),t['site'],pulse['direction'],t['tick'],pulse['payload']))
    if mode in('cut','sham'):
        for b in banks:
            site=n.move(b['source'],(b['sign'],0,1),1)
            if mode=='sham':site=n.move(site,(0,1,0),19)
            rr.append(n.submit(a,'MI01.own.'+name+'.formed_cut.'+str(b['sign']),site,(0,0,0),T,0,4))
    if common:rr.append(n.arrive(a,'MI01.own.'+name+'.common',S,(1,0,0),end,0))
    p={'name':name,'prepared_tick':a.tick,'source_tick':T,'banks':banks,'routes':routes,'arrival_tick':end,'S':S,'mode':mode,'common':common,'requests':rr,
      'scope':'Prepared P0 recall opportunities, content from actual stored E1 matter. Not self-initiated repair, readout of an inaccessible code or cloning. Both sign paths fixed before reading them.'};records[name]=p;put(a,cfg);return p

def advance(a,*,name):
    cfg=saved(a);p=cfg['own_content_recalls'][name];events={}
    for key,r in p['routes'].items():
        for i,z in enumerate(r['turns']):
            if a.tick<z['tick']:events.setdefault(z['tick'],[]).append((key,i,z))
    rows=[]
    if a.tick<p['source_tick']:
        a.run_until(p['source_tick']);source=[{'sign':b['sign'],'native':n.obs(a,b['source'])}for b in p['banks']]
    else:source=[]
    for t in sorted(events):
        a.run_until(t);rows.append({'tick':t,'turns':[{'route':key,'index':i,'native':n.obs(a,z['site']),'expected':z}for key,i,z in events[t]]})
    a.run_until(p['arrival_tick']);output=n.obs(a,p['S']);g=n.configuration(a);g['last_selector_tick']=a.tick;n.save(a,g)
    p['last_result']={'tick':a.tick,'output':output};put(a,cfg)
    return{'source':source,'turns':rows,'output':output,'requests':n.receipts(a,p['requests']),'clock_anchor_only_updated':'last_selector_tick identifies this actual physical encounter, not a content or success value'}
