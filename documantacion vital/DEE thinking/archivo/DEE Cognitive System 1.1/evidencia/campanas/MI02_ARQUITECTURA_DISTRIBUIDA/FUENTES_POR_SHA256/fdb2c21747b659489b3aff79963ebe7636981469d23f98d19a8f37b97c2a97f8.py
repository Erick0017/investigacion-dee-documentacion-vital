"""Second bounded reader family revision, all first-version failures retained."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from app.lives import WorldAdapter
from capacidades.geometria_distribuida_mi02_r8 import unified_recipe
from capacidades import integracion_distribuida_mi02_r8 as b
cases=[(230,'intact',(61,19)),(231,'no_refresh_source',(61,19)),(232,'cut_query',(61,19)),(233,'cut_message',(61,19)),(234,'intact',(19,61)),(235,'no_private_history',(None,None))]
atomic_json(E/'LECTOR_SOCIAL42_FIJADO.json',{'cases':cases,'new_T0_own':[11,11],'future':[-1]*4+[1]*4,'why_R7_not_accepted_as_ephemeral':'Its5load B reader remained active and omitted refresh resource did not change that; no empty/readmit claim was valid.','revision':'Zero-load B reader; identical generic5 is supplied on both first-turn branches only after native private-dependent output. Not a per-answer source.','metrics':'Native B empty/active transitions and qualified outputs, A received context and actual contact utility; no host recovery or clearing','new_lives_not_MAIN':True,'sources':archive()})
for case,control,private in cases:
    life='MI02_SOCIAL_NEUTRO_'+str(case);r,g=unified_recipe(control);a=WorldAdapter(d.OrganizationalWorld.create(r));p=E/(life+'.PREPARACION_T0.deetsnap.gz');a.save(p);Store().import_state(p,life,'fisica_directa',expected=sha(p));atomic_json(E/(life+'.RECETA_T0.json'),{'geometry':g,'sources':archive(),'new_untrained_T0':True})
    run(life,'SOCIAL42_ACQUIRE_'+str(case),lambda a,g=g,private=private:b.acquire(a,geometry=g,own=(11,11),private=private))
    run(life,'SOCIAL42_USE_'+str(case),lambda a:b.live(a,availability=[-1]*4+[1]*4))
atomic_json(E/'SOCIAL42_CORTES.json',{str(i):Store().record('MI02_SOCIAL_NEUTRO_'+str(i))for i,_,_ in cases})
