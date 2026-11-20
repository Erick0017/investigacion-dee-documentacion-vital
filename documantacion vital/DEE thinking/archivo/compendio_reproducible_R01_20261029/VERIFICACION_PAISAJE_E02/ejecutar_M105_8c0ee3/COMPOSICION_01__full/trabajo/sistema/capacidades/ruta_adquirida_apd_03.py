"""APD01 separate native route reference within the SAME existing N67 world.

Prepared geometry is admitted through legal interfaces on exact RAW0 sites.
No learned content is transplanted. One explicit B contact supplies a seed
history. Common excess feedback never chooses an A/B port according to action.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata
from dee_thinking.consolidated import exact_observation,exact_receipt
from capacidades import selector_acrecion_nativo as sel

VERSION='APD01.separate_route_O2.common_cost.candidate.R3'
KEY='DEE.Cognitive.System.1.1.APD01.route_O2.R3'
N=67;O=(15,45,15);PREFIX='APD.route';BUDGET=2
S=sel.at(O,(-1,0,1),N);SHAM=sel.at(O,(-1,0,5),N)


def obs(a,p):return exact_observation(a.world.runtime.observe(d.Coordinate(*p)))
def refs(a):return[obs(a,sel.at(O,v,N))for v in((-1,-1,0),(1,-1,0))]
def get(a):
    if int(a.world.runtime.dimension)!=N:raise ValueError('Same N67 life required')
    e=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in e:raise ValueError('Explicit separate-route preparation required')
    return decode_metadata(e[KEY])
def save(a,m):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m))
def declare(a,name,p,direction,state=1,semantic=1):
    old=next((i for i in a.world.interfaces if i.name==name),None)
    if old is not None:
        c=old.channel
        if ([c.injection_site.x,c.injection_site.y,c.injection_site.z],[c.direction.dx,c.direction.dy,c.direction.dz],c.state,c.semantic)!=(list(p),list(direction),state,semantic):raise ValueError('Existing source has another fixed contract')
        return
    c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*p);c.direction=d.Direction(*direction);c.state=state;c.semantic=semantic;c.allow_experience=True;c.allow_probe=False
    i=d.InterfaceSpec();i.name=name;i.channel=c;a.world.declare_interface(i)
def submit(a,name,value,tick):
    r=a.world.submit(name,value,tick);return{'id':int(r.id),'port':name,'payload':value,'tick':tick}
def receipts(a,rs):return[{**r,'receipt':exact_receipt(a.world.runtime.receipt(r['id']))}for r in rs]


def geometry():
    rows={tuple(r['site']):r for r in sel.geometry(O,N)}
    for x in(-1,0,1):
        for z in(0,-1):
            p=sel.at(O,(3*x,3,3*z),N)
            r={'site':p,'state':0,'s_reg':0,'semantic':4,'direction':(0,0,0),'raw':int(d.pack_record(0,0,0,0,0,4))}
            if p in rows and rows[p]['raw']!=r['raw']:raise ValueError('Prepared geometry conflict')
            rows[p]=r
    return[rows[p]for p in sorted(rows)]


def prepare(a):
    if int(a.world.runtime.dimension)!=N:raise ValueError('Cannot resize a lived world')
    if KEY in dict(a.world.runtime.snapshot_metadata_entries):raise ValueError('Already admitted; no reset/reinstallation')
    rows=geometry();pre=[obs(a,r['site'])for r in rows]
    if any(int(o['raw'])!=0 for o in pre):raise ValueError('Fixed O2 anatomy intersects nonzero RAW; retain it and fail, never overwrite')
    rs=[];tick=a.tick+2
    for n,r in enumerate(rows):
        name=PREFIX+'.prepare.'+str(n);declare(a,name,r['site'],(0,0,0),r['state'],r['semantic']);rs.append(submit(a,name,r['s_reg'],tick))
    a.run_until(tick+1);rr=receipts(a,rs)
    sel.declare(a.world,O,N,PREFIX)
    declare(a,PREFIX+'.cost',S,(0,0,0));declare(a,PREFIX+'.cost_sham',SHAM,(0,0,0))
    save(a,{'version':VERSION,'origin':list(O),'prepared_tick':a.tick,'explicit_seeds':0,
            'route_uses':0,'environmental_returns':0,'learned_scalar_stored_in_metadata':False,
            'assistance':'Separate P0 route anatomy, six frozen gates, operator initiative, '
                         'generic queries, fixed excess>2 and even391 feedback cadence. '
                         'Physical reference changes only through native evolution.'})
    return{'version':VERSION,'classification':'New prepared anatomy in SAME lived world, no learned fields copied',
           'pre':pre,'rows':rows,'post':[obs(a,r['site'])for r in rows],'requests':rr,'references':refs(a),
           'all_admitted':all(x['receipt']['status']=='applied'for x in rr)}


def seed_B(a):
    m=get(a)
    if m['explicit_seeds']:raise ValueError('Only one declared seed contact, no repeat-until-positive')
    k=(int(a.tick)+5)//391+1
    if k%2==0:k+=1
    arrival=k*391;before=refs(a);r=sel.experience(a.world,'B',arrival,PREFIX)
    frames=[]
    for t in range(arrival-1,arrival+3):
        a.run_until(t);frames.append({'tick':a.tick,'references':refs(a)})
    m['explicit_seeds']+=1;save(a,m)
    return{'kind':'explicit_B_seed','arrival':arrival,'before':before,'after':refs(a),
           'request':sel.receipt(a.world,r),'frames':frames,
           'scope':'Explicit content/reference preparation, not learned optimal routing'}

def explicit_contact(a,side):
    """A declared teacher revision, never used by the outcome transducer."""
    m=get(a)
    if side not in ('A','B'):raise ValueError('The external teacher must explicitly specify A or B')
    k=(int(a.tick)+5)//391+1
    if k%2==0:k+=1
    arrival=k*391;before=refs(a);request=sel.experience(a.world,side,arrival,PREFIX)
    a.run_until(arrival+2);m['explicit_revisions']=m.get('explicit_revisions',0)+1;save(a,m)
    return {'kind':'explicit_route_teacher_revision','side_supplied_by_teacher':side,'arrival':arrival,
            'before':before,'after':refs(a),'request':sel.receipt(a.world,request),
            'not_an_autonomous_policy_change':True,'not_called_by_return_cost':True}


def read(a):
    observations=[];candidates=[]
    for x in(-1,0,1):
        for z in(0,-1):
            o=obs(a,sel.at(O,(2*x,2,2*z),N));observations.append(o)
            if o['state']>0 and o['semantic']==1 and o['direction']==[x,1,z]:candidates.append(x)
    return{'tick':a.tick,'origin':list(O),'observations':observations,'candidates':candidates,
           'choice':candidates[0]if len(candidates)==1 else None,
           'scope':'All six O2 gates fixed before response; no target/history decoder'}


def use(a):
    m=get(a);q=a.tick+4;before=refs(a);rs=sel.query(a.world,q,5,PREFIX)
    a.run_until(q+6);reader=read(a);a.run_until(q+8)
    m['route_uses']+=1;save(a,m)
    return{'kind':'separate_native_route_use','query_tick':q,'read_tick':q+6,
           'references_before':before,'references_after':refs(a),'reader':reader,
           'requests':[sel.receipt(a.world,r)for r in rs]}


def return_cost(a,cost,*,mode='real'):
    m=get(a);k=(int(a.tick)+12+390)//391
    if k%2:k+=1
    q=k*391-4
    if type(cost)is not int or not 0<=cost<=32:raise ValueError('Literal modelled environment cost0..32')
    if mode not in('real','omit','sham'):raise ValueError('Fixed return modality only')
    before=refs(a);rs=[]
    if cost>BUDGET and mode!='omit':rs.append(submit(a,PREFIX+('.cost'if mode=='real'else'.cost_sham'),cost,q+3))
    qr=sel.query(a.world,q,5,PREFIX);frames=[]
    for t in range(q-1,q+9):
        a.run_until(t);frames.append({'tick':a.tick,'references':refs(a),'S':obs(a,S),'sham':obs(a,SHAM)})
        if t==q+6:reader=read(a)
    m['environmental_returns']+=1;save(a,m)
    return{'kind':'separate_route_common_cost','cost':cost,'fixed_budget':BUDGET,
           'mode':mode,'boundary_multiplier':k,'query_tick':q,'datum_tick':q+3,
           'before':before,'after':refs(a),'reader':reader,'frames':frames,
           'requests':receipts(a,rs)+[sel.receipt(a.world,r)for r in qr],
           'scope':'One common literal-cost port, no action-dependent A/B assignment. '
                   'Calendar/excess gate/asymmetric physical bias remain prepared P0.'}
