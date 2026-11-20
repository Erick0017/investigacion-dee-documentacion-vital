"""Operational candidate extracted from FI01 B05, not another manager.

Install as capacidades/percepcion_cruda_fi01.py after bounded verification.
No laboratory/evidence paths, historical answers, precomputed component sums,
campaign-close flag, snapshot loader or selected-answer routing are used here.
The caller owns the Runtime/writer and saves its complete state normally.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata
from dee_thinking.consolidated import exact_observation,exact_receipt
from app.native_tools import physical
from capacidades import selector_acrecion_nativo as sel

KEY='DEE.Cognitive.System.1.1.FI01.raw_perception.B05.v1'
VERSION='FI01.B05.operational_candidate.R1'
N=67;E=(15,15,15);S=(14,15,16)
FACTORS={8:[4],16:[4,2],32:[4,4],64:[4,4,2],128:[4,4,4]}

def geometry(level):
    """Fixed geometry only; no scalar observations or expected answer argument."""
    if level not in FACTORS:raise ValueError('Declared raw-input levels8/16/32/64/128 only')
    nodes=[];raw=[];resources=[];opened=set();factors=FACTORS[level]
    def add(p,v,k=1):return tuple(p[i]+k*v[i]for i in range(3))
    def visit(side,p,t,depth,path):
        name=side+'.'+path;nodes.append({'id':name,'site':list(p),'join_tick_relative':t,'arity':factors[depth]});opened.add(p)
        if depth==0:
            for j,(sx,sy)in enumerate(((-1,-1),(-1,1),(1,-1),(1,1))):
                site=add(p,(sx,sy,1));raw.append({'id':name+'.raw.'+str(j),'side':side,'site':list(site),'direction':[-sx,-sy,-1],'injection_tick_relative':t-1,'head':list(p),'head_tick_relative':t});opened.add(site)
            return
        spacing=3**depth+1;offsets=((-1,-1),(-1,1),(1,-1),(1,1))if factors[depth]==4 else((-1,0),(1,0))
        for j,(sx,sy)in enumerate(offsets):
            child=(p[0]+sx*spacing,p[1]+sy*spacing,p[2]+spacing+2);ct=t-spacing-2;visit(side,child,ct,depth-1,path+'.'+str(j))
            junction=add(child,(0,0,-1),2);source=add(junction,(sx,sy,1));v=(-sx,-sy,-1)
            resources.append({'id':name+'.turn.'+str(j),'side':side,'site':list(source),'direction':list(v),'injection_tick_relative':ct+1,'payload':0});opened.add(source)
            opened.update(add(child,(0,0,-1),k)for k in range(3));opened.update(add(junction,v,k)for k in range(spacing+1))
    visit('left',(16,16,16),0,len(factors)-1,'root');visit('right',(50,50,16),0,len(factors)-1,'root')
    for side,parity in(('left',0),('right',1)):
        for j,q in enumerate(x for x in raw if x['side']==side):q['component_index']=2*j+parity
    def actual(p,side):
        x,y,z=p;zz=z+1 if side=='left'else N-5-z
        return[(E[0]-36+y)%N,(E[1]-N+4+zz)%N,(E[2]-30+x)%N]
    def actual_direction(v,side):return[v[1],v[2]if side=='left'else-v[2],v[0]]
    corridor=set()
    for p in opened:corridor.add(tuple(actual(p,'left'if p[0]<33 else'right')))
    for q in raw:
        q['site']=actual(q['site'],q['side']);q['head']=actual(q['head'],q['side']);q['direction']=actual_direction(q['direction'],q['side'])
    for q in resources:q['site']=actual(q['site'],q['side']);q['direction']=actual_direction(q['direction'],q['side']);q.pop('side')
    for q in nodes:q['site']=actual(q['site'],q['id'].split('.')[0])
    def f(p):return[(E[0]-36+p[1])%N,(E[1]-N+4+p[2])%N,(E[2]-30+p[0])%N]
    def vv(v):return[v[1],v[2],v[0]]
    for side,root,dz,dy,dx in(('left',(16,16,17),-1,1,1),('right',(50,50,N-21),1,-1,-1)):
        J=add(root,(0,0,dz),2);H=(root[0],33,N-2);v=(0,dy,dz);r=(dx,-dy,-dz)
        resources.extend([{'id':side+'.root.turnY','site':f(add(J,v,-1)),'direction':vv(v),'injection_tick_relative':1,'payload':0},
          {'id':side+'.root.turnX','site':f(add(H,r,-1)),'direction':vv(r),'injection_tick_relative':18,'payload':0}])
        corridor.update(tuple(f(add(root,(0,0,dz),k)))for k in range(3));corridor.update(tuple(f(add(J,v,k)))for k in range(18));corridor.update(tuple(f(add(H,(dx,0,0),k)))for k in range(18))
    C=(12,17,18);v=(1,-1,-1)
    resources.append({'id':'remote_root.constant_exit_X_minusY_minusZ','site':list(add(C,v,-1)),'direction':list(v),'injection_tick_relative':35,'payload':0})
    corridor.update(tuple(x%N for x in add(C,v,k))for k in(-1,0,1,2))
    corridor.update(tuple(q['site'])for q in raw+resources)
    return {'version':VERSION,'level':level,'N':N,'E':list(E),'datum_site':list(S),'remote_aggregate_site':list(C),
      'raw_sources':raw,'generic_sources':resources,'nodes':nodes,'opened':list(map(list,sorted(corridor))),
      'raw_relative_tick':raw[0]['injection_tick_relative'],'datum_relative_tick':38,'input_to_datum_ticks':38-raw[0]['injection_tick_relative']}

def observe(a,p):return exact_observation(a.world.runtime.observe(d.Coordinate(*p)))
def get(a):
    if int(a.world.runtime.dimension)!=N:raise ValueError('This exact B05 contract is N67; never resize or substitute a lived world')
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:raise ValueError('Explicit prepare required; never silently install/reconstruct a reader')
    m=decode_metadata(entries[KEY])
    if m.get('version')!=VERSION:raise ValueError('Raw-perception interface version mismatch')
    return m
def save(a,m):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m))
def declare(a,name,site,direction,*,state=1,semantic=1):
    old=next((x for x in a.world.interfaces if x.name==name),None)
    if old is not None:
        c=old.channel
        actual=([c.injection_site.x,c.injection_site.y,c.injection_site.z],[c.direction.dx,c.direction.dy,c.direction.dz],c.state,c.semantic)
        if actual!=(list(site),list(direction),state,semantic):raise ValueError('Immutable physical source contract differs: '+name)
        return
    c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*site);c.direction=d.Direction(*direction);c.state=state;c.semantic=semantic;c.allow_experience=True;c.allow_probe=False
    i=d.InterfaceSpec();i.name=name;i.channel=c;a.world.declare_interface(i)
def submit(a,name,site,direction,tick,payload):
    declare(a,name,site,direction);v=a.world.submit(name,payload,tick)
    return {'id':int(v.id),'port':name,'site':list(site),'direction':list(direction),'tick':tick,'payload':payload}
def receipts(a,rs):return[{**r,'receipt':exact_receipt(a.world.runtime.receipt(r['id']))}for r in rs]

def prepare(a,level=128):
    from capacidades import mente_unificada_01 as mu
    mu.get(a)
    if int(a.world.runtime.dimension)!=N:raise ValueError('No other dimension is claimed by this operational profile')
    if KEY in dict(a.world.runtime.snapshot_metadata_entries):raise ValueError('Raw perception already admitted; do not reinstall over a lived future')
    g=geometry(level);m=mu.get(a)
    front=mu.prepare_current(a)if not m.get('current_frontend')else{'existing_current_frontend':True,'not_reinstalled':True}
    p=(15,14,15);o=observe(a,p);inert=int(d.pack_record(0,0,0,0,0,4));rs=[]
    if int(o['raw'])!=inert:
        if int(o['raw'])!=0:raise ValueError('Spill stop intersects nonzero RAW, including inactive state; preserve it and fail without clearing')
        name='MU.raw.spill_stop';declare(a,name,p,(0,0,0),state=0,semantic=4);t=a.tick+2;r=a.world.submit(name,0,t);rs=[{'id':int(r.id),'port':name,'site':list(p),'tick':t,'payload':0}];a.run_until(t+1)
    rr=receipts(a,rs)
    if any(x['receipt']['status']!='applied'for x in rr):raise ValueError('Spill stop not admitted; keep reached state, no silent retry')
    for q in g['raw_sources']+g['generic_sources']:declare(a,'MU.raw.L'+str(level)+'.'+q['id'],q['site'],q['direction'])
    save(a,{'version':VERSION,'level':level,'prepared_tick':a.tick,'frames':0,'raw_requests':0,'generic_requests':0,
      'interface_contract':'One simultaneous raw scalar0..32 per fixed source; generic zero resources; six fixed native actuator classes. Metadata stores no learned target/reference/aggregate.',
      'assistance':'Operator initiates the frame; fixed geometry and codec P0. Native acquired references and encounters determine output; repeated-domain limits remain declared.'})
    return {'version':VERSION,'level':level,'current_frontend':front,'spill_stop':{'site':list(p),'pre':o,'post':observe(a,p),'requests':rr},
      'raw_interfaces':len(g['raw_sources']),'generic_interfaces':len(g['generic_sources']),'classification':'Explicit external P0 sensory extension, NOT new acquired content or autonomous initiative.'}

def frame(a,components,*,detailed=False):
    from capacidades import mente_unificada_01 as mu
    m=get(a);g=geometry(m['level']);level=g['level']
    if not isinstance(components,list)or len(components)!=level or any(type(v)is not int or not 0<=v<=32 for v in components):raise ValueError('One independent exact raw scalar0..32 per declared component')
    if not mu.get(a).get('current_frontend'):raise ValueError('The common six-class frontend contract is not admitted')
    start=a.tick;before=physical(a.world);leaf=start+2;root=leaf-g['raw_relative_tick'];datum=root+38
    timing=mu.query_timing(a,int(datum-3));shift=timing['wait_ticks'];leaf+=shift;root+=shift;datum+=shift;q=timing['effective_query_tick'];rs=[]
    pre_datum=observe(a,S);pre_refs=[observe(a,p)for p in((14,14,15),(16,14,15))]
    for s in g['raw_sources']:rs.append(submit(a,'MU.raw.L'+str(level)+'.'+s['id'],s['site'],s['direction'],root+s['injection_tick_relative'],components[s['component_index']]))
    for s in g['generic_sources']:rs.append(submit(a,'MU.raw.L'+str(level)+'.'+s['id'],s['site'],s['direction'],root+s['injection_tick_relative'],0))
    rs.extend(sel.query(a.world,q,5,'MU.selector'))
    points={'E':E,'S':S,'A':(14,14,15),'B':(16,14,15),'C':g['remote_aggregate_site']}
    if detailed:points.update({n['id']:n['site']for n in g['nodes']})
    ticks={datum-2,datum-1,datum,datum+1,q+6,q+8}
    if detailed:ticks.update(root+n['join_tick_relative']for n in g['nodes'])
    frames=[];answer=None
    for t in sorted(ticks):
        a.run_until(t);frames.append({'tick':a.tick,'fields':{k:observe(a,p)for k,p in points.items()}})
        if t==q+6:answer=mu.current_read(a)
    # The tested domain includes physical returns, not a zero-tick clock skip.
    a.run_until(q+8+2*N)
    m['frames']+=1;m['raw_requests']+=len(g['raw_sources']);m['generic_requests']+=len(g['generic_sources'])+3;save(a,m)
    return {'kind':'native_joint_raw_perception','version':VERSION,'level':level,'raw_components':components,'input_tick':leaf,'all_components_same_tick':True,
      'datum_tick':datum,'query_tick':q,'read_tick':q+6,'timing':timing,'reader':answer,'before':before,'after':physical(a.world,occupation=True),
      'datum_pre':pre_datum,'datum_after':observe(a,S),'references_pre':pre_refs,'references_after':[observe(a,p)for p in((14,14,15),(16,14,15))],
      'requests':receipts(a,rs),'frames':frames,'minimum_passive_horizon_ticks':2*N,
      'scope':'Prepared simultaneous raw codec/tree plus the actual life acquired reference. No host sum or answer selection. Capacity is sparse near-boundary aggregation/use, NOT128concepts, language or a generally competent policy. Reuse was tested with old-memory queries interleaved; other cadence requires its own coverage.'}
