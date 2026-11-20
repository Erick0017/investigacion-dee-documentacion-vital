"""Research builders around the immutable native 3.0.0 Runtime."""
import dee_thinking as dt
from observations import add, c, receipt

OPTIONS=dt.TickOptions(dt.Backend.LAZY,1)

def channel(rt,name,site,direction,state=1,semantic=1,probe=True):
    s=dt.ChannelSpec(); s.name=name; s.injection_site=c(site)
    s.state=state; s.direction=dt.Direction(*direction); s.semantic=semantic
    s.allow_experience=True; s.allow_probe=probe; rt.register_channel(s)

def request(catalog_id, instance, anchor, params=None):
    r=dt.OrganizationRequest(); r.catalog_id=catalog_id; r.instance_id=instance
    r.anchor=c(anchor); r.parameters=params or {}; return r

def connect(planner,source,sourceport,target,targetport):
    e1=dt.Endpoint(); e1.instance=source; e1.port=sourceport
    e2=dt.Endpoint(); e2.instance=target; e2.port=targetport
    z=dt.ConnectionRequest(); z.source=e1; z.target=e2; z.purpose='physical research connection'
    planner.connect(z)

def c6_pair(anchors=((10,10,8),(10,10,24))):
    """Two fixed signal routes, installed before any experience; N=34 reference."""
    cat=dt.OrganizationCatalog(); pl=dt.CompositionPlanner(34)
    for i,a in enumerate(anchors):
        pl.add(cat.instantiate(request('relation_learning.c6h01.v1',f'l{i}',a)))
        pl.add(cat.instantiate(request('relation_query.c6h01.v1',f'q{i}',add(a,(0,1,0),8,34))))
        connect(pl,f'l{i}','learned_relation',f'q{i}','relation_input')
    w=pl.build(); w.runtime.execution_options=OPTIONS
    return w

def schedule(rt,log,name,tick,load,kind='experience'):
    r=getattr(rt,kind)(name,tick,load)
    log.append({'operation':kind,'called_at_tick':rt.current_tick,**receipt(r)})
    return r

def schedule_composed(w,log,instance,port,tick,load,probe=False):
    r=w.probe(instance,port,tick,load) if probe else w.experience(instance,port,tick,load)
    log.append({'operation':'probe' if probe else 'experience','called_at_tick':w.runtime.current_tick,
                'instance':instance,'port':port,**receipt(r)})
    return r

def research_world(n,placements,tick=0):
    raw=[0]*(n**3); clocks=[0]*(n**3)
    for p in placements:
        q=p['site']; i=dt.linear_index(*q,n)
        if raw[i] != 0: raise ValueError(f'preparation overlap {q}')
        raw[i]=dt.pack_record(p.get('state',1),p.get('load',0),*p['direction'],p.get('semantic',1))
        clocks[i]=p.get('clock',0)
    rt=dt.Runtime.import_research_state(n,tick,raw,clocks); rt.execution_options=OPTIONS
    return rt

def flight(site,direction,load,state=1,semantic=1,clock=0):
    return {'site':list(site),'direction':list(direction),'load':load,'state':state,
            'semantic':semantic,'clock':clock}

def collision_sources(hub, direction, time, loads, n):
    """CORE06 geometry, translating the same reducer mechanism to +y/-y/+z."""
    qdir=(-1,0,0); edir=(1,direction[1],direction[2])
    return [flight(add(hub,qdir,-time,n),qdir,loads[0]),
            flight(add(hub,edir,-time,n),edir,loads[1])]

def chain_world(loads1=(5,7),loads2=(9,15),query=13,arm='full',translation=(0,0,0),receiver_axis='y',receiver_sign=1,receiver_shift=(0,0,0)):
    n=34; h1=add((10,10,8),translation,1,n)
    meet1=add(h1,(0,1,0),8,n); meet2=add(meet1,(-1,1,0),5,n)
    d2=(0,receiver_sign,0) if receiver_axis=='y' else (0,0,receiver_sign)
    h2=add(add(meet2,d2,-13,n),receiver_shift,1,n)
    placements=[]
    if arm not in ('omit1','naive1'): placements+=collision_sources(h1,(0,1,0),3,loads1,n)
    if arm not in ('omit2','naive2'): placements+=collision_sources(h2,d2,3,loads2,n)
    rt=research_world(n,placements)
    channel(rt,'query',add(meet1,(-1,0,0),-5,n),(-1,0,0))
    return rt,{'N':n,'hub1':h1,'hub2':h2,'meeting1':meet1,'meeting2':meet2,
               'direction2':d2,'query_boundary':6,'query':query,'placements':placements,
               'channel':'query','memory_birth_tick':3,'meetings':[11,16],
               'reader_semantics':'destructive physical query; sequential collisions in one Runtime'}

