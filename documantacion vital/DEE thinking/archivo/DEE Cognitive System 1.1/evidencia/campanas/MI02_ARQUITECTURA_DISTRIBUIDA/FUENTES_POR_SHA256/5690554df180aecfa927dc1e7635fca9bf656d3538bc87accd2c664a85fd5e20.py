"""First spatially coupled alternative; independent T0 lives, no E1 transplant."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from app.lives import WorldAdapter
from capacidades import distribucion_social_mi02 as b
atomic_json(E/'PROTOCOLO_SOCIAL_12.json',{'N':25,'own_samples':[10,10],'private_B_histories':[[47,17],[17,47]],'control':'Native channel cut after emission; sham comparable fixed matter outside path','frozen_before_results':'Same native sources and symmetric physical paths in both histories. No answer callback; all preparations precede acquired content. No learned policy/Spanish/general mind claimed.'})
for case,values,control in[(100,(47,17),'intact'),(101,(17,47),'intact'),(102,(47,17),'cut_message'),(103,(47,17),'sham'),(104,(None,None),'intact')]:
    life='MI02_DISTRIBUIDA_'+str(case);r,g=b.design(control=control);sources=archive();a=WorldAdapter(d.OrganizationalWorld.create(r));p=E/(life+'.PREPARACION_T0.deetsnap.gz');a.save(p);Store().import_state(p,life,'fisica_directa',expected=sha(p));atomic_json(E/(life+'.RECETA_T0.json'),{'geometry':g,'sources':sources,'new_untrained_life':True,'not_inherited_E1':True})
    run(life,'SOCIAL12_ADQUIRIR_'+str(case),lambda a,values=values,g=g:b.acquire(a,private=values,geometry=g))
    z=run(life,'SOCIAL12_USAR_'+str(case),lambda a:b.continue_world(a,ticks=180))
    print(json.dumps({'case':case,'A_directions':{str(v):sum(tuple(x['A']['direction'])==v for x in z['rows'])for v in set(tuple(x['A']['direction'])for x in z['rows'])},'final':z['final']},ensure_ascii=False),flush=True)
