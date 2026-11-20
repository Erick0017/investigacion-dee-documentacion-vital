"""MI02 candidate: persistent acquired fields, native context plasticity.

Prepared anatomy and periodic environmental supplies are explicit. No host
computes a selected action or writes a learned-memory update. Both admitted
histories and the actual v27 evolution decide the next material direction.
"""
import json
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata
from dee_thinking.consolidated import exact_observation,exact_receipt
from app.native_tools import physical
KEY='DEE.Cognitive.System.1.1.MI02.distributed.v1'
def get(a):
    e=dict(a.world.runtime.snapshot_metadata_entries)
    return decode_metadata(e[KEY])if KEY in e else None
def put(a,s):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(json.loads(json.dumps(s,allow_nan=False))))
def xyz(a,c,v,k=1):return[(c[i]+k*v[i])%int(a.world.runtime.dimension)for i in range(3)]
def obs(a,p):return exact_observation(a.world.runtime.observe(d.Coordinate(*p)))
def send(a,name,p,v,t,load=0,sem=1):
    old=next((q for q in a.world.interfaces if q.name==name),None)
    if old is None:
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*p);c.direction=d.Direction(*v);c.state=1;c.semantic=sem;c.allow_experience=True;c.allow_probe=True;s=d.InterfaceSpec();s.name=name;s.channel=c;a.world.declare_interface(s)
    else:
        c=old.channel
        if([c.injection_site.x,c.injection_site.y,c.injection_site.z],[c.direction.dx,c.direction.dy,c.direction.dz],c.semantic)!=(list(p),list(v),sem):raise ValueError('Immutable source identity differs')
    r=a.world.submit(name,load,t);return{'id':int(r.id),'port':name,'site':list(p),'direction':list(v),'tick':t,'payload':load,'semantic':sem}
def receipts(a,rows):return[{**x,'receipt':exact_receipt(a.world.runtime.receipt(x['id']))}for x in rows]
def inspect(a,s=None):
    s=s or get(a)
    if s is None:raise ValueError('No lived MI02 body; never reconstruct it silently')
    return{'physical':physical(a.world,occupation=True),'Q':obs(a,s['Q']),'memories':[obs(a,p)for p in s['memories']],'pending_protocol':s.get('pending',[]),'assistance':'Prepared permanent frame, neutral baseline observations, one common reader and fixed recurrent environmental material supplies. State/selection updates occur in v27.'}
def prepare(a,*,center=(20,20,20),values=(10,10),control='intact'):
    if get(a)is not None:raise ValueError('Body already present; continue it, do not renew anatomy')
    if control not in('intact','cut_action','cut_return','sham_cut'):raise ValueError('Declared initial physical control')
    C=list(center);base=a.tick+2
    if base%2:base+=1
    support=[(-1,0,1),(-1,1,0),(0,1,1),(1,0,1),(1,1,0),(-1,0,0),(1,0,0),(0,0,1)]
    if control=='cut_action':support.extend((r,-1,-1)for r in(-1,0,1))
    if control=='cut_return':support.extend((-2*r,-1,2)for r in(-1,0,1))
    if control=='sham_cut':support.extend((r,-1,9)for r in(-1,0,1))
    rr=[];pre=[];physical_seen=set()
    for k,v in enumerate(support):
        p=xyz(a,C,v)
        if tuple(p)in physical_seen:continue
        physical_seen.add(tuple(p));v0=obs(a,p);pre.append(v0);value=1 if tuple(v)in((-1,0,1),(-1,1,0))else 0
        if not(v0['state']==1 and v0['semantic']==4 and v0['s_reg']==value and v0['direction']==[0,0,0]):rr.append(send(a,'MI02.frame.'+str(k),p,(0,0,0),base,value,4))
    M=[xyz(a,C,v)for v in[(-1,1,1),(1,1,1)]];a.run_until(base+5);before={'M':[obs(a,p)for p in M],'Q':obs(a,C)}
    # Separate raw scalar experiences, not target directions or a trained state.
    rr.append(send(a,'MI02.reader',C,(0,0,-1),base+8,0))
    if values[0]is not None:rr.append(send(a,'MI02.memory.L',M[0],(0,0,0),base+8,int(values[0])))
    if values[1]is not None:rr.append(send(a,'MI02.memory.R',M[1],(0,0,0),base+12,int(values[1])))
    a.run_until(base+24)
    s={'schema':'MI02.distributed.candidate.r1','Q':C,'memories':M,'N':int(a.world.runtime.dimension),'prepared_at':base,'control':control,'frames':support,'initial_experiences':list(values),'index':0,'pending':[],'physical_sources':'Fixed reusable source ports. Environmental contact law is periodic, not a per-answer repair. No source ever writes an acquired memory after its first raw experience.','motor_code':'state1 semantic1 direction(x,-1,-1), x=-1/0/+1; x>=0 selects left affordance, x<0 right. A null direction or other state is not a decision. Zero load is valid native matter, not silence.'};put(a,s)
    s['schema']='MI02.distributed.candidate.r8';s['route_revision']='outer_feedback_finite_supplied';s['motor_code']='state>0 semantic1 direction(x,-1,-1), x=-1/0/+1; x>=0 selects left, x<0 right. Fixed codec; no output-derived host choice.';put(a,s)
    return{'before_acquisition':before,'frame_sites_before':pre,'requests':receipts(a,rr),'after':inspect(a,s),'scope':'The first untrained sample does not count as utility learning. Fixed material anatomy, finite/opportunity source limits and phase dependence are declared.'}