def predictive_world(sign=1,paired=True,consequence=True,translation=(0,0,0),query=13,consequence_tick=18):
    n=34; h=add((10,15,14),translation,1,n)
    dst=add(h,(0,sign,0),8,n); opportunity=add(dst,(-1,sign,0),3,n)
    consequence_site=add(dst,(-1,sign,0),consequence_tick-11,n)
    placements=collision_sources(h,(0,sign,0),3,(5,7),n) if paired else []
    if not paired:
        # Same carrier inventory, different arrival time: pairing is removed physically.
        ss=collision_sources(h,(0,sign,0),3,(5,7),n)
        ss[1]['site']=list(add(ss[1]['site'],tuple(ss[1]['direction']),-1,n)); placements+=ss
    if consequence:
        placements.append(flight(add(consequence_site,(1,-sign,0),-consequence_tick,n),(1,-sign,0),23))
    rt=research_world(n,placements)
    for j,s in enumerate((1,-1)):
        qsite=add(add(h,(0,s,0),8,n),(-1,0,0),-5,n)
        channel(rt,f'signal{j}',qsite,(-1,0,0))
    return rt,{'N':n,'hub':h,'response_site':dst,'opportunity':opportunity,
               'consequence_site':consequence_site,'consequence_tick':consequence_tick,
               'query_tick':6,'query':query,'sign':sign,'placements':placements,
               'goal_route_direction':[-1,sign,0],'opportunity_tick':14,
               'goal_contract':'carrier reaches declared route at 14, before consequence at declared tick; physical teacher direction defines environmental regime'}

def basal(history='AB',control='FULL',origin=(15,15,15),contextual=False):
    f=dt.create_contextual_world if contextual else dt.create_relational_world
    kwargs={'control':getattr(dt.BasalControl,control),'origin':origin,'backend':dt.Backend.LAZY,'threads':1}
    if not contextual: kwargs['history']=getattr(dt.BasalHistory,history)
    return f(**kwargs)

def edited(rt,site,raw=None,clock=None,label='diagnostic'):
    e=dt.ResearchStateEdit();e.coordinate=c(site);e.raw=raw;e.clock=clock;e.label=label
    f=rt.diagnostic_fork([e],True)
    before=rt.observe(c(site));after=f.observe(c(site))
    return f,{'modality':'DIAGNOSTIC','tick':rt.current_tick,'label':label,'site':list(site),
              'raw_before':before.raw,'raw_after':after.raw,'clock_before':before.clock,'clock_after':after.clock}

# Extension 02 builders. Inherited functions above are retained verbatim.
from observations import coord

def phase_world(mode=0,anchor=(15,15,15),n=31,distance=4,clock_offset=0,permutation=0,signs=0,selected_source=3):
    cat=dt.OrganizationCatalog();pl=dt.CompositionPlanner(n)
    params={'control_mode':mode,'distance':distance,'permutation_code':permutation,'sign_mask':signs,'source_index':selected_source}
    if clock_offset:
        for j in range(4):
            params[f'source{j}_clock_high']=clock_offset>>32;params[f'source{j}_clock_low']=clock_offset&0xffffffff
    pl.add(cat.instantiate(request('temporal_phase_memory.core05.v1','phase',anchor,params)))
    w=pl.build();w.runtime.execution_options=OPTIONS
    return w

def distributed_world(history=1,anchor=(30,30,30),with_history=True,with_recurrence=True):
    cat=dt.OrganizationCatalog();pl=dt.CompositionPlanner(127)
    pl.add(cat.instantiate(request('distributed_context.i05.v1','context',anchor)))
    if with_history:
        pl.add(cat.instantiate(request('relative_history.i02.v1','history',anchor,{'history_mode':history})))
        connect(pl,'context','context_output','history','context')
    if with_recurrence:
        pl.add(cat.instantiate(request('contextual_multichannel_recurrence.p02.v1','integration',anchor)))
        if with_history:connect(pl,'history','history_state','integration','context_input')
        else:connect(pl,'context','context_output','integration','context_input')
    w=pl.build();w.runtime.execution_options=OPTIONS;return w

def cascade_world(depth=4,loads=None,omit=None,translation=(0,0,0)):
    n=127;h0=add((40,30,30),translation,1,n);first=add(h0,(0,1,0),8,n)
    pairs=loads or [(3,9+2*j) for j in range(depth)]
    placements=[];hubs=[];meetings=[]
    for j,pair in enumerate(pairs):
        t=11+5*j;meet=add(first,(-1,1,0),5*j,n);hub=add(meet,(0,1,0),-(t-3),n)
        hubs.append(hub);meetings.append({'tick':t,'site':meet,'loads':pair})
        if j!=omit:placements+=collision_sources(hub,(0,1,0),3,pair,n)
    rt=research_world(n,placements);channel(rt,'query',add(first,(-1,0,0),-5,n),(-1,0,0))
    return rt,{'N':n,'depth':depth,'hubs':hubs,'meetings':meetings,'placements':placements,
               'query_start':6,'omit':omit,'direction_after_first':[-1,1,0]}

