"""R5 keeps social support outside motor and acquired-local-memory contexts."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from app.lives import WorldAdapter
from capacidades.geometria_distribuida_mi02_r5 import unified_recipe
from capacidades import integracion_distribuida_mi02_r5 as b
seq=[-1]*4+[1]*3
atomic_json(E/'PROTOCOLO_UNIFICADO_21.json',{'conditions':seq,'N':26,'hypothesis':'R4 sustained content but its receiver support raised alive-neighbour counts at motors, blocking outflow. R5 relocates context to oppositeY and puts its five supports atX+/-2 outside Q, local-memory and bus-coupler neighbourhoods. Original adverse lives remain intact.','controls':['query cut','message cut','return cut','private history reversed'],'scope':'New T0 architecture. No trained transplant, no online port clearing or clock changes.'})
for case,control,private in[(170,'intact',(47,17)),(171,'cut_query',(47,17)),(172,'cut_message',(47,17)),(173,'cut_return',(47,17)),(174,'intact',(17,47))]:
    life='MI02_UNIFICADA_'+str(case);r,g=unified_recipe(control=control);sources=archive();a=WorldAdapter(d.OrganizationalWorld.create(r));p=E/(life+'.PREPARACION_T0.deetsnap.gz');a.save(p);Store().import_state(p,life,'fisica_directa',expected=sha(p));atomic_json(E/(life+'.RECETA_T0.json'),{'sources':sources,'geometry':g,'new_untrained_T0':True,'no_E1_memory_transplant':True})
    run(life,'UNIFICADA21_ADQUIRIR_'+str(case),lambda a,g=g,private=private:b.acquire(a,geometry=g,private=private))
    z=run(life,'UNIFICADA21_VIVIR_'+str(case),lambda a:b.live(a,availability=seq))
    print(json.dumps({'case':case,'useful':sum(bool(x['useful_material_actions'])for x in z['rows']),'queries':sum(x['query_material']for x in z['rows']),'B_active_frames':sum(f['B']['state']>0 for x in z['rows']for f in x['frames']),'rows':[{'t':x['critical_tick'],'available':x['availability'],'useful':x['useful_material_actions'],'failed':x['failed_material_actions'],'query':x['query_material'],'M':[v['s_reg']for v in x['frames'][-1]['M']]}for x in z['rows']]},ensure_ascii=False),flush=True)
