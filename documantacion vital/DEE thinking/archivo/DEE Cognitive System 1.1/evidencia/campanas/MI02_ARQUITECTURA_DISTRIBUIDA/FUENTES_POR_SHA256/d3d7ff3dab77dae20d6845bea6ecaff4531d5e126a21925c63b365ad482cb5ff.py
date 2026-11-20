"""Reserved new raw contents on already frozen R9 anatomy; not MAIN replacement."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from app.lives import WorldAdapter
from capacidades.geometria_distribuida_mi02_r9 import unified_recipe
from capacidades import integracion_distribuida_mi02_r9 as b
cases=[(246,'intact',(91,29),-1),(247,'intact',(29,91),1),(248,'cut_message',(91,29),-1),(249,'sham_query',(91,29),-1),(250,'no_private_history',(None,None),-1)]
atomic_json(E/'RESERVA_REUSABLE46_FIJADA.json',{'candidates':cases,'own':[13,13],'sequence':'Two identical right-available experiences, third affordance fixed by the predeclared hidden world condition. B alone initially receives the private raw observations; no target is sent to A.','freeze':'R9 geometry, generic support, zero B-reader load, downstream symmetric5 and reader criteria frozen before all five new lives.','not_claimed':'These auxiliary lives do not replace or contribute memories to D1MAIN. No arbitrary new-message update or language understanding is credited.','sources':archive()})
for case,control,private,third in cases:
    life='MI02_RESERVA_REUSABLE_'+str(case);r,g=unified_recipe(control);a=WorldAdapter(d.OrganizationalWorld.create(r));p=E/(life+'.PREPARACION_T0.deetsnap.gz');a.save(p);Store().import_state(p,life,'fisica_directa',expected=sha(p));atomic_json(E/(life+'.RECETA_T0.json'),{'geometry':g,'sources':archive(),'new_untrained_T0':True})
    run(life,'RESERVA46_ACQUIRE_'+str(case),lambda a,g=g,private=private:b.acquire(a,geometry=g,own=(13,13),private=private))
    run(life,'RESERVA46_USE_'+str(case),lambda a,third=third:b.live(a,availability=[-1,-1,third]))
atomic_json(E/'RESERVA46_CORTES.json',{str(i):Store().record('MI02_RESERVA_REUSABLE_'+str(i))for i,_,_,_ in cases})
