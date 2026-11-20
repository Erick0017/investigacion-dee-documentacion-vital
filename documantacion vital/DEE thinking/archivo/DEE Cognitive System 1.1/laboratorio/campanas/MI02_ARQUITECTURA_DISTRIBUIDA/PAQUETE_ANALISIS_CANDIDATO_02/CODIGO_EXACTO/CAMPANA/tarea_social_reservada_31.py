"""New hidden-world contexts and raw referents, target never delivered to A."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from app.lives import WorldAdapter
from capacidades.geometria_distribuida_mi02_r6 import unified_recipe
from capacidades import integracion_distribuida_mi02_r6 as b
cases=[(190,'intact',(61,19),-1),(191,'intact',(19,61),1),(192,'cut_message',(61,19),-1),(193,'cut_message',(19,61),1),(194,'sham_query',(61,19),-1),(195,'no_gate_resource',(61,19),-1),(196,'cut_query',(61,19),-1),(197,'cut_return',(61,19),-1)]
atomic_json(E/'RESERVA_SOCIAL31_FIJADA.json',{'cases':cases,'own_experiences':[11,11],'latent_world_rule':'Two predeclared hidden world states determine B-only raw observations and the third physical affordance. The first two opportunities are identical. No code compares B values to select A action, no target enters A, and all routes are fixed beforehand.','new_referents':'61/19 and19/61 not used to tune R6 geometry','metric':'First third-opportunity material action in the actual available branch, excluding conflicts. B-private differences and their native transport must account for any gain.','scope':'Prepared private-world task, not general semantic productivity. New T0 lives remain auxiliary; their knowledge is never imported into MAIN.'})
for case,control,private,available in cases:
    life='MI02_RESERVA_SOCIAL_'+str(case);r,g=unified_recipe(control=control);sources=archive();a=WorldAdapter(d.OrganizationalWorld.create(r));p=E/(life+'.PREPARACION_T0.deetsnap.gz');a.save(p);Store().import_state(p,life,'fisica_directa',expected=sha(p));atomic_json(E/(life+'.RECETA_T0.json'),{'sources':sources,'geometry':g,'new_untrained_T0':True})
    run(life,'SOCIAL31_ACQUIRE_'+str(case),lambda a,g=g,private=private:b.acquire(a,geometry=g,own=(11,11),private=private))
    z=run(life,'SOCIAL31_USE_'+str(case),lambda a,available=available:b.live(a,availability=[-1,-1,available]));last=z['rows'][-1]
    print(json.dumps({'case':case,'reserved_available':available,'third_useful':last['useful_material_actions'],'third_failed':last['failed_material_actions'],'B_active':z['final']['regions']['B']['state']>0}),flush=True)
