"""R2 corrects failed private retention before the dormant B reader opens."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from app.lives import WorldAdapter
from capacidades.geometria_distribuida_mi02_r2 import unified_recipe
from capacidades import integracion_distribuida_mi02_r2 as b
atomic_json(E/'PROTOCOLO_UNIFICADO_18.json',{'conditions':[-1]*5,'hypothesis':'R1 private raw samples were admitted but their five-neighbour memories decayed without a live B reader. Two zero-load supports outside B reader neighbourhood now preserve those samples before any query. This is a new declared architecture, not a repaired future of120.','native_query_hypothesis':'Two actual failed-action consequences should bring local fields to a balance from which native x0 requests can activate dormant B through the fixed gate.','controls':['formed-query cut','generic gate resource absent','private histories reversed'],'no_host_query_callback':True})
for case,control,private in[(130,'intact',(47,17)),(131,'cut_query',(47,17)),(132,'no_gate_resource',(47,17)),(133,'intact',(17,47))]:
    life='MI02_UNIFICADA_'+str(case);r,g=unified_recipe(control=control);sources=archive();a=WorldAdapter(d.OrganizationalWorld.create(r));p=E/(life+'.PREPARACION_T0.deetsnap.gz');a.save(p);Store().import_state(p,life,'fisica_directa',expected=sha(p));atomic_json(E/(life+'.RECETA_T0.json'),{'sources':sources,'geometry':g,'new_untrained_T0':True,'no_E1_memory_transplant':True})
    run(life,'UNIFICADA18_ADQUIRIR_'+str(case),lambda a,g=g,private=private:b.acquire(a,geometry=g,private=private))
    z=run(life,'UNIFICADA18_VIVIR_'+str(case),lambda a:b.live(a,availability=[-1]*5))
    print(json.dumps({'case':case,'useful':sum(bool(x['useful_material_actions'])for x in z['rows']),'queries':sum(x['query_material']for x in z['rows']),'B_active_frames':sum(f['B']['state']>0 for x in z['rows']for f in x['frames']),'rows':[{'t':x['critical_tick'],'useful':x['useful_material_actions'],'failed':x['failed_material_actions'],'query':x['query_material'],'M':[v['s_reg']for v in x['frames'][-1]['M']]}for x in z['rows']]},ensure_ascii=False),flush=True)