def quiescent(history='AB',origin=(15,15,15),keep_reader=False):
    w=basal(history,'BARE' if keep_reader else 'READ_CUT',origin)
    rt=w.runtime
    if not keep_reader:
        for q in w.ports.environmental_sources:rt,_=edited(rt,tuple(coord(q)),0,label='pre-T0 environmental omission')
    return rt,{'origin':tuple(origin),'A':tuple(coord(w.ports.a)),'B':tuple(coord(w.ports.b)),
               'supports':[tuple(coord(q)) for q in w.ports.supports],
               'reader_source':tuple(coord(w.ports.reader_source)),
               'removed_environmental_sources':[tuple(coord(q)) for q in w.ports.environmental_sources] if not keep_reader else []}

def native_probe_world(history='AB',hidden=23,informative_side=1,origin=(15,15,15),extra_receiver=True):
    # Single conditional encounter: unlike old L09, no second/third return sources
    # independently reveal the condition to both routes.
    rt,meta=quiescent(history,origin,keep_reader=True);n=47
    action=add(origin,(informative_side,1,0),5,n);hdir=(-informative_side,0,1)
    source=add(action,hdir,-8,n)
    raw=rt.raw_copy();clk=rt.clock_copy()
    placements=[flight(source,hdir,hidden)]
    continuation=(0,1,1);response=add(action,continuation,8,n)
    if extra_receiver:placements.append(flight(add(response,(-1,0,0),-16,n),(-1,0,0),13))
    for p in placements:
        i=dt.linear_index(*p['site'],n)
        if raw[i]!=0:raise ValueError('native information interface overlaps preset')
        raw[i]=dt.pack_record(p['state'],p['load'],*p['direction'],p['semantic']);clk[i]=p['clock']
    new=dt.Runtime.import_research_state(n,32,raw,clk);new.execution_options=OPTIONS
    meta.update({'hidden_load':hidden,'informative_side':informative_side,'hidden_source':source,
                 'conditional_meeting':action,'downstream_site':response,'placements':placements,
                 'history':history,'domain':'body input plus actual chosen action trajectory to relative 16; no whole-body-return claim'})
    return new,meta

def competition_world(arm='both',occupied='empty',shift=0,translation=(0,0,0),second_direction=(0,0,1)):
    n=34;meet=add((12,16,15),translation,1,n);h1=add(meet,(0,1,0),-3,n);h2=add(meet,second_direction,-3-shift,n)
    placements=[]
    if arm!='B_only':placements+=collision_sources(h1,(0,1,0),3,(5,7),n)
    if arm!='A_only':placements+=collision_sources(h2,second_direction,3,(9,15),n)
    if occupied!='empty':
        placements.append(flight(meet,(0,0,0),100,state=1000,semantic=4 if occupied=='protected' else 1,clock=1))
        if occupied=='material':
            for j,d in enumerate(((-1,0,0),(-1,1,1),(0,0,1),(0,1,0))):
                placements.append(flight(add(meet,d,1,n),(0,0,0),0,state=3000+j,semantic=4,clock=31+j))
    rt=research_world(n,placements)
    final=add(meet,(0,1,1),4,n)
    channel(rt,'joint_query',add(final,(-1,0,0),-4,n),(-1,0,0))
    return rt,{'N':n,'meeting':meet,'birth_tick':3,'contact_tick':6,'joint_query_tick':6,
               'readout_tick':10,'readout':final,'hubs':[h1,h2],'placements':placements,
               'arm':arm,'occupied':occupied,'shift':shift,'second_direction':second_direction}

def mobile_basal_world(body_history='AB',paired=True,offpath=False,mobile_only=False,body_only=False,origin=(15,15,15)):
    n=47;rt,meta=quiescent(body_history,origin)
    if mobile_only:rt=research_world(47,[],32)
    raw=rt.raw_copy();clk=rt.clock_copy()
    hub=add(origin,(0,-1,0),3,n)
    if offpath:hub=add(hub,(0,0,1),6,n)
    placements=collision_sources(hub,(0,1,0),3,(5,7),n) if not body_only else []
    if placements and not paired:placements[1]['site']=list(add(tuple(placements[1]['site']),tuple(placements[1]['direction']),-1,n))
    for p in placements:
        i=dt.linear_index(*p['site'],n)
        if raw[i]!=0:raise ValueError('mobile/basal installation overlaps nonzero RAW')
        raw[i]=dt.pack_record(p['state'],p['load'],*p['direction'],p['semantic']);clk[i]=p['clock']
    new=dt.Runtime.import_research_state(n,32,raw,clk);new.execution_options=OPTIONS
    meta.update({'mobile_hub':hub,'mobile_birth':3,'input_neighborhood_arrival':5,'placements':placements,
                 'paired':paired,'offpath':offpath,'mobile_only':mobile_only,'body_only':body_only,
                 'preparation_boundary_tick':32})
    return new,meta