def qualified(v):return v['state']>0 and v['semantic']==1 and v['direction'][1:]==[-1,-1]and v['direction'][0]in(-1,0,1)
def cycle_plan(a,s,available,critical):
    C=s['Q'];turn=critical-15;plans=[];routes=[]
    for r in(-1,0,1):
        P=xyz(a,C,(r,-1,-1));which=1 if r>=0 else-1
        if r:
            stages=[(P,turn,[(0,0,1)],(r,-1,0),3),
                    (xyz(a,C,(4*r,-4,-1)),turn+3,[(-r,1,1),(0,1,0)],(0,1,1),3),
                    (xyz(a,C,(4*r,-1,2)),turn+6,[(-r,-1,-1)],(-r,0,0),6),
                    (xyz(a,C,(-2*r,-1,2)),turn+12,[(r,1,0)],(0,1,0),3)]
        else:
            stages=[(P,turn,[(0,0,1)],(0,-1,0),4),
                    (xyz(a,C,(0,-5,-1)),turn+4,[(1,1,1)],(1,0,1),4),
                    (xyz(a,C,(4,-5,3)),turn+8,[(-1,1,-1),(-1,0,0)],(-1,1,0),6),
                    (xyz(a,C,(-2,1,3)),turn+14,[(1,-1,-1)],(0,0,-1),1)]
        for j,(head,t,pulses,out,length)in enumerate(stages):
            routes.append({'r':r,'stage':j,'head':head,'tick':t,'out':list(out),'length':length})
            if j==0 and which==available:continue
            for k,v in enumerate(pulses):plans.append({'name':'MI02.outer.'+str(r)+'.'+str(j)+'.'+str(k),'site':xyz(a,head,v,-3),'direction':list(v),'tick':t-3,'payload':0,'role':'Fixed outer contact/return resource. Actual action determines presence of a consequence, not a host update.'})
    return{'critical':critical,'contact_tick':turn,'availability':available,'sources':plans,'routes':routes,'age_phase':'Odd391 boundary. The longer outer route avoids the dense first near-reader leg; all helpers and ghost stops fixed in preparation.'}
def live(a,*,availability,mode='intact',first_critical=None,trace=False):
    if mode not in('intact','omit_return','sham_return'):raise ValueError('Declared causal control')
    if not 1<=len(availability)<=32 or any(v not in(-1,1)for v in availability):raise ValueError('Finite world condition list +/-1')
    s=get(a)
    if s is None:raise ValueError('Body absent')
    if s.get('route_revision')!='outer_feedback_finite_supplied':raise ValueError('Another architecture revision is not silently repaired')
    first=391+782*max(0,(a.tick+20-391+781)//782)if first_critical is None else first_critical
    if first<a.tick+12 or first%782!=391:raise ValueError('Declared clock domain requires a future odd391 boundary')
    plans=[cycle_plan(a,s,v,first+782*i)for i,v in enumerate(availability)];all_requests=[];seen={};aliases=[]
    # Freeze all future material opportunities in this call before any reading.
    for p in plans:
        for row in p['sources']:
            if mode=='omit_return':continue
            pos=xyz(a,row['site'],(0,0,1),9)if mode=='sham_return'else row['site'];key=tuple(pos)+tuple(row['direction'])+(row['tick'],row['payload'])
            if key in seen:aliases.append({'logical':row,'event_id':seen[key]});continue
            rec=send(a,row['name'],pos,row['direction'],row['tick'],row['payload']);seen[key]=rec['id'];all_requests.append(rec)
    rows=[]
    for i,p in enumerate(plans):
        C=s['Q'];crit=p['critical'];frames=[]
        times=range(crit-20,crit+4)if trace else(crit-16,crit-15,crit-2,crit-1,crit,crit+1,crit+2)
        for t in times:
            a.run_until(t);frames.append({'tick':t,'Q':obs(a,C),'M':[obs(a,z)for z in s['memories']],'contacts':{str(r):obs(a,xyz(a,C,(r,-1,-1)))for r in(-1,0,1)},'return_heads':{str(r):obs(a,xyz(a,C,(-2*r,-1,2)))for r in(-1,0,1)},'neighbourhoods':[[obs(a,xyz(a,z,(x,y,k)))for x in(-1,0,1)for y in(-1,0,1)for k in(-1,0,1)]for z in s['memories']]if trace else[]})
        action=frames[0]['Q'];r=action['direction'][0]if qualified(action)else None;choice=(1 if r>=0 else-1)if r is not None else None
        contact=next(f for f in frames if f['tick']==crit-15)['contacts'].get(str(r))if r is not None else None
        material_action=bool(contact and contact['state']>0 and contact['semantic']==1 and contact['direction']==[r,-1,-1])
        failure_product=bool(contact and contact['state']>0 and contact['semantic']==1 and contact['direction']==[r,-1,0] and choice!=p['availability'])if r is not None else False
        rows.append({'index':s['index']+i,'critical_tick':crit,'availability':p['availability'],'action_sample':action,'physical_choice':choice,'native_direction':r,'choice_matches_environment':choice==p['availability']if choice is not None else False,'material_action':material_action,'failure_product':failure_product,'useful_material_action':bool(material_action and choice==p['availability']),'frames':frames})
    s['index']+=len(plans);s['last_critical']=plans[-1]['critical'];put(a,s)
    return{'plans':plans,'mode':mode,'rows':rows,'requests':receipts(a,all_requests),'deduplicated_aliases':aliases,'source_grammar':'Same fixed source-port law each782ticks. All calls prequeue conditions before action. This supply is environmental P0, not autonomous replenishment; no indefinite-duration claim.','final':inspect(a,s)}
