"""Final bounded construction revision in this reader family; new controls."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from app.lives import WorldAdapter
from capacidades.geometria_distribuida_mi02_r9 import unified_recipe
from capacidades import integracion_distribuida_mi02_r9 as b
cases=[(240,'intact',(61,19)),(241,'no_refresh_source',(61,19)),(242,'cut_query',(61,19)),(243,'cut_message',(61,19)),(244,'intact',(19,61)),(245,'no_private_history',(None,None))]
atomic_json(E/'LECTOR_SOCIAL44_FIJADO.json',{'cases':cases,'own':[11,11],'future':[-1]*4+[1]*4,'revision_basis':'DIAGNOSTICO_SOPORTE43 saved-state calculation, NOT an assumed history lineage. The old removed frame gap atB+(0,1,1) became a new alive support in bothR7/R8.','change':'Inert native SEM4 boundary at removed frame gaps from newT0, no learned fields copied or cleared. Zero-load B reader and generic downstream transport5 unchanged fromR8.','metric':'B reader empty/active episodes, native private-dependent response and actual A use, not shape resemblance','bounded_family':'This is the third/final construction revision after two unsuccessful reader-release hypotheses. Preserve all outcomes.','sources':archive()})
for case,control,private in cases:
    life='MI02_SOCIAL_REUSABLE_'+str(case);r,g=unified_recipe(control);a=WorldAdapter(d.OrganizationalWorld.create(r));p=E/(life+'.PREPARACION_T0.deetsnap.gz');a.save(p);Store().import_state(p,life,'fisica_directa',expected=sha(p));atomic_json(E/(life+'.RECETA_T0.json'),{'geometry':g,'sources':archive(),'new_untrained_T0':True})
    run(life,'SOCIAL44_ACQUIRE_'+str(case),lambda a,g=g,private=private:b.acquire(a,geometry=g,own=(11,11),private=private))
    run(life,'SOCIAL44_USE_'+str(case),lambda a:b.live(a,availability=[-1]*4+[1]*4))
atomic_json(E/'SOCIAL44_CORTES.json',{str(i):Store().record('MI02_SOCIAL_REUSABLE_'+str(i))for i,_,_ in cases})
