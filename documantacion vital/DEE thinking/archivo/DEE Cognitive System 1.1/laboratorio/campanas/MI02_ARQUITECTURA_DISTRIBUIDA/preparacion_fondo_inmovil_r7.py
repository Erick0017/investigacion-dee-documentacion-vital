"""External T0 geometry compiler, no learned content and no kernel emulation.
State0 SEM4 is a native prepared inert region, not free/uninformative vacuum.
"""
from comun_mi02 import *
from capacidades import arquitectura_distribuida_mi02_r7 as b
from app.lives import WorldAdapter
from types import SimpleNamespace

def recipe(N=17,center=(8,8,8),control='intact'):
    fake=SimpleNamespace(world=SimpleNamespace(runtime=SimpleNamespace(dimension=N)))
    C=list(center);S={'Q':C};opened=set();anchors={}
    def pos(v):return tuple(b.xyz(fake,C,v))
    for v in((0,0,0),(-1,1,1),(1,1,1)):opened.add(pos(v))
    support=[(-1,0,1),(-1,1,0),(0,1,1),(1,0,1),(1,1,0),(-1,0,0),(1,0,0),(0,0,1)]
    if control=='cut_action':support.extend((r,-1,-1)for r in(-1,0,1))
    if control=='cut_return':support.extend((-2*r,-1,2)for r in(-1,0,1))
    if control=='sham_cut':support.extend((r,-1,9)for r in(-1,0,1))
    for v in support:anchors[pos(v)]=1 if tuple(v)in((-1,0,1),(-1,1,0))else 0
    for available in(-1,1):
        p=b.cycle_plan(fake,S,available,391)
        for source in p['sources']:
            for k in range(4):opened.add(tuple(b.xyz(fake,source['site'],source['direction'],k)))
    for r in(-1,0,1):
        P=b.xyz(fake,C,(r,-1,-1));v=(-r,0,1);H=b.xyz(fake,C,(-2*r,-1,2));out=(-1,1,0)if r==0 else(0,1,0)
        for k in range(4):opened.add(tuple(b.xyz(fake,P,v,k)));opened.add(tuple(b.xyz(fake,H,out,k)))
        for k in range(3):opened.add(pos((k*r,-k,-k)))
    placements=[];inert=0
    for x in range(N):
        for y in range(N):
            for z in range(N):
                p=(x,y,z)
                if p in opened and p not in anchors:continue
                q=d.InitialPlacement();q.site=d.Coordinate(*p);q.clock=0
                if p in anchors:q.raw=d.pack_record(1,anchors[p],0,0,0,4);q.role='Prepared material frame/absorber; no acquired answer'
                else:q.raw=d.pack_record(0,0,0,0,0,4);q.role='Prepared inert state0 observer background; not available empty storage';inert+=1
                placements.append(q)
    r=d.OrganizationRecipe.research(N,placements,0);r.execution=d.TickOptions(d.Backend.LAZY,1)
    return r,{'N':N,'center':C,'control':control,'open_sites':sorted(opened-set(anchors)),'material_anchors':[{'site':list(p),'load':v}for p,v in sorted(anchors.items())],'inert_state0_SEM4_count':inert,'no_learned_memory_preloaded':True,'not_a_kernel_change':True,'not_a_memory_capacity_claim':True}

def new_life(life,N=17,center=(8,8,8),control='intact'):
    budget();r,g=recipe(N,center,control);sources=archive();attempt=len(list(E.glob(life+'.CONSTRUCCION_*.json')))+1
    atomic_json(E/(life+'.CONSTRUCCION_'+str(attempt)+'.json'),{'native_ticks':0,'sources':sources,'geometry':g,'instrumental_API_version':r.version,'research_variant':'MI02.R4 inert physical background, not a replacement of native recipe ABI version'})
    world=d.OrganizationalWorld.create(r);a=WorldAdapter(world);p=E/(life+'.PREPARACION_T0.deetsnap.gz');a.save(p)
    rec=Store().import_state(p,life,'fisica_directa',expected=sha(p));atomic_json(E/(life+'.RECETA_T0.json'),{'new_untrained_architecture':True,'not_inherited_E1_continuity':True,'native_ticks':0,'geometry':g,'record':rec,'sources':sources});return rec
