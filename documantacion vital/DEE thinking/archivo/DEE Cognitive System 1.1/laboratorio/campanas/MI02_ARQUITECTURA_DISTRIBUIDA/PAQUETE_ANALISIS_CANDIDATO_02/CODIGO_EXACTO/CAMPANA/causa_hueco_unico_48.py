"""One-site structural control for the R8->R9 reader-support diagnosis."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from app.lives import WorldAdapter
from capacidades.geometria_distribuida_mi02_r8 import unified_recipe
from capacidades.geometria_distribuida_mi02 import compile_geometry
from capacidades import integracion_distribuida_mi02_r8 as b
cases=[(251,'middle_gap',[0,1,1]),(252,'other_gap_sham',[-1,0,0])]
atomic_json(E/'CAUSA_HUECO48_FIJADO.json',{'baseline':'R8 neutral reader profile, same61/19 private and11/11 own histories','cases':cases,'intervention':'One previously raw0 removed-frame site is prepared as the same native inert boundary, either observed newborn-support site or off-target removed-frame gap. New T0 worlds, not editing existing learned matter.','future':[-1]*4+[1]*4,'criterion':'Does one-site closure change persistent B-reader occupancy into release while preserving private references and the social-use chain?','controls':'Existing230no closure plus252same one-site boundary outside the implicated middle support','sources':archive()})
for case,label,offset in cases:
    r,g=unified_recipe();N=g['N'];site=tuple((g['B'][i]+offset[i])%N for i in range(3));anchors={tuple(x['site']):(x['load'],tuple(x['direction']))for x in g['anchors']};opened={tuple(x)for x in g['opened']};pinned={tuple(x)for x in g['pinned']};assert site not in anchors;opened.discard(site);pinned.add(site);g['opened']=[list(x)for x in sorted(opened)];g['pinned']=[list(x)for x in sorted(pinned)];g['diagnostic_one_site_boundary']={'label':label,'site':list(site)}
    recipe=compile_geometry(N,opened,anchors,pinned);a=WorldAdapter(d.OrganizationalWorld.create(recipe));life='MI02_CAUSA_HUECO_'+str(case);p=E/(life+'.PREPARACION_T0.deetsnap.gz');a.save(p);Store().import_state(p,life,'fisica_directa',expected=sha(p));atomic_json(E/(life+'.RECETA_T0.json'),{'geometry':g,'sources':archive(),'new_T0_diagnostic_architecture':True})
    run(life,'HUECO48_ACQUIRE_'+str(case),lambda a,g=g:b.acquire(a,geometry=g,own=(11,11),private=(61,19)))
    run(life,'HUECO48_USE_'+str(case),lambda a:b.live(a,availability=[-1]*4+[1]*4))
atomic_json(E/'HUECO48_CORTES.json',{str(i):Store().record('MI02_CAUSA_HUECO_'+str(i))for i,_,_ in cases})
