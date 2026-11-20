"""Native situated-learning candidate, fixed geometry and no answer selection.

Training reuses the tested AA01 consequence encounters but imports no state.
The closed-loop candidate schedules resources at both action endpoints.
MI01 postformed-cut controls40-44 show later zero-load route products can
alter the selector even without an executed contact. Do not infer that every
R6 update is caused by the actual action merely from this prepared geometry.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata
from dee_thinking.consolidated import exact_receipt,exact_observation
from functools import lru_cache
from copy import deepcopy
from capacidades import conductos_acceso_aa01 as _transport
_original_turning_inputs=_transport.turning_inputs
@lru_cache(maxsize=1024)
def _cached_turn(i,o):return _original_turning_inputs(i,o)
def _same_turn(i,o):return deepcopy(_cached_turn(tuple(i),tuple(o)))
# Pure finite geometry memoization, local to this capability. Do not replace
# another admitted capability's module-global function on system import.
KEY='DEE.Cognitive.System.1.1.IC01.v1'
N=67;CENTER=[15,15,50]
def move(p,v,k=1):return[(p[i]+v[i]*k)%N for i in range(3)]
def obs(a,p):return exact_observation(a.world.runtime.observe(d.Coordinate(*p)))
def configuration(a):
    m=dict(a.world.runtime.snapshot_metadata_entries)
    return decode_metadata(m[KEY])if KEY in m else {'schema':'IC01.native.r1','center':CENTER,'episodes':{},'steps':[]}
def save(a,g):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(g))
def submit(a,name,site,v,t,load=0,semantic=1):
    if t<a.tick:raise ValueError('No past input')
    old=next((x for x in a.world.interfaces if x.name==name),None)
    if old is None:
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*site);c.direction=d.Direction(*v);c.state=1;c.semantic=semantic;c.allow_experience=True;c.allow_probe=True;p=d.InterfaceSpec();p.name=name;p.channel=c;a.world.declare_interface(p)
    else:
        c=old.channel
        if ([c.injection_site.x,c.injection_site.y,c.injection_site.z],[c.direction.dx,c.direction.dy,c.direction.dz],c.semantic)!=(list(site),list(v),semantic):raise ValueError('Interface identity mismatch')
    rec=a.world.submit(name,load,t)
    return {'id':int(rec.id),'port':name,'site':list(site),'direction':list(v),'tick':t,'payload':load,'semantic':semantic}
def arrive(a,name,target,v,t,load=0):
    site=move(target,v,-3);cache=getattr(a,'_ic_shared_opportunities',None)
    key=tuple(site)+tuple(v)+(t-3,load,1)
    if cache is not None and key in cache:
        return {**cache[key],'logical_alias':name,'shared_physical_opportunity':True}
    row=submit(a,name,site,v,t-3,load)
    if cache is not None:cache[key]=row
    return row
def receipts(a,rr):return [{**r,'receipt':exact_receipt(a.world.runtime.receipt(r['id']))}for r in rr]
def train(a,*,episode,contexts=(1,-1),feedback='paired',center=None):
    if feedback not in('paired','omit','unpaired'):raise ValueError('Declared feedback mode')
    g=configuration(a);S=list(center or g['center']);g['center']=S
    if episode in g['episodes']:raise ValueError('Episode already exists')
    epoch=6+67*max(0,(a.tick+10-6+66)//67);rr=[];layout={};supports=[]
    for j in(-1,1):
        for r in(-1,1):
            E=move(move(S,(j,0,0),-10),(0,r,0),10);Q=move(E,(j,r,1),-4);H=move(Q,(0,0,1),-6);label=str(j)+','+str(r);layout[label]={'E':E,'Q':Q,'H':H,'r':r,'j':j}
            for role,p,dt in(('pulse',move(Q,(1,0,0),6),13),('feedback',move(E,(0,-r,-1),4),16)):
                before=obs(a,p)
                if before['state']==1 and before['semantic']==4 and before['direction']==[0,0,0]:supports.append({'site':p,'reused':True,'pre':before})
                else:
                    rr.append(submit(a,'IC01.'+episode+'.support.'+label+'.'+role,p,(0,0,0),epoch+dt,0,4));supports.append({'site':p,'pre':before,'legal_input_no_overwrite':True})
    for i,available in enumerate(contexts):
        if available not in(-1,1):raise ValueError('Physical route context required')
        off=67*i
        for label,z in layout.items():
            j=z['j'];r=z['r'];tag='IC01.'+episode+'.'+str(i)+'.'+label
            rr.append(arrive(a,tag+'.cue',z['H'],(-1,0,0),epoch+off+3,5));rr.append(arrive(a,tag+'.sample',z['H'],(1,0,1),epoch+off+3,11))
            if r!=available:rr.append(submit(a,tag+'.environment',z['Q'],(1,0,0),epoch+off+8,3))
            rr.append(arrive(a,tag+'.explore',z['Q'],(j,r,0),epoch+off+9,5))
            if feedback=='omit':continue
            shift=int(feedback=='unpaired')
            rr.append(arrive(a,tag+'.consequence1',z['E'],(0,-r,-1),epoch+off+13+shift,7));rr.append(arrive(a,tag+'.consequence2',z['E'],(0,-r,0),epoch+off+13+shift,7))
    captures=[]
    for i in range(len(contexts)):
        a.run_until(epoch+67*i+23);captures.append({'tick':a.tick,'selector':obs(a,S),'route_ends':{k:obs(a,z['E'])for k,z in layout.items()}})
    ep={'epoch':epoch,'contexts':list(contexts),'feedback':feedback,'center':S,'layout':layout,'supports':supports,'captures':captures,'requests':receipts(a,rr),'last_selector_tick':a.tick,'candidate':'R1_AA_NATIVE_TRAINING_ONLY','assistance':'Prepared routes, physical contexts, generic exploration and consequence opportunities; no target is supplied to the common future query.'}
    g['episodes'][episode]=ep;g['last_selector_tick']=a.tick;save(a,g);return ep
def loop(a,*,name,steps=2,mode='intact',query_lead=67,return_load=7,delay=0):
    if mode not in('intact','omit_return','unpaired_return','sham'):raise ValueError('Unknown loop control')
    g=configuration(a);S=g['center'];last=g.get('last_selector_tick')
    if last is None:raise ValueError('No lived selector history')
    first=last+67*max(1,(a.tick+4-last+66)//67)+delay
    rows=[]
    for i in range(steps):
        t=first+75*i;prefix='IC01.loop.'+name+'.'+str(i);rr=[];pre=obs(a,S)
        rr.append(arrive(a,prefix+'.common',S,(1,0,0),t,5))
        for r in(-1,1):
            E=move(S,(1,r,0),4);shift=1 if mode=='unpaired_return'else 0
            if mode!='omit_return':
                T=move(E,(0,0,1),9)if mode=='sham'else E
                rr.append(arrive(a,prefix+'.feedback1.'+str(r),T,(-1,-r,1),t+4+shift,return_load));rr.append(arrive(a,prefix+'.feedback2.'+str(r),T,(-1,-r,-1),t+4+shift,return_load))
        rr.append(arrive(a,prefix+'.normalizer',S,(1,0,0),t+8,0))
        a.run_until(t);action=obs(a,S)
        a.run_until(t+4);ends={str(r):obs(a,move(S,(1,r,0),4))for r in(-1,1)}
        a.run_until(t+8);post=obs(a,S);g['last_selector_tick']=a.tick
        row={'name':name,'index':i,'query_tick':t,'mode':mode,'pre':pre,'action':action,'environment_after':ends,'return_selector':post,'requests':receipts(a,rr)};rows.append(row)
    g['steps'].extend(rows);save(a,g);return rows

def loop2(a,*,name,steps=2,mode='intact',return_load=7,delay=0):
    """R2 turns actual XY action into the AA consequence-gated return path.

    Unlike R1, consequence pulses without a command do not point back to S.
    All turn and outcome opportunities are provided to BOTH branches.
    """
    from capacidades.conductos_acceso_aa01 import turning_inputs
    if mode not in('intact','omit_return','unpaired_return','sham','no_action'):raise ValueError('Unknown R2 control')
    g=configuration(a);S=g['center'];last=g.get('last_selector_tick')
    if last is None:raise ValueError('No acquired selector')
    first=last+67*max(1,(a.tick+4-last+66)//67)+delay;rows=[]
    for i in range(steps):
        t=first+96*i;prefix='IC01.R2.'+name+'.'+str(i);rr=[];pre=obs(a,S);turn_plan=[]
        if mode!='no_action':rr.append(arrive(a,prefix+'.common',S,(1,0,0),t,5))
        for r in(-1,1):
            P=move(S,(1,r,0),4);R=move(P,(1,0,0),9);Q=move(R,(0,r,-1),3);E=move(S,(1,r,0),10)
            for j,(site,when,vin,vout)in enumerate(((P,t+4,(1,r,0),(1,0,0)),(R,t+13,(1,0,0),(0,r,-1)),(Q,t+16,(0,r,-1),(-1,r,1)))):
                pulses=turning_inputs(vin,vout);turn_plan.append({'r':r,'site':site,'tick':when,'incoming':list(vin),'outgoing':list(vout),'pulses':pulses})
                for z,pulse in enumerate(pulses):rr.append(arrive(a,prefix+'.turn.'+str(r)+'.'+str(j)+'.'+str(z),site,pulse['direction'],when,pulse['payload']))
            if mode!='omit_return':
                T=move(E,(0,0,1),9)if mode=='sham'else E;shift=int(mode=='unpaired_return')
                rr.append(arrive(a,prefix+'.consequence1.'+str(r),T,(0,-r,-1),t+19+shift,return_load));rr.append(arrive(a,prefix+'.consequence2.'+str(r),T,(0,-r,0),t+19+shift,return_load))
        rr.append(arrive(a,prefix+'.normalizer',S,(1,0,0),t+29,0))
        a.run_until(t);action=obs(a,S);turns=[]
        for off in(4,13,16,19):
            a.run_until(t+off);turns.append({'tick':a.tick,'routes':{str(r):obs(a,move(S,(1,r,0),10)if off==19 else move(S,(1,r,0),4)if off==4 else move(move(S,(1,r,0),4),(1,0,0),9)if off==13 else move(move(move(S,(1,r,0),4),(1,0,0),9),(0,r,-1),3))for r in(-1,1)}})
        a.run_until(t+29);post=obs(a,S);g['last_selector_tick']=a.tick
        row={'revision':'R2','name':name,'index':i,'query_tick':t,'mode':mode,'pre':pre,'action':action,'turn_plan':turn_plan,'propagation':turns,'return_selector':post,'requests':receipts(a,rr)};rows.append(row)
    g['steps'].extend(rows);save(a,g);return rows

def situated(a,*,name,availability=(1,1,-1,-1),mode='intact',trace=False,compact=False,gap=67,stream=False,queue_only=False,shunt='none'):
    """R3 win-stay/lose-switch candidate embodied by native contacts.

    Availability chooses environmental material BEFORE any action. It never
    selects a reader based on a response. A real command plus those materials
    forms one of four directional states; identical fixed return opportunities
    for all four map it to a persistent route. This is a prepared learning law;
    only its acquired directional state belongs to the lived organization.
    """
    from capacidades.conductos_acceso_aa01 import routes_for_common_arrival
    turning_inputs=_same_turn
    if mode not in('intact','omit_return','no_action','unpaired','sham','cut_action','sham_action'):raise ValueError('Explicit R3 control')
    g=configuration(a);S=g['center'];last=g['last_selector_tick'];rows=[]
    resumed=stream and g.get('stream_action_tick')==a.tick
    first=a.tick if resumed else last+67*max(1,(a.tick+4-last+66)//67);phase=first%67;t=first
    # Freeze the ENTIRE geometry/calendar before measuring any response.
    plans=[]
    for i,available in enumerate(availability):
        if available not in(-1,1):raise ValueError('Availability property +/-1 required')
        starts={};ends={};contacts=[]
        for r in(-1,1):
            P=move(S,(1,r,0),4);sigma=1 if r==available else-1
            contacts.append({'r':r,'site':P,'tick':t+4,'incoming':[1,r,0],'outgoing':[sigma,r,0],'pulses':turning_inputs((1,r,0),(sigma,r,0))})
            for s in(-1,1):
                key=str(r)+','+str(s);starts[key]={'site':move(P,(s,r,0),4),'direction':[s,r,0]};ends[key]={'site':S,'direction':[0,r*s,0]}
        # A final orthogonal approach prevents an impossible conditional180
        # turn at the final pure-Y support; the original bounded failure is kept.
        prestage={key:{'site':move(S,(0,z['direction'][1],0),-5),'direction':[0,0,1]}for key,z in ends.items()}
        routes={}if compact else routes_for_common_arrival(starts,prestage,t+8,phase=(phase-5)%67)
        if compact:
            for key,z in starts.items():
                r,s=map(int,key.split(','));p=list(z['site']);when=t+8;vin=z['direction'];turns=[];travel=[]
                segments=[([0,-r,0],16),([-1,0,0],14)]if s==1 else[([0,0,1],6),([-1,0,0],12),([0,0,-1],6),([1,0,0],6)]
                for v,k in segments:
                    pulses=turning_inputs(tuple(vin),tuple(v))
                    if pulses:turns.append({'site':p[:],'tick':when,'incoming':vin[:],'outgoing':v[:],'pulses':pulses})
                    p=move(p,v,k);when+=k;travel.append({'site_after':p[:],'tick_after':when,'direction':v[:],'steps':k});vin=v
                # Shared native convergence. Same zero-load resources for either
                # possible command; no host detects which one actually arrived.
                turns.append({'site':p[:],'tick':when,'incoming':vin[:],'outgoing':[1,0,0],'pulses':[{'direction':[1,1,0],'payload':0},{'direction':[1,-1,0],'payload':0}],'zero_ghost_has_no_acquired_payload':True})
                p=move(p,(1,0,0),6);when+=6;travel.append({'site_after':p[:],'tick_after':when,'direction':[1,0,0],'steps':6})
                final=[0,r*s,0];turns.append({'site':p[:],'tick':when,'incoming':[1,0,0],'outgoing':final,'pulses':turning_inputs((1,0,0),tuple(final))})
                p=move(p,final,8);when+=8;travel.append({'site_after':p[:],'tick_after':when,'direction':final,'steps':8});vin=final
                if p!=S or when!=t+52:raise AssertionError('Compact route geometry')
                routes[key]={'turns':turns,'travel':travel,'destination':p,'arrival_tick':when,'last_direction':vin,'fixed_prepared_transport':True}
        for key,route in ([]if compact else routes.items()):
            direction=ends[key]['direction'];tail=list(route['destination']);when=route['arrival_tick'];pulses=turning_inputs(tuple(route['last_direction']),tuple(direction))
            if pulses:route['turns'].append({'site':tail,'tick':when,'incoming':route['last_direction'],'outgoing':direction,'pulses':pulses,'without_command_direction':'OFF_FINAL_Y_ROUTE'})
            route['travel'].append({'site_after':S,'tick_after':when+5,'direction':direction,'steps':5});route.update(destination=S,arrival_tick=when+5,last_direction=direction)
        arrival=next(iter(routes.values()))['arrival_tick'];plans.append({'index':i,'query_tick':t,'availability':available,'contacts':contacts,'routes':routes,'return_tick':arrival});t=arrival+gap
    # All environmental opportunities, including common queries, are queued
    # before observing the first action. Overlapping cycles use no host rescue.
    scheduled=[]
    for plan in plans:
        i=plan['index'];t=plan['query_tick'];prefix='IC01.R3.'+name+'.'+str(i);rr=[]
        a._ic_shared_opportunities={}
        if mode!='no_action'and not(resumed and i==0):rr.append(arrive(a,prefix+'.common',S,(1,0,0),t,0 if compact else 5))
        if i==0 and mode in('cut_action','sham_action'):
            target=move(S,(1,1,0),2)
            if mode=='sham_action':target=move(target,(0,0,1),9)
            rr.append(submit(a,prefix+'.postformed_interceptor',target,(0,0,0),t+1,0,4))
        for contact in plan['contacts']:
            for j,pulse in enumerate(contact['pulses']):rr.append(arrive(a,prefix+'.environment.'+str(contact['r'])+'.'+str(j),contact['site'],pulse['direction'],contact['tick'],pulse['payload']))
        if mode!='omit_return':
            shift=int(mode=='unpaired')
            for key,route in plan['routes'].items():
                # Environmental context fixes which material outcome can exist
                # on EACH action branch, before either branch is selected by DEE.
                # Do not furnish impossible counterfactual outcome routes; their
                # ungated zero-load ghosts were a measured R4 interference.
                r,s=map(int,key.split(','))
                if s!=(1 if r==plan['availability']else-1):continue
                for j,turn in enumerate(route['turns']):
                    target=move(turn['site'],(0,0,1),9)if mode=='sham'else turn['site']
                    for k,pulse in enumerate(turn['pulses']):rr.append(arrive(a,prefix+'.return.'+key+'.'+str(j)+'.'+str(k),target,pulse['direction'],turn['tick']+shift,pulse['payload']))
        scheduled.append(rr)
        del a._ic_shared_opportunities
    if stream and mode!='no_action':
        final=plans[-1]['return_tick'];scheduled[-1].append(arrive(a,'IC01.stream.'+name+'.next_common',S,(1,0,0),final,0))
    if shunt not in('none','a_only','all','sham'):raise ValueError('Prepared transient-shunt variant')
    shunts=[];seen=set()
    if shunt!='none':
        for p in plans:
            for key,route in p['routes'].items():
                r,s=map(int,key.split(','))
                if s!=(1 if r==p['availability']else-1):continue
                for j,turn in enumerate(route['turns']):
                    if shunt in('a_only','sham')and j!=0:continue
                    pulses=turn['pulses'];ghost=tuple((sum(q['direction'][i]for q in pulses)>0)-(sum(q['direction'][i]for q in pulses)<0)for i in range(3))
                    if not any(ghost)or list(ghost)==turn['outgoing']:continue
                    axis=next((i for i in(2,0,1)if ghost[i]==0),0);v=[0,0,0];v[axis]=1 if ghost[axis]==0 else-ghost[axis]
                    target=move(turn['site'],ghost,6)
                    if shunt=='sham':target=move(target,(0,0,1),19)
                    when=turn['tick']+6;physical_key=tuple(target)+tuple(v)+(when,)
                    if physical_key in seen:continue
                    seen.add(physical_key);req=arrive(a,'IC01.shunt.'+name+'.'+str(len(shunts)),target,v,when,0);scheduled[0].append(req);shunts.append({'source_turn':turn,'ghost':list(ghost),'target':target,'tick':when,'counterflow':v,'request':req,'classification':'Prepared P0 transient diversion, not learned filtering or clearing'})
    if queue_only:
        return{'plans':plans,'requests':scheduled,'center':S,'name':name,'stream':stream,'mode':mode,'first_action_already_formed':resumed,'end_tick':plans[-1]['return_tick'],'shunts':shunts}
    for plan,rr in zip(plans,scheduled):
        t=plan['query_tick'];i=plan['index']
        trace_frames=[];events={}
        if trace:
            for key,route in plan['routes'].items():
                for j,turn in enumerate(route['turns']):
                    for offset in(-1,0,1):events.setdefault(turn['tick']+offset,[]).append((key,j,turn))
        def advance(until):
            for when in sorted(k for k in events if a.tick<k<=until):
                a.run_until(when)
                trace_frames.append({'tick':when,'regions':[{'key':key,'turn':j,'expected':turn,'context':[obs(a,move(turn['site'],(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]}for key,j,turn in events[when]]})
            a.run_until(until)
        advance(t);action=obs(a,S);advance(t+4);contact_rows={str(r):obs(a,move(S,(1,r,0),4))for r in(-1,1)}
        advance(t+8);source_rows={key:obs(a,route['turns'][0]['site']if route['turns']else route['destination'])for key,route in plan['routes'].items()}
        advance(plan['return_tick']);post=obs(a,S);g['last_selector_tick']=a.tick
        row={'revision':'R6'if gap==0 else'R5B'if compact else'R3D','name':name,**plan,'mode':mode,'gap_ticks':gap,'action':action,'contact':contact_rows,'return_sources':source_rows,'return_selector':post,'requests':receipts(a,rr),'physical_opportunity_count':len(set(r['id']for r in rr)),'host_decisions':'Prepared availability and context-compatible outcome opportunities on BOTH action branches, ALL queued before measuring the first action. No response-dependent route or selector update. Identical generic resources are shared. Query payload is zero; zero-load route ghosts are not qualified actions.'};rows.append(row)
        row['passive_trace']=trace_frames
        if i==0:row['shunts']=shunts
    g['steps'].extend([{k:row[k]for k in('revision','name','index','query_tick','return_tick','mode','action','return_selector')}for row in rows]);
    if stream:g['stream_action_tick']=a.tick
    save(a,g);return rows
