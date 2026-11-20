"""R3 context ports separated from motors. New lives, not an R1/R2 repair."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from app.lives import WorldAdapter
from capacidades.geometria_distribuida_mi02_r3 import unified_recipe
from capacidades import integracion_distribuida_mi02_r3 as b
atomic_json(E/'PROTOCOLO_UNIFICADO_19.json',{'conditions':[-1]*5,'N':26,'architecture':'New context ports upperZ, motors lowerZ, queryx0. Matched native transport lengths in an even torus; no claimed periodN. Two supports preserve privateB before a reader exists.','contrasts':['intact','querycut','returncut','generic gate resource absent'],'hypothesis':'Earlier social zero-resource ghosts obstructed motor ports even before B responded. R3 stops those ghosts away from motor/query interfaces; an actual native request is required to initialize B.','frozen_criteria':'Useful physical action at available contact; native x0 carrier counted separately as request. No host calls a recovery/reader when it observes failure.'})
for case,control in[(150,'intact'),(151,'cut_query'),(152,'cut_return'),(153,'no_gate_resource')]:
    life='MI02_UNIFICADA_'+str(case);r,g=unified_recipe(control=control);sources=archive();a=WorldAdapter(d.OrganizationalWorld.create(r));p=E/(life+'.PREPARACION_T0.deetsnap.gz');a.save(p);Store().import_state(p,life,'fisica_directa',expected=sha(p));atomic_json(E/(life+'.RECETA_T0.json'),{'sources':sources,'geometry':g,'new_untrained_T0':True,'no_E1_memory_transplant':True})
    run(life,'UNIFICADA19_ADQUIRIR_'+str(case),lambda a,g=g:b.acquire(a,geometry=g))
    z=run(life,'UNIFICADA19_VIVIR_'+str(case),lambda a:b.live(a,availability=[-1]*5))
    print(json.dumps({'case':case,'useful':sum(bool(x['useful_material_actions'])for x in z['rows']),'queries':sum(x['query_material']for x in z['rows']),'B_active_frames':sum(f['B']['state']>0 for x in z['rows']for f in x['frames']),'rows':[{'t':x['critical_tick'],'useful':x['useful_material_actions'],'failed':x['failed_material_actions'],'query':x['query_material'],'M':[v['s_reg']for v in x['frames'][-1]['M']]}for x in z['rows']]},ensure_ascii=False),flush=True)
