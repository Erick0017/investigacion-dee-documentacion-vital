"""Native situated-learning candidate, fixed geometry and no answer selection.

Training reuses the tested AA01 consequence encounters but imports no state.
The closed-loop candidate schedules equal resources at both action endpoints;
only an actually emitted native carrier can return and alter the next route.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata
from dee_thinking.consolidated import exact_receipt,exact_observation
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
def arrive(a,name,target,v,t,load=0):return submit(a,name,move(target,v,-3),v,t-3,load)
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
