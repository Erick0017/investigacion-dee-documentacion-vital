"""Last bounded controller-family route revision; B cooperation proceeds next."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from app.lives import WorldAdapter
from capacidades import arquitectura_distribuida_mi02_r8 as b
from types import SimpleNamespace

def createbody(life,control):
    N=17;C=[8,8,8];f=SimpleNamespace(world=SimpleNamespace(runtime=SimpleNamespace(dimension=N)));opened=set();anchors={};pinned=set()
    def pos(v):return tuple(b.xyz(f,C,v))
    support=[(-1,0,1),(-1,1,0),(0,1,1),(1,0,1),(1,1,0),(-1,0,0),(1,0,0),(0,0,1)]
    for v in support:anchors[pos(v)]=1 if v in((-1,0,1),(-1,1,0))else 0
    for v in((0,0,0),(-1,1,1),(1,1,1)):opened.add(pos(v))
    plan=b.cycle_plan(f,{'Q':C},-1,391)
    other=b.cycle_plan(f,{'Q':C},1,391)
    for source in plan['sources']+other['sources']:
        for k in range(4):opened.add(tuple(b.xyz(f,source['site'],source['direction'],k)))
    for r in plan['routes']:
        for k in range(r['length']+1):opened.add(tuple(b.xyz(f,r['head'],r['out'],k)))
    for r in(-1,0,1):
        for k in range(3):opened.add(pos((r*k,-k,-k)))
    for v in((-1,0,2),(1,0,2),(3,-4,2)):pinned.add(pos(v))
    if control=='cut_action':
        for r in(-1,0,1):anchors[pos((r,-1,-1))]=0
    if control=='cut_return':
        for r in(-1,1):anchors[pos((4*r,-4,-1))]=0
        anchors[pos((0,-5,-1))]=0
    if control=='sham_cut':anchors[pos((6,6,6))]=0
    placements=[]
    for x in range(N):
        for y in range(N):
            for z in range(N):
                p=(x,y,z)
                if p in opened and p not in anchors and p not in pinned:continue
                q=d.InitialPlacement();q.site=d.Coordinate(*p);q.clock=0;q.raw=d.pack_record(1,anchors[p],0,0,0,4)if p in anchors else d.pack_record(0,0,0,0,0,4);q.role='Prepared stationary frame or inert physical boundary';placements.append(q)
    sources=archive();r=d.OrganizationRecipe.research(N,placements,0);r.execution=d.TickOptions(d.Backend.LAZY,1);a=WorldAdapter(d.OrganizationalWorld.create(r));p=E/(life+'.PREPARACION_T0.deetsnap.gz');a.save(p);Store().import_state(p,life,'fisica_directa',expected=sha(p));atomic_json(E/(life+'.RECETA_T0.json'),{'sources':sources,'N':N,'center':C,'opened':sorted(opened),'pinned_ghost_stops':sorted(pinned),'anchors':[{'p':list(k),'load':v}for k,v in anchors.items()],'new_untrained_life':True,'control':control})

if __name__=='__main__':
    atomic_json(E/'PROTOCOLO_RETORNO_EXTERIOR_11.json',{'availability':[-1,-1,-1,1,1,-1],'hypothesis':'Route physical failure around the dense Q-neighbour region; zero-state SEM4 stops only predetermined resource ghosts. No acquired contents are refreshed.','scope':'Recurrent environmental supply under fixed rule, finite horizon; not autonomous source construction.'})
    for case,control,mode in[(90,'intact','intact'),(91,'intact','omit_return'),(92,'cut_return','intact')]:
        life='MI02_CONTROLADOR_'+str(case);createbody(life,control);run(life,'CONTROLADOR_PREPARAR_'+str(case),lambda a:b.prepare(a,center=[8,8,8]))
        z=run(life,'CONTROLADOR_VIVIR_'+str(case),lambda a,mode=mode:b.live(a,availability=[-1,-1,-1,1,1,-1],mode=mode,trace=True))
        print(json.dumps({'case':case,'rows':[{'t':x['critical_tick'],'choice':x['physical_choice'],'failure':x['failure_product'],'useful':x['useful_material_action'],'M_after':[v['s_reg']for v in x['frames'][-1]['M']]}for x in z['rows']]},ensure_ascii=False),flush=True)
