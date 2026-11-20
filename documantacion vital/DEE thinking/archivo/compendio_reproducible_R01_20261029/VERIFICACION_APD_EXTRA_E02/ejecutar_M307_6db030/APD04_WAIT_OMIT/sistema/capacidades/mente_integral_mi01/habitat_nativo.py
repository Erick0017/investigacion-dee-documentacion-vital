"""Finite shared-world query/action/consequence candidate, entirely v27.

Preparation installs all possible opportunities before responses. Execution
only advances the existing owner and observes. No Python branch selects an
action, reader or a successful source. Environmental availability is a fixed
physical perturbation, not an E1 answer. Utility is calculated by the auditor.
"""
from capacidades.integracion_situada_01 import ic_native_core as n
from capacidades.conductos_acceso_aa01 import path_variants,turning_inputs
from app.native_tools import physical
from . import saved,put,material_command
from . import consulta_nativa as query,retorno_selector as reply

def exact_route(start,end,t0,arrival,allow_prestage=True):
    candidates=[];vin=start['direction']
    for path in path_variants(start['site'],end['site'],end['direction']):
        base=sum(k for v,k in path);extra=arrival-t0-base
        triangle=[]
        if extra%2:
            # Odd33-step closed pentagon, all turns have distinct-source
            # conditional native realizations. A triangular135degree turn
            # failed the existing no-aligned-ghost compiler and is NOT used.
            triangle=[([1,0,0],6),([1,0,1],5),([-1,0,1],6),([-1,0,0],5),([0,0,-1],11)];extra-=33
        if extra<20 or extra>264:continue
        for h in range(5,67):
            w=extra//2-h
            if not 5<=w<=66:continue
            prefix=[([1,0,0],w),([0,0,1],h),([-1,0,0],w),([0,0,-1],h)]if triangle or vin==[0,0,-1]else[([0,0,1],h),([1,0,0],w),([0,0,-1],h),([-1,0,0],w)]
            full=triangle+prefix+path;prior=vin
            try:
                for v,k in full:turning_inputs(prior,v);prior=v
            except ValueError:continue
            candidates.append((max(h,w),abs(h-w),base,full))
    if not candidates:
        if allow_prestage:
            # A pure180degree two-resource turn is not silently invented.
            # Use an explicit orthogonal final approach and five final steps.
            final=end['direction'];pre={'site':n.move(end['site'],final,-5)}
            for direction in([1,0,0],[-1,0,0],[0,0,1],[0,0,-1]):
                try:
                    r=exact_route(start,{**pre,'direction':direction},t0,arrival-5,False);pulses=turning_inputs(direction,final)
                except ValueError:continue
                if pulses:r['turns'].append({'site':pre['site'],'tick':arrival-5,'incoming':direction,'outgoing':final,'pulses':pulses})
                r['travel'].append({'site_after':end['site'],'tick_after':arrival,'direction':final,'steps':5});r.update(destination=end['site'],arrival_tick=arrival,orthogonal_final_approach=True)
                return r
        raise ValueError('No finite exact native route at the declared opportunity clock')
    selected=min(candidates,key=lambda z:z[:3])[-1];p=list(start['site']);t=t0;prior=list(vin);turns=[];travel=[]
    for v,k in selected:
        pulses=turning_inputs(prior,v)
        if pulses:turns.append({'site':p[:],'tick':t,'incoming':prior[:],'outgoing':list(v),'pulses':pulses})
        p=n.move(p,v,k);t+=k;travel.append({'site_after':p[:],'tick_after':t,'direction':list(v),'steps':k});prior=list(v)
    if p!=end['site']or t!=arrival:raise AssertionError('Physical route geometry/clock mismatch')
    return{'turns':turns,'travel':travel,'destination':p,'arrival_tick':t,'prepared_geometry_not_learned_policy':True}

