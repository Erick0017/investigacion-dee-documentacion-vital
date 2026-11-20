"""Candidate P0 apparatus for native acquired-reference P1 selection.

No world creation, metadata lookup, history decoder, bank selection or external
worker is hidden here. The same three generic query pulses are always submitted.
Anatomy coordinates are relative, so another shared-world experiment may prepare
the apparatus legally and acquire its OWN history; never transplant learned RAW.
"""
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
VERSION='MUFI01.selector_accretion.r06'
def at(origin,delta,N=67):return tuple((origin[i]+delta[i])%N for i in range(3))
def geometry(origin=(33,33,33),N=67):
    frame={(-1,-1,0):(1,0,1),(1,-1,0):(1,0,1)}
    for x in(-2,2):
        for y in(-2,-1):
            for z in(-1,0,1):frame[(x,y,z)]=(1,0,4)
    for p in((0,1,1),(0,1,-1)):frame[p]=(1,0,4)
    for p in((0,0,1),(-1,-3,0),(1,-3,0),(-1,-2,1),(1,-2,1),(2,1,2),(-2,0,0),(-3,3,0),(3,3,0)):
        frame[p]=(0,0,4)
    return [{'site':at(origin,p,N),'state':v[0],'s_reg':v[1],'semantic':v[2],'direction':(0,0,0),'raw':int(d.pack_record(v[0],v[1],0,0,0,v[2]))}for p,v in sorted(frame.items())]
def placements(origin=(33,33,33),N=67):
    out=[]
    for r in geometry(origin,N):
        p=d.InitialPlacement();p.site=d.Coordinate(*r['site']);p.raw=r['raw'];p.clock=0;p.role='P0 reference baseline or generic support/terminator; no acquired choice';out.append(p)
    return out
def ports(origin=(33,33,33),N=67,prefix='selector'):
    # Teaching contact first occupies reference-Z and disappears by low density.
    out={prefix+'.experience.A':(at(origin,(-1,-1,-4),N),(0,0,1)),prefix+'.experience.B':(at(origin,(1,-1,-4),N),(0,0,1))}
    out[prefix+'.query']=(at(origin,(0,0,-3),N),(0,0,1))
    out[prefix+'.support.plus']=(at(origin,(-2,1,-2),N),(1,0,1))
    out[prefix+'.support.minus']=(at(origin,(2,4,0),N),(-1,-1,0))
    return out
def declare(world,origin=(33,33,33),N=67,prefix='selector'):
    present=set(world.runtime.channel_names)
    for name,(pos,v)in ports(origin,N,prefix).items():
        if name in present:continue
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*pos);c.direction=d.Direction(*v);c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=True
        i=d.InterfaceSpec();i.name=name;i.channel=c;world.declare_interface(i)
def submit(world,name,payload,tick):
    r=world.submit(name,int(payload),int(tick))
    return {'id':int(r.id),'port':name,'payload':int(payload),'tick':int(tick)}
def experience(world,side,arrival_tick,prefix='selector'):
    if side not in('A','B'):raise ValueError('Explicit experience side must be A or B; not selected by this apparatus')
    return submit(world,prefix+'.experience.'+side,0,int(arrival_tick)-3)
def query(world,tick,payload=0,prefix='selector',supports=True):
    out=[submit(world,prefix+'.query',payload,tick)]
    if supports:
        out+=[submit(world,prefix+'.support.plus',0,tick),submit(world,prefix+'.support.minus',0,tick)]
    return out
def read(world,origin=(33,33,33),N=67):
    candidates=[];observations=[]
    for sign in(-1,0,1):
        pos=at(origin,(2*sign,2,0),N);o=exact_observation(world.runtime.observe(d.Coordinate(*pos)));observations.append(o)
        if o['state']>0 and o['semantic']==1 and o['direction']==[sign,1,0]:candidates.append({'choice':sign,'observation':o})
    return {'tick':int(world.runtime.current_tick),'observations':observations,'candidates':candidates,'choice':candidates[0]['choice']if len(candidates)==1 else None,'information':'Only all three physical actuator sites and fixed direction classes; no target/history/metadata.'}
def receipt(world,request):return dict(request,receipt=exact_receipt(world.runtime.receipt(request['id'])))
