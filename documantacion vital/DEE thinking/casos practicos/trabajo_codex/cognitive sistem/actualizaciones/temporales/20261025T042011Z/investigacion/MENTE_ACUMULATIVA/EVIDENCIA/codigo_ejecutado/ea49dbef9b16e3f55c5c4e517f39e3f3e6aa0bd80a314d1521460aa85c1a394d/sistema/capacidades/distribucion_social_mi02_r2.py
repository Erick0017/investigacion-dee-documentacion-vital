"""Two learned scalar regions and prepared native recurrent transport.

One Runtime; no callback reads B to write A. Geometry/source material is
prepared, raw scalar contents are acquired later at each participant only.
"""
import json
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata
from capacidades import arquitectura_distribuida_mi02_r7 as n
from app.native_tools import physical
KEY='DEE.Cognitive.System.1.1.MI02.social_distributed.v1'
SUPPORT=[(-1,0,1),(-1,1,0),(0,1,1),(1,0,1),(1,1,0),(-1,0,0),(1,0,0),(0,0,1)]

def saved(a):
    m=dict(a.world.runtime.snapshot_metadata_entries)
    return decode_metadata(m[KEY])if KEY in m else None

def put(a,s):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(json.loads(json.dumps(s,allow_nan=False))))

def design(N=25,control='intact'):
    if control not in('intact','cut_message','sham'):raise ValueError('Declared physical message control')
    A=[6,14,14];B=[18,14,14]
    def move(c,v,k=1):return tuple((c[i]+k*v[i])%N for i in range(3))
    anchors={};opened=set();emitters=[];routes=[];sinks=set()
    for center in(A,B):
        for v in SUPPORT:anchors[move(center,v)]=(1 if v in((-1,0,1),(-1,1,0))else 0,(0,0,0))
        for v in((0,0,0),(-1,1,1),(1,1,1)):opened.add(move(center,v))
        for r in(-1,0,1):
            for k in range(1,4):opened.add(move(center,(r,-1,-1),k))
    for r in(-1,1):
        H=move(B,(3*r,-3,-3));J=move(A,(r,-3,-3));distance=(r*(J[0]-H[0]))%N
        for k in range(distance+1):opened.add(move(H,(r,0,0),k))
        # Native permanent SEM4 source gives a stream every other tick.
        for label,head,v,lag in[('turn1',H,(0,1,1),4),('turn2',J,(-r,1,1),3 if r<0 else 4)]:
            p=move(head,v,-lag);anchors[p]=(0,v);emitters.append({'id':str(r)+'.'+label,'site':list(p),'direction':list(v),'arrival_distance':lag,'target':list(head),'prepared_generic_load':0})
            for k in range(lag+1):opened.add(move(p,v,k))
            for k in range(1,4):opened.add(move(head,v,k))
        for k in range(3):opened.add(move(J,(0,1,1),k))
        # A toroidal X message encounters the opposite branch coupler first.
        # Its signed diagonal is retained, not decoded/reinjected by the host.
        for k in range(3):opened.add(move(J,(-r,1,1),k))
        sinks.add(move(A,(r,0,0)));sinks.add(move(B,(r,0,0)))
        cut=move(H,(r,0,0),max(2,distance//2))
        if control=='cut_message':anchors[cut]=(0,(0,0,0))
        if control=='sham':anchors[move(cut,(0,0,1),6)]=(0,(0,0,0))
        routes.append({'sign':r,'first_turn':list(H),'second_turn':list(J),'x_steps':distance,'arrival_to_A_context':list(move(J,(0,1,1),2)),'cut':list(cut)})
    placements=[]
    for x in range(N):
        for y in range(N):
            for z in range(N):
                p=(x,y,z)
                if p in opened and p not in anchors:continue
                q=d.InitialPlacement();q.site=d.Coordinate(*p);q.clock=0
                if p in anchors:load,v=anchors[p];q.raw=d.pack_record(1,load,*v,4);q.role='Prepared stable frame or generic zero-load recurrent source'
                else:q.raw=d.pack_record(0,0,0,0,0,4);q.role='Prepared inert native boundary, not free memory'
                placements.append(q)
    r=d.OrganizationRecipe.research(N,placements,0);r.execution=d.TickOptions(d.Backend.LAZY,1)
    return r,{'schema':'MI02.distributed_social.r2','A':A,'B':B,'N':N,'control':control,'emitters':emitters,'routes':routes,'open_sites':[list(v)for v in sorted(opened)],'anchors':[{'site':list(k),'load':v[0],'direction':list(v[1])}for k,v in sorted(anchors.items())],'history':[],'current_tick':0,'classification':'One compound prepared organization with spatially distinct A and B participant regions and native recurrent channels. B is not claimed a complete second mind. Only their functional memberships, not all Runtime sites, define participants.','host_assistance':'Initial geometry, scalar experiences and observation schedule; no answer forwarding, route selection or memory update from Python.'}

def acquire(a,*,own=(10,10),private=(47,17),geometry):
    if saved(a)is not None:raise ValueError('Architecture already lived; never silently reprepare')
    s=json.loads(json.dumps(geometry));t=a.tick+8;rr=[]
    for name,center,values,resource in[('A',s['A'],own,0),('B',s['B'],private,5)]:
        rr.append(n.send(a,'MI02.social.'+name+'.reader',center,(0,0,-1),t,resource))
        for j,value in enumerate(values):
            if value is not None:rr.append(n.send(a,'MI02.social.'+name+'.sample.'+str(j),n.xyz(a,center,(-1 if j==0 else 1,1,1)),(0,0,0),t+4*j,int(value)))
    a.run_until(t+20);s['current_tick']=a.tick;s['history'].append({'kind':'SEPARATE_RAW_EXPERIENCES','tick':t,'own':list(own),'private_B_only':list(private),'no_A_message_content_written':True});put(a,s)
    # Shared motor/state inspection adapter; native state is not copied.
    n.put(a,{'schema':'MI02.social_distributed.motor_view','Q':s['A'],'memories':[n.xyz(a,s['A'],v)for v in[(-1,1,1),(1,1,1)]],'N':s['N'],'route_revision':'social_r1','index':0,'pending':[],'history_in_metadata_not_used_for_decisions':True})
    return{'requests':n.receipts(a,rr),'after':state(a),'attribution':'Two separately acquired scalar relations, fixed gradient comparison, native message transport and context composition are hypotheses measured next, not success labels.'}

def state(a):
    s=saved(a)
    if not s:raise ValueError('No MI02 distributed social state; no reconstruction fallback')
    return{'physical':physical(a.world,occupation=True),'A':n.obs(a,s['A']),'B':n.obs(a,s['B']),'memories':{name:[n.obs(a,n.xyz(a,s[name],v))for v in[(-1,1,1),(1,1,1)]]for name in('A','B')},'memberships':['A learned local relation/use','B learned private relation/emission','prepared native sources and connecting environment'],'pending_protocol':[]}

def continue_world(a,*,ticks=160,detail=True):
    if type(ticks)is not int or not 1<=ticks<=4000:raise ValueError('Bounded native continuation required')
    s=saved(a)
    if not s:raise ValueError('Existing lived organization required')
    rows=[];end=a.tick+ticks;stride=1 if detail else 7
    while a.tick<end:
        a.run_until(min(end,a.tick+stride));row={'tick':a.tick,'A':n.obs(a,s['A']),'B':n.obs(a,s['B']),'A_context':[n.obs(a,n.xyz(a,s['A'],(r,-1,-1)))for r in(-1,0,1)]}
        if detail:
            row['turns']=[{'sign':r['sign'],'first':n.obs(a,r['first_turn']),'second':n.obs(a,r['second_turn'])}for r in s['routes']]
        rows.append(row)
    s['current_tick']=a.tick;put(a,s)
    return{'rows':rows,'final':state(a),'new_external_packets':0,'attribution':'Prepared sources and acquired fields evolve through official owner only. Passive observations never select responses.'}
