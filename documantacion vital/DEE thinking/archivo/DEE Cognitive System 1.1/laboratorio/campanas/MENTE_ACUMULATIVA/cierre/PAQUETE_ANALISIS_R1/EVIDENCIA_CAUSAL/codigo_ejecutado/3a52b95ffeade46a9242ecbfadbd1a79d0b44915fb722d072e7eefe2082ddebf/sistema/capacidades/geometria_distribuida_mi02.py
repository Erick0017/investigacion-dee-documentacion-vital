"""Explicit experimental T0 geometry compiler, not a cognitive controller."""
from types import SimpleNamespace
from dee_thinking import _native as d
from capacidades import arquitectura_distribuida_mi02_r8 as body
from capacidades import distribucion_social_mi02_r2 as social

def return_geometry(N=17,C=(8,8,8),control='intact',include_zero=True):
    f=SimpleNamespace(world=SimpleNamespace(runtime=SimpleNamespace(dimension=N)));C=list(C);opened=set();anchors={};pinned=set()
    def pos(v):return tuple(body.xyz(f,C,v))
    for v in social.SUPPORT:anchors[pos(v)]=(1 if v in((-1,0,1),(-1,1,0))else 0,(0,0,0))
    for v in((0,0,0),(-1,1,1),(1,1,1)):opened.add(pos(v))
    plans=[body.cycle_plan(f,{'Q':C},v,391)for v in(-1,1)]
    for plan in plans:
        for source in plan['sources']:
            if not include_zero and source['name'].startswith('MI02.outer.0.'):continue
            for k in range(4):opened.add(tuple(body.xyz(f,source['site'],source['direction'],k)))
        for r in plan['routes']:
            if not include_zero and not r['r']:continue
            for k in range(r['length']+1):opened.add(tuple(body.xyz(f,r['head'],r['out'],k)))
    for r in(-1,0,1):
        for k in range(3):opened.add(pos((r*k,-k,-k)))
    for v in((-1,0,2),(1,0,2),(3,-4,2)):pinned.add(pos(v))
    if control=='cut_action':
        for r in(-1,0,1):anchors[pos((r,-1,-1))]=(0,(0,0,0))
    if control=='cut_return':
        for r in(-1,1):anchors[pos((4*r,-4,-1))]=(0,(0,0,0))
    if control=='sham_cut':anchors[pos((6,6,6))]=(0,(0,0,0))
    return{'opened':opened,'anchors':anchors,'pinned':pinned,'N':N,'center':C,'control':control}

def compile_geometry(N,opened,anchors,pinned=()):
    opened=set(map(tuple,opened));pinned=set(map(tuple,pinned));placements=[]
    for x in range(N):
        for y in range(N):
            for z in range(N):
                p=(x,y,z)
                if p in opened and p not in anchors and p not in pinned:continue
                q=d.InitialPlacement();q.site=d.Coordinate(*p);q.clock=0
                if p in anchors:load,v=anchors[p];q.raw=d.pack_record(1,load,*v,4);q.role='Prepared physical frame or recurrent native source'
                else:q.raw=d.pack_record(0,0,0,0,0,4);q.role='Prepared inert physical boundary, not an empty learned-memory bank'
                placements.append(q)
    recipe=d.OrganizationRecipe.research(N,placements,0);recipe.execution=d.TickOptions(d.Backend.LAZY,1);return recipe

def return_recipe(N=17,C=(8,8,8),control='intact'):
    g=return_geometry(N,C,control);r=compile_geometry(N,g['opened'],g['anchors'],g['pinned'])
    return r,{'variant':'outer_return_r8','N':N,'center':list(C),'control':control,'opened':[list(v)for v in sorted(g['opened'])],'pinned':[list(v)for v in sorted(g['pinned'])],'anchors':[{'site':list(k),'load':v[0],'direction':list(v[1])}for k,v in sorted(g['anchors'].items())]}

def unified_recipe(control='intact'):
    if control not in('intact','cut_query','cut_message','cut_return','sham_query','no_gate_resource'):raise ValueError('Finite predeclared unified control')
    N=25;_,sg=social.design(N,control='cut_message'if control=='cut_message'else'intact');A=sg['A'];B=sg['B'];f=SimpleNamespace(world=SimpleNamespace(runtime=SimpleNamespace(dimension=N)))
    opened=set(map(tuple,sg['open_sites']));anchors={tuple(v['site']):(v['load'],tuple(v['direction']))for v in sg['anchors']};rg=return_geometry(N,A,'cut_return'if control=='cut_return'else'intact',include_zero=False);opened.update(rg['opened']);pinned=rg['pinned']
    for p,v in rg['anchors'].items():
        if p in anchors and anchors[p]!=v:raise ValueError('Conflicting fixed material preparation at '+str(p))
        anchors[p]=v
    # Fixed query wire: x0 from A is physically distinct from either motor.
    points=[([A[0],A[1]-3,A[2]-3],(0,0,1),0,4,(0,-1,0),7),
            ([A[0],4,11],(1,1,1),0,3,(1,0,1),3),
            ([9,4,14],(0,0,-1),0,4,(1,0,0),6),
            ([15,4,14],(-1,1,0),0,4,(0,1,0),4),
            ([15,8,14],(1,0,0),0,4,(1,1,0),3),
            ([18,11,14],(-1,0,0),5,3,(0,1,0),3)]
    query=[]
    for j,(head,v,load,lag,out,length)in enumerate(points):
        head=[x%N for x in head];origin=tuple(body.xyz(f,head,v,-lag));anchors[origin]=(load,v)
        if j==5 and control=='no_gate_resource':anchors.pop(origin)
        for k in range(lag+1):opened.add(tuple(body.xyz(f,origin,v,k)))
        for k in range(length+1):opened.add(tuple(body.xyz(f,head,out,k)))
        for k in range(1,4):opened.add(tuple(body.xyz(f,head,v,k)))
        query.append({'stage':j,'head':head,'source':list(origin),'source_direction':list(v),'source_load':load,'source_distance':lag,'outgoing':list(out),'outgoing_length':length})
    query_cut=tuple(body.xyz(f,A,(0,-1,-1),2))
    if control=='cut_query':anchors[query_cut]=(0,(0,0,0))
    if control=='sham_query':anchors[tuple(body.xyz(f,query_cut,(0,0,1),7))]=(0,(0,0,0))
    # Ghost stops are causal material from T0, never an online cleanup.
    geometry={'schema':'MI02.unified.r1','N':N,'A':A,'B':B,'social':sg,'query':query,'control':control,'query_cut':list(query_cut),'opened':[list(p)for p in sorted(opened)],'pinned':[list(p)for p in sorted(pinned)],'anchors':[{'site':list(k),'load':v[0],'direction':list(v[1])}for k,v in sorted(anchors.items())],'prepared':'Stationary frames, generic sources, action/return/query/social wiring and inert boundaries. Neither local scalar relation nor B private relation is preloaded.','hypothesis':'An actual failed action changes A relative fields. At balance, x0 goes physically to query gate. Generic fixed load5 plus actual request activates B reader; B acquired relation determines response. Native response changes A subsequent decisions together with local history.','not_claimed':'A complete mind, innate Spanish, autonomous generation of anatomy or resources, or learned external control.'}
    return compile_geometry(N,opened,anchors,pinned),geometry
