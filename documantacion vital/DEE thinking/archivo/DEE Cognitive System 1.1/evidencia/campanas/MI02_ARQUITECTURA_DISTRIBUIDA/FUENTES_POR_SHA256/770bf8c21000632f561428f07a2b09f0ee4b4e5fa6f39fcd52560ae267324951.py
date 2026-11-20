"""R6 routes around the actual fixed receiver obstruction found in R5."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from app.lives import WorldAdapter
from capacidades.geometria_distribuida_mi02_r6 import unified_recipe
from capacidades import integracion_distribuida_mi02_r6 as b
seq=[-1]*4+[1]*3
atomic_json(E/'PROTOCOLO_UNIFICADO_22.json',{'conditions':seq,'N':26,'hypothesis':'R5 retained native adaptation and initiated B, but receiver support lay on the message bus. R6 keeps those memory supports and approaches recipients diagonally from an outer bus. Actual source/cut coordinates, not drawn distance, determine the contrast.','controls':['query cut','message cut','return cut','private history reversed'],'architecture_freeze':'No changes to any life after its T0 preparation.'})
for case,control,private in[(180,'intact',(47,17)),(181,'cut_query',(47,17)),(182,'cut_message',(47,17)),(183,'cut_return',(47,17)),(184,'intact',(17,47))]:
    life='MI02_UNIFICADA_'+str(case);r,g=unified_recipe(control=control);sources=archive();a=WorldAdapter(d.OrganizationalWorld.create(r));p=E/(life+'.PREPARACION_T0.deetsnap.gz');a.save(p);Store().import_state(p,life,'fisica_directa',expected=sha(p));atomic_json(E/(life+'.RECETA_T0.json'),{'sources':sources,'geometry':g,'new_untrained_T0':True,'no_E1_memory_transplant':True})
    run(life,'UNIFICADA22_ADQUIRIR_'+str(case),lambda a,g=g,private=private:b.acquire(a,geometry=g,private=private))
    z=run(life,'UNIFICADA22_VIVIR_'+str(case),lambda a:b.live(a,availability=seq))
    print(json.dumps({'case':case,'useful':sum(bool(x['useful_material_actions'])for x in z['rows']),'queries':sum(x['query_material']for x in z['rows']),'B_active_frames':sum(f['B']['state']>0 for x in z['rows']for f in x['frames']),'rows':[{'t':x['critical_tick'],'available':x['availability'],'useful':x['useful_material_actions'],'failed':x['failed_material_actions'],'query':x['query_material'],'M':[v['s_reg']for v in x['frames'][-1]['M']]}for x in z['rows']]},ensure_ascii=False),flush=True)