def prepare(a,*,name,availability,private_values,mode='intact',actor_ghost_guards=True):
    if mode not in('intact','omit_actor_return','cut_actor','cut_question','sham_actor'):raise ValueError('Declared finite habitat contrast')
    if not 2<=len(availability)<=16 or len(availability)!=len(private_values)or any(v not in(-1,1)for v in availability):raise ValueError('2..16 fixed opportunities, actual physical route condition+/-1')
    cfg=saved(a);bodies=cfg.setdefault('native_habitats',{})
    if name in bodies:raise ValueError('This lived native habitat already exists; continue it, do not restart')
    g=n.configuration(a);S=g['center']
    if S!=[40,35,55]:raise ValueError('MI01 candidate is explicitly the late extension40 geometry')
    first=g['last_selector_tick']+67*max(1,(a.tick+5-g['last_selector_tick']+66)//67)
    qperiod=335;plans=[];extra=[];fixtures=set()
    # Freeze every service opportunity and BOTH possible private-content return
    # paths before measuring the first command. No branch reads E1 outputs.
    for i,(available,private)in enumerate(zip(availability,private_values)):
        q=first+qperiod*i;arrival=q+qperiod
        p=query.prepare(a,name=name+'.Q'+str(i),private_value=private,query_tick=q,drive=i==0,mode='cut'if mode=='cut_question'else'intact',wire_external=False,reader_guard=True,late_protection='full')
        r=reply.prepare(a,query_name=p['name'],name=name+'.R'+str(i),common=False,phase=29,ghost_guard='local')
        if r['arrival_tick']!=arrival:raise ValueError('The selected query/return geometry changed its335tick domain')
        if i>0:extra.append(n.arrive(a,'MI01.habitat.'+name+'.common.'+str(i),S,(1,0,0),q,0))
        P=n.move(S,(1,1,0),4);sigma=1 if available==1 else-1
        contact={'site':P,'tick':q+4,'incoming':[1,1,0],'outgoing':[sigma,1,0],'pulses':turning_inputs((1,1,0),(sigma,1,0))}
        for j,pulse in enumerate(contact['pulses']):extra.append(n.arrive(a,'MI01.habitat.'+name+'.condition.'+str(i)+'.'+str(j),P,pulse['direction'],q+4,pulse['payload']))
        source={'site':n.move(P,(sigma,1,0),4),'direction':[sigma,1,0]};end={'site':S,'direction':[0,sigma,0]}
        route=exact_route(source,end,q+8,arrival)
        if mode!='omit_actor_return':
            for j,turn in enumerate(route['turns']):
                for k,pulse in enumerate(turn['pulses']):extra.append(n.arrive(a,'MI01.habitat.'+name+'.consequence.'+str(i)+'.'+str(j)+'.'+str(k),turn['site'],pulse['direction'],turn['tick'],pulse['payload']))
                if actor_ghost_guards:
                    sums=[sum(v['direction'][axis]for v in turn['pulses'])for axis in range(3)];ghost=[(x>0)-(x<0)for x in sums]
                    if any(ghost)and ghost!=turn['outgoing']:
                        site=n.move(turn['site'],ghost,4);key=tuple(site)
                        if key not in fixtures:
                            fixtures.add(key);extra.append(n.submit(a,'MI01.habitat.'+name+'.ghost_fixture.'+str(len(fixtures)),site,(0,0,0),turn['tick']+2,0,4))
        if i==1 and mode in('cut_actor','sham_actor'):
            site=n.move(S,(1,1,0),2)
            if mode=='sham_actor':site=n.move(site,(0,0,1),19)
            extra.append(n.submit(a,'MI01.habitat.'+name+'.postformed_actor',site,(0,0,0),q+1,0,4))
        plans.append({'index':i,'query_tick':q,'return_tick':arrival,'availability':available,'private_B_raw':private,'query_name':p['name'],'reply_name':r['name'],'contact':contact,'actor_source':source,'actor_return':route})
    # One final common opportunity exposes the last consequence; no next answer
    # is taught or generated. Afterwards the finite agenda is allowed to drain.
    extra.append(n.arrive(a,'MI01.habitat.'+name+'.last_common',S,(1,0,0),plans[-1]['return_tick'],0))
    cfg=saved(a);cfg.setdefault('native_habitats',{})[name]={'name':name,'start_tick':a.tick,'S':S,'period':qperiod,'mode':mode,'actor_ghost_guards':actor_ghost_guards,'plans':plans,'extra_requests':extra,'end_tick':plans[-1]['return_tick'],'last_observed_tick':a.tick,'frames':[],
       'prepared':'Mutable directional state, routes, fixed opportunity clock, native conditional physical contact and bidirectional service conduits. These are not invented by E1.',
       'acquired':'Only actual experience-dependent native content/selection and later transformations. No environmental utility/desired action is supplied to E1.'}
    put(a,cfg);return cfg['native_habitats'][name]

def advance(a,*,name,until=None,record=True):
    cfg=saved(a);p=cfg['native_habitats'][name];until=p['end_tick']if until is None else until
    if until<a.tick:raise ValueError('No native habitat rewind')
    events={}
    def event(t,kind,index):
        if a.tick<t<=until:events.setdefault(t,[]).append((kind,index))
    for z in p['plans']:
        i=z['index'];event(z['query_tick'],'command',i);event(z['query_tick']+4,'contact',i);event(z['query_tick']+8,'actor_source',i);event(z['return_tick'],'returned',i)
        qp=cfg['material_queries'][z['query_name']]
        for key in('comparison_arrival','source_tick','turn_tick','end_tick'):event(qp[key],key,i)
    rows=[]
    for t in sorted(events):
        a.run_until(t)
        if record:
            for kind,i in events[t]:
                z=p['plans'][i];qp=cfg['material_queries'][z['query_name']];site=p['S']if kind in('command','returned')else z['contact']['site']if kind=='contact'else z['actor_source']['site']if kind=='actor_source'else qp['B']
                row={'tick':t,'kind':kind,'index':i,'native':n.obs(a,site)}
                if kind in('command','returned'):row['positive_load_command']=material_command(row['native'])and row['native']['s_reg']>0
                if kind in('turn_tick','end_tick'):row['banks']=[{'sign':b['sign'],'native':n.obs(a,b['turn']if kind=='turn_tick'else b['target'])}for b in qp['banks']]
                rows.append(row)
    a.run_until(until);p['last_observed_tick']=a.tick;p['frames'].extend(rows);put(a,cfg)
    return {'frames':rows,'physical':physical(a.world,occupation=True),'requests':n.receipts(a,p['extra_requests']),
      'scope':'Only fixed observer events in execution. All action/query/return selection is native; material opportunities and their clock remain prepared.'}
