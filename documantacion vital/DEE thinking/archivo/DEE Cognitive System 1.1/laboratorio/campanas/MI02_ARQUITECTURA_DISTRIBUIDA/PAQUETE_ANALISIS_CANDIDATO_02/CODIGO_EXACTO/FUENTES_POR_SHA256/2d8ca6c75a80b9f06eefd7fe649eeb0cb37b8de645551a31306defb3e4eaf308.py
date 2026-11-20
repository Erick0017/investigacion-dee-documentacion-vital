"""Bounded architecture contrast, not a trained transplant or continuation ofMAIN."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from app.lives import WorldAdapter
from capacidades.geometria_distribuida_mi02_r7 import unified_recipe
from capacidades import integracion_distribuida_mi02_r7 as b
cases=[(220,'intact',(61,19)),(221,'cut_query',(61,19)),(222,'cut_message',(61,19)),(223,'intact',(19,61)),(224,'no_refresh_source',(61,19))]
atomic_json(E/'LECTOR_SOCIAL40_FIJADO.json',{'cases':cases,'new_T0_own':[11,11],'future':[-1]*4+[1]*4,'metric':'Actual native query arrivals, B-reader state transitions/replies, retained learned private fields, A context and material contact utility. Never equate an empty reader with erased reference.','question':'Can the already useful R6 social link reuse a naturally consumable B reader instead of relying on a permanently active reader?','controls':['query route cut','message cut','opposite private history','generic recurring support omitted'],'not_claimed':'Autonomous source construction or new MAIN biography','sources':archive()})
for case,control,private in cases:
    life='MI02_SOCIAL_EFIMERO_'+str(case);r,g=unified_recipe(control);a=WorldAdapter(d.OrganizationalWorld.create(r));p=E/(life+'.PREPARACION_T0.deetsnap.gz');a.save(p);Store().import_state(p,life,'fisica_directa',expected=sha(p));atomic_json(E/(life+'.RECETA_T0.json'),{'geometry':g,'sources':archive(),'new_untrained_T0':True})
    run(life,'SOCIAL40_ACQUIRE_'+str(case),lambda a,g=g,private=private:b.acquire(a,geometry=g,own=(11,11),private=private))
    run(life,'SOCIAL40_USE_'+str(case),lambda a:b.live(a,availability=[-1]*4+[1]*4))
atomic_json(E/'SOCIAL40_CORTES.json',{str(i):Store().record('MI02_SOCIAL_EFIMERO_'+str(i))for i,_,_ in cases})
